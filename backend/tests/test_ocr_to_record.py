"""M22 — OCR ExtractionResult → controlled field extraction → observation → current record.

The headline test drives the REAL local candidate path end to end (rasterize a synthetic PDF →
Tesseract → ExtractionResult → controlled field extractor → AttributeObservation → current
record) and checks the two currently approved attributes and their provenance.

    *** THIS IS A TECHNICAL INTEGRATION TEST. IT IS NOT S-6 EVIDENCE. ***

The PDF is synthetic (authored in-test with Pillow), the values are the project's synthetic test
data — not a real person's document, not the S-6 corpus. Nothing here selects an engine, sets a
threshold, or claims accuracy. Production extraction stays on the unconfigured extractor.

The negative tests are pure (no DB): they feed the field extractor known blocks and prove it does
not guess, preserves multiple candidates, and refuses unsupported attributes.
"""

from __future__ import annotations

import io
import uuid
from typing import Any

import pytest
from ocr_candidates.tesseract_adapter import TesseractExtractor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.db.models import User
from app.db.session import create_session_factory
from app.services.attribute_observation import list_current_attribute_observations
from app.services.current_record import get_current_value
from app.services.document_service import store_document
from app.services.extraction import ExtractedPage, ExtractionResult, TextBlock, TextRegion
from app.services.extraction_store import build_extraction_run
from app.services.field_extraction import build_field_extractor
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, requires_postgres

FULL_NAME = "person.full_name"
DOB = "person.date_of_birth"


# --------------------------------------------------------------------------- helpers (pure)
def _run_from_lines(*lines: tuple[str, float | None]) -> Any:
    """A persisted-shape ExtractionRun graph built from one block per OCR line (no DB)."""
    blocks = tuple(
        TextBlock(
            text=text,
            region=TextRegion(page=1, x=0.1, y=0.1 + i * 0.1, width=0.4, height=0.05),
            confidence=conf,
        )
        for i, (text, conf) in enumerate(lines)
    )
    result = ExtractionResult(
        pages=(ExtractedPage(number=1, text=" / ".join(t for t, _ in lines), blocks=blocks),),
        engine="deterministic-test-double",
        engine_version="1.0",
    )
    return build_extraction_run(document_id=uuid.uuid4(), result=result)


def _extract(*lines: tuple[str, float | None]) -> dict[str, list[str]]:
    """Run the controlled extractor over the lines; return {identifier: [values...]}."""
    out: dict[str, list[str]] = {}
    for candidate in build_field_extractor().extract_fields(_run_from_lines(*lines)):
        out.setdefault(candidate.canonical_identifier, []).append(candidate.value)
    return out


# --------------------------------------------------------------------------- positive (pure)
def test_extracts_both_controlled_attributes_from_table_rows() -> None:
    got = _extract(
        ("Full Name Vedant Santosh Kadam", 0.94),
        ("Date of Birth 24 March 2007", 0.95),
    )
    assert got[FULL_NAME] == ["Vedant Santosh Kadam"]
    assert got[DOB] == ["2007-03-24"]  # normalised to canonical ISO (N-DATE)


@pytest.mark.parametrize(
    ("printed", "iso"),
    [
        ("24 March 2007", "2007-03-24"),
        ("2007-03-24", "2007-03-24"),
        ("1 January 1990", "1990-01-01"),
    ],
)
def test_dob_normalisation_supported_forms(printed: str, iso: str) -> None:
    assert _extract((f"Date of Birth {printed}", 0.9))[DOB] == [iso]


# --------------------------------------------------------------------------- negative (pure)
def test_missing_full_name_yields_no_name_observation() -> None:
    got = _extract(("Date of Birth 24 March 2007", 0.9))
    assert FULL_NAME not in got
    assert got[DOB] == ["2007-03-24"]


def test_missing_dob_yields_no_dob_observation() -> None:
    got = _extract(("Full Name Vedant Santosh Kadam", 0.9))
    assert DOB not in got
    assert got[FULL_NAME] == ["Vedant Santosh Kadam"]


@pytest.mark.parametrize(
    "value",
    ["banana", "31 February 2007", "March 2007", "24 Marchz 2007", "24/03/2007", "2007"],
)
def test_malformed_or_unsupported_date_yields_nothing(value: str) -> None:
    # Unsupported surface form or an impossible calendar date → no observation, no guess.
    assert DOB not in _extract((f"Date of Birth {value}", 0.9))


def test_multiple_candidate_names_are_all_preserved() -> None:
    got = _extract(("Full Name Priya Sharma", 0.9), ("Full Name Riya Verma", 0.8))
    assert got[FULL_NAME] == ["Priya Sharma", "Riya Verma"]  # both kept, none selected


def test_conflicting_dob_candidates_are_all_preserved() -> None:
    got = _extract(("Date of Birth 24 March 2007", 0.9), ("Date of Birth 25 March 2007", 0.9))
    assert got[DOB] == ["2007-03-24", "2007-03-25"]  # both kept for the record to judge


@pytest.mark.parametrize(
    "line",
    [
        "Email Address vedant@example.com",
        "Phone Number 9876543210",
        "Address 12 MG Road Pune",
        "PAN ABCDE1234F",
        "Aadhaar 1234 5678 9012",
        "Some entirely unrelated caption",
    ],
)
def test_unsupported_or_unrelated_lines_produce_no_observations(line: str) -> None:
    # No released canonical attribute covers these, so nothing enters the structured record.
    assert _extract((line, 0.95)) == {}


# --------------------------------------------------------------------------- integration (DB)
pytestmark_note = "the DB test below is gated by requires_postgres"


def _author_profile_pdf() -> bytes:
    """Synthetic profile PDF (image-only) with the two controlled fields on their own lines."""
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    try:
        font = ImageFont.load_default(size=44)
    except TypeError:
        font = ImageFont.load_default()
    image = Image.new("RGB", (800, 320), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 60), "Full Name Vedant Santosh Kadam", fill="black", font=font)
    draw.text((40, 160), "Date of Birth 24 March 2007", fill="black", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PDF")
    return buffer.getvalue()


@requires_postgres
class TestRealOcrToRecord:
    """Real Tesseract + rasterizer → record. NOT S-6 evidence (see module docstring)."""

    @pytest.fixture
    def session_factory(self, db_engine: Any) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(db_engine)

    @pytest.fixture
    def storage(self, db_settings: Settings) -> DocumentStorage:
        return build_document_storage(db_settings)

    async def test_ocr_populates_the_record_with_provenance(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        extractor = TesseractExtractor()
        if not extractor.is_available():
            pytest.skip("Tesseract binary/pytesseract not installed")
        pytest.importorskip("pypdfium2")
        pdf = _author_profile_pdf()

        # Seed a document owned by a user (used only for ownership/provenance wiring).
        async with session_factory() as db:
            user = await db.scalar(select(User).where(User.email == "m22@example.com"))
            if user is None:
                user = User(email="m22@example.com", password_hash="argon2-unused")
                db.add(user)
                await db.commit()
            document = await store_document(
                db, owner=user, source=io.BytesIO(PDF_BYTES), filename="profile.pdf",
                declared_content_type="application/pdf", storage=storage, settings=db_settings,
            )
            user_id, document_id = document.user_id, document.id

        # Candidate path: real OCR on the synthetic PDF → persist run → controlled extraction.
        result = extractor.extract(io.BytesIO(pdf), content_type="application/pdf")
        async with session_factory() as db:
            from app.services.field_extraction import apply_field_extraction

            run = build_extraction_run(document_id=document_id, result=result)
            db.add(run)
            await db.flush()
            await apply_field_extraction(db, run=run, extractor=build_field_extractor())
            await db.commit()

        async with session_factory() as db:
            name = await get_current_value(db, user_id=user_id, canonical_identifier=FULL_NAME)
            dob = await get_current_value(db, user_id=user_id, canonical_identifier=DOB)
            observations = await list_current_attribute_observations(db, document_id=document_id)

        assert name is not None
        assert name.value == "Vedant Santosh Kadam"
        assert name.is_ambiguous is False
        assert dob is not None
        assert dob.value == "2007-03-24"
        assert dob.is_ambiguous is False

        # Provenance is exact and traceable: block → page → run → document; confidence measured.
        by_id = {o.canonical_identifier: o for o in observations}
        for identifier in (FULL_NAME, DOB):
            obs = by_id[identifier]
            assert obs.source_block.page.run.document_id == document_id
            assert obs.source_block.region_x is not None  # normalized bbox retained
            assert obs.confidence is not None  # measured OCR confidence, not invented
            assert 0.0 < obs.confidence <= 1.0
