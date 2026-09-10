// Sensitive-approval + deterministic review (M6). The safety boundary that sits AFTER M5
// retrieval: before any supported value could ever be disclosed to a form, this layer decides
// whether disclosure is even permitted, and if it needs the user's explicit, per-disclosure
// approval. It is PURE (no DOM, no fetch, no Chrome APIs) — it prepares a review, it never
// fills a field, never operates a submit control, and never touches a declaration/consent
// control. M6 is preparation + decision surfacing, not autofill (BR-008, FR-SUB-001/002).
//
// Grounding (SPRINT_4_DECISION_REGISTER §D-06.5 / G-14):
//   * The three-tier framework is frozen — routine · sensitive · consequential — and the
//     ATTRIBUTE and the DETECTED FIELD are two distinct classified units (FR-SENS-001).
//   * The tier ASSIGNMENT content is blocked on assumption A-5 (G-14, studies S-1/S-4):
//     "This boundary must be set by users, not by us." Every approved attribute's tier reads
//     TBD by design (vocabulary property 7). So tier assignment is an INJECTED seam and the
//     production seam below resolves nothing — every field's tier is `unknown`.
//   * The register cites, WITH ITS COST, and does NOT adopt "default unmapped → sensitive".
//     So `unknown` is not silently treated as routine (that could disclose without approval,
//     violating BR-005) nor labelled sensitive (that invents an assignment). Unknown tier ⇒
//     DOCURA refuses to disclose and says so — the conservative, non-guessing floor
//     (FR-INF-007: a TBD-tier attribute may not be acted upon).

import { computeRetrieval } from "./retrieval.js";

// ---- injected classification seams (production resolves nothing) ------------

// Sensitivity tier of a detected field / its attribute. No approved assignment exists
// (G-14 blocked on A-5), so production classifies nothing: every field is `unknown`.
export function noApprovedSensitivityTier(/* field */) {
  return "unknown";
}

// Whether a detected field is a legal declaration / agreement / consent control (BR-006).
// No approved declaration classification exists yet, so production cannot assert one:
// `unknown`. A known declaration (approved config, or a future explicit classifier) returns
// true and is then permanently blocked from any DOCURA automation.
export function noApprovedDeclarationClassification(/* field */) {
  return "unknown";
}

const TIERS = new Set(["routine", "sensitive", "consequential", "unknown"]);
const SENSITIVE_TIERS = new Set(["sensitive", "consequential"]); // require per-disclosure approval

// ---- approval model: exact-scope, one-time, never inherited (BR-005/BR-007) --
// An approval authorises exactly one disclosure: this user, this session, this form, this
// field, this attribute, this value. It is bound to all six; changing any one is a different
// disclosure and is NOT authorised. It is one-time (consumed on use) and lives only in the
// session's in-memory ledger — never persisted, remembered, or generalised (BR-007).

// The exact scope key. canonical_identifier is in the key, so an approval for one attribute
// cannot authorise another. userId/sessionId/formId/fieldId isolate user, session, form, field.
function scopeKey({ userId, sessionId, formId, fieldId, canonicalIdentifier }) {
  return JSON.stringify([userId ?? null, sessionId ?? null, formId ?? null, fieldId ?? null, canonicalIdentifier ?? null]);
}

// A fresh, empty session ledger. Held in the isolated world and cleared on teardown.
export function newApprovalLedger() {
  return new Map();
}

// Record the user's explicit approval of one disclosure. The bound value guards against
// generalisation to a different value for the same field/attribute (BR-007).
export function grantApproval(ledger, scope) {
  const record = { ...scope, state: "granted", consumed: false };
  ledger.set(scopeKey(scope), record);
  return record;
}

// "granted" only on an exact-scope, unconsumed match whose bound value equals the value now
// being disclosed; otherwise "required". Never a partial or generalised match.
export function checkApproval(ledger, scope) {
  const record = ledger.get(scopeKey(scope));
  if (!record || record.consumed) return "required";
  if (record.value !== scope.value) return "required"; // a different value = a different disclosure
  return "granted";
}

// One-time: consume the approval at the moment of disclosure so it cannot authorise a second.
export function consumeApproval(ledger, scope) {
  const record = ledger.get(scopeKey(scope));
  if (record) record.consumed = true;
  return record ?? null;
}

// ---- review model ----------------------------------------------------------

const BLOCK = {
  declaration: "Declaration/consent control is user-owned; DOCURA never operates it (BR-006).",
  approvalRequired: "Sensitive value requires the user's explicit approval for this exact disclosure (BR-005).",
  tierUnknown: "Sensitivity tier is unassigned (G-14/A-5); DOCURA will not disclose until it is classified.",
};

// Drop the raw value from each provenance entry while keeping its source references, so an
// unapproved sensitive value is never carried into the review (FR-SENS-004 masking) yet the
// document/page/run chain stays available for explanation (BR-010 explainability).
function projectProvenance(candidates, reveal) {
  return (candidates ?? []).map((c) => ({
    value: reveal ? c.value : undefined,
    provenance: (c.provenance ?? []).map((p) => ({ ...p, value: reveal ? p.value : undefined })),
  }));
}

// Build the review decision for one detected field from its M5 retrieval decision.
function reviewField(decision, { classifyTier, classifyDeclaration, approvals, context, formId, field }) {
  const base = {
    fieldId: decision.fieldId,
    type: decision.type,
    required: decision.required,
    canonicalIdentifier: decision.canonicalIdentifier,
    status: decision.status, // M5: available | ambiguous | conflict | unavailable | unknown
    canSubmit: false, // BR-008: DOCURA never submits — invariant on every field.
    action: "none", // never "fill"/"submit"/"click"; only some fields become "prepare".
  };

  // A declaration/consent control is user-owned and permanently blocked from automation,
  // whatever its retrieval status (BR-006). Checked first and independently.
  if (classifyDeclaration(field) === true) {
    return { ...base, isDeclaration: true, sensitivity: "n/a", approvalState: "blocked", requiresUser: true, blockedReason: BLOCK.declaration, candidates: [] };
  }

  // Only an `available` single value is ever a disclosure candidate. Ambiguous/conflict/
  // unavailable/unknown have nothing to disclose — they stay M5 ask states, untouched here.
  if (decision.status !== "available") {
    return {
      ...base,
      isDeclaration: classifyDeclaration(field),
      sensitivity: "n/a",
      approvalState: "not_applicable",
      requiresUser: decision.requiresUser,
      blockedReason: null,
      candidates: projectProvenance(decision.candidates, true), // M5 already governs this surface
    };
  }

  const tier = classifyTier(field);
  const sensitivity = TIERS.has(tier) ? tier : "unknown";

  // Unknown tier: refuse to disclose (do not guess routine, do not invent sensitive).
  if (sensitivity === "unknown") {
    return { ...base, isDeclaration: base.isDeclaration ?? classifyDeclaration(field), sensitivity, approvalState: "blocked", requiresUser: true, blockedReason: BLOCK.tierUnknown, candidates: projectProvenance(decision.candidates, false) };
  }

  // Routine: no sensitive-approval needed. A proposal may be prepared for the user to place
  // themselves — M6 still does not fill it (that is a later milestone).
  if (!SENSITIVE_TIERS.has(sensitivity)) {
    return { ...base, isDeclaration: classifyDeclaration(field), sensitivity, approvalState: "not_required", action: "prepare", requiresUser: false, blockedReason: null, value: decision.value, candidates: projectProvenance(decision.candidates, true) };
  }

  // Sensitive / consequential: explicit per-disclosure approval required (BR-005).
  const scope = { ...context, formId, fieldId: decision.fieldId, canonicalIdentifier: decision.canonicalIdentifier, value: decision.value };
  if (checkApproval(approvals, scope) === "granted") {
    return { ...base, isDeclaration: classifyDeclaration(field), sensitivity, approvalState: "granted", action: "prepare", requiresUser: false, blockedReason: null, value: decision.value, candidates: projectProvenance(decision.candidates, true) };
  }
  // Unapproved: value is masked out of the review entirely; only the ask remains.
  return { ...base, isDeclaration: classifyDeclaration(field), sensitivity, approvalState: "required", requiresUser: true, blockedReason: BLOCK.approvalRequired, candidates: projectProvenance(decision.candidates, false) };
}

// Compute the deterministic review over a whole M3 snapshot. Reuses M5 retrieval for status +
// provenance, then layers sensitivity, declaration, approval, and the submission boundary.
// Production defaults resolve/classify nothing and grant nothing, so the honest default review
// is "every field unknown; nothing disclosable; DOCURA submits nothing".
export function computeReview({
  snapshot,
  record,
  resolveField,
  classifyTier = noApprovedSensitivityTier,
  classifyDeclaration = noApprovedDeclarationClassification,
  approvals = newApprovalLedger(),
  context = {},
} = {}) {
  const retrieval = computeRetrieval({ snapshot, record, resolveField });
  const summary = { total: 0, disclosable: 0, approvalRequired: 0, blocked: 0, requiresUser: 0 };

  const forms = retrieval.forms.map((form, i) => {
    const snapForm = snapshot?.forms?.[i];
    const fields = form.fields.map((decision, j) => {
      const field = snapForm?.fields?.[j] ?? {};
      const entry = reviewField(decision, { classifyTier, classifyDeclaration, approvals, context, formId: form.formId, field });
      summary.total += 1;
      if (entry.action === "prepare") summary.disclosable += 1;
      if (entry.approvalState === "required") summary.approvalRequired += 1;
      if (entry.approvalState === "blocked") summary.blocked += 1;
      if (entry.requiresUser) summary.requiresUser += 1;
      return entry;
    });
    // The submission boundary is explicit and per-form: DOCURA never operates a submit control.
    return { formId: form.formId, standalone: form.standalone, fields, submit: { operated: false, reason: "DOCURA never submits a form or operates a submit control (BR-008)." } };
  });

  return { forms, summary };
}
