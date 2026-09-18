// DEMO regression: the realistic form (meaningless ids/names) driven through the REAL modules
// detect.describeField → demo interpreter → computeFillPlan → applyFillPlan (actual DOM writes),
// with a CLEAN single-person record. Mirrors test/fixtures/demo-realistic-form.html.
// TECHNICAL TEST ONLY — not S-6 evidence, not production attribute release.

import { test } from "node:test";
import assert from "node:assert/strict";

import { describeField } from "../src/detect.js";
import { computeFillPlan, applyFillPlan } from "../src/autofill.js";
import { grantApproval } from "../src/sensitivity.js";
import { demoResolveField, demoFieldAutomation, isDemoForm } from "../src/demo.js";

// A DOM input as detect.describeField reads it (value-free surface). Meaning is ONLY in the label.
function input({ type = "text", id, name, label }) {
  const bag = { type };
  if (name) bag.name = name;
  return {
    tagName: "INPUT",
    type,
    id: id ?? null,
    name: name ?? null,
    required: false,
    multiple: false,
    getAttribute: (k) => (k in bag ? String(bag[k]) : null),
    labels: label ? [{ tagName: "LABEL", textContent: label }] : [],
  };
}

// The realistic fixture's fields — opaque ids/names, meaning in the label.
const RAW = [
  input({ id: "x71", name: "field_891", label: "Applicant Name" }),
  input({ id: "random_22", name: "abc991", label: "Birth Date" }),
  input({ id: "field_q1", name: "z77", label: "Permanent Account Number" }),
  input({ id: "foo_991", name: "bar_18", label: "UIDAI Number" }),
  input({ type: "tel", id: "anything", name: "field_x", label: "Mobile Number" }),
  input({ type: "email", id: "randomEmail", name: "qwe_123", label: "Email Address" }),
  input({ id: "q9", name: "n2", label: "Residential Address" }),
  input({ id: "c1", name: "c2", label: "Favourite Colour" }),
  input({ type: "checkbox", id: "decl1", name: "d1", label: "I agree to the terms and conditions" }),
];

const FIELDS = RAW.map(describeField); // REAL detection → value-free descriptors
const FORM_ID = "demo-application-form";
const SNAPSHOT = { forms: [{ formId: FORM_ID, standalone: true, fields: FIELDS }] };

function attr(id, value) {
  return { canonical_identifier: id, value, is_ambiguous: false,
    observations: [{ value, confidence: 0.95, document_id: "doc1", extraction_run_id: "run1", page_number: 1, region: null }] };
}
// A CLEAN single-person record (values as OCR would yield them; not hard-coded into any extractor).
const RECORD = { attributes: [
  attr("person.full_name", "Neha Kulkarni"),
  attr("person.date_of_birth", "1998-07-12"),
  attr("person.age", "27"),
  attr("person.email", "neha.kulkarni@example.com"),
  attr("person.phone", "9812345670"),
  attr("person.address", "Bengaluru, Karnataka"),
  attr("identity.pan_number", "ZYXWV9876Z"),
  attr("identity.aadhaar_number", "9876 5432 1098"),
]};

const seams = { resolveField: demoResolveField, fieldAutomation: demoFieldAutomation, isEligibleForm: isDemoForm };

function fakeRoot(fields) {
  const els = new Map();
  for (const f of fields) els.set(f.id, { value: "", attrs: {}, setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k] ?? null; } });
  return { getElementById: (id) => els.get(id) ?? null, querySelector: () => null, _els: els };
}

test("detect captures the label, not the opaque id, and is value-free", () => {
  const pan = FIELDS[2];
  assert.equal(pan.label, "Permanent Account Number");
  assert.equal(pan.id, "field_q1"); // opaque id preserved but not used for meaning
  assert.equal("value" in pan, false);
  assert.equal(demoResolveField(pan), "identity.pan_number"); // resolved from the LABEL
});

test("routine fields fill; sensitive need approval; unknown/declaration untouched", () => {
  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, context: {}, ...seams });
  const by = Object.fromEntries(plan.forms[0].fields.map((f) => [f.fieldId, f]));
  assert.equal(by.x71.action, "fill");            // Applicant Name → routine
  assert.equal(by.anything.action, "fill");       // Mobile → routine
  assert.equal(by.randomEmail.action, "fill");    // Email → routine
  assert.equal(by.q9.action, "fill");             // Residential Address → routine
  assert.equal(by.random_22.action, "approval_required"); // Birth Date → sensitive
  assert.equal(by.field_q1.action, "approval_required");  // PAN → sensitive
  assert.equal(by.foo_991.action, "approval_required");   // UIDAI → sensitive
  assert.equal(by.c1.action, "untouched");        // Favourite Colour → unknown
  assert.equal(by.decl1.action, "untouched");     // Declaration → never automated
});

test("actual DOM: routine written, sensitive blank until approval then written", () => {
  // Pass 1: no approvals.
  let plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, context: {}, ...seams });
  const root = fakeRoot(FIELDS);
  applyFillPlan({ plan, root });
  assert.equal(root._els.get("x71").value, "Neha Kulkarni");     // routine filled
  assert.equal(root._els.get("randomEmail").value, "neha.kulkarni@example.com");
  assert.equal(root._els.get("anything").value, "9812345670");
  assert.equal(root._els.get("q9").value, "Bengaluru, Karnataka");
  assert.equal(root._els.get("field_q1").value, "");            // PAN blank (no approval)
  assert.equal(root._els.get("random_22").value, "");           // DOB blank
  assert.equal(root._els.get("c1").value, "");                  // unknown blank
  assert.equal(root._els.get("decl1").value, "");               // declaration blank

  // Pass 2: approve PAN exactly, recompute, apply → PAN now fills; others still gated.
  const approvals = new Map();
  grantApproval(approvals, { userId: null, sessionId: null, formId: FORM_ID, fieldId: "field_q1", canonicalIdentifier: "identity.pan_number", value: "ZYXWV9876Z" });
  plan = computeFillPlan({ snapshot: SNAPSHOT, record: RECORD, approvals, context: { userId: null, sessionId: null }, ...seams });
  applyFillPlan({ plan, root, approvals });
  assert.equal(root._els.get("field_q1").value, "ZYXWV9876Z");  // filled after approval
  assert.equal(root._els.get("random_22").value, "");           // DOB still gated (not approved)
});

test("record ambiguity (two names) is asked, never auto-filled", () => {
  const ambiguous = { attributes: [{ canonical_identifier: "person.full_name", value: null, is_ambiguous: true,
    observations: [
      { value: "Arjun Mehta", confidence: 0.9, document_id: "d1", extraction_run_id: "r1", page_number: 1, region: null },
      { value: "Riya Sharma", confidence: 0.9, document_id: "d1", extraction_run_id: "r1", page_number: 1, region: null },
    ] }] };
  const plan = computeFillPlan({ snapshot: SNAPSHOT, record: ambiguous, context: {}, ...seams });
  const name = plan.forms[0].fields.find((f) => f.fieldId === "x71");
  assert.equal(name.action, "ask"); // single-source ambiguity → ask, not fill (matches the demo PDF)
});
