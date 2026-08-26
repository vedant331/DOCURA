# Document Lifecycle Flow

**Step 4 · Document 5 of 20** — From a file on the user's disk to a permanently destroyed record, with every failure
path Step 3 specifies.

**Use cases:** UC-006, UC-007, UC-008, UC-009, UC-010, UC-011, UC-012 · **Governing view:** Step 3 §7 Table 7.1

---

## 1. Part 1 — Intake and understanding

<!--DIAGRAM:04a-document-intake-->

## 2. Part 2 — Stored life, retrieval and deletion

<!--DIAGRAM:04b-document-stored-life-->

## 3. The status state machine

The five statuses are exactly those named in FR-UPL-005 — *queued, processing, ready, needs review, failed*. Two
further states, *superseded* and *deleted*, follow from FR-DOC-005/006 and FR-DOC-007/008. Nothing else is invented.

<!--DIAGRAM:16-document-status-states-->

---

## 4. Diagram key — stage to requirement

This is Step 3 §7 Table 7.1 with the Step 4 use case added. It confirms that **every stage of a document's life is
governed** — the check that table exists to make.

| Stage | What must happen | Governed by | Use case |
|---|---|---|---|
| Upload | Accept PDF, JPG, PNG from local storage, singly or in batches, with visible per-document status | FR-UPL-001/002/005 | UC-006 |
| File validation | Check type, size and integrity **before** acceptance; reject with a reason and the accepted alternatives; state limits in advance | FR-UPL-003/004, AR-DET-001 | UC-006 |
| OCR | Extract machine-readable text, including from multi-page documents; retain the original if extraction fails | FR-OCR-001/008/009 | UC-007 |
| Classification | Assign a document type with a confidence, or return **unrecognised** rather than forcing a type | FR-OCR-002/003, AR-AST-002 | UC-007 |
| Information extraction | Extract the defined field set for the type, with per-field confidence | FR-OCR-004/005, FR-INF-001 | UC-007 |
| Confidence | Record confidence at document and field level; **withhold** low-confidence values from automatic use; mark them for review | FR-OCR-005/006, BR-001, BR-002 | UC-007 |
| User correction | Show each value against its source region; allow correction; treat the corrected value as authoritative and preserve it through reprocessing | FR-OCR-007, FR-INF-003, BR-012 | UC-008 |
| Conflict handling | Detect disagreement between documents; surface it; **never resolve automatically** | FR-INF-004/005/006, BR-004 | UC-009 |
| Versioning | Allow a newer version while retaining the previous one; allow one document of a type to be designated primary | FR-DOC-005/006 | UC-010 |
| Search | Find by type, label, extracted text, or attribute value, and identify where the match occurred | FR-SRCH-001…004 | UC-012 |
| Retrieval | Serve the original exactly as uploaded, through time-limited, single-purpose access | FR-DOC-004, NFR-SEC-007 | UC-012 |
| Preparation | Produce constraint-compliant copies without altering the original; stop rather than degrade below the quality floor | FR-MATCH-006/007/010, AR-DET-002, BR-013 | UC-020 |
| Deletion | Delete on request with a confirmation naming what is lost; support a recovery grace period; remove derived copies within the stated period | FR-DOC-007/008, NFR-PRIV-003 | UC-011 |
| Access control | Authorise every access against the requesting user; never infer ownership from a client-supplied identifier; encrypt at rest and in transit | NFR-SEC-001/002/003 | all |

---

## 5. Failure paths, in full

Each is specified behaviour, not a note. In almost every case the behaviour follows from **BR-016: fail towards
inaction and tell the user.**

| # | Failure | Detection | DOCURA's response | Recovery | Automation |
|---|---|---|---|---|---|
| 1 | **Unsupported file** | Deterministic type check before acceptance (AR-DET-001) | Rejected before upload, with the reason **and the accepted types** | User converts or chooses another file | Never started |
| 2 | **Oversized file** | Deterministic size check; limits stated **in advance** (FR-UPL-003) | Rejected before upload | User re-selects | Never started |
| 3 | **Corrupt file** | Integrity check | Rejected with corruption named specifically | Re-export or re-scan | Never started |
| 4 | **Interrupted upload** | Transfer does not complete | **No partial document appears in the vault** | Retry without re-selecting the file (FR-UPL-006) | Resumes on retry |
| 5 | **Duplicate file** | Duplicate detection (FR-UPL-007) | Offers keep both / replace / version — **no silent duplicate** | User chooses | Continues |
| 6 | **OCR failure — EC-001** | Extraction produces nothing usable | Status *failed*; **original retained**; reason stated; retry **and manual entry** both offered | Retry, or the user enters the information manually | Document stays stored and searchable by label |
| 7 | **Poor-quality document — EC-002** | Per-field confidence below the review threshold | Extract what is legible; mark low-confidence fields; tell the user which could not be read confidently | User corrects | Continues, but those values are **withheld from automatic filling** |
| 8 | **Wrong document uploaded — EC-003** | Classification confidence low, or type mismatches | Classify honestly. If clear, store as that type. If unclear, store **unclassified** and ask. **Never force it into an expected slot** | User identifies it | Continues |
| 9 | **Conflicting information — EC-004** | Deterministic conflict detection (AR-DET-008) | Raise a conflict; mark **neither** authoritative; treat any dependent field as ambiguous until resolved | User resolves; alternatives retained | Dependent fields wait |
| 10 | **Missing information** | Attribute absent from the record | Reported as missing at the readiness summary and again at review; **nothing substituted** (BR-009) | User adds a document, or fills manually | Continues on other fields |
| 11 | **Quality floor breached — EC-020** | Preparation cannot meet constraints without unacceptable loss | **Attach nothing**; explain; offer the original for manual handling | User handles it manually | That field only |
| 12 | **Repeat processing** | Same operation, same input | **No duplicate documents, no duplicate attribute entries** (NFR-REL-005) | — | Idempotent |
| 13 | **Processing interrupted** | Component failure mid-pipeline | Recoverable; **the uploaded original is never lost because processing failed** (NFR-REL-002) | Retry | Resumes |

---

## 6. Three invariants the flow enforces

**The original is never modified — BR-013.** Format conversions and resizing produce *copies*. The user can always
open the original exactly as uploaded (FR-DOC-004). This is why the preparation path in Part 2 branches to a copy
rather than transforming the stored file.

**A user correction outranks extraction — BR-012.** Once the user supplies a value it becomes authoritative, and it
survives reprocessing (AC-US-004-3). Extraction can never quietly overwrite a human decision.

**Low confidence is a floor, not a preference — BR-002.** Information extracted below the review threshold is never
used for automatic action, *regardless of how well it matches a field*. This is the requirement that makes R-4
(silent comprehension errors) survivable: "a misread value filled confidently is worse than no automation, because
it defeats the user's own proofreading."

---

## 7. Open parameters

| Parameter | Requirement | Status | How it will be set |
|---|---|---|---|
| Review threshold | BR-002 | TBD | Study S-6 — extraction evaluation on real, imperfect documents |
| Automatic-action threshold | BR-001 | TBD | Study S-6 |
| Deletion grace period | FR-DOC-008 | TBD | To be validated |
| Deletion completion period | NFR-PRIV-003 | TBD | Against legal requirements |
| Quality floor | FR-MATCH-010 | TBD | To be validated |
| MVP language and script set | FR-OCR-012 | TBD | Study S-6 against a real corpus |

Step 3 §7.1 adds a condition worth carrying forward: a document type whose extraction cannot meet the review
threshold on real documents **is moved to store-and-search only rather than shipped as unreliable**.
