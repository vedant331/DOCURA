# Sensitive Information Flow

**Step 4 · Document 11 of 20** — Explicit, scoped, per-instance approval before anything sensitive reaches a form.

**Use case:** UC-021 · **Governing rules:** BR-005, BR-007, BR-020 · **Traces to:** N-07, Step 2 §13.2, A-5, R-1

---

## 1. The classification this flow uses

Step 2 §13.2 supplies a three-tier working classification, and Step 3 FR-INF-007 / FR-SENS-001 make it a
requirement for both stored attributes and detected form fields. **No new classification system is invented here** —
this is the one Steps 1–3 already carry.

| Tier | Examples given in Step 2 §13.2 | Expected behaviour |
|---|---|---|
| **Routine** | Name, date of birth, education history, marks, addresses already public on the application | Fill it silently. Asking each time is experienced as friction, not care. |
| **Sensitive** | Government identifier numbers, bank details, signature images, category and income details | **Show it, confirm it, then fill it.** Never place it without an explicit action. |
| **Consequential** | Legal declarations, agreements, affidavit-style statements, final submission | **Never automated under any confidence level.** The user performs the act themselves. → [`legal-consent-flow.md`](legal-consent-flow.md) |

The examples the brief mentions — PAN, Aadhaar, other identity information, sensitive documents — fall under
"government identifier numbers" and Step 3 §7.1's identity document set. They are examples of an existing tier, not
a new taxonomy.

> **This boundary is the most important unresolved question in Step 2.** §13.2: "The boundary between routine and
> sensitive … determines how often DOCURA interrupts. Interrupt too often and the product is slower than typing;
> interrupt too rarely and it violates the principle it was built on. **This boundary must be set by users, not by
> us** — it is assumption A-5." Step 3 §12.3 lists all of FR-SENS-001…006 and NFR-USE-002 as dependent on it.

---

## 2. The flow

<!--DIAGRAM:10-sensitive-approval-->

---

## 3. The required sequence

```
Detect sensitive request → Stop automatic disclosure → Show what is being requested
→ Show source → Ask user → User approves OR rejects → Continue appropriately
```

| Step | Obligation | Requirement |
|---|---|---|
| **Detect** | The field or document is classified sensitive — **before any value is placed in it** | FR-FLD-003, FR-SENS-001 |
| **Stop** | Sensitive information is never placed into a form without explicit approval for **that specific disclosure** | FR-SENS-002, BR-005, AC-US-012-1 |
| **Show what** | The approval request shows the **exact value or document** to be disclosed | FR-SENS-003, AC-US-012-2 |
| **Show where** | …and **the field receiving it** | FR-SENS-003, AC-US-012-2 |
| **Show why** | Every approval request states what will happen, where, and **why DOCURA is asking rather than acting** | FR-APR-001 |
| **Show source** | The value's source document is traceable | FR-INF-002, BR-010 |
| **Ask** | The user approves or denies **each request individually** | FR-APR-002 |
| **Record** | Approvals and denials are recorded in the session history **with their subject** | FR-APR-004, FR-AUD-003 |
| **Continue** | A denial leaves the field untouched and **does not block the remainder of the session** | FR-APR-003, AC-US-012-3 |

While in DOCURA's own interface, sensitive values are **masked by default** and revealed only on user action
(FR-SENS-004).

---

## 4. What "explicit, scoped, session-bound" means here

The brief asks that approval be explicit, scoped, and session-bound where the requirements support it. Step 3 is
stricter than session-bound — BR-007 states the scope precisely:

> **BR-007 · Scope of approval.** An approval applies to **exactly one disclosure, in one field, in one form, in one
> session.** Approval is never inherited, remembered, or generalised.

| Dimension | Scope of one approval |
|---|---|
| Which value | That one |
| Which field | That one |
| Which form | That one |
| Which session | That one |

So the same government identifier requested in a second field on the **same** form requires a **second** approval
(FR-SENS-005, AC-US-012-4). This is a deliberate difference from ambiguity answers, which *may* be reused within a
session (FR-AMB-006). Answering a question is not the same act as consenting to a disclosure.

**There is no "always allow".** FR-APR-005: "No control shall exist that approves consequential items in bulk or in
advance." Step 3 §10.3 lists bulk approval among the explicit MVP exclusions, and §12.2 explains the deferral:
reviewed bulk approval "would reduce interruption fatigue (R-3), but **relaxes BR-007**. Deferred until interruption
cost is measured rather than assumed." Even the future version (FR-APR-006, UC-035) requires the user to see each
item first.

---

## 5. Interaction with EC-019 — the same attribute twice in one form

EC-019 requires that where the same attribute is requested twice in one form, both are filled consistently from the
same authoritative value. For a **sensitive** attribute this appears to collide with BR-007, which requires a fresh
approval per field.

Step 3 §5 settles it: *"Where a requirement and a rule appear to conflict, the rule governs."* So **two approvals
are requested**, and consistency in EC-019 means both fields receive the same value — not that one approval covers
both. Recorded as [Q4-02b](questions-and-conflicts.md) because the interaction is derived rather than stated.

---

## 6. The trust sequence this flow protects

Step 2 §13.1 records that users evaluate trust repeatedly, in order — and that "trust is granted incrementally and
**withdrawn instantly**. A single unexpected autofill of a sensitive field can end adoption permanently, regardless
of how correct every prior action was."

| When | What the user is asking | Where this flow answers it |
|---|---|---|
| Before uploading anything | Who can see this? Where does it go? | NFR-PRIV-006 — off-device processing disclosed before the first upload |
| On first automated action | Did it do exactly what I expected, and can I see why? | BR-010, BR-011 — traceable and visibly marked |
| **On the first sensitive field** | **Did it ask me, or did it decide for me?** | **This flow. BR-005.** |
| On the first mistake | Was it visible and correctable, or did I find it later? | NFR-REL-004, BR-012, BR-015 |

Risk **R-1** — the cold-start trust barrier — is why the product must be valuable before the vault is fully
populated (NFR-USE-004), and why this flow must never trade an interruption for a surprise.

---

## 7. Raising, and never lowering

The user may **raise** an attribute's sensitivity (FR-SENS-006, UC-028). Nobody may lower a consequential
classification — not the user, not an administrator, not a future enterprise customer (BR-020). Assisted components
carry the same asymmetry: they "may add a sensitivity classification, never remove one" (AR-AST-007).

*Warning when a form requests an unusual combination of sensitive information is FR-SENS-007 — **FUTURE**. Step 3
records this as ASM-006: a refinement, not a baseline safety requirement, to be reconsidered before public release.*
