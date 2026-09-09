"""Persisting an engine-neutral extraction result (Sprint 4, second milestone).

The pipeline hands over an :class:`~app.services.extraction.ExtractionResult` — the
same shape whatever engine produced it — and this turns it into the relational graph
in :mod:`app.db.models` (:class:`ExtractionRun` and its pages, blocks, and metadata).

Two boundaries are kept deliberately clean:

* This builds the ORM objects and returns the root; it does **not** commit. The
  caller owns the transaction, so a run is persisted in the same commit as the
  document reaching ``ready`` — the two are true together or not at all.
* It stores only what the seam represents. No field, attribute, classification, or
  sensitivity is derived here: that is FR-OCR-004 / FR-INF (gap G-12), and it will
  read these rows rather than replace them.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ExtractionBlock, ExtractionPage, ExtractionRun, ExtractionRunMetadata
from app.services.extraction import ExtractionResult


def build_extraction_run(*, document_id: uuid.UUID, result: ExtractionResult) -> ExtractionRun:
    """Map an :class:`ExtractionResult` onto a persistable :class:`ExtractionRun`.

    Pure construction — no session, no I/O. The relationship collections are filled
    in place, so ``session.add(run)`` inserts the whole graph in foreign-key order.
    Block order is captured as an explicit ``sequence`` because the database does not
    preserve the seam's tuple order on its own.
    """
    return ExtractionRun(
        document_id=document_id,
        engine=result.engine,
        engine_version=result.engine_version,
        run_metadata=[
            ExtractionRunMetadata(key=key, value=value)
            for key, value in result.metadata.items()
        ],
        pages=[
            ExtractionPage(
                number=page.number,
                text=page.text,
                confidence=page.confidence,
                blocks=[
                    ExtractionBlock(
                        sequence=index,
                        text=block.text,
                        confidence=block.confidence,
                        region_x=block.region.x if block.region is not None else None,
                        region_y=block.region.y if block.region is not None else None,
                        region_width=block.region.width if block.region is not None else None,
                        region_height=block.region.height if block.region is not None else None,
                    )
                    for index, block in enumerate(page.blocks)
                ],
            )
            for page in result.pages
        ],
    )


async def list_extraction_runs(
    db: AsyncSession, *, document_id: uuid.UUID
) -> list[ExtractionRun]:
    """Every run for a document, oldest first — the retained processing history.

    The future retrieval layer reads the most recent run; the older ones stay so a
    stored value can be traced to the engine version that produced it.
    """
    result = await db.scalars(
        select(ExtractionRun)
        .where(ExtractionRun.document_id == document_id)
        .order_by(ExtractionRun.created_at, ExtractionRun.id)
    )
    return list(result)
