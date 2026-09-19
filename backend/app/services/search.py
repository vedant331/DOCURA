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

from sqlalchemy.ext.asyncio import AsyncSession

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


async def search(db: AsyncSession, *, user_id: uuid.UUID, query: str) -> SearchResults:
    """Search the user's own documents and record for ``query`` (case-insensitive substring)."""
    needle = query.strip().casefold()

    docs = await list_documents(db, user_id=user_id)
    document_matches = [
        DocumentMatch(id=d.id, original_filename=d.original_filename, status=d.status.value)
        for d in docs
        if needle in d.original_filename.casefold()
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
        attribute_matches.append(
            AttributeMatch(
                canonical_identifier=attr.canonical_identifier,
                value=attr.value,
                is_ambiguous=attr.is_ambiguous,
                document_id=first.source_block.page.run.document_id if first else None,
                page_number=first.source_block.page.number if first else None,
            )
        )

    return SearchResults(
        query=query.strip(), documents=document_matches, attributes=attribute_matches
    )
