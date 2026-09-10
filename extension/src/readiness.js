// Deterministic readiness (M4). Given the M3 form snapshot and the user's current
// DOCURA record, it answers four questions without interpreting, guessing, matching,
// or filling anything (FR-INT-002/003):
//
//   1. What information/documents does the detected form require?  → every field, from M3
//   2. What does DOCURA currently have?                            → the passed-in record
//   3. What is missing?                                            → status "missing"
//   4. What requires the user?                                     → `requiresUser`
//
// It is a PURE function of its inputs — no DOM, no fetch, no Chrome APIs, no global
// state — so it unit-tests in Node and cannot reach another account's data: it sees
// only the record it is handed, which the backend already scoped to the session
// (GET /record/attributes, NFR-SEC-003). It never mutates that record.
//
// The one thing it deliberately does NOT do is decide what a form field *means*. Mapping
// a third-party form field to a canonical attribute is field interpretation (a later
// milestone, carrying confidence, ASM-008) and depends on an approved form-field→attribute
// mapping that does not exist yet: the vocabulary approves exactly one attribute
// (person.full_name) and the mock form's information fields (L-INFO) are owed by the team,
// not derivable from step3.pdf (G-12/G-13; MOCK_FORM_FIELD_INVENTORY §4). So the mapping is
// an *injected* resolver, and the production resolver below resolves nothing. No mapping is
// invented here; when one is approved it is supplied as config, and this logic is unchanged.

// Production field resolver: no approved form-field→canonical-attribute mapping exists yet
// (G-12 unapproved, L-INFO owed). Resolving anything would be an invented mapping, which
// BR-009 / G-13.11 forbid. So every field is unknown/unmapped until PM approves a mapping.
export function noApprovedFieldMapping(/* field */) {
  return null;
}

// Index the current record (the AttributeRecordResponse shape from /record/attributes) by
// canonical identifier. Read-only; the record object is never touched.
function indexRecord(record) {
  const byId = new Map();
  for (const attr of record?.attributes ?? []) {
    byId.set(attr.canonical_identifier, attr);
  }
  return byId;
}

// Classify one detected field. Deterministic: the only mapping is `resolve`, and a value is
// only ever read from the record for the field's own resolved attribute — never inferred
// from another field, never guessed, never invented.
function classifyField(field, byId, resolve) {
  const isDocument = field.type === "file"; // a file-upload asks for a document, not a datum
  const canonicalIdentifier = resolve(field) ?? null;

  let status;
  if (canonicalIdentifier === null) {
    status = "unknown"; // cannot be safely mapped to a supported concept
  } else {
    const attr = byId.get(canonicalIdentifier);
    if (attr === undefined) {
      status = "missing"; // supported concept, but DOCURA holds no value for this user
    } else if (attr.is_ambiguous || attr.value === null || attr.value === undefined) {
      // Documents disagree (G-20 has no approved precedence): surface it, never resolve it.
      status = attr.is_ambiguous ? "conflict" : "missing";
    } else {
      status = "available";
    }
  }

  // A field needs the user when DOCURA cannot deterministically satisfy it: a document
  // (M4 does no matching), an unresolved conflict, or a required field with no value.
  const requiresUser =
    isDocument || status === "conflict" || (field.required && status !== "available");

  return {
    fieldId: field.fieldId ?? null,
    type: field.type,
    required: !!field.required,
    isDocument,
    canonicalIdentifier,
    status,
    requiresUser,
  };
}

// Compute readiness over a whole M3 snapshot. `record` defaults to empty (nothing held) and
// `resolveField` to the production resolver (nothing mapped), so the honest default result
// is "every field unknown; required fields and documents require the user" — no invention.
export function computeReadiness({ snapshot, record, resolveField = noApprovedFieldMapping } = {}) {
  const byId = indexRecord(record);
  const summary = {
    total: 0,
    available: 0,
    missing: 0,
    unknown: 0,
    conflict: 0,
    requiresUser: 0,
    documentsRequired: 0,
  };

  const forms = (snapshot?.forms ?? []).map((form) => {
    const fields = form.fields.map((field) => classifyField(field, byId, resolveField));
    for (const f of fields) {
      summary.total += 1;
      summary[f.status] += 1;
      if (f.requiresUser) summary.requiresUser += 1;
      if (f.isDocument) summary.documentsRequired += 1;
    }
    return { formId: form.formId ?? null, standalone: !!form.standalone, fields };
  });

  // Ready = DOCURA needs nothing further from the user to satisfy what this form requires.
  summary.ready = summary.requiresUser === 0;
  return { forms, summary };
}
