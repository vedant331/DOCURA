# Use Case Catalogue

**Step 4 · Document 2 of 20** — 41 use cases: **28 MVP**, **13 Future**.

Every use case below was derived by walking the nineteen functional-requirement modules of Step 3 §1, the twenty-four
user stories of §3, and the fourteen demonstration steps D1–D14 of §10.1. `UC-nnn` identifiers are introduced by this
step and are stable for the life of the project; every other identifier already exists in Steps 1–3.

---

## 1. How this differs from the suggested starting list

The Step 4 brief offered a candidate list of twenty-one use cases. It was checked against the actual requirements
rather than adopted. The changes, with reasons:

| Change | What happened | Why |
|---|---|---|
| **Merged** | "Review Extracted Information" + "Correct Extracted Information" → **UC-008** | US-004 covers both as one outcome, and its acceptance criteria (AC-US-004-1…4) interleave seeing and correcting. Splitting them would produce a use case with no independent goal. |
| **Split** | "Detect Form Fields" → **UC-014** (detect and enumerate) + **UC-015** (derive requirements and show readiness) | Step 3 separates FR-FRM (structure) from FR-INT-002/003 (what the form *needs*), and §10.1 makes D5 and D6 separate observable steps. |
| **Split** | "Understand Form Field" → **UC-016** only | Field interpretation and sensitivity classification are one act: FR-FLD-003 requires classification "before any value is placed in it", so they cannot be separate use cases. |
| **Added** | **UC-002** Install and Connect the Browser Extension | FR-EXT-001/002 are MVP MUST and had no use case in the suggested list. Without it the extension requirements are unreachable. |
| **Added** | **UC-003** Manage Active Sessions | FR-ACC-008 is MVP SHOULD and appears in no user story. Flagged as a traceability gap — see [Q4-04](questions-and-conflicts.md). |
| **Added** | **UC-004** Export Complete Record | FR-ACC-006 / US-020, part of the ownership guarantee BR-018. Absent from the suggested list. |
| **Added** | **UC-010** Manage Documents in the Vault | FR-DOC-001…006 (label, version, primary, view original) are MVP and were unrepresented. |
| **Added** | **UC-028** Raise the Sensitivity of an Attribute | FR-SENS-006 is MVP SHOULD with no story and no acceptance criterion. Flagged as [Q4-05](questions-and-conflicts.md). |
| **Renamed** | "Pause / Stop DOCURA" → **UC-024 Stop DOCURA** | FR-EXT-006 and US-016 describe stopping, not pausing. Nothing in Steps 1–3 defines a resumable pause; inventing one would add unsupported behaviour. |
| **Not created** | "Handle sensitive dropdown option" as its own use case | Covered by UC-017 plus UC-021. Creating it would duplicate an obligation defined once. |

---

## 2. MVP use cases

Column meanings — **Actor**: who initiates. **Supporting**: who else participates. **Pri**: the MoSCoW priority of
the use case's governing requirements, taken from Step 3.

### 2.1 Account, record ownership and setup

| ID | Name | Primary actor | Supporting | Pri | Requirements | Stories | Purpose |
|---|---|---|---|---|---|---|---|
| **UC-001** | Create Account and Authenticate | User | DOCURA | MUST | FR-ACC-001/002/005, NFR-SEC-004 | US-001 | Establish the single-person account that everything else is authorised against. |
| **UC-002** | Install and Connect the Browser Extension | User | DOCURA Extension, Web Browser | MUST | FR-EXT-001/002, NFR-SEC-006 | *none* | Put the extension in place, sharing the application's account, with the narrowest permissions that work. |
| **UC-003** | Manage Active Sessions | User | DOCURA | SHOULD | FR-ACC-008, NFR-SEC-005 | *none* | Let the user see where they are signed in and revoke it. |
| **UC-004** | Export the Complete Record | User | DOCURA | SHOULD | FR-ACC-006 | US-020 | Deliver the ownership guarantee: the record is exportable in an openable format. |
| **UC-005** | Delete Account and All Data | User | DOCURA | MUST | FR-ACC-007, NFR-PRIV-003 | US-019 | Destroy everything, after a confirmation that states what will be destroyed. |

### 2.2 Building and maintaining the record

| ID | Name | Primary actor | Supporting | Pri | Requirements | Stories | Purpose |
|---|---|---|---|---|---|---|---|
| **UC-006** | Upload Documents to the Vault | User | DOCURA | MUST | FR-UPL-001…007, AR-DET-001 | US-002 | Get documents in, once, with validation stated in advance and status visible per file. |
| **UC-007** | Process and Understand a Document | DOCURA | Document Intelligence, User | MUST | FR-OCR-001…010, AR-AST-001/002 | US-003 | Turn an image into classified, extracted, confidence-scored information — or say honestly that it could not. |
| **UC-008** | Review and Correct Extracted Information | User | DOCURA | MUST | FR-OCR-007, FR-INF-002/003, FR-ACC-004 | US-004 | Show each value against its source region and let the user make a correction authoritative. |
| **UC-009** | Resolve Conflicting Information | User | DOCURA | MUST | FR-INF-004/005/006, AR-DET-008 | US-005 | Surface a disagreement between the user's own documents and let *them* settle it. |
| **UC-010** | Manage Documents in the Vault | User | DOCURA | MUST | FR-DOC-001…006 | US-002, US-006 | Label, view the original, add a version, and designate one document of a type as primary. |
| **UC-011** | Delete a Document | User | DOCURA | MUST | FR-DOC-007/008, NFR-PRIV-003 | US-019 | Remove a document with a confirmation naming the information lost, and a grace period before destruction. |
| **UC-012** | Search the Record and Retrieve a Document | User | DOCURA | MUST | FR-SRCH-001…005, FR-DOC-004, NFR-SEC-007 | US-006 | Turn the vault into a working reference: find a fact or a file in seconds, with the document that supports it. |
| **UC-028** | Raise the Sensitivity of an Attribute | User | DOCURA | SHOULD | FR-SENS-006, BR-020 | *none* | Let the user tighten protection. Lowering the consequential tier is impossible for anyone. |

### 2.3 Starting a form session

| ID | Name | Primary actor | Supporting | Pri | Requirements | Stories | Purpose |
|---|---|---|---|---|---|---|---|
| **UC-013** | Activate DOCURA on a Form | User | DOCURA Extension | MUST | FR-INT-001, FR-EXT-003/004/005, BR-014 | US-007 | Declare intent explicitly. Nothing is read, and no filling begins, without this act. |
| **UC-014** | Detect the Form and Enumerate Fields | DOCURA Extension | External Form | MUST | FR-FRM-001…007, AR-DET-007 | US-007 | Build a fresh model of the form — fields, types, required flags, declared constraints — on every activation. |
| **UC-015** | Derive Requirements and Present the Readiness Summary | DOCURA Extension | DOCURA, User | SHOULD † | FR-INT-002/003 | US-007 | Tell the user up front what the form needs, what they have, and what is missing — before they start. |
| **UC-016** | Interpret Field Meaning and Classify Sensitivity | Form Intelligence | DOCURA Extension | MUST | FR-FLD-001…007, AR-AST-003, AR-DET-005/006 | US-008, US-013 | Work out what each field means, with a confidence and an explicit "unknown", and assign its tier before any value is placed. |

> † **UC-015 carries a priority conflict.** FR-INT-003 is marked SHOULD, but US-007 (MUST), demonstration step D4,
> AC-US-007-2/3, and EC-005 all depend on the readiness summary existing. Recorded as [Q4-01](questions-and-conflicts.md).

### 2.4 Acting, asking, and refusing

| ID | Name | Primary actor | Supporting | Pri | Requirements | Stories | Purpose |
|---|---|---|---|---|---|---|---|
| **UC-017** | Fill a High-Confidence Routine Field | DOCURA Extension | Form Intelligence, External Form | MUST | FR-FILL-001…008, BR-001, BR-010, BR-011 | US-008 | Fill only what is defensible: routine tier, both confidences above threshold, visibly marked, traceable, reversible. |
| **UC-018** | Resolve a Dropdown, Radio, or Checkbox | DOCURA Extension | Form Intelligence, External Form | MUST | FR-DRP-001…008 | US-009 | Match by meaning rather than string equality, and select only where exactly one option clears the threshold. |
| **UC-019** | Handle an Ambiguous Field | DOCURA Extension | User | MUST | FR-AMB-001…007, BR-003, BR-004 | US-010 | Stop, explain, and ask — never choose the most likely candidate on the user's behalf. |
| **UC-020** | Match and Prepare a Required Document | DOCURA Extension | DOCURA, User | MUST | FR-MATCH-001…008/010, AR-DET-002, BR-013 | US-011 | Find the right document, make a constraint-compliant copy, and never touch the stored original. |
| **UC-021** | Approve a Sensitive Disclosure | User | DOCURA Extension | MUST | FR-SENS-001…005, FR-APR-001…005, BR-005, BR-007 | US-012 | Require explicit, itemised, per-instance approval before any sensitive value or file reaches a form. |
| **UC-022** | Leave Declarations and Consent to the User | DOCURA Extension | User | MUST | FR-FLD-004, FR-DRP-007, FR-APR-005, FR-REV-005, BR-006, BR-020 | US-013 | Detect consequential controls, classify them irreversibly, and never act on them at any confidence level. |

### 2.5 User control and closing the session

| ID | Name | Primary actor | Supporting | Pri | Requirements | Stories | Purpose |
|---|---|---|---|---|---|---|---|
| **UC-023** | Edit or Clear a DOCURA-Filled Value | User | DOCURA Extension | MUST | FR-FILL-005/006, BR-012, BR-015 | US-018 | Let the user override anything, and guarantee it is never overwritten afterwards. |
| **UC-024** | Stop DOCURA | User | DOCURA Extension | MUST | FR-EXT-005/006 | US-016 | Halt all activity at once, leave placed values untouched, and require a fresh activation to resume. |
| **UC-025** | Review the Completed Form | User | DOCURA Extension | MUST | FR-REV-001…006 | US-014 | Replace anxious re-reading with one verifiable summary — outstanding items first. |
| **UC-026** | Hand Back for User Submission | DOCURA Extension | User, External Form | MUST | FR-SUB-001…004, BR-008 | US-015 | Stop. State that submission is the user's. Record the hand-back and claim nothing about what followed. |
| **UC-027** | View Session History | User | DOCURA | SHOULD | FR-AUD-001…006, BR-017 | US-017 | Show what DOCURA did, asked, and was told — without retaining the third-party form's contents. |

---

## 3. Future use cases

Each is bound to the unlocking condition Step 3 §11 assigns it. None may enter MVP without an explicit scope change
recorded with a new version number (Step 3 §11, Containment Rule).

| ID | Name | Requirements | Story | Horizon | Unlocking condition |
|---|---|---|---|---|---|
| **UC-029** | Capture a Document with the Device Camera | FR-UPL-008 | US-021 | H1 | MVP loop works; A-1 and A-2 report favourably |
| **UC-030** | Import from Cloud Storage, Email, or a Locker | FR-UPL-009/010 | *none* | H4 | Users maintain records across more than one season |
| **UC-031** | Reuse a Remembered Answer Across Forms | FR-AMB-008 | US-022 | H1 | Requires explicit consent; remembering is a form of assumed consent |
| **UC-032** | Save a Submission Confirmation to the Vault | FR-SUB-005, FR-REV-007 | US-023 | H1 | Closes the P-11 loop, deliberately deferred in full |
| **UC-033** | Manage Another Person's Record | FR-ACC-010 | US-024 | H6 | Single-user model proven **and** a third-party consent architecture designed |
| **UC-034** | Query the Record in Natural Language | FR-SRCH-006 | *none* | H4 | Vault maturity. Note: Step 1 §03 describes this at vision level |
| **UC-035** | Approve a Reviewed Set of Disclosures in One Action | FR-APR-006 | *none* | H5 | The sensitivity boundary settled by evidence (A-5); relaxes BR-007 |
| **UC-036** | Authenticate with a Second Factor | FR-ACC-009 | *none* | H1 | **Becomes MUST before any real identity document is stored by a real user** |
| **UC-037** | Work in a Named Application Context | FR-INT-004, FR-INT-005 | *none* | H4 / H6 | Contexts at H4; proactive deadline awareness at H6 |
| **UC-038** | Learn Field Interpretation from Corrections | FR-FLD-010 | *none* | H5 | Interruption cost measured |
| **UC-039** | Operate on a Mobile Browser | FR-EXT-008 | *none* | H2 | **A-8 reports.** The highest-risk exclusion — if A-8 fails this is a wrong primary surface, not a deferred feature |
| **UC-040** | Handle Multi-Select and Custom Widget Fields | FR-FLD-008/009, FR-DRP-009 | *none* | H2 | Surface expansion |
| **UC-041** | Operate on Forms in Embedded Frames | FR-FRM-008 | *none* | H2 | ASM-004 — assumed rare enough in target portals to defer |

---

## 4. Actor / use case overview

<!--DIAGRAM:02-actor-use-case-overview-->

---

## 5. Coverage against the MVP demonstration journey

Step 3 §10.1 defines the fourteen steps the MVP must demonstrate end to end. Every one maps to a use case.

| Demo step | What must be observable | Use case |
|---|---|---|
| D1 | Documents accepted, validated, queued with visible status | UC-006 |
| D2 | Each document classified, information extracted with per-field confidence | UC-007 |
| D3 | Structured record assembled, each value linked to its source, low-confidence values flagged | UC-007, UC-008 |
| D4 | Extension activated explicitly; readiness summary shown; activity indicator visible | UC-013, UC-015 |
| D5 | All seven MVP field types enumerated with constraints and required flags | UC-014 |
| D6 | Field meanings interpreted with confidence; unknown fields marked and left alone | UC-016 |
| D7 | Routine fields above threshold filled, reformatted, marked, source inspectable | UC-017 |
| D8 | Single high-confidence match selected; dependent dropdown re-read after its controller changes | UC-018 |
| D9 | A deliberately ambiguous field triggers a prompt with candidates, sources, and the reason | UC-019 |
| D10 | Correct document identified for an upload field and prepared to the declared size and format | UC-020 |
| D11 | A sensitive field and a sensitive document each require explicit, itemised approval | UC-021 |
| D12 | A declaration checkbox detected, classified consequential, and demonstrably untouched | UC-022 |
| D13 | Full summary with values, sources, methods, attachments, outstanding items first | UC-025 |
| D14 | DOCURA states submission belongs to the user and does not operate the submit control | UC-026 |

**Use cases not exercised by the demonstration journey:** UC-001–UC-005, UC-009, UC-010, UC-011, UC-012, UC-023,
UC-024, UC-027, UC-028. These are MVP requirements that the fourteen-step demonstration does not stage. That is a
property of the demonstration script, not a scope gap — but it means **UC-009 (conflict resolution) and UC-024
(stop) are MVP MUST behaviours with no demonstration step**, which is worth noting before the demo is designed.
Recorded as [Q4-09](questions-and-conflicts.md).
