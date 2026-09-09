"""Sprint 4 D-09 — the durable processing pipeline.

These tests are about *orchestration*, not OCR. No engine is configured, so the
``UnconfiguredExtractor`` drives the failure path end to end, and a small recording
double stands in only to prove the pipeline depends on the D-01 seam rather than on
any concrete engine. Nothing here asserts a document was read correctly, because
nothing can read one yet (AR-AST-008).

They need a real PostgreSQL: the claim uses ``SELECT … FOR UPDATE SKIP LOCKED`` and
the model uses native UUID and enum types, none of which a stand-in reproduces. They
skip — never silently pass — when ``TEST_DATABASE_URL`` is unset.
"""

from __future__ import annotations

import asyncio
import io
from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.errors import (
    DocumentNotReprocessableError,
    DuplicateDocumentError,
    ExtractionNotConfiguredError,
)
from app.db.models import Document, DocumentStatus, JobState, ProcessingJob, User
from app.db.session import create_session_factory
from app.services import document_service, processing
from app.services.document_service import request_reprocess, store_document
from app.services.extraction import ExtractedPage, ExtractionResult, UnconfiguredExtractor
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, requires_postgres

pytestmark = requires_postgres


class RecordingExtractor:
    """A stand-in engine that succeeds, used only to prove the seam is substitutable."""

    name = "recording-test-double"
    version = "0"

    def is_available(self) -> bool:
        return True

    def extract(self, source: Any, *, content_type: str) -> ExtractionResult:
        return ExtractionResult(
            pages=(ExtractedPage(number=1, text="test double"),),
            engine=self.name,
            engine_version=self.version,
        )


@pytest.fixture
def session_factory(db_engine: Any) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(db_engine)


@pytest.fixture
def storage(db_settings: Settings) -> DocumentStorage:
    return build_document_storage(db_settings)


def _with_max_attempts(db_settings: Settings, attempts: int) -> Settings:
    """A copy of the test settings with a specific retry ceiling."""
    return db_settings.model_copy(update={"worker_max_attempts": attempts})


async def _make_user(db: AsyncSession, email: str = "worker@example.com") -> User:
    user = User(email=email, password_hash="argon2-hash-not-exercised-here")
    db.add(user)
    await db.commit()
    return user


async def _seed_document(
    session_factory: async_sessionmaker[AsyncSession],
    storage: DocumentStorage,
    settings: Settings,
    *,
    content: bytes = PDF_BYTES,
) -> Document:
    """Create a user and upload one document — its job created in the same transaction."""
    async with session_factory() as db:
        user = await _make_user(db)
        return await store_document(
            db,
            owner=user,
            source=io.BytesIO(content),
            filename="marksheet.pdf",
            declared_content_type="application/pdf",
            storage=storage,
            settings=settings,
        )


async def _load(
    session_factory: async_sessionmaker[AsyncSession], document_id: Any
) -> tuple[Document, ProcessingJob]:
    """Read a document and its job back in a fresh session."""
    async with session_factory() as db:
        document = await db.get(Document, document_id)
        assert document is not None
        job = await db.scalar(
            select(ProcessingJob).where(ProcessingJob.document_id == document_id)
        )
        assert job is not None
        return document, job


async def _count(session_factory: async_sessionmaker[AsyncSession], model: Any) -> int:
    async with session_factory() as db:
        return await db.scalar(select(func.count()).select_from(model)) or 0


class TestTransactionalCreation:
    async def test_document_and_job_are_created_together(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)

        loaded, job = await _load(session_factory, document.id)
        assert loaded.status is DocumentStatus.QUEUED
        assert loaded.failure_reason is None
        assert job.state is JobState.PENDING
        assert job.attempts == 0
        assert job.max_attempts == db_settings.worker_max_attempts
        assert job.document_id == document.id

    async def test_rollback_leaves_no_orphan_job(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The document and its job share one transaction — a failed upload persists neither.

        The duplicate pre-check is disabled so the second upload reaches the unique
        index and rolls back on the ``IntegrityError``, which is the real path that
        must not leave a job whose document was never committed.
        """
        first = await _seed_document(session_factory, storage, db_settings)

        async def _no_precheck(*_a: Any, **_k: Any) -> None:
            return None

        monkeypatch.setattr(document_service, "_existing_by_checksum", _no_precheck)

        async with session_factory() as db:
            user = await db.get(User, first.user_id)
            assert user is not None
            with pytest.raises(DuplicateDocumentError):
                await store_document(
                    db,
                    owner=user,
                    source=io.BytesIO(PDF_BYTES),  # identical bytes -> same checksum
                    filename="again.pdf",
                    declared_content_type="application/pdf",
                    storage=storage,
                    settings=db_settings,
                )

        # Exactly the first document and its one job survive; the loser left nothing.
        assert await _count(session_factory, Document) == 1
        assert await _count(session_factory, ProcessingJob) == 1


class TestClaiming:
    async def test_claim_moves_document_to_processing(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)

        async with session_factory() as db:
            claimed = await processing.claim_next_job(
                db, claim_timeout_seconds=300, now=datetime.now(UTC)
            )
        assert claimed is not None

        loaded, job = await _load(session_factory, document.id)
        assert loaded.status is DocumentStatus.PROCESSING
        assert job.state is JobState.CLAIMED
        assert job.attempts == 1

    async def test_concurrent_workers_cannot_claim_the_same_job(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """SKIP LOCKED: two workers racing for one job — exactly one takes it."""
        document = await _seed_document(session_factory, storage, db_settings)
        now = datetime.now(UTC)

        async with session_factory() as db_a, session_factory() as db_b:
            first, second = await asyncio.gather(
                processing.claim_next_job(db_a, claim_timeout_seconds=300, now=now),
                processing.claim_next_job(db_b, claim_timeout_seconds=300, now=now),
            )

        claimed = [job for job in (first, second) if job is not None]
        assert len(claimed) == 1

        _, job = await _load(session_factory, document.id)
        assert job.state is JobState.CLAIMED
        assert job.attempts == 1


class TestExecution:
    async def test_queued_to_processing_to_failed_against_unconfigured(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = _with_max_attempts(db_settings, 1)
        document = await _seed_document(session_factory, storage, settings)

        worked = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=UnconfiguredExtractor(),
            settings=settings,
        )
        assert worked is True

        loaded, job = await _load(session_factory, document.id)
        assert loaded.status is DocumentStatus.FAILED
        assert job.state is JobState.FAILED
        assert job.attempts == 1

    async def test_failure_states_a_reason_and_keeps_the_original(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = _with_max_attempts(db_settings, 1)
        document = await _seed_document(session_factory, storage, settings)

        await processing.process_one(
            session_factory,
            storage=storage,
            extractor=UnconfiguredExtractor(),
            settings=settings,
        )

        loaded, _ = await _load(session_factory, document.id)
        # FR-OCR-009: what failed is stated, in the safe words of the error itself.
        assert loaded.failure_reason == ExtractionNotConfiguredError().detail
        # ...and the original file is untouched and still readable (BR-013).
        handle = storage.open(loaded.storage_key)
        try:
            assert handle.read() == PDF_BYTES
        finally:
            handle.close()

    async def test_retry_is_bounded(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = _with_max_attempts(db_settings, 2)
        document = await _seed_document(session_factory, storage, settings)
        extractor = UnconfiguredExtractor()

        # First attempt fails but has a retry left: back to the queue.
        await processing.process_one(
            session_factory, storage=storage, extractor=extractor, settings=settings
        )
        loaded, job = await _load(session_factory, document.id)
        assert job.state is JobState.PENDING
        assert job.attempts == 1
        assert loaded.status is DocumentStatus.QUEUED

        # Second attempt exhausts the ceiling: terminal failure.
        await processing.process_one(
            session_factory, storage=storage, extractor=extractor, settings=settings
        )
        loaded, job = await _load(session_factory, document.id)
        assert job.state is JobState.FAILED
        assert job.attempts == 2
        assert loaded.status is DocumentStatus.FAILED

        # A terminal job is not runnable: nothing more is attempted.
        worked = await processing.process_one(
            session_factory, storage=storage, extractor=extractor, settings=settings
        )
        assert worked is False
        _, job = await _load(session_factory, document.id)
        assert job.attempts == 2

    async def test_a_substituted_engine_drives_success(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """The pipeline depends only on the D-01 seam: swap the extractor, get success.

        This is the whole of the "no engine leaks into the pipeline" guarantee that
        can be made before an engine exists — the pipeline never names one, so any
        DocumentExtractor drives it.
        """
        document = await _seed_document(session_factory, storage, db_settings)

        worked = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=RecordingExtractor(),
            settings=db_settings,
        )
        assert worked is True

        loaded, job = await _load(session_factory, document.id)
        assert loaded.status is DocumentStatus.READY
        assert loaded.failure_reason is None
        assert job.state is JobState.SUCCEEDED


class TestReprocess:
    async def test_reprocess_returns_a_terminal_document_to_queued(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = _with_max_attempts(db_settings, 1)
        document = await _seed_document(session_factory, storage, settings)
        await processing.process_one(
            session_factory,
            storage=storage,
            extractor=UnconfiguredExtractor(),
            settings=settings,
        )

        async with session_factory() as db:
            reprocessed = await request_reprocess(
                db, user_id=document.user_id, document_id=document.id
            )
        assert reprocessed.status is DocumentStatus.QUEUED

        loaded, job = await _load(session_factory, document.id)
        assert loaded.status is DocumentStatus.QUEUED
        assert loaded.failure_reason is None
        assert job.state is JobState.PENDING
        assert job.attempts == 0
        assert job.last_error is None

        # And it is runnable again.
        worked = await processing.process_one(
            session_factory,
            storage=storage,
            extractor=RecordingExtractor(),
            settings=settings,
        )
        assert worked is True

    async def test_reprocess_refuses_a_document_still_in_flight(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)  # QUEUED

        async with session_factory() as db:
            with pytest.raises(DocumentNotReprocessableError):
                await request_reprocess(
                    db, user_id=document.user_id, document_id=document.id
                )


class TestNoLeaksOrDisclosure:
    async def test_job_records_hold_no_document_content_or_personal_values(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """NFR-PRIV-007: the job's error and the document's reason are safe strings only."""
        settings = _with_max_attempts(db_settings, 1)
        document = await _seed_document(session_factory, storage, settings)
        await processing.process_one(
            session_factory,
            storage=storage,
            extractor=UnconfiguredExtractor(),
            settings=settings,
        )

        loaded, job = await _load(session_factory, document.id)
        # The internal error is a class name and message — not bytes, not a key.
        assert job.last_error is not None
        assert "ExtractionNotConfiguredError" in job.last_error
        assert loaded.storage_key not in job.last_error
        assert loaded.original_filename not in job.last_error
        # The user-facing reason is exactly the error's safe detail.
        assert loaded.failure_reason == ExtractionNotConfiguredError().detail

    def test_the_pipeline_imports_only_the_extraction_seam(self) -> None:
        """processing.py and worker.py name the abstractions, never a concrete engine."""
        from pathlib import Path

        # The engine-neutral seams the pipeline is allowed to depend on: the OCR
        # extraction seam (D-01) and the field-extraction seam (blocks → attributes).
        # Neither names a concrete engine, which is the property this guards.
        allowed_seams = ("app.services.extraction", "app.services.field_extraction")
        app_root = Path(__file__).resolve().parents[1] / "app"
        for module in ("services/processing.py", "worker.py"):
            source = (app_root / module).read_text(encoding="utf-8")
            for line in source.splitlines():
                if "import" in line and "extraction" in line:
                    assert any(seam in line for seam in allowed_seams)
