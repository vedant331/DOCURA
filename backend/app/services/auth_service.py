"""Account and session logic.

Kept out of the route handlers so that the security-relevant decisions — how a
password is checked, when a session is valid, who owns what — sit in one readable
place rather than being spread across endpoints.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import (
    DeletionNotConfirmedError,
    DocumentStorageError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    WeakPasswordError,
)
from app.core.logging import get_logger
from app.core.security import (
    generate_reset_token,
    generate_session_token,
    hash_password,
    hash_reset_token,
    hash_session_token,
    needs_rehash,
    verify_dummy_password,
    verify_password,
)
from app.db.models import Document, PasswordResetToken, Session, User
from app.services.reset_delivery import ResetDeliveryChannel
from app.services.storage import DocumentStorage

logger = get_logger(__name__)


async def delete_account(
    db: AsyncSession, *, user: User, confirm_email: str, storage: DocumentStorage
) -> tuple[int, int]:
    """Irreversibly delete an account and everything derived from it (FR-ACC-006/007/008,
    NFR-PRIV-003).

    FR-ACC-007 requires an explicit confirmation: the caller must echo their own account email
    (case-insensitively). A missing or mismatched confirmation deletes nothing.

    The account row is removed first and committed, then the stored originals are deleted —
    the same ordering as :func:`app.services.document_service.delete_document`, for the same
    reason: the only state that can survive a partial failure is orphaned bytes (unreachable,
    since the key that named them is gone, and sweepable), never a visible record whose file is
    missing. Deleting the ``users`` row triggers the database's ``ON DELETE CASCADE`` for
    sessions, reset tokens, documents (→ processing jobs, extraction runs → pages/blocks/
    observations), and form sessions (→ actions) — so extracted information and derived rows go
    with it. Returns ``(documents_removed, objects_removed)``; nothing about the values is logged.
    """
    if confirm_email.strip().casefold() != user.email.casefold():
        raise DeletionNotConfirmedError

    result = await db.scalars(select(Document.storage_key).where(Document.user_id == user.id))
    keys = list(result.all())

    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()

    objects_removed = 0
    for key in keys:
        try:
            if storage.delete(key):
                objects_removed += 1
        except DocumentStorageError:
            # The account is already gone; a leftover object is an operational sweepable, not
            # the user's error. No key/value is logged (NFR-PRIV-007).
            logger.error("account.orphaned_object", reason="delete_failed", user_id=str(user.id))

    logger.info(
        "account.deleted",
        user_id=str(user.id),
        documents_removed=len(keys),
        objects_removed=objects_removed,
    )
    return len(keys), objects_removed


def normalise_email(email: str) -> str:
    """Lowercase and strip, so ``A@B.com `` and ``a@b.com`` are one account."""
    return email.strip().lower()


def validate_password_strength(password: str, settings: Settings) -> None:
    """Enforce the configured policy.

    Length is the requirement that actually resists guessing, so it is the one that
    is enforced. Character-class rules are deliberately not imposed: they push
    people towards predictable substitutions without adding real entropy, and NIST
    SP 800-63B advises against them.
    """
    if len(password) < settings.password_min_length:
        raise WeakPasswordError(
            detail=(
                f"The password must be at least {settings.password_min_length} characters long."
            ),
            remediation=(
                f"Choose a password of {settings.password_min_length} characters or "
                "more. A memorable phrase works well."
            ),
        )


async def register_user(db: AsyncSession, *, email: str, password: str, settings: Settings) -> User:
    """Create an account, or fail if the address is taken."""
    normalised = normalise_email(email)
    validate_password_strength(password, settings)

    user = User(email=normalised, password_hash=hash_password(password))
    db.add(user)

    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        # Uniqueness is decided by the database, so two simultaneous registrations
        # cannot both succeed the way a read-then-write check would allow.
        raise EmailAlreadyRegisteredError from exc

    await db.commit()
    logger.info("auth.user_registered", user_id=str(user.id))
    return user


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> User:
    """Verify credentials, raising the same error for every kind of failure."""
    normalised = normalise_email(email)
    user = await db.scalar(select(User).where(User.email == normalised))

    if user is None:
        # Spend the same time as a real verification so that response latency does
        # not reveal whether this address has a DOCURA account.
        verify_dummy_password(password)
        logger.info("auth.login_failed", reason="unknown_account")
        raise InvalidCredentialsError

    if not verify_password(password, user.password_hash):
        logger.info("auth.login_failed", reason="bad_password", user_id=str(user.id))
        raise InvalidCredentialsError

    if not user.is_active:
        logger.info("auth.login_failed", reason="inactive", user_id=str(user.id))
        raise InvalidCredentialsError

    if needs_rehash(user.password_hash):
        # Argon2 parameters were raised since this password was set; upgrade it now,
        # while the plaintext is legitimately in hand.
        user.password_hash = hash_password(password)
        await db.commit()
        logger.info("auth.password_rehashed", user_id=str(user.id))

    return user


async def create_session(
    db: AsyncSession, *, user: User, settings: Settings
) -> tuple[Session, str]:
    """Open a session, returning it with the clear token exactly once."""
    token = generate_session_token()
    now = datetime.now(UTC)

    session = Session(
        user_id=user.id,
        token_hash=hash_session_token(token),
        expires_at=now + timedelta(minutes=settings.session_idle_timeout_minutes),
        absolute_expires_at=now + timedelta(hours=settings.session_absolute_timeout_hours),
        last_used_at=now,
    )
    db.add(session)
    await db.commit()

    # `session_ref` rather than `session_id`: the latter is redacted by default,
    # because in most systems a session id is itself the credential. DOCURA's is a
    # primary key — the credential is the token, which is hashed and never logged.
    logger.info("auth.session_created", user_id=str(user.id), session_ref=str(session.id))
    return session, token


async def resolve_session(db: AsyncSession, *, token: str, settings: Settings) -> Session | None:
    """Look up a live session by token, sliding its inactivity deadline forward.

    Returns ``None`` for absent, unknown, revoked, idle-expired, and
    absolute-expired alike — the caller must not be able to tell these apart.
    """
    digest = hash_session_token(token)
    # Matching on the stored digest is itself the constant-time-safe comparison:
    # the lookup is by an indexed 256-bit hash, so there is no per-character leak.
    session = await db.scalar(select(Session).where(Session.token_hash == digest))

    if session is None:
        return None

    now = datetime.now(UTC)
    if session.revoked_at is not None:
        return None
    if session.expires_at <= now or session.absolute_expires_at <= now:
        return None

    session.expires_at = now + timedelta(minutes=settings.session_idle_timeout_minutes)
    session.last_used_at = now
    await db.commit()
    return session


async def revoke_session(db: AsyncSession, *, session: Session) -> None:
    """End one session (logout)."""
    if session.revoked_at is None:
        session.revoked_at = datetime.now(UTC)
        await db.commit()
        logger.info(
            "auth.session_revoked",
            user_id=str(session.user_id),
            session_ref=str(session.id),
        )


async def list_active_sessions(db: AsyncSession, *, user_id: uuid.UUID) -> list[Session]:
    """Active sessions for one user (FR-ACC-008).

    Scoped by ``user_id`` in the query itself, so the isolation cannot be lost by a
    caller forgetting to filter the result.
    """
    now = datetime.now(UTC)
    result = await db.scalars(
        select(Session)
        .where(
            Session.user_id == user_id,
            Session.revoked_at.is_(None),
            Session.expires_at > now,
            Session.absolute_expires_at > now,
        )
        .order_by(Session.created_at.desc())
    )
    return list(result)


async def revoke_all_sessions(
    db: AsyncSession, *, user_id: uuid.UUID, except_session_id: uuid.UUID | None = None
) -> int:
    """Sign out of every session for one user (UC-003 step 5). Returns the count."""
    sessions = await list_active_sessions(db, user_id=user_id)
    now = datetime.now(UTC)

    revoked = 0
    for session in sessions:
        if except_session_id is not None and session.id == except_session_id:
            continue
        session.revoked_at = now
        revoked += 1

    await db.commit()
    logger.info("auth.sessions_revoked", user_id=str(user_id), count=revoked)
    return revoked


# --------------------------------------------------------------------------
# Password reset (FR-ACC-005, UC-001 A2)
#
# The shape of this flow is fixed by the requirement's two words. "Verified":
# possession of a secret sent to the address already on the account is what proves
# identity, so the token is the only credential the confirm step accepts. "Must not
# weaken the vault": every property below exists to keep the reset path from being
# a cheaper way in than the password it replaces — single use, short life, no
# account-existence oracle, and every existing session revoked on success.
# --------------------------------------------------------------------------


async def _supersede_reset_tokens(db: AsyncSession, *, user_id: uuid.UUID, now: datetime) -> None:
    """Spend every outstanding token for this account, so only the newest link works.

    Without this, each request would leave another live way in, and the account's
    exposure would grow with every forgotten-password click.
    """
    outstanding = await db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
    )
    for token in outstanding:
        token.used_at = now


async def request_password_reset(
    db: AsyncSession,
    *,
    email: str,
    settings: Settings,
    delivery: ResetDeliveryChannel,
) -> None:
    """Start the reset process. Returns nothing, and reveals nothing.

    The caller answers identically whether or not the address has an account: the
    endpoint is unauthenticated, so any difference in status, body, or wording would
    turn it into a register of who holds a DOCURA vault.
    """
    normalised = normalise_email(email)
    user = await db.scalar(select(User).where(User.email == normalised))

    if user is None or not user.is_active:
        logger.info("auth.password_reset_requested", outcome="no_active_account")
        return

    now = datetime.now(UTC)
    await _supersede_reset_tokens(db, user_id=user.id, now=now)

    token = generate_reset_token()
    record = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_reset_token(token),
        expires_at=now + timedelta(minutes=settings.password_reset_token_ttl_minutes),
    )
    db.add(record)
    await db.commit()

    # `reset_ref` is the row's primary key, not the credential — the token itself is
    # held only in the local `token` variable and the delivery channel.
    logger.info(
        "auth.password_reset_issued",
        user_id=str(user.id),
        reset_ref=str(record.id),
    )
    await delivery.send(email=user.email, token=token)


async def reset_password(
    db: AsyncSession, *, token: str, new_password: str, settings: Settings
) -> int:
    """Complete the reset. Returns how many sessions the change ended.

    Order matters here. The password policy is checked *before* the token is spent,
    so a rejected password does not burn the user's only link; the token is spent
    and every session revoked in the same transaction, so a reset can never leave
    the old password working or an attacker's session alive.
    """
    digest = hash_reset_token(token)
    record = await db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == digest)
    )
    now = datetime.now(UTC)

    if record is None or record.used_at is not None or record.expires_at <= now:
        logger.info("auth.password_reset_failed", reason="unusable_token")
        raise InvalidResetTokenError

    user = await db.get(User, record.user_id)
    if user is None or not user.is_active:
        logger.info("auth.password_reset_failed", reason="no_active_account")
        raise InvalidResetTokenError

    # Raises before anything is mutated, leaving the token usable for a second try.
    validate_password_strength(new_password, settings)

    user.password_hash = hash_password(new_password)
    record.used_at = now
    await _supersede_reset_tokens(db, user_id=user.id, now=now)

    # NFR-SEC-005 and UC-001 A2: whoever was signed in with the old password —
    # including whoever prompted the reset — is signed out by it.
    sessions = await list_active_sessions(db, user_id=user.id)
    for session in sessions:
        session.revoked_at = now

    await db.commit()

    logger.info(
        "auth.password_reset_completed",
        user_id=str(user.id),
        reset_ref=str(record.id),
        sessions_revoked=len(sessions),
    )
    return len(sessions)
