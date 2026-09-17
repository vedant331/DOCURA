# DOCURA — Sprint 4 M17: DOM Semantic Field Metadata Capture

| Field | Value |
| --- | --- |
| Type | Extension detection milestone (metadata capture only) |
| Status | Value-free semantic label metadata captured by `detect.js` and consumed by the M16 interpreter. Controlled-form safety, M10/M13 behaviour, and privacy unchanged. |
| Scope | Extension only. **No** OCR, LLM, semantic AI, fuzzy matching, new attributes, backend/record/sensitivity/approval/audit changes, or autofill generalisation. |

## 1. Why id/name alone are insufficient

M16 can interpret a field only from the text it is given. Real forms often name a field by a
human-readable **label** (`<label>`, `aria-label`, `aria-labelledby`) while the `id`/`name`
are opaque (`field_7`, `q3`). Until M17, `detect.js` captured only `id`/`name`, so the
interpreter could not see the label a user actually reads. M17 captures that label metadata —
**value-free** — so interpretation works from the information the user sees.

## 2. Semantic metadata sources (kept distinct)

`describeField` now adds these to each field descriptor, each `null` when absent:

| Source | From |
| --- | --- |
| `label` | the field's `<label>` — explicit `<label for=id>` or a wrapping `<label>` |
| `ariaLabel` | `aria-label` attribute |
| `ariaLabelledBy` | resolved text of the element(s) named by `aria-labelledby` |
| `placeholder` | `placeholder` attribute |
| `title` | `title` attribute |

They are **not** collapsed into one string — the interpreter chooses among them by priority
(§ interpreter integration). Existing structural metadata (`id`, `name`, `tag`, `type`,
`required`, `constraints`, form association) is unchanged.

## 3. Label resolution rules

`label` is resolved in this order, each step guarded so it never throws:

1. **Native `element.labels`** — reflects both `<label for>` and wrapping `<label>`.
2. **`ownerDocument.querySelector('label[for="id"]')`** — explicit association fallback.
3. **`element.closest('label')`** — wrapping-label fallback.

The label's text is `labelEl.textContent`, whitespace-normalised, trimmed, and length-capped
(300 chars). Because a form control contributes **no** text nodes, a wrapped
`<label>DOB <input value="secret"></label>` yields `"DOB"` — the input's value is never in
`textContent`, so this is value-free by construction.

## 4. aria-label / aria-labelledby handling

- `aria-label` is read verbatim (normalised).
- `aria-labelledby` resolves each referenced id via `ownerDocument.getElementById`, takes each
  element's `textContent`, and space-joins them (normalised). Only the referenced elements are
  read — never a broad DOM walk.

## 5. Value-free privacy boundary

Captured metadata is **strictly value-free**. `describeField` never reads `.value`,
`defaultValue`, `innerHTML`, `outerHTML`, option/choice values, or unrelated page text, and it
does not serialise the form/document. A password field is described (metadata only) but its
contents are never captured. Tests assert descriptors contain none of
`value / defaultValue / innerHTML / outerHTML / textContent / nodeValue`, and that unrelated
page text and injected values never appear in the descriptor. Metadata stays in the isolated
content path; **nothing new is sent to the backend** (the backend still handles only record,
lifecycle, audit, ownership, and policy).

## 6. Interaction with the M16 interpreter

Detection answers "what metadata does this field expose?"; interpretation (unchanged module
`interpret.js`) answers "what does it mean?". `interpretField` now reads the semantic sources
with an explicit priority (M17 §4):

- **Primary:** `label`, `ariaLabel`, `ariaLabelledBy`, `name`, `id` — an accessible label and
  the identifiers are peers; if two disagree the result is **ambiguous** (never auto-chosen).
- **Secondary:** `placeholder`, `title` — consulted **only** when nothing primary matches, so a
  placeholder or title can never override an explicit accessible label.

Matching remains exact-after-normalisation (no fuzzy/substring), maps only to the two released
attributes, and returns `resolved | ambiguous | unknown`.

## 7. Dynamic-field handling

The existing `FormWatcher`/`MutationObserver` flow is preserved: a rescan re-runs
`describeField`, so a dynamically inserted field's semantic metadata is captured exactly like
an initial field, and a removed field drops out (no stale entry, no persistent page storage).
The observer's `attributeFilter` now also watches `aria-label`, `aria-labelledby`,
`placeholder`, and `title`, so a change to a field's accessible label triggers a rescan.

## 8. Controlled-form safety (unchanged)

Richer metadata does **not** widen authorisation. Autofill still fires only on the controlled
form (`isControlledForm`, M11-D5); the controlled fields resolve via their frozen exact mapping;
`person.full_name` auto-fills, `person.date_of_birth` is approval-gated; declarations, unknown,
ambiguous, and conflict stay untouched; no submission/attachment/override. A field may now
carry a rich label and still be entirely ineligible for autofill (policy decides, not the label).

## 9. What is intentionally not implemented

- No OCR, LLM, semantic AI, or fuzzy/similarity matching.
- No new canonical attributes; no autofill on arbitrary sites.
- No transmission of label/DOM metadata to the backend.
- No capture of values, page HTML, or arbitrary page text.
- Real-DOM label resolution is unit-tested against a faithful fake-DOM model (the extension
  keeps its zero-dependency `node:test` setup); the existing `mock-form-m10.html` carries
  `<label for>` labels for manual browser observation via `globalThis.__docuraForms`.
