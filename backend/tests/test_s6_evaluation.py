"""M19 — S-6 metrics, engine adapter contract, and evaluation runner.

Uses SYNTHETIC STRUCTURAL FIXTURES and a TEST-ONLY engine double — never real OCR output and
never S-6 evidence. No database required.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import BinaryIO

import pytest

from app.core.config import Environment, Settings
from app.evaluation import corpus as c
from app.evaluation.corpus import Annotation, Corpus, CorpusItem, ExpectedText
from app.evaluation.engines import EngineNotInstalledError, build_engine
from app.evaluation.metrics import aggregate, score_document
from app.evaluation.runner import run_evaluation, summarize
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
    UnconfiguredExtractor,
)


class SyntheticEngine:
    """A TEST-ONLY DocumentExtractor double — returns a fixed result. Not production, not OCR."""

    name = "synthetic-test-double"
    version = "1"

    def __init__(self, result: ExtractionResult) -> None:
        self._result = result

    def is_available(self) -> bool:
        return True

    def extract(self, source: BinaryIO, *, content_type: str) -> ExtractionResult:
        return self._result


def _result(*blocks: TextBlock) -> ExtractionResult:
    return ExtractionResult(
        pages=(ExtractedPage(number=1, text="page one", blocks=blocks),),
        engine="synthetic-test-double",
        engine_version="1",
    )


def test_score_document_counts_matches_missing_and_region() -> None:
    annotation = Annotation(
        document_id="a1",
        expected=(
            ExpectedText(text="Vedant Kadam", page=1, canonical_identifier="person.full_name",
                         region=(0.1, 0.1, 0.2, 0.05)),
            ExpectedText(text="2007-03-24", page=1, canonical_identifier="person.date_of_birth"),
            ExpectedText(text="Never Extracted", page=1),
        ),
    )
    region = TextRegion(page=1, x=0.1, y=0.1, width=0.2, height=0.05)
    result = _result(
        TextBlock(text="Vedant Kadam", region=region),
        TextBlock(text="  2007-03-24 "),  # normalized match, no region
    )
    m = score_document(document_id="a1", document_type="aadhaar", page_count=1,
                       annotation=annotation, result=result)
    assert m.failed is False
    assert m.expected_count == 3
    assert m.exact_match == 1  # "Vedant Kadam" exact; the DOB needed normalization
    assert m.normalized_match == 2  # Vedant + DOB
    assert m.missing == 1  # "Never Extracted"
    assert m.region_expected == 1
    assert m.region_available == 1  # the matched Vedant block carried a region


def test_score_document_failure_scores_zero_not_crash() -> None:
    annotation = Annotation(document_id="a1", expected=(ExpectedText(text="X", page=1),))
    m = score_document(document_id="a1", document_type="aadhaar", page_count=2,
                       annotation=annotation, result=None)
    assert m.failed is True
    assert m.missing == 1
    assert m.pages_with_text == 0


def test_aggregate_overall_and_by_type() -> None:
    a = score_document(document_id="a1", document_type="aadhaar", page_count=1,
                       annotation=Annotation("a1", (ExpectedText("N", 1),)),
                       result=_result(TextBlock(text="N")))
    b = score_document(document_id="b1", document_type="pan", page_count=1,
                       annotation=Annotation("b1", (ExpectedText("Z", 1),)), result=None)
    agg = aggregate([a, b])
    assert agg["overall"]["documents"] == 2
    assert agg["overall"]["processing_failure_rate"] == 0.5
    assert agg["by_document_type"]["aadhaar"]["field_exact_match_accuracy"] == 1.0
    assert agg["by_document_type"]["pan"]["processing_failure_rate"] == 1.0
    # Stage-2 / classifier / calibration metrics are honestly TBD, never invented.
    assert agg["overall"]["incorrect_field_rate"] is None
    assert agg["overall"]["classification_accuracy"] is None


def test_build_engine_contract(tmp_path: Path) -> None:
    # A self-contained Settings (no DB connection is made — the plug point only logs).
    settings = Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "documents",
    )
    # 'unconfigured' comes via the production plug point: an extractor that cannot work yet.
    engine = build_engine("unconfigured", settings)
    assert engine.name == "unconfigured"
    assert engine.is_available() is False
    with pytest.raises(EngineNotInstalledError):
        build_engine("tesseract", settings)  # a candidate name, deliberately not installed
    with pytest.raises(EngineNotInstalledError):
        build_engine("something-else", settings)


def _valid_corpus(root: Path) -> Corpus:
    body = b"%PDF-1.4 seed"
    c.documents_dir(root).mkdir(parents=True, exist_ok=True)
    (c.documents_dir(root) / "a1.pdf").write_bytes(body)
    c.annotations_dir(root).mkdir(parents=True, exist_ok=True)
    c.annotation_path(root, "a1").write_text(
        json.dumps({"document_id": "a1", "expected": [{"text": "Vedant Kadam", "page": 1}]}),
        encoding="utf-8",
    )
    item = CorpusItem(
        id="a1", document_type="aadhaar", page_count=1, source_category="volunteer",
        consent_status="consented", annotation_status="annotated", split="held_out",
        deidentification_status="deidentified", checksum_sha256=hashlib.sha256(body).hexdigest(),
    )
    corpus = Corpus(version="v1", items=(item,))
    c.save_corpus(root, corpus)
    return corpus


def test_runner_with_unconfigured_records_honest_failures(tmp_path: Path) -> None:
    corpus = _valid_corpus(tmp_path)
    result = run_evaluation(corpus, tmp_path, UnconfiguredExtractor(), config_id="cfg")
    assert result.engine_name == "unconfigured"
    assert result.failures == ["a1"]
    assert result.metrics["overall"]["processing_failure_rate"] == 1.0
    assert "S-6 evaluation" in summarize(result)


def test_runner_with_synthetic_engine_scores_and_is_pii_free(tmp_path: Path) -> None:
    corpus = _valid_corpus(tmp_path)
    engine = SyntheticEngine(_result(TextBlock(text="Vedant Kadam")))
    result = run_evaluation(corpus, tmp_path, engine)
    assert result.metrics["overall"]["field_exact_match_accuracy"] == 1.0
    assert result.failures == []
    # Result schema completeness.
    for key in ("run_id", "corpus_version", "engine_name", "engine_version", "config_id",
                "timestamp", "document_count", "page_count", "metrics", "per_document",
                "failures", "missing_or_invalid_annotations", "environment"):
        assert key in result.to_dict()
    # PII-free: the expected/extracted value never appears in the serialised result.
    assert "Vedant Kadam" not in result.to_json()


def test_runner_refuses_an_invalid_corpus(tmp_path: Path) -> None:
    from app.evaluation.validation import CorpusValidationError

    bad = Corpus(version="v1", items=(CorpusItem(
        id="ghost", document_type="aadhaar", page_count=1, source_category="v",
        consent_status="consented", annotation_status="pending", split="held_out",
        deidentification_status="raw", checksum_sha256="x" * 64),))
    c.save_corpus(tmp_path, bad)
    with pytest.raises(CorpusValidationError):
        run_evaluation(bad, tmp_path, UnconfiguredExtractor())
