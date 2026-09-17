# DOCURA — Sprint 4 M18: Semantic Interpreter Provider Architecture

| Field | Value |
| --- | --- |
| Type | Extension architecture milestone (interpretation seam) |
| Status | Interpretation refactored behind a replaceable provider contract; deterministic provider preserved exactly; all M16/M17 behaviour and controlled-form safety unchanged. |
| Scope | Extension only. **No** LLM, external AI API, model download, embeddings, vector DB, or network call. No new attributes; no autofill generalisation; no backend/record/sensitivity/approval/audit/DOM changes. |

## 1. Relationship to M16 and M17

M16 introduced the interpretation seam (`resolved | ambiguous | unknown`) with a small
deterministic alias matcher. M17 made detection capture value-free semantic label metadata
(`label`, `ariaLabel`, `ariaLabelledBy`, `placeholder`, `title`). M18 turns interpretation into
a **provider architecture** so a future stronger interpreter can be dropped in without touching
retrieval, safety policy, sensitivity, approval, audit, DOM execution, or the backend.

## 2. Provider contract

A provider is any object:

```
{ name: string, interpret(metadata) -> FieldInterpretationResult }
```

`interpret` receives value-free field **metadata** and returns a proposed result. It must not
fetch the record, call the backend, approve disclosure, write the DOM, submit, select
documents, or create audit actions — it only names a meaning.

## 3. Result contract (unchanged)

`{ status: "resolved" | "ambiguous" | "unknown", fieldRef, canonicalIdentifier, candidates,
confidence, reason, method }`. `UNKNOWN` and `AMBIGUOUS` remain first-class. A result never
contains a value from the user's record.

## 4. Provider selection

`selectProvider()` is the single point where the active provider is chosen. Today it returns
the `deterministicProvider`. `interpretField(field, { provider })` uses the selected provider by
default and accepts an injected provider (used only by unit tests). Consumers call the stable
`interpretField(field)` and never know which provider produced the result.

## 5. Current deterministic provider

`deterministicProvider` holds the M16/M17 logic verbatim: exact alias match after
normalisation over the primary sources (`label`, `ariaLabel`, `ariaLabelledBy`, `name`, `id`)
with `placeholder`/`title` as a fallback (M17 §4). It resolves only the two released
attributes and their approved aliases — no email/phone/address/aadhaar/pan/education/gender/etc.

## 6. Canonical-vocabulary validation (the trust boundary)

`interpretField` validates every provider's output before returning it:

- `resolved` → the `canonicalIdentifier` must be in `RELEASED_ATTRIBUTES`
  (`person.full_name`, `person.date_of_birth`) **and** `confidence` must be a number in
  `[0, 1]`; otherwise the result degrades to `unknown`. A provider naming `person.email` (or any
  unreleased id) never becomes fill-eligible.
- `ambiguous` → candidates are filtered to released ids; genuine ambiguity needs **≥ 2**
  supported candidates, else it degrades to `unknown` (DOCURA will not choose).
- `unknown` → passed through.

The wrapper builds the returned object itself from validated pieces, so no extra/unsafe keys
(and no value) can pass through from a provider.

## 7. Failure behaviour (safe by default)

A provider that throws, returns a non-object, a bad `status`, a missing/unsupported
`canonicalIdentifier`, or an out-of-range `confidence` all degrade to `unknown` → the field is
left untouched. Internal error text is never surfaced. There is no guessing fallback.

## 8. Confidence semantics

Confidence answers "how confident are we about what this field **means**?" It is **not**
permission to fill, a sensitivity decision, or the BR-001 automatic-action threshold (TBD/G-04).
The policy layer (controlled-form boundary + `fieldAutomation`) decides eligibility.

## 9. Ambiguity

Multiple plausible approved meanings → `status = ambiguous`, `canonicalIdentifier = null`,
`candidates` = the distinct supported ids. Never auto-chosen; the field stays untouched.

## 10. Privacy boundary

The provider receives only value-free metadata via `toProviderMetadata` — a strict whitelist
(`fieldRef`, `id`, `name`, `fieldId`, `type`, `required`, `label`, `ariaLabel`,
`ariaLabelledBy`, `placeholder`, `title`, `constraints`). Even if a caller's field object
carried a `value`/`defaultValue`/password, the provider never sees it. No provider makes
backend calls. Distinct label sources are preserved (not collapsed).

## 11. M17 metadata compatibility

The provider input carries all M17 label sources separately, so a provider can prefer an
accessible label over a placeholder/title (as the deterministic provider does).

## 12. Controlled-form safety (unchanged)

Autofill still fires only on the controlled form (`isControlledForm`, M11-D5); controlled
fields resolve via their frozen exact mapping; `person.full_name` auto-fills;
`person.date_of_birth` is approval-gated; declarations/unknown/ambiguous/conflict stay
untouched; no submission/attachment/override. A provider can identify meaning, but the policy
layer decides whether an action is allowed.

## 13. Future model-provider insertion point

To add an approved provider later: implement `{ name, interpret(metadata) }` (returning the
result contract), and return it from `selectProvider()` (behind whatever approval/config gate
governs it). Retrieval, policy, sensitivity, approval, audit, and DOM execution are unchanged.
The validation boundary (§6/§7) already contains any new provider's output to the released
vocabulary and safe failure modes.

## 14. Why no LLM in this milestone

M18 is an architecture milestone: it builds the seam and the safety/validation boundary an
approved semantic provider would need. An LLM/external AI provider is explicitly out of scope
(no network, no model, no embeddings) and would additionally require governance the project has
not granted. The deterministic provider remains the only enabled implementation.

## 15. Test provider

A test-only mock provider (defined in `test/interpret-provider.test.js`, never in `src/`)
simulates resolved / unknown / ambiguous / malformed / unsupported-attribute / out-of-range /
throwing behaviour, and asserts the value-free metadata boundary. It is never enabled in
production.

## Remaining blockers

S-6 OCR and G-14/G-15 (→ G-13-B) unresolved: no additional released attributes, no real-portal
generalisation, and no approved semantic (model) provider yet. The seam is ready for one.
