"""Data model: accounts, sessions, reset tokens, and the document vault.

Sprint 2 added what FR-ACC-001/002/003/005/008 and NFR-SEC-004/005 require. Sprint 3
adds :class:`Document`, the vault's metadata table.

What is deliberately *absent* from :class:`Document` says as much as what is present.
There is no extracted text, no classification confidence, no per-field value and no
attribute table: OCR and document understanding are FR-OCR and FR-INF, a later
sprint, and modelling their output before the extractor exists would fix a shape
around requirements whose thresholds are still TBD. The profile of FR-ACC-004 is
likewise still unmodelled, because its "canonical personal attributes" are derived
from extraction rather than from upload.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Longest address RFC 5321 permits.
EMAIL_MAX_LENGTH = 254

# A filename is display metadata, never a path. 255 is the ceiling on every
# filesystem DOCURA is likely to meet, so it is the ceiling here too.
FILENAME_MAX_LENGTH = 255
# "ab/cd/" plus 32 hex characters, per app.services.storage.
STORAGE_KEY_MAX_LENGTH = 64
# Long enough for the parameterised media types the accepted set could grow into.
CONTENT_TYPE_MAX_LENGTH = 128
# Hex SHA-256.
CHECKSUM_LENGTH = 64


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
    documents: Mapped[list[Document]] = relationship(
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


class DocumentStatus(enum.StrEnum):
    """Per-document processing status (FR-UPL-005).

    Exactly the five states the requirement names — no more were invented, and none
    were dropped. Sprint 3 stores documents and only ever sets ``QUEUED``: the
    transitions out of it belong to the extraction pipeline (FR-OCR-001 to 009),
    which is a later sprint. A document sitting at ``QUEUED`` is therefore an honest
    statement of where the system is, not a stalled job.
    """

    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class DocumentType(enum.StrEnum):
    """The document's kind (FR-DOC-002).

    Only ``UNCLASSIFIED`` exists yet, and that is deliberate. FR-DOC-002 says the
    type is "assigned automatically", which is the classifier's job (FR-OCR-002);
    Step 3 section 7.1 already provides for a document held with no type - "Other,
    stored and searchable as an unclassified document". Enumerating Aadhaar,
    marksheet and the rest now would be writing down a taxonomy this sprint cannot
    assign and that study S-6 may still change.
    """

    UNCLASSIFIED = "unclassified"


class Document(Base):
    """One stored original, owned by exactly one account (FR-ACC-003, NFR-SEC-003).

    ``user_id`` is the whole of the vault's isolation, and it is applied in the
    ``WHERE`` clause of every query rather than checked after a row is loaded - see
    :mod:`app.services.document_service`. The requirement is stronger than "check
    permissions": NFR-SEC-003 forbids ownership being inferred from an identifier
    the client supplied, so the id in the URL only ever narrows a set that has
    already been restricted to the authenticated account.
    """

    __tablename__ = "documents"

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

    # As the user named it, sanitised for display and for Content-Disposition. It is
    # never joined to a path: the bytes are found by `storage_key` alone.
    original_filename: Mapped[str] = mapped_column(String(FILENAME_MAX_LENGTH), nullable=False)
    # Opaque object identifier minted from the CSPRNG. Not returned by any endpoint:
    # it describes where DOCURA keeps the file, which is nobody else's business.
    storage_key: Mapped[str] = mapped_column(String(STORAGE_KEY_MAX_LENGTH), nullable=False)
    content_type: Mapped[str] = mapped_column(String(CONTENT_TYPE_MAX_LENGTH), nullable=False)
    # BigInteger rather than Integer: the column should not be the thing that has to
    # change if the configured size ceiling is ever raised past 2 GiB.
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # SHA-256 of the stored bytes. Two jobs: it detects a re-upload of the identical
    # file (FR-UPL-007, NFR-REL-005), and it is the integrity reference that shows a
    # stored original still matches what was uploaded (BR-013).
    checksum_sha256: Mapped[str] = mapped_column(String(CHECKSUM_LENGTH), nullable=False)

    # `values_callable` makes PostgreSQL store the enum's *values* rather than its
    # member names. Without it the column would hold "NEEDS_REVIEW" while the API
    # returned "needs_review", and anyone reading the table directly would see a
    # vocabulary that appears nowhere in the requirements.
    document_type: Mapped[DocumentType] = mapped_column(
        SqlEnum(
            DocumentType,
            name="document_type",
            native_enum=True,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=DocumentType.UNCLASSIFIED,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SqlEnum(
            DocumentStatus,
            name="document_status",
            native_enum=True,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=DocumentStatus.QUEUED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="documents")

    __table_args__ = (
        # Newest first is the only order the vault listing uses (FR-DOC-001).
        Index("ix_documents_user_id_created_at", "user_id", "created_at"),
        # "No silent duplicate is created" (AC-US-002-4) is enforced by the database,
        # not by a read-then-write check that two concurrent uploads would race past
        # - the same reasoning as the unique index on users.email. Scoped to the
        # owner: two accounts storing the same public form is not a collision.
        Index(
            "ix_documents_user_id_checksum_unique",
            "user_id",
            "checksum_sha256",
            unique=True,
        ),
        Index("ix_documents_storage_key_unique", "storage_key", unique=True),
    )
