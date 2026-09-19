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

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import FormActionOutcome, FormActionType, FormSessionState

# Action types a client (the extension) may record. The lifecycle transitions
# HAND_BACK and STOP are deliberately excluded: they have their own endpoints and move
# the session's state, so they are never posted as free history (that is the backend's
# to write). These are the in-session effects DOCURA performs on the page.
CLIENT_RECORDABLE_ACTIONS = frozenset(
    {
        FormActionType.FILL,
        FormActionType.SELECT,
        FormActionType.ATTACH,
        FormActionType.ASK,
        FormActionType.ANSWER,
        FormActionType.APPROVAL_REQUEST,
        FormActionType.APPROVAL_DECISION,
        FormActionType.OVERRIDE,
    }
)


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


class FormActionCreate(BaseModel):
    """One in-session action the extension asks the backend to record (FR-AUD-001…003).

    Carries a field *handle* and provenance *references* only — never a field value or
    any third-party form content (FR-AUD-006, BR-017, NFR-PRIV-007). ``detail`` is
    DOCURA's own short note (e.g. the canonical attribute filled), not the value placed.
    Referenced ids are validated owner-scoped by the service; a lifecycle transition
    (hand_back / stop) is rejected here — those have their own endpoints.
    """

    model_config = ConfigDict(extra="forbid")

    action_type: FormActionType
    outcome: FormActionOutcome
    field_ref: str | None = Field(
        default=None,
        max_length=300,
        description="The field's opaque handle on the page — never its value.",
    )
    document_id: uuid.UUID | None = Field(
        default=None,
        description="A supporting document this action used; must be owned by you.",
    )
    observation_id: uuid.UUID | None = Field(
        default=None,
        description="The source observation a filled value came from; must be owned by you.",
    )
    reverses_action_id: uuid.UUID | None = Field(
        default=None,
        description="An earlier action in THIS session that this one corrects/reverses.",
    )
    detail: str | None = Field(
        default=None,
        max_length=500,
        description="DOCURA's own note (e.g. the canonical attribute id) — never the field value.",
    )

    @field_validator("action_type")
    @classmethod
    def _only_client_recordable(cls, value: FormActionType) -> FormActionType:
        if value not in CLIENT_RECORDABLE_ACTIONS:
            allowed = ", ".join(sorted(a.value for a in CLIENT_RECORDABLE_ACTIONS))
            msg = (
                f"action_type must be one of: {allowed} "
                "(lifecycle transitions have their own endpoints)"
            )
            raise ValueError(msg)
        return value


class FormActionListResponse(BaseModel):
    """A session's history, in the order it happened (FR-AUD-004)."""

    model_config = ConfigDict(extra="forbid")

    actions: list[FormActionResponse]
    count: int
