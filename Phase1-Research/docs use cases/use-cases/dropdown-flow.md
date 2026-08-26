# Dropdown, Radio & Checkbox Flow

**Step 4 · Document 8 of 20** — Option matching, and the one rule that makes it different from every autofill tool.

**Use case:** UC-018 · **Governing rules:** BR-001, BR-003, BR-006, BR-009 · **Traces to:** P-04, RC-2

---

## 1. Why this needs its own flow

Step 2 identifies P-04 — "dropdown options that do not match the document's wording" — as **high frequency and high
severity**, and "a frequent source of silent, disqualifying mismatches." Root cause RC-2 explains why: there is no
shared vocabulary between forms. The same fact appears as "Father's Name", "Guardian Name", "Parent/Guardian", and
"Name of Father (as per 10th certificate)" across four portals.

Step 2 §14 records what existing autofill does here: "string matching only; no documents; **no dropdown reasoning**;
no confidence model." Matching options by meaning rather than by string equality is the specific gap DOCURA fills —
and the specific place where guessing does the most damage.

---

## 2. The flow

<!--DIAGRAM:07-dropdown-decision-->

---

## 3. Worked example

> **Department**  `[ Select ]`

| # | Step | What happens | Requirement |
|---|---|---|---|
| 1 | **Understand the field** | Derive that this field means *department / branch of study*, with a confidence and the ability to return "unknown". | FR-FLD-001/002, AR-AST-003 |
| 2 | **Identify the options** | Read **every** available option before attempting any match. Not the first plausible one — all of them. | FR-DRP-001 |
| 3 | **Compare with the record** | Match the user's stored value to an option **by meaning**, not by exact string equality. The certificate may say "Computer Engineering" where the form offers "CSE". | FR-DRP-002 |
| 4 | **Evaluate confidence** | Produce a **ranked candidate list with confidences** — never a single forced answer. | AR-AST-004 |
| 5 | **Decide** | Count how many options are at or above the automatic-action threshold. | BR-001, AR-DET-004 |

And then, exactly as the brief states it:

| Outcome | DOCURA's action | Requirement |
|---|---|---|
| **Exactly one high-confidence match** | **Select it** — marked DOCURA-selected, source recorded, page input handling fired. | FR-DRP-003, AC-US-009-1 |
| **Multiple reasonable matches** | **Ask the user** — select nothing, present each candidate with the reason it was considered. | FR-DRP-004, BR-003, EC-006, AC-US-009-2 |
| **No valid match** | **Do not select.** Leave the field unset, report it as needing attention, and offer the option list for a direct choice. | FR-DRP-005, BR-009, EC-007, AC-US-009-3 |

---

## 4. Diagram key — node to requirement

| Node | Requirements |
|---|---|
| Understand the field | FR-FLD-001/002, AR-AST-003 |
| What kind of control, and which tier? | FR-FLD-003, FR-FLD-007, AR-DET-005 |
| Consequential checkbox | FR-DRP-007, BR-006, AC-US-009-5 |
| Unknown | FR-FLD-006, BR-009, EC-008 |
| Read every available option | FR-DRP-001 |
| Options depend on another field? | FR-DRP-008 |
| Re-read after its controller changes | FR-DRP-008, AC-US-009-4, EC-015 |
| Compare by meaning | FR-DRP-002, RC-2 |
| Evaluate confidence | AR-AST-004 |
| How many above the threshold? | FR-DRP-003, BR-001, AR-DET-004 |
| Sensitive | FR-SENS-002, BR-005 |
| Select the option | FR-DRP-003, FR-FILL-003/008, BR-011 |
| Two or more plausible | FR-DRP-004, BR-003, EC-006 |
| Ask the user | FR-AMB-002 |
| No acceptable match | FR-DRP-005, BR-009, EC-007 |
| Offer the option list | EC-007, FR-AMB-003 |
| Unset and outstanding | FR-AMB-004/007, FR-REV-004 |

---

## 5. Four rules specific to option controls

**Radio groups are dropdowns.** Treated as single-choice fields subject to the same thresholds (FR-DRP-006). No
separate leniency.

**Checkboxes are set only when routine.** A checkbox is set automatically only where classified routine. Checkboxes
classified **consequential are never set by DOCURA** — at any confidence value (FR-DRP-007, AC-US-009-5).

> **A gap worth naming.** FR-DRP-007 addresses *routine* and *consequential* checkboxes but is silent on
> **sensitive** ones. The behaviour is derivable — FR-SENS-002 forbids placing sensitive information without
> explicit approval, and BR-005 governs — so this flow requires per-instance approval for a sensitive checkbox.
> Recorded as [Q4-03](questions-and-conflicts.md) because it is a derivation, not a stated requirement.

**Dependent lists are re-read, never remembered.** Where selecting one option changes the options available in a
dependent field, the dependent field is **re-read before matching it** (FR-DRP-008, AC-US-009-4). A district list
that changes when the state changes must not be matched against the old list.

**Search-based and asynchronously loaded lists are out of MVP scope.** FR-DRP-009 is FUTURE (UC-040). They are
reported rather than partially handled — a partially-read option list would make the "how many match?" count
meaningless, and could produce a false "exactly one".

---

## 6. What DOCURA must never do here

| Never | Rule |
|---|---|
| Select the closest option when two are plausible | BR-003 |
| Select on string similarity without meaning | FR-DRP-002 |
| Select before reading all the options | FR-DRP-001 |
| Select from a stale dependent list | FR-DRP-008, EC-015 |
| Set a consequential checkbox | BR-006, FR-DRP-007 |
| Leave a "best guess" in place instead of reporting no match | BR-009, EC-007 |

Step 2 named the cost of getting this wrong: "a wrong board selected from a dropdown … can invalidate an
application." The mismatch is silent — the form accepts it, and the applicant finds out after the deadline.
