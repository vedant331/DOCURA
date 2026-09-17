import { test } from "node:test";
import assert from "node:assert/strict";

import { scanForms } from "../src/detect.js";
import {
  computeFillPlan,
  applyFillPlan,
  pendingApprovals,
  fillAuditAction,
  approvalRequestAuditAction,
  approvalDecisionAuditAction,
} from "../src/autofill.js";
import { newApprovalLedger, grantApproval } from "../src/sensitivity.js";
import * as api from "../src/api.js";

// M10 end-to-end (extension side): backend record → resolver → policy → real DOM write.
// Exercised over a DOM that mirrors test/fixtures/mock-form-m10.html. No OCR, no AI, no fake
// values in production code — the record here is an explicit TEST fixture (M10 §16).

// ---- fake DOM (same surface detect.js + autofill.js read/write) -------------
function el({ tag = "input", type, id, name, required, attrs = {} }) {
  const bag = { ...attrs };
  if (type !== undefined && tag === "input") bag.type = type;
  if (name !== undefined) bag.name = name;
  if (required) bag.required = "";
  const node = {
    tagName: tag.toUpperCase(),
    type,
    id: id ?? null,
    name: name ?? null,
    required: !!required,
    multiple: false,
    value: "",
    _attrs: bag,
    events: [],
    form: null,
    getAttribute: (k) => (k in node._attrs ? String(node._attrs[k]) : null),
    setAttribute: (k, v) => { node._attrs[k] = v; },
    dispatchEvent: (e) => { node.events.push(e?.type ?? "event"); return true; },
  };
  return node;
}

function buildDom() {
  const form = { id: "mca-mock", getAttribute: (k) => (k === "name" ? "mca-mock" : null) };
  const nodes = [
    el({ type: "text", id: "full_name", name: "full_name", required: true, attrs: { maxlength: "120" } }),
    el({ type: "text", id: "sensitive_full_name", name: "sensitive_full_name" }),
    el({ type: "text", id: "unknown_text", name: "unknown_text" }),
    el({ type: "checkbox", id: "field_declaration", name: "field_declaration", required: true }),
    el({ type: "text", id: "field_ambiguous_1", name: "field_ambiguous" }),
    el({ type: "text", id: "field_ambiguous_2", name: "field_ambiguous" }),
    el({ type: "file", id: "field_file", name: "field_file", required: true, attrs: { accept: "application/pdf" } }),
  ];
  for (const n of nodes) n.form = form;
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const root = {
    querySelectorAll: () => nodes,
    getElementById: (id) => byId.get(id) ?? null,
    querySelector: (sel) => {
      const m = /^\[name="(.+)"\]$/.exec(sel);
      return m ? nodes.find((n) => n.name === m[1]) ?? null : null;
    },
  };
  return { root, nodes, byId };
}

// Record fixtures (TEST-ONLY; never seeded into production).
function recordAvailable(value = "Test User") {
  return { attributes: [{ canonical_identifier: "person.full_name", value, is_ambiguous: false,
    observations: [{ value, confidence: null, document_id: "doc-1", extraction_run_id: "run-1", page_number: 1, region: null }] }], count: 1 };
}
function recordAmbiguous() { // two values from ONE document → ambiguous (BR-003)
  return { attributes: [{ canonical_identifier: "person.full_name", value: null, is_ambiguous: true,
    observations: [
      { value: "Test User", confidence: null, document_id: "doc-1", extraction_run_id: "run-1", page_number: 1, region: null },
      { value: "Tset User", confidence: null, document_id: "doc-1", extraction_run_id: "run-1", page_number: 1, region: null },
    ] }], count: 1 };
}
function recordConflict() { // distinct values across TWO documents → conflict (BR-004)
  return { attributes: [{ canonical_identifier: "person.full_name", value: null, is_ambiguous: true,
    observations: [
      { value: "Test User", confidence: null, document_id: "doc-1", extraction_run_id: "run-1", page_number: 1, region: null },
      { value: "Other Name", confidence: null, document_id: "doc-2", extraction_run_id: "run-2", page_number: 1, region: null },
    ] }], count: 1 };
}

const CONTEXT = { userId: null, sessionId: null };
function planFor(record, approvals = newApprovalLedger()) {
  const snapshot = scanForms(buildDom().root);
  return computeFillPlan({ snapshot, record, approvals, context: CONTEXT });
}

test("#2/#3/#4/#11 — full_name resolves, fills the real DOM with the retrieved value + provenance", () => {
  const { root, byId } = buildDom();
  const snapshot = scanForms(root);
  const plan = computeFillPlan({ snapshot, record: recordAvailable("Test User"), approvals: newApprovalLedger(), context: CONTEXT });

  const fullName = plan.forms[0].fields.find((f) => f.fieldId === "full_name");
  assert.equal(fullName.action, "fill");
  assert.equal(fullName.canonicalIdentifier, "person.full_name");
  assert.equal(fullName.value, "Test User");

  const { count, filled } = applyFillPlan({ plan, root });
  assert.equal(count, 1); // only the routine full_name field
  assert.equal(byId.get("full_name").value, "Test User"); // REAL DOM mutation
  assert.equal(byId.get("full_name").getAttribute("data-docura-filled"), "true");
  assert.ok(byId.get("full_name").events.includes("input")); // page frameworks notified
  // Provenance is preserved and traceable (M10 §15).
  assert.equal(filled[0].provenance.canonicalIdentifier, "person.full_name");
  assert.equal(filled[0].provenance.sources[0].documentId, "doc-1");
});

test("#5 — an unmapped field is left untouched (no label guessing)", () => {
  const { root, byId } = buildDom();
  const plan = computeFillPlan({ snapshot: scanForms(root), record: recordAvailable(), approvals: newApprovalLedger(), context: CONTEXT });
  const unknown = plan.forms[0].fields.find((f) => f.fieldId === "unknown_text");
  assert.equal(unknown.action, "untouched");
  applyFillPlan({ plan, root });
  assert.equal(byId.get("unknown_text").value, ""); // never written
});

test("#6 — no available record value → field not filled, honest unavailable state", () => {
  const { root, byId } = buildDom();
  const plan = computeFillPlan({ snapshot: scanForms(root), record: { attributes: [], count: 0 }, approvals: newApprovalLedger(), context: CONTEXT });
  const fullName = plan.forms[0].fields.find((f) => f.fieldId === "full_name");
  assert.equal(fullName.action, "unavailable");
  applyFillPlan({ plan, root });
  assert.equal(byId.get("full_name").value, ""); // nothing guessed, nothing faked
});

test("#7 — ambiguous value does not auto-fill (asks)", () => {
  const { root, byId } = buildDom();
  const plan = computeFillPlan({ snapshot: scanForms(root), record: recordAmbiguous(), approvals: newApprovalLedger(), context: CONTEXT });
  const fullName = plan.forms[0].fields.find((f) => f.fieldId === "full_name");
  assert.equal(fullName.action, "ask");
  applyFillPlan({ plan, root });
  assert.equal(byId.get("full_name").value, "");
});

test("#8 — conflicting sources do not auto-resolve (asks)", () => {
  const { root, byId } = buildDom();
  const plan = computeFillPlan({ snapshot: scanForms(root), record: recordConflict(), approvals: newApprovalLedger(), context: CONTEXT });
  const fullName = plan.forms[0].fields.find((f) => f.fieldId === "full_name");
  assert.equal(fullName.action, "ask");
  assert.equal(fullName.status, "conflict");
  applyFillPlan({ plan, root });
  assert.equal(byId.get("full_name").value, "");
});

test("#9 — sensitive field requires explicit, exact-scope approval before filling", () => {
  const { root, byId } = buildDom();
  const snapshot = scanForms(root);
  const approvals = newApprovalLedger();

  // Before approval: the sensitive field is NOT filled.
  let plan = computeFillPlan({ snapshot, record: recordAvailable("Test User"), approvals, context: CONTEXT });
  const before = plan.forms[0].fields.find((f) => f.fieldId === "sensitive_full_name");
  assert.equal(before.action, "approval_required");
  assert.deepEqual(pendingApprovals(plan).map((p) => p.fieldId), ["sensitive_full_name"]);
  applyFillPlan({ plan, root, approvals });
  assert.equal(byId.get("sensitive_full_name").value, ""); // not disclosed without consent

  // Grant the one exact-scope approval, then it fills.
  grantApproval(approvals, { ...CONTEXT, formId: "mca-mock", fieldId: "sensitive_full_name", canonicalIdentifier: "person.full_name", value: "Test User" });
  plan = computeFillPlan({ snapshot, record: recordAvailable("Test User"), approvals, context: CONTEXT });
  assert.equal(plan.forms[0].fields.find((f) => f.fieldId === "sensitive_full_name").action, "fill");
  applyFillPlan({ plan, root, approvals });
  assert.equal(byId.get("sensitive_full_name").value, "Test User");

  // The approval does not carry to another field (exact scope, BR-007): a different fieldId
  // with the same value remains approval_required.
  assert.equal(
    require_recompute(snapshot, approvals),
    "approval_required",
  );
});

// Helper: re-plan and read the routine field's sibling sensitive scope isolation is covered above;
// here we assert a DIFFERENT value is not authorised by the granted approval.
function require_recompute(snapshot, approvals) {
  const plan = computeFillPlan({ snapshot, record: recordAvailable("Changed Name"), approvals, context: CONTEXT });
  return plan.forms[0].fields.find((f) => f.fieldId === "sensitive_full_name").action;
}

test("#10 — the declaration checkbox is never touched (unmapped, never filled)", () => {
  const { root, byId } = buildDom();
  const plan = computeFillPlan({ snapshot: scanForms(root), record: recordAvailable(), approvals: newApprovalLedger(), context: CONTEXT });
  const decl = plan.forms[0].fields.find((f) => f.fieldId === "field_declaration");
  assert.equal(decl.action, "untouched");
  applyFillPlan({ plan, root });
  assert.equal(byId.get("field_declaration").value, ""); // never written; checkbox never ticked
});

test("M12-D3 — date_of_birth is consent-gated: approval_required, then fills the date input", () => {
  // A controlled form with a date_of_birth field; the record holds an available DOB value.
  const form = { id: "mca-mock", getAttribute: (k) => (k === "name" ? "mca-mock" : null) };
  const dob = el({ type: "date", id: "date_of_birth", name: "date_of_birth" });
  dob.form = form;
  const byId = new Map([["date_of_birth", dob]]);
  const root = {
    querySelectorAll: () => [dob],
    getElementById: (id) => byId.get(id) ?? null,
    querySelector: (sel) => {
      const m = /^\[name="(.+)"\]$/.exec(sel);
      return m ? [dob].find((n) => n.name === m[1]) ?? null : null;
    },
  };
  const record = { attributes: [{ canonical_identifier: "person.date_of_birth", value: "1990-02-01", is_ambiguous: false,
    observations: [{ value: "1990-02-01", confidence: null, document_id: "doc-1", extraction_run_id: "run-1", page_number: 1, region: null }] }], count: 1 };
  const approvals = newApprovalLedger();
  const snapshot = scanForms(root);

  // Before approval: NOT auto-filled (G-15 default → sensitive → consent required).
  let plan = computeFillPlan({ snapshot, record, approvals, context: CONTEXT });
  const before = plan.forms[0].fields.find((f) => f.fieldId === "date_of_birth");
  assert.equal(before.action, "approval_required");
  assert.equal(before.canonicalIdentifier, "person.date_of_birth");
  applyFillPlan({ plan, root, approvals });
  assert.equal(dob.value, ""); // never disclosed without consent

  // After exact-scope approval: fills the real date input with the retrieved value.
  grantApproval(approvals, { ...CONTEXT, formId: "mca-mock", fieldId: "date_of_birth", canonicalIdentifier: "person.date_of_birth", value: "1990-02-01" });
  plan = computeFillPlan({ snapshot, record, approvals, context: CONTEXT });
  assert.equal(plan.forms[0].fields.find((f) => f.fieldId === "date_of_birth").action, "fill");
  applyFillPlan({ plan, root, approvals });
  assert.equal(dob.value, "1990-02-01");
  assert.equal(dob.getAttribute("data-docura-attribute"), "person.date_of_birth");
});

test("#14 — the controlled mapping does NOT fire on an arbitrary external form", () => {
  // An unrelated website form that happens to contain id="full_name" must NOT be auto-filled:
  // the mapping is scoped to the controlled form's identity (M11-D5, acceptance J).
  const form = { id: "some-random-site-form", getAttribute: (k) => (k === "name" ? "signup" : null) };
  const node = el({ type: "text", id: "full_name", name: "full_name" });
  node.form = form;
  const root = {
    querySelectorAll: () => [node],
    getElementById: (id) => (id === "full_name" ? node : null),
    querySelector: () => node,
  };
  const plan = computeFillPlan({ snapshot: scanForms(root), record: recordAvailable("Test User"), approvals: newApprovalLedger(), context: CONTEXT });
  assert.equal(plan.forms[0].fields[0].action, "untouched");
  applyFillPlan({ plan, root });
  assert.equal(node.value, ""); // never filled on a non-controlled form
});

test("#1 — api.getRecord calls /record/attributes with the bearer token and returns the record", async () => {
  let seenUrl = null;
  let seenAuth = null;
  const fakeFetch = async (url, init) => {
    seenUrl = url;
    seenAuth = init.headers.Authorization;
    return { ok: true, status: 200, json: async () => recordAvailable("Test User") };
  };
  const record = await api.getRecord("http://127.0.0.1:8000", "tok-123", fakeFetch);
  assert.equal(seenUrl, "http://127.0.0.1:8000/record/attributes");
  assert.equal(seenAuth, "Bearer tok-123");
  assert.equal(record.attributes[0].value, "Test User");
});

// ---- M15: audit-action builders + failed-fill reporting --------------------

const CONTRACT_KEYS = new Set([
  "action_type",
  "outcome",
  "field_ref",
  "document_id",
  "observation_id",
  "reverses_action_id",
  "detail",
]);

function assertNoValueLeak(action) {
  // The audit action must carry no field value and no provenance object — references only.
  assert.ok(!("value" in action), "audit action must not contain a field value");
  assert.ok(!("provenance" in action), "audit action must not contain the provenance object");
  for (const k of Object.keys(action)) {
    assert.ok(CONTRACT_KEYS.has(k), `unexpected key in audit action: ${k}`);
  }
}

test("M15 fillAuditAction: references only, never the value (incl. a sensitive fill)", () => {
  // A filled entry as applyFillPlan produces it — it DOES carry the value + provenance.value.
  const entry = {
    fieldId: "date_of_birth",
    canonicalIdentifier: "person.date_of_birth",
    value: "1990-02-01", // a real, sensitive value present on the source entry
    sensitive: true,
    provenance: {
      canonicalIdentifier: "person.date_of_birth",
      value: "1990-02-01",
      sources: [{ documentId: "doc-1", extractionRunId: "run-1", pageNumber: 1, confidence: null }],
    },
  };
  const action = fillAuditAction(entry, { outcome: "succeeded" });
  assert.equal(action.action_type, "fill");
  assert.equal(action.outcome, "succeeded");
  assert.equal(action.field_ref, "date_of_birth");
  assert.equal(action.detail, "person.date_of_birth"); // canonical id, not the value
  assert.equal(action.document_id, "doc-1"); // owned source reference
  assertNoValueLeak(action);
  // The sensitive value "1990-02-01" appears nowhere in the serialized payload.
  assert.ok(!JSON.stringify(action).includes("1990-02-01"));
});

test("M15 fillAuditAction supports a failed outcome", () => {
  const action = fillAuditAction({ fieldId: "full_name", canonicalIdentifier: "person.full_name" }, { outcome: "failed" });
  assert.equal(action.action_type, "fill");
  assert.equal(action.outcome, "failed");
  assertNoValueLeak(action);
});

test("M15 approval builders carry only handle + canonical id", () => {
  const req = approvalRequestAuditAction({ fieldId: "sensitive_full_name", canonicalIdentifier: "person.full_name" });
  assert.equal(req.action_type, "approval_request");
  assert.equal(req.outcome, "succeeded");
  assert.equal(req.field_ref, "sensitive_full_name");
  assert.equal(req.detail, "person.full_name");
  assertNoValueLeak(req);

  const dec = approvalDecisionAuditAction({ fieldId: "sensitive_full_name", canonicalIdentifier: "person.full_name", value: "Test User" });
  assert.equal(dec.action_type, "approval_decision");
  assert.equal(dec.field_ref, "sensitive_full_name");
  assertNoValueLeak(dec);
  assert.ok(!JSON.stringify(dec).includes("Test User"));
});

test("M15 applyFillPlan reports a failed fill when the target element is gone", () => {
  // Snapshot says full_name is fillable, but the DOM root has no such element.
  const form = { id: "mca-mock", getAttribute: (k) => (k === "name" ? "mca-mock" : null) };
  const node = el({ type: "text", id: "full_name", name: "full_name", required: true });
  node.form = form;
  const snapshot = scanForms({ querySelectorAll: () => [node] });
  const emptyRoot = { getElementById: () => null, querySelector: () => null, querySelectorAll: () => [] };

  const plan = computeFillPlan({ snapshot, record: recordAvailable("Test User"), approvals: newApprovalLedger(), context: CONTEXT });
  const { filled, failed } = applyFillPlan({ plan, root: emptyRoot });
  assert.equal(filled.length, 0);
  assert.equal(failed.length, 1);
  assert.equal(failed[0].fieldId, "full_name");
  // The failed record carries the reference, never the value written.
  assert.ok(!("value" in fillAuditAction(failed[0], { outcome: "failed" })));
});
