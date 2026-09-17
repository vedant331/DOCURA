"""S-6 evaluation metrics (M19 §9/§10), following the D-02 §8.2 methodology.

These are METHODS, not targets. No pass/fail threshold is invented here: AR-AST-008 forbids
setting thresholds before the evaluation, so anything the methodology leaves undecided is
reported as ``None`` (TBD), never guessed. Per-document metrics store counts and ids only —
never the extracted text or any value — so evaluation summaries carry no PII.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.evaluation.corpus import Annotation, ExpectedText
from app.services.extraction import ExtractionResult


def normalize(text: str) -> str:
    """Comparison form for a text match: case-folded, whitespace-collapsed, trimmed."""
    return " ".join(text.split()).casefold()


@dataclass(frozen=True, slots=True)
class DocumentMetrics:
    document_id: str
    document_type: str
    page_count: int
    failed: bool
    expected_count: int
    exact_match: int
    normalized_match: int
    missing: int
    region_expected: int
    region_available: int
    pages_with_text: int


def _predicted_block_texts(result: ExtractionResult) -> list[tuple[str, bool]]:
    """Every predicted block's text with whether it carried a region. Page text is included as
    a region-less block so a document that yields only page text still matches values."""
    blocks: list[tuple[str, bool]] = []
    for page in result.pages:
        if page.text:
            blocks.append((page.text, False))
        for block in page.blocks:
            blocks.append((block.text, block.region is not None))
    return blocks


def score_document(
    *,
    document_id: str,
    document_type: str,
    page_count: int,
    annotation: Annotation | None,
    result: ExtractionResult | None,
) -> DocumentMetrics:
    """Compare one document's prediction against its ground truth. ``result=None`` means the
    engine failed (a processing failure — FR-OCR-009), which scores zero matches, not a crash."""
    expected: tuple[ExpectedText, ...] = annotation.expected if annotation else ()
    region_expected = sum(1 for e in expected if e.region is not None)

    if result is None:
        return DocumentMetrics(
            document_id=document_id,
            document_type=document_type,
            page_count=page_count,
            failed=True,
            expected_count=len(expected),
            exact_match=0,
            normalized_match=0,
            missing=len(expected),
            region_expected=region_expected,
            region_available=0,
            pages_with_text=0,
        )

    predicted = _predicted_block_texts(result)
    predicted_exact = {text for text, _ in predicted}
    predicted_norm = {normalize(text): has_region for text, has_region in predicted}

    exact_match = 0
    normalized_match = 0
    region_available = 0
    for item in expected:
        if item.text in predicted_exact:
            exact_match += 1
        norm = normalize(item.text)
        if norm in predicted_norm:
            normalized_match += 1
            if item.region is not None and predicted_norm[norm]:
                region_available += 1

    pages_with_text = sum(1 for page in result.pages if page.text)
    return DocumentMetrics(
        document_id=document_id,
        document_type=document_type,
        page_count=page_count,
        failed=False,
        expected_count=len(expected),
        exact_match=exact_match,
        normalized_match=normalized_match,
        missing=len(expected) - normalized_match,
        region_expected=region_expected,
        region_available=region_available,
        pages_with_text=pages_with_text,
    )


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _summarize(docs: list[DocumentMetrics]) -> dict[str, Any]:
    total = len(docs)
    failed = sum(1 for d in docs if d.failed)
    expected = sum(d.expected_count for d in docs)
    exact = sum(d.exact_match for d in docs)
    norm = sum(d.normalized_match for d in docs)
    missing = sum(d.missing for d in docs)
    region_expected = sum(d.region_expected for d in docs)
    region_available = sum(d.region_available for d in docs)
    pages = sum(d.page_count for d in docs)
    pages_with_text = sum(d.pages_with_text for d in docs)
    return {
        "documents": total,
        "failed_documents": failed,
        "processing_failure_rate": _ratio(failed, total),
        "expected_fields": expected,
        "field_exact_match_accuracy": _ratio(exact, expected),
        "normalized_field_accuracy": _ratio(norm, expected),
        "missing_field_rate": _ratio(missing, expected),
        "region_availability": _ratio(region_available, region_expected),
        "page_success_rate": _ratio(pages_with_text, pages),
        # Explicitly not evaluable from the raw extractor output at stage 1 (D-02 §19): these
        # need a classifier / field-extractor / engine confidences respectively. TBD, never guessed.
        "incorrect_field_rate": None,
        "classification_accuracy": None,
        "confidence_calibration": None,
    }


def aggregate(docs: list[DocumentMetrics]) -> dict[str, Any]:
    """Overall summary plus breakdowns by document type (D-02 per-type table). Page-level and
    field-level rollups are included in the overall summary and per type."""
    by_type: dict[str, dict[str, Any]] = {}
    types = sorted({d.document_type for d in docs})
    for document_type in types:
        by_type[document_type] = _summarize([d for d in docs if d.document_type == document_type])
    return {"overall": _summarize(docs), "by_document_type": by_type}
