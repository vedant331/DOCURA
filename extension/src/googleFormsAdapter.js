// Google Forms PROTOTYPE adapter (validation only — NOT a production form type).
//
// One job: translate the Google Forms DOM into the EXISTING DOCURA field metadata shape
// (the same descriptors detect.js emits), so the unchanged pipeline — interpret → mapping →
// retrieval → sensitivity → approval → autofill → audit — runs against a real Google Form.
// There is NO Google Forms autofill engine here: this module only reads structure and hands
// clean, value-free metadata to `scanGoogleForm`, which content.js feeds to the SAME
// FormWatcher/computeFillPlan path the controlled/demo forms use.
//
// Why an adapter is needed at all (discoveries from the real DOM):
//   * Google Forms wraps short-answer/email in `<input>` and paragraph in `<textarea>` — native
//     controls scanForms would find — BUT their accessible name comes from `aria-labelledby`
//     that references the question heading *plus* the "*"/"Required question"/description nodes.
//     Space-joined, that is "Full Name Required question", which the EXACT-alias interpreter
//     (BR-009, no fuzzy match) never resolves. The adapter supplies the clean question title as
//     the field's `label` so the existing interpreter matches without any Google-specific logic
//     leaking into interpret.js/demo.js.
//   * The visible inputs usually carry no stable id/name (the submit uses hidden `entry.*`
//     inputs we deliberately ignore). The adapter tags each fillable control with a value-free
//     `data-docura-field` so autofill.js can locate it — a generic locator, not Google-specific.
//   * Radio/checkbox/dropdown are `<div role=...>`, not native controls, so scanForms cannot see
//     them at all. The adapter surfaces them as metadata-only descriptors (never TEXT_FILLABLE),
//     so a consent checkbox is correctly recognised as a declaration and BLOCKED, and any other
//     choice question resolves to unknown → untouched. DOCURA never operates a div control.
//
// Safety is entirely inherited from the existing pipeline: unknown/ambiguous/declaration fields
// stay untouched, sensitive fields wait for per-disclosure approval, and DOCURA never submits.
// This module writes nothing, fetches nothing, and sends nothing anywhere.

import { describeField } from "./detect.js";

// Explicit PROTOTYPE opt-in. Gates the adapter on top of the host check below — BOTH must hold,
// so this never silently turns Google Forms into a production-wide supported form type. Set to
// false for a build that should ignore Google Forms entirely; the controlled/demo path is
// unaffected either way.
export const GOOGLE_FORMS_MODE = true;

// Host restriction (kept out of the pipeline). The prototype is limited strictly to Google
// Forms pages. Activation already scopes injection to the one tab the user invoked (activeTab),
// so no host permission is added; this is the in-code guard that the adapter runs ONLY here.
export function isGoogleFormsHost(loc = typeof location !== "undefined" ? location : null) {
  if (!loc) return false;
  return loc.hostname === "docs.google.com" && String(loc.pathname || "").startsWith("/forms/");
}

// A stable, constant form id for the whole Google Form. formId is only used as part of the
// session-scoped approval key and for eligibility (the dynamic seam accepts any form), so a
// constant is sufficient and avoids depending on Google's unstable internal ids.
const GOOGLE_FORM_ID = "google-form";

// The question title, cleaned of Google's required marker / helper text so the EXISTING exact
// alias interpreter can match it. Never reads any entered value.
function cleanQuestionText(raw) {
  if (raw === null || raw === undefined) return null;
  let t = String(raw).replace(/\s+/g, " ").trim();
  t = t.replace(/\s*\*+\s*$/, "").trim(); // trailing required asterisk(s)
  t = t.replace(/\s*Required question\s*$/i, "").trim();
  return t || null;
}

// Prefer the question block's heading text; fall back to the first aria-labelledby target.
function questionLabel(container) {
  const heading = container.querySelector('[role="heading"]');
  if (heading) return cleanQuestionText(heading.textContent);
  const control = container.querySelector("[aria-labelledby]");
  const firstId = control ? (control.getAttribute("aria-labelledby") || "").split(/\s+/)[0] : null;
  const doc = container.ownerDocument;
  const ref = firstId && doc && doc.getElementById ? doc.getElementById(firstId) : null;
  return ref ? cleanQuestionText(ref.textContent) : null;
}

// Native, user-fillable control inside a question block (the vocabulary — name/email/phone/
// address/date/PAN/Aadhaar — is all text/date, which Google renders as these).
const NATIVE_SELECTOR =
  'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="image"]), textarea, select';

// A choice control we can only DETECT (never fill): Google renders these as divs with a role.
const CHOICE_ROLES = [
  ['[role="radiogroup"]', "radio"],
  ['[role="checkbox"]', "checkbox"],
  ['[role="listbox"]', "select"],
];

let seq = 0; // per-scan counter for synthetic, stable-within-scan field ids

// One question block → at most one field descriptor in the EXISTING shape, or null to skip.
function describeQuestion(container) {
  const label = questionLabel(container);

  const nativeEl = container.querySelector(NATIVE_SELECTOR);
  if (nativeEl) {
    const base = describeField(nativeEl);
    if (!base) return null;
    // Override ONLY the semantic label sources with the clean question title, so the interpreter
    // sees clean semantics — not Google's noisy aria strings. Type/required/constraints inherited.
    const field = { ...base, label, ariaLabel: null, ariaLabelledBy: null };
    if (!field.fieldId) {
      // No stable id/name on the visible input: tag it with a value-free locator the generic
      // autofill.findElement understands. data-docura-field is NOT in the observer's attribute
      // filter, so tagging does not trigger a rescan loop.
      const fid = `gf-${seq++}`;
      if (nativeEl.setAttribute) nativeEl.setAttribute("data-docura-field", fid);
      field.fieldId = fid;
    }
    return field;
  }

  for (const [selector, type] of CHOICE_ROLES) {
    const el = container.querySelector(selector);
    if (!el) continue;
    return {
      fieldId: `gf-${seq++}`,
      id: null,
      name: null,
      tag: "div",
      type, // radio | checkbox | select — never TEXT_FILLABLE, so autofill never writes it
      required: !!container.querySelector('[aria-required="true"]'),
      constraints: {},
      label,
      ariaLabel: null,
      ariaLabelledBy: null,
      placeholder: null,
      title: null,
    };
  }
  return null;
}

// Snapshot the Google Form in the SAME { forms, formCount } shape scanForms returns, so it is a
// drop-in `scan` for FormWatcher. Groups all questions under one logical form.
export function scanGoogleForm(root) {
  seq = 0;
  const containers = root.querySelectorAll ? Array.from(root.querySelectorAll('[role="listitem"]')) : [];
  const fields = [];
  for (const c of containers) {
    const field = describeQuestion(c);
    if (field) fields.push(field);
  }
  return { forms: [{ formId: GOOGLE_FORM_ID, standalone: false, fields }], formCount: 1 };
}
