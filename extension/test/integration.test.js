import { test } from "node:test";
import assert from "node:assert/strict";

import { scanForms } from "../src/detect.js";
import { computeReadiness } from "../src/readiness.js";
import { computeRetrieval } from "../src/retrieval.js";
import { computeMatching } from "../src/matching.js";
import { computeReview, newApprovalLedger } from "../src/sensitivity.js";

// M9 end-to-end integration for the extension's in-page pipeline, exercised over a DOM
// that mirrors the controlled mock form (test/fixtures/mock-form.html). It composes the
// SAME pure modules content.js wires together and asserts the honest, frozen-safe contract:
//
//   DETECT      — every fillable field of all seven types is enumerated (submit excluded),
//                 with declared constraints and required flags.
//   READINESS   — with no approved form-field→attribute mapping (G-12/G-13) the production
//                 resolver maps nothing, so every field is "unknown" and nothing is satisfied.
//   RETRIEVAL   — likewise every field "unknown"; no value is chosen, nothing is filled.
//   MATCHING    — with no approved matcher/threshold, every file-upload field is "unresolved";
//                 no document is proposed or auto-selected.
//   REVIEW      — nothing is disclosable (no tier), and the submit control is never operated.
//
// This is the safety demonstration M9 can make under the frozen OCR/S-6 and G-12/G-13
// blockers: the pipeline runs end to end and correctly does nothing unsafe. No mapping,
// record, OCR result, match, or approval is invented here.

// ---- DOM fakes mirroring mock-form.html (same surface detect.js reads) ------
function ctrl({ tag = "input", type, id, name, required, form, attrs = {} }) {
  const bag = { ...attrs };
  if (type !== undefined && tag === "input") bag.type = type;
  if (name !== undefined) bag.name = name;
  if (required) bag.required = "";
  return {
    tagName: tag.toUpperCase(),
    type,
    id: id ?? null,
    name,
    required: !!required,
    multiple: false,
    form,
    getAttribute: (k) => (k in bag ? String(bag[k]) : null),
  };
}

function buildMockFormRoot() {
  const form = { id: "mca-mock", getAttribute: (k) => (k === "name" ? "mca-mock" : null) };
  const controls = [
    ctrl({ type: "text", id: "field_text_a", name: "field_text_a", required: true, form, attrs: { maxlength: "64", minlength: "2" } }),
    ctrl({ type: "number", id: "field_number", name: "field_number", form, attrs: { min: "0", max: "100", step: "1" } }),
    ctrl({ type: "date", id: "field_date", name: "field_date", required: true, form, attrs: { min: "1900-01-01", max: "2100-12-31" } }),
    ctrl({ tag: "select", id: "field_select_static", name: "field_select_static", form }),
    ctrl({ type: "radio", name: "field_radio", form }),
    ctrl({ type: "radio", name: "field_radio", form }),
    ctrl({ type: "checkbox", id: "field_checkbox_routine", name: "field_checkbox_routine", form }),
    ctrl({ type: "file", id: "field_file", name: "field_file", required: true, form, attrs: { accept: "application/pdf,image/png,image/jpeg", "data-max-size": "5MB" } }),
    ctrl({ tag: "select", id: "field_select_controller", name: "field_select_controller", form }),
    ctrl({ tag: "select", id: "field_select_dependent", name: "field_select_dependent", form }),
    ctrl({ type: "text", id: "field_ambiguous_1", name: "field_ambiguous", form }),
    ctrl({ type: "text", id: "field_ambiguous_2", name: "field_ambiguous", form }),
    ctrl({ type: "text", id: "field_sensitive_slot", name: "field_sensitive_slot", required: true, form }),
    ctrl({ type: "checkbox", id: "field_declaration", name: "field_declaration", required: true, form }),
    // Non-fillable: must be excluded by detection.
    ctrl({ type: "submit", name: "submit", form }),
  ];
  return { querySelectorAll: () => controls };
}

test("DETECT — all seven field types enumerated, submit excluded, constraints read", () => {
  const snapshot = scanForms(buildMockFormRoot());
  assert.equal(snapshot.forms.length, 1);
  const fields = snapshot.forms[0].fields;

  // 14 fillable fields; the submit control is not a field.
  assert.equal(fields.length, 14);
  assert.ok(fields.every((f) => f.type !== "submit"));

  const types = new Set(fields.map((f) => f.type));
  for (const t of ["text", "number", "date", "select", "radio", "checkbox", "file"]) {
    assert.ok(types.has(t), `missing field type: ${t}`);
  }

  // Declared constraints and required flags are captured, never invented.
  const file = fields.find((f) => f.type === "file");
  assert.equal(file.required, true);
  assert.equal(file.constraints.accept, "application/pdf,image/png,image/jpeg");
  assert.equal(file.constraints.maxSize, "5MB");
  const text = fields.find((f) => f.fieldId === "field_text_a");
  assert.equal(text.constraints.maxLength, 64);
});

test("READINESS — nothing maps, required/file fields require the user, form not ready", () => {
  const snapshot = scanForms(buildMockFormRoot());
  const { summary, forms } = computeReadiness({ snapshot });

  assert.equal(summary.total, 14);
  assert.equal(summary.unknown, 14); // no approved mapping → every field unknown
  assert.equal(summary.available, 0); // nothing can be satisfied from an (empty) record
  assert.ok(summary.documentsRequired >= 1); // the file-upload field
  assert.equal(summary.ready, false);

  // Every field is unmapped and no value was read for any of them.
  for (const f of forms[0].fields) {
    assert.equal(f.canonicalIdentifier, null);
    assert.equal(f.status, "unknown");
  }
});

test("RETRIEVAL — every field unknown; no value chosen, nothing filled", () => {
  const snapshot = scanForms(buildMockFormRoot());
  const { summary, forms } = computeRetrieval({ snapshot });

  assert.equal(summary.total, 14);
  assert.equal(summary.unknown, 14);
  assert.equal(summary.available, 0);
  assert.equal(summary.ambiguous, 0);
  assert.equal(summary.conflict, 0);
  // No decision carries a chosen value — retrieval surfaces, it never fills.
  assert.ok(forms[0].fields.every((f) => f.value === undefined));
});

test("MATCHING — file-upload field is unresolved; no document auto-selected", () => {
  const snapshot = scanForms(buildMockFormRoot());
  const { summary, forms } = computeMatching({ snapshot, documents: [] });

  const uploads = forms[0].fields;
  assert.equal(uploads.length, 1); // only the file field is a matching target
  assert.equal(uploads[0].status, "unresolved");
  assert.equal(uploads[0].requiresUser, true);
  assert.equal(summary.proposable, 0); // nothing proposed
  assert.equal(summary.candidate, 0); // nothing matched
});

test("REVIEW — nothing disclosable and the submit control is never operated", () => {
  const snapshot = scanForms(buildMockFormRoot());
  const approvals = newApprovalLedger();
  const { summary, forms } = computeReview({ snapshot, approvals });

  assert.equal(summary.disclosable, 0); // no tier assigned → nothing disclosable
  assert.equal(summary.approvalRequired, 0); // no sensitive value to approve
  assert.equal(forms[0].submit.operated, false); // DOCURA never submits (BR-008)
});
