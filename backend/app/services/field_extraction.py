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
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.core.config import Settings

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
    / "canonical_attributes.v0.2-draft.toml"
)

# The two controlled attributes this slice recognises. Referenced by identifier only; each
# extractor emits its attribute solely when the versioned vocabulary still defines it (below).
_PERSON_FULL_NAME = "person.full_name"
_PERSON_DATE_OF_BIRTH = "person.date_of_birth"

# A single block of the form "<name label><sep?><value>", e.g. "Name: Priya Sharma",
# "Full Name - Priya Sharma", or "Full Name Vedant Santosh Kadam" (a table row where the
# label and value sit on one OCR line, separated only by whitespace). The separator is
# optional; the value is whatever follows it. Case-insensitive. See FullNameFieldExtractor.
_FULL_NAME_LINE = re.compile(
    r"^\s*(?:full\s+name|name)\s*[:\-]?\s+(?P<value>\S.*?)\s*$", re.IGNORECASE
)

# A single block of the form "date of birth<sep?><value>", e.g. "Date of Birth: 24 March
# 2007" or the table-row form "Date of Birth 24 March 2007". See DateOfBirthFieldExtractor.
_DOB_LINE = re.compile(
    r"^\s*date\s+of\s+birth\s*[:\-]?\s+(?P<value>\S.*?)\s*$", re.IGNORECASE
)

# English month names, lower-cased. Deliberately NOT multilingual: N-DATE excludes ambiguous
# parsing (vocabulary §N-DATE), and the only date evidence we have is English "24 March 2007".
_MONTHS = {
    name.lower(): index
    for index, name in enumerate(
        (
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ),
        start=1,
    )
}

# The only two date surface forms justified by the current controlled evidence: ISO
# "YYYY-MM-DD" (already canonical) and "D[D] <MonthName> YYYY" (the test document's form).
_DOB_ISO = re.compile(r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})$")
_DOB_DAY_MONTH_YEAR = re.compile(r"^(?P<d>\d{1,2})\s+(?P<month>[A-Za-z]+)\s+(?P<y>\d{4})$")


def _normalise_date_of_birth(raw: str) -> str | None:
    """Normalise a recognised date to canonical ISO ``YYYY-MM-DD`` (N-DATE), or ``None``.

    Only the two surface forms above are accepted; anything else — or a value that does not
    denote a real calendar date (e.g. "31 February 2007") — returns ``None`` so no observation
    is produced. Nothing is guessed: no locale-ambiguous DD/MM inference, no two-digit-year
    completion (those are excluded by the vocabulary's N-DATE rule).
    """
    value = " ".join(raw.split())
    iso = _DOB_ISO.match(value)
    dmy = _DOB_DAY_MONTH_YEAR.match(value)
    try:
        if iso is not None:
            parsed = date(int(iso["y"]), int(iso["m"]), int(iso["d"]))
        elif dmy is not None:
            month = _MONTHS.get(dmy["month"].lower())
            if month is None:
                return None
            parsed = date(int(dmy["y"]), month, int(dmy["d"]))
        else:
            return None
    except ValueError:
        return None  # a well-formed shape that is not a real date — do not guess
    return parsed.isoformat()


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


class DateOfBirthFieldExtractor:
    """Deterministic controlled extractor: ``person.date_of_birth`` from a labelled block.

    Mirrors :class:`FullNameFieldExtractor`'s discipline: it recognises **only**
    ``person.date_of_birth``, and only from a single block whose text is
    ``date of birth <sep?> <value>``. The value is normalised to canonical ISO
    (``YYYY-MM-DD``, N-DATE) by :func:`_normalise_date_of_birth`; a value in an unsupported
    surface form or one that is not a real calendar date yields **nothing** — it never guesses
    (M22 §5). It emits nothing when the vocabulary no longer defines the attribute.

    Provenance is the exact matched block; confidence is that block's OCR confidence unchanged
    (or ``None``). The stored value is the canonical ISO form so agreeing dates fold together
    and disagreeing ones surface as a conflict through the existing record logic.
    """

    name = "deterministic-date-of-birth"
    version = "0.2-draft"

    def extract_fields(self, run: ExtractionRun) -> list[CandidateObservation]:
        if _PERSON_DATE_OF_BIRTH not in _canonical_identifiers():
            return []
        candidates: list[CandidateObservation] = []
        for page in run.pages:
            for block in page.blocks:
                match = _DOB_LINE.match(block.text)
                if match is None:
                    continue
                normalised = _normalise_date_of_birth(match.group("value"))
                if normalised is None:
                    continue  # unsupported/invalid date — no observation, no guess
                candidates.append(
                    CandidateObservation(
                        canonical_identifier=_PERSON_DATE_OF_BIRTH,
                        value=normalised,
                        source_block=block,
                        confidence=block.confidence,  # attributable, or None; never invented
                    )
                )
        return candidates


class ControlledFieldExtractor:
    """The controlled field extractor: the currently approved attributes, and only those.

    Composes the two single-attribute extractors (``person.full_name`` and
    ``person.date_of_birth``). It adds no new canonical attribute and folds no candidates
    together — each sub-extractor contributes its candidates independently, and ambiguity /
    conflict is left to the existing current-record derivation (G-20).
    """

    name = "controlled-fields"
    version = "0.2-draft"

    def __init__(self) -> None:
        self._extractors: tuple[FieldExtractor, ...] = (
            FullNameFieldExtractor(),
            DateOfBirthFieldExtractor(),
        )

    def extract_fields(self, run: ExtractionRun) -> list[CandidateObservation]:
        candidates: list[CandidateObservation] = []
        for extractor in self._extractors:
            candidates.extend(extractor.extract_fields(run))
        return candidates


# ---------------------------------------------------------------------------------------------
# DEMO field extractor (dev/evaluation only, DOCURA_DEMO_MODE=true) — NOT production-released.
# ---------------------------------------------------------------------------------------------

_DEMO_VOCAB_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "vocabulary"
    / "canonical_attributes.demo.toml"
)


def _normalize_label(raw: str) -> str:
    """Fold a label for exact alias comparison: lower-case, separators→space, drop other
    punctuation, collapse whitespace. Meaning-preserving, NOT fuzzy (mirrors the extension's
    ``normalizeLabel``)."""
    text = raw.lower()
    text = re.sub(r"[._\-/]+", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True, slots=True)
class _DemoVocab:
    alias_to_canonical: dict[str, str]
    rule: dict[str, str]


@lru_cache(maxsize=1)
def _load_demo_vocab() -> _DemoVocab:
    with _DEMO_VOCAB_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    alias_to_canonical: dict[str, str] = {}
    rule: dict[str, str] = {}
    for entry in data.get("attribute", []):
        canonical = str(entry["canonical_identifier"])
        rule[canonical] = str(entry.get("normalisation_rule", "verbatim"))
        for alias in entry.get("aliases", []):
            norm = _normalize_label(str(alias))
            if norm:
                alias_to_canonical[norm] = canonical
    return _DemoVocab(alias_to_canonical=alias_to_canonical, rule=rule)


def _demo_split(text: str, alias_to_canonical: dict[str, str]) -> tuple[str, str] | None:
    """Find a labelled key/value in one line: ``Label: Value`` / ``Label - Value`` /
    ``Label Value``. Returns (canonical_identifier, raw_value) on an EXACT alias match, else
    None. No fuzzy/substring guessing (BR-009)."""
    stripped = text.strip()
    for sep in (":", " - "):
        if sep in stripped:
            left, right = stripped.split(sep, 1)
            canonical = alias_to_canonical.get(_normalize_label(left))
            if canonical and right.strip():
                return canonical, right.strip()
            return None
    tokens = stripped.split()
    for k in range(min(len(tokens) - 1, 4), 0, -1):  # longest alias prefix wins; ≥1 value token
        canonical = alias_to_canonical.get(_normalize_label(" ".join(tokens[:k])))
        if canonical:
            value = " ".join(tokens[k:]).strip()
            if value:
                return canonical, value
    return None


def _normalise_demo_value(canonical: str, raw: str, rules: dict[str, str]) -> str | None:
    """Normalise a demo value: N-DATE → ISO (or None if unrecognised); otherwise trim/collapse
    whitespace. Never guesses a date it cannot parse."""
    if rules.get(canonical) == "N-DATE":
        return _normalise_date_of_birth(raw)
    collapsed = " ".join(raw.split())
    return collapsed or None


class DemoFieldExtractor:
    """DEMO-ONLY: discover common labelled key/value fields from OCR line blocks using the
    data-driven demo synonym vocabulary. Same discipline as the controlled extractors —
    exact alias match, one source block per value, honest confidence, no guessing. Handles a
    ``Label: Value`` / ``Label Value`` line and a label-only line followed by a value line.

    It is engine-neutral and adds no new architecture — it emits ``CandidateObservation``s the
    existing observation service persists. It is used ONLY under ``DOCURA_DEMO_MODE``; the
    attributes it names are demo attributes, not production-released (see the demo vocabulary).
    """

    name = "demo-dynamic-fields"
    version = "demo-v1"

    def extract_fields(self, run: ExtractionRun) -> list[CandidateObservation]:
        vocab = _load_demo_vocab()
        candidates: list[CandidateObservation] = []
        for page in run.pages:
            blocks = list(page.blocks)
            consumed: set[int] = set()
            for i, block in enumerate(blocks):
                if i in consumed:
                    continue
                result = _demo_split(block.text, vocab.alias_to_canonical)
                source = block
                if result is None:
                    # A label-only line ("Full Name") takes the next line as its value.
                    canonical = vocab.alias_to_canonical.get(_normalize_label(block.text))
                    if canonical is not None and i + 1 < len(blocks):
                        source = blocks[i + 1]
                        result = (canonical, source.text.strip())
                        consumed.add(i + 1)
                if result is None:
                    continue
                canonical, raw_value = result
                value = _normalise_demo_value(canonical, raw_value, vocab.rule)
                if value is None:
                    continue
                candidates.append(
                    CandidateObservation(
                        canonical_identifier=canonical,
                        value=value,
                        source_block=source,
                        confidence=source.confidence,  # measured, or None; never invented
                    )
                )
        return candidates


def build_field_extractor(settings: Settings | None = None) -> FieldExtractor:
    """Construct the configured field extractor — the plug point, mirroring D-01.

    Default (production posture): the controlled extractor for the currently approved attributes
    (``person.full_name`` and ``person.date_of_birth``). When ``settings.demo_mode`` is set
    (``DOCURA_DEMO_MODE=true``, dev/evaluation only), the DEMO extractor is used instead so the
    end-to-end dynamic demo can discover common labelled fields. It is engine-neutral, so it is
    usable independently of which OCR engine D-01 eventually selects.
    """
    if settings is not None and settings.demo_mode:
        return DemoFieldExtractor()
    return ControlledFieldExtractor()


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
