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

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
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
# A user-facing sentence stating what failed (FR-OCR-009). It holds a DocuraError's
# already-safe `detail`, never an internal trace or engine message (NFR-ERR-004).
FAILURE_REASON_MAX_LENGTH = 500
# The internal error a worker records for operators — a class name and message. Kept
# on the job, never returned to a user.
JOB_ERROR_MAX_LENGTH = 500


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
    form_sessions: Mapped[list[FormSession]] = relationship(
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
    # Set when `status` is FAILED (FR-OCR-009: "state what failed"). Null otherwise,
    # and cleared when the document is re-queued. It is a user-facing string — the
    # safe `detail` of the failure — so the internal cause stays on the job.
    failure_reason: Mapped[str | None] = mapped_column(
        String(FAILURE_REASON_MAX_LENGTH), nullable=True
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
    # Exactly one job per document (NFR-REL-005): the row is created with the
    # document and removed with it. `delete-orphan` keeps the ORM consistent with the
    # database's ON DELETE CASCADE.
    processing_job: Mapped[ProcessingJob | None] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # Every successful extraction of this document, newest last. Retained rather than
    # overwritten: a reprocess adds a run, so the history of what each engine version
    # read stays inspectable (the reason ExtractionResult carries its engine version).
    extraction_runs: Mapped[list[ExtractionRun]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ExtractionRun.created_at",
    )

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


class JobState(enum.StrEnum):
    """The processing job's own state (Sprint 4 decision D-09).

    Deliberately *not* the same enum as :class:`DocumentStatus`. FR-UPL-005 names the
    five states a user sees; a job additionally carries claim, attempt, and error
    machinery a user must never see (NFR-ERR-004). The document's status is derived
    from the job's outcome, so the two stay independent — the discipline D-09.3 asks
    for and that Sprint 3 already applied to ``DocumentStatus``.
    """

    PENDING = "pending"
    CLAIMED = "claimed"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ProcessingJob(Base):
    """One durable unit of extraction work for one document (D-09 Option B).

    The job is a committed database row, created in the same transaction as its
    document (a document can never exist without its job), and it is what makes
    interrupted processing recoverable (NFR-REL-002): a worker that dies leaves a
    claim that goes stale and is picked up again. There is exactly one job per
    document (NFR-REL-005) — enforced by the unique index below — so redelivery or a
    reprocess request resets this row rather than creating a second.
    """

    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    state: Mapped[JobState] = mapped_column(
        SqlEnum(
            JobState,
            name="job_state",
            native_enum=True,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=JobState.PENDING,
    )
    # How many times execution has been attempted. Incremented when the job is
    # claimed, so a crash between claim and outcome still counts — an unbounded loop
    # on a poison document is what the ceiling below prevents.
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # The retry ceiling, captured at creation from configuration so that changing the
    # setting does not silently re-open jobs that already exhausted the old limit.
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    # When a worker claimed this job. A claim older than the configured timeout is
    # treated as abandoned and may be reclaimed (NFR-REL-002 recoverability).
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Operator-facing cause of the last failure (a class name and message). Never
    # returned to a user — that is what documents.failure_reason is for (NFR-ERR-004).
    last_error: Mapped[str | None] = mapped_column(String(JOB_ERROR_MAX_LENGTH), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    document: Mapped[Document] = relationship(back_populates="processing_job")

    __table_args__ = (
        # One job per document (NFR-REL-005). The unique constraint is what actually
        # guarantees it; the service resets the existing row rather than inserting.
        Index("ix_processing_jobs_document_id_unique", "document_id", unique=True),
        # The claim query scans by state and age; this index keeps it off a table
        # scan as the vault grows.
        Index("ix_processing_jobs_state_created_at", "state", "created_at"),
    )


class ExtractionRun(Base):
    """One successful, engine-neutral reading of a document (FR-OCR-001, D-01/D-09).

    This is the persisted form of :class:`~app.services.extraction.ExtractionResult`:
    it exists only when an engine produced a whole result, so a failed attempt leaves
    no run at all (the failure lives on the :class:`ProcessingJob`). A document may
    accumulate several runs — one per successful (re)processing — and they are kept,
    not overwritten, so a value can later be traced to the exact engine version that
    read it (AR-AST-008 evaluation, D-02 L4/L5).

    It holds only what the seam already represents. There is deliberately **no field,
    attribute, or classification here**: mapping this text to the defined field set is
    FR-OCR-004 / FR-INF (gap G-12), and it will *reference* these rows rather than
    replace them.
    """

    __tablename__ = "extraction_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Which component produced this run, recorded on the run rather than in
    # configuration: a result calibrated against one engine version is not evidence
    # for another (ExtractionResult carries these for the same reason).
    engine: Mapped[str] = mapped_column(String(100), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    document: Mapped[Document] = relationship(back_populates="extraction_runs")
    pages: Mapped[list[ExtractionPage]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ExtractionPage.number",
    )
    # The engine-neutral facts about the run (timings, settings, page counts). Never
    # document content and never an extracted personal value (NFR-PRIV-007) — the
    # seam guarantees that, and this stores only what it hands over.
    run_metadata: Mapped[list[ExtractionRunMetadata]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # The structured attribute values recognised in this run. Kept with the run, so a
    # reprocess adds a newer run's observations without disturbing this one's, and the
    # "current" state is the newest run's — no `is_current` flag is stored.
    attribute_observations: Mapped[list[AttributeObservation]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        # History for one document, in order.
        Index("ix_extraction_runs_document_id_created_at", "document_id", "created_at"),
    )


class ExtractionRunMetadata(Base):
    """One engine-neutral fact about a run — a key and a value (the seam's mapping).

    A relational key/value pair rather than a JSON blob: the mapping is genuinely
    open-ended, so this is its normal relational form, and it stays queryable.
    """

    __tablename__ = "extraction_run_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("extraction_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    run: Mapped[ExtractionRun] = relationship(back_populates="run_metadata")

    __table_args__ = (
        # One value per key per run.
        Index("ix_extraction_run_metadata_run_id_key_unique", "run_id", "key", unique=True),
    )


class ExtractionPage(Base):
    """One page of a run (FR-OCR-008: multi-page documents stay one document)."""

    __tablename__ = "extraction_pages"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("extraction_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    # 1-based, as the seam numbers pages.
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # The page-level confidence, or NULL where the engine reported none — a distinct
    # fact from a low confidence, kept distinguishable (FR-OCR-005, AR-AST-001).
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    run: Mapped[ExtractionRun] = relationship(back_populates="pages")
    blocks: Mapped[list[ExtractionBlock]] = relationship(
        back_populates="page",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ExtractionBlock.sequence",
    )

    __table_args__ = (
        Index("ix_extraction_pages_run_id_number_unique", "run_id", "number", unique=True),
    )


class ExtractionBlock(Base):
    """A run of text an engine read, with where it came from and how sure it was.

    A block is a unit of *text*, not a unit of *meaning* (mirroring TextBlock): it is
    deliberately not a field. Its region — the fractional box on the page (FR-OCR-007
    provenance) — is stored inline because it is one-to-one with the block and small;
    the region's page number is not stored, as it equals this block's page by
    construction. All four coordinates are present together or all NULL.
    """

    __tablename__ = "extraction_blocks"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("extraction_pages.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Order within the page: the seam hands blocks over as an ordered tuple, and this
    # preserves that order across the round trip.
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Page-relative fractions (0..1), or all NULL when the engine gave no region.
    region_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    region_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    region_width: Mapped[float | None] = mapped_column(Float, nullable=True)
    region_height: Mapped[float | None] = mapped_column(Float, nullable=True)

    page: Mapped[ExtractionPage] = relationship(back_populates="blocks")

    __table_args__ = (
        Index("ix_extraction_blocks_page_id_sequence_unique", "page_id", "sequence", unique=True),
    )


class AttributeObservation(Base):
    """A value read for a canonical attribute, with where it came from (Sprint 4, D-05).

    This is the third and distinct layer of the extraction model, and it must not be
    collapsed into the other two: an :class:`ExtractionBlock` is a unit of *text*; the
    canonical vocabulary (``config/vocabulary/…``) is the *definition* of an attribute;
    an ``AttributeObservation`` is one *value*, read from a block, recognised **as** a
    named attribute. It is what FR-INF-002's "every attribute value shall reference the
    document it came from and the confidence with which it was read" attaches to.

    It stores only the canonical attribute's **identifier** (``person.full_name``), not
    its definition: the vocabulary is versioned configuration and stays the one place a
    definition lives (G-13). Nothing here is a sensitivity tier (FR-INF-007, gaps
    G-14/G-15 — a property of the *definition*, not of a value), a conflict/duplicate
    decision (FR-INF-004, NFR-REL-005, gap G-20 — several observations of one attribute
    sit here side by side, uncompared), or any file metadata (that lives on
    :class:`Document`, reached through ``run.document_id`` and never copied).

    **Provenance is exact**: ``source_block`` → its page → ``run`` → ``run.document``.
    **History is by run**: the observation is owned by the run that produced it, kept
    when a later run supersedes it, so "current" is the newest run's observations and
    needs no stored flag. ``run_id`` equals ``source_block``'s run by construction — an
    observation is built from a block of the run that produced it.
    """

    __tablename__ = "attribute_observations"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # The run that produced this observation — its run identity, and (through
    # `run.document_id`) its document. Owned by the run: a reprocess adds a newer run's
    # observations and this row stays, which is what makes "current = newest run" work.
    run_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("extraction_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    # The exact block the value was read from (FR-OCR-007 / BR-010 attributability).
    # Page and region are reached through it; its run equals `run_id` by construction.
    source_block_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("extraction_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )
    # The canonical attribute's stable identifier, from the versioned vocabulary. Only
    # the handle is stored; the definition it names is not copied onto the row (G-13).
    canonical_identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    # The value as recognised for the attribute. Text, because a value is not sized in
    # advance and the vocabulary's data type is not enumerated here.
    value: Mapped[str] = mapped_column(Text, nullable=False)
    # The confidence the value was read with, or NULL where the engine reported none —
    # a distinct fact from a low confidence, kept distinguishable (FR-OCR-005).
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    run: Mapped[ExtractionRun] = relationship(back_populates="attribute_observations")
    source_block: Mapped[ExtractionBlock] = relationship()

    __table_args__ = (
        # Retrieval and the "newest run" currency query both filter by run.
        Index("ix_attribute_observations_run_id", "run_id"),
    )


# A form field's stable handle or label — the field DOCURA touched, never its value
# (FR-AUD-006 records the fields affected, not the third-party form's contents).
FIELD_REF_MAX_LENGTH = 200
# DOCURA's own short description of an action, or the user's own answer to an
# ambiguity (FR-AUD-002). Never third-party form content (FR-AUD-006, BR-017).
ACTION_DETAIL_MAX_LENGTH = 500


class FormSessionState(enum.StrEnum):
    """The lifecycle of one authenticated form session (M1, step3.pdf §1.7-1.20).

    A form session exists only after the user *explicitly activates* DOCURA on an
    open form (FR-INT-001, BR-014): there is no passive or pre-activation state to
    model, so creation is activation and ``created_at`` records it. From ``ACTIVE`` it
    reaches exactly one terminal state, each named by a requirement:

    * ``HANDED_BACK`` — review finished and control returned to the user; DOCURA
      records reaching this point and makes no claim about whether the user submitted
      (FR-SUB-003/004, D14).
    * ``STOPPED`` — the user stopped DOCURA, signed out, or uninstalled, or the form
      was submitted while DOCURA was mid-action (FR-EXT-006, EC-017, EC-018, US-016).
    * ``EXPIRED`` — the authenticating session expired mid-form, so automated action
      halts until re-authentication (EC-016, NFR-SEC-005).

    A transient *degraded* connection (EC-014, NFR-REL-003) is **not** a lifecycle
    state: the session stays ``ACTIVE`` and the failure is recorded as a
    :class:`FormAction` with ``outcome = FAILED`` — never as a success (BR-016).
    """

    ACTIVE = "active"
    HANDED_BACK = "handed_back"
    STOPPED = "stopped"
    EXPIRED = "expired"


class FormActionType(enum.StrEnum):
    """What DOCURA attempted or did during a form session (FR-AUD-001/002/003).

    The vocabulary of the append-only history, enumerated from the requirements that
    define it — the same discipline :class:`DocumentStatus` uses (all five FR-UPL-005
    states named though Sprint 3 only sets one). M1 *writes* only ``HAND_BACK`` and
    ``STOP``, through the session lifecycle endpoints; the rest are the categories the
    fill/select/attach/ask/approval milestones will record through
    :func:`app.services.form_session.record_action`, and are listed here so those
    milestones append a row rather than alter this type.

    No value implies DOCURA acts on its own: every fill, selection, and attachment is
    an action the user activated (BR-014) and can reverse (BR-015); DOCURA never
    submits (BR-008) and never accepts a declaration or consent (BR-006).
    """

    # Written by M1 (the session lifecycle):
    HAND_BACK = "hand_back"  # FR-SUB-004: session reached hand-back
    STOP = "stop"  # FR-EXT-006: user stopped DOCURA
    # Reserved for later milestones (the form-action pipeline):
    FILL = "fill"  # FR-AUD-001, FR-FILL: a value placed in a field
    SELECT = "select"  # FR-AUD-001, FR-DRP: an option selected
    ATTACH = "attach"  # FR-AUD-001, FR-MATCH: a document attached
    ASK = "ask"  # FR-AUD-002, FR-AMB: a question asked
    ANSWER = "answer"  # FR-AUD-002, FR-AMB-006: an answer the user gave
    APPROVAL_REQUEST = "approval_request"  # FR-AUD-003, FR-APR-001
    APPROVAL_DECISION = "approval_decision"  # FR-AUD-003, FR-APR-002
    OVERRIDE = "override"  # FR-FILL-006, EC-013: the user changed a filled value


class FormActionOutcome(enum.StrEnum):
    """How an action ended — generic and small, so success is never assumed.

    Three outcomes, and deliberately no approval-specific ones (approve/deny is the
    *content* of an ``APPROVAL_DECISION``, recorded in ``detail``, not an outcome the
    audit layer must define before approval exists — M1 invents no approval semantics):

    * ``SUCCEEDED`` — the action was performed (a value placed, the hand-back made).
    * ``FAILED`` — the attempt did not complete: a component failed, or the connection
      degraded (BR-016, EC-014). Recorded as a failure, never dressed up as success.
    * ``SKIPPED`` — DOCURA deliberately left the field untouched (an unknown field,
      BR-009; a skipped ambiguity, FR-AMB-004; a denied disclosure, FR-APR-003).
    """

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


def _form_enum(enum_cls: type[enum.StrEnum], name: str) -> SqlEnum:
    """A native PostgreSQL enum that stores the members' *values*, like the others.

    ``values_callable`` keeps "hand_back" in the column rather than "HAND_BACK", so a
    reader of the table sees the vocabulary the requirements use — the same reason the
    document and job enums do it.
    """
    return SqlEnum(
        enum_cls,
        name=name,
        native_enum=True,
        validate_strings=True,
        values_callable=lambda cls: [member.value for member in cls],
    )


class FormSession(Base):
    """One authenticated user's session on one form (M1 — the form-action foundation).

    This is the infrastructure the future browser extension and form-action pipeline
    hang from. It is deliberately *not* a workflow engine: a row, a lifecycle state,
    and a start/end time, owned by exactly one account. ``user_id`` is the whole of
    its isolation and is applied in the ``WHERE`` clause of every query
    (:mod:`app.services.form_session`, NFR-SEC-003), never checked after a global load.

    What is **absent** is as deliberate as what is present. There is no stored form
    URL, page origin, or third-party form content: no MVP requirement needs one, and
    BR-017/FR-AUD-006 keep third-party context out. A session is identified by its own
    id; the extension holds which tab it belongs to. Naming and revisiting an
    application context across sessions is FR-INT-004, FUTURE WON'T, so it is unmodelled.
    """

    __tablename__ = "form_sessions"

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
    state: Mapped[FormSessionState] = mapped_column(
        _form_enum(FormSessionState, "form_session_state"),
        nullable=False,
        default=FormSessionState.ACTIVE,
    )

    # Creation *is* activation (FR-INT-001, BR-014): a session exists only after the
    # user explicitly activated DOCURA, so no separate ``activated_at`` is stored.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # Set once, when the session leaves ACTIVE for any terminal state. ``state`` says
    # which terminal state; this says when. Null while the session is live.
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="form_sessions")
    actions: Mapped[list[FormAction]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="FormAction.created_at",
    )

    __table_args__ = (
        # The listing is per-account, newest first (like the vault listing).
        Index("ix_form_sessions_user_id_created_at", "user_id", "created_at"),
    )


class FormAction(Base):
    """One append-only entry in a form session's history (FR-AUD-001…006).

    History entries are never edited; a correction or reversal is a *new* row that
    points back at the one it supersedes (FR-AUD-005, BR-015) — the whole of the
    reversibility model, and not an event-sourcing framework. The service only ever
    inserts; nothing updates or deletes a row (a deleted account cascades the lot).

    It records what DOCURA did and the field it affected, and references provenance by
    id rather than copying it (BR-010, FR-INF-002, item 8): the source ``document`` and
    ``observation`` (value + confidence live on the observation) are foreign keys, not
    duplicated bytes, storage keys, checksums, or extracted values. It stores **no**
    third-party form content (FR-AUD-006, BR-017): ``field_ref`` is a field's handle,
    ``detail`` is DOCURA's own words or the user's own answer, and both are bounded.
    """

    __tablename__ = "form_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("form_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    action_type: Mapped[FormActionType] = mapped_column(
        _form_enum(FormActionType, "form_action_type"), nullable=False
    )
    outcome: Mapped[FormActionOutcome] = mapped_column(
        _form_enum(FormActionOutcome, "form_action_outcome"), nullable=False
    )

    # The form field DOCURA touched — its stable handle or label, never its value
    # (FR-AUD-006). Null for actions not tied to a single field (a hand-back, a stop).
    field_ref: Mapped[str | None] = mapped_column(String(FIELD_REF_MAX_LENGTH), nullable=True)
    # Provenance, referenced by id (BR-010). SET NULL rather than CASCADE: deleting a
    # document (BR-018) must not erase the history of what DOCURA did with it — the
    # entry survives with the link cleared.
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_observation_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("attribute_observations.id", ondelete="SET NULL"),
        nullable=True,
    )
    # The earlier action this one reverses or corrects (FR-AUD-005, BR-015). Null for
    # an original action. Same session, so it cascades with it.
    reverses_action_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("form_actions.id", ondelete="CASCADE"),
        nullable=True,
    )
    # DOCURA's own short description, or the user's own answer to an ambiguity
    # (FR-AUD-002). Never third-party form content (FR-AUD-006, BR-017).
    detail: Mapped[str | None] = mapped_column(String(ACTION_DETAIL_MAX_LENGTH), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped[FormSession] = relationship(back_populates="actions")

    __table_args__ = (
        # Viewing a session's history in order (FR-AUD-004) filters by session, by time.
        Index("ix_form_actions_session_id_created_at", "session_id", "created_at"),
    )
