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
    unconfigured extractor). Every real candidate raises :class:`EngineNotInstalledError` — its
    adapter (a ``DocumentExtractor`` implementation) is added beside the plug point when, and
    only when, S-6 evaluation and governance permit selecting it. No engine is chosen or
    installed in this milestone.
    """
    if name == "unconfigured":
        return build_document_extractor(settings)
    if name in CANDIDATE_ENGINES:
        raise EngineNotInstalledError(
            f"candidate engine {name!r} is not installed; add a DocumentExtractor adapter for it "
            "once S-6 evaluation and governance permit engine selection"
        )
    raise EngineNotInstalledError(f"unknown engine {name!r}")
