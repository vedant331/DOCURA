"""Response models for the document vault.

One rule governs every model here: a response describes a document, it never
contains one, and it never says where DOCURA keeps it. ``storage_key`` is absent
from all of them by construction rather than by an ``exclude`` list that a later
edit could undo — the fields are written out one by one, and the storage key is not
among them (NFR-ERR-004, NFR-PRIV-007).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    """One document, as its owner may see it.

    The fields are exactly what FR-DOC-001 asks a vault listing to show — type, date
    added, processing status — plus the identity and size a client needs to render
    and fetch it. ``checksum_sha256`` is included because it is the user's own
    integrity reference for their original (BR-013); it discloses nothing about
    another account, since it can only be seen by the owner of the file it hashes.
    """

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    original_filename: str
    content_type: str
    byte_size: int
    checksum_sha256: str
    document_type: DocumentType
    status: DocumentStatus = Field(
        description="Processing status (FR-UPL-005).",
    )
    failure_reason: str | None = Field(
        default=None,
        description=(
            "When status is 'failed', a plain-language statement of what went wrong "
            "(FR-OCR-009). Null otherwise. The original file is retained regardless."
        ),
    )
    created_at: datetime
    updated_at: datetime


class RejectedUpload(BaseModel):
    """One file in a batch that was not accepted.

    NFR-ERR-003 requires partial success to be reported as partial and itemised, so
    a rejection carries the same two things a whole-request error does: what went
    wrong, and what to do about it (NFR-ERR-001).
    """

    model_config = ConfigDict(extra="forbid")

    filename: str = Field(description="The name as sent, after sanitisation.")
    reason: str
    remediation: str


class UploadResponse(BaseModel):
    """The outcome of one upload request (FR-UPL-002, NFR-ERR-003).

    Both lists are always present. A batch where every file was accepted still
    reports an empty ``rejected``, so a client reads one shape rather than guessing
    from the status code which fields exist.
    """

    model_config = ConfigDict(extra="forbid")

    accepted: list[DocumentResponse]
    rejected: list[RejectedUpload]


class DocumentListResponse(BaseModel):
    """The account's vault (FR-DOC-001). Metadata only — never file contents."""

    model_config = ConfigDict(extra="forbid")

    documents: list[DocumentResponse]
    count: int


class DocumentDeletionResponse(BaseModel):
    """Confirmation naming what was destroyed (FR-DOC-007).

    The requirement asks for a confirmation that names what is lost. The interface
    asks before; this is what the API says after, so the user has a record of the
    specific document that went rather than a bare 204.
    """

    model_config = ConfigDict(extra="forbid")

    deleted: bool = True
    id: uuid.UUID
    original_filename: str
    content_type: str
    byte_size: int
    detail: str = Field(
        description="Plain-language statement of what was removed and what was not.",
    )


class UploadLimits(BaseModel):
    """The limits, stated in advance (FR-UPL-003).

    This exists because the requirement says the limits must be stated *before* a
    file is chosen, not discovered by having one rejected. It is read by anything
    that renders a file picker.
    """

    model_config = ConfigDict(extra="forbid")

    accepted_media_types: list[str]
    accepted_extensions: list[str]
    max_document_bytes: int
    max_documents_per_upload: int
