"""Candidate OCR engine adapters — evaluation/dev only, never production (M20).

This package lives DELIBERATELY OUTSIDE the ``app`` package. It exists so the S-6
evaluation harness can invoke a *real* candidate engine behind the production
``DocumentExtractor`` seam (``app.services.extraction``) for TECHNICAL SMOKE TESTING —
not so any candidate becomes the production engine.

Why it is not under ``app``:

* ``app.services.extraction`` owns the invariant "no engine may be imported outside
  this module", and ``tests/test_extraction.py`` enforces that no module under ``app``
  imports a concrete OCR provider or names a concrete extractor. A candidate adapter
  necessarily imports an OCR library, so it cannot live under ``app``.
* Production is unaffected: ``build_document_extractor`` still returns the unconfigured
  extractor. Nothing here is imported by ``app.main`` or any request path.

Selection remains BLOCKED on S-6 (see ``backend/docs/SPRINT_4_M14_S6_OCR_EVALUATION.md``
and ``SPRINT_4_M20_OCR_CANDIDATE_ADAPTER.md``): a working adapter is not evidence that
this engine is good enough, only that the seam can carry a real one.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Serverless/demo builds (see ``backend/build.py``) install this package's OCR dependencies
# (pytesseract, Pillow, pypdfium2) into ``backend/vendor/pydeps`` rather than the app
# environment — that keeps them out of ``pyproject.toml`` (tests/test_extraction.py forbids an
# OCR engine as a declared dependency). Put that dir on the import path here, before any lazy
# ``import pytesseract`` in the adapter/rasterizer. Absent on a normal dev checkout: a no-op.
_pydeps = Path(__file__).resolve().parent.parent / "vendor" / "pydeps"
if _pydeps.is_dir() and str(_pydeps) not in sys.path:
    sys.path.insert(0, str(_pydeps))
