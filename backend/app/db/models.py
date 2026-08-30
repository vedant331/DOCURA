"""Sprint 2 data model: accounts, sessions, and password-reset tokens.

Only what FR-ACC-001/002/003/005/008 and NFR-SEC-004/005 require exists here. There is
no document, extraction, or form-session table — those belong to later sprints, and
FR-ACC-004's "canonical personal attributes" are *derived from documents*, so the
profile cannot be modelled before documents are.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Longest address RFC 5321 permits.
EMAIL_MAX_LENGTH = 254


class Base(DeclarativeBase):
    """Declarative base for every DOCURA table."""


class User(Base):
    """One account, owning exactly one record (FR-ACC-003, BR-018)."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Stored lowercased and stripped so that uniqueness is not defeated by case.
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), nullable=False)
    # Argon2id encoded hash. The plaintext password is never persisted or returned.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    sessions: Mapped[list[Session]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    password_reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Uniqueness is enforced by the database, not by a read-then-write check in
        # application code, which two concurrent registrations would race past.
        Index("ix_users_email_unique", "email", unique=True),
    )


class Session(Base):
    """An authenticated session (NFR-SEC-005, FR-ACC-008).

    Server-side state is what makes a session *revocable*: UC-003 requires signing
    out of active sessions and EC-016 requires a revoked session to stop automated
    action immediately. A self-contained token would stay valid until it expired.
    """

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    # SHA-256 of the token. The token itself is returned once, at login, and never
    # stored — a database leak therefore yields nothing that can be replayed.
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # Sliding inactivity deadline (NFR-SEC-005).
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Hard ceiling, so an active session cannot be extended indefinitely.
    absolute_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")

    __table_args__ = (
        Index("ix_sessions_token_hash_unique", "token_hash", unique=True),
        Index("ix_sessions_user_id", "user_id"),
    )


class PasswordResetToken(Base):
    """A single-use credential for the verified reset process (FR-ACC-005, UC-001 A2).

    Server-side, like a session: a reset must be revocable the instant it is used or
    superseded, and "the reset must not weaken the vault" — so the token is
    single-use, short-lived, and stored only as a digest.
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    # SHA-256 of the token, for the same reason as Session.token_hash: a database
    # leak must not yield anything that can be presented to the confirm endpoint.
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Set when the token is spent or superseded. A token is usable exactly once.
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="password_reset_tokens")

    __table_args__ = (
        Index("ix_password_reset_tokens_token_hash_unique", "token_hash", unique=True),
        Index("ix_password_reset_tokens_user_id", "user_id"),
    )
