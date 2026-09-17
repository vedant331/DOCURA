// Safe autofill (M10): turn approved mappings + the user's structured record into a set of
// real DOM writes, and nothing more. It is the LAST layer and deliberately thin:
//
//   snapshot (detect.js) + record (backend) + mapping (mapping.js) + approvals (sensitivity.js)
//        → computeFillPlan → a per-field decision
//        → applyFillPlan → real DOM value writes + provenance, ONLY for safe "fill" actions.
//
// Safety rules enforced here (M10 §10–§15, BR-005/BR-006/BR-009):
//   * Unmapped field               → "untouched" (never guessed from its label).
//   * Ambiguous / conflict value   → "ask"       (never auto-selected/auto-resolved).
//   * No value on record           → "unavailable" (honest; no guess, no fake value).
//   * Sensitive form field         → "approval_required" until an exact-scope approval is granted,
//                                     then "fill" (one-time, per BR-005/BR-007).
//   * Declaration/consent control  → unmapped by construction → "untouched" (BR-006).
// Only action "fill" ever writes to the DOM.

import { computeRetrieval } from "./retrieval.js";
import { resolveField, fieldAutomation, isControlledForm } from "./mapping.js";
import { checkApproval, consumeApproval } from "./sensitivity.js";

// Form-field input types we will write a text value into. Everything else (checkbox, radio,
// file, select, submit, …) is never auto-written in M10 — those are matching/declaration/choice
// concerns, not a text fill.
const TEXT_FILLABLE = new Set([
  "text", "textarea", "email", "tel", "url", "search", "number", "date",
]);

function provenanceFrom(decision) {
  // The "available" retrieval decision carries one candidate with its provenance chain.
  const candidate = decision.candidates?.[0];
  return {
    canonicalIdentifier: decision.canonicalIdentifier ?? null,
    value: decision.value ?? candidate?.value ?? null,
    sources: (candidate?.provenance ?? []).map((p) => ({
      documentId: p.documentId,
      extractionRunId: p.extractionRunId,
      pageNumber: p.pageNumber,
      confidence: p.confidence ?? null,
    })),
  };
}

// Decide what to do with one field, given its retrieval decision and automation class.
function planField(field, decision, automation, { approvals, context }) {
  const base = {
    fieldId: field.fieldId ?? null,
    id: field.id ?? null,
    name: field.name ?? null,
    type: field.type,
    canonicalIdentifier: decision.canonicalIdentifier ?? null,
  };

  // Unmapped (includes declarations/consent, which are never in the approved table).
  if (automation === null || decision.canonicalIdentifier === null) {
    return { ...base, action: "untouched", reason: "No approved mapping for this field." };
  }
  // The backend did not produce a single agreed value → never fill.
  if (decision.status === "ambiguous" || decision.status === "conflict") {
    return { ...base, action: "ask", status: decision.status, candidates: decision.candidates ?? [], reason: decision.reason };
  }
  if (decision.status !== "available") {
    return { ...base, action: "unavailable", reason: decision.reason };
  }
  // A value is available. `never` is a mapped-but-do-not-automate escape hatch.
  if (automation === "never") {
    return { ...base, action: "untouched", reason: "Mapping marks this field do-not-automate." };
  }

  const provenance = provenanceFrom(decision);

  // Sensitive form field: fill ONLY with an exact-scope, unconsumed approval for THIS value.
  if (automation === "approval") {
    const scope = { ...context, fieldId: base.fieldId, canonicalIdentifier: base.canonicalIdentifier, value: decision.value };
    if (checkApproval(approvals, scope) === "granted") {
      return { ...base, action: "fill", value: decision.value, provenance, sensitive: true, approved: true, scope };
    }
    return { ...base, action: "approval_required", value: decision.value, provenance, sensitive: true };
  }

  // Routine form field: fill.
  return { ...base, action: "fill", value: decision.value, provenance, sensitive: false };
}

// Build the full plan over a snapshot. `record` is the backend AttributeRecordResponse (or
// null/empty when the user has nothing). `approvals` is the session ledger; `context` carries
// { userId, sessionId } for approval scoping.
export function computeFillPlan({ snapshot, record, approvals, context = {} } = {}) {
  const retrieval = computeRetrieval({ snapshot, record, resolveField });
  const summary = { total: 0, fill: 0, approval_required: 0, ask: 0, unavailable: 0, untouched: 0 };

  const forms = (snapshot?.forms ?? []).map((form, fi) => {
    const rForm = retrieval.forms[fi];
    // formId is part of the approval scope key, so bind it into the per-form context.
    const formContext = { ...context, formId: form.formId ?? null };
    // The approved mapping applies ONLY to the controlled form (M11-D5, §22). On any other
    // form every field is left untouched — no mapping, no auto-fill, no label guessing.
    const controlled = isControlledForm(form.formId);
    const fields = form.fields.map((field, j) => {
      const decision = rForm.fields[j];
      const automation = controlled ? fieldAutomation(field) : null;
      const entry = planField(field, decision, automation, { approvals, context: formContext });
      summary.total += 1;
      summary[entry.action] += 1;
      return entry;
    });
    return { formId: form.formId ?? null, standalone: !!form.standalone, fields };
  });

  return { forms, summary };
}

// Find the element a plan entry refers to, preferring its id, then its name.
function findElement(root, entry) {
  if (entry.id && root.getElementById) {
    const byId = root.getElementById(entry.id);
    if (byId) return byId;
  }
  if (entry.name && root.querySelector) {
    return root.querySelector(`[name="${entry.name.replace(/"/g, '\\"')}"]`);
  }
  return null;
}

// Write one value into an element and record provenance ON the element, so the fill is traceable
// in the page (FR-FILL + M10 §15). Dispatches input+change so page frameworks observe the value.
function writeValue(el, entry) {
  el.value = entry.value;
  if (el.setAttribute) {
    el.setAttribute("data-docura-filled", "true");
    el.setAttribute("data-docura-attribute", entry.canonicalIdentifier ?? "");
    const firstSource = entry.provenance?.sources?.[0];
    if (firstSource?.documentId) el.setAttribute("data-docura-source-document", firstSource.documentId);
  }
  if (typeof el.dispatchEvent === "function") {
    try {
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    } catch {
      /* non-DOM fake in tests: events are optional */
    }
  }
}

// Apply a plan to a DOM root. ONLY "fill" actions write; everything else is left untouched.
// If `approvals` is given, an approved-sensitive fill is consumed (one-time, BR-007).
// Returns the provenance records for what was filled (for __docuraFills / diagnostics —
// references only, never page content beyond the value the user is filling themselves).
export function applyFillPlan({ plan, root, approvals } = {}) {
  const filled = [];
  const failed = [];
  for (const form of plan?.forms ?? []) {
    for (const entry of form.fields) {
      if (entry.action !== "fill") continue;
      if (!TEXT_FILLABLE.has(entry.type)) continue; // never write a non-text control
      const el = findElement(root, entry);
      if (!el) {
        // A fill DOCURA meant to perform but could not (the field is gone): a real failed
        // operation, kept auditable (references only, never a value).
        failed.push({
          fieldId: entry.fieldId,
          canonicalIdentifier: entry.canonicalIdentifier,
          provenance: entry.provenance,
          sensitive: !!entry.sensitive,
        });
        continue;
      }
      // Idempotent: don't re-write (and re-dispatch) a field DOCURA already filled, so a
      // rescan triggered by our own input/change events cannot loop.
      if (el.getAttribute && el.getAttribute("data-docura-filled") === "true") continue;
      writeValue(el, entry);
      if (entry.approved && approvals && entry.scope) consumeApproval(approvals, entry.scope);
      filled.push({
        fieldId: entry.fieldId,
        canonicalIdentifier: entry.canonicalIdentifier,
        value: entry.value,
        provenance: entry.provenance,
        sensitive: !!entry.sensitive,
      });
    }
  }
  return { filled, failed, count: filled.length };
}

// ---- audit action builders (M15) -------------------------------------------
// Pure functions that turn a fill/approval outcome into the backend audit contract shape.
// They exist so the "no value ever leaves the page" guarantee is directly testable: each
// returns ONLY a field handle, the canonical attribute id, and (for a fill) the owned source
// document reference — never the field value, the provenance object, or any page content.

export function fillAuditAction(entry, { outcome = "succeeded" } = {}) {
  return {
    action_type: "fill",
    outcome,
    field_ref: entry?.fieldId ?? null,
    document_id: entry?.provenance?.sources?.[0]?.documentId ?? null,
    detail: entry?.canonicalIdentifier ?? null,
  };
}

export function approvalRequestAuditAction(pendingItem) {
  return {
    action_type: "approval_request",
    outcome: "succeeded",
    field_ref: pendingItem?.fieldId ?? null,
    detail: pendingItem?.canonicalIdentifier ?? null,
  };
}

export function approvalDecisionAuditAction(field) {
  return {
    action_type: "approval_decision",
    outcome: "succeeded",
    field_ref: field?.fieldId ?? null,
    detail: field?.canonicalIdentifier ?? null,
  };
}

// The fields awaiting the user's explicit approval — for a trusted surface (the popup) to list.
// Carries NO raw value (masking, FR-SENS-004); the value is disclosed only on/after approval.
export function pendingApprovals(plan) {
  const out = [];
  for (const form of plan?.forms ?? []) {
    for (const entry of form.fields) {
      if (entry.action === "approval_required") {
        out.push({ fieldId: entry.fieldId, canonicalIdentifier: entry.canonicalIdentifier, formId: form.formId });
      }
    }
  }
  return out;
}
