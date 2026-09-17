// Controlled-form field policy + resolution bridge (M10 → M16).
//
// Kept SEPARATE from DOM detection (detect.js), retrieval (retrieval.js), sensitivity
// (sensitivity.js), DOM filling (autofill.js), and — since M16 — field *interpretation*
// (interpret.js). Two responsibilities live here, and only these:
//   * resolveField(field) — the canonical id a field MEANS. The frozen controlled-form
//     fields resolve via their authoritative mapping below; every other field defers to the
//     generic interpreter (interpret.js). Meaning only — it fills nothing.
//   * fieldAutomation(field) — the POLICY: may this field be auto-filled, must it be
//     approved, or neither. This is the controlled-form boundary and it, not interpretation,
//     decides eligibility (M16 §8).
// isControlledForm(formId) keeps autofill scoped to the team-constructed controlled form.
//
// FROZEN-DECISION BOUNDARY (read before adding an entry):
//   * The only approved canonical attribute is `person.full_name` (PD-B, G-13 v0.1-draft) with
//     its N-TEXT normalisation. No other attribute is approved for filling.
//   * `step3.pdf` enumerates NO form information fields; the §10/ASM-002 mock form is
//     *constructed by the team*, so the team authors the mapping for ITS OWN controlled form's
//     field identifiers (SPRINT_4_MOCK_FORM_FIELD_INVENTORY.md §4.1). That is the ONLY scope of
//     this table — it is NOT a general real-portal interpreter (that needs the owed L-INFO /
//     field-interpretation ruleset, still unresolved).
//   * The controlled-form fields match EXACTLY on their stable identifiers (frozen). Any other
//     field's meaning is resolved by interpret.js — deterministic, alias-based, and normalised,
//     never fuzzy/substring guessing (BR-009) — but its automation policy here is null, so a
//     merely-interpreted field is left untouched.
//   * Automation of a field is gated further in autofill.js by the backend's value agreement
//     (available vs ambiguous vs conflict) and by sensitivity — this table never fills by itself.
//
// See M10-D1 (approve the controlled-form mapping), M10-D2 (routine is a FORM-FIELD
// classification; the attribute-level G-14 tier stays unresolved), M10-D3 (the sensitive
// entry is a controlled construct to exercise the approval gate).

import { interpretField } from "./interpret.js";

export const MAPPING_VERSION = "m16-controlled-mock-form-v1";

// The approved mapping applies ONLY to the team-constructed controlled MVP form, identified
// by its form id (M11-D5, §3/§22). On any other form — an arbitrary external website — there
// is NO approved mapping, so NO auto-fill, and never a fall back to label guessing. This is the
// production-vs-controlled boundary: the mapping cannot accidentally fire on a real portal that
// happens to contain an input named "full_name".
export const CONTROLLED_FORM_IDS = new Set(["mca-mock"]);

export function isControlledForm(formId) {
  return CONTROLLED_FORM_IDS.has(formId);
}

// automation: "auto"     — routine form field; fill when the record value is unambiguously available.
//             "approval" — the form field is sensitive; fill ONLY after explicit, exact-scope approval.
//             "never"    — mapped but must never be automated (reserved; unused today).
// A declaration/consent control is simply absent from this table → resolves to null → untouched.
// G-15 default (adopted for the controlled MVP by M12-D3): an attribute with no assigned
// sensitivity tier is treated as SENSITIVE — so it discloses only through the per-instance
// approval gate, never a silent auto-fill. Both authored attributes carry a TBD tier
// (v0.2-draft), so the default would make BOTH "approval". `full_name` is the one documented
// EXCEPTION (M10-D2): its controlled-form field is classified routine → "auto". Every other
// mapped field follows the default → "approval".
// The frozen controlled-form field policy (M10-D1/D2/D3, M12-D3), keyed by the controlled
// form's exact field identifiers. This is authoritative for those fields and stays exact —
// it encodes the per-field automation the team set for its OWN form:
//   automation "auto"     — routine form field; fill when the record value is unambiguously available.
//              "approval" — sensitive form field; fill ONLY after explicit, exact-scope approval.
//              "never"    — mapped but must never be automated (reserved; unused today).
// G-15 default (M12-D3): an un-tiered attribute is treated as SENSITIVE (approval); `full_name`
// is the one documented routine EXCEPTION (M10-D2). A field absent here has automation null →
// untouched, so a merely-interpreted field is never auto-filled without an explicit policy (§8).
const CONTROLLED_FORM_FIELDS = {
  full_name: { canonicalIdentifier: "person.full_name", automation: "auto" },
  sensitive_full_name: { canonicalIdentifier: "person.full_name", automation: "approval" },
  date_of_birth: { canonicalIdentifier: "person.date_of_birth", automation: "approval" },
};

// The controlled field's exact-identifier entry, or undefined. Exact match, no normalisation —
// the controlled-form mapping is frozen and authoritative for these ids.
function controlledEntry(field) {
  const key = field?.id ?? field?.fieldId ?? field?.name ?? null;
  if (key === null) return undefined;
  return Object.prototype.hasOwnProperty.call(CONTROLLED_FORM_FIELDS, key)
    ? CONTROLLED_FORM_FIELDS[key]
    : undefined;
}

// The canonical identifier a field MEANS, or null. The frozen controlled-form fields resolve
// via their authoritative mapping; every other field defers to the generic interpreter
// (interpret.js), which returns a canonical id only on a confident, unambiguous, approved
// match — never a guess (M16 §5/§9). Meaning only: this authorises no fill (see fieldAutomation).
export function resolveField(field) {
  const controlled = controlledEntry(field);
  if (controlled) return controlled.canonicalIdentifier;
  const interpreted = interpretField(field);
  return interpreted.status === "resolved" ? interpreted.canonicalIdentifier : null;
}

// The automation POLICY for a field: "auto" | "approval" | "never", or null. Only the
// controlled-form fields carry a policy; any other field (even one the interpreter resolved)
// returns null → untouched, so interpretation never authorises autofill on its own (M16 §8).
export function fieldAutomation(field) {
  return controlledEntry(field)?.automation ?? null;
}
