"""Structured attribute observations (Sprint 4, third milestone).

This is the layer between the persisted engine-neutral extraction result
(:mod:`app.services.extraction_store`) and the future retrieval / chat / extension
features. It is deliberately the *smallest* thing that can represent a candidate
canonical attribute value with provenance and confidence, and read those values back.

Three concerns are kept separate and are **not** collapsed here:

1. **extracted text observations** — :class:`~app.db.models.ExtractionBlock` and
   friends: units of *text*, not of meaning;
2. **structured attribute observations** — :class:`~app.db.models.AttributeObservation`:
   a value recognised *as* a canonical attribute, this module's subject;
3. **canonical attribute definitions** — the versioned vocabulary configuration
   (``config/vocabulary/…``): referenced by identifier only, never copied into a row.

What is deliberately absent, because each is a separate, still-open decision:

* the mapping rule that decides *which* block is *which* attribute (FR-OCR-004 /
  FR-INF, gap G-12): this module stores candidates a caller hands it and derives none;
* conflict / duplicate detection (FR-INF-004, NFR-REL-005, gap G-20): several
  observations of one attribute are stored side by side and never compared here;
* the sensitivity tier (FR-INF-007, gaps G-14/G-15): a property of the *definition*,
  not of an observed value.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AttributeObservation, ExtractionBlock, ExtractionRun


@dataclass(frozen=True, slots=True)
class CandidateObservation:
    """One value a future mapping step (G-12 / FR-INF) recognised as an attribute.

    It names the canonical attribute by its vocabulary *identifier* — the stable handle,
    not the definition — the value read, the block it was read from (its exact
    provenance), and the confidence the engine gave, or ``None`` where it gave none.
    This milestone builds no rule that produces these; it builds the layer that stores
    them, and the tests supply them directly to prove the model works.
    """

    canonical_identifier: str
    value: str
    source_block: ExtractionBlock
    confidence: float | None = None


def build_attribute_observations(
    *, run: ExtractionRun, candidates: Iterable[CandidateObservation]
) -> list[AttributeObservation]:
    """Construct structured observations for a *persisted* run. Pure — no session, no I/O.

    ``run`` and each candidate's ``source_block`` must already have ids (the caller has
    flushed the run's graph). Each observation records the run that produced it — its
    run identity, and its document through ``run.document_id`` — and the block it was
    read from; ``run_id`` equals that block's run because the caller supplies blocks
    from this run, so the two agree and no document metadata is copied onto the row.

    The caller owns the transaction. Building against a flushed-but-uncommitted run and
    committing once keeps a run and its observations atomic — true together or not at
    all — so a failed extraction (which persists no run) can persist no observation.
    """
    return [
        AttributeObservation(
            run_id=run.id,
            source_block_id=candidate.source_block.id,
            canonical_identifier=candidate.canonical_identifier,
            value=candidate.value,
            confidence=candidate.confidence,
        )
        for candidate in candidates
    ]


async def list_attribute_observations(
    db: AsyncSession, *, document_id: uuid.UUID
) -> list[AttributeObservation]:
    """Every structured observation for a document, across all runs — deterministic.

    Ordered by the producing run (oldest first), then observation id, so a given set of
    rows always comes back in the same sequence. Ownership is the caller's to enforce,
    as with :func:`app.services.extraction_store.list_extraction_runs`.
    """
    result = await db.scalars(
        select(AttributeObservation)
        .join(ExtractionRun, AttributeObservation.run_id == ExtractionRun.id)
        .where(ExtractionRun.document_id == document_id)
        .order_by(ExtractionRun.created_at, AttributeObservation.id)
    )
    return list(result)


async def list_current_attribute_observations(
    db: AsyncSession, *, document_id: uuid.UUID
) -> list[AttributeObservation]:
    """The newest run's observations only — the document's current structured state.

    "Current" is *derived*, never stored: there is no ``is_current`` flag. The newest
    run is the newest successful one (a failed attempt persists no run), so a reprocess
    supersedes the previous state simply by adding a newer run, while every earlier
    run's observations stay for history and provenance.
    """
    newest_run = (
        select(ExtractionRun.id)
        .where(ExtractionRun.document_id == document_id)
        .order_by(ExtractionRun.created_at.desc(), ExtractionRun.id.desc())
        .limit(1)
        .scalar_subquery()
    )
    result = await db.scalars(
        select(AttributeObservation)
        .where(AttributeObservation.run_id == newest_run)
        .order_by(AttributeObservation.id)
    )
    return list(result)
