# Final Review & Submission Flow

**Step 4 · Document 13 of 20** — One verifiable summary, then a full stop.

**Use cases:** UC-025, UC-026 · **Governing rule:** BR-008 *(non-negotiable)* · **Traces to:** P-07, S8, N-06

---

## USER SUBMITS — DOCURA DOES NOT SUBMIT.

> **BR-008 · Final submission.** DOCURA never submits a form and never operates a submit control. Submission is
> always performed by the user.

**FR-SUB-001** removes every escape hatch: "Under no confidence level, setting, or user preference may submission be
automated." **FR-SUB-002** removes the mechanism: DOCURA "shall not activate, click, or otherwise operate the form's
submit control." **AR-AGT-004** removes it again at the automation layer: no agentic action "shall navigate, submit,
dismiss a dialog, or otherwise alter the state of the page beyond the field it is filling."

---

## 1. The flow

<!--DIAGRAM:12-review-submission-->

---

## 2. What the review summary must show

Step 3 §1.17 defines six obligations. The order below is the order the summary presents them, because FR-REV-004
requires outstanding items **first**.

| Order | Content | Requirement | Brief's term |
|---|---|---|---|
| 1 | **Every required field that is unfilled, skipped, or unresolved** — prominently and first, visually distinct | FR-REV-004, AC-US-014-2, AC-US-010-5 | Any unresolved issues |
| 2 | **Declarations and consent controls that remain uncompleted** — identified, *not* completed | FR-REV-005, AC-US-013-3 | — |
| 3 | **Every field**: the value present, **how it got there** (automatic, answered, approved, or user-entered), and its source document where applicable | FR-REV-002, AC-US-014-1 | Fields filled |
| 4 | **Every document attached, and the field it was attached to** | FR-REV-003, AC-US-014-3 | Documents attached |
| 5 | **Ambiguities resolved** — visible as fields whose method is *answered* | FR-REV-002, FR-AUD-002 | Ambiguities resolved |
| 6 | **Sensitive approvals** — every approval request and its outcome | FR-AUD-003, FR-APR-004 | Sensitive approvals |
| 7 | **What DOCURA could not complete** — unknown fields, unsupported field types, missing documents | FR-REV-004, EC-005, EC-010 | Actions DOCURA could not complete |

Every entry is navigable: selecting it brings the corresponding field into view in the form (FR-REV-006,
AC-US-014-4).

The "how it got there" column is the one that does the most work. Step 3 §12.2 explains why traceability is MUST:
"Without it, a careful user re-verifies everything and the time saving disappears (N-05). Traceability is what
converts speed into trust." Step 2 S8 describes what it replaces: "the user is proofreading their own typing."

---

## 3. The hand-back

| Step | Obligation | Requirement |
|---|---|---|
| DOCURA hands control back with a clear statement that **submission is theirs to perform** | FR-SUB-003 | AC-US-015-1 |
| DOCURA takes **no submission action itself** | FR-SUB-001 | AC-US-015-1 |
| DOCURA does not activate, click, or otherwise operate the submit control | FR-SUB-002 | AC-US-015-2 |
| DOCURA records that the session **reached the hand-back point** | FR-SUB-004 | AC-US-015-3 |
| DOCURA records **no claim about whether the user submitted** | FR-SUB-004 | AC-US-015-3 |

That last line is a deliberate epistemic limit. DOCURA stops before the submit control, so it **cannot know**
whether submission occurred — and Step 3 requires it not to pretend otherwise. Claiming a submission it did not
observe would violate BR-019 (no absolute claims) and misrepresent an action the user alone performed.

*Detecting a confirmation or receipt page and offering to save it is FR-SUB-005 — **FUTURE** (UC-032). It is the
only pain from Step 2 (P-11) deliberately deferred in full.*

---

## 4. Editing during review

Review is not read-only. BR-015 requires that **every automated action be reversible by the user before
submission**, and the review summary is where that happens.

| The user… | What happens | Requirement |
|---|---|---|
| Edits a DOCURA-filled value | Re-marked **user-entered**; never overwritten again; override recorded with old and new values | FR-FILL-005/006, BR-012, AC-US-018-1…3 |
| Completes a declaration themselves | Recorded as a user action. DOCURA took no part | BR-006, AC-US-013-3 |
| Adds a missing document manually | The summary reflects it; DOCURA does not need to re-derive the whole form | FR-REV-004 |
| Navigates to a field from a review entry | The field is brought into view | FR-REV-006, AC-US-014-4 |
| Finds the same attribute diverging in two fields — EC-019 | Flagged here, **not** silently propagated | FR-REV-002, BR-012 |

---

## 5. Four ways the session can end without a hand-back

| Case | Behaviour | Requirement |
|---|---|---|
| **User stops DOCURA** | All activity ceases; placed values remain and are never reverted; a fresh activation is required to resume | FR-EXT-006, AC-US-016-1…3 |
| **User signs out or uninstalls — EC-017** | Activity ceases at once. **DOCURA does not clean up the user's form** | FR-EXT-006, NFR-REL-001 |
| **Session expires mid-form — EC-016** | All automated action halts immediately; values in the form untouched; re-authentication required; nothing filled from a stale session | NFR-SEC-005, BR-016 |
| **User submits while DOCURA is mid-action — EC-018** | **DOCURA never blocks the user's submission.** Pending action is abandoned rather than applied to a submitted form, and the session ends | FR-SUB-002, BR-008 |

EC-018 is worth dwelling on: the user's authority to submit outranks DOCURA's work in progress. DOCURA does not
finish its action first, does not warn-and-block, and does not apply a queued value to a form that has already gone.

> Whether a hand-back is recorded in the EC-018 case is not specified in Steps 1–3 — see
> [Q4-10](questions-and-conflicts.md).

---

## 6. The promise this closes

Step 2 **P-07** — "anxiety that something was missed after submitting" — is high frequency, and "persists after the
task ends; rarely resolvable by the user." **N-06** is the need: justified confidence at the moment of submission.
US-014 states the outcome in the user's words: *"so that I can stop re-reading the form three times."*

And US-015 states why the stop is not merely a safety feature but the product's position:

> As an applicant, I want to be the one who presses submit, so that **the moment of commitment is mine and DOCURA
> cannot take it from me.**
