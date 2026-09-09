"""The document-classification seam (Sprint 4, seventh milestone).

Between *text that was read* (:class:`~app.db.models.ExtractionRun`) and *document-type-
aware* field extraction sits one question: **what kind of document is this?** This module
is the replaceable, engine-neutral seam that will answer it — the same shape as the D-01
extraction seam and the field-extraction seam, for the same §6 reason: DOCURA specifies
what the layer must guarantee, not which model provides it.

What ships here is the **seam and its result type only** — not a classifier. No model is
selected (that waits on the AR-AST-008 held-out evaluation, exactly as the OCR engine
does), so the configured implementation **abstains**: it returns the ``UNCLASSIFIED``
bucket that FR-OCR-002 / AR-AST-002 / §7.1 already provide for "unrecognised", rather than
forcing a guess.

Kept deliberately distinct from its neighbours, never collapsed into them: OCR/extraction
(units of text), **classification** (a document's type — this module), field extraction
(a block's value as an attribute), the canonical vocabulary (what an attribute means), and
attribute observations (persisted values). Absent by design: any threshold (D-03, BR-001 —
a confidence is carried, compared nowhere), and any document type beyond the one the model
defines today (§7.1's set is TBD pending evaluation — none are invented here).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from app.core.logging import get_logger
from app.db.models import DocumentType, ExtractionRun

logger = get_logger(__name__)


def _check_confidence(value: float | None) -> None:
    """A classification confidence is a fraction or absent — never inferred.

    ``None`` (the engine reported none) is a different fact from a low confidence and
    stays distinguishable, mirroring the extraction seam. This is the *classification*
    confidence (FR-OCR-003); it is not, and must not be read as, a field confidence
    (FR-OCR-005) — the two live on different types and never mix.
    """
    if value is None:
        return
    if not 0.0 <= value <= 1.0:
        msg = "classification confidence must be between 0 and 1, or None where none is reported"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """What every classifier returns, whichever model produced it.

    ``document_type`` is the assigned type; ``UNCLASSIFIED`` is abstention — the
    "unrecognised / Other" bucket of FR-OCR-002 and §7.1, not a forced choice.
    ``confidence`` is the classifier's own confidence (FR-OCR-003) or ``None``.
    ``metadata`` carries engine-neutral facts for future explanation/provenance and never
    document content.
    """

    document_type: DocumentType
    confidence: float | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _check_confidence(self.confidence)

    @property
    def is_classified(self) -> bool:
        """True when a supported type was assigned; False for abstention (UNCLASSIFIED).

        The explicit form of "supported type vs unrecognised", so a consumer never has to
        infer abstention from a bare enum value. Only ``UNCLASSIFIED`` exists today, so
        this is currently always False; it flips the day §7.1's type set is populated.
        """
        return self.document_type is not DocumentType.UNCLASSIFIED


@runtime_checkable
class DocumentClassifier(Protocol):
    """Assigns a document type to a persisted extraction run.

    Engine-neutral and replaceable: it reads the :class:`ExtractionRun` graph and returns
    a :class:`ClassificationResult`. It performs no persistence — the caller owns the
    transaction. Abstaining (returning ``UNCLASSIFIED``) is a valid, honest output, not a
    failure, so — unlike the OCR extractor — there is no failure/`is_available` surface.
    """

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def classify(self, run: ExtractionRun) -> ClassificationResult:
        """The document's type, confidence, and any explanation metadata."""
        ...


class UnclassifiedClassifier:
    """The classifier in place while D-02's evaluation has not selected a model.

    It abstains on every document — the honest position when no classifier exists — by
    returning ``UNCLASSIFIED`` with no confidence. A placeholder that guessed a type would
    manufacture the evidence AR-AST-008's evaluation is meant to produce, exactly the trap
    the unconfigured OCR extractor avoids on the extraction side.
    """

    name = "unclassified"
    version = "0"

    def classify(self, run: ExtractionRun) -> ClassificationResult:
        return ClassificationResult(document_type=DocumentType.UNCLASSIFIED, confidence=None)


def build_document_classifier() -> DocumentClassifier:
    """Construct the configured classifier — the plug point, mirroring D-01.

    Returns the abstaining classifier until the held-out evaluation (AR-AST-008) selects a
    model; its implementation is then added beside this one and chosen here, a change to
    this function and nothing above it.
    """
    classifier = UnclassifiedClassifier()
    logger.info("classification.model_unconfigured", classifier=classifier.name)
    return classifier
