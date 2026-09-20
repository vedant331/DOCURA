"""Search endpoint (FR-SRCH, MVP subset).

Authenticated and owner-scoped: identity comes from the session, so a caller can only search
their own documents and record. Delegates to :mod:`app.services.search`, which reuses the vault
and current-record services (both filter by ``user_id`` in the query).
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.db.models import DocumentType
from app.schemas.search import (
    AttributeMatchResponse,
    DocumentMatchResponse,
    SearchResponse,
)
from app.services.search import search as search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse, summary="Search your documents and record")
async def search(
    user: CurrentUser,
    db: DbSession,
    q: str = Query(min_length=1, max_length=200, description="The text to look for."),
    document_type: Annotated[
        DocumentType | None, Query(description="Filter to one document type (FR-SRCH-005).")
    ] = None,
    added_after: Annotated[
        date | None, Query(description="Only documents added on/after this date (YYYY-MM-DD).")
    ] = None,
    added_before: Annotated[
        date | None, Query(description="Only documents added on/before this date (YYYY-MM-DD).")
    ] = None,
) -> SearchResponse:
    """Find the caller's own documents (by filename) and record attributes (by id/value),
    optionally filtered by document type and date added (FR-SRCH-005).

    The optional ``document_type`` / ``added_after`` / ``added_before`` filters narrow the
    results of the text query. An invalid ``document_type`` or a malformed date is rejected by
    request validation (422) before any query runs. Attribute matches carry the supporting
    document and page so the client can
    navigate to the source (FR-SRCH-003/004). Full extracted-text search (FR-SRCH-002) is not
    offered: no OCR engine is configured, so there is no page text to search — never fabricated.
    """
    results = await search_service(
        db,
        user_id=user.id,
        query=q,
        document_type=document_type,
        added_after=added_after,
        added_before=added_before,
    )
    return SearchResponse(
        query=results.query,
        documents=[
            DocumentMatchResponse(id=d.id, original_filename=d.original_filename, status=d.status)
            for d in results.documents
        ],
        attributes=[
            AttributeMatchResponse(
                canonical_identifier=a.canonical_identifier,
                value=a.value,
                is_ambiguous=a.is_ambiguous,
                document_id=a.document_id,
                page_number=a.page_number,
            )
            for a in results.attributes
        ],
        document_count=len(results.documents),
        attribute_count=len(results.attributes),
    )
