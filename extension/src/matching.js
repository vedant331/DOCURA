// Deterministic document matching + constraint preparation (M7). The last preparation
// layer before a (future) attachment executor: for each FILE-UPLOAD field detected by M3
// it answers, without interpreting meaning, guessing, ranking, or attaching anything
// (FR-MATCH-001…010):
//
//   1. Which stored documents could satisfy this upload requirement?   → injected matcher
//   2. Can a defensible single candidate satisfy the field's declared
//      format/size constraints, or be safely converted into a copy that does?
//   3. If a copy is needed, prepare a DERIVED copy — never the original.  → injected preparer
//   4. Is the candidate sensitive?  → M6 exact-scope, per-instance approval (BR-005/BR-007)
//   5. Expose the exact file that WOULD be attached, as a preview target — and stop.
//
// It is a PURE function of its inputs — no DOM, no fetch, no Chrome APIs, no global state —
// so it unit-tests in Node and cannot reach another account's data: it sees only the vault
// listing it is handed, which the backend already scoped to the session (NFR-SEC-003). It
// NEVER mutates a stored document, NEVER attaches/uploads a file, NEVER operates the form,
// and NEVER submits (BR-008, BR-013, FR-MATCH-007). M7 is the matching/preparation seam,
// not the attachment executor.
//
// THREE FROZEN GAPS force the honest production default to "nothing is resolvable":
//   * G-12/G-13 — no approved form-field→document mapping and no document taxonomy exist
//     (DocumentType has only `unclassified`). So the matcher is an INJECTED seam and the
//     production seam resolves NOTHING: every upload field is `unresolved`. Inventing a
//     mapping is exactly what BR-009 / G-13.11 forbid.
//   * G-14/A-5 — no sensitivity tier is assigned to any attribute or document. So document
//     sensitivity is an INJECTED seam; production returns `unknown`, and an unknown tier is
//     REFUSED disclosure (never guessed routine — that could disclose without approval,
//     BR-005; never invented sensitive — that fabricates an assignment). Mirrors M6.
//   * BR-001 — the automatic-action threshold is TBD. So the threshold is INJECTED; with no
//     approved threshold the threshold-dependent "propose" action is left UNRESOLVED. A
//     confidence is never invented either — it is only ever what the matcher supplied.
//
// FR-MATCH-011 (assembling/merging derived documents) is FUTURE/WON'T and is deliberately
// absent: no code path here ever combines two documents into one.

import { checkApproval } from "./sensitivity.js";

// ---- injected seams (production resolves / prepares nothing) -----------------

// Which stored documents could satisfy this upload field? Returns:
//   * null  → no approved matcher/mapping exists (G-12/G-13): the requirement is UNRESOLVED.
//   * []    → a matcher ran and found no suitable stored document: MISSING (FR-MATCH-005).
//   * [ { documentId, confidence? }, … ] → the plausible candidates, in the matcher's own
//            order. Confidence is passed through verbatim (FR-MATCH-002) and is never
//            invented, re-ranked, or used to drop a candidate here (BR-003).
// The production seam maps nothing — the only honest default until PM approves a mapping.
export function noApprovedDocumentMatcher(/* field, documents */) {
  return null;
}

// Sensitivity tier of a candidate document. No approved assignment exists (G-14/A-5), so
// production classifies nothing: `unknown`. A known routine/sensitive/consequential tier
// comes from approved config or a future classifier.
export function noApprovedDocumentSensitivity(/* document */) {
  return "unknown";
}

// The automatic-action threshold (BR-001). TBD by design, so production supplies none.
export function noApprovedMatchThreshold() {
  return null;
}

// Turn a defensible candidate that does NOT already satisfy the field's constraints into a
// constraint-compliant DERIVED COPY (FR-MATCH-006). No safe transform capability exists in
// the project yet, so production returns `unavailable` — it NEVER fabricates a converted
// file. A real preparer returns one of:
//   { status: "prepared", derived: { … provenance … } } — a copy meeting the constraints.
//   { status: "quality_floor" } — cannot meet them without unacceptable loss (FR-MATCH-010).
//   { status: "unavailable" }   — no transform capability for this conversion.
export function preparationUnavailable(/* field, document, unmet */) {
  return { status: "unavailable" };
}

const SENSITIVE_TIERS = new Set(["sensitive", "consequential"]); // require per-disclosure approval
const KNOWN_TIERS = new Set(["routine", "sensitive", "consequential", "unknown"]);

const REASON = {
  unresolved: "No approved matcher maps this upload field to a document; DOCURA leaves it for the user (G-12/G-13).",
  missing: "No stored document satisfies this upload field; DOCURA reports it missing and substitutes nothing (FR-MATCH-005).",
  ambiguous: "More than one stored document could satisfy this field; DOCURA will not choose — ask the user (BR-003).",
  constraintUnavailable: "The candidate does not meet the field's declared constraints and no safe conversion is available; DOCURA attaches nothing (FR-MATCH-006).",
  constraintQualityFloor: "Meeting the field's constraints would require unacceptable quality loss; DOCURA stops rather than attach a degraded file (FR-MATCH-010).",
  tierUnknown: "The candidate's sensitivity tier is unassigned (G-14/A-5); DOCURA will not disclose it until it is classified.",
  approvalRequired: "The candidate is sensitive; attachment needs the user's explicit approval for this exact disclosure (BR-005).",
  ready: "One candidate is prepared and previewable; DOCURA never attaches — the user confirms attachment (BR-008/BR-015).",
  thresholdUnknown: "One candidate is prepared, but the automatic-action threshold is unset (BR-001) or the candidate carries no confidence; DOCURA proposes nothing automatically.",
  proposable: "Exactly one non-sensitive candidate is at/above the approved threshold; DOCURA proposes it for attachment (not attached) (FR-MATCH-003).",
};

// ---- deterministic constraint check ----------------------------------------
// Reads ONLY what M3 already declared on the field (detect.js: `accept`, `maxSize`). HTML
// exposes no standard image-dimension constraint and the vault listing carries none, so
// dimensions are neither declared nor checkable here and are deliberately not invented.

function matchesAccept(accept, document) {
  if (!accept) return true; // no declared format constraint
  const tokens = accept.split(",").map((t) => t.trim().toLowerCase()).filter(Boolean);
  if (tokens.length === 0) return true;
  const type = (document.content_type ?? document.contentType ?? "").toLowerCase();
  const name = (document.original_filename ?? document.originalFilename ?? "").toLowerCase();
  return tokens.some((tok) => {
    if (tok.endsWith("/*")) return type.startsWith(tok.slice(0, -1)); // e.g. image/*
    if (tok.startsWith(".")) return name.endsWith(tok); // extension token
    return type === tok; // exact media type
  });
}

function withinSize(maxSize, document) {
  if (maxSize === null || maxSize === undefined) return true; // no declared size limit
  const limit = typeof maxSize === "number" ? maxSize : Number.parseInt(maxSize, 10);
  if (Number.isNaN(limit)) return true; // undeclared/uninterpretable → not a constraint we can test
  const size = document.byte_size ?? document.byteSize;
  if (size === null || size === undefined) return true; // nothing to compare
  return size <= limit;
}

// Deterministic: does this document, as stored, already satisfy the field's declared
// constraints? Pure read of metadata — never touches the document.
export function evaluateConstraints(field, document) {
  const c = field?.constraints ?? {};
  const format = matchesAccept(c.accept, document);
  const size = withinSize(c.maxSize, document);
  const unmet = [];
  if (!format) unmet.push("format");
  if (!size) unmet.push("size");
  return { format, size, satisfied: unmet.length === 0, unmet };
}

// Self-contained, distinguishing metadata for one candidate (FR-MATCH-004: identified
// clearly enough to tell candidates apart). A fresh object — never the vault row — so the
// result is serialisable and the source document is provably never mutated. References only.
function describeCandidate(document, confidence, field) {
  return {
    documentId: document.id ?? document.documentId ?? null,
    confidence: confidence ?? null, // verbatim from the matcher; never invented
    filename: document.original_filename ?? document.originalFilename ?? null,
    contentType: document.content_type ?? document.contentType ?? null,
    byteSize: document.byte_size ?? document.byteSize ?? null,
    documentType: document.document_type ?? document.documentType ?? null,
    // Deterministic hint to help the user tell candidates apart; NEVER used to select one.
    satisfiesConstraints: evaluateConstraints(field, document).satisfied,
  };
}

// The exact-file identity a document disclosure is bound to (BR-007). Prefer the stored
// checksum; fall back to the id so an approval is still bound to a specific file. When a
// derived copy is prepared, its own identity is used, so approving the original never
// authorises attaching a different (derived) file.
function fileIdentity(document, derived) {
  if (derived) return derived.checksum_sha256 ?? derived.checksum ?? `derived:${document.id ?? ""}`;
  return document.checksum_sha256 ?? document.checksumSha256 ?? document.id ?? null;
}

// ---- per-field matching -----------------------------------------------------

// The base result for one upload field. `attach.performed` is a hard invariant: M7 never
// attaches, whatever the status (BR-008 shape for file uploads; the executor is M8).
function baseResult(field) {
  return {
    fieldId: field.fieldId ?? null,
    type: field.type,
    required: !!field.required,
    candidates: [],
    action: "none", // never "attach"/"upload"/"submit"
    preview: null, // set only when a single exact file is prepared/identified
    attach: { performed: false, reason: "M7 never attaches a document to a form (BR-008); attachment is a later, user-confirmed step." },
  };
}

// Decide the whole matching result for ONE file-upload field.
export function matchUploadField({
  field,
  documents = [],
  matchDocuments = noApprovedDocumentMatcher,
  classifySensitivity = noApprovedDocumentSensitivity,
  prepare = preparationUnavailable,
  threshold = noApprovedMatchThreshold,
  approvals = null,
  context = {},
} = {}) {
  const base = baseResult(field);
  const byId = new Map(documents.map((d) => [d.id ?? d.documentId, d]));

  // 1 — Which documents could satisfy this? null = no approved matcher (unresolved).
  const matched = matchDocuments(field, documents);
  if (matched === null || matched === undefined) {
    return { ...base, status: "unresolved", requiresUser: true, reason: REASON.unresolved };
  }

  // Project matcher hits onto real vault rows, preserving the matcher's order. A hit whose
  // documentId is not in the (session-scoped) vault is dropped — never fabricated (test 7).
  const hits = matched
    .map((m) => ({ document: byId.get(m.documentId), confidence: m.confidence }))
    .filter((h) => h.document !== undefined);

  // 2 — No candidate: MISSING. Never substitute a different document (FR-MATCH-005).
  if (hits.length === 0) {
    return { ...base, status: "missing", requiresUser: true, reason: REASON.missing };
  }

  const candidates = hits.map((h) => describeCandidate(h.document, h.confidence, field));

  // 3 — More than one plausible candidate: AMBIGUOUS. Surface all; choose none by ordering,
  //     recency, filename, or "most likely" (BR-003). No preview target — the user chooses.
  if (hits.length > 1) {
    return { ...base, status: "ambiguous", candidates, requiresUser: true, reason: REASON.ambiguous };
  }

  // 4 — Exactly one defensible candidate.
  const { document, confidence } = hits[0];
  const candidate = candidates[0];
  const constraints = evaluateConstraints(field, document);

  // 4a — Determine the EXACT file that would be attached: the original if it already meets
  //      the constraints, else a prepared derived copy. The original is only ever read.
  let derived = null;
  if (!constraints.satisfied) {
    const prep = prepare(field, document, constraints.unmet);
    if (prep.status === "prepared") {
      derived = prep.derived;
    } else {
      // CASE D — cannot satisfy constraints. Stop; degrade nothing; attach nothing.
      const reason = prep.status === "quality_floor" ? REASON.constraintQualityFloor : REASON.constraintUnavailable;
      return { ...base, status: "constraint_failure", candidates, constraints, requiresUser: true, reason };
    }
  }

  // The exact file that would be attached — the preview target (FR-MATCH-008). Set now,
  // BEFORE any approval/threshold gate, so the user previews exactly what stops at the gate
  // (EC-011: prepare and preview, then stop).
  const preview = derived
    ? { source: "derived", documentId: candidate.documentId, derivedFrom: candidate.documentId, derived, contentType: derived.content_type ?? derived.contentType ?? null, byteSize: derived.byte_size ?? derived.byteSize ?? null }
    : { source: "original", documentId: candidate.documentId, contentType: candidate.contentType, byteSize: candidate.byteSize };

  const withPrep = { ...base, status: "candidate", candidates, candidate, constraints, preview, preparation: derived ? { needed: true, status: "prepared" } : { needed: false, status: "not_needed" } };

  // 4b — Sensitivity + per-instance approval (CASE E, FR-MATCH-009, BR-005/BR-007).
  const rawTier = classifySensitivity(document);
  const sensitivity = KNOWN_TIERS.has(rawTier) ? rawTier : "unknown";

  if (sensitivity === "unknown") {
    // Unknown tier: refuse disclosure (don't guess routine, don't invent sensitive).
    return { ...withPrep, sensitivity, approvalState: "blocked", action: "none", requiresUser: true, reason: REASON.tierUnknown };
  }

  if (SENSITIVE_TIERS.has(sensitivity)) {
    // Bind approval to this exact file (original or derived). No ledger, or no approval yet,
    // ⇒ approval required; the value stays gated (no automatic sensitive disclosure, test 14).
    const scope = { ...context, formId: context.formId ?? null, fieldId: field.fieldId ?? null, canonicalIdentifier: `document:${candidate.documentId}`, value: fileIdentity(document, derived) };
    const granted = approvals && checkApproval(approvals, scope) === "granted";
    if (!granted) {
      return { ...withPrep, sensitivity, approvalState: "required", action: "none", requiresUser: true, reason: REASON.approvalRequired };
    }
    return decideThreshold({ ...withPrep, sensitivity, approvalState: "granted" }, confidence, threshold);
  }

  // Routine: no sensitive-approval needed.
  return decideThreshold({ ...withPrep, sensitivity, approvalState: "not_required" }, confidence, threshold);
}

// The threshold-dependent decision, isolated so BR-001's TBD stays in one place. A candidate
// is only ever PROPOSED (never attached) when an approved threshold exists and the candidate's
// (matcher-supplied) confidence meets it. With no threshold or no confidence, the action is
// left UNRESOLVED — never proposed on an invented number (FR-MATCH-003, BR-001).
function decideThreshold(result, confidence, threshold) {
  const t = threshold();
  if (t === null || t === undefined || confidence === null || confidence === undefined) {
    return { ...result, action: "prepare", requiresUser: true, reason: REASON.thresholdUnknown };
  }
  if (confidence >= t) {
    return { ...result, action: "propose", requiresUser: false, reason: REASON.proposable };
  }
  // Below the approved threshold: prepared and previewable, but not proposed automatically.
  return { ...result, action: "prepare", requiresUser: true, reason: REASON.ready };
}

// Compute matching over a whole M3 snapshot. Only FILE-UPLOAD fields carry a document
// requirement (FR-MATCH-001); every other field is governed by M4/M5/M6 and is not repeated
// here. With all seams at their production no-ops, no document is fetched and every upload
// field is `unresolved` — no invention, and no personal data crosses into this world.
export function computeMatching({
  snapshot,
  documents = [],
  matchDocuments = noApprovedDocumentMatcher,
  classifySensitivity = noApprovedDocumentSensitivity,
  prepare = preparationUnavailable,
  threshold = noApprovedMatchThreshold,
  approvals = null,
  context = {},
} = {}) {
  const summary = { total: 0, unresolved: 0, missing: 0, ambiguous: 0, constraint_failure: 0, candidate: 0, proposable: 0, approvalRequired: 0, blocked: 0, requiresUser: 0 };

  const forms = (snapshot?.forms ?? []).map((form) => {
    const uploads = form.fields.filter((f) => f.type === "file");
    const fields = uploads.map((field) => {
      const result = matchUploadField({ field, documents, matchDocuments, classifySensitivity, prepare, threshold, approvals, context: { ...context, formId: form.formId ?? null } });
      summary.total += 1;
      summary[result.status] += 1;
      if (result.action === "propose") summary.proposable += 1;
      if (result.approvalState === "required") summary.approvalRequired += 1;
      if (result.approvalState === "blocked") summary.blocked += 1;
      if (result.requiresUser) summary.requiresUser += 1;
      return result;
    });
    return { formId: form.formId ?? null, standalone: !!form.standalone, fields };
  });

  return { forms, summary };
}
