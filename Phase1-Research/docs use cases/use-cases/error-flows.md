# Error & Exception Flow Catalogue

**Step 4 · Document 14 of 20** — All twenty edge cases of Step 3 §14, specified as behaviour, with detection,
response, notification, recovery, and whether automation continues.

**Governing rule:** BR-016 — fail towards inaction.

---

## 1. The generic path

Every failure runs through the same five obligations before it reaches its specific handling.

<!--DIAGRAM:13-error-handling-->

| Obligation | Rule |
|---|---|
| **Fail towards inaction.** When any component fails or is uncertain, do nothing and inform the user — never proceed on partial information. | BR-016, NFR-ERR-002 |
| **Protect what is already there.** A failure in any DOCURA component shall never corrupt, clear, or alter data the user has already entered into a form. | NFR-REL-001 |
| **Surface at the point of failure.** Where DOCURA cannot complete an action, the failure is visible **at the point of failure, not discovered later at review**. | NFR-REL-004 |
| **Say what to do next.** Every error message states what went wrong and what the user can do next. Messages that only apologise or restate failure are not acceptable, and none exposes internal identifiers, stack traces, or infrastructure detail. | NFR-ERR-001, NFR-ERR-004 |
| **Report partial as partial.** Itemise what succeeded and what did not. Where an operation is retryable, offer the retry **in place** rather than making the user start over. | NFR-ERR-003, NFR-ERR-005 |

---

## 2. The twenty edge cases

Columns: **Detection** — how DOCURA knows. **Response** — what it does. **Notification** — what the user is told.
**Recovery** — how it is fixed. **Automation** — continues or stops.

### 2.1 Document intake and understanding

| ID | Situation | Detection | DOCURA's response | Notification | Recovery | Automation |
|---|---|---|---|---|---|---|
| **EC-001** | OCR fails entirely | Extraction produces nothing usable | **Retain the original**; mark the document *failed* with a stated reason | Reason stated on the document; both retry **and manual entry** offered | Retry, or the user enters information manually | Document remains stored and **searchable by label** |
| **EC-002** | Poor-quality document | Per-field confidence below the review threshold | Extract what is legible; mark low-confidence fields for review | Tell the user **which fields** could not be read confidently. Never present a low-confidence value as settled | User corrects the flagged values | Continues — but those values are **withheld from automatic filling** (BR-002) |
| **EC-003** | Wrong document uploaded | Classification confidence low, or type mismatch | Classify honestly. If the type is clear, store it as that type. If unclear, store as **unclassified** and ask. **Never force it into an expected slot** | The user is asked to identify it | User assigns the type | Continues |
| **EC-004** | Documents conflict | Deterministic conflict detection (AR-DET-008) | Raise a conflict; mark **neither** authoritative | The disagreement is shown with each value and its source | User resolves; alternatives retained | Any field needing that attribute is **treated as ambiguous** until resolved |

### 2.2 Documents in a form session

| ID | Situation | Detection | DOCURA's response | Notification | Recovery | Automation |
|---|---|---|---|---|---|---|
| **EC-005** | Required document missing | No candidate satisfies the upload field | Report as missing. **Never substitute a different document** | Named in the **readiness summary before filling begins**, and again at review | User uploads it, or attaches manually | Continues on other fields |
| **EC-011** | Sensitive document requested | Document classified sensitive | Prepare and preview, then **stop**. Attach only on explicit per-instance approval | Approval request shows the exact file and the receiving field | User approves or denies | A denial leaves the field empty and **the session continues** |
| **EC-012** | User rejects a suggested document | User declines the proposal | Do not attach it; **do not propose it again for that field in that session** | Remaining candidates or manual selection offered | User picks another or attaches manually | Continues |
| **EC-020** | Prepared document falls below the quality floor | Constraints cannot be met without unacceptable loss | **Attach nothing.** Do not degrade | Explain why; offer the original for manual handling | User handles it manually | That field only; the session continues |

### 2.3 Fields and matching

| ID | Situation | Detection | DOCURA's response | Notification | Recovery | Automation |
|---|---|---|---|---|---|---|
| **EC-006** | Multiple dropdown matches | Two or more options above the threshold | **Select nothing.** Ask | Each candidate shown **with why it was considered** | User chooses, or supplies another value | Continues after the answer |
| **EC-007** | No dropdown option matches | No option acceptable | Leave unset | Report as needing attention; **offer the option list** to choose from directly | User picks from the list, or skips | Continues |
| **EC-008** | Unfamiliar terminology | Interpretation confidence below threshold | Mark the field **unknown** and leave it untouched — **never guessed from a superficially similar label** | Listed at review as requiring the user | User fills it manually | Continues |
| **EC-010** | Unsupported field type | Type outside the MVP seven | Enumerate it, mark it unsupported, **exclude it from filling** | Listed in review as requiring the user | User fills it manually | Continues |
| **EC-019** | Same attribute requested twice | Two fields map to one attribute | Fill both consistently from the same authoritative value. If the user overrides one, **do not propagate silently** | The divergence is **flagged at review** | User reconciles | Continues |

### 2.4 The page changing underneath

| ID | Situation | Detection | DOCURA's response | Notification | Recovery | Automation |
|---|---|---|---|---|---|---|
| **EC-009** | Website structure changes between sessions | Every activation derives mappings fresh | **Re-derive field mappings from scratch on each activation.** Stored mappings are never trusted across sessions | — (normal operation) | — | Continues |
| **EC-015** | Form changes while filling | Structural change detected mid-session | Detect the change, re-examine the form, **discard stale mappings**. Never apply a mapping to a field that has moved | Inform the user that the form changed | Re-derived automatically | Continues after re-derivation |

### 2.5 Session and connectivity

| ID | Situation | Detection | DOCURA's response | Notification | Recovery | Automation |
|---|---|---|---|---|---|---|
| **EC-014** | Network failure mid-session | Transport loss | **Stop initiating new actions.** Preserve everything already placed. **Never leave a field half-filled** | Show a clear degraded state — not a silent failure | Resume **only on explicit user action** | **Stops** until the user resumes |
| **EC-016** | Session expires mid-form | Session validity check | **Halt all automated action immediately.** Values already in the form are left untouched | Re-authentication required | User re-authenticates, then re-activates | **Stops.** Nothing is filled from a stale session |
| **EC-017** | User signs out or uninstalls | Extension loses its account binding | Cease all extension activity at once. Values already placed **remain in the page — DOCURA does not clean up the user's form** | — | Fresh install / sign-in and re-activation | **Stops** |
| **EC-018** | Form submitted while DOCURA is mid-action | Submission observed | **DOCURA never blocks the user's submission.** Any pending action is **abandoned** rather than applied to a submitted form | — | — | **Stops.** The session ends |

### 2.6 User-initiated

| ID | Situation | Detection | DOCURA's response | Notification | Recovery | Automation |
|---|---|---|---|---|---|---|
| **EC-013** | User changes an automatically filled value | Field edited by the user | Re-mark the field **user-entered**; **never overwrite it afterwards** | Override recorded in history with old and new values | — | Continues |
| *(user denial)* | User denies a sensitive disclosure | Approval denied | Field left untouched; denial recorded | Listed at review as outstanding | User may fill it manually | **Continues** — a denial never blocks the session (FR-APR-003) |
| *(user cancellation)* | User stops DOCURA | Stop requested | All activity ceases; placed values remain and are never reverted | — | **Fresh activation required** | **Stops** |

---

## 3. Where automation goes after a failure

Grouping the twenty cases by blast radius is what makes the catalogue usable:

| Scope | Edge cases | Outcome |
|---|---|---|
| **This field only** — automation continues | EC-002, EC-003, EC-005, EC-006, EC-007, EC-008, EC-010, EC-012, EC-013, EC-019, EC-020 | The field is left alone and reported; the rest of the session proceeds |
| **The form model is stale** — re-derive, then continue | EC-009, EC-015 | Mappings discarded and rebuilt |
| **The session halts** | EC-014, EC-016, EC-017, EC-018 | Nothing further is initiated; placed values remain |
| **The document, not the session** | EC-001, EC-004 | The user resolves it in the vault |
| **The consent boundary** | EC-011 | The user decides; the session continues either way |

---

## 4. Recovery behaviour that would be unsafe — and is therefore excluded

The brief asks that no unsafe recovery be designed. These are the recoveries that were available and deliberately
not used, each with the rule that forbids it:

| Tempting recovery | Why it is unsafe | Forbidden by |
|---|---|---|
| Retry with a lowered confidence threshold | Turns a refusal into a guess | BR-001, BR-009 |
| Pick the highest-ranked candidate after the user skips | Converts an unanswered question into a decision made for them | BR-003 |
| Substitute a similar document when the right one is missing | The wrong document invalidates the application | BR-009, FR-MATCH-005 |
| Compress harder to meet a size limit | An illegible file is a rejected application | FR-MATCH-010, EC-020 |
| Re-apply cached field mappings after a page change | Applies a mapping to a field that has moved | FR-FRM-007, EC-015 |
| Continue filling on a stale session after expiry | Acts without a valid authorisation | NFR-SEC-005, EC-016 |
| Clear or revert fields on failure to "leave things clean" | Destroys the user's own work | NFR-REL-001, EC-017 |
| Finish the pending action before honouring a submit | Applies a value to a form that has already gone | EC-018, BR-008 |
| Carry a sensitive approval forward to save an interruption | Consent inherited is consent assumed | BR-007 |
| Save the failure up and report it at review | Discovery too late to act on | NFR-REL-004 |

---

## 5. What the user is always guaranteed after any failure

1. **Nothing they typed was touched.** — NFR-REL-001
2. **No field was left half-filled.** — EC-014
3. **The original document still exists.** — FR-OCR-009, NFR-REL-002
4. **They were told at the moment it happened, not at review.** — NFR-REL-004
5. **They were told what to do next.** — NFR-ERR-001
6. **Nothing was guessed to paper over the gap.** — BR-009, BR-016
