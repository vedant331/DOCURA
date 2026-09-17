# DOCURA — Sprint 4 M16: Generic Field Interpretation Foundation

| Field | Value |
| --- | --- |
| Type | Architecture / seam milestone (extension) |
| Status | Interpreter seam added; controlled-form safety and M10/M13 behaviour preserved unchanged. |
| Scope | Extension only. **No** OCR, LLM, external AI, backend/extension redesign, or new released canonical attributes. |
| Governance | Interpretation maps ONLY to the two released attributes (`person.full_name`, `person.date_of_birth`). G-13-B / G-14 / G-15 / S-6 remain blocked; nothing here bypasses them. |

## 1. Problem

Until M16, "what does this field mean?" was answered only by an **exact match on the
controlled form's field ids** (`mapping.js`). That is correct and safe for the team's
controlled form, but it hard-codes individual field names and cannot grow toward
understanding a field by its *label/synonyms* without scattering `if/else` logic. M16 adds a
clean, replaceable **interpretation seam** so DOCURA is architecturally capable of field
understanding — without expanding the released vocabulary or loosening any safety boundary.

## 2. Current architecture (after M16)

```
detect.js        raw form field (value-free metadata: id/name/type/constraints)
   ↓
interpret.js     MEANING:  field → canonical attribute? (resolved | ambiguous | unknown)   ← new seam
   ↓
mapping.js       resolveField() bridges meaning into the pipeline; fieldAutomation() = POLICY;
                 isControlledForm() = controlled-form boundary
   ↓
retrieval.js     "do we hold that canonical attribute's value?" (available/ambiguous/conflict/unavailable)
   ↓
autofill.js      SAFETY POLICY → fill / ask / approval / untouched  → real DOM write
   ↓
content.js       execution + audit (M15)
```

Each stage stays a separate module. Interpretation never writes to the DOM and never decides
eligibility; retrieval never interprets; policy (automation + controlled-form gate) still
decides whether an interpreted, available field may actually be filled.

## 3. Interpreter contract

`interpretField(field)` → **FieldInterpretationResult**:

| Field | Meaning |
| --- | --- |
| `status` | `resolved` \| `ambiguous` \| `unknown` (both non-resolved states are first-class) |
| `fieldRef` | the field's handle (id/name) — never a value |
| `canonicalIdentifier` | the resolved canonical id (only when `resolved`), else `null` |
| `candidates` | the competing canonical ids (when `ambiguous`), else `[resolved]` or `[]` |
| `confidence` | `EXACT_ALIAS_CONFIDENCE` (1) when resolved; `null` otherwise |
| `reason` | short human explanation |
| `method` | `"controlled-alias-v1"` — the interpreter implementation identifier |

It is a pure function of value-free metadata (`label`, `name`, `id`) — no DOM, no fetch, no
Chrome APIs, no field value or page content.

## 4. resolved / ambiguous / unknown semantics

- **resolved** — exactly one approved meaning matched (exact match after normalisation). Carries
  the canonical id + full confidence (certain about the *meaning* by construction).
- **ambiguous** — more than one distinct approved meaning matched (e.g. the label says one
  thing and the id another). DOCURA **never** auto-chooses; `canonicalIdentifier` stays null.
- **unknown** — nothing matched. The field is left for the policy layer to leave untouched.

Normalisation (M16 §6): lowercase; harmless separators `._-/` → space; drop other punctuation;
collapse whitespace; trim. It is **meaning-preserving, not fuzzy** — no camelCase splitting,
stemming, substring, prefix, or edit-distance matching. So `"Full Name"`, `"full-name"`,
`"FULL_NAME"`, `"  full   name  "` all resolve to `person.full_name`, while `"fullname"`,
`"user full name"`, and `"full name of applicant"` stay **unknown** (no accidental match).

## 5. Current controlled attributes (and only these)

`person.full_name` and `person.date_of_birth` — the two released `v0.2-draft` entries.
Aliases (data-driven, in `interpret.js`):

- `person.full_name`: full name, name, applicant name, candidate name
- `person.date_of_birth`: date of birth, dob, d o b, birth date

## 6. Why no additional attributes were added

Email, phone, address, Aadhaar, PAN, education, gender, nationality, blood group, etc. are
**not released**: G-13-B is not met (sensitivity tiers G-14/G-15 depend on A-5 / studies
S-1/S-4), and several are blocked by C-a/C-b/C-c or explicitly rejected in G-12. Adding an
alias for any of them would introduce an unreleased attribute (BR-009). The interpreter maps
to nothing beyond the two released attributes; a unit test asserts labels like "Email"/"PAN"
stay `unknown`.

## 7. How a future interpreter plugs into the seam

Replace `interpretField` with a stronger deterministic rules engine or an approved local
semantic model that returns the same `FieldInterpretationResult`. `resolveField` in
`mapping.js` (its only consumer) is unchanged, and retrieval, sensitivity, approval, audit,
and DOM execution are untouched (M16 §13). A future detection layer may also capture a
field's `<label>`/`aria-label` (value-free) and pass it as `field.label`; the interpreter
already reads `label` first.

## 8. Safety invariants preserved

- **Controlled-form boundary intact.** Autofill still fires only on the controlled form
  (`isControlledForm`, M11-D5); the frozen controlled-form fields resolve via their exact,
  authoritative mapping. An interpreted-but-unpolicied field (`fieldAutomation` → null) is
  **left untouched** — interpretation never authorises a fill (M16 §8, integration-tested).
- **Meaning ≠ authorization.** The interpreter's confidence is about meaning only; it is not
  the BR-001 automatic-action threshold (TBD/G-04) and grants no sensitive disclosure,
  declaration/consent, submission, attachment, or arbitrary-site fill.
- **M10/M13 unchanged.** `full_name` auto-fills; `date_of_birth` requires one-time exact-scope
  approval; declarations/unknown/ambiguous/conflict stay untouched — all existing tests pass.
- **Privacy.** Interpretation reads value-free metadata only; no field value, page HTML, page
  text, password, or form payload enters interpretation or the M15 audit (audit `detail`
  carries only the canonical id).

## 9. Governance blockers (unchanged)

S-6 OCR (no corpus/engine), G-14/G-15 sensitivity tiers, and therefore G-13-B remain blocked.
Real-portal generalisation of autofill is intentionally NOT enabled. This milestone builds the
foundation only.
