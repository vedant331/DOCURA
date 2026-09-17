"""S-6 corpus validation (M19 §5). Fails loudly; never silently repairs evaluation data."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from app.evaluation.corpus import (
    ANNOTATION_STATUSES,
    CANDIDATE_DOCUMENT_TYPES,
    CONSENT_STATUSES,
    DEID_STATUSES,
    SPLITS,
    Corpus,
    CorpusError,
    document_path,
    is_valid_id,
    load_annotation,
    sha256_of,
)


class CorpusValidationError(CorpusError):
    """The corpus definition is invalid. Carries every error found, not just the first."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_corpus(corpus: Corpus, root: Path) -> list[str]:
    """Return every problem found (empty list = valid). Checks structure, references, and the
    held-out invariant. Does not modify anything."""
    errors: list[str] = []

    ids = [item.id for item in corpus.items]
    for dup, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate corpus id: {dup} ({count} times)")

    # Duplicate checksums across items, and — the load-bearing one — the same document
    # (checksum) appearing in the held-out split AND any other split (leakage, M19 §7).
    by_checksum: dict[str, list[str]] = {}
    for item in corpus.items:
        by_checksum.setdefault(item.checksum_sha256, []).append(item.split)
    for checksum, splits in by_checksum.items():
        if len(splits) > 1:
            errors.append(f"duplicate checksum across items: {checksum} in splits {splits}")
        if "held_out" in splits and any(s != "held_out" for s in splits):
            errors.append(f"held-out leakage: checksum {checksum} appears in {splits}")

    for item in corpus.items:
        where = f"item {item.id!r}"
        if not item.id or not is_valid_id(item.id):
            errors.append(f"{where}: id must match [A-Za-z0-9_-]+")
        if item.split not in SPLITS:
            errors.append(f"{where}: invalid split {item.split!r} (allowed: {sorted(SPLITS)})")
        if item.document_type not in CANDIDATE_DOCUMENT_TYPES:
            errors.append(f"{where}: unsupported document_type {item.document_type!r}")
        if item.consent_status not in CONSENT_STATUSES:
            errors.append(f"{where}: invalid consent_status {item.consent_status!r}")
        if item.annotation_status not in ANNOTATION_STATUSES:
            errors.append(f"{where}: invalid annotation_status {item.annotation_status!r}")
        if item.deidentification_status not in DEID_STATUSES:
            errors.append(
                f"{where}: invalid deidentification_status {item.deidentification_status!r}"
            )
        if item.page_count < 1:
            errors.append(f"{where}: page_count must be >= 1")
        if not item.checksum_sha256:
            errors.append(f"{where}: missing checksum_sha256")

        # A non-excluded item must have its document present, with a matching checksum.
        if item.excluded_reason is None:
            path = document_path(root, item)
            if path is None:
                errors.append(f"{where}: document file is missing")
            elif sha256_of(path) != item.checksum_sha256:
                errors.append(
                    f"{where}: checksum does not match the document file (inconsistent metadata)"
                )
            # Annotated items must have a well-formed annotation file.
            if item.annotation_status == "annotated":
                try:
                    annotation = load_annotation(root, item.id)
                except CorpusError as exc:
                    errors.append(f"{where}: malformed annotation ({exc})")
                    annotation = None
                if annotation is None:
                    errors.append(f"{where}: annotation_status 'annotated' but no annotation file")

    return errors


def ensure_valid(corpus: Corpus, root: Path) -> None:
    """Raise :class:`CorpusValidationError` if the corpus is invalid."""
    errors = validate_corpus(corpus, root)
    if errors:
        raise CorpusValidationError(errors)
