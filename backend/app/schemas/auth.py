"""Request and response models for accounts and sessions.

No response model in this module carries a password, a password hash, or a session
token. The one exception is :class:`LoginResponse`, which returns the session token
at the single moment it exists in clear — immediately after login. A password-reset
token has no such exception: it never appears in a response at all, because the
whole point of the reset is that only the account's verified address receives it.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, model_validator

from app.db.models import EMAIL_MAX_LENGTH

# Argon2 accepts arbitrarily long input, but an unbounded password field is a cheap
# way to make every login attempt expensive for the server.
PASSWORD_MAX_LENGTH = 1024

# A reset token is 32 URL-safe base64 bytes (43 characters). The bound is generous
# enough for a longer token later, and small enough that an oversized body is
# rejected before it reaches a database lookup.
RESET_TOKEN_MAX_LENGTH = 256


class RegisterRequest(BaseModel):
    """Account creation (FR-ACC-001)."""

    model_config = ConfigDict(extra="forbid")

    email: Annotated[EmailStr, Field(max_length=EMAIL_MAX_LENGTH)]
    # SecretStr keeps the value out of any accidental repr, log line, or traceback.
    password: SecretStr = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)

    @model_validator(mode="after")
    def _check_password_length(self) -> Self:
        """Length is checked here so the raw value never reaches a generic validator.

        The complexity policy lives in ``app.services.auth_service`` alongside the
        configured minimum; this only enforces the absolute bounds.
        """
        if len(self.password.get_secret_value()) > PASSWORD_MAX_LENGTH:
            msg = "password is too long"
            raise ValueError(msg)
        return self


class LoginRequest(BaseModel):
    """Credential presentation (FR-ACC-001)."""

    model_config = ConfigDict(extra="forbid")

    email: Annotated[EmailStr, Field(max_length=EMAIL_MAX_LENGTH)]
    password: SecretStr = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class UserResponse(BaseModel):
    """The account, as its owner may see it.

    Built explicitly rather than with ``from_attributes`` on the ORM row: an
    opt-out model would start returning ``password_hash`` the moment someone adds a
    field, and the safe direction here is to have to opt *in*.
    """

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """The only response that ever carries a session token."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    # S105 is suppressed because this is the OAuth 2.0 `token_type` field
    # (RFC 6749 5.1): its value is the literal scheme name, not a secret.
    token_type: Literal["bearer"] = "bearer"  # noqa: S105
    expires_at: datetime
    user: UserResponse


class SessionResponse(BaseModel):
    """One active session, for UC-003. Carries no token or digest."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    current: bool = Field(description="True for the session making this request.")


class SessionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessions: list[SessionResponse]


class RevocationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revoked: int = Field(description="How many sessions this call ended.")


class PasswordResetRequest(BaseModel):
    """Ask for a reset link (FR-ACC-005, UC-001 A2)."""

    model_config = ConfigDict(extra="forbid")

    email: Annotated[EmailStr, Field(max_length=EMAIL_MAX_LENGTH)]


class PasswordResetRequestResponse(BaseModel):
    """Deliberately uninformative.

    The same body is returned whether or not the address has an account, so an
    unauthenticated caller cannot use this endpoint to discover who holds a vault.
    """

    model_config = ConfigDict(extra="forbid")

    status: Literal["accepted"] = "accepted"
    detail: str = Field(
        default=("If that address has a DOCURA account, a reset link is on its way to it."),
        description="Identical for every request, by design.",
    )


class PasswordResetConfirmRequest(BaseModel):
    """Present the emailed token together with the replacement password."""

    model_config = ConfigDict(extra="forbid")

    # SecretStr for the same reason as a password: this token is a credential for
    # the account until it is spent, and must not surface in a repr or traceback.
    token: SecretStr = Field(min_length=1, max_length=RESET_TOKEN_MAX_LENGTH)
    password: SecretStr = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class PasswordResetConfirmResponse(BaseModel):
    """What the completed reset did — no token, no identifiers."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["reset"] = "reset"
    sessions_revoked: int = Field(
        description="Sessions ended by the password change. Sign in again to continue.",
    )
