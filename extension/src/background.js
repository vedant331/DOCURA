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

async function activeTabId() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.id;
}

// Popup commands. Each resolves to a state descriptor the popup renders.
async function handle(message) {
  switch (message?.type) {
    case "getState":
      return controller.getState();
    case "signIn":
      return controller.signIn(message.email, message.password);
    case "signOut":
      return controller.signOut();
    case "activate": {
      const tabId = await activeTabId();
      if (tabId === undefined) return controller.getState().then((s) => ({ ...s, error: "No active tab." }));
      return controller.activate(tabId);
    }
    case "stop":
      return controller.stop();
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
  void controller.handleTabClosed(tabId);
});
