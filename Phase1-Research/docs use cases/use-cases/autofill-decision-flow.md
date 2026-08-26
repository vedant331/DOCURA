# Autofill Decision Flow

**Step 4 · Document 7 of 20** — The decision DOCURA makes for **one field**, from first observation to a reversible
result.

**Use cases:** UC-016, UC-017, UC-019, UC-021, UC-022 · **Governing rules:** BR-001, BR-002, BR-003, BR-005,
BR-006, BR-009

---

## 1. The shape of the decision

```
OBSERVE → UNDERSTAND → MATCH → CONFIDENCE CHECK → SENSITIVITY CHECK → ACT OR ASK → VERIFY
```

The order matters and is not arbitrary. **Sensitivity is checked after confidence but before action**, because
AR-AGT-002 requires that "every agentic action shall be preceded by a threshold check (BR-001) *and* a sensitivity
check (BR-005)." Two of the gates — unknown meaning and consequential tier — sit even earlier, before matching
begins, because there is no point looking for a value for a field DOCURA must not touch.

## 2. Part 1 — Observe, understand, and the four gates

<!--DIAGRAM:06a-field-decision-gates-->

## 3. Part 2 — Confidence, sensitivity, act or ask, verify

<!--DIAGRAM:06b-field-decision-act-or-ask-->

---

## 4. Diagram key — node to requirement

| Node | Requirements |
|---|---|
| OBSERVE | FR-FLD-001, FR-FRM-004 |
| UNDERSTAND | FR-FLD-002, AR-AST-003 |
| Gate 1 · meaning above threshold? | FR-FLD-006 |
| UNKNOWN | FR-FLD-006, FR-FILL-007, BR-009, EC-008 |
| Gate 2 · declaration or consent? | FR-FLD-004, AR-DET-006 |
| CONSEQUENTIAL | BR-006, FR-REV-005 |
| MATCH | FR-INF-001, AR-AST-004 |
| Gate 3 · information present? | FR-AMB-001 |
| MISSING | FR-MATCH-005, BR-009, EC-005 |
| Gate 4 · sources conflict? | FR-INF-004, AR-DET-008 |
| CONFLICT | FR-INF-005, BR-004, EC-004 |
| Above the review threshold? | FR-OCR-006 |
| BELOW THE FLOOR | BR-002 |
| CONFIDENCE CHECK | FR-FILL-001, BR-001, AR-DET-004 |
| AMBIGUOUS | FR-AMB-001, BR-003 |
| SENSITIVITY CHECK | FR-FLD-003, AR-DET-005 |
| ASK FOR APPROVAL | FR-SENS-002/003, FR-APR-001, BR-005, BR-007 |
| ASK THE USER | FR-AMB-002 |
| DENIED or SKIPPED | FR-APR-003, FR-AMB-004 |
| ACT | FR-FILL-001/002, AR-AGT-001 |
| VERIFY | FR-FILL-003/004/008, FR-AUD-001, BR-010, BR-011 |
| REVERSIBLE | FR-FILL-005, BR-012, BR-015 |

---

## 5. The five branches, stated as rules

### HIGH CONFIDENCE → act
Exactly one candidate is at or above the automatic-action threshold, **both** confidences clear it, and the tier is
routine. DOCURA fills, reformatting to the field's declared constraints without changing meaning. The field is
marked DOCURA-filled, its source is inspectable, and the page's own input handling fires as if a person had typed.
*(FR-FILL-001/002/003/004/008, BR-001, BR-010, BR-011.)*

### LOW CONFIDENCE → ask, or refuse
Two different floors, with two different consequences:

| Floor | Rule | Consequence |
|---|---|---|
| **Review threshold** | BR-002 | The value is never used for automatic action, *however well it matches the field*. It does not get a second chance at fill time. |
| **Automatic-action threshold** | BR-001 | Both the field interpretation and the source value must clear it. Below it, the field is ambiguous. |

### AMBIGUOUS → stop and ask
More than one plausible answer exists. **DOCURA may not select the most likely candidate.** It halts on that field,
states the field, lists the candidates, identifies each candidate's source, and explains why it could not decide.
*(BR-003, FR-AMB-001/002.)* See [`ambiguity-flow.md`](ambiguity-flow.md).

### SENSITIVE → ask for approval
The tier is sensitive. Nothing is placed until the user approves **that specific disclosure**, having seen the
exact value and the field receiving it. Approval is never inherited across fields, forms, or sessions.
*(BR-005, BR-007, FR-SENS-002/003/005.)* See [`sensitive-information-flow.md`](sensitive-information-flow.md).

### UNKNOWN → leave it alone and say so
The meaning cannot be determined with sufficient confidence, or the information is simply absent. The field is left
untouched and reported. **Guessing, inferring from similar fields, and filling with placeholder values are all
prohibited.** *(BR-009, FR-FLD-006, FR-FILL-007, EC-008.)*

---

## 6. The rule that governs all five

> **BR-009 · Unknown information.** Where DOCURA does not have reliable information, it must leave the field
> untouched and say so. Guessing, inferring from similar fields, and filling with placeholder values are all
> prohibited.

Every branch that does not end in *act* ends in *leave untouched and report*. There is no branch in which DOCURA
proceeds on a best effort. Step 3 §14 makes the same point for the whole edge-case catalogue: "In almost every case
the correct behaviour follows from BR-016: fail towards inaction and tell the user."

---

## 7. What "verify" means, and why it is a step

Filling is not finished when the value lands. Four things must be true afterwards, each from a separate requirement:

1. **It is visibly marked as DOCURA-filled**, distinguishable from user-entered values — BR-011, FR-FILL-003.
2. **Its source is inspectable** — the user can see which document the value came from — BR-010, FR-FILL-004.
3. **The page's own validation ran**, because filling triggered the form's input handling as if a person had typed —
   FR-FILL-008. Without this, a form's dependent behaviour would not fire and the value could be silently invalid.
4. **It is reversible** — the user may change or clear it, and DOCURA never overwrites it afterwards — BR-012,
   BR-015, FR-FILL-005.

Step 3 §12.2 explains why traceability is MUST rather than SHOULD: "Without it, a careful user re-verifies
everything and the time saving disappears (N-05). Traceability is what converts speed into trust."

---

## 8. Two cases the flow handles that are easy to miss

**Reformatting that would change meaning.** FR-FILL-002 requires values to be reformatted to satisfy declared
constraints — but adds: "where meaning would change, the field shall be treated as ambiguous." A date reformatted
between conventions is fine; a name truncated to fit a length limit is not. The flow routes this back to the
ambiguity branch rather than filling a mangled value.

**The same attribute requested twice in one form — EC-019.** Both occurrences are filled consistently from the same
authoritative value. If the user then overrides one, the change is **not** propagated silently to the other; the
divergence is flagged at review. Silent propagation would violate BR-012 by making a decision on the user's behalf
in a field they did not touch.
