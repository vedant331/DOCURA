"""CLI: validate a local S-6 corpus WITHOUT running any OCR engine (dev-only intake check).

    .venv/Scripts/python.exe -m scripts.s6_validate --root var/s6_corpus

Reuses the existing corpus loader and validator (app.evaluation): it checks structure,
document/checksum references, annotation well-formedness, and the held-out leakage invariant,
and prints a per-split summary. It selects no engine, sets no threshold, and reads no document
content beyond the checksum — it only tells you whether a manually supplied corpus is valid
before you run scripts.s6_evaluate. Corpus data lives under var/ (gitignored), never committed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from app.evaluation.corpus import CorpusError, load_corpus
from app.evaluation.validation import validate_corpus


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a local S-6 corpus (no OCR, no threshold)."
    )
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()

    try:
        corpus = load_corpus(args.root)
    except CorpusError as exc:
        print(f"CORPUS UNREADABLE: {exc}")
        return 1

    errors = validate_corpus(corpus, args.root)

    by_split = Counter(item.split for item in corpus.items)
    by_annotation = Counter(item.annotation_status for item in corpus.items)
    print(f"corpus version: {corpus.version}")
    print(f"items: {len(corpus.items)}")
    print(f"  by split:      {dict(by_split)}")
    print(f"  by annotation: {dict(by_annotation)}")

    if errors:
        print(f"\nINVALID — {len(errors)} problem(s):")
        for problem in errors:
            print(f"  - {problem}")
        return 1

    print("\nVALID — corpus structure, references, annotations, and held-out isolation all pass.")
    if not corpus.items:
        print("NOTE: the corpus is empty; add real documents before running scripts.s6_evaluate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
