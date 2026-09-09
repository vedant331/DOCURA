"""Sprint 4 (seventh milestone) — the document-classification seam.

These tests prove the seam and its result type, not a classifier: a replaceable
``DocumentClassifier`` returning a deterministic ``ClassificationResult`` (type +
confidence + metadata), abstention as ``UNCLASSIFIED``, confidence kept separate from
field confidence, optional pipeline integration that changes no existing behavior, and
**no new persistence** — the result is written to the existing ``Document.document_type``.

Only ``DocumentType.UNCLASSIFIED`` exists (§7.1's type set is TBD pending evaluation), so
no supported type is invented to make a test interesting.

Some tests need a real PostgreSQL; those are the pipeline ones. The pure result/seam tests
do not, but the module shares the ``requires_postgres`` mark for simplicity.
"""

from __future__ import annotations

import io
import uuid
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.db.models import (
    AttributeObservation,
    Base,
    Document,
    DocumentStatus,
    DocumentType,
    ExtractionRun,
    User,
)
from app.db.session import create_session_factory
from app.services import processing
from app.services.classification import (
    ClassificationResult,
    DocumentClassifier,
    UnclassifiedClassifier,
    build_document_classifier,
)
from app.services.current_record import get_current_value
from app.services.document_service import store_document
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    UnconfiguredExtractor,
)
from app.services.extraction_store import build_extraction_run
from app.services.field_extraction import FullNameFieldExtractor
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, pdf_bytes, requires_postgres

pytestmark = requires_postgres

PERSON_FULL_NAME = "person.full_name"


def _result(*block_texts: str) -> ExtractionResult:
    blocks = tuple(TextBlock(text=text, confidence=0.9) for text in block_texts)
    return ExtractionResult(
        pages=(ExtractedPage(number=1, text="page one", confidence=None, blocks=blocks),),
        engine="deterministic-test-double",
        engine_version="1.0",
        metadata={},
    )


class LabeledExtractor:
    """Returns a fixed extraction result (ignores the bytes)."""

    name = "deterministic-test-double"
    version = "1.0"

    def __init__(self, result: ExtractionResult) -> None:
        self._result = result

    def is_available(self) -> bool:
        return True

    def extract(self, source: Any, *, content_type: str) -> ExtractionResult:
        return self._result


class StubClassifier:
    """A deterministic classifier returning a fixed result — the test fixture."""

    name = "stub-classifier"
    version = "1.0"

    def __init__(self, result: ClassificationResult) -> None:
        self._result = result

    def classify(self, run: ExtractionRun) -> ClassificationResult:
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
    email: str = "classify@example.com",
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


async def _document_type(
    session_factory: async_sessionmaker[AsyncSession], document_id: Any
) -> DocumentType:
    async with session_factory() as db:
        document = await db.get(Document, document_id)
        assert document is not None
        return document.document_type


# --------------------------------------------------------------------------
# The result type and the seam — no persistence needed.
# --------------------------------------------------------------------------


class TestResultAndSeam:
    def test_result_carries_type_confidence_and_metadata(self) -> None:
        result = ClassificationResult(
            document_type=DocumentType.UNCLASSIFIED,
            confidence=0.87,
            metadata={"model": "stub"},
        )
        assert result.document_type is DocumentType.UNCLASSIFIED
        assert result.confidence == pytest.approx(0.87)
        assert result.metadata == {"model": "stub"}

    def test_confidence_defaults_to_none_and_none_is_allowed(self) -> None:
        assert ClassificationResult(document_type=DocumentType.UNCLASSIFIED).confidence is None

    def test_out_of_range_confidence_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="between 0 and 1"):
            ClassificationResult(document_type=DocumentType.UNCLASSIFIED, confidence=1.5)

    def test_unclassified_is_abstention(self) -> None:
        # UNCLASSIFIED is the "unrecognised" bucket; is_classified reports abstention.
        assert ClassificationResult(document_type=DocumentType.UNCLASSIFIED).is_classified is False

    def test_unconfigured_classifier_abstains(self) -> None:
        run = build_extraction_run(document_id=uuid.uuid4(), result=_result("hello"))
        result = UnclassifiedClassifier().classify(run)
        assert result.document_type is DocumentType.UNCLASSIFIED
        assert result.confidence is None
        assert result.is_classified is False

    def test_builder_returns_a_classifier_matching_the_protocol(self) -> None:
        classifier = build_document_classifier()
        assert isinstance(classifier, DocumentClassifier)
        assert classifier.name == "unclassified"

    def test_stub_fixture_is_deterministic(self) -> None:
        run = build_extraction_run(document_id=uuid.uuid4(), result=_result("hi"))
        stub = StubClassifier(
            ClassificationResult(document_type=DocumentType.UNCLASSIFIED, confidence=0.4)
        )
        first, second = stub.classify(run), stub.classify(run)
        assert first is second
        assert first.confidence == pytest.approx(0.4)

    def test_no_classification_table_or_new_document_type_was_added(self) -> None:
        # Persistence decision: reuse Document.document_type; add no table.
        assert "classifications" not in Base.metadata.tables
        assert "classification_results" not in Base.metadata.tables
        # No supported document type was invented to make classification interesting.
        assert {member.name for member in DocumentType} == {"UNCLASSIFIED"}


# --------------------------------------------------------------------------
# Pipeline integration — against a real database.
# --------------------------------------------------------------------------


class TestPipelineIntegration:
    async def test_pipeline_works_with_classifier_omitted(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        processed = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=LabeledExtractor(_result("Name: Priya Sharma")),
            settings=db_settings,
        )
        assert processed is True
        assert await _document_type(session_factory, document.id) is DocumentType.UNCLASSIFIED

    async def test_pipeline_works_with_a_deterministic_classifier(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        stub = StubClassifier(
            ClassificationResult(document_type=DocumentType.UNCLASSIFIED, confidence=0.72)
        )
        processed = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=LabeledExtractor(_result("Name: Priya Sharma")),
            settings=db_settings,
            classifier=stub,
        )
        assert processed is True
        # The classifier's assigned type is written to the existing column.
        assert await _document_type(session_factory, document.id) is DocumentType.UNCLASSIFIED

    async def test_classification_does_not_alter_extraction_behavior(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        # With and without a classifier, extraction persists the same run graph.
        with_stub = await _seed_document(
            session_factory, storage, db_settings, email="w@example.com", content=pdf_bytes(b"W")
        )
        without = await _seed_document(
            session_factory, storage, db_settings, email="n@example.com", content=pdf_bytes(b"N")
        )
        extractor = LabeledExtractor(_result("Name: Priya Sharma"))
        stub = StubClassifier(ClassificationResult(document_type=DocumentType.UNCLASSIFIED))

        await processing.process_one(
            session_factory, storage=storage, extractor=extractor, settings=db_settings,
            classifier=stub,
        )
        await processing.process_one(
            session_factory, storage=storage, extractor=extractor, settings=db_settings,
        )

        async with session_factory() as db:
            for doc_id in (with_stub.id, without.id):
                runs = await db.scalars(
                    select(ExtractionRun).where(ExtractionRun.document_id == doc_id)
                )
                run_list = list(runs)
                assert len(run_list) == 1
                assert run_list[0].engine == "deterministic-test-double"

    async def test_field_extraction_remains_document_type_agnostic(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        # A classifier that abstains does not stop person.full_name extraction, and the
        # field observation's confidence comes from the block, not the classifier.
        document = await _seed_document(session_factory, storage, db_settings)
        stub = StubClassifier(
            ClassificationResult(document_type=DocumentType.UNCLASSIFIED, confidence=0.11)
        )
        await processing.process_one(
            session_factory,
            storage=storage,
            extractor=LabeledExtractor(_result("Name: Priya Sharma")),
            settings=db_settings,
            classifier=stub,
            field_extractor=FullNameFieldExtractor(),
        )
        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        assert value.value == "Priya Sharma"
        # Field confidence is the block's 0.9, never the classifier's 0.11.
        assert value.observations[0].confidence == pytest.approx(0.9)

    async def test_classification_does_not_leak_across_documents(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        mine = await _seed_document(
            session_factory, storage, db_settings, email="a@example.com", content=pdf_bytes(b"A")
        )
        theirs = await _seed_document(
            session_factory, storage, db_settings, email="b@example.com", content=pdf_bytes(b"B")
        )
        # Classify only `mine`. The other document and its owner are untouched.
        await processing.process_one(
            session_factory,
            storage=storage,
            extractor=LabeledExtractor(_result("Name: Priya Sharma")),
            settings=db_settings,
            classifier=StubClassifier(
                ClassificationResult(document_type=DocumentType.UNCLASSIFIED)
            ),
        )
        assert await _document_type(session_factory, mine.id) is DocumentType.UNCLASSIFIED
        # `theirs` was never processed: still queued, still unclassified, no runs.
        async with session_factory() as db:
            other = await db.get(Document, theirs.id)
            assert other is not None
            assert other.status is DocumentStatus.QUEUED
            assert other.document_type is DocumentType.UNCLASSIFIED
            run_count = await db.scalar(
                select(func.count()).select_from(ExtractionRun).where(
                    ExtractionRun.document_id == theirs.id
                )
            )
        assert run_count == 0

    async def test_unconfigured_extractor_failure_path_is_unchanged(
        self, session_factory: async_sessionmaker[AsyncSession], storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = db_settings.model_copy(update={"worker_max_attempts": 1})
        document = await _seed_document(session_factory, storage, settings)
        # A classifier is configured, but the success path is never reached.
        processed = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=UnconfiguredExtractor(),
            settings=settings,
            classifier=StubClassifier(
                ClassificationResult(document_type=DocumentType.UNCLASSIFIED, confidence=0.9)
            ),
        )
        assert processed is True
        async with session_factory() as db:
            reloaded = await db.get(Document, document.id)
            assert reloaded is not None
            run_count = await db.scalar(
                select(func.count()).select_from(ExtractionRun).where(
                    ExtractionRun.document_id == document.id
                )
            )
            obs_count = await db.scalar(
                select(func.count())
                .select_from(AttributeObservation)
                .join(ExtractionRun, AttributeObservation.run_id == ExtractionRun.id)
                .where(ExtractionRun.document_id == document.id)
            )
        # Failed: no run, no observation, document FAILED, type unchanged.
        assert run_count == 0
        assert obs_count == 0
        assert reloaded.status is DocumentStatus.FAILED
        assert reloaded.document_type is DocumentType.UNCLASSIFIED
