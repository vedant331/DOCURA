# DOCURA — Sprint 4 G-12 Per-Document Field Definitions

| Field | Value |
| --- | --- |
| Gap | **G-12 — no field definitions exist for any document type** |
| Status | **PROPOSED — AWAITING APPROVAL.** Nothing in this document is a requirement unless explicitly cited as one from `backend/step3.pdf`. |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0, 25 August 2026 |
| Related | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) — D-04 (document types), **D-05 (field definitions)**, D-06 (sensitivity), gaps G-08…G-16, G-19, G-20, G-27 |
| Related | [`SPRINT_4_D02_OCR_EVALUATION_PLAN.md`](SPRINT_4_D02_OCR_EVALUATION_PLAN.md) — §3.2, §7 (ground-truth layers L4/L5), §11, §12, §17.2, §19 |
| Related | [`SPRINT_4_G02_CORPUS_GOVERNANCE.md`](SPRINT_4_G02_CORPUS_GOVERNANCE.md) — §8.3, §8.6 (redaction scope, blocked on this gap) |
| Explicitly **not** resolved here | **G-13** — the canonical attribute vocabulary. **APPROVED 5 September 2026** (register D-05.6); its seven-property shape is used unaltered in §14–§15 and is not reopened. Also not resolved: **G-09, G-10, G-11, G-19, G-20**. |
| Document structure | **§1–§13 are the original requirements analysis (unchanged).** **§14–§21 are the field-definition authoring added 5 September 2026**, after G-13's approval made a mapping target available. §1–§13 establish that the specification defines nothing; §14–§21 propose what should therefore be authored. |
| Fields invented | **None in §1–§13.** §14–§21 **propose 10 canonical attributes across 13 document types, every one labelled PROPOSED DECISION — REQUIRES APPROVAL.** None is presented as an existing requirement, and `backend/step3.pdf` still defines zero information fields. |
| Documents collected | **0** |
| OCR installed / run | **No** |
| Production code modified | **No** |

---

## 1. Purpose

### 1.1 The question this document answers

**FR-OCR-004** (MVP, MUST) reads:

> "For each supported document type, the system shall extract **the defined set of information fields** for that type."

The requirement is written in the passive voice of something defined elsewhere. This document establishes, by exhaustive search of `backend/step3.pdf`, **where that definition is** — and finds that it is nowhere.

The objective is **not** to invent the field set. It is to state the requirements gap precisely enough that Product Management can close it, and to establish exactly which parts of the D-02 evaluation are and are not blocked by it in the meantime.

### 1.2 The three-way separation maintained throughout

| Category | Marking | Meaning |
| --- | --- | --- |
| What the specification **requires** | **REQUIREMENT** + ID | Quoted from `backend/step3.pdf`. Binding today. |
| What the specification **leaves undefined** | **REQUIREMENTS GAP** + gap ID | An absence. Cannot be closed by engineering judgement. |
| What is **newly proposed here** | **PROPOSED DECISION — REQUIRES APPROVAL** | Not binding until approved. Confined to §10 and §11. |
| What cannot yet be decided | **TBD** | Named, with what would settle it. |

### 1.3 What this document deliberately does not do

It does not author a field set, name a single extractable field, install or run OCR, collect or create documents, modify application code or schemas, create migrations, add dependencies, commit, or push. It does not resolve **G-13**. It does not finalise the MVP document type set — §7.1 makes that the output of study S-6 and **ASM-001** records it as open.

### 1.4 A necessary disambiguation: two meanings of "field"

`step3.pdf` uses the word **field** for two different things, and conflating them makes the gap look smaller than it is.

| Sense | Where | Defined? |
| --- | --- | --- |
| **Form field** — an input on a third-party web page | FR-FRM-002, FR-FLD-001…010, FR-FILL-*, FR-DRP-*, §8 | **Yes, substantially.** Seven types are enumerated (FR-FLD-007), their interpretation carries confidence (FR-FLD-002), an "unknown" outcome is mandatory (FR-FLD-006), and **ASM-008** records the seven-type coverage assumption. |
| **Document information field** — a value read out of a stored document | FR-OCR-004, FR-OCR-005, FR-OCR-006, FR-OCR-007, §7.1, NFR-MNT-001, D2/D3 | **No. Not once, for any type.** |

**G-12 concerns only the second sense.** The comparatively rich treatment of the first is what makes the absence of the second easy to miss.

---

## 2. Source Requirements

Every requirement below is quoted from `backend/step3.pdf`. These are the requirements that either *demand* field definitions or *presuppose* them.

### 2.1 The obligation itself

| ID | Release / Priority | Requirement | Trace |
| --- | --- | --- | --- |
| **FR-OCR-004** | MVP · MUST | "For each supported document type, the system shall extract the defined set of information fields for that type." | L2 |
| **FR-OCR-005** | MVP · MUST | "The system shall record a confidence value for every extracted field independently of the document-level confidence." | BR-001 |
| **FR-OCR-006** | MVP · MUST | "Extracted fields below the review threshold shall be marked as needing user review and shall not be used for automatic filling." | BR-002 |
| **FR-OCR-007** | MVP · SHOULD | "The system shall show each extracted value alongside the region of the source document it was read from." | N-05 |

### 2.2 The requirements that presuppose a defined field set

| ID | Release / Priority | Requirement (abbreviated where marked …) | Why it presupposes field definitions |
| --- | --- | --- | --- |
| **FR-INF-001** | MVP · MUST | "…maintain a structured record of the user's personal information, assembled from all processed documents." | "Assembled from all documents" requires knowing which document field feeds which record entry |
| **FR-INF-002** | MVP · MUST | "Every attribute value shall reference the document it came from and the confidence with which it was read." | Attaches provenance to an entity that must first exist |
| **FR-INF-004** | MVP · MUST | "…detect when two documents give different values for the same attribute." | Requires attribute identity across types — **the hard dependency, and it is G-13's** |
| **FR-INF-007** | MVP · MUST | "Every attribute shall carry a sensitivity classification of routine, sensitive, or consequential." | Tiers attach to enumerable attributes |
| **FR-INF-008** | MVP · MUST | "…normalise attribute formats deterministically — dates, casing, spacing, and numeric precision — without altering meaning." | Normalisers are selected per field/attribute type |
| **FR-ACC-004** | MVP · MUST | "…maintain a user profile of canonical personal attributes derived from documents and editable by the user." | The word *canonical* appears here and nowhere else in the document |
| **FR-SRCH-003** | MVP · SHOULD | "…search by attribute value and receive the supporting document." | Requires addressable attributes |
| **NFR-MNT-001** | MVP · MUST | "Supported document types and their extractable fields shall be definable as configuration, so adding a type does not require re-engineering." | Specifies the *mechanism* for holding field sets; someone must still author their content |
| **AR-AST-008** | MVP | "Assisted components shall be evaluated against a held-out corpus of real, imperfect documents before any threshold is set." | Field extraction cannot be evaluated against an undefined target |
| **EC-019** | — | "The same attribute is requested twice in one form…" | Requires attribute identity |

### 2.3 The scope statement

**§7.1 — Supported document types — MVP**, quoted in full:

> "The MVP supports a defined set of types. Any document outside the set is still stored and searchable, but its information is not extracted into the structured record. The set is deliberately narrow so that extraction quality can be evaluated honestly before it is widened.
>
> Final inclusion of each type is subject to the extraction evaluation in study S-6; a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only rather than shipped as unreliable.
>
> Identity and address — Aadhaar, PAN, address proof.
> Education — 10th marksheet, 12th marksheet, semester result, degree certificate.
> Application assets — photograph, signature, student ID, hall ticket, resume.
> Other — stored and searchable as an unclassified document, no structured extraction. **ASM-001**"

**§7.1 is the only enumeration of document types in the specification.** It names types. It defines no fields.

### 2.4 The assumption that governs the set

> **ASM-001** — "The MVP document type set is the right one — broad enough to demonstrate value, narrow enough to extract reliably." · Affects **§7.1, FR-OCR-004** · Settled by "Study S-6 extraction evaluation on a real corpus."

**ASM-001 explicitly names FR-OCR-004 as affected.** The specification therefore knows that the type set and the extraction obligation are both provisional — but it registers the *type set* as the assumption and leaves the *field set* undocumented entirely.

---

## 3. Document Type Inventory

### 3.1 Method

Every occurrence of a document-type noun in `backend/step3.pdf` was located and read in context. Types were recorded only where the specification **names** them. No type was added from domain knowledge, and no type was inferred from a form-field name, a persona, or an example journey.

### 3.2 Types named by the specification

| # | Exact name used | Reference | Context | Explicitly in the intended MVP type set? | Fields defined? |
| --- | --- | --- | --- | --- | --- |
| 1 | **Aadhaar** | §7.1, "Identity and address" | Type-set enumeration | **Yes** — subject to S-6 (§7.1, ASM-001) | **No** |
| 2 | **PAN** | §7.1, "Identity and address" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 3 | **address proof** | §7.1, "Identity and address" | Type-set enumeration | **Yes as written** — but it is a *category*, not a document type; its members are never enumerated (**G-09**) | **No** |
| 4 | **10th marksheet** | §7.1, "Education" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 5 | **12th marksheet** | §7.1, "Education" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 6 | **semester result** | §7.1, "Education" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 6a | **semester marksheet** | AC-US-003-1 | Acceptance criterion: "GIVEN the user has uploaded a semester marksheet… THEN the document appears in the vault classified as **a marksheet**" | **TBD** — same type as #6, a distinct type, or a family label (**G-10**) | **No** |
| 6b | **marksheet** | AC-US-003-1; NFR-USE-005 | AC-US-003-1 as the resulting classification; NFR-USE-005 as an example of user-facing product language | **TBD** — whether "marksheet" is a type, a family covering #4/#5/#6, or only a display word (**G-10**) | **No** |
| 7 | **degree certificate** | §7.1, "Education" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 8 | **photograph** | §7.1, "Application assets"; NFR-USE-005 (as a user-facing word) | Type-set enumeration | **Yes** — but whether it is an *extraction* type is never stated (**G-11**) | **No — and whether any exist is undefined** |
| 9 | **signature** | §7.1, "Application assets" | Type-set enumeration | **Yes** — same qualification as #8 (**G-11**) | **No — and whether any exist is undefined** |
| 10 | **student ID** | §7.1, "Application assets" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 11 | **hall ticket** | §7.1, "Application assets" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 12 | **resume** | §7.1, "Application assets" | Type-set enumeration | **Yes** — subject to S-6 | **No** |
| 13 | **Other / unclassified document** | §7.1, "Other"; AC-US-003-3 | "stored and searchable as an unclassified document, **no structured extraction**" | **Yes — as the explicit non-extraction case** | **N/A — the specification states there are none. This is the one fully specified extraction behaviour in the entire type set.** |

### 3.3 Type-adjacent terms that are NOT document types

Recorded so they are not mistaken for types later:

| Term | Reference | What it actually is |
| --- | --- | --- |
| **unrecognised** | FR-OCR-002, AR-AST-002 | A classification *outcome*, not a type. Note the vocabulary inconsistency with "unclassified" (AC-US-003-3, §7.1) — the specification uses both words for what appears to be one state, and **G-08** records that the resulting state is never modelled. |
| **declaration** | NFR-USE-005, FR-FLD-004, BR-006 | A *form control* (a consent/agreement control on a third-party page), never a stored document type. NFR-USE-005 lists it beside "marksheet" and "photograph" only as an example of user-facing vocabulary. |
| **"a controlled mock application form", "an MCA-style application"** | §10, ASM-002 | The MVP *demonstration surface*, not a stored document. |
| **"Several real document types"** | §10.1, step D1 | An unquantified reference back to §7.1. Names no type and adds none. |
| **confirmation or receipt page** | FR-SUB-005 (FUTURE, WON'T) | A future capability, explicitly excluded in §10.3. Not an MVP type. |

### 3.4 Inventory findings

1. **Thirteen type names appear, in exactly one place: §7.1.** No other section of the specification adds, removes, or refines a type.
2. **The set is provisional by the specification's own statement.** §7.1 subjects final inclusion to study S-6; ASM-001 records the whole set as an untested assumption. Any list presented as "the MVP types" before S-6 reports would be an invention with the appearance of a requirement.
3. **Three of the thirteen entries are not usable as types as written:** "address proof" is a category (**G-09**); "semester result" may or may not be the same thing as the "semester marksheet"/"marksheet" of AC-US-003-1 (**G-10**); "photograph" and "signature" may or may not be extraction types at all (**G-11**).
4. **Zero of the thirteen have a field set.**

---

## 4. Field and Attribute References

### 4.1 Method

The specification text was searched for every term the brief lists — *field, attribute, extracted information, structured information, metadata, identity information, document information, names, dates, numbers, identifiers, addresses, classifications* — plus every noun that could name a piece of information the system understands. Every hit was read in context and classified. Occurrences in the **form-field** sense (§1.4) are excluded from §4.2 and §4.3 and listed separately in §4.5.

### 4.2 Document-level fields that ARE explicitly required

This is the one place the specification does define fields. They are **document metadata**, not extracted content.

| # | Exact wording | Reference | Document type | Explicitly required? | Type/format defined? | Provenance requirement defined? |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | "its **type**, date added, and processing status" | FR-DOC-001 | All | **Yes (MUST)** | Domain = §7.1 type set + unclassified. Value undefined per type only insofar as §7.1 is provisional | N/A — assigned by the system (FR-DOC-002) |
| M2 | "type, **date added**, and processing status" | FR-DOC-001 | All | **Yes (MUST)** | Not defined (a timestamp is implied, never stated) | N/A — system-generated |
| M3 | "type, date added, and **processing status**" | FR-DOC-001; **FR-UPL-005** | All | **Yes (MUST)** | **Yes — enumerated: "queued, processing, ready, needs review, or failed"** (FR-UPL-005). The only enumerated value domain in the specification | N/A — system-generated |
| M4 | "a **document type**, assigned automatically and correctable by the user" | FR-DOC-002 | All | **Yes (MUST)** | Domain = §7.1 | Automatic assignment, user-correctable |
| M5 | "a **confidence value for the classification**" | FR-OCR-003 | All | **Yes (MUST)** | **No** — no scale or semantics (**G-06**) | Document-level |
| M6 | "a **personal label** without altering its type" | FR-DOC-003 | All | Yes (COULD) | Free text, implied | User-supplied |
| M7 | "a newer **version** of an existing document, retaining the previous version" | FR-DOC-005 | All | Yes (SHOULD) | Not defined | System |
| M8 | "designate one as **primary** for automatic use" | FR-DOC-006 | All (where several of one type exist) | Yes (SHOULD) | Boolean, implied | User-designated |
| M9 | "machine-readable **text**" from the document | FR-OCR-001 | All | **Yes (MUST)** | Not defined (whole-document text; no structure required) | Per document; multi-page documents are one document (FR-OCR-008) |

**M1–M9 are implementable today.** Sprint 3 already implements most of them. **None of them is an "information field" in the FR-OCR-004 sense** — none is a value read *out of* the document's content into the structured record.

### 4.3 Extracted-information field references — the actual G-12 surface

| # | Exact wording | Reference | Associated document type | Explicitly required? | Type/format defined? | Provenance defined? | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | "the **defined set of information fields** for that type" | FR-OCR-004 | "each supported document type" — i.e. all of §7.1 | **The obligation is required (MUST). The set is never stated.** | **No** | **No** | **UNDEFINED** |
| F2 | "a confidence value for **every extracted field**" | FR-OCR-005 | All | Yes (MUST) — but it applies to a field set that does not exist | **No** — no scale, no semantics (**G-06**) | Independent of document-level confidence — that much *is* specified | **PARTIALLY DEFINED** (obligation defined, subject undefined) |
| F3 | "**Extracted fields** below the review threshold" | FR-OCR-006 | All | Yes (MUST) | Threshold has no value (**G-04**) | — | **PARTIALLY DEFINED** |
| F4 | "each extracted value alongside the **region of the source document** it was read from" | FR-OCR-007 | All | Yes (SHOULD) | Region representation not defined | **Yes — this is an explicit field-level provenance requirement** | **PARTIALLY DEFINED** (obligation clear, subject undefined) |
| F5 | "a **structured record** of the user's personal information" | FR-INF-001 | Assembled across all | Yes (MUST) | **No** — contents never enumerated | — | **UNDEFINED (contents)** |
| F6 | "**Every attribute value** shall reference the document it came from and the confidence with which it was read" | FR-INF-002 | All | Yes (MUST) | **No** | **Yes — document reference + confidence, mandatory for every value** | **DEFINED (the provenance rule); UNDEFINED (what an attribute is)** |
| F7 | "two documents give different values for **the same attribute**" | FR-INF-004 | Cross-type | Yes (MUST) | **No** | — | **UNDEFINED — requires attribute identity (G-13)** |
| F8 | "**Every attribute** shall carry a sensitivity classification of routine, sensitive, or consequential" | FR-INF-007 | All | Yes (MUST) | **Tier names are defined; the rules that assign them are not (G-14), and there is no default tier (G-15)** | — | **PARTIALLY DEFINED** |
| F9 | "normalise **attribute formats** deterministically — **dates, casing, spacing, and numeric precision**" | FR-INF-008 | All | Yes (MUST) | **Categories are named; no rule is stated for any of them** | — | **PARTIALLY DEFINED — categories only** |
| F10 | "a history of changes to **each attribute**, including who or what changed it" | FR-INF-009 | All | Yes (SHOULD) | **No** | **Yes — actor recorded per change** | **PARTIALLY DEFINED** |
| F11 | "a user profile of **canonical personal attributes** derived from documents" | FR-ACC-004 | Cross-type | Yes (MUST) | **No — "canonical" is used once and never defined** | Derived from documents; user-editable | **UNDEFINED — this is G-13's subject** |
| F12 | "search by **attribute value**" | FR-SRCH-003 | Cross-type | Yes (SHOULD) | **No** | Returns "the supporting document" | **UNDEFINED (subject)** |
| F13 | "Supported document types and their **extractable fields** shall be definable as configuration" | NFR-MNT-001 | All | **Yes (MUST) — for the mechanism** | **No content** | — | **DEFINED (mechanism) / UNDEFINED (content)** |
| F14 | "the same attribute is requested twice in one form" | EC-019 | Cross-type | Required behaviour | **No** | — | **UNDEFINED (subject)** |
| F15 | "each document classified and **its information extracted with per-field confidence**" | §10.1 step D2 | Demonstration journey | Demonstration obligation | **No** | — | **UNDEFINED (subject)** |
| F16 | "A structured record assembled, **each value linked to its source**; low-confidence values flagged for review" | §10.1 step D3 | Demonstration journey | Demonstration obligation | **No** | **Yes — value-to-source link** | **UNDEFINED (subject)** |
| F17 | "Extract the **defined field set** for the document type, with per-field confidence" | §7.1 lifecycle table (Information extraction row) | All | Restates FR-OCR-004/005 — §7 explicitly "references rather than repeats" (§0.3) | **No** | — | **UNDEFINED** |

### 4.4 Field-like nouns that are EXAMPLES ONLY — not requirements

These are the passages most likely to be mistaken for a field definition. **None of them is one.**

| Wording | Reference | Why it is not a field definition |
| --- | --- | --- |
| "**dates, casing, spacing, and numeric precision**" | FR-INF-008, AR-DET-003 | **Normalisation categories**, listed to scope the normaliser's job. They name *kinds of transformation*, not fields. No date field, and no date format, is named anywhere. |
| "**marksheet**, **photograph**, **declaration**" | NFR-USE-005 | Explicitly an example of **product language** — "name things as users do… not as the system models them". Two are document types (§7.1); one is a form control. None is a field. |
| "**Name mismatches** (P-06)" | §12.2 prioritisation rationale; §13.1 traceability (P-06 "Detail mismatch") | Names a *pain* from document 02 and the reason conflict detection is MUST. It **implies** that a name attribute will exist. It does not define one, does not name it, and gives it no format. |
| "Government identifier numbers, bank details, signature images, category and income details" / "Name, date of birth, education history, marks, addresses" | **Document 02, Table 13.1** — cited *by reference only* from FR-INF-007 and FR-SENS-001; the table itself is **not reproduced in `step3.pdf`** | A **working sensitivity classification for research purposes**, tied to untested assumption **A-5** (§12.3: "the sensitivity boundary is wrong"). It is a list of **sensitivity examples**, and **G-14** records that the classification rules are not in `step3.pdf` at all. **Promoting this list into a field schema would convert an untested research assumption into a requirement.** It must not be done. |
| "text, number, date, dropdown, radio, checkbox, and file-upload" | FR-FLD-007 | **Form-field types** (§1.4, second sense). Not document information fields, and not a data-type system for extracted values. |
| "length, pattern, accepted file types, size limits" | FR-FRM-004 | Constraints a **third-party form** declares about its own inputs. Nothing to do with what DOCURA extracts. |
| "**a semester marksheet**" | AC-US-003-1 | A type name used in a test scenario, not a field. Its own type identity is unresolved (**G-10**). |

### 4.5 "Field" occurrences excluded as form-field sense

FR-FRM-002/003/004, FR-FLD-001…010, FR-FILL-001…008, FR-DRP-001…009, FR-AMB-001…007, FR-MATCH-001…010, FR-REV-002/004, FR-APR-*, FR-SENS-002/003/005, EC-006…EC-020, §8 Table 8.1, §10.1 steps D5–D13, AR-DET-007, AR-AST-003. **All concern inputs on a third-party page.** They are well specified and are not part of G-12.

### 4.6 The finding

**Across 39 pages, 157 functional and 57 non-functional requirements, 20 business rules, 22 automation requirements, 24 user stories, and 20 edge cases, the specification names exactly one enumerated value domain for anything read from or held about a document — the five processing-status values of FR-UPL-005 — and it names zero information fields for zero document types.**

---

## 5. Requirements Matrix

Statuses: **DEFINED** · **PARTIALLY DEFINED** · **EXAMPLE ONLY** · **UNDEFINED** · **TBD**

### 5.1 Per document type — extracted information fields (the FR-OCR-004 obligation)

| Document Type | Field/Attribute | Explicit Requirement? | Source Requirement | Format Defined? | Provenance Defined? | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Aadhaar | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | Rule defined (FR-INF-002), subject not | **UNDEFINED** |
| PAN | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| address proof | *none stated* — and the type itself is a category (**G-09**) | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** (type undefined first) |
| 10th marksheet | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| 12th marksheet | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| semester result | *none stated* — type name unresolved (**G-10**) | Obligation yes, set no | FR-OCR-004, §7.1, AC-US-003-1 | No | As above | **UNDEFINED** (naming first) |
| degree certificate | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| photograph | *unknown whether any exist* (**G-11**) | **Not determinable** | §7.1, FR-OCR-004, FR-INF-007 | No | — | **TBD** |
| signature | *unknown whether any exist* (**G-11**) | **Not determinable** | §7.1, FR-OCR-004, FR-INF-007 | No | — | **TBD** |
| student ID | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| hall ticket | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| resume | *none stated* | Obligation yes, set no | FR-OCR-004, §7.1 | No | As above | **UNDEFINED** |
| Other / unclassified | **No fields — explicitly none** | **Yes** | §7.1 ("no structured extraction"), AC-US-003-3 | N/A | N/A | **DEFINED** |

**One row of thirteen is defined, and it is the row that defines an absence of extraction.**

### 5.2 Cross-type document metadata (all types)

| Document Type | Field/Attribute | Explicit Requirement? | Source Requirement | Format Defined? | Provenance Defined? | Status |
| --- | --- | --- | --- | --- | --- | --- |
| All | document type | **Yes — MUST** | FR-DOC-001, FR-DOC-002 | Domain = §7.1, itself provisional (ASM-001) | Auto-assigned, user-correctable | **PARTIALLY DEFINED** |
| All | date added | **Yes — MUST** | FR-DOC-001 | No | System | **PARTIALLY DEFINED** |
| All | processing status | **Yes — MUST** | FR-DOC-001, **FR-UPL-005** | **Yes — queued / processing / ready / needs review / failed** | System | **DEFINED** |
| All | classification confidence | **Yes — MUST** | FR-OCR-003 | **No scale or semantics (G-06)** | Document-level | **PARTIALLY DEFINED** |
| All | personal label | Yes — COULD | FR-DOC-003 | Free text implied | User | **PARTIALLY DEFINED** |
| All | version lineage | Yes — SHOULD | FR-DOC-005 | No | System | **PARTIALLY DEFINED** |
| All | primary designation | Yes — SHOULD | FR-DOC-006 | Boolean implied | User | **PARTIALLY DEFINED** |
| All | extracted document text | **Yes — MUST** | FR-OCR-001, FR-OCR-008 | No | Whole document, all pages | **PARTIALLY DEFINED** |
| All | failure reason (on failed processing) | **Yes — MUST** | FR-OCR-009, AC-US-003-5, EC-001 | No | System | **PARTIALLY DEFINED** |

### 5.3 Properties every extracted field must carry (defined as rules, applied to an undefined set)

| Property | Explicit Requirement? | Source Requirement | Defined? | Status |
| --- | --- | --- | --- | --- |
| Per-field confidence, independent of document-level | **Yes — MUST** | FR-OCR-005 | Obligation yes; scale and semantics no (**G-06**) | **PARTIALLY DEFINED** |
| Source-document reference | **Yes — MUST** | FR-INF-002, BR-010, §10.1 D3 | **Yes — mandatory for every value** | **DEFINED** |
| Source region within the document | Yes — SHOULD | FR-OCR-007, AC-US-004-1 | Obligation yes; representation no | **PARTIALLY DEFINED** |
| Sensitivity tier (routine / sensitive / consequential) | **Yes — MUST** | FR-INF-007, FR-SENS-001 | Tier names yes; assignment rules no (**G-14**); default no (**G-15**) | **PARTIALLY DEFINED** |
| Review-threshold marking | **Yes — MUST** | FR-OCR-006, BR-002 | Behaviour yes; threshold value no (**G-04**) | **PARTIALLY DEFINED** |
| Deterministic normalisation | **Yes — MUST** | FR-INF-008, AR-DET-003 | Categories yes; rules no | **PARTIALLY DEFINED** |
| User correction, and its precedence over extraction | **Yes — MUST** | FR-INF-003, BR-012, AC-US-004-2/3 | **Yes — behaviour fully specified** | **DEFINED** |
| Change history with actor | Yes — SHOULD | FR-INF-009 | Obligation yes; which history (**G-28**) and duplicate semantics (**G-20**) no | **PARTIALLY DEFINED** |
| Conflict participation across documents | **Yes — MUST** | FR-INF-004/005/006, BR-004 | Behaviour yes; attribute identity no (**G-13**) | **PARTIALLY DEFINED** |
| Mandatory vs optional | **No — never mentioned for any field** | — | No | **UNDEFINED** |
| Data type | **No** | — | No | **UNDEFINED** |
| Multiple / repeating values | **No** | — | No | **UNDEFINED** |
| Missing-field behaviour (a field absent from a document of its type) | **No** | — | No | **UNDEFINED** |
| Canonical identifier / name | **No** | FR-ACC-004 names "canonical" without contents | No | **UNDEFINED — G-13** |

---

## 6. What Is Actually Defined

The specification is not silent about extraction. It is silent about *what is extracted*. Precisely these things **are** defined and are implementable or testable today:

1. **That a defined field set must exist per type, and that extraction must follow it** — FR-OCR-004.
2. **Where field sets live**: configuration, not code, so adding a type needs no re-engineering — NFR-MNT-001.
3. **That every extracted field carries its own confidence, independent of the document-level confidence** — FR-OCR-005. The independence is explicit and is a testable structural property.
4. **That a below-threshold field is marked for review and never used for automatic filling** — FR-OCR-006, BR-002, AC-US-004-4.
5. **That every value carries provenance**: the document it came from and the confidence it was read with — FR-INF-002; reinforced by BR-010 ("every value DOCURA places must be attributable to a source document or to an answer the user gave") and §10.1 D3.
6. **That every value can be shown against the region it was read from** — FR-OCR-007, AC-US-004-1.
7. **That the user's correction is authoritative and survives reprocessing** — FR-INF-003, BR-012, AC-US-004-2, AC-US-004-3.
8. **That conflicts between documents are detected deterministically, surfaced, and never auto-resolved** — FR-INF-004/005/006, BR-004, AR-DET-008, EC-004.
9. **The three sensitivity tier names, and that every attribute carries one** — FR-INF-007, FR-SENS-001; with monotonicity (AR-AST-007, BR-020) and a reviewable rule set (AR-DET-005, NFR-MNT-004).
10. **The normalisation categories**: dates, casing, spacing, numeric precision — deterministic and reversible — FR-INF-008, AR-DET-003.
11. **Document metadata fields** — §4.2, M1–M9 — including the only enumerated value domain in the specification, FR-UPL-005's five processing states.
12. **That the "Other" type extracts nothing** — §7.1. The single fully specified extraction behaviour in the type set.
13. **That the field sets are provisional and evaluation-gated** — §7.1's demotion rule and ASM-001. A type whose extraction cannot meet the review threshold on real documents is moved to store-and-search only.

**Read together, items 1–13 are a complete specification of the *envelope* around an extracted field, and no specification of the field itself.** The specification defines the box; it never says what goes in it.

---

## 7. What Is Not Defined

### 7.1 The answers required by Step 4 of the brief

**A. Does `step3.pdf` define a complete field set for every document type?**
**No. Not defined in step3.pdf** — for any type. FR-OCR-004 requires "the defined set of information fields for that type"; §7.1 enumerates type names only; NFR-MNT-001 says field sets are configuration but authors no configuration. The single exception is "Other", for which §7.1 defines the set as empty.

**B. Does it define a minimum required field set?**
**Not defined in step3.pdf.** No floor, no core set, no "at minimum" clause anywhere. §10.1 steps D2 and D3 require the demonstration to show "information extracted with per-field confidence" and "a structured record assembled" without naming a single value that must appear.

**C. Does it define which fields are mandatory vs optional?**
**Not defined in step3.pdf.** The distinction is never raised for document fields. (FR-FRM-003 requires reading which fields *a third-party form* marks required — that is the form-field sense, §1.4, and carries no implication for document fields.)

**D. Does it define field data types?**
**Not defined in step3.pdf.** FR-INF-008 names normalisation categories — "dates, casing, spacing, and numeric precision" — which imply that some values are dates and some are numeric, but no field is assigned a type and no type system is defined. FR-FLD-007's seven types are form-input types, not value types.

**E. Does it define normalization rules?**
**Partially.** FR-INF-008 (MUST) and AR-DET-003 (MVP) require normalisation to be deterministic, reversible, and meaning-preserving, and name four categories. **No rule for any category is stated** — no canonical date representation, no casing rule, no whitespace rule, no precision rule. AC-US-008-4 requires a date to be reformatted to a form's declared format "without altering the date", which constrains *output* formatting at fill time; it does not define a stored representation.

**F. Does it define how multiple values are represented?**
**Not defined in step3.pdf.** Nothing addresses repeating groups (per-subject marks on a marksheet being the obvious case), multi-valued attributes, or ordered lists. FR-INF-006 requires that when the user designates one value authoritative the alternatives are *retained* — that is conflict alternatives, a different concept from a field legitimately holding several values.

**G. Does it define missing-field behaviour?**
**Not defined in step3.pdf** at the field level. Adjacent requirements exist and do not cover it: FR-INF-010 (indicating missing commonly-required information) is **FUTURE/WON'T**; FR-AMB-001 makes a *form* field ambiguous when "the required information is absent"; EC-002 covers a field that could not be *read* confidently from a poor-quality document. **What none of them defines is the state of a field that a document of its type simply does not contain** — absent, null, not-applicable, or extraction-failed. **G-27** records the related absence: FR-OCR-009's "manual-entry path" has no defined destination while no field set exists.

**H. Does it define conflicting-field behaviour?**
**Yes, at the level of behaviour — and it is one of the better specified areas.** FR-INF-004 (detect), FR-INF-005 (surface, never auto-resolve), FR-INF-006 (record the designated value, retain alternatives), BR-004 (never resolve by rule, recency, or preference), AR-DET-008 (detection deterministic; resolution never automated), EC-004, AC-US-005-1/2/3, and the human-decision point in §6.4 all govern it. **What is not defined is what "the same attribute" means** — the identity relation the whole mechanism operates on (**G-13**) — and AC-US-005-3's "appears in history" does not say which history (**G-28**). So: behaviour DEFINED, subject UNDEFINED.

**I. Does it define fields that are allowed to contain sensitive information?**
**Not defined in step3.pdf.** FR-INF-007 requires *every* attribute to carry one of three tiers and FR-SENS-001 requires the classification to be maintained for stored attributes and form fields alike; AR-DET-005 requires a reviewable rule set; NFR-MNT-004 requires the rules to be a reviewable list. **The rules themselves are not in `step3.pdf`** (**G-14**) — the referenced document 02 Table 13.1 is an ASM-tagged working classification bound to untested assumption **A-5** — and there is **no default tier for an attribute no rule covers** (**G-15**). Document-level sensitivity is presupposed by FR-MATCH-009 and EC-011 and defined nowhere (**G-16**). Note also that no requirement anywhere *prohibits* a field from holding sensitive content; the model is to classify and gate disclosure, not to refuse storage.

**J. Does it define whether fields may be automatically used downstream?**
**Yes — this is well specified, and it is conditional rather than per-field.** BR-001 permits automatic action only where both the field interpretation and the source value meet the automatic-action threshold; BR-002 bars any below-review-threshold value from automatic action "regardless of how well it matches a field"; FR-OCR-006 marks such fields for review and bars automatic filling; FR-FILL-001 additionally requires the *form* field to be classified routine; BR-005/FR-SENS-002 require per-instance approval for sensitive disclosure; BR-009 forbids guessing. **What is not defined is the threshold value** (**G-04**), the relationship between the two thresholds (**G-05**), the confidence scale (**G-06**), and whether thresholds are global or per type (**G-07**). So: the gate is defined; its setting is not. **No field is granted or denied downstream use by virtue of being that field.**

**K. Does it define field-level confidence requirements?**
**Yes, as an obligation.** FR-OCR-005 (MUST) requires a confidence value for every extracted field, explicitly independent of the document-level value; AR-AST-001 requires text extraction to produce a confidence "usable by BR-001"; AR-AST-007 forbids an assisted component from raising its own confidence; AC-US-003-2 requires every extracted field to be shown with its own confidence indication. **What is not defined is what the number means** — no scale, no bounds, no calibration semantics, no cross-component comparability (**G-06**) — which is what makes BR-001 untestable as written.

**L. Does it define field-level provenance requirements?**
**Yes — the strongest of the twelve answers.** FR-INF-002 (MUST): every attribute value references the document it came from *and* the confidence it was read with. FR-OCR-007 (SHOULD) and AC-US-004-1: the value is shown against the region it was read from. AR-AST-006 (MVP): every assisted output is explainable in terms of the source it came from. BR-010: every placed value is attributable to a source document or a user answer. FR-INF-009 (SHOULD): change history including who or what changed it. §10.1 D3: each value linked to its source. **What is not defined is the representation of a region, and which history a change is written to (G-28).**

### 7.2 Summary of the twelve answers

| # | Question | Answer |
| --- | --- | --- |
| A | Complete field set per type? | **No — not defined in step3.pdf for any type** |
| B | Minimum required field set? | **Not defined in step3.pdf** |
| C | Mandatory vs optional? | **Not defined in step3.pdf** |
| D | Field data types? | **Not defined in step3.pdf** |
| E | Normalisation rules? | **Partially — four categories named, no rule stated** |
| F | Multiple values? | **Not defined in step3.pdf** |
| G | Missing-field behaviour? | **Not defined in step3.pdf** |
| H | Conflicting-field behaviour? | **Yes for behaviour; the subject ("same attribute") is undefined — G-13** |
| I | Fields allowed to hold sensitive information? | **Tiers defined; assignment rules not in step3.pdf — G-14, G-15, G-16** |
| J | Automatic downstream use? | **Yes — conditional on thresholds; the values are TBD — G-04…G-07** |
| K | Field-level confidence? | **Yes as an obligation; the scale and semantics are undefined — G-06** |
| L | Field-level provenance? | **Yes — document reference and confidence are mandatory per value** |

---

## 8. G-12 Requirements Gap

### 8.1 Statement of the gap

**G-12 — `backend/step3.pdf` requires the extraction of "the defined set of information fields" for each supported document type (FR-OCR-004, MVP, MUST) and defines that set for no type. Twelve of the thirteen §7.1 entries have no field definition; the thirteenth ("Other") is defined as having none.**

The specification defines the obligation, the storage mechanism (NFR-MNT-001, configuration), and every property a field must carry — confidence, provenance, sensitivity tier, normalisation, correction precedence, conflict participation. It never defines a field.

### 8.2 What this is not

- **It is not an engineering difficulty.** No amount of design work, corpus collection, or OCR evaluation produces a field set; the set is the input those activities consume.
- **It is not a TBD in the specification's own sense.** §2's preamble marks a needed-but-unknowable *number* as "TBD — to be validated" and assigns it a study; twelve such markers exist. **FR-OCR-004 carries no TBD marker at all.** The specification does not appear to know that this definition is missing — unlike BR-001's threshold, which it flags explicitly. That is what makes G-12 different in kind from G-04.
- **It is not covered by ASM-001.** ASM-001 registers the *type set* as an assumption to be settled by S-6. The *field sets* are not registered anywhere, as an assumption or otherwise.
- **It is not resolvable by engineering judgement.** These fields determine what DOCURA reads out of a real person's identity documents and holds about them. Under **BR-017** (data minimisation) and **NFR-PRIV-001** (collect only what a requested function needs), the field set is a privacy decision as much as a functional one.

### 8.3 Consequences — what is blocked

| Requirement | Priority | Consequence |
| --- | --- | --- |
| **FR-OCR-004** | MUST | Unimplementable as written for every type |
| **FR-OCR-005** | MUST | The independent-confidence *structure* is buildable; there is nothing to attach it to |
| **FR-OCR-006** | MUST | Behaviour is specified; the subject and the threshold are both missing (**G-04**) |
| **FR-OCR-007** | SHOULD | Region provenance for *field values* has no field values |
| **FR-INF-001, FR-INF-002** | MUST | Structured record has undefined contents |
| **FR-INF-004/005/006** | MUST | Conflict detection has no attribute identity (**G-13**) — **US-005 blocked in full** |
| **FR-INF-007** | MUST | Nothing enumerable to classify |
| **FR-INF-008** | MUST | No field to attach a normaliser to |
| **FR-ACC-004** | MUST | Profile of "canonical personal attributes" has no contents (**G-13**) |
| **FR-SRCH-003** | SHOULD | No addressable attributes |
| **NFR-MNT-001** | MUST | Mechanism READY; content missing |
| **FR-OCR-009** | MUST | The *manual-entry path* has no destination (**G-27**); retain-original and state-the-reason are unaffected |
| **§7.1 demotion rule** | — | A type cannot be demoted on extraction evidence that cannot be produced |
| **AC-US-003-2, AC-US-004-1…4, AC-US-005-1…3** | — | Not executable as tests |
| **§10.1 steps D2, D3** | — | Not demonstrable in the field-extraction half |
| **G-02.7 redaction scope** | — | Derived-artefact redaction scope cannot be finalised — governance §8.3/§8.6 holds an interim rule pending G-12 |

### 8.4 Relationship to neighbouring gaps

```
G-13  canonical attribute vocabulary   (what DOCURA knows about a person)
  │      FR-ACC-004, FR-INF-001/004/007/008, FR-SRCH-003, EC-019
  │      each attribute: meaning, value type, normalisation rule, sensitivity tier
  ▼
G-12  per-type field sets              (what DOCURA reads from each document)
  │      FR-OCR-004/005, NFR-MNT-001
  │      each field: which type, mandatory/optional, format, → one attribute or explicitly none
  ├──► G-09  address proof is a category, not a type    (must be settled before its fields)
  ├──► G-10  semester result vs semester marksheet      (must be settled before its fields)
  ├──► G-11  do photograph and signature extract at all (must be settled before their fields)
  ├──► G-14/G-15/G-16  sensitivity rules, default tier, document-level sensitivity
  ├──► G-19/G-20  profile vs structured record; duplicate attribute entries
  └──► G-27  manual-entry destination
       │
       ▼
D-02 stage 2   field-extraction evaluation, calibration, BR-001 threshold, §7.1 type inclusion
       │            gated additionally on G-04, G-05, G-06, G-07
       ▼
FR-OCR-004/005/006 committed to build   (also gated by §12.3 A-7)
```

**G-13 is upstream of G-12.** A per-type field set whose fields do not map to a shared vocabulary cannot satisfy FR-INF-001's "assembled from all processed documents" or FR-INF-004's "the same attribute". This ordering is why §11 recommends authoring the vocabulary first and why this document does not attempt G-13's content.

---

## 9. Impact on Evaluation

### 9.1 The dependency chain

```
Document
   │  (corpus governance — G-02, APPROVED 3 Sep 2026; corpus not yet collected)
   ▼
OCR text ─────────────────► character/word accuracy, page coverage, failure behaviour
   │                          NOT blocked by G-12
   ▼
Document classification ──► per-type precision/recall, unrecognised-rate, confidence behaviour
   │                          NOT blocked by G-12 (blocked by G-10 for one type boundary)
   ▼
Field extraction ─────────► per-field precision/recall against field-level ground truth
   │                          FULLY BLOCKED by G-12 and G-13
   ▼
Field-level evaluation ───► per-field error analysis, per-type extraction quality
   │                          FULLY BLOCKED
   ▼
Confidence calibration ───► does a confidence of X mean X% correct?
   │                          BLOCKED at field level (G-12); also needs G-06
   ▼
Threshold decision ───────► BR-001 automatic-action threshold, BR-002 review threshold
   │                          BLOCKED (G-04, G-05, G-06, G-07 and the calibration above)
   ▼
§7.1 type inclusion ──────► which types ship extracting, which are demoted to store-and-search
                              BLOCKED — the evidence is per-type extraction quality
```

### 9.2 What can proceed without G-12

The specification supports evaluating OCR and classification independently of field definitions, and **the D-02 plan is already structured around that split** (§3.2, §19). Specifically:

| Stage | Blocked by G-12? | Basis |
| --- | --- | --- |
| **Corpus collection and governance** | **No** | AR-AST-008 requires real, imperfect documents. Governance is approved (G-02). Collection depends on the type *names* (§7.1), not on field sets. |
| **Ground truth L1 — document type label** | **No** | Requires only §7.1's type names. Subject to G-10 for the marksheet boundary. |
| **Ground truth L2 — page-level full text** | **No** | FR-OCR-001 requires machine-readable text with no structure imposed. |
| **Ground truth L3 — text-block regions** | **No** | Region annotation at text-block level needs no field identity. |
| **OCR quality evaluation** | **No** | FR-OCR-001, FR-OCR-008 — character/word accuracy, multi-page handling. |
| **Classification evaluation** | **No** | FR-OCR-002, FR-OCR-003, AR-AST-002 — including the mandatory "unrecognised" outcome and AC-US-003-3. |
| **Failure-behaviour evaluation** | **Partly** | FR-OCR-009's *retain the original* and *state the reason* halves are evaluable now (EC-001, AC-US-003-5). The *manual-entry path* half is not (**G-27**). |
| **Engine eligibility screening** | **No** | §6's Selection Principle — a candidate must produce a confidence, be able to return "unknown", and be explainable. All testable without field sets. |
| **Document-level confidence behaviour** | **Partly** | FR-OCR-003's classification confidence is measurable; its calibration is still hampered by **G-06**, not by G-12. |

### 9.3 What cannot proceed without G-12

| Stage | Basis |
| --- | --- |
| Ground truth **L4 — field values** | There is no field to record a value for. D-02 §7 records this. |
| Ground truth **L5 — field regions** | Same. |
| **Field-extraction evaluation** (D-02 §11 in its entirety) | FR-OCR-004 has no measurable target |
| **Per-field confidence calibration** (D-02 §12) | Requires field-level correctness labels |
| **BR-001 / BR-002 threshold selection** | AR-AST-008 requires evaluation *before any threshold is set*; the evaluation that would set it is the blocked one |
| **§7.1 per-type inclusion decision** | The demotion criterion is "extraction cannot meet the review threshold" — both terms unavailable |
| **Conflict-detection evaluation** (FR-INF-004, US-005) | Requires attribute identity — **G-13** |
| **AC-US-004-4 as an executable test** | "an extracted value below the review threshold" presupposes both |

### 9.4 The honest statement of blockage

**The OCR evaluation as a whole is NOT blocked by G-12.** Roughly the first half of the D-02 pipeline — text extraction, classification, failure behaviour, engine eligibility — is evaluable as soon as the corpus exists, and D-02 §19 already splits the exit criteria into two stages on exactly this line. Claiming otherwise would idle corpus work behind a product-definition task for no reason.

**What G-12 blocks is the half that produces the numbers the product depends on**: per-field quality, calibration, the BR-001 threshold, and the §7.1 type-inclusion decision. The specification treats S-6 as a single study; running it in two stages is a **PROPOSED DECISION** already recorded in D-02 §19, not a requirement.

---

## 10. Potential Product Decisions

Everything in §10 and §11 is a proposal. Nothing here is a requirement, and `backend/step3.pdf` is not amended by this document.

### 10.1 Required Decisions

These must be made before field-extraction evaluation can begin. They are listed as *decisions*, not as answers.

| # | Decision required | Why it must be made | Owner | Blocks |
| --- | --- | --- | --- | --- |
| **R1** | **Whether the per-type field sets are authored as a product artefact at all**, versus FR-OCR-004 being amended or descoped | FR-OCR-004 is MVP/MUST and unimplementable as written | Product Management | Everything below |
| **R2** | **Which document types are in scope for field authoring**, given that §7.1 is provisional (ASM-001) and three entries are unusable as written (G-09, G-10, G-11) | Authoring fields for a type that will be demoted or renamed is wasted, and inventing types is prohibited | Product Management | R4 |
| **R3** | **Whether photograph and signature are extraction types at all** (G-11) | Determines whether FR-OCR-004 applies to them; the register's D-04.6 recommends *classified but non-extracting*, and notes that is not what the specification says | Product Management | R4 for two types |
| **R4** | **The field set for each in-scope type**: for each field, which type it belongs to, whether it is mandatory or optional, its data type and format, its normalisation rule, and the canonical attribute it maps to — **or explicitly none** | This is G-12's substance | Product Management (content) · Engineering (format) | Field-extraction evaluation |
| **R5** | **Missing-field semantics**: the state of a field a document of its type does not contain — absent, not-applicable, extraction-failed — and whether that state differs from below-threshold (FR-OCR-006) | Question **G** is unanswered; ground-truth annotation cannot label an absence without it | Product Management | Ground truth L4 |
| **R6** | **Multi-value representation**: whether a field may hold several values, and how (question **F**) | Per-subject marks on a marksheet are the obvious case; the choice changes the data model and the evaluation metric | Product Management · Architecture | R4, D-08 |
| **R7** | **Whether the field set is authored before or after the OCR/classification stage of D-02** | Determines whether S-6 runs in one stage or two | Product Management | D-02 sequencing |
| **R8** | **Whether the field definitions are versioned, and whether an evaluation run records the version it ran against** | Without it, an evaluation result cannot be attributed to a definition; related to **G-03** | Engineering · Product Management | Evaluation reproducibility |

### 10.2 Decisions That Belong to G-13 — NOT resolved here

**G-13 is the canonical attribute vocabulary: what DOCURA knows about a person, independent of any one document.** G-12 asks "what fields exist for each document type?". G-13 asks "what standardised names and semantics represent those fields across types?". They are separate artefacts, and this document deliberately produces neither.

The following are **G-13's** and are explicitly **left open here**:

| # | Belongs to G-13 | Requirement that needs it |
| --- | --- | --- |
| V1 | The enumeration of canonical attributes | FR-ACC-004 ("canonical personal attributes") |
| V2 | Each attribute's canonical identifier and user-facing name | FR-ACC-004, NFR-USE-005 |
| V3 | Each attribute's meaning — the identity relation that makes "the same attribute" decidable across two documents | **FR-INF-004** — the hard dependency |
| V4 | Each attribute's value type and normalisation rule | FR-INF-008, AR-DET-003 |
| V5 | Each attribute's sensitivity tier and the rules that assign it | FR-INF-007, AR-DET-005, NFR-MNT-004 — additionally **G-14**, **G-15** |
| V6 | The relationship between FR-ACC-004's "profile" and FR-INF-001's "structured record" | **G-19** |
| V7 | What constitutes a duplicate attribute entry | **G-20**, NFR-REL-005 |

**Note on ordering.** G-13 is *upstream* of G-12: R4 asks each field to map to "one canonical attribute or explicitly none", and that mapping cannot be authored before the vocabulary exists. This document therefore identifies the dependency without discharging it. **Recommending that G-13 be authored first is not the same as resolving it, and no attribute is named anywhere in this document.**

### 10.3 Decisions That Must Remain TBD

These cannot be settled now, by anyone, and naming them prevents them from being quietly assumed:

| # | Must remain TBD | Why | What would settle it |
| --- | --- | --- | --- |
| T1 | **The final MVP document type set** | §7.1 makes inclusion the output of study S-6; ASM-001 registers the whole set as untested | S-6 extraction evaluation on a real corpus |
| T2 | **Which types are demoted to store-and-search only** | §7.1's demotion rule is evidence-driven by construction | Per-type extraction results (D-02 §17.2) |
| T3 | **The BR-001 automatic-action threshold and the BR-002 review threshold** | Explicitly TBD in the specification (BR-001); **G-04** records that BR-002 carries no marker at all | The evaluation AR-AST-008 requires |
| T4 | **Whether thresholds are global or per document type** | **G-07** — never addressed | Product decision informed by per-type results |
| T5 | **The confidence scale and its semantics** | **G-06** — no scale, bounds, or comparability defined | Architecture + product decision; makes BR-001 testable |
| T6 | **Per-field accuracy targets** | The specification sets none, for any field or type | Would follow from T3 and the evaluation |
| T7 | **Whether extraction quality justifies FR-OCR-004 at all** | §12.3: if **A-7** fails, "extraction is unreliable on real scans; thresholds may exclude most automatic action", affecting FR-OCR-004…006 and BR-001 | Study A-7 / S-6 |
| T8 | **Final derived-artefact redaction scope for the evaluation corpus** | G-02 §8.3/§8.6 — interim rule approved, scope revisited at G-12 closure | G-12 closure, then the G-02 revisit |

### 10.4 Potential Product Decision — Not Currently Required

**This subsection exists to hold ideas that are logically appealing and are NOT requirements. Nothing here is proposed for adoption, and nothing here is a field.**

The brief's example — that a passport "should" have name, passport number, DOB, nationality — is exactly the reasoning this document refuses. Note that *passport is not even in the §7.1 type set*, which is a demonstration of how quickly common-sense field reasoning imports scope that the specification never granted.

Observations that a future authoring exercise may find useful, none of which is a requirement and none of which names a field:

1. **A pain implies a field without defining one.** P-06 "Detail mismatch" and §12.2's "Name mismatches (P-06) are a silent disqualifier" mean conflict detection will, in practice, need *some* attribute over which a mismatch is detected. The specification never names it. **Inferring one from a pain would be inventing a requirement.**
2. **The normalisation categories hint at value types.** FR-INF-008's "dates… numeric precision" implies at least one date-shaped and one number-shaped value will exist. This constrains the *type system* R4 must supply; it does not name a field.
3. **Document 02 Table 13.1 is the tempting shortcut.** It is a *sensitivity* classification for research purposes, ASM-tagged and bound to untested A-5, and it is not reproduced in `step3.pdf`. **Using it as a field list would promote an untested research assumption into a product requirement, and G-14 already records that even its sensitivity content is not binding.** It should be an input to G-13's sensitivity work, never to G-12's field list.
4. **Data minimisation cuts against generosity.** BR-017 and NFR-PRIV-001 mean the correct authoring instinct is the smallest field set that serves a function the user asked for — not the largest set the document happens to contain. A field that no form-filling path consumes is collected personal data with no justifying function.
5. **§7.1's demotion rule already handles the doubtful types.** Where it is unclear whether a type extracts usefully (resume being the clearest case — user-authored, free-form, unbounded layout), the specification already provides store-and-search-only as the outcome. That is a mechanism to *use*, not a decision to pre-empt.

---

## 11. Recommended G-12 Resolution

### 11.1 What the recommendation deliberately is

The minimum decision that unblocks field-extraction evaluation is **not** a field list produced here. It is a decision about **who authors the field sets, in what order, in what shape, and under what constraints** — plus the two type-level questions that must be settled before any field for those types can be written.

Each proposal below is labelled and requires approval.

---

**G-12.1 — PROPOSED DECISION — REQUIRES APPROVAL**
**The per-type field sets shall be authored as a reviewed product artefact owned by Product Management, held as configuration, and versioned.**
*Basis:* NFR-MNT-001 requires field sets to be configuration; NFR-MNT-004 requires related classification rules to be "a reviewable list, not scattered through the implementation". *Scope:* Product Management owns the content; Engineering owns the format and the loading mechanism. *Not a requirement today:* `step3.pdf` says field sets exist and are configuration; it does not say who authors them.

**G-12.2 — PROPOSED DECISION — REQUIRES APPROVAL**
**No field shall be created by engineering, inferred from an OCR engine's output, or derived from what an extraction library happens to return.**
*Basis:* §6's Selection Principle — "any component may be replaced provided its replacement meets the same guarantees". Deriving the schema from an engine inverts that and turns engine replacement into a data migration. *Consequence:* the field set is an input to engine selection, never an output of it.

**G-12.3 — PROPOSED DECISION — REQUIRES APPROVAL**
**Authoring order: G-13 (the canonical attribute vocabulary) first, then G-12 (the per-type field sets), with each field mapping to exactly one canonical attribute or explicitly to none.**
*Basis:* FR-INF-001 requires the record to be "assembled from all processed documents" and FR-INF-004 requires detecting disagreement about "the same attribute" — both require attribute identity to exist before per-type fields can be related to each other. *Note:* this decision fixes the **order**; it does not author the vocabulary, and this document names no attribute.

**G-12.4 — PROPOSED DECISION — REQUIRES APPROVAL**
**Each field definition shall carry, at minimum, this shape** — the *shape*, not the content:

| Property | Why it is required | Source |
| --- | --- | --- |
| Owning document type | FR-OCR-004 is per-type | FR-OCR-004 |
| Field identifier (stable, never reused) | Consistency with §0.1's identifier discipline | §0.1 |
| User-facing name | Product language must name things as users do | NFR-USE-005 |
| Mandatory or optional for that type | Answers question **C**; ground truth cannot be annotated without it | Gap — question C |
| Data type and format | Answers question **D** | Gap — question D |
| Normalisation rule reference | FR-INF-008 requires deterministic normalisation | FR-INF-008, AR-DET-003 |
| Canonical attribute mapping, **or explicitly none** | FR-INF-001, FR-INF-004 | G-13 dependency |
| Multiplicity — single or repeating | Answers question **F** | Gap — question F |
| Missing-value semantics | Answers question **G** | Gap — question G |

*Sensitivity tier is deliberately absent from this list:* FR-INF-007 attaches it to the **attribute**, which places it in G-13 and in G-14/G-15. A field's tier follows from the attribute it maps to.

**G-12.5 — PROPOSED DECISION — REQUIRES APPROVAL**
**Three type-level questions shall be settled before any field is authored for the types they affect, and none of them shall be settled by engineering:** address proof's membership (**G-09**), the semester result / semester marksheet / marksheet identity (**G-10**), and whether photograph and signature extract at all (**G-11**).
*Basis:* a field set cannot be authored for a type whose boundary is undefined. G-10 additionally changes the meaning of AC-US-003-1 as a test.

**G-12.6 — PROPOSED DECISION — REQUIRES APPROVAL**
**Field sets shall be authored and approved per document type, and stage-2 evaluation may begin per type as each type's set closes** — rather than gating all evaluation on the complete set for all types.
*Basis:* §7.1 already treats inclusion as a per-type decision, and its demotion rule operates per type. *Effect:* the long pole shortens without widening scope. *Constraint:* this does not select which types go first — that is **R2**, and it is Product Management's.

**G-12.7 — PROPOSED DECISION — REQUIRES APPROVAL**
**Until G-12 closes, FR-OCR-004, FR-OCR-005, FR-OCR-006, FR-INF-001, FR-INF-004, FR-INF-005, FR-INF-006, FR-INF-007 and FR-INF-008 remain BLOCKED — REQUIREMENTS GAP, and no placeholder, illustrative, or "temporary" field set shall be introduced into code, configuration, schema, or test fixtures.**
*Basis:* BR-009 (no guessing, no placeholder values) is the product's own instinct applied to its own construction; §11's Containment Rule forbids scope entering informally; a placeholder schema in a fixture is the most common way an invented requirement becomes a real one. *Explicit consequence:* Sprint 4's field-extraction work does not start on a provisional schema.

**G-12.8 — PROPOSED DECISION — REQUIRES APPROVAL**
**The approved field-definition artefact shall be versioned, and every evaluation run shall record the version it was evaluated against.**
*Basis:* AR-AST-008 requires evaluation before any threshold is set; a threshold justified by an evaluation against a superseded field set is not evidence. Related to **G-03** (no re-evaluation trigger on component change).

**G-12.9 — PROPOSED DECISION — REQUIRES APPROVAL**
**The field set shall be authored to the minimum that serves a function the user asked for, and each field shall be justifiable against a requirement that consumes it.**
*Basis:* BR-017 (data minimisation) and NFR-PRIV-001 (collect only what a requested function needs). *Effect:* the burden of proof sits on including a field, not on excluding it — which is the correct default for a product that holds identity documents.

**G-12.10 — PROPOSED DECISION — REQUIRES APPROVAL**
**Closing G-12 by approval of this document is not an amendment to `backend/step3.pdf`.** As with G-02, the gap in the specification remains open until §11's Containment Rule is followed and the specification is amended with a new version number.

### 11.2 What this recommendation does not do

- It **names no field**, for any type, anywhere.
- It **does not resolve G-13** — it fixes only the order in which G-13 and G-12 are authored.
- It **does not select the MVP type set** — that is §7.1's and S-6's (T1, T2).
- It **does not set any threshold** — that is T3–T5 and the evaluation.
- It **does not answer G-09, G-10 or G-11** — it requires that Product Management answer them first.
- It **touches no production code, schema, migration, or dependency.**

---

## 12. Approval Required

| # | Decision | Approver | Cannot be delegated to engineering because |
| --- | --- | --- | --- |
| G-12.1 | Field sets are a PM-owned, versioned configuration artefact | Product Management | Determines what DOCURA reads from a person's identity documents |
| G-12.2 | No engineering-invented or engine-derived fields | Product Management · Architecture | Protects §6's Selection Principle |
| G-12.3 | G-13 first, then G-12; every field maps to an attribute or explicitly none | Product Management | Fixes the dependency order for two product artefacts |
| G-12.4 | The minimum shape of a field definition | Product Management (content properties) · Engineering (format) | Four of the nine properties are gaps in the requirements (C, D, F, G) |
| G-12.5 | G-09, G-10, G-11 settled before their types' fields are authored | Product Management | Type boundaries and an acceptance criterion's meaning |
| G-12.6 | Per-type authoring; per-type stage-2 evaluation entry | Product Management | Sequencing decision with schedule consequences |
| G-12.7 | No placeholder field set anywhere until G-12 closes | Product Management · Engineering | Prevents an invention becoming a de-facto requirement |
| G-12.8 | Field definitions versioned; evaluation records the version | Engineering · Product Management | Determines whether an evaluation result is evidence |
| G-12.9 | Minimum justifiable field set (data minimisation) | Product Management · Privacy | BR-017 / NFR-PRIV-001 privacy decision |
| G-12.10 | Approval here is not an amendment to `step3.pdf` | Product Management | §11 Containment Rule |

**Also requiring approval, and not proposed here:** R2 (which types are in scope for authoring), R3 (G-11's answer), R4 (the field sets themselves), R5 (missing-field semantics), R6 (multi-value representation), R7 (one-stage or two-stage S-6).

---

## 13. G-12 Exit Criteria

G-12 is closed when **all** of the following hold. Criteria are ordered by dependency.

| # | Exit criterion | Depends on | Status today |
| --- | --- | --- | --- |
| **X1** | G-12.1…G-12.10 approved, or explicitly rejected with an alternative recorded | This document | **Not met — awaiting approval** |
| **X2** | **G-09** answered: what documents qualify as address proof | Product Management | **Not met** |
| **X3** | **G-10** answered: the semester result / semester marksheet / marksheet identity, and the user-facing name (NFR-USE-005) | Product Management | **Not met** |
| **X4** | **G-11** answered: whether photograph and signature are extraction types | Product Management | **Not met** |
| **X5** | **G-13** closed: the canonical attribute vocabulary authored and approved | Product Management | **Not met — separate gap** |
| **X6** | For each in-scope document type, a field set authored to the G-12.4 shape, each field mapping to one canonical attribute or explicitly to none | X1–X5 | **Not met** |
| **X7** | Mandatory vs optional stated for every field (question **C**) | X6 | **Not met** |
| **X8** | Data type and format stated for every field (question **D**) | X6 | **Not met** |
| **X9** | Normalisation rule referenced for every field, and the rule itself stated (question **E**) | X5, X6 | **Not met** |
| **X10** | Multi-value representation decided (question **F**) | X6 | **Not met** |
| **X11** | Missing-field semantics decided, and distinguished from below-threshold (question **G**) | X6 | **Not met** |
| **X12** | The artefact is held as configuration (NFR-MNT-001) and versioned (G-12.8) | X6 | **Not met** |
| **X13** | Each field justified against a requirement that consumes it (G-12.9, BR-017) | X6 | **Not met** |
| **X14** | D-02 ground-truth layers **L4** (field values) and **L5** (field regions) become annotatable | X6 | **Not met** |
| **X15** | G-02's derived-artefact redaction scope revisited now that "what is needed" is determinable (G-02 §8.6, T8) | X6 | **Not met** |
| **X16** | `step3.pdf` amended under §11's Containment Rule, or the divergence formally accepted and recorded | X1–X13 | **Not met** |

**Note on what closure does and does not unblock.** X1–X14 unblock the *design and annotation* of field-extraction evaluation. They do not by themselves unblock the BR-001 threshold, which additionally requires **G-04**, **G-05**, **G-06**, **G-07** and the evaluation itself; nor the §7.1 type-inclusion decision, which requires per-type results; nor the build of FR-OCR-004…006, which §12.3 additionally gates on assumption **A-7**.

---

### G-12 Decision Summary

| ID | Decision | Status | Source / Reason | Approval Required |
| --- | --- | --- | --- | --- |
| **G-12.a** | Extraction must follow a defined field set per supported type | **REQUIREMENT** | FR-OCR-004 (MVP, MUST) | No — already binding |
| **G-12.b** | Field sets are held as configuration, not code | **REQUIREMENT** | NFR-MNT-001 (MVP, MUST) | No — already binding |
| **G-12.c** | Every extracted field carries its own confidence, independent of the document-level value | **REQUIREMENT** | FR-OCR-005 (MVP, MUST) | No — already binding |
| **G-12.d** | Every attribute value references its source document and the confidence it was read with | **REQUIREMENT** | FR-INF-002 (MVP, MUST); BR-010 | No — already binding |
| **G-12.e** | Below-review-threshold fields are marked for review and never automatically used | **REQUIREMENT** | FR-OCR-006, BR-002 | No — already binding |
| **G-12.f** | Every attribute carries one of routine / sensitive / consequential | **REQUIREMENT** | FR-INF-007, FR-SENS-001 | No — already binding |
| **G-12.g** | "Other" documents are stored and searchable with **no** structured extraction | **REQUIREMENT** | §7.1 | No — already binding |
| **G-12.h** | Processing status has an enumerated domain: queued / processing / ready / needs review / failed | **REQUIREMENT** | FR-UPL-005, FR-DOC-001 | No — already binding |
| **G-12.i** | **No field definition exists for any of the twelve extracting document types** | **REQUIREMENTS GAP (G-12)** | Complete search of `step3.pdf`; FR-OCR-004 carries no TBD marker | Closure requires PM |
| **G-12.j** | Mandatory vs optional, data types, normalisation rules, multi-value representation, and missing-field behaviour are all undefined | **REQUIREMENTS GAP (G-12)** | Questions C, D, E, F, G — §7.1 | Closure requires PM |
| **G-12.k** | The canonical attribute vocabulary does not exist | **REQUIREMENTS GAP (G-13)** — *not resolved here* | FR-ACC-004 names it; no section enumerates it | Separate G-13 resolution |
| **G-12.l** | Address proof is a category, not a type | **REQUIREMENTS GAP (G-09)** | §7.1 | Yes — PM, before its fields |
| **G-12.m** | "Semester result" vs "semester marksheet" vs "marksheet" is unresolved | **REQUIREMENTS GAP (G-10)** | §7.1 vs AC-US-003-1 vs NFR-USE-005 | Yes — PM, before its fields |
| **G-12.n** | Whether photograph and signature extract at all is unstated | **REQUIREMENTS GAP (G-11)** | §7.1, FR-OCR-004, FR-INF-007 | Yes — PM, before their fields |
| **G-12.o** | The final MVP document type set | **TBD** | §7.1 subjects inclusion to S-6; ASM-001 | Settled by evaluation, not approval |
| **G-12.p** | Which types are demoted to store-and-search only | **TBD** | §7.1 demotion rule | Settled by evaluation |
| **G-12.q** | BR-001 / BR-002 threshold values, their relationship, the confidence scale, global vs per-type | **TBD** | G-04, G-05, G-06, G-07 | Settled by evaluation, then PM |
| **G-12.r** | Whether extraction quality justifies FR-OCR-004 at all | **TBD** | §12.3, assumption A-7 | Settled by study |
| **G-12.s** | Field sets authored as a PM-owned, versioned configuration artefact | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.1; NFR-MNT-001, NFR-MNT-004 | **Yes — PM** |
| **G-12.t** | No engineering-invented or engine-derived fields | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.2; §6 Selection Principle | **Yes — PM · Architecture** |
| **G-12.u** | Authoring order: G-13 first, then G-12; each field maps to one attribute or explicitly none | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.3; FR-INF-001, FR-INF-004 | **Yes — PM** |
| **G-12.v** | The minimum shape of a field definition (nine properties) | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.4 | **Yes — PM (content) · Engineering (format)** |
| **G-12.w** | G-09, G-10, G-11 settled before authoring fields for the affected types | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.5 | **Yes — PM** |
| **G-12.x** | Per-type authoring; stage-2 evaluation may enter per type | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.6; §7.1 per-type demotion | **Yes — PM** |
| **G-12.y** | No placeholder field set in code, configuration, schema, or fixtures until G-12 closes | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.7; BR-009, §11 Containment Rule | **Yes — PM · Engineering** |
| **G-12.z** | Field definitions versioned; every evaluation run records the version | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.8; AR-AST-008, G-03 | **Yes — Engineering · PM** |
| **G-12.aa** | Minimum justifiable field set; each field justified by a requirement that consumes it | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.9; BR-017, NFR-PRIV-001 | **Yes — PM · Privacy** |
| **G-12.ab** | Approval here does not amend `step3.pdf` | **PROPOSED DECISION — REQUIRES APPROVAL** | G-12.10; §11 Containment Rule | **Yes — PM** |
| **G-12.ac** | OCR quality, classification, failure behaviour and engine eligibility are **not** blocked by G-12 and may be evaluated once the corpus exists | **PROPOSED DECISION — REQUIRES APPROVAL** | §9.2; consistent with D-02 §3.2 and §19's two-stage split | **Yes — PM** |

---

# PART II — FIELD DEFINITION AUTHORING

*Added 5 September 2026, after G-13's approval. §1–§13 above are unchanged and remain the requirements analysis: they establish that `backend/step3.pdf` defines **zero** information fields for **zero** document types. Nothing below changes that finding. Everything below is new and proposed.*

---

## 14. Proposed Per-Document Field Definitions

### 14.0 Authoring method, and the tests each proposal had to pass

**Nothing in §14–§21 is a requirement.** Every attribute is a **PROPOSED DECISION — REQUIRES APPROVAL**. `backend/step3.pdf` names no information field, so every field here is new product scope.

**The four tests applied to every candidate attribute.** A candidate had to pass all four to appear.

| Test | Basis | Effect |
| --- | --- | --- |
| **1. Named consumer** | **G-13.12** (approved): each attribute justifiable against a requirement that consumes it; **BR-017**, **NFR-PRIV-001** | An attribute with no MVP requirement consuming it is retained personal data with no justifying function. Rejected |
| **2. Not FUTURE/WON'T** | §10.3, §11 Containment Rule | If the only requirement that would consume it is FUTURE, the attribute is FUTURE. Rejected |
| **3. Semantic distinctness** | Step 4 of this authoring task; **G-13.3** (approved) | Two concepts are merged only where the meaning is the same, never because labels look alike |
| **4. Definable now** | Step 13 | If it cannot be defined without inventing behaviour, it is recorded as a gap rather than guessed |

**Result: 10 attributes.** Six of the thirteen §7.1 entries receive **no** proposed field at all — five because of unresolved decisions or a failed test, one because the specification already defines its extraction as empty.

### 14.0.1 The canonical normalisation rules referenced below

Proposed under **FR-INF-008**'s four categories ("dates, casing, spacing, and numeric precision") and **AR-DET-003** (deterministic and reversible). Reversibility is satisfied by **G-13.6** (approved): the raw as-printed value is retained alongside the normalised form and is what is shown to the user (**NFR-USE-005**, **FR-OCR-007**). Per **G-13.5** (approved), the normalised form is also the comparison function for **FR-INF-004**, so each rule below is simultaneously a conflict-detection decision.

| Rule | Source representation → canonical representation | Category | Status |
| --- | --- | --- | --- |
| **N1 — whitespace** | Runs of whitespace collapsed to a single space; leading and trailing whitespace removed | FR-INF-008 "spacing" / AR-DET-003 "whitespace" | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **N2 — casing** | Folded to upper case in the canonical form. The as-printed value is retained (G-13.6) and is what the user sees | FR-INF-008 "casing" | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **N3 — date** | Any printed date form → **ISO 8601 calendar date, `YYYY-MM-DD`** | FR-INF-008 "dates" | **PROPOSED DECISION — REQUIRES APPROVAL.** Day/month order in the *source* is not always determinable — **CANDIDATE GAP**, §18.2 |
| **N4 — integer** | Digits only; separators and leading zeros removed; no fractional part | FR-INF-008 "numeric precision" | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **N5 — identifier compaction** | All whitespace and printed grouping separators removed, then N2 | FR-INF-008 "spacing" + "casing" | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **N0 — none** | The value is stored exactly as read | — | Used only where a rule cannot yet be defined; recorded as such |

> **ILLUSTRATIVE EXAMPLE — NOT A REQUIREMENT.** N5 in pattern notation only: a grouped identifier printed as `NNNN NNNN NNNN` normalises to `NNNNNNNNNNNN`; an alphanumeric identifier printed as `AAAAA9999A` is already compact and only N2 applies. No specimen identifier value appears anywhere in this document.

### 14.0.2 A finding that constrains every education attribute

**Education attributes are qualification-scoped, not person-scoped.** A person legitimately has a year of passing for a 10th marksheet, another for a 12th marksheet, and another for a degree certificate. These are **not** disagreements — but under **FR-INF-004** as written, and under **G-13.3**'s approved identity rule, three documents giving three different values for one canonical attribute is exactly the definition of a conflict.

The approved **G-13** seven-property shape has **no property that scopes an attribute to a qualification, a document, or any other grouping**. This is not resolvable inside G-12 and must not be patched by inventing per-type attribute names (which would violate the reuse discipline in Step 4) or by making the attributes multi-valued (which would misrepresent three distinct qualifications as one repeating value).

**Recorded as CANDIDATE GAP — ID TO BE ASSIGNED (§18.1).** Its consequence is carried through every table below: education attributes are marked **NOT EVALUATION-READY** and their multiplicity is **TBD**.

---

### 14.1 Document Type: **Aadhaar**

*Exact §7.1 name, "Identity and address" group. Type identity is not in dispute.*

| Canonical Identifier | Display Label | Semantic Definition | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | The person's name as given on an identity or education document | string | N1 + N2 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `person.date_of_birth` | Date of birth | The person's date of birth | date | N3 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `person.postal_address` | Address | The person's residential postal address as printed on a document that evidences it | **TBD — structured object, component set undecided** | **N0 — cannot be defined before the component set is** | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Optional** for this type | **PROPOSED — NOT EVALUATION-READY** (§18.3) |
| `person.aadhaar_number` | Aadhaar number | The person's Aadhaar identifier as issued under that scheme | string | N5 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — BLOCKED ON THE UNRESOLVED STORAGE DECISION** (D-02 §11.7, D-05.3): whether the number is stored at all, masked, or stored in part is unsettled and safety-relevant |

**Consumer justification.** `person.full_name` and `person.date_of_birth` are consumed by **FR-FILL-001** (filling routine text and date fields) and **FR-INF-004** (§12.2 records name mismatches, P-06, as "a silent disqualifier"). `person.aadhaar_number` is the document's entire product purpose: without it the type has nothing a form consumes. `person.postal_address` is consumed by FR-FILL-001 where a form asks for an address.

---

### 14.2 Document Type: **PAN**

| Canonical Identifier | Display Label | Semantic Definition | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | *(as §15)* | string | N1 + N2 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `person.date_of_birth` | Date of birth | *(as §15)* | date | N3 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `person.pan_number` | PAN | The person's Permanent Account Number as issued under that scheme | string | N5 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — BLOCKED ON THE UNRESOLVED STORAGE DECISION** (D-02 §11.7, D-05.3) |

**Note on non-merger.** `person.aadhaar_number` and `person.pan_number` are **not** merged into one "government identifier" attribute. They are different identifiers under different schemes with different formats and different disclosure consequences; merging them would fail test 3 and would make **FR-INF-004** compare two values that were never meant to agree. See §16.2.

---

### 14.3 Document Type: **address proof**

> **DEPENDENT ON G-09 — NOT RESOLVED HERE.** §7.1 lists "address proof" in the "Identity and address" group. §3.2 of this document establishes it is a **category**, not a document type, and that its members are never enumerated. **A field set cannot be closed for a type whose membership is undefined.** The proposal below is conditional and must not be treated as closed.

| Canonical Identifier | Display Label | Semantic Definition | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | *(as §15)* | string | N1 + N2 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — DEPENDENT ON G-09** |
| `person.postal_address` | Address | *(as §15)* | **TBD — structured object** | **N0** | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — DEPENDENT ON G-09 AND NOT EVALUATION-READY** (§18.3) |

**Consumer justification.** The address is the category's defining content; a member document that does not evidence an address is not an address proof. **No other attribute is proposed**, because the category's membership determines what else is present and that membership is G-09's to settle.

---

### 14.4 Document Type: **10th marksheet**

| Canonical Identifier | Display Label | Semantic Definition | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | *(as §15)* | string | N1 + N2 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `education.awarding_body` | Board or university | The authority that awarded the qualification the document evidences | string | N1 + N2 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — NOT EVALUATION-READY** (§18.1) |
| `education.year_of_passing` | Year of passing | The calendar year in which the qualification was awarded | number | N4 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — NOT EVALUATION-READY** (§18.1, §18.4) |
| `education.aggregate_result` | Result | The overall result of the qualification, as printed on the document | string | N1 + N2 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | **Required** for this type | **PROPOSED — NOT EVALUATION-READY** (§18.1, §18.5) |
| `education.roll_number` | Roll number | The number identifying the candidate for the examination the document reports | string | N5 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | **Optional** for this type | **PROPOSED — NOT EVALUATION-READY** (§18.1) |
| `person.date_of_birth` | Date of birth | *(as §15)* | date | N3 | single | **TBD — REQUIRES SENSITIVITY DECISION** | **Optional** for this type | **PROPOSED DECISION — REQUIRES APPROVAL** |

**Consumer justification.** All five education-block values are consumed by **FR-FILL-001** — an application form's education section asks for board, year, and result, and asks for the roll number where it verifies the marksheet. `person.date_of_birth` is marked **Optional** here rather than Required because whether a given board prints it is a property of real documents, not of the specification — see §18.6.

**Deliberately not proposed: per-subject marks.** A marksheet lists a mark per subject. No MVP requirement consumes them; a form's education block asks for the aggregate. Proposing them would create the repeating group that G-12 §7.1 question **F** records as undefined, for no consumer. Excluded under tests 1 and 4.

---

### 14.5 Document Type: **12th marksheet**

**Identical to §14.4 in every respect** — same five attributes, same types, same normalisation, same required/optional split, same status. The two types are distinguished by classification (**FR-OCR-002**), not by their field sets.

| Canonical Identifier | Display Label | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | string | N1 + N2 | single | **TBD** | **Required** | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `education.awarding_body` | Board or university | string | N1 + N2 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** |
| `education.year_of_passing` | Year of passing | number | N4 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** |
| `education.aggregate_result` | Result | string | N1 + N2 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** |
| `education.roll_number` | Roll number | string | N5 | **TBD** | **TBD** | Optional | **PROPOSED — NOT EVALUATION-READY** |
| `person.date_of_birth` | Date of birth | date | N3 | single | **TBD** | Optional | **PROPOSED DECISION — REQUIRES APPROVAL** |

**No new canonical attribute is introduced by this type.** That is the intended outcome of the reuse discipline (§16).

---

### 14.6 Document Type: **semester result**

> **DEPENDENT ON G-10 — NOT RESOLVED HERE.** §7.1 says "semester result"; **AC-US-003-1** says "semester marksheet… classified as a **marksheet**"; **NFR-USE-005** offers "marksheet" as user-facing language. Whether these name one type, two types, or a family is unresolved. **The field set below is authored against §7.1's name only.** If G-10 resolves the names differently, the *type* changes and this table must be re-pointed; the *attributes* would not change, because they are canonical and type-independent.

| Canonical Identifier | Display Label | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | string | N1 + N2 | single | **TBD** | **Required** | **PROPOSED — DEPENDENT ON G-10** |
| `education.awarding_body` | Board or university | string | N1 + N2 | **TBD** | **TBD** | **Required** | **PROPOSED — DEPENDENT ON G-10; NOT EVALUATION-READY** |
| `education.year_of_passing` | Year of passing | number | N4 | **TBD** | **TBD** | Optional | **PROPOSED — DEPENDENT ON G-10; NOT EVALUATION-READY** |
| `education.aggregate_result` | Result | string | N1 + N2 | **TBD** | **TBD** | **Required** | **PROPOSED — DEPENDENT ON G-10; NOT EVALUATION-READY** |
| `education.roll_number` | Roll number | string | N5 | **TBD** | **TBD** | Optional | **PROPOSED — DEPENDENT ON G-10; NOT EVALUATION-READY** |

**Note.** `education.year_of_passing` is **Optional** here and **Required** on §14.4/§14.5, because a single semester's result may report a semester and session rather than a year of award. The distinction between a *semester* and a *year of passing* is a further instance of §14.0.2's scoping gap.

---

### 14.7 Document Type: **degree certificate**

| Canonical Identifier | Display Label | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | string | N1 + N2 | single | **TBD** | **Required** | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `education.qualification_name` | Qualification | string | N1 + N2 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** (§18.1) |
| `education.awarding_body` | Board or university | string | N1 + N2 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** (§18.1) |
| `education.year_of_passing` | Year of passing | number | N4 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** (§18.1, §18.4) |
| `education.aggregate_result` | Result | string | N1 + N2 | **TBD** | **TBD** | Optional | **PROPOSED — NOT EVALUATION-READY** (§18.1, §18.5) |

**`education.qualification_name` is introduced here and only here.** A marksheet reports an examination whose identity is carried by the document type itself ("10th", "12th"); a degree certificate names the qualification awarded, and an application form asks for it. This is the one type-specific concept in the education group that survives test 1.

---

### 14.8 Document Type: **photograph**

> **DEPENDENT ON G-11 — NOT RESOLVED HERE.**

**No attribute is proposed.** §7.1 lists photograph as a supported type and says nothing about whether it has extractable information; **G-11** records that whether this type extracts at all is unstated, and register **D-04.6** recommends *classify-and-attach-only* while noting that is not what the specification says. Authoring a field set for a type that may not be an extraction type would fail test 4 and would pre-empt a Product Management decision.

**Its MVP product purpose is served without any attribute**: **FR-MATCH-001…008** match and attach the document to a file-upload field, using the document *type*, not extracted content.

---

### 14.9 Document Type: **signature**

> **DEPENDENT ON G-11 — NOT RESOLVED HERE.**

**No attribute is proposed.** Identical reasoning to §14.8.

---

### 14.10 Document Type: **student ID**

| Canonical Identifier | Display Label | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | string | N1 + N2 | single | **TBD** | **Required** | **PROPOSED DECISION — REQUIRES APPROVAL** |

**One attribute, deliberately.** A student ID card carries an institution name, an enrolment number, a validity date and a photograph. **None of them passes test 1:**

| Candidate rejected | Why |
| --- | --- |
| Institution name | An application form's education block asks for the *awarding body* of a qualification, which comes from the marksheet or degree certificate. Nothing in the MVP consumes the name on an ID card |
| Enrolment number | Semantically distinct from `education.roll_number` (§16.3) and has no MVP consumer of its own |
| Validity / expiry date | The only requirement that would consume it is **FR-DOC-009** (indicating expired or superseded documents), which is **FUTURE / WON'T** (§10.3). Fails test 2 |
| Photograph on the card | An image, not structured information; document matching operates on the *photograph* document type |

**Consequence, flagged not decided.** A type whose extraction reduces to the person's name is a candidate for §7.1's store-and-search-only outcome. That is register **D-04.4**'s question and **§7.1**'s demotion rule operating on S-6 evidence — **not** a decision this document makes.

---

### 14.11 Document Type: **hall ticket**

| Canonical Identifier | Display Label | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Required/Optional | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | string | N1 + N2 | single | **TBD** | **Required** | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `education.roll_number` | Roll number | string | N5 | **TBD** | **TBD** | **Required** | **PROPOSED — NOT EVALUATION-READY** (§18.1) |

**Two attributes.** The roll number is the hall ticket's identifying content and is the same concept as the roll number printed on the corresponding marksheet — which is precisely the cross-document case **FR-INF-004** exists to check. Rejected: examination name, examination date, and examination centre — the only requirement that would consume a future examination date is **FR-INT-005** (proactive deadline notification), **FUTURE / WON'T**. Fails test 2.

---

### 14.12 Document Type: **resume**

> **DEPENDENT ON REGISTER D-04.7 — NOT RESOLVED HERE.**

**No attribute is proposed.** A resume is user-authored, free-form, and unbounded in layout; register **D-04.7** already questions whether it is an extraction type at all. Authoring a field set for it means authoring a document ontology — exactly what Step 2 of this authoring task forbids — and **G-12 R2** warns that authoring fields for a type that will be demoted is wasted work. §10.4 of this document already identified resume as "the clearest case" for §7.1's store-and-search-only outcome.

---

### 14.13 Document Type: **Other / unclassified**

**No attribute — and this one is not a proposal.**

> **§7.1**: "Other — stored and searchable as an unclassified document, **no structured extraction**."

This is the single document type whose extraction behaviour the specification fully defines, and it defines it as empty. Status: **REQUIREMENT**, unchanged from §5.1.

---

### 14.14 Coverage summary

| # | §7.1 document type | Attributes proposed | Status |
| --- | --- | --- | --- |
| 1 | Aadhaar | 4 | Proposed; 1 blocked on the storage decision |
| 2 | PAN | 3 | Proposed; 1 blocked on the storage decision |
| 3 | address proof | 2 | **Dependent on G-09** |
| 4 | 10th marksheet | 6 | Proposed |
| 5 | 12th marksheet | 6 | Proposed |
| 6 | semester result | 5 | **Dependent on G-10** |
| 7 | degree certificate | 5 | Proposed |
| 8 | photograph | **0** | **Dependent on G-11** |
| 9 | signature | **0** | **Dependent on G-11** |
| 10 | student ID | 1 | Proposed |
| 11 | hall ticket | 2 | Proposed |
| 12 | resume | **0** | **Dependent on D-04.7** |
| 13 | Other / unclassified | **0** | **REQUIREMENT** — §7.1 defines the set as empty |

**13 document types covered. 10 unique canonical attributes. No document type was renamed, merged, added, or removed.**

---

## 15. Canonical Attribute Registry

The consolidated registry. **Each attribute appears exactly once**, however many document types carry it. All seven **G-13**-approved properties are present for every entry; none is added and none is dropped.

| Identifier | Display Label | Semantic Definition | Data Type | Normalisation | Multiplicity | Sensitivity Tier | Applicable Types | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | Full name | The name identifying the person who is the subject of the document, as that document gives it | string | N1 + N2 | single | **TBD — REQUIRES SENSITIVITY DECISION** | Aadhaar · PAN · address proof · 10th marksheet · 12th marksheet · semester result · degree certificate · student ID · hall ticket | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `person.date_of_birth` | Date of birth | The calendar date on which the person was born | date | N3 | single | **TBD — REQUIRES SENSITIVITY DECISION** | Aadhaar · PAN · 10th marksheet · 12th marksheet | **PROPOSED DECISION — REQUIRES APPROVAL** |
| `person.postal_address` | Address | The person's residential postal address as evidenced by the document | **TBD — structured object, component set undecided** | **N0** | single | **TBD — REQUIRES SENSITIVITY DECISION** | Aadhaar · address proof | **PROPOSED — NOT EVALUATION-READY** (§18.3) |
| `person.aadhaar_number` | Aadhaar number | The person's identifier under the Aadhaar scheme | string | N5 | single | **TBD — REQUIRES SENSITIVITY DECISION** | Aadhaar | **PROPOSED — BLOCKED ON THE STORAGE DECISION** (D-02 §11.7, D-05.3) |
| `person.pan_number` | PAN | The person's Permanent Account Number | string | N5 | single | **TBD — REQUIRES SENSITIVITY DECISION** | PAN | **PROPOSED — BLOCKED ON THE STORAGE DECISION** (D-02 §11.7, D-05.3) |
| `education.awarding_body` | Board or university | The authority that awarded the qualification the document evidences | string | N1 + N2 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | 10th marksheet · 12th marksheet · semester result · degree certificate | **PROPOSED — NOT EVALUATION-READY** (§18.1) |
| `education.qualification_name` | Qualification | The name of the qualification awarded, where the document names one | string | N1 + N2 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | degree certificate | **PROPOSED — NOT EVALUATION-READY** (§18.1) |
| `education.year_of_passing` | Year of passing | The calendar year in which the qualification was awarded | number | N4 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | 10th marksheet · 12th marksheet · semester result · degree certificate | **PROPOSED — NOT EVALUATION-READY** (§18.1, §18.4) |
| `education.aggregate_result` | Result | The overall result of the qualification, exactly as the document prints it | string | N1 + N2 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | 10th marksheet · 12th marksheet · semester result · degree certificate | **PROPOSED — NOT EVALUATION-READY** (§18.1, §18.5) |
| `education.roll_number` | Roll number | The number identifying the candidate for a specific examination | string | N5 | **TBD — §14.0.2** | **TBD — REQUIRES SENSITIVITY DECISION** | 10th marksheet · 12th marksheet · semester result · hall ticket | **PROPOSED — NOT EVALUATION-READY** (§18.1) |

**Total: 10 unique canonical attributes.**

### 15.1 Why every sensitivity tier reads TBD

**G-13.9** (approved) requires every attribute to carry a tier and forbids publishing one without it. **No tier can be determined from `backend/step3.pdf`:**

- **FR-INF-007** and **FR-SENS-001** define the three tier names and require every attribute to carry one. They assign none.
- **G-14** records that the classification rules are not in `step3.pdf` at all; the referenced **document 02 Table 13.1** is not reproduced there, is ASM-tagged, and is bound to untested assumption **A-5**. §4.4 of this document already ruled that promoting it into a schema is prohibited.
- **G-15** records that there is no default tier.
- The only tier the specification assigns to anything is **consequential**, to legal declarations and consent controls (**FR-FLD-004**, **BR-006**) — which are **form controls**, not stored attributes.

Assigning a tier here would be exactly the intuition-based classification Step 9 forbids. **The registry cannot be published under G-13.9 until G-14 and G-15 resolve** — recorded in §20 and §21.

### 15.2 Identifier scheme

`<domain>.<concept>`, lower case, underscore-separated, two domains only: `person` and `education`. **No identifier carries a document-type prefix** — `person.full_name`, never `aadhaar.name` — so that the same concept read from nine different types resolves to one identifier, as **G-13.3** requires. The two exceptions, `person.aadhaar_number` and `person.pan_number`, name an **identifier scheme**, not a document: the scheme is the concept, and a PAN read from any document is still a PAN. No identifier encodes a format, an engine, a version, or any other implementation detail.

---

## 16. Attributes Reused Across Document Types

Reuse is the point of the exercise. **13 document types carry 40 field slots between them, drawn from 10 unique attributes.**

### 16.1 Where reuse was applied

| Attribute | Types | Justification for treating these as one concept |
| --- | --- | --- |
| `person.full_name` | 9 | The name of the same person, printed by different issuers. This is the concept **FR-INF-004** exists to check across documents, and §12.2 names it directly: "Name mismatches (P-06) are a silent disqualifier". Creating a per-type name attribute would make the requirement undetectable by construction |
| `person.date_of_birth` | 4 | One person, one date of birth. A disagreement between two documents is a genuine conflict, which is the correct outcome |
| `person.postal_address` | 2 | The address the document evidences. Aadhaar and an address proof evidencing different addresses is a real conflict a user should see |
| `education.awarding_body` | 4 | The authority that awarded the qualification. A board and a university are the same role in different education stages, and a form's education block asks for them in one field. **Subject to §14.0.2** — different qualifications legitimately have different awarding bodies, which is not a conflict |
| `education.year_of_passing` | 4 | Same, and same caveat |
| `education.aggregate_result` | 4 | Same, and same caveat |
| `education.roll_number` | 4 | The candidate's number for one examination. The marksheet-to-hall-ticket case is the clearest genuine cross-document match in the whole set |

### 16.2 Where reuse was refused — identifiers

`person.aadhaar_number` and `person.pan_number` were **not** merged into a single government-identifier attribute. They are issued under different schemes, have different formats, serve different purposes, and carry different disclosure consequences. Merging them would satisfy a superficial label similarity ("identity number") while making **FR-INF-004** compare two values that were never meant to agree — producing a permanent false conflict for every user holding both documents.

### 16.3 Where reuse was refused — education numbers

A **roll number** identifies a candidate *for an examination*. An **enrolment number** identifies a student *at an institution*. A **registration number** identifies a candidate *with a board*. These look alike and are not alike. Only `education.roll_number` has an MVP consumer, so only it is proposed; the other two are recorded in §17.2 as excluded rather than folded into it. Forcing them together is precisely the error Step 4 warns against.

### 16.4 Where reuse was refused — awarding body vs institution attended

A candidate `education.institution_name` — the school or college attended, as distinct from the awarding board or university — was considered and **rejected under test 1**. No MVP requirement distinguishes the attended institution from the awarding body, and an application form's education block asks for the awarding body. **NFR-MNT-001** makes adding a field later a configuration change, not re-engineering, so the cheaper error is to omit it now.

---

## 17. Proposed Decisions

Every item is new product scope. **`backend/step3.pdf` defines none of them.**

### 17.1 The decisions

| ID | Proposed decision | Status |
| --- | --- | --- |
| **G-12.P1** | The canonical attribute registry of §15 — **10 attributes** — is adopted as the initial vocabulary content, authored to the G-13-approved seven-property shape | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P2** | `person.full_name` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P3** | `person.date_of_birth` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P4** | `person.postal_address` exists; **its data type and component set are TBD** | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P5** | `person.aadhaar_number` exists — **subject to the unresolved decision on whether the number is stored at all, masked, or in part** | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P6** | `person.pan_number` exists — same qualification | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P7** | `education.awarding_body` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P8** | `education.qualification_name` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P9** | `education.year_of_passing` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P10** | `education.aggregate_result` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P11** | `education.roll_number` exists, as defined in §15 | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P12** | The per-type field sets of §14.1–§14.13, including the **required/optional** marking of each field **for its type** | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P13** | Normalisation rules **N1–N5**, each stated as source representation → canonical representation (§14.0.1) | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P14** | The identifier scheme `<domain>.<concept>` with two domains, no document-type prefixes (§15.2) | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P15** | **photograph, signature and resume receive no field set** pending G-11 and D-04.7 respectively | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P16** | **student ID receives one attribute and hall ticket two**, on the ground that nothing in the MVP consumes their remaining content | **PROPOSED DECISION — REQUIRES APPROVAL** |
| **G-12.P17** | Per-subject marks, enrolment number, registration number, institution attended, examination date, examination centre, and document validity dates are **excluded from the MVP field sets** (§17.2) | **PROPOSED DECISION — REQUIRES APPROVAL** |

### 17.2 Explicitly excluded, with the test each failed

Recorded so that exclusions are decisions rather than oversights, per §11's Containment Rule.

| Excluded concept | Test failed | Reason |
| --- | --- | --- |
| Per-subject marks on a marksheet | 1, 4 | No MVP consumer; would create the undefined repeating group of question **F** |
| Enrolment number | 1, 3 | No MVP consumer; not the same concept as a roll number |
| Registration number | 1, 3 | Same |
| Institution attended (as distinct from awarding body) | 1 | §16.4 |
| Examination name, date, centre | 1, 2 | The only consumer would be **FR-INT-005**, FUTURE / WON'T |
| Document validity or expiry date | 2 | The only consumer would be **FR-DOC-009**, FUTURE / WON'T |
| Father's / mother's / guardian's name | 1 | No MVP requirement consumes it. Printed on many of these documents; that is not a reason |
| Gender, category, nationality, blood group | 1 | No MVP requirement consumes any of them |
| Photograph or signature image embedded in another document | 1, 4 | An image, not structured information; **FR-MATCH** operates on the document, not on an embedded region |
| Issuing date, issuing office, document serial numbers | 1 | No MVP consumer |

**Ten concepts excluded against ten proposed.** The exclusions are the more important half: each is a piece of personal data DOCURA will not read, under **BR-017** and **NFR-PRIV-001**.

---

## 18. Candidate Gaps

Discovered during authoring. **No G-number is assigned; assigning one belongs to the owner of the decision register.**

### 18.1 Qualification scoping of education attributes

**CANDIDATE GAP — ID TO BE ASSIGNED.**
A person legitimately holds several qualifications, each with its own awarding body, year, result and roll number. Under **FR-INF-004** and the approved **G-13.3** identity rule, three documents giving three different values for `education.year_of_passing` is a conflict — but it is not a disagreement. The **G-13**-approved seven-property shape has **no property that scopes an attribute to a qualification**, and none may be added here.
*Affects:* FR-INF-004, FR-INF-005, AC-US-005-1/2, D-02 §11.6 and layers L6/L7, and the multiplicity of five attributes.
*Consequence carried in this document:* all five education attributes are **NOT EVALUATION-READY** and their multiplicity is **TBD**.
*Note for the G-13 owner:* this is the first evidence that the approved shape may be incomplete. It is recorded, not acted on — **G-13 is approved and is not reopened here.**

### 18.2 Day/month order in printed dates

**CANDIDATE GAP — ID TO BE ASSIGNED.**
N3 fixes the *canonical* representation as `YYYY-MM-DD`. It does not resolve the *source*: a printed date whose first two components are both ≤ 12 is ambiguous, and **AR-DET-003** requires normalisation to be deterministic. Resolving it by locale assumption would be an invention.
*Affects:* `person.date_of_birth`, FR-INF-008, AR-DET-003, AC-US-008-4.

### 18.3 Address component set

**CANDIDATE GAP — ID TO BE ASSIGNED.**
`person.postal_address` has no defensible data type until it is decided whether an address is one string or a structured object, and if structured, which components. Forms ask for address in parts; the specification says nothing. Until decided, the attribute has data type **TBD** and normalisation **N0**.
*Affects:* `person.postal_address`, FR-FILL-001, FR-FILL-002, G-12 question **D**.

### 18.4 Year-of-passing granularity

**CANDIDATE GAP — ID TO BE ASSIGNED.**
Some documents print a month and year of award rather than a year. Storing only the year discards information, which sits uneasily with **FR-INF-008**'s "without altering meaning" and **AR-DET-003**'s reversibility — though **G-13.6**'s retained raw value mitigates it.
*Affects:* `education.year_of_passing`.

### 18.5 Aggregate-result comparability

**CANDIDATE GAP — ID TO BE ASSIGNED.**
`education.aggregate_result` is proposed as a string precisely because a percentage, a CGPA and a letter grade are not comparable without a conversion rule that no requirement supplies. As a string it can be *filled* into a form (FR-FILL-001) but cannot be meaningfully *compared* — so **FR-INF-004** over this attribute would compare two incomparable representations.
*Affects:* `education.aggregate_result`, FR-INF-004, FR-FILL-002.

### 18.6 Per-type field presence is asserted, not evidenced

**CANDIDATE GAP — ID TO BE ASSIGNED.**
The required/optional markings in §14 state which concepts a document type carries. **`backend/step3.pdf` says nothing about the contents of any document**, and no corpus has been inspected — **G-02** is approved but collection has not begun. These markings are therefore informed expectation, not evidence, and every one of them is a hypothesis that stage-1 evaluation should confirm or correct.
*Affects:* every required/optional marking in §14; D-02 §7 ground-truth annotation.
*This is the single most likely place where this document is wrong.*

### 18.7 Whether the identifier numbers may be stored at all

**Already raised elsewhere; recorded here for completeness.** D-02 §11.7 and register D-05.3 raise, unresolved and marked safety-relevant, whether an identifier number "is stored at all, masked, or stored in part". `person.aadhaar_number` and `person.pan_number` cannot be closed until it is answered.

### 18.8 Destination of a value that maps to no attribute

**Already raised as G-13.g1** (§12 of the approved G-13 document; register D-05.7, awaiting a numbered entry). Authoring made it concrete: every excluded concept in §17.2 is a value an OCR engine will read and the vocabulary will not accept.

---

## 19. Evaluation Readiness

A field is **evaluation-ready** only where its semantic meaning, data type, normalisation, multiplicity and document applicability are all sufficiently defined for ground-truth annotation (**D-02 §7**, layers L4/L5).

### 19.1 Per-attribute readiness

| Attribute | Meaning | Data type | Normalisation | Multiplicity | Applicability | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | ✔ | ✔ string | ✔ N1+N2 | ✔ single | ✔ 9 types | **EVALUATION-READY** |
| `person.date_of_birth` | ✔ | ✔ date | ✔ N3 (source ambiguity §18.2 affects accuracy, not definition) | ✔ single | ✔ 4 types | **EVALUATION-READY** |
| `person.aadhaar_number` | ✔ | ✔ string | ✔ N5 | ✔ single | ✔ 1 type | **EVALUATION-READY** — but **not implementable** until §18.7 resolves |
| `person.pan_number` | ✔ | ✔ string | ✔ N5 | ✔ single | ✔ 1 type | **EVALUATION-READY** — same qualification |
| `person.postal_address` | ✔ | ✘ **TBD** | ✘ **N0** | ✔ single | ✔ 2 types | **NOT EVALUATION-READY — REQUIRES DECISION** (§18.3) |
| `education.awarding_body` | ✔ | ✔ string | ✔ N1+N2 | ✘ **TBD** | ✔ 4 types | **NOT EVALUATION-READY — REQUIRES DECISION** (§18.1) |
| `education.qualification_name` | ✔ | ✔ string | ✔ N1+N2 | ✘ **TBD** | ✔ 1 type | **NOT EVALUATION-READY — REQUIRES DECISION** (§18.1) |
| `education.year_of_passing` | ✔ | ✔ number | ✔ N4 | ✘ **TBD** | ✔ 4 types | **NOT EVALUATION-READY — REQUIRES DECISION** (§18.1, §18.4) |
| `education.aggregate_result` | ✔ | ✔ string | ✔ N1+N2 | ✘ **TBD** | ✔ 4 types | **NOT EVALUATION-READY — REQUIRES DECISION** (§18.1, §18.5) |
| `education.roll_number` | ✔ | ✔ string | ✔ N5 | ✘ **TBD** | ✔ 4 types | **NOT EVALUATION-READY — REQUIRES DECISION** (§18.1) |

**4 of 10 evaluation-ready** — two of which are blocked for implementation by §18.7. **6 of 10 not evaluation-ready**, five of them on the single scoping gap of §18.1.

### 19.2 Per-document-type readiness

| Document type | Readiness | Dependency |
| --- | --- | --- |
| Aadhaar | **Partially ready** — 3 of 4 attributes ready | §18.3 (address), §18.7 (number) |
| PAN | **Ready** — all 3 attributes ready | §18.7 for the number's implementation |
| address proof | **Not ready** | **G-09**, §18.3 |
| 10th marksheet | **Not ready** — 2 of 6 ready | **§18.1** |
| 12th marksheet | **Not ready** — 2 of 6 ready | **§18.1** |
| semester result | **Not ready** | **G-10**, §18.1 |
| degree certificate | **Not ready** — 1 of 5 ready | **§18.1** |
| photograph | **Not applicable — no field set** | **G-11** |
| signature | **Not applicable — no field set** | **G-11** |
| student ID | **Ready** — its single attribute is ready | — |
| hall ticket | **Not ready** — 1 of 2 ready | **§18.1** |
| resume | **Not applicable — no field set** | D-04.7 |
| Other / unclassified | **Ready** — the empty set is fully specified by §7.1 | — |

### 19.3 Evaluation-ready is not implementation-ready

Two separate bars, and this document meets neither fully:

- **Evaluation readiness** requires the five properties above. **Sensitivity is not among them**, which is why §15's universal TBD tier does not by itself block ground-truth annotation.
- **Implementation readiness** additionally requires the sensitivity tier (**FR-INF-007**, MUST), and therefore **G-14** and **G-15**. **Not one of the 10 attributes is implementation-ready**, and **G-13.9** forbids publishing the registry until every tier is filled.

### 19.4 Effect on D-02

**Unchanged from §9.4 and §14.4 of the approved G-13 document: stage-1 evaluation is not blocked.** What changes is that stage 2 now has a target for four attributes rather than none. **D-02 layers L4/L5** become partially annotatable — for `person.full_name`, `person.date_of_birth`, and the two identifier numbers — while **L6/L7** remain blocked on §18.1, because cross-document attribute mapping for the education group is exactly what the scoping gap prevents.

---

## 20. G-12 Approval Requirements

**G-12 cannot become APPROVED on this document alone.** The following must be approved or resolved, by owner.

| # | What must be approved or resolved | Owner | Why it cannot be skipped |
| --- | --- | --- | --- |
| **A1** | **G-12.P1 … G-12.P17** (§17.1) | Product Management | They are the substance. Every one is new product scope |
| **A2** | The **§17.2 exclusions** as decisions | Product Management | Ten concepts DOCURA will deliberately not read. Under BR-017 this is a privacy decision, not an omission |
| **A3** | **G-14** and **G-15** — sensitivity rules and default tier | Product Management | **G-13.9** forbids publishing an attribute without a tier. All 10 tiers currently read TBD. **This is the binding constraint on G-12 closure** |
| **A4** | **§18.1** — qualification scoping | Product Management + Architecture | Blocks five of ten attributes and the whole conflict-detection evaluation. Touches the G-13-approved shape and so needs that document's owner too |
| **A5** | **§18.7** — whether the identifier numbers are stored at all, masked, or in part | Product Management + Privacy | Safety-relevant and already open at D-02 §11.7 |
| **A6** | **§18.3** — address component set | Product Management | Without it `person.postal_address` has no type |
| **A7** | **G-09** | Product Management | address proof's field set cannot close |
| **A8** | **G-10** | Product Management | semester result's type identity, and AC-US-003-1 as a test |
| **A9** | **G-11** | Product Management | Whether photograph and signature get field sets at all |
| **A10** | **D-04.7** — resume | Product Management | Whether it is an extraction type |
| **A11** | **§18.2, §18.4, §18.5** — date order, year granularity, result comparability | Product Management | Each is a normalisation decision and therefore, under **G-13.5**, a conflict-detection decision |
| **A12** | Register entries for the **§18 candidate gaps** | Owner of the decision register | No G-number is invented here |
| **A13** | The **§11 Containment Rule amendment** to `step3.pdf` | Product Management | Approval here is a project decision beside the specification, never an amendment to it |

**Also required, and outside this document:** confirmation by **corpus evidence** (§18.6) that the per-type presence markings in §14 are correct.

---

## 21. G-12 Exit Criteria

Superseding §13's criteria, which were written before any field existed. G-12 is closed when **all** hold.

| # | Exit criterion | Depends on | Status today |
| --- | --- | --- | --- |
| **Y1** | §17.1's proposed decisions approved, or rejected with alternatives recorded | A1 | **Not met — awaiting approval** |
| **Y2** | §17.2's exclusions approved as decisions | A2 | **Not met** |
| **Y3** | Every attribute in §15 carries a real sensitivity tier — **G-14 and G-15 closed** | A3 | **Not met — 10 of 10 tiers are TBD** |
| **Y4** | §18.1 qualification scoping resolved, and multiplicity stated for all five education attributes | A4 | **Not met** |
| **Y5** | §18.7 resolved, and `person.aadhaar_number` / `person.pan_number` either confirmed, narrowed, or withdrawn | A5 | **Not met** |
| **Y6** | §18.3 resolved and `person.postal_address` given a data type and normalisation rule | A6 | **Not met** |
| **Y7** | **G-09**, **G-10**, **G-11** answered, and §14.3, §14.6, §14.8, §14.9 closed accordingly | A7–A9 | **Not met** |
| **Y8** | **D-04.7** answered and §14.12 closed accordingly | A10 | **Not met** |
| **Y9** | §18.2, §18.4, §18.5 resolved | A11 | **Not met** |
| **Y10** | All §18 candidate gaps carry register IDs | A12 | **Not met** |
| **Y11** | Every attribute in §15 is **EVALUATION-READY** under §19's five criteria | Y3–Y9 | **Not met — 4 of 10** |
| **Y12** | Every field justified against a requirement that consumes it (**G-13.12**), and the justification reviewed | A1, A2 | **Met in draft** — §14 states a consumer for each; review outstanding |
| **Y13** | The field sets and the vocabulary are held as configuration and versioned (**NFR-MNT-001**, **G-13.1**, **G-13.10**) | Y1 | **Not met** |
| **Y14** | §18.6 discharged: per-type presence confirmed against the collected corpus | Corpus, stage-1 evaluation | **Not met — corpus not collected** |
| **Y15** | D-02 layers **L4** and **L5** annotatable for every in-scope type | Y11 | **Not met — partially annotatable for 4 attributes** |
| **Y16** | `step3.pdf` amended under §11's Containment Rule, or the divergence formally accepted | Y1–Y13 | **Not met** |

**What closure does not unblock.** Y1–Y15 unblock the design and annotation of field-extraction evaluation. They do not unblock **L6/L7** or **D-02 §11.6** beyond what §18.1's resolution permits; nor the **BR-001** threshold, which additionally requires G-04, G-05, G-06, G-07 and the evaluation itself; nor the build of FR-OCR-004…006 and FR-INF-001…009, which §12.3 additionally gates on assumptions **A-5** and **A-7**.

---

**Verification performed before completion**

| Check | Result |
| --- | --- |
| Every document type claim traceable to `step3.pdf` | **Yes** — §3.2 cites §7.1, AC-US-003-1, NFR-USE-005; §3.3 records non-types. §14 uses the thirteen §7.1 entries verbatim: **none renamed, merged, added, or removed** |
| Every explicitly required field traceable to `step3.pdf` | **Yes** — §4.2 (M1–M9) and §4.3 (F1–F17) carry requirement IDs |
| Examples presented as requirements | **No** — §4.4 isolates them, including document 02 Table 13.1; §14.0.1's format illustration is labelled **ILLUSTRATIVE EXAMPLE — NOT A REQUIREMENT** and uses pattern notation only, never a specimen value |
| Any existing requirement falsely claimed to define a field | **No** — §14–§21 state throughout that `step3.pdf` defines zero information fields. The only field-set claim carrying **REQUIREMENT** status is §14.13, where §7.1 defines the set as empty |
| Fields authored | **Yes, in Part II only — 10 canonical attributes across 13 document types.** Every one carries **PROPOSED DECISION — REQUIRES APPROVAL**; none is presented as existing. §1–§13 are unchanged and still name no field |
| G-13's approved seven-property shape | **Preserved unaltered** — §15 carries all seven for every attribute, adds none, drops none. §18.1 records evidence that the shape may be incomplete and **does not act on it** |
| G-09 / G-10 / G-11 silently resolved | **No** — §14.3 (G-09), §14.6 (G-10), §14.8/§14.9 (G-11) are each marked dependent and left open |
| G-13, G-19, G-20 resolved | **No** — G-13 is approved elsewhere and not reopened; G-19 and G-20 are untouched |
| New G-number invented | **No** — §18 uses **CANDIDATE GAP — ID TO BE ASSIGNED** throughout |
| Canonical vocabulary document modified | **No** — `SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md` is unchanged by this authoring |
| Prior analysis deleted | **No** — §1–§13 are preserved in full and unmodified; Part II is additive |
| Production code touched | **No** |
| `step3.pdf` modified | **No** |
| Documents collected / OCR run | **0 / No** |
| Committed or pushed | **No** |
