# Document Matching Flow

**Step 4 · Document 10 of 20** — From a form's upload slot to a previewed, constraint-compliant file — or to an
honest "you don't have this".

**Use case:** UC-020 · **Governing rules:** BR-001, BR-003, BR-005, BR-009, BR-013 · **Traces to:** P-03, P-05,
P-12, RC-3, S4

---

## 1. Why this is a distinct flow

Step 2 records two separate pains here. **P-03** — file format and size rejections — is high frequency and high
severity, and "often discovered at submission, under time pressure." **P-05** — uncertainty about which of several
similar documents is required — is the judgement problem: "provisional vs final, attested vs plain, consolidated vs
per-semester."

They need different treatments. P-03 is **fully mechanical**: Step 2 S4 calls document preparation "mechanical,
rule-based, and fully automatable with certainty", and Step 3 §12.2 calls FR-MATCH-006 "the largest certain win in
the MVP." P-05 is **fully a judgement call** and must be asked about. This flow keeps them apart.

Step 3 RC-3 states the design consequence: "Document preparation is part of the problem, not a separate utility.
Storing the original is not enough."

---

## 2. Part 1 — Requirement to chosen candidate

<!--DIAGRAM:09a-document-matching-selection-->

## 3. Part 2 — Preparation, approval, attachment

<!--DIAGRAM:09b-document-preparation-attachment-->

---

## 4. The required sequence

```
Form requirement → Determine required document → Search the vault
                 → Candidate documents → Match confidence → Branch
```

| Step | Obligation | Requirement |
|---|---|---|
| Determine the requirement | Which document this slot wants, and what format, size and dimension constraints it declares | FR-MATCH-001, FR-FRM-004, FR-FLD-005 |
| Search the vault | Every stored document that could satisfy it | FR-MATCH-001 |
| Rank candidates | A ranked candidate list **with confidences** — not a single answer | FR-MATCH-002, AR-AST-005 |
| Match confidence | Count how many clear the automatic-action threshold | BR-001, AR-DET-004 |

---

## 5. The four branches

### One high-confidence match → prepare
Exactly one candidate is at or above the threshold **and the document is not sensitive** — so it is proposed for
attachment (FR-MATCH-003, AC-US-011-1). Preparation follows: a copy meeting the declared format, size and
dimension constraints (FR-MATCH-006), produced deterministically (AR-DET-002). The user previews **exactly the file
that will be attached** before it goes anywhere (FR-MATCH-008).

### Multiple possible matches → ask
**Attach nothing.** The user is asked to choose, with each candidate "identified clearly enough to tell them apart"
(FR-MATCH-004, AC-US-011-3). That phrase is doing real work: showing two files both called *marksheet.pdf* is not
a choice. Distinguishing detail — semester, year, attested or plain, provisional or final — is what makes the
question answerable.

### No match → say so
The requirement is **reported as missing**, and **no other document is substituted** (FR-MATCH-005, BR-009,
AC-US-011-4, EC-005). It is named twice: in the readiness summary *before filling begins*, and again at review.
Telling the user early is the point — Step 2 S2 identifies discovering requirements late as a core failure.

### Wrong, expired, or invalid → never automatically
A wrong, superseded, or expired document is never used automatically; the choice returns to the user. Where several
documents of one type exist and one is designated **primary**, the primary is used for automatic action
(FR-DOC-006). Where none is designated, they are multiple plausible candidates and the user is asked.

*(Automatic detection that a document appears expired or superseded is FR-DOC-009 — **FUTURE**. In the MVP the user
designates the primary; DOCURA does not infer expiry.)*

---

## 6. Diagram key — node to requirement

| Node | Requirements |
|---|---|
| Determine the requirement | FR-MATCH-001, FR-FRM-004, FR-FLD-005 |
| Search the vault | FR-MATCH-001, FR-SRCH-001 |
| Rank the candidates | FR-MATCH-002, AR-AST-005 |
| How many above the threshold? | FR-MATCH-003, BR-001 |
| No match | FR-MATCH-005, BR-009, EC-005 |
| Named in the readiness summary | FR-INT-003, FR-REV-004 |
| Two or more plausible | FR-MATCH-004, BR-003 |
| Ask the user to choose | FR-MATCH-004, AC-US-011-3 |
| Correct version, not superseded? | FR-DOC-005/006, P-05 |
| Prepare a copy | FR-MATCH-006, AR-DET-002 |
| The original is never modified | FR-MATCH-007, BR-013 |
| Quality floor | FR-MATCH-010, EC-020 |
| Preview the exact file | FR-MATCH-008 |
| Per-instance approval | FR-MATCH-009, BR-005, BR-007, EC-011 |
| Denied | FR-APR-003, EC-011, EC-012 |
| Attach the copy | AR-AGT-001, BR-011, BR-015 |
| Recorded | FR-AUD-001, FR-REV-003 |

---

## 7. Where user approval is required

Approval is **not** required for every attachment. Step 3 is specific about when it is:

| Case | Approval required? | Rule |
|---|---|---|
| Routine document, one high-confidence match | **No** — but preview is still shown | FR-MATCH-003, FR-MATCH-008 |
| Document classified **sensitive** | **Yes — explicit, per-instance** | FR-MATCH-009, BR-005, EC-011 |
| Same sensitive document, a second field | **Yes, again.** Approval is never inherited | BR-007, FR-SENS-005 |
| Multiple candidates | A **choice**, not an approval — the user selects | FR-MATCH-004, BR-003 |

A denial leaves the field empty, is recorded, and **the session continues** (FR-APR-003, EC-011). The document is
not proposed again for that field in that session, and the remaining candidates or manual selection are offered
(EC-012).

---

## 8. Two invariants

**The stored original is never modified — BR-013.** "Preparing a copy shall never modify or replace the stored
original" (FR-MATCH-007). Every conversion, resize, compression and crop produces a copy. The user can always open
the original exactly as uploaded.

**Degrade is not an option — FR-MATCH-010, EC-020.** Where preparation cannot meet the constraints without
unacceptable quality loss, DOCURA **stops and tells the user** rather than attaching a degraded file, and offers
the original for manual handling. An illegible compressed marksheet that satisfies a size limit is a rejected
application, not a solved problem.

> **Open parameter:** the quality floor is *TBD — to be validated* (FR-MATCH-010). This flow specifies that a floor
> is enforced and what happens when it is breached — not its value.

*Assembling derived documents, such as merging several files into one, is FR-MATCH-011 — **FUTURE** (horizon H3).*
