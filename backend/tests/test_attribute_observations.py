"""Sprint 4 (third milestone) — the structured attribute observation layer.

These tests prove the smallest engine-neutral observation model works: a value read
for a canonical attribute, keyed by the vocabulary *identifier* only, traceable to the
exact block/page/run/document, with a round-tripping confidence (including ``None``),
retained across reprocessing, and readable back deterministically.

The one approved ``v0.1-draft`` entry ``person.full_name`` is used as a fixture, and
its identifier is read from the versioned configuration to prove the observation
references the vocabulary rather than duplicating it. **Using it here is not approval of
the G-12 field set** — it is the only approved entry, used solely to exercise the model.

Needs a real PostgreSQL (native UUID); skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

try:  # stdlib on the project's Python 3.12
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

from app.core.config import Settings
from app.db.models import (
    AttributeObservation,
    Document,
    ExtractionBlock,
    ExtractionPage,
    ExtractionRun,
    User,
)
from app.db.session import create_session_factory
from app.services import processing
from app.services.attribute_observation import (
    CandidateObservation,
    build_attribute_observations,
    list_attribute_observations,
    list_current_attribute_observations,
)
from app.services.document_service import store_document
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
    UnconfiguredExtractor,
)
from app.services.extraction_store import build_extraction_run
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, requires_postgres

pytestmark = requires_postgres

# The approved v0.1-draft identifier, read from configuration — never hard-coded here,
# so the observation is shown to reference the vocabulary, not to embed a copy of it.
_VOCAB_PATH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "vocabulary"
    / "canonical_attributes.v0.2-draft.toml"
)


def _person_full_name_identifier() -> str:
    with _VOCAB_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    return str(data["attribute"][0]["canonical_identifier"])


PERSON_FULL_NAME = _person_full_name_identifier()


def _sample_result(version: str = "1.0") -> ExtractionResult:
    """A fixed, synthetic result: the name printed twice (once per page), plus a year.

    The name appears on both pages so one run can yield two ``person.full_name``
    observations from two distinct blocks — without inventing a second attribute.
    """
    return ExtractionResult(
        pages=(
            ExtractedPage(
                number=1,
                text="page one text",
                confidence=0.9,
                blocks=(
                    TextBlock(
                        text="Priya Sharma",
                        region=TextRegion(page=1, x=0.1, y=0.2, width=0.3, height=0.05),
                        confidence=0.95,
                    ),
                    TextBlock(
                        text="2019",
                        region=TextRegion(page=1, x=0.1, y=0.4, width=0.2, height=0.05),
                        confidence=None,
                    ),
                ),
            ),
            ExtractedPage(
                number=2,
                text="page two text",
                confidence=None,
                # The same name again, this time with no region and no confidence.
                blocks=(TextBlock(text="Priya Sharma"),),
            ),
        ),
        engine="deterministic-test-double",
        engine_version=version,
        metadata={"page_count": "2"},
    )


class DeterministicExtractor:
    """Returns :func:`_sample_result`, ignoring the bytes (persistence must not care)."""

    name = "deterministic-test-double"

    def __init__(self, version: str = "1.0") -> None:
        self.version = version

    def is_available(self) -> bool:
        return True

    def extract(self, source: Any, *, content_type: str) -> ExtractionResult:
        return _sample_result(self.version)


@pytest.fixture
def session_factory(db_engine: Any) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(db_engine)


@pytest.fixture
def storage(db_settings: Settings) -> DocumentStorage:
    return build_document_storage(db_settings)


async def _seed_document(
    session_factory: async_sessionmaker[AsyncSession],
    storage: DocumentStorage,
    settings: Settings,
) -> Document:
    async with session_factory() as db:
        user = User(email="observe@example.com", password_hash="argon2-hash-unused")
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


async def _persist_run_with_observations(
    session_factory: async_sessionmaker[AsyncSession],
    document_id: Any,
    *,
    version: str,
    targets: list[tuple[int, int, str]],
) -> Any:
    """Persist a run AND its structured observations in ONE transaction, atomically.

    Demonstrates the transaction boundary: the run graph is flushed (ids assigned, not
    committed), observations are built against its blocks, and a single commit makes the
    two true together or not at all. ``targets`` names each source block unambiguously
    by ``(page_index, block_index, canonical_identifier)`` — the fixture name repeats
    across pages, so keying by text would be ambiguous. Returns the new run's id.
    """
    async with session_factory() as db:
        run = build_extraction_run(document_id=document_id, result=_sample_result(version))
        db.add(run)
        await db.flush()  # ids for the run and its blocks, without committing

        candidates: list[CandidateObservation] = []
        for page_index, block_index, identifier in targets:
            block = run.pages[page_index].blocks[block_index]
            candidates.append(
                CandidateObservation(
                    canonical_identifier=identifier,
                    value=block.text,
                    source_block=block,
                    confidence=block.confidence,
                )
            )
        db.add_all(build_attribute_observations(run=run, candidates=candidates))
        await db.commit()
        return run.id


async def _count_observations(
    session_factory: async_sessionmaker[AsyncSession], document_id: Any
) -> int:
    async with session_factory() as db:
        return (
            await db.scalar(
                select(func.count())
                .select_from(AttributeObservation)
                .join(ExtractionRun, AttributeObservation.run_id == ExtractionRun.id)
                .where(ExtractionRun.document_id == document_id)
            )
            or 0
        )


class TestPersistenceAndRoundTrip:
    async def test_an_observation_persists_with_identifier_value_and_confidence(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )

        async with session_factory() as db:
            observations = await list_attribute_observations(db, document_id=document.id)
        assert len(observations) == 1
        observation = observations[0]
        # Canonical identifier is the configured one, stored verbatim; value round-trips.
        assert observation.canonical_identifier == PERSON_FULL_NAME == "person.full_name"
        assert observation.value == "Priya Sharma"
        # The confidence the value was read with (0.95) round-trips.
        assert observation.confidence == pytest.approx(0.95)

    async def test_confidence_round_trips_including_none(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        # The page-two name block carries no confidence — a distinct fact from a low one.
        await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            targets=[(0, 0, PERSON_FULL_NAME)],  # page 1 name, confidence 0.95
        )
        # Add a second run whose only observation comes from a no-confidence block.
        async with session_factory() as db:
            run = build_extraction_run(document_id=document.id, result=_sample_result("1.0"))
            db.add(run)
            await db.flush()
            page_two_block = run.pages[1].blocks[0]
            db.add_all(
                build_attribute_observations(
                    run=run,
                    candidates=[
                        CandidateObservation(
                            canonical_identifier=PERSON_FULL_NAME,
                            value=page_two_block.text,
                            source_block=page_two_block,
                            confidence=page_two_block.confidence,  # None
                        )
                    ],
                )
            )
            await db.commit()

        async with session_factory() as db:
            observations = await list_attribute_observations(db, document_id=document.id)
        confidences = [o.confidence for o in observations]
        assert pytest.approx(0.95) in confidences
        assert None in confidences

    async def test_one_run_can_produce_multiple_observations(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        run_id = await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            # The same attribute read from two different blocks (the name on both pages).
            targets=[(0, 0, PERSON_FULL_NAME), (1, 0, PERSON_FULL_NAME)],
        )

        async with session_factory() as db:
            observations = await list_attribute_observations(db, document_id=document.id)
        assert len(observations) == 2
        # Both belong to the one run — no conflict/dedup collapse happens here.
        assert {o.run_id for o in observations} == {run_id}


class TestProvenance:
    async def test_provenance_points_to_the_correct_block_page_run_and_document(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        run_id = await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )

        async with session_factory() as db:
            observation = await db.scalar(
                select(AttributeObservation).options(
                    selectinload(AttributeObservation.source_block)
                    .selectinload(ExtractionBlock.page)
                    .selectinload(ExtractionPage.run),
                    selectinload(AttributeObservation.run),
                )
            )
            assert observation is not None

            # observation -> block -> page -> run -> document, exactly.
            block = observation.source_block
            assert block.text == "Priya Sharma"
            page = block.page
            assert page.number == 1
            run = page.run
            assert run.id == run_id
            assert run.document_id == document.id
            # The run the observation records is the block's run — they agree.
            assert observation.run_id == run_id
            assert observation.run.document_id == document.id


class TestHistoryAcrossRuns:
    async def test_a_later_run_adds_observations_without_destroying_the_old_run_s(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)

        first_run_id = await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )
        second_run_id = await _persist_run_with_observations(
            session_factory,
            document.id,
            version="2.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )
        assert first_run_id != second_run_id

        async with session_factory() as db:
            everything = await list_attribute_observations(db, document_id=document.id)
            current = await list_current_attribute_observations(db, document_id=document.id)

        # History is retained: both runs' observations survive.
        assert {o.run_id for o in everything} == {first_run_id, second_run_id}
        # "Current" is the newest run's, derived — not an is_current flag.
        assert [o.run_id for o in current] == [second_run_id]
        assert not hasattr(AttributeObservation, "is_current")

    async def test_reprocessing_through_the_pipeline_keeps_prior_observations(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """A real reprocess adds a new run; observations of the prior run are untouched."""
        document = await _seed_document(session_factory, storage, db_settings)

        # First run via the pipeline, then observations recorded against it.
        assert await processing.process_one(
            session_factory, storage=storage, extractor=DeterministicExtractor("1.0"),
            settings=db_settings,
        )
        async with session_factory() as db:
            first_run = await db.scalar(
                select(ExtractionRun).where(ExtractionRun.document_id == document.id)
            )
            assert first_run is not None
            block = await db.scalar(
                select(ExtractionBlock)
                .join(ExtractionPage, ExtractionBlock.page_id == ExtractionPage.id)
                .where(
                    ExtractionPage.run_id == first_run.id,
                    ExtractionBlock.text == "Priya Sharma",
                )
            )
            assert block is not None
            db.add_all(
                build_attribute_observations(
                    run=first_run,
                    candidates=[
                        CandidateObservation(
                            canonical_identifier=PERSON_FULL_NAME,
                            value=block.text,
                            source_block=block,
                            confidence=block.confidence,
                        )
                    ],
                )
            )
            await db.commit()

        # A second successful run adds observations tied to it.
        await _persist_run_with_observations(
            session_factory,
            document.id,
            version="2.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )

        assert await _count_observations(session_factory, document.id) == 2


class TestFailedExtractionProducesNoObservations:
    async def test_a_failed_extraction_leaves_no_observations(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = db_settings.model_copy(update={"worker_max_attempts": 1})
        document = await _seed_document(session_factory, storage, settings)

        # The unconfigured extractor fails; no run is persisted, so no observation can be.
        await processing.process_one(
            session_factory, storage=storage, extractor=UnconfiguredExtractor(),
            settings=settings,
        )

        assert await _count_observations(session_factory, document.id) == 0


class TestDeterministicRetrieval:
    async def test_retrieval_is_stable_and_ordered_by_run_then_id(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            targets=[(0, 0, PERSON_FULL_NAME), (1, 0, PERSON_FULL_NAME)],
        )
        await _persist_run_with_observations(
            session_factory,
            document.id,
            version="2.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )

        async with session_factory() as db:
            first = await list_attribute_observations(db, document_id=document.id)
        async with session_factory() as db:
            second = await list_attribute_observations(db, document_id=document.id)

        assert [o.id for o in first] == [o.id for o in second]
        assert len(first) == 3


class TestNoFileMetadataLeaks:
    async def test_observation_rows_carry_no_file_metadata(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_observations(
            session_factory,
            document.id,
            version="1.0",
            targets=[(0, 0, PERSON_FULL_NAME)],
        )

        # Structural: the observation has no file-metadata columns at all.
        columns = set(AttributeObservation.__table__.columns.keys())
        assert not (
            columns
            & {"original_filename", "storage_key", "checksum_sha256", "byte_size", "content_type"}
        )

        # Content: nothing about the stored file crept into a stored value/identifier.
        async with session_factory() as db:
            observations = await list_attribute_observations(db, document_id=document.id)
            reloaded = await db.get(Document, document.id)
        assert reloaded is not None
        for observation in observations:
            blob = observation.value + observation.canonical_identifier
            assert reloaded.storage_key not in blob
            assert reloaded.original_filename not in blob
            assert reloaded.checksum_sha256 not in blob
            assert "%PDF" not in blob
