"""M19 — S-6 corpus model, validation, split isolation, and ingestion.

Pure filesystem/logic tests (no database), using SYNTHETIC STRUCTURAL FIXTURES only. These
fixtures test the harness; they are NOT S-6 evaluation evidence and contain no real documents.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.evaluation import corpus as c
from app.evaluation.corpus import (
    Corpus,
    CorpusItem,
    HeldOutAccessError,
    guard_no_held_out,
    items_for_evaluation,
    items_for_tuning,
    load_corpus,
)
from app.evaluation.ingest import IngestionError, ingest_document
from app.evaluation.validation import ensure_valid, validate_corpus


def _doc(root: Path, item_id: str, body: bytes) -> str:
    c.documents_dir(root).mkdir(parents=True, exist_ok=True)
    (c.documents_dir(root) / f"{item_id}.pdf").write_bytes(body)
    return hashlib.sha256(body).hexdigest()


def _annotate(root: Path, item_id: str, expected: list[dict[str, object]]) -> None:
    c.annotations_dir(root).mkdir(parents=True, exist_ok=True)
    c.annotation_path(root, item_id).write_text(
        json.dumps({"document_id": item_id, "expected": expected}), encoding="utf-8"
    )


def _item(item_id: str, checksum: str, **over: object) -> CorpusItem:
    base: dict[str, object] = {
        "id": item_id,
        "document_type": "aadhaar",
        "page_count": 1,
        "source_category": "volunteer",
        "consent_status": "consented",
        "annotation_status": "annotated",
        "split": "held_out",
        "deidentification_status": "deidentified",
        "checksum_sha256": checksum,
    }
    base.update(over)
    return CorpusItem(**base)  # type: ignore[arg-type]


def test_valid_corpus_passes(tmp_path: Path) -> None:
    ck = _doc(tmp_path, "a1", b"%PDF-1.4 one")
    _annotate(tmp_path, "a1", [{"text": "V", "page": 1, "canonical_identifier": "person.name"}])
    corpus = Corpus(version="v1", items=(_item("a1", ck),))
    c.save_corpus(tmp_path, corpus)
    assert validate_corpus(load_corpus(tmp_path), tmp_path) == []
    ensure_valid(load_corpus(tmp_path), tmp_path)  # does not raise


def test_duplicate_id_is_rejected(tmp_path: Path) -> None:
    ck1 = _doc(tmp_path, "a1", b"%PDF one")
    corpus = Corpus(version="v1", items=(_item("a1", ck1, annotation_status="pending"),
                                          _item("a1", ck1, annotation_status="pending")))
    errors = validate_corpus(corpus, tmp_path)
    assert any("duplicate corpus id" in e for e in errors)


def test_held_out_leakage_is_detected(tmp_path: Path) -> None:
    # Same document (same checksum) in held_out AND development = leakage.
    ck = _doc(tmp_path, "a1", b"%PDF leaky")
    _doc(tmp_path, "a2", b"%PDF leaky")  # identical bytes -> same checksum
    corpus = Corpus(version="v1", items=(
        _item("a1", ck, split="held_out", annotation_status="pending"),
        _item("a2", ck, split="development", annotation_status="pending"),
    ))
    errors = validate_corpus(corpus, tmp_path)
    assert any("leakage" in e for e in errors)


def test_missing_document_is_rejected(tmp_path: Path) -> None:
    corpus = Corpus(version="v1", items=(_item("ghost", "deadbeef", annotation_status="pending"),))
    errors = validate_corpus(corpus, tmp_path)
    assert any("document file is missing" in e for e in errors)


def test_checksum_mismatch_is_rejected(tmp_path: Path) -> None:
    _doc(tmp_path, "a1", b"%PDF real")
    corpus = Corpus(version="v1", items=(_item("a1", "0" * 64, annotation_status="pending"),))
    errors = validate_corpus(corpus, tmp_path)
    assert any("checksum does not match" in e for e in errors)


def test_unsupported_document_type_is_rejected(tmp_path: Path) -> None:
    ck = _doc(tmp_path, "a1", b"%PDF t")
    item = _item("a1", ck, document_type="passport", annotation_status="pending")
    errors = validate_corpus(Corpus(version="v1", items=(item,)), tmp_path)
    assert any("unsupported document_type" in e for e in errors)


def test_malformed_annotation_is_rejected(tmp_path: Path) -> None:
    ck = _doc(tmp_path, "a1", b"%PDF m")
    c.annotations_dir(tmp_path).mkdir(parents=True, exist_ok=True)
    c.annotation_path(tmp_path, "a1").write_text("{ not json", encoding="utf-8")
    corpus = Corpus(version="v1", items=(_item("a1", ck),))
    errors = validate_corpus(corpus, tmp_path)
    assert any("malformed annotation" in e for e in errors)


def test_split_isolation_and_held_out_guard() -> None:
    tuning = _item("t1", "c1", split="development", annotation_status="pending")
    held = _item("h1", "c2", split="held_out", annotation_status="pending")
    corpus = Corpus(version="v1", items=(tuning, held))
    assert [i.id for i in items_for_tuning(corpus)] == ["t1"]
    assert [i.id for i in items_for_evaluation(corpus)] == ["h1"]
    # Tuning code must never receive held-out items.
    guard_no_held_out(items_for_tuning(corpus))  # ok
    with pytest.raises(HeldOutAccessError):
        guard_no_held_out(corpus.items)


def test_ingestion_registers_and_rejects_duplicates(tmp_path: Path) -> None:
    source = tmp_path / "incoming.pdf"
    source.write_bytes(b"%PDF-1.4 incoming")
    item = ingest_document(
        tmp_path / "corpus", source, item_id="a1", document_type="aadhaar",
        source_category="volunteer", consent_status="consented", split="held_out",
        deidentification_status="deidentified", page_count=1,
    )
    assert item.checksum_sha256 == hashlib.sha256(b"%PDF-1.4 incoming").hexdigest()
    assert (tmp_path / "corpus" / "documents" / "a1.pdf").is_file()
    assert source.is_file()  # original preserved (copied, not moved)

    # Duplicate id.
    with pytest.raises(IngestionError):
        ingest_document(tmp_path / "corpus", source, item_id="a1", document_type="aadhaar",
                        source_category="volunteer", consent_status="consented", split="held_out",
                        deidentification_status="deidentified", page_count=1)
    # Duplicate checksum under a new id.
    with pytest.raises(IngestionError):
        ingest_document(tmp_path / "corpus", source, item_id="a2", document_type="aadhaar",
                        source_category="volunteer", consent_status="consented", split="held_out",
                        deidentification_status="deidentified", page_count=1)


def test_ingestion_rejects_bad_metadata(tmp_path: Path) -> None:
    source = tmp_path / "x.pdf"
    source.write_bytes(b"%PDF x")
    with pytest.raises(IngestionError):
        ingest_document(tmp_path / "corpus", source, item_id="bad id!", document_type="aadhaar",
                        source_category="volunteer", consent_status="consented", split="nope",
                        deidentification_status="deidentified", page_count=1)
