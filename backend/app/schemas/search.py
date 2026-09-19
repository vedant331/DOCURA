"""Response models for owner-scoped search (FR-SRCH, MVP subset).

References a document by id and carries no file bytes, storage key, or secret — the same
privacy rule as the record and vault schemas.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class DocumentMatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    original_filename: str
    status: str


class AttributeMatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_identifier: str
    value: str | None
    is_ambiguous: bool
    document_id: uuid.UUID | None
    page_number: int | None


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    documents: list[DocumentMatchResponse]
    attributes: list[AttributeMatchResponse]
    document_count: int
    attribute_count: int
