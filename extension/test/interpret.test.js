import { test } from "node:test";
import assert from "node:assert/strict";

import {
  interpretField,
  normalizeLabel,
  INTERPRETER_METHOD,
  EXACT_ALIAS_CONFIDENCE,
  CONTROLLED_ALIASES,
} from "../src/interpret.js";

// M16 field-interpretation seam. Deterministic alias matching for ONLY the two released
// controlled attributes. UNKNOWN and AMBIGUOUS are first-class; no fuzzy/partial matching;
// no new canonical attributes; value-free (label/name/id only).

const APPROVED_IDS = new Set(["person.full_name", "person.date_of_birth"]);

test("exact approved label resolves to person.full_name", () => {
  const r = interpretField({ label: "Full Name", id: "f1" });
  assert.equal(r.status, "resolved");
  assert.equal(r.canonicalIdentifier, "person.full_name");
  assert.equal(r.confidence, EXACT_ALIAS_CONFIDENCE);
  assert.equal(r.method, INTERPRETER_METHOD);
  assert.equal(r.fieldRef, "f1");
});

test("approved aliases resolve (Applicant Name → full_name; DOB → date_of_birth)", () => {
  assert.equal(interpretField({ label: "Applicant Name" }).canonicalIdentifier, "person.full_name");
  assert.equal(interpretField({ label: "Candidate Name" }).canonicalIdentifier, "person.full_name");
  assert.equal(interpretField({ label: "DOB" }).canonicalIdentifier, "person.date_of_birth");
  assert.equal(interpretField({ label: "Birth Date" }).canonicalIdentifier, "person.date_of_birth");
});

test("case, whitespace, and punctuation are normalised before comparison", () => {
  assert.equal(interpretField({ label: "FULL NAME" }).canonicalIdentifier, "person.full_name");
  assert.equal(interpretField({ label: "  full   name  " }).canonicalIdentifier, "person.full_name");
  assert.equal(interpretField({ label: "Date of Birth" }).canonicalIdentifier, "person.date_of_birth");
  assert.equal(interpretField({ label: "D.O.B." }).canonicalIdentifier, "person.date_of_birth");
  assert.equal(interpretField({ id: "date-of-birth" }).canonicalIdentifier, "person.date_of_birth");
  assert.equal(interpretField({ id: "full_name" }).canonicalIdentifier, "person.full_name");
});

test("unknown label is first-class (status unknown, no guess)", () => {
  const r = interpretField({ label: "Favourite Colour", id: "fav" });
  assert.equal(r.status, "unknown");
  assert.equal(r.canonicalIdentifier, null);
  assert.equal(r.confidence, null);
  assert.deepEqual(r.candidates, []);
});

test("ambiguity is first-class: conflicting signals never auto-choose", () => {
  // Label says full name, id says DOB — two approved meanings, so DOCURA will not choose.
  const r = interpretField({ label: "Full Name", id: "dob" });
  assert.equal(r.status, "ambiguous");
  assert.equal(r.canonicalIdentifier, null);
  assert.equal(r.candidates.length, 2);
  assert.deepEqual([...r.candidates].sort(), ["person.date_of_birth", "person.full_name"]);
});

test("no accidental partial/prefix/fuzzy match", () => {
  for (const label of ["user full name", "full name of applicant", "fullname", "namexyz", "n a m e"]) {
    assert.equal(interpretField({ label }).status, "unknown", `must not match: ${label}`);
  }
});

test("only the two released canonical attributes can ever be returned", () => {
  // Every alias in the table maps to one of exactly two approved ids — nothing else.
  for (const canonical of Object.keys(CONTROLLED_ALIASES)) {
    assert.ok(APPROVED_IDS.has(canonical), `unexpected canonical id in aliases: ${canonical}`);
  }
  // Labels that could tempt a broader vocabulary must stay unknown.
  for (const label of ["Email", "Phone", "Mobile", "Address", "Aadhaar", "PAN", "Gender", "Nationality"]) {
    assert.equal(interpretField({ label }).status, "unknown", `must not introduce attribute for: ${label}`);
  }
});

test("interpretField is value-free: it reads label/name/id and ignores any value", () => {
  const r = interpretField({ label: "Full Name", value: "Priya Sharma", name: "n1" });
  assert.equal(r.canonicalIdentifier, "person.full_name");
  // The interpretation result never carries the value.
  assert.ok(!JSON.stringify(r).includes("Priya Sharma"));
});

test("normalizeLabel: deterministic, meaning-preserving", () => {
  assert.equal(normalizeLabel("  Full_Name "), "full name");
  assert.equal(normalizeLabel("D.O.B."), "d o b");
  assert.equal(normalizeLabel(null), "");
  assert.equal(normalizeLabel(undefined), "");
});
