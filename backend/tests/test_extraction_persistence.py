"""Sprint 4 (second milestone) — persisting the engine-neutral extraction result.

No OCR engine exists, so a deterministic in-test extractor stands in: it returns a
fixed, obviously synthetic result so that persistence can be exercised without any
claim about extraction quality (AR-AST-008). The unconfigured extractor's failure
path is preserved and tested here too.

Needs a real PostgreSQL (native UUID, and the pipeline's SKIP LOCKED claim); skips
when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

import io
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.db.models import (
    Document,
    DocumentStatus,
    ExtractionBlock,
    ExtractionRun,
    ExtractionRunMetadata,
    User,
)
from app.db.session import create_session_factory
from app.services import processing
from app.services.document_service import request_reprocess, store_document
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
    UnconfiguredExtractor,
)
from app.services.extraction_store import list_extraction_runs
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, requires_postgres

pytestmark = requires_postgres


class DeterministicExtractor:
    """A fixed, synthetic extractor: two pages, blocks with and without a region.

    It ignores the document bytes entirely — like the real seam, persistence must not
    depend on having read anything in particular — and its ``version`` is settable so
    a second run can be told from the first.
    """

    name = "deterministic-test-double"

    def __init__(self, version: str = "1.0") -> None:
        self.version = version

    def is_available(self) -> bool:
        return True

    def extract(self, source: Any, *, content_type: str) -> ExtractionResult:
        return ExtractionResult(
            pages=(
                ExtractedPage(
                    number=1,
                    text="page one text",
                    confidence=0.9,
                    blocks=(
                        TextBlock(
                            text="Alice Example",
                            region=TextRegion(page=1, x=0.1, y=0.2, width=0.3, height=0.05),
                            confidence=0.95,
                        ),
                        # No confidence reported — a distinct fact from a low one.
                        TextBlock(
                            text="2020",
                            region=TextRegion(page=1, x=0.1, y=0.35, width=0.2, height=0.05),
                            confidence=None,
                        ),
                    ),
                ),
                ExtractedPage(
                    number=2,
                    text="page two text",
                    confidence=None,
                    # A block with no region at all.
                    blocks=(TextBlock(text="no region here"),),
                ),
            ),
            engine=self.name,
            engine_version=self.version,
            metadata={"duration_ms": "12", "page_count": "2"},
        )


@pytest.fixture
def session_factory(db_engine: Any) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(db_engine)


@pytest.fixture
def storage(db_settings: Settings) -> DocumentStorage:
    return build_document_storage(db_settings)


def _with_max_attempts(db_settings: Settings, attempts: int) -> Settings:
    return db_settings.model_copy(update={"worker_max_attempts": attempts})


async def _seed_document(
    session_factory: async_sessionmaker[AsyncSession],
    storage: DocumentStorage,
    settings: Settings,
) -> Document:
    async with session_factory() as db:
        user = User(email="persist@example.com", password_hash="argon2-hash-unused")
        db.add(user)
        await db.commit()
        return await store_document(
            db,
            owner=user,
            source=io.BytesIO(PDF_BYTES),
            filename="marksheet.pdf",
            declared_content_type="application/pdf",
            storage=storage,
            settings=settings,
        )


async def _load_run(
    session_factory: async_sessionmaker[AsyncSession], document_id: Any
) -> ExtractionRun | None:
    """Load a document's single run with its pages, blocks, and metadata eagerly."""
    async with session_factory() as db:
        run: ExtractionRun | None = await db.scalar(
            select(ExtractionRun)
            .where(ExtractionRun.document_id == document_id)
            .options(
                selectinload(ExtractionRun.pages),
                selectinload(ExtractionRun.run_metadata),
            )
        )
        return run


async def _process(
    session_factory: async_sessionmaker[AsyncSession],
    storage: DocumentStorage,
    settings: Settings,
    extractor: Any,
) -> bool:
    return await processing.process_one(
        session_factory, storage=storage, extractor=extractor, settings=settings
    )


class TestSuccessfulPersistence:
    async def test_a_result_is_persisted_with_its_pages_blocks_and_regions(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)

        assert await _process(session_factory, storage, db_settings, DeterministicExtractor())

        run = await _load_run(session_factory, document.id)
        assert run is not None
        assert run.document_id == document.id
        assert run.engine == "deterministic-test-double"
        assert run.engine_version == "1.0"

        # Pages come back in page order.
        assert [p.number for p in run.pages] == [1, 2]
        page_one, page_two = run.pages
        assert page_one.text == "page one text"
        assert page_two.text == "page two text"

        # Blocks keep their order within the page, and provenance runs
        # block -> page -> run -> document.
        async with session_factory() as db:
            blocks_one = list(
                await db.scalars(
                    select(ExtractionBlock).where(ExtractionBlock.page_id == page_one.id).order_by(
                        ExtractionBlock.sequence
                    )
                )
            )
        assert [b.sequence for b in blocks_one] == [0, 1]
        assert [b.text for b in blocks_one] == ["Alice Example", "2020"]

        first_block = blocks_one[0]
        assert first_block.region_x == pytest.approx(0.1)
        assert first_block.region_y == pytest.approx(0.2)
        assert first_block.region_width == pytest.approx(0.3)
        assert first_block.region_height == pytest.approx(0.05)

    async def test_confidence_round_trips_including_absent(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _process(session_factory, storage, db_settings, DeterministicExtractor())

        run = await _load_run(session_factory, document.id)
        assert run is not None
        page_one, page_two = run.pages
        assert page_one.confidence == pytest.approx(0.9)
        # A page/block the engine gave no confidence for stays NULL, not zero.
        assert page_two.confidence is None

        async with session_factory() as db:
            blocks = list(
                await db.scalars(
                    select(ExtractionBlock).where(ExtractionBlock.page_id == page_one.id).order_by(
                        ExtractionBlock.sequence
                    )
                )
            )
        assert blocks[0].confidence == pytest.approx(0.95)
        assert blocks[1].confidence is None

    async def test_a_block_without_a_region_stores_no_coordinates(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _process(session_factory, storage, db_settings, DeterministicExtractor())

        run = await _load_run(session_factory, document.id)
        assert run is not None
        page_two = run.pages[1]
        async with session_factory() as db:
            block = await db.scalar(
                select(ExtractionBlock).where(ExtractionBlock.page_id == page_two.id)
            )
        assert block is not None
        assert block.region_x is None
        assert block.region_y is None
        assert block.region_width is None
        assert block.region_height is None

    async def test_metadata_round_trips(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _process(session_factory, storage, db_settings, DeterministicExtractor())

        run = await _load_run(session_factory, document.id)
        assert run is not None
        assert {m.key: m.value for m in run.run_metadata} == {
            "duration_ms": "12",
            "page_count": "2",
        }


class TestFailurePersistsNoRun:
    async def test_failed_extraction_creates_no_run(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = _with_max_attempts(db_settings, 1)
        document = await _seed_document(session_factory, storage, settings)

        await _process(session_factory, storage, settings, UnconfiguredExtractor())

        # No partial run, and the failure is still recorded on the document.
        assert await _count_runs(session_factory, document.id) == 0
        async with session_factory() as db:
            reloaded = await db.get(Document, document.id)
        assert reloaded is not None
        assert reloaded.status is DocumentStatus.FAILED
        assert reloaded.failure_reason is not None

    async def test_unconfigured_extractor_still_drives_the_failed_path(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = _with_max_attempts(db_settings, 1)
        document = await _seed_document(session_factory, storage, settings)

        worked = await _process(session_factory, storage, settings, UnconfiguredExtractor())
        assert worked is True

        async with session_factory() as db:
            reloaded = await db.get(Document, document.id)
        assert reloaded is not None
        assert reloaded.status is DocumentStatus.FAILED


class TestHistoryAndReprocessing:
    async def test_reprocess_adds_a_run_and_keeps_the_old_one(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)

        # First successful run.
        await _process(session_factory, storage, db_settings, DeterministicExtractor(version="1.0"))
        first_runs = await list_extraction_runs_via(session_factory, document.id)
        assert len(first_runs) == 1
        first_id = first_runs[0].id

        # Reprocess and run again with a different engine version.
        async with session_factory() as db:
            await request_reprocess(db, user_id=document.user_id, document_id=document.id)
        await _process(session_factory, storage, db_settings, DeterministicExtractor(version="2.0"))

        runs = await list_extraction_runs_via(session_factory, document.id)
        # The old run survives; a new, distinct run is added — history is retained.
        assert len(runs) == 2
        ids = {r.id for r in runs}
        assert first_id in ids
        assert {r.engine_version for r in runs} == {"1.0", "2.0"}


class TestNoLeakage:
    async def test_no_document_bytes_or_file_metadata_leak_into_stored_metadata(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """NFR-PRIV-007: only the engine-neutral metadata is stored — nothing about the file."""
        document = await _seed_document(session_factory, storage, db_settings)
        await _process(session_factory, storage, db_settings, DeterministicExtractor())

        async with session_factory() as db:
            metadata_rows = list(await db.scalars(select(ExtractionRunMetadata)))
            reloaded = await db.get(Document, document.id)
        assert reloaded is not None

        stored = {row.key: row.value for row in metadata_rows}
        assert stored == {"duration_ms": "12", "page_count": "2"}
        # Nothing about the stored file crept into the metadata.
        for value in stored.values():
            assert reloaded.storage_key not in value
            assert reloaded.original_filename not in value
            assert reloaded.checksum_sha256 not in value
        blob = "".join(stored.keys()) + "".join(stored.values())
        assert "%PDF" not in blob


async def _count_runs(session_factory: async_sessionmaker[AsyncSession], document_id: Any) -> int:
    async with session_factory() as db:
        return (
            await db.scalar(
                select(func.count())
                .select_from(ExtractionRun)
                .where(ExtractionRun.document_id == document_id)
            )
            or 0
        )


async def list_extraction_runs_via(
    session_factory: async_sessionmaker[AsyncSession], document_id: Any
) -> list[ExtractionRun]:
    async with session_factory() as db:
        return await list_extraction_runs(db, document_id=document_id)
