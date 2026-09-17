"""S-6 corpus ingestion (M19 §6). Local/dev only — registers an evaluation document into the
corpus under ``var/s6_corpus/`` (gitignored). It is NOT a production upload path and never
writes to the production document vault. It computes a checksum, validates governance metadata,
rejects duplicates, preserves the original bytes, and records the result in the manifest.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from app.evaluation.corpus import (
    ANNOTATION_STATUSES,
    CANDIDATE_DOCUMENT_TYPES,
    CONSENT_STATUSES,
    DEID_STATUSES,
    SPLITS,
    Corpus,
    CorpusError,
    CorpusItem,
    documents_dir,
    is_valid_id,
    load_corpus,
    manifest_path,
    save_corpus,
    sha256_of,
)


class IngestionError(CorpusError):
    """A corpus item could not be ingested (bad metadata, duplicate, or missing source)."""


def _validate_metadata(item: CorpusItem) -> None:
    problems: list[str] = []
    if not is_valid_id(item.id):
        problems.append("id must match [A-Za-z0-9_-]+")
    if item.split not in SPLITS:
        problems.append(f"invalid split {item.split!r}")
    if item.document_type not in CANDIDATE_DOCUMENT_TYPES:
        problems.append(f"unsupported document_type {item.document_type!r}")
    if item.consent_status not in CONSENT_STATUSES:
        problems.append(f"invalid consent_status {item.consent_status!r}")
    if item.annotation_status not in ANNOTATION_STATUSES:
        problems.append(f"invalid annotation_status {item.annotation_status!r}")
    if item.deidentification_status not in DEID_STATUSES:
        problems.append(f"invalid deidentification_status {item.deidentification_status!r}")
    if item.page_count < 1:
        problems.append("page_count must be >= 1")
    if problems:
        raise IngestionError("; ".join(problems))


def ingest_document(
    root: Path,
    source: Path,
    *,
    item_id: str,
    document_type: str,
    source_category: str,
    consent_status: str,
    split: str,
    deidentification_status: str,
    page_count: int,
    annotation_status: str = "pending",
) -> CorpusItem:
    """Register ``source`` as corpus item ``item_id``. Returns the recorded manifest item.

    Rejects a duplicate id or a document whose checksum is already in the corpus. Copies the
    original into ``<root>/documents/`` (never moving or altering it)."""
    if not source.is_file():
        raise IngestionError(f"source document not found: {source}")

    checksum = sha256_of(source)
    corpus = load_corpus(root) if manifest_path(root).is_file() else Corpus(version="v0", items=())

    for existing in corpus.items:
        if existing.id == item_id:
            raise IngestionError(f"duplicate corpus id: {item_id}")
        if existing.checksum_sha256 == checksum:
            raise IngestionError(
                f"document already in corpus as {existing.id!r} (same checksum); not re-ingested"
            )

    item = CorpusItem(
        id=item_id,
        document_type=document_type,
        page_count=page_count,
        source_category=source_category,
        consent_status=consent_status,
        annotation_status=annotation_status,
        split=split,
        deidentification_status=deidentification_status,
        checksum_sha256=checksum,
    )
    _validate_metadata(item)

    documents_dir(root).mkdir(parents=True, exist_ok=True)
    destination = documents_dir(root) / f"{item_id}{source.suffix.lower()}"
    shutil.copyfile(source, destination)  # preserve the original; copy, never move

    save_corpus(root, Corpus(version=corpus.version, items=(*corpus.items, item)))
    return item
