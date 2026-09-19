"""Response models for the current-record retrieval boundary (Sprint 4, fifth milestone).

These are the stable shapes the future chatbot/voice and browser-extension clients read
after they have translated a request into a canonical identifier. They project the
derived view from :mod:`app.services.current_record` — a current value, its ambiguity
state, and the supporting observations with their provenance and confidence.

Two rules, as in the document schemas: a response *references* a document by id, it never
contains one — no file bytes and no storage key appear here (NFR-ERR-004, NFR-PRIV-007);
and the value is kept distinct from its supporting observations, so a future sensitivity
layer (G-14/G-15) can gate disclosure per attribute before any value is returned.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceRegionResponse(BaseModel):
    """The region of the source page a value was read from (FR-OCR-007).

    Page-relative fractions (0..1). Present only when the engine reported a region.
    """

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    width: float
    height: float


class SupportingObservationResponse(BaseModel):
    """One observation backing a value, with its provenance and confidence.

    The chain a client can follow: value → this observation → block/page → run →
    ``document_id``. ``document_id`` references the existing vault (``GET
    /documents/{id}`` / ``/content``); no document content is duplicated here.
    """

    model_config = ConfigDict(extra="forbid")

    value: str = Field(description="The value as read from this source; sources may differ.")
    confidence: float | None = Field(
        description="The confidence this value was read with, or null if the engine gave none."
    )
    document_id: uuid.UUID = Field(description="The supporting document, fetchable via the vault.")
    extraction_run_id: uuid.UUID
    page_number: int
    region: SourceRegionResponse | None


class AttributeValueResponse(BaseModel):
    """The current known value of one canonical attribute for the authenticated user.

    ``value`` is the current value when the supporting observations agree, and null when
    they genuinely disagree — in which case ``is_ambiguous`` is true and every candidate
    stays visible in ``observations``. No winner is chosen here (G-20 is unresolved).
    """

    model_config = ConfigDict(extra="forbid")

    canonical_identifier: str
    value: str | None = Field(
        description="The current value, or null when the supporting observations disagree.",
    )
    is_ambiguous: bool = Field(
        description="True when observations genuinely disagree and no value is selected.",
    )
    observations: list[SupportingObservationResponse]


class AttributeRecordResponse(BaseModel):
    """The user's whole current record — one entry per canonical attribute they have."""

    model_config = ConfigDict(extra="forbid")

    attributes: list[AttributeValueResponse]
    count: int


class ExportedDocument(BaseModel):
    """One document in the export — metadata only, never bytes or the storage key.

    The same fields the vault listing shows (FR-DOC-001), so the export is the user's own
    record of what they have stored, openable and self-describing.
    """

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    original_filename: str
    content_type: str
    byte_size: int
    checksum_sha256: str
    document_type: str
    status: str
    created_at: datetime


class RecordExportResponse(BaseModel):
    """The user's complete record export (FR-ACC-006): their documents and the extracted
    information, in one openable JSON document.

    It references documents by id and carries no file bytes, no storage key, and no secret
    (the same privacy rules as every other response here). Deterministically ordered — the
    attributes and documents come out in the same order the record and vault APIs return.
    """

    model_config = ConfigDict(extra="forbid")

    docura_export_version: str = "1"
    exported_at: datetime
    account_email: str
    documents: list[ExportedDocument]
    attributes: list[AttributeValueResponse]
    document_count: int
    attribute_count: int
