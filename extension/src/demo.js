// DEMO dynamic field interpretation + safety seams (dev/evaluation ONLY).
//
// *** This module powers the local end-to-end DYNAMIC AUTOFILL DEMO. It is NOT production. ***
//
// It reuses the existing pipeline unchanged: detection (detect.js, M17 semantic metadata),
// retrieval (retrieval.js), review/approval (sensitivity.js), and fill (autofill.js). It only
// supplies DEMO implementations of the injectable seams those functions already accept:
//   * demoResolveField(field)        — which demo attribute a field MEANS (label-driven, exact).
//   * demoFieldAutomation(field)     — the fill POLICY: routine → "auto", sensitive → "approval".
//   * isDemoForm(formId)             — eligibility gate (see DEMO_MODE below).
//   * demoClassifyTier(field)        — "routine" | "sensitive" for computeReview.
//   * demoClassifyDeclaration(field) — true for a declaration/consent control (never automated).
//
// DEMO_MODE is the explicit opt-in that turns these seams on: content.js wires the demo
// resolve/automation/eligibility/classification seams ONLY when DEMO_MODE is true, and uses the
// production controlled-form path otherwise. It is currently TRUE to run the local end-to-end
// dynamic demo; set it to false for a production/default build, which restores controlled-form-
// only behaviour (isControlledForm / `mca-mock`). Either way the safety invariants are identical
// — meaning is resolved from the field's accessible LABEL and M17 semantic metadata, NEVER from
// its HTML id/name; matching is exact-alias only (data-driven, normalised), never fuzzy (BR-009);
// sensitive fields stay approval-gated, declarations are never touched, and DOCURA never submits.
// No LLM, no network, no external AI.

import { normalizeLabel, toProviderMetadata } from "./interpret.js";

// Currently true to run the local dynamic demo. Set to false for production/default builds.
export const DEMO_MODE = true;

// Demo attributes + label synonyms (mirrors config/vocabulary/canonical_attributes.demo.toml).
// Data-driven: extend the lists, not the code. These are DEMO attributes, not G-13-released.
export const DEMO_ALIASES = {
  "person.full_name": ["full name", "name", "applicant name", "candidate name"],
  "person.date_of_birth": ["date of birth", "dob", "d o b", "birth date", "birthdate"],
  "person.age": ["age", "applicant age"],
  "person.email": ["email", "email address", "e mail"],
  "person.phone": ["phone", "phone number", "mobile", "mobile number", "contact number"],
  "person.address": ["address", "residential address", "permanent address", "current address"],
  "identity.pan_number": ["pan", "pan number", "pan card number", "permanent account number"],
  "identity.aadhaar_number": ["aadhaar", "aadhar", "aadhaar number", "aadhaar card number", "uidai number"],
};

// OWNER-APPROVED sensitivity tiers (D-A5 RESOLVED — see
// backend/docs/SENSITIVITY_GOVERNANCE_DECISION.md). This map is the extension runtime mirror of
// the single config record in backend/config/vocabulary/canonical_attributes.demo.toml
// (`sensitivity`), the same convention the alias lists already follow — kept in sync, one map
// here (no scattered tier rules). Tiers drive the SAME existing safety machinery:
//   routine       → may auto-fill (BR-001 threshold still TBD);
//   sensitive     → per-instance approval + masking (BR-005 / FR-SENS-002/004/005);
//   consequential → strongest existing protection: approval-gated at the immutable floor
//                   (BR-020 raise-only, never lowered). Declaration/consent CONTROLS remain
//                   never-accepted (BR-006) via demoClassifyDeclaration, independent of this map.
export const DEMO_TIERS = {
  "person.full_name": "routine",
  "person.date_of_birth": "sensitive",
  "person.age": "routine",
  "person.email": "sensitive",
  "person.phone": "sensitive",
  "person.address": "sensitive",
  "identity.pan_number": "consequential",
  "identity.aadhaar_number": "consequential",
};

// Approved D-A5 default: an attribute with no explicit tier is treated as SENSITIVE (never
// silently routine — that could disclose without approval), matching the conservative floor.
export const DEMO_DEFAULT_TIER = "sensitive";

// Tiers that require per-disclosure approval before any value is placed (BR-005). Consequential
// is the strongest tier and is likewise approval-gated (and pinned at the BR-020 floor).
const DEMO_APPROVAL_TIERS = new Set(["sensitive", "consequential"]);

export const DEMO_RELEASED = new Set(Object.keys(DEMO_ALIASES));

function buildIndex(aliases) {
  const index = new Map();
  for (const [canonical, list] of Object.entries(aliases)) {
    for (const alias of list) {
      const norm = normalizeLabel(alias);
      if (norm) index.set(norm, canonical);
    }
  }
  return index;
}

const DEMO_INDEX = buildIndex(DEMO_ALIASES);

function matchSources(sources) {
  const matched = new Set();
  for (const source of sources) {
    const norm = normalizeLabel(source);
    if (norm && DEMO_INDEX.has(norm)) matched.add(DEMO_INDEX.get(norm));
  }
  return matched;
}

// The demo interpreter: resolved | ambiguous | unknown, over the demo vocabulary. Same
// discipline as interpret.js — primary sources are the accessible label + identifiers, with
// placeholder/title as a secondary fallback; exact match only; >1 match → ambiguous.
export function interpretDemoField(field) {
  const m = toProviderMetadata(field);
  const primary = [m.label, m.ariaLabel, m.ariaLabelledBy, m.name, m.id, m.fieldId];
  const secondary = [m.placeholder, m.title];
  let matched = matchSources(primary);
  if (matched.size === 0) matched = matchSources(secondary);
  const fieldRef = m.fieldRef ?? null;
  if (matched.size === 0) return { status: "unknown", fieldRef, canonicalIdentifier: null, candidates: [] };
  if (matched.size > 1) return { status: "ambiguous", fieldRef, canonicalIdentifier: null, candidates: [...matched] };
  const [only] = matched;
  return { status: "resolved", fieldRef, canonicalIdentifier: only, candidates: [only] };
}

// The canonical id a field MEANS, or null (unknown/ambiguous → null → untouched). Never guesses.
export function demoResolveField(field) {
  const r = interpretDemoField(field);
  return r.status === "resolved" ? r.canonicalIdentifier : null;
}

// A declaration/consent control is user-owned and never automated (BR-006). Recognise the
// common demo shape: a checkbox, or a label mentioning agree/consent/declaration/terms.
export function demoClassifyDeclaration(field) {
  if (!field || typeof field !== "object") return false;
  if (String(field.type ?? "").toLowerCase() === "checkbox") return true;
  const label = normalizeLabel([field.label, field.ariaLabel, field.title].filter(Boolean).join(" "));
  return /\b(i agree|agree|consent|declaration|declare|terms|i confirm)\b/.test(label);
}

// The approved sensitivity tier of a field: routine/sensitive/consequential from its resolved
// attribute (default SENSITIVE for a resolved-but-untiered attribute, per D-A5), else "unknown"
// when the field resolves to no attribute (computeReview then leaves it untouched — never guessed).
export function demoClassifyTier(field) {
  const canonical = demoResolveField(field);
  if (canonical === null) return "unknown";
  return DEMO_TIERS[canonical] ?? DEMO_DEFAULT_TIER;
}

// The fill POLICY for autofill.js: routine → "auto"; sensitive/consequential → "approval"
// (disclose only after explicit per-instance approval); unresolved → null (untouched). A
// declaration is not a demo attribute, so it resolves to null and is untouched.
export function demoFieldAutomation(field) {
  const canonical = demoResolveField(field);
  if (canonical === null) return null;
  const tier = DEMO_TIERS[canonical] ?? DEMO_DEFAULT_TIER;
  return DEMO_APPROVAL_TIERS.has(tier) ? "approval" : "auto";
}

// Eligibility gate. DEMO_MODE is the explicit opt-in; when it is on, the demo seams apply to the
// forms the developer visits locally (production is unaffected because DEMO_MODE is false by
// default and content.js only wires these seams when it is true). Kept as a function so a build
// could restrict it to specific demo form ids without touching callers.
export function isDemoForm(/* formId */) {
  return true;
}
