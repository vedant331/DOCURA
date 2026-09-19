"""DEMO dynamic key/value extraction from OCR line blocks — dev/evaluation only.

    *** DEMO INTEGRATION TEST — NOT S-6 EVIDENCE, NOT production attribute release. ***

Proves the demo field extractor discovers common labelled attributes from OCR output using the
data-driven synonym vocabulary, normalises dates, keeps provenance/confidence, and does not
guess. Values are supplied by (real or synthetic) OCR text, never hard-coded in the extractor.
"""

from __future__ import annotations

import io
import uuid
from typing import Any

import pytest

from app.core.config import Environment, OcrEngine, Settings
from app.services.extraction import ExtractedPage, ExtractionResult, TextBlock, TextRegion
from app.services.extraction_store import build_extraction_run
from app.services.field_extraction import (
    ControlledFieldExtractor,
    DemoFieldExtractor,
    build_field_extractor,
)


def _run(*lines: str) -> Any:
    """A persisted-shape run with one block per OCR line (region + confidence present)."""
    blocks = tuple(
        TextBlock(
            text=t,
            region=TextRegion(page=1, x=0.1, y=0.1 + i * 0.05, width=0.5, height=0.03),
            confidence=0.9,
        )
        for i, t in enumerate(lines)
    )
    result = ExtractionResult(
        pages=(ExtractedPage(number=1, text=" / ".join(lines), blocks=blocks),),
        engine="demo-test-double",
        engine_version="1",
    )
    return build_extraction_run(document_id=uuid.uuid4(), result=result)


def _extract(*lines: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in DemoFieldExtractor().extract_fields(_run(*lines)):
        out[c.canonical_identifier] = c.value
    return out


# ------------------------------------------------------------------ builder / production default
def test_builder_defaults_to_controlled_extractor() -> None:
    assert isinstance(build_field_extractor(), ControlledFieldExtractor)
    prod = Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root="var/x",
        demo_mode=False,
    )
    assert isinstance(build_field_extractor(prod), ControlledFieldExtractor)


def test_builder_uses_demo_extractor_only_under_demo_mode(tmp_path: Any) -> None:
    demo = Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "docs",
        ocr_engine=OcrEngine.TESSERACT,
        demo_mode=True,
    )
    assert isinstance(build_field_extractor(demo), DemoFieldExtractor)


# --------------------------------------------------------------------------- extraction (pure)
def test_extracts_all_common_demo_attributes() -> None:
    got = _extract(
        "Full Name: Vedant Santosh Kadam",
        "Date of Birth: 24 March 2007",
        "Age: 19",
        "Email: example@gmail.com",
        "Phone Number: 9876543210",
        "PAN Number: ABCDE1234F",
        "Aadhaar Number: 1234 5678 9012",
        "Address: Mumbai, Maharashtra",
    )
    assert got == {
        "person.full_name": "Vedant Santosh Kadam",
        "person.date_of_birth": "2007-03-24",  # normalised to ISO (N-DATE)
        "person.age": "19",
        "person.email": "example@gmail.com",
        "person.phone": "9876543210",
        "identity.pan_number": "ABCDE1234F",
        "identity.aadhaar_number": "1234 5678 9012",
        "person.address": "Mumbai, Maharashtra",
    }


def test_recognises_synonyms_and_separators() -> None:
    assert _extract("UIDAI Number: 1111 2222 3333")["identity.aadhaar_number"] == "1111 2222 3333"
    assert _extract("Permanent Account Number - AAAAA0000A")["identity.pan_number"] == "AAAAA0000A"
    assert _extract("Mobile 9998887776")["person.phone"] == "9998887776"  # space-separated
    assert _extract("DOB: 1 January 1990")["person.date_of_birth"] == "1990-01-01"


def test_label_only_line_takes_the_next_line_as_value() -> None:
    got = _extract("Full Name", "Vedant Santosh Kadam", "Email", "a@b.com")
    assert got["person.full_name"] == "Vedant Santosh Kadam"
    assert got["person.email"] == "a@b.com"


def test_unrelated_lines_and_bad_dates_are_ignored() -> None:
    got = _extract(
        "Personal Details",
        "This document is synthetic",
        "Date of Birth: banana",  # unparseable date → no DOB observation
        "Reference 12345",
    )
    assert got == {}


def test_provenance_and_confidence_preserved() -> None:
    cands = DemoFieldExtractor().extract_fields(_run("PAN Number: ABCDE1234F"))
    assert len(cands) == 1
    assert cands[0].source_block.text == "PAN Number: ABCDE1234F"
    assert cands[0].confidence == pytest.approx(0.9)  # the block's OCR confidence, unchanged


# ------------------------------------------------------------------------- real OCR (skips)
def test_real_ocr_to_demo_record() -> None:
    from ocr_candidates.tesseract_adapter import TesseractExtractor

    extractor = TesseractExtractor()
    if not extractor.is_available():
        pytest.skip("Tesseract not installed")
    pytest.importorskip("pypdfium2")
    pil = pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    try:
        font = ImageFont.load_default(size=36)
    except TypeError:
        font = ImageFont.load_default()
    lines = ["Full Name: Vedant Santosh Kadam", "PAN Number: ABCDE1234F"]
    image = Image.new("RGB", (900, 220), "white")
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((40, 40 + i * 80), line, fill="black", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)

    result = extractor.extract(buffer, content_type="application/pdf")
    run = build_extraction_run(document_id=uuid.uuid4(), result=result)
    got = {c.canonical_identifier: c.value for c in DemoFieldExtractor().extract_fields(run)}
    assert got.get("person.full_name") == "Vedant Santosh Kadam"  # from OCR, not hard-coded
    assert got.get("identity.pan_number") == "ABCDE1234F"
    assert pil is not None
