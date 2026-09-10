# DOCURA Browser Extension — M2 (Core)

The real DOCURA extension for a Chromium desktop browser (Chrome/Edge). This milestone
implements **only** the extension *core*: explicit activation, a persistent active
indicator, and user-controlled stop. It does **not** detect forms, interpret fields,
fill anything, match documents, approve, review, or run any OCR/LLM — those are later
milestones. In M2 the extension **reads no page content at all**.

## What it does

- Signs in with the **existing** DOCURA account (`POST /auth/login`) — there is no
  second user system. The bearer token is the same one any client gets.
- On **explicit activation**, opens an M1 form session (`POST /form-sessions`) and shows
  a persistent green banner on the page plus an `ON` toolbar badge.
- On **stop**, ends the session (`POST /form-sessions/{id}/stop`) and removes the
  indicator. Already-present page values are left untouched (nothing was ever filled).

## Trust boundary (important)

- **The token lives only in `chrome.storage.session`** — in-memory, cleared when the
  browser closes, never written to disk, and **not reachable by web pages or by the
  injected content script**. It is never placed in `localStorage` or
  `chrome.storage.local`. See the comment block in `src/background.js`.
- **Nothing runs on any page passively.** There is no `content_scripts` entry in
  `manifest.json`. The indicator (`src/content.js`) is injected via `chrome.scripting`
  **only on activation**, using the `activeTab` permission (granted for the current tab
  only, only because the user invoked the action). This is BR-014 / FR-EXT-003/004 by
  construction, not by a runtime check that could be forgotten.
- The backend is the **single source of truth** for session lifecycle. The extension
  stores only `{ token, sessionId, tabId }`.

## Load it (unpacked)

1. Start the backend: from `backend/`, run the app on `http://127.0.0.1:8000`
   (the URL in `src/config.js` and `manifest.json` `host_permissions`).
2. In Chrome/Edge open `chrome://extensions`, enable **Developer mode**,
   click **Load unpacked**, and choose this `extension/` folder.

## Tests

```
cd extension
node --test          # or: npm test
```

No dependencies — the tests use Node's built-in runner with hand-written fakes for the
Chrome and fetch APIs. They cover the activation/stop gates, fail-toward-inaction, and
the guarantee that no page content is stored.
