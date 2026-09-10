// Deterministic retrieval + ambiguity/ask (M5). It sits AFTER M4 readiness and answers a
// narrower question for each field readiness mapped to a supported canonical attribute:
// *is there exactly one defensible value to present, or must DOCURA ask the user?*
//
// It is a PURE function of its inputs — no DOM, no fetch, no Chrome APIs, no global state —
// so it unit-tests in Node and cannot reach another account's data: it sees only the record
// it is handed, which the backend already scoped to the session (GET /record/attributes,
// NFR-SEC-003). It NEVER mutates that record and NEVER writes a value into a form field:
// M5 is retrieval + decision surfacing, not filling.
//
// The four cases (mapped directly onto the existing backend contract in
// app/schemas/record.py — AttributeValueResponse: value, is_ambiguous, observations[]):
//
//   A available   — one defensible value (backend chose it: value set, is_ambiguous false).
//                    Present it with its provenance for the next layer to confirm; do NOT fill.
//   B ambiguous   — more than one reasonable value from a SINGLE source (BR-003). Surface every
//                    candidate + provenance; requiresUser; select none.
//   C conflict    — the user's own DOCUMENTS disagree (BR-004): distinct values span >=2
//                    documents. Surface candidates + provenance; requiresUser; resolve nothing
//                    by recency, preference, or ordering.
//   D unavailable — no reliable value on record (BR-009). Invent nothing; requiresUser only when
//                    the field is required/user-actionable, matching M4's readiness rule.
//
// Splitting B from C uses only data the contract already carries — each observation's
// document_id — so no confidence, recency, or precedence signal is invented (G-20 unresolved).
// The backend has already decided whether observations agree (its approved N-TEXT
// normalisation); M5 does not re-litigate that, it only reads value/is_ambiguous/observations.

import { noApprovedFieldMapping } from "./readiness.js";

// One human-readable reason per status, for a future ask UI. No values are interpolated.
const REASON = {
  available: "One supported value is on record; present it for the user to confirm (not filled).",
  ambiguous: "More than one value is on record and each is reasonable; DOCURA will not choose — ask the user.",
  conflict: "Your documents disagree on this value; DOCURA will not resolve it — ask the user.",
  unavailable: "No reliable value is on record for this field; DOCURA leaves it untouched.",
  unknown: "This field has no approved mapping to a supported attribute.",
};

// Project one backend SupportingObservationResponse into a self-contained provenance entry.
// A fresh object (never the record's own) so the result is serialisable for the UI and the
// source record is provably never mutated. Only reference fields — no bytes (NFR-PRIV-007).
function provenanceOf(o) {
  return {
    value: o.value,
    confidence: o.confidence ?? null,
    documentId: o.document_id,
    extractionRunId: o.extraction_run_id,
    pageNumber: o.page_number,
    region: o.region ?? null,
  };
}

// Group observations into candidates by their verbatim value, first-seen order preserved.
// No sorting: the backend already ordered deterministically, and reordering by any metric
// would be exactly the recency/preference selection BR-003/BR-004 forbid.
function candidatesOf(observations) {
  const byValue = new Map();
  for (const o of observations) {
    if (!byValue.has(o.value)) byValue.set(o.value, { value: o.value, provenance: [] });
    byValue.get(o.value).provenance.push(provenanceOf(o));
  }
  return [...byValue.values()];
}

// The ask decision for ONE supported attribute — the small, pure, browser-free result model.
// `attribute` is the AttributeValueResponse for this canonical id, or undefined if the user
// holds none. `required` comes from the detected field (M4 readiness) and only affects the
// unavailable case's requiresUser, exactly as readiness decides.
export function askForAttribute({ canonicalIdentifier, attribute, required = false } = {}) {
  const base = { canonicalIdentifier, candidates: [] };

  // D — nothing on record for this attribute.
  if (attribute === undefined || attribute === null) {
    return { ...base, status: "unavailable", requiresUser: !!required, reason: REASON.unavailable };
  }

  const observations = attribute.observations ?? [];

  // C / B — the backend found genuine disagreement (value withheld). Never resolved here.
  if (attribute.is_ambiguous) {
    const candidates = candidatesOf(observations);
    const documents = new Set(observations.map((o) => o.document_id));
    const status = documents.size > 1 ? "conflict" : "ambiguous"; // documents disagree vs one source
    return { ...base, status, candidates, requiresUser: true, reason: REASON[status] };
  }

  // A — the backend selected exactly one value; present it, do not re-split its provenance.
  if (attribute.value !== null && attribute.value !== undefined) {
    return {
      ...base,
      status: "available",
      value: attribute.value,
      candidates: [{ value: attribute.value, provenance: observations.map(provenanceOf) }],
      requiresUser: false,
      reason: REASON.available,
    };
  }

  // D — attribute present but no value and no disagreement: still nothing reliable to present.
  return { ...base, status: "unavailable", requiresUser: !!required, reason: REASON.unavailable };
}

// Index the current record (AttributeRecordResponse) by canonical id. Read-only.
function indexRecord(record) {
  const byId = new Map();
  for (const attr of record?.attributes ?? []) byId.set(attr.canonical_identifier, attr);
  return byId;
}

// Run the ask decision across a whole M3 snapshot, mirroring computeReadiness. Unmapped fields
// stay "unknown" (BR-009 / G-13: no invented mapping); the production resolver maps nothing, so
// the honest default is every field unknown and no record is ever read.
export function computeRetrieval({ snapshot, record, resolveField = noApprovedFieldMapping } = {}) {
  const byId = indexRecord(record);
  const summary = { total: 0, available: 0, ambiguous: 0, conflict: 0, unavailable: 0, unknown: 0, requiresUser: 0 };

  const forms = (snapshot?.forms ?? []).map((form) => {
    const fields = form.fields.map((field) => {
      const canonicalIdentifier = resolveField(field) ?? null;
      const decision =
        canonicalIdentifier === null
          ? { canonicalIdentifier: null, status: "unknown", candidates: [], requiresUser: !!field.required, reason: REASON.unknown }
          : askForAttribute({ canonicalIdentifier, attribute: byId.get(canonicalIdentifier), required: field.required });

      summary.total += 1;
      summary[decision.status] += 1;
      if (decision.requiresUser) summary.requiresUser += 1;

      return { fieldId: field.fieldId ?? null, type: field.type, required: !!field.required, ...decision };
    });
    return { formId: form.formId ?? null, standalone: !!form.standalone, fields };
  });

  // ready = nothing further is needed from the user for any field this form requires.
  summary.ready = summary.requiresUser === 0;
  return { forms, summary };
}
