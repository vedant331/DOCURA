"""CLI: run the S-6 evaluation over a local corpus (dev-only).

    .venv/Scripts/python.exe -m scripts.s6_evaluate --root var/s6_corpus --engine unconfigured

Only ``unconfigured`` is installed today (it fails every extraction honestly); a real
candidate raises "not installed" until S-6 and governance permit selecting an engine. No
thresholds are invented. See backend/docs/SPRINT_4_M19_S6_CORPUS_AND_EVALUATION.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.config import Settings
from app.evaluation.corpus import CorpusError, load_corpus
from app.evaluation.engines import EngineNotInstalledError, build_engine
from app.evaluation.runner import run_evaluation, summarize, write_result
from app.evaluation.validation import CorpusValidationError


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the S-6 OCR evaluation over a local corpus.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--engine", default="unconfigured")
    parser.add_argument("--config-id", default="default")
    parser.add_argument("--split", default="held_out")
    parser.add_argument(
        "--write", action="store_true", help="persist the result under <root>/results/"
    )
    args = parser.parse_args()

    try:
        corpus = load_corpus(args.root)
        engine = build_engine(args.engine, Settings())
        result = run_evaluation(
            corpus, args.root, engine, config_id=args.config_id, split=args.split
        )
    except (CorpusError, CorpusValidationError) as exc:
        print(f"CORPUS INVALID: {exc}")
        return 1
    except EngineNotInstalledError as exc:
        print(f"ENGINE UNAVAILABLE: {exc}")
        return 2

    print(summarize(result))
    if args.write:
        path = write_result(args.root, result)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
