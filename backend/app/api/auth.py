"""Authentication endpoints (FR-ACC-001/002/005/008, NFR-SEC-004/005)."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.api.deps import (
    AppSettings,
    CurrentSession,
    CurrentUser,
    DbSession,
    ResetDelivery,
    client_key,
    enforce_auth_rate_limit,
)
from app.core.ratelimit import SlidingWindowRateLimiter
from app.db.models import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RegisterRequest,
    RevocationResponse,
    SessionListResponse,
    SessionResponse,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_session,
    list_active_sessions,
    register_user,
    request_password_reset,
    reset_password,
    revoke_all_sessions,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Module-level so the window survives across requests. Built lazily on first use so
# that it picks up the running application's configured limits.
_limiter: SlidingWindowRateLimiter | None = None


def _get_limiter(settings: AppSettings) -> SlidingWindowRateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = SlidingWindowRateLimiter(
            max_attempts=settings.auth_rate_limit_attempts,
            window_seconds=settings.auth_rate_limit_window_seconds,
        )
    return _limiter


def reset_rate_limiter() -> None:
    """Drop the process-wide limiter. Used by tests to isolate one case from the next."""
    global _limiter
    _limiter = None


def _to_user_response(user: User) -> UserResponse:
    """Project an account row onto its public shape.

    Written out field by field on purpose: an ORM-wide conversion would start
    exposing ``password_hash`` the day someone adds a field to the model.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
)
async def register(
    request: Request,
    payload: RegisterRequest,
    db: DbSession,
    settings: AppSettings,
) -> UserResponse:
    """Create a single-person account (FR-ACC-001, FR-ACC-003).

    Rate limited on the same terms as login: registration also runs Argon2, so an
    unlimited endpoint is a cheap way to exhaust the server's CPU.
    """
    enforce_auth_rate_limit(request, _get_limiter(settings))

    user = await register_user(
        db,
        email=payload.email,
        password=payload.password.get_secret_value(),
        settings=settings,
    )
    return _to_user_response(user)


@router.post("/login", response_model=LoginResponse, summary="Sign in")
async def login(
    request: Request,
    payload: LoginRequest,
    db: DbSession,
    settings: AppSettings,
) -> LoginResponse:
    """Authenticate and open a revocable session (UC-001 step 6, NFR-SEC-005)."""
    limiter = _get_limiter(settings)
    enforce_auth_rate_limit(request, limiter)

    user = await authenticate_user(
        db, email=payload.email, password=payload.password.get_secret_value()
    )
    session, token = await create_session(db, user=user, settings=settings)

    # A successful sign-in clears the window, so earlier typos do not count against
    # the legitimate owner for the rest of it.
    limiter.reset(client_key(request))

    return LoginResponse(
        access_token=token,
        expires_at=session.expires_at,
        user=_to_user_response(user),
    )


@router.post(
    "/logout",
    response_model=RevocationResponse,
    summary="End the current session",
)
async def logout(session: CurrentSession, db: DbSession) -> RevocationResponse:
    """Revoke the session that made this request (NFR-SEC-005).

    Server-side revocation is immediate: the next request carrying this token is
    rejected, which EC-016 requires and a self-contained token could not provide.
    """
    await revoke_session(db, session=session)
    return RevocationResponse(revoked=1)


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List active sessions",
)
async def list_sessions(
    user: CurrentUser, session: CurrentSession, db: DbSession
) -> SessionListResponse:
    """Show this account's own sessions (FR-ACC-008, UC-003).

    Scoped to ``user.id`` from the authenticated session — never to an id supplied
    by the caller (NFR-SEC-003).
    """
    sessions = await list_active_sessions(db, user_id=user.id)
    return SessionListResponse(
        sessions=[
            SessionResponse(
                id=item.id,
                created_at=item.created_at,
                last_used_at=item.last_used_at,
                expires_at=item.expires_at,
                current=item.id == session.id,
            )
            for item in sessions
        ]
    )


@router.post(
    "/sessions/revoke-all",
    response_model=RevocationResponse,
    summary="Sign out everywhere",
)
async def revoke_all(user: CurrentUser, db: DbSession) -> RevocationResponse:
    """End every session for this account, including this one (UC-003 steps 4-5)."""
    revoked = await revoke_all_sessions(db, user_id=user.id)
    return RevocationResponse(revoked=revoked)


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a password reset link",
)
async def request_reset(
    request: Request,
    payload: PasswordResetRequest,
    db: DbSession,
    settings: AppSettings,
    delivery: ResetDelivery,
) -> PasswordResetRequestResponse:
    """Begin the verified reset process (FR-ACC-005, UC-001 A2).

    Answers 202 with an identical body for every address. A 404 for unknown
    accounts would make this endpoint a free membership check on a document vault,
    which is exactly the kind of disclosure the reset is meant to avoid.

    Rate limited: unlimited, it would both spam a real inbox and let an attacker
    enumerate addresses by volume.
    """
    enforce_auth_rate_limit(request, _get_limiter(settings))

    await request_password_reset(db, email=payload.email, settings=settings, delivery=delivery)
    return PasswordResetRequestResponse()


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetConfirmResponse,
    summary="Set a new password using a reset link",
)
async def confirm_reset(
    request: Request,
    payload: PasswordResetConfirmRequest,
    db: DbSession,
    settings: AppSettings,
) -> PasswordResetConfirmResponse:
    """Spend the token and set the new password (FR-ACC-005).

    No session is opened here. The user signs in with the new password, which keeps
    possession of a mailbox from being, on its own, an authenticated session — and
    means the reset cannot be a quieter way in than the front door.
    """
    enforce_auth_rate_limit(request, _get_limiter(settings))

    revoked = await reset_password(
        db,
        token=payload.token.get_secret_value(),
        new_password=payload.password.get_secret_value(),
        settings=settings,
    )
    return PasswordResetConfirmResponse(sessions_revoked=revoked)
