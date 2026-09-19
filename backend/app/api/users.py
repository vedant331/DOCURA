"""User endpoints (FR-ACC-002, FR-ACC-006/007/008)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession, DocumentStore
from app.schemas.auth import (
    AccountDeletionRequest,
    AccountDeletionResponse,
    UserResponse,
)
from app.services.auth_service import delete_account

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, summary="The authenticated account")
async def read_current_user(user: CurrentUser) -> UserResponse:
    """Return the caller's own account.

    There is no ``/users/{id}`` counterpart in this sprint, and that is the point:
    identity comes from the session alone, so there is no path by which one account
    can name another (NFR-SEC-003, BR-018). Isolation here is structural rather
    than a check that could be forgotten.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.delete("/me", response_model=AccountDeletionResponse, summary="Delete this account")
async def delete_current_user(
    user: CurrentUser,
    db: DbSession,
    storage: DocumentStore,
    payload: AccountDeletionRequest,
) -> AccountDeletionResponse:
    """Irreversibly delete the caller's account and all of their data (FR-ACC-006/007/008,
    NFR-PRIV-003).

    Acts only on the authenticated account — identity comes from the session, never a
    client-supplied id, so one account can never delete another. The request must carry the
    explicit confirmation FR-ACC-007 requires (the account's own email); the response states
    what was destroyed. Removing the account cascades every document, all extracted
    information, derived rows, sessions (this one included, so the token is invalidated), and
    form-session history; the stored originals are then deleted from storage.
    """
    documents_removed, objects_removed = await delete_account(
        db, user=user, confirm_email=payload.confirm_email, storage=storage
    )
    return AccountDeletionResponse(
        email=user.email,
        documents_removed=documents_removed,
        objects_removed=objects_removed,
    )
