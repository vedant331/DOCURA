"""The extraction boundary: what DOCURA needs from an OCR engine, and nothing more.

Sprint 4 decision D-01 selected a **self-hosted** extraction architecture behind a
replaceable interface, and deliberately did **not** select the engine: AR-AST-008
requires assisted components to be evaluated against a held-out corpus of real,
imperfect documents before any threshold is set, and the same evidence should
choose the engine. Until that evaluation reports, the concrete engine is TBD and
this module is the only place that will have to know which one won.

That is what §6 of the Requirements Specification asks for in terms: "This document
specifies what each layer must guarantee, not what technology provides it. Any
component may be replaced provided its replacement meets the same guarantees."
:class:`DocumentExtractor` is those guarantees written down. It is the same shape as
:class:`~app.services.storage.DocumentStorage`, for the same reason — one seam, one
builder, and no caller that knows what is on the other side.

**What this module deliberately does not contain**, because each is a separate
decision or is evaluation-dependent:

* document-type-specific field definitions (FR-OCR-004, decision D-05);
* the review and automatic-action thresholds (FR-OCR-006, BR-001, decision D-03) —
  a confidence is *carried* here and compared nowhere;
* sensitivity classification (FR-INF-007, decision D-06);
* the canonical attribute vocabulary (FR-ACC-004, decision D-05);
* document classification (FR-OCR-002) and structured information (FR-INF), which
  are separate assisted components and will get their own ports;
* the durable processing pipeline that will call this (NFR-PERF-002, decision D-09).

The port is synchronous. Extraction is CPU-bound rather than I/O-bound, and the
component that will drive it is a worker outside the request path, so an interface
that returned awaitables would describe the work dishonestly and buy nothing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import BinaryIO, Protocol, runtime_checkable

from app.core.config import Settings
from app.core.errors import ExtractionNotConfiguredError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Coordinates are page-relative fractions rather than pixels or points. An engine
# that reads a 200-DPI scan and one that reads a PDF's text layer do not agree on a
# unit; both agree on "a third of the way down the page". Slack absorbs the float
# arithmetic an engine does before it hands the box over.
_BOUNDS_EPSILON = 1e-6


def _check_fraction(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0 + _BOUNDS_EPSILON:
        msg = f"{name} must be a page-relative fraction between 0 and 1"
        raise ValueError(msg)


def _check_confidence(value: float | None) -> None:
    """A confidence is a fraction or it is absent. It is never inferred here.

    ``None`` means the engine did not report one, which is a different fact from a
    low confidence and must stay distinguishable: FR-OCR-005 requires a confidence
    to be *recorded*, and AR-AST-001 requires it to mean something. Substituting a
    number for a missing one would manufacture the evidence BR-001 later relies on.
    """
    if value is None:
        return
    if not 0.0 <= value <= 1.0:
        msg = "confidence must be between 0 and 1, or None where the engine reports none"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class TextRegion:
    """Where on the page a piece of text was read from (FR-OCR-007).

    FR-OCR-007 requires each extracted value to be shown "alongside the region of
    the source document it was read from", and AR-AST-006 requires every assisted
    output to be explainable in terms of its source. Provenance therefore has to
    survive the engine boundary, which means it belongs in the result type rather
    than in whatever a particular engine happens to return.
    """

    page: int
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.page < 1:
            msg = "page numbers are 1-based"
            raise ValueError(msg)
        _check_fraction("x", self.x)
        _check_fraction("y", self.y)
        if not 0.0 < self.width <= 1.0 + _BOUNDS_EPSILON:
            msg = "width must be a positive page-relative fraction"
            raise ValueError(msg)
        if not 0.0 < self.height <= 1.0 + _BOUNDS_EPSILON:
            msg = "height must be a positive page-relative fraction"
            raise ValueError(msg)
        if self.x + self.width > 1.0 + _BOUNDS_EPSILON:
            msg = "region extends past the right edge of the page"
            raise ValueError(msg)
        if self.y + self.height > 1.0 + _BOUNDS_EPSILON:
            msg = "region extends past the bottom edge of the page"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class TextBlock:
    """A run of text an engine read, with where it came from and how sure it was.

    A block is a unit of *text*, not a unit of *meaning*. It is deliberately not a
    field: which fields exist for which document type is FR-OCR-004, and that
    definition does not exist yet (decision D-05).
    """

    text: str
    region: TextRegion | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        _check_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    """One page of a document. Multi-page documents stay one document (FR-OCR-008)."""

    number: int
    text: str
    blocks: tuple[TextBlock, ...] = ()
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.number < 1:
            msg = "page numbers are 1-based"
            raise ValueError(msg)
        _check_confidence(self.confidence)
        for block in self.blocks:
            if block.region is not None and block.region.page != self.number:
                msg = f"block region names page {block.region.page} on page {self.number}"
                raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """What every extractor returns, whichever engine produced it.

    ``engine`` and ``engine_version`` are part of the result rather than of the
    configuration because AR-AST-008's evaluation is evidence about *a specific
    component*: a threshold calibrated against one engine version is not evidence
    for another. Recording which component produced a value is what will later make
    it possible to tell whether a stored result predates an engine change.
    """

    pages: tuple[ExtractedPage, ...]
    engine: str
    engine_version: str
    # Engine-neutral facts about the run — timings, engine settings, page counts.
    # Never document content and never an extracted personal value (NFR-PRIV-007).
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.engine:
            msg = "an extraction result must name the engine that produced it"
            raise ValueError(msg)
        previous = 0
        for page in self.pages:
            if page.number <= previous:
                msg = "pages must be ordered and their numbers strictly increasing"
                raise ValueError(msg)
            previous = page.number

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def text(self) -> str:
        """The document's text, in page order (FR-OCR-001).

        Joined here rather than stored twice, so the whole-document text and the
        per-page text can never disagree.
        """
        return "\n".join(page.text for page in self.pages)


@runtime_checkable
class DocumentExtractor(Protocol):
    """What DOCURA needs from an extraction engine.

    An implementation must be substitutable without any change above this module.
    It must also be honest: where it cannot read a document it raises
    :class:`~app.core.errors.DocumentExtractionError` rather than returning an empty
    or invented result, because FR-OCR-009 requires a failure to be stated and
    BR-016 requires a failing component to do nothing rather than proceed on partial
    information.
    """

    @property
    def name(self) -> str:
        """Stable identifier of the engine, recorded on every result it produces."""
        ...

    @property
    def version(self) -> str:
        """The engine's version, for the reason given on :class:`ExtractionResult`."""
        ...

    def is_available(self) -> bool:
        """True when this extractor can actually do work.

        Callers use it to tell "no engine is configured" from "extraction failed",
        without having to provoke an exception to find out.
        """
        ...

    def extract(self, source: BinaryIO, *, content_type: str) -> ExtractionResult:
        """Read ``source`` and return its text, pages, regions, and confidences.

        ``source`` is an open binary stream positioned at the start; the caller owns
        it and closes it. ``content_type`` is the media type the vault validated on
        upload, passed so an engine need not sniff bytes it has already been told
        about.
        """
        ...


class UnconfiguredExtractor:
    """The extractor that is in place while D-01's engine selection is TBD.

    It exists so that the boundary can be built, injected, and tested before an
    engine is chosen — and so that the absence of an engine is *loud*. It reads
    nothing, returns nothing, and raises a failure that says exactly what is
    missing. A placeholder that returned empty text would be indistinguishable from
    a document with no readable content, and one that returned plausible text would
    be worse: AR-AST-008's evaluation is meaningless if anything in the system can
    manufacture a result.
    """

    name = "unconfigured"
    version = "0"

    def is_available(self) -> bool:
        return False

    def extract(self, source: BinaryIO, *, content_type: str) -> ExtractionResult:
        """Always fails. The stream is not read and the media type is not inspected."""
        raise ExtractionNotConfiguredError


def build_document_extractor(settings: Settings) -> DocumentExtractor:
    """Construct the configured extractor.

    This is the plug point. When the held-out evaluation (AR-AST-008, study S-6)
    names an engine, its implementation is added beside
    :class:`UnconfiguredExtractor` and selected here — a change to this function and
    to nothing above it. No engine may be imported outside this module.

    The engine is deliberately not selectable by configuration yet: a setting whose
    only valid value is "none" would describe a choice that has not been made.
    """
    extractor = UnconfiguredExtractor()
    logger.info(
        "extraction.engine_unconfigured",
        engine=extractor.name,
        reason="d01_engine_pending_held_out_evaluation",
        environment=settings.environment.value,
    )
    return extractor
