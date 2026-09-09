"""Sprint 4 G-13 exit criterion X12 — the vocabulary held as versioned configuration.

These tests do not evaluate extraction and assert nothing about OCR. They prove one
thing: that the canonical attribute vocabulary is held as a **structurally valid,
versioned configuration artefact** whose contents are **exactly** the approved
G-13 ``v0.1-draft`` — one entry (``person.full_name``), the seven-property shape with
no eighth property, property 7 (sensitivity tier) TBD by design, the scope-keyed
cardinality, and the approved N-TEXT normalisation semantics.

Approved content: PD-B (§21 / register D-05.11) and PD-A/C/D/E (§22 / register
D-05.12). The authoritative human record is
``backend/docs/SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md``; this test guards the
machine-readable artefact against divergence from it, and against silently widening
N-TEXT or resolving a tier that G-14/G-15 still own.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # stdlib on the project's Python 3.12; backport only where run on <3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised only on older interpreters
    import tomli as tomllib  # type: ignore[no-redef]

BACKEND_ROOT = Path(__file__).resolve().parents[1]
VOCAB_VERSION = "v0.1-draft"
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


def _load() -> dict[str, Any]:
    with VOCAB_PATH.open("rb") as handle:
        return tomllib.load(handle)


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
        """G-13.9: property 7 TBD -> NOT RELEASABLE (gate G-13-B)."""
        assert _load()["releasable"] is False

    def test_only_the_two_approved_scope_subjects_are_admitted(self) -> None:
        """G-13.2 revision (§9.0.1): person and qualification, and no others."""
        assert _load()["admitted_scope_subjects"] == ["person", "qualification"]


class TestOneApprovedEntry:
    def test_there_is_exactly_one_attribute(self) -> None:
        """PD-B item 2: the one-attribute scope. Nine candidates are not authored."""
        assert len(_load()["attribute"]) == 1

    def test_the_entry_has_exactly_the_seven_properties_and_no_eighth(self) -> None:
        attr = _load()["attribute"][0]
        assert tuple(attr.keys()) == SEVEN_PROPERTIES

    def test_the_person_full_name_entry_is_preserved_exactly(self) -> None:
        attr = _load()["attribute"][0]
        assert attr["canonical_identifier"] == "person.full_name"
        assert attr["display_label"] == "Full name"
        assert attr["semantic_definition"] == (
            "The name of the person who owns the record, "
            "as printed on a document that evidences it."
        )
        assert attr["data_type"] == "text"
        assert attr["normalisation_rule"] == "N-TEXT"

    def test_property_6_is_scope_keyed_cardinality_one_per_person(self) -> None:
        """FR-ACC-003 makes the record single-person; §12.2 makes a name diff a conflict."""
        data = _load()
        mult = data["attribute"][0]["multiplicity"]
        assert mult == {"scope_subject": "person", "cardinality": "one"}
        assert mult["scope_subject"] in data["admitted_scope_subjects"]

    def test_property_7_sensitivity_tier_is_tbd_with_the_slot_present_and_empty(self) -> None:
        """FR-INF-007 requires a tier; G-14/G-15 own it (gate G-13-B). TBD by design here."""
        tier = _load()["attribute"][0]["sensitivity_tier"]
        assert tier == {"status": "TBD", "value": ""}


class TestNTextNormalisation:
    def test_the_entry_references_a_defined_normalisation_rule(self) -> None:
        data = _load()
        rule = data["attribute"][0]["normalisation_rule"]
        assert rule in data["normalisation"], "property 5 references an undefined rule"

    def test_n_text_states_exactly_the_approved_semantics(self) -> None:
        """The four approved rules (§20.3), and applicability to `text`."""
        nt = _load()["normalisation"]["N-TEXT"]
        assert nt["applies_to_data_type"] == "text"
        assert nt["casing_is_not_meaning"] is True
        assert nt["whitespace_run_length_is_not_meaning"] is True
        assert nt["edge_whitespace_is_not_meaning"] is True
        assert nt["nothing_else_is_folded"] is True
        assert nt["raw_value_retained_and_shown"] is True

    def test_n_text_is_not_silently_widened(self) -> None:
        """No key beyond the approved set — no diacritic/unicode/nickname/edit-distance
        folding may creep in without re-approval (G-13.5, D-02 §11.6)."""
        assert set(_load()["normalisation"]["N-TEXT"].keys()) == N_TEXT_KEYS


class TestArtefactHoldsOnlyApprovedContent:
    def test_no_second_normalisation_rule_and_no_sensitivity_content(self) -> None:
        """Guards the two open gates: no tier content (G-14/G-15), one rule only."""
        data = _load()
        assert list(data["normalisation"].keys()) == ["N-TEXT"]
        assert data["attribute"][0]["sensitivity_tier"]["value"] == ""
