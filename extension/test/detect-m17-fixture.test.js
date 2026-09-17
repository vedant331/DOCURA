import { test } from "node:test";
import assert from "node:assert/strict";

import { describeField } from "../src/detect.js";
import { interpretField } from "../src/interpret.js";

// Pins the EXPECTED detected metadata for test/fixtures/mock-form-m17-labels.html, where the
// meaning of each field lives ONLY in the label / aria-label and the id/name are opaque.
// Models the three fixture fields with the DOM surface describeField reads (value-free).

function labelEl(text) {
  return { tagName: "LABEL", textContent: text };
}

function input({ type = "text", id, name, labels, attrs = {} } = {}) {
  const bag = { ...attrs };
  if (type) bag.type = type;
  if (name) bag.name = name;
  return {
    tagName: "INPUT",
    type,
    id: id ?? null,
    name: name ?? null,
    required: false,
    multiple: false,
    getAttribute: (k) => (k in bag ? String(bag[k]) : null),
    labels,
  };
}

const FORBIDDEN = ["value", "defaultValue", "innerHTML", "outerHTML", "textContent"];
function assertValueFree(f) {
  for (const k of FORBIDDEN) assert.equal(k in f, false, `descriptor must not contain ${k}`);
}

test("fixture: Date of Birth — meaning is in the label, id/name are opaque", () => {
  const f = describeField(input({ type: "date", id: "dob", name: "field_123", labels: [labelEl("Date of Birth")] }));
  assert.deepEqual(
    { fieldRef: f.fieldId, id: f.id, name: f.name, type: f.type, label: f.label, ariaLabel: f.ariaLabel, ariaLabelledBy: f.ariaLabelledBy, placeholder: f.placeholder, title: f.title },
    { fieldRef: "dob", id: "dob", name: "field_123", type: "date", label: "Date of Birth", ariaLabel: null, ariaLabelledBy: null, placeholder: null, title: null },
  );
  assertValueFree(f);
  assert.equal(interpretField(f).canonicalIdentifier, "person.date_of_birth"); // meaning from the label
});

test("fixture: Full Name — meaning is in the label, id/name are opaque", () => {
  const f = describeField(input({ type: "text", id: "name", name: "field_456", labels: [labelEl("Full Name")] }));
  assert.deepEqual(
    { fieldRef: f.fieldId, id: f.id, name: f.name, type: f.type, label: f.label, ariaLabel: f.ariaLabel, ariaLabelledBy: f.ariaLabelledBy, placeholder: f.placeholder, title: f.title },
    { fieldRef: "name", id: "name", name: "field_456", type: "text", label: "Full Name", ariaLabel: null, ariaLabelledBy: null, placeholder: null, title: null },
  );
  assertValueFree(f);
  assert.equal(interpretField(f).canonicalIdentifier, "person.full_name");
});

test("fixture: Email Address — accessible name via aria-label only; stays unknown (not released)", () => {
  const f = describeField(input({ type: "text", id: "email_test", name: "field_789", attrs: { "aria-label": "Email Address" } }));
  assert.deepEqual(
    { fieldRef: f.fieldId, id: f.id, name: f.name, type: f.type, label: f.label, ariaLabel: f.ariaLabel, ariaLabelledBy: f.ariaLabelledBy, placeholder: f.placeholder, title: f.title },
    { fieldRef: "email_test", id: "email_test", name: "field_789", type: "text", label: null, ariaLabel: "Email Address", ariaLabelledBy: null, placeholder: null, title: null },
  );
  assertValueFree(f);
  assert.equal(interpretField(f).status, "unknown"); // email is not a released attribute
});
