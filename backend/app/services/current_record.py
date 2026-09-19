"""The user's current structured record (Sprint 4, fourth milestone).

This is the derived view that answers one question: *what is the current known value
for this canonical attribute, for this user?* — while keeping the underlying
:class:`~app.db.models.AttributeObservation` history and its provenance intact.

    user → canonical attribute → current value → supporting observation(s)
         → extraction run → document

It is **derived, never stored**. There is no structured-record table: "current" is
recomputed from observation history on every read, so a new extraction run changes it
with no rebuild step and no ``is_current`` flag — the same discipline
:func:`app.services.attribute_observation.list_current_attribute_observations` uses per
document, lifted to *all* of a user's documents at once.

Three still-open decisions are deliberately **not** made here:

* **G-20 (conflict resolution).** When a user's documents disagree on an attribute, no
  precedence rule is approved, so none is invented: the disagreement is exposed as
  ambiguity rather than silently resolved. Values that *agree* under the attribute's
  approved normalisation are not a conflict — they are one value.
* **G-12/G-13 (the vocabulary itself).** Only the identifier is used, referenced from
  the versioned configuration; the definition is never copied.
* **G-14/G-15 (sensitivity tiers).** Absent — a property of the definition, not a value.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:  # stdlib on the project's Python 3.12
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only on older interpreters
    import tomli as tomllib  # type: ignore[no-redef]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.db.models import (
    AttributeObservation,
    Document,
    ExtractionBlock,
    ExtractionPage,
    ExtractionRun,
)

# The current vocabulary artefact (v0.2-draft, M12-D3). v0.1-draft is retained as the
# immutable historical version; pinned by name like the vocabulary tests.
_VOCAB_PATH = (
    Path(__file__).resolve().parents[2]  # app/services/ -> backend/
    / "config"
    / "vocabulary"
    / "canonical_attributes.v0.2-draft.toml"
)


@lru_cache(maxsize=1)
def _ntext_identifiers() -> frozenset[str]:
    """Identifiers whose approved normalisation rule is N-TEXT, read from the vocabulary.

    Read from configuration, never hard-coded here: an attribute carrying any other
    rule — or one still TBD — is not folded, so no normalisation is invented for an
    attribute the vocabulary has not approved one for.
    """
    with _VOCAB_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    return frozenset(
        entry["canonical_identifier"]
        for entry in data.get("attribute", [])
        if entry.get("normalisation_rule") == "N-TEXT"
    )


def _comparison_form(canonical_identifier: str, value: str) -> str:
    """The approved comparison-time form of a value (G-13 N-TEXT), or the value verbatim.

    N-TEXT folds casing and whitespace-run length and edge whitespace, and **nothing
    else** (§20.3): ``" ".join(value.split())`` collapses whitespace runs and strips the
    edges, ``casefold`` removes casing. Only identifiers the vocabulary marks N-TEXT are
    folded; every other identifier is compared verbatim. The raw value is what is retained
    and shown (N-TEXT rule 4) — this form is used only to decide whether values agree.
    """
    if canonical_identifier in _ntext_identifiers():
        return " ".join(value.split()).casefold()
    return value


@dataclass(frozen=True, slots=True)
class CurrentAttributeValue:
    """The current known value of one canonical attribute for one user — a derived view.

    ``observations`` are the supporting current observations (the newest run's, per
    document, across the user's documents), in deterministic order, each keeping its own
    provenance (block → page → run → document) and confidence. When they agree on a value
    under the attribute's approved normalisation, ``value`` is that value in the raw form
    of the first supporting observation (N-TEXT retains the raw). When they disagree,
    ``is_ambiguous`` is True and ``value`` is None: G-20 has no approved precedence rule,
    so no winner is chosen here and every candidate stays visible on ``observations``.
    """

    canonical_identifier: str
    value: str | None
    is_ambiguous: bool
    observations: tuple[AttributeObservation, ...]


async def _current_observations(
    db: AsyncSession, *, user_id: uuid.UUID, canonical_identifier: str | None = None
) -> list[AttributeObservation]:
    """The user's current observations: each document's newest run's, user-scoped.

    User isolation is in the ``WHERE`` clause, never a post-load check (NFR-SEC-003): a
    row belonging to another account cannot enter the set. "Current" per document is the
    newest run — a failed attempt persists none — so a reprocess supersedes a document's
    contribution simply by adding a newer run. Ordered deterministically so grouping is
    stable.
    """
    inner_run = aliased(ExtractionRun)
    newest_run_for_document = (
        select(inner_run.id)
        .where(inner_run.document_id == Document.id)
        .order_by(inner_run.created_at.desc(), inner_run.id.desc())
        .limit(1)
        # Correlate only the outer Document; the aliased run is the subquery's own FROM.
        .correlate(Document)
        .scalar_subquery()
    )
    query = (
        select(AttributeObservation)
        .join(ExtractionRun, AttributeObservation.run_id == ExtractionRun.id)
        .join(Document, ExtractionRun.document_id == Document.id)
        .where(
            Document.user_id == user_id,
            ExtractionRun.id == newest_run_for_document,
        )
        .order_by(
            AttributeObservation.canonical_identifier,
            ExtractionRun.created_at,
            AttributeObservation.id,
        )
        # Eager-load the provenance chain (block → page → run) so a caller — the
        # retrieval API — can project it without an async lazy load. Additive: the
        # existing callers ignore it.
        .options(
            selectinload(AttributeObservation.source_block)
            .selectinload(ExtractionBlock.page)
            .selectinload(ExtractionPage.run)
        )
    )
    if canonical_identifier is not None:
        query = query.where(AttributeObservation.canonical_identifier == canonical_identifier)
    result = await db.scalars(query)
    return list(result)


def _resolve(
    canonical_identifier: str, observations: list[AttributeObservation]
) -> CurrentAttributeValue:
    """Fold agreeing observations into one value; expose disagreement as ambiguity."""
    distinct = {_comparison_form(canonical_identifier, o.value) for o in observations}
    ambiguous = len(distinct) > 1
    return CurrentAttributeValue(
        canonical_identifier=canonical_identifier,
        value=None if ambiguous else observations[0].value,
        is_ambiguous=ambiguous,
        observations=tuple(observations),
    )


async def build_current_record(
    db: AsyncSession, *, user_id: uuid.UUID
) -> list[CurrentAttributeValue]:
    """The user's whole current record — one entry per canonical attribute, deterministic.

    Read-only and recomputed from history; the caller owns the transaction. Attributes
    are returned in canonical-identifier order.
    """
    observations = await _current_observations(db, user_id=user_id)
    grouped: dict[str, list[AttributeObservation]] = {}
    for observation in observations:
        grouped.setdefault(observation.canonical_identifier, []).append(observation)
    return [_resolve(identifier, group) for identifier, group in sorted(grouped.items())]


async def get_current_value(
    db: AsyncSession, *, user_id: uuid.UUID, canonical_identifier: str
) -> CurrentAttributeValue | None:
    """The current value for one canonical attribute, or ``None`` if the user has none."""
    observations = await _current_observations(
        db, user_id=user_id, canonical_identifier=canonical_identifier
    )
    if not observations:
        return None
    return _resolve(canonical_identifier, observations)
