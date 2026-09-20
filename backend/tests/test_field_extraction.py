"""Sprint 4 (sixth milestone) — the field-extraction seam: blocks → AttributeObservation.

These tests prove the first vertical slice: a deterministic ``person.full_name`` extractor
that maps a labelled text block to a candidate attribute observation, persisted through the
existing service with exact provenance and honest confidence, idempotent per run, and
integrated into the processing pipeline behind an optional, engine-neutral seam.

``person.full_name`` is the only vocabulary-dependent fixture, read from configuration.
Using it exercises the slice; it does not complete G-12.

Needs a real PostgreSQL (native UUID); skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

import io
import uuid
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
from app.services.attribute_observation import list_attribute_observations
from app.services.current_record import get_current_value
from app.services.document_service import store_document
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
    UnconfiguredExtractor,
)
from app.services.extraction_store import build_extraction_run
from app.services.field_extraction import (
    FullNameFieldExtractor,
    apply_field_extraction,
    build_field_extractor,
)
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, requires_postgres

pytestmark = requires_postgres

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


def _result(
    *blocks: tuple[str, float | None], version: str = "1.0", with_region: bool = False
) -> ExtractionResult:
    text_blocks = []
    for index, (text, confidence) in enumerate(blocks):
        region = (
            TextRegion(page=1, x=0.1, y=0.1 + index * 0.1, width=0.3, height=0.05)
            if with_region
            else None
        )
        text_blocks.append(TextBlock(text=text, region=region, confidence=confidence))
    page = ExtractedPage(number=1, text="page one", confidence=None, blocks=tuple(text_blocks))
    return ExtractionResult(
        pages=(page,),
        engine="deterministic-test-double",
        engine_version=version,
        metadata={},
    )


class LabeledExtractor:
    """Returns a fixed result carrying labelled blocks (ignores the bytes)."""

    name = "deterministic-test-double"
    version = "1.0"

    def __init__(self, result: ExtractionResult) -> None:
        self._result = result

    def is_available(self) -> bool:
        return True

    def extract(self, source: Any, *, content_type: str) -> ExtractionResult:
        return self._result


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
    *,
    email: str = "field@example.com",
    content: bytes = PDF_BYTES,
) -> Document:
    async with session_factory() as db:
        user = await db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, password_hash="argon2-hash-unused")
            db.add(user)
            await db.commit()
        return await store_document(
            db,
            owner=user,
            source=io.BytesIO(content),
            filename="marksheet.pdf",
            declared_content_type="application/pdf",
            storage=storage,
            settings=settings,
        )


# --------------------------------------------------------------------------
# The extractor's mapping logic — no persistence needed.
# --------------------------------------------------------------------------


class TestExtractLogic:
    def _run(self, result: ExtractionResult) -> ExtractionRun:
        return build_extraction_run(document_id=uuid.uuid4(), result=result)

    def test_extracts_full_name_from_a_labeled_block(self) -> None:
        run = self._run(_result(("Name: Priya Sharma", 0.95)))
        candidates = FullNameFieldExtractor().extract_fields(run)
        assert len(candidates) == 1
        candidate = candidates[0]
        assert candidate.canonical_identifier == PERSON_FULL_NAME == "person.full_name"
        assert candidate.value == "Priya Sharma"
        # Provenance points at the exact block; its confidence is used unchanged.
        assert candidate.source_block is run.pages[0].blocks[0]
        assert candidate.confidence == pytest.approx(0.95)

    def test_recognises_the_full_name_label_variant(self) -> None:
        run = self._run(_result(("Full Name - Priya Sharma", 0.5)))
        candidates = FullNameFieldExtractor().extract_fields(run)
        assert len(candidates) == 1
        assert candidates[0].value == "Priya Sharma"

    def test_missing_block_confidence_is_not_invented(self) -> None:
        run = self._run(_result(("Name: Priya Sharma", None)))
        candidate = FullNameFieldExtractor().extract_fields(run)[0]
        assert candidate.confidence is None

    def test_unlabeled_block_yields_nothing(self) -> None:
        # A bare value with no label is not recognised — no output is invented.
        run = self._run(_result(("Priya Sharma", 0.95), ("2019", None)))
        assert FullNameFieldExtractor().extract_fields(run) == []

    def test_empty_value_after_label_yields_nothing(self) -> None:
        run = self._run(_result(("Name: ", 0.9)))
        assert FullNameFieldExtractor().extract_fields(run) == []

    def test_multiple_labeled_blocks_yield_multiple_candidates(self) -> None:
        run = self._run(_result(("Name: Priya Sharma", 0.9), ("Name: Riya Verma", 0.8)))
        candidates = FullNameFieldExtractor().extract_fields(run)
        assert [c.value for c in candidates] == ["Priya Sharma", "Riya Verma"]

    def test_bare_name_prefix_on_prose_is_not_a_false_extraction(self) -> None:
        # Precision (BR-009, S-6 false-extraction): a sentence that merely begins with "Name"
        # but has no ":"/"-" separator must NOT be read as a name. The bare "name" alias
        # requires an explicit separator; only the explicit "Full Name" label may use whitespace.
        run = self._run(
            _result(
                ("Name mismatches are a silent disqualifier; detecting them is cheap", 0.9),
                ("named entity recognition is future work", 0.9),
            )
        )
        assert FullNameFieldExtractor().extract_fields(run) == []

    def test_full_name_label_still_matches_with_whitespace_separator(self) -> None:
        # The legitimate table-row form ("Full Name <value>") is preserved by the fix.
        run = self._run(_result(("Full Name Vedant Santosh Kadam", 0.9)))
        candidates = FullNameFieldExtractor().extract_fields(run)
        assert [c.value for c in candidates] == ["Vedant Santosh Kadam"]

    def test_builder_returns_a_usable_extractor(self) -> None:
        run = self._run(_result(("Name: Priya Sharma", 0.9)))
        assert build_field_extractor().extract_fields(run)[0].value == "Priya Sharma"


# --------------------------------------------------------------------------
# Persistence, provenance, idempotency — against a real database.
# --------------------------------------------------------------------------


async def _persist_run_and_extract(
    session_factory: async_sessionmaker[AsyncSession],
    document_id: Any,
    result: ExtractionResult,
) -> Any:
    async with session_factory() as db:
        run = build_extraction_run(document_id=document_id, result=result)
        db.add(run)
        await db.flush()
        await apply_field_extraction(db, run=run, extractor=FullNameFieldExtractor())
        await db.commit()
        return run.id


async def _count(session_factory: async_sessionmaker[AsyncSession], document_id: Any) -> int:
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


class TestPersistenceAndProvenance:
    async def test_apply_persists_value_with_exact_provenance(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        run_id = await _persist_run_and_extract(
            session_factory, document.id, _result(("Name: Priya Sharma", 0.95), with_region=True)
        )

        async with session_factory() as db:
            observation = await db.scalar(
                select(AttributeObservation).options(
                    selectinload(AttributeObservation.source_block)
                    .selectinload(ExtractionBlock.page)
                    .selectinload(ExtractionPage.run)
                )
            )
        assert observation is not None
        assert observation.canonical_identifier == PERSON_FULL_NAME
        # The stored value is the extracted name; provenance is the labelled block itself.
        assert observation.value == "Priya Sharma"
        assert observation.source_block.text == "Name: Priya Sharma"
        assert observation.confidence == pytest.approx(0.95)
        # block → page → run → document, exactly.
        assert observation.source_block.page.number == 1
        assert observation.source_block.page.run.id == run_id
        assert observation.source_block.page.run.document_id == document.id

    async def test_rerun_against_the_same_run_creates_no_duplicates(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        async with session_factory() as db:
            run = build_extraction_run(
                document_id=document.id, result=_result(("Name: Priya Sharma", 0.9))
            )
            db.add(run)
            await db.flush()
            first = await apply_field_extraction(db, run=run, extractor=FullNameFieldExtractor())
            # Second pass over the same run is a no-op — the run already has observations.
            second = await apply_field_extraction(db, run=run, extractor=FullNameFieldExtractor())
            await db.commit()
        assert len(first) == 1
        assert second == []
        assert await _count(session_factory, document.id) == 1

    async def test_different_runs_create_independent_observations(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        run_a = await _persist_run_and_extract(
            session_factory, document.id, _result(("Name: Priya Sharma", 0.9), version="1.0")
        )
        run_b = await _persist_run_and_extract(
            session_factory, document.id, _result(("Name: Priya Verma", 0.9), version="2.0")
        )
        assert run_a != run_b
        assert await _count(session_factory, document.id) == 2
        async with session_factory() as db:
            observations = await list_attribute_observations(db, document_id=document.id)
        assert {o.run_id for o in observations} == {run_a, run_b}

    async def test_disagreeing_candidates_surface_as_ambiguity(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        # One run, two labelled blocks disagreeing — two observations, no winner chosen.
        await _persist_run_and_extract(
            session_factory,
            document.id,
            _result(("Name: Priya Sharma", 0.9), ("Name: Riya Verma", 0.8)),
        )
        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        assert value.is_ambiguous is True
        assert value.value is None
        assert {o.value for o in value.observations} == {"Priya Sharma", "Riya Verma"}

    async def test_no_file_metadata_leaks_into_observations(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_and_extract(
            session_factory, document.id, _result(("Name: Priya Sharma", 0.9))
        )
        # Structural: no file-metadata columns on the observation.
        columns = set(AttributeObservation.__table__.columns.keys())
        assert not (
            columns
            & {"original_filename", "storage_key", "checksum_sha256", "byte_size", "content_type"}
        )
        # Content: nothing about the stored file crept into a value or identifier.
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


# --------------------------------------------------------------------------
# Processing-pipeline integration.
# --------------------------------------------------------------------------


class TestPipelineIntegration:
    async def test_pipeline_creates_observations_from_deterministic_data(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        extractor = LabeledExtractor(_result(("Name: Priya Sharma", 0.9)))

        processed = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=extractor,
            settings=db_settings,
            field_extractor=FullNameFieldExtractor(),
        )
        assert processed is True

        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        assert value.value == "Priya Sharma"
        assert value.is_ambiguous is False

    async def test_pipeline_without_a_field_extractor_creates_no_observations(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        extractor = LabeledExtractor(_result(("Name: Priya Sharma", 0.9)))

        # No field extractor: the run persists, extraction infra is unaffected, and no
        # attribute observation is created.
        processed = await processing.process_one(
            session_factory, storage=storage, extractor=extractor, settings=db_settings
        )
        assert processed is True
        async with session_factory() as db:
            run_exists = await db.scalar(
                select(func.count()).select_from(ExtractionRun).where(
                    ExtractionRun.document_id == document.id
                )
            )
        assert run_exists == 1
        assert await _count(session_factory, document.id) == 0

    async def test_unconfigured_extractor_failure_path_is_unchanged(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = db_settings.model_copy(update={"worker_max_attempts": 1})
        document = await _seed_document(session_factory, storage, settings)

        # A field extractor is configured, but the success path is never reached: the
        # unconfigured engine fails, so no run and no observation exist.
        processed = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=UnconfiguredExtractor(),
            settings=settings,
            field_extractor=FullNameFieldExtractor(),
        )
        assert processed is True
        async with session_factory() as db:
            run_count = await db.scalar(
                select(func.count()).select_from(ExtractionRun).where(
                    ExtractionRun.document_id == document.id
                )
            )
        assert run_count == 0
        assert await _count(session_factory, document.id) == 0
