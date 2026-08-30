"""User endpoints (FR-ACC-002)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.auth import UserResponse

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
