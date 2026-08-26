# Requirements Traceability

**Step 4 · Document 17 of 20** — Use case → user story → functional requirement → business rule → acceptance
criterion, plus an honest account of what does not trace.

**Only identifiers that exist in Steps 1–3 appear here.** `UC-nnn` is the sole identifier introduced by Step 4.

---

## 1. The chain

Step 3 §13 defines the chain this step extends by one link on the left:

```
PROBLEM (02) → USER NEED (02) → USER STORY (03) → REQUIREMENT (03) → ACCEPTANCE CRITERION (03)
                                        ▲
                                  USE CASE (04)
```

A use case is the behavioural expression of one or more stories. It does not replace any link — it makes the story
executable as a flow.

---

## 2. Master traceability matrix — MVP

| Use case | User story | Functional requirements | Business rules | Acceptance criteria |
|---|---|---|---|---|
| **UC-001** Create Account and Authenticate | US-001 | FR-ACC-001, FR-ACC-002, FR-ACC-003, FR-ACC-005 | BR-018, BR-019 | *none defined* |
| **UC-002** Install and Connect the Extension | *none* ⚠ | FR-EXT-001, FR-EXT-002, FR-EXT-004 | BR-014, BR-017 | *none defined* |
| **UC-003** Manage Active Sessions | *none* ⚠ | FR-ACC-008 | BR-018 | *none defined* |
| **UC-004** Export the Complete Record | US-020 | FR-ACC-006 | BR-018 | *none defined* ⚠ |
| **UC-005** Delete Account and All Data | US-019 | FR-ACC-007 | BR-017, BR-018 | AC-US-019-3 |
| **UC-006** Upload Documents | US-002 | FR-UPL-001…007 | BR-013, BR-017 | AC-US-002-1…5 |
| **UC-007** Process and Understand a Document | US-003 | FR-OCR-001…010, FR-INF-001/002/007/008 | BR-002, BR-004, BR-010, BR-012, BR-013, BR-016 | AC-US-003-1…5 |
| **UC-008** Review and Correct Extracted Information | US-004 | FR-OCR-007, FR-INF-002/003/009, FR-ACC-004 | BR-002, BR-010, BR-012 | AC-US-004-1…4 |
| **UC-009** Resolve Conflicting Information | US-005 | FR-INF-004, FR-INF-005, FR-INF-006 | **BR-004**, BR-010, BR-012 | AC-US-005-1…3 |
| **UC-010** Manage Documents in the Vault | US-002, US-006 | FR-DOC-001…006 | BR-013, BR-018 | *none directly* ⚠ |
| **UC-011** Delete a Document | US-019 | FR-DOC-007, FR-DOC-008 | BR-009, BR-017, BR-018 | AC-US-019-1, AC-US-019-2 |
| **UC-012** Search the Record | US-006 | FR-SRCH-001…005, FR-DOC-004 | BR-010, BR-018 | *none defined* ⚠ |
| **UC-013** Activate DOCURA on a Form | US-007, US-016 | FR-INT-001, FR-EXT-002…005 | **BR-014**, BR-017 | AC-US-007-1, AC-US-007-4 |
| **UC-014** Detect the Form and Enumerate Fields | US-007 | FR-FRM-001…007, FR-FLD-006/007 | BR-009, BR-014, BR-017 | AC-US-007-2 |
| **UC-015** Derive Requirements / Readiness Summary | US-007 | FR-INT-002, FR-INT-003 | BR-009, BR-016 | AC-US-007-2, AC-US-007-3 |
| **UC-016** Interpret Field Meaning and Classify | US-008, US-013 | FR-FLD-001…007, FR-SENS-001 | BR-006, BR-009, BR-020 | AC-US-008-3 |
| **UC-017** Fill a High-Confidence Routine Field | US-008 | FR-FILL-001…008, FR-AUD-001 | **BR-001**, BR-002, BR-009, BR-010, BR-011, BR-015, BR-016 | AC-US-008-1…5 |
| **UC-018** Resolve a Dropdown, Radio, or Checkbox | US-009 | FR-DRP-001…008 | BR-001, **BR-003**, BR-006, BR-009, BR-011 | AC-US-009-1…5 |
| **UC-019** Handle an Ambiguous Field | US-010 | FR-AMB-001…007, FR-AUD-002 | **BR-003**, BR-004, BR-009, BR-010 | AC-US-010-1…5 |
| **UC-020** Match and Prepare a Required Document | US-011 | FR-MATCH-001…010 | BR-001, BR-003, BR-005, BR-009, **BR-013**, BR-015 | AC-US-011-1…5 |
| **UC-021** Approve a Sensitive Disclosure | US-012 | FR-SENS-001…005, FR-APR-001…005, FR-MATCH-009, FR-AUD-003 | **BR-005**, **BR-007**, BR-015, BR-020 | AC-US-012-1…4 |
| **UC-022** Leave Declarations and Consent to the User | US-013 | FR-FLD-004, FR-DRP-007, FR-APR-005, FR-REV-005, FR-SENS-006 | **BR-006**, BR-020 | AC-US-013-1…3, AC-US-009-5 |
| **UC-023** Edit or Clear a DOCURA-Filled Value | US-018 | FR-FILL-005, FR-FILL-006, FR-REV-002 | **BR-012**, BR-015 | AC-US-018-1…3 |
| **UC-024** Stop DOCURA | US-016 | FR-EXT-005, FR-EXT-006 | BR-014, BR-016 | AC-US-016-1…3 |
| **UC-025** Review the Completed Form | US-014 | FR-REV-001…006, FR-AUD-003 | BR-010, BR-011, BR-015 | AC-US-014-1…4 |
| **UC-026** Hand Back for User Submission | US-015 | FR-SUB-001…004 | **BR-008**, BR-015 | AC-US-015-1…3 |
| **UC-027** View Session History | US-017 | FR-AUD-001…006, FR-EXT-007 | BR-010, BR-017 | *none defined* ⚠ |
| **UC-028** Raise the Sensitivity of an Attribute | *none* ⚠ | FR-SENS-006, FR-SENS-001/002, FR-INF-007 | **BR-020**, BR-005 | *none defined* ⚠ |

⚠ marks a gap analysed in §5.

---

## 3. Business rule coverage — all 20

Every business rule in Step 3 §5 is enforced by at least one use case.

| Rule | Subject | Enforced in |
|---|---|---|
| BR-001 | Confidence | UC-017, UC-018, UC-020 |
| BR-002 | Confidence floor | UC-007, UC-008, UC-017 |
| BR-003 | Ambiguity | UC-018, UC-019, UC-020 |
| BR-004 | Conflict | UC-007, UC-009, UC-019 |
| BR-005 | Sensitive information | UC-020, UC-021, UC-028 |
| BR-006 | Consent and declarations | UC-016, UC-018, UC-022 |
| BR-007 | Scope of approval | UC-021 |
| BR-008 | Final submission | UC-026 |
| BR-009 | Unknown information | UC-011, UC-014, UC-015, UC-016, UC-017, UC-018, UC-019, UC-020 |
| BR-010 | Traceability | UC-007, UC-008, UC-012, UC-017, UC-025, UC-027 |
| BR-011 | Visibility of action | UC-017, UC-018, UC-025 |
| BR-012 | User precedence | UC-007, UC-008, UC-009, UC-023 |
| BR-013 | Original integrity | UC-006, UC-007, UC-010, UC-020 |
| BR-014 | Activation | UC-002, UC-013, UC-014, UC-024 |
| BR-015 | Reversibility | UC-020, UC-021, UC-023, UC-025, UC-026 |
| BR-016 | Fail towards inaction | UC-007, UC-015, UC-017, UC-024 |
| BR-017 | Data minimisation | UC-002, UC-005, UC-006, UC-013, UC-027 |
| BR-018 | Ownership | UC-001, UC-003, UC-004, UC-005, UC-010, UC-011, UC-012 |
| BR-019 | No absolute claims | UC-001 |
| BR-020 | Sensitivity floor | UC-016, UC-021, UC-022, UC-028 |

**The non-negotiable set** — BR-006, BR-008, BR-009 — is enforced across eleven use cases and appears in nine of the
twenty-three diagrams.

---

## 4. Automation requirement coverage — all 22

| ID | Covered by | ID | Covered by |
|---|---|---|---|
| AR-DET-001 | UC-006 | AR-AST-001 | UC-007 |
| AR-DET-002 | UC-020 | AR-AST-002 | UC-007 |
| AR-DET-003 | UC-007, UC-017 | AR-AST-003 | UC-016 |
| AR-DET-004 | UC-017, UC-018, UC-020 | AR-AST-004 | UC-017, UC-018 |
| AR-DET-005 | UC-016 | AR-AST-005 | UC-020 |
| AR-DET-006 | UC-016, UC-022 | AR-AST-006 | UC-008 |
| AR-DET-007 | UC-014 | AR-AST-007 | UC-016, UC-022, UC-028 |
| AR-DET-008 | UC-007, UC-009 | AR-AST-008 | UC-007 |
| AR-AGT-001 | UC-017, UC-018, UC-020 | AR-AGT-004 | UC-026 |
| AR-AGT-002 | UC-017, UC-021 | AR-AGT-005 | UC-014, UC-019, UC-024 |
| AR-AGT-003 | UC-017, UC-020 | AR-AGT-006 | UC-022, UC-026 |

---

## 5. Coverage gaps — stated, not smoothed over

### 5.1 MVP requirements with no user story

Step 3 says stories exist "only where a story captures a distinct user outcome, not for every requirement", so a
missing story is not automatically a defect. These are recorded because a reader tracing a use case backwards will
look for one and not find it.

| Requirement | Priority | Use case | Assessment |
|---|---|---|---|
| FR-ACC-004 — canonical profile of personal attributes | MUST | UC-008 | Covered behaviourally by US-004; no story of its own |
| FR-ACC-008 — view and revoke active sessions | SHOULD | UC-003 | **Genuine gap.** A user-facing security capability with neither a story nor an acceptance criterion |
| FR-EXT-001 / FR-EXT-002 — install and account binding | MUST | UC-002 | **Genuine gap.** Prerequisite for every extension story |
| FR-DOC-003 — personal label | COULD | UC-010 | Listed under US-002/US-006 in Step 3 Table 13.1 but not in the Table 3.1 story index |
| FR-SRCH-005 — filter by type and date | COULD | UC-012 | US-006 lists FR-SRCH-001…004 only |
| FR-SENS-006 — raise attribute sensitivity | SHOULD | UC-028 | **Genuine gap.** No story, no acceptance criterion — see [Q4-05](questions-and-conflicts.md) |
| FR-INF-008 / FR-INF-009 — normalisation, attribute history | MUST | UC-007, UC-008 | Behaviourally inside US-003/US-004 |

### 5.2 MVP user stories with no acceptance criteria

Step 3 §4 defines acceptance criteria for fifteen of the twenty MVP stories. Five have none:

| Story | Use case | Consequence |
|---|---|---|
| US-001 — Create an account and sign in securely | UC-001 | A MUST story with no executable test |
| US-006 — Find a document or a fact quickly | UC-012 | A MUST story with no executable test |
| US-017 — See what DOCURA did on my behalf | UC-027 | SHOULD |
| US-019 — Delete a document or my entire record *(has AC-US-019-1…3)* | UC-005, UC-011 | ✓ covered |
| US-020 — Export everything I have stored | UC-004 | SHOULD |

**Three MUST-or-SHOULD stories — US-001, US-006, US-020 — plus US-017 have no acceptance criteria in Step 3.**
Recorded as [Q4-06](questions-and-conflicts.md). Step 4 cannot fix this: writing criteria here would be inventing
Step 3 content.

### 5.3 Use cases with no corresponding requirement

**None.** Every one of the 41 use cases traces to at least one requirement in Step 3. This was the check that
governed catalogue construction: no use case was created to make a flow more detailed.

### 5.4 Two documented inconsistencies inside Step 3 itself

| Inconsistency | Detail |
|---|---|
| **Story index vs traceability matrix** | Table 3.1 maps US-002 to FR-UPL-001…007 only; Table 13.1 additionally attributes FR-DOC-001…004 to US-002/US-006. Both are defensible; they simply differ. |
| **FR-INT-003 priority** | Marked SHOULD in §1.7 and §12.2, but required by MUST story US-007, demonstration step D4, AC-US-007-2/3, and EC-005. See [Q4-01](questions-and-conflicts.md). |

---

## 6. Pain and need coverage

Step 3 §13 states that every pain P-01…P-12 traces to at least one requirement, and every need N-01…N-10 is
addressed. Step 4 confirms each now also reaches a use case.

| Pain | Use cases | Need | Use cases |
|---|---|---|---|
| P-01 Retrieval | UC-006, UC-010, UC-012 | N-01 Correct values in correct fields | UC-017, UC-018 |
| P-02 Re-entry | UC-017 | N-02 Right document, right slot, right format | UC-020 |
| P-03 Format rejection | UC-020 | N-03 Fast retrieval | UC-012 |
| P-04 Dropdown mismatch | UC-018, UC-019 | N-04 Visibility of requirements before starting | UC-015 |
| P-05 Which document | UC-010, UC-020 | N-05 See where each value came from | UC-008, UC-017, UC-025, UC-027 |
| P-06 Detail mismatch | UC-009 | N-06 Justified confidence at submission | UC-025, UC-026 |
| P-07 Post-submission anxiety | UC-025, UC-027 | N-07 Final authority over disclosure and consent | UC-021, UC-022, UC-026 |
| P-08 Lost progress | UC-024 | N-08 Private, inspectable, correctable, exportable, deletable | UC-001, UC-004, UC-005, UC-011 |
| P-09 Dependency on others | UC-012 | N-09 Low-effort maintenance | UC-010 |
| P-10 Unread declarations | UC-022 | N-10 Access from where the form is filled | UC-002, UC-013 |
| P-11 Lost confirmations | **UC-032 — FUTURE** | | |
| P-12 Repeated preparation | UC-020 | | |

**P-11 is the only pain with no MVP use case**, matching Step 3 §13's own statement that it "is the only pain
deliberately deferred in full."

---

## 7. Requirements suspended pending untested assumptions

Step 3 §12.3 states these must **not be committed to build** until their supporting assumption reports. The use
cases that specify them are complete, but carry this dependency.

| Assumption | If it fails | Requirements | Use cases affected |
|---|---|---|---|
| **A-1** — users will upload real identity documents | The vault model is wrong; re-conceive around per-session, non-retained documents | All FR-UPL, FR-DOC, FR-INF | UC-006…UC-012 |
| **A-2** — being asked is experienced as trustworthy | The ambiguity model needs **redesign, not adjustment** | All FR-AMB, FR-APR-001 | UC-019, UC-021 |
| **A-5** — users agree with the sensitivity boundary | Interruption frequency is wrong in one direction or the other | FR-SENS-001…006, NFR-USE-002 | UC-016, UC-021, UC-028 |
| **A-7** — extraction is accurate enough on real scans | Thresholds may exclude most automatic action | FR-OCR-004…006, BR-001 | UC-007, UC-008, UC-017 |
| **A-8** — a browser extension is the right surface | **The extension is the wrong surface entirely** | All FR-EXT, FR-FRM, FR-FLD, FR-FILL, FR-DRP | UC-002, UC-013…UC-026 |

**If A-8 fails, 15 of the 28 MVP use cases target the wrong surface.** That is the single largest risk carried by
this step, and it is inherited from Step 3, not introduced here.
