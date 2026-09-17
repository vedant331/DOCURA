"""CLI: register one document into the local S-6 corpus (dev-only). NOT a production path.

    .venv/Scripts/python.exe -m scripts.s6_ingest \
        --root var/s6_corpus --source /path/to/doc.pdf --id aadhaar_001 \
        --document-type aadhaar --source-category volunteer --consent consented \
        --split held_out --deid deidentified --page-count 1

Corpus data lives under var/ (gitignored) and is never committed. See
backend/docs/SPRINT_4_M19_S6_CORPUS_AND_EVALUATION.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.evaluation.ingest import IngestionError, ingest_document


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a document into the local S-6 corpus.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--document-type", required=True)
    parser.add_argument("--source-category", required=True)
    parser.add_argument("--consent", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--deid", required=True)
    parser.add_argument("--page-count", required=True, type=int)
    parser.add_argument("--annotation-status", default="pending")
    args = parser.parse_args()

    try:
        item = ingest_document(
            args.root,
            args.source,
            item_id=args.id,
            document_type=args.document_type,
            source_category=args.source_category,
            consent_status=args.consent,
            split=args.split,
            deidentification_status=args.deid,
            page_count=args.page_count,
            annotation_status=args.annotation_status,
        )
    except IngestionError as exc:
        print(f"INGEST FAILED: {exc}")
        return 1
    print(
        f"ingested {item.id} ({item.document_type}, split={item.split}, "
        f"checksum={item.checksum_sha256[:12]}...)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
