"""Sprint 4 G-13 exit criterion X12 — the vocabulary held as versioned configuration.

These tests do not evaluate extraction and assert nothing about OCR. They prove one
thing: that the canonical attribute vocabulary is held as a **structurally valid,
versioned configuration artefact** whose contents are **exactly** the approved G-13
``v0.2-draft`` — two entries (``person.full_name`` and ``person.date_of_birth``, M12-D3),
the seven-property shape with no eighth property, property 7 (sensitivity tier) TBD by
design on BOTH entries, the scope-keyed cardinality, and the approved N-TEXT / N-DATE
normalisation semantics.

Approved content: PD-B (§21 / register D-05.11) and PD-A/C/D/E (§22 / register D-05.12)
for the first entry; **M12-D3** (17 Sep 2026) for the second entry and N-DATE. The
authoritative human record is ``backend/docs/SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md``;
this test guards the machine-readable artefact against divergence from it, against silently
widening N-TEXT/N-DATE, and against resolving a tier that G-14/G-15 still own.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # stdlib on the project's Python 3.12; backport only where run on <3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised only on older interpreters
    import tomli as tomllib  # type: ignore[no-redef]

BACKEND_ROOT = Path(__file__).resolve().parents[1]
VOCAB_VERSION = "v0.2-draft"
VOCAB_PATH = BACKEND_ROOT / "config" / "vocabulary" / f"canonical_attributes.{VOCAB_VERSION}.toml"

# The seven properties of G-13.2, in order. Exactly these — no eighth.
SEVEN_PROPERTIES = (
    "canonical_identifier",
    "display_label",
    "semantic_definition",
    "data_type",
    "normalisation_rule",
    "multiplicity",
    "sensitivity_tier",
)

# N-TEXT's approved keys (§20.3 / §21.1). Exactly these — no widening.
N_TEXT_KEYS = {
    "applies_to_data_type",
    "casing_is_not_meaning",
    "whitespace_run_length_is_not_meaning",
    "edge_whitespace_is_not_meaning",
    "nothing_else_is_folded",
    "raw_value_retained_and_shown",
}

# N-DATE's approved keys (M12-D3). Exactly these — no widening (no ambiguous-format parsing).
N_DATE_KEYS = {
    "applies_to_data_type",
    "surface_format_is_not_meaning",
    "calendar_date_is_meaning",
    "nothing_else_is_folded",
    "raw_value_retained_and_shown",
}


def _load() -> dict[str, Any]:
    with VOCAB_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _entry(identifier: str) -> dict[str, Any]:
    return next(a for a in _load()["attribute"] if a["canonical_identifier"] == identifier)


class TestArtefactStructure:
    def test_the_artefact_exists_and_parses(self) -> None:
        assert VOCAB_PATH.is_file(), f"vocabulary artefact missing: {VOCAB_PATH}"
        assert isinstance(_load(), dict)

    def test_it_is_versioned_and_the_version_matches_its_filename(self) -> None:
        """G-13.10: the artefact is versioned. Filename and content must agree."""
        data = _load()
        assert data["vocabulary_version"] == VOCAB_VERSION
        assert f".{VOCAB_VERSION}.toml" in VOCAB_PATH.name

    def test_it_is_not_releasable_while_a_tier_is_tbd(self) -> None:
        """G-13.9: any property 7 TBD -> NOT RELEASABLE (gate G-13-B). Both tiers are TBD."""
        assert _load()["releasable"] is False

    def test_only_the_two_approved_scope_subjects_are_admitted(self) -> None:
        """G-13.2 revision (§9.0.1): person and qualification, and no others."""
        assert _load()["admitted_scope_subjects"] == ["person", "qualification"]


class TestAuthoredEntries:
    def test_there_are_exactly_two_attributes(self) -> None:
        """M12-D3: full_name (PD-B) and date_of_birth. No other candidate is authored."""
        assert len(_load()["attribute"]) == 2

    def test_the_authored_identifiers_are_exactly_these_two(self) -> None:
        ids = {a["canonical_identifier"] for a in _load()["attribute"]}
        assert ids == {"person.full_name", "person.date_of_birth"}

    def test_every_entry_has_exactly_the_seven_properties_and_no_eighth(self) -> None:
        for attr in _load()["attribute"]:
            assert tuple(attr.keys()) == SEVEN_PROPERTIES

    def test_the_person_full_name_entry_is_preserved_exactly(self) -> None:
        attr = _entry("person.full_name")
        assert attr["display_label"] == "Full name"
        assert attr["semantic_definition"] == (
            "The name of the person who owns the record, "
            "as printed on a document that evidences it."
        )
        assert attr["data_type"] == "text"
        assert attr["normalisation_rule"] == "N-TEXT"

    def test_the_person_date_of_birth_entry(self) -> None:
        attr = _entry("person.date_of_birth")
        assert attr["display_label"] == "Date of birth"
        assert attr["data_type"] == "date"
        assert attr["normalisation_rule"] == "N-DATE"

    def test_every_entry_is_scope_keyed_cardinality_one_per_person(self) -> None:
        data = _load()
        for attr in data["attribute"]:
            mult = attr["multiplicity"]
            assert mult == {"scope_subject": "person", "cardinality": "one"}
            assert mult["scope_subject"] in data["admitted_scope_subjects"]

    def test_property_7_sensitivity_tier_is_tbd_on_both_entries(self) -> None:
        """FR-INF-007 requires a tier; G-14/G-15 own it (gate G-13-B). TBD by design here.
        No tier content — in particular date_of_birth is NOT stamped sensitive (D-06.5 §D)."""
        for attr in _load()["attribute"]:
            assert attr["sensitivity_tier"] == {"status": "TBD", "value": ""}


class TestNormalisationRules:
    def test_each_entry_references_a_defined_normalisation_rule(self) -> None:
        data = _load()
        for attr in data["attribute"]:
            assert attr["normalisation_rule"] in data["normalisation"]

    def test_n_text_states_exactly_the_approved_semantics(self) -> None:
        nt = _load()["normalisation"]["N-TEXT"]
        assert nt["applies_to_data_type"] == "text"
        assert nt["casing_is_not_meaning"] is True
        assert nt["whitespace_run_length_is_not_meaning"] is True
        assert nt["edge_whitespace_is_not_meaning"] is True
        assert nt["nothing_else_is_folded"] is True
        assert nt["raw_value_retained_and_shown"] is True

    def test_n_text_is_not_silently_widened(self) -> None:
        assert set(_load()["normalisation"]["N-TEXT"].keys()) == N_TEXT_KEYS

    def test_n_date_states_the_minimum_semantic_date_rule(self) -> None:
        """M12-D3: same calendar date is one value; a different calendar date is a difference."""
        nd = _load()["normalisation"]["N-DATE"]
        assert nd["applies_to_data_type"] == "date"
        assert nd["surface_format_is_not_meaning"] is True
        assert nd["calendar_date_is_meaning"] is True
        assert nd["nothing_else_is_folded"] is True
        assert nd["raw_value_retained_and_shown"] is True

    def test_n_date_is_not_silently_widened(self) -> None:
        """No ambiguous-format parsing / century inference / timezone folding creeps in
        without re-approval (G-13.5, D-02 §11.6)."""
        assert set(_load()["normalisation"]["N-DATE"].keys()) == N_DATE_KEYS


class TestArtefactHoldsOnlyApprovedContent:
    def test_exactly_two_normalisation_rules_and_no_sensitivity_content(self) -> None:
        """Guards the two open gates: no tier content (G-14/G-15); exactly the two rules."""
        data = _load()
        assert set(data["normalisation"].keys()) == {"N-TEXT", "N-DATE"}
        for attr in data["attribute"]:
            assert attr["sensitivity_tier"]["value"] == ""
