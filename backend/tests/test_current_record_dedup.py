"""False-duplicate OCR observations must collapse; genuine conflicts must not (G-20).

A single document can report the same value for a field more than once (the same value read
twice on a page, or matched by two aliases). Those exact duplicates were surfacing as multiple
competing record values / duplicate source chips — a *false* conflict. These pure tests pin the
fix in :func:`app.services.current_record._resolve`: exact duplicates (same document, page,
attribute, normalised value) collapse to one candidate, while genuinely different values stay a
conflict, exactly as before. No DB — the derivation is a pure function of its observations.
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any

from app.services.current_record import _resolve

FULL_NAME = "person.full_name"  # N-TEXT (folds case/whitespace) in the v0.2-draft vocabulary
ADDRESS = "person.address"  # not in v0.2-draft → compared verbatim

DOC_A = uuid.uuid4()
DOC_B = uuid.uuid4()


def obs(
    value: str, *, doc: uuid.UUID = DOC_A, page: int = 1, confidence: float | None = 0.9
) -> Any:
    """An observation double carrying the provenance chain _resolve reads (block→page→run)."""
    run = SimpleNamespace(document_id=doc, id=uuid.uuid4())
    pg = SimpleNamespace(number=page, run=run)
    block = SimpleNamespace(page=pg, text=value)
    return SimpleNamespace(value=value, confidence=confidence, source_block=block)


# 1. Same document + page + field + value twice → ONE candidate, ONE source (no false conflict).
def test_same_doc_page_value_twice_collapses_to_one() -> None:
    r = _resolve(FULL_NAME, [obs("Vedant Santosh Kadam"), obs("Vedant Santosh Kadam")])
    assert r.is_ambiguous is False
    assert r.value == "Vedant Santosh Kadam"
    assert len(r.observations) == 1  # 6. duplicate source chips not shown twice


# 1b. Exact duplicates via a normalisation-equal variant (N-TEXT folds case/whitespace) collapse.
def test_normalisation_equal_duplicates_on_same_page_collapse() -> None:
    r = _resolve(FULL_NAME, [obs("Vedant Santosh Kadam"), obs("vedant   santosh kadam")])
    assert r.is_ambiguous is False
    assert len(r.observations) == 1


# 2. Same document, same value, DIFFERENT pages → not a conflict; both pages kept as sources.
def test_same_value_different_pages_is_not_a_conflict() -> None:
    r = _resolve(ADDRESS, [obs("Mumbai, Maharashtra", page=1), obs("Mumbai, Maharashtra", page=2)])
    assert r.is_ambiguous is False
    assert r.value == "Mumbai, Maharashtra"
    assert len(r.observations) == 2  # legitimately separate observations, not duplicates


# 3. Different documents, same value → one logical value with multiple supporting sources.
def test_same_value_across_documents_is_one_value_two_sources() -> None:
    r = _resolve(
        ADDRESS, [obs("Mumbai, Maharashtra", doc=DOC_A), obs("Mumbai, Maharashtra", doc=DOC_B)]
    )
    assert r.is_ambiguous is False
    assert r.value == "Mumbai, Maharashtra"
    assert len(r.observations) == 2


# 4. Different documents, different values → genuine conflict remains (G-20).
def test_different_values_across_documents_remain_a_conflict() -> None:
    r = _resolve(ADDRESS, [obs("Mumbai", doc=DOC_A), obs("Pune", doc=DOC_B)])
    assert r.is_ambiguous is True
    assert r.value is None
    assert len(r.observations) == 2


# 5. Same document + page, genuinely different values → conflict remains (never auto-resolved).
def test_genuinely_different_values_same_page_remain_a_conflict() -> None:
    r = _resolve(FULL_NAME, [obs("Vedant Santosh Kadam"), obs("Vedant Kumar Kadam")])
    assert r.is_ambiguous is True
    assert r.value is None
    assert len(r.observations) == 2


# 5b. A real conflict is not masked when it is mixed with exact duplicates of one side.
def test_duplicates_do_not_hide_a_real_conflicting_value() -> None:
    r = _resolve(
        ADDRESS,
        [obs("Mumbai", doc=DOC_A), obs("Mumbai", doc=DOC_A), obs("Pune", doc=DOC_B)],
    )
    assert r.is_ambiguous is True  # Mumbai vs Pune still conflicts
    assert len(r.observations) == 2  # the two Mumbai readings collapsed to one; Pune remains


# 7. Existing ambiguity behaviour is unchanged for values that are not duplicates.
def test_ambiguity_threshold_unchanged_for_distinct_values() -> None:
    single = _resolve(ADDRESS, [obs("Mumbai")])
    assert single.is_ambiguous is False
    two = _resolve(ADDRESS, [obs("Mumbai"), obs("Delhi")])
    assert two.is_ambiguous is True


# 8. Confidence and provenance are preserved on the surviving observation (first occurrence).
def test_confidence_and_provenance_preserved_on_survivor() -> None:
    first = obs("Vedant Santosh Kadam", confidence=0.42)
    dup = obs("Vedant Santosh Kadam", confidence=0.99)
    r = _resolve(FULL_NAME, [first, dup])
    assert len(r.observations) == 1
    assert r.observations[0] is first  # first-occurrence kept, order stable
    assert r.observations[0].confidence == 0.42
    assert r.observations[0].source_block is first.source_block  # provenance intact, not removed
