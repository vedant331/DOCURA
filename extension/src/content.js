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
    import(chrome.runtime.getURL("src/sensitivity.js")),
    import(chrome.runtime.getURL("src/matching.js")),
    import(chrome.runtime.getURL("src/autofill.js")),
    import(chrome.runtime.getURL("src/mapping.js")),
    import(chrome.runtime.getURL("src/demo.js")),
  ])
    .then(
      ([
        { FormWatcher },
        { computeReadiness },
        { computeRetrieval },
        { computeReview, newApprovalLedger, grantApproval },
        { computeMatching },
        {
          computeFillPlan,
          applyFillPlan,
          pendingApprovals,
          fillAuditAction,
          approvalRequestAuditAction,
          approvalDecisionAuditAction,
        },
        { resolveField },
        {
          DEMO_MODE,
          demoResolveField,
          demoFieldAutomation,
          isDemoForm,
          demoClassifyTier,
          demoClassifyDeclaration,
        },
      ]) => {
        // DEMO opt-in: when on, the SAME pipeline uses the dynamic demo seams (label-driven
        // interpretation over common attributes). Off by default → production is unchanged.
        const fillSeams = DEMO_MODE
          ? { resolveField: demoResolveField, fieldAutomation: demoFieldAutomation, isEligibleForm: isDemoForm }
          : {};
        const resolveFieldActive = DEMO_MODE ? demoResolveField : resolveField;
        const reviewSeams = DEMO_MODE
          ? { classifyTier: demoClassifyTier, classifyDeclaration: demoClassifyDeclaration }
          : {};
        if (globalThis.__docuraWatcher) return;
        // Session-scoped, in-memory approval ledger (BR-007: never persisted or generalised).
        const approvals = (globalThis.__docuraApprovals = newApprovalLedger());
        // The user's structured record, fetched via the worker (which holds the token). Until it
        // arrives it is null, so nothing is filled. userId/sessionId stay null: the ledger's own
        // lifetime IS the session, so its entries are already session-isolated.
        let record = null;
        let latest = null;
        const context = { userId: null, sessionId: null };

        // Audit (M15): report each real in-session action to the worker, which posts it to the
        // backend with the token + session id it alone holds. `reported` de-duplicates across
        // rescans so one effect is one audit entry. NEVER carries a field value or page content —
        // only a field handle, the canonical attribute id, and (for a fill) the owned source
        // document reference. Fire-and-forget: an audit failure never blocks or weakens the
        // already-safe action it records (M15 §7), and lifecycle (hand_back/stop) is never sent
        // here — those keep their own endpoints.
        const reported = new Set();
        const report = (action) => {
          chrome.runtime.sendMessage({ type: "recordAction", action }).catch(() => {});
        };
        const reportOnce = (key, action) => {
          if (reported.has(key)) return;
          reported.add(key);
          report(action);
        };

        // Safe autofill (M10): plan from the approved mapping + the record, then write only the
        // "fill" actions into the DOM. Sensitive fields wait for approval; unmapped, ambiguous,
        // conflicting, and declaration fields are left untouched.
        const runFill = () => {
          if (!latest) return;
          const plan = computeFillPlan({ snapshot: latest, record, approvals, context, ...fillSeams });
          globalThis.__docuraFillPlan = plan;
          const { filled, failed } = applyFillPlan({ plan, root: document, approvals });
          globalThis.__docuraFills = filled;

          // Audit each real fill (FR-AUD-001): a value was placed in a field. Reference only.
          for (const f of filled) {
            reportOnce(`fill:${f.fieldId}`, fillAuditAction(f, { outcome: "succeeded" }));
          }
          // A fill DOCURA intended but could not perform is auditable as a failure.
          for (const f of failed) {
            reportOnce(`fillfail:${f.fieldId}`, fillAuditAction(f, { outcome: "failed" }));
          }

          // Sensitive fields awaiting approval. Tell the trusted popup (ids only — never a
          // value), and audit that DOCURA asked for approval (FR-AUD-003, approval_request).
          const pend = pendingApprovals(plan);
          chrome.runtime.sendMessage({ type: "reportPending", pending: pend }).catch(() => {});
          for (const p of pend) {
            reportOnce(`req:${p.fieldId}`, approvalRequestAuditAction(p));
          }
        };

        const recompute = (result) => {
          latest = result;
          globalThis.__docuraForms = result;
          // M10: the APPROVED mapping is now injected, and the user's record is supplied, so
          // supported fields resolve to a value. Everything else stays unknown/untouched.
          globalThis.__docuraReadiness = computeReadiness({ snapshot: result, record, resolveField: resolveFieldActive });
          globalThis.__docuraRetrieval = computeRetrieval({ snapshot: result, record, resolveField: resolveFieldActive });
          globalThis.__docuraReview = computeReview({ snapshot: result, record, resolveField: resolveFieldActive, approvals, ...reviewSeams });
          // Document matching stays at its frozen default (no approved matcher/threshold).
          globalThis.__docuraMatching = computeMatching({ snapshot: result, approvals });
          runFill();
        };

        const watcher = new FormWatcher({
          root: document,
          // Latest snapshot only; stale enumerations are never retained (FR-FRM-007).
          onChange: recompute,
        }).start();
        globalThis.__docuraWatcher = watcher;

        // Fetch the record once (token never leaves the worker). On arrival, recompute so the
        // safe fills run. On failure the record stays null and nothing is filled (fail inaction).
        chrome.runtime
          .sendMessage({ type: "getRecord" })
          .then((res) => {
            record = res && res.record ? res.record : null;
            if (latest) recompute(latest);
          })
          .catch(() => {
            /* backend unreachable / stale token: no record, nothing filled */
          });

        // The user approved one disclosure in the trusted popup: grant the exact-scope approval
        // for this field's available value, then fill just that one field (one-time, BR-005/007).
        const onApprove = (msg) => {
          if (msg?.type !== "approveField" || !latest) return;
          const plan = computeFillPlan({ snapshot: latest, record, approvals, context, ...fillSeams });
          for (const form of plan.forms) {
            for (const f of form.fields) {
              if (f.fieldId === msg.fieldId && f.action === "approval_required") {
                grantApproval(approvals, {
                  ...context,
                  formId: form.formId,
                  fieldId: f.fieldId,
                  canonicalIdentifier: f.canonicalIdentifier,
                  value: f.value,
                });
                // Audit the user's approval decision (FR-AUD-003). The subsequent fill of this
                // field is audited by runFill(). Value is never included.
                reportOnce(`decision:${f.fieldId}`, approvalDecisionAuditAction(f));
              }
            }
          }
          runFill();
        };
        chrome.runtime.onMessage.addListener(onApprove);

        // Called by background.js on stop/tab-close/sign-out: all activity ceases. DOCURA-placed
        // values are LEFT in the form (EC-017); only DOCURA's own state is cleared.
        globalThis.__docuraTeardown = () => {
          watcher.stop();
          chrome.runtime.onMessage.removeListener(onApprove);
          globalThis.__docuraWatcher = null;
          globalThis.__docuraForms = null;
          globalThis.__docuraReadiness = null;
          globalThis.__docuraRetrieval = null;
          globalThis.__docuraReview = null;
          globalThis.__docuraMatching = null;
          globalThis.__docuraFillPlan = null;
          globalThis.__docuraFills = null;
          approvals.clear(); // no approval survives the session (BR-007).
          globalThis.__docuraApprovals = null;
          reported.clear(); // audit de-dup is session-scoped; nothing survives teardown.
          record = null;
          chrome.runtime.sendMessage({ type: "reportPending", pending: [] }).catch(() => {});
        };
      },
    )
    .catch(() => {
      /* detection module unavailable; the indicator and activation are unaffected */
    });
})();
