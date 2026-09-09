"""The field-extraction seam (Sprint 4, sixth milestone): blocks → attribute candidates.

This is the missing connection between *text that was read* and *a value recognised as a
canonical attribute*. It is a distinct layer from the three it sits between, and does not
collapse any of them:

* **extraction observations** — :class:`~app.db.models.ExtractionRun` and its pages,
  blocks, regions, and OCR confidence: units of *text*, produced by the D-01 engine seam;
* **field extraction** (this module) — deciding that a particular block's text *is* a
  known attribute's value;
* **canonical vocabulary** (``config/vocabulary/…``) — what an attribute *means*;
* **:class:`~app.db.models.AttributeObservation`** — the persisted candidate value with
  provenance and confidence, written by the existing
  :mod:`app.services.attribute_observation` service (reused, not replaced).

Like the extraction engine (D-01), the field extractor is a **replaceable, engine-neutral
seam**: it consumes the persisted extraction representation, names no OCR engine, and can
be swapped for a document-type-aware or evaluated implementation later. What ships here is
a first vertical slice for the one draft attribute (``person.full_name``) — **not**
completion of G-12, and not a production-grade extractor.

What is deliberately absent, because each is a still-open decision: a field set or
required/optional marking (G-12), a confidence threshold (D-03, BR-001 — a confidence is
carried, compared nowhere), conflict resolution across candidates (G-20 — several
candidates sit side by side, uncompared), a sensitivity tier (G-14/G-15), and any document
classification (FR-OCR-002 — the MVP slice is type-agnostic, as ``person.full_name`` is in
the draft evidence).
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Protocol, runtime_checkable

try:  # stdlib on the project's Python 3.12
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only on older interpreters
    import tomli as tomllib  # type: ignore[no-redef]

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import AttributeObservation, ExtractionRun
from app.services.attribute_observation import CandidateObservation, build_attribute_observations

logger = get_logger(__name__)

_VOCAB_PATH = (
    Path(__file__).resolve().parents[2]  # app/services/ -> backend/
    / "config"
    / "vocabulary"
    / "canonical_attributes.v0.1-draft.toml"
)

# The one draft attribute this slice recognises. Referenced by identifier only; the
# extractor emits it solely when the versioned vocabulary still defines it (below).
_PERSON_FULL_NAME = "person.full_name"

# A single block of the form "<name label><sep><value>", e.g. "Name: Priya Sharma" or
# "Full Name - Priya Sharma". Case-insensitive; the value is whatever follows the
# separator. This is the whole heuristic — see FullNameFieldExtractor for its limits.
_FULL_NAME_LINE = re.compile(
    r"^\s*(?:full\s+name|name)\s*[:\-]\s*(?P<value>.+?)\s*$", re.IGNORECASE
)


@lru_cache(maxsize=1)
def _canonical_identifiers() -> frozenset[str]:
    """The identifiers the versioned vocabulary currently defines, read from config."""
    with _VOCAB_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    return frozenset(entry["canonical_identifier"] for entry in data.get("attribute", []))


@runtime_checkable
class FieldExtractor(Protocol):
    """Turns a persisted extraction run into candidate attribute observations.

    Engine-neutral and replaceable: it reads the :class:`ExtractionRun` graph (pages,
    blocks, regions, confidence) and returns candidates that name a canonical attribute
    by identifier and point at the exact block they came from. It performs no I/O and
    persists nothing — the caller owns the transaction. An implementation that returns
    ``[]`` for input it does not recognise is behaving correctly, never inventing output.
    """

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def extract_fields(self, run: ExtractionRun) -> list[CandidateObservation]:
        """Candidates read from ``run``'s in-memory block graph. May be empty."""
        ...


class FullNameFieldExtractor:
    """Deterministic MVP: ``person.full_name`` from a single labelled block.

    **Assumptions, stated plainly (this is a first slice, not production extraction):**

    * It recognises **only** ``person.full_name``, and only from a **single** block whose
      text is ``<name label><:|-><value>`` (e.g. ``"Name: Priya Sharma"``). A label and a
      value in *separate* blocks are not handled — deliberately, so provenance stays one
      block and no confidence has to be combined.
    * The value is the text after the separator, stripped; an empty value yields nothing.
    * It is **document-type-agnostic**, because the draft evidence lists ``person.full_name``
      across every candidate type (G-12 §19); a type-aware extractor can inspect
      ``run.document`` later without changing this seam.
    * It emits nothing when the vocabulary no longer defines ``person.full_name`` — it
      references the vocabulary rather than asserting the attribute exists.

    **Provenance and confidence.** Each candidate points at the exact block matched, and
    carries **that block's** OCR confidence unchanged — or ``None`` where the engine gave
    none. Because a candidate comes from one block, no confidence is combined or invented.

    No accuracy is claimed. Several matching blocks produce several candidates; nothing
    here compares or de-duplicates them (G-20).
    """

    name = "deterministic-full-name"
    version = "0.1-draft"

    def extract_fields(self, run: ExtractionRun) -> list[CandidateObservation]:
        if _PERSON_FULL_NAME not in _canonical_identifiers():
            return []
        candidates: list[CandidateObservation] = []
        for page in run.pages:
            for block in page.blocks:
                match = _FULL_NAME_LINE.match(block.text)
                if match is None:
                    continue
                value = match.group("value").strip()
                if not value:
                    continue
                candidates.append(
                    CandidateObservation(
                        canonical_identifier=_PERSON_FULL_NAME,
                        value=value,
                        source_block=block,
                        confidence=block.confidence,  # attributable, or None; never invented
                    )
                )
        return candidates


def build_field_extractor() -> FieldExtractor:
    """Construct the configured field extractor — the plug point, mirroring D-01.

    Returns the deterministic ``person.full_name`` slice. It is engine-neutral (it maps
    already-extracted text, not pixels), so it is usable independently of which OCR engine
    D-01 eventually selects. A later, evaluated, or type-aware extractor replaces it here.
    """
    return FullNameFieldExtractor()


async def apply_field_extraction(
    db: AsyncSession, *, run: ExtractionRun, extractor: FieldExtractor
) -> list[AttributeObservation]:
    """Persist candidate observations for one **flushed** run. Idempotent per run.

    The caller owns the transaction: ``run`` and its blocks must already have ids (the
    graph is flushed, not committed), so observations point at real blocks and commit with
    them atomically. **Idempotency:** a run that already carries observations is not
    re-extracted, so running twice against the same run cannot duplicate; a *different*
    run has its own id and is unaffected — which is exactly the run-owned history model, so
    no schema constraint is added for it. Returns the observations added (``[]`` if the run
    was already extracted or nothing was recognised).
    """
    already = await db.scalar(
        select(func.count())
        .select_from(AttributeObservation)
        .where(AttributeObservation.run_id == run.id)
    )
    if already:
        return []
    observations = build_attribute_observations(run=run, candidates=extractor.extract_fields(run))
    db.add_all(observations)
    # Flush so the run now visibly carries observations: a second call in the same
    # session sees them and skips, regardless of the session's autoflush setting.
    await db.flush()
    return observations
