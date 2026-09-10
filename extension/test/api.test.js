import { test } from "node:test";
import assert from "node:assert/strict";

import { login, createSession, stopSession, me } from "../src/api.js";

const BASE = "http://backend.test";

// A fetch double: records the last call and returns a canned Response-like object.
function fakeFetch(response) {
  const calls = [];
  const impl = async (url, opts) => {
    calls.push({ url, opts });
    return response;
  };
  impl.calls = calls;
  return impl;
}

function ok(body) {
  return { ok: true, status: 200, json: async () => body };
}
function fail(status, body) {
  return { ok: false, status, json: async () => body };
}

test("login posts credentials to /auth/login and returns the token", async () => {
  const fetchImpl = fakeFetch(ok({ access_token: "tok", user: { email: "a@b.c" } }));
  const result = await login(BASE, { email: "a@b.c", password: "pw" }, fetchImpl);

  const { url, opts } = fetchImpl.calls[0];
  assert.equal(url, "http://backend.test/auth/login");
  assert.equal(opts.method, "POST");
  assert.deepEqual(JSON.parse(opts.body), { email: "a@b.c", password: "pw" });
  assert.equal(result.access_token, "tok");
});

test("createSession calls M1 POST /form-sessions with the bearer token", async () => {
  const fetchImpl = fakeFetch(ok({ id: "sess-1", state: "active" }));
  const session = await createSession(BASE, "tok", fetchImpl);

  const { url, opts } = fetchImpl.calls[0];
  assert.equal(url, "http://backend.test/form-sessions");
  assert.equal(opts.method, "POST");
  assert.equal(opts.headers.Authorization, "Bearer tok");
  assert.equal(session.id, "sess-1");
  // No page content is sent on activation — only the auth header.
  assert.equal(opts.body, undefined);
});

test("stopSession targets the session's stop route", async () => {
  const fetchImpl = fakeFetch(ok({ id: "sess-1", state: "stopped" }));
  await stopSession(BASE, "tok", "sess-1", fetchImpl);
  assert.equal(fetchImpl.calls[0].url, "http://backend.test/form-sessions/sess-1/stop");
});

test("a non-2xx response throws with the backend's detail (so the caller stops)", async () => {
  const fetchImpl = fakeFetch(fail(401, { detail: "Not authenticated" }));
  await assert.rejects(() => me(BASE, "stale", fetchImpl), /Not authenticated/);
});
