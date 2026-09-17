// The service worker: the extension's single authority for session state (there is
// no second session system — the backend M1 form session is authoritative, and this
// only holds the token plus { sessionId, tabId } to talk to it). It wires Chrome APIs
// to the pure DocuraController in ./session.js and nothing more.
//
// Trust boundary — read this before changing storage:
//   * The bearer token lives ONLY in chrome.storage.session. That store is in-memory,
//     cleared when the browser closes, never written to disk, and — unlike
//     chrome.storage.local or a page's localStorage — not reachable by web pages or by
//     injected content scripts. The token is therefore never exposed to the third-
//     party page DOCURA is activated on. Do not move it to local/localStorage.
//   * The content script (content.js) runs in an isolated world, is injected only on
//     activation, and is given no token and no page-reading code.

import { API_BASE } from "./config.js";
import * as api from "./api.js";
import { DocuraController } from "./session.js";

const storage = {
  async load() {
    return chrome.storage.session.get(["token", "expiresAt", "userEmail", "session"]);
  },
  async save(state) {
    await chrome.storage.session.set(state);
  },
  async clear() {
    await chrome.storage.session.clear();
  },
};

const injector = {
  async inject(tabId) {
    // activeTab grants access to this one tab only because the user just invoked the
    // action; this is the first and only time DOCURA touches the page.
    await chrome.scripting.executeScript({ target: { tabId }, files: ["src/content.js"] });
  },
  async remove(tabId) {
    await chrome.scripting.executeScript({
      target: { tabId },
      // Stop form observation immediately, then remove the indicator. Both run in the
      // same isolated world content.js used, so the teardown hook is reachable.
      func: () => {
        globalThis.__docuraTeardown?.();
        document.getElementById("docura-active-indicator")?.remove();
      },
    });
  },
};

const badge = {
  async setActive() {
    await chrome.action.setBadgeText({ text: "ON" });
    await chrome.action.setBadgeBackgroundColor({ color: "#0b6b3a" });
  },
  async clear() {
    await chrome.action.setBadgeText({ text: "" });
  },
};

const controller = new DocuraController({ base: API_BASE, api, storage, injector, badge });

// Transient, in-memory list of sensitive fields on the active page awaiting the user's
// explicit approval (M10 §13). Reported by the content script, shown by the popup, never
// persisted and cleared the moment the session ends (BR-007). Holds no raw value.
let pendingApprovals = [];

async function activeTabId() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.id;
}

// The content script (isolated world, NO token) asks the worker to fetch the user's record.
// The token never leaves the worker; only the user's own attribute values return, and only
// while a session is active on this account (M10 §8/§20).
async function fetchRecordForActiveSession() {
  const state = await storage.load();
  if (!state?.token) return { error: "Sign in to DOCURA first." };
  if (!state?.session) return { error: "No active DOCURA session." };
  try {
    return { record: await api.getRecord(API_BASE, state.token) };
  } catch (error) {
    return { error: error.message };
  }
}

// The content script asks the worker to record one in-session action (M15). The token and the
// session id stay in the worker: the content script never sees either. The payload is rebuilt
// from a strict whitelist here, so ONLY contract fields are ever transmitted — a value (or any
// other stray field) added upstream by mistake cannot reach the backend. A failure to record
// is returned, never thrown, and never blocks the underlying (already-safe) action (M15 §7).
async function recordActionForActiveSession(action) {
  const state = await storage.load();
  if (!state?.token || !state?.session) return { error: "No active DOCURA session." };
  const a = action ?? {};
  const payload = {
    action_type: a.action_type,
    outcome: a.outcome,
    field_ref: a.field_ref ?? null,
    document_id: a.document_id ?? null,
    observation_id: a.observation_id ?? null,
    reverses_action_id: a.reverses_action_id ?? null,
    detail: a.detail ?? null,
  };
  try {
    const recorded = await api.recordAction(API_BASE, state.token, state.session.sessionId, payload);
    return { ok: true, id: recorded.id };
  } catch (error) {
    return { error: error.message };
  }
}

// Popup + content-script commands. Each resolves to a response the sender renders/uses.
async function handle(message) {
  switch (message?.type) {
    case "getState":
      return { ...(await controller.getState()), pending: pendingApprovals };
    case "signIn":
      return controller.signIn(message.email, message.password);
    case "signOut":
      pendingApprovals = [];
      return controller.signOut();
    case "activate": {
      const tabId = await activeTabId();
      if (tabId === undefined) return controller.getState().then((s) => ({ ...s, error: "No active tab." }));
      return controller.activate(tabId);
    }
    case "stop":
      pendingApprovals = [];
      return controller.stop();

    // ---- M10 record access + sensitive approval (content ↔ worker ↔ popup) ----
    case "getRecord":
      return fetchRecordForActiveSession();
    case "recordAction":
      return recordActionForActiveSession(message.action);
    case "reportPending":
      // The content script reports which sensitive fields await approval (fieldId/attribute
      // only — never a value). Replaces the list wholesale (latest snapshot only).
      pendingApprovals = Array.isArray(message.pending) ? message.pending : [];
      return { ok: true };
    case "approve": {
      // The user approved one disclosure in the trusted popup. Tell the active tab to grant
      // the exact-scope approval and fill that one field. Approval never leaves this session.
      const state = await storage.load();
      const tabId = state?.session?.tabId;
      if (tabId != null) {
        try {
          await chrome.tabs.sendMessage(tabId, { type: "approveField", fieldId: message.fieldId });
        } catch {
          /* tab gone; nothing to fill */
        }
      }
      pendingApprovals = pendingApprovals.filter((p) => p.fieldId !== message.fieldId);
      return { ...(await controller.getState()), pending: pendingApprovals };
    }
    default:
      return { status: "signed_out", error: "Unknown command." };
  }
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  handle(message).then(sendResponse, (error) => sendResponse({ error: error.message }));
  return true; // keep the channel open for the async response.
});

// If the activated tab closes, end the session so nothing lingers.
chrome.tabs.onRemoved.addListener((tabId) => {
  pendingApprovals = [];
  void controller.handleTabClosed(tabId);
});
