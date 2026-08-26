# Legal Declaration & Consent Flow

**Step 4 · Document 12 of 20** — The boundary automation never crosses.

**Use case:** UC-022 · **Governing rule:** BR-006 *(non-negotiable)* · **Traces to:** P-10, S7, Vision §7

---

## 1. The rule

> **BR-006 · Consent and declarations.** DOCURA never accepts a legal declaration, agreement, or consent control.
> This applies at **every confidence level** and admits **no setting, exception, or user preference.**

Step 3 §5 places BR-006 in the **non-negotiable set** with BR-008 and BR-009:

> A future request to relax any of them — for a partner, an enterprise buyer, or a conversion metric — is a request
> to change the product's identity, and must be escalated as such rather than handled as a configuration change.

Step 1 §07 states the same boundary as product philosophy: consent is "structurally excluded from automation. This
is a boundary in the product's architecture, not a setting in its preferences."

---

## 2. The flow

<!--DIAGRAM:11-legal-consent-->

---

## 3. The required sequence

```
DOCURA detects legal/consent action → DOCURA does not accept it
→ User is informed → USER performs the action manually
```

| Step | Obligation | Requirement |
|---|---|---|
| **Detect** | Identify legal declarations, agreements, and consent controls | FR-FLD-004 |
| **Detect deterministically** | Deterministic rules are the **primary mechanism** | AR-DET-006 |
| **Never downgrade** | Assisted interpretation is only an additional safeguard — it may **add** the consequential classification, **never remove** it | AR-DET-006, AR-AST-007 |
| **Classify** | Mark the control consequential — and it can never be reclassified downward by any actor | FR-FLD-004, BR-020 |
| **Do not act** | DOCURA does not alter it under any circumstance | BR-006, AC-US-013-1 |
| **Offer no setting** | No setting to automate declarations exists in the product | AC-US-013-2 |
| **Inform** | The control is identified and shown to the user | FR-REV-005 |
| **List at review** | Uncompleted declarations and consent controls are identified **without being completed** | FR-REV-005, AC-US-013-3 |
| **Hand over** | The user performs the action themselves | US-013 |

---

## 4. Diagram key — node to requirement

| Node | Requirements |
|---|---|
| DOCURA enumerates the form fields | FR-FRM-002 |
| Deterministic rules detect declarations | AR-DET-006 |
| Assisted interpretation may only ADD | AR-DET-006, AR-AST-007 |
| Declaration, agreement, or consent control? | FR-FLD-004 |
| Classify consequential | FR-FLD-004, BR-020 |
| DOCURA does not act | BR-006, AC-US-013-1 |
| No setting exists to automate it | FR-APR-005, AC-US-013-2 |
| Inform the user | FR-REV-005 |
| At review — listed as requiring the user | FR-REV-005, AC-US-013-3 |
| The user acts themselves | US-013 |

---

## 5. What DOCURA must not do

The brief lists three. All three are already prohibited by Steps 1–3, and this flow shows none of them:

| Must not | Rule |
|---|---|
| Tick legal declarations | BR-006, FR-DRP-007 — "checkboxes classified consequential shall never be set by DOCURA" |
| Accept consent | BR-006, FR-FLD-004 |
| Sign on behalf of the user | BR-006 — a signature on a declaration *is* accepting it |

Two further prohibitions follow from the same rule:

| Must not | Rule |
|---|---|
| Offer a setting, preference, or "expert mode" that enables any of the above | AC-US-013-2, FR-APR-005 |
| Approve consequential items in bulk or in advance | FR-APR-005 |

And one from the automation layer: **AR-AGT-006** — "The product shall not offer an autonomous mode in which the
user is absent from the loop."

---

## 6. Why detection is deterministic-first

AR-DET-006 is unusually specific, and the asymmetry is the whole point:

> Detection of declaration and consent controls shall use **deterministic rules as its primary mechanism**, with
> assisted interpretation only as an additional safeguard that can **add — never remove —** the consequential
> classification.

A probabilistic classifier that occasionally *misses* a declaration would let DOCURA tick a legal agreement, which
BR-006 forbids absolutely. A deterministic rule set that occasionally over-classifies merely asks the user to do
something themselves — the safe direction of error. Assisted interpretation is therefore allowed to widen the net
and forbidden to narrow it.

This is the same asymmetry as AR-AST-007: an assisted component "may lower a confidence, never raise it, and may
add a sensitivity classification, never remove one."

---

## 7. The user need this serves — and does not pretend to serve

Step 2 rates **P-10**, signing declarations without reading them, as **high frequency, medium severity** — and then
says something the flow must respect:

> P-10 is the outlier: users do not experience it as pain, but it is where automation would do the most harm — **it
> is in scope because of our philosophy, not because of demand.**

And on the journey stage S7:

> Legal exposure accepted without comprehension — a real risk, not merely a formality. **Deliberately unautomated.
> Opportunity is to make the moment clearer, never faster.**

So this flow's success criterion is not speed. DOCURA identifies the control, shows what it asks the user to agree
to, and stops. Making the moment *clearer* is permitted; making it *faster* is not the goal, and making it
*automatic* is prohibited.

Step 1 §05 states the promise this keeps: "DOCURA converts a person's documents into leverage, without ever
converting their consent into a default."
