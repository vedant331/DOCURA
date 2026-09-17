"""S-6 evaluation runner and result format (M19 §9/§10).

Runs a candidate engine (a ``DocumentExtractor``) over the sealed held-out split of a VALID
corpus, compares predictions to ground truth, and emits a reproducible, PII-free result. It
invents no thresholds and — because the only installed engine is the unconfigured extractor
from the plug point — manufactures no OCR output: with no engine it records honest failures.
"""

from __future__ import annotations

import json
import platform
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.errors import DocumentExtractionError
from app.evaluation.corpus import (
    EVALUATION_SPLIT,
    Corpus,
    CorpusItem,
    document_path,
    items_for_evaluation,
    load_annotation,
    results_dir,
)
from app.evaluation.metrics import DocumentMetrics, aggregate, score_document
from app.evaluation.validation import ensure_valid
from app.services.extraction import DocumentExtractor, ExtractionResult

_MEDIA_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    run_id: str
    corpus_version: str
    split: str
    engine_name: str
    engine_version: str
    config_id: str
    timestamp: str
    document_count: int
    page_count: int
    metrics: dict[str, Any]
    per_document: list[dict[str, Any]]
    failures: list[str]
    missing_or_invalid_annotations: list[str]
    environment: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _content_type_for(path: Path) -> str:
    return _MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream")


def _extract_one(engine: DocumentExtractor, path: Path) -> ExtractionResult | None:
    """Run the engine on one document; None on an honest extraction failure (not a crash)."""
    try:
        with path.open("rb") as handle:
            return engine.extract(handle, content_type=_content_type_for(path))
    except DocumentExtractionError:
        return None


def run_evaluation(
    corpus: Corpus,
    root: Path,
    engine: DocumentExtractor,
    *,
    config_id: str = "default",
    split: str = EVALUATION_SPLIT,
) -> EvaluationResult:
    """Evaluate ``engine`` over the corpus's evaluation split. The corpus MUST be valid; this
    raises if it is not, rather than scoring against a broken definition."""
    ensure_valid(corpus, root)

    items: tuple[CorpusItem, ...] = (
        items_for_evaluation(corpus)
        if split == EVALUATION_SPLIT
        else tuple(i for i in corpus.items if i.split == split)
    )

    docs: list[DocumentMetrics] = []
    failures: list[str] = []
    missing_annotations: list[str] = []

    for item in items:
        if item.excluded_reason is not None:
            continue
        path = document_path(root, item)
        annotation = load_annotation(root, item.id)
        if annotation is None:
            missing_annotations.append(item.id)
        result = _extract_one(engine, path) if path is not None else None
        if result is None:
            failures.append(item.id)
        docs.append(
            score_document(
                document_id=item.id,
                document_type=item.document_type,
                page_count=item.page_count,
                annotation=annotation,
                result=result,
            )
        )

    return EvaluationResult(
        run_id=str(uuid.uuid4()),
        corpus_version=corpus.version,
        split=split,
        engine_name=engine.name,
        engine_version=engine.version,
        config_id=config_id,
        timestamp=datetime.now(UTC).isoformat(),
        document_count=len(docs),
        page_count=sum(d.page_count for d in docs),
        metrics=aggregate(docs),
        per_document=[asdict(d) for d in docs],
        failures=failures,
        missing_or_invalid_annotations=missing_annotations,
        environment={
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "engine": f"{engine.name}@{engine.version}",
        },
    )


def write_result(root: Path, result: EvaluationResult) -> Path:
    """Persist a result under ``<root>/results/`` (local, gitignored). Returns the path."""
    out_dir = results_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = result.timestamp.replace(":", "-")
    path = out_dir / f"{stamp}_{result.engine_name}_{result.run_id}.json"
    path.write_text(result.to_json(), encoding="utf-8")
    return path


def summarize(result: EvaluationResult) -> str:
    """A short human-readable summary (no PII — counts and rates only)."""
    overall = result.metrics.get("overall", {})
    lines = [
        f"S-6 evaluation {result.run_id}",
        f"  engine:   {result.engine_name}@{result.engine_version} (config {result.config_id})",
        f"  corpus:   {result.corpus_version}  split={result.split}",
        f"  documents:{result.document_count}  pages:{result.page_count}  "
        f"failures:{len(result.failures)}",
        f"  field exact-match:     {overall.get('field_exact_match_accuracy')}",
        f"  normalized accuracy:   {overall.get('normalized_field_accuracy')}",
        f"  missing-field rate:    {overall.get('missing_field_rate')}",
        f"  processing failure:    {overall.get('processing_failure_rate')}",
        f"  region availability:   {overall.get('region_availability')}",
        f"  page success rate:     {overall.get('page_success_rate')}",
        "  (incorrect-field / classification / confidence calibration: TBD — see D-02 §19)",
    ]
    return "\n".join(lines)
