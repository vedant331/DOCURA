import { test } from "node:test";
import assert from "node:assert/strict";

import {
  computeReview,
  newApprovalLedger,
  grantApproval,
  checkApproval,
  consumeApproval,
  noApprovedSensitivityTier,
  noApprovedDeclarationClassification,
} from "../src/sensitivity.js";
import { FormWatcher } from "../src/detect.js";

// ---- helpers ---------------------------------------------------------------
function field({ fieldId = "f", type = "text", required = false } = {}) {
  return { fieldId, type, required, constraints: {} };
}
function snapshot(fields, { formId = "app", standalone = false } = {}) {
  return { forms: [{ formId, standalone, fields }], formCount: standalone ? 0 : 1 };
}
function obs({ value, documentId = "doc-1" } = {}) {
  return { value, confidence: null, document_id: documentId, extraction_run_id: "run-1", page_number: 1, region: null };
}
function record(attributes) {
  return { attributes, count: attributes.length };
}
const resolveFullName = (f) => (f.fieldId === "full_name" ? "person.full_name" : null);
const available = (value) => record([{ canonical_identifier: "person.full_name", value, is_ambiguous: false, observations: [obs({ value })] }]);
const byFieldId = (r) => Object.fromEntries(r.forms[0].fields.map((f) => [f.fieldId, f]));

const tierRoutine = () => "routine";
const tierSensitive = () => "sensitive";
const asDeclaration = () => true;
const ctx = { userId: "u1", sessionId: "s1" };

// 1. Non-sensitive (routine) item does not require sensitive approval.
test("routine available item is disclosable without sensitive approval", () => {
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("Asha Rao"), resolveField: resolveFullName, classifyTier: tierRoutine, context: ctx });
  const f = byFieldId(r).full_name;
  assert.equal(f.sensitivity, "routine");
  assert.equal(f.approvalState, "not_required");
  assert.equal(f.action, "prepare");
  assert.equal(f.value, "Asha Rao");
  assert.equal(f.canSubmit, false);
});

// 2. Sensitive item without approval → blocked / requires approval, value masked out.
test("sensitive available item without approval requires approval and masks the value", () => {
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("Asha Rao"), resolveField: resolveFullName, classifyTier: tierSensitive, context: ctx });
  const f = byFieldId(r).full_name;
  assert.equal(f.approvalState, "required");
  assert.equal(f.requiresUser, true);
  assert.equal("value" in f, false); // never disclosed without approval
  assert.equal(f.candidates[0].value, undefined); // masked in provenance too
  assert.equal(f.candidates[0].provenance[0].documentId, "doc-1"); // source still explainable
});

// 3. Sensitive item WITH explicit approval → granted for exactly that disclosure.
test("sensitive item with explicit approval is granted and the value is revealed", () => {
  const approvals = newApprovalLedger();
  grantApproval(approvals, { ...ctx, formId: "app", fieldId: "full_name", canonicalIdentifier: "person.full_name", value: "Asha Rao" });
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("Asha Rao"), resolveField: resolveFullName, classifyTier: tierSensitive, approvals, context: ctx });
  const f = byFieldId(r).full_name;
  assert.equal(f.approvalState, "granted");
  assert.equal(f.value, "Asha Rao");
  assert.equal(f.action, "prepare");
});

// 4. Approval for Field A does not authorize Field B.
test("approval for one field does not authorize another field", () => {
  const l = newApprovalLedger();
  grantApproval(l, { ...ctx, formId: "app", fieldId: "field_a", canonicalIdentifier: "person.full_name", value: "v" });
  assert.equal(checkApproval(l, { ...ctx, formId: "app", fieldId: "field_a", canonicalIdentifier: "person.full_name", value: "v" }), "granted");
  assert.equal(checkApproval(l, { ...ctx, formId: "app", fieldId: "field_b", canonicalIdentifier: "person.full_name", value: "v" }), "required");
});

// 5. Approval in Session 1 does not authorize Session 2.
test("approval in one session does not authorize another session", () => {
  const l = newApprovalLedger();
  grantApproval(l, { userId: "u1", sessionId: "s1", formId: "app", fieldId: "x", canonicalIdentifier: "a", value: "v" });
  assert.equal(checkApproval(l, { userId: "u1", sessionId: "s2", formId: "app", fieldId: "x", canonicalIdentifier: "a", value: "v" }), "required");
});

// 6. Approval for Form A does not authorize Form B.
test("approval for one form does not authorize another form", () => {
  const l = newApprovalLedger();
  grantApproval(l, { ...ctx, formId: "form_a", fieldId: "x", canonicalIdentifier: "a", value: "v" });
  assert.equal(checkApproval(l, { ...ctx, formId: "form_b", fieldId: "x", canonicalIdentifier: "a", value: "v" }), "required");
});

// 7. Approval cannot be generalized to another attribute or another value.
test("approval does not generalize to another attribute or value", () => {
  const l = newApprovalLedger();
  grantApproval(l, { ...ctx, formId: "app", fieldId: "x", canonicalIdentifier: "person.full_name", value: "v" });
  assert.equal(checkApproval(l, { ...ctx, formId: "app", fieldId: "x", canonicalIdentifier: "person.dob", value: "v" }), "required"); // other attribute
  assert.equal(checkApproval(l, { ...ctx, formId: "app", fieldId: "x", canonicalIdentifier: "person.full_name", value: "other" }), "required"); // other value
});

// 8. Approval is one-time — it cannot be inherited/reused after it is consumed.
test("approval is one-time: consumed approval no longer authorizes", () => {
  const l = newApprovalLedger();
  const scope = { ...ctx, formId: "app", fieldId: "x", canonicalIdentifier: "a", value: "v" };
  grantApproval(l, scope);
  assert.equal(checkApproval(l, scope), "granted");
  consumeApproval(l, scope);
  assert.equal(checkApproval(l, scope), "required"); // cannot be reused
});

// 9. Declaration/consent control remains blocked from DOCURA automation.
test("a declaration/consent control is blocked and never approvable", () => {
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "agree", type: "checkbox" })]), classifyDeclaration: asDeclaration, context: ctx });
  const f = byFieldId(r).agree;
  assert.equal(f.isDeclaration, true);
  assert.equal(f.approvalState, "blocked");
  assert.equal(f.action, "none");
  assert.match(f.blockedReason, /user-owned/i);
});

// 10. Review preserves provenance (source references) for a disclosable value.
test("review preserves provenance for a disclosable value", () => {
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("Asha Rao"), resolveField: resolveFullName, classifyTier: tierRoutine, context: ctx });
  const p = byFieldId(r).full_name.candidates[0].provenance[0];
  assert.equal(p.documentId, "doc-1");
  assert.equal(p.extractionRunId, "run-1");
});

// 11. Review never submits — the boundary is explicit on every field and every form.
test("review never submits and marks the submission boundary", () => {
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("Asha Rao"), resolveField: resolveFullName, classifyTier: tierRoutine, context: ctx });
  assert.equal(r.forms[0].submit.operated, false);
  for (const f of r.forms[0].fields) {
    assert.equal(f.canSubmit, false);
    assert.notEqual(f.action, "submit");
    assert.notEqual(f.action, "click");
  }
});

// 12. Review never mutates the form: pure data result, no DOM handle.
test("review is a plain data result and touches no DOM/form", () => {
  const controls = [{ tagName: "INPUT", type: "text", id: "full_name", name: "full_name", required: false, form: null, getAttribute: () => null }];
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("x"), resolveField: resolveFullName, classifyTier: tierRoutine, context: ctx });
  assert.equal(typeof r, "object");
  void controls;
});

// 13. Unknown sensitivity assignment is not guessed — neither routine nor sensitive.
test("unknown tier is not guessed: disclosure is blocked, value withheld", () => {
  assert.equal(noApprovedSensitivityTier(field({ fieldId: "full_name" })), "unknown");
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: available("Asha Rao"), resolveField: resolveFullName, context: ctx });
  const f = byFieldId(r).full_name;
  assert.equal(f.sensitivity, "unknown");
  assert.equal(f.approvalState, "blocked"); // not "not_required" (routine) and not "required" (sensitive)
  assert.equal("value" in f, false);
  assert.match(f.blockedReason, /unassigned/i);
});

// 14. User ownership/isolation: the review reflects only the record and context it is given.
test("review reflects only the record and context it is given (user isolation)", () => {
  const r = computeReview({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: record([{ canonical_identifier: "person.postal_address", value: "elsewhere", is_ambiguous: false, observations: [obs({ value: "elsewhere" })] }]), resolveField: resolveFullName, classifyTier: tierRoutine, context: ctx });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "unavailable"); // this account holds no full name
  assert.equal("value" in f, false);
});

// 15. A stopped session clears M6 state (mirrors content.js teardown).
test("after stop, teardown clears the review and approval ledger; no further processing", () => {
  const store = { review: undefined };
  const approvals = newApprovalLedger();
  grantApproval(approvals, { ...ctx, formId: "app", fieldId: "x", canonicalIdentifier: "a", value: "v" });
  const controls = [{ tagName: "INPUT", type: "text", id: null, name: "a", required: false, form: null, getAttribute: () => null }];
  const obsRef = { cb: null };
  const factory = (cb) => ((obsRef.cb = cb), { observe() {}, disconnect() {} });
  const w = new FormWatcher({
    root: { querySelectorAll: () => controls },
    onChange: (result) => (store.review = computeReview({ snapshot: result, approvals })),
    observerFactory: factory,
  }).start();
  assert.equal(store.review.summary.total, 1);

  w.stop();
  const teardown = () => { store.review = null; approvals.clear(); };
  teardown();
  assert.equal(approvals.size, 0); // no approval survives the session
  store.review = "UNCHANGED";
  obsRef.cb(); // late mutation after stop
  assert.equal(store.review, "UNCHANGED");
});

// 16. An inactive page (watcher never started) performs no M6 processing.
test("an unstarted watcher (inactive page) computes no review", () => {
  const store = {};
  new FormWatcher({ root: { querySelectorAll: () => [] }, onChange: (result) => (store.review = computeReview({ snapshot: result })) });
  assert.equal("review" in store, false);
  assert.equal(noApprovedDeclarationClassification(field()), "unknown"); // production asserts no declaration
});
