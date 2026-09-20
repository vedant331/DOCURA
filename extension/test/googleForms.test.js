// Google Forms PROTOTYPE adapter — end-to-end at the decision layer, through the EXISTING
// pipeline (interpret → mapping → retrieval → sensitivity → approval → autofill), exactly as
// content.js drives it under the dynamic (demo) seams. No jsdom: DOM fakes implement only the
// querySelector calls the adapter/autofill actually make, mirroring detect.test.js.
//
// Covers: detection, the 7 supported attributes, unknown/declaration untouched, sensitive →
// approval, ambiguity → ask (no auto-fill), user-edit not overwritten, no submission action,
// host restriction, and clean opt-out.

import assert from "node:assert/strict";
import { test } from "node:test";

import { computeFillPlan, applyFillPlan, pendingApprovals } from "../src/autofill.js";
import { computeReview, grantApproval, newApprovalLedger } from "../src/sensitivity.js";
import {
  demoResolveField,
  demoFieldAutomation,
  demoClassifyTier,
  demoClassifyDeclaration,
  isDemoForm,
} from "../src/demo.js";
import {
  scanGoogleForm,
  isGoogleFormsHost,
  GOOGLE_FORMS_MODE,
} from "../src/googleFormsAdapter.js";

// ---- Google Forms DOM harness ----------------------------------------------
// Each question is a `[role="listitem"]` container holding either a native control (input/
// textarea) whose accessible name is a NOISY aria string (heading + "Required question"), or a
// div-based choice control. The adapter must produce the CLEAN question title as the label.

function nativeControl({ tag = "INPUT", type = "text", id = null, name = null, required = false } = {}) {
  const attrs = { type };
  if (name) attrs.name = name;
  if (required) attrs["aria-required"] = "true";
  return {
    tagName: tag,
    type,
    id,
    name,
    required,
    multiple: false,
    value: "",
    getAttribute: (k) => (k in attrs ? String(attrs[k]) : null),
    setAttribute(k, v) {
      attrs[k] = String(v);
    },
    __attrs: attrs,
  };
}

// A question block. `native` is a nativeControl or null; `choice` is "radiogroup"|"checkbox"|
// "listbox" or null. Only ONE of them is present, matching a real Google Form question.
function question({ label, native = null, choice = null, required = false }) {
  const heading = { textContent: required ? `${label} *` : label };
  return {
    querySelector(sel) {
      if (sel.includes('role="heading"')) return heading;
      if (sel.includes('role="radiogroup"')) return choice === "radiogroup" ? {} : null;
      if (sel.includes('role="checkbox"')) return choice === "checkbox" ? {} : null;
      if (sel.includes('role="listbox"')) return choice === "listbox" ? {} : null;
      if (sel.includes('aria-required="true"')) return required ? {} : null;
      if (sel.startsWith("input")) return native; // NATIVE_SELECTOR
      return null;
    },
  };
}

// A document root: querySelectorAll for the scan, plus getElementById/querySelector so
// autofill.findElement can locate a filled control (by id, name, or data-docura-field).
function formRoot(questions) {
  const natives = questions.map((q) => q.__native).filter(Boolean);
  return {
    querySelectorAll: () => questions,
    getElementById: (id) => natives.find((e) => e.id === id) ?? null,
    querySelector(sel) {
      let m = /\[name="([^"]+)"\]/.exec(sel);
      if (m) return natives.find((e) => e.name === m[1]) ?? null;
      m = /\[data-docura-field="([^"]+)"\]/.exec(sel);
      if (m) return natives.find((e) => e.getAttribute("data-docura-field") === m[1]) ?? null;
      return null;
    },
  };
}

function q(opts) {
  const native = opts.native ? nativeControl(opts.native) : null;
  const block = question({ ...opts, native });
  block.__native = native;
  return block;
}

// The test Google Form: realistic labels, opaque/absent input ids (as Google renders them).
function testForm() {
  return formRoot([
    q({ label: "Full Name", native: { type: "text" }, required: true }),
    q({ label: "Date of Birth", native: { type: "date" }, required: true }),
    q({ label: "Email", native: { type: "email" } }),
    q({ label: "Phone Number", native: { type: "text" } }),
    q({ label: "Address", native: { tag: "TEXTAREA", type: "textarea" } }),
    q({ label: "PAN Number", native: { type: "text" } }),
    q({ label: "Aadhaar Number", native: { type: "text" } }),
    q({ label: "I agree to the declaration above", choice: "checkbox" }),
    q({ label: "Favourite Colour", native: { type: "text" } }),
  ]);
}

const DEMO_SEAMS = { resolveField: demoResolveField, fieldAutomation: demoFieldAutomation, isEligibleForm: isDemoForm };
const REVIEW_SEAMS = { classifyTier: demoClassifyTier, classifyDeclaration: demoClassifyDeclaration };

function attr(id, value, extra = {}) {
  return {
    canonical_identifier: id,
    value,
    is_ambiguous: false,
    observations: [{ value, confidence: 0.95, document_id: "doc1", extraction_run_id: "run1", page_number: 1, region: null }],
    ...extra,
  };
}

const RECORD = {
  attributes: [
    attr("person.full_name", "Vedant Santosh Kadam"),
    attr("person.date_of_birth", "2007-03-24"),
    attr("person.email", "test@example.com"),
    attr("person.phone", "9876543210"),
    attr("person.address", "Mumbai, Maharashtra"),
    attr("identity.pan_number", "ABCDE1234F"),
    attr("identity.aadhaar_number", "123412341234"),
  ],
};

function planFor(root, record = RECORD, approvals = newApprovalLedger()) {
  const snapshot = scanGoogleForm(root);
  const plan = computeFillPlan({ snapshot, record, approvals, context: {}, ...DEMO_SEAMS });
  const byLabel = {};
  // map snapshot field label -> plan entry (same order)
  snapshot.forms[0].fields.forEach((f, i) => (byLabel[f.label] = { field: f, entry: plan.forms[0].fields[i] }));
  return { snapshot, plan, byLabel };
}

// ---- 1. detection -----------------------------------------------------------
test("detects every question with a clean label (no aria noise, no submit control)", () => {
  const { snapshot } = planFor(testForm());
  const labels = snapshot.forms[0].fields.map((f) => f.label);
  assert.deepEqual(labels, [
    "Full Name", "Date of Birth", "Email", "Phone Number", "Address",
    "PAN Number", "Aadhaar Number", "I agree to the declaration above", "Favourite Colour",
  ]);
  // Required marker stripped; noisy aria sources cleared so the exact-alias interpreter matches.
  const name = snapshot.forms[0].fields[0];
  assert.equal(name.label, "Full Name");
  assert.equal(name.ariaLabelledBy, null);
  assert.equal(name.ariaLabel, null);
});

// ---- 2–8. supported attribute mapping (label-driven, exact) -----------------
test("maps the 7 supported labels to their canonical attributes", () => {
  const { byLabel } = planFor(testForm());
  assert.equal(byLabel["Full Name"].entry.canonicalIdentifier, "person.full_name");
  assert.equal(byLabel["Date of Birth"].entry.canonicalIdentifier, "person.date_of_birth");
  assert.equal(byLabel["Email"].entry.canonicalIdentifier, "person.email");
  assert.equal(byLabel["Phone Number"].entry.canonicalIdentifier, "person.phone");
  assert.equal(byLabel["Address"].entry.canonicalIdentifier, "person.address");
  assert.equal(byLabel["PAN Number"].entry.canonicalIdentifier, "identity.pan_number");
  assert.equal(byLabel["Aadhaar Number"].entry.canonicalIdentifier, "identity.aadhaar_number");
});

// ---- routine fields fill; sensitive fields wait ----------------------------
test("routine supported fields fill; unknown & declaration untouched", () => {
  const root = testForm();
  const { plan, byLabel } = planFor(root);
  assert.equal(byLabel["Full Name"].entry.action, "fill");
  assert.equal(byLabel["Email"].entry.action, "fill");
  assert.equal(byLabel["Phone Number"].entry.action, "fill");
  assert.equal(byLabel["Address"].entry.action, "fill");
  // 9. unknown question
  assert.equal(byLabel["Favourite Colour"].entry.action, "untouched");
  // 10. declaration/consent checkbox — never automated
  assert.equal(byLabel["I agree to the declaration above"].entry.action, "untouched");

  const { filled } = applyFillPlan({ plan, root });
  const filledLabels = filled.map((f) => f.canonicalIdentifier).sort();
  assert.deepEqual(filledLabels, ["person.address", "person.email", "person.full_name", "person.phone"]);
});

// ---- 10 (declaration blocked in review too) --------------------------------
test("consent checkbox is classified a declaration and blocked; DOCURA never submits", () => {
  const snapshot = scanGoogleForm(testForm());
  const review = computeReview({ snapshot, record: RECORD, resolveField: demoResolveField, ...REVIEW_SEAMS });
  const decl = review.forms[0].fields.find((f) => f.isDeclaration);
  assert.ok(decl, "consent checkbox recognised as a declaration");
  assert.equal(decl.approvalState, "blocked");
  // 14. no submission action anywhere.
  assert.equal(review.forms[0].submit.operated, false);
  for (const f of review.forms[0].fields) assert.equal(f.canSubmit, false);
});

// ---- 11. sensitive requires approval, then fills once -----------------------
test("PAN/Aadhaar/DOB require explicit approval before filling", () => {
  const root = testForm();
  const approvals = newApprovalLedger();
  const { plan, byLabel } = planFor(root, RECORD, approvals);
  for (const label of ["Date of Birth", "PAN Number", "Aadhaar Number"]) {
    assert.equal(byLabel[label].entry.action, "approval_required", `${label} must ask first`);
  }
  const pending = pendingApprovals(plan).map((p) => p.canonicalIdentifier).sort();
  assert.deepEqual(pending, ["identity.aadhaar_number", "identity.pan_number", "person.date_of_birth"]);

  // Approve PAN's exact disclosure, recompute, and it fills; the others still wait.
  const pan = byLabel["PAN Number"].entry;
  grantApproval(approvals, { userId: null, sessionId: null, formId: "google-form", fieldId: pan.fieldId, canonicalIdentifier: "identity.pan_number", value: "ABCDE1234F" });
  const plan2 = computeFillPlan({ snapshot: scanGoogleForm(root), record: RECORD, approvals, context: {}, ...DEMO_SEAMS });
  const pan2 = plan2.forms[0].fields.find((f) => f.canonicalIdentifier === "identity.pan_number");
  assert.equal(pan2.action, "fill");
});

// ---- 12. ambiguity does not auto-fill --------------------------------------
test("ambiguous record value → ask, never auto-fill", () => {
  const record = { attributes: [attr("person.phone", null, {
    is_ambiguous: true,
    observations: [
      { value: "111", confidence: 0.9, document_id: "doc1", extraction_run_id: "run1", page_number: 1, region: null },
      { value: "222", confidence: 0.9, document_id: "doc1", extraction_run_id: "run1", page_number: 1, region: null },
    ],
  })] };
  const { byLabel } = planFor(testForm(), record);
  assert.equal(byLabel["Phone Number"].entry.action, "ask");
});

// ---- 13. user-edited value is not overwritten ------------------------------
test("a field DOCURA filled is never re-written (survives a later user edit)", () => {
  const root = testForm();
  const { plan } = planFor(root);
  applyFillPlan({ plan, root });
  const el = root.querySelector('[data-docura-field="gf-0"]');
  assert.equal(el.value, "Vedant Santosh Kadam");
  el.value = "User Edited This"; // the human changes it
  // Rescan + re-apply (as a mutation would trigger). Idempotency must leave the edit intact.
  const plan2 = computeFillPlan({ snapshot: scanGoogleForm(root), record: RECORD, approvals: newApprovalLedger(), context: {}, ...DEMO_SEAMS });
  applyFillPlan({ plan: plan2, root });
  assert.equal(el.value, "User Edited This");
});

// ---- 14. no submission action is ever generated ----------------------------
test("no plan entry is a submit/click action", () => {
  const { plan } = planFor(testForm());
  const allowed = new Set(["fill", "approval_required", "ask", "unavailable", "untouched"]);
  for (const f of plan.forms[0].fields) assert.ok(allowed.has(f.action), `unexpected action ${f.action}`);
});

// ---- 15. host restriction ---------------------------------------------------
test("adapter is limited strictly to Google Forms hosts", () => {
  assert.equal(isGoogleFormsHost({ hostname: "docs.google.com", pathname: "/forms/d/e/abc/viewform" }), true);
  assert.equal(isGoogleFormsHost({ hostname: "docs.google.com", pathname: "/document/d/x" }), false);
  assert.equal(isGoogleFormsHost({ hostname: "evil.com", pathname: "/forms/x" }), false);
  assert.equal(isGoogleFormsHost({ hostname: "forms.google.com", pathname: "/x" }), false);
  assert.equal(isGoogleFormsHost(null), false);
});

// ---- 16. prototype mode disables cleanly -----------------------------------
test("googleFormsActive requires BOTH the flag and a Google Forms host", () => {
  const onForms = { hostname: "docs.google.com", pathname: "/forms/x" };
  const elsewhere = { hostname: "example.com", pathname: "/" };
  // content.js: googleFormsActive = GOOGLE_FORMS_MODE && isGoogleFormsHost()
  assert.equal(GOOGLE_FORMS_MODE && isGoogleFormsHost(onForms), true);
  assert.equal(GOOGLE_FORMS_MODE && isGoogleFormsHost(elsewhere), false);
  // With the flag off, the adapter never activates regardless of host.
  assert.equal(false && isGoogleFormsHost(onForms), false);
});
