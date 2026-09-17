import { test } from "node:test";
import assert from "node:assert/strict";

import { describeField, FormWatcher } from "../src/detect.js";

// M17: value-free semantic label capture. A fake DOM modelling ONLY the surface describeField
// reads (getAttribute, labels, closest, ownerDocument.getElementById/querySelector,
// textContent). Value-free by construction: form controls expose no textContent, and labels
// expose only their own text — so an input's `.value` can never enter the captured metadata.

function makeDoc() {
  const byId = new Map();
  const labelForId = new Map();
  const doc = {
    _register(el) {
      if (el.id) byId.set(el.id, el);
    },
    registerLabelFor(id, el) {
      labelForId.set(id, el);
    },
    getElementById: (id) => byId.get(id) ?? null,
    querySelector: (sel) => {
      const m = /^label\[for="(.+)"\]$/.exec(sel);
      return m ? (labelForId.get(m[1]) ?? null) : null;
    },
  };
  return doc;
}

function labelEl(text) {
  return { tagName: "LABEL", textContent: text };
}

function span(doc, id, text) {
  const el = { id, textContent: text, ownerDocument: doc };
  doc._register(el);
  return el;
}

function input({ doc, type = "text", id, name, attrs = {}, labels, closestLabel } = {}) {
  const bag = { ...attrs };
  if (type) bag.type = type;
  if (name) bag.name = name;
  const el = {
    tagName: "INPUT",
    type,
    id: id ?? null,
    name: name ?? null,
    required: false,
    multiple: false,
    ownerDocument: doc ?? null,
    getAttribute: (k) => (k in bag ? String(bag[k]) : null),
    labels,
    closest: closestLabel !== undefined ? (sel) => (sel === "label" ? closestLabel : null) : undefined,
  };
  if (doc) doc._register(el);
  return el;
}

// Metadata that must NEVER appear on a descriptor.
const FORBIDDEN_KEYS = ["value", "defaultValue", "innerHTML", "outerHTML", "textContent", "nodeValue"];
function assertValueFree(field) {
  for (const k of FORBIDDEN_KEYS) assert.equal(k in field, false, `descriptor must not contain ${k}`);
}

test("A — explicit label[for] via querySelector fallback", () => {
  const doc = makeDoc();
  doc.registerLabelFor("dob", labelEl("Date of Birth"));
  const f = describeField(input({ doc, type: "date", id: "dob" }));
  assert.equal(f.label, "Date of Birth");
  assertValueFree(f);
});

test("A — explicit label via the native labels collection", () => {
  const f = describeField(input({ type: "text", id: "fn", labels: [labelEl("Full Name")] }));
  assert.equal(f.label, "Full Name");
});

test("B — wrapped label, and the nested input's value is NOT captured", () => {
  // A real wrapped label's textContent excludes the input's value; the fake mirrors that.
  const f = describeField(input({ type: "date", closestLabel: labelEl("Date of Birth") }));
  assert.equal(f.label, "Date of Birth");
  assert.ok(!JSON.stringify(f).includes("secret"));
});

test("C — aria-label", () => {
  const f = describeField(input({ type: "date", attrs: { "aria-label": "Date of Birth" } }));
  assert.equal(f.ariaLabel, "Date of Birth");
  assert.equal(f.label, null);
});

test("D — aria-labelledby resolves the referenced element text", () => {
  const doc = makeDoc();
  span(doc, "dob-label", "Date of Birth");
  const f = describeField(input({ doc, type: "date", attrs: { "aria-labelledby": "dob-label" } }));
  assert.equal(f.ariaLabelledBy, "Date of Birth");
});

test("D — aria-labelledby joins multiple referenced elements", () => {
  const doc = makeDoc();
  span(doc, "a", "Date of");
  span(doc, "b", "Birth");
  const f = describeField(input({ doc, type: "date", attrs: { "aria-labelledby": "a b" } }));
  assert.equal(f.ariaLabelledBy, "Date of Birth");
});

test("E — label and aria-label are kept as distinct sources", () => {
  const f = describeField(
    input({ type: "text", labels: [labelEl("Full Name")], attrs: { "aria-label": "Applicant Name" } }),
  );
  assert.equal(f.label, "Full Name");
  assert.equal(f.ariaLabel, "Applicant Name");
});

test("F — placeholder-only", () => {
  const f = describeField(input({ type: "text", attrs: { placeholder: "Enter your name" } }));
  assert.equal(f.placeholder, "Enter your name");
  assert.equal(f.label, null);
  assert.equal(f.ariaLabel, null);
});

test("G — title-only", () => {
  const f = describeField(input({ type: "date", attrs: { title: "Date of Birth" } }));
  assert.equal(f.title, "Date of Birth");
});

test("H — id and name but no label: all semantic label sources are null", () => {
  const f = describeField(input({ type: "text", id: "field7", name: "field7" }));
  assert.equal(f.id, "field7");
  assert.equal(f.name, "field7");
  assert.equal(f.label, null);
  assert.equal(f.ariaLabel, null);
  assert.equal(f.ariaLabelledBy, null);
  assert.equal(f.placeholder, null);
  assert.equal(f.title, null);
});

test("J — unrelated page text never becomes field metadata", () => {
  const doc = makeDoc();
  span(doc, "page-heading", "Welcome to the Application Portal"); // unrelated
  const f = describeField(input({ doc, type: "text", id: "field8", name: "field8" }));
  assert.equal(f.label, null);
  assert.equal(f.ariaLabelledBy, null);
  assert.ok(!JSON.stringify(f).includes("Welcome to the Application Portal"));
});

test("whitespace in labels is normalised", () => {
  const f = describeField(input({ type: "text", labels: [labelEl("  Full   Name \n")] }));
  assert.equal(f.label, "Full Name");
});

test("a password field is described value-free and captures no contents", () => {
  const f = describeField(input({ type: "password", id: "pw", name: "pw", attrs: { "aria-label": "Password" } }));
  assert.equal(f.type, "password");
  assertValueFree(f);
  assert.ok(!JSON.stringify(f).includes("hunter2"));
});

test("I — a dynamically inserted labelled field gets its label; removed fields drop out", () => {
  let controls = [];
  const root = { querySelectorAll: () => controls };
  let fire;
  const observer = { observe() {}, disconnect() {} };
  const w = new FormWatcher({ root, onChange: () => {}, observerFactory: (cb) => { fire = cb; return observer; } }).start();

  // Insert a labelled field dynamically, then fire the observer callback (a DOM mutation).
  controls = [input({ type: "date", id: "dob", labels: [labelEl("Date of Birth")] })];
  fire();
  const fields = w.latest.forms[0].fields;
  assert.equal(fields[0].label, "Date of Birth");

  // Remove it — it must not remain as a stale detected field.
  controls = [];
  fire();
  assert.equal(w.latest.forms.length, 0);
});
