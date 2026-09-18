"""Evaluation-side engine adapter contract (M19 §8).

Candidate OCR engines are run through the SAME production seam, ``DocumentExtractor``
(``app.services.extraction``). This milestone selects NO engine and installs none: candidate
names are configuration options only, and every candidate raises "not installed" until its
adapter is added behind the seam.

Per the extraction module's own invariant ("no engine may be imported outside this module"),
this module never names a concrete extractor implementation: the ``unconfigured`` engine is
obtained from the production plug point ``build_document_extractor`` — which today returns the
always-failing unconfigured extractor, so a runner wired to it records honest failures and
never manufactures OCR output (AR-AST-008).
"""

from __future__ import annotations

from app.core.config import Settings
from app.services.extraction import DocumentExtractor, build_document_extractor

# Candidate engines discussed in M14, as NAMES only. Adding a name here does not install or
# select an engine; it records that a candidate exists to be evaluated behind the seam.
CANDIDATE_ENGINES: tuple[str, ...] = ("tesseract", "paddleocr", "easyocr", "doctr")


class EngineNotInstalledError(Exception):
    """A candidate engine was requested but no adapter is installed for it (by design)."""


def build_engine(name: str, settings: Settings) -> DocumentExtractor:
    """Return the extractor adapter for a candidate name.

    ``unconfigured`` comes from the production plug point (currently the always-failing
    unconfigured extractor). ``tesseract`` has an adapter for TECHNICAL SMOKE TESTING (M20),
    returned only when its dependency is actually installed; otherwise, like every other
    candidate, it raises :class:`EngineNotInstalledError`. Building a candidate here is not
    engine selection: production still uses the unconfigured extractor and selection stays
    blocked on S-6 evaluation and governance (D-02 / AR-AST-008).

    The adapter lives OUTSIDE the ``app`` package (``ocr_candidates``) and is imported lazily,
    so no OCR-library knowledge enters the application's import surface (the invariant in
    ``app.services.extraction``).
    """
    if name == "unconfigured":
        return build_document_extractor(settings)
    if name == "tesseract":
        from ocr_candidates.tesseract_adapter import build_tesseract_extractor

        extractor = build_tesseract_extractor(settings)
        if not extractor.is_available():
            raise EngineNotInstalledError(
                "candidate engine 'tesseract' adapter is present but its dependency "
                "(pytesseract + the Tesseract binary) is not installed; install it to run "
                "the candidate for smoke testing"
            )
        return extractor
    if name in CANDIDATE_ENGINES:
        raise EngineNotInstalledError(
            f"candidate engine {name!r} is not installed; add a DocumentExtractor adapter for it "
            "once S-6 evaluation and governance permit engine selection"
        )
    raise EngineNotInstalledError(f"unknown engine {name!r}")
