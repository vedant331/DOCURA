import { test } from "node:test";
import assert from "node:assert/strict";

import { computeReadiness, noApprovedFieldMapping } from "../src/readiness.js";
import { FormWatcher } from "../src/detect.js";

// ---- helpers ---------------------------------------------------------------
// A field descriptor as M3's describeField produces it (metadata only, never a value).
function field({ fieldId = "f", type = "text", required = false } = {}) {
  return { fieldId, type, required, constraints: {} };
}

function snapshot(fields, { formId = "app", standalone = false } = {}) {
  return { forms: [{ formId, standalone, fields }], formCount: standalone ? 0 : 1 };
}

// The AttributeRecordResponse shape from GET /record/attributes.
function record(attributes) {
  return { attributes, count: attributes.length };
}

// A resolver that maps only the one approved concept — supplied by the *test*, never by
// production (production has no approved mapping). Mirrors what an approved config would do.
const resolveFullName = (f) => (f.fieldId === "full_name" ? "person.full_name" : null);

const byFieldId = (r) => Object.fromEntries(r.forms[0].fields.map((f) => [f.fieldId, f]));

// 1. A form field with a supported available record value → available.
test("mapped field with an available record value is 'available'", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    record: record([{ canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false }]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "available");
  assert.equal(f.canonicalIdentifier, "person.full_name");
  assert.equal(f.requiresUser, false);
  assert.equal(r.summary.available, 1);
});

// 2. A required field with missing record information → missing + requiresUser.
test("required mapped field with no record value is 'missing' and requires the user", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name", required: true })]),
    record: record([]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "missing");
  assert.equal(f.requiresUser, true);
  assert.equal(r.summary.missing, 1);
  assert.equal(r.summary.ready, false);
});

// 3. An optional field with available information → available, no user action.
test("optional mapped field with a value is 'available' and needs no user action", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name", required: false })]),
    record: record([{ canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false }]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "available");
  assert.equal(f.requiresUser, false);
});

// 4. An optional field with missing information → missing, but does NOT require the user.
test("optional mapped field with no value is 'missing' but does not require the user", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name", required: false })]),
    record: record([]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "missing");
  assert.equal(f.requiresUser, false); // optional: not a blocker
});

// 5. Multiple required fields are each classified independently.
test("multiple required fields are classified independently", () => {
  const r = computeReadiness({
    snapshot: snapshot([
      field({ fieldId: "full_name", required: true }),
      field({ fieldId: "email", required: true }), // unmapped
      field({ fieldId: "proof", type: "file", required: true }), // a document
    ]),
    record: record([{ canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false }]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r);
  assert.equal(f.full_name.status, "available");
  assert.equal(f.email.status, "unknown");
  assert.equal(f.proof.isDocument, true);
  assert.equal(f.proof.requiresUser, true); // documents always require the user (no matching)
  assert.equal(r.summary.requiresUser, 2); // email (required+unknown) and proof (document)
  assert.equal(r.summary.documentsRequired, 1);
});

// 6. An unknown/unmapped field → unknown, no invented identifier.
test("a field with no approved mapping is 'unknown' with a null identifier", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "mystery_field" })]),
    record: record([{ canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false }]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).mystery_field;
  assert.equal(f.status, "unknown");
  assert.equal(f.canonicalIdentifier, null);
  assert.equal(r.summary.unknown, 1);
});

// 7. Conflicting record values are surfaced, never silently resolved.
test("an ambiguous record attribute is surfaced as 'conflict', not resolved", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name", required: true })]),
    // Backend marks disagreement with is_ambiguous + value:null (G-20 has no precedence rule).
    record: record([{ canonical_identifier: "person.full_name", value: null, is_ambiguous: true }]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "conflict");
  assert.equal(f.requiresUser, true);
  assert.equal(r.summary.conflict, 1);
});

// 8. Missing/unknown information is never guessed — no value field is ever produced.
test("readiness never invents a value for a missing or unknown field", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "mystery_field" }), field({ fieldId: "full_name" })]),
    record: record([]),
    resolveField: resolveFullName,
  });
  for (const f of r.forms[0].fields) {
    assert.equal("value" in f, false); // the readiness layer holds no value at all
  }
  assert.equal(byFieldId(r).mystery_field.status, "unknown");
  assert.equal(byFieldId(r).full_name.status, "missing");
});

// 9. Readiness does not mutate the source record.
test("computing readiness does not mutate the record it is given", () => {
  const src = record([{ canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false }]);
  const before = structuredClone(src);
  computeReadiness({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: src, resolveField: resolveFullName });
  assert.deepEqual(src, before);
  // Frozen record still computes without throwing (proves no write is attempted).
  Object.freeze(src);
  Object.freeze(src.attributes);
  assert.doesNotThrow(() =>
    computeReadiness({ snapshot: snapshot([field({ fieldId: "full_name" })]), record: src, resolveField: resolveFullName }),
  );
});

// 10. A stopped session performs no further readiness processing.
test("after stop, a later mutation produces no new readiness (integration)", () => {
  // Mirror content.js's wiring: onChange stores readiness computed from the snapshot.
  const store = {};
  const controls = [{ tagName: "INPUT", type: "text", id: null, name: "a", required: false, form: null, getAttribute: () => null }];
  const obs = { cb: null };
  const factory = (cb) => ((obs.cb = cb), { observe() {}, disconnect() {} });
  const w = new FormWatcher({
    root: { querySelectorAll: () => controls },
    onChange: (result) => (store.readiness = computeReadiness({ snapshot: result })),
    observerFactory: factory,
  }).start();
  assert.equal(store.readiness.summary.total, 1); // initial readiness computed while active

  w.stop();
  store.readiness = "UNCHANGED";
  obs.cb(); // a late mutation after stop
  assert.equal(store.readiness, "UNCHANGED"); // stopped session computed nothing further
});

// 11. An inactive page (watcher never started) performs no readiness processing.
test("an unstarted watcher (inactive page) computes no readiness", () => {
  const store = {};
  new FormWatcher({
    root: { querySelectorAll: () => [] },
    onChange: (result) => (store.readiness = computeReadiness({ snapshot: result })),
  });
  // No start() — content.js is never injected on a non-activated page.
  assert.equal("readiness" in store, false);
});

// 12. User isolation: readiness reads only the record it is handed. A field mapped to an
// identifier absent from that (already user-scoped) record is 'missing' — never borrowed
// from anywhere. Readiness performs no fetch and holds no identity, so it cannot reach
// another account's data.
test("readiness only reflects the record it is given (user isolation)", () => {
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name" })]),
    // This account's record simply has no full name.
    record: record([{ canonical_identifier: "person.postal_address", value: "elsewhere", is_ambiguous: false }]),
    resolveField: resolveFullName,
  });
  const f = byFieldId(r).full_name;
  assert.equal(f.status, "missing"); // not "available" from an unrelated attribute
  assert.equal("value" in f, false);
});

// The production resolver maps nothing: every field is unknown until a mapping is approved.
test("the production resolver leaves every field unknown (no invented mapping)", () => {
  assert.equal(noApprovedFieldMapping(field({ fieldId: "full_name" })), null);
  const r = computeReadiness({
    snapshot: snapshot([field({ fieldId: "full_name", required: true }), field({ fieldId: "proof", type: "file" })]),
    record: record([{ canonical_identifier: "person.full_name", value: "Asha Rao", is_ambiguous: false }]),
    // default resolveField = noApprovedFieldMapping
  });
  const f = byFieldId(r);
  assert.equal(f.full_name.status, "unknown"); // not mapped, despite a value existing
  assert.equal(f.full_name.requiresUser, true); // required + not available
  assert.equal(f.proof.requiresUser, true); // document
  assert.equal(r.summary.unknown, 2);
});
