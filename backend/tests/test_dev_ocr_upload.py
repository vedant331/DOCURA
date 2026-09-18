"""M23 — DEV/EVALUATION-ONLY OCR activation for the normal upload/processing flow.

    *** DEV OCR INTEGRATION TEST — NOT S-6 EVIDENCE. ***

With DOCURA_OCR_ENGINE=tesseract, the SAME document-processing pipeline (claim job → extract →
persist run → classify → field extract → status) runs the M20/M21 Tesseract candidate on a
synthetic PDF and populates the record for the two controlled attributes. The default (unset)
stays on the unconfigured extractor, and these tests prove production is untouched. No engine is
selected, no threshold set, no value hard-coded — values come from real OCR.
"""

from __future__ import annotations

import io
import sys
import uuid
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import ConfigurationError, Environment, OcrEngine, Settings
from app.db.models import AttributeObservation, Document, DocumentStatus, ExtractionRun, User
from app.db.session import create_session_factory
from app.services.classification import build_document_classifier
from app.services.current_record import get_current_value
from app.services.document_service import store_document
from app.services.extraction import build_document_extractor
from app.services.field_extraction import build_field_extractor
from app.services.processing import process_one
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import requires_postgres

FULL_NAME = "person.full_name"
DOB = "person.date_of_birth"


def _settings(tmp_path: Any, engine: OcrEngine) -> Settings:
    return Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "documents",
        ocr_engine=engine,
    )


# --------------------------------------------------------------- config switch (no DB)
def test_default_builds_the_unconfigured_extractor(tmp_path: Any) -> None:
    extractor = build_document_extractor(_settings(tmp_path, OcrEngine.UNCONFIGURED))
    assert extractor.name == "unconfigured"
    assert extractor.is_available() is False


def test_opt_in_builds_the_tesseract_candidate_when_available(tmp_path: Any) -> None:
    settings = _settings(tmp_path, OcrEngine.TESSERACT)
    try:
        extractor = build_document_extractor(settings)
    except ConfigurationError:
        pytest.skip("Tesseract candidate not installed in this environment")
    assert extractor.name == "tesseract"
    assert extractor.is_available() is True


def test_opt_in_without_the_dependency_is_a_loud_config_error(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Force the candidate unavailable regardless of what is installed — no silent fallback.
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    with pytest.raises(ConfigurationError):
        build_document_extractor(_settings(tmp_path, OcrEngine.TESSERACT))


def test_an_unrecognised_engine_value_is_rejected_at_load(tmp_path: Any) -> None:
    # pydantic validates the enum, so an unsupported value never reaches the builder.
    with pytest.raises(ValidationError):
        Settings(
            environment=Environment.TEST,
            database_url="postgresql://u:p@localhost:5432/none",
            document_storage_root=tmp_path / "documents",
            ocr_engine="paddleocr",
        )


# --------------------------------------------------------------------- upload flow (DB)
def _profile_pdf() -> bytes:
    """Synthetic profile PDF; unique per call so re-runs never collide on the dedup checksum."""
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    try:
        font = ImageFont.load_default(size=44)
    except TypeError:
        font = ImageFont.load_default()
    image = Image.new("RGB", (820, 360), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 60), "Full Name Vedant Santosh Kadam", fill="black", font=font)
    draw.text((40, 160), "Date of Birth 24 March 2007", fill="black", font=font)
    # A small unique marker keeps the file's bytes distinct across runs (dedup safety); it is
    # not a controlled field, so it produces no observation.
    draw.text((40, 300), f"ref {uuid.uuid4()}", fill="black", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PDF")
    return buffer.getvalue()


@requires_postgres
class TestDevOcrUploadFlow:
    @pytest.fixture
    def session_factory(self, db_engine: Any) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(db_engine)

    @pytest.fixture
    def storage(self, db_settings: Settings) -> DocumentStorage:
        return build_document_storage(db_settings)

    async def _upload(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        settings: Settings,
        *,
        email: str,
        content: bytes,
    ) -> tuple[uuid.UUID, uuid.UUID]:
        async with session_factory() as db:
            user = await db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(email=email, password_hash="argon2-unused")
                db.add(user)
                await db.commit()
            document = await store_document(
                db, owner=user, source=io.BytesIO(content), filename="profile.pdf",
                declared_content_type="application/pdf", storage=storage, settings=settings,
            )
            return document.user_id, document.id

    async def test_dev_ocr_upload_populates_record_through_normal_pipeline(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = db_settings.model_copy(update={"ocr_engine": OcrEngine.TESSERACT})
        extractor = build_document_extractor(settings)
        if extractor.name != "tesseract":  # pragma: no cover - defensive
            pytest.skip("Tesseract candidate not available")
        pytest.importorskip("pypdfium2")

        user_id, document_id = await self._upload(
            session_factory, storage, settings, email="m23-dev@example.com",
            content=_profile_pdf(),
        )

        # The normal pipeline unit — same one the worker loops — with the DEV extractor.
        processed = await process_one(
            session_factory,
            storage=storage,
            extractor=extractor,
            settings=settings,
            classifier=build_document_classifier(),
            field_extractor=build_field_extractor(),
        )
        assert processed is True

        async with session_factory() as db:
            document = await db.get(Document, document_id)
            name = await get_current_value(db, user_id=user_id, canonical_identifier=FULL_NAME)
            dob = await get_current_value(db, user_id=user_id, canonical_identifier=DOB)

        assert document is not None
        assert document.status == DocumentStatus.READY  # existing success status
        assert name is not None
        assert name.value == "Vedant Santosh Kadam"  # from real OCR, not hard-coded
        assert name.is_ambiguous is False
        assert dob is not None
        assert dob.value == "2007-03-24"
        # Provenance travelled the normal chain: observation → block → page → run → document.
        obs = name.observations[0]
        assert obs.source_block.page.run.document_id == document_id
        assert obs.confidence is not None

    async def test_default_upload_does_not_invoke_tesseract(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        # Default settings → unconfigured extractor → the success path is never reached, so no
        # extraction run and no observation exist. This is the production posture.
        settings = db_settings.model_copy(update={"worker_max_attempts": 1})
        assert build_document_extractor(settings).name == "unconfigured"

        _user_id, document_id = await self._upload(
            session_factory, storage, settings, email="m23-prod@example.com",
            content=_profile_pdf(),
        )
        processed = await process_one(
            session_factory,
            storage=storage,
            extractor=build_document_extractor(settings),
            settings=settings,
            classifier=build_document_classifier(),
            field_extractor=build_field_extractor(),
        )
        assert processed is True

        async with session_factory() as db:
            document = await db.get(Document, document_id)
            runs = await db.scalar(
                select(func.count()).select_from(ExtractionRun).where(
                    ExtractionRun.document_id == document_id
                )
            )
            observations = await db.scalar(
                select(func.count())
                .select_from(AttributeObservation)
                .join(ExtractionRun, AttributeObservation.run_id == ExtractionRun.id)
                .where(ExtractionRun.document_id == document_id)
            )
        assert document is not None
        assert document.status == DocumentStatus.FAILED  # unconfigured extractor fails honestly
        assert runs == 0
        assert observations == 0
