"""Form-session and audit logic (M1 — the form-action foundation).

Every function takes ``user_id`` as a keyword argument and puts it in the ``WHERE``
clause, for the reason :mod:`app.services.document_service` spells out: NFR-SEC-003
forbids ownership being inferred from a client-supplied identifier, and the guarantee
is that the owner is part of the *query*, not a check against an already-loaded row.
A session's actions are reached only through a session that was already restricted to
the caller, so the history is transitively owner-scoped — it is never loaded globally
and filtered afterward.

This is infrastructure for the future extension and form-action pipeline. It does not
read pages, detect forms, fill fields, attach documents, or approve anything. What it
provides is the session lifecycle and the append-only history those milestones write
into through :func:`record_action`.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    AttributeNotFoundError,
    DocumentNotFoundError,
    FormActionNotFoundError,
    FormSessionNotActiveError,
    FormSessionNotFoundError,
)
from app.core.logging import get_logger
from app.db.models import (
    AttributeObservation,
    Document,
    ExtractionRun,
    FormAction,
    FormActionOutcome,
    FormActionType,
    FormSession,
    FormSessionState,
)

logger = get_logger(__name__)


async def create_form_session(db: AsyncSession, *, user_id: uuid.UUID) -> FormSession:
    """Open a session for the authenticated user (FR-INT-001, BR-014).

    Creation *is* activation: a session exists only because the user explicitly
    activated DOCURA on an open form. It starts ``ACTIVE``; ``created_at`` is the
    activation time.
    """
    session = FormSession(user_id=user_id, state=FormSessionState.ACTIVE)
    db.add(session)
    await db.commit()
    logger.info("form_session.activated", user_id=str(user_id), session_ref=str(session.id))
    return session


async def get_form_session(
    db: AsyncSession, *, user_id: uuid.UUID, session_id: uuid.UUID
) -> FormSession:
    """One form session belonging to this account, or a 404.

    A session owned by someone else and one that does not exist answer identically,
    so the id cannot be used to probe which sessions are real.
    """
    session = await db.scalar(
        select(FormSession).where(
            FormSession.id == session_id,
            FormSession.user_id == user_id,
        )
    )
    if session is None:
        logger.info("form_session.access_denied", user_id=str(user_id))
        raise FormSessionNotFoundError
    return session


async def list_form_sessions(db: AsyncSession, *, user_id: uuid.UUID) -> list[FormSession]:
    """This account's form sessions, newest first. Scoped to ``user_id`` in the query."""
    result = await db.scalars(
        select(FormSession)
        .where(FormSession.user_id == user_id)
        .order_by(FormSession.created_at.desc(), FormSession.id.desc())
    )
    return list(result)


async def record_action(
    db: AsyncSession,
    *,
    session: FormSession,
    action_type: FormActionType,
    outcome: FormActionOutcome,
    field_ref: str | None = None,
    source_document_id: uuid.UUID | None = None,
    source_observation_id: uuid.UUID | None = None,
    reverses_action_id: uuid.UUID | None = None,
    detail: str | None = None,
) -> FormAction:
    """Append one entry to a session's history (FR-AUD-001…006).

    Append-only: this only ever inserts. A correction or reversal is a new action that
    references ``reverses_action_id`` (FR-AUD-005, BR-015), never a mutation of the
    original. This is the single writer the fill/select/attach/ask/approval milestones
    call; M1 itself calls it only from the lifecycle transitions below.

    The caller owns the transaction so a form action can be committed atomically with
    the effect it records.
    """
    action = FormAction(
        session_id=session.id,
        action_type=action_type,
        outcome=outcome,
        field_ref=field_ref,
        source_document_id=source_document_id,
        source_observation_id=source_observation_id,
        reverses_action_id=reverses_action_id,
        detail=detail,
    )
    db.add(action)
    await db.flush()
    return action


async def append_client_action(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    action_type: FormActionType,
    outcome: FormActionOutcome,
    field_ref: str | None = None,
    document_id: uuid.UUID | None = None,
    observation_id: uuid.UUID | None = None,
    reverses_action_id: uuid.UUID | None = None,
    detail: str | None = None,
) -> FormAction:
    """Record one in-session action the extension performed (FR-AUD-001…003).

    This is the client-facing writer that :func:`record_action` (the internal writer)
    could not be: it is fully owner-scoped and refuses anything a client should not be
    able to forge —

      * the session must belong to the caller and still be ACTIVE (history of an ended
        session is immutable);
      * every referenced id is validated as the caller's own — a ``document_id`` via the
        owner-scoped vault query, an ``observation_id`` via its run→document→user chain,
        and a ``reverses_action_id`` must name an earlier action of THIS session;
      * lifecycle transitions (hand_back / stop) are not accepted here (the schema bars
        them) — they have their own endpoints and move the session's state.

    No field value or third-party form content is stored — only a field handle and
    provenance references (FR-AUD-006, NFR-PRIV-007). Commits so the entry is durable.
    """
    session = await get_form_session(db, user_id=user_id, session_id=session_id)
    if session.state is not FormSessionState.ACTIVE:
        raise FormSessionNotActiveError

    if document_id is not None:
        # Owner-scoped: raises 404 (indistinguishable from "no such document") if not owned.
        owned = await db.scalar(
            select(Document.id).where(Document.id == document_id, Document.user_id == user_id)
        )
        if owned is None:
            raise DocumentNotFoundError

    if observation_id is not None:
        # An observation is owned via run -> document -> user. Same oracle-avoidance 404.
        owned_obs = await db.scalar(
            select(AttributeObservation.id)
            .join(ExtractionRun, AttributeObservation.run_id == ExtractionRun.id)
            .join(Document, ExtractionRun.document_id == Document.id)
            .where(AttributeObservation.id == observation_id, Document.user_id == user_id)
        )
        if owned_obs is None:
            raise AttributeNotFoundError

    if reverses_action_id is not None:
        # A reversal may only point at an earlier action of this same (owned) session.
        reversed_ok = await db.scalar(
            select(FormAction.id).where(
                FormAction.id == reverses_action_id,
                FormAction.session_id == session.id,
            )
        )
        if reversed_ok is None:
            raise FormActionNotFoundError

    action = await record_action(
        db,
        session=session,
        action_type=action_type,
        outcome=outcome,
        field_ref=field_ref,
        source_document_id=document_id,
        source_observation_id=observation_id,
        reverses_action_id=reverses_action_id,
        detail=detail,
    )
    await db.commit()
    await db.refresh(action)
    logger.info(
        "form_session.action_recorded",
        user_id=str(user_id),
        session_ref=str(session.id),
        action_type=action_type.value,
        outcome=outcome.value,
    )
    return action


async def list_actions(db: AsyncSession, *, session: FormSession) -> list[FormAction]:
    """A session's history in the order it happened (FR-AUD-004).

    Takes an already-owned session, so the entries are transitively scoped to the
    caller — no session belonging to another account can reach here.
    """
    result = await db.scalars(
        select(FormAction)
        .where(FormAction.session_id == session.id)
        .order_by(FormAction.created_at, FormAction.id)
    )
    return list(result)


async def _end_session(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    terminal_state: FormSessionState,
    action_type: FormActionType | None,
) -> FormSession:
    """Move an ACTIVE session to a terminal state, once, recording it in history.

    Only an ``ACTIVE`` session transitions; an already-ended one is refused rather
    than ended twice (BR-016), which keeps the record of the first ending intact.
    """
    session = await get_form_session(db, user_id=user_id, session_id=session_id)
    if session.state is not FormSessionState.ACTIVE:
        raise FormSessionNotActiveError

    session.state = terminal_state
    session.ended_at = func.now()
    if action_type is not None:
        await record_action(
            db, session=session, action_type=action_type, outcome=FormActionOutcome.SUCCEEDED
        )
    await db.commit()
    await db.refresh(session)
    logger.info(
        "form_session.ended",
        user_id=str(user_id),
        session_ref=str(session.id),
        state=terminal_state.value,
    )
    return session


async def hand_back(db: AsyncSession, *, user_id: uuid.UUID, session_id: uuid.UUID) -> FormSession:
    """Reach the hand-back point: control returns to the user (FR-SUB-003/004, D14).

    Records that hand-back was reached and makes no claim about whether the user
    submitted — DOCURA never submits (BR-008).
    """
    return await _end_session(
        db,
        user_id=user_id,
        session_id=session_id,
        terminal_state=FormSessionState.HANDED_BACK,
        action_type=FormActionType.HAND_BACK,
    )


async def stop(db: AsyncSession, *, user_id: uuid.UUID, session_id: uuid.UUID) -> FormSession:
    """Stop DOCURA at the user's request (FR-EXT-006, US-016).

    Values already placed in the form are the user's and are left untouched — this
    ends the session, it does not clean up the page (EC-017).
    """
    return await _end_session(
        db,
        user_id=user_id,
        session_id=session_id,
        terminal_state=FormSessionState.STOPPED,
        action_type=FormActionType.STOP,
    )


async def expire_form_session(
    db: AsyncSession, *, user_id: uuid.UUID, session_id: uuid.UUID
) -> FormSession:
    """Mark a session expired when its authenticating session lapsed (EC-016).

    Server-driven, not a client action, so there is no endpoint for it: the
    authentication layer that detects the lapse is what will call this. Provided in M1
    so the expired state is representable; the wiring to session expiry is later work.
    """
    return await _end_session(
        db,
        user_id=user_id,
        session_id=session_id,
        terminal_state=FormSessionState.EXPIRED,
        action_type=None,
    )
