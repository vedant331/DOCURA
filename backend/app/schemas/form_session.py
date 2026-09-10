"""Response models for the form-session and audit boundary (M1).

The shapes the future browser extension reads for a session's lifecycle and history.
Two rules, as in the document and record schemas: a response *references* provenance
by id and never contains file bytes, a storage key, or a checksum (NFR-ERR-004,
NFR-PRIV-007); and it carries no third-party form content (FR-AUD-006, BR-017) — only
the field DOCURA touched, what it did, and how it ended.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import FormActionOutcome, FormActionType, FormSessionState


class FormSessionResponse(BaseModel):
    """One form session's identity and lifecycle."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    state: FormSessionState = Field(description="active, handed_back, stopped, or expired.")
    created_at: datetime = Field(description="When the user activated DOCURA on the form.")
    ended_at: datetime | None = Field(
        description="When the session left the active state, or null while it is live.",
    )


class FormSessionListResponse(BaseModel):
    """This account's form sessions, newest first."""

    model_config = ConfigDict(extra="forbid")

    sessions: list[FormSessionResponse]
    count: int


class FormActionResponse(BaseModel):
    """One append-only history entry — what DOCURA did and the field it affected.

    ``field_ref`` is the field's handle, never its value; provenance is referenced by
    id (``document_id``, ``observation_id``), fetchable through the vault and record
    APIs. No file content appears here.
    """

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    action_type: FormActionType
    outcome: FormActionOutcome
    field_ref: str | None
    document_id: uuid.UUID | None = Field(
        description="The supporting document, fetchable via the vault; null if none.",
    )
    observation_id: uuid.UUID | None
    reverses_action_id: uuid.UUID | None = Field(
        description="The earlier action this one reverses or corrects; null for an original.",
    )
    detail: str | None = Field(
        description="DOCURA's own note or the user's own answer; never form content.",
    )
    created_at: datetime


class FormActionListResponse(BaseModel):
    """A session's history, in the order it happened (FR-AUD-004)."""

    model_config = ConfigDict(extra="forbid")

    actions: list[FormActionResponse]
    count: int
