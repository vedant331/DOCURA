// Generic field interpretation (M16) — the replaceable seam that answers ONE question:
//
//     "What canonical attribute does this detected form field mean?"
//
// It does NOT answer "do we hold that value?" (retrieval.js) or "may we fill it?"
// (mapping.js policy + isControlledForm) or "write it to the DOM" (autofill.js). Those
// stay separate (M16 §3/§4/§8). This module is a pure function of a detected field's
// value-free metadata (label / name / id) — no DOM, no fetch, no Chrome APIs, no page
// values — so it unit-tests in Node and can be replaced later by a stronger deterministic
// rules engine or an approved local semantic model WITHOUT touching retrieval, sensitivity,
// approval, audit, or DOM execution (M16 §13).
//
// FROZEN-DECISION BOUNDARY: it maps ONLY to the two RELEASED controlled attributes,
// `person.full_name` and `person.date_of_birth`. It adds NO new canonical attribute
// (email/phone/address/aadhaar/pan/education/gender/etc. are unreleased — G-13-B, G-14/G-15),
// and it authorises nothing: identifying a meaning never fills, discloses, submits, or
// generalises autofill to arbitrary sites. UNKNOWN and AMBIGUOUS are first-class results —
// when the meaning is uncertain, DOCURA says so rather than guessing (M16 §7, BR-009).

export const INTERPRETER_METHOD = "controlled-alias-v1";

// Deterministic exact-alias matches are certain about the MEANING by construction, so a
// resolved result carries full confidence. NOTE: this is confidence in the *meaning* only —
// it does NOT authorise autofill and is NOT the BR-001 automatic-action threshold (that gate
// is TBD/G-04 and lives in the policy layer, which still decides eligibility).
export const EXACT_ALIAS_CONFIDENCE = 1;

// Data-driven aliases (M16 §6). Canonical id → the safe, in-scope synonyms for the CONTROLLED
// MVP. Extend the lists here (data, not if/else) — but never add a new canonical id without
// the required G-13/G-14/G-15 governance evidence.
export const CONTROLLED_ALIASES = {
  "person.full_name": ["full name", "name", "applicant name", "candidate name"],
  "person.date_of_birth": ["date of birth", "dob", "d o b", "birth date"],
};

// Normalise a label before comparison (M16 §6): case-fold, turn harmless separators
// (._-/) into spaces, drop other punctuation, collapse whitespace, trim. Deterministic and
// meaning-preserving — it does NOT do camelCase splitting, stemming, or any fuzzy/edit-distance
// transform, so it can never silently turn one attribute's label into another's.
export function normalizeLabel(raw) {
  if (raw === null || raw === undefined) return "";
  return String(raw)
    .toLowerCase()
    .replace(/[._\-/]+/g, " ")
    .replace(/[^\p{L}\p{N} ]+/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

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

const DEFAULT_INDEX = buildIndex(CONTROLLED_ALIASES);

// A FieldInterpretationResult:
//   { status: "resolved" | "ambiguous" | "unknown",
//     fieldRef, canonicalIdentifier|null, candidates: string[], confidence|null,
//     reason, method }
// resolved   → exactly one approved meaning matched; canonicalIdentifier + confidence set.
// ambiguous  → more than one distinct approved meaning matched (e.g. label and id disagree);
//              candidates lists them; NOTHING is auto-chosen (M16 §7).
// unknown    → no approved meaning matched; the field is left for policy to leave untouched.
function matchSources(sources, index) {
  const matched = new Set();
  for (const source of sources) {
    const norm = normalizeLabel(source);
    if (!norm) continue;
    const hit = index.get(norm);
    if (hit) matched.add(hit);
  }
  return matched;
}

export function interpretField(field, { index = DEFAULT_INDEX } = {}) {
  const fieldRef = field?.id ?? field?.fieldId ?? field?.name ?? null;

  // Value-free label sources only (M17): the accessible label the user actually sees
  // (label / aria-label / aria-labelledby) and the field's name/id are PRIMARY; placeholder
  // and title are weak hints consulted ONLY when nothing primary matches, so a placeholder/
  // title can never override an explicit accessible label (M17 §4). NEVER the field's value or
  // page content. EXACT match after normalisation — never substring, prefix, or fuzzy — so
  // "user full name" or "fullname" do not accidentally resolve to `person.full_name`.
  const primary = [field?.label, field?.ariaLabel, field?.ariaLabelledBy, field?.name, field?.id, field?.fieldId];
  const secondary = [field?.placeholder, field?.title];
  let matched = matchSources(primary, index);
  if (matched.size === 0) matched = matchSources(secondary, index);

  if (matched.size === 0) {
    return {
      status: "unknown",
      fieldRef,
      canonicalIdentifier: null,
      candidates: [],
      confidence: null,
      reason: "No approved field meaning matched this field's label.",
      method: INTERPRETER_METHOD,
    };
  }
  if (matched.size > 1) {
    return {
      status: "ambiguous",
      fieldRef,
      canonicalIdentifier: null,
      candidates: [...matched],
      confidence: null,
      reason: "The field matched more than one approved attribute; DOCURA will not choose.",
      method: INTERPRETER_METHOD,
    };
  }
  const [only] = matched;
  return {
    status: "resolved",
    fieldRef,
    canonicalIdentifier: only,
    candidates: [only],
    confidence: EXACT_ALIAS_CONFIDENCE,
    reason: "Exact match to an approved field alias.",
    method: INTERPRETER_METHOD,
  };
}
