# DOCURA — Sprint 4 M11 Controlled-Form Information Mapping Decision

| Field | Value |
| --- | --- |
| Status | **BLOCKED for expansion — evidence/decision required.** The approved controlled-form mapping set is **unchanged from M10**: `person.full_name` only. |
| Authority | `config/vocabulary/canonical_attributes.v0.1-draft.toml`, `SPRINT_4_DECISION_REGISTER.md` (D-05.6/.8/.9), `SPRINT_4_G12_FIELD_DEFINITIONS.md`, `SPRINT_4_G13_*`, `SPRINT_4_MOCK_FORM_FIELD_INVENTORY.md` |
| Rule applied | M11 §2 (no "approve everything"), §6 (no duplicate concepts; stop if a decision is required), **§25 (insufficient evidence → DO NOT CODE; report BLOCKED)** |
| Code changed | **No new mapping/attribute.** The only code change is a **safety hardening** (M11-D5): the controlled mapping is now scoped to the controlled form's identity so it cannot fire on arbitrary external forms. The frozen `v0.1-draft.toml` is untouched (adding an entry would fail `tests/test_vocabulary_config.py::test_there_is_exactly_one_attribute`). |

## 1. G-12 / G-13 findings (verified against the repository)

- The authoritative vocabulary config holds **exactly one approved attribute: `person.full_name`** (PD-B, 7 Sep 2026; D-05.11). `releasable = false`; `admitted_scope_subjects = ["person","qualification"]`.
- The register is explicit: **"the ten G-12 candidate attributes are not approved"** and **"nine candidates are not authored"** (D-05.8, D-05.9). Only `person.full_name` is authored.
- Two-gate model (D-05.8): **G-13-A** (structural authoring) and **G-13-B** (releasable, every tier assigned). **Both NOT MET.** G-13-B is the gate that controls **"automatic placement of any value into a form"** (FR-INF-007; FR-SENS-002/BR-005) and depends on **G-14/G-15** (assumption A-5; studies S-1/S-4) — unresolved.
- Normalisation: N-TEXT (casing/spacing) approved for `text`; **"dates and numeric precision remain TBD"** — there is no approved normalisation rule for a `date` or numeric attribute.
- Sensitivity tiers are **TBD on every entry** (G-14/G-15 unresolved). This is separate from "personal" (M11 §8): an attribute being personal does not set its tier.

## 2. Proposed mapping table (§7) with evidence and decision

| Form field | Canonical attribute | Evidence in repo | Automation | Decision |
| --- | --- | --- | --- | --- |
| `full_name` | `person.full_name` | **Approved** (PD-B, v0.1-draft); N-TEXT approved; consumer FR-FILL-001 + FR-INF-004 (§12.2 P-06) | auto (routine **form-field** class, M10-D2) | **APPROVED** (already mapped, M10) |
| `sensitive_full_name` | `person.full_name` | Controlled sensitive construct (M10-D3) to exercise the approval gate | approval | **APPROVED** (already mapped, M10) |
| `date_of_birth` | `person.date_of_birth` | G-12 **candidate** with real consumer (FR-FILL-001), but status **"PROPOSED — REQUIRES APPROVAL"**; not authored into the vocab; **date normalisation N3 TBD**; tier TBD | — | **BLOCKED** |
| `address` | `person.postal_address` | PD-A approved the **shape** (structured object); **components owed by L-INFO**; not authored; tier TBD; blocked by C-b | — | **BLOCKED** |
| `email` | *(none)* | **No candidate, no occurrence** anywhere in G-12/G-13/step3.pdf | — | **BLOCKED — no evidence** |
| `phone` | *(none)* | **No candidate, no occurrence** anywhere | — | **BLOCKED — no evidence** |
| `gender` | *(none)* | **Explicitly REJECTED** in G-12: "Gender, category, nationality, blood group — No MVP requirement consumes any of them" | — | **BLOCKED — rejected (no consumer)** |
| `aadhaar` / `pan` | `person.aadhaar_number` / `person.pan_number` | Candidates, but **blocked by C-c** (identifier-storage decision, D-05.3) | — | **BLOCKED** |
| education fields | `education.*` (5) | Candidates, but **C-a still owed** (no discriminating consumer beyond the owed L-INFO) | — | **BLOCKED** |

## 3. Why even the strongest candidate (date_of_birth) cannot be coded now

Approving `person.date_of_birth` for controlled-form autofill would require, all of which are unresolved and none of which may be invented (BR-009, M11 §25):

1. **G-13-A authoring** of the entry (it is a draft candidate, not authored content — D-05.9).
2. **A date normalisation rule (N3)** — explicitly TBD; authoring one is a conflict-detection decision under G-13.5 and is **evaluation-dependent** (D-02 §11.6). Not a "team constructs the form" act.
3. **A sensitivity tier** — G-14/G-15, blocked on A-5 / S-1 / S-4.
4. **Passing G-13-B**, the gate that specifically licenses automatic placement of a value into a form.

Fabricating any of these to raise the autofill field count is exactly what §25 forbids.

## 4. M11 decision records

- **M11-D1 — Controlled-form mapping set (unchanged):** `full_name → person.full_name` (auto) and `sensitive_full_name → person.full_name` (approval). No expansion is approved; the set is identical to M10 because `person.full_name` remains the only approved canonical attribute.
- **M11-D2 — Unmapped candidates and why:** `email`/`phone` — not candidates, no evidence (would be invention). `gender` — explicitly rejected in G-12 (no consumer). `date_of_birth` — proposed/unauthored; date normalisation + tier TBD; G-13-B blocks form autofill. `postal_address` — shape approved, components owed (C-b). identifiers — C-c blocked. education.* — C-a owed. All **LEFT UNMAPPED** (M11 §2/§25).
- **M11-D3 — Automation classifications:** `person.full_name` = SAFE AUTOMATE (routine form-field class) and, via the sensitive construct, REQUIRES APPROVAL. Declaration/consent = MUST REMAIN USER CONTROLLED. Every other candidate = **NOT YET MAPPED**. No automation inferred from confidence; BR-001 threshold not invented.
- **M11-D5 — Controlled-form identity gate:** the approved mapping applies only when the detected form's id is a controlled form (`mca-mock`); on any other form there is no mapping and no auto-fill, with no fall back to label guessing (§22, acceptance J). This adds no attribute and changes no approval — it narrows where the one approved mapping may fire.
- **M11-D4 — Canonical attributes added/approved:** **NONE.** Adding any requires G-13-A authoring + an approved normalisation rule (for date/numeric) + a G-14/G-15 tier + G-13-B, plus PM approval. The frozen `v0.1-draft.toml` (one entry) is untouched, and this record does not amend any historical decision.

## 5. What would unblock expansion (for a future milestone / PM)

1. Resolve **G-14/G-15** (sensitivity tiers) so **G-13-B** can be met — the single gate blocking automatic form-fill of any attribute. (Depends on A-5; studies S-1/S-4.)
2. Complete **G-13-A authoring** for the specific attribute (properties 1–6), including an approved **normalisation rule** for its data type (date/number rules are TBD).
3. For the education block, discharge **C-a** by recording the controlled form's L-INFO (team construction) — necessary but not sufficient (still needs 1 and 2).
4. For identifiers, resolve **C-c** (identifier storage). For address components, resolve **C-b** (L-INFO components).

Until then, the controlled-form mapping stays at the one approved attribute, and DOCURA fills only what it is licensed to fill — the honest outcome M11 §25 requires.
