import { test } from "node:test";
import assert from "node:assert/strict";

import {
  interpretField,
  selectProvider,
  deterministicProvider,
  toProviderMetadata,
  INTERPRETER_METHOD,
} from "../src/interpret.js";

// M18: the provider architecture. `interpretField` selects a provider, runs it defensively,
// and VALIDATES its output against the released vocabulary. A test-only mock provider (defined
// here, never enabled in production) simulates each behaviour a real/future provider might
// exhibit. The wrapper must degrade every unsafe case to a safe UNKNOWN — never a guess.

// ---- test-only mock provider factory (NOT production) ----
function mockProvider(behavior) {
  return {
    name: "mock-provider",
    interpret(metadata) {
      if (typeof behavior === "function") return behavior(metadata);
      return behavior;
    },
  };
}

test("default provider selection is the deterministic alias provider", () => {
  assert.equal(selectProvider(), deterministicProvider);
  // With no provider passed, interpretField uses the deterministic provider (M16/M17 behaviour).
  const r = interpretField({ label: "Full Name" });
  assert.equal(r.status, "resolved");
  assert.equal(r.canonicalIdentifier, "person.full_name");
  assert.equal(r.method, INTERPRETER_METHOD);
});

test("provider: resolved to a released attribute passes validation", () => {
  const r = interpretField({ id: "f" }, {
    provider: mockProvider({ status: "resolved", canonicalIdentifier: "person.date_of_birth", candidates: ["person.date_of_birth"], confidence: 0.8, reason: "m", method: "mock-provider" }),
  });
  assert.equal(r.status, "resolved");
  assert.equal(r.canonicalIdentifier, "person.date_of_birth");
  assert.equal(r.confidence, 0.8);
  assert.equal(r.method, "mock-provider");
});

test("provider: unknown stays unknown", () => {
  const r = interpretField({ id: "f" }, { provider: mockProvider({ status: "unknown" }) });
  assert.equal(r.status, "unknown");
  assert.equal(r.canonicalIdentifier, null);
});

test("provider: ambiguous with two released candidates stays ambiguous, never chosen", () => {
  const r = interpretField({ id: "f" }, {
    provider: mockProvider({ status: "ambiguous", candidates: ["person.full_name", "person.date_of_birth"] }),
  });
  assert.equal(r.status, "ambiguous");
  assert.equal(r.canonicalIdentifier, null);
  assert.deepEqual([...r.candidates].sort(), ["person.date_of_birth", "person.full_name"]);
});

test("provider: unsupported attribute is rejected to unknown (never fill-eligible)", () => {
  for (const id of ["person.email", "person.phone", "person.aadhaar_number", "user.name", "email"]) {
    const r = interpretField({ id: "f" }, {
      provider: mockProvider({ status: "resolved", canonicalIdentifier: id, confidence: 0.99 }),
    });
    assert.equal(r.status, "unknown", `must reject unsupported ${id}`);
    assert.equal(r.canonicalIdentifier, null);
  }
});

test("provider: confidence outside [0,1] (or non-numeric) is rejected to unknown", () => {
  for (const c of [5, -1, Number.NaN, Infinity, "high", null, undefined]) {
    const r = interpretField({ id: "f" }, {
      provider: mockProvider({ status: "resolved", canonicalIdentifier: "person.full_name", confidence: c }),
    });
    assert.equal(r.status, "unknown", `must reject confidence ${String(c)}`);
  }
});

test("provider: malformed output degrades to unknown", () => {
  for (const bad of [null, undefined, 42, "resolved", {}, { status: "weird" }, { status: "resolved" /* no id */ }]) {
    const r = interpretField({ id: "f" }, { provider: mockProvider(bad) });
    assert.equal(r.status, "unknown", `must reject malformed ${JSON.stringify(bad)}`);
  }
});

test("provider: ambiguous with fewer than two supported candidates degrades to unknown", () => {
  const r = interpretField({ id: "f" }, {
    provider: mockProvider({ status: "ambiguous", candidates: ["person.full_name", "person.email"] }),
  });
  assert.equal(r.status, "unknown"); // only one supported candidate survives → do not choose
});

test("provider: a thrown/failed provider degrades to unknown", () => {
  const r = interpretField({ id: "f" }, {
    provider: mockProvider(() => {
      throw new Error("provider exploded");
    }),
  });
  assert.equal(r.status, "unknown");
  assert.ok(!JSON.stringify(r).includes("exploded")); // internal error text is not surfaced
});

test("provider receives METADATA ONLY — never a field value", () => {
  let seen = null;
  const spy = {
    name: "spy",
    interpret(metadata) {
      seen = metadata;
      return { status: "unknown" };
    },
  };
  interpretField(
    { id: "x", name: "y", type: "text", label: "Full Name", value: "SECRET VALUE", defaultValue: "D", password: "p" },
    { provider: spy },
  );
  assert.equal("value" in seen, false);
  assert.equal("defaultValue" in seen, false);
  assert.equal("password" in seen, false);
  assert.equal(seen.label, "Full Name"); // safe metadata is present
  assert.equal(seen.id, "x");
  assert.ok(!JSON.stringify(seen).includes("SECRET VALUE"));
});

test("sensitive value never appears in the interpretation result", () => {
  const r = interpretField(
    { label: "Full Name", value: "Vedant Santosh Kadam" },
    { provider: mockProvider({ status: "resolved", canonicalIdentifier: "person.full_name", confidence: 1 }) },
  );
  assert.equal(r.canonicalIdentifier, "person.full_name");
  assert.ok(!JSON.stringify(r).includes("Vedant Santosh Kadam"));
});

test("toProviderMetadata whitelists safe keys only", () => {
  const m = toProviderMetadata({ id: "a", name: "b", label: "L", value: "v", defaultValue: "d", innerHTML: "<b>" });
  assert.equal("value" in m, false);
  assert.equal("defaultValue" in m, false);
  assert.equal("innerHTML" in m, false);
  assert.equal(m.label, "L");
});
