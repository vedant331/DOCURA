import { test } from "node:test";
import assert from "node:assert/strict";

import { scanForms, describeField, FormWatcher } from "../src/detect.js";

// ---- Minimal DOM fakes -----------------------------------------------------
// scanForms/describeField only ever read: tagName, type, id, name, required,
// multiple, getAttribute(), and el.form. We fake exactly that surface — no DOM
// library needed, and every field stays value-free by construction.

function ctrl({ tag = "input", type, id, name, required, multiple, form = null, attrs = {} } = {}) {
  const bag = { ...attrs };
  if (type !== undefined && tag === "input") bag.type = type;
  if (name !== undefined) bag.name = name;
  if (required) bag.required = "";
  if (multiple) bag.multiple = "";
  return {
    tagName: tag.toUpperCase(),
    type,
    id: id ?? null,
    name,
    required: !!required,
    multiple: !!multiple,
    form,
    getAttribute: (k) => (k in bag ? String(bag[k]) : null),
  };
}

function form({ id, name } = {}) {
  return { id: id ?? null, getAttribute: (k) => (k === "name" ? name ?? null : null) };
}

function root(controls) {
  return { querySelectorAll: () => controls };
}

// A fake MutationObserver whose callback we fire on demand.
function fakeObserverFactory() {
  const obs = { observed: null, disconnected: false, cb: null };
  const factory = (cb) => {
    obs.cb = cb;
    return {
      observe: (target, opts) => (obs.observed = { target, opts }),
      disconnect: () => (obs.disconnected = true),
    };
  };
  return { factory, obs };
}

// ---- scanForms / describeField ---------------------------------------------

test("no form present → no forms detected", () => {
  assert.deepEqual(scanForms(root([])), { forms: [], formCount: 0 });
});

test("one form with text/email/date/file fields is enumerated with types", () => {
  const f = form({ id: "signup" });
  const r = root([
    ctrl({ type: "text", name: "full_name", form: f }),
    ctrl({ type: "email", name: "email", form: f }),
    ctrl({ type: "date", name: "dob", form: f }),
    ctrl({ type: "file", name: "proof", form: f }),
    ctrl({ type: "submit", form: f }), // action, not a field
  ]);
  const { forms, formCount } = scanForms(r);
  assert.equal(formCount, 1);
  assert.equal(forms[0].formId, "signup");
  assert.deepEqual(forms[0].fields.map((x) => x.type), ["text", "email", "date", "file"]);
});

test("required vs optional fields are distinguished", () => {
  const f = form({ id: "f" });
  const { forms } = scanForms(root([
    ctrl({ type: "text", name: "a", required: true, form: f }),
    ctrl({ type: "text", name: "b", form: f }),
  ]));
  assert.deepEqual(forms[0].fields.map((x) => x.required), [true, false]);
});

test("aria-required marks a field required", () => {
  const field = describeField(ctrl({ type: "text", name: "a", attrs: { "aria-required": "true" } }));
  assert.equal(field.required, true);
});

test("minlength/maxlength/pattern constraints are captured", () => {
  const field = describeField(ctrl({ type: "text", name: "pin", attrs: { minlength: "4", maxlength: "6", pattern: "\\d+" } }));
  assert.deepEqual(field.constraints, { minLength: 4, maxLength: 6, pattern: "\\d+" });
});

test("file accept, multiple, and declared size attribute are captured", () => {
  const field = describeField(ctrl({ type: "file", name: "doc", multiple: true, attrs: { accept: ".pdf,image/*", "data-max-size": "5242880" } }));
  assert.deepEqual(field.constraints, { accept: ".pdf,image/*", multiple: true, maxSize: "5242880" });
});

test("select/radio/checkbox metadata is captured without option values", () => {
  const sel = describeField(ctrl({ tag: "select", name: "country", multiple: true }));
  assert.equal(sel.type, "select");
  assert.equal(sel.constraints.multiple, true);
  assert.equal("value" in sel, false); // no value ever captured

  assert.equal(describeField(ctrl({ type: "radio", name: "g" })).type, "radio");
  assert.equal(describeField(ctrl({ type: "checkbox", name: "agree" })).type, "checkbox");
});

test("field identifier prefers id, falls back to name, else null", () => {
  assert.equal(describeField(ctrl({ type: "text", id: "x", name: "y" })).fieldId, "x");
  assert.equal(describeField(ctrl({ type: "text", name: "y" })).fieldId, "y");
  assert.equal(describeField(ctrl({ type: "text" })).fieldId, null); // never fabricated
});

test("hidden and button controls are not treated as fillable fields", () => {
  assert.equal(describeField(ctrl({ type: "hidden", name: "csrf" })), null);
  assert.equal(describeField(ctrl({ type: "button" })), null);
});

test("controls outside any <form> are reported as a standalone group", () => {
  const { forms, formCount } = scanForms(root([ctrl({ type: "text", name: "loose" })]));
  assert.equal(formCount, 0);
  assert.equal(forms[0].standalone, true);
  assert.equal(forms[0].fields.length, 1);
});

// ---- FormWatcher: activation → detect → re-scan → stop ----------------------

test("starting the watcher performs an initial detection", () => {
  const f = form({ id: "f" });
  const controls = [ctrl({ type: "text", name: "a", form: f })];
  const seen = [];
  const { factory } = fakeObserverFactory();
  const w = new FormWatcher({ root: root(controls), onChange: (r) => seen.push(r), observerFactory: factory }).start();
  assert.equal(seen.length, 1);
  assert.equal(w.latest.formCount, 1);
});

test("a dynamically inserted field is picked up on the next scan", () => {
  const f = form({ id: "f" });
  const controls = [ctrl({ type: "text", name: "a", form: f })];
  const { factory, obs } = fakeObserverFactory();
  const w = new FormWatcher({ root: root(controls), observerFactory: factory }).start();
  assert.equal(w.latest.forms[0].fields.length, 1);

  controls.push(ctrl({ type: "email", name: "b", form: f })); // field added after load
  obs.cb(); // MutationObserver fires
  assert.deepEqual(w.latest.forms[0].fields.map((x) => x.name), ["a", "b"]);
});

test("a removed/replaced field leaves no stale mapping", () => {
  const f = form({ id: "f" });
  const controls = [ctrl({ type: "text", name: "a", form: f }), ctrl({ type: "text", name: "b", form: f })];
  const { factory, obs } = fakeObserverFactory();
  const w = new FormWatcher({ root: root(controls), observerFactory: factory }).start();

  controls.shift(); // "a" removed
  obs.cb();
  assert.deepEqual(w.latest.forms[0].fields.map((x) => x.name), ["b"]); // "a" is gone, not stale
});

test("a structure change triggers a fresh detection with reason 'mutation'", () => {
  const reasons = [];
  const { factory, obs } = fakeObserverFactory();
  const controls = [ctrl({ type: "text", name: "a" })];
  new FormWatcher({ root: root(controls), onChange: (_r, why) => reasons.push(why), observerFactory: factory }).start();
  obs.cb();
  assert.deepEqual(reasons, ["initial", "mutation"]);
});

test("stop disconnects the observer and prevents further detection", () => {
  const seen = [];
  const { factory, obs } = fakeObserverFactory();
  const controls = [ctrl({ type: "text", name: "a" })];
  const w = new FormWatcher({ root: root(controls), onChange: (r) => seen.push(r), observerFactory: factory }).start();
  assert.equal(seen.length, 1);

  w.stop();
  assert.equal(obs.disconnected, true);
  obs.cb(); // a late mutation event after stop
  assert.equal(seen.length, 1); // no further detection happened
  assert.equal(w.rescan("mutation"), null); // stopped session processes nothing
});

test("an unstarted watcher performs no detection (inactive page)", () => {
  const seen = [];
  new FormWatcher({ root: root([ctrl({ type: "text" })]), onChange: (r) => seen.push(r) });
  // No start() — as on a non-activated page, where content.js is never injected.
  assert.deepEqual(seen, []);
});
