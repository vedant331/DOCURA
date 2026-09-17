"""S-6 corpus model, on-disk layout, and split access (M19).

Layout under a corpus root (default ``var/s6_corpus/`` — ``var/`` is gitignored, so real
documents never enter source control):

    <root>/manifest.json            # the machine-readable corpus manifest (this module)
    <root>/documents/<id>.<ext>     # the source documents (never committed)
    <root>/annotations/<id>.json    # ground-truth annotations (this module)
    <root>/results/                 # evaluation result files (runner.py)

Splits are a manifest field, not separate trees, so one document is one file with one
checksum — which is what makes held-out leakage detectable (validation.py). The evaluation
runner reads the ``held_out`` split; tuning/development code may read only ``train`` +
``development`` and is refused ``held_out`` (see ``items_for_tuning``).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SPLITS: frozenset[str] = frozenset({"train", "development", "held_out"})
TUNING_SPLITS: frozenset[str] = frozenset({"train", "development"})
EVALUATION_SPLIT = "held_out"

CONSENT_STATUSES: frozenset[str] = frozenset(
    {"consented", "pending", "withdrawn", "not_applicable"}
)
ANNOTATION_STATUSES: frozenset[str] = frozenset({"annotated", "pending", "not_applicable"})
DEID_STATUSES: frozenset[str] = frozenset({"deidentified", "raw", "not_applicable"})

# Candidate document categories from the requirements' §7.1 list. IMPORTANT: §7.1 inclusion in
# the shipped MVP set is TBD — it is exactly what S-6 decides — so these are the CANDIDATE
# categories a corpus may contain, never an approved shipped set.
CANDIDATE_DOCUMENT_TYPES: frozenset[str] = frozenset(
    {
        "aadhaar",
        "pan",
        "address_proof",
        "marksheet_10",
        "marksheet_12",
        "semester_result",
        "degree_certificate",
        "photograph",
        "signature",
        "student_id",
        "hall_ticket",
        "resume",
        "other",
    }
)

_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class CorpusError(Exception):
    """A corpus manifest or annotation could not be read or is structurally invalid."""


@dataclass(frozen=True, slots=True)
class CorpusItem:
    """One corpus document's metadata. Carries NO document content and no unnecessary PII."""

    id: str
    document_type: str
    page_count: int
    source_category: str
    consent_status: str
    annotation_status: str
    split: str
    deidentification_status: str
    checksum_sha256: str
    excluded_reason: str | None = None


@dataclass(frozen=True, slots=True)
class Corpus:
    version: str
    items: tuple[CorpusItem, ...]


@dataclass(frozen=True, slots=True)
class ExpectedText:
    """One expected extraction, for ground truth. Value-free of the record: this is what the
    document is expected to yield, not a user's stored value. ``region`` (x, y, width, height,
    page-relative fractions) is optional — D-02 evaluates region *availability*, not geometry."""

    text: str
    page: int
    canonical_identifier: str | None = None
    region: tuple[float, float, float, float] | None = None


@dataclass(frozen=True, slots=True)
class Annotation:
    document_id: str
    expected: tuple[ExpectedText, ...]


def is_valid_id(value: str) -> bool:
    return bool(_ID_RE.match(value))


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_path(root: Path) -> Path:
    return root / "manifest.json"


def documents_dir(root: Path) -> Path:
    return root / "documents"


def annotations_dir(root: Path) -> Path:
    return root / "annotations"


def results_dir(root: Path) -> Path:
    return root / "results"


def document_path(root: Path, item: CorpusItem) -> Path | None:
    """The document file for an item (``documents/<id>.<ext>``), or None if absent."""
    matches = sorted(documents_dir(root).glob(f"{item.id}.*"))
    return matches[0] if matches else None


def annotation_path(root: Path, document_id: str) -> Path:
    return annotations_dir(root) / f"{document_id}.json"


def _require(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise CorpusError(f"missing required field: {key}")
    return mapping[key]


def _item_from_dict(raw: dict[str, Any]) -> CorpusItem:
    try:
        return CorpusItem(
            id=str(_require(raw, "id")),
            document_type=str(_require(raw, "document_type")),
            page_count=int(_require(raw, "page_count")),
            source_category=str(_require(raw, "source_category")),
            consent_status=str(_require(raw, "consent_status")),
            annotation_status=str(_require(raw, "annotation_status")),
            split=str(_require(raw, "split")),
            deidentification_status=str(_require(raw, "deidentification_status")),
            checksum_sha256=str(_require(raw, "checksum_sha256")),
            excluded_reason=(str(raw["excluded_reason"]) if raw.get("excluded_reason") else None),
        )
    except (TypeError, ValueError) as exc:
        raise CorpusError(f"malformed manifest item: {exc}") from exc


def load_corpus(root: Path) -> Corpus:
    path = manifest_path(root)
    if not path.is_file():
        raise CorpusError(f"no corpus manifest at {path}")
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CorpusError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise CorpusError("manifest must be a JSON object")
    items_raw = data.get("items", [])
    if not isinstance(items_raw, list):
        raise CorpusError("manifest 'items' must be a list")
    items = tuple(_item_from_dict(dict(entry)) for entry in items_raw)
    return Corpus(version=str(data.get("version", "unversioned")), items=items)


def save_corpus(root: Path, corpus: Corpus) -> None:
    root.mkdir(parents=True, exist_ok=True)
    payload = {"version": corpus.version, "items": [asdict(item) for item in corpus.items]}
    manifest_path(root).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _expected_from_dict(raw: dict[str, Any]) -> ExpectedText:
    region_raw = raw.get("region")
    region: tuple[float, float, float, float] | None = None
    if region_raw is not None:
        try:
            region = (
                float(region_raw["x"]),
                float(region_raw["y"]),
                float(region_raw["width"]),
                float(region_raw["height"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CorpusError(f"malformed annotation region: {exc}") from exc
    try:
        return ExpectedText(
            text=str(_require(raw, "text")),
            page=int(_require(raw, "page")),
            canonical_identifier=(
                str(raw["canonical_identifier"]) if raw.get("canonical_identifier") else None
            ),
            region=region,
        )
    except (TypeError, ValueError) as exc:
        raise CorpusError(f"malformed annotation entry: {exc}") from exc


def load_annotation(root: Path, document_id: str) -> Annotation | None:
    path = annotation_path(root, document_id)
    if not path.is_file():
        return None
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CorpusError(f"annotation for {document_id} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise CorpusError(f"annotation for {document_id} must be a JSON object")
    expected_raw = data.get("expected", [])
    if not isinstance(expected_raw, list):
        raise CorpusError(f"annotation 'expected' for {document_id} must be a list")
    expected = tuple(_expected_from_dict(dict(entry)) for entry in expected_raw)
    return Annotation(document_id=str(data.get("document_id", document_id)), expected=expected)


class HeldOutAccessError(Exception):
    """Tuning/development code attempted to read the sealed held-out split (M19 §7)."""


def items_for_tuning(corpus: Corpus) -> tuple[CorpusItem, ...]:
    """Items usable for tuning/rule/alias/threshold development — NEVER the held-out split."""
    return tuple(item for item in corpus.items if item.split in TUNING_SPLITS)


def items_for_evaluation(corpus: Corpus) -> tuple[CorpusItem, ...]:
    """The sealed held-out split — read only by the evaluation runner (M19 §7)."""
    return tuple(item for item in corpus.items if item.split == EVALUATION_SPLIT)


def guard_no_held_out(items: tuple[CorpusItem, ...]) -> tuple[CorpusItem, ...]:
    """Raise if any item is held-out; use to protect a tuning/development code path."""
    leaked = [item.id for item in items if item.split == EVALUATION_SPLIT]
    if leaked:
        raise HeldOutAccessError(
            f"held-out items must not be used for tuning/development: {', '.join(leaked)}"
        )
    return items
