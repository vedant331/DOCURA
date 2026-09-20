"""Owner-scoped search over the user's own documents and current record (FR-SRCH, MVP subset).

It reuses the existing vault and current-record services — no new store, no ranking, no AI. It
searches what the user actually has:

* **documents** by filename (FR-SRCH-001, the practical "find a document"), and
* **record attributes** by canonical identifier and value, returning the supporting document and
  its page as the location (FR-SRCH-003, FR-SRCH-004).

Deliberately NOT implemented here (and reported honestly, never faked):

* **FR-SRCH-002** — searching the full *extracted text* of documents. There is no extracted text:
  the OCR engine is unconfigured (S-6), so documents carry no page text to search.
* **FR-SRCH-006** — natural-language query. FUTURE/WON'T.

Matching is a case-insensitive substring — deterministic and explainable, never fuzzy/semantic.
Isolation comes from the reused services, which filter by ``user_id`` in the query.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentType
from app.services.current_record import build_current_record
from app.services.document_service import list_documents


@dataclass(frozen=True, slots=True)
class DocumentMatch:
    id: uuid.UUID
    original_filename: str
    status: str


@dataclass(frozen=True, slots=True)
class AttributeMatch:
    canonical_identifier: str
    value: str | None
    is_ambiguous: bool
    # The supporting document and page, so the client can navigate to where the value came
    # from (FR-SRCH-004). None only when the attribute somehow has no observation.
    document_id: uuid.UUID | None
    page_number: int | None


@dataclass(frozen=True, slots=True)
class SearchResults:
    query: str
    documents: list[DocumentMatch]
    attributes: list[AttributeMatch]


def _passes_document_filters(
    doc: Document,
    *,
    document_type: DocumentType | None,
    added_after: date | None,
    added_before: date | None,
) -> bool:
    """FR-SRCH-005: keep a document only if it matches the type and date-added filters.

    Reuses the document's own metadata — its ``document_type`` and ``created_at`` ("date added")
    — with no new storage. Dates are compared on the calendar day, inclusive, so ``added_after``
    and ``added_before`` behave as a closed range. A filter left as ``None`` is not applied.
    """
    # Compare on the enum value (str): DocumentType currently has a single released member
    # (UNCLASSIFIED), so a direct enum `!=` is provably constant to the type checker; comparing
    # the string values keeps this correct and future-proof as the S-6 taxonomy adds members.
    if document_type is not None and doc.document_type.value != document_type.value:
        return False
    added = doc.created_at.date()
    if added_after is not None and added < added_after:
        return False
    return not (added_before is not None and added > added_before)


async def search(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    query: str = "",
    document_type: DocumentType | None = None,
    added_after: date | None = None,
    added_before: date | None = None,
) -> SearchResults:
    """Search the user's own documents and record (case-insensitive substring), optionally
    filtered by document type and date added (FR-SRCH-005).

    The filters narrow the results of ``query``. (An empty ``query`` matches everything at the
    service level; the HTTP API still requires a non-empty ``q``, preserving the existing
    contract.) Filters apply to document results and, so "filter results" stays consistent, to
    attribute results via their supporting document. Owner isolation is
    already enforced by ``list_documents`` (``WHERE user_id``); these are pure post-filters over
    that owner-scoped set, so they can never widen access to another account.
    """
    needle = query.strip().casefold()
    filtering = document_type is not None or added_after is not None or added_before is not None

    def passes(doc: Document) -> bool:
        return _passes_document_filters(
            doc,
            document_type=document_type,
            added_after=added_after,
            added_before=added_before,
        )

    docs = await list_documents(db, user_id=user_id)
    doc_by_id: dict[uuid.UUID, Document] = {d.id: d for d in docs}
    document_matches = [
        DocumentMatch(id=d.id, original_filename=d.original_filename, status=d.status.value)
        for d in docs
        if needle in d.original_filename.casefold() and passes(d)
    ]

    record = await build_current_record(db, user_id=user_id)
    attribute_matches: list[AttributeMatch] = []
    for attr in record:
        haystacks = [attr.canonical_identifier.casefold()]
        if attr.value:
            haystacks.append(attr.value.casefold())
        haystacks.extend(o.value.casefold() for o in attr.observations)
        if not any(needle in h for h in haystacks):
            continue
        first = attr.observations[0] if attr.observations else None
        supporting_id = first.source_block.page.run.document_id if first else None
        # When filtering, an attribute survives only if its supporting document matches the
        # filters. An attribute with no resolvable supporting document cannot be verified against
        # a document filter, so it is excluded while filtering (never guessed in).
        if filtering:
            supporting = doc_by_id.get(supporting_id) if supporting_id is not None else None
            if supporting is None or not passes(supporting):
                continue
        attribute_matches.append(
            AttributeMatch(
                canonical_identifier=attr.canonical_identifier,
                value=attr.value,
                is_ambiguous=attr.is_ambiguous,
                document_id=supporting_id,
                page_number=first.source_block.page.number if first else None,
            )
        )

    return SearchResults(
        query=query.strip(), documents=document_matches, attributes=attribute_matches
    )
