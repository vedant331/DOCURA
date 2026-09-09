# Sprint 4 — D-02: Held-Out OCR / Extraction Evaluation Plan

| Field | Value |
| --- | --- |
| Decision | **D-02 — held-out evaluation corpus and evaluation method (AR-AST-008, study S-6)** |
| Status | **Planning only.** No corpus collected. No engine installed. No engine selected. No evaluation run. No results exist. |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0 (39 pages) |
| Related | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) — D-02.1 to D-02.4 and the gap inventory G-01…G-28 |
| Related | [`SPRINT_4_D01_OCR_ARCHITECTURE.md`](SPRINT_4_D01_OCR_ARCHITECTURE.md) — the extraction port this evaluation runs candidates through |
| Blocking | BR-001, the review threshold, §7.1 MVP type set, FR-OCR-004/005/006, and engine selection |

---

## 0. How to read this document

### 0.1 The evidence rule

Every statement in this plan is one of five kinds, and each is labelled where it appears:

| Label | Meaning |
| --- | --- |
| **REQUIRED** | Stated in `backend/step3.pdf`. Quoted or cited by requirement ID. Not negotiable. |
| **RECOMMENDED** | A method proposal by engineering. Not in the specification. May be rejected without amending requirements. |
| **TBD** | A value the specification itself marks as undetermined, or one that only the evaluation can produce. **No number is invented in this document.** |
| **REQUIREMENTS GAP** | The specification is silent on something it needs. Requires a requirements amendment, not a design decision. |
| **DECISION REQUIRED** | A choice the specification deliberately leaves to product or legal ownership. Named owner, not resolved here. |

### 0.2 What this document does not do

This is D-02 **planning**. It does not install an OCR engine, select an OCR engine, collect documents, create evaluation data, produce evaluation results, modify production code, change the database schema, write a migration, define an API, or add a dependency.

Where a number would be needed to make a statement concrete and the specification does not supply one, the number is marked **TBD** and left unset. A plausible-sounding invented figure would make this plan appear rigorous while making it untestable — the same failure the specification's own §02 preamble warns against: *"Inventing a plausible-sounding figure here would make the requirement untestable while appearing rigorous."*

---

## 1. Purpose

### 1.1 The obligation this plan discharges

> **AR-AST-008** (MVP): *"Assisted components shall be evaluated against a held-out corpus of real, imperfect documents before any threshold is set."* — **REQUIRED**

This plan defines **how** that evaluation will be conducted, **what evidence** it must produce, and **which decisions** that evidence is permitted to settle. It does not conduct it.

### 1.2 Why the evaluation precedes the engine

The specification orders these events explicitly, and the order is the point:

1. A corpus of real, imperfect documents is assembled — **AR-AST-008**.
2. Candidate assisted components are evaluated against it — **AR-AST-008**.
3. Only then are thresholds set — **AR-AST-008** ("before any threshold is set"); **BR-001** ("Threshold value: TBD — to be validated (study S-6)").
4. Only then is the MVP document-type set final — **§7.1** ("Final inclusion of each type is subject to the extraction evaluation in study S-6").

Selecting an engine first and evaluating it afterwards inverts steps 2 and 3 and produces a threshold that merely describes whatever the chosen engine happens to do. D-01 therefore built the extraction port with the engine deliberately unselected, so that this evaluation can select it.

### 1.3 What this evaluation is authorised to decide

| Decision | Authorised by | Status today |
| --- | --- | --- |
| The value of the automatic-action threshold | BR-001 — "TBD — to be validated (study S-6)" | **TBD** |
| The value of the review threshold | FR-OCR-006, BR-002, §7.1 | **TBD** — and see **G-04**: the specification gives it no value *and* no TBD marker |
| Which candidate document types enter the MVP with structured extraction | §7.1, ASM-001 | **TBD** — all twelve are provisional |
| Which candidate types are demoted to store-and-search only | §7.1 | **TBD** |
| Which OCR / extraction engine is adopted | §6 Selection Principle, AR-AST-008 | **TBD — pending this evaluation** |
| Whether assumption A-7 holds | §12.3 | **TBD** |

### 1.4 What this evaluation cannot decide

It cannot supply requirements that do not exist. In particular, the field-extraction half of the evaluation (§11) **cannot run at all** until the per-type field definitions (**G-12**) and the canonical attribute vocabulary (**G-13**) are authored and approved, because there is nothing to measure extraction *against*. This constraint is stated once here and carried through §11, §17, and §19.

It also cannot settle A-1, A-2, A-5, or A-8. §12.3 assigns those to other studies; this plan addresses **A-7** and **ASM-001** only.

---

## 2. Source Requirements

Every requirement below is quoted or cited from `backend/step3.pdf`. Nothing in this section is engineering opinion.

### 2.1 The governing architectural requirement

| ID | Text | Release |
| --- | --- | --- |
| **AR-AST-008** | "Assisted components shall be evaluated against a held-out corpus of real, imperfect documents before any threshold is set." | MVP |

Four separable obligations sit inside that one sentence. Each constrains this plan independently:

| Obligation | The word that carries it | Consequence for this plan |
| --- | --- | --- |
| The corpus is **held out** | "held-out" | It must not be the material used to build, tune, or configure the extractor — §6 |
| The documents are **real** | "real" | Synthetic or template-generated documents do not satisfy the requirement — §4.2 |
| The documents are **imperfect** | "imperfect" | A corpus of clean scans does not satisfy the requirement — §4.4 |
| Evaluation **precedes** thresholds | "before any threshold is set" | No threshold may be assigned first and validated later — §12 |

### 2.2 The assisted-component contract every candidate must satisfy

| ID | Text | Bearing on evaluation |
| --- | --- | --- |
| **AR-AST-001** | "Text extraction from document images shall produce, for each extracted value, a confidence measure usable by BR-001." | A candidate with no per-value confidence is **ineligible**, whatever its accuracy — §13.2 |
| **AR-AST-002** | "Document classification shall produce a type and a confidence, and shall be able to return 'unrecognised' rather than a forced choice." | The corpus must contain out-of-set documents or this cannot be measured — §10 |
| **AR-AST-003** | "Field-meaning interpretation shall produce a semantic label and a confidence, and shall be able to return 'unknown'." | Belongs to the extension side of the product; recorded here because it shares the threshold set of §12 |
| **AR-AST-006** | "Every assisted output shall be explainable to the user in terms of the source it came from." | Source region is an evaluated property, not a nicety — §9 |
| **AR-AST-007** | "No assisted component shall be permitted to escalate its own authority — it may lower a confidence, never raise it, and may add a sensitivity classification, never remove one." | Constrains any calibration or post-processing applied to engine output — §12.5 |

### 2.3 Functional requirements under evaluation

| ID | Requirement text (abbreviated where long) | Evaluated in |
| --- | --- | --- |
| **FR-OCR-001** | "extract machine-readable text from each uploaded document" | §8 |
| **FR-OCR-002** | "classify each document into a supported document type, or as unrecognised" | §10 |
| **FR-OCR-003** | "record a confidence value for the classification" | §10, §12 |
| **FR-OCR-004** | "For each supported document type, extract the defined set of information fields for that type" | §11 — **blocked on G-12** |
| **FR-OCR-005** | "record a confidence value for every extracted field independently of the document-level confidence" | §11, §12 |
| **FR-OCR-006** | "Extracted fields below the review threshold shall be marked as needing user review and shall not be used for automatic filling" | §12 |
| **FR-OCR-007** (SHOULD) | "show each extracted value alongside the region of the source document it was read from" | §9 |
| **FR-OCR-008** | "process multi-page documents as a single document" | §4.5, §8.5 |
| **FR-OCR-009** | "Where processing fails, retain the original file, state what failed, and offer a retry and a manual-entry path" | §15 |
| **FR-OCR-010** (SHOULD) | "The user shall be able to request reprocessing of a document" | §15.4 |
| **FR-INF-002** | "Every attribute value shall reference the document it came from and the confidence with which it was read." | §9, §11 |
| **FR-INF-004** | "detect when two documents give different values for the same attribute" | §4.6, §11.6 |
| **FR-INF-007** | "Every attribute shall carry a sensitivity classification of routine, sensitive, or consequential." | §5, §16 — **blocked on G-14** |
| **FR-INF-008** | "normalise attribute formats deterministically — dates, casing, spacing, and numeric precision — without altering meaning" | §7.5 |

### 2.4 Business rules that govern the evaluation's conclusions

| ID | Rule | Effect on this plan |
| --- | --- | --- |
| **BR-001** | "An action may be taken automatically only when the confidence of both the field interpretation and the source value meets or exceeds the automatic-action threshold. **Threshold value: TBD — to be validated (study S-6).**" | The evaluation's primary numeric output |
| **BR-002** | "Information extracted below the review threshold is never used for automatic action, regardless of how well it matches a field." | Fixes the direction of the safety argument in §12.4 |
| **BR-003** | "Where more than one reasonable value, option, or document exists, DOCURA must ask the user. It may not select the most likely candidate on the user's behalf." | A candidate that resolves ambiguity silently fails regardless of score |
| **BR-004** | "Where the user's own documents disagree, DOCURA must surface the disagreement and may not resolve it by rule, recency, or preference." | Makes the person-grouped corpus structure of §4.6 mandatory |
| **BR-016** | Summarised in §14 as: "fail towards inaction and tell the user" | The scoring asymmetry of §12.4 |

The specification states that BR-001 to BR-009 "are the formal statement of the product principle and are not configurable by anyone, including the user, an administrator, or a future enterprise customer." **The evaluation sets the value inside BR-001; it cannot relax the rule.**

### 2.5 Non-functional requirements that constrain how the evaluation is run

| ID | Text (abbreviated) | Constraint on this plan |
| --- | --- | --- |
| **NFR-SEC-002** | "Documents and extracted information shall be encrypted at rest." | §16.2 — meaning undefined, see G-21…G-24 |
| **NFR-SEC-003** | "Every request for a document or attribute shall be authorised against the requesting user's identity; ownership shall never be inferred from an identifier supplied by the client." | §16.3 |
| **NFR-SEC-008** | "The system shall not claim to be unbreachable... Security statements shall describe specific measures and their limits." | §16.7 — applies to how this plan describes its own controls |
| **NFR-PRIV-001** | "collect only information required to deliver a function the user has requested" | §5.3 — an evaluation corpus is not a function the contributor requested |
| **NFR-PRIV-002** | "A user's documents and extracted information shall not be used to train shared models, and shall not be readable by other users under any circumstance." | §5.2 — binds users to users; **silent on team access (G-02)** |
| **NFR-PRIV-003** | "Deletion requested by the user shall remove the document, its extracted information, and its derived copies within a stated period. **Period: TBD**" | §5.6 — does not cover an evaluation corpus (G-02) |
| **NFR-PRIV-006** | "Any processing performed outside the user's device shall be disclosed in plain language before the user's first upload." | §5.5, §13.4 — governs any externally hosted candidate |
| **NFR-PRIV-007** | "Diagnostic and analytics data shall exclude document contents and extracted personal values." | §14.4 — constrains what the evaluation report may contain |
| **NFR-MNT-001** | "Supported document types and their extractable fields shall be definable as configuration, so adding a type does not require re-engineering." | §7.2 — ground truth attaches to the configured field set |
| **NFR-MNT-002** | "Confidence thresholds shall be externally configurable and changeable without a code release." | §12.6 — the evaluation's output is configuration, not code |
| **NFR-OBS-001** | "measure extraction and field-interpretation confidence distributions in aggregate, without retaining the underlying values" | §12.2 |
| **NFR-OBS-003** | "measure user override rate on automatically filled fields as the primary indicator of silent error" | §17.4 — the production counterpart of this evaluation |
| **NFR-OBS-004** | "Failures in detection, extraction, or matching shall be recorded with enough context to diagnose them, and without personal values." | §15.2 |

### 2.6 Edge cases the corpus must exercise

| ID | Situation | Required behaviour (quoted) | Corpus consequence |
| --- | --- | --- | --- |
| **EC-001** | OCR fails entirely | "Retain the original, mark the document as failed with a stated reason, offer retry and manual entry. The document remains stored and searchable by label." | Corpus must contain documents on which extraction is expected to fail — §4.7 |
| **EC-002** | Poor-quality document | "Extract what is legible, mark low-confidence fields for review, and tell the user which fields could not be read confidently. Never present a low-confidence value as settled." | Corpus must contain degraded-but-legible documents, distinct from EC-001 — §4.4 |
| **EC-003** | Wrong document uploaded | "Classify honestly. If the type is clear, store it as that type. If unclear, store as unclassified and ask. Never force it into an expected slot." | Corpus must contain out-of-set documents — §4.8 |
| **EC-004** | Documents conflict | "Raise a conflict, mark neither authoritative, and treat any field needing that attribute as ambiguous until the user resolves it." | Corpus must be grouped by person — §4.6 |

### 2.7 Acceptance criteria this evaluation supplies evidence for

| AC | Text (abbreviated) | Evaluated in |
| --- | --- | --- |
| **AC-US-003-1** | "GIVEN the user has uploaded a semester marksheet... THEN the document appears in the vault classified as a marksheet with its extracted information attached." | §10, §11 |
| **AC-US-003-2** | "WHEN the user views it, THEN every extracted field is shown with its own confidence indication." | §11, §12 |
| **AC-US-003-3** | "GIVEN a document whose type cannot be determined confidently... THEN it is stored as unclassified, the user is asked to identify it, and no type is assumed." | §10.4 |
| **AC-US-003-4** | "GIVEN a document of five pages, WHEN it is processed, THEN it is stored as one document and information from every page is available." | §4.5, §8.5 |
| **AC-US-003-5** | "GIVEN processing fails... THEN the original file is still present and downloadable, the failure reason is stated, and both retry and manual entry are offered." | §15 |
| **AC-US-004-1** | "WHEN the user opens an extracted value, THEN the source document and the region the value was read from are shown." | §9 |
| **AC-US-004-4** | "GIVEN an extracted value below the review threshold... THEN that value is never placed automatically." | §12.4 |
| **AC-US-005-1** | "GIVEN two documents give different values for the same attribute... THEN a conflict is raised and neither value is marked authoritative." | §11.6 |

The specification notes that criteria depending on a TBD threshold "test the behaviour at the threshold rather than the number itself, so it remains valid once the number is set." **This evaluation produces the number those criteria are waiting for.**

### 2.8 Assumptions this evaluation is designed to settle

| ID | Assumption / failure mode | Source |
| --- | --- | --- |
| **A-7** | §12.3 states the failure mode as: "Extraction is unreliable on real scans; thresholds may exclude most automatic action." Affected requirements: FR-OCR-004…006, BR-001. | §12.3 |
| **ASM-001** | "The MVP document type set is the right one — broad enough to demonstrate value, narrow enough to extract reliably." How to settle it: "Study S-6 extraction evaluation on a real corpus." | Appendix A, Table A.1 |

Horizon **H3** in §11 confirms the same dependency from the other direction: comprehension expansion (FR-OCR-011/012, FR-MATCH-011) unlocks only when "Extraction quality on the MVP type set is proven against real documents."

### 2.9 What the specification does not say about this evaluation

**REQUIREMENTS GAP — G-02 and G-03 in the decision register.** The specification names the corpus obligation and nothing else about it. It gives:

- **no** corpus size, at any level — total, per type, or per condition;
- **no** acquisition method;
- **no** consent model for evaluation use;
- **no** retention or destruction rule for evaluation material;
- **no** access-control rule for the DOCURA team;
- **no** definition of "imperfect";
- **no** per-type coverage minimum;
- **no** pass/fail criterion;
- **no** named owner of the corpus;
- **no** re-evaluation trigger when a component version changes.

**No corpus size is proposed anywhere in this document.** Every one of these absences is carried into §18.

---

## 3. Requirement-to-Evidence Matrix

This matrix is the spine of the plan: for each requirement under evaluation, what artefact would demonstrate it, and what currently blocks that artefact. A requirement with no producible evidence is not "at risk" — it is **not evaluable**, and saying so is the useful output.

### 3.1 Matrix

| Requirement | What must be shown | Evidence artefact | Corpus property it depends on | Blocked by | Status |
| --- | --- | --- | --- | --- | --- |
| **FR-OCR-001** | Machine-readable text is produced for each document | Per-document text output plus character/word error rates against transcription ground truth (§8) | Real, imperfect documents (§4.2, §4.4) | Corpus not collected | **Evaluable once corpus exists** |
| **FR-OCR-008** | A multi-page document yields one result with every page represented | Per-page presence check; a field located on a later page is recovered (§8.5) | Multi-page documents, incl. late-page fields (§4.5) | Corpus not collected | **Evaluable once corpus exists** |
| **FR-OCR-002** | A type is assigned, or "unrecognised" is returned honestly | Confusion matrix over candidate types plus an explicit unrecognised class (§10) | Type-labelled in-set documents **and** out-of-set documents (§4.8) | §7.1 type set is provisional (D-04) | **Evaluable once corpus exists** |
| **FR-OCR-003** | A classification confidence is recorded | Confidence recorded for every classification decision, including "unrecognised" (§10.5) | As above | Confidence semantics undefined (**G-06**) | **Partially evaluable** — comparability across candidates unresolved |
| **FR-OCR-004** | The **defined set** of fields is extracted per type | Per-field precision/recall against field-level ground truth (§11) | Field-level ground truth (§7) | **G-12 — no field definitions exist for any type** | **NOT EVALUABLE** |
| **FR-OCR-005** | A per-field confidence exists, independent of the document-level one | Per-field confidence recorded and demonstrably not a copy of the document score (§11.4) | Field-level ground truth | **G-12**, and **G-06** | **NOT EVALUABLE** |
| **FR-OCR-006** | Below-threshold fields are marked for review and never auto-filled | Threshold sweep showing the behavioural split (§12.4) | Field-level ground truth | **G-04** (no value), **G-12** | **NOT EVALUABLE** — this evaluation is what would produce the value |
| **FR-OCR-007** | Each value is shown with the source region it was read from | Region-localisation accuracy against region ground truth (§9) | Region ground truth (§7.4) | **G-12** for field regions; text-block regions are evaluable | **Partially evaluable** |
| **FR-OCR-009** | Failure retains the original, states the reason, offers retry and manual entry | Failure-path exercise over expected-failure documents (§15) | Expected-failure documents (§4.7) | Manual-entry destination undefined (**G-27**) | **Partially evaluable** |
| **FR-OCR-010** | Reprocessing can be requested | Reprocessing determinism check (§15.4) | Any corpus document | Correction-retention semantics (**G-20**) | **Partially evaluable** |
| **FR-INF-002** | Every value references its document and its confidence | Provenance completeness check — no value without a document reference and a confidence (§9.5) | Field-level ground truth | **G-12** | **NOT EVALUABLE** |
| **FR-INF-004** | Disagreement between two documents on one attribute is detected | Conflict detection recall/precision over person-grouped sets (§11.6) | **Person-grouped** corpus with known disagreements (§4.6) | **G-13 — no canonical attribute vocabulary** | **NOT EVALUABLE** |
| **FR-INF-007** | Every attribute carries a sensitivity tier | Tier assignment coverage over the extracted attribute set (§5.7) | Attribute vocabulary | **G-14 — classification rules are not in the specification** | **NOT EVALUABLE** |
| **FR-INF-008** | Normalisation is deterministic and meaning-preserving | Same input, same normalised output, across runs; a normalisation that changes meaning is a defect (§7.5) | Ground truth expressed in normalised form | **G-13** for per-attribute rules | **Partially evaluable** |
| **AR-AST-001** | A per-value confidence exists that is "usable by BR-001" | Candidate eligibility check (§13.2) plus calibration evidence (§12.2) | Any corpus | **G-06** — "usable" is undefined | **Partially evaluable** |
| **AR-AST-002** | The classifier can return "unrecognised" rather than forcing a choice | Rate of correct abstention on out-of-set documents (§10.4) | Out-of-set documents (§4.8) | None — this is evaluable as specified | **Evaluable once corpus exists** |
| **AR-AST-006** | Every assisted output is explainable by its source | Every output carries page and region provenance (§9.5) | Region ground truth | **G-12** for field-level; page-level evaluable | **Partially evaluable** |
| **AR-AST-007** | No component raises its own confidence or removes a sensitivity tier | Audit of any calibration or post-processing step (§12.5) | N/A — a property of the pipeline, not the corpus | **G-14** for the sensitivity half | **Partially evaluable** |
| **AR-AST-008** | Evaluation occurred against a held-out corpus of real, imperfect documents before thresholds were set | The versioned evaluation report itself (§14.3) | The whole corpus | **DECISION REQUIRED** — no artefact is specified (D-02.o) | **Definition missing** |
| **BR-001** | The automatic-action threshold is set on evidence | Threshold-selection rationale derived from the sweep (§12.4) | Field-level ground truth | **G-04**, **G-05**, **G-12** | **NOT EVALUABLE** yet |
| **§7.1 type inclusion** | Each candidate type meets the review threshold, or is demoted | Per-type pass/fail table (§17.2) | Every candidate type present (§4.3) | **G-12**, and the threshold itself | **NOT EVALUABLE** yet |
| **EC-001 / EC-002 split** | Illegible fails honestly; degraded-but-legible extracts partially | Behavioural comparison across the two corpus strata (§15.3) | Both strata present (§4.4, §4.7) | None beyond corpus | **Evaluable once corpus exists** |
| **EC-003** | A wrong or out-of-set document is not forced into an expected slot | Forced-classification rate on out-of-set documents (§10.4) | Out-of-set documents | None beyond corpus | **Evaluable once corpus exists** |

### 3.2 What the matrix shows

Three findings follow directly from the table and should be read as the plan's headline:

1. **The OCR-quality half of the evaluation (§8, §9 text-level, §10, §15) is evaluable as soon as a corpus exists.** It depends on no missing requirement. Text extraction, classification, honest abstention, multi-page handling, and the failure path can all be measured against a corpus and a transcription.

2. **The field-extraction half (§11, §12, and therefore §17's type-inclusion decision and BR-001's number) is not evaluable at all today.** It is blocked not by engineering difficulty but by two absences in the requirements: **G-12** (no field definitions for any type) and **G-13** (no canonical attribute vocabulary). No amount of corpus collection unblocks it.

3. **The evaluation can therefore be run in two stages**, and §19 splits the exit criteria accordingly. **RECOMMENDED**: run stage 1 (OCR quality, classification, failure behaviour, engine eligibility) as soon as the corpus exists, and stage 2 (field extraction, calibration, threshold selection, type inclusion) once G-12 and G-13 are closed. This is a proposal, not a requirement; the specification treats S-6 as one study.

### 3.3 Requirements deliberately out of scope for D-02

| Requirement | Why it is not evaluated here |
| --- | --- |
| FR-OCR-011, FR-OCR-012 | FUTURE / WON'T. Handwriting and additional scripts are H3, unlocked by this evaluation's success — not by it. |
| FR-FLD, FR-FRM, FR-FILL, FR-DRP | Extension-side interpretation. Governed by A-8 and study S-3/S-5, not S-6. AR-AST-003 is noted in §2.2 only because it shares the threshold set. |
| NFR-PERF-001, NFR-PERF-003 | §15 of the specification states these cannot be fully tested until a manual baseline is measured in study S-2. Processing latency is recorded as an observation in §14.5, never scored. |
| FR-INF-003, FR-INF-006, FR-INF-009 | User correction, authoritative designation, and history are behaviours of the record, not properties of extraction. |

---

## 4. Corpus Design

**Nothing in this section states a size.** The specification gives none, and §2.9 records that absence as a gap. What follows specifies the corpus's **required properties** — which the specification does constrain — and marks every quantity **TBD**.

### 4.1 The corpus is a product deliverable

**RECOMMENDED.** The corpus gates BR-001, the review threshold, §7.1's type set, D-03, D-04, and D-05 simultaneously. Treating it as a testing task owned by nobody is how AR-AST-008 quietly goes unmet. It needs a named owner, a version, and a lifecycle.

**DECISION REQUIRED — corpus ownership (D-02.a).** Who owns the corpus as an asset — the company, the study, or the individual contributors — and who may authorise its use for a second purpose, such as re-evaluating a new engine version later. *Owner: PM + Legal.*

### 4.2 Property 1 — the documents must be real

> **AR-AST-008**: "...a held-out corpus of **real**, imperfect documents..." — **REQUIRED**

Synthetic documents, template-generated documents, and filled-in blank forms do not satisfy this. The register records document 02's own warning about the sibling study S-1: *"Any study that substitutes dummy data will produce a false positive on our riskiest assumption."* The same warning applies with more force here, because A-7 is the assumption S-6 exists to settle.

**DECISION REQUIRED — acquisition method (D-02.d).** Volunteer donation, a paid panel, staff-and-family documents, or public-record documents. Each has a different consent profile and a different representativeness profile, and the choice determines §5 entirely. *Owner: PM.*

**Note on staff-and-family documents.** They are the cheapest source and the most likely to be unrepresentative: a team's own documents skew toward a narrow set of issuing authorities, languages, and scan qualities. If chosen, that skew is a stated limitation of the evaluation report (§14.6), not a footnote.

### 4.3 Property 2 — every candidate document type must appear

> **§7.1**: "Final inclusion of each type is subject to the extraction evaluation in study S-6; a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only rather than shipped as unreliable." — **REQUIRED**

A type absent from the corpus cannot be included in the MVP, because §7.1 makes inclusion conditional on evidence this evaluation produces. The candidate set from §7.1 is:

| Group | Types named in §7.1 | Status per the specification |
| --- | --- | --- |
| Identity and address | Aadhaar, PAN, address proof | All **provisional** — conditional on S-6 |
| Education | 10th marksheet, 12th marksheet, semester result, degree certificate | All **provisional** — conditional on S-6 |
| Application assets | photograph, signature, student ID, hall ticket, resume | All **provisional** — conditional on S-6 |
| Other | unclassified — "stored and searchable as an unclassified document, no structured extraction" | The **only** unconditional entry in §7.1 |

**There are no unconditionally supported extraction types in the specification.** All twelve are provisional by the plain text of §7.1 and by ASM-001.

**DECISION REQUIRED — per-type coverage (D-02.h).** The specification requires every candidate type to be evaluable but sets no per-type minimum count. **TBD.** *Owner: PM + Engineering.*

Three type definitions are themselves unresolved and constrain what can be collected:

| Type | Problem | Gap |
| --- | --- | --- |
| Address proof | A category, not a document type; its members are never enumerated. Cannot be sampled without knowing what qualifies. | **G-09** |
| Semester result | §7.1 says "semester result"; AC-US-003-1 says "semester marksheet". One type or two is unresolved. | **G-10** |
| Photograph, signature | Whether these have any structured information to extract is never stated. They may be classification-only. | **G-11** |

**Consequence:** for a type with no defined fields, only **classification** (§10) can be evaluated, not **field extraction** (§11). The corpus must still contain it, because the classifier must be able to recognise it or decline.

### 4.4 Property 3 — the documents must be imperfect

> **AR-AST-008**: "...real, **imperfect** documents..." — **REQUIRED**

A corpus of clean scans does not satisfy AR-AST-008 and would produce a threshold calibrated for conditions that do not occur.

The specification does not define "imperfect". **DECISION REQUIRED — the degradation taxonomy (D-02.i).** *Engineering proposes, PM approves.*

**RECOMMENDED** taxonomy, offered as a starting proposal only — each dimension is a condition the corpus should span, with **counts and proportions TBD**:

| Dimension | Range to span |
| --- | --- |
| Capture method | Flatbed scan, phone photograph, screenshot, PDF export, photocopy |
| Resolution | High-DPI down to the lowest DPI the vault accepts (Sprint 3 upload limits govern what can exist) |
| Geometry | Square-on, skewed, rotated, mixed page orientation within one document |
| Lighting | Even, glare, shadow, partial over-exposure |
| Completeness | Whole page, cropped edge, cut-off text |
| Overlay | Stamps, seals, signatures over text, handwritten annotations on printed text, watermarks |
| Print quality | Clean print, faded print, photocopy-of-photocopy degradation, show-through from the reverse side |
| Colour | Colour, greyscale, thresholded black-and-white |

The behavioural anchor for this stratum is **EC-002**: "Extract what is legible, mark low-confidence fields for review, and tell the user which fields could not be read confidently."

**The corpus must be stratified by degradation**, not merely contain degraded examples — otherwise a per-condition result cannot be reported, and the evaluation cannot say *which* conditions break extraction. That distinction is what makes the result actionable.

### 4.5 Property 4 — multi-page documents

> **FR-OCR-008**: "The system shall process multi-page documents as a single document." — **REQUIRED**
> **AC-US-003-4**: "GIVEN a document of five pages, WHEN it is processed, THEN it is stored as one document and information from every page is available." — **REQUIRED**

**REQUIRED corpus property:** multi-page documents must be present, and must include at least one document where a required value appears **only on a later page**. A multi-page corpus in which every value sits on page 1 does not test FR-OCR-008 at all — it tests page-1 extraction with extra pages attached.

Page-depth distribution and count: **TBD**. AC-US-003-4's five-page example is an illustration in an acceptance criterion, not a corpus specification, and is not treated as one here.

### 4.6 Property 5 — the corpus is grouped by person, not pooled

> **FR-INF-004**: "The system shall detect when two documents give different values for the same attribute." — **REQUIRED**
> **BR-004**: "Where the user's own documents disagree, DOCURA must surface the disagreement and may not resolve it by rule, recency, or preference." — **REQUIRED**
> **AC-US-005-1**: "GIVEN two documents give different values for the same attribute, WHEN processing completes, THEN a conflict is raised and neither value is marked authoritative." — **REQUIRED**

This is a **corpus-structure requirement**, and it is the one most easily missed. Conflict detection cannot be evaluated against a flat pool of documents. It requires **document sets belonging to one person**, in which two documents disagree on the same attribute — a name spelled differently across two certificates, a date of birth transcribed differently, an address that has changed.

**RECOMMENDED:** the corpus is organised as *person → documents*, with each person's set carrying a known conflict inventory (which attributes disagree, and how). Persons with **no** conflicts are equally necessary, to measure false-positive conflict raising — a system that reports conflicts everywhere is as unusable as one that reports none.

**Note:** conflict *detection* is deterministic under **AR-DET-008** ("Conflict detection between documents shall be deterministic; conflict resolution shall never be automated at all"). What the corpus evaluates is therefore not a model's judgement but whether extraction plus normalisation produces values on which the deterministic comparison behaves correctly. That is why §11.6 measures it downstream of extraction rather than as a separate component.

### 4.7 Property 6 — documents on which extraction is expected to fail

> **FR-OCR-009**: "Where processing fails, the system shall retain the original file, state what failed, and offer a retry and a manual-entry path." — **REQUIRED**
> **EC-001**: "OCR fails entirely — Retain the original, mark the document as failed with a stated reason, offer retry and manual entry." — **REQUIRED**

**REQUIRED corpus property:** documents on which extraction is *expected* to fail must be present, so the failure path is evaluated rather than assumed. A corpus containing only documents that succeed evaluates half the requirement set.

**The EC-001 / EC-002 distinction is a corpus stratum boundary**, and it must be drawn during ground-truth annotation (§7.6), not inferred from results:

| Stratum | Definition | Required behaviour |
| --- | --- | --- |
| Degraded but legible | A human annotator can read the values | EC-002 — extract what is legible, mark low confidence |
| Not legible | A human annotator cannot read the values | EC-001 — fail honestly, retain original, offer retry and manual entry |

Deciding which stratum a document belongs to *after* seeing the engine's output would make the evaluation unfalsifiable. **The stratum is part of the ground truth.**

### 4.8 Property 7 — out-of-set documents

> **FR-OCR-002**: "...classify each document into a supported document type, **or as unrecognised**." — **REQUIRED**
> **AR-AST-002**: "...shall be able to return 'unrecognised' rather than a forced choice." — **REQUIRED**
> **EC-003**: "Classify honestly... If unclear, store as unclassified and ask. Never force it into an expected slot." — **REQUIRED**
> **§7.1**: "Any document outside the set is still stored and searchable, but its information is not extracted into the structured record." — **REQUIRED**

**REQUIRED corpus property:** documents outside the candidate type set must be present. A classifier evaluated only on in-set documents can score perfectly and still violate AR-AST-002 in production, because its ability to decline was never measured.

**RECOMMENDED** composition for this stratum — a classifier that never sees a near-miss is not tested on the case that matters:

- documents plainly outside the set (an unrelated letter, a utility bill if address proof is not resolved as a type);
- documents **adjacent** to the set — a document of a type the product will not support but that resembles one it does;
- documents of a supported type in a **presentation** the corpus otherwise lacks (a different issuing authority or state format).

### 4.9 Corpus quantities — all TBD

| Quantity | Value | Basis |
| --- | --- | --- |
| Total corpus size | **TBD** | No size stated anywhere in `backend/step3.pdf` |
| Per-document-type minimum | **TBD** | §7.1 requires every type to be evaluated; no minimum given |
| Per-degradation-condition minimum | **TBD** | "Imperfect" is undefined (D-02.i) |
| Number of persons in the person-grouped structure | **TBD** | FR-INF-004 requires the structure; no count given |
| Proportion of multi-page documents | **TBD** | FR-OCR-008 requires their presence; no proportion given |
| Proportion of expected-failure documents | **TBD** | EC-001 requires their presence; no proportion given |
| Proportion of out-of-set documents | **TBD** | AR-AST-002 requires their presence; no proportion given |
| Held-out / development split ratio | **TBD** | §6 — "held-out" is required; the ratio is not |

**These are deliberately unset.** Any of them could be given a defensible-sounding value; none of them can be given a *sourced* value, and a sourced value is the only kind this plan is permitted to state.

### 4.10 Corpus versioning

**RECOMMENDED.** The corpus carries a version identifier, and every evaluation result cites the corpus version it was produced against. Adding documents to a corpus after a result has been recorded, without a version change, silently invalidates the result. This matters because **G-03** guarantees the evaluation will be repeated.

---

## 5. Privacy and Consent

This section is dominated by a single finding, and it should not be softened: **the specification contains no requirement governing an evaluation corpus at all.** Every privacy requirement in `step3.pdf` concerns a *user's* documents held for the *user's* benefit. A corpus of real documents held for the team's benefit is a different activity, and the requirements do not reach it.

**REQUIREMENTS GAP — G-02.** Recorded in the decision register as: *"No requirement governs the collection, consent, retention, destruction, or team-readability of a real-document evaluation corpus."*

### 5.1 Why this is not a formality

AR-AST-008 requires **real** documents. Real documents of the kind §7.1 lists — Aadhaar, PAN, marksheets, address proofs — are exactly the material the rest of the specification treats as needing the strongest handling. Requiring their collection in one requirement while governing their handling in none is the gap. It cannot be closed by engineering judgement.

### 5.2 NFR-PRIV-002 — does it bind the team?

> **NFR-PRIV-002**: "A user's documents and extracted information shall not be used to train shared models, and shall not be readable by other users under any circumstance." — **REQUIRED**

Two halves, with different reach:

| Half | Reach | Consequence for D-02 |
| --- | --- | --- |
| "shall not be used to train shared models" | Unambiguous. **Binds this evaluation absolutely.** | Corpus documents may be used to *measure* a component. They may **not** be used to train, fine-tune, or otherwise fit one. See §5.4. |
| "shall not be readable by other users under any circumstance" | Binds *users* to *users*. Whether it binds the DOCURA team is **not stated**. | An evaluation corpus is by definition readable by the team. **REQUIREMENTS GAP — G-02.** |

**DECISION REQUIRED — privacy scope (D-02.c).** Whether NFR-PRIV-002's readability prohibition extends to the team must be settled explicitly by amendment, not by interpretation in a planning document. *Owner: PM + Legal.*

### 5.3 NFR-PRIV-001 — collection minimality

> **NFR-PRIV-001**: "The system shall collect only information required to deliver a function the user has requested." — **REQUIRED**

An evaluation corpus is not a function the contributor requested. Two readings exist, and they lead to different collection designs:

1. NFR-PRIV-001 governs the *product's* collection from its users, and corpus contribution is a separate, consented activity outside it.
2. NFR-PRIV-001 governs all collection, and corpus contribution must be constructed as a function the contributor requested.

**DECISION REQUIRED.** Reading (1) is the more natural fit with the requirement's wording, but the choice determines whether corpus contributors are "users" at all — which in turn determines whether NFR-PRIV-003's deletion obligation and NFR-SEC-003's authorisation obligation apply to them. *Owner: PM + Legal.*

### 5.4 The training prohibition is absolute

**REQUIRED.** Under NFR-PRIV-002, no corpus document and no value extracted from one may be used to train, fine-tune, adapt, or otherwise fit any model. This constrains the evaluation method itself:

- **Permitted:** measuring a candidate's output against ground truth; selecting a threshold from observed confidence distributions; selecting between candidates.
- **Not permitted:** fitting model weights; fine-tuning; building a template or layout model derived from corpus documents; any procedure whose output embeds corpus content.

**Boundary case — DECISION REQUIRED.** Confidence *calibration* (§12.2) fits a mapping from raw scores to calibrated scores using corpus outcomes. Whether that constitutes "training a shared model" under NFR-PRIV-002 is not settled by the specification. It fits parameters from user documents, but embeds no document content. **This must be settled before §12.2 is executed.** *Owner: PM + Legal.* Note that if calibration is permitted, the held-out discipline of §6 applies to it with full force: a calibration fitted on the held-out set and evaluated on the same set is not evidence.

### 5.5 NFR-PRIV-006 — disclosure of off-device processing

> **NFR-PRIV-006**: "Any processing performed outside the user's device shall be disclosed in plain language before the user's first upload." — **REQUIRED**

Bearing on D-02:

1. If a **candidate engine is externally hosted** (§13.4), evaluating it sends real documents to a third party. That is an act of disclosure to that party, and it happens during evaluation, before any product decision. It requires its own consent basis — a contributor consent covering "evaluation" does not self-evidently cover "transmission to a named third party".
2. **G-17** records that "processing" is undefined in NFR-PRIV-006, so whether the obligation was already triggered at Sprint 3 is unclear. That ambiguity carries into corpus collection.

**RECOMMENDED:** the consent text (§5.8) names every party that will receive the documents, including candidate engine vendors, or the corpus is restricted to self-hosted candidates. Whichever is chosen must be chosen **before** collection — retrofitting consent to cover a vendor added later is not consent.

### 5.6 Retention and destruction

> **NFR-PRIV-003**: "Deletion requested by the user shall remove the document, its extracted information, and its derived copies within a stated period. **Period: TBD — to be validated against legal requirements.**" — **REQUIRED**, with the period unset.

NFR-PRIV-003 governs *user* documents. It does not cover a corpus held for evaluation.

**REQUIREMENTS GAP — G-02.** The following must be specified and do not exist:

| Item | Status | Owner |
| --- | --- | --- |
| Corpus retention period | **REQUIREMENTS GAP** — no requirement exists; period **TBD** | PM + Legal |
| Retention justification | **REQUIREMENTS GAP** | PM + Legal |
| Destruction trigger | **REQUIREMENTS GAP** — D-02.f | PM + Legal |
| Destruction method | **REQUIREMENTS GAP** — D-02.f | PM + Legal + Engineering |
| Destruction verification and evidence | **REQUIREMENTS GAP** — D-02.f | PM + Legal |
| Contributor withdrawal path | **REQUIREMENTS GAP** — D-02.b | PM + Legal |

**Withdrawal interacts with reproducibility (§14).** If a contributor withdraws after a result has been recorded, the corpus version that produced the result no longer exists in full. The register must record the withdrawal, and the affected result must be marked as no longer reproducible — rather than the corpus being quietly re-versioned as if nothing happened. **DECISION REQUIRED.**

**Retention interacts with G-03.** A re-evaluation trigger implies the corpus outlives the first evaluation. A short retention period and a re-evaluation obligation are in direct tension, and the tension must be resolved deliberately.

### 5.7 Sensitivity classification cannot govern the corpus

> **FR-INF-007**: "Every attribute shall carry a sensitivity classification of routine, sensitive, or consequential." — **REQUIRED**

It would be natural to protect the corpus according to the sensitivity of what it contains. **That is not currently possible.**

**REQUIREMENTS GAP — G-14.** FR-INF-007 and FR-SENS-001 trace to "§02 Table 13.1", which the register records as an **ASM**-tagged *"WORKING SENSITIVITY CLASSIFICATION"* giving examples rather than rules, and explicitly qualified: *"This boundary must be set by users, not by us — it is assumption A-5."* §12.3 confirms A-5 is untested. **The rules do not exist in settled form.**

**G-15** adds that no default tier is specified for an attribute no rule covers, and **G-16** that document-level sensitivity — which is what a corpus actually holds — is undefined entirely.

**Consequence:** corpus protection cannot be derived from the sensitivity model. It must be set independently, and set high. **RECOMMENDED:** treat the entire corpus at the highest protection level the team can apply, on the ground that it contains identity documents, and revisit only once A-5 reports. This is a conservative default chosen because the specification offers no basis for a graduated one — it is not a claim that the graduated model is unnecessary.

### 5.8 Consent — what must exist before collection

**REQUIREMENTS GAP — G-02 / D-02.b.** No requirement covers evaluation consent. Before any real document is collected, the following must exist and be approved. **This plan does not draft them.**

| Element | Content required | Status |
| --- | --- | --- |
| Consent text | Plain language, per NFR-PRIV-006's standard for disclosure | **REQUIREMENTS GAP** |
| Purpose scope | Which evaluations the consent covers — this one only, or future re-evaluations under G-03 | **DECISION REQUIRED** |
| Recipient scope | Every party that will receive the documents, including any external candidate engine (§5.5) | **DECISION REQUIRED** |
| Access scope | Which roles inside the team may read corpus documents (§16.3) | **DECISION REQUIRED** |
| Retention period | How long the documents are kept, and why (§5.6) | **REQUIREMENTS GAP** |
| Withdrawal path | How a contributor withdraws, what happens to derived artefacts, and the effect on recorded results | **REQUIREMENTS GAP** |
| Training prohibition | An explicit statement that documents will not be used to train models, per NFR-PRIV-002 | **REQUIRED** by NFR-PRIV-002 |

### 5.9 Blocking statement

**Corpus collection cannot begin until §5.8 is complete.** Not because a process demands it, but because collecting real identity documents under a consent that has not been written is the failure this plan exists to prevent. Engineering can specify what the corpus must contain — §4 does — and cannot authorise its collection.

---

## 6. Development vs Held-Out Separation

> **AR-AST-008**: "...evaluated against a **held-out** corpus..." — **REQUIRED**

### 6.1 What "held out" obliges

The corpus used to *evaluate* must not be the material used to *build*. Concretely, held-out material may not be used to:

- choose or tune extraction parameters (thresholds internal to an engine, pre-processing settings, DPI or binarisation choices);
- design or refine field-location heuristics, templates, or per-type extraction configuration;
- write or refine prompts, if a candidate is prompt-driven;
- select between candidate engines by iterative inspection;
- calibrate confidence (§12.2), if calibration is permitted at all under §5.4.

A result produced from material that shaped any of the above is not evidence of anything except that the material shaped it.

### 6.2 The mechanism is not specified

**DECISION REQUIRED — D-02.g.** AR-AST-008 states the requirement; the specification does not say how separation is achieved, who may see the held-out set, or how leakage is prevented and evidenced. Three sub-decisions:

| Sub-decision | Options | Owner |
| --- | --- | --- |
| Is a separate development set collected at all? | (a) Yes — a distinct development corpus is collected alongside the held-out one; (b) No — development uses only synthetic or team-authored material, and the held-out corpus is the only real one | Engineering + PM |
| Who may see the held-out set? | (a) Nobody who works on extraction configuration; (b) An evaluation role distinct from the implementation role; (c) Anyone, with process discipline only | Engineering + PM |
| How is leakage evidenced? | Access logging, a sealed split, split-membership recorded before any engine is installed | Engineering |

### 6.3 RECOMMENDED separation model

**RECOMMENDED**, offered for approval rather than adopted:

1. **A development set is collected alongside the held-out set, from the same acquisition process and under the same consent**, and is subject to the same §5 and §16 controls. Its purpose is to make the held-out set genuinely untouched. If development can only proceed by looking at held-out documents, held-out status is lost on the first day.

2. **The split is fixed before any engine is installed**, recorded as part of the corpus version (§4.10), and never revised to improve a result. A split adjusted after seeing results is not a split.

3. **Split assignment is by person, not by document.** Because the corpus is person-grouped (§4.6), splitting by document would place two documents of the same person on both sides. The overlap would leak layout, issuing authority, and — for conflict detection — the very attribute values under test.

4. **The held-out set is used exactly once per candidate configuration.** Repeated evaluation against the held-out set while adjusting configuration between runs converts it into a development set by degrees. If iteration is needed, it happens on the development set.

5. **Every held-out run is recorded**: what was run, when, by whom, against which corpus version, with which engine version. This is the evidence that separation held — and §14 needs it regardless.

**Ratio: TBD.** No split ratio is proposed. The specification gives none, and the right ratio depends on a corpus size that is itself TBD.

### 6.4 A specific hazard: the type set is decided by this evaluation

§7.1 makes type inclusion conditional on the evaluation. That creates a direct route to leakage: an unfavourable per-type result invites re-running with adjusted configuration until the type passes. That process **selects on the held-out set** and destroys the evidence value of the entire evaluation, including for the types that passed the first time.

**RECOMMENDED:** the per-type pass criterion is fixed **before** the held-out run (§17.2), and a type that fails is demoted per §7.1 rather than retried. Re-running after configuration changes is permitted only as an explicitly recorded **new evaluation**, against a corpus version that has not been used for the previous run — which, given a finite corpus, may not be possible. That constraint is real, and it is why the criterion must be fixed first.

### 6.5 Held-out status and re-evaluation

**REQUIREMENTS GAP — G-03.** AR-AST-008 is silent on what happens when an assisted component changes version. A held-out set is held out *once*. After the first evaluation, the team has seen its results; a second evaluation of a new engine version against the same corpus is weaker evidence than the first, and this weakening is never acknowledged in the specification.

**DECISION REQUIRED.** Whether re-evaluation reuses the corpus (accepting degraded independence, stated as a limitation) or requires fresh material (accepting recurring collection cost and a recurring consent obligation). *Owner: PM.* This decision has a direct cost consequence and should not be deferred to the moment an engine upgrade is proposed.

---

## 7. Ground Truth

Ground truth is what an evaluation compares against. Without it there are outputs but no measurements. This section defines what must be annotated, and records honestly which parts cannot be annotated yet.

### 7.1 Ground truth layers

| Layer | What is annotated | Supports | Blocked by |
| --- | --- | --- | --- |
| **L1 — Document metadata** | Capture method, degradation conditions present (§4.4), page count, legibility stratum (§4.7), person group (§4.6) | Stratified reporting throughout | Degradation taxonomy is **DECISION REQUIRED** (D-02.i) |
| **L2 — Type label** | The true document type, or "out of set" | §10 classification | Type-set definition issues **G-09**, **G-10** |
| **L3 — Text transcription** | The document's readable text content | §8 OCR quality | Transcription convention is **DECISION REQUIRED** (§7.3) |
| **L4 — Field values** | The correct value of each defined field for the type | §11 field extraction | **G-12 — no field definitions exist** |
| **L5 — Field regions** | Where on the page each field value appears | §9 source regions, FR-OCR-007 | **G-12** |
| **L6 — Canonical attributes** | Which canonical attribute each field value maps to, per person | §11.6 conflict detection | **G-13 — no attribute vocabulary exists** |
| **L7 — Conflict inventory** | Which attributes disagree within a person's document set, and how | §11.6, FR-INF-004 | **G-13** |

**L1, L2, and L3 are annotatable today.** **L4 through L7 are not** — not for want of effort, but because the specification does not define what a field is for any type (G-12) or what attributes exist (G-13).

### 7.2 Ground truth attaches to configuration, not code

> **NFR-MNT-001**: "Supported document types and their extractable fields shall be definable as configuration, so adding a type does not require re-engineering." — **REQUIRED**

**RECOMMENDED:** L4 ground truth is expressed against the **configured field set** identified by version, not against an implicit list held in the annotation tool or in an annotator's head. When the field set changes, existing annotations must be re-validated against the new version rather than silently reinterpreted. Ground truth that does not name the field-set version it was authored against will not survive the first field-definition revision.

### 7.3 Transcription conventions — DECISION REQUIRED

L3 requires conventions decided before annotation begins, because they change the measured error rate without changing any engine behaviour:

| Convention | Question | Status |
| --- | --- | --- |
| Reading order | Multi-column and tabular layouts — is a column-major transcription "correct"? | **DECISION REQUIRED** |
| Whitespace | Is line-break and spacing structure part of the truth, or normalised away before comparison? | **DECISION REQUIRED** |
| Case | Is case preserved in the transcription, or folded before comparison? | **DECISION REQUIRED** |
| Illegible spans | How is "a human cannot read this" recorded, and is it excluded from the denominator? | **DECISION REQUIRED** |
| Non-text content | Are stamps, seals, logos, photographs, and signature images transcribed, described, or excluded? | **DECISION REQUIRED** |
| Script and language | How is mixed-script content transcribed? Note FR-OCR-012 defers non-MVP scripts, but the **MVP set itself is "TBD — to be validated against a real document corpus (study S-6)"** — this evaluation must therefore record what scripts the corpus actually contains | **TBD**, per FR-OCR-012 |

The last row deserves emphasis: **FR-OCR-012 makes the MVP language and script set an output of this evaluation**, not an input. The corpus records what it contains; the evaluation reports per-script results; the MVP set is set afterwards.

### 7.4 Region ground truth

**FR-OCR-007** (SHOULD) requires each value to be shown alongside the region it was read from. To evaluate it, L5 must record where each value is.

**RECOMMENDED:** regions are annotated in the same coordinate system the extraction port already uses — **page-relative fractional coordinates** (`page`, `x`, `y`, `width`, `height`), as implemented in D-01's `TextRegion`. The reason is stated in the D-01 architecture: an engine reading a 200-DPI scan and one reading a PDF text layer do not agree on a pixel, but they do agree on "a third of the way down the page". Annotating in pixels would make two candidates' region output incomparable, which defeats §13.

**Region correctness criterion — DECISION REQUIRED.** Whether a predicted region is "correct" needs a rule: containment of the true region, overlap above some fraction, or centre-point containment. The rule affects the score and no rule is specified. **No overlap value is proposed here.** See §9.3.

### 7.5 Normalisation and the ground-truth comparison

> **FR-INF-008**: "The system shall normalise attribute formats deterministically — dates, casing, spacing, and numeric precision — without altering meaning." — **REQUIRED**

A comparison of extracted values against ground truth must state whether it compares **raw** or **normalised** values, and it must be both:

| Comparison | What it measures | Why both are needed |
| --- | --- | --- |
| Raw extracted value vs raw ground truth | What the engine actually read | Isolates extraction error from normalisation error |
| Normalised extracted value vs normalised ground truth | What the record would contain | This is what FR-INF-004 conflict detection actually compares |

**A date read as `01/02/2019` and truth `1 Feb 2019` is an extraction success and a normalisation question, not an extraction failure.** Conflating them attributes normalisation defects to the engine and would corrupt engine selection.

**Blocked:** per-attribute normalisation rules belong to the canonical attribute vocabulary, which does not exist (**G-13**). Normalisation can be evaluated for *determinism* (same input, same output, across runs) today; it cannot be evaluated for *correctness* until the rules exist.

### 7.6 Annotation quality

Ground truth annotated once by one person is an opinion. Since it is the standard against which BR-001's threshold will be set, its own reliability matters.

**RECOMMENDED:**

1. **Double annotation with adjudication** on a subset — proportion **TBD** — with inter-annotator agreement reported in the evaluation output (§14.3). If annotators disagree materially, the ground truth is not yet a standard and no threshold derived from it is trustworthy.
2. **The legibility stratum (§4.7) is annotated blind to engine output.** This is the single most important annotation discipline in the plan: deciding EC-001 vs EC-002 after seeing whether the engine succeeded makes the failure-path evaluation circular.
3. **Annotator access is corpus access** and falls entirely under §5 and §16. Annotation is the activity that most widens the set of people who read real identity documents, and it must be scoped deliberately rather than staffed opportunistically.

### 7.7 Ground truth status summary

| Layer | Can be produced today? |
| --- | --- |
| L1 Document metadata | **Yes**, once the degradation taxonomy is approved |
| L2 Type label | **Yes**, with G-09 / G-10 caveats recorded per document |
| L3 Text transcription | **Yes**, once transcription conventions are decided |
| L4 Field values | **No — blocked on G-12** |
| L5 Field regions | **No — blocked on G-12** |
| L6 Canonical attributes | **No — blocked on G-13** |
| L7 Conflict inventory | **No — blocked on G-13** |

---

## 8. OCR Evaluation

Evaluates **FR-OCR-001** and, jointly with §4.5, **FR-OCR-008**. This is the layer that is fully evaluable against L3 ground truth without any of the blocked requirements — it is the part of the evaluation that can proceed first.

### 8.1 What is being measured

> **FR-OCR-001**: "The system shall extract machine-readable text from each uploaded document." — **REQUIRED**

FR-OCR-001 states an obligation with no quality bar. The quality bar arrives indirectly, through §7.1's demotion rule and through BR-002's confidence floor. So §8 measures text quality not to pass or fail it in isolation, but to explain §11's field-extraction results: a field that cannot be extracted because the text under it was never read is a different defect from a field that was read and mislocated.

### 8.2 Metrics — RECOMMENDED

The specification names no metric. The following are standard and are proposed as method, not requirement. **No target value is attached to any of them** — targets would be thresholds, and AR-AST-008 forbids setting thresholds before evaluation.

| Metric | Definition | Why it is included |
| --- | --- | --- |
| **Character error rate (CER)** | Character-level edit distance between output and L3 transcription, normalised by transcription length | The primary text-quality measure; insensitive to tokenisation disputes |
| **Word error rate (WER)** | Word-level edit distance, normalised by transcription word count | Closer to how a field value fails; a single wrong character can destroy a field |
| **Per-page coverage** | Fraction of pages producing any text at all | Distinguishes "read badly" from "not read" — the EC-001 / EC-002 boundary |
| **Numeric-span accuracy** | Exact-match rate on digit sequences | **RECOMMENDED** and specifically motivated: identifiers, marks, and dates are the values the product's document types are full of, and character-level averages hide digit errors |
| **Structural preservation** | Whether tabular content retains row/column association | Marksheets are tables; a correct character stream in the wrong order is unusable for field extraction |

### 8.3 Stratified reporting — REQUIRED by the corpus design

A single aggregate CER across the corpus is close to useless for the decisions this evaluation must inform. Results must be reported broken down by:

| Stratum | Why the breakdown is decision-relevant |
| --- | --- |
| Document type | §7.1's demotion rule operates per type |
| Degradation condition (§4.4) | Identifies which real-world conditions break extraction — the actionable output |
| Capture method | Distinguishes "phone photographs fail" from "extraction fails" |
| Page position within document | Reveals whether later pages degrade (§8.5) |
| Script and language | FR-OCR-012 makes the MVP script set an output of this study (§7.3) |

An aggregate number that averages a clean PDF export with a shadowed phone photograph describes neither.

### 8.4 What good text quality does not prove

**Stated deliberately.** A low CER does not establish that field extraction will succeed, and a candidate must not be selected on CER alone:

- Fields can be read correctly and located wrongly (§9).
- Fields can be read correctly and classified as the wrong field (§11).
- **A candidate with excellent text quality and no usable per-value confidence is ineligible under AR-AST-001**, however it scores (§13.2).

### 8.5 Multi-page handling

> **FR-OCR-008**: "The system shall process multi-page documents as a single document." — **REQUIRED**
> **AC-US-003-4**: "...THEN it is stored as one document and information from every page is available." — **REQUIRED**

Checks — pass/fail on requirement conformance, not scored:

| Check | Requirement |
| --- | --- |
| One document in, one result out — never one result per page | FR-OCR-008 |
| Every page is represented in the result, in order | AC-US-003-4 |
| Page numbering in the result matches the source document | FR-OCR-007, AR-AST-006 — a region is meaningless without a correct page number |
| A value present only on a later page is recoverable | AC-US-003-4, §4.5 |
| Mixed page orientation within one document is handled | §4.4 degradation taxonomy |

### 8.6 Processing observations — recorded, not scored

Per-document processing time is **recorded** as a corpus-conditioned observation. It is **not scored**, because:

- **NFR-PERF-002** requires processing to be asynchronous, so latency does not block the user;
- **NFR-PERF-001** and **NFR-PERF-003** carry targets marked TBD, and §15 of the specification states they cannot be fully tested until study S-2 measures a manual baseline.

Recording it now means the S-2 comparison has data when it needs it, without this evaluation inventing a performance bar.

---

## 9. Source Region Evaluation

> **FR-OCR-007** (MVP, SHOULD): "The system shall show each extracted value alongside the region of the source document it was read from."
> **AR-AST-006** (MVP): "Every assisted output shall be explainable to the user in terms of the source it came from."
> **AC-US-004-1**: "GIVEN a processed document, WHEN the user opens an extracted value, THEN the source document and the region the value was read from are shown."

### 9.1 Why a SHOULD gets its own evaluation section

FR-OCR-007 is priority SHOULD, but the capability it depends on is not optional:

- **AR-AST-006 is a MUST-equivalent architectural requirement** and applies to every assisted output.
- **FR-INF-002 is MUST**: "Every attribute value shall reference the document it came from and the confidence with which it was read."
- §12.2 of the specification names traceability as the reason the product works at all: *"Without it, a careful user re-verifies everything and the time saving disappears (N-05). Traceability is what converts speed into trust."*

An engine that cannot produce region information may still satisfy FR-INF-002 at document granularity, but it forecloses FR-OCR-007 and weakens AR-AST-006 permanently. **That is an engine-selection consequence (§13.2), which is why it is measured here rather than deferred to a later sprint.**

### 9.2 What is measured

| Measure | Against | Status |
| --- | --- | --- |
| **Region availability** | Does the candidate emit a region for each text unit at all? | **Evaluable now** — a candidate property, no ground truth needed |
| **Text-block region accuracy** | L5-style annotation at text-block granularity vs predicted block regions | **Evaluable once L3/L5 block annotation exists** |
| **Field region accuracy** | Predicted region for an extracted field vs the true region of that field's value | **NOT EVALUABLE — blocked on G-12** |
| **Page attribution** | Is the region on the correct page? | **Evaluable now** — a region on the wrong page is worse than no region, because it presents false provenance |
| **Coordinate stability** | Do regions remain correct under skew and rotation? | **Evaluable once corpus exists** — the degraded strata are where region output is most likely to drift |

### 9.3 Correctness criterion — DECISION REQUIRED

The specification does not define when a region is "correct". Candidate rules:

| Rule | Consequence |
| --- | --- |
| Predicted region contains the true region | Tolerant; a region covering the whole page would pass, so it needs an area bound |
| Overlap ratio above a stated fraction | Standard, but requires a fraction — **and no fraction is proposed here**, because it would be an invented threshold |
| Centre of the true region falls inside the predicted region | Simple and reasonably robust to boundary conventions |

**DECISION REQUIRED.** The rule must be fixed before the held-out run (§6.4), not chosen after seeing which rule flatters a candidate. *Owner: Engineering proposes, PM approves.*

### 9.4 The user-facing criterion

**RECOMMENDED.** Region accuracy has a purpose beyond a score: FR-OCR-007 exists so a user can look at the document and see where a value came from. A region that is numerically close but points a user at the wrong line has failed the requirement while passing the metric.

The proposal is a **qualitative check** alongside the quantitative one: on a sample (size **TBD**), does the highlighted region let a human find the value without searching? This is a judgement, reported as a judgement — not converted into a number that would imply a precision it does not have.

### 9.5 Provenance completeness

**REQUIRED by FR-INF-002 and AR-AST-006.** Independent of accuracy, a completeness check: is there any extracted value that lacks a document reference, a page, or a confidence?

Any such value is a **conformance failure, not a scoring input**. FR-INF-002 admits no exception, and D-01's `ExtractionResult` type is structured so that an engine unable to supply these is visibly non-compliant rather than quietly accommodated.

**Blocked at field level on G-12.** At page and text-block level, evaluable now.

---

## 10. Document Classification Evaluation

> **FR-OCR-002**: "The system shall classify each document into a supported document type, **or as unrecognised**." — **REQUIRED**
> **FR-OCR-003**: "The system shall record a confidence value for the classification." — **REQUIRED**
> **AR-AST-002**: "Document classification shall produce a type and a confidence, and shall be able to return 'unrecognised' rather than a forced choice." — **REQUIRED**
> **EC-003**: "Classify honestly... Never force it into an expected slot." — **REQUIRED**
> **AC-US-003-3**: "GIVEN a document whose type cannot be determined confidently... THEN it is stored as unclassified, the user is asked to identify it, and no type is assumed." — **REQUIRED**

### 10.1 The unrecognised class is a first-class outcome

The single most important property of this section: **"unrecognised" is a correct answer, not a failure.** An evaluation that treats every unrecognised output as an error would select for exactly the forced-choice behaviour EC-003 and AR-AST-002 prohibit.

Every measure below therefore treats unrecognised as its own class, on both the truth axis and the prediction axis.

### 10.2 Measures — RECOMMENDED

| Measure | Definition |
| --- | --- |
| **Confusion matrix over candidate types plus unrecognised** | Rows = true label (§7.1 types, or out-of-set); columns = predicted (types, or unrecognised) |
| **Per-type recall** | Of documents truly of type T, the fraction classified as T |
| **Per-type precision** | Of documents classified as T, the fraction truly of type T |
| **Misclassification rate between types** | Wrong-type assignment — the most damaging outcome, because §7.1 attaches field extraction to type |
| **Forced-classification rate** | Of out-of-set documents, the fraction assigned a type instead of unrecognised — the direct AR-AST-002 / EC-003 measure |
| **Abstention rate on in-set documents** | Of in-set documents, the fraction returned unrecognised — the cost of caution, reported alongside the benefit |

**No target value is attached to any of these.** Targets are thresholds; AR-AST-008 forbids setting them first.

### 10.3 Asymmetry of errors — RECOMMENDED

Three outcomes carry unequal cost under the specification, and the evaluation must report them separately rather than folded into one accuracy figure:

| Outcome | Product consequence | Governing requirement |
| --- | --- | --- |
| Correct type | Field extraction runs against the right field set | FR-OCR-004 |
| Unrecognised, when a type existed | Document stored and searchable; the user is asked; no wrong data enters the record | §7.1, AC-US-003-3, BR-016 |
| **Wrong type** | **Field extraction runs against the wrong field set; wrong values may enter the record with a document-level confidence that appears sound** | Violates the spirit of BR-016 |

**Wrong-type classification is the worst outcome available to this component**, and a candidate whose accuracy comes from rarely abstaining should be visibly penalised by this reporting, not rewarded by an aggregate score.

### 10.4 Honest abstention

Measured over the out-of-set stratum (§4.8):

| Check | Requirement |
| --- | --- |
| An out-of-set document is returned as unrecognised, not forced into a type | AR-AST-002, EC-003 |
| A near-miss document — adjacent to a supported type — is returned unrecognised | AR-AST-002 |
| An unrecognised result still carries a confidence | FR-OCR-003 — the requirement admits no exception for the unrecognised outcome |
| The result state is distinguishable from a processing failure | EC-001 vs EC-003 are different behaviours with different user paths |

### 10.5 Classification confidence

**FR-OCR-003** requires a confidence for the classification. **FR-OCR-005** requires field confidences to be recorded *independently* of the document-level confidence — so this evaluation must confirm the two are genuinely separate signals and not the same number surfaced twice.

**REQUIREMENTS GAP — G-05.** Which threshold governs classification is never stated. AC-US-003-3's phrase "cannot be determined **confidently**" implies a threshold on classification confidence, but the specification defines only the review threshold (fields) and the automatic-action threshold (actions), and never says which — if either — applies to a classification decision.

**Consequence for this plan:** §12 sweeps classification confidence and reports the resulting behaviour, but **cannot select a classification threshold** until G-05 is closed.

### 10.6 Interaction with the unresolved type set

Three type-definition gaps (§4.3) affect the confusion matrix directly, and must be recorded per document at annotation time rather than resolved by the annotator:

- **G-09** — "address proof" is a category; documents provisionally in it may need to be reported separately by underlying document kind, or the row is uninterpretable.
- **G-10** — "semester result" and "semester marksheet" may be one class or two. Reporting them merged and unmerged, and letting the decision follow the evidence, is **RECOMMENDED**.
- **G-11** — photograph and signature may be classification-only types. They still appear in the matrix; they simply have no §11 row.

---

## 11. Field Extraction Evaluation

### 11.1 Blocking statement — read this first

> **FR-OCR-004**: "For each supported document type, the system shall extract **the defined set of information fields** for that type." — **REQUIRED**

**REQUIREMENTS GAP — G-12: no field definitions exist for any document type in `backend/step3.pdf`.** The register records the result of a complete search: the specification defines the *obligation* to extract a defined field set, and the *mechanism* by which field sets are maintained (NFR-MNT-001, configuration), but never states the sets, and never points to a document that does.

**REQUIREMENTS GAP — G-13: the canonical attribute vocabulary does not exist.** FR-ACC-004 names "canonical personal attributes"; no section enumerates them.

**Therefore: §11 cannot be executed today.** Not partially, not approximately. There is no defined set to extract, so there is nothing to measure recall against and nothing to measure precision against. This is an absence in the requirements, not a difficulty of engineering.

**No fields are invented in this document.** The nearest field-like nouns anywhere in the specification are FR-INF-008's normalisation *categories* ("dates, casing, spacing, and numeric precision") and document 02's ASM-tagged sensitivity examples — the register is explicit that the latter "is a list of sensitivity examples, not a field definition, and must not be promoted into one."

**What follows is the method that becomes executable the day G-12 and G-13 close.** It is specified now so that the evaluation is not designed under time pressure later, and so the cost of those gaps is visible.

### 11.2 Prerequisites

| Prerequisite | Content | Owner | Status |
| --- | --- | --- | --- |
| Canonical attribute vocabulary | Attribute name, meaning, value type, normalisation rule, sensitivity tier | PM owns content, Engineering owns format | **REQUIREMENTS GAP — G-13** |
| Per-type field sets | For each type: field name, mandatory or optional, format, and the canonical attribute it maps to — or explicitly none | PM owns content | **REQUIREMENTS GAP — G-12** |
| Type set resolution | G-09 (address proof), G-10 (semester result naming), G-11 (photograph / signature extraction scope) | PM | **DECISION REQUIRED** |
| L4–L7 ground truth | §7.1 layers, annotated against a named field-set version | Engineering + annotators | Blocked on the above |

The register's D-05.5 ordering applies and is not negotiable: **the vocabulary first, then the per-type field sets** — because field sets map into the vocabulary, and a vocabulary derived after the fact from whatever fields were listed would not serve FR-INF-004.

Its third recommendation bears directly on this evaluation: *"Do not derive the vocabulary from whatever the chosen engine happens to return."* Doing so would invert §6's Selection Principle, make the vocabulary a property of the engine, and turn a later engine change into a data migration.

### 11.3 Measures — RECOMMENDED, once unblocked

| Measure | Definition | Requirement |
| --- | --- | --- |
| **Per-field recall** | Of documents where field F is truly present, the fraction where a value was extracted | FR-OCR-004 |
| **Per-field precision** | Of extractions of field F, the fraction whose value matches ground truth | FR-OCR-004 |
| **Exact-match rate** | Value identical to ground truth after the stated normalisation (§7.5) | FR-OCR-004, FR-INF-008 |
| **Near-miss rate** | Value differing by a small edit distance — separated because a one-character error in an identifier is a *silent* error, the most dangerous class | NFR-OBS-003's concern, applied pre-release |
| **Wrong-field rate** | A correct value assigned to the wrong field | FR-OCR-004 |
| **Absent-field behaviour** | For a field genuinely absent from the document, is nothing returned rather than something plausible? | BR-003, BR-016 |
| **Per-type field-set completeness** | Of the defined field set for type T, the fraction extractable at all | §7.1's demotion rule operates on this |

Reported stratified by document type, by degradation condition, and by field — for the same reason as §8.3: §7.1's decision is per type, and remediation is per condition.

### 11.4 Confidence independence — REQUIRED

> **FR-OCR-005**: "The system shall record a confidence value for every extracted field **independently of the document-level confidence**." — **REQUIRED**

A conformance check, not a score: are field confidences genuinely per-field, or is a document-level score repeated across every field? If the latter, the candidate does not satisfy FR-OCR-005, and BR-001's requirement that "the confidence of both the field interpretation and the source value" meet the threshold cannot be evaluated for that candidate at all.

**AC-US-003-2** depends on the same property: "every extracted field is shown with its own confidence indication."

### 11.5 Raw and normalised comparison

Per §7.5, both comparisons are reported. A value correctly read but incorrectly normalised is a **normalisation defect** (FR-INF-008), not an extraction defect, and must not count against engine selection. Conflating the two would attribute DOCURA's own deterministic-code defects to the candidate.

### 11.6 Conflict detection

> **FR-INF-004** (MUST): "The system shall detect when two documents give different values for the same attribute."
> **AR-DET-008**: "Conflict detection between documents shall be deterministic; conflict resolution shall never be automated at all."
> **AC-US-005-1**: "...a conflict is raised and neither value is marked authoritative."

Evaluated over the person-grouped corpus (§4.6) against the L7 conflict inventory:

| Measure | Definition |
| --- | --- |
| **Conflict recall** | Of known disagreements, the fraction detected |
| **Conflict precision** | Of raised conflicts, the fraction that are real disagreements |
| **False-conflict source attribution** | For each false conflict, its cause under a **four-way** taxonomy: extraction error, normalisation, **scope-model error (scope collapse)**, or genuine document variance (§11.6.1) |

That last row is the one that makes this section worth running. Detection is deterministic under AR-DET-008 — it cannot be "improved" by choosing a better engine. So **a false conflict is always evidence about extraction, normalisation, or the scope model** (§11.6.1), and the attribution is what turns a conflict-detection result into an actionable finding. A system that raises conflicts on every person because extraction transcribes names inconsistently satisfies FR-INF-004 literally while making the product unusable, and only this measure exposes that.

#### 11.6.1 The fourth attribution category — scope-model error (scope collapse)

*Added to close G-13 exit criterion **X15**; the analysis is at [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§11.4.1**. This section applies that recorded analysis and introduces no new evaluation methodology.*

The three-way premise above is incomplete. **Scope collapse** is a fourth, distinct cause: two values describing **different scope instances of the attribute's subject** are compared because they share one canonical-attribute identifier, and a conflict is raised although extraction was correct, normalisation was correct, and the documents disagree about nothing — the worked case being three documents reporting the year of passing of three different qualifications. Under the original three-way taxonomy every such instance would be filed as *genuine document variance* — the category that reads *no action needed* — so the gap would **silently disarm the measure built to detect it** (G-13 §11.4.1). The consequence is quoted requirement-by-requirement at G-13 §11.4.1 (FR-INF-004 → AR-DET-008 → FR-INF-005 → BR-004 → EC-004 → FR-AMB-001 → FR-INF-006): the product's only conflict-clearing path would demote correct data.

**How it is told apart, without new methodology.** Each false conflict is already attributed against the L6/L7 ground truth (§7: L6 = canonical attribute per person; L7 = conflict inventory). A false conflict is **scope-model error** when its two values map to the **same canonical attribute but different scope instances of its subject** under the attribute's scope-keyed cardinality (**G-13.2** property 6), and **genuine document variance** only when they share one scope instance. Distinguishing them therefore requires L6/L7 to record the **scope instance**, not only the attribute — an obligation that binds when the first non-`person` (e.g. `qualification`) attribute enters the vocabulary, and that follows the scope-instance derivation deferred by **PD-D**. For the approved `v0.1-draft`, whose only attribute is `person`-scoped in a single-person record (**FR-ACC-003**), scope collapse cannot arise, so no additional annotation is owed to design the measure against that subject.

**Designable at gate A (X15 met); execution still blocked on the G-13 contents.** With the four-category taxonomy complete (§11.6.1) and the approved `v0.1-draft` a real subject to design against, this measure is now designable — G-13 exit criterion **X15** is satisfied. *Executing* it — recall/precision over a real person-grouped corpus — still requires the vocabulary's contents to grow and G-12's field→attribute mapping, both beyond gate A; attribute identity across documents is what those define.

### 11.7 Fields that must not be extracted

**DECISION REQUIRED, safety-relevant.** The register's D-05.3 raises, for Aadhaar, "whether the identifier number is stored at all, masked, or stored in part". That question is not settled, and it is a *field-definition* decision with a privacy consequence.

Until it is settled, **the evaluation must not assume that every readable value is a value to be extracted.** Ground truth annotation (§7) will necessarily record such values; §16 governs their handling; and the field-set definition decides whether the product extracts them at all. These are three separate decisions and this plan does not merge them.

---

## 12. Confidence Calibration

### 12.1 What the specification requires and does not define

| ID | Text | Status |
| --- | --- | --- |
| **BR-001** | "...meets or exceeds the automatic-action threshold. **Threshold value: TBD — to be validated (study S-6).**" | Value **TBD** — this evaluation's primary output |
| **BR-002** | "Information extracted below the review threshold is never used for automatic action, regardless of how well it matches a field." | Rule stated; **value undefined** |
| **FR-OCR-006** | "Extracted fields below the review threshold shall be marked as needing user review and shall not be used for automatic filling." | Behaviour stated; **value undefined** |
| **AR-AST-001** | Confidence must be "usable by BR-001" | "Usable" undefined |
| **NFR-MNT-002** | "Confidence thresholds shall be externally configurable and changeable without a code release." | **REQUIRED** — constrains how the output is delivered |

Four gaps from the register bear directly on this section:

| Gap | Content |
| --- | --- |
| **G-04** | Neither threshold has a value. BR-001 is explicitly TBD; **the review threshold carries no value and no TBD marker anywhere** — it is simply undefined. |
| **G-05** | The relationship between the two thresholds is never stated. BR-002's logic implies review ≤ automatic, "but implication is not specification." Nor is it stated which governs classification (§10.5). |
| **G-06** | Confidence has **no defined scale, semantics, or cross-component comparability** — not a range, not whether it is a probability, not whether classifier and field confidences share a scale, not whether two engines' confidences are comparable. |
| **G-07** | Global vs per-document-type thresholds is unaddressed. |

**G-06 is the deepest of these.** BR-001 compares two confidences — "the confidence of both the field interpretation and the source value" — against one threshold. That comparison presumes a shared, stable meaning the specification never defines. **Until G-06 is closed, BR-001 is untestable as written**, and the register says so.

### 12.2 Calibration measurement — RECOMMENDED

A confidence is *useful* to BR-001 only if it predicts correctness. High confidence that is frequently wrong is worse than no confidence at all, because BR-001 acts on it.

| Measure | What it shows |
| --- | --- |
| **Confidence distribution** by outcome | Do correct and incorrect extractions occupy different confidence ranges at all? If they overlap completely, no threshold can separate them and the candidate is unusable under BR-001 regardless of accuracy. |
| **Reliability curve** (observed accuracy vs stated confidence, binned) | Whether stated confidence corresponds to observed correctness |
| **Accuracy above / below a swept threshold** | The direct input to threshold selection (§12.4) |
| **Per-type and per-condition calibration** | Whether one global threshold can serve all types — the evidence G-07 needs |
| **Cross-component comparability** | Whether classification confidence and field confidence mean the same thing — the evidence G-06 needs |

**NFR-OBS-001** requires the production system to "measure extraction and field-interpretation confidence distributions in aggregate, without retaining the underlying values." The evaluation harness measures the same distributions with ground truth available — and the aggregate form is what may be retained in the report (§14.4).

**Note the §5.4 boundary:** whether *fitting* a calibration mapping is permitted under NFR-PRIV-002 is **DECISION REQUIRED**. *Measuring* calibration is unambiguously permitted.

### 12.3 Threshold selection method — RECOMMENDED

**No threshold value is proposed in this document.** The method is:

1. Sweep the candidate threshold across its full range.
2. At each point, report — separately, never blended into one score:
   - fields that would be auto-filled and are correct (correct automatic action);
   - **fields that would be auto-filled and are wrong (silent error)**;
   - fields that would be marked for review and are wrong (correct caution);
   - fields that would be marked for review and are correct (unnecessary interruption).
3. Report the same sweep **per document type**, so §7.1's per-type demotion rule can be applied on evidence, and so G-07 has data.
4. Present the trade-off to PM. **The number is a product risk decision informed by evidence, not an engineering output.** The register assigns G-04 that way, and this plan does not take it back.

### 12.4 The asymmetry is not negotiable

**REQUIRED by BR-002 and BR-016.** The four outcomes above are not equally costly, and the specification is explicit about which way to err:

> **BR-016** (as summarised in §14 of the specification): "fail towards inaction and tell the user."
> **US-010**: "I want DOCURA to ask me when it is not sure rather than pick something plausible, **so that a confident mistake never gets past me into a submitted application**."
> **EC-002**: "Never present a low-confidence value as settled."
> **AC-US-004-4**: "GIVEN an extracted value below the review threshold, WHEN the record is used for filling, THEN that value is never placed automatically."

**A silent error — an incorrect value auto-filled with high confidence — is the failure mode the entire product philosophy exists to prevent.** An unnecessary interruption is a cost. They are not interchangeable, and any threshold-selection procedure that optimises a single blended accuracy figure has silently traded the first against the second.

**RECOMMENDED:** the evaluation report presents the trade-off curve and never recommends a single "optimal" number. The choice is PM's, on evidence.

### 12.5 AR-AST-007 constrains post-processing

> **AR-AST-007**: "No assisted component shall be permitted to escalate its own authority — it may lower a confidence, never raise it, and may add a sensitivity classification, never remove one." — **REQUIRED**

Any calibration or post-processing applied between the engine and the threshold check must be audited against this. A calibration that **raises** a confidence — even one that is statistically better justified — violates AR-AST-007 as written.

**DECISION REQUIRED.** Whether AR-AST-007 constrains a calibration mapping applied by DOCURA (as opposed to a component raising its own confidence) is a genuine ambiguity in the requirement. It must be settled before any calibration is applied, because a downward-only calibration and a free calibration produce different thresholds. *Owner: PM + Engineering.*

### 12.6 The output is configuration

> **NFR-MNT-002**: "Confidence thresholds shall be externally configurable and changeable without a code release." — **REQUIRED**

The evaluation's numeric output is delivered as **configuration values with a recorded derivation**, not as constants in code. The derivation record must name the corpus version, the engine, the engine version, and the date — because **G-03** means the derivation will be revisited.

**Note:** D-01 deliberately implemented confidence as a value that is *carried* and *compared nowhere*. No threshold comparison exists in the codebase, and none should be added before this evaluation supplies the number.

### 12.7 Status

| Item | Status |
| --- | --- |
| Automatic-action threshold value | **TBD** — BR-001, output of this evaluation |
| Review threshold value | **TBD** — **G-04**, and it lacks even a TBD marker in the specification |
| Relationship between the two | **REQUIREMENTS GAP — G-05** |
| Confidence scale and semantics | **REQUIREMENTS GAP — G-06** — makes BR-001 untestable as written |
| Global vs per-type thresholds | **REQUIREMENTS GAP — G-07** |
| Which threshold governs classification | **REQUIREMENTS GAP — G-05** |
| Whether calibration is permitted under NFR-PRIV-002 | **DECISION REQUIRED** — §5.4 |
| Whether AR-AST-007 constrains DOCURA-side calibration | **DECISION REQUIRED** — §12.5 |

---

## 13. Candidate Engine Comparison

### 13.1 No engine is named in this document

**TBD — pending this evaluation.** D-01 selected a self-hosted architecture behind a replaceable interface and deliberately did **not** select an engine, because §6's Selection Principle assigns technology selection to document 04 and AR-AST-008 requires evidence first.

The register's D-01.5 recommendation is that the evaluation should compare **at least one self-hosted candidate and at least one external candidate**, and record the outcome in Step 4 per §6. That recommendation stands and is not resolved here.

### 13.2 Eligibility gates — REQUIRED, applied before scoring

A candidate that fails any gate below is **ineligible**, and is not scored. Scoring an ineligible candidate invites a later argument that its accuracy should outweigh a requirement it cannot meet.

| Gate | Requirement | Test |
| --- | --- | --- |
| Produces a **per-value confidence** | **AR-AST-001** — "for each extracted value, a confidence measure usable by BR-001" | Inspect output; a document-level score repeated per value fails **FR-OCR-005** (§11.4) |
| Can return **nothing** rather than a forced answer | **AR-AST-002**, **BR-003** | Out-of-set stratum (§10.4) |
| Supplies **provenance** sufficient to explain a value by its source | **AR-AST-006**, **FR-OCR-007**, **FR-INF-002** | Region availability and page attribution (§9.2) |
| Handles **multi-page documents as one document** | **FR-OCR-008** | §8.5 |
| Does not **raise** its own confidence or remove a sensitivity tier | **AR-AST-007** | Behavioural audit (§12.5) |
| Operates **within DOCURA's own infrastructure**, or its externality is disclosed and consented | **D-01**, **NFR-PRIV-006** | §13.4 |
| Does not require **training on user documents** | **NFR-PRIV-002** | Vendor terms and integration review |

**An engine that is accurate but cannot produce a meaningful confidence is not eligible, however well it scores.** This is stated in D-01 and restated here because it is the gate most likely to be argued away when a high-accuracy candidate fails it.

### 13.3 Comparison conditions — REQUIRED for a comparison to mean anything

| Condition | Why |
| --- | --- |
| Same corpus version | Otherwise the candidates are measured on different material |
| Same ground truth version | Otherwise they are measured against different standards |
| Same metric definitions and same region-correctness rule (§9.3) | Fixed before the run, per §6.4 |
| **Through the same interface** — D-01's `DocumentExtractor` port | Otherwise two integrations are being compared, not two engines |
| Same normalisation applied to both | Per §7.5, so normalisation defects are attributed to DOCURA, not to a candidate |
| Engine and engine version recorded with every result | **G-03**; D-01's `ExtractionResult` carries `engine` and `engine_version` for exactly this |
| Regions compared in page-relative fractional coordinates | Per §7.4 — two engines do not agree on a pixel |

### 13.4 External candidates carry additional obligations

If an externally hosted candidate is evaluated, real documents leave DOCURA's infrastructure **during the evaluation**:

| Obligation | Source |
| --- | --- |
| The consent obtained under §5.8 must name that recipient | **REQUIREMENTS GAP — G-02**; NFR-PRIV-006 |
| The vendor's terms must be verified to exclude training on submitted content | **NFR-PRIV-002** |
| The vendor's retention of submitted documents must be established and reconciled with §5.6 | **NFR-PRIV-003** analogue; **G-23** records that external processor custody is undefined |
| The disclosure obligation must be evaluated as a *product* consequence, not only an evaluation one | **NFR-PRIV-006**, **G-17**, **G-18** |

**RECOMMENDED:** if an external candidate would require a consent scope the corpus contributors were not offered, it is **not evaluated on the real corpus**. Evaluating it "just to see" would be the disclosure the consent did not cover, and it cannot be undone.

### 13.5 What the comparison outputs

**A recommendation with evidence, not a decision.** Per §6 of the specification, technology selection belongs to document 04. This evaluation supplies:

1. Eligibility pass/fail per candidate (§13.2) — the gate, reported first;
2. Per-metric, per-type, per-condition results for eligible candidates;
3. Calibration quality per candidate (§12.2) — separately, because it is what makes BR-001 workable;
4. The per-type consequence: which types would pass and which would be demoted under §7.1, **per candidate**;
5. Stated limitations (§14.6).

### 13.6 A specific caution

**A candidate that is best on text quality is not necessarily best for this product.** The specification's requirement set weights confidence quality, honest abstention, and provenance as heavily as accuracy — because BR-001, BR-003, and AR-AST-006 depend on them. A candidate with slightly lower accuracy and well-calibrated confidence supports a **higher** automatic-action threshold safely, and therefore automates more, than a candidate with higher accuracy and uninformative confidence.

**RECOMMENDED:** the comparison reports "automatic actions available at an acceptable silent-error rate" per candidate, alongside raw accuracy — because that, not CER, is the quantity the product cares about. The acceptable rate is itself **TBD** and PM's to set (§12.3, §17.3).

---

## 14. Reproducibility

### 14.1 Why this section exists

**REQUIREMENTS GAP — G-03.** AR-AST-008 is silent on what happens when an assisted component changes. Thresholds calibrated against engine v1 are not evidence for engine v2. The evaluation **will** be repeated, and an evaluation that cannot be repeated cannot be compared against.

**DECISION REQUIRED — D-02.o.** AR-AST-008 requires the evaluation to happen but does not say what artefact proves it happened, who reviews it, what a passing result is, or where it is retained. **Without a defined artefact, "evaluated" is unfalsifiable.** *Owner: PM + Engineering.*

### 14.2 What must be recorded for a run to be reproducible

| Item | Reason |
| --- | --- |
| Corpus version and its exact membership | §4.10 — a changed corpus invalidates comparison |
| Held-out / development split, and when it was fixed | §6.3 — evidence that separation held |
| Ground truth version, including field-set version | §7.2 |
| Engine identity and version | **G-03**; `ExtractionResult.engine` / `engine_version` |
| Engine configuration and any pre-processing settings | A different DPI or binarisation setting is a different experiment |
| Metric definitions and the region-correctness rule in force | §9.3 — fixed before the run |
| Harness version | The measurement instrument is part of the measurement |
| Date and operator | Audit trail |
| Any contributor withdrawals affecting the corpus since | §5.6 — a withdrawal may make a prior run unreproducible, and that must be visible |

### 14.3 The evaluation report — RECOMMENDED artefact definition

Offered to close D-02.o. The report is **versioned, reviewed, and retained**, and contains:

1. Corpus description — properties and stratification per §4, **no document content**;
2. The §14.2 provenance record;
3. Per-candidate eligibility results (§13.2);
4. Per-metric, per-type, per-condition results (§8, §9, §10, and §11 when unblocked);
5. Calibration evidence and the threshold sweep (§12), **presented as a trade-off, not as a recommended number**;
6. Failure analysis (§15);
7. Per-type inclusion consequence under §7.1 (§17.2);
8. Stated limitations (§14.6);
9. Open gaps that prevented parts of the evaluation from running (§18).

**DECISION REQUIRED:** who reviews and signs it, and where it is retained. *Owner: PM.*

### 14.4 What the report may not contain

> **NFR-PRIV-007**: "Diagnostic and analytics data shall exclude document contents and extracted personal values." — **REQUIRED**
> **NFR-OBS-004**: failures shall be recorded "with enough context to diagnose them, **and without personal values**." — **REQUIRED**

**REQUIRED constraints on the report and on all harness output:**

- no document images or excerpts;
- no extracted personal values;
- no ground-truth values;
- no contributor identity;
- aggregate distributions and error *counts* only, never the values behind them.

**This creates a real tension with §15 failure analysis**, and §15.2 addresses it rather than pretending it away.

### 14.5 Harness properties — RECOMMENDED

| Property | Rationale |
| --- | --- |
| Deterministic given the same inputs | Otherwise a difference between runs cannot be attributed |
| Runs candidates through D-01's `DocumentExtractor` port | §13.3 — otherwise it compares integrations |
| Records processing time per document | §8.6 — data for S-2, not a score |
| Distinguishes "no engine configured" from "extraction failed" | D-01's `is_available()` exists for this; an unconfigured environment must never be recorded as a poor result |
| Separates its own defects from candidate defects | A harness bug recorded as an engine failure would corrupt selection |
| **Not part of the production application** | Nothing in this plan modifies production code |

### 14.6 Stated limitations — REQUIRED by NFR-SEC-008's principle

> **NFR-SEC-008**: "The system shall not claim to be unbreachable in any user-facing or internal material. Security statements shall describe specific measures and their limits."

The requirement is about security claims, but its principle — describe measures and their limits — applies to evaluation claims, and **RECOMMENDED** here for that reason. Every report states, at minimum:

- how the corpus was acquired and what population it does and does not represent (§4.2);
- which degradation conditions are present and which are absent;
- which requirements could not be evaluated, and which gap blocked each (§3.1);
- the ground truth's own reliability (§7.6);
- whether held-out status was fully preserved (§6);
- for a repeat evaluation, that the corpus is no longer fully independent (§6.5).

**An evaluation that overstates its own generality is worse than none**, because it will be cited as evidence for a threshold protecting real applications.

---

## 15. Failure Analysis

### 15.1 Failure is a required behaviour, not an outcome to minimise

> **FR-OCR-009**: "Where processing fails, the system shall retain the original file, state what failed, and offer a retry and a manual-entry path." — **REQUIRED**
> **EC-001**: "Retain the original, mark the document as failed with a stated reason, offer retry and manual entry. The document remains stored and searchable by label."
> **AC-US-003-5**: "...the original file is still present and downloadable, the failure reason is stated, and both retry and manual entry are offered."

Failing correctly is a specified behaviour with its own acceptance criterion. The corpus contains expected-failure documents (§4.7) precisely so this path is evaluated rather than assumed.

### 15.2 Failure taxonomy — RECOMMENDED

The purpose is attribution: a failure of the *engine* and a failure of the *pipeline* lead to different decisions.

| Class | Description | Decision it informs |
| --- | --- | --- |
| **Input rejected** | Format or size outside what the vault accepts | Sprint 3 upload limits, not extraction |
| **No text recovered** | Engine returns nothing usable | EC-001 path — expected on the illegible stratum |
| **Partial recovery** | Some pages or regions unread | EC-002 path — the "extract what is legible" behaviour |
| **Text recovered, classification failed** | Readable, type not determinable | §10 — unrecognised, per AC-US-003-3 |
| **Classification succeeded, extraction failed** | Right type, fields not recoverable | §7.1 demotion evidence — blocked on G-12 |
| **Wrong-type classification** | Fields extracted against the wrong set | §10.3 — the worst classification outcome |
| **Silent error** | A wrong value returned with high confidence | §12.4 — the failure the product exists to prevent |
| **Engine error** | Crash, timeout, malformed output | Engine eligibility and operational readiness |
| **Harness error** | A defect in the evaluation instrument | Excluded from candidate results (§14.5) |

**The privacy tension, addressed rather than deferred.** NFR-OBS-004 requires failures to be recorded "with enough context to diagnose them, and without personal values." For evaluation purposes the corpus documents themselves remain available under §16 controls, so diagnosis can proceed against the source document while the **recorded** failure context stays value-free.

**RECOMMENDED:** failure records reference a corpus document by identifier and record the failure class and structural context — page, region, condition — and never the value. This is also the pattern the production system will need under NFR-OBS-004, so the discipline is not evaluation-specific overhead.

### 15.3 The EC-001 / EC-002 boundary

The most decision-relevant analysis in this section: for each document in the illegible stratum and each in the degraded-but-legible stratum, does behaviour match the required edge case?

| Ground-truth stratum | Required behaviour | Failure mode being detected |
| --- | --- | --- |
| Illegible (EC-001) | Fail honestly; retain original; state reason; offer retry and manual entry | **Fabrication** — the engine returns confident text for a document a human cannot read |
| Degraded but legible (EC-002) | Extract what is legible; mark low-confidence fields for review | **Over-caution** — the engine fails a document a human can read, losing recoverable information |

**The first failure mode is disqualifying.** An engine that produces confident output on an illegible document is producing fabricated values with sound-looking confidence — the exact input BR-001 is designed to act on. It is why §7.6 requires the stratum to be annotated **blind to engine output**.

### 15.4 Reprocessing

> **FR-OCR-010** (SHOULD): "The user shall be able to request reprocessing of a document."

| Check | Note |
| --- | --- |
| Same document, same engine version, same configuration → same result | If not, results are not reproducible (§14) and thresholds are unstable |
| A change in engine version produces a recorded difference | **G-03** — the re-evaluation trigger |
| Reprocessing does not overwrite a user correction | **AC-US-004-3**: "GIVEN a value the user has corrected, WHEN the document is later reprocessed, THEN the user's value is retained and is not overwritten by extraction." — but **G-20** records that "duplicate attribute entries" is undefined, so the reprocessing semantics are not fully specified |

**G-25** additionally records that retry behaviour has no observability requirement at all — a gap this evaluation can expose but cannot close.

### 15.5 The manual-entry path

**FR-OCR-009** requires a manual-entry path. **REQUIREMENTS GAP — G-27:** "The 'manual-entry path' of FR-OCR-009 has no defined destination while field definitions do not exist."

**Consequence:** the *retain-original* and *state-the-reason* halves of FR-OCR-009 are evaluable now. The *manual-entry* half is not, because there is no defined field set to enter values into. Same root cause as §11: **G-12**.

### 15.6 Per-condition failure attribution

**RECOMMENDED, and the most actionable output of §15.** For each degradation condition in §4.4, the failure rate attributable to it. This is what converts an evaluation into engineering direction:

- if failures concentrate in **one capture method**, the remedy may be capture guidance in the product, not a different engine;
- if they concentrate in **one document type**, §7.1's demotion rule applies to that type;
- if they concentrate in **one degradation condition**, pre-processing may address it — noting that pre-processing choices are made on the **development** set, never the held-out set (§6.1).

---

## 16. Security

The corpus is a collection of real identity and education documents belonging to real people, held for the team's benefit rather than the contributors'. It is, in concentrated form, the most sensitive asset the project will hold. **The specification does not govern it (G-02).**

### 16.1 The controls that do apply

| Requirement | Text | Application to the corpus |
| --- | --- | --- |
| **NFR-SEC-002** | "Documents and extracted information shall be encrypted at rest." | Applies to the product's storage. **RECOMMENDED** to apply to corpus storage by extension, noting G-21…G-24 leave "encrypted at rest" undefined |
| **NFR-SEC-003** | "Every request for a document or attribute shall be authorised against the requesting user's identity; ownership shall never be inferred from an identifier supplied by the client." | The corpus has no "requesting user" in the product sense — see §16.3 |
| **NFR-SEC-001** | "All data in transit shall be encrypted using current industry-standard transport security." | Applies to any transfer of corpus documents, including to an external candidate (§13.4) |
| **NFR-SEC-008** | Security statements must "describe specific measures and their limits" | Applies to how this plan and the evaluation report describe corpus protection — §16.7 |
| **NFR-SEC-009** | "The product shall undergo independent security review before any release to users outside the team." (SHOULD) | **DECISION REQUIRED** — whether corpus handling is in that review's scope. It should be |

### 16.2 Encryption at rest — inherited gaps

**REQUIREMENTS GAP — G-21, G-22, G-23, G-24**, all inherited directly:

| Gap | Content | Corpus consequence |
| --- | --- | --- |
| **G-21** | "Encrypted at rest" has no threat model — full-disk, storage-service-managed, application-level envelope, or column-level encryption all satisfy the words differently | The corpus's protection level cannot be specified by citing NFR-SEC-002 |
| **G-22** | **Key management is entirely absent** from the specification — no generation, storage, separation, rotation, escrow, or destruction | No key policy can be inherited; one must be authored |
| **G-23** | The encryption boundary is undefined — backups, replicas, logs, temporary processing artefacts, and external processor custody | An evaluation run creates **all** of these: intermediate outputs, harness logs, and annotation working copies |
| **G-24** | Whether crypto-erasure satisfies deletion is unaddressed, and the deletion period is TBD | The destruction method of §5.6 cannot be specified by inheritance |

**G-23 is the acute one for D-02.** An evaluation pipeline generates derived artefacts as a matter of course. Each one is a copy of corpus content, and each is outside a boundary the specification never drew.

### 16.3 Access control

**NFR-SEC-003** is written for a product where every document has an owning user. The corpus does not fit that model: its documents belong to contributors, but are accessed by team members.

**DECISION REQUIRED — D-02.c and D-02.g together.** The following must be specified:

| Item | Status |
| --- | --- |
| Which roles may read corpus documents | **DECISION REQUIRED** |
| Whether annotation access differs from evaluation access | **DECISION REQUIRED** |
| Whether held-out access is separated from development access | **DECISION REQUIRED** — §6.2; this is a security control *and* a validity control |
| Whether access is logged, and where those logs live | **DECISION REQUIRED** — **G-26** records that no requirement obliges recording security-relevant events at all |
| Whether corpus storage is isolated from production user storage | **RECOMMENDED: yes** — see §16.4 |

**G-26** deserves emphasis here: the register describes the absence of any security-event recording requirement as "serious for a product handling identity documents". A corpus access log is therefore a control this plan proposes, not one it inherits.

### 16.4 Isolation from production — RECOMMENDED

Corpus documents are **not** user documents of the running system. Storing them in production document storage would:

- place non-user documents inside a store governed by user-facing deletion obligations (NFR-PRIV-003) that do not fit them;
- make NFR-SEC-003's per-user authorisation model ambiguous for objects with no owning user;
- risk a corpus document appearing in a user's vault, which would breach NFR-PRIV-002 unambiguously.

**RECOMMENDED:** the corpus lives in a separate, access-controlled store, with its own retention and destruction policy per §5.6, and the evaluation harness never writes to production storage.

### 16.5 Derived artefacts

Every derived artefact contains corpus content and inherits its protection:

| Artefact | Contains | Treatment |
| --- | --- | --- |
| Extraction output (text, fields, regions) | Personal values | Corpus-level protection; destroyed with the corpus (§5.6) |
| Ground truth annotations | Personal values, in structured form — **arguably the most exposed artefact**, since values are labelled and indexed | Corpus-level protection |
| Harness logs | **Must not** contain values, per NFR-PRIV-007 / NFR-OBS-004 | Value-free by construction (§15.2) |
| The evaluation report | Aggregates only, per §14.4 | May be retained beyond the corpus — **and see §16.6** |
| Annotation working copies | Personal values | Enumerated and destroyed; **G-23** does not cover them |

### 16.6 The report outlives the corpus

**RECOMMENDED and worth stating explicitly:** because the evaluation report contains only aggregates (§14.4), it can be retained after the corpus is destroyed. That is what makes a short corpus retention period compatible with keeping the evidence for AR-AST-008 — and it is the reason §14.4's constraints are drawn tightly. A report containing examples "for illustration" would forfeit this property and become a small corpus of its own.

### 16.7 Honest description of controls

> **NFR-SEC-008**: "The system shall not claim to be unbreachable in any user-facing or internal material. Security statements shall describe specific measures and their limits." — **REQUIRED**

Applied to this section: the controls above are **proposals inside a requirements gap**. They are not inherited from an approved security model, because the specification does not contain one for evaluation material. Stating them as though they were approved would be exactly the overclaiming NFR-SEC-008 prohibits. **The corpus security model requires security ownership and approval before collection begins** — the same gate as §5.9.

---

## 17. Evaluation Decision Criteria

### 17.1 What must be fixed before the held-out run

**REQUIRED by §6.4.** Every criterion below is fixed, recorded, and approved **before** the held-out corpus is used. A criterion chosen after seeing results is not a criterion; it is a rationalisation, and it destroys the evidence value of the run for every type, not just the disputed one.

| Criterion | Fixed before the run | Status |
| --- | --- | --- |
| Per-type pass definition | §17.2 | **DECISION REQUIRED** |
| Acceptable silent-error rate | §17.3 | **DECISION REQUIRED — TBD** |
| Region-correctness rule | §9.3 | **DECISION REQUIRED** |
| Metric definitions | §8.2, §10.2, §11.3 | **RECOMMENDED** — approval needed |
| Candidate eligibility gates | §13.2 | **REQUIRED** — derived from AR-AST requirements |
| What constitutes a completed evaluation | §14.3, §19 | **DECISION REQUIRED — D-02.o** |

### 17.2 The per-type decision — REQUIRED by §7.1

> **§7.1**: "a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only rather than shipped as unreliable." — **REQUIRED**

This is the one decision rule the specification states outright. Its three-way outcome:

| Outcome | Meaning | Requirement |
| --- | --- | --- |
| **Include with structured extraction** | Type is classified and its fields extracted into the record | §7.1, FR-OCR-004 |
| **Demote to store-and-search only** | Type is recognised and stored; **no** structured extraction | §7.1 |
| **Unclassified** | Type not recognised; stored and searchable as unclassified | §7.1 "Other", FR-OCR-002 |

**REQUIREMENTS GAP — G-08.** The middle state is not defined in the data model: *"The 'store-and-search only' state a demoted type falls into is not defined as a document state."* It is distinct from unclassified — the document has a **known type** but no extraction — and §7.1 requires it while FR-DOC-002 does not provide it.

**Consequence:** if any type is demoted, a user-visible document state that the specification does not define becomes necessary. **That must be resolved before the evaluation reports, not after** — otherwise the evaluation produces a verdict the product cannot express.

**DECISION REQUIRED — the pass definition itself.** §7.1 says "cannot meet the review threshold", which requires: (a) the review threshold value (**G-04**), (b) whether it is global or per type (**G-07**), and (c) what fraction of a type's field set must meet it for the *type* to pass — §7.1 speaks of a type meeting a threshold, but a threshold applies to a *field*. That last is a genuine gap in the rule's arithmetic and is **DECISION REQUIRED**. *Owner: PM.*

### 17.3 The engine decision

**Order of application — REQUIRED:**

1. **Eligibility gates first** (§13.2). An ineligible candidate is not scored. This ordering is deliberate: it prevents a high-accuracy, no-confidence candidate from being argued into scope on its numbers.
2. **Then evidence** across §8–§12, reported per type and per condition.
3. **Then the product decision** — PM's, recorded in Step 4 per §6's Selection Principle.

**DECISION REQUIRED — the acceptable silent-error rate.** §12.4 establishes that a silent error and an unnecessary interruption are not interchangeable. The rate the product will accept is a **product risk decision**, is **TBD**, and **no value is proposed here**. It is the single number that most determines how much DOCURA automates.

### 17.4 The A-7 verdict

> **§12.3, A-7**: "Extraction is unreliable on real scans; thresholds may exclude most automatic action." Affected: FR-OCR-004…006, BR-001.

The evaluation must state a verdict on A-7 explicitly, in one of three forms:

| Verdict | Consequence |
| --- | --- |
| **A-7 holds** | Extraction is reliable enough on real, imperfect documents for a threshold to permit meaningful automatic action. FR-OCR-004…006 and BR-001 proceed to build. |
| **A-7 holds partially** | Reliable for some types or conditions. §7.1's demotion rule applies to the rest, per type. |
| **A-7 fails** | Thresholds exclude most automatic action. **This is a product-level finding**, not an engineering setback: the MVP's automation premise does not hold on real documents, and §12.3 requires FR-OCR-004…006 and BR-001 not to be committed to build. |

**The third outcome must be reportable without prejudice.** §12.3's whole purpose is to make it sayable, and §15 of the specification records the project's own standard: recording that something is only partially met "is more useful than claiming completeness". An evaluation designed so that A-7 cannot fail is not an evaluation.

**NFR-OBS-003** provides the production continuation: "user override rate on automatically filled fields as the primary indicator of silent error." The held-out evaluation sets the threshold; the override rate tests it against reality afterwards. **RECOMMENDED:** the evaluation report names the override rate as the post-release check on its own conclusion, so the threshold is understood as revisable evidence rather than a settled constant.

### 17.5 What the evaluation may not do

| Prohibited | Why |
| --- | --- |
| Set a threshold that permits automatic action on evidence of unreliability | **BR-001**, **BR-002** — not configurable by anyone |
| Include a type that failed its criterion | **§7.1** — "rather than shipped as unreliable" |
| Adjust criteria after seeing results | **§6.4** — destroys held-out status |
| Select a candidate that failed an eligibility gate | **§13.2** — AR-AST-001/002/006/007 are MVP requirements, not preferences |
| Report an aggregate that hides a per-type failure | **§7.1** operates per type; an average conceals the decision it is meant to inform |
| Treat unrecognised outputs as errors | **AR-AST-002**, **EC-003** — abstention is a correct answer |
| Substitute synthetic documents for real ones | **AR-AST-008** — and it would produce a false positive on the riskiest assumption |

---

## 18. Open Decisions / Requirements Gaps

Every item below blocks or constrains D-02. Gap IDs are those of the decision register; no new IDs are created here.

### 18.1 Requirements gaps — need a requirements amendment

| Gap | Content | Requirements affected | Blocks in this plan |
| --- | --- | --- | --- |
| **G-02** | No requirement governs the collection, consent, retention, destruction, or team-readability of a real-document evaluation corpus | AR-AST-008, NFR-PRIV-002, NFR-PRIV-003 | §5 entirely; **corpus collection cannot begin** |
| **G-03** | No re-evaluation trigger when an assisted component changes version | AR-AST-008 | §6.5, §14; determines when a calibrated threshold ceases to be evidence |
| **G-04** | Neither threshold has a value; the review threshold carries no TBD marker and no study reference | BR-001, BR-002, FR-OCR-006 | §12; §17.2's pass definition |
| **G-05** | The relationship between the review and automatic-action thresholds is never stated, nor which governs classification | BR-001, BR-002, FR-OCR-003/006, AC-US-003-3 | §10.5, §12.7 |
| **G-06** | Confidence has no defined scale, semantics, or cross-component comparability — **makes BR-001 untestable as written** | AR-AST-001, FR-OCR-003/005, BR-001 | §12.1; cross-candidate comparability in §13 |
| **G-07** | Global vs per-document-type thresholds unaddressed | NFR-MNT-002, BR-001, §7.1 | §12.2, §17.2 |
| **G-08** | The "store-and-search only" state a demoted type falls into is not defined as a document state | §7.1, FR-DOC-002, FR-OCR-002 | §17.2 — the evaluation could produce a verdict the product cannot express |
| **G-09** | "Address proof" is a category, not a document type; its members are never enumerated | §7.1, FR-OCR-002, FR-OCR-004 | §4.3 sampling; §10.6 |
| **G-10** | "Semester result" (§7.1) and "semester marksheet" (AC-US-003-1) may be one type or two | §7.1, AC-US-003-1 | §4.3, §10.6 |
| **G-11** | Whether photograph and signature have structured information requirements is never stated | §7.1, FR-OCR-004, FR-INF-007 | §4.3; whether they have a §11 row at all |
| **G-12** | **No field definitions exist for any document type** | FR-OCR-004, FR-OCR-005, NFR-MNT-001 | **§11 entirely**, §7 layers L4/L5, §12's threshold selection, §17.2 |
| **G-13** | **The canonical attribute vocabulary does not exist**, though FR-ACC-004 names it | FR-ACC-004, FR-INF-001/004/007/008 | **§11.6 entirely**, §7 layers L6/L7 |
| **G-14** | Sensitivity classification rules are not in `step3.pdf`; §02 Table 13.1 is an ASM-tagged working classification whose boundary A-5 says must be set by users | FR-INF-007, FR-SENS-001 | §5.7 — corpus protection cannot be derived from the sensitivity model |
| **G-15** | No default sensitivity tier for an attribute no rule covers | FR-INF-007 | §5.7 |
| **G-16** | Document-level sensitivity is presupposed but defined nowhere | FR-SENS-001, FR-MATCH-009, EC-011 | §5.7 — the corpus holds *documents*, not attributes |
| **G-17** | "Processing" in NFR-PRIV-006 is undefined | NFR-PRIV-006 | §5.5, §13.4 |
| **G-18** | No re-disclosure requirement when the processing arrangement changes | NFR-PRIV-006 | §13.4 |
| **G-20** | "Duplicate attribute entries" is undefined, so reprocessing semantics are unspecified | NFR-REL-005 | §15.4 |
| **G-21** | "Encrypted at rest" has no threat model | NFR-SEC-002 | §16.2 |
| **G-22** | **Key management is entirely absent** from the specification | NFR-SEC-002 | §16.2 |
| **G-23** | The encryption boundary — backups, replicas, logs, temporary artefacts, external processor custody — is undefined | NFR-SEC-002, NFR-PRIV-003 | §16.2, §16.5 — an evaluation run creates all of these |
| **G-24** | Whether crypto-erasure satisfies deletion is unaddressed; the period remains TBD | NFR-PRIV-003 | §5.6 destruction method |
| **G-25** | Retry behaviour has no observability requirement | NFR-OBS-004, FR-OCR-009 | §15.4 |
| **G-26** | No requirement obliges recording security-relevant events | NFR-OBS-004, NFR-SEC-009 | §16.3 — corpus access logging is proposed, not inherited |
| **G-27** | FR-OCR-009's "manual-entry path" has no defined destination while field definitions do not exist | FR-OCR-009, AC-US-003-5 | §15.5 |

### 18.2 Decisions required — ownership, not amendment

| Ref | Decision | Owner | Blocks |
| --- | --- | --- | --- |
| **D-02.a** | Corpus ownership as an asset, and who may authorise a second use | PM + Legal | §4.1; re-evaluation under G-03 |
| **D-02.b** | Consent model, scope, and withdrawal path | PM + Legal | §5.8 — **collection** |
| **D-02.c** | Whether NFR-PRIV-002's readability prohibition binds the team | PM + Legal | §5.2, §16.3 |
| **D-02.d** | Acquisition method — volunteer, paid panel, staff-and-family, public record | PM | §4.2; determines §5 entirely |
| **D-02.e/f** | Retention period, destruction trigger, method, verification, evidence | PM + Legal | §5.6 |
| **D-02.g** | Held-out separation mechanism, access, leakage evidence | Engineering + PM | §6.2 |
| **D-02.h** | Per-type coverage minimums | PM + Engineering | §4.3 — **TBD** |
| **D-02.i** | Definition of "imperfect" — the degradation taxonomy | Engineering proposes, PM approves | §4.4, §7 layer L1 |
| **D-02.j** | Multi-page count and page-depth distribution | Engineering + PM | §4.5 — **TBD** |
| **D-02.o** | What artefact proves the evaluation happened, who reviews it, where it is retained | PM + Engineering | §14.3, §19 — without it, "evaluated" is unfalsifiable |
| — | Whether confidence *calibration* constitutes training under NFR-PRIV-002 | PM + Legal | §5.4, §12.2 |
| — | Whether AR-AST-007 constrains DOCURA-side calibration | PM + Engineering | §12.5 |
| — | Region-correctness rule | Engineering proposes, PM approves | §9.3 |
| — | Transcription conventions | Engineering proposes, PM approves | §7.3 |
| — | Acceptable silent-error rate | PM | §17.3 — **TBD**, the number that most determines how much DOCURA automates |
| — | Per-type pass definition, including what fraction of a field set must pass for the type to pass | PM | §17.2 |
| — | Whether corpus handling is in NFR-SEC-009's independent security review scope | PM + Security | §16.1 |
| — | Whether external candidates may be evaluated on the real corpus | PM + Legal | §13.4 |
| — | Whether re-evaluation reuses the corpus or requires fresh material | PM | §6.5 |

### 18.3 Values that remain TBD

Every one of these is unset because `backend/step3.pdf` supplies no basis for it. **None is invented here.**

| Value | Source of the TBD |
| --- | --- |
| Automatic-action threshold | BR-001 — "TBD — to be validated (study S-6)" |
| Review threshold | Undefined; **G-04** |
| Total corpus size | No size stated anywhere in the specification |
| Per-type, per-condition, per-person minimums | Not stated |
| Held-out / development split ratio | Not stated |
| Multi-page proportion and page depth | Not stated |
| Expected-failure and out-of-set proportions | Not stated |
| Acceptable silent-error rate | Not stated |
| Region-overlap correctness fraction | Not stated |
| Double-annotation proportion | Not stated |
| Corpus retention period | Not stated; NFR-PRIV-003's own period is TBD |
| MVP script and language set | FR-OCR-012 — "TBD — to be validated against a real document corpus (study S-6)" |
| Engine choice | §6 Selection Principle — pending this evaluation |

### 18.4 Dependency order

Reading the gaps as a sequence rather than a list:

```
G-02 + D-02.b/c/d/e/f  ──►  corpus collection may begin        (§5.9, §16.7)
        │
        ├──► D-02.i  ──►  L1 ground truth  ──►  stratified reporting     (§4.4, §7)
        ├──► §7.3    ──►  L3 ground truth  ──►  §8 OCR evaluation
        └──► G-09/10/11 ─►  L2 ground truth  ──►  §10 classification

G-13 (attribute vocabulary)  ──►  G-12 (per-type field sets)
        │                                │
        │                                ├──►  L4/L5  ──►  §11 field extraction
        │                                └──►  §12 threshold sweep  ──►  G-04 value
        └──►  L6/L7  ──►  §11.6 conflict detection

G-04 + G-05 + G-07  ──►  §17.2 per-type pass definition  ──►  §7.1 type-set decision
G-08                ──►  the demoted-type state must exist before that decision lands
G-06                ──►  BR-001 testable at all;  cross-candidate comparability (§13)
```

The two independent roots are **G-02** (gates collection, and therefore everything) and **G-13** (gates the entire field-extraction half). They can be worked in parallel: G-02 is a legal and product task, G-13 a product-definition task. **Neither is an engineering task, and neither can be started by engineering.**

---

## 19. Exit Criteria for D-02

D-02 is a **planning** deliverable. Its exit criteria concern the plan, not the evaluation. The evaluation's own criteria are stated separately below, so the boundary is unambiguous.

### 19.1 Exit criteria for D-02 (this document)

| # | Criterion | Status |
| --- | --- | --- |
| 1 | AR-AST-008's four obligations identified and each traced to a corpus property | **Met** — §2.1, §4 |
| 2 | Every requirement bearing on the evaluation cited from `backend/step3.pdf` | **Met** — §2 |
| 3 | A requirement-to-evidence matrix stating, per requirement, what evidence is needed and what blocks it | **Met** — §3 |
| 4 | Corpus properties specified as requirements, with all quantities left TBD | **Met** — §4 |
| 5 | Privacy and consent obligations stated, with the governing gap named | **Met** — §5, G-02 |
| 6 | Held-out separation obligation stated and a mechanism proposed for approval | **Met** — §6 |
| 7 | Ground truth layers defined, with each blocked layer's blocker named | **Met** — §7 |
| 8 | Evaluation method specified for OCR, regions, classification, and field extraction | **Met** — §8–§11 |
| 9 | Calibration and threshold-selection method specified, with **no value proposed** | **Met** — §12 |
| 10 | Engine-comparison method and eligibility gates specified, with **no engine named** | **Met** — §13 |
| 11 | Reproducibility requirements and report definition specified | **Met** — §14 |
| 12 | Failure analysis method specified, including the EC-001 / EC-002 boundary | **Met** — §15 |
| 13 | Security obligations stated, with inherited gaps named | **Met** — §16 |
| 14 | Decision criteria specified, fixed-before-run discipline stated | **Met** — §17 |
| 15 | All gaps and decisions consolidated with owners | **Met** — §18 |
| 16 | No requirement, field, threshold, corpus size, engine, sensitivity rule, or result invented | **Met** — every quantity is TBD or cited |
| 17 | Plan reviewed and approved by PM and Engineering | **Not met — pending review** |

**D-02 exits when criterion 17 is met.** Everything above it is complete in this document.

### 19.2 Entry criteria for the evaluation itself

The evaluation described here **cannot begin** until all of the following hold. This is the practical output of the plan.

**Before corpus collection:**

| # | Gate | Blocker |
| --- | --- | --- |
| E1 | Consent model, scope, and withdrawal path authored and approved | **G-02**, D-02.b |
| E2 | Corpus ownership named | D-02.a |
| E3 | Acquisition method decided | D-02.d |
| E4 | Retention period, destruction trigger, method, and verification specified | **G-02**, D-02.e/f |
| E5 | Team access model specified — who may read corpus documents | D-02.c, **G-26** |
| E6 | Corpus security model authored and approved by security ownership | §16.7, **G-21/22/23** |
| E7 | Recipient scope fixed — including whether external candidates are permitted | §13.4, NFR-PRIV-006 |

**Before annotation:**

| # | Gate | Blocker |
| --- | --- | --- |
| E8 | Degradation taxonomy approved | D-02.i |
| E9 | Transcription conventions decided | §7.3 |
| E10 | Type-set questions resolved | **G-09**, **G-10**, **G-11** |
| E11 | Held-out / development split fixed and recorded, **before any engine is installed** | §6.3 |

**Before the field-extraction half:**

| # | Gate | Blocker |
| --- | --- | --- |
| E12 | Canonical attribute vocabulary authored and approved | **G-13** |
| E13 | Per-type field sets authored, each field mapping to an attribute or explicitly to none | **G-12** |
| E14 | Per-attribute normalisation rules defined | **G-13**, FR-INF-008 |
| E15 | Whether calibration is permitted under NFR-PRIV-002 settled | §5.4 |

**Before the held-out run:**

| # | Gate | Blocker |
| --- | --- | --- |
| E16 | Per-type pass definition fixed | §17.2, **G-04**, **G-05**, **G-07** |
| E17 | Acceptable silent-error rate fixed | §17.3 |
| E18 | Region-correctness rule fixed | §9.3 |
| E19 | Evaluation-report definition, reviewer, and retention agreed | D-02.o |
| E20 | The demoted-type document state defined, so a demotion verdict can be expressed | **G-08** |

### 19.3 The staged option

**RECOMMENDED.** §3.2 establishes that the OCR-quality half is unblocked by G-12 and G-13 while the field-extraction half is entirely blocked by them. Gating the whole evaluation on the field definitions would idle the corpus work behind a product-definition task.

| Stage | Content | Gated by | Produces |
| --- | --- | --- | --- |
| **Stage 1** | §8 OCR quality, §9 text-block regions, §10 classification, §15 failure behaviour, §13.2 eligibility | E1–E11 | Engine eligibility and a shortlist; per-type classification evidence; per-condition failure attribution; a first read on **A-7** |
| **Stage 2** | §11 field extraction, §11.6 conflict detection, §12 calibration and threshold selection, §17.2 type inclusion | E12–E20, plus Stage 1 | **BR-001's value**, the review threshold, the §7.1 type set, the **A-7 verdict** |

Two cautions attach to staging, and they are not minor:

1. **Stage 1 must not be reported as satisfying AR-AST-008.** AR-AST-008 requires evaluation "before any threshold is set", and Stage 1 sets no threshold. Only Stage 2 discharges the requirement.
2. **Stage 1 consumes held-out independence.** Once Stage 1's results are seen, the corpus is no longer fully naive for Stage 2. Either the split reserves material for Stage 2 (**decided at E11, before either stage runs**), or Stage 2's report states the reduced independence as a limitation under §14.6. **DECISION REQUIRED**, and it must be taken at E11 — not discovered at Stage 2.

### 19.4 What Sprint 4 cannot deliver until this evaluation completes

Stated plainly, because it is the practical consequence of the whole plan:

| Item | Blocked by |
| --- | --- |
| An OCR engine selection | AR-AST-008, §6 Selection Principle |
| Any confidence threshold | BR-001, AR-AST-008 "before any threshold is set" |
| The final MVP document-type set | §7.1, ASM-001 |
| FR-OCR-004, FR-OCR-005, FR-OCR-006 committed to build | §12.3 (A-7), plus **G-12** |
| FR-INF-004/005/006 committed to build | **G-13** |
| Any claim that A-7 holds | §12.3 |

D-01's position — an extraction port with the engine deliberately unselected — remains correct until this evaluation reports. **No dependency, engine, or threshold should be added to the codebase before then.**

---

## 20. Status

| Item | Status |
| --- | --- |
| D-02 evaluation plan | **Complete — pending review** |
| Corpus | **Not collected.** Collection blocked at E1–E7 |
| Ground truth | **Not annotated.** L1–L3 blocked at E8–E10; L4–L7 blocked on G-12 / G-13 |
| OCR engine | **TBD — pending this evaluation** |
| Evaluation harness | **Not built.** No production code modified |
| Evaluation results | **None exist.** No result is reported, estimated, or implied anywhere in this document |
| Thresholds | **TBD** — BR-001 and the review threshold both unset |
| MVP document-type set | **TBD** — all twelve candidate types provisional under §7.1 |
| Dependencies added | **None** |
| Database schema | **Unchanged** |
| Migrations | **None** |
| APIs | **None** |
| Production code | **Unmodified** |
