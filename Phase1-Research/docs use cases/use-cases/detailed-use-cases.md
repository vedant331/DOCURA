# Detailed Use Case Specifications

**Step 4 · Document 3 of 20** — Full specification for all **28 MVP use cases**. Future use cases (UC-029…UC-041)
are catalogued in [`use-case-catalogue.md`](use-case-catalogue.md) but deliberately not specified here: specifying
them would invite them into scope, which Step 3 §11 forbids.

---

## How to read a step

Every step in a Main Success Flow is prefixed with the actor performing it:

| Prefix | Actor |
|---|---|
| **USER** | The human account holder |
| **DOCURA** | The application |
| **EXTENSION** | The DOCURA Extension |
| **EXTERNAL FORM** | The third-party page |

Where a step is performed by a named responsibility inside DOCURA — Document Intelligence, Form Intelligence,
Decision & Policy Engine, Action Executor — the prefix names it, because the flow depends on which layer may act.

**Threshold language.** Step 3 leaves several numbers as *TBD — to be validated*: the automatic-action threshold
(BR-001), the review threshold (BR-002), the quality floor (FR-MATCH-010), the deletion grace period (FR-DOC-008),
the session-expiry period (NFR-SEC-005), and the interruption budget (NFR-USE-002). These specifications therefore
test **behaviour at the threshold**, never a value — exactly as Step 3 §4 does. No number is invented here.

---

# UC-001 — Create Account and Authenticate

**MVP · MUST**

## Goal
Establish the single-person account that every document, value, and action is authorised against.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user has reached DOCURA and has no existing account, or has one and is signed out.

## Trigger
The user chooses to create an account or to sign in.

## Main Success Flow
1. **USER** requests account creation.
2. **DOCURA** discloses, in plain language, any processing performed outside the user's device — **before the first upload** (NFR-PRIV-006).
3. **USER** supplies credentials.
4. **DOCURA** stores the credential using a current password-hashing standard, never in recoverable form (NFR-SEC-004).
5. **DOCURA** creates a record owned by exactly one user (FR-ACC-003).
6. **DOCURA** authenticates the user and opens a session that will expire after inactivity and is revocable (NFR-SEC-005).
7. **DOCURA** presents an empty vault, usable immediately — value does not require a complete record (NFR-USE-004).

## Alternative Flows
- **A1 · Returning user.** At step 1 the user signs in instead; flow resumes at step 6.
- **A2 · Forgotten credential.** The user recovers access through a verified reset process (FR-ACC-005). The reset must not weaken the vault.

## Exception Flows
- **E1 · Authentication fails.** No document, extracted value, or history is readable (FR-ACC-002). The error states what went wrong and what to do next, exposing no internal identifiers (NFR-ERR-001/004).
- **E2 · Session expires later, mid-form.** See [EC-016](error-flows.md) — all automated action halts immediately; nothing is filled from a stale session.

## Postconditions
- A single-person account exists; an authenticated session is open; ownership is established for every later authorisation check (NFR-SEC-003).

## Business Rules
BR-018 (ownership: the record belongs to the user), BR-019 (no absolute security claims in any user-facing material).

## Requirements Traceability
**FR** FR-ACC-001, FR-ACC-002, FR-ACC-003, FR-ACC-005 · **NFR** NFR-SEC-003, NFR-SEC-004, NFR-SEC-005, NFR-PRIV-006, NFR-ERR-001, NFR-ERR-004, NFR-USE-004 · **US** US-001 · **BR** BR-018, BR-019 · **AC** *(none — Step 3 §4 defines no acceptance criteria for US-001; see [Q4-06](questions-and-conflicts.md))*

---

# UC-002 — Install and Connect the Browser Extension

**MVP · MUST**

## Goal
Get the extension in place so that it works without further configuration and shares the application's account.

## Primary Actor
User

## Supporting Actors
DOCURA Extension, Web Browser

## Preconditions
- The user has a DOCURA account (UC-001).
- The user is on a supported desktop browser. Mobile browsers are FUTURE (FR-EXT-008).

## Trigger
The user installs the DOCURA Extension.

## Main Success Flow
1. **USER** installs the extension into a supported desktop browser.
2. **EXTENSION** requests the narrowest browser permissions that allow its function, and **justifies each one in user-facing language** (NFR-SEC-006).
3. **USER** grants the permissions.
4. **EXTENSION** becomes usable without any further configuration (FR-EXT-001).
5. **EXTENSION** connects to the account of the application — it does not maintain a separate identity (FR-EXT-002).
6. **EXTENSION** enters the dormant state on every page: reading nothing, logging nothing, transmitting nothing (FR-EXT-004, BR-014).

## Alternative Flows
- **A1 · Not signed in.** The extension operates only for an authenticated user; it prompts for sign-in at first activation rather than at install.

## Exception Flows
- **E1 · Permissions denied.** The extension states which function is unavailable and why, in the same plain language used to request it. It does not operate partially or silently.
- **E2 · User uninstalls later.** See [EC-017](error-flows.md) — all extension activity ceases at once and values already placed in a form remain; DOCURA does not clean up the user's form.

## Postconditions
- The extension is installed, permissioned, bound to the user's account, and dormant.

## Business Rules
BR-014 (activation: no passive or background observation), BR-017 (data minimisation).

## Requirements Traceability
**FR** FR-EXT-001, FR-EXT-002, FR-EXT-004 · **NFR** NFR-SEC-006, NFR-PRIV-001 · **US** *(none — flagged as [Q4-04](questions-and-conflicts.md))* · **BR** BR-014, BR-017 · **EC** EC-017

---

# UC-003 — Manage Active Sessions

**MVP · SHOULD**

## Goal
Let the user see where their account is signed in, and revoke it.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user is authenticated.

## Trigger
The user opens session management, or suspects unauthorised access.

## Main Success Flow
1. **USER** requests the list of active sessions.
2. **DOCURA** authorises the request against the requesting user's identity — never inferring ownership from a client-supplied identifier (NFR-SEC-003).
3. **DOCURA** presents the active sessions (FR-ACC-008).
4. **USER** signs out of all of them.
5. **DOCURA** revokes the sessions (NFR-SEC-005).

## Alternative Flows
- **A1 · A revoked session was driving a form.** The extension halts all automated action immediately; values already in the form are left untouched, and re-authentication is required before any further action ([EC-016](error-flows.md)).

## Exception Flows
- **E1 · Revocation fails.** Reported as partial, itemising which sessions ended and which did not (NFR-ERR-003).

## Postconditions
- The chosen sessions are revoked; no automated action can proceed on a stale session.

## Business Rules
BR-018 (ownership).

## Requirements Traceability
**FR** FR-ACC-008 · **NFR** NFR-SEC-003, NFR-SEC-005, NFR-ERR-003 · **US** *(none — [Q4-04](questions-and-conflicts.md))* · **BR** BR-018 · **EC** EC-016

---

# UC-004 — Export the Complete Record

**MVP · SHOULD**

## Goal
Take everything away — documents and extracted information — in a format that opens.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user is authenticated and has at least one stored document.

## Trigger
The user requests an export.

## Main Success Flow
1. **USER** requests an export of the complete record.
2. **DOCURA** assembles the documents **and** the extracted information (FR-ACC-006).
3. **DOCURA** delivers them in an openable format.

## Alternative Flows
- **A1 · Partially processed record.** Documents still processing are exported as originals; the export states which had no extracted information yet rather than omitting them silently.

## Exception Flows
- **E1 · Export fails part-way.** Reported as partial, itemising what was included and what was not (NFR-ERR-003), with the retry offered in place (NFR-ERR-005).

## Postconditions
- The user holds a complete, openable copy. Nothing in the vault is altered by exporting it.

## Business Rules
BR-018 (the record is inspectable, correctable, exportable, and deletable at any time).

## Requirements Traceability
**FR** FR-ACC-006 · **NFR** NFR-ERR-003, NFR-ERR-005, NFR-SEC-007 · **US** US-020 · **BR** BR-018 · **AC** *(none defined for US-020)*

---

# UC-005 — Delete Account and All Data

**MVP · MUST**

## Goal
Destroy the entire record — and know exactly what is being destroyed before it happens.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user is authenticated.

## Trigger
The user requests account deletion.

## Main Success Flow
1. **USER** requests deletion of the account.
2. **DOCURA** presents an explicit confirmation **stating what will be destroyed** (FR-ACC-007).
3. **USER** confirms.
4. **DOCURA** removes the documents, the extracted information, and every derived copy within the stated period (NFR-PRIV-003).
5. **DOCURA** confirms completion to the user (AC-US-019-3).

## Alternative Flows
- **A1 · User cancels at the confirmation.** Nothing is destroyed; the record is untouched.

## Exception Flows
- **E1 · Deletion partially completes.** Reported as partial and itemised (NFR-ERR-003). Because deletion is a stated guarantee, the outstanding portion is retried rather than reported and abandoned.

## Postconditions
- Account, documents, extracted information, and derived copies are gone within the stated period.

## Business Rules
BR-018 (ownership), BR-017 (data minimisation).

## Requirements Traceability
**FR** FR-ACC-007 · **NFR** NFR-PRIV-003, NFR-ERR-003 · **US** US-019 · **BR** BR-017, BR-018 · **AC** AC-US-019-3

---

# UC-006 — Upload Documents to the Vault

**MVP · MUST**

## Goal
Get documents in once, without a filing decision, and know immediately whether each was accepted.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user is authenticated (FR-ACC-002).

## Trigger
The user selects one or more files to upload.

## Main Success Flow
1. **DOCURA** states the accepted file types and size limits **in advance** (FR-UPL-003).
2. **USER** selects one or more PDF, JPG, or PNG files from local storage — several at once if they wish (FR-UPL-001, FR-UPL-002).
3. **DOCURA** validates type, size, and integrity deterministically, before accepting the file (FR-UPL-003, AR-DET-001).
4. **DOCURA** accepts each valid file as a separate document with its own status (AC-US-002-2).
5. **DOCURA** shows per-document status: *queued* (FR-UPL-005).
6. **DOCURA** hands each document to processing asynchronously; the user is never blocked and can continue working (NFR-PERF-002). → **UC-007**

## Alternative Flows
- **A1 · Duplicate detected.** DOCURA detects that the file duplicates one already stored and offers **keep both / replace / add as a new version**. No silent duplicate is created (FR-UPL-007, AC-US-002-4).
- **A2 · Upload interrupted.** The upload is retryable without the user re-selecting the file, and no partial document appears in the vault (FR-UPL-006, AC-US-002-5).

## Exception Flows
- **E1 · Unsupported type or oversized file.** Rejected **before** upload, with a message naming both the reason and the accepted alternatives (FR-UPL-004, AC-US-002-3).
- **E2 · Corrupt file.** Same treatment as E1 — the reason names corruption specifically (FR-UPL-004).

## Postconditions
- Every accepted file exists as a distinct document with a visible status; nothing partial or duplicated was created.

## Business Rules
BR-013 (the stored original is never modified), BR-017 (data minimisation).

## Requirements Traceability
**FR** FR-UPL-001…007, FR-ACC-002 · **NFR** NFR-PERF-002, NFR-REL-005, NFR-ERR-001, NFR-USE-001 · **AR** AR-DET-001 · **US** US-002 · **BR** BR-013, BR-017 · **AC** AC-US-002-1…5

---

# UC-007 — Process and Understand a Document

**MVP · MUST**

## Goal
Turn an image of a document into classified, extracted, confidence-scored information — or say honestly that it could not.

## Primary Actor
DOCURA *(system-initiated)*

## Supporting Actors
Document Intelligence Layer, User

## Preconditions
- A document has been accepted and queued (UC-006).

## Trigger
The document reaches the front of the processing queue.

## Main Success Flow
1. **DOCURA** sets status *processing* (FR-UPL-005).
2. **DOCUMENT INTELLIGENCE** extracts machine-readable text, treating a multi-page document as a single document (FR-OCR-001, FR-OCR-008).
3. **DOCUMENT INTELLIGENCE** classifies the document into a supported type, or returns **unrecognised** rather than forcing a choice (FR-OCR-002, AR-AST-002).
4. **DOCUMENT INTELLIGENCE** records a classification confidence (FR-OCR-003).
5. **DOCUMENT INTELLIGENCE** extracts the defined field set for that type, recording a confidence for **every field independently** of the document-level confidence (FR-OCR-004, FR-OCR-005).
6. **DECISION & POLICY ENGINE** compares each field confidence with the review threshold. Fields below it are marked as needing review and **withheld from automatic filling** (FR-OCR-006, BR-002).
7. **DOCURA** detects deterministically whether any value disagrees with an existing one (AR-DET-008). → **UC-009** if so.
8. **DOCURA** assembles the values into the structured record, each referencing its source document and confidence (FR-INF-001, FR-INF-002).
9. **DOCURA** normalises formats deterministically — dates, casing, spacing, numeric precision — **without altering meaning** (FR-INF-008, AR-DET-003).
10. **DOCURA** assigns each attribute a sensitivity classification of routine, sensitive, or consequential (FR-INF-007).
11. **DOCURA** sets status *ready*.

## Alternative Flows
- **A1 · Type not determined confidently.** Stored as unclassified; no type is assumed; the user is asked to identify it (FR-OCR-002, EC-003, AC-US-003-3). *Note: the prompt is asserted by AC-US-003-3 but by no functional requirement — see [Q4-07](questions-and-conflicts.md).*
- **A2 · Document outside the MVP supported type set.** Stored and searchable as an unclassified document, with **no structured extraction** (Step 3 §7.1, ASM-001).
- **A3 · Reprocessing requested.** The user may request reprocessing (FR-OCR-010). Any value the user previously corrected is retained and is **not** overwritten by extraction (AC-US-004-3, BR-012).

## Exception Flows
- **E1 · Extraction fails entirely — EC-001.** The **original file is retained**, the failure reason is stated, and both retry and manual entry are offered (FR-OCR-009). The document remains stored and searchable by label. The uploaded original is never lost because processing failed (NFR-REL-002).
- **E2 · Poor-quality document — EC-002.** Whatever is legible is extracted; low-confidence fields are marked for review; the user is told which fields could not be read confidently. A low-confidence value is **never presented as settled**.
- **E3 · Repeat processing of the same input.** Produces no duplicate documents and no duplicate attribute entries (NFR-REL-005).

## Postconditions
- The document has a type (or is honestly unclassified), a confidence, an extracted field set with per-field confidences, and a status. Values below the review threshold cannot be used automatically.

## Business Rules
BR-002 (confidence floor), BR-004 (conflict), BR-010 (traceability), BR-012 (user precedence), BR-013 (original integrity), BR-016 (fail towards inaction).

## Requirements Traceability
**FR** FR-OCR-001…010, FR-INF-001, FR-INF-002, FR-INF-007, FR-INF-008, FR-UPL-005 · **NFR** NFR-PERF-002, NFR-REL-002, NFR-REL-005, NFR-OBS-001, NFR-OBS-004 · **AR** AR-AST-001, AR-AST-002, AR-AST-006, AR-AST-008, AR-DET-003, AR-DET-008 · **US** US-003 · **BR** BR-002, BR-004, BR-010, BR-012, BR-013, BR-016 · **AC** AC-US-003-1…5 · **EC** EC-001, EC-002, EC-003

---

# UC-008 — Review and Correct Extracted Information

**MVP · MUST**

## Goal
See exactly what DOCURA read from each document, and make a correction that sticks.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- At least one document has been processed (UC-007).

## Trigger
The user opens a document's extracted information, or follows a *needs review* flag.

## Main Success Flow
1. **USER** opens an extracted value.
2. **DOCURA** shows the value **alongside the region of the source document it was read from** (FR-OCR-007, AC-US-004-1).
3. **DOCURA** shows the confidence with which it was read (FR-INF-002, AC-US-003-2).
4. **USER** corrects an incorrect value.
5. **DOCURA** makes the user-supplied value **authoritative over any extracted value** (FR-INF-003, BR-012).
6. **DOCURA** records the change in the attribute's history, including who or what changed it (FR-INF-009).
7. **DOCURA** uses the corrected value for all subsequent form filling (AC-US-004-2).
8. **DOCURA** maintains the user profile of canonical personal attributes, editable by the user (FR-ACC-004).

## Alternative Flows
- **A1 · Value is correct.** The user confirms nothing; no action is required. A value above the review threshold is already usable.
- **A2 · Document is later reprocessed.** The user's value is retained and is not overwritten by extraction (AC-US-004-3).
- **A3 · Sensitive attribute.** The value is masked in DOCURA's own interface by default and revealed only on user action (FR-SENS-004).

## Exception Flows
- **E1 · The value below the review threshold is never used.** Whatever the user does or does not do, a value below the review threshold is never placed automatically (AC-US-004-4, BR-002).

## Postconditions
- Every reviewed value is either extracted-and-above-threshold or user-authoritative. Its source is inspectable.

## Business Rules
BR-002 (confidence floor), BR-010 (traceability), BR-012 (user precedence).

## Requirements Traceability
**FR** FR-OCR-007, FR-INF-002, FR-INF-003, FR-INF-009, FR-ACC-004, FR-SENS-004 · **NFR** NFR-USE-001, NFR-USE-005, NFR-A11Y-003 · **US** US-004 · **BR** BR-002, BR-010, BR-012 · **AC** AC-US-004-1…4

---

# UC-009 — Resolve Conflicting Information Between Documents

**MVP · MUST**

## Goal
Settle a disagreement between the user's own documents — a decision only the user can make.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- Two or more processed documents give different values for the same attribute.

## Trigger
DOCURA detects the disagreement during processing (UC-007 step 7).

## Main Success Flow
1. **DOCURA** detects deterministically that two documents give different values for the same attribute (FR-INF-004, AR-DET-008).
2. **DOCURA** raises a conflict and marks **neither** value authoritative (AC-US-005-1).
3. **DOCURA** presents the disagreement to the user, showing each value and the document it came from (FR-INF-005).
4. **USER** designates one value authoritative.
5. **DOCURA** records which value the user designated and **retains the alternatives** (FR-INF-006).
6. **DOCURA** records the decision in history (AC-US-005-3).

## Alternative Flows
- **A1 · Conflict left unresolved when a form requests that attribute.** DOCURA treats the field as **ambiguous** and asks rather than choosing (AC-US-005-2, FR-AMB-001). → **UC-019**
- **A2 · The user supplies a third value.** The user-supplied value becomes authoritative over both extracted values (FR-INF-003, BR-012).

## Exception Flows
- **E1 · DOCURA is asked to resolve it.** It cannot. Conflict resolution **is never automated at all** — not by rule, not by recency, not by preference (AR-DET-008, BR-004).

## Postconditions
- Either the conflict is resolved with a recorded, authoritative choice and retained alternatives, or it remains open and every dependent field is treated as ambiguous.

## Business Rules
**BR-004 (conflict) — governing.** Also BR-010, BR-012.

## Requirements Traceability
**FR** FR-INF-004, FR-INF-005, FR-INF-006, FR-INF-003 · **AR** AR-DET-008 · **US** US-005 · **BR** BR-004, BR-010, BR-012 · **AC** AC-US-005-1…3 · **EC** EC-004 · **Traces to** P-06 (name and detail mismatches across documents)

---

# UC-010 — Manage Documents in the Vault

**MVP · MUST**

## Goal
Keep the vault usable: find things by name, see the original, keep versions straight, and say which document is the one to use.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user is authenticated and has at least one stored document.

## Trigger
The user opens the vault.

## Main Success Flow
1. **DOCURA** lists every stored document with its type, date added, and processing status (FR-DOC-001).
2. **DOCURA** shows the document type it assigned automatically; **USER** may correct it (FR-DOC-002).
3. **USER** gives a document a personal label **without altering its type** (FR-DOC-003).
4. **USER** opens and views the original file **exactly as uploaded** (FR-DOC-004), served through time-limited, single-purpose access (NFR-SEC-007).
5. **USER** adds a newer version of an existing document; **DOCURA** retains the previous version (FR-DOC-005).
6. Where several documents of the same type exist, **USER** designates one as **primary** for automatic use (FR-DOC-006).

## Alternative Flows
- **A1 · No primary designated among several of a type.** Document matching treats them as multiple plausible candidates and asks the user (FR-MATCH-004, BR-003). → **UC-020**

## Exception Flows
- **E1 · Original cannot be served.** The failure is visible at the point of failure, not discovered later (NFR-REL-004), with the retry offered in place (NFR-ERR-005).

## Postconditions
- Documents are labelled, versioned, and — where several of a type exist — one is designated primary.

## Business Rules
BR-013 (original integrity), BR-018 (ownership).

## Requirements Traceability
**FR** FR-DOC-001…006 · **NFR** NFR-SEC-007, NFR-REL-004, NFR-ERR-005, NFR-USE-005 · **US** US-002, US-006 · **BR** BR-013, BR-018 · **Traces to** P-01, P-05

---

# UC-011 — Delete a Document

**MVP · MUST**

## Goal
Remove a document, knowing what information goes with it, with a window to change one's mind.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The document exists in the vault.

## Trigger
The user deletes a document.

## Main Success Flow
1. **USER** deletes a document.
2. **DOCURA** presents a confirmation **naming the information that will be lost with it** (FR-DOC-007, AC-US-019-1).
3. **USER** confirms.
4. **DOCURA** removes the document from active use and starts the grace period (FR-DOC-008).
5. After the grace period, **DOCURA** destroys the document, its extracted information, and its derived copies within the stated period (NFR-PRIV-003).

## Alternative Flows
- **A1 · Restore within the grace period.** The user restores the document (AC-US-019-2).
- **A2 · After the grace period.** It is unrecoverable, **and the interface says so** (AC-US-019-2).

## Exception Flows
- **E1 · A form session is relying on that document.** Deletion does not silently break the session; the document is reported as missing at review rather than substituted (FR-MATCH-005, BR-009).

## Postconditions
- The document and everything derived from it are gone, or restorable until the grace period elapses.

## Business Rules
BR-009 (unknown information — never substitute), BR-017, BR-018.

## Requirements Traceability
**FR** FR-DOC-007, FR-DOC-008, FR-MATCH-005 · **NFR** NFR-PRIV-003 · **US** US-019 · **BR** BR-009, BR-017, BR-018 · **AC** AC-US-019-1, AC-US-019-2

> **Open parameter:** the grace period is *TBD — to be validated* (FR-DOC-008). This specification tests that a
> restorable window exists and that the interface states when it has closed — not its length.

---

# UC-012 — Search the Record and Retrieve a Document

**MVP · MUST**

## Goal
Find a fact or a file in seconds, with the document that supports it — so a small question does not become a ten-minute search.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The user is authenticated and has processed documents.

## Trigger
The user searches.

## Main Success Flow
1. **USER** searches by document type or personal label (FR-SRCH-001).
2. **USER** searches the extracted text of all documents (FR-SRCH-002).
3. **USER** searches by attribute value and **receives the supporting document** (FR-SRCH-003).
4. **DOCURA** identifies, for each result, the document **and the location within it** where the match occurred (FR-SRCH-004).
5. **USER** filters results by document type and date added (FR-SRCH-005).
6. **DOCURA** returns results without a perceptible wait at expected record sizes (NFR-PERF-004).

## Alternative Flows
- **A1 · The match is in an unclassified document.** It is still found: documents outside the MVP type set remain stored and searchable, they simply have no structured extraction (Step 3 §7.1).
- **A2 · The match is in a document whose processing failed.** Still searchable by label ([EC-001](error-flows.md)).

## Exception Flows
- **E1 · No results.** Stated plainly, with what the user can do next (NFR-ERR-001). Nothing approximate is returned in place of a match.

## Postconditions
- The user has the fact and the document that proves it, or a clear statement that neither exists.

## Business Rules
BR-010 (traceability), BR-018 (ownership).

## Requirements Traceability
**FR** FR-SRCH-001…005, FR-DOC-004 · **NFR** NFR-PERF-004, NFR-SEC-007, NFR-ERR-001 · **US** US-006 · **BR** BR-010, BR-018 · **Traces to** N-03, P-01, P-09
*Natural-language query (FR-SRCH-006) is **FUTURE** — UC-034.*

---

# UC-013 — Activate DOCURA on a Form

**MVP · MUST**

## Goal
Declare intent. Nothing is read and nothing is filled until the user asks for it, on this page.

## Primary Actor
User

## Supporting Actors
DOCURA Extension

## Preconditions
- The extension is installed and bound to the account (UC-002).
- The user has opened a form page.
- **DOCURA has read nothing on that page** (FR-EXT-004, AC-US-007-1).

## Trigger
The user activates DOCURA on the open form.

## Main Success Flow
1. **USER** explicitly activates DOCURA on the open form. **No filling activity begins without this action** (FR-INT-001, BR-014).
2. **EXTENSION** confirms an authenticated session, sharing the application's account (FR-EXT-002).
3. **EXTENSION** displays a **persistent, unambiguous indicator** that it is active on the page — visible at all times thereafter (FR-EXT-005, AC-US-007-4).
4. **EXTENSION** begins reading the page content, on this page only (FR-EXT-003). → **UC-014**

## Alternative Flows
- **A1 · Not signed in.** The user signs in; activation then proceeds. The extension operates only for an authenticated user (FR-EXT-002).
- **A2 · Page not activated.** DOCURA reads nothing and shows no indicator of activity (AC-US-007-1). This is the default state of every page.

## Exception Flows
- **E1 · User navigates away.** The session ends. There is no background observation of the page afterwards (FR-EXT-004).
- **E2 · Form structure changes later.** Field mappings are re-derived from scratch on each activation; stored mappings are **never trusted across sessions** ([EC-009](error-flows.md), FR-FRM-007).

## Postconditions
- DOCURA is active on exactly one page, visibly, with the user's explicit consent to read it.

## Business Rules
**BR-014 (activation) — governing.** Also BR-017 (third-party form content is not retained).

## Requirements Traceability
**FR** FR-INT-001, FR-EXT-002, FR-EXT-003, FR-EXT-004, FR-EXT-005 · **NFR** NFR-PRIV-004, NFR-SEC-006 · **US** US-007, US-016 · **BR** BR-014, BR-017 · **AC** AC-US-007-1, AC-US-007-4 · **EC** EC-009

---

# UC-014 — Detect the Form and Enumerate Fields

**MVP · MUST**

## Goal
Build a fresh, accurate model of the form — every time, from scratch.

## Primary Actor
DOCURA Extension

## Supporting Actors
External Form

## Preconditions
- The user has activated DOCURA on this page (UC-013).

## Trigger
Activation completes.

## Main Success Flow
1. **EXTENSION** detects the presence of a fillable form on the activated page (FR-FRM-001).
2. **EXTENSION** enumerates the form's fields together with their input type — deterministically (FR-FRM-002, AR-DET-007).
3. **EXTENSION** identifies which fields the form marks as **required** (FR-FRM-003).
4. **EXTENSION** reads the validation constraints the form declares: length, pattern, accepted file types, size limits (FR-FRM-004).
5. **EXTENSION** transmits only the minimum form structure needed to interpret fields, and no page content unrelated to the form (NFR-PRIV-004).
6. **EXTENSION** supports the seven MVP field types: text, number, date, dropdown, radio, checkbox, file-upload (FR-FLD-007). → **UC-016**

## Alternative Flows
- **A1 · Form spans multiple steps or pages.** Treated as **one application** (FR-FRM-005).
- **A2 · Fields added after initial load.** Detected (FR-FRM-006).
- **A3 · Form structure changes during the session — EC-015.** The extension re-examines the form, **discards stale field mappings**, and informs the user. A mapping is never applied to a field that has moved (FR-FRM-007, AR-AGT-005).

## Exception Flows
- **E1 · No fillable form found.** Reported. No action is taken. DOCURA does not guess that some other element is a form.
- **E2 · Field type outside the MVP seven — EC-010.** Enumerated, marked unsupported, excluded from filling, and listed in review as requiring the user (FR-FLD-006, FR-REV-004).
- **E3 · Form inside an embedded frame.** Out of MVP scope (FR-FRM-008, ASM-004). Reported rather than silently skipped.

## Postconditions
- A field inventory exists for this session, derived fresh, with types, required flags, and declared constraints.

## Business Rules
BR-009 (unknown information), BR-014 (activation), BR-017 (form content not retained).

## Requirements Traceability
**FR** FR-FRM-001…007, FR-FLD-006, FR-FLD-007, FR-REV-004 · **NFR** NFR-PRIV-004, NFR-MNT-003 (interpretation must not depend on any specific website's internal structure), NFR-PERF-001, NFR-PERF-005 · **AR** AR-DET-007, AR-AGT-005 · **US** US-007 · **BR** BR-009, BR-014, BR-017 · **AC** AC-US-007-2 · **EC** EC-009, EC-010, EC-015 · **Mitigates** R-5 (portal volatility)

---

# UC-015 — Derive Requirements and Present the Readiness Summary

**MVP · SHOULD** † *(priority conflict — see [Q4-01](questions-and-conflicts.md))*

## Goal
Find out about a missing document **before** starting the form, rather than at the end.

## Primary Actor
DOCURA Extension

## Supporting Actors
DOCURA, User

## Preconditions
- The form has been detected and its fields enumerated (UC-014).

## Trigger
Field enumeration completes.

## Main Success Flow
1. **EXTENSION** derives the set of information and documents the form requires (FR-INT-002).
2. **EXTENSION** queries the structured record for what is available.
3. **EXTENSION** presents a readiness summary **before filling**: what the form needs, what is available, what is missing, and what will require the user (FR-INT-003, AC-US-007-2).
4. **EXTENSION** lists any required document the user has not stored as **missing, before any filling begins** (EC-005, AC-US-007-3).
5. **USER** reads it and proceeds. → **UC-016**

## Alternative Flows
- **A1 · Record is only partially populated.** DOCURA remains usable; value does not require a complete vault (NFR-USE-004). The summary states what is missing rather than refusing to start.
- **A2 · User leaves to add a missing document.** They return, re-activate (BR-014), and the form model is derived fresh (EC-009).

## Exception Flows
- **E1 · Requirements cannot be derived for some fields.** Those fields are reported as needing the user rather than assumed satisfied (BR-009, BR-016).

## Postconditions
- The user knows, before typing anything, what this form will need from them.

## Business Rules
BR-009 (unknown information), BR-016 (fail towards inaction).

## Requirements Traceability
**FR** FR-INT-002, FR-INT-003, FR-MATCH-005 · **NFR** NFR-USE-004, NFR-PERF-001 · **US** US-007 · **BR** BR-009, BR-016 · **AC** AC-US-007-2, AC-US-007-3 · **EC** EC-005 · **Traces to** N-04, S2, P-05

---

# UC-016 — Interpret Field Meaning and Classify Sensitivity

**MVP · MUST**

## Goal
Work out what each field actually means — and decide its tier before any value can reach it.

## Primary Actor
Form Intelligence Layer

## Supporting Actors
DOCURA Extension, Decision & Policy Engine

## Preconditions
- Fields have been enumerated with their types and constraints (UC-014).

## Trigger
The readiness summary is presented, or filling begins.

## Main Success Flow
1. **FORM INTELLIGENCE** determines the meaning of each field from its visible label, adjacent text, placeholder, and declared attributes (FR-FLD-001).
2. **FORM INTELLIGENCE** produces a semantic label **and a confidence**, and is able to return **"unknown"** (FR-FLD-002, AR-AST-003).
3. **DECISION & POLICY ENGINE** classifies each field routine, sensitive, or consequential — **before any value is placed in it** (FR-FLD-003), driven by a reviewable rule set rather than inferred per session (AR-DET-005).
4. **DECISION & POLICY ENGINE** identifies legal declarations, agreements, and consent controls using **deterministic rules as the primary mechanism**, and marks them consequential (FR-FLD-004, AR-DET-006). → **UC-022**
5. **FORM INTELLIGENCE** may act only as an additional safeguard here: it may **add** the consequential classification, never remove it, and may lower a confidence, never raise it (AR-DET-006, AR-AST-007).
6. **EXTENSION** identifies file-upload fields and the document each one is asking for (FR-FLD-005). → **UC-020**
7. **EXTENSION** conveys each field's state — filled, asked, approved, unknown — by more than colour alone (NFR-A11Y-003).

## Alternative Flows
- **A1 · Meaning cannot be determined with sufficient confidence — EC-008.** The field is marked **unknown** and **left untouched** — never guessed from a superficially similar label (FR-FLD-006, BR-009, AC-US-008-3).
- **A2 · Multi-select or custom widget.** Out of MVP scope (FR-FLD-008, FR-FLD-009). Marked unsupported and listed at review (EC-010).

## Exception Flows
- **E1 · An assisted component attempts to escalate its own authority.** Structurally prohibited (AR-AST-007).

## Postconditions
- Every field has a meaning-or-unknown, a confidence, and a sensitivity tier — assigned before any value could reach it.

## Business Rules
BR-006 (consent and declarations), BR-009 (unknown information), BR-020 (sensitivity floor — consequential can never be reclassified downward).

## Requirements Traceability
**FR** FR-FLD-001…007, FR-SENS-001 · **NFR** NFR-A11Y-003, NFR-MNT-003, NFR-MNT-004, NFR-OBS-001 · **AR** AR-AST-003, AR-AST-007, AR-DET-005, AR-DET-006 · **US** US-008, US-013 · **BR** BR-006, BR-009, BR-020 · **AC** AC-US-008-3 · **EC** EC-008, EC-010 · **Traces to** RC-2 (no shared vocabulary between forms)

---

# UC-017 — Fill a High-Confidence Routine Field

**MVP · MUST**

## Goal
Fill only what is defensible, mark it visibly, and keep it reversible.

## Primary Actor
DOCURA Extension *(Action Executor)*

## Supporting Actors
Form Intelligence Layer, External Form

## Preconditions
- The field is interpreted, classified **routine**, and is a text, number, or date field (UC-016).

## Trigger
Filling runs for this field.

## Main Success Flow
1. **FORM INTELLIGENCE** produces ranked candidate values from the structured record (AR-AST-004).
2. **DECISION & POLICY ENGINE** checks that **both** the field interpretation and the source value are at or above the automatic-action threshold (FR-FILL-001, BR-001, AR-DET-004).
3. **DECISION & POLICY ENGINE** confirms the tier is routine (FR-FILL-001) and performs the sensitivity check (AR-AGT-002).
4. **ACTION EXECUTOR** reformats the value to satisfy the field's declared constraints **without changing its meaning** — deterministically (FR-FILL-002, AR-DET-003).
5. **ACTION EXECUTOR** places the value. This is one of only three permitted agentic actions (AR-AGT-001).
6. **EXTENSION** marks the field visually as **DOCURA-filled**, distinguishable from user-entered values (FR-FILL-003, BR-011, AC-US-008-1).
7. **EXTENSION** makes the source document inspectable for that value (FR-FILL-004, BR-010, AC-US-008-2).
8. **ACTION EXECUTOR** triggers the page's own input handling, so the form's validation and dependent behaviour respond **as if a person had typed** (FR-FILL-008, AC-US-008-5).
9. **DOCURA** records the value placed (FR-AUD-001).

## Alternative Flows
- **A1 · Format differs from the stored format.** The value is reformatted to the field's format without altering its meaning — for example a date (AC-US-008-4).
- **A2 · Reformatting would change the meaning.** The field is treated as **ambiguous** instead (FR-FILL-002). → **UC-019**
- **A3 · Same attribute requested twice in one form — EC-019.** Both are filled consistently from the same authoritative value. If the user overrides one, the change is **not** propagated silently to the other; the divergence is flagged at review (FR-REV-002, BR-012).

## Exception Flows
- **E1 · Field marked unknown.** No value is placed (FR-FILL-007, BR-009).
- **E2 · Source value below the review threshold.** Never used for automatic action, however well it matches (BR-002, AC-US-004-4).
- **E3 · Component failure mid-fill.** DOCURA fails towards inaction: the field is left untouched and the user is told (BR-016, NFR-ERR-002). A field is never left half-filled (EC-014).

## Postconditions
- The field either holds a traceable, visibly-marked, reversible DOCURA value, or is untouched and reported.

## Business Rules
BR-001 (confidence), BR-002 (confidence floor), BR-009 (unknown), BR-010 (traceability), BR-011 (visibility of action), BR-015 (reversibility), BR-016 (fail towards inaction).

## Requirements Traceability
**FR** FR-FILL-001…008, FR-AUD-001 · **NFR** NFR-PERF-001, NFR-PERF-005, NFR-REL-001, NFR-ERR-002, NFR-A11Y-003, NFR-A11Y-005, NFR-OBS-002, NFR-OBS-003 · **AR** AR-AST-004, AR-DET-003, AR-DET-004, AR-AGT-001, AR-AGT-002, AR-AGT-003 · **US** US-008 · **BR** BR-001, BR-002, BR-009, BR-010, BR-011, BR-015, BR-016 · **AC** AC-US-008-1…5 · **EC** EC-014, EC-019 · **Traces to** P-02, S5, L2

---

# UC-018 — Resolve a Dropdown, Radio, or Checkbox

**MVP · MUST**

## Goal
Match the user's information to an option by **meaning**, and select only where exactly one option is defensible.

## Primary Actor
DOCURA Extension

## Supporting Actors
Form Intelligence Layer, External Form

## Preconditions
- The field is interpreted and classified (UC-016).

## Trigger
Filling runs for a dropdown, radio group, or checkbox group.

## Main Success Flow
1. **EXTENSION** reads **all** available options before attempting a match (FR-DRP-001).
2. **FORM INTELLIGENCE** matches the user's value to an option **by meaning, not by exact string equality** (FR-DRP-002), producing a ranked candidate list with confidences (AR-AST-004).
3. **DECISION & POLICY ENGINE** selects automatically only where **exactly one** option matches at or above the automatic-action threshold (FR-DRP-003, BR-001, AC-US-009-1).
4. **ACTION EXECUTOR** selects the option and marks it DOCURA-selected (BR-011).
5. **ACTION EXECUTOR** triggers the page's own input handling (FR-FILL-008).

## Alternative Flows
- **A1 · Radio group.** Treated as a single-choice field, subject to the same thresholds as dropdowns (FR-DRP-006).
- **A2 · Checkbox, routine tier.** Set automatically only where classified routine (FR-DRP-007).
- **A3 · Dependent option list.** Where selecting one option changes the options available in a dependent field, the dependent field is **re-read before matching it** (FR-DRP-008, AC-US-009-4).
- **A4 · Sensitive option.** Explicit per-instance approval is required before selection (FR-SENS-002, BR-005). → **UC-021**

## Exception Flows
- **E1 · Two or more options plausible — EC-006.** **Nothing is selected.** The user is asked, with each candidate shown and the reason it was considered (FR-DRP-004, BR-003, AC-US-009-2). → **UC-019**
- **E2 · No option matches acceptably — EC-007.** The field is left unset and reported as needing attention; the user is offered the option list to choose from directly (FR-DRP-005, BR-009, AC-US-009-3).
- **E3 · Checkbox classified consequential.** **Never set by DOCURA under any confidence value** (FR-DRP-007, BR-006, AC-US-009-5). → **UC-022**
- **E4 · Search-based or asynchronously loaded option list.** Out of MVP scope (FR-DRP-009). Reported rather than partially handled.

## Postconditions
- The control holds exactly one defensible selection, or is unset and reported. Nothing was chosen on likelihood.

## Business Rules
BR-001, **BR-003 (ambiguity) — governing for E1**, BR-006, BR-009, BR-011.

## Requirements Traceability
**FR** FR-DRP-001…008, FR-FILL-008, FR-SENS-002 · **NFR** NFR-PERF-001, NFR-A11Y-003 · **AR** AR-AST-004, AR-DET-004, AR-AGT-001 · **US** US-009 · **BR** BR-001, BR-003, BR-006, BR-009, BR-011 · **AC** AC-US-009-1…5 · **EC** EC-006, EC-007, EC-015 · **Traces to** P-04, RC-2

---

# UC-019 — Handle an Ambiguous Field

**MVP · MUST**

## Goal
Make sure a confident mistake never gets past the user into a submitted application.

## Primary Actor
DOCURA Extension

## Supporting Actors
User

## Preconditions
- A field has been interpreted and one of the four ambiguity conditions holds.

## Trigger
Any of: several candidate values or options are plausible; confidence is below the automatic-action threshold; source documents conflict; or the required information is absent (FR-AMB-001).

## Main Success Flow
1. **DECISION & POLICY ENGINE** detects the ambiguity and **halts automatic action on that field** (FR-AMB-001, BR-003).
2. **EXTENSION** states the field, lists the candidates, identifies **the source of each candidate**, and explains **why DOCURA could not decide** (FR-AMB-002, AC-US-010-1).
3. **EXTENSION** groups this question with other open questions where doing so does not delay filling of unaffected fields (FR-AMB-005).
4. **EXTENSION** presents the question so it is answerable **without leaving the form page** (NFR-USE-003) and operable by keyboard alone (NFR-A11Y-002).
5. **USER** chooses a candidate.
6. **DOCURA** records the question asked and the answer given (FR-AUD-002).
7. **EXTENSION** applies the answer and marks the field as *answered* rather than *automatic* (FR-REV-002).
8. **EXTENSION** does not ask the same question again **in this session** (FR-AMB-006, AC-US-010-4).

## Alternative Flows
- **A1 · User supplies a value not among the candidates.** It is accepted and used (FR-AMB-003, AC-US-010-2).
- **A2 · User skips.** The field is left unfilled and listed in the review summary as outstanding (FR-AMB-004, AC-US-010-3).
- **A3 · User rejects every candidate.** Same as A2 — nothing is applied.
- **A4 · User stops DOCURA.** → **UC-024**. Values already placed remain and are never reverted.

## Exception Flows
- **E1 · There are no candidates to present.** The fourth ambiguity condition — required information absent — has nothing to prompt with. The field is **reported as missing or unknown** rather than prompted, per BR-009 and EC-005. *See [Q4-08](questions-and-conflicts.md): FR-AMB-001 classes absence as ambiguity, while FR-AMB-002 assumes a candidate list exists.*
- **E2 · A required field is left unanswered.** DOCURA does not proceed past it silently; it is **recorded as outstanding** in the review summary and listed first (FR-AMB-007, AC-US-010-5).

## Postconditions
- Every ambiguous field is either answered by the user and recorded, or explicitly outstanding. **None was guessed.**

## Business Rules
**BR-003 (ambiguity) — governing.** Also BR-004 (conflict), BR-009 (unknown), BR-010 (traceability).

## Requirements Traceability
**FR** FR-AMB-001…007, FR-AUD-002, FR-REV-002 · **NFR** NFR-USE-002, NFR-USE-003, NFR-A11Y-002, NFR-A11Y-004, NFR-OBS-002 · **US** US-010 · **BR** BR-003, BR-004, BR-009, BR-010 · **AC** AC-US-010-1…5 · **EC** EC-004, EC-006, EC-007 · **Traces to** P-04, S6, L3, A-2
*Cross-session remembered answers (FR-AMB-008) are **FUTURE** — UC-031. Every session starts from the record, not from history (Step 3 §10.3).*

---

# UC-020 — Match and Prepare a Required Document

**MVP · MUST**

## Goal
Attach the correct document, already sized and formatted the way the portal demands — so an upload rule never becomes the reason an application fails.

## Primary Actor
DOCURA Extension

## Supporting Actors
DOCURA, User

## Preconditions
- A file-upload field has been identified along with the document it is asking for (UC-016 step 6).

## Trigger
Matching runs for a file-upload field.

## Main Success Flow
1. **EXTENSION** determines which stored documents could satisfy the field (FR-MATCH-001).
2. **FORM INTELLIGENCE** ranks the candidate documents with confidence values (FR-MATCH-002, AR-AST-005).
3. **DECISION & POLICY ENGINE** finds **exactly one** candidate at or above the automatic-action threshold, and the document is not sensitive — so it is proposed for attachment (FR-MATCH-003, BR-001, AC-US-011-1).
4. **DOCURA** produces a **copy** satisfying the field's declared format, size, and dimension constraints — deterministically (FR-MATCH-006, AR-DET-002).
5. **DOCURA** leaves the stored original **unmodified**; preparation always produces a copy (FR-MATCH-007, BR-013, AC-US-011-2).
6. **EXTENSION** lets the user **preview exactly the file that will be attached** (FR-MATCH-008).
7. **ACTION EXECUTOR** attaches the prepared copy (AR-AGT-001).
8. **DOCURA** records the document attached and the field that received it (FR-AUD-001, FR-REV-003).

## Alternative Flows
- **A1 · More than one candidate plausible.** The user is asked to choose, with each candidate identified clearly enough to tell them apart — provisional vs final, attested vs plain, consolidated vs per-semester (FR-MATCH-004, BR-003, AC-US-011-3). → **UC-019**
- **A2 · Document classified sensitive.** Attached only after explicit **per-instance approval** (FR-MATCH-009, BR-005, EC-011). → **UC-021**
- **A3 · User rejects a suggested document — EC-012.** It is not attached, not proposed again for that field in that session, and the remaining candidates or manual selection are offered.
- **A4 · Several documents of one type, one designated primary.** The primary is used for automatic action (FR-DOC-006).

## Exception Flows
- **E1 · No stored document satisfies the requirement — EC-005.** Reported as **missing**. **No different document is substituted** (FR-MATCH-005, BR-009, AC-US-011-4). It is named in the readiness summary before filling and again at review.
- **E2 · Constraints cannot be met without unacceptable quality loss — EC-020.** DOCURA **stops and tells the user** rather than attaching a degraded file, and offers the original for manual handling (FR-MATCH-010, AC-US-011-5).
- **E3 · Wrong, expired, or superseded document.** Never used automatically; the choice returns to the user (BR-003, BR-009).

## Postconditions
- The upload field holds a previewed, constraint-compliant copy of the correct document — or nothing, with the reason stated. The original is untouched.

## Business Rules
BR-001, BR-003, BR-005, BR-009, **BR-013 (original integrity) — governing for step 5**, BR-015.

## Requirements Traceability
**FR** FR-MATCH-001…010, FR-DOC-006, FR-AUD-001, FR-REV-003 · **NFR** NFR-REL-005, NFR-ERR-002, NFR-ERR-003 · **AR** AR-AST-005, AR-DET-002, AR-AGT-001, AR-AGT-003 · **US** US-011 · **BR** BR-001, BR-003, BR-005, BR-009, BR-013, BR-015 · **AC** AC-US-011-1…5 · **EC** EC-005, EC-011, EC-012, EC-020 · **Traces to** P-03, P-05, P-12, RC-3, S4
*Derived-document assembly such as merging files (FR-MATCH-011) is **FUTURE**.*

> **Open parameter:** the quality floor is *TBD — to be validated* (FR-MATCH-010). This specification tests that a
> floor is enforced and that DOCURA stops rather than degrades — not its value.

---

# UC-021 — Approve a Sensitive Disclosure

**MVP · MUST**

## Goal
Ensure speed never costs the user control over what they reveal, and to whom.

## Primary Actor
User

## Supporting Actors
DOCURA Extension

## Preconditions
- A field or a document has been classified **sensitive** (UC-016, FR-SENS-001).

## Trigger
Filling or matching reaches a sensitive item.

## Main Success Flow
1. **DECISION & POLICY ENGINE** halts before disclosure. Sensitive information is **never placed into a form without explicit approval for that specific disclosure** (FR-SENS-002, BR-005, AC-US-012-1).
2. **EXTENSION** presents an approval request showing **the exact value or document to be disclosed** and **the field receiving it** (FR-SENS-003, AC-US-012-2).
3. **EXTENSION** states what will happen, where, and **why DOCURA is asking rather than acting** (FR-APR-001).
4. **DOCURA** keeps the value masked in its own interface by default, revealed only on user action (FR-SENS-004).
5. **USER** approves this request individually (FR-APR-002).
6. **ACTION EXECUTOR** places the value or attaches the document.
7. **DOCURA** records the approval request and its outcome, with its subject (FR-APR-004, FR-AUD-003).

## Alternative Flows
- **A1 · The same information is requested again — another field, another form, or another session.** **Approval is requested again.** It is never inherited, remembered, or generalised (FR-SENS-005, BR-007, AC-US-012-4).
- **A2 · Sensitive document rather than a value — EC-011.** DOCURA prepares and previews, then stops. Attachment follows only on explicit per-instance approval (FR-MATCH-009).

## Exception Flows
- **E1 · User denies.** The field is left **untouched**, the denial is recorded, and **the remainder of the session is not blocked** (FR-APR-003, AC-US-012-3, EC-011). The item is listed at review as outstanding.
- **E2 · A bulk or advance approval is sought.** **No such control exists.** No control approves consequential items in bulk or in advance (FR-APR-005).

## Postconditions
- Every sensitive disclosure that happened was individually approved and recorded. Every one denied left its field untouched, with the session continuing.

## Business Rules
**BR-005 (sensitive information) and BR-007 (scope of approval) — governing.** Also BR-015 (reversibility), BR-020 (sensitivity floor).

## Requirements Traceability
**FR** FR-SENS-001…005, FR-APR-001…005, FR-MATCH-009, FR-AUD-003 · **NFR** NFR-A11Y-002, NFR-A11Y-004, NFR-USE-002, NFR-USE-003, NFR-PRIV-001 · **AR** AR-AGT-002, AR-AGT-003 · **US** US-012 · **BR** BR-005, BR-007, BR-015, BR-020 · **AC** AC-US-012-1…4 · **EC** EC-011 · **Traces to** N-07, Step 2 §13.2, A-5, R-1
*Reviewed bulk approval within a single form (FR-APR-006) is **FUTURE** — UC-035 — and would relax BR-007, so it requires the sensitivity boundary from A-5 first.*

---

# UC-022 — Leave Declarations and Consent to the User

**MVP · MUST**

## Goal
Guarantee that what the user has agreed to is always something they decided.

## Primary Actor
DOCURA Extension

## Supporting Actors
User

## Preconditions
- Fields have been enumerated (UC-014).

## Trigger
Field classification encounters a legal declaration, agreement, or consent control.

## Main Success Flow
1. **DECISION & POLICY ENGINE** identifies the declaration, agreement, or consent control using **deterministic rules as its primary mechanism** (FR-FLD-004, AR-DET-006).
2. **DECISION & POLICY ENGINE** marks it **consequential**. Assisted interpretation may **add** this classification but never remove it (AR-DET-006, AR-AST-007).
3. **EXTENSION** takes **no action on the control**. DOCURA never accepts a legal declaration, agreement, or consent control — at every confidence level, with no setting, exception, or user preference (BR-006, AC-US-013-1).
4. **EXTENSION** shows the user the control and what it asks them to agree to.
5. **EXTENSION** lists it at review as **requiring the user's own action**, without completing it (FR-REV-005, AC-US-013-3).
6. **USER** performs the action themselves.

## Alternative Flows
- **A1 · The control is a checkbox.** Checkboxes classified consequential are **never set by DOCURA** (FR-DRP-007, AC-US-009-5).
- **A2 · The user does not agree.** The item stays outstanding. DOCURA does not press, re-ask, or nudge.

## Exception Flows
- **E1 · The user looks for a setting to automate declarations.** **No such setting exists** (AC-US-013-2). Its absence is the requirement.
- **E2 · Something attempts to reclassify a consequential item downward.** Impossible for any actor — user, administrator, or future enterprise customer (FR-SENS-006, BR-020).

## Postconditions
- Every consequential control is either completed by the user personally, or outstanding. **None was touched by DOCURA.**

## Business Rules
**BR-006 (consent and declarations) — governing, non-negotiable.** Also BR-020 (sensitivity floor).

## Requirements Traceability
**FR** FR-FLD-004, FR-DRP-007, FR-APR-005, FR-REV-005, FR-SENS-006 · **AR** AR-DET-006, AR-AST-007, AR-AGT-006 (no autonomous mode in which the user is absent from the loop) · **US** US-013 · **BR** BR-006, BR-020 · **AC** AC-US-013-1…3, AC-US-009-5 · **Traces to** P-10, S7, Vision §7

> Step 3 §5 names BR-006, BR-008 and BR-009 the **non-negotiable set**: "A future request to relax any of them — for
> a partner, an enterprise buyer, or a conversion metric — is a request to change the product's identity, and must be
> escalated as such rather than handled as a configuration change."

---

# UC-023 — Edit or Clear a DOCURA-Filled Value

**MVP · MUST**

## Goal
Correct something DOCURA filled, and have the correction stay corrected.

## Primary Actor
User

## Supporting Actors
DOCURA Extension

## Preconditions
- A field holds a DOCURA-filled value (UC-017 or UC-018).

## Trigger
The user edits or clears the value.

## Main Success Flow
1. **USER** changes or clears the value (FR-FILL-005).
2. **EXTENSION** re-marks the field as **user-entered** (AC-US-018-1).
3. **EXTENSION** does **not** overwrite it afterwards — a user value always takes precedence and is never overwritten automatically (FR-FILL-005, BR-012, AC-US-018-2).
4. **DOCURA** records the override in the session history, with the original and replacement values (FR-FILL-006, AC-US-018-3).

## Alternative Flows
- **A1 · The same attribute appears twice in the form — EC-019.** The change is **not** propagated silently to the other occurrence; the divergence is flagged at review (FR-REV-002).
- **A2 · The user corrects the underlying record instead.** → **UC-008**. The correction becomes authoritative for all subsequent filling.

## Exception Flows
- **E1 · DOCURA runs again in the same session.** It does not overwrite the user's value (AC-US-018-2).

## Postconditions
- The field holds the user's value, marked as theirs, recorded, and safe from overwrite.

## Business Rules
**BR-012 (user precedence) — governing.** Also BR-015 (reversibility: every automated action must be reversible by the user before submission).

## Requirements Traceability
**FR** FR-FILL-005, FR-FILL-006, FR-REV-002 · **NFR** NFR-OBS-003 (override rate is the primary indicator of silent error) · **US** US-018 · **BR** BR-012, BR-015 · **AC** AC-US-018-1…3 · **EC** EC-013, EC-019

---

# UC-024 — Stop DOCURA

**MVP · MUST**

## Goal
Halt everything, immediately, without losing work already done.

## Primary Actor
User

## Supporting Actors
DOCURA Extension

## Preconditions
- DOCURA is active on a page (UC-013).

## Trigger
The user stops DOCURA.

## Main Success Flow
1. **USER** stops DOCURA — the persistent activity indicator is always visible, so this is always available (FR-EXT-005).
2. **EXTENSION** ceases **all** activity within the current interaction and takes no further action on the page (FR-EXT-006, AC-US-016-1).
3. **EXTENSION** leaves values already placed **in place and untouched thereafter** — nothing is reverted or cleared (FR-EXT-006, AC-US-016-2).
4. **EXTENSION** does not resume when the page changes or new fields appear — **a fresh activation is required** (AC-US-016-3).

## Alternative Flows
- **A1 · User signs out or uninstalls — EC-017.** Extension activity ceases at once. Values already placed remain: **DOCURA does not clean up the user's form.**
- **A2 · User submits while DOCURA is mid-action — EC-018.** DOCURA **never blocks the user's submission**. Any pending action is abandoned rather than applied to a submitted form, and the session ends.

## Exception Flows
- **E1 · Network loss mid-session — EC-014.** Not a stop, but adjacent: DOCURA stops initiating new actions, preserves everything already placed, shows a clear degraded state, and resumes only on explicit user action. **Never leaves a field half-filled.**
- **E2 · Session expires mid-form — EC-016.** All automated action halts immediately. Values already in the form are untouched. Re-authentication is required; nothing is filled from a stale session.

## Postconditions
- No DOCURA activity is in progress. Everything the user had is intact. Resumption requires a deliberate act.

## Business Rules
BR-014 (activation), BR-016 (fail towards inaction).

## Requirements Traceability
**FR** FR-EXT-005, FR-EXT-006 · **NFR** NFR-REL-001, NFR-REL-003 · **AR** AR-AGT-005 (halt on any unexpected page state and hand control to the user rather than adapting) · **US** US-016 · **BR** BR-014, BR-016 · **AC** AC-US-016-1…3 · **EC** EC-014, EC-016, EC-017, EC-018 · **Traces to** P-08, N-10

---

# UC-025 — Review the Completed Form

**MVP · MUST**

## Goal
Replace three anxious re-readings of the form with one verifiable summary.

## Primary Actor
User

## Supporting Actors
DOCURA Extension

## Preconditions
- Filling has finished for every field DOCURA could reach.

## Trigger
The user opens review, or filling completes.

## Main Success Flow
1. **EXTENSION** presents a review summary of the **entire form** before submission (FR-REV-001).
2. **EXTENSION** lists, **prominently and first**, every required field that is unfilled, skipped, or unresolved (FR-REV-004, AC-US-014-2, AC-US-010-5).
3. **EXTENSION** identifies declarations and consent controls that remain uncompleted — **without completing them** (FR-REV-005).
4. **EXTENSION** shows, for every field: the value present, **how it got there** (automatic, answered, approved, or user-entered), and its source document where applicable (FR-REV-002, AC-US-014-1).
5. **EXTENSION** lists every document attached and **the field it was attached to** (FR-REV-003, AC-US-014-3).
6. **EXTENSION** shows the sensitive approvals granted and denied (FR-AUD-003).
7. **EXTENSION** reports what DOCURA could not complete — unknown fields, unsupported field types, missing documents (FR-REV-004, EC-010, EC-005).
8. **USER** selects any review entry; **EXTENSION** brings the corresponding field into view in the form (FR-REV-006, AC-US-014-4).
9. **USER** makes any changes. → **UC-023**, **UC-022**

## Alternative Flows
- **A1 · The same attribute diverges between two fields — EC-019.** The divergence is flagged here rather than silently propagated.
- **A2 · The user adds a missing document manually.** The summary is re-checked; DOCURA does not need to re-derive the whole form to reflect it.

## Exception Flows
- **E1 · A failure occurred earlier in the session.** It was already made visible at the point of failure, not saved up for review (NFR-REL-004). Review restates it rather than revealing it for the first time.

## Postconditions
- The user has seen every value, its provenance, every attachment, every approval, and everything still outstanding — in one place.

## Business Rules
BR-010 (traceability), BR-011 (visibility of action), BR-015 (reversibility before submission).

## Requirements Traceability
**FR** FR-REV-001…006, FR-AUD-003 · **NFR** NFR-REL-004, NFR-A11Y-002, NFR-A11Y-003, NFR-USE-005 · **US** US-014 · **BR** BR-010, BR-011, BR-015 · **AC** AC-US-014-1…4 · **EC** EC-005, EC-010, EC-019 · **Traces to** P-07, S8, N-06
*Exporting or saving the review summary (FR-REV-007) is **FUTURE** — UC-032.*

---

# UC-026 — Hand Back for User Submission

**MVP · MUST**

## Goal
Make the moment of commitment the user's, and make it impossible for DOCURA to take it from them.

## Primary Actor
DOCURA Extension

## Supporting Actors
User, External Form

## Preconditions
- The user has finished review (UC-025).

## Trigger
Review completes.

## Main Success Flow
1. **EXTENSION** hands control back to the user with a **clear statement that submission is theirs to perform** (FR-SUB-003, AC-US-015-1).
2. **EXTENSION** takes **no submission action itself** (FR-SUB-001).
3. **EXTENSION** does **not** activate, click, or otherwise operate the form's submit control (FR-SUB-002, AC-US-015-2).
4. **DOCURA** records that the session reached the hand-back point, and **records no claim about whether the user submitted** (FR-SUB-004, AC-US-015-3).
5. **USER** submits the form.

## Alternative Flows
- **A1 · The user does not submit.** Nothing further happens. DOCURA neither prompts nor retries.
- **A2 · The user submits before review — EC-018.** DOCURA never blocks the submission. Pending action is abandoned rather than applied to a submitted form, and the session ends. *Whether a hand-back is recorded in this case is unspecified in Steps 1–3 — see [Q4-10](questions-and-conflicts.md).*

## Exception Flows
- **E1 · Any confidence level, setting, or user preference is invoked to automate submission.** **Under none of them may submission be automated** (FR-SUB-001). No such control exists to invoke.

## Postconditions
- DOCURA has stopped. The submit control was never operated by DOCURA. The record states that hand-back occurred and asserts nothing beyond it.

## Business Rules
**BR-008 (final submission) — governing, non-negotiable.** Also BR-015, BR-019.

## Requirements Traceability
**FR** FR-SUB-001…004 · **AR** AR-AGT-004 (no agentic action shall navigate, submit, dismiss a dialog, or otherwise alter the state of the page beyond the field it is filling), AR-AGT-006 · **US** US-015 · **BR** BR-008, BR-015 · **AC** AC-US-015-1…3 · **EC** EC-018 · **Traces to** Vision §7, N-07
*Detecting and saving a confirmation or receipt page (FR-SUB-005) is **FUTURE** — UC-032.*

---

# UC-027 — View Session History

**MVP · SHOULD**

## Goal
See what DOCURA did on the user's behalf — and be able to check it later.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- At least one form session has occurred.

## Trigger
The user opens history.

## Main Success Flow
1. **USER** opens the history of a form session (FR-AUD-004).
2. **DOCURA** shows every value it placed, every option it selected, and every document it attached (FR-AUD-001).
3. **DOCURA** shows every question asked and the answer given (FR-AUD-002).
4. **DOCURA** shows every approval request and its outcome (FR-AUD-003).
5. **DOCURA** shows DOCURA's own actions and the fields they affected — and **not the full contents of the third-party form** (FR-AUD-006, BR-017).

## Alternative Flows
- **A1 · The user disagrees with an entry.** History entries are **not editable**; corrections are recorded as **new entries** (FR-AUD-005).

## Exception Flows
- **E1 · The session ended abnormally.** History records what occurred up to that point and makes no claim beyond it — including no claim about submission (FR-SUB-004).

## Postconditions
- The user can account for every automated action, question, and approval in the session.

## Business Rules
BR-010 (traceability), BR-017 (data minimisation — third-party form content is not retained).

## Requirements Traceability
**FR** FR-AUD-001…006, FR-EXT-007 · **NFR** NFR-PRIV-004, NFR-PRIV-007, NFR-OBS-002 · **US** US-017 · **BR** BR-010, BR-017 · **AC** *(none defined for US-017)*
*History export (FR-AUD-007) is **FUTURE**.*

> **Unresolved tension.** FR-AUD-001 requires recording *every value DOCURA placed*, which for a sensitive field
> means retaining a sensitive value in history — while BR-017 and NFR-PRIV-001 require minimisation and FR-SENS-004
> requires masking. Steps 1–3 do not say whether history stores such values in full, masked, or by reference. See
> [Q4-02](questions-and-conflicts.md).

---

# UC-028 — Raise the Sensitivity of an Attribute

**MVP · SHOULD**

## Goal
Let the user tighten protection on something they consider more sensitive than DOCURA does.

## Primary Actor
User

## Supporting Actors
DOCURA

## Preconditions
- The attribute exists in the structured record with a classification (FR-INF-007).

## Trigger
The user raises an attribute's sensitivity.

## Main Success Flow
1. **USER** raises the sensitivity of an attribute — routine to sensitive, or sensitive to consequential (FR-SENS-006).
2. **DOCURA** applies the new classification to both the stored attribute and its use in form filling (FR-SENS-001).
3. Subsequent filling treats the attribute at the raised tier — a raised-to-sensitive attribute now requires per-instance approval (FR-SENS-002). → **UC-021**

## Alternative Flows
- *(none — the requirement defines a single direction of travel)*

## Exception Flows
- **E1 · The user attempts to lower a classification.** **Lowering the consequential tier is not possible for any user** (FR-SENS-006), and an attribute or field classified consequential can never be reclassified downward **by any actor** (BR-020).

## Postconditions
- The attribute carries the raised classification, and every downstream decision honours it.

## Business Rules
**BR-020 (sensitivity floor) — governing.** Also BR-005.

## Requirements Traceability
**FR** FR-SENS-001, FR-SENS-002, FR-SENS-006, FR-INF-007 · **NFR** NFR-MNT-004 · **AR** AR-AST-007 (an assisted component may add a sensitivity classification, never remove one) · **US** *(none — flagged as [Q4-05](questions-and-conflicts.md))* · **BR** BR-005, BR-020 · **AC** *(none defined)*

> This use case depends on assumption **A-5** (users agree with the routine / sensitive / consequential boundary),
> which Step 3 §12.3 lists as untested and load-bearing for all of FR-SENS-001…006.
