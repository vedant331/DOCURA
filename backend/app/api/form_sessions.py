"""Form-session and audit endpoints (M1 — FR-INT-001, FR-EXT-006, FR-SUB-003/004, FR-AUD-004).

The backend surface the future browser extension calls to open a session on a form,
end it (hand back or stop), and read its history. Identity comes from the session,
never from the path: a caller has no vocabulary for another account's sessions, so
isolation is structural, exactly as in the vault and the record API.

There is no endpoint that appends an arbitrary history entry. History is written by
DOCURA's own actions — the fill/attach/ask/approval milestones, and the hand-back and
stop below — never posted by a client, which could otherwise forge a record of what
DOCURA did. Filling, detection, attachment, and approval are later milestones and are
not exposed here.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.db.models import FormAction, FormSession
from app.schemas.form_session import (
    FormActionListResponse,
    FormActionResponse,
    FormSessionListResponse,
    FormSessionResponse,
)
from app.services.form_session import (
    create_form_session,
    get_form_session,
    hand_back,
    list_actions,
    list_form_sessions,
    stop,
)

router = APIRouter(prefix="/form-sessions", tags=["form-sessions"])


def _to_response(session: FormSession) -> FormSessionResponse:
    return FormSessionResponse(
        id=session.id,
        state=session.state,
        created_at=session.created_at,
        ended_at=session.ended_at,
    )


def _action_response(action: FormAction) -> FormActionResponse:
    return FormActionResponse(
        id=action.id,
        action_type=action.action_type,
        outcome=action.outcome,
        field_ref=action.field_ref,
        document_id=action.source_document_id,
        observation_id=action.source_observation_id,
        reverses_action_id=action.reverses_action_id,
        detail=action.detail,
        created_at=action.created_at,
    )


@router.post(
    "",
    response_model=FormSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Activate DOCURA on a form",
)
async def activate_session(user: CurrentUser, db: DbSession) -> FormSessionResponse:
    """Open a form session for the authenticated user (FR-INT-001, BR-014).

    Creating the session is the explicit activation: nothing is read, detected, or
    filled here — that is later milestones — but from this point the session exists
    and its history can be recorded.
    """
    session = await create_form_session(db, user_id=user.id)
    return _to_response(session)


@router.get(
    "",
    response_model=FormSessionListResponse,
    summary="List this account's form sessions",
)
async def list_sessions(user: CurrentUser, db: DbSession) -> FormSessionListResponse:
    """The caller's own sessions, newest first. No identifier can widen the scope."""
    sessions = await list_form_sessions(db, user_id=user.id)
    return FormSessionListResponse(
        sessions=[_to_response(session) for session in sessions],
        count=len(sessions),
    )


@router.get(
    "/{session_id}",
    response_model=FormSessionResponse,
    summary="One form session",
)
async def read_session(
    session_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> FormSessionResponse:
    """One session, if this account owns it. Another account's answers 404 (NFR-SEC-003)."""
    session = await get_form_session(db, user_id=user.id, session_id=session_id)
    return _to_response(session)


@router.post(
    "/{session_id}/hand-back",
    response_model=FormSessionResponse,
    summary="Hand control back to the user",
)
async def hand_back_session(
    session_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> FormSessionResponse:
    """Reach the hand-back point (FR-SUB-003/004).

    Records that the session reached hand-back and makes no claim about whether the
    user submitted; submission is theirs alone (BR-008).
    """
    session = await hand_back(db, user_id=user.id, session_id=session_id)
    return _to_response(session)


@router.post(
    "/{session_id}/stop",
    response_model=FormSessionResponse,
    summary="Stop DOCURA",
)
async def stop_session(
    session_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> FormSessionResponse:
    """Stop DOCURA at the user's request (FR-EXT-006).

    Ends the session; values already placed in the form are left untouched (EC-017).
    """
    session = await stop(db, user_id=user.id, session_id=session_id)
    return _to_response(session)


@router.get(
    "/{session_id}/actions",
    response_model=FormActionListResponse,
    summary="A form session's history",
)
async def read_session_history(
    session_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> FormActionListResponse:
    """Everything DOCURA did in this session, in order (FR-AUD-004).

    The session is fetched owner-scoped first, so its history is reachable only by the
    account that owns it — the entries are never loaded globally and filtered.
    """
    session = await get_form_session(db, user_id=user.id, session_id=session_id)
    actions = await list_actions(db, session=session)
    return FormActionListResponse(
        actions=[_action_response(action) for action in actions],
        count=len(actions),
    )
