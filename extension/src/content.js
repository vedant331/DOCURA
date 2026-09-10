// The active indicator (FR-EXT-005) and, in M3, the form-detection watcher. Both run
// ONLY because activation injected this script on one tab — there is still no
// `content_scripts` entry in the manifest, so nothing runs on any page passively
// (FR-EXT-003/004, BR-014). No detection happens on a non-activated page.
//
// M3 reads form *structure* only (see detect.js): no field values, no transmission
// to the backend, no autofill, no interpretation.
(() => {
  const ID = "docura-active-indicator";
  if (document.getElementById(ID)) return; // idempotent: activation injects once.

  const banner = document.createElement("div");
  banner.id = ID;
  banner.setAttribute("role", "status");
  banner.setAttribute("aria-live", "polite");
  banner.textContent = "● DOCURA is active on this page";
  // Styles are inline so the page's own CSS cannot hide or restyle the indicator.
  Object.assign(banner.style, {
    position: "fixed",
    top: "0",
    left: "0",
    right: "0",
    zIndex: "2147483647", // max — above page content.
    margin: "0",
    padding: "8px 12px",
    font: "600 13px/1.4 system-ui, -apple-system, Segoe UI, sans-serif",
    color: "#ffffff",
    background: "#0b6b3a",
    textAlign: "center",
    letterSpacing: "0.02em",
    boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
    pointerEvents: "none", // never intercepts the user's interaction with the page.
  });
  document.documentElement.appendChild(banner);

  // Form detection (M3). detect.js is loaded as a module (web_accessible_resources)
  // so its logic stays a single, unit-tested source of truth. It runs in this
  // isolated world; the watcher scans only the currently-present forms — the
  // foundation for multi-step forms, with no navigation behaviour invented.
  if (globalThis.__docuraWatcher) return; // a watcher is already running on this tab.
  Promise.all([
    import(chrome.runtime.getURL("src/detect.js")),
    import(chrome.runtime.getURL("src/readiness.js")),
    import(chrome.runtime.getURL("src/retrieval.js")),
  ])
    .then(([{ FormWatcher }, { computeReadiness }, { computeRetrieval }]) => {
      if (globalThis.__docuraWatcher) return;
      const watcher = new FormWatcher({
        root: document,
        // Latest snapshot only; stale enumerations are never retained (FR-FRM-007).
        onChange: (result) => {
          globalThis.__docuraForms = result;
          // Deterministic readiness (M4) on the latest snapshot only. No field values are
          // read and nothing is transmitted: with no approved form-field→attribute mapping
          // the default resolver maps nothing, so the record is neither needed nor fetched
          // and no personal data crosses into this world.
          globalThis.__docuraReadiness = computeReadiness({ snapshot: result });
          // Deterministic retrieval + ambiguity/ask (M5) on the same latest snapshot. Same
          // frozen boundary: with no approved mapping the default resolver maps nothing, so no
          // record is fetched and no personal value ever crosses into this world. M5 only
          // surfaces a decision (available/ambiguous/conflict/unavailable) — it never fills.
          globalThis.__docuraRetrieval = computeRetrieval({ snapshot: result });
        },
      }).start();
      globalThis.__docuraWatcher = watcher;
      // Called by background.js on stop/tab-close/sign-out: detection AND readiness cease.
      globalThis.__docuraTeardown = () => {
        watcher.stop();
        globalThis.__docuraWatcher = null;
        globalThis.__docuraForms = null;
        globalThis.__docuraReadiness = null;
        globalThis.__docuraRetrieval = null;
      };
    })
    .catch(() => {
      /* detection module unavailable; the indicator and activation are unaffected */
    });
})();
