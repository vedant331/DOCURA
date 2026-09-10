// DocuraController — the extension's entire state machine, kept free of Chrome APIs
// so it is unit-testable with plain fakes.
//
// It reuses M1 as the single source of truth for session lifecycle: the backend owns
// whether a form session is active, handed back, or stopped. The extension stores
// only the *minimum* needed to function — a bearer token and, while active, the pair
// { sessionId, tabId } — and nothing else. It never reads or stores page content.
//
// States, derived not stored:
//   signed_out  — no token.
//   inactive    — signed in, no active form session. Nothing runs on any page.
//   active       — a form session exists; the indicator is injected on its tab.
//
// The gates are the point of this milestone:
//   * no token            → activation does nothing (fail toward inaction, BR-016).
//   * backend throws      → no page action is taken (do nothing on an unreachable
//                            backend or a stale token; never continue silently).
//   * after stop           → the session is cleared, so any later action is a no-op
//                            until the user activates again (BR-014: fresh activation).
//
// Injected deps:
//   base      — backend base URL.
//   api       — the module in ./api.js (login/me/logout/createSession/stopSession).
//   storage   — { load(): state, save(patch), clear() } over chrome.storage.session.
//   injector  — { inject(tabId), remove(tabId) } — mounts/removes the page indicator.
//   badge     — { setActive(), clear() } — the toolbar indicator.
//   fetchImpl — passed through to `api` (defaults to global fetch).

const EMPTY = { token: null, expiresAt: null, userEmail: null, session: null };

export class DocuraController {
  constructor({ base, api, storage, injector, badge, fetchImpl }) {
    this.base = base;
    this.api = api;
    this.storage = storage;
    this.injector = injector;
    this.badge = badge;
    this.fetchImpl = fetchImpl;
  }

  async _state() {
    return { ...EMPTY, ...(await this.storage.load()) };
  }

  static _describe(state, extra = {}) {
    let status = "signed_out";
    if (state.token) status = state.session ? "active" : "inactive";
    return {
      status,
      userEmail: state.userEmail ?? null,
      sessionId: state.session?.sessionId ?? null,
      ...extra,
    };
  }

  async getState() {
    return DocuraController._describe(await this._state());
  }

  async signIn(email, password) {
    const result = await this.api.login(this.base, { email, password }, this.fetchImpl);
    const next = {
      token: result.access_token,
      expiresAt: result.expires_at ?? null,
      userEmail: result.user?.email ?? email,
      session: null,
    };
    await this.storage.save(next);
    return DocuraController._describe(next);
  }

  // Explicit activation on one tab (FR-INT-001, BR-014). Reads no page content; the
  // only side effect on the page is the injected indicator.
  async activate(tabId) {
    const state = await this._state();
    if (!state.token) {
      // Never act without an authenticated account (fail toward inaction).
      return DocuraController._describe(state, { error: "Sign in to DOCURA first." });
    }
    if (state.session) {
      // Already active; do not open a second session.
      return DocuraController._describe(state);
    }

    let session;
    try {
      session = await this.api.createSession(this.base, state.token, this.fetchImpl);
    } catch (error) {
      // Backend unreachable or token stale: take no page action at all.
      return DocuraController._describe(state, { error: error.message });
    }

    const next = { ...state, session: { sessionId: session.id, tabId } };
    await this.storage.save(next);

    try {
      await this.injector.inject(tabId);
    } catch (error) {
      // The indicator could not be mounted. An active backend session with no visible
      // indicator would violate FR-EXT-005, so undo: stop the session and go inactive.
      await this._teardown(state.token, session.id, tabId);
      await this.storage.save({ ...state, session: null });
      return DocuraController._describe(state, { error: `Could not activate: ${error.message}` });
    }

    await this.badge.setActive();
    return DocuraController._describe(next);
  }

  // User-controlled stop (FR-EXT-006). Ends the backend session and removes every
  // trace of extension activity from the page. Already-present page values are left
  // untouched — the extension never placed any (fill is a later milestone).
  async stop() {
    const state = await this._state();
    if (!state.session) {
      return DocuraController._describe(state);
    }
    const { sessionId, tabId } = state.session;

    let error = null;
    try {
      await this.api.stopSession(this.base, state.token, sessionId, this.fetchImpl);
    } catch (backendError) {
      // The backend session may linger, but the extension must still go inactive:
      // stopping locally is the fail-toward-inaction outcome, never "keep running".
      error = `Session stop could not be confirmed with the backend; DOCURA is now inactive.`;
      void backendError;
    }

    await this._teardown(state.token, sessionId, tabId);
    const next = { ...state, session: null };
    await this.storage.save(next);
    return DocuraController._describe(next, error ? { error } : {});
  }

  // Sign out: end any active session, revoke the token server-side, and forget
  // everything. A subsequent action finds no token and does nothing.
  async signOut() {
    const state = await this._state();
    if (state.session) await this.stop();
    if (state.token) {
      try {
        await this.api.logout(this.base, state.token, this.fetchImpl);
      } catch {
        /* best-effort revocation; the token is being discarded regardless */
      }
    }
    await this.storage.clear();
    return DocuraController._describe(EMPTY);
  }

  // The tab hosting the active session went away: treat it as a stop so nothing
  // lingers (EC-017/EC-018 shape — cease activity, leave the page alone).
  async handleTabClosed(tabId) {
    const state = await this._state();
    if (state.session && state.session.tabId === tabId) {
      await this.stop();
    }
  }

  async _teardown(token, sessionId, tabId) {
    // Remove the indicator and clear the toolbar badge. Both are best-effort: a tab
    // that is already gone cannot be un-injected, and that is fine.
    try {
      await this.injector.remove(tabId);
    } catch {
      /* tab closed or navigated; nothing to remove */
    }
    try {
      await this.badge.clear();
    } catch {
      /* badge clear never fails in practice */
    }
    void token;
    void sessionId;
  }
}
