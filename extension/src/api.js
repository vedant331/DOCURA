// The extension's whole conversation with the DOCURA backend.
//
// It reuses the *existing* account and session system — there is no second user
// store. Sign-in returns the same bearer token `/auth/login` issues to any client
// (app.api.auth.LoginResponse.access_token); every other call carries it as
// `Authorization: Bearer <token>`, exactly as the backend's own dependency expects.
//
// Every function throws on a non-2xx response or a transport failure. That is
// deliberate: the controller treats a throw as "do nothing" (BR-016, fail toward
// inaction), so a backend that is unreachable or a token that is stale can never be
// silently continued past. `fetch` is a parameter so the tests can drive it without
// a browser.

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` };
}

async function readOrThrow(response) {
  if (!response.ok) {
    // The body is a problem+json document; its `detail` is safe to surface. We do
    // not leak status-specific behaviour beyond that — the caller just stops.
    let detail = `Request failed (${response.status}).`;
    try {
      const body = await response.json();
      if (body && typeof body.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body; keep the generic message */
    }
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

// Sign in and receive the shared session token. Returns { access_token, expires_at, user }.
export async function login(base, { email, password }, fetchImpl = fetch) {
  const response = await fetchImpl(`${base}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return readOrThrow(response);
}

// Confirm the token still names a live account (account sharing check).
export async function me(base, token, fetchImpl = fetch) {
  return readOrThrow(await fetchImpl(`${base}/users/me`, { headers: authHeaders(token) }));
}

// Revoke this session server-side (sign out). Best-effort at the call site.
export async function logout(base, token, fetchImpl = fetch) {
  return readOrThrow(
    await fetchImpl(`${base}/auth/logout`, { method: "POST", headers: authHeaders(token) }),
  );
}

// Explicit activation: open a form session (M1 POST /form-sessions). Sends no page
// content — activation is the only thing being asserted. Returns the FormSession.
export async function createSession(base, token, fetchImpl = fetch) {
  return readOrThrow(
    await fetchImpl(`${base}/form-sessions`, { method: "POST", headers: authHeaders(token) }),
  );
}

// End the session (M1 POST /form-sessions/{id}/stop). The backend records the stop
// in its own audit history; the extension forges nothing.
export async function stopSession(base, token, sessionId, fetchImpl = fetch) {
  return readOrThrow(
    await fetchImpl(`${base}/form-sessions/${sessionId}/stop`, {
      method: "POST",
      headers: authHeaders(token),
    }),
  );
}
