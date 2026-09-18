"""M21 — local PDF rasterization for the OCR candidate path. TECHNICAL tests, NOT S-6 evidence.

Fixtures are synthetic image-only PDFs authored in-test with Pillow (scan-style: text rendered
to a bitmap, no text layer) — never real personal documents, never S-6 corpus. Nothing here is
an evaluation score, sets a threshold, or selects an engine.

The rasterizer/adapter are exercised both for real (pypdfium2 + Tesseract are installed) and
deterministically via fakes/injected readers (cleanup, missing-dependency, structure), so both
success and failure branches are covered without depending on the environment for the failure
paths.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import socket
import sys
import types
from pathlib import Path

import pytest
from ocr_candidates.pdf_rasterizer import rasterize_pdf
from ocr_candidates.tesseract_adapter import (
    ImageWords,
    TesseractExtractor,
    Word,
    result_from_pages,
)

from app.core.config import Environment, Settings
from app.core.errors import DocumentExtractionError
from app.evaluation import corpus as c
from app.evaluation.corpus import Corpus, CorpusItem
from app.evaluation.runner import run_evaluation
from app.services.extraction import build_document_extractor

PDF = "application/pdf"


def _make_pdf(pages_text: list[str], *, size: tuple[int, int] = (600, 220)) -> bytes:
    """Author a synthetic multi-page image PDF with Pillow (skips if Pillow is absent)."""
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    try:
        font = ImageFont.load_default(size=48)
    except TypeError:  # older Pillow without a sized default font
        font = ImageFont.load_default()

    images = []
    for text in pages_text:
        image = Image.new("RGB", size, "white")
        ImageDraw.Draw(image).text((30, 80), text, fill="black", font=font)
        images.append(image)
    buffer = io.BytesIO()
    images[0].save(buffer, format="PDF", save_all=True, append_images=images[1:])
    return buffer.getvalue()


# --------------------------------------------------------------- rasterizer: real happy path
def test_rasterize_pdf_renders_every_page_in_order() -> None:
    pytest.importorskip("pypdfium2")
    images = rasterize_pdf(io.BytesIO(_make_pdf(["ONE", "TWO", "THREE"])), scale=1.5)
    try:
        assert len(images) == 3  # multi-page output
        width, height = images[0].size
        assert width > 0  # dimensions exposed/preserved
        assert height > 0
        assert all(image.size == (width, height) for image in images)  # consistent page size
    finally:
        for image in images:
            image.close()


# ------------------------------------------------------------------ rasterizer: failure paths
def test_rasterize_pdf_rejects_an_empty_document() -> None:
    with pytest.raises(DocumentExtractionError):
        rasterize_pdf(io.BytesIO(b""))


def test_rasterize_pdf_rejects_a_malformed_document() -> None:
    pytest.importorskip("pypdfium2")
    with pytest.raises(DocumentExtractionError):
        rasterize_pdf(io.BytesIO(b"this is not a pdf at all"))


def test_rasterize_pdf_reports_a_missing_renderer_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "pypdfium2", None)  # force ImportError
    with pytest.raises(DocumentExtractionError):
        rasterize_pdf(io.BytesIO(b"%PDF-1.4 anything"))


def test_rasterize_pdf_cleans_up_handles_when_a_page_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deterministic cleanup: the document and page handles are closed even on a render error."""
    log: list[str] = []

    class FakePage:
        def render(self, *, scale: float) -> object:
            raise RuntimeError("render boom")

        def close(self) -> None:
            log.append("page.close")

    class FakeDoc:
        def __init__(self, _data: bytes) -> None:
            pass

        def __len__(self) -> int:
            return 1

        def __getitem__(self, _index: int) -> FakePage:
            return FakePage()

        def close(self) -> None:
            log.append("doc.close")

    fake = types.ModuleType("pypdfium2")
    fake.PdfDocument = FakeDoc  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pypdfium2", fake)

    with pytest.raises(DocumentExtractionError):
        rasterize_pdf(io.BytesIO(b"%PDF-1.4 anything"))
    assert "page.close" in log
    assert "doc.close" in log


# ------------------------------------------------------- adapter PDF path: pure/deterministic
def test_result_from_pages_preserves_order_structure_and_confidence() -> None:
    reads = [
        ImageWords([Word("ONE", 90.0, 0, 0, 50, 20)], 1000, 500),
        ImageWords([Word("TWO", 80.0, 10, 10, 60, 20)], 1000, 500),
    ]
    result = result_from_pages(reads, engine_version="5.5.3")
    assert result.page_count == 2
    assert (result.pages[0].number, result.pages[1].number) == (1, 2)
    assert result.pages[0].text == "ONE"
    assert result.pages[1].text == "TWO"
    assert result.pages[0].blocks[0].confidence == pytest.approx(0.9)
    assert result.pages[0].blocks[0].region is not None  # normalized bbox present
    assert result.metadata["page_count"] == "2"


def test_extract_pdf_uses_an_injected_page_reader() -> None:
    def pages(_source: object) -> list[ImageWords]:
        return [
            ImageWords([Word("P1", 95.0, 0, 0, 10, 10)], 100, 100),
            ImageWords([Word("P2", 95.0, 0, 0, 10, 10)], 100, 100),
        ]

    result = TesseractExtractor(page_reader=pages).extract(io.BytesIO(b"x"), content_type=PDF)
    assert result.page_count == 2
    assert result.engine == "tesseract"


def test_missing_tesseract_dependency_on_the_pdf_path_is_honest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("pypdfium2")
    data = _make_pdf(["X"])
    monkeypatch.setitem(sys.modules, "pytesseract", None)  # rasterizes, then OCR dep missing
    with pytest.raises(DocumentExtractionError):
        TesseractExtractor().extract(io.BytesIO(data), content_type=PDF)


# --------------------------------------------------------------- adapter PDF path: real engine
def test_tesseract_reads_a_multipage_pdf_end_to_end() -> None:
    extractor = TesseractExtractor()
    if not extractor.is_available():
        pytest.skip("Tesseract binary/pytesseract not installed in this environment")
    pytest.importorskip("pypdfium2")

    result = extractor.extract(io.BytesIO(_make_pdf(["HELLO ALPHA", "HELLO BRAVO"])),
                               content_type=PDF)
    assert result.page_count == 2
    assert result.engine == "tesseract"
    # Page order is preserved through rasterization + OCR.
    assert "ALPHA" in result.pages[0].text.upper()
    assert "BRAVO" in result.pages[1].text.upper()
    # Confidence is carried where Tesseract supplies it.
    assert any(b.confidence is not None for page in result.pages for b in page.blocks)


def test_the_pdf_path_makes_no_network_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = TesseractExtractor()
    if not extractor.is_available():
        pytest.skip("Tesseract binary/pytesseract not installed in this environment")
    pytest.importorskip("pypdfium2")
    data = _make_pdf(["NETLESS"])

    def no_sockets(*_a: object, **_k: object) -> None:
        raise AssertionError("PDF rasterization + OCR must not open a network socket")

    monkeypatch.setattr(socket, "socket", no_sockets)
    result = extractor.extract(io.BytesIO(data), content_type=PDF)
    assert result.page_count == 1


# ------------------------------------------------------------------------ production / leakage
def test_production_builder_still_returns_the_unconfigured_extractor(tmp_path: Path) -> None:
    extractor = build_document_extractor(
        Settings(
            environment=Environment.TEST,
            database_url="postgresql://u:p@localhost:5432/none",
            document_storage_root=tmp_path / "documents",
        )
    )
    assert extractor.name == "unconfigured"
    assert extractor.is_available() is False


def _valid_pdf_corpus(root: Path) -> Corpus:
    """A tiny VALID held-out corpus with one PDF document (synthetic; NOT S-6 evidence)."""
    body = _make_pdf(["Vedant"])
    c.documents_dir(root).mkdir(parents=True, exist_ok=True)
    (c.documents_dir(root) / "pdf1.pdf").write_bytes(body)
    c.annotations_dir(root).mkdir(parents=True, exist_ok=True)
    c.annotation_path(root, "pdf1").write_text(
        json.dumps({"document_id": "pdf1", "expected": [{"text": "Vedant", "page": 1}]}),
        encoding="utf-8",
    )
    item = CorpusItem(
        id="pdf1", document_type="aadhaar", page_count=1, source_category="volunteer",
        consent_status="consented", annotation_status="annotated", split="held_out",
        deidentification_status="deidentified", checksum_sha256=hashlib.sha256(body).hexdigest(),
    )
    corpus = Corpus(version="pdf-smoke-v1", items=(item,))
    c.save_corpus(root, corpus)
    return corpus


def test_the_m19_runner_can_drive_the_candidate_on_a_pdf_item(tmp_path: Path) -> None:
    # A .pdf corpus item flows: runner → adapter → (rasterizer) → OCR → ExtractionResult →
    # metrics. Deterministic via an injected page reader — a WIRING check, not an OCR score.
    corpus = _valid_pdf_corpus(tmp_path)

    def pages(_source: object) -> list[ImageWords]:
        return [ImageWords([Word("Vedant", 99.0, 0, 0, 100, 40)], 1000, 500)]

    engine = TesseractExtractor(page_reader=pages)
    result = run_evaluation(corpus, tmp_path, engine)

    assert result.engine_name == "tesseract"
    assert result.failures == []
    assert result.metrics["overall"]["field_exact_match_accuracy"] == 1.0
    assert "Vedant" not in result.to_json()  # PII-free result


def test_no_app_module_imports_the_pdf_renderer_or_ocr_engine() -> None:
    app_root = Path(__file__).resolve().parents[1] / "app"
    pattern = re.compile(r"^\s*(?:from|import)\s+(pypdfium2|pytesseract)\b", re.MULTILINE)
    offenders = [
        path.name
        for path in app_root.rglob("*.py")
        if pattern.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == []
