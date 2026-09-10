// Form detection (M3). Deterministic, value-free reading of the page's form
// structure. It runs ONLY inside the content script, which activation injects on
// one tab — there is no passive observation anywhere (there is still no
// `content_scripts` entry in the manifest).
//
// Hard boundaries this module keeps (FR-FRM safety):
//   * It captures field *metadata* only — identifier, type, required, declared
//     constraints, form association. It never reads `.value` or any entered text,
//     and it never captures option/choice values (that would be interpretation and
//     is a later milestone).
//   * It is a pure function of the DOM plus a thin observer wrapper. Nothing here
//     talks to the backend; M3 transmits no field data.
//
// Kept engine-neutral of Chrome APIs so it unit-tests in Node with plain fakes:
// scanForms/describeField only use standard DOM reads, and FormWatcher takes its
// MutationObserver factory as a dependency.

// Controls that exist in a form but are not user-fillable data fields. Buttons are
// actions, not fields; hidden inputs are structure/tokens we deliberately do not
// capture. Enumerating these would add noise and, for hidden, risk leaking tokens.
const NON_FILLABLE = new Set(["submit", "button", "reset", "image", "hidden"]);

// Declared constraint attributes we read verbatim. Presence-only: a key appears in
// the descriptor only when the form actually declares it, so we never invent a
// constraint the author did not state. HTML has no standard file *size* attribute,
// so size limits are read from the conventional data-* attributes when present.
const SIZE_ATTRS = ["data-max-size", "data-maxsize", "data-max-file-size"];

function attr(el, name) {
  const v = el.getAttribute ? el.getAttribute(name) : null;
  return v === null || v === undefined ? null : v;
}

function toInt(v) {
  if (v === null) return null;
  const n = Number.parseInt(v, 10);
  return Number.isNaN(n) ? v : n; // keep the raw string if it is not an integer
}

function collectConstraints(el) {
  const c = {};
  const minlength = attr(el, "minlength");
  const maxlength = attr(el, "maxlength");
  if (minlength !== null) c.minLength = toInt(minlength);
  if (maxlength !== null) c.maxLength = toInt(maxlength);
  const pattern = attr(el, "pattern");
  if (pattern !== null) c.pattern = pattern;
  // Numeric / date range — the "size-related" declared limits for those types.
  for (const k of ["min", "max", "step"]) {
    const v = attr(el, k);
    if (v !== null) c[k] = v;
  }
  const accept = attr(el, "accept");
  if (accept !== null) c.accept = accept;
  if (el.multiple || attr(el, "multiple") !== null) c.multiple = true;
  for (const k of SIZE_ATTRS) {
    const v = attr(el, k);
    if (v !== null) {
      c.maxSize = v; // declared, not interpreted
      break;
    }
  }
  return c;
}

// Describe one control, or return null if it is not a fillable field. Metadata only.
export function describeField(el) {
  const tag = (el.tagName || "").toLowerCase();
  let type;
  if (tag === "select") type = "select";
  else if (tag === "textarea") type = "textarea";
  else if (tag === "input") type = (el.type || "text").toLowerCase();
  else return null;
  if (NON_FILLABLE.has(type)) return null;

  const id = el.id || null;
  const name = (attr(el, "name") ?? el.name) || null;
  const required = !!el.required || attr(el, "required") !== null || attr(el, "aria-required") === "true";

  return {
    // Stable identifier where safely available; never fabricated.
    fieldId: id ?? name,
    id,
    name,
    tag,
    type,
    required,
    constraints: collectConstraints(el),
  };
}

// Snapshot the fillable forms currently present under `root`. Groups controls by
// their native form association (`el.form`, which honours the `form=` attribute), so
// controls reassigned or living outside any <form> are attributed correctly.
// A group with no owning <form> is reported as `standalone` (bare inputs on a page).
export function scanForms(root) {
  const controls = Array.from(root.querySelectorAll("input, select, textarea"));
  const groups = new Map(); // owner form element (or null) -> field descriptors

  for (const el of controls) {
    const field = describeField(el);
    if (!field) continue;
    const owner = el.form ?? null;
    if (!groups.has(owner)) groups.set(owner, []);
    groups.get(owner).push(field);
  }

  const forms = [];
  for (const [owner, fields] of groups) {
    forms.push({
      formId: owner ? (owner.id || attr(owner, "name") || null) : null,
      standalone: owner === null,
      fields,
    });
  }
  return { forms, formCount: forms.filter((f) => !f.standalone).length };
}

// Watches `root` and re-scans on structural change. Each scan REPLACES the previous
// result wholesale — the watcher holds no field mapping across scans, so a changed
// form can never be described by a stale enumeration (FR-FRM-006/007). Fields added
// after load and removed/replaced fields are picked up by the same mechanism.
//
// The MutationObserver factory is injected so this is unit-testable without a
// browser: pass a fake that hands back the callback to fire on demand.
export class FormWatcher {
  constructor({ root, onChange, observerFactory } = {}) {
    this.root = root;
    this.onChange = onChange;
    this.factory = observerFactory ?? ((cb) => new MutationObserver(cb));
    this.observer = null;
    this.stopped = false;
    this.latest = null;
  }

  start() {
    this.rescan("initial");
    this.observer = this.factory(() => this.rescan("mutation"));
    this.observer.observe(this.root, {
      childList: true,
      subtree: true,
      attributes: true,
      // Only attributes that change what fields exist or what they require/accept.
      attributeFilter: [
        "type", "name", "id", "required", "aria-required", "disabled", "form",
        "pattern", "min", "max", "step", "minlength", "maxlength", "accept", "multiple",
      ],
    });
    return this;
  }

  rescan(reason) {
    if (this.stopped) return null; // a stopped session processes no further mutations
    this.latest = scanForms(this.root);
    if (this.onChange) this.onChange(this.latest, reason);
    return this.latest;
  }

  // Stop observing immediately. Idempotent; after this, mutations are ignored.
  stop() {
    this.stopped = true;
    if (this.observer) this.observer.disconnect();
    this.observer = null;
  }
}
