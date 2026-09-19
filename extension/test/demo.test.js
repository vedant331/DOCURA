// DEMO dynamic web-field interpretation + safe autofill — end-to-end at the decision layer.
// TECHNICAL TEST ONLY (not S-6 evidence, not production attribute release).
//
// Proves: fields with MEANINGLESS ids/names resolve by their accessible LABEL through the demo
// interpreter; routine fields fill, sensitive fields require approval (then fill), unknown and
// declaration fields stay untouched; and audit carries no value. Uses the SAME computeFillPlan
// pipeline content.js uses, with the demo seams injected (as content.js does under DEMO_MODE).

import assert from "node:assert/strict";
import { test } from "node:test";

import {
  computeFillPlan,
  applyFillPlan,
  pendingApprovals,
  fillAuditAction,
} from "../src/autofill.js";
import { grantApproval } from "../src/sensitivity.js";
import {
  demoResolveField,
  demoFieldAutomation,
  demoClassifyTier,
  demoClassifyDeclaration,
  isDemoForm,
} from "../src/demo.js";

// Fields as detect.js would emit them for the realistic fixture: MEANINGLESS id/name, meaning
// only in the label.
const FIELDS = [
  { fieldId: "x71", id: "x71", name: "field_891", type: "text", required: false, label: "Applicant Name" },
  { fieldId: "random_22", id: "random_22", name: "abc991", type: "text", required: false, label: "Birth Date" },
  { fieldId: "field_q1", id: "field_q1", name: "z77", type: "text", required: false, label: "Permanent Account Number" },
  { fieldId: "foo_991", id: "foo_991", name: "bar_18", type: "text", required: false, label: "UIDAI Number" },
  { fieldId: "anything", id: "anything", name: "field_x", type: "tel", required: false, label: "Mobile Number" },
  { fieldId: "randomEmail", id: "randomEmail", name: "qwe_123", type: "email", required: false, label: "Email Address" },
  { fieldId: "q9", id: "q9", name: "n2", type: "text", required: false, label: "Residential Address" },
  { fieldId: "c1", id: "c1", name: "c2", type: "text", required: false, label: "Favourite Colour" },
  { fieldId: "decl1", id: "decl1", name: "d1", type: "checkbox", required: false, label: "I agree to the terms and conditions" },
];

const FORM_ID = "demo-application-form";
const SNAPSHOT = { forms: [{ formId: FORM_ID, standalone: true, fields: FIELDS }] };

function attr(id, value) {
  return {
    canonical_identifier: id,
    value,
    is_ambiguous: false,
    observations: [{ value, confidence: 0.95, document_id: "doc1", extraction_run_id: "run1", page_number: 1, region: null }],
  };
}

const RECORD = {
  attributes: [
    attr("person.full_name", "Vedant Santosh Kadam"),
    attr("person.date_of_birth", "2007-03-24"),
    attr("person.email", "example@gmail.com"),
    attr("person.phone", "9876543210"),
    attr("person.address", "Mumbai, Maharashtra"),
    attr("identity.pan_number", "ABCDE1234F"),
    attr("identity.aadhaar_number", "1234 5678 9012"),
  ],
};

const seams = {
  resolveField: demoResolveField,
  fieldAutomation: demoFieldAutomation,
  isEligibleForm: isDemoForm,
};

// A minimal fake DOM: text inputs addressable by id, recording writes.
function fakeRoot(fields) {
  const els = new Map();
  for (const f of fields) {
    els.set(f.id, { value: "", attrs: {}, setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k] ?? null; } });
  }
  return { getElementById: (id) => els.get(id) ?? null, querySelector: () => null, _els: els };
}

// --- interpretation is label-driven, ids/names are ignored --------------------------------
test("meaningful labels resolve; meaningless id/name alone does not", () => {
  assert.equal(demoResolveField({ label: "Permanent Account Number", id: "z77", name: "field_891" }), "identity.pan_number");
  assert.equal(demoResolveField({ label: "UIDAI Number", id: "foo_991" }), "identity.aadhaar_number");
  assert.equal(demoResolveField({ label: "Birth Date", id: "random_22" }), "person.date_of_birth");
  // No matching label — a meaningless id/name must NOT resolve (no guessing).
  assert.equal(demoResolveField({ label: "Favourite Colour", id: "c1", name: "c2" }), null);
  assert.equal(demoResolveField({ id: "z77", name: "field_891" }), null);
});

test("tiers and declaration are classified from meaning, not id", () => {
  assert.equal(demoClassifyTier({ label: "Applicant Name" }), "routine");
  assert.equal(demoClassifyTier({ label: "Permanent Account Number" }), "sensitive");
  assert.equal(demoClassifyTier({ label: "Favourite Colour" }), "unknown");
  assert.equal(demoClassifyDeclaration({ type: "checkbox", label: "I agree to the terms and conditions" }), true);
  assert.equal(demoClassifyDeclaration({ type: "text", label: "Applicant Name" }), false);
});

// --- the safety decisions over the realistic form -----------------------------------------
test("routine fills, sensitive needs approval, unknown/declaration untouched", () => {
  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, context: {}, ...seams });
  const byField = Object.fromEntries(plan.forms[0].fields.map((f) => [f.fieldId, f]));

  assert.equal(byField.x71.action, "fill"); // Applicant Name (routine)
  assert.equal(byField.x71.value, "Vedant Santosh Kadam");
  assert.equal(byField.anything.action, "fill"); // Mobile (routine)
  assert.equal(byField.randomEmail.action, "fill"); // Email (routine)
  assert.equal(byField.q9.action, "fill"); // Address (routine)

  assert.equal(byField.random_22.action, "approval_required"); // Birth Date (sensitive)
  assert.equal(byField.field_q1.action, "approval_required"); // PAN (sensitive)
  assert.equal(byField.foo_991.action, "approval_required"); // Aadhaar (sensitive)

  assert.equal(byField.c1.action, "untouched"); // Favourite Colour (unknown)
  assert.equal(byField.decl1.action, "untouched"); // Declaration (never automated)
});

test("actual DOM: routine values are written, sensitive/unknown/declaration are not", () => {
  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, context: {}, ...seams });
  const root = fakeRoot(FIELDS);
  const { filled } = applyFillPlan({ plan, root });

  assert.equal(root._els.get("x71").value, "Vedant Santosh Kadam"); // routine filled
  assert.equal(root._els.get("randomEmail").value, "example@gmail.com");
  assert.equal(root._els.get("field_q1").value, ""); // sensitive PAN NOT filled (no approval)
  assert.equal(root._els.get("c1").value, ""); // unknown untouched
  assert.equal(root._els.get("decl1").value, ""); // declaration untouched
  assert.ok(filled.every((f) => f.fieldId !== "field_q1" && f.fieldId !== "decl1"));
});

test("sensitive field fills only AFTER an exact-scope approval", () => {
  const approvals = new Map();
  const context = { userId: null, sessionId: null };
  const scope = { ...context, formId: FORM_ID, fieldId: "field_q1", canonicalIdentifier: "identity.pan_number", value: "ABCDE1234F" };
  grantApproval(approvals, scope);

  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, approvals, context, ...seams });
  const pan = plan.forms[0].fields.find((f) => f.fieldId === "field_q1");
  assert.equal(pan.action, "fill");
  assert.equal(pan.value, "ABCDE1234F");

  const root = fakeRoot(FIELDS);
  applyFillPlan({ plan, root, approvals });
  assert.equal(root._els.get("field_q1").value, "ABCDE1234F"); // now filled, post-approval
});

test("pending approvals list carries no value; audit is value-free", () => {
  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, context: {}, ...seams });
  const pending = pendingApprovals(plan);
  for (const p of pending) {
    assert.equal("value" in p, false); // FR-SENS-004: no raw value in the ask surface
  }
  const routine = plan.forms[0].fields.find((f) => f.fieldId === "x71");
  const audit = fillAuditAction(routine, { outcome: "succeeded" });
  assert.equal("value" in audit, false);
  assert.equal(audit.detail, "person.full_name"); // canonical id only
  assert.ok(!JSON.stringify(audit).includes("Vedant")); // the value never appears
});

test("record ambiguity is surfaced as ask, not silently filled", () => {
  const ambiguousRecord = {
    attributes: [{
      canonical_identifier: "person.full_name",
      value: null,
      is_ambiguous: true,
      observations: [
        { value: "Vedant Santosh Kadam", confidence: 0.9, document_id: "d1", extraction_run_id: "r1", page_number: 1, region: null },
        { value: "V S Kadam", confidence: 0.9, document_id: "d2", extraction_run_id: "r2", page_number: 1, region: null },
      ],
    }],
  };
  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: ambiguousRecord, context: {}, ...seams });
  const name = plan.forms[0].fields.find((f) => f.fieldId === "x71");
  assert.equal(name.action, "ask");
});
