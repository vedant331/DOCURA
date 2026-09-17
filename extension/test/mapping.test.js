import { test } from "node:test";
import assert from "node:assert/strict";

import { resolveField, fieldAutomation, MAPPING_VERSION } from "../src/mapping.js";

// Controlled-form policy + resolution bridge. The frozen controlled fields resolve exactly;
// every other field's MEANING comes from the generic interpreter (interpret.js, M16) — but its
// automation POLICY is null, so interpretation alone never authorises a fill (M16 §8).

test("the approved full-name field resolves to person.full_name (auto)", () => {
  assert.equal(resolveField({ id: "full_name", name: "full_name", type: "text" }), "person.full_name");
  assert.equal(fieldAutomation({ id: "full_name", type: "text" }), "auto");
});

test("the sensitive full-name field resolves to person.full_name (approval)", () => {
  assert.equal(resolveField({ id: "sensitive_full_name", type: "text" }), "person.full_name");
  assert.equal(fieldAutomation({ id: "sensitive_full_name", type: "text" }), "approval");
});

test("the date-of-birth field resolves to person.date_of_birth (approval / consent-gated)", () => {
  // M12-D3: authored attribute, consent-gated by the G-15 default (tier TBD → treated sensitive).
  assert.equal(resolveField({ id: "date_of_birth", type: "date" }), "person.date_of_birth");
  assert.equal(fieldAutomation({ id: "date_of_birth", type: "date" }), "approval");
});

test("an unmapped field resolves to null and has no automation (left untouched)", () => {
  assert.equal(resolveField({ id: "unknown_text", name: "unknown_text", type: "text" }), null);
  assert.equal(fieldAutomation({ id: "unknown_text", type: "text" }), null);
  assert.equal(resolveField({ id: "field_declaration", type: "checkbox" }), null);
});

test("M16: non-controlled fields resolve by normalised alias, but carry NO fill policy", () => {
  // These are not controlled-form ids; the interpreter resolves their MEANING (normalisation
  // + approved aliases), yet the automation policy is null so they are never auto-filled (§8).
  for (const id of ["name", "full-name", "FULL_NAME", "applicant_name"]) {
    assert.equal(resolveField({ id, type: "text" }), "person.full_name", `should interpret ${id}`);
    assert.equal(fieldAutomation({ id, type: "text" }), null, `must have no fill policy: ${id}`);
  }
});

test("no partial/prefix/camelCase/fuzzy match resolves", () => {
  // Normalisation is meaning-preserving, not fuzzy: extra tokens, camelCase, and near-misses
  // must NOT silently resolve to an approved attribute.
  for (const id of ["fullName", "user_full_name", "full_name_of_applicant", "namexyz"]) {
    assert.equal(resolveField({ id, type: "text" }), null, `must not map ${id}`);
  }
});

test("a field with no identifier is not mapped", () => {
  assert.equal(resolveField({ id: null, name: null, type: "text" }), null);
  assert.ok(typeof MAPPING_VERSION === "string");
});
