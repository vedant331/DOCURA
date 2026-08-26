# Master End-to-End User Flow

**Step 4 · Document 4 of 20** — The complete DOCURA MVP journey, from a folder of scans to a form the user submits
themselves.

---

## 1. What this flow covers

Step 3 §10.1 defines fourteen steps the MVP must demonstrate end to end against the controlled mock MCA-style
application form. This flow is those fourteen steps, in order, with every decision point that can divert them.

```
USER → DOCURA APP → DOCUMENT UNDERSTANDING → BROWSER EXTENSION → MOCK MCA FORM
     → FIELD UNDERSTANDING → AUTOFILL → AMBIGUITY → DOCUMENT MATCHING
     → SENSITIVE APPROVAL → REVIEW → USER SUBMISSION
```

**Detail is delegated, not duplicated.** D1–D3 are expanded in [`document-lifecycle.md`](document-lifecycle.md);
the per-field triage in D7 is expanded in [`autofill-decision-flow.md`](autofill-decision-flow.md). Repeating them
here would create two places to maintain one obligation — the failure Step 3 §0.3 explicitly avoided.

---

## 2. The master flow

<!--DIAGRAM:03-master-end-to-end-flow-->

---

## 3. Diagram key — node to requirement

| Node | Use case | Requirements |
|---|---|---|
| D1 to D3 · Build the record | UC-006, UC-007, UC-008, UC-009 | FR-UPL-001…005, FR-OCR-001…008, FR-INF-001/002/007 |
| D4 · USER activates DOCURA | UC-013 | FR-INT-001, FR-EXT-003/005, BR-014 |
| D5 / D6 · Detect, enumerate, readiness summary | UC-014, UC-015 | FR-FRM-001…004, FR-FLD-007, FR-INT-002/003 |
| Required document missing? | UC-015, UC-020 | FR-MATCH-005, EC-005 |
| D7 · Interpret every field | UC-016 | FR-FLD-001/002/003/006, AR-AST-003, AR-DET-005 |
| Per field — which tier? | UC-016 | FR-FLD-003, BR-001, AR-DET-004 |
| ACT — fill, select, attach | UC-017, UC-018, UC-020 | FR-FILL-001…005, FR-DRP-001…003/006/008, FR-MATCH-001…008 |
| AMBIGUOUS — ask | UC-019 | FR-AMB-001…004, BR-003 |
| SENSITIVE — ask approval | UC-021 | FR-SENS-002/003, FR-APR-001…004, BR-005, BR-007 |
| CONSEQUENTIAL — never touched | UC-022 | FR-FLD-004, FR-DRP-007, BR-006 |
| UNKNOWN — left alone, reported | UC-016 | FR-FLD-006, FR-FILL-007, BR-009 |
| D13 · Review summary | UC-025 | FR-REV-001…005 |
| USER edits | UC-023 | FR-FILL-005/006, BR-012 |
| D14 · DOCURA STOPS | UC-026 | FR-SUB-001…003, BR-008 |
| USER SUBMITS | UC-026 | FR-SUB-002, BR-008 |

---

## 4. The five decisions that shape the journey

Everything distinctive about DOCURA happens at five branch points. Each is governed by a business rule that cannot
be configured away.

### 4.1 The confidence decision — BR-001

> An action may be taken automatically only when the confidence of **both** the field interpretation **and** the
> source value meets or exceeds the automatic-action threshold.

Two confidences, not one. A perfectly-read value in a poorly-understood field is not fillable, and neither is a
confidently-understood field with a doubtful value. Below the *review* threshold (BR-002), a value is not usable
automatically at all, however well it matches.

### 4.2 The ambiguity decision — BR-003

> Where more than one reasonable value, option, or document exists, DOCURA **must ask** the user. It may not select
> the most likely candidate on the user's behalf.

This is the branch that separates DOCURA from an autonomous form-filler. The flow shows it as a stop, not a
fallback: automatic action on that field halts, and resumes only with a human answer.

### 4.3 The sensitivity decision — BR-005 and BR-007

> Sensitive information is never disclosed to a form without explicit approval for that specific disclosure.
> An approval applies to exactly one disclosure, in one field, in one form, in one session.

The flow therefore shows approval as a *per-field event*, not a session gate. Approving the government identifier
for one field does not approve it for the next one.

### 4.4 The consent boundary — BR-006

> DOCURA never accepts a legal declaration, agreement, or consent control. This applies at every confidence level
> and admits no setting, exception, or user preference.

Note where this sits in the flow: consequential fields bypass the whole confidence and sensitivity machinery. There
is no confidence high enough to reach them.

### 4.5 The submission stop — BR-008

> DOCURA never submits a form and never operates a submit control. Submission is always performed by the user.

The terminal node reads **USER SUBMITS — DOCURA DOES NOT SUBMIT**, and DOCURA's own final node is a full stop.

---

## 5. What the flow deliberately does not show

| Not shown | Why |
|---|---|
| A "fill everything" or "auto-submit" path | No such path exists. AR-AGT-006: the product shall not offer an autonomous mode in which the user is absent from the loop. |
| A confidence value or percentage | Every threshold in Step 3 is *TBD — to be validated*. Showing a number would invent one. |
| Cross-session memory of answers | FR-AMB-008 is FUTURE. Every session starts from the record, not from history (Step 3 §10.3). |
| A retry loop that eventually guesses | BR-009 and BR-016: where DOCURA lacks reliable information it leaves the field untouched and says so. Guessing, inferring from similar fields, and placeholder values are all prohibited. |
| Anything after submission | FR-SUB-005 (receipt capture) is FUTURE. DOCURA's world ends at the submit control. |

---

## 6. Where time is saved and where confidence is restored

Step 2 §10 found these are **not the same stages** — "a product that only saves time will not resolve the anxiety,
and a product that only reassures will feel slow." The master flow addresses both, and they are measured separately.

| Current-state stage | Pain | Where this flow addresses it |
|---|---|---|
| S3 · Document gathering | P-01 — cannot find the right version | D1–D3, and search (UC-012) |
| S4 · Document preparation | P-03, P-12 — format and size rejections | D10 — constraint-compliant copies (UC-020) |
| S5 · Data entry | P-02, P-04 — re-entry and dropdown mismatch | D7, D8 (UC-017, UC-018) |
| S6 · Ambiguity resolution | P-04, P-05 — guessing introduces disqualifying errors | D9 — ask, don't guess (UC-019) |
| S7 · Declarations | P-10 — signing without reading | D12 — deliberately **not** made faster (UC-022) |
| S8 · Review and submit | P-07 — anxiety, proofreading one's own typing | D13 — one verifiable summary (UC-025) |

Step 2's note on P-10 is worth repeating: users do not experience it as pain, "but it is where automation would do
the most harm — it is in scope because of our philosophy, not because of demand."
