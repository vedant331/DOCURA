import { test } from "node:test";
import assert from "node:assert/strict";

import { DocuraController } from "../src/session.js";

// ---- Fakes -----------------------------------------------------------------

function fakeStorage() {
  let data = {};
  return {
    async load() {
      return { ...data };
    },
    async save(state) {
      data = { ...data, ...state };
    },
    async clear() {
      data = {};
    },
    _raw: () => data,
  };
}

function fakeApi(overrides = {}) {
  const calls = [];
  const record = (name) => (...args) => {
    calls.push({ name, args });
    const fn = overrides[name];
    if (typeof fn === "function") return fn(...args);
    return Promise.resolve(fn ?? {});
  };
  return {
    calls,
    names: () => calls.map((c) => c.name),
    login: record("login"),
    me: record("me"),
    logout: record("logout"),
    createSession: record("createSession"),
    stopSession: record("stopSession"),
  };
}

function recorder() {
  const events = [];
  return {
    events,
    inject: async (tabId) => void events.push(["inject", tabId]),
    remove: async (tabId) => void events.push(["remove", tabId]),
    setActive: async () => void events.push(["badgeOn"]),
    clear: async () => void events.push(["badgeOff"]),
  };
}

function build(api, opts = {}) {
  const storage = opts.storage ?? fakeStorage();
  const inj = recorder();
  const bad = recorder();
  const controller = new DocuraController({
    base: "http://backend.test",
    api,
    storage,
    injector: { inject: inj.inject, remove: inj.remove },
    badge: { setActive: bad.setActive, clear: bad.clear },
  });
  return { controller, storage, inj, bad };
}

const SIGNED_IN = { token: "tok", userEmail: "a@b.c", session: null };

// ---- Tests -----------------------------------------------------------------

test("a fresh controller is signed out and does nothing on the page", async () => {
  const api = fakeApi();
  const { controller, inj } = build(api);
  assert.equal((await controller.getState()).status, "signed_out");
  assert.deepEqual(inj.events, []); // nothing injected: no page access while inactive.
});

test("activation is refused with no token and makes no backend or page call", async () => {
  const api = fakeApi();
  const { controller, inj } = build(api);

  const state = await controller.activate(7);
  assert.equal(state.status, "signed_out");
  assert.match(state.error, /Sign in/);
  assert.deepEqual(api.names(), []); // no createSession
  assert.deepEqual(inj.events, []); // no injection
});

test("sign in then activate creates a form session, injects the indicator, sets the badge", async () => {
  const api = fakeApi({ login: { access_token: "tok", user: { email: "a@b.c" } }, createSession: { id: "sess-1" } });
  const { controller, storage, inj, bad } = build(api);

  await controller.signIn("a@b.c", "pw");
  const state = await controller.activate(42);

  assert.equal(state.status, "active");
  assert.equal(state.sessionId, "sess-1");
  assert.deepEqual(api.names(), ["login", "createSession"]);
  assert.deepEqual(inj.events, [["inject", 42]]);
  assert.deepEqual(bad.events, [["badgeOn"]]);
  // Only minimal session info is stored — and never page content.
  assert.deepEqual(storage._raw().session, { sessionId: "sess-1", tabId: 42 });
});

test("stop ends the session, removes the indicator, clears the badge, returns to inactive", async () => {
  const storage = fakeStorage();
  await storage.save({ ...SIGNED_IN, session: { sessionId: "sess-1", tabId: 42 } });
  const api = fakeApi({ stopSession: { id: "sess-1", state: "stopped" } });
  const { controller, inj, bad } = build(api, { storage });

  const state = await controller.stop();

  assert.equal(state.status, "inactive");
  assert.deepEqual(api.names(), ["stopSession"]);
  assert.deepEqual(inj.events, [["remove", 42]]);
  assert.deepEqual(bad.events, [["badgeOff"]]);
  assert.equal(storage._raw().session, null);
});

test("after stop, a second stop is a no-op (activity cannot continue)", async () => {
  const storage = fakeStorage();
  await storage.save({ ...SIGNED_IN, session: { sessionId: "sess-1", tabId: 42 } });
  const api = fakeApi({ stopSession: { state: "stopped" } });
  const { controller } = build(api, { storage });

  await controller.stop();
  const again = await controller.stop();
  assert.equal(again.status, "inactive");
  assert.equal(api.calls.filter((c) => c.name === "stopSession").length, 1); // not called twice
});

test("a backend that is unreachable at activation triggers no page action", async () => {
  const storage = fakeStorage();
  await storage.save({ ...SIGNED_IN });
  const api = fakeApi({
    createSession: () => Promise.reject(new Error("backend down")),
  });
  const { controller, inj } = build(api, { storage });

  const state = await controller.activate(9);
  assert.equal(state.status, "inactive");
  assert.match(state.error, /backend down/);
  assert.deepEqual(inj.events, []); // no indicator, no page touch on failure
  assert.equal(storage._raw().session, null);
});

test("stop still deactivates locally even if the backend stop fails (fail toward inaction)", async () => {
  const storage = fakeStorage();
  await storage.save({ ...SIGNED_IN, session: { sessionId: "sess-1", tabId: 42 } });
  const api = fakeApi({ stopSession: () => Promise.reject(new Error("network")) });
  const { controller, inj, bad } = build(api, { storage });

  const state = await controller.stop();
  assert.equal(state.status, "inactive");
  assert.ok(state.error); // the user is told it could not be confirmed
  assert.deepEqual(inj.events, [["remove", 42]]); // indicator removed regardless
  assert.deepEqual(bad.events, [["badgeOff"]]);
  assert.equal(storage._raw().session, null); // never continues on stale session state
});

test("sign out ends an active session, revokes the token, and forgets everything", async () => {
  const storage = fakeStorage();
  await storage.save({ ...SIGNED_IN, session: { sessionId: "sess-1", tabId: 42 } });
  const api = fakeApi({ stopSession: { state: "stopped" }, logout: { revoked: 1 } });
  const { controller } = build(api, { storage });

  const state = await controller.signOut();
  assert.equal(state.status, "signed_out");
  assert.ok(api.names().includes("stopSession"));
  assert.ok(api.names().includes("logout"));
  assert.deepEqual(storage._raw(), {}); // no token, no session, no page content
});

test("closing the activated tab ends the session", async () => {
  const storage = fakeStorage();
  await storage.save({ ...SIGNED_IN, session: { sessionId: "sess-1", tabId: 42 } });
  const api = fakeApi({ stopSession: { state: "stopped" } });
  const { controller, inj } = build(api, { storage });

  await controller.handleTabClosed(42);
  assert.equal(storage._raw().session, null);
  assert.deepEqual(inj.events, [["remove", 42]]);
});

test("no page content is ever stored — storage holds only auth and session ids", async () => {
  const api = fakeApi({ login: { access_token: "tok", user: { email: "a@b.c" } }, createSession: { id: "sess-1" } });
  const { controller, storage } = build(api);

  await controller.signIn("a@b.c", "pw");
  await controller.activate(42);

  const keys = Object.keys(storage._raw());
  assert.deepEqual(new Set(keys), new Set(["token", "expiresAt", "userEmail", "session"]));
  // No key that could hold third-party page content.
  for (const k of keys) assert.doesNotMatch(k, /page|dom|content|html/i);
});
