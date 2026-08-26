# Browser Extension Lifecycle

**Step 4 · Document 6 of 20** — The thirteen-step lifecycle from a dormant extension to a form the user submits.

**Use cases:** UC-002, UC-013, UC-014, UC-015, UC-016, UC-017, UC-018, UC-019, UC-020, UC-021, UC-022, UC-023,
UC-024, UC-025, UC-026 · **Governing view:** Step 3 §8 Table 8.1

---

## 1. Part 1 — Activation and understanding (steps 1–6)

<!--DIAGRAM:05a-extension-activation-->

## 2. Part 2 — Acting, asking, and hand-back (steps 7–13)

<!--DIAGRAM:05b-extension-acting-handback-->

## 3. The session state machine

What the extension is *permitted to do* in each state — including the four ways a session can end abnormally.

<!--DIAGRAM:17-form-session-states-->

---

## 4. The thirteen steps, with their requirements

| # | Step | Actor | Requirements | Use case |
|---|---|---|---|---|
| 1 | User opens a supported form page | USER | — (DOCURA is dormant: FR-EXT-004) | — |
| 2 | User activates DOCURA **on that page** | USER | FR-INT-001, FR-EXT-003, BR-014 | UC-013 |
| 3 | Extension reads the activated page content | EXTENSION | FR-EXT-003, FR-EXT-005, NFR-PRIV-004 | UC-013 |
| 4 | Form is detected | EXTENSION | FR-FRM-001 | UC-014 |
| 5 | Fields are enumerated with types, required flags, constraints | EXTENSION | FR-FRM-002/003/004, FR-FLD-007, AR-DET-007 | UC-014 |
| 6 | Fields are interpreted and classified by tier | Form Intelligence | FR-FLD-001/002/003/004, AR-AST-003, AR-DET-005/006 | UC-016 |
| 7 | Information is matched from the record | Form Intelligence | FR-FILL-001, FR-DRP-002, FR-MATCH-001/002, AR-AST-004/005 | UC-017, UC-018, UC-020 |
| 8 | Confidence is evaluated | Decision & Policy Engine | BR-001, BR-002, AR-DET-004 | UC-017 |
| 9 | Appropriate action is taken — act, leave, or never touch | Action Executor | FR-FILL-001…008, FR-DRP-003, FR-MATCH-003, BR-006, BR-009, AR-AGT-001 | UC-017, UC-018, UC-020, UC-022 |
| 10 | User is asked when required | EXTENSION → USER | FR-AMB-002…005, FR-APR-001/002, FR-SENS-003 | UC-019, UC-021 |
| 11 | Form is reviewed | EXTENSION → USER | FR-REV-001…006 | UC-025 |
| 12 | DOCURA stops | EXTENSION | FR-SUB-001…004, BR-008 | UC-026 |
| 13 | User submits | USER | FR-SUB-002, BR-008 | UC-026 |

---

## 5. Diagram key — node to requirement

| Node | Requirements |
|---|---|
| DOCURA is dormant | FR-EXT-004, BR-014 |
| USER activates DOCURA | FR-INT-001, FR-EXT-003 |
| Authenticated session valid? | FR-EXT-002, NFR-SEC-005 |
| Persistent activity indicator | FR-EXT-005 |
| Read the activated page structure only | FR-EXT-003, NFR-PRIV-004 |
| Fillable form detected? | FR-FRM-001 |
| Enumerate fields, types, flags, constraints | FR-FRM-002/003/004, AR-DET-007 |
| Presented across several steps? | FR-FRM-005 |
| Interpret each field meaning | FR-FLD-001/002, AR-AST-003 |
| Classify routine / sensitive / consequential | FR-FLD-003, AR-DET-005 |
| Readiness summary | FR-INT-002/003 |
| Match the record to the field | AR-AST-004, AR-AST-005 |
| Confidence and sensitivity | BR-001, BR-005, AR-DET-004, AR-AGT-002 |
| ACT | FR-FILL-001…008, FR-DRP-003, FR-MATCH-003, AR-AGT-001 |
| ASK | FR-AMB-002, FR-APR-001, FR-SENS-003 |
| LEAVE UNTOUCHED and REPORT | FR-FLD-006, FR-FILL-007, FR-DRP-005, FR-MATCH-005, BR-009 |
| NEVER TOUCH | FR-FLD-004, FR-DRP-007, BR-006 |
| Form structure changed? | FR-FRM-006/007, AR-AGT-005 |
| Review summary | FR-REV-001…005 |
| DOCURA STOPS | FR-SUB-001…004, BR-008 |
| USER stops DOCURA | FR-EXT-006 |
| Network loss or session expiry | NFR-REL-003, NFR-SEC-005 |

---

## 6. The six branch conditions the brief asks about

### 6.1 The form is unsupported
No fillable form is detected. The extension **reports that no form was found and takes no action**. It does not
guess that some other element is a form, and it does not fall back to string-matching field names. It remains
activated but idle — the user's activation is not silently revoked. *(BR-016; FR-FRM-001.)*

Two structural cases are unsupported in the MVP by decision, not by failure: forms in **embedded frames**
(FR-FRM-008, deferred on ASM-004) and **mobile browsers** (FR-EXT-008, deferred pending A-8). Both are reported
rather than silently skipped.

### 6.2 A field is unknown — EC-008
Interpretation confidence falls below the threshold. The field is **marked unknown and left untouched** — never
guessed from a superficially similar label. It is listed at review as requiring the user. *(FR-FLD-006,
FR-FILL-007, BR-009, AC-US-008-3.)*

The same treatment applies to a field type outside the MVP seven — EC-010: enumerated, marked unsupported, excluded
from filling, listed at review.

### 6.3 Confidence is too low
Two distinct floors apply, and both must clear:

- **The review threshold (BR-002).** A value extracted below it is never used for automatic action, *however well
  it matches the field.* It does not get a second chance at fill time.
- **The automatic-action threshold (BR-001).** Both the field interpretation **and** the source value must reach it.

Below either, the field becomes ambiguous rather than filled — and if there is nothing to choose between, it is
reported rather than prompted (see [`ambiguity-flow.md`](ambiguity-flow.md) §5).

### 6.4 Multiple matches exist — EC-006
**Nothing is selected and nothing is attached.** The user is asked, and each candidate is shown with the reason it
was considered. BR-003 states the rule without qualification: DOCURA "may not select the most likely candidate on
the user's behalf." *(FR-DRP-004, FR-MATCH-004, FR-AMB-001.)*

### 6.5 The user rejects a suggestion — EC-012
The suggestion is not applied, **is not proposed again for that field in that session**, and the remaining
candidates or manual selection are offered. A rejection is not treated as a transient error to retry.

For a sensitive item, a denial additionally: leaves the field untouched, is recorded, and **does not block the
remainder of the session** (FR-APR-003, EC-011).

### 6.6 The user stops DOCURA
All activity ceases within the current interaction. **Values already placed remain and are not reverted or
cleared.** DOCURA does not resume when the page changes or new fields appear — a fresh activation is required.
*(FR-EXT-006, AC-US-016-1…3.)*

Note the deliberate absence: **there is no pause state.** Steps 1–3 define stopping, not suspending. Inventing a
resumable pause would add behaviour no requirement supports — see [`use-case-catalogue.md`](use-case-catalogue.md) §1.

---

## 7. Capability boundary — what the MVP extension does and does not do

Reproduced from Step 3 §8 Table 8.1 so the MVP line is visible while reading the flow.

| Capability | Release | MVP boundary |
|---|---|---|
| Detect supported forms | MVP | Standard forms on the page. Embedded frames excluded. |
| Detect field types | MVP | Text, number, date, dropdown, radio, checkbox, file. Multi-select and custom widgets excluded. |
| Understand field labels | MVP | Semantic interpretation with confidence and an explicit "unknown" outcome. |
| Match user information | MVP | From the structured record only. **No inference from unrelated fields.** |
| Match documents | MVP | Includes constraint-compliant preparation. Merging or generating documents excluded. |
| Fill text fields | MVP | Routine fields above threshold, visibly marked and reversible. |
| Handle dropdowns | MVP | Static and dependent lists. Search-based and async lists excluded. |
| Handle radio buttons | MVP | Single-choice, dropdown thresholds. |
| Handle checkboxes | MVP | Routine only. **Consequential checkboxes never set.** |
| Handle file uploads | MVP | Attachment after preview; approval required for sensitive documents. |
| Detect ambiguity | MVP | All four ambiguity conditions. |
| Ask the user | MVP | In-page, answerable without leaving the form. **Cross-session memory excluded.** |
| Protect sensitive information | MVP | Per-instance approval, never inherited. |
| Pause for approval | MVP | Individual approve or deny. **No bulk approval.** |
| Continue after approval | MVP | A denial does not end the session. |
| Review completed form | MVP | Full summary with sources and outstanding items. |
| Stop at submission | MVP | **Absolute. No exception.** |
| Multi-step forms | MVP | Treated as one application across steps. |
| Frames, multi-select, custom widgets, async lists, mobile, learning, receipts | FUTURE | Excluded — UC-031, UC-032, UC-038, UC-039, UC-040, UC-041 |

---

## 8. A dependency worth stating plainly

Step 3 §12.3 records that **every requirement in this document depends on assumption A-8** — that a browser
extension is an acceptable and reachable delivery mechanism. If A-8 fails, "the extension is the wrong surface
entirely", affecting all of FR-EXT, FR-FRM, FR-FLD, FR-FILL and FR-DRP.

Step 2 R-7 puts it more bluntly: if most applications are completed on phones, a browser extension reaches the
wrong surface. This flow is specified as though A-8 holds, because that is what Steps 1–3 direct — but it is the
highest-risk exclusion in the MVP, and Step 3 §12.2 says so: mobile support "is not a deferred feature but a wrong
primary surface" if A-8 fails.
