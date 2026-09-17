// Field interpretation — provider architecture (M18, over M16/M17).
//
// One question, one seam: "What canonical attribute does this detected form field mean?"
// The answer is produced by a REPLACEABLE provider. `interpretField(field)` is the stable
// public API every consumer uses (mapping.js); it selects a provider, runs it defensively,
// and VALIDATES the provider's output against the released vocabulary before anyone
// downstream sees it. The rest of DOCURA — retrieval, safety policy, sensitivity, approval,
// audit, DOM execution, backend — does not know or care which provider produced a result.
//
// A provider is anything with `{ name, interpret(metadata) -> FieldInterpretationResult }`.
// Today the only enabled provider is the deterministic alias provider below. A future
// approved provider (a stronger deterministic rules engine or an approved LOCAL semantic
// model) drops in at selectProvider() with NO change to the pipeline. This milestone
// implements NO LLM, no external AI API, no model download, no embeddings, no network call.
//
// HARD BOUNDARIES a provider must honour (enforced by the wrapper where it can be):
//   * It receives value-free METADATA only (see toProviderMetadata) — never a field value,
//     defaultValue, password, HTML, or page text, and never a record value.
//   * It may NOT fetch the record, call the backend, approve disclosure, write the DOM,
//     submit, select documents, or create audit actions. It only names a meaning.
//   * Its output is validated: an unsupported attribute, malformed shape, out-of-range
//     confidence, a throw, or a timeout all degrade to a safe UNKNOWN — never a guess.

export const INTERPRETER_METHOD = "controlled-alias-v1";

// Deterministic exact-alias matches are certain about the MEANING by construction, so a
// resolved result carries full confidence. Confidence is about MEANING only — it does NOT
// authorise a fill and is NOT the BR-001 automatic-action threshold (TBD/G-04); the policy
// layer still decides eligibility.
export const EXACT_ALIAS_CONFIDENCE = 1;

// Data-driven aliases (M16 §6). Canonical id → safe in-scope synonyms for the CONTROLLED MVP.
// Extend the lists here (data, not if/else) — but never add a new canonical id without the
// required G-13/G-14/G-15 governance evidence.
export const CONTROLLED_ALIASES = {
  "person.full_name": ["full name", "name", "applicant name", "candidate name"],
  "person.date_of_birth": ["date of birth", "dob", "d o b", "birth date"],
};

// The released vocabulary the interpreter may EVER resolve to. Any provider output naming an
// identifier outside this set is rejected (validated to unknown), so a provider cannot widen
// the fill-eligible vocabulary by merely mentioning "person.email" etc.
export const RELEASED_ATTRIBUTES = new Set(Object.keys(CONTROLLED_ALIASES));

// Normalise a label before comparison (M16 §6): case-fold, separators (._-/) → space, drop
// other punctuation, collapse whitespace, trim. Meaning-preserving, NOT fuzzy — no camelCase
// splitting, stemming, or edit distance.
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

// The value-free metadata a provider is given. A strict whitelist: even if the caller's field
// object carried a value (it must not), the provider never sees it. Distinct label sources are
// preserved (M17 §4/§14) — not collapsed into one string.
export function toProviderMetadata(field) {
  if (!field || typeof field !== "object") return {};
  return {
    fieldRef: field.id ?? field.fieldId ?? field.name ?? null,
    id: field.id ?? null,
    name: field.name ?? null,
    fieldId: field.fieldId ?? null,
    type: field.type ?? null,
    required: !!field.required,
    label: field.label ?? null,
    ariaLabel: field.ariaLabel ?? null,
    ariaLabelledBy: field.ariaLabelledBy ?? null,
    placeholder: field.placeholder ?? null,
    title: field.title ?? null,
    constraints: field.constraints ?? null,
  };
}

// ---- the deterministic alias provider (the M16/M17 logic, now behind the contract) --------
export const deterministicProvider = {
  name: INTERPRETER_METHOD,
  interpret(metadata, { index = DEFAULT_INDEX } = {}) {
    const fieldRef = metadata?.id ?? metadata?.fieldId ?? metadata?.name ?? null;
    // Primary: the accessible label the user sees + the identifiers (peers; disagreement →
    // ambiguous). Secondary: placeholder/title, consulted only if nothing primary matched, so
    // they can never override an explicit accessible label (M17 §4). Exact match only.
    const primary = [
      metadata?.label,
      metadata?.ariaLabel,
      metadata?.ariaLabelledBy,
      metadata?.name,
      metadata?.id,
      metadata?.fieldId,
    ];
    const secondary = [metadata?.placeholder, metadata?.title];
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
  },
};

// The single point where the active provider is chosen. Only the deterministic provider is
// enabled today; a future approved (local, non-LLM in this milestone) provider is selected
// here — nothing else in DOCURA changes when it is.
export function selectProvider() {
  return deterministicProvider;
}

// ---- validation of any provider's output (the trust boundary) -----------------------------
const VALID_STATUSES = new Set(["resolved", "ambiguous", "unknown"]);

function isReleased(identifier) {
  return typeof identifier === "string" && RELEASED_ATTRIBUTES.has(identifier);
}

function inConfidenceRange(confidence) {
  return typeof confidence === "number" && Number.isFinite(confidence) && confidence >= 0 && confidence <= 1;
}

function unknownResult(fieldRef, reason, method) {
  return {
    status: "unknown",
    fieldRef,
    canonicalIdentifier: null,
    candidates: [],
    confidence: null,
    reason,
    method,
  };
}

// The stable public API. Runs a provider defensively and returns a validated, well-formed,
// value-free FieldInterpretationResult. Every failure mode degrades to a safe UNKNOWN.
export function interpretField(field, { provider } = {}) {
  const active = provider ?? selectProvider();
  const fieldRef = field?.id ?? field?.fieldId ?? field?.name ?? null;
  const method = active && typeof active.name === "string" ? active.name : "unknown-provider";

  let raw;
  try {
    raw = active.interpret(toProviderMetadata(field));
  } catch {
    return unknownResult(fieldRef, "Interpreter provider failed; field left unknown.", method);
  }

  if (!raw || typeof raw !== "object" || !VALID_STATUSES.has(raw.status)) {
    return unknownResult(fieldRef, "Interpreter provider returned malformed output; field left unknown.", method);
  }
  const reason = typeof raw.reason === "string" ? raw.reason.slice(0, 300) : "";

  if (raw.status === "resolved") {
    // Must name a RELEASED attribute with an in-range confidence, or it is not fill-eligible.
    if (!isReleased(raw.canonicalIdentifier) || !inConfidenceRange(raw.confidence)) {
      return unknownResult(
        fieldRef,
        "Interpreter returned an unsupported attribute or invalid confidence; field left unknown.",
        method,
      );
    }
    return {
      status: "resolved",
      fieldRef,
      canonicalIdentifier: raw.canonicalIdentifier,
      candidates: [raw.canonicalIdentifier],
      confidence: raw.confidence,
      reason: reason || "Resolved to an approved attribute.",
      method,
    };
  }

  if (raw.status === "ambiguous") {
    const released = [...new Set((Array.isArray(raw.candidates) ? raw.candidates : []).filter(isReleased))];
    // Genuine ambiguity needs >= 2 SUPPORTED candidates; otherwise DOCURA cannot confidently
    // resolve and must not choose — degrade to unknown (safe, untouched).
    if (released.length >= 2) {
      return {
        status: "ambiguous",
        fieldRef,
        canonicalIdentifier: null,
        candidates: released,
        confidence: null,
        reason: reason || "More than one approved meaning matched; DOCURA will not choose.",
        method,
      };
    }
    return unknownResult(fieldRef, "Ambiguous result had no two supported candidates; field left unknown.", method);
  }

  // unknown
  return unknownResult(fieldRef, reason || "No approved field meaning matched.", method);
}
