// The single source of truth for where the bearer token lives on the client.
//
// APP-1 decision: token in localStorage (matches how the extension holds a bearer
// token; the backend has no httpOnly-cookie/refresh flow to restore a session on
// reload). Kept behind these helpers so the storage choice is changeable in one place
// and never read by string key elsewhere. Wrapped in try/catch: storage can be
// unavailable (private mode, disabled site data) and must never crash the app.

const TOKEN_KEY = "docura.token";

export function readToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function writeToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* storage unavailable; the in-memory session still works for this tab */
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* nothing to clear if storage is unavailable */
  }
}
