import { test } from "node:test";
import assert from "node:assert/strict";

import { computeRetrieval, askForAttribute } from "../src/retrieval.js";
import { FormWatcher } from "../src/detect.js";

// ---- helpers ---------------------------------------------------------------
// A field descriptor as M3's describeField produces it (metadata only, never a value).
function field({ fieldId = "f", type = "text", required = false } = {}) {
  return { fieldId, type, required, constraints: {} };
}

function snapshot(fields, { formId = "app", standalone = false } = {}) {
  return { forms: [{ formId, standalone, fields }], formCount: standalone ? 0 : 1 };
}

// The AttributeRecordResponse shape from GET /record/attributes (see backend schemas/record.py).
function record(attributes) {
  return { attributes, count: attributes.length };
}

// One SupportingObservationResponse. document_id is the only knob that splits ambiguous/conflict.
function obs({ value, documentId = "doc-1", confidence = null, page = 1 } = {}) {
  return {
    value,
    confidence,
    document_id: documentId,
    extraction_run_id: "run-1",
    page_number: page,
    region: null,
  };
}

// Maps only the one approved concept — supplied by the *test*, never by production.
const resolveFullName = (f) => (f.fieldId === "full_name" ? "person.full_name" : null);
const byFieldId = (r) => Object.fromEntries(r.forms[0].fields.map((f) => [f.fieldId, f]));

// 1. One supported canonical attribute with exactly one value → available.
test("one defensible value → available (present, not filled)", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    record: record([
      { canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false, observations: [obs({ value: "Asha Rao" })] },
    ]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "available");
  assert.equal(f.value, "Asha Rao");
  assert.equal(f.requiresUser, false);
  assert.equal(r.summary.available, 1);
});

// 2. Provenance is preserved on an available value.
test("available value preserves source/provenance", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    record: record([
      { canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false, observations: [obs({ value: "Asha Rao", documentId: "doc-9", page: 3 })] },
    ]),
    resolveField: resolveFullName,
  });
  const p = byFieldId(r).full_name.candidates[0].provenance[0];
  assert.equal(p.documentId, "doc-9");
  assert.equal(p.pageNumber, 3);
  assert.equal(p.extractionRunId, "run-1");
});

// 3. Multiple candidate values from ONE source → ambiguous + requiresUser (BR-003).
test("multiple reasonable values from one document → ambiguous + requiresUser", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    record: record([
      {
        canonical_identifier: "person.full_name",
        value: null, // backend withholds a value when observations disagree
        is_ambiguous: true,
        observations: [obs({ value: "Asha Rao", documentId: "doc-1" }), obs({ value: "A. Rao", documentId: "doc-1" })],
      },
    ]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "ambiguous");
  assert.equal(f.requiresUser, true);
  assert.equal(f.candidates.length, 2);
  assert.equal("value" in f, false); // no single value selected
});

// 4. Ambiguous candidates each retain source/provenance.
test("ambiguous candidates retain per-candidate provenance", () => {
  const [c1, c2] = askForAttribute({
    canonicalIdentifier: "person.full_name",
    attribute: {
      canonical_identifier: "person.full_name",
      value: null,
      is_ambiguous: true,
      observations: [obs({ value: "Asha Rao", documentId: "doc-1", page: 1 }), obs({ value: "A. Rao", documentId: "doc-1", page: 2 })],
    },
  }).candidates;
  assert.equal(c1.provenance[0].pageNumber, 1);
  assert.equal(c2.provenance[0].pageNumber, 2);
});

// 5. Conflicting values across TWO documents → conflict + requiresUser (BR-004).
test("documents disagree (>=2 docs) → conflict + requiresUser", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    record: record([
      {
        canonical_identifier: "person.full_name",
        value: null,
        is_ambiguous: true,
        observations: [obs({ value: "Asha Rao", documentId: "passport" }), obs({ value: "Asha K Rao", documentId: "licence" })],
      },
    ]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "conflict");
  assert.equal(f.requiresUser, true);
  assert.equal(f.candidates.length, 2);
  assert.match(f.reason, /disagree/i);
});

// 6. No candidate on record → unavailable/unknown.
test("no record value → unavailable; required field still requires the user", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name", required: true })]),
    record: record([]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "unavailable");
  assert.equal(f.requiresUser, true); // required + no value
  assert.equal(f.candidates.length, 0);
});

// 7. No guessing: unavailable/unknown carry no value and no candidates.
test("no guessing — unavailable and unknown never carry a value", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name" }), field({ fieldId: "mystery" })]),
    record: record([]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r);
  assert.equal("value" in f.full_name, false);
  assert.equal(f.full_name.candidates.length, 0);
  assert.equal(f.mystery.status, "unknown");
  assert.equal("value" in f.mystery, false);
});

// 8. No recency/preference resolution: ambiguity is never collapsed to a "best" candidate,
// and candidate order follows the backend's given order (not sorted by any metric).
test("ambiguity is not resolved by recency/preference/ordering", () => {
  const attribute = {
    canonical_identifier: "person.full_name",
    value: null,
    is_ambiguous: true,
    observations: [obs({ value: "First", documentId: "a", confidence: 0.1 }), obs({ value: "Second", documentId: "b", confidence: 0.99 })],
  };
  const d = askForAttribute({ canonicalIdentifier: "person.full_name", attribute });
  assert.equal(d.status, "conflict");
  assert.equal("value" in d, false); // higher-confidence "Second" was NOT selected
  assert.equal(d.candidates[0].value, "First"); // order preserved, not re-ranked by confidence
});

// 9. User-scoped retrieval: reads only the record it is handed. A mapped id absent from the
// (already user-scoped) record is unavailable — never borrowed from another attribute/account.
test("retrieval reflects only the record it is given (user isolation)", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    record: record([
      { canonical_identifier: "person.postal_address", value: "elsewhere", is_ambiguous: false, observations: [obs({ value: "elsewhere" })] },
    ]),
    resolveField: resolveFullName,
  });
  assert.equal(byFieldId(r).full_name.status, "unavailable");
});

// 10. Unsupported/unmapped field stays unknown with a null identifier (production resolver).
test("unmapped field is 'unknown' with no invented identifier", () => {
  const r = computeRetrieval({
    snapshot: snapshot([field({ fieldId: "full_name", required: true }), field({ fieldId: "proof", type: "file" })]),
    // default resolveField = noApprovedFieldMapping → maps nothing, ignores any record.
    record: record([
      { canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false, observations: [obs({ value: "Asha Rao" })] },
    ]),
  });
  const f = byFieldId(r);
  assert.equal(f.full_name.status, "unknown");
  assert.equal(f.full_name.canonicalIdentifier, null);
  assert.equal(f.full_name.requiresUser, true); // required + unknown
  assert.equal(r.summary.unknown, 2);
});

// 11. M5 never mutates the record it is handed (frozen input still computes).
test("computing retrieval does not mutate the record", () => {
  const src = record([
    { canonical_identifier: "person.full_name", value: null, is_ambiguous: true, observations: [obs({ value: "A", documentId: "d1" }), obs({ value: "B", documentId: "d2" })] },
  ]);
  const before = structuredClone(src);
  computeRetrieval({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: src, resolveField: resolveFullName });
  assert.deepEqual(src, before);
  Object.freeze(src);
  Object.freeze(src.attributes);
  for (const a of src.attributes) { Object.freeze(a); Object.freeze(a.observations); }
  assert.doesNotThrow(() =>
    computeRetrieval({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: src, resolveField: resolveFullName }),
  );
});

// 12. M5 never mutates DOM/form values — it is a pure function with no DOM handle at all.
// (Structural guarantee: the module imports nothing from the DOM and returns a plain result.)
test("retrieval produces only a plain data result, touching no DOM/form value", () => {
  const controls = [{ tagName: "INPUT", type: "text", id: "full_name", name: "full_name", required: false, form: null, getAttribute: () => null }];
  const r = computeRetrieval({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: record([]), resolveField: resolveFullName });
  assert.equal(typeof r, "object");
  assert.equal("value" in byFieldId(r).full_name, false); // nothing to write back into a field
  void controls;
});

// 13. An inactive page (watcher never started) performs no retrieval.
test("an unstarted watcher (inactive page) computes no retrieval", () => {
  const store = {};
  new FormWatcher({
    root: { querySelectorAll: () => [] },
    onChange: (result) => (store.retrieval = computeRetrieval({ snapshot: result })),
  });
  assert.equal("retrieval" in store, false); // no start() → content.js never injected
});

// 14. A stopped session clears/stops M5 processing (mirrors content.js teardown wiring).
test("after stop, a later mutation produces no new retrieval; teardown clears it", () => {
  const store = { retrieval: undefined };
  const controls = [{ tagName: "INPUT", type: "text", id: null, name: "a", required: false, form: null, getAttribute: () => null }];
  const obsRef = { cb: null };
  const factory = (cb) => ((obsRef.cb = cb), { observe() {}, disconnect() {} });
  const w = new FormWatcher({
    root: { querySelectorAll: () => controls },
    onChange: (result) => (store.retrieval = computeRetrieval({ snapshot: result })),
    observerFactory: factory,
  }).start();
  assert.equal(store.retrieval.summary.total, 1); // computed while active

  w.stop();
  const teardown = () => (store.retrieval = null); // content.js sets __docuraRetrieval = null
  teardown();
  store.retrieval = "UNCHANGED";
  obsRef.cb(); // a late mutation after stop
  assert.equal(store.retrieval, "UNCHANGED"); // stopped session computed nothing further
});
