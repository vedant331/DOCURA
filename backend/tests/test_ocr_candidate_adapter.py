"""M20 — Tesseract candidate adapter, for TECHNICAL SMOKE TESTING only.

Nothing here is an S-6 evaluation result. These tests prove the *mechanics*: that a real
candidate can sit behind the ``DocumentExtractor`` seam, produce the seam's engine-neutral
result, fail honestly, run without network access, and be driven by the M19 harness — and
that production is untouched. No threshold is set and no extraction quality is claimed
(AR-AST-008: quality claims require the held-out corpus, which does not exist).

The adapter is exercised without the Tesseract binary by injecting a deterministic
``word_reader`` (a stand-in for the real ``pytesseract`` call). One test runs the *real*
engine and skips when it is not installed.
"""

from __future__ import annotations

import hashlib
import io
import json
import socket
import sys
from pathlib import Path

import pytest
from ocr_candidates.tesseract_adapter import (
    ImageWords,
    TesseractExtractor,
    Word,
    WordReader,
    _words_from_tsv_dict,
    result_from_words,
)

from app.core.config import Environment, Settings
from app.core.errors import DocumentExtractionError
from app.evaluation import corpus as c
from app.evaluation.corpus import Corpus, CorpusItem
from app.evaluation.engines import EngineNotInstalledError, build_engine
from app.evaluation.runner import run_evaluation
from app.services.extraction import DocumentExtractor, build_document_extractor

PNG = "image/png"


def _real_tesseract_available() -> bool:
    """Ground-truth probe: is pytesseract importable AND the Tesseract binary runnable?

    Independent of the adapter so the availability tests are environment-aware rather than
    hard-coding whether Tesseract happens to be installed on this machine.
    """
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
    except Exception:
        return False
    return True


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "documents",
    )


def _reader(words: list[Word], *, w: int = 1000, h: int = 500) -> WordReader:
    def read(_source: object, _content_type: str) -> ImageWords:
        return ImageWords(words=words, image_width=w, image_height=h)

    return read


# --------------------------------------------------------------------------- construction
def test_the_adapter_satisfies_the_document_extractor_protocol() -> None:
    assert isinstance(TesseractExtractor(word_reader=_reader([])), DocumentExtractor)


def test_injected_reader_is_always_available() -> None:
    # An injected reader stands in for the engine, so the adapter is usable with no binary.
    assert TesseractExtractor(word_reader=_reader([])).is_available() is True


def test_bare_adapter_availability_matches_the_environment() -> None:
    # Environment-aware: True where the real Tesseract dependency is installed, False otherwise.
    assert TesseractExtractor().is_available() is _real_tesseract_available()


def test_is_available_is_false_when_the_dependency_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Deterministic unavailable branch without uninstalling Tesseract: force the import to fail.
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    assert TesseractExtractor().is_available() is False


# ----------------------------------------------------------------------------- successful
def test_result_from_words_produces_the_engine_neutral_contract() -> None:
    read = ImageWords(
        words=[
            Word(text="Vedant", conf=96.0, left=100, top=50, width=200, height=40),
            Word(text="", conf=-1.0, left=0, top=0, width=0, height=0),  # non-word: dropped
        ],
        image_width=1000,
        image_height=500,
    )
    result = result_from_words(read, engine_version="5.3.0")

    assert result.engine == "tesseract"
    assert result.engine_version == "5.3.0"
    assert result.page_count == 1
    assert result.text == "Vedant"
    (block,) = result.pages[0].blocks
    assert block.text == "Vedant"
    assert block.confidence == pytest.approx(0.96)
    assert block.region is not None
    assert block.region.x == pytest.approx(0.1)  # 100 / 1000
    assert block.region.y == pytest.approx(0.1)  # 50 / 500
    assert block.region.width == pytest.approx(0.2)
    assert block.region.height == pytest.approx(0.08)


def test_extract_reads_a_supported_image_through_the_seam() -> None:
    extractor = TesseractExtractor(
        word_reader=_reader([Word("Kadam", 88.0, 10, 10, 50, 20)])
    )
    result = extractor.extract(io.BytesIO(b"fake-png-bytes"), content_type=PNG)
    assert result.text == "Kadam"
    assert result.pages[0].blocks[0].confidence == pytest.approx(0.88)


def test_a_single_image_is_one_page() -> None:
    # Tesseract reads one image at a time; the adapter models that as a one-page document
    # (multi-page PDFs are out of scope, M20 §4).
    result = TesseractExtractor(word_reader=_reader([Word("A", 50.0, 0, 0, 10, 10)])).extract(
        io.BytesIO(b"x"), content_type=PNG
    )
    assert result.page_count == 1


# -------------------------------------------------------------------------------- parsing
def test_words_from_tsv_dict_parses_realistic_output() -> None:
    data: dict[str, list[object]] = {
        "text": ["Full", "Name", ""],
        "conf": ["95", "91", "-1"],
        "left": ["10", "80", "0"],
        "top": ["5", "5", "0"],
        "width": ["60", "70", "0"],
        "height": ["20", "20", "0"],
    }
    words = _words_from_tsv_dict(data)
    assert [w.text for w in words] == ["Full", "Name", ""]
    assert words[0].conf == 95.0
    assert words[2].conf == -1.0


# ------------------------------------------------------------------------ failure handling
def test_a_missing_dependency_is_an_honest_extraction_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force ``import pytesseract`` to fail regardless of what is installed.
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    with pytest.raises(DocumentExtractionError):
        TesseractExtractor().extract(io.BytesIO(b"x"), content_type=PNG)


def test_an_engine_crash_surfaces_as_an_extraction_failure() -> None:
    def boom(_source: object, _ct: str) -> ImageWords:
        raise DocumentExtractionError

    with pytest.raises(DocumentExtractionError):
        TesseractExtractor(word_reader=boom).extract(io.BytesIO(b"x"), content_type=PNG)


def test_malformed_engine_output_is_rejected_not_silently_emptied() -> None:
    with pytest.raises(DocumentExtractionError):
        _words_from_tsv_dict({"text": ["hi"]})  # missing conf/left/top/width/height
    with pytest.raises(DocumentExtractionError):
        _words_from_tsv_dict(
            {"text": ["hi"], "conf": ["x"], "left": ["0"], "top": ["0"],
             "width": ["1"], "height": ["1"]}
        )


def test_an_unsupported_content_type_is_rejected() -> None:
    # PDF is supported as of M21; a genuinely unsupported type still fails honestly.
    with pytest.raises(DocumentExtractionError):
        TesseractExtractor(word_reader=_reader([])).extract(
            io.BytesIO(b"plain text"), content_type="text/plain"
        )


# ----------------------------------------------------------------------------- no network
def test_the_adapter_makes_no_network_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_sockets(*_a: object, **_k: object) -> None:
        raise AssertionError("the OCR adapter must not open a network socket")

    monkeypatch.setattr(socket, "socket", no_sockets)
    result = TesseractExtractor(word_reader=_reader([Word("x", 70.0, 0, 0, 5, 5)])).extract(
        io.BytesIO(b"x"), content_type=PNG
    )
    assert result.text == "x"


# ------------------------------------------------------------- engine-selection boundary
def test_build_engine_tesseract_matches_the_environment(tmp_path: Path) -> None:
    # Environment-aware: with the dependency installed the builder returns the adapter; without
    # it, the builder refuses rather than silently degrading to a working-looking engine.
    if _real_tesseract_available():
        assert isinstance(build_engine("tesseract", _settings(tmp_path)), TesseractExtractor)
    else:
        with pytest.raises(EngineNotInstalledError):
            build_engine("tesseract", _settings(tmp_path))


def test_build_engine_tesseract_raises_when_the_dependency_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Deterministic unavailable branch without uninstalling Tesseract.
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    with pytest.raises(EngineNotInstalledError):
        build_engine("tesseract", _settings(tmp_path))


def test_production_builder_still_returns_the_unconfigured_extractor(tmp_path: Path) -> None:
    extractor = build_document_extractor(_settings(tmp_path))
    assert extractor.name == "unconfigured"
    assert extractor.is_available() is False


# ------------------------------------------------------------------- M19 harness smoke test
def _valid_image_corpus(root: Path) -> Corpus:
    """A tiny VALID held-out corpus with one image document (synthetic; NOT S-6 evidence)."""
    body = b"\x89PNG\r\n\x1a\n synthetic smoke fixture"
    c.documents_dir(root).mkdir(parents=True, exist_ok=True)
    (c.documents_dir(root) / "smoke1.png").write_bytes(body)
    c.annotations_dir(root).mkdir(parents=True, exist_ok=True)
    c.annotation_path(root, "smoke1").write_text(
        json.dumps({"document_id": "smoke1", "expected": [{"text": "Vedant", "page": 1}]}),
        encoding="utf-8",
    )
    item = CorpusItem(
        id="smoke1", document_type="aadhaar", page_count=1, source_category="volunteer",
        consent_status="consented", annotation_status="annotated", split="held_out",
        deidentification_status="deidentified",
        checksum_sha256=hashlib.sha256(body).hexdigest(),
    )
    corpus = Corpus(version="smoke-v1", items=(item,))
    c.save_corpus(root, corpus)
    return corpus


def test_the_m19_runner_can_drive_the_candidate_adapter(tmp_path: Path) -> None:
    corpus = _valid_image_corpus(tmp_path)
    # Deterministic stub reader so the smoke test needs no binary; this is a WIRING check,
    # not an OCR score.
    engine = TesseractExtractor(word_reader=_reader([Word("Vedant", 99.0, 0, 0, 100, 40)]))
    result = run_evaluation(corpus, tmp_path, engine)

    assert result.engine_name == "tesseract"
    assert result.failures == []
    assert result.metrics["overall"]["field_exact_match_accuracy"] == 1.0
    # PII-free: the extracted/expected value never appears in the serialised result.
    assert "Vedant" not in result.to_json()


# --------------------------------------------------------------- real engine (skips if absent)
def test_real_tesseract_end_to_end_or_skip(tmp_path: Path) -> None:
    extractor = TesseractExtractor()
    if not extractor.is_available():
        pytest.skip("Tesseract binary/pytesseract not installed in this environment")
    pil = pytest.importorskip("PIL")
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (400, 120), "white")
    ImageDraw.Draw(img).text((20, 40), "HELLO", fill="black")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    result = extractor.extract(buffer, content_type=PNG)
    assert "HELLO" in result.text.upper()
    assert result.engine == "tesseract"
    assert pil is not None
