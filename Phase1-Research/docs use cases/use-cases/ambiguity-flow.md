# Ambiguity Flow

**Step 4 · Document 9 of 20** — What happens when more than one reasonable answer exists.

**Use case:** UC-019 · **Governing rule:** BR-003 · **Traces to:** P-04, P-05, S6, L3, A-2

---

## 1. The critical rule

> **BR-003 · Ambiguity.** Where more than one reasonable value, option, or document exists, DOCURA **must ask** the
> user. It may not select the most likely candidate on the user's behalf.

This is the rule Step 2 identified as the distinguishing job: "autofill and autonomous agents treat consent as
friction to be minimised. Treating control as a job to be served — rather than an obstacle to be reduced — is what
makes DOCURA a different product rather than a better one." Step 3 §4.2 puts the cost concretely: "On applications
with deadlines and legal declarations, a confident guess is worse than a question."

---

## 2. The flow

<!--DIAGRAM:08-ambiguity-handling-->

---

## 3. The four conditions that trigger it

FR-AMB-001 defines ambiguity as **any** of four conditions. They are not variations on one thing — each has a
different cause and, importantly, they do not all produce the same response.

| # | Condition | Cause | Response |
|---|---|---|---|
| 1 | Multiple candidate values or options are plausible | Two certificates, two option matches, two documents | **Ask** — present the candidates |
| 2 | Confidence is below the automatic-action threshold | Poor scan, unfamiliar label, weak semantic match | **Ask** if candidates exist |
| 3 | Source documents conflict | The user's own records disagree — BR-004 | **Ask** — present both values and their sources |
| 4 | The required information is absent | Nothing in the record answers this field | **Report as missing** — there is nothing to ask about |

> **Condition 4 behaves differently, and Steps 1–3 do not fully reconcile this.** FR-AMB-001 classes absence as
> ambiguity, but FR-AMB-002 requires an ambiguity prompt to "state the field, the candidates, the source of each
> candidate" — and absence has no candidates. BR-009 and EC-005 resolve it in practice: report it as missing,
> substitute nothing. This flow follows BR-009, since Step 3 §5 states that where a requirement and a rule appear to
> conflict, **the rule governs**. Recorded as [Q4-08](questions-and-conflicts.md).

---

## 4. The required sequence

```
Detect ambiguity → Stop automatic action → Explain → Present choices
                 → User chooses → Record decision → Continue
```

| Step | Obligation | Requirement |
|---|---|---|
| **Detect** | Any of the four conditions | FR-AMB-001 |
| **Stop** | Automatic action on that field halts. Nothing is placed, nothing is selected. | BR-003, AR-AGT-005 |
| **Explain** | State the field · list the candidates · identify **the source of each** · say **why DOCURA could not decide** | FR-AMB-002, AC-US-010-1 |
| **Present** | Answerable **in place**, without leaving the form page; operable by keyboard alone; announced to assistive technology without stealing focus | NFR-USE-003, NFR-A11Y-002, NFR-A11Y-004 |
| **Choose** | The user picks, supplies another value, or skips | FR-AMB-003, FR-AMB-004 |
| **Record** | Question and answer written to history; history is not user-editable | FR-AUD-002, FR-AUD-005 |
| **Continue** | The answer applies for the rest of **this session**, and the field is marked *answered* rather than *automatic* | FR-AMB-006, FR-REV-002 |

Ambiguities are **grouped and presented together** where doing so does not delay filling of unaffected fields
(FR-AMB-005) — so the user answers a short batch rather than being interrupted field by field.

---

## 5. Diagram key — node to requirement

| Node | Requirements |
|---|---|
| Four trigger conditions | FR-AMB-001 |
| Stop automatic action | BR-003, AR-AGT-005 |
| Are there candidates to present? | FR-AMB-002, BR-009 |
| Nothing to choose between | BR-009, EC-005, EC-008 |
| Explain the ambiguity | FR-AMB-002, AC-US-010-1 |
| Grouped with other open questions | FR-AMB-005 |
| Present the choices | NFR-USE-003, NFR-A11Y-002 |
| Supplies a value not offered | FR-AMB-003, AC-US-010-2 |
| Skips the question | FR-AMB-004, AC-US-010-3 |
| Stops DOCURA entirely | FR-EXT-006 |
| Record the decision | FR-AUD-002, FR-AUD-005 |
| Apply the answer | FR-REV-002, BR-010 |
| Reused in the same session only | FR-AMB-006, AC-US-010-4 |
| Left unfilled — outstanding | FR-AMB-004, FR-AMB-007 |
| Listed first at review | FR-REV-004, AC-US-010-5 |

---

## 6. The four ways a user can respond

The brief asks specifically about rejection, cancellation, and a different value. All four are specified:

**They pick a candidate.** Applied, recorded, marked *answered*, and not asked again this session.

**They supply a value that was not offered.** Accepted and used (FR-AMB-003, AC-US-010-2). The candidate list is a
convenience, not a constraint — DOCURA's inability to find the right answer does not limit the user to its guesses.

**They reject every candidate, or skip.** The field is left unfilled and listed in the review summary as
outstanding (FR-AMB-004, AC-US-010-3). If it is a **required** field, DOCURA does not proceed past it silently: it
is recorded as outstanding (FR-AMB-007) and listed **first and visually distinct** at review (FR-REV-004,
AC-US-010-5).

**They cancel — stopping DOCURA entirely.** All activity ceases; values already placed **remain and are never
reverted** (FR-EXT-006, AC-US-016-2). → UC-024.

In every case, **one unanswered question never blocks the rest of the session.** FR-APR-003 says the same for
denials: a denial "shall not block the remainder of the session."

---

## 7. Scope of an answer

| Scope | Rule | Release |
|---|---|---|
| The same question, later in the **same session** | Not asked again — FR-AMB-006 | MVP |
| The same question in **another form or session** | **Asked again.** Every session starts from the record, not from history | MVP (§10.3) |
| Making an answer permanent | FR-AMB-008 — **FUTURE**, UC-031 | Excluded |

Step 3 §12.2 explains why the permanent case is deferred rather than cheap: "Attractive and dangerous: remembering
an answer is a form of assumed consent. It requires the sensitivity boundary from A-5 first."

Note the asymmetry with approvals, which is deliberate: an **ambiguity answer** may be reused within a session
(FR-AMB-006), but an **approval** may not be reused at all (BR-007, FR-SENS-005). Answering a question is not the
same act as consenting to a disclosure.

---

## 8. The assumption underneath this flow

Assumption **A-2** — "being asked at ambiguous points is experienced as trustworthy, not as the product failing" —
is untested, and Step 2 rates the damage if it is wrong as **fatal**. Step 3 §12.3 lists all of FR-AMB and
FR-APR-001 as dependent on it: if A-2 fails, "asking is experienced as failure; the ambiguity model needs redesign,
not adjustment."

Two counter-pressures are already recorded and are the reason FR-AMB-005 (grouping) exists: risk **R-3**,
interruption fatigue — "if the sensitivity boundary is set too cautiously, asking becomes nagging and the product
feels slower than typing" — and NFR-USE-002, which caps interruptions at the number of genuinely ambiguous or
sensitive items, with the budget itself *TBD*, to be set by study S-4.
