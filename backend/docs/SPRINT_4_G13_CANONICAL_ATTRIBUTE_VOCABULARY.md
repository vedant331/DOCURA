# DOCURA — Sprint 4 G-13 Canonical Attribute Vocabulary

| Field | Value |
| --- | --- |
| Gap | **G-13 — the canonical attribute vocabulary does not exist, though FR-ACC-004 names it** |
| Status | **PRODUCT DECISION — APPROVED. Shape approved 5 September 2026; the revision approved 6 September 2026.** Decisions G-13.1 … G-13.14 (§15.1) were approved as **PRODUCT DECISION — APPROVED** and recorded in [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) **D-05.6**. **Three of the fourteen were revised — G-13.2, G-13.5, G-13.9. A fourth, G-13.11, had its trigger clarified with its wording unchanged, and a fifteenth, G-13.15, was added. All five were approved on 6 September 2026 and are recorded in D-05.8. The other ten stand as approved on 5 September 2026, untouched.** **A T1 content approval — PD-B — was recorded on 7 September 2026 (§21, D-05.11): it approves `v0.1-draft`'s one entry, its one-attribute scope, and N-TEXT, and nothing else; it meets no gate and closes no gap.** **PD-A, PD-C, PD-D and PD-E were approved on 8 September 2026 (§22, D-05.12); the engineering act X12 was completed the same day (§22.6), and X15 was closed the same day (§22.7) by applying the fourth false-conflict attribution category at D-02 §11.6.1. **G-13-A is MET (8 September 2026).** G-13-B remains NOT MET (property-7 tiers G-14/G-15; §12.3 A-5/A-7).** **REQUIREMENTS GAP G-13 REMAINS OPEN** — what is approved is a set of product decisions beside the specification, never a closure of the gap. The approval fixes the **shape** of a canonical attribute definition and the rules governing it. **It creates no attribute, closes no requirements gap, and does not amend `backend/step3.pdf`.** Nothing in this document is a requirement unless explicitly cited as one from `backend/step3.pdf`. |
| Revision — what changed | **G-13.2** property 6 redefined from `single \| repeating` to a **scope-keyed cardinality**; the property count stays **seven** and no eighth property is added. **G-13.5** comparison function qualified to operate **within a scope instance**. **G-13.9** narrowed to release-time, splitting closure into **G-13-A** (structural) and **G-13-B** (releasable). **G-13.11**'s wording is untouched; its “until G-13 closes” **trigger** is clarified to mean **G-13-A**. Driver: [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) §5, §6, §9. |
| Revision — what is **not** changed | **G-13.3 is NOT reopened** — identity remains established by the field→attribute mapping alone. **No eighth property.** G-13.1, G-13.4, G-13.6, G-13.7, G-13.8, G-13.10, G-13.12, G-13.13, G-13.14 are untouched. **G-13.11's decision wording is unchanged**; only its *trigger* is clarified against the two-gate model (§15.1), which adds no prohibition and lifts none before G-13-A. **No attribute is created, approved, or named.** **G-14 and G-15 are not resolved.** |
| T1 — vocabulary contents | **AUTHORED 6 September 2026 as `v0.1-draft` (§19); COMPLETED same day (§20: N-TEXT proposed, properties 1–6 complete, property 7 TBD by design); APPROVED 7 September 2026 — PD-B (§21, D-05.11):** the one entry `person.full_name`, its **one-attribute scope**, and **N-TEXT**. One entry authored, nine candidates not authored, none approved. X3 and X5 resolved; **X7, X8, X10 and X18 now MET** for this version; **PD-A, PD-C, PD-D, PD-E APPROVED 8 September 2026 (§22, D-05.12):** X2, X4, X6, X8, X11, X13, X14 and X17 are now MET for `v0.1-draft`. **The version remains NOT RELEASABLE (property 7 TBD).** **X12 was completed 8 September 2026 (§22.6); X15 was closed the same day (§22.7) by applying the fourth false-conflict attribution category at D-02 §11.6.1. G-13-A is MET (§22.3, §22.7). G-13-B remains NOT MET (G-14/G-15; §12.3 A-5/A-7).** |
| Still outstanding after approval | **The vocabulary's contents beyond `v0.1-draft`** (§15.3 T1, §19.5) · the `qualification` scope-instance derivation, deferred to the first such attribute (§22.1 PD-D) · the address component set, from the §10/ASM-002 mock-form inventory (§22.1 PD-A) · other TBDs in §15.3 · **X12** (hold as versioned configuration) · **X15** (D-02 §11.4.1, owed by the D-02 owner) · G-12 · G-14 · G-15 · G-20 · the §11 Containment Rule amendment (§18 X16). **Resolved 8 September 2026: G-19 (PD-C), the scope-instance rule for `v0.1-draft` (PD-D), and the unmapped-value destination G-29 (PD-E).** |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0, 25 August 2026 |
| Related | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) — **D-05.4** (the vocabulary), D-05.5, D-06, D-08.3/D-08.4, D-12; gaps **G-13**, G-14, G-15, G-19, G-20, G-27, G-28 |
| Related | [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) — §10.2 (V1–V7), §11 (G-12.3, G-12.4) |
| Related | [`SPRINT_4_D02_OCR_EVALUATION_PLAN.md`](SPRINT_4_D02_OCR_EVALUATION_PLAN.md) — §3.2, §7.1 (layers L6/L7), §11.6, §18, §19 |
| Related | [`SPRINT_4_G02_CORPUS_GOVERNANCE.md`](SPRINT_4_G02_CORPUS_GOVERNANCE.md) — APPROVED; §12 gate list. This document does not alter it. |
| Explicitly **not** resolved here | **G-12** — which concepts/fields exist for each document type. See §15.2. |
| Attributes named | **One authored as proposed content under T1 — `person.full_name` (§19.4). Nine further candidates are named in §19.5 only to record why they are NOT authored. No attribute is approved, and none is evaluation- or implementation-ready.** |
| Fields named | **None** |
| Documents collected | **0** |
| OCR installed / run | **No** |
| Production code modified | **No** |

---

## 1. Purpose

### 1.1 The question this document answers

**FR-ACC-004** (MVP, MUST) reads:

> "The system shall maintain a user profile of **canonical personal attributes** derived from documents and editable by the user."

**FR-INF-004** (MVP, MUST) reads:

> "The system shall detect when two documents give different values for **the same attribute**."

Both requirements are written as though a vocabulary of attributes exists. This document establishes, by exhaustive search of `backend/step3.pdf`, **whether it does** — and finds that the word *canonical* appears exactly once in thirty-nine pages, that no section enumerates an attribute, and that the identity relation FR-INF-004 depends on ("the same attribute") is never defined.

The objective is **not** to author the vocabulary. It is to state the gap precisely, to determine the **minimum shape** a canonical attribute definition must have for the requirements that consume it to function, and to identify which parts of the D-02 evaluation are and are not blocked meanwhile.

### 1.2 The critical distinction: G-13 is not G-12

| | Question | Artefact | Status |
| --- | --- | --- | --- |
| **G-13** *(this document)* | **HOW is an extracted concept represented consistently?** The identity, naming, typing, normalisation and multiplicity of a concept, independent of any one document. | The canonical attribute vocabulary | **OPEN** — analysed here |
| **G-12** | **WHICH concepts/fields exist for each document type?** | Per-type field sets | **ANALYSED, NOT APPROVED** — [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) |

**Consequence for this document:** it defines no Aadhaar attribute, no PAN attribute, no marksheet attribute, and no attribute of any other kind. It produces a *shape*, not a *list*. Where the shape requires content, the content is named as a Product Management task, not supplied.

### 1.3 What this document deliberately does not do

It named no attribute and no field when it was written; **§19's T1 pass, added 6 September 2026, authors one attribute as proposed content and names nine further candidates in order to record why they are not authored** — it approves none of them and creates no field. It does not resolve G-12; it does not resolve G-14, G-15, G-19 or G-20; it does not amend `backend/step3.pdf`; it does not mark **REQUIREMENTS GAP G-13** closed in the decision register or anywhere else — the decisions of §15.1 are approved as **product decisions** (D-05.6, D-05.8), which is a different thing from closing the gap; and it touches no application code, schema, migration, dependency, corpus, or document.

### 1.4 Three meanings of "name" that must not be conflated

The word *name* is the most dangerous word in this gap, because `step3.pdf` uses label-shaped language for four unrelated things. §11 develops this; the separation is stated here so it governs the whole document.

| Sense | Example in the specification | Whose concern |
| --- | --- | --- |
| **The canonical attribute's own identity** | *Nothing. No requirement names an attribute.* | **G-13** |
| **The label printed on a document** — what a marksheet actually prints above a value | *Nothing. Never addressed anywhere in the specification.* | **G-12** (the field→attribute mapping absorbs it) |
| **The label on a third-party form field** | FR-FLD-001 "visible label, adjacent text, placeholder, and declared attributes" | Neither — form-field sense, already specified |
| **The user's personal label for a document** | FR-DOC-003 "a personal label without altering its type" | Already specified; unrelated to attributes |

---

## 2. Source Requirements

Every requirement below is quoted from `backend/step3.pdf`. These are the requirements that either **name** the concept, **presuppose** a vocabulary, or **attach a property** to an attribute.

### 2.1 The one requirement that names the concept

| ID | Release / Priority | Requirement | Trace |
| --- | --- | --- | --- |
| **FR-ACC-004** | MVP · MUST | "The system shall maintain a user profile of **canonical personal attributes** derived from documents and editable by the user." | N-01 |

**This is the only occurrence of the word "canonical" in `backend/step3.pdf`.** It names the concept and defines none of its contents.

### 2.2 The requirements that cannot function without attribute identity

| ID | Release / Priority | Requirement | Why it needs the vocabulary |
| --- | --- | --- | --- |
| **FR-INF-001** | MVP · MUST | "The system shall maintain a structured record of the user's personal information, **assembled from all processed documents**." | "Assembled from all documents" requires knowing that a value read from document A and a value read from document B are the *same* thing |
| **FR-INF-004** | MVP · MUST | "The system shall detect when two documents give different values for **the same attribute**." | **The hard dependency.** Conflict detection is an operation on an identity relation the specification never defines |
| **FR-INF-005** | MVP · MUST | "Detected conflicts shall be presented to the user for resolution. The system shall not resolve a conflict automatically." | Operates on FR-INF-004's output |
| **FR-INF-006** | MVP · MUST | "The system shall record which value the user designated authoritative and **retain the alternatives**." | Alternatives are alternatives *for one attribute* |
| **FR-SRCH-003** | MVP · SHOULD | "The user shall be able to search by **attribute value** and receive the supporting document." | Requires addressable attributes |
| **EC-019** | — | "The same attribute is requested twice in one form" → "Fill both consistently from the same authoritative value…" | Requires attribute identity across two form fields |
| **NFR-REL-005** | MVP · SHOULD | "Repeating the same operation on the same input shall not produce duplicate documents or **duplicate attribute entries**." | "Duplicate" is a statement about attribute identity (**G-20**) |
| **AC-US-005-1** | — | "GIVEN two documents give different values for **the same attribute**, WHEN processing completes, THEN a conflict is raised and neither value is marked authoritative." | Not executable as a test without the relation |
| **AC-US-005-2** | — | "GIVEN an unresolved conflict on an attribute, WHEN a form requests that attribute, THEN DOCURA treats the field as ambiguous and asks rather than choosing." | Requires attribute-to-form-field resolution |

### 2.3 The requirements that attach a property to an attribute

These are the specification's statements about what an attribute *has* — the envelope around a vocabulary that does not exist.

| ID | Release / Priority | Requirement | Property attached |
| --- | --- | --- | --- |
| **FR-INF-002** | MVP · MUST | "**Every attribute value** shall reference the document it came from and the confidence with which it was read." | Per-value provenance + confidence |
| **FR-INF-003** | MVP · MUST | "The user shall be able to correct **any attribute value**; a user-supplied value shall become authoritative over any extracted value." | Correction precedence |
| **FR-INF-007** | MVP · MUST | "**Every attribute** shall carry a sensitivity classification of routine, sensitive, or consequential." | Sensitivity tier — **per attribute, not per value** |
| **FR-INF-008** | MVP · MUST | "The system shall normalise **attribute formats** deterministically — dates, casing, spacing, and numeric precision — without altering meaning." | Normalisation — **per attribute format** |
| **FR-INF-009** | MVP · SHOULD | "The system shall record a history of changes to **each attribute**, including who or what changed it." | Change history with actor |
| **FR-SENS-001** | MVP · MUST | "…maintain the three-tier sensitivity classification for both **stored attributes** and detected form fields." | Sensitivity applies to stored attributes |
| **FR-SENS-006** | MVP · SHOULD | "The user shall be able to **raise** the sensitivity of an attribute. Lowering the consequential tier shall not be possible for any user." | Monotonic tier |
| **AR-DET-003** | MVP | "**Value normalisation** — dates, casing, whitespace, numeric precision — shall be deterministic and **reversible**." | Determinism **and reversibility** |
| **AR-DET-008** | MVP | "**Conflict detection** between documents shall be deterministic; conflict resolution shall never be automated at all." | Detection is deterministic — so the identity relation must be deterministic |
| **AR-AST-007** | MVP | "No assisted component shall be permitted to escalate its own authority — it may lower a confidence, never raise it, and **may add a sensitivity classification, never remove one**." | Tier monotonicity |
| **BR-004** | — | "Where the user's own documents disagree, DOCURA must surface the disagreement and **may not resolve it by rule, recency, or preference**." | Governs FR-INF-004/005 |
| **BR-010** | — | "Every value DOCURA places must be attributable to a source document or to an answer the user gave." | Traceability |
| **BR-012** | — | "A value entered or corrected by the user always takes precedence over an extracted value and is never overwritten automatically." | User precedence |
| **BR-020** | — | "An **attribute** or field classified consequential can never be reclassified downward by any actor." | Sensitivity floor |

### 2.4 The requirements that constrain where the vocabulary lives and what it may cost

| ID | Release / Priority | Requirement | Constraint imposed |
| --- | --- | --- | --- |
| **NFR-MNT-001** | MVP · MUST | "Supported document types and their extractable fields shall be definable as **configuration**, so adding a type does not require re-engineering." | Speaks of *types and fields*. It does **not** mention attributes — see §7.2 |
| **NFR-MNT-004** | MVP · SHOULD | "Sensitivity classification rules shall be maintainable as a **reviewable list**, not scattered through the implementation." | Rules that attach to attributes must be reviewable |
| **NFR-USE-005** | MVP · SHOULD | "Product language shall name things as users do — 'marksheet', 'photograph', 'declaration' — not as the system models them." | A user-facing name is required wherever the system shows a thing to a user |
| **BR-017** | — | "DOCURA stores what it needs to serve a function the user asked for, and no more." | Data minimisation applies to the vocabulary itself |
| **NFR-PRIV-001** | MVP · MUST | "The system shall collect only information required to deliver a function the user has requested." | Same |
| **AR-AST-008** | MVP | "Assisted components shall be evaluated against a held-out corpus of real, imperfect documents **before any threshold is set**." | An evaluation is evidence only against a stated vocabulary version |
| **§6 Selection Principle** | — | "Any component may be replaced provided its replacement meets the same guarantees…" | The vocabulary must not be derived from an engine's output |

### 2.5 The assumption that constrains the whole area

> **A-5** (§12.3) — if it fails, "The sensitivity boundary is wrong; interruption frequency is wrong in one direction or the other." · Affects **FR-SENS-001…006, NFR-USE-002**.

> **A-7** (§12.3) — if it fails, "Extraction is unreliable on real scans; thresholds may exclude most automatic action." · Affects **FR-OCR-004…006, BR-001**.

A vocabulary whose sensitivity tiers are load-bearing (FR-INF-007) inherits **A-5**'s untested status for those tiers. This is why §15.3 holds the tier *content* as TBD while §15.1 requires the tier *slot*.

---

## 3. Existing Vocabulary / Attribute References

### 3.1 Method

The full text of all thirty-nine pages of `backend/step3.pdf` was extracted and searched, case-insensitively, for every term the brief lists. Counts below are occurrences in the extracted text. Every hit was read in context and classified. **No requirement was inferred; absence is reported as absence.**

### 3.2 Term-by-term search result

| Term searched | Occurrences | Where, and in what sense |
| --- | --- | --- |
| **canonical** | **1** | FR-ACC-004 only — "canonical personal attributes". Names the concept, defines nothing |
| **vocabulary** | **0** | **The word does not appear in the specification** |
| **schema** | **0** | Does not appear |
| **property** | **0** | Does not appear |
| **alias** | **0** | Does not appear |
| **synonym** | **0** | Does not appear |
| **metadata** | **0** | Does not appear — the term is this project's, not the specification's |
| **name/value**, key/value | **0** | Does not appear |
| **attribute** | 21 | FR-ACC-004; FR-INF-002/003/004/007/008/009; FR-SRCH-003; FR-SENS-001/006; NFR-SEC-003; NFR-REL-005; BR-020; AC-US-005-1/2; EC-004; EC-019; §6.4; §7.1 lifecycle; §8 Table 8.1; FR-FLD-001. **All but one are the stored-attribute sense.** FR-FLD-001's "declared attributes" is HTML attributes on a form input — form-field sense |
| **identifier** | 4 | §0.1 "Identifier scheme" — **identifiers for requirements in this document**, not for data; NFR-SEC-003 "an identifier supplied by the client"; NFR-ERR-004 "internal identifiers" must not leak; §9 Table 9.1 restating NFR-SEC-003. **No requirement establishes an identifier for an attribute** |
| **semantic** | 3 | AR-AST-003 "a semantic label" for a **form field**; Table 6.1 "matching values to options semantically"; Table 8.1 "Semantic interpretation with confidence". **All three are the form-field sense** |
| **normalis*** | 4 | FR-INF-008; AR-DET-003; Table 6.1 (deterministic layer may be trusted for "normalisation"); §7.1 lifecycle table (by reference) |
| **structured** | 7 | FR-INF-001 and §1.5's title; §7.1 ("not extracted into the structured record", "no structured extraction"); Table 8.1 ("From the structured record only"); §10.1 D3; Appendix B |
| **extracted** | 20+ | FR-OCR-005/006/007; FR-INF-003; FR-SRCH-002; NFR-SEC-002; NFR-PRIV-002/003/007; FR-ACC-002/006; NFR-USE-001; AR-AST-001; BR-002; BR-012; AC-US-003-1/2, AC-US-004-1/2/4; AC-US-019-3; §7.1; §10.1 D2 |

### 3.3 Step 1 findings table

| Requirement ID | Exact concept | What it **defines** | What it does **NOT** define |
| --- | --- | --- | --- |
| **FR-ACC-004** | "canonical personal attributes" | That a *profile* of them exists, is derived from documents, and is user-editable | What "canonical" means; which attributes; any identifier, name, type, or rule. **The word appears once and is never elaborated** |
| **FR-INF-001** | "structured record… assembled from all processed documents" | That one record spans all documents | Its contents; its relation to FR-ACC-004's profile (**G-19**) |
| **FR-INF-002** | "every attribute value… document it came from and the confidence" | **Per-value provenance is mandatory and complete** | What an attribute is; how a document reference is represented |
| **FR-INF-003** | "correct any attribute value"; user value "authoritative" | Correction precedence, fully | Which attributes are correctable (all, by implication); the correction's representation |
| **FR-INF-004** | "different values for **the same attribute**" | That disagreement must be detected, and (via AR-DET-008) **deterministically** | **The identity relation itself.** Nothing states when two values are "the same attribute", and nothing states when two values are "different" |
| **FR-INF-005/006** | conflict presentation; retained alternatives | That resolution is never automatic; alternatives are kept | The conflict's lifecycle; where alternatives live |
| **FR-INF-007** | "every attribute… routine, sensitive, or consequential" | **Three tier names, and that the tier attaches to the attribute** | Which tier for which attribute (**G-14**); the default tier (**G-15**) |
| **FR-INF-008** | "normalise **attribute formats**… dates, casing, spacing, and numeric precision" | That normalisation is per-attribute-format, deterministic, meaning-preserving; **four categories** | **No rule for any category.** No canonical date form, casing rule, spacing rule, or precision rule |
| **FR-INF-009** | "history of changes to each attribute… who or what" | That change history records the actor | Which history (**G-28**); the change record's shape |
| **FR-SRCH-003** | "search by attribute value" | That attributes are searchable | Addressing — by what handle a user or query names an attribute |
| **FR-SENS-001** | tier for "stored attributes and detected form fields" | That one classification spans both | The rules (**G-14**) |
| **FR-SENS-006 / BR-020 / AR-AST-007** | raise-only sensitivity | **Monotonicity, fully specified** | — |
| **AR-DET-003** | "deterministic and **reversible**" normalisation | Determinism **and reversibility** — reversibility appears here and nowhere else | What reversibility obliges (retention of the raw value is implied, never stated) |
| **AR-DET-008** | "conflict detection… deterministic" | That the comparison cannot be probabilistic | The comparison function |
| **NFR-REL-005** | "duplicate attribute entries" | That duplicates must not arise | What a duplicate *is* (**G-20**) |
| **NFR-MNT-001** | "types and their extractable **fields**… configuration" | That **fields** live in configuration | Anything about attributes — the word is absent from this requirement (§7.2) |
| **NFR-USE-005** | "name things as users do" | That user-facing language is the user's, not the system's | That an attribute carries a display label — it constrains product surfaces, not data definitions |
| **EC-019** | "the same attribute… twice in one form" | Required behaviour: fill consistently, flag divergence | The identity relation, again |
| **§0.1** | "Identifier scheme… never reused" | Identifier discipline **for requirements in this specification** | Nothing about product data. **This must not be cited as a requirement for attribute identifiers** (§16.2) |

### 3.4 The finding

**Across 39 pages, the specification uses "attribute" twenty-one times, requires an identity relation over attributes in four MUST requirements and three acceptance criteria, requires that relation to be deterministic (AR-DET-008), and defines the relation nowhere. The words *vocabulary*, *schema*, *property*, *alias*, *synonym*, and *metadata* do not occur at all. The word *canonical* occurs once.**

---

## 4. G-12 V1–V7 Scope Verification

G-12 §10.2 lists seven items as belonging to G-13. Each is reproduced in this document's own words, checked against `backend/step3.pdf`, and either accepted, refined, or reassigned. **V1–V7 were not accepted on G-12's authority.**

### V1 — The enumeration of canonical attributes

**Meaning:** the list of things DOCURA knows about a person, independent of any document.
**Requirement served:** FR-ACC-004 ("canonical personal attributes"); FR-INF-001.
**Genuinely G-13?** **Yes.** It is the artefact's substance.
**Becomes a G-13 decision?** **No — and this is the important correction.** The enumeration is *content*, and content cannot be produced by analysis without inventing it. G-13 can decide the **shape** an entry takes and **who authors** it; the entries themselves are a Product Management authoring task that this document must not perform. Recorded as an exit criterion (§18 X6), not a decision.
**Dependency:** BR-017 / NFR-PRIV-001 bound its size (§15.1, G-13.12); A-5 bounds its sensitivity tiers.

### V2 — Each attribute's canonical identifier and user-facing name

**Meaning:** a stable machine handle, plus the word shown to a person.
**Requirement served:** G-12 cites FR-ACC-004 and NFR-USE-005.
**Genuinely G-13?** **Yes for both, but on different footing, and G-12's citation is partly unsupported.**

- **User-facing name:** NFR-USE-005 (MVP, SHOULD) does require product language to name things as users do, and FR-SENS-003, FR-AMB-002, FR-REV-002 and FR-INF-002 all put attribute values in front of a user. The requirement constrains *surfaces*, not *definitions* — so a display label is strongly supported but is not, strictly, a stated property of an attribute. Classified **REQUIRED TO RESOLVE G-13, supported by NFR-USE-005** (§9).
- **Canonical identifier:** **not required by `step3.pdf` at all.** No requirement establishes an identifier for anything in the product's data. See §16.2 — G-12 §11's **G-12.4** cites **§0.1** as the source for a stable field identifier; §0.1 governs *requirement* identifiers in the specification document and says nothing about product data. That citation does not support the property. The property is still necessary — FR-INF-004 needs a decidable identity and AR-DET-008 requires it to be deterministic — but it must be labelled a **new product decision**, not an existing requirement.

**Becomes a G-13 decision?** **Yes** — G-13.2 (shape), G-13.4 (stability).
**Dependency:** none.

### V3 — Each attribute's meaning: the identity relation that makes "the same attribute" decidable

**Meaning:** a written definition precise enough that two people mapping two different documents reach the same answer.
**Requirement served:** **FR-INF-004** (MUST), reinforced by AR-DET-008 (detection must be deterministic), AC-US-005-1/2, EC-019, FR-INF-001.
**Genuinely G-13?** **Yes — this is the load-bearing item, and it is the one V1–V7 gets most right.**
**Becomes a G-13 decision?** **Yes** — G-13.3, which is the single most consequential proposal in this document.
**Dependency:** none upstream. Everything attribute-shaped is downstream of it.
**Verification note:** `step3.pdf` uses the phrase "the same attribute" three times (FR-INF-004, EC-019, §6.4) and never defines it. Confirmed by full-text search. G-12's characterisation of this as "the hard dependency" is accurate.

### V4 — Each attribute's value type and normalisation rule

**Meaning:** what kind of value it holds, and how that value is put into a canonical form.
**Requirement served:** FR-INF-008, AR-DET-003.
**Genuinely G-13?** **Yes, but the two halves have different status and must not be merged:**

- **Normalisation rule — REQUIRED BY EXISTING SPECIFICATION.** FR-INF-008 says "normalise **attribute formats**". The requirement attaches normalisation to the attribute by its own wording. Per-attribute rules are therefore G-13's by the specification's own construction, not by this document's preference.
- **Value type — not named anywhere.** FR-INF-008's categories ("dates… numeric precision") imply that some values are date-shaped and some number-shaped, but no requirement assigns a type to anything, and FR-FLD-007's seven types are **form-input** types, not value types. Classified **REQUIRED TO RESOLVE G-13**: a deterministic normaliser (AR-DET-003) cannot be selected without knowing what it is normalising.

**Becomes a G-13 decision?** **Yes** — G-13.2 and G-13.5.
**Dependency:** the *content* of each rule is authoring work; §15.3 holds the rules themselves open.

### V5 — Each attribute's sensitivity tier and the rules that assign it

**Meaning:** which of routine / sensitive / consequential the attribute carries, and why.
**Requirement served:** FR-INF-007 (MUST), FR-SENS-001, AR-DET-005, NFR-MNT-004.
**Genuinely G-13?** **Partly. G-12 assigned this wholly to G-13; that is too broad and this document splits it:**

- **The tier slot is G-13's.** FR-INF-007 says "**Every attribute** shall carry a sensitivity classification". The tier attaches to the attribute, so the vocabulary must carry it or FR-INF-007 has nowhere to live. **REQUIRED BY EXISTING SPECIFICATION.**
- **The rules that populate the slot are G-14's**, and the default for an attribute no rule covers is **G-15's**. Both are separately registered gaps. Both depend on assumption **A-5**, which §12.3 records as untested. G-13 must not author them.

**Becomes a G-13 decision?** **Yes, narrowed** — G-13.9: the slot is mandatory and no attribute ships without a tier; the content is delegated.
**Dependency:** **G-14, G-15, A-5.** **G-13-A** can be reached with the slot defined and empty of policy; **G-13-B** requires every tier assigned; **neither gate may be reached with the slot absent** (revised G-13.9).

### V6 — The relationship between FR-ACC-004's "profile" and FR-INF-001's "structured record"

**Meaning:** whether these are one thing under two names, or two things.
**Requirement served:** FR-ACC-004, FR-INF-001, FR-INF-003.
**Genuinely G-13?** **No — this is G-19, and reassigning it matters.** It is separately registered in the decision register as **G-19** ("FR-ACC-004's 'profile' and FR-INF-001's 'structured record' are never distinguished or unified"), described there as defining the central data model, and the register's **D-08** treats it as a data-model decision with an architecture component. It is not a property of an attribute and cannot be settled by naming attributes.
**Becomes a G-13 decision?** **No.** It is recorded here as an **upstream dependency and a risk to G-13's shape** (§16.1): if profile and record turn out to be two stores rather than two views, the vocabulary may need to state which store an attribute belongs to — a property not currently in §9's minimum set.
**Verification note:** G-12 §10.2 listing V6 as G-13's is the one item this verification rejects outright.

### V7 — What constitutes a duplicate attribute entry

**Meaning:** when two stored entries are the same entry.
**Requirement served:** NFR-REL-005 (SHOULD).
**Genuinely G-13?** **No — this is G-20, and it is *downstream* of G-13, not part of it.** The register's D-08.4 enumerates four candidate identities; one of them — `(document, canonical attribute, normalised value)` — uses FR-INF-008 normalisation as the identity function and therefore **needs** G-13's output. The other three do not. Choosing between them is a data-model and idempotency decision (register D-08.4 recommends run-scoped superseding extraction, explicitly "not a requirement").
**Becomes a G-13 decision?** **No.** Recorded as a **consumer** of G-13 (§16.1): whichever identity G-20 picks, if it is the normalised-value one, it inherits G-13.5's re-approval consequence.

### 4.1 Verification outcome

| Item | G-12 §10.2 said | This verification says | Change |
| --- | --- | --- | --- |
| V1 | G-13 | G-13 — but it is **content**, an exit criterion, not a decision | Refined |
| V2 | G-13, citing FR-ACC-004 + NFR-USE-005 | G-13 — display label supported by NFR-USE-005; **identifier is a new product decision, and G-12.4's §0.1 citation does not support it** | **Corrected** |
| V3 | G-13 — the hard dependency | **Confirmed exactly** | None |
| V4 | G-13 | G-13 — **normalisation rule is an existing requirement (FR-INF-008 "attribute formats"); value type is new** | Split |
| V5 | G-13 | **Slot** is G-13 (FR-INF-007); **rules** are G-14; **default** is G-15; all gated by A-5 | **Split and narrowed** |
| V6 | G-13 | **G-19** — upstream dependency, not a G-13 decision | **Reassigned** |
| V7 | G-13 | **G-20** — downstream consumer, not a G-13 decision | **Reassigned** |

**Net: five of seven items survive as G-13 concerns, two are reassigned to their own registered gaps, and one citation in G-12 §11 is corrected. `step3.pdf` contradicts none of V1–V7; it simply supports less of them than G-12 §10.2 implies.**

---

## 5. Current Specification State

The specification's treatment of the canonical vocabulary has the same shape as its treatment of per-type fields, with one difference that makes G-13 harder.

**The same shape:** every *property* an attribute must carry is required — provenance, confidence, sensitivity tier, normalisation, correction precedence, change history — and no attribute is ever named. The specification defines the envelope, not the contents.

**The difference that makes G-13 harder than G-12:** G-12's gap is a missing *list*. G-13's gap is a missing *relation*. FR-INF-004 does not merely lack examples — it performs an operation ("the same attribute") on a relation that is never defined, and AR-DET-008 requires that operation to be **deterministic**. A missing list can be authored. A missing relation must be *decided* before it can be authored, because two reasonable people will draw it differently. This is why §15.1's G-13.3 is the pivotal proposal and why it is a decision rather than an authoring task.

**Neither gap is marked in the specification.** §2's preamble marks a needed-but-unknowable number as "TBD — to be validated" and assigns it a study; fourteen such markers exist and §15.1 acknowledges twelve threshold-dependent requirements. **FR-ACC-004 and FR-INF-004 carry no TBD marker.** The specification does not appear to know the vocabulary is missing.

---

## 6. What Is Defined

Precisely these things **are** defined about attributes, and are testable or implementable as structural properties today:

1. **That a profile of canonical personal attributes exists, derived from documents and user-editable** — FR-ACC-004.
2. **That one structured record spans all processed documents** — FR-INF-001.
3. **That every attribute value carries provenance**: the document it came from and the confidence it was read with — FR-INF-002; reinforced by BR-010 and §10.1 D3. **The strongest-specified property in the area.**
4. **That any attribute value is user-correctable and the user's value becomes authoritative** — FR-INF-003, BR-012, AC-US-004-2/3.
5. **That conflicts are detected deterministically, surfaced, and never auto-resolved** — FR-INF-004, FR-INF-005, AR-DET-008, BR-004, EC-004, §6.4.
6. **That the alternatives are retained when the user designates one value authoritative** — FR-INF-006.
7. **That every attribute carries exactly one of three named tiers** — FR-INF-007, FR-SENS-001; raise-only (FR-SENS-006), with a consequential floor (BR-020) and assisted components unable to remove a tier (AR-AST-007). **The tier names are defined; nothing else about tiers is.**
8. **That attribute formats are normalised deterministically, reversibly, and without altering meaning, across four named categories** — FR-INF-008, AR-DET-003, Table 6.1.
9. **That a change history records who or what changed an attribute** — FR-INF-009.
10. **That attribute values are searchable and return the supporting document** — FR-SRCH-003.
11. **That repeating an operation must not create duplicate attribute entries** — NFR-REL-005.
12. **That an unresolved conflict makes a dependent form field ambiguous** — AC-US-005-2, EC-004, FR-AMB-001.
13. **That the same attribute appearing twice in one form is filled consistently, and a divergence after a user override is flagged at review** — EC-019.
14. **That user-facing language is the user's, not the system's** — NFR-USE-005.
15. **That the record belongs to the user: inspectable, correctable, exportable, deletable** — BR-018, FR-ACC-006/007.

**Items 1–15 constitute a complete specification of what happens *to* an attribute and no specification of what an attribute *is*.**

---

## 7. What Is Not Defined

### 7.1 The vocabulary itself

| # | Not defined | Consequence |
| --- | --- | --- |
| 1 | **Which attributes exist** — no attribute is named anywhere **in `backend/step3.pdf`** (§19.3 confirms this by a second, data-side full-text search) | FR-ACC-004's profile has no contents. **§19's T1 pass proposes one entry; the specification still names none** |
| 2 | **The identity relation** — when two values are "the same attribute" | **FR-INF-004 is not implementable, and AR-DET-008 requires it to be deterministic** |
| 3 | **The difference relation** — when two values of one attribute are "different" | Whether "Priya Sharma" and "PRIYA SHARMA" conflict depends entirely on a normalisation rule that does not exist |
| 4 | **Any identifier for an attribute** | Nothing to key storage, configuration, ground truth, or evaluation on |
| 5 | **Any name for an attribute** | Nothing to show a user (NFR-USE-005) and nothing to write in a conflict prompt (FR-AMB-002) |
| 6 | **Any value type** | No normaliser can be selected |
| 7 | **Any normalisation rule** — four categories are named, no rule is stated | FR-INF-008 is a MUST with no content |
| 8 | **Multiplicity** — whether an attribute may legitimately hold more than one value | **FR-INF-004 cannot distinguish a conflict from two legitimate values** |
| 9 | **What happens to an extracted value that maps to no attribute** | See §12 — there is no such path in the specification |
| 10 | **Versioning of the vocabulary** | An evaluation result cannot be attributed to a definition (AR-AST-008, G-03) |
| 11 | **Aliases or document-specific labels** | Not defined — and §9 concludes they are not needed in the vocabulary |

### 7.2 A specific and easily-missed absence: NFR-MNT-001 does not cover the vocabulary

**NFR-MNT-001** (MVP, MUST) reads: "**Supported document types and their extractable fields** shall be definable as configuration, so adding a type does not require re-engineering."

It names **types** and **fields**. **It does not name attributes.** The canonical vocabulary is a *third* artefact, and no requirement in `step3.pdf` says where it lives, in what form, or who may change it. G-12 §11's **G-12.1** correctly grounds the *field sets* in NFR-MNT-001; the same grounding is **not available** for the vocabulary. **G-13.1 is therefore a new product decision, not an application of an existing requirement** — and §15.1 labels it accordingly. NFR-MNT-004 (sensitivity rules as a reviewable list) is the closest support and covers only the tier rules, which are G-14's.

### 7.3 Adjacent gaps that are not G-13's to close

| Gap | Subject | Relation to G-13 |
| --- | --- | --- |
| **G-14** | The sensitivity classification rules are not in `step3.pdf` | Populates G-13's tier slot. Gated on A-5 |
| **G-15** | No default tier for an attribute no rule covers | Same |
| **G-19** | Profile vs structured record | **Upstream** — may change G-13's shape (§16.1) |
| **G-20** | What a duplicate attribute entry is | **Downstream** — one candidate identity consumes G-13's normalisation |
| **G-27** | FR-OCR-009's manual-entry path has no destination | Downstream of G-12 and G-13 |
| **G-28** | Which history a conflict resolution appears in | Independent; affects FR-INF-009's record, not the vocabulary |
| **G-06** | Confidence has no scale or semantics | Independent of G-13 — confidence is per value, not per attribute |

---

## 8. G-13 Requirements Gap

### 8.1 Statement of the gap

**G-13 — `backend/step3.pdf` requires a user profile of "canonical personal attributes" (FR-ACC-004, MVP, MUST) and the deterministic detection of two documents disagreeing about "the same attribute" (FR-INF-004, MVP, MUST + AR-DET-008), and defines neither the attributes nor the identity relation. The word *canonical* appears once in thirty-nine pages; the words *vocabulary*, *schema*, *property*, *alias* and *synonym* appear zero times.**

### 8.2 What this gap is not

- **It is not a naming exercise.** Choosing labels is trivial; choosing the *identity relation* (§15.1, G-13.3) changes what the product detects as a conflict, and therefore how often it interrupts a user. That is a product behaviour decision.
- **It is not a TBD in the specification's own sense.** FR-ACC-004 and FR-INF-004 carry no TBD marker and no study reference, unlike BR-001's threshold.
- **It is not covered by NFR-MNT-001** (§7.2) — that requirement names types and fields, not attributes.
- **It is not resolvable by engineering judgement.** The vocabulary defines what DOCURA *knows about a person*. Under **BR-017** and **NFR-PRIV-001**, deciding it is a privacy decision as much as a data-modelling one.
- **It is not blocked on the corpus.** G-02 is approved and collection is a separate track; the vocabulary is authored from requirements, not from documents. D-02 §18 records G-02 and G-13 as the two independent roots that can be worked in parallel.

### 8.3 Consequences — what is blocked

Statuses reproduced from the decision register's readiness matrix, verified against `step3.pdf`.

| Requirement | Priority | Consequence |
| --- | --- | --- |
| **FR-ACC-004** | MUST | Profile of canonical attributes has no contents (with **G-19**) |
| **FR-INF-001** | MUST | Structured record has no contents (with **G-19**) |
| **FR-INF-002** | MUST | The provenance *structure* is READY; the subject it attaches to is missing |
| **FR-INF-003** | MUST | Correction precedence is fully specified; there is nothing to correct |
| **FR-INF-004** | MUST | **Not implementable — "the same attribute" is undefined** |
| **FR-INF-005** | MUST | Never-auto-resolve is READY as an invariant; detection is blocked |
| **FR-INF-006** | MUST | Alternatives are alternatives for an undefined subject |
| **FR-INF-007** | MUST | Nothing enumerable to classify (also **G-14**, **G-15**) |
| **FR-INF-008** | MUST | **No attribute to attach a normaliser to; no rule stated for any category** |
| **FR-INF-009** | SHOULD | No subject; also **G-28** |
| **FR-SRCH-003** | SHOULD | No addressable attributes |
| **NFR-REL-005** | SHOULD | No attribute-level meaning (**G-20**) |
| **AR-DET-003** | MVP | No per-attribute normalisation rules |
| **AR-DET-008** | MVP | Deterministic detection has no deterministic comparison function |
| **US-005** | MUST | **Blocked in full** — every one of its acceptance criteria depends on the vocabulary |
| **AC-US-005-1/2/3** | — | Not executable as tests |
| **§10.1 step D3** | — | "A structured record assembled, each value linked to its source" is not demonstrable |
| **D-02 §11.6** | — | Conflict-detection evaluation cannot be designed against a subject that does not exist |
| **D-02 §7.1 layers L6, L7** | — | Not annotatable |
| **G-12 in full** | — | Per-type field sets cannot map fields to attributes that do not exist |

---

## 9. Minimum Canonical Attribute Definition

Twelve candidate properties, each classified and reasoned. **Classifying a property as required is not the same as supplying its content**; every property below is a slot, and every slot is empty.

Classifications: **REQUIRED BY EXISTING SPECIFICATION** · **REQUIRED TO RESOLVE G-13** · **RECOMMENDED** · **NOT REQUIRED / OUT OF SCOPE** · **TBD**

| # | Property | Classification | Reasoning |
| --- | --- | --- | --- |
| 1 | **Canonical identifier** — a stable machine handle | **REQUIRED TO RESOLVE G-13** | Not named in `step3.pdf` (§3.2: zero occurrences in a data sense). Necessary because FR-INF-004 needs a decidable identity and AR-DET-008 requires the decision to be deterministic; a display label cannot serve, because NFR-USE-005 makes labels answerable to user language and therefore changeable. **§0.1 does not support this — see §16.2.** New product decision |
| 2 | **Canonical name** — a second human-readable name distinct from both the identifier and the display label | **NOT REQUIRED / OUT OF SCOPE** | Three names for one thing is three things to keep in sync. The identifier serves machines; the display label serves users (NFR-USE-005). No requirement asks for a third. Excluding it is the smaller artefact and the smaller failure surface |
| 3 | **Display label** — the word shown to a person | **REQUIRED TO RESOLVE G-13**, supported by **NFR-USE-005** (SHOULD) | Attribute values reach users in ambiguity prompts (FR-AMB-002 "shall state the field"), approval requests (FR-SENS-003), review (FR-REV-002), extraction review (AC-US-003-2) and conflict resolution (FR-INF-005). NFR-USE-005 requires that language be the user's. It constrains *surfaces* rather than *definitions*, so the property is necessary rather than literally required |
| 4 | **Semantic definition** — prose precise enough that two authors mapping two documents agree | **REQUIRED TO RESOLVE G-13 — the pivotal property** | FR-INF-004 + AR-DET-008 require a deterministic answer to "the same attribute". Determinism at the *comparison* step is worthless if the *mapping* step is a judgement call, because the error simply moves upstream into G-12's authoring. The definition is what makes the mapping repeatable. **Not named in `step3.pdf`** |
| 5 | **Aliases / synonyms** | **NOT REQUIRED / OUT OF SCOPE — belongs to G-12** | Zero occurrences in `step3.pdf`. A document's printed label is captured by G-12's field→attribute mapping, which G-12 §11's **G-12.4** already requires ("Canonical attribute mapping, or explicitly none"). An alias list in the vocabulary would duplicate that mapping in a second place and let the two disagree. Form-field labels are a different problem entirely, already solved probabilistically by FR-FLD-001 / AR-AST-003 |
| 6 | **Data type** | **REQUIRED TO RESOLVE G-13** | FR-INF-008 names date-shaped and number-shaped categories, so types exist in effect; no requirement assigns one. AR-DET-003 requires normalisation to be *deterministic*, which is not decidable without knowing what is being normalised. FR-FLD-007's seven types are **form-input** types and must not be reused here |
| 7 | **Normalisation rule** | **REQUIRED BY EXISTING SPECIFICATION** | **FR-INF-008 attaches normalisation to the attribute by its own wording — "normalise attribute formats".** With AR-DET-003 (deterministic and reversible). The requirement exists; the rule content does not (§11) |
| 8 | **Multiplicity / cardinality** — *scope-keyed; see the note below* | **REQUIRED TO RESOLVE G-13** | **Not defined in step3.pdf.** Necessary because FR-INF-004 cannot otherwise distinguish "two documents disagree" (a conflict, BR-004) from "this attribute legitimately holds two values" (not a conflict). Getting this wrong produces either false conflicts — which D-02 §11.6 identifies as the failure mode that satisfies FR-INF-004 literally while making the product unusable — or silently missed ones |
| 9 | **Document-type applicability** — which types can supply this attribute | **NOT REQUIRED / OUT OF SCOPE — belongs to G-12** | The mapping direction the artefacts already establish is field→attribute (G-12.4). Recording the inverse in the vocabulary is derivable, duplicated, and a second place to be wrong. It would also couple the vocabulary to the §7.1 type set, which is provisional under ASM-001 and subject to S-6 demotion |
| 10 | **Sensitivity tier** | **REQUIRED BY EXISTING SPECIFICATION (the slot only)** | **FR-INF-007 (MUST): "Every attribute shall carry a sensitivity classification of routine, sensitive, or consequential."** The slot is mandatory and must exist in the vocabulary or the requirement has nowhere to live. **The assignment rules are G-14 and the default is G-15**, both gated on untested assumption **A-5**. §15.1's G-13.9 requires the slot and delegates the content |
| 11 | **Provenance** | **NOT REQUIRED / OUT OF SCOPE — it is a property of the value, not the definition** | FR-INF-002 attaches provenance to "every attribute **value**". The register records the provenance *structure* as READY. Putting it in the definition would be a category error: one definition, many values, one provenance each |
| 12 | **Confidence** | **NOT REQUIRED / OUT OF SCOPE — property of the value** | FR-OCR-005 attaches confidence to each extracted field value. Its scale and semantics are **G-06**, independent of G-13 |
| 13 | **Vocabulary version** *(added by this analysis; not on the brief's list)* | **RECOMMENDED — at artefact level, not per attribute** | AR-AST-008 requires evaluation before any threshold is set; an evaluation against a superseded vocabulary is not evidence for a threshold. Related to **G-03**. Parallel to G-12 §11's G-12.8 |

### 9.0.1 Property 8 revisited — why it is scope-keyed

**REVISION, 6 September 2026. Driver: [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) §5.5, §6.**

Property 8's justification above is that **FR-INF-004 cannot otherwise distinguish "two documents disagree" from "this attribute legitimately holds two values."** That is the correct job. A two-value domain of `single | repeating` cannot do it.

A person legitimately holds several qualifications. The concept "year of passing" has one value for a 10th qualification, another for a 12th, another for a degree. Under the domain as first written, both settings are wrong:

- **`single`** — three values for one identifier is a conflict by construction, so FR-INF-004 fires on every multi-qualification person and **BR-004** forbids resolving it by rule. The consequence chain is verified in §11.4.1.
- **`repeating`** — suppresses those false conflicts *and* the true ones together: two documents disagreeing about the **same** qualification's year become two legitimate values, and FR-INF-004 goes silent on a real disagreement. Property 8's own reasoning names that outcome — "or silently missed ones".

`single | repeating` is a one-bit answer to a grouping question: it says *how many*, and cannot say *how many per what*.

**The property was in the right place and was given too narrow a domain for the purpose §9 assigned to it.** The revision widens the domain; it does not add a property, and it does not move the job elsewhere. This is why the revision is a redefinition of property 8 rather than an eighth property — **an eighth `scope` property would leave two properties answering one question, which is the duplication test §9 itself used to reject aliases (property 5) and document-type applicability (property 9).**

### 9.1 The minimum set

**Seven properties per attribute:** canonical identifier · display label · semantic definition · data type · normalisation rule · **scope-keyed multiplicity** · sensitivity tier — plus **one artefact-level version**.

**The count is seven, unchanged. No eighth property is introduced.** Property 6 in G-13.2's ordering (multiplicity) carries the scope key; §9.0.1 gives the reasoning and **G-13.2** states the revised wording.

**Two are existing requirements** (normalisation rule, sensitivity tier slot). **Five are new product decisions.** **Five candidate properties are excluded**, four of them because they belong to G-12 or to the value rather than the definition.

---

## 10. Cross-Document Consistency

**Does `step3.pdf` require that the same concept appearing in two document types have a consistent representation?**

**Not in those words. Not defined in step3.pdf as an explicit statement.**

**But the obligation is entailed by four MUST requirements that cannot function without it**, and this must be stated precisely so that an entailment is not mistaken for a quotation:

| Requirement | What it says | What it entails |
| --- | --- | --- |
| **FR-INF-001** (MUST) | The structured record is "assembled from all processed documents" | Assembly across documents is meaningless unless a concept read from two documents lands in one place |
| **FR-INF-004** (MUST) | Detect when "two documents give different values for **the same attribute**" | The relation is explicitly **cross-document** — the requirement's subject is two documents. This is the strongest entailment in the specification |
| **AR-DET-008** (MVP) | Conflict detection "shall be deterministic" | A cross-document relation that varies by document type is not deterministic |
| **AC-US-005-1** | "GIVEN two documents give different values for the same attribute… a conflict is raised" | Not executable unless cross-document identity holds |
| **EC-019** | "The same attribute is requested twice in one form… fill both consistently from the same authoritative value" | One authoritative value per attribute, regardless of which document supplied it |

**The honest formulation:** the specification never states a consistency rule, and it never states its converse either. It performs operations that presuppose consistency. **The obligation is real; the mechanism that achieves it is Not defined in step3.pdf.**

**What this document must not do with that finding:** treat "one representation is easier to build" as the basis. It is not the basis. The basis is FR-INF-004's cross-document subject and AR-DET-008's determinism requirement. Engineering convenience would point the same way, which is exactly why the requirement grounding must be stated explicitly rather than assumed.

**Bounded by:** **FR-INF-010** — "The system shall indicate which commonly required information is missing from the record" — is **FUTURE / WON'T**. The MVP record is therefore **not** required to know which attributes are absent. This usefully bounds the vocabulary: it must support consistency for attributes that are *present*, and is not obliged to enumerate a complete expected set for completeness reporting.

---

## 11. Normalization and Representation

Normalisation is the area where invention is most tempting and most damaging, because a normalisation rule silently *is* a conflict-detection rule (§11.4). This section states only what `step3.pdf` contains.

### 11.1 What the specification actually contains

| ID | Exact wording | Categories named |
| --- | --- | --- |
| **FR-INF-008** (MVP, MUST) | "The system shall normalise attribute formats deterministically — **dates, casing, spacing, and numeric precision** — without altering meaning." | dates · casing · **spacing** · numeric precision |
| **AR-DET-003** (MVP) | "Value normalisation — **dates, casing, whitespace, numeric precision** — shall be deterministic and **reversible**." | dates · casing · **whitespace** · numeric precision |
| **Table 6.1** | Deterministic automation may be trusted for "format conversion, resizing, validation, **normalisation**, threshold comparison…" | — |
| **§7.1 lifecycle table** | References the above; §0.3 confirms §7 "reference[s] rather than repeat[s]" | — |

**Four categories. Zero rules.** No canonical date representation, no casing rule, no whitespace rule, no numeric precision rule is stated for anything.

### 11.2 Two textual observations, recorded not resolved

1. **"spacing" (FR-INF-008) vs "whitespace" (AR-DET-003).** The specification uses two words for what appears to be one category. A minor vocabulary inconsistency of the same kind as "unrecognised" (FR-OCR-002) vs "unclassified" (§7.1, AC-US-003-3), recorded in G-12 §3.3. **This document does not choose between them**; it notes that the authored rules will have to.
2. **"reversible" appears in AR-DET-003 and not in FR-INF-008.** Reversibility is a real and unusual constraint: it means the normalised form must not destroy the original. Combined with FR-INF-002 (provenance per value) and FR-OCR-007 (the region a value was read from), the natural reading is that the raw extracted value is retained alongside the normalised one — **but `step3.pdf` never says so.** §15.1's **G-13.6** proposes it as the minimum way to satisfy AR-DET-003 and labels it a proposal, not a requirement.

### 11.3 The four distinctions the brief requires

| Concept | Status in `step3.pdf` | Owner |
| --- | --- | --- |
| **(a) Normalisation of an extracted value** | **PARTIALLY DEFINED.** Obligation is MUST (FR-INF-008), determinism and reversibility required (AR-DET-003), four categories named, **no rule stated for any of them** | G-13 (rules attach to attributes, per FR-INF-008's own wording) |
| **(b) Naming of the attribute itself** | **Not defined in step3.pdf.** No requirement names, identifies, or labels an attribute. Zero occurrences of *vocabulary*, *schema*, *property*, *alias*, *synonym* | G-13 (§9, properties 1 and 3) |
| **(c) Document-specific labels** — the words a marksheet or a PAN card actually prints above a value | **Not defined in step3.pdf. Never addressed at all.** The only "label" requirement about documents is FR-DOC-003, which is *the user's personal label for a document* — an unrelated concept that must not be conflated with it | **G-12** — absorbed by the field→attribute mapping (§9, property 5) |
| **(d) Canonical representation** — the stored normalised form | **PARTIALLY DEFINED.** FR-INF-008 requires it to exist, be deterministic and preserve meaning; AR-DET-003 adds reversibility. **Its shape is undefined for every category** | G-13 |

**A fifth operation, deliberately kept separate:** **FR-FILL-002** and **AC-US-008-4** require a value to be *reformatted to a third-party form's declared format* — "GIVEN a date field with a declared format different from the stored format… the value is reformatted to the field's format without altering the date". **This is output formatting at fill time, not storage normalisation.** It reads the canonical representation and writes something else. It is already specified, it is not G-13's, and the existence of AC-US-008-4 must not be mistaken for a defined stored date format — it is evidence that the stored format and the form's format are expected to differ.

### 11.4 Why normalisation is the highest-consequence part of G-13

**AR-DET-008 makes conflict detection deterministic. Determinism means the comparison is a function. The normalisation rule *is* that function.**

It follows that:

- Whether two values of one attribute "differ" (FR-INF-004) is decided entirely by the normalisation rule. A casing rule decides whether two spellings of a name are a conflict. A whitespace rule decides whether two renderings of an address are a conflict.
- **A change to a normalisation rule is a change to the product's conflict behaviour**, not a refactor. D-02 §11.6 makes this measurable: its *false-conflict source attribution* measure asks, for each false conflict, whether the cause was extraction error, normalisation, or genuine document variance — and observes that a system raising conflicts on every person because of inconsistent transcription "satisfies FR-INF-004 literally while making the product unusable".
- The register's **D-08.4** offers `(document, canonical attribute, normalised value)` as one candidate identity for **G-20**'s duplicate question, which would make the normalisation rule the duplicate-detection function as well.

This is the reasoning behind **G-13.5**.

### 11.4.1 Scope collapse — a fourth, distinct source of false conflict

**REVISION, 6 September 2026. Driver: [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) §5.2, §5.3.**

§11.4 above treats the normalisation rule as the whole comparison function. That is no longer accurate, and the gap it leaves has a name.

**Scope collapse** is what happens when two values that describe **different subjects** are compared because they share a canonical attribute identifier. Three documents reporting the year of passing of three different qualifications is the worked case. Extraction was correct. Normalisation was correct. The documents do not disagree about anything. A conflict is raised anyway.

**The consequence chain, every step quoted from `backend/step3.pdf`:**

| Step | Requirement | Text | Effect |
| --- | --- | --- | --- |
| 1 | **FR-INF-004** (MUST) | "detect when two documents give different values for the same attribute" | Fires |
| 2 | **AR-DET-008** (MVP) | detection "shall be deterministic" | Fires every time, for every such person |
| 3 | **FR-INF-005** (MUST) | "Detected conflicts shall be presented to the user for resolution. The system shall not resolve a conflict automatically." | Surfaced to the user |
| 4 | **BR-004** | "may not resolve it by rule, recency, or preference" | **No automatic escape exists** |
| 5 | **EC-004** | "Raise a conflict, mark neither authoritative, and **treat any field needing that attribute as ambiguous until the user resolves it**" | Field blocked |
| 6 | **FR-AMB-001** (MUST) | a field is ambiguous when "source documents conflict" | Autofill blocked for that field |
| 7 | **FR-INF-006** (MUST) | "record which value the user designated authoritative and **retain the alternatives**" | **The only clearing path demotes two correct values to "alternatives"** |

Step 7 is the sharpest point. To clear the conflict the user must designate **one** year of passing authoritative across three distinct qualifications. **The product's only conflict-clearing path destroys correct data**, and it does so for every user holding more than one qualification.

**Why this matters to the evaluation, and not only to the product.** D-02 §11.6's *false-conflict source attribution* measure offers three causes — extraction error, normalisation, or genuine document variance — on the stated premise that "a false conflict is always evidence about extraction or normalisation." **Scope collapse fails that premise.** It is neither extraction nor normalisation, and it is not genuine document variance either, since the documents vary about nothing. Under the three-way taxonomy every instance would be filed under "genuine document variance" — the category that reads as *no action needed*. **The gap would silently disarm the measure built to detect it.**

**Recorded for the owner of [`SPRINT_4_D02_OCR_EVALUATION_PLAN.md`](SPRINT_4_D02_OCR_EVALUATION_PLAN.md):** D-02 §11.6 needs a fourth attribution category — *scope-model error*. The revision analysis records the same recommendation at its **G-13R.11**. **APPLIED 8 September 2026:** D-02 §11.6.1 now records this fourth category — scope-model error (scope collapse) — closing exit criterion **X15** (§22.7; register D-05.14).

**This is the reasoning behind the revision to G-13.5.**

---

## 12. Unknown / Unrecognized Attributes

### 12.1 What the specification provides

`step3.pdf` provides an explicit "I do not know" outcome at **two** levels, and both are well specified:

| Level | Outcome | Requirements |
| --- | --- | --- |
| **Document type** | "unrecognised" / "unclassified" — the type is not forced | FR-OCR-002, AR-AST-002 ("shall be able to return 'unrecognised' rather than a forced choice"), AC-US-003-3, EC-003 ("Never force it into an expected slot"), §7.1 "Other" |
| **Form field** | "unknown" — the field is marked and left untouched | FR-FLD-006, AR-AST-003 ("shall be able to return 'unknown'"), FR-FILL-007, BR-009, EC-008, EC-010 |

### 12.2 What it does not provide

**There is no third path.** `step3.pdf` never addresses what happens to a value that is successfully read from a document but corresponds to no canonical attribute.

**Not defined in step3.pdf.**

Each adjacent requirement was checked and none covers it:

| Candidate | Why it does not cover the case |
| --- | --- |
| FR-OCR-002 / AR-AST-002 "unrecognised" | Document **type** level. The document here is classified fine |
| FR-FLD-006 / AR-AST-003 "unknown" | Third-party **form field** level. No form is involved at extraction time |
| §7.1 "Other" | Document **type** level — a whole document with no extraction, not a value within an extracted one |
| BR-009 "unknown information" | Governs **placing a value into a form field**; the enforcing requirements listed against it are FR-FLD-006, FR-FILL-007, FR-DRP-005, FR-MATCH-005 — all form-side |
| EC-002 "poor-quality document" | A value that could not be **read** confidently — the opposite case; here the value is read fine |
| FR-OCR-006 | Below the **review threshold** — a confidence outcome, not a mapping outcome |
| G-27 | The **manual-entry** path's destination — a different hole, downstream of the same absence |
| G-08 | The **store-and-search-only** state of a demoted type — type level again |

### 12.3 Why this matters more than it looks

Three MVP requirements route through this hole:

- **G-12's own interface.** G-12 §11's **G-12.4** requires each field to map to "one canonical attribute, **or explicitly none**". *Or explicitly none* has no defined destination. A field deliberately mapped to nothing is exactly the case this section describes.
- **FR-INF-007** requires every attribute to carry a sensitivity tier. A value that never becomes an attribute never acquires a tier — so an unmapped value is unclassified personal data sitting in the system with no sensitivity handling.
- **D-02 §11.7** (safety-relevant, DECISION REQUIRED) already raises the mirror case: whether a readable identifier number "is stored at all, masked, or stored in part", and warns that "the evaluation must not assume that every readable value is a value to be extracted."

### 12.4 Registered as a candidate new gap

**G-13.g1 (candidate new gap) — the specification defines no behaviour for an extracted value that maps to no canonical attribute.** The decision register currently holds G-01…G-28 and **this document does not modify it**; if this analysis is accepted, a register entry should be added by whoever owns that document.

A behaviour is **proposed, not assumed**, in §15.1 as **G-13.7**. Its shape follows the product's own instincts — **BR-009** forbids "inferring from similar fields", **BR-016** requires failing towards inaction, **AR-AST-007** forbids a component escalating its own authority, **EC-003** forbids forcing a thing "into an expected slot" — so the one option those rules exclude is coercing the value into the nearest-looking attribute. What *should* happen to it instead (discard, retain outside the record, or surface to the user) is a Product Management decision with a privacy consequence, and this document does not make it.

---

## 13. Relationship to G-12

### 13.1 Direction

```
G-13  canonical attribute vocabulary      "HOW is a concept represented consistently?"
  │      FR-ACC-004, FR-INF-001/004/007/008, FR-SRCH-003, EC-019, NFR-REL-005
  │      per attribute: identifier · label · meaning · type · normalisation ·
  │                     scope-keyed multiplicity · tier slot          (seven — no eighth)
  │
  │   GATE G-13-A  structural: properties 1–6 complete, tier slot TBD, NOT RELEASABLE
  │                └── unblocks G-12 authoring, L6/L7 design, D-02 §11.6 design
  │   GATE G-13-B  releasable: every tier assigned  ← G-14 / G-15 (A-5; S-1, S-4)
  │                └── unblocks implementation, production storage, and automatic
  │                    placement of a value (FR-INF-007; FR-SENS-002 / BR-005)
  │
  │   interface contract: each G-12 field maps to exactly ONE canonical attribute, or explicitly NONE
  ▼
G-12  per-type field sets                 "WHICH concepts exist for each document type?"
  │      FR-OCR-004/005, NFR-MNT-001            (needs G-13-A only, not G-13-B)
  ├──► G-09 / G-10 / G-11 / D-04.4 / D-04.7   type boundaries — G-12's dependencies,
  │                                            NOT the vocabulary's; run in parallel
  ├──► G-27                 manual-entry destination
  └──► L4 / L5 ground truth ──► D-02 §11 field extraction ──► §12 calibration ──► BR-001
  │
  └──(G-13 also feeds directly)──► L6 / L7 ──► D-02 §11.6 conflict detection
```

**G-13 is upstream.** G-12 §11's **G-12.3** already proposes this order from the G-12 side; this document confirms it from the G-13 side and, in **§15.1 G-13.8**, states it as G-13's own decision so that neither artefact depends on the other's approval to establish the ordering.

**G-13 also feeds D-02 directly**, not only through G-12: D-02 §7.1 attributes layers **L6** (which canonical attribute each field value maps to) and **L7** (the conflict inventory) to **G-13**, while **L4/L5** are attributed to **G-12**. D-02 §18 names G-02 and G-13 as the two independent roots of the whole dependency graph.

### 13.2 What G-13 must not decide

| G-13 must not decide | Because |
| --- | --- |
| Which attributes a marksheet, a PAN card, or any other document contains | That is G-12's field set, per type |
| The document-specific label printed above a value | G-12's field→attribute mapping absorbs it (§9, property 5) |
| Whether a type extracts at all | G-11 and D-04.6; §7.1's demotion rule and study S-6 |
| Whether a field is mandatory for a type | G-12 (question C in G-12 §7.1) |
| What happens when a document of a type lacks a field it should have | **G-12** — field-level absence. Distinct from the record-level completeness question, which is **FR-INF-010, FUTURE / WON'T** |

### 13.3 One correction to G-12 carried here

G-12 §11's **G-12.4** lists nine properties for a field definition and cites **§0.1** as the source for "Field identifier (stable, never reused)". §0.1 is the specification's **requirement**-identifier scheme; it governs IDs like `FR-OCR-004` inside the document and says nothing about product data. The property is still necessary — for the reasons in §9, property 1 — but its basis is a new product decision, not §0.1. **G-12's substance is unaffected; only the citation is over-broad.** Recorded in §16.2.

---

## 14. Evaluation Impact

### 14.1 The dependency chain, with G-13 located precisely

```
Document
   │   (G-02 corpus governance APPROVED; corpus not yet collected)
   ▼
OCR text ──────────────────► character/word accuracy, page coverage      NOT blocked by G-13
   │                          D-02 §8 · L3 annotatable today
   ▼
Document classification ───► precision/recall, unrecognised-rate         NOT blocked by G-13
   │                          D-02 §10 · L2 annotatable today (G-10 affects one boundary)
   ▼
Failure behaviour ─────────► retain original, state reason               NOT blocked by G-13
   │                          FR-OCR-009, EC-001 · manual-entry half blocked by G-27
   ▼
Engine eligibility ────────► confidence produced? "unknown" returnable?  NOT blocked by G-13
   │                          explainable? — §6 Selection Principle, D-02 §13
   ▼
Field extraction ──────────► per-field precision/recall                  blocked by G-12
   │                          L4/L5 · G-13 blocks it TRANSITIVELY, via G-12
   ▼
Canonicalised ground truth ► which attribute each value maps to          BLOCKED BY G-13 DIRECTLY
   │                          D-02 §7.1 layer L6
   ▼
Cross-document / conflict ─► conflict recall, precision,                 BLOCKED BY G-13 DIRECTLY
   │  evaluation              false-conflict attribution — D-02 §11.6, L7
   ▼
Calibration ───────────────► attribute-dependent calibration blocked;
   │                          also needs G-06 for the scale
   ▼
Threshold decision ────────► BR-001 / BR-002 — G-04, G-05, G-06, G-07 as well
```

### 14.2 Can proceed without G-13

| Stage | Blocked by G-13? | Basis |
| --- | --- | --- |
| **Corpus collection and governance** | **No** | G-02 approved; collection depends on §7.1 type names |
| **Ground truth L1 — document metadata** | **No** | D-02 §7.1; blocked only by D-02.i's degradation taxonomy |
| **Ground truth L2 — type label** | **No** | Needs §7.1 type names only (G-09/G-10 affect boundaries) |
| **Ground truth L3 — text transcription** | **No** | FR-OCR-001 imposes no structure |
| **OCR text evaluation** | **No** | D-02 §8 — FR-OCR-001, FR-OCR-008 |
| **Classification evaluation** | **No** | D-02 §10 — FR-OCR-002/003, AR-AST-002, AC-US-003-3 |
| **OCR failure behaviour** | **Partly** | FR-OCR-009's *retain the original* and *state the reason* halves are evaluable (EC-001, AC-US-003-5); the *manual-entry* half is **G-27** |
| **Engine eligibility screening** | **No** | §6 Selection Principle — confidence, "unknown", explainability all testable |
| **Normalisation determinism** | **No** | Same input → same output across runs is testable without knowing the rules |
| **Normalisation correctness** | **Yes** | Requires the per-attribute rules — D-02 §7.5 records this |

### 14.3 Requires G-13

| Stage | Basis |
| --- | --- |
| **Ground truth L6 — canonical attributes** | D-02 §7.1: "Which canonical attribute each field value maps to, per person" — blocked by G-13 |
| **Ground truth L7 — conflict inventory** | D-02 §7.1 — blocked by G-13 |
| **Conflict-detection evaluation** (D-02 §11.6 entirely) | Conflict recall, precision, false-conflict source attribution. "Attribute identity across documents is precisely what the missing vocabulary defines" |
| **Cross-document field evaluation** | Requires that a value on document A and a value on document B be comparable |
| **Field-level comparison against ground truth** | Requires a normalised comparison function (§11.4) |
| **Any calibration keyed on canonical attributes** | Per-attribute calibration has no key |
| **FR-INF-008 correctness evaluation** | Rules do not exist |
| **US-005 acceptance criteria as executable tests** | AC-US-005-1/2/3 — the register's D-12 records US-005 as the most completely blocked story |
| **Field extraction (L4/L5, D-02 §11)** | Blocked by **G-12** directly; by G-13 **transitively**, since G-12 cannot be authored first |

### 14.4 The honest statement of blockage

**G-13 does not block the OCR evaluation as a whole.** Stage 1 — OCR text quality, classification, failure behaviour, engine eligibility — is evaluable as soon as the corpus exists and is unaffected by the vocabulary. D-02 §3.2 states this and §19 already splits the exit criteria on exactly this line; D-02 §18 records G-02 and G-13 as **independent roots that can be worked in parallel**, one a legal-and-product task, the other a product-definition task.

**What G-13 blocks is the conflict-detection half of the evaluation directly, and the field-extraction half transitively through G-12.** Precision matters here: D-02 §7.1 attributes L4/L5 to G-12 and L6/L7 to G-13. Claiming G-13 blocks L4/L5 directly would overstate it; claiming it blocks nothing until G-12 closes would understate it, because L6/L7 and §11.6 are G-13's alone.

---

## 15. Proposed G-13 Resolution

**APPROVED 5 September 2026.** G-13.1 … G-13.14 below were proposed by this document and have since been approved as product decisions; they are binding on implementation as project decisions and are recorded in [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) **D-05.6**.

**REVISED 6 September 2026 — THE REVISION APPROVED 6 September 2026 (D-05.8).** Three of the fourteen are revised, a fourth has its trigger clarified without any change to its wording, and one new decision is added. **All five are approved as product decisions:**

| Decision | Change | Status |
| --- | --- | --- |
| **G-13.2** | Property 6 redefined from `single \| repeating` to a **scope-keyed cardinality**. **Property count unchanged at seven; no eighth property** | **REVISION APPROVED 6 Sep 2026** |
| **G-13.5** | Comparison function for FR-INF-004 qualified to operate **within a scope instance**; the re-approval consequence extended to scope rules | **REVISION APPROVED 6 Sep 2026** |
| **G-13.9** | Narrowed to release-time; closure split into **G-13-A** (structural) and **G-13-B** (releasable) | **REVISION APPROVED 6 Sep 2026** |
| **G-13.11** | Decision wording **unchanged**; its “until G-13 closes” **trigger clarified** to mean **G-13-A**, and approved gate-A content recorded as not a placeholder within its meaning | **CLARIFICATION APPROVED 6 Sep 2026** |
| **G-13.15** | *New* — the scope-instance resolution rule is a PM decision, constrained and **deliberately not made here** | **APPROVED 6 Sep 2026** — *the rule itself stays undecided (T12)* |

**G-13.3 is NOT reopened.** Identity remains established by the field→attribute mapping alone. **G-13.1, G-13.4, G-13.6, G-13.7, G-13.8, G-13.10, G-13.12, G-13.13 and G-13.14 stand exactly as approved** and their wording is preserved unchanged. **G-13.11's decision wording is likewise unchanged**, but the two-gate split made its “until G-13 closes” trigger ambiguous, so a **trigger clarification** is added below it — it narrows nothing and forbids nothing new. Driver for the revision: [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) §9.2 (G-13R.7, G-13R.8, G-13R.4/R5, G-13R.9).

**Neither the approval nor the revision amends `backend/step3.pdf`** (G-13.13), **closes REQUIREMENTS GAP G-13**, or **creates any attribute**: what is approved is the shape of a definition, not its contents (§15.3 T1, §18 X6). §15.2 and §15.3 remain open. **The ten candidate attributes drafted in [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) §15 are a DRAFT CANDIDATE SET and are neither approved nor adopted by this revision** — see §15.4.

### 15.1 Proposed Decisions

---

**G-13.1 — PRODUCT DECISION — APPROVED 5 September 2026**
**The canonical attribute vocabulary shall be authored as a single reviewed product artefact owned by Product Management, held as configuration alongside the per-type field sets, and versioned.**
*Basis:* NFR-MNT-004 requires sensitivity rules — which attach to attributes (FR-INF-007) — to be "a reviewable list, not scattered through the implementation". *Explicitly new:* **NFR-MNT-001 names types and fields, not attributes** (§7.2), so unlike G-12.1 this decision **cannot be grounded in an existing requirement**. It is a new product decision. *Scope:* PM owns content; Engineering owns format and loading.

---

**G-13.2 — PRODUCT DECISION — APPROVED 5 September 2026 · PROPERTY 6 REVISED AND THE REVISION APPROVED 6 September 2026**
**Each canonical attribute shall carry exactly these seven properties, and no others** — the *shape*, not the content:

| Property | Classification | Source |
| --- | --- | --- |
| Canonical identifier — stable, machine-readable | New product decision | §9.1; FR-INF-004 needs a decidable identity, AR-DET-008 a deterministic one |
| Display label — user-facing | New, supported by **NFR-USE-005** | FR-AMB-002, FR-SENS-003, FR-REV-002, AC-US-003-2 all show attributes to users |
| Semantic definition — prose | New product decision | FR-INF-004 + AR-DET-008; makes the G-12 mapping repeatable |
| Data type | New product decision | FR-INF-008's date/numeric categories; AR-DET-003 determinism |
| Normalisation rule reference | **Existing requirement** | **FR-INF-008 — "normalise attribute formats"**; AR-DET-003 |
| **Multiplicity — scope-keyed cardinality: how many values the attribute may hold, and per what subject** *(**REVISED** — was "single or repeating")* | New product decision | FR-INF-004 cannot otherwise separate a conflict from two legitimate values, **nor a disagreement from two values describing different subjects** — §9.0.1, §11.4.1 |
| Sensitivity tier | **Existing requirement (slot)** | **FR-INF-007 — "Every attribute shall carry…"**; content is G-14/G-15 |

*Excluded, with reasons in §9:* a separate canonical name (redundant); aliases (duplicates G-12's mapping); document-type applicability (G-12's, and derivable); provenance and confidence (properties of the **value**, per FR-INF-002 and FR-OCR-005, not of the definition).

---

**The property 6 revision, stated exactly**

**REVISION APPROVED 6 September 2026 (D-05.8).** Property 6's value domain widens from `single | repeating` to a **scope-keyed cardinality**, written as *how many values, per what subject*:

| Form | Meaning | Illustrative shape only — **no attribute is named or created here** |
| --- | --- | --- |
| *one per `<subject>`* | The attribute holds at most one value for each instance of that subject. Two values for the **same** subject instance are a conflict under FR-INF-004; two values for **different** subject instances are not | A person-scoped identity concept: *one per person* |
| *many per `<subject>`* | The attribute may legitimately hold several values for one subject instance | Replaces what `repeating` meant |

**Subjects admitted by the evidence to date: `person` and `qualification`.** Whether any other subject is needed is an authoring question for the vocabulary's contents (§15.3 **T1**), not a shape question, and is **not decided here**.

*Basis:* **§9, property 8** — the property's own approved justification is that "FR-INF-004 cannot otherwise distinguish 'two documents disagree' from 'this attribute legitimately holds two values'", which is a verbatim statement of the failure the two-value domain cannot express (§9.0.1). FR-INF-004, AR-DET-008, BR-004, FR-INF-005, EC-004, FR-AMB-001, FR-INF-006 — the chain verified in §11.4.1.

*What this revision does **not** do:*
- **It adds no eighth property.** The count remains **seven**, and the "exactly these seven properties, and no others" clause above is retained unchanged and still binding.
- **It does not reopen G-13.3.** Identity is still established by the field→attribute mapping alone. A scope key qualifies *which values are compared*; it never establishes identity by label, value, proximity, or position.
- **It does not decide how a scope instance is resolved** — that is **§15.3 T12** and **G-13.15**.
- **It creates no attribute** and assigns a scope to none.

---

**G-13.3 — PRODUCT DECISION — APPROVED 5 September 2026 — the pivotal decision — NOT REOPENED BY THE REVISION**
**"The same attribute" (FR-INF-004) shall mean: two values map to the same canonical attribute identifier. Identity shall be established by the field→attribute mapping alone — never by label similarity, never by value similarity, never by proximity or position on a document.**
*Basis:* **AR-DET-008** requires conflict detection to be deterministic, and only a lookup is deterministic; **BR-009** prohibits "inferring from similar fields"; **BR-004** prohibits resolving disagreement "by rule, recency, or preference"; **AR-AST-007** forbids an assisted component escalating its own authority — so a probabilistic matcher must not decide attribute identity.
*Consequence, stated plainly:* all judgement moves to the **authoring** of the vocabulary and of G-12's mappings, where it is reviewable, versioned, and correctable — and out of runtime, where it would be none of those things.
*Explicitly new:* `step3.pdf` uses "the same attribute" three times and defines it zero times.

---

**G-13.4 — PRODUCT DECISION — APPROVED 5 September 2026**
**Canonical attribute identifiers shall be stable and never reused. Changing an attribute's display label shall not change its identifier; changing an attribute's meaning shall require a new identifier rather than an edit.**
*Basis:* NFR-USE-005 makes labels answerable to user language and therefore changeable, so a label cannot carry identity; AR-AST-008 requires evaluation results to remain attributable, which a silently redefined identifier destroys.
*Explicitly new:* **§0.1's identifier discipline governs requirement IDs in the specification document, not product data, and is cited here as an analogy only** (§13.3, §16.2).

---

**G-13.5 — PRODUCT DECISION — APPROVED 5 September 2026 · REVISED AND THE REVISION APPROVED 6 September 2026**
**Per-attribute normalisation rules shall be part of the vocabulary, and the comparison function used for FR-INF-004 shall be the normalised form *within a scope instance*. Two values are compared only where they carry the same canonical attribute identifier **and** the same scope instance; values of one attribute in different scope instances are distinct values, not competing ones, and no conflict arises between them. A change to any normalisation rule **or to any scope rule** shall be treated as a change to conflict-detection behaviour: it requires re-approval and invalidates prior evaluation evidence for the affected attributes.**

*Basis:* FR-INF-008 attaches normalisation to "attribute formats"; AR-DET-003 requires determinism and reversibility; **AR-DET-008** requires deterministic detection — and is **satisfied, not weakened**, because a scope instance resolved deterministically keeps the comparison a function; **FR-INF-004**'s subject is two documents; D-02 §11.6's false-conflict source attribution exists precisely to distinguish comparison-caused conflicts from real ones. *Related:* **G-03** (no re-evaluation trigger on component change).

*Consistency with each requirement the revision must not break:*

| Requirement | Effect of the revision |
| --- | --- |
| **FR-INF-004** (MUST) | Still detects when two documents give different values for the same attribute — now only where the two values describe the same subject. Detection of genuine disagreement is **unchanged**; §11.4.1's false positives stop |
| **AR-DET-008** (MVP) | **Preserved.** The comparison remains a deterministic function. Determinism was never the defect — the wrong thing was being determined. **G-13.15** forbids a resolution rule that would reintroduce non-determinism |
| **FR-INF-005** (MUST) | Unchanged. Every detected conflict is still presented and never auto-resolved. Fewer conflicts reach the user, and none is suppressed by rule |
| **BR-004** | **Unchanged and unweakened.** Nothing is resolved "by rule, recency, or preference". Scope determines *whether two values are competing at all*; it never chooses between competing values |
| **EC-004** | Unchanged where a real conflict exists. Fields stop being permanently ambiguous for scope-distinct values (§11.4.1 steps 5–6) |
| **FR-AMB-001** (MUST) | Unchanged. "Source documents conflict" still makes a field ambiguous — it simply stops being true when the documents do not conflict |
| **FR-INF-006** (MUST) | Unchanged for real conflicts. The data-destroying clearing path of §11.4.1 step 7 is no longer reached for scope-distinct values |

*Explicitly recorded:* **scope collapse is a source of false conflict distinct from extraction error, from normalisation, and from genuine document variance** (§11.4.1). **APPLIED 8 September 2026:** D-02 §11.6's attribution taxonomy now carries it as a fourth category (D-02 §11.6.1), closing **X15** (§22.7).

*Not decided here:* **the normalisation rules themselves** — §15.3 **T3**; **the scope-instance resolution rule** — §15.3 **T12** and **G-13.15**.

---

**G-13.6 — PRODUCT DECISION — APPROVED 5 September 2026**
**The raw extracted value shall be retained alongside its normalised form.**
*Basis:* **AR-DET-003** requires normalisation to be "deterministic and **reversible**", and reversibility is not otherwise achievable for lossy categories such as casing and spacing. Consistent with FR-INF-002 (provenance per value), FR-OCR-007 (the region a value was read from), and FR-INF-006 (retain the alternatives).
*Explicitly new:* `step3.pdf` requires reversibility and never says how it is obtained. This is the minimum way to satisfy it, not the only conceivable one.

---

**G-13.7 — PRODUCT DECISION — APPROVED 5 September 2026**
**An extracted value that maps to no canonical attribute shall never be coerced into the nearest-looking attribute, and shall not enter the structured record as though it were one. Its destination — discarded, retained outside the record, or surfaced to the user — is a Product Management decision that this document does not make.**
*Basis:* **BR-009** ("Guessing, inferring from similar fields, and filling with placeholder values are all prohibited"), **BR-016** (fail towards inaction), **EC-003** ("Never force it into an expected slot"), **AR-AST-007** (no self-escalation). Together these exclude coercion; none of them supplies the destination.
*Registered as:* **G-13.g1**, a candidate new gap (§12.4). **The decision register is not modified by this document.**
*Related and distinct:* **G-27** (FR-OCR-009's manual-entry destination), **G-08** (the store-and-search-only state), **D-02 §11.7** (whether some readable values should be extracted at all — safety-relevant, unsettled).

---

**G-13.8 — PRODUCT DECISION — APPROVED 5 September 2026**
**The vocabulary shall be authored and approved before the per-type field sets, and no vocabulary entry shall be created by engineering or derived from what an OCR or extraction engine happens to return.**
*Basis:* FR-INF-001 ("assembled from all processed documents") and FR-INF-004 ("the same attribute") require attribute identity to exist before per-type fields can be related to one another; **§6's Selection Principle** — "any component may be replaced provided its replacement meets the same guarantees" — is inverted if the vocabulary is derived from an engine, because engine replacement then becomes a data migration.
*Relationship:* confirms G-12 §11's **G-12.3** from the G-13 side. Neither artefact's ordering now depends on the other's approval.

---

**G-13.9 — PRODUCT DECISION — APPROVED 5 September 2026 · NARROWED AND THE NARROWING APPROVED 6 September 2026**
**Every canonical attribute shall carry a sensitivity tier slot. No attribute shall be released to implementation, to stored production data, or to any surface that discloses or fills a value, without an assigned tier. A vocabulary version may be approved *structurally* with tier slots present and marked TBD, provided that version is marked NOT RELEASABLE. The rules that assign tiers (G-14) and the default tier for an attribute no rule covers (G-15) are delegated and are not decided here.**

*Basis for the slot:* **FR-INF-007** (MUST) — "Every attribute shall carry a sensitivity classification of routine, sensitive, or consequential"; FR-SENS-001; with monotonicity from FR-SENS-006, BR-020, AR-AST-007, and the reviewable-rule-set requirements AR-DET-005 and NFR-MNT-004.

*Basis for the narrowing:* **FR-INF-007 and FR-SENS-001 bind the system, not an analysis artefact.** The protection the original wording provides is against an untiered attribute reaching a surface where **FR-SENS-002**'s per-instance approval gate would be silently bypassed — a protection that attaches at **disclosure**, not at authoring. Ground-truth annotation records what a document says and discloses nothing to a form, so it does not engage FR-SENS-002. The evaluation/implementation distinction is already drawn in [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) §19.3 and survives scrutiny.

*What the narrowing buys, and why it was needed.* Under the original wording, read with §18's X6 ("all seven properties, none blank") and X9, **G-13 could not close until G-14 and G-15 closed** — and those are gated on assumption **A-5**, which document 02 itself says "must be set by users, not by us", routed by register **D-06.4** to studies **S-1** and **S-4**. That placed a user-research study on the critical path of G-12 authoring, ground-truth annotation, and D-02 §11.6 design. **Nothing in `backend/step3.pdf` requires that; the original G-13.9 wording was the only thing putting it there.**

**Closure is therefore split into two named gates:**

| Gate | Content | Unblocks | Gated on |
| --- | --- | --- | --- |
| **G-13-A — structurally complete** | Shape frozen; every attribute carries properties 1–6 complete; property 7 present and **TBD**; the version marked **NOT RELEASABLE** | **G-12** authoring · D-02 **L6/L7** annotation and its design · D-02 §11.6 evaluation design | G-19, the property-6 revision, **G-13.15**, the G-13.12 minimality test, **§18 X18** |
| **G-13-B — releasable** | Every tier assigned | Implementation of FR-INF-001…009 · production storage of attribute values · **automatic placement of any value into a form** (**FR-INF-007** primary; **FR-SENS-002 / BR-005** for disclosure of a tiered value) | **G-14, G-15** (assumption A-5; studies S-1, S-4) |

*Recorded, not adopted — the interim-default route and its price.* Register **D-06.4** already holds a recommendation for G-15: default to **sensitive** for any attribute no rule covers. Adopting it would leave no tier blank and satisfy the original wording verbatim. Two costs, both verified against `backend/step3.pdf`:

**(i) Every value would require explicit per-instance approval before reaching a form.** **FR-SENS-002** (MUST) — "Sensitive information shall never be placed into a form without explicit approval for that specific disclosure" — with **BR-005**. Nothing would be placed automatically, for as long as the default stood. **Effect on the §10.1 demonstration: step D7** ("Routine fields above threshold filled, reformatted to constraints, visibly marked") **becomes unrunnable**, because no value would be eligible for automatic placement. **Step D11 remains runnable** — it exercises exactly this approval path ("A sensitive field and a sensitive document each require explicit, itemised approval", FR-SENS-002/003, FR-APR-001…004) and would if anything be easier to demonstrate. What is lost is the **contrast** between D7 and D11 that the journey is built to show.

*A distinction that must not be blurred here.* **FR-FILL-001**'s "and the field is classified routine" governs the **detected form field**, classified under **FR-FLD-003** (MVP MUST — "Each field shall be classified as routine, sensitive, or consequential before any value is placed in it"), and **FR-SENS-001** keeps the two classifications separate: the tier is maintained "for both stored attributes **and** detected form fields". A *stored attribute's* tier therefore reaches form filling through **FR-SENS-002 / BR-005**, not through FR-FILL-001's routine clause.

**(ii) Reversing it is constrained** — **BR-020**'s floor bites only at *consequential*, so *sensitive → routine* is not barred outright, but **FR-SENS-006** bars a user and **AR-AST-007** bars an assisted component from lowering, leaving only a Product Management change to the AR-DET-005 rule set. An interim default intended to be lowered later must say so explicitly when adopted, or it will read as a floor. **This is recorded so PM can see the price. It is not recommended and not adopted here.**

*Explicitly not decided:* **any tier, for any attribute; any classification rule; the default tier. G-14 and G-15 are untouched by this revision.**

*Gating:* the tier **content** inherits assumption **A-5**, which §12.3 records as untested and which, if it fails, means "the sensitivity boundary is wrong". **G-13-A** can be reached with the slot defined and empty; **neither gate may be reached with the slot absent.**

---

**G-13.10 — PRODUCT DECISION — APPROVED 5 September 2026**
**The vocabulary shall be versioned. Every evaluation run and every stored attribute value shall record the vocabulary version it was produced under.**
*Basis:* **AR-AST-008** requires evaluation against a real corpus before any threshold is set; a threshold justified by an evaluation against a superseded vocabulary is not evidence. *Related:* **G-03**; parallel to G-12 §11's **G-12.8**.

---

**G-13.11 — PRODUCT DECISION — APPROVED 5 September 2026 · TRIGGER CLARIFIED AND THE CLARIFICATION APPROVED 6 September 2026**
**Until G-13 closes, no placeholder, illustrative, example, or "temporary" attribute shall be introduced into code, configuration, database schema, migrations, test fixtures, or evaluation tooling.**
*Basis:* **BR-009** — the product's own prohibition on placeholder values, applied to its own construction; **§11's Containment Rule** — scope may not enter informally. A placeholder vocabulary in a fixture is the most direct route by which an invented requirement becomes a real one.
*Explicit consequence:* nothing attribute-shaped is built in Sprint 4 on a provisional vocabulary.

*Trigger, under the two-gate model (clarification only — the decision's wording above is unchanged).* The revised **G-13.9** splits closure into **G-13-A** and **G-13-B**, which leaves "until G-13 closes" ambiguous. **The trigger is G-13-A.** Two things follow, and neither weakens the prohibition:

- **Approved G-13-A content is not a placeholder, illustrative, example, or "temporary" attribute** within this decision's meaning. It is reviewed, versioned vocabulary content whose only incomplete property is the sensitivity tier, which **G-13.9** deliberately defers to **G-13-B**. The clause targets *invented* attributes standing in for absent ones; it does not target *approved* ones awaiting a tier.
- **Before G-13-A, the prohibition applies in full** — including to the ten draft candidates of §15.4, which may not enter code, configuration, schema, migrations, fixtures, or evaluation tooling in any form.

*What this permits, and what it still forbids.* After **G-13-A** it permits **ground-truth annotation and evaluation tooling** to reference approved attributes — which is what **§18 X14** and **X15** record. It still forbids, until **G-13-B**, any entry into **production code, database schema, migrations, or stored production data**, because an attribute whose tier reads TBD does not satisfy **FR-INF-007** (MUST). Ground-truth annotation is not production storage and discloses no value to a form, so it does not engage **FR-SENS-002** or **BR-005**.

---

**G-13.12 — PRODUCT DECISION — APPROVED 5 September 2026**
**The vocabulary shall be authored to the minimum that serves a requirement which consumes it. Each attribute shall be justifiable against a named requirement, and the burden of proof shall sit on including an attribute rather than on excluding it.**
*Basis:* **BR-017** (data minimisation) and **NFR-PRIV-001** ("collect only information required to deliver a function the user has requested"). The vocabulary defines what DOCURA knows about a person; an attribute no requirement consumes is retained personal data with no justifying function.

---

**G-13.13 — PRODUCT DECISION — APPROVED 5 September 2026**
**Approval of this document does not amend `backend/step3.pdf`.** As with G-02 and G-12, the gap in the specification remains open until **§11's Containment Rule** is followed and the specification is amended under a new version number.

---

**G-13.14 — PRODUCT DECISION — APPROVED 5 September 2026**
**Stage-1 D-02 evaluation — OCR text quality, classification, failure behaviour, engine eligibility, and normalisation *determinism* — is not blocked by G-13 and may proceed as soon as the corpus exists under the approved G-02 governance.**
*Basis:* §14.2; consistent with D-02 §3.2, §18 (G-02 and G-13 as independent parallel roots) and §19's two-stage exit criteria. Gating stage 1 on the vocabulary would idle approved corpus work behind a product-definition task for no requirement-based reason.

---

**G-13.15 — PRODUCT DECISION — APPROVED 6 September 2026 — *new***
*What is approved is the constraint — that the rule is PM's, deterministic, and never derived from an extracted content value. **The rule itself remains unresolved** (§15.3 **T12**, §18 **X17**).*
**The rule by which a value's scope instance is resolved shall be a Product Management decision, recorded in the vocabulary version it applies to, and shall be deterministic without reference to any extracted content value.**

*Basis:* **AR-DET-008** requires conflict detection to be deterministic, and G-13.5 as revised makes the scope instance part of the comparison function; **G-13.3** (not reopened) prohibits identity established "by value similarity"; **AR-AST-007** forbids an assisted component escalating its own authority, which is what letting a probabilistic read decide conflict identity would do.

*Candidate derivations — recorded so the choice is visible. **None is selected here.***

| Candidate | Deterministic? | Notes |
| --- | --- | --- |
| Derived from the document's **classified type** (FR-OCR-002/003) | Yes — classification is already an owed output, and needs no content extraction | Two qualifications sharing one type still collapse; couples scope to the **§7.1** type set, which is provisional under **ASM-001** and demotable; **G-10** can merge types and reintroduce the collapse |
| **Declared per type in the G-12 mapping** | Yes — same mechanism, owned by G-12 | Keeps the type coupling inside G-12, where §7.1's provisionality already lives |
| A **user-designated** qualification grouping | Yes, once designated | Beyond anything `backend/step3.pdf` requires. **New scope** |
| Derived from an **extracted content value** naming the qualification | **No** | **Excluded by G-13.3 and AR-AST-007** — it is identity by value similarity and makes conflict detection depend on extraction accuracy |
| Derived from the **source document's identity** | Yes | **Excluded on requirement grounds:** two documents would never share a scope instance, so **FR-INF-004 would detect nothing, ever** — determinism satisfied by making the requirement vacuous |

*Explicitly not decided here.* Two of the five are excluded by approved decisions or by FR-INF-004 itself; the remaining three are a live Product Management choice. **This is the single place in the revision where a model could most easily be invented, and it is not invented.** Recorded as **§15.3 T12**.

---

### 15.2 Decisions That Belong to G-12

**Not resolved here. No field is named in this document, and no attribute is mapped to a document type here.** *(§19, added later, authors one attribute as proposed vocabulary **content**; the field→attribute mapping below remains G-12's.)*

| # | Belongs to G-12 | Requirement it serves |
| --- | --- | --- |
| F1 | Which concepts/fields exist for each document type | FR-OCR-004 |
| F2 | The document-specific label printed above each value, and its mapping to an attribute | §11.3(c); G-12.4's mapping property |
| F3 | Whether each field is mandatory or optional for its type | G-12 question C |
| F4 | Whether a given field maps to an attribute or **explicitly to none** — and, per G-13.7, what "none" then means | G-12.4; **G-13.g1** |
| F5 | Field-level missing-value semantics — a document of a type that does not contain a field it normally would | G-12 question G / R5 |
| F6 | Which document types are in scope for field authoring at all | G-12 R2; G-09, G-10, G-11; §7.1 and ASM-001 |

**Record-level completeness — which attributes the record is *missing* — is neither G-12's nor G-13's: FR-INF-010 is FUTURE / WON'T.**

### 15.3 Decisions That Must Remain TBD

| # | Must remain TBD | Why | What would settle it |
| --- | --- | --- | --- |
| **T1** | **The vocabulary's actual contents** — which attributes exist | Authoring content is not analysis; producing a list here would be exactly the invention this task forbids | PM authoring against G-13.2's shape and G-13.12's minimality test |
| **T2** | **Sensitivity tier assignment rules, and the default tier** | **G-14**, **G-15** — the referenced §02 Table 13.1 is an ASM-tagged working classification, not reproduced in `step3.pdf`, bound to untested **A-5**. **Under the revised G-13.9 these gate G-13-B only**, not G-13-A, and may proceed in parallel with vocabulary authoring and with G-12 | G-14 / G-15 resolution; studies S-1, S-4 |
| **T3** | **PARTIALLY RESOLVED — casing and spacing/whitespace APPROVED 7 Sep 2026 (N-TEXT, PD-B, §21).** Settled for a `text` attribute. **Dates and numeric precision remain TBD**, and so does every widening of N-TEXT beyond the two categories FR-INF-008 names | N-TEXT is the **evaluation-independent floor** that FR-INF-008 states outright. No rule is stated for dates or numeric precision because **no date-typed or numeric attribute is authored**, and writing one for a hypothetical attribute would be invention. Any widening — diacritics, script, transliteration — is a conflict-detection behaviour change (§11.4) | Approval of **N-TEXT**; then, per category as attributes are authored, a PM decision informed by D-02 §11.6 false-conflict attribution |
| **T4** | **The "spacing" vs "whitespace" wording** | `step3.pdf` uses both (FR-INF-008 vs AR-DET-003) | Specification amendment under §11's Containment Rule |
| **T5** | **The profile / structured-record relationship** | **G-19** — may add a property to G-13.2's shape (§16.1) | PM + Architecture; register D-08.2 |
| **T6** | **What a duplicate attribute entry is** | **G-20** — downstream; register D-08.4 recommends run-scoped superseding, "not a requirement" | PM + Architecture |
| **T7** | **The destination of an unmapped extracted value** | **G-13.g1** — G-13.7 excludes coercion and does not choose the destination | PM, with a privacy consequence |
| **T8** | **The confidence scale and semantics** | **G-06** — independent of G-13; confidence is per value | Architecture + PM |
| **T9** | **BR-001 / BR-002 threshold values, relationship, and global-vs-per-type** | **G-04, G-05, G-07** — and AR-AST-008 requires evaluation first | Stage-2 evaluation, then PM |
| **T10** | **Whether extraction quality justifies the attribute-dependent requirements at all** | §12.3 — if **A-7** fails, FR-OCR-004…006 and BR-001 are affected | Study A-7 / S-6 |
| **T11** | **Which history a change or conflict resolution is written to** | **G-28** — FR-INF-009 vs FR-AUD | PM |
| **T12** | **The scope-instance resolution rule** *(new, 6 September 2026)* | **G-13.15** — the revised G-13.2 declares a scope *subject*; the *instance* must be resolved deterministically at comparison time, and two of the five candidate derivations are excluded by G-13.3, AR-AST-007, or FR-INF-004 itself | PM decision, recorded in the vocabulary version; constrained by AR-DET-008 |

---

### 15.4 The G-12 candidate attributes — DRAFT CANDIDATE SET, not adopted

*Added 6 September 2026 as part of the revision.*

[`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) §15 drafts ten canonical attributes and its §17.1 **G-12.P1** proposes adopting them "as the initial vocabulary content". **Ownership of vocabulary contents is G-13's** — §15.3 **T1**, §18 **X6**, **G-13.8**, and §13.2 all say so, and the revision analysis confirms it at G-13R.1.

**This revision does not adopt them, approve them, or repair them.** They are recorded here as a **DRAFT CANDIDATE SET** so that the transfer of ownership is visible without the content being smuggled in with it. **No attribute is created by this document.**

Before any candidate may enter a vocabulary version under **X6**, four challenges raised by the revision analysis (§9.4) must be discharged. **They remain open and are restated here, not resolved:**

| # | Challenge | Why it stands |
| --- | --- | --- |
| **C-a** | **The consumer justification does not discriminate.** **G-13.12** (approved) requires each attribute to be justifiable against a named consuming requirement. G-12's named consumer for eight of ten is **FR-FILL-001**, which is a *gate* on filling — "only when… the field is classified routine" — and enumerates no information. It admits every candidate equally. The discriminating claims ("a form's education block asks for the awarding body") are **not in `backend/step3.pdf`** | The evidence that would discriminate exists and needs no corpus: §10 / **ASM-002** makes the controlled mock form a **team-constructed artefact**. Its field inventory is the missing input to the G-13.12 test |
| **C-b** | **Six of ten fail G-12's own "definable now" test**, though G-12 §14.0 asserts all ten passed it. Five education candidates had no multiplicity; **the address candidate** has no data type and no normalisation rule | The property-6 revision supplies multiplicity for the five. **The address candidate remains undefinable** until G-12 §18.3 resolves the address component set |
| **C-c** | **The two identifier-number candidates are gated by a safety decision that precedes their existence.** D-02 §11.7 and register **D-05.3** leave open "whether the identifier number is stored at all, masked, or stored in part". If the answer is *not stored*, the attribute should not exist | G-12 §19.1 rated both **EVALUATION-READY**, which would authorise transcription into ground truth while **G-02 §8.6** states derived-artefact redaction scope "cannot be answered today". **Both must be NOT EVALUATION-READY until this resolves** |
| **C-d** | **One candidate's semantic definition is by page position, not by meaning** — "the overall result… as printed on the document". **G-13.2 property 3** requires prose "precise enough that two authors mapping two documents agree", and a marksheet printing both a percentage and a division defeats that. G-12 §18.5 concedes the values cannot be meaningfully compared | **FR-INF-004** over it would be inoperative as defined. Must be redefined or withdrawn |

**None of these four is repaired here.** Silently fixing a candidate's definition would convert a draft into approved content without a review, which is the failure mode **G-13.11** exists to prevent.

**Tested, not adopted — 6 September 2026.** **§19**'s T1 authoring pass runs all ten candidates against an admission test drawn from the approved decisions. **One concept is carried into an entry authored on independently stated evidence** (§19.4.1); **nine are not authored** (§19.5). **This changes nothing above:** the candidate set is still DRAFT, C-a…C-d are still open, and §19 repairs none of them.

---

## 16. Conflicts and Dependencies

### 16.1 Dependencies

| Direction | Gap / decision | Effect on G-13 |
| --- | --- | --- |
| **Upstream** | **G-19** — profile vs structured record | **Still the one dependency that could change G-13.2's shape**, and §18 **X4** still makes the freeze depend on it. If profile and record are two stores rather than two views, the vocabulary may need an eighth property stating which store an attribute belongs to. **The property-6 revision does not pre-empt this and does not consume the eighth slot** — it redefines an existing property rather than adding one. **Because X4 freezes the property list once, G-19's answer and the property-6 revision should land in a single revision event** (revision analysis §5.7, G-13R.10); the alternative remains to freeze without G-19 and record the risk, which is a PM call |
| **Upstream (content only)** | **G-14, G-15**, assumption **A-5** | Populate the tier slot. **Under the revised G-13.9 these gate G-13-B only.** **G-13-A** can be reached with the slot defined and empty of policy, so G-14/G-15 may proceed **in parallel** with vocabulary authoring and with G-12 rather than ahead of them |
| **Parallel** | **G-02** (APPROVED) | Independent root. Corpus collection proceeds; nothing in this document alters the approved governance |
| **Parallel — G-12's dependencies, not G-13's** | **G-09**, **G-10**, **G-11**, **D-04.4** (student ID, hall ticket), **D-04.7** (resume) | Type-boundary decisions. They gate **G-12**'s per-type mapping and **do not gate the vocabulary**: §9 property 9 deliberately decoupled the vocabulary from the §7.1 type set, which is provisional under **ASM-001**. They therefore run **in parallel** with vocabulary authoring. *Note for G-12's owner:* **D-04.4** records "DECISION REQUIRED" for **student ID** and **hall ticket** in the same terms as G-11 does for photograph and signature |
| **Downstream** | **G-12** | Cannot be authored until the vocabulary's contents exist (G-13.8). **Gated on G-13-A, not on G-13-B** — so G-14/G-15 do not block G-12 authoring |
| **Downstream** | **G-20** | If the duplicate identity chosen is `(document, attribute, normalised value)`, it inherits G-13.5's re-approval consequence |
| **Downstream** | **G-27**, **G-13.g1** | Both concern where a value goes when it has no defined home |
| **Downstream** | D-02 **L6/L7**, **§11.6** | Directly blocked; see §14.3 |
| **Independent** | **G-06**, **G-28**, **G-08** | Not affected by G-13 and do not affect it |

### 16.2 Conflicts and inconsistencies found

| # | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| 1 | **G-12 §11's G-12.4 cites §0.1** as the source for a stable field identifier. §0.1 is the **requirement**-identifier scheme for the specification document and says nothing about product data | Low — a citation defect, not a substance defect | Recorded in §4 (V2), §13.3. **G-12's proposal stands; its basis should be relabelled a new product decision.** This document does not edit `SPRINT_4_G12_FIELD_DEFINITIONS.md` |
| 2 | **G-12 §10.2 assigns V6 and V7 to G-13.** V6 is **G-19** and V7 is **G-20**, both separately registered | Low — scope precision | Reassigned in §4; both recorded as dependencies rather than G-13 decisions |
| 3 | **G-12 §10.2 assigns V5 (tier *and* rules) wholly to G-13.** The tier slot is G-13's (FR-INF-007); the rules are **G-14**'s and the default is **G-15**'s | Low — scope precision | Split in §4 (V5) and narrowed in G-13.9 |
| 4 | **`step3.pdf` uses "spacing" (FR-INF-008) and "whitespace" (AR-DET-003)** for what appears to be one normalisation category | Low — same class as "unrecognised"/"unclassified" | Recorded, not resolved. **T4** |
| 5 | **AR-DET-003 requires normalisation to be "reversible"; FR-INF-008 does not mention reversibility** and no requirement says what reversibility obliges | Medium — it constrains storage | **G-13.6** proposes the minimum satisfying reading, labelled a proposal |
| 6 | **NFR-MNT-001 covers types and fields but not attributes**, so the vocabulary has no specified home | Medium — it removes the grounding G-12.1 enjoys | **G-13.1** is labelled a new product decision rather than an application of NFR-MNT-001 (§7.2) |
| 7 | **No unmappable-value path exists** at the attribute level, though the specification provides one at the document-type level and one at the form-field level | **High** — three MVP requirements route through it, and it is where unclassified personal data would accumulate | **G-13.g1** raised (§12.4); **G-13.7** proposes the exclusion and defers the destination |
| 8 | **G-12.4's "maps to explicitly none"** has no defined destination | High — same hole as #7, reached from the G-12 side | Recorded in §12.3 and §15.2 F4 |
| 9 | **FR-ACC-004 and FR-INF-004 carry no TBD marker**, unlike the twelve threshold-dependent requirements §15.1 acknowledges | Informational | Recorded in §5. The specification does not appear to know the vocabulary is missing |

**No conflict was found between this analysis and `backend/step3.pdf`.** Every conflict above is either internal to the specification (4, 5, 9), an absence in it (6, 7, 8), or a citation or scoping refinement to the G-12 document (1, 2, 3).

---

## 17. Approval Required

**APPROVAL OBTAINED.** G-13.1…G-13.14 were approved on **5 September 2026** (register **D-05.6**); the revision — **G-13.2**, **G-13.5**, **G-13.9**, the new **G-13.15**, and **G-13.11**'s trigger clarification — was approved on **6 September 2026** (register **D-05.8**). The table below is the record of what was approved and by whom. **Approval of every row leaves REQUIREMENTS GAP G-13 open**, creates no attribute, meets neither gate, and amends nothing in `backend/step3.pdf`.

| # | Decision | Approver | Cannot be delegated to engineering because |
| --- | --- | --- | --- |
| **G-13.1** | Vocabulary is a PM-owned, versioned configuration artefact | Product Management | It defines what DOCURA knows about a person; **and NFR-MNT-001 does not cover it**, so nothing existing authorises it |
| **G-13.2** | The seven-property minimum shape — **property 6 REVISED to a scope-keyed cardinality; count unchanged at seven, no eighth property** | Product Management (content properties) · Engineering (format) | Five of the seven are gaps in the requirements; the revision changes what FR-INF-004 raises as a conflict |
| **G-13.3** | **Identity by mapping, never by similarity** | Product Management | Determines what the product raises as a conflict, and therefore how often it interrupts a user |
| **G-13.4** | Stable, never-reused identifiers; labels do not carry identity | Product Management · Engineering | Determines whether evaluation results stay attributable |
| **G-13.5** | Normalisation rules are vocabulary content; changing one is a behaviour change — **REVISED: the comparison function operates within a scope instance, and scope rules inherit the same re-approval consequence** | Product Management | A normalisation rule is a conflict-detection rule (§11.4); so is a scope rule (§11.4.1) |
| **G-13.6** | Raw value retained alongside normalised form | Product Management · Architecture | Satisfies AR-DET-003's reversibility; a storage and privacy consequence |
| **G-13.7** | No coercion of unmapped values; destination deferred | Product Management · Privacy | Determines whether unclassified personal data accumulates |
| **G-13.8** | Vocabulary before field sets; never engine-derived | Product Management · Architecture | Protects §6's Selection Principle |
| **G-13.9** | Tier slot mandatory; rules delegated to G-14/G-15 — **REVISED: narrowed to release-time; closure split into G-13-A and G-13-B** | Product Management · Privacy | Sensitivity is a user-safety decision gated on A-5. The narrowing decides *when* the bar applies, never *what* a tier is |
| **G-13.10** | Versioned; runs and values record the version | Engineering · Product Management | Determines whether an evaluation result is evidence |
| **G-13.11** | No placeholder vocabulary until closure — **trigger CLARIFIED to G-13-A; decision wording unchanged** | Product Management · Engineering | Prevents an invention becoming a de-facto requirement; the clarification decides *when* the bar lifts, never *what* it forbids |
| **G-13.12** | Minimum justifiable vocabulary | Product Management · Privacy | BR-017 / NFR-PRIV-001 privacy decision |
| **G-13.13** | Approval here does not amend `step3.pdf` | Product Management | §11 Containment Rule |
| **G-13.14** | Stage-1 evaluation not blocked by G-13 | Product Management | Sequencing decision with schedule consequences |
| **G-13.15** | *New* — the scope-instance resolution rule is PM's, deterministic, and never derived from an extracted content value | Product Management · Architecture | It decides which values FR-INF-004 compares; AR-DET-008, G-13.3 and AR-AST-007 constrain it, and none of them supplies it |

**Also requiring approval and not proposed here:** T1 (the vocabulary's contents), T2 (G-14 / G-15), T3 (the normalisation rules), T5 (G-19), T6 (G-20), T7 (the unmapped-value destination), and the addition of **G-13.g1** to the decision register.

---

## 18. G-13 Exit Criteria

**REVISED 6 September 2026; the revision APPROVED 6 September 2026 (D-05.8).** Closure is now reached in two gates, per the revised **G-13.9**. **The approval satisfies X1 and nothing else: G-13-A and G-13-B both remain NOT MET.** **Updated by the T1 completion pass (§20): X3 and X5 became MET; X7, X8, X10 and X18 were satisfiable for `v0.1-draft` on approval of §20.3. §20.5 classifies every criterion. After PD-B (§21, 7 Sep 2026): X7, X8, X10 and X18 are now MET for `v0.1-draft`; X6 stays gated on X4/X17; four gate-A decisions remain — PD-A, PD-C, PD-D, PD-E. G-13-A remains NOT MET.** **Superseded by §22 (8 Sep 2026): PD-A/C/D/E approved (D-05.12); X2, X4, X6, X8, X11, X13, X14 and X17 now MET for `v0.1-draft`. X12 was then MET 8 Sep 2026 (§22.6), and X15 was MET the same day (§22.7) by applying the fourth false-conflict attribution category at D-02 §11.6.1 — **G-13-A is now MET.** See §22.3 for the recalculated table; the per-row Status cells below are as of 7 Sep and are read through §22.3/§22.6/§22.7.** The criterion numbering **X1–X16 is preserved unchanged** because other documents cite it; a **Gate** column says which gate each belongs to, and **X17–X18** are added by the revision.

**G-13-A — structurally complete (NOT RELEASABLE).** Unblocks **G-12** authoring, D-02 **L6/L7** annotation design, and D-02 §11.6 evaluation design.
**G-13-B — releasable.** Unblocks implementation of FR-INF-001…009, production storage of attribute values, and automatic placement of a value into a form.

| # | Gate | Exit criterion | Depends on | Status today |
| --- | --- | --- | --- | --- |
| **X1** | A | G-13.1…G-13.15 approved, or explicitly rejected with an alternative recorded | This document | **MET — 6 September 2026.** G-13.1, G-13.3, G-13.4, G-13.6–G-13.8, G-13.10–G-13.14 approved 5 Sep 2026 (D-05.6); **G-13.2, G-13.5, G-13.9 as revised, G-13.15 as new, and G-13.11's trigger clarification approved 6 Sep 2026 (D-05.8)**. *X1 is one criterion of eighteen — it does not make gate A* |
| **X2** | A | **G-19** answered: whether FR-ACC-004's profile and FR-INF-001's structured record are one thing or two | Product Management | **Not met** — may still add a property to X4. The property-6 revision does not consume that slot |
| **X3** | A | **G-13.g1** accepted as a gap and recorded in the decision register by its owner | X1 | **MET — 6 September 2026.** Recorded in the register's §4 gap table as **G-29** by that document's owner (§20.5) |
| **X4** | A | The seven-property shape (G-13.2, **as revised**) approved and frozen for a version | X1, X2 | **Not met.** The list freezes **once** — G-19's answer and the property-6 revision should land in one revision event (§16.1), or the freeze-without-G-19 risk must be explicitly accepted |
| **X5** | A | The identity relation (G-13.3) approved, and stated in language an author can apply without judgement | X1 | **MET — 6 September 2026.** G-13.3 is approved (X1) and states identity as a lookup through the field→attribute mapping, with label, value, proximity and position expressly excluded — applicable without judgement. **Not reopened by the revision** |
| **X6** | A | **The vocabulary authored**: every attribute carries all seven properties, **property 7 may be TBD at this gate** | X4, X5, X17 | **Contents and scope APPROVED 7 Sep 2026 (PD-B, §21); criterion remains NOT MET.** `v0.1-draft`'s one entry has properties 1–6 complete (property 5 now **N-TEXT**), property 7 TBD by design. **X6 stays gated on X4 and X17.** Nine candidates are not authored; §15.4's set is still **draft** and C-a…C-d are open |
| **X7** | A | A normalisation rule stated for every attribute, covering all four categories where applicable (question **E**, T3) | X6 | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B).** N-TEXT approved (§20.3, §21). Casing and spacing apply and are stated; dates and numeric precision apply to no authored attribute. **Reopens if the version gains an attribute in an unruled category** |
| **X8** | A | **Scope-keyed multiplicity** stated for every attribute — how many values, and per what subject | X4, X6, X17 | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B)** *(criterion revised: was "Multiplicity stated for every attribute")*. Stated for the one entry authored in §19.4 — *one per `person`* — and unstated for every candidate not authored |
| **X9** | **B** | A sensitivity tier **assigned** on every attribute — requires **G-14** and **G-15** | X6, G-14, G-15 | **Not met.** *Moved to gate B by the revised G-13.9.* At gate A the slot must be **present and TBD**; the version is then marked **NOT RELEASABLE** |
| **X10** | A | Every attribute justified against a requirement that consumes it (G-13.12, BR-017) | X6 | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B).** §15.4 **C-a** records that FR-FILL-001 does not discriminate, so the §10/ASM-002 mock-form inventory is the evidence owed for any *added* candidate. **Discharged for `person.full_name`**, the only entry, by §12.2's "Name mismatches" (§19.8, §20.5) |
| **X11** | A | The unmapped-value destination decided (G-13.7, T7) | X1, X3 | **Not met** |
| **X12** | A | The artefact is held as configuration and versioned (G-13.1, G-13.10) | X6 | **MET — 8 September 2026 (§22.6).** Held as `config/vocabulary/canonical_attributes.v0.1-draft.toml` (versioned), validated by `tests/test_vocabulary_config.py` (13 tests pass). Configuration, not production code; D-01 untouched |
| **X13** | A | **G-12 unblocked**: field sets may be authored, each field mapping to one attribute or explicitly to none | X6 | **Not met.** *Its stated dependency is unchanged — X6, and **it never depended on X9, directly or transitively**: X9 hangs off X6 as a sibling criterion, not upstream of X13. What changed is **X6 itself** — property 7 may now read TBD at gate A, so X6 no longer requires tiers, and it was that original X6 wording, not X9, that carried **G-14/G-15** into X13* |
| **X14** | A | D-02 ground-truth layers **L6** and **L7** become annotatable. **G-13.11 permits this at gate A**: approved gate-A content is not a placeholder within that decision's meaning, and annotation is neither production storage nor disclosure to a form | X6 | **Not met** |
| **X15** | A | D-02 §11.6 conflict-detection evaluation becomes designable against a real subject | X6, X7, X8, X17 | **MET — 8 September 2026 (§22.7).** The fourth false-conflict attribution category — scope-model error (scope collapse), §11.4.1 — is applied at D-02 §11.6.1; with X6/X7/X8/X17 met, §11.6 is designable against `v0.1-draft` |
| **X16** | — | `step3.pdf` amended under §11's Containment Rule, or the divergence formally accepted and recorded | X1–X12 | **Not met** |
| **X17** | A | **The scope-instance resolution rule decided** (G-13.15, T12) — deterministic, not derived from any extracted content value | X1, X4 | **Not met** *(added by the revision)*. **Decision required — PD-D.** §20.5 records a **proposed** per-subject reading of this criterion, under which `v0.1-draft` would not need it; **that reading is not taken here** |
| **X18** | A | §15.4's challenges **C-a…C-d** discharged for every candidate before it enters X6 — or the candidate withdrawn | X6, X10 | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B).** The criterion is conditional on a candidate **entering** X6, and **no challenged candidate enters `v0.1-draft`**. **C-a…C-d remain open and reopen this criterion the moment any candidate is added** (§20.5) |

**What each gate does and does not unblock.**

**Gate A** unblocks the *authoring* of G-12 and the *design and annotation* of the conflict-detection and field-extraction evaluation. It does **not** unblock: **L4/L5** or D-02 §11 (which additionally require **G-12** to close); the **BR-001 threshold** (which additionally requires G-04, G-05, G-06, G-07 and the evaluation itself); the **§7.1 type-inclusion decision** (which requires per-type results); or anything at gate B.

**Gate B** unblocks the **build** of FR-INF-001…009, production storage, and **automatic placement of a value into a form**. The gating requirement is **FR-INF-007** (MUST) — "Every attribute shall carry a sensitivity classification" — which an attribute whose tier reads TBD does not satisfy, so it may not exist in the running system at all. Once tiers are assigned, **FR-SENS-002** and **BR-005** govern whether a given value may be placed without explicit per-instance approval. *(**FR-FILL-001**'s "the field is classified routine" is a separate condition on the **detected form field**, classified under **FR-FLD-003** — see the note in G-13.9.)* §12.3 additionally gates that build on assumptions **A-5** and **A-7**.

**What neither gate unblocks, and must not be read as unblocked:** the vocabulary's *contents* still do not exist; **REQUIREMENTS GAP G-13 remains open**; and neither gate amends `backend/step3.pdf` (**G-13.13**, X16).

## 19. T1 — Authoring the Vocabulary Contents

**T1 AUTHORING PASS — 6 September 2026. PROPOSED CONTENT — REQUIRES PRODUCT MANAGEMENT APPROVAL. NOT APPROVED HERE.**

This section discharges **§15.3 T1** — *the vocabulary's actual contents* — by authoring against the shape approved in §15.1. It is **content**, not structure: **it amends no decision in §15.1, reopens nothing, approves nothing, closes no gap, and meets no gate.** The approval record above stands exactly as written.

> **Superseded status note.** This §19 header table is the **6 September authoring-pass snapshot**, taken before the normalisation rule existed. The completion pass (§20, 6 Sep) proposed **N-TEXT**, completing property 5; **PD-B (§21, 7 Sep) then APPROVED `v0.1-draft`, its one-attribute scope and N-TEXT.** For the current status of this version read **§20.4** and **§21**. The "NOT COMPLETE" / "property 5's rule does not exist" rows below record only the state at authoring time.

| Field | Value |
| --- | --- |
| Vocabulary version | **`v0.1-draft`** — **NOT FROZEN** (X4 unmet; **G-19** open and may still add a property) |
| Release marking | **NOT RELEASABLE** — every sensitivity tier reads TBD (**G-13.9**, gate **G-13-B**) |
| Gate-A completeness | **NOT COMPLETE.** No entry carries properties 1–6 complete, because **property 5's rule does not exist for any category** (§15.3 **T3**, exit criterion **X7**) |
| Entries authored | **One** — `person.full_name` (§19.4) |
| Candidates examined and **not** authored | **Nine** (§19.5) |
| Attributes approved | **None.** Authoring is not approval (**G-13.1** — PM owns content) |
| Evaluation readiness | **None claimed.** No entry is evaluation-ready or implementation-ready by virtue of having been authored (§19.6) |

---

### 19.1 (A) The approved structure this pass stands on — recap, not re-decided

| Approved decision | What it contributes to this pass | Re-decided here? |
| --- | --- | --- |
| **G-13.1** | PM owns contents; Engineering owns format. This pass *proposes* content; it cannot approve it | **No** |
| **G-13.2** (as revised) | The seven properties, property 6 being a scope-keyed cardinality. Every entry below uses exactly these seven | **No** |
| **G-13.3** | Identity by the field→attribute mapping alone. No entry below is identified by label, value, proximity, or position | **No — not reopened** |
| **G-13.5** (as revised) | Comparison is the normalised form within a scope instance. This is why property 5 and property 6 are load-bearing, and why an unresolved property 5 blocks completeness | **No** |
| **G-13.8** | The vocabulary is authored before the per-type field sets and is never engine-derived. No corpus has been collected and no engine has been run (**0 documents**, **G-02** collection not begun), so nothing below is engine-derived | **No** |
| **G-13.9** (as narrowed) | Tier slot present and TBD at gate A; the version is marked NOT RELEASABLE | **No** |
| **G-13.11** (trigger clarified) | Nothing below may enter code, configuration, schema, migrations, fixtures, or evaluation tooling — the trigger is **G-13-A**, which is **not met** | **No** |
| **G-13.12** | Minimum justifiable vocabulary; the burden of proof sits on **including** an attribute. This is the test that decided nine of ten outcomes below | **No** |
| **G-13.15** | The scope-instance resolution rule is PM's and remains **unresolved** (**T12**, **X17**). Nothing below resolves it | **No** |

**§15.4 is unchanged.** The ten G-12 candidates remain a **DRAFT CANDIDATE SET**, and challenges **C-a … C-d** remain open. This pass **tests** them; it does not adopt, approve, or repair them.

---

### 19.2 The admission test actually applied

Every test below is taken from an approved decision or an existing exit criterion. **No new test is invented, and no test is waived.**

| # | Test | Source | What it demands |
| --- | --- | --- | --- |
| **T-a** | **Discriminating consumer** | **G-13.12**; §15.4 **C-a** | A named requirement that consumes *this* attribute, and would be inoperative or under-specified without it. A requirement that admits every candidate equally (**FR-FILL-001**) does not discriminate and does not satisfy the test |
| **T-b** | **Gate-A property completeness** | **G-13.2**; §18 **X6**, **X7**, **X8** | Properties 1–6 complete, property 7 present and TBD. A property whose content the requirements do not supply is marked **unresolved** — it is not filled by inference |
| **T-c** | **Definitional precision** | **G-13.2** property 3; **G-13.3**; §15.4 **C-d** | A semantic definition precise enough that two authors mapping two documents agree. A definition by page position rather than meaning fails |
| **T-d** | **Challenges discharged** | §18 **X18** | **C-a … C-d** discharged for that candidate, or the candidate is not admitted |
| **T-e** | **Minimality and safety** | **G-13.12**; **BR-017**; **NFR-PRIV-001**; **BR-016** | An attribute no requirement consumes is retained personal data with no justifying function. Where a *prior* safety decision governs whether the value may exist at all, that decision precedes the attribute |

---

### 19.3 The governing finding — what `backend/step3.pdf` actually names

§3.2 searched the structural vocabulary of the gap (*canonical*, *attribute*, *identifier*, *semantic*). **This pass searched the other direction: for personal data itself.** The result governs every outcome in §19.4 and §19.5.

| Term searched | Occurrences in 39 pages | Every occurrence, and its sense |
| --- | --- | --- |
| **"Name mismatches"** | **1** | **§12.2**, the prioritisation rationale for **FR-INF-004**: *"Name mismatches (P-06) are a silent disqualifier. Detecting them is cheap; missing them undermines the correctness claim."* **This is the only place the specification names a personal datum** |
| *name* / *names* (all other uses) | 8 | Verbs, or the naming of a **field**, a **document**, or **information lost on deletion** — FR-DOC-007, FR-INT-004, NFR-USE-005, AC-US-002-3, AC-US-010-1, AC-US-019-1, §04 preamble. **None names a personal datum** |
| *address* | 2 | **§7.1** *"Identity and address — Aadhaar, PAN, address proof"* — a **document-type grouping label**; and *"every need N-01 to N-10 is addressed"* in the §13 coverage check. **No address attribute** |
| *Aadhaar*, *PAN* | 1 each | **§7.1 only**, as **document types**. Neither is described, and no field, number, or value of either is mentioned anywhere |
| *date of birth*, *birth* | **0** | The term does not appear |
| *roll*, *board*, *university*, *qualification*, *percentage*, *CGPA* | **0** | None appears |
| *grade*, *marks* | 0 as personal data | Only inside *"upgrade"*, *"degrade"*, *"marks as required"*, *"visibly marked"* |

**The finding, stated plainly.** The specification names **document types** (§7.1) and never names an attribute — with exactly one exception, **§12.2's "Name mismatches"**, which is a *reason given for a MUST requirement* and therefore requirement-grade evidence that the product must be able to compare **the person's name** across two documents.

**Consequence for T1.** Only one candidate passes **T-a** on evidence internal to `backend/step3.pdf`. For the other nine, the discriminating evidence **C-a** identified as owed — the field inventory of the **§10 / ASM-002** controlled mock form — still does not exist. Authoring them now would be exactly the invention **G-13.11** and **BR-009** exist to prevent.

---

### 19.4 (B) Vocabulary contents authored under T1

#### `person.full_name` — PROPOSED VOCABULARY ENTRY — REQUIRES PM APPROVAL

| # | Property | Value | Status and basis |
| --- | --- | --- | --- |
| **1** | **Canonical identifier** | `person.full_name` | **PROPOSED.** A stable machine handle is required by **G-13.4** and **FR-INF-004**'s need for a decidable identity; the specification supplies none (§3.3, §0.1 is the *requirement*-ID scheme and must not be cited). The string deliberately matches the G-12 candidate's identifier so the transfer is traceable — **which does not approve that candidate** (§19.4.1) |
| **2** | **Display label** | *"Full name"* | **PROPOSED — product decision, no requirement supplies it.** **NFR-USE-005** requires user language on product surfaces and thereby supports the *existence* of a label (**G-13.2** property 2); it does not supply this or any other label's value (§3.3) |
| **3** | **Semantic definition** | *The name of the person who owns the record, as printed on a document that evidences it.* | **PROPOSED.** Passes **T-c**: **§12.2** treats two documents printing different names as a **mismatch to detect**, which is only coherent if both printings are the same concept. **Excludes**, expressly: any name printed on a document that is not the record owner's — a parent's, a guarantor's, an issuing officer's. Which printed label on which document type maps here is **G-12's** (§15.2 F2), not decided here |
| **4** | **Data type** | **text** | **PROPOSED — inferred, and labelled as inference.** **FR-INF-008** names *casing* and *spacing* as normalisation categories, which apply only to text; **FR-FILL-001** and **FR-FLD-007** give the field-type set as *text, number, date*. **The specification states a data type for no attribute** (§3.3) |
| **5** | **Normalisation rule reference** | **UNRESOLVED at this pass — §15.3 T3.** *Resolved later the same day by the T1 completion pass: **N-TEXT**, §20.3 — proposed, requires approval* | **NOT COMPLETE AS AUTHORED HERE; completed in §20.4.** **FR-INF-008** requires normalisation and names the applicable categories (*casing*, *spacing*); **AR-DET-003** requires it to be deterministic and reversible. **No rule exists for either category** — T3 is an approved TBD, settled by PM informed by **D-02 §11.6**. G-12 §14.0.1's **N1/N2** are *candidate* rules inside an unapproved document and are **not adopted here**. **This single unresolved property is why the entry is not gate-A complete (X7)** |
| **6** | **Multiplicity — scope-keyed cardinality** | **one per `person`** | **PROPOSED — requirement-supported.** **§12.2** classifies a name difference between documents as a *mismatch*, i.e. a conflict and not legitimate multiplicity; **FR-INF-004** exists to detect it; **FR-ACC-003** — *"Each record shall belong to exactly one user. No shared, delegated, or multi-person records exist in MVP"* — makes `person` the record's single subject. Subject `person` is one of the two admitted by the approved **G-13.2** revision |
| **7** | **Sensitivity tier** | **TBD — slot present, empty** | **CORRECT AT GATE A, by design.** **FR-INF-007** requires a tier; **G-14** owns the rules and **G-15** the default; both are gated on assumption **A-5**. Assigning one here would resolve G-14/G-15 by the back door. The version is therefore **NOT RELEASABLE** (**G-13.9**, gate **G-13-B**) |

**Admission test result:** **T-a PASS** (§12.2 names this datum as the thing FR-INF-004 must detect) · **T-b FAIL on property 5 only** (T3) · **T-c PASS** · **T-d** — C-a discharged for this candidate by §12.2; **C-b, C-c, C-d do not apply to it** · **T-e PASS** (one attribute, consumed by a MUST requirement).

**Verdict: AUTHORED into `v0.1-draft` as proposed content. NOT gate-A complete. NOT evaluation-ready. NOT implementation-ready. NOT approved.**

##### 19.4.1 What authoring this entry does *not* do

- **It does not approve G-12's `person.full_name` row.** That row carries a data type, normalisation `N1 + N2`, multiplicity *single*, and applicability to nine document types. **None of those is adopted.** Multiplicity here is *one per `person`* under the revised property 6, not *single*; normalisation is **unresolved**; applicability is **G-12's** (§15.2 F1/F2) and is not restated. The identifier string is shared deliberately, so that if PM approves both, no rename is needed and no second concept is created.
- **It does not resolve the scope-instance question.** `person` is a *subject*; **G-13.15 / T12** — how an *instance* is resolved — remains unresolved. **FR-ACC-003** means the MVP record contains exactly one `person` instance, so the unresolved rule is **not exercised** by this entry. **That is an observation about MVP scope, not a resolution rule, and it must not be cited as one**; the rule is still owed, and **X17** still gates gate A because the `qualification` subject needs it.
- **It creates no field, names no document type, and maps nothing.** The field→attribute mapping is **G-12's** in both directions (§13.1, §15.2).

---

### 19.5 (C) Candidates examined and NOT authored

Each row states the test failed and what would discharge it. **None is rejected; each remains a candidate.** Naming them here is required to record *why* they are not authored — no attribute below is created, and none enters `v0.1-draft`.

| Candidate | First test failed | Why, on the evidence | What would discharge it | Disposition |
| --- | --- | --- | --- | --- |
| `person.date_of_birth` | **T-a** | **The strongest near-miss.** The specification establishes that *a* date-typed attribute exists — **AC-US-008-4** reformats a stored date to a field's declared format, and **FR-INF-008** names *dates* as a normalisation category, which would be inert otherwise. **It never says which date.** *"date of birth"* and *"birth"* appear **zero** times. Naming it requires domain knowledge, which **BR-009** and G-13.11 forbid substituting for evidence | The **§10 / ASM-002** mock-form field inventory — a team-constructed artefact needing no corpus — or a specification amendment under §11's Containment Rule | **CANDIDATE — evidence insufficient to name.** Recommended first candidate for a second T1 pass once the mock form exists |
| `person.postal_address` | **T-b** | **C-b stands unrepaired.** No data type and no normalisation rule; G-12 **§18.3** leaves the component set undecided, and *address* appears in the specification only as a **document-type grouping label** (§7.1) and in the word *"addressed"*. Property 4 and property 5 are both unfillable | G-12 §18.3 resolved (one string or a structured object, and which components), **and** T-a evidence that a named requirement consumes it | **CANDIDATE — undefinable now.** C-b unresolved |
| `person.aadhaar_number` | **T-e** | **C-c stands.** A prior safety decision governs whether the value may exist at all: **D-02 §11.7** and register **D-05.3** leave open *"whether the identifier number is stored at all, masked, or stored in part"*. **BR-017** and **NFR-PRIV-001** put the burden on inclusion. *Aadhaar* appears once in 39 pages, as a **document type**, with no field of any kind described | **D-05.3 / D-02 §11.7** answered first. If the answer is *not stored*, the attribute must not exist | **CANDIDATE — blocked by a prior safety decision.** **NOT EVALUATION-READY**, per C-c, overriding G-12 §19.1's EVALUATION-READY rating |
| `person.pan_number` | **T-e** | As above, identically. *PAN* appears once, in §7.1, as a **document type** | As above | **CANDIDATE — blocked by a prior safety decision. NOT EVALUATION-READY** |
| `education.awarding_body` | **T-a** | **C-a stands.** *board*, *university* and *qualification* appear **zero** times. G-12's discriminating claim — *"a form's education block asks for the awarding body"* — **is not in `backend/step3.pdf`**; its only named consumer is **FR-FILL-001**, which admits every candidate equally | The **§10 / ASM-002** mock-form field inventory | **CANDIDATE — no discriminating consumer** |
| `education.qualification_name` | **T-a** | As above. *qualification* appears zero times | As above | **CANDIDATE — no discriminating consumer** |
| `education.year_of_passing` | **T-a** | As above. Additionally, G-12 **§18.4** leaves granularity open — some documents print a month and year — so property 4 is contestable even if T-a were passed | As above, plus §18.4 | **CANDIDATE — no discriminating consumer** |
| `education.aggregate_result` | **T-c** | **C-d stands, and is the hardest failure.** G-12 defines it *"exactly as the document prints it"* — a definition **by page position, not by meaning** — and its own §18.5 concedes a percentage, a CGPA and a letter grade *"cannot be meaningfully compared"*. **FR-INF-004** over it would be inoperative as defined, which is a defect in the definition, not in the requirement | Redefinition by meaning with a stated comparison basis, **or** withdrawal. It fails T-a as well | **CANDIDATE — must be redefined or withdrawn.** C-d unresolved |
| `education.roll_number` | **T-a** | *roll* appears **zero** times as personal data. Its only named consumer is FR-FILL-001. G-12 §16.1's own justification is a cross-document *match* between a marksheet and a hall ticket — and **D-04.4** records *"DECISION REQUIRED"* for **student ID** and **hall ticket**, so the document boundary it depends on is itself unsettled | The mock-form inventory, **and** **D-04.4** resolved | **CANDIDATE — no discriminating consumer; type boundary unsettled** |

**Five of the nine are `qualification`-scoped** (`awarding_body`, `qualification_name`, `year_of_passing`, `aggregate_result`, `roll_number`). Property 6 could *state* their subject — *one per `qualification`* — under the approved revision, because declaring a subject is not resolving an instance. **They are not authored for a reason that precedes scope entirely: no requirement names any of them.** Their scope-instance dependency on **G-13.15 / T12** and **X17** is real and additional, and is not the ground of this outcome.

---

### 19.6 Unresolved properties and questions carried by this pass

| # | Unresolved | Affects | Owner / route |
| --- | --- | --- | --- |
| **U1** | **The normalisation rule for every category** — §15.3 **T3**. **PARTIALLY RESOLVED (§20.3): N-TEXT** settles casing and spacing for a `text` attribute; **dates and numeric precision remain open**, as does any widening beyond the two named categories | Property 5 of every entry. **No longer blocks X7 for `v0.1-draft`**; blocks it again for any attribute in an unruled category | Approval of **N-TEXT**; the widening is **evaluation-dependent** on **D-02 §11.6**. G-12's N1–N5 are candidates in an unapproved document and remain unadopted |
| **U2** | **The scope-instance resolution rule** — **G-13.15**, **T12**, **X17** | Not exercised by `person.full_name` (**FR-ACC-003**, one instance); required before any `qualification`-scoped entry can be compared under **FR-INF-004** | PM · Architecture. Three of five candidate derivations remain live; **none is selected** |
| **U3** | **Every sensitivity tier** — **G-14**, **G-15**, assumption **A-5** | Property 7 of every entry. Gate **G-13-B** only | PM · Privacy; studies **S-1**, **S-4** |
| **U4** | **Profile vs structured record** — **G-19** | May still add an eighth property, which is why `v0.1-draft` **must not be frozen** (**X4** freezes the list once) | PM · Architecture |
| **U5** | **The discriminating consumer evidence** — §15.4 **C-a** | Nine of the ten candidates | The **§10 / ASM-002** mock-form field inventory. **No corpus is needed**; this is the cheapest open blocker in the set |
| **U6** | **Identifier-number storage** — **D-05.3**, **D-02 §11.7** | `person.aadhaar_number`, `person.pan_number`; and **G-02 §8.6**'s derived-artefact redaction scope, which *"cannot be answered today"* | PM · Privacy, before either attribute may exist or be annotated |
| **U7** | **The destination of an unmapped value** — **G-13.g1**, **T7**, **X11** | Every value an engine reads that `v0.1-draft` does not accept — which, with one entry, is **almost everything** | PM · Privacy. Still awaits a numbered register entry from that document's owner |
| **U8** | **Per-type field presence** — G-12 §18.6 | Whether any document type actually prints what a candidate assumes. **No corpus exists**; G-02 collection has not begun | Stage-1 evaluation under approved **G-02** governance |

---

### 19.7 (D) Dependencies preventing G-13-A closure

**G-13-A remains NOT MET.** X1 is met by the 6 September approval; nothing in **this** pass changes any other criterion's status. **The table below is the state at the T1 authoring pass. It is superseded by §20.5**, which resolves X3 and X5 and satisfies X7, X8, X10 and X18 for `v0.1-draft` on approval — and which leaves G-13-A **NOT MET**.

| Criterion | Status after T1 | What blocks it |
| --- | --- | --- |
| **X1** | **MET** | — |
| **X2** | Not met | **G-19** unanswered |
| **X3** | Not met | **G-13.g1** not yet recorded as a numbered gap by the register's owner |
| **X4** | Not met | The list freezes **once**; G-19 may still add a property (**U4**). Freezing now would be the one irreversible error available here |
| **X5** | Not met | Approved (**G-13.3**), but the criterion is stated against a frozen version, which does not exist |
| **X6** | **Not met — advanced, not satisfied** | One entry now exists in draft; **property 7 may read TBD at this gate, property 5 may not**, and it does (**U1**). Nine candidates are not authored (**U5**) |
| **X7** | Not met | **T3** — no normalisation rule exists for any category. **This is the binding constraint on the one authored entry** |
| **X8** | Partially demonstrated, not met | *one per `person`* is stated for the authored entry; unstated for every candidate not authored |
| **X9** | Not met — **gate B** | **G-14**, **G-15**, **A-5** |
| **X10** | Not met | **C-a** — the mock-form inventory (**U5**). Discharged for `person.full_name` alone, by §12.2 |
| **X11** | Not met | **G-13.g1** / **T7** (**U7**) |
| **X12** | Not met | `v0.1-draft` is a draft in an analysis document, not configuration. **G-13.11 forbids it entering configuration before gate A** |
| **X13** | Not met | Depends on **X6** |
| **X14** | Not met | Depends on **X6** |
| **X15** | Not met | Depends on X6, X7, X8, X17 |
| **X16** | Not met | The specification amendment (**G-13.13**) |
| **X17** | Not met | **G-13.15 / T12** (**U2**) |
| **X18** | Not met | **C-b**, **C-c**, **C-d** unrepaired; **C-a** discharged for one candidate only |

**The shortest path to gate A, on this evidence:** **U5** (the mock-form inventory — a team artefact, no corpus, no study), then **U1** (T3 normalisation rules), then **U4** (G-19, so the shape can freeze once), then **U2** (G-13.15). **U3** does not gate A.

---

### 19.8 (E) Evidence traceability

Every claim below is quoted from `backend/step3.pdf` or cited to an approved decision. **Where evidence is absent, the row says so rather than reaching for a substitute.**

| Attribute | Exact evidence | Source | What it establishes | What it does **not** establish |
| --- | --- | --- | --- | --- |
| `person.full_name` | *"Name mismatches (P-06) are a silent disqualifier. Detecting them is cheap; missing them undermines the correctness claim."* | **§12.2**, prioritisation rationale for **FR-INF-004** (MVP MUST) | That the product must compare **the person's name** across two documents — a **discriminating** consumer, which is what **G-13.12** and **C-a** require | Its data type, its normalisation rule, its display label, or its tier |
| `person.full_name` | *"The system shall detect when two documents give different values for the same attribute."* · *"Each record shall belong to exactly one user."* | **FR-INF-004**, **FR-ACC-003** (both MVP MUST) | Multiplicity **one per `person`**: a second name for the same person is a conflict, and the record has exactly one person | The scope-**instance** rule (**G-13.15**), which this entry does not exercise |
| `person.full_name` | *"normalise attribute formats deterministically — dates, casing, spacing, and numeric precision — without altering meaning"* | **FR-INF-008** (MVP MUST); **AR-DET-003** | That *casing* and *spacing* are the applicable categories, and that a rule is owed | **Any rule.** Property 5 stays unresolved (**T3**) |
| `person.date_of_birth` | *"GIVEN a date field with a declared format different from the stored format… the value is reformatted to the field's format without altering the date."* | **AC-US-008-4**; **FR-INF-008** *"dates"* | That **at least one date-typed attribute exists** in the record | **Which** date. *"date of birth"* and *"birth"* appear **zero** times in 39 pages |
| `person.postal_address` | *"Identity and address — Aadhaar, PAN, address proof."* | **§7.1** | A **document-type grouping label** | That an address **attribute** exists; its components; its type; its normalisation. G-12 §18.3 is unresolved |
| `person.aadhaar_number` · `person.pan_number` | *"Identity and address — Aadhaar, PAN, address proof."* — the only occurrence of either word | **§7.1**; and **D-02 §11.7** / **D-05.3** for the open storage question | That Aadhaar and PAN are **document types** in the MVP set, subject to **ASM-001** | That any number is extracted, stored, masked, or exists as an attribute. The storage question is **open and safety-relevant** |
| The five education candidates | **No evidence exists.** *board*, *university*, *qualification*, *roll*, *percentage*, *CGPA* — **zero occurrences each** | Full-text search of `backend/step3.pdf` (§19.3) | Nothing | Their existence, meaning, type, normalisation, multiplicity, or consumer. **C-a's owed evidence (§10 / ASM-002) does not yet exist** |
| `education.aggregate_result` | G-12 §18.5: a percentage, a CGPA and a letter grade *"cannot be meaningfully compared"* | G-12 (analysed, **not approved**) | That the candidate as defined **fails G-13.2 property 3** and would make **FR-INF-004** inoperative over it | Any repaired definition. **C-d is recorded, not fixed** |
| `education.roll_number` | **D-04.4** records *"DECISION REQUIRED"* for **student ID** and **hall ticket** | Register D-04.4 | That the document boundary its cross-document match depends on is **unsettled** | Anything about the attribute itself |

---

### 19.9 What this authoring pass does not do

1. **It does not approve any attribute.** `v0.1-draft` is proposed content; **G-13.1** gives approval to Product Management.
2. **It does not approve, adopt, or repair the ten G-12 candidates.** §15.4 stands; **C-a, C-b, C-c, C-d** stand. One candidate's *concept and identifier* are carried into an entry authored on independently stated evidence (§19.4.1); nine are not authored.
3. **It does not add an eighth property, and does not introduce scope as a property.** Every entry uses exactly the approved seven; scope appears only inside property 6's scope-keyed cardinality.
4. **It does not resolve G-13.15 or T12.** No scope-instance rule is chosen. **FR-ACC-003**'s single-person record is recorded as an *observation about MVP scope*, expressly not as a resolution rule.
5. **It does not resolve G-14, G-15, or assign any sensitivity tier.** Every property 7 reads TBD and the version is **NOT RELEASABLE**.
6. **It does not resolve G-19**, and therefore **does not freeze the property list** (**X4**).
7. **It does not resolve T3**, and therefore **no entry is gate-A complete** (**X7**).
8. **It does not close REQUIREMENTS GAP G-13**, and does not meet **G-13-A** or **G-13-B**.
9. **It does not claim evaluation readiness or implementation readiness for anything.** It expressly **overrides G-12 §19.1's EVALUATION-READY rating for `person.aadhaar_number` and `person.pan_number`**, which **C-c** requires to read **NOT EVALUATION-READY** until D-05.3 / D-02 §11.7 resolve.
10. **It amends no line of `backend/step3.pdf`** (**G-13.13**, **X16**), touches no production code, schema, migration, dependency, fixture, or evaluation tooling (**G-13.11**), collects no document, and runs no OCR.

## 20. T1 Completion Pass — Removing the Avoidable Gate-A Blockers

**T1 COMPLETION PASS — 6 September 2026. PROPOSED CONTENT — REQUIRES PRODUCT MANAGEMENT APPROVAL.**

This pass takes every remaining **G-13-A** criterion and asks one question: *can it be resolved from `backend/step3.pdf`, from an already-approved G-13 decision, from an already-recorded project decision, or from existing G-12 candidate evidence?* Where the answer is yes, it is resolved here. Where it is no, the pass states **exactly which product decision is required** and stops. **No requirement is invented, no gate is declared met, and REQUIREMENTS GAP G-13 stays OPEN.**

| Field | Value |
| --- | --- |
| Newly resolved | **§15.3 T3 for the text categories** (§20.3) · exit criteria **X3** and **X5** · **X7**, **X8**, **X10**, **X18** for `v0.1-draft` |
| Vocabulary version | **`v0.1-draft`** — one entry, now **complete in properties 1–6**, property 7 TBD by design. Still **NOT FROZEN**, still **NOT RELEASABLE** |
| Attributes authored | **One**, unchanged — §20.2 re-examined all ten candidates semantically and the outcome did not change |
| Gate status | **G-13-A NOT MET · G-13-B NOT MET** |
| Decisions required to finish gate A | **Five**, all Product Management's, **none requiring a corpus, an engine, or a study** (§20.6) |

---

### 20.1 What counted as resolvable

| Admitted as evidence | Not admitted |
| --- | --- |
| `backend/step3.pdf` read **semantically** — requirement text, document-type groupings, acceptance criteria, and what a MUST requirement would be inoperative without | General domain knowledge about Indian documents, forms, or naming conventions |
| The fifteen **approved** G-13 decisions (§15.1) | Any new decision branch. This pass creates none |
| Recorded project decisions — D-04.4, D-05.3, D-06.4, D-08.2, D-08.4, G-02, D-02 §11.6/§11.7 | Anything a study or a corpus would settle. **No corpus exists** |
| G-12's candidate evidence, **as evidence about the candidates**, never as approved content | G-12's proposed values (types, N1–N5, applicability). None is adopted |

---

### 20.2 The ten candidates, re-examined semantically

The T1 pass reported a term-frequency finding (§19.3). **That finding is not the test, and was not used as one.** Each candidate is re-examined below by asking what the requirements *entail*, not what they spell. **The outcome is unchanged — one attribute — but two candidates' reasons change, and both changes are recorded.**

| Candidate | Semantic re-examination | Outcome |
| --- | --- | --- |
| `person.full_name` | **§12.2** makes name comparison the worked justification for **FR-INF-004** (MUST). Unchanged | **AUTHORED** (§19.4, completed in §20.4) |
| `person.postal_address` | **CHANGED — the reason, not the outcome.** §7.1's own grouping label is *"**Identity and address** — Aadhaar, PAN, address proof"*, and **FR-OCR-004** (MUST) requires a defined field set to be extracted for every supported type. A supported type named *address proof*, grouped by the specification under *address*, whose extraction is required, **entails that the record holds an address concept**. T1 recorded this as *"no evidence it exists"*; **that was too strong, and is corrected here — existence is entailed.** It still fails **T-b**: the specification supplies **no data type and no normalisation rule**, and G-12 **§18.3** leaves the component set undecided. Authoring it as text would repair **C-b** silently, which §15.4 and X18 forbid | **CANDIDATE — existence entailed, representation undecided.** Requires **PD-A** (§20.6) |
| `person.date_of_birth` | **AC-US-008-4** requires a stored date to be reformatted to a field's declared format, and **FR-INF-008** names *dates* as one of four normalisation categories — a category that would be inert if the record held no date. **The specification therefore entails that at least one date-typed canonical attribute exists.** It names none, and nothing in §7.1, §04 or §10.1 identifies which date. Selecting *date of birth* is domain knowledge, which **BR-009** forbids substituting for evidence | **CANDIDATE.** The entailment is recorded in §20.5 as a concrete instance of gap G-13 for the **X16** amendment |
| `person.aadhaar_number` · `person.pan_number` | §7.1 names both as **document types** under *Identity*, and **FR-OCR-004** requires a field set for each — so *some* field is owed for each type. **Which** field is undefined, and the prior question is not definitional but **safety**: **D-05.3** and **D-02 §11.7** hold open *"whether the identifier number is stored at all, masked, or stored in part"*, with **BR-017** and **NFR-PRIV-001** placing the burden on inclusion. A decision that the number may not be stored would mean the attribute must not exist. Definitional work cannot precede it | **CANDIDATE — blocked by a prior safety decision.** **NOT EVALUATION-READY** (C-c) |
| `education.awarding_body` · `education.qualification_name` · `education.year_of_passing` · `education.aggregate_result` · `education.roll_number` | **AC-US-003-1** requires a processed marksheet to appear *"with its extracted information attached"*, and §7.1 admits four education types under **FR-OCR-004**. **The specification therefore entails that the education types have extractable fields** — and names not one of them, for any type. No requirement, acceptance criterion, edge case or business rule distinguishes an awarding body from a year from a result. The only named consumer for all five remains **FR-FILL-001**, which **C-a** already records as admitting every candidate equally | **CANDIDATES.** `education.aggregate_result` additionally fails **T-c** (**C-d**), which no amount of evidence about *existence* repairs |

**The finding this produces.** The specification **entails** that fields exist for the identity, address and education types — **FR-OCR-004** is a MUST and would otherwise be vacuous — and **names none of them**. That is not a defect in the search; it is the precise content of **REQUIREMENTS GAP G-13** together with **G-12**, and it is why nine candidates cannot be authored from `step3.pdf` alone. **The evidence that would name them is the §10 / ASM-002 controlled mock form's field inventory** — a team-constructed artefact requiring no corpus, no engine and no study (**C-a**). That, not further analysis, is the unblocking step.

---

### 20.3 T3 — the minimum semantic normalisation rule for a text attribute

**Proposed at this pass; APPROVED 7 September 2026 — PD-B (§21, D-05.11).** Recorded as **N-TEXT**. It resolves **§15.3 T3 for the two categories that apply to a text attribute** and leaves the other two open.

**Grounding, entirely in existing requirements and approved decisions:** **FR-INF-008** (MVP MUST) — *"normalise attribute formats deterministically — dates, casing, spacing, and numeric precision — **without altering meaning**"*; **AR-DET-003** — deterministic and **reversible**; **G-13.6** (approved) — the raw as-printed value is retained, which is what supplies reversibility; **G-13.5** (approved) — the normalised form is the comparison function for **FR-INF-004**; **AR-DET-008** — that comparison must be deterministic; **G-13.3** (approved) — identity is never established by value similarity.

#### N-TEXT — semantic content (this is the rule)

| # | The rule | Why it is not an invention |
| --- | --- | --- |
| **1** | **Casing is not meaning.** Two values that differ only in the case of their characters are **the same value** under FR-INF-004 | **FR-INF-008 states it**: casing is a normalisation category, and normalising it does not alter meaning. The requirement asserts the premise |
| **2** | **Whitespace run length and edge whitespace are not meaning.** Two values that differ only in the number of whitespace characters between tokens, or in leading or trailing whitespace, are **the same value** | **FR-INF-008** *"spacing"* / **AR-DET-003** *"whitespace"*. Same argument. (The wording divergence is **T4** and is unaffected) |
| **3** | **Nothing else is folded.** Any other difference — a different character, a different token, different punctuation, a different token order, an expanded or abbreviated token — **is a difference in value**, and **FR-INF-004** must raise it for the user | Forced by **BR-009** (no inferring from similar fields), **BR-004** (no resolution by rule), **BR-016** (fail towards inaction) and **G-13.3**. Folding more would suppress a real disagreement silently, which is the failure §12.2 calls *"a silent disqualifier"* |
| **4** | **The raw as-printed value is retained and is what the user sees.** Normalisation is a comparison-time form, never a display form | **G-13.6** (approved); **FR-OCR-007**; **NFR-USE-005**. No user-visible consequence follows from rules 1–3 |

#### What N-TEXT deliberately does **not** decide

| Excluded | Why |
| --- | --- |
| **The canonical spelling** — whether the normalised form is upper case, lower case, or any other fixed form | **No comparison outcome depends on it.** It is a format question, which **G-13.1** assigns to Engineering, and document 04's concern |
| **Unicode normalisation form, diacritic folding, script handling, transliteration** | **No requirement supplies any of them.** They are not excluded on principle — they are **not decided**. If a real corpus shows they cause false conflicts, adopting one is a change to conflict-detection behaviour and requires re-approval under **G-13.5**. This is the **evaluation-dependent** part of T3, owed to **D-02 §11.6** |
| **Punctuation stripping, token reordering, initial expansion, nickname or alias matching** | **Excluded on principle.** Each is identity by value similarity, barred by **G-13.3**, **AR-AST-007** and **BR-009** |
| **Any edit distance, similarity score, or threshold** | Same bar, plus **AR-DET-008**: a probabilistic comparison is not deterministic |
| **Any library, algorithm, or collation implementation** | Architecture, document 04. **G-13.1**'s content/format split |

#### Scope, and what remains open in T3

**N-TEXT applies to a canonical attribute whose data type is `text`.** The remaining two FR-INF-008 categories — **dates** and **numeric precision** — are **not stated here**, because **`v0.1-draft` contains no date-typed and no numeric attribute**. Writing a rule for an attribute that does not exist is precisely the invention this workstream forbids, and G-12 **§18.2** (day/month order in printed dates) shows the date rule is not free of an unresolved question in any case.

**T3 is therefore PARTIALLY RESOLVED**: settled for the categories that apply to the vocabulary as it stands, open for the categories that do not yet apply. **Exit criterion X7 reads *"covering all four categories **where applicable**"*, and is MET for `v0.1-draft` on the PD-B approval of N-TEXT (§21).**

#### Can N-TEXT be applied to the other candidates?

**Only to a candidate whose data type is settled as `text` — and no other candidate's is.** `person.postal_address` has no data type (**C-b**, §18.3). The four remaining education text candidates have no consuming requirement (**C-a**) and cannot be authored at all, so a normalisation rule for them would have nothing to attach to. The two identifier candidates are blocked by the storage decision. **N-TEXT is written to be reusable, and is used once.**

---

### 20.4 `v0.1-draft` after this pass

| # | Property | Value | Status |
| --- | --- | --- | --- |
| **1** | **Canonical identifier** | `person.full_name` | Proposed (§19.4) |
| **2** | **Display label** | *"Full name"* | Proposed — product decision |
| **3** | **Semantic definition** | The name of the person who owns the record, as printed on a document that evidences it | Proposed (§19.4) |
| **4** | **Data type** | **text** | Proposed — inference from FR-INF-008's categories, labelled as such |
| **5** | **Normalisation rule reference** | **N-TEXT** (§20.3) | **APPROVED 7 Sep 2026 (PD-B, §21).** Proposed at this pass; was UNRESOLVED at the T1 authoring pass |
| **6** | **Multiplicity — scope-keyed cardinality** | **one per `person`** | Proposed — requirement-supported |
| **7** | **Sensitivity tier** | **TBD — slot present, empty** | Correct at gate A. **G-14 / G-15, gate B** |

**Properties 1–6 are now complete. Property 7 is TBD by design.** The entry, its one-attribute scope and N-TEXT were **APPROVED as `v0.1-draft` on 7 September 2026 (PD-B — §21, D-05.11)**, satisfying **X7, X8, X10 and X18** for this version; **X6 stays NOT MET, formally gated on X4 and X17.** **The version is still not frozen, not releasable, not evaluation-ready and not implementation-ready.**

---

### 20.5 (7) Every gate-A criterion, classified

**Classification key:** **MET** · **RESOLVABLE NOW** — content proposed in this pass, needs only approval · **DECISION REQUIRED** — a real product decision, named · **DEPENDENCY** — waits on another criterion · **EVALUATION-DEPENDENT** — needs a corpus or a study · **REQUIREMENTS GAP** — closes only by amending the specification.

| # | Classification | Status after this pass | What it needs |
| --- | --- | --- | --- |
| **X1** | **MET** | **MET** — all fifteen decisions approved 5/6 Sep (D-05.6, D-05.8) | — |
| **X2** | **DECISION REQUIRED** | Not met | **PD-C — G-19.** Nothing in `step3.pdf` distinguishes FR-ACC-004's *profile* from FR-INF-001's *structured record*: both are maintained, both derived from processed documents, and no requirement treats them differently. **That is a finding, not a decision** — D-08.2 owns it, and this pass does not decide it |
| **X3** | **MET** | **MET — resolved in this pass.** **G-13.g1** is recorded in the register's §4 gap table as **G-29** by the register's owner | — |
| **X4** | **DEPENDENCY** | Not met | X2. The list freezes **once**; freezing before G-19 is the one irreversible error available here. PM's alternative — freeze now and accept the risk explicitly — remains recorded in §16.1 and is **not** taken here |
| **X5** | **MET** | **MET — resolved in this pass.** **G-13.3** is approved (X1) and states identity as a lookup through the field→attribute mapping, with label, value, proximity and position expressly excluded — applicable by an author without judgement | — |
| **X6** | **RESOLVABLE NOW**, then **DEPENDENCY** | **Contents and scope APPROVED 7 Sep 2026 (PD-B, §21); criterion remains NOT MET** | Every property except the tier is now complete (§20.4) and **approved**. **X6 stays gated on X4** (needs **G-19**/PD-C) **and X17** (needs **G-13.15**/PD-D), because an eighth property or a scope-instance rule would change what a complete entry is |
| **X7** | **RESOLVABLE NOW** | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B).** N-TEXT approved | The criterion reads *"where applicable"*; casing and spacing apply and are stated (§20.3); dates and numeric precision do not apply to any authored attribute. **Reopens if the version gains an attribute in an unruled category** |
| **X8** | **RESOLVABLE NOW** | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B)** | *one per `person`* is stated for the only entry |
| **X9** | **DEPENDENCY — gate B only** | Not met | **G-14**, **G-15**, assumption **A-5**, studies **S-1**/**S-4**. **Does not gate G-13-A** |
| **X10** | **RESOLVABLE NOW** | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B)** | The only entry is justified against **FR-INF-004** by §12.2. **C-a's owed mock-form inventory is required only for candidates that would be added** |
| **X11** | **DECISION REQUIRED** | Not met | **PD-E — the destination of an unmapped extracted value**: discarded, retained outside the record, or surfaced to the user. **G-13.7** (approved) excludes coercion and deliberately does not choose. With one attribute in the vocabulary, almost every readable value is unmapped, so this is **more** urgent, not less |
| **X12** | **DEPENDENCY**, then engineering | Not met — **PD-B discharged 7 Sep 2026; engineering act outstanding** | Its decision-dependency (PD-B) is now approved. **G-13.11** does not bar it: its post-gate-A bar is on production code, schema, migrations and stored production data, and configuration is where **G-13.1** and **G-13.10** put the artefact. What remains is the engineering act of holding and versioning it |
| **X13** | **DEPENDENCY** | Not met | **X6**. This is the criterion that unblocks **G-12** |
| **X14** | **DEPENDENCY** | Not met | **X6** |
| **X15** | **DEPENDENCY** | Not met | X6, X7, X8, **X17**. Also still owes D-02 its fourth false-conflict attribution category, which is that document's owner's |
| **X16** | **REQUIREMENTS GAP** — **not a gate-A criterion** | Not met | The §11 Containment Rule amendment. §20.2's entailments — *a date-typed attribute is required and none is named*; *education types must have extractable fields and none is named* — are concrete material for it |
| **X17** | **DECISION REQUIRED** | Not met | **PD-D — G-13.15.** Either select a scope-instance derivation from the three live candidates, **or** approve the narrowing proposed below |
| **X18** | **RESOLVABLE NOW** | **MET for `v0.1-draft` — 7 Sep 2026 (PD-B)** | The criterion is conditional — *"discharged for every candidate **before it enters X6**"*. **No challenged candidate enters `v0.1-draft`**, so nothing is owed for this version. **C-a…C-d remain open and reopen this criterion the moment any candidate is added** |

#### A narrowing proposed for X17 — **PROPOSED, NOT TAKEN**

**X17 could be read per-subject rather than per-version:** *the scope-instance resolution rule is required before the first attribute of that subject enters a vocabulary version.* On that reading `v0.1-draft` — which contains one `person`-scoped attribute, in a record **FR-ACC-003** makes single-person — would not need it, and X17 would bind at the first `qualification`-scoped entry instead.

**This pass does not take that reading.** It is a change to an approved exit criterion and therefore **PD-D**, Product Management's. It is recorded because it is the difference between gate A waiting on **G-13.15** and gate A not waiting on it, and because the alternative — choosing a scope-instance model to unblock a vocabulary that contains nothing scoped that way — would be the invention **G-13.15** exists to prevent.

---

### 20.6 (B) The decisions required to finish gate A

**Five. All Product Management's. None requires a corpus, an engine, an OCR run, or a study.**

| # | Decision required | Unblocks | Note |
| --- | --- | --- | --- |
| **PD-A** | **The representation of an address** — one text value, or a structured object and which components | `person.postal_address` becomes authorable immediately (its existence is entailed, §20.2) | G-12 §18.3 owns it. **C-b** is discharged by this decision and by nothing else |
| **PD-B** | ~~**Approve `v0.1-draft`** — its contents, its one-attribute **scope**, and **N-TEXT**~~ | **X6, X7, X8, X10, X18**, then **X12** | **APPROVED 7 September 2026 (§21, D-05.11).** X7, X8, X10, X18 now MET for `v0.1-draft`; X6 stays gated on X4/X17; X12's decision-dependency discharged. The scope question was the substantive half: **G-13.12** puts the burden of proof on *including* an attribute, and on this evidence that yields one |
| **PD-C** | **G-19** — is FR-ACC-004's profile the same thing as FR-INF-001's structured record | **X2**, then **X4**, then the shape freezes once | D-08.2. Nothing in `step3.pdf` distinguishes them (§20.5 X2) |
| **PD-D** | **G-13.15** — select a scope-instance derivation, **or** approve the per-subject narrowing of X17 | **X17**, then **X15** | Three candidate derivations remain live; two are already excluded on requirement grounds |
| **PD-E** | **The unmapped-value destination** (**G-13.g1**, now register gap **G-29**) | **X11** | **G-13.7** excluded coercion and deferred the destination. Privacy consequence |

**Then, and only then, G-12.** **X13** follows from **X6**; nothing else in this document gates it.

**Not on this list, deliberately:** **G-14** and **G-15** — they gate **G-13-B** only, and the §10.1 D7/D11 cost of D-06.4's interim default is recorded at **G-13.9** for whenever they are taken up.

---

### 20.7 What this pass does not do

1. **It approves nothing.** N-TEXT, the completed entry, and the X17 narrowing were all **proposed** at this pass; **G-13.1** gives approval to Product Management. *(N-TEXT and the entry were subsequently APPROVED as `v0.1-draft` by **PD-B**, §21 / D-05.11, on 7 September 2026; the X17 narrowing remains proposed — **PD-D**.)*
2. **It declares no gate met.** **G-13-A NOT MET**, **G-13-B NOT MET**.
3. **It does not close REQUIREMENTS GAP G-13**, and **no project decision here amends `backend/step3.pdf`** (**G-13.13**, **X16**).
4. **It adds no eighth property and no scope property.** Scope remains inside property 6.
5. **It does not resolve G-13.15**, and does not choose a scope-instance model. The X17 narrowing is a proposal about a *criterion's applicability*, not a scope model.
6. **It does not resolve G-19**, and does not freeze the property list.
7. **It does not resolve G-14 or G-15**, and assigns no sensitivity tier.
8. **It does not approve the ten G-12 candidates and repairs none of C-a…C-d.** `person.postal_address`'s *reason* is corrected (§20.2); its **blocker is unchanged**.
9. **It resolves T3 only for the categories that apply to an authored attribute.** Dates and numeric precision remain open, as does every widening beyond N-TEXT, which is **evaluation-dependent** under **D-02 §11.6**.
10. **It touches no production code, schema, migration, dependency, fixture, corpus, OCR engine, or evaluation tooling**, and creates no new decision branch. The one registry action taken — numbering **G-13.g1** as **G-29** — is the action the register itself already recorded as owed to its owner.

---

## 21. PD-B — PRODUCT DECISION — APPROVED (7 September 2026)

**Status: APPROVED.** Product Management approves **PD-B** as scoped in §20.6: **`v0.1-draft`'s contents, its one-attribute scope, and N-TEXT.** Recorded in [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) **D-05.11**. **This is a product decision standing beside `backend/step3.pdf` (G-13.1, G-13.13). It closes no requirements gap, meets no gate, and amends no line of the specification.**

The T1 completion pass (§20, 6 September 2026) *proposed* these three items and approved nothing (§20.7). This section takes the approval the pass owed to Product Management, and only that. **PD-A, PD-C, PD-D and PD-E are not taken here.**

### 21.1 What is approved — exactly three things

| # | Approved | Evidence it rests on | Where it lives |
| --- | --- | --- | --- |
| 1 | **The one entry `person.full_name`** as vocabulary version **`v0.1-draft`**, properties 1–6 complete (§20.4), property 7 (**sensitivity tier**) **TBD by design** — the slot is present and empty, and its content is **G-14/G-15**, gate **G-13-B** | **§12.2** makes name comparison the worked justification for **FR-INF-004** (MUST); **P-06** names name mismatches "a silent disqualifier". Grounded, not invented | §19.4, §20.4 |
| 2 | **The one-attribute scope** — that `v0.1-draft` contains this entry **and no other** on the present evidence | **G-13.12** (approved) puts the burden of proof on *including* an attribute; each of the nine other candidates carries a recorded blocker (§19.5, §20.2 — C-a…C-d, a prior safety decision, or an undecided data type). On this evidence exactly one attribute qualifies | §19.5, §20.2 |
| 3 | **N-TEXT** — the minimum semantic normalisation for a `text` attribute: **casing differences do not change value identity; edge whitespace and whitespace-run length do not change meaning; no other folding is assumed; the raw as-printed value is retained and is what the user sees** | Entirely **FR-INF-008** ("casing, spacing … without altering meaning"), the deterministic-and-**reversible** normalisation requirement, **AR-DET-008** (determinism), and approved **G-13.3 / G-13.5 / G-13.6**, with **BR-004 / BR-009 / BR-016** forcing the conservative "nothing else is folded" clause | §20.3 |

**N-TEXT leaves undecided, deliberately:** Unicode normalisation form, diacritic folding, transliteration, punctuation folding, token reordering, alias/nickname matching, edit distance, and any similarity threshold. None is supplied by a requirement; each is either barred by **G-13.3** (identity by value similarity) and **AR-DET-008** (a probabilistic comparison is not deterministic), or is **evaluation-dependent** under **D-02 §11.6** and would require re-approval under **G-13.5**. Approving PD-B does not adopt any of them (§20.3).

### 21.2 What the approval changes — the gate-A criteria it satisfies

| Criterion | Before | After PD-B |
| --- | --- | --- |
| **X7** — a normalisation rule for every attribute, all four categories where applicable | Satisfied *on approval of N-TEXT* | **MET for `v0.1-draft`.** Casing and spacing stated; dates and numeric precision apply to no authored attribute. **Reopens if the version gains an attribute in an unruled category** |
| **X8** — scope-keyed multiplicity stated for every attribute | Satisfied *on approval* | **MET for `v0.1-draft`** — *one per `person`* is stated for the only entry |
| **X10** — every attribute justified against a consuming requirement | Satisfied *on approval* | **MET for `v0.1-draft`** — the only entry is justified against **FR-INF-004** by §12.2 |
| **X18** — §15.4's C-a…C-d discharged for every candidate before it enters X6 | Satisfied *for `v0.1-draft` on approval* | **MET for `v0.1-draft`** — no challenged candidate enters this version. **C-a…C-d remain open and reopen this criterion the moment any candidate is added** |
| **X6** — the vocabulary authored, every attribute carrying all seven properties | Not met; contents/scope proposed | **Contents and scope APPROVED**, but **X6 remains NOT MET** — it is formally gated on **X4** (needs **G-19**/PD-C) and **X17** (needs **G-13.15**/PD-D). Approving the contents does not lift those |
| **X12** — the artefact held as configuration and versioned | Dependency on PD-B, then engineering | **Its decision-dependency (PD-B) is now discharged.** **Still NOT MET** — the engineering act of holding and versioning it is outstanding |

### 21.3 What the approval does NOT do

1. **It does not close REQUIREMENTS GAP G-13.** The gap stays **OPEN** in the register's §4; the specification still names no attribute, and closing it needs the §11 Containment Rule amendment (**X16**, **G-13.13**).
2. **It does not meet gate G-13-A.** **G-13-A remains NOT MET** — **X2, X4, X6, X11, X13, X14, X15 and X17** are still unmet. **G-13-B remains NOT MET.**
3. **It assigns no sensitivity tier.** Property 7 stays **TBD by design**; **G-14 and G-15** are untouched and gate **G-13-B** only.
4. **It resolves neither G-19 (PD-C), G-13.15 (PD-D), nor G-29 (PD-E),** and does not freeze the property list (the shape freezes once, at **X4**, after G-19).
5. **It adds no eighth property and no scope property.** Scope remains inside property 6. The count stays **seven**.
6. **It approves none of the nine candidates and repairs none of C-a…C-d,** and does not make PD-A's address decision.
7. **It widens N-TEXT no further than casing and spacing;** dates and numeric precision remain TBD, and every widening is evaluation-dependent under **D-02 §11.6**.
8. **It amends no line of `backend/step3.pdf`** and **touches no production code, schema, migration, dependency, fixture, corpus, OCR engine, or evaluation tooling.**

## 22. PD-A, PD-C, PD-D, PD-E — PRODUCT DECISIONS — APPROVED (8 September 2026)

**Status: APPROVED.** Product Management approves the four gate-A decisions named in §20.6 and laid out in [`SPRINT_4_G13_PM_DECISION_BRIEF.md`](SPRINT_4_G13_PM_DECISION_BRIEF.md). Recorded in [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) **D-05.12**. **These are product decisions standing beside `backend/step3.pdf` (G-13.1, G-13.13). They close no requirements gap, and amend no line of the specification.** With PD-B (§21) they complete every **Product-Management-owned** gate-A criterion; two gate-A criteria that are **not** PM decisions remain (§22.4).

### 22.1 What is approved — exactly four decisions

| # | Approved | Evidence it rests on |
| --- | --- | --- |
| **PD-A** | **Structured address representation.** `person.postal_address` is a **structured object**, not a single text value. **Its component set is derived only from the §10 / ASM-002 mock-form field inventory — none is invented here.** Until that inventory is produced, the attribute's shape is decided (structured) and its components are pending that artefact | §7.1 groups a supported type under *"Identity and address"* and **FR-OCR-004** (MUST) requires a field set per type → an address concept is entailed (§20.2); **FR-FILL-002** requires fields matched in parts; the mock form is a team artefact needing no corpus, engine, or study (**C-a** unblocker) |
| **PD-C** | **G-19 — one store, two views.** The **FR-ACC-004** profile is the **resolved view** over per-document **FR-INF-001** observations; it is not a second copy | Register **D-08.2**. Gives **FR-INF-003** (correction authoritative), **FR-INF-006** (authoritative value + retained alternatives) and **AC-US-005-1** (no authoritative value during a conflict) one coherent home. It is a **data-model relation (D-08)** between resolved values and observations, and **adds no eighth property** to the seven-property definition shape |
| **PD-D** | **G-13.15 / X17 — narrowed per-subject.** The scope-instance resolution rule is required before the first attribute **of a subject** enters a version. `v0.1-draft`'s one `person`-scoped attribute, in a record **FR-ACC-003** makes single-person, needs none. The derivation for `qualification` is **deferred** to the first `qualification` attribute and to the **G-12 mapping** | §20.5's proposed narrowing, now taken. Constrained by **AR-DET-008** and **G-13.15**; invents no scope-instance model for values that do not yet exist |
| **PD-E** | **G-29 — discard unmapped values for MVP.** An extracted value that maps to no canonical attribute is **not retained**. The **original document is retained** (Sprint 3) as the recovery source; **FR-OCR-010** reprocessing recovers the value once the vocabulary gains the attribute. Coercion stays barred (**G-13.7**) | **BR-016** (fail towards inaction), **BR-017 / NFR-PRIV-001** (minimality — burden on inclusion); avoids untiered personal data accumulating (**FR-INF-007** / §12.3 hazard) |

### 22.2 What the approval changes — the gate-A criteria it satisfies

| Decision | Directly satisfies | Then enables |
| --- | --- | --- |
| **PD-C** | **X2** (G-19 answered) → **X4** (the seven-property shape freezes; C1 adds no property) | **X6** (with X17), then **X8** |
| **PD-D** | **X17** (per-subject; `v0.1-draft` needs no scope-instance rule) | **X6**, and X15's X-dependencies |
| **PD-E** | **X11** (unmapped-value destination decided) | — |
| **PD-A** | discharges **C-b**; makes `person.postal_address` authorable (shape decided; components pending the mock-form inventory) | required before any **second** attribute enters `v0.1-draft`; does not itself flip an X for the one-entry version |

**The cascade for `v0.1-draft`.** With **X4** (PD-C), **X5** (already met) and **X17** (PD-D) all met, **X6 becomes MET** for `v0.1-draft` — its one entry carries properties 1–6 complete (property 5 = N-TEXT), property 7 TBD by design. X6 being met in turn makes **X13** (G-12 field sets authorable — mapping to the one attribute or, per PD-E, explicitly to none) and **X14** (D-02 L6/L7 annotatable) MET. **X15 does not follow**, for the reason in §22.4.

### 22.3 G-13-A recalculated — every gate-A criterion after PD-A/C/D/E

| # | Gate | Criterion (abbrev.) | Status after 8 Sep 2026 |
| --- | --- | --- | --- |
| **X1** | A | Decisions approved | **MET** (6 Sep) |
| **X2** | A | G-19 answered | **MET — PD-C** |
| **X3** | A | G-13.g1 recorded as a gap | **MET** (G-29, 6 Sep) |
| **X4** | A | Seven-property shape frozen | **MET — PD-C** (G-19 answered; C1 adds no property; shape frozen at seven) |
| **X5** | A | Identity relation approved | **MET** (6 Sep) |
| **X6** | A | Vocabulary authored, all seven properties (7 may be TBD) | **MET for `v0.1-draft`** — gated only on X4 and X17, now both met |
| **X7** | A | Normalisation rule per attribute | **MET for `v0.1-draft`** (N-TEXT, PD-B) |
| **X8** | A | Scope-keyed multiplicity per attribute | **MET for `v0.1-draft`** (PD-B; X4/X6/X17 now met) |
| **X9** | **B** | Sensitivity tier assigned | **NOT MET — gate B** (G-14/G-15); not required for gate A |
| **X10** | A | Each attribute justified against a consumer | **MET for `v0.1-draft`** (PD-B) |
| **X11** | A | Unmapped-value destination decided | **MET — PD-E** |
| **X12** | A | Vocabulary held as versioned configuration | **MET — 8 Sep 2026 (§22.6):** artefact `config/vocabulary/canonical_attributes.v0.1-draft.toml`, versioned; `tests/test_vocabulary_config.py` (13 tests) pass |
| **X13** | A | G-12 field sets authorable | **MET** (follows X6) |
| **X14** | A | D-02 L6/L7 annotatable | **MET** (follows X6; G-13.11 permits at gate A) |
| **X15** | A | D-02 §11.6 evaluation designable | **MET — 8 Sep 2026 (§22.7):** the fourth attribution category (scope collapse) applied at D-02 §11.6.1 |
| **X16** | — | `step3.pdf` amended or divergence recorded | **NOT MET** — not a gate-A criterion; gap-closure only |
| **X17** | A | Scope-instance rule decided | **MET for `v0.1-draft`** — PD-D (per-subject narrowing) |
| **X18** | A | C-a…C-d discharged for any entering candidate | **MET for `v0.1-draft`** — no challenged candidate enters |

**G-13-A: MET — 8 September 2026 (§22.7).** Every gate-A criterion (X1–X8, X10–X14, X17, X18) is satisfied: the PM-owned criteria by PD-A/B/C/D/E, **X12** by the versioned configuration artefact (§22.6), and **X15** by applying the fourth false-conflict attribution category at D-02 §11.6.1 (§22.7). **G-13-B remains NOT MET** — property-7 tiers (G-14/G-15) and §12.3's A-5/A-7.

### 22.4 What remains before G-13-A can close

| Remaining | Owner | What it is |
| --- | --- | --- |
| ~~**X12**~~ | Engineering | **MET 8 September 2026 (§22.6)** — the vocabulary is held as a versioned configuration artefact |
| ~~**X15**~~ | D-02 document owner | **MET 8 September 2026 (§22.7)** — the fourth false-conflict attribution category (scope collapse) is applied at D-02 §11.6.1 |

**X15 was closed on 8 September 2026 (§22.7); every gate-A criterion is now met — G-13-A is MET.** No further PM decision is required for gate A. (**Gate G-13-B** remains separately blocked on **G-14 / G-15** — the sensitivity tiers, property 7 — and on §12.3's assumptions A-5 / A-7; that is unchanged.)

### 22.5 What the approval does NOT do

1. **It closes no requirements gap.** **REQUIREMENTS GAP G-13 remains OPEN**; `step3.pdf` still names no attribute, and closing it needs the §11 Containment-Rule amendment (**X16**, **G-13.13**) — **not made, by instruction**.
2. **It meets no gate.** **G-13-A remains NOT MET** (X12, X15 outstanding); **G-13-B remains NOT MET**.
3. **It creates no attribute beyond `v0.1-draft`.** The nine candidates stay unauthored, §15.4's set stays **draft**, and **C-a…C-d remain open** — so **X18 reopens the moment any candidate is added**. PD-A decides the address *shape* only; it authors no entry and does not choose the component set (deferred to the mock-form inventory).
4. **It assigns no sensitivity tier.** Property 7 stays **TBD by design**; **G-14 / G-15** are untouched and gate G-13-B only.
5. **It chooses no `qualification` scope-instance derivation** — PD-D defers that to the first `qualification` attribute; and it invents no address component set.
6. **It amends no line of `backend/step3.pdf`** and **touches no production code, schema, migration, dependency, fixture, corpus, OCR engine, or evaluation tooling.** No commit or push.

### 22.6 X12 — MET (8 September 2026): the vocabulary held as versioned configuration

**Status: MET.** The engineering act X12 required — *"the artefact is held as configuration and versioned"* (G-13.1, G-13.10) — is done. It is an engineering act, **not a PM decision**, and G-13.11 does not bar it: its post-gate-A bar is on production code, schema, migrations and stored production data, and **configuration is where G-13.1 and G-13.10 put the artefact** (§18 X12).

| What | Where |
| --- | --- |
| **Configuration artefact** | `backend/config/vocabulary/canonical_attributes.v0.1-draft.toml` — TOML (repo convention: `pyproject.toml`; stdlib-readable via `tomllib`, no new dependency). Holds **exactly** `v0.1-draft`: the one entry `person.full_name` with the seven properties in order, **no eighth property**, property 7 (`sensitivity_tier`) **TBD by design** (`status = "TBD"`, empty value), the **scope-keyed cardinality** (`one` per `person`), and **N-TEXT** as a named rule referenced by property 5. Artefact-level `vocabulary_version = "v0.1-draft"` (also in the filename); `releasable = false` (G-13.9, tiers TBD) |
| **Validation** | `backend/tests/test_vocabulary_config.py` — 13 tests: structural validity, version/filename agreement, not-releasable, exactly one entry, exactly the seven property keys, the `person.full_name` values preserved verbatim, property 6 = *one per person*, property 7 = TBD slot present-and-empty, N-TEXT's four approved semantics, and a guard that N-TEXT is **not silently widened** and no second rule or tier content has crept in. **All 13 pass.** |

**What X12 being MET does and does not mean.**
- It **does not touch production code**: the artefact is configuration, the tests are test code, and **D-01's replaceable extraction interface (`app/services/extraction.py`) is untouched**. The artefact is not wired into extraction — placing values into the running system is gate-B build work.
- It **resolves no open gap**: G-14/G-15 (property 7), G-19, G-29 and G-13.15 stand exactly as their already-approved decisions leave them; no attribute is added; `step3.pdf` is unchanged.
- At the time X12 was recorded, **X15** was still open; it was closed later the same day (§22.7), so **G-13-A is now MET** — see §22.7.

### 22.7 X15 — MET (8 September 2026): G-13-A now MET

**Status: MET.** The last gate-A criterion, **X15** — *"D-02 §11.6 conflict-detection evaluation becomes designable against a real subject"* — is satisfied. Its only outstanding dependency was the **fourth false-conflict attribution category** owed to the owner of the evaluation plan; that category, analysed at **§11.4.1** of this document, is now **applied** at **D-02 §11.6.1**.

| What | Detail |
| --- | --- |
| **Fourth attribution category** | **scope-model error (scope collapse)** — added to D-02 §11.6's false-conflict source-attribution measure as a fourth cause beside extraction error, normalisation, and genuine document variance (D-02 §11.6.1). It is told apart from genuine variance by whether the two values map to the same canonical attribute but **different scope instances of its subject** (G-13.2 property 6), read from the L6/L7 ground truth. **No new evaluation methodology is introduced** — the recorded §11.4.1 analysis is applied. |
| **Designable against a real subject** | `v0.1-draft`'s `person.full_name` is `person`-scoped in a single-person record (**FR-ACC-003**), so scope collapse cannot arise for it and no extra annotation is owed to design the measure against that subject; the scope-instance annotation binds when a `qualification`-scoped attribute later enters, following **PD-D**. |

**G-13-A recalculated — MET.** Every gate-A criterion is satisfied: **X1–X8, X10, X11, X12, X13, X14, X17, X18** and now **X15**. Recorded in the register at **D-05.14**.

**What this does NOT do.**
1. **It does not close REQUIREMENTS GAP G-13.** The `step3.pdf` §11 Containment-Rule amendment (**X16**) is still owed; the gap stays **OPEN**.
2. **It does not meet G-13-B.** Property-7 sensitivity tiers remain **TBD** (**G-14 / G-15**), and §12.3's assumptions **A-5 / A-7** still gate any build.
3. **It changes no production code, no approved vocabulary content, and no line of `backend/step3.pdf`**, and resolves neither G-14 nor G-15. No commit or push.

**What gate A now unblocks:** **G-12** authoring, and the **design and annotation** of the §11 field-extraction and §11.6 conflict-detection evaluations — not their *execution*, which additionally needs the vocabulary's contents and G-12 (both beyond gate A).

---

### G-13 Decision Summary

| ID | Decision | Status | Source / Reason | Approval Required |
| --- | --- | --- | --- | --- |
| **G-13.a** | A profile of canonical personal attributes exists, derived from documents and user-editable | **REQUIREMENT** | FR-ACC-004 (MVP, MUST) | No — already binding |
| **G-13.b** | A structured record spans all processed documents | **REQUIREMENT** | FR-INF-001 (MVP, MUST) | No — already binding |
| **G-13.c** | Every attribute value references its source document and the confidence it was read with | **REQUIREMENT** | FR-INF-002 (MVP, MUST); BR-010 | No — already binding |
| **G-13.d** | Every attribute carries exactly one of routine / sensitive / consequential, raise-only | **REQUIREMENT** | FR-INF-007, FR-SENS-001/006, BR-020, AR-AST-007 | No — already binding |
| **G-13.e** | Attribute formats are normalised deterministically, reversibly, meaning-preservingly, over four named categories | **REQUIREMENT** | FR-INF-008 (MUST); AR-DET-003 | No — already binding |
| **G-13.f** | Conflict detection is deterministic; resolution is never automated | **REQUIREMENT** | FR-INF-004/005, AR-DET-008, BR-004 | No — already binding |
| **G-13.g** | A user correction is authoritative over any extracted value and is never automatically overwritten | **REQUIREMENT** | FR-INF-003, BR-012, AC-US-004-2/3 | No — already binding |
| **G-13.h** | **No canonical attribute is defined anywhere; "canonical" appears once in 39 pages and is never elaborated** | **REQUIREMENTS GAP (G-13)** | Full-text search of `step3.pdf`; FR-ACC-004 carries no TBD marker | Closure requires PM |
| **G-13.i** | **The identity relation "the same attribute" is used three times and defined zero times, while AR-DET-008 requires it to be deterministic** | **REQUIREMENTS GAP (G-13)** | FR-INF-004, EC-019, §6.4, AR-DET-008 | Closure requires PM |
| **G-13.j** | Attribute identifiers, names, value types and multiplicity are undefined; the four normalisation categories have no rules; **no requirement supplies a scope or grouping notion for an attribute** | **REQUIREMENTS GAP (G-13)** | §7.1; §11.1; §11.4.1 | Closure requires PM |
| **G-13.k** | **NFR-MNT-001 covers types and fields but not attributes — the vocabulary has no specified home** | **REQUIREMENTS GAP (G-13)** | NFR-MNT-001 verbatim | Closure requires PM |
| **G-13.l** | **No behaviour is defined for an extracted value that maps to no canonical attribute** | **REQUIREMENTS GAP — G-13.g1 (candidate new gap; register not modified)** | §12; unknown paths exist only at document-type and form-field level | Yes — PM · Privacy |
| **G-13.m** | Which concepts/fields exist per document type | **REQUIREMENTS GAP (G-12)** — *not resolved here* | FR-OCR-004; `SPRINT_4_G12_FIELD_DEFINITIONS.md` | Separate G-12 resolution |
| **G-13.n** | Sensitivity assignment rules and the default tier | **REQUIREMENTS GAP (G-14, G-15)** — *not resolved here* | FR-INF-007, AR-DET-005, NFR-MNT-004; A-5 | Separate resolution |
| **G-13.o** | Profile vs structured record | **REQUIREMENTS GAP (G-19)** — *upstream, not resolved here* | FR-ACC-004 vs FR-INF-001 | Separate resolution |
| **G-13.p** | What a duplicate attribute entry is | **REQUIREMENTS GAP (G-20)** — *downstream, not resolved here* | NFR-REL-005; register D-08.4 | Separate resolution |
| **G-13.q** | The vocabulary's actual contents | **TBD** | Authoring is PM's; producing a list here would be invention | Settled by authoring |
| **G-13.r** | The normalisation rule for each category | **TBD** | No rule stated for any category; each is a conflict-detection decision | Settled by PM, informed by D-02 §11.6 |
| **G-13.s** | "spacing" (FR-INF-008) vs "whitespace" (AR-DET-003) | **TBD** | Internal inconsistency in `step3.pdf` | Settled by specification amendment |
| **G-13.t** | Confidence scale; BR-001/BR-002 thresholds; global vs per-type | **TBD** | G-06, G-04, G-05, G-07 — independent of G-13 | Settled by evaluation, then PM |
| **G-13.u** | Whether extraction quality justifies the attribute-dependent requirements at all | **TBD** | §12.3, assumptions A-5 and A-7 | Settled by study |
| **G-13.v** | Vocabulary is a PM-owned, versioned configuration artefact | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.1; NFR-MNT-004 — **not NFR-MNT-001** | **Obtained — PM** |
| **G-13.w** | The seven-property minimum shape, **property 6 being a scope-keyed cardinality** | **PRODUCT DECISION — APPROVED 5 Sep 2026 · REVISION APPROVED 6 Sep 2026** | G-13.2; §9, §9.0.1 | **Obtained — PM (content) · Engineering (format)** |
| **G-13.x** | **Identity by mapping, never by label or value similarity** | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.3; AR-DET-008, BR-009, BR-004, AR-AST-007 | **Obtained — PM** |
| **G-13.y** | Stable, never-reused identifiers; labels do not carry identity | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.4; NFR-USE-005, AR-AST-008 | **Obtained — PM · Engineering** |
| **G-13.z** | Normalisation rules are vocabulary content; **the comparison function for FR-INF-004 operates within a scope instance**; a change to a normalisation **or scope** rule is a conflict-behaviour change requiring re-approval and re-evaluation | **PRODUCT DECISION — APPROVED 5 Sep 2026 · REVISION APPROVED 6 Sep 2026** | G-13.5; FR-INF-008, AR-DET-003/008, FR-INF-004/005/006, BR-004, EC-004, FR-AMB-001, G-03 | **Obtained — PM** |
| **G-13.aa** | Raw value retained alongside the normalised form | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.6; AR-DET-003 "reversible" | **Obtained — PM · Architecture** |
| **G-13.ab** | No coercion of an unmapped value; destination deferred to PM | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.7; BR-009, BR-016, EC-003, AR-AST-007 | **Obtained — PM · Privacy** |
| **G-13.ac** | Vocabulary authored before field sets; never engineering-invented or engine-derived | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.8; FR-INF-001/004, §6 Selection Principle | **Obtained — PM · Architecture** |
| **G-13.ad** | Tier slot mandatory on every attribute; **the bar on an untiered attribute applies at release, not at authoring**; closure split into **G-13-A** and **G-13-B**; rules still delegated to G-14/G-15 | **PRODUCT DECISION — APPROVED 5 Sep 2026 · NARROWING APPROVED 6 Sep 2026** | G-13.9; **FR-INF-007** (the gate-B requirement), FR-SENS-001, **FR-SENS-002 / BR-005** (disclosure of a tiered value). **FR-FILL-001 is not a basis** — its “classified routine” clause governs the detected form field under FR-FLD-003 | **Obtained — PM · Privacy** |
| **G-13.ae** | Vocabulary versioned; runs and stored values record the version | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.10; AR-AST-008, G-03 | **Obtained — Engineering · PM** |
| **G-13.af** | No placeholder vocabulary in code, configuration, schema, migrations, or fixtures until closure — **the trigger being G-13-A** | **PRODUCT DECISION — APPROVED 5 Sep 2026 · CLARIFICATION APPROVED 6 Sep 2026** | G-13.11; BR-009, §11 Containment Rule; FR-INF-007, FR-SENS-002 | **Obtained — PM · Engineering** |
| **G-13.ag** | Minimum justifiable vocabulary; each attribute justified by a requirement that consumes it | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.12; BR-017, NFR-PRIV-001 | **Obtained — PM · Privacy** |
| **G-13.ah** | Approval here does not amend `step3.pdf` | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.13; §11 Containment Rule | **Obtained — PM** |
| **G-13.ai** | Stage-1 evaluation (OCR quality, classification, failure behaviour, engine eligibility, normalisation determinism) is **not** blocked by G-13 | **PRODUCT DECISION — APPROVED 5 Sep 2026** | G-13.14; §14.2, D-02 §3.2/§18/§19 | **Obtained — PM** |
| **G-13.aj** | The scope-instance resolution rule is PM's, deterministic, and never derived from an extracted content value | **PRODUCT DECISION — APPROVED 6 Sep 2026** *(new)* — *the rule itself stays unresolved (T12)* | G-13.15; AR-DET-008, G-13.3, AR-AST-007 | **Obtained — PM · Architecture** |
| **G-13.ak** | The ten attributes drafted in G-12 §15 are a **DRAFT CANDIDATE SET**, not vocabulary content; challenges C-a…C-d stand | **DRAFT — NOT APPROVED** | §15.4; G-13.8, G-13.12, §18 X6/X18 | **Yes — PM, after C-a…C-d** |
| **G-13.al** | **T1 vocabulary contents authored as `v0.1-draft`** — one entry, `person.full_name`, with all seven properties; property 5 now **N-TEXT** and property 7 **TBD (G-14/G-15)** | **APPROVED as `v0.1-draft` — 7 Sep 2026 (PD-B, §21, D-05.11).** Properties 1–6 complete; property 7 TBD by design. **Not frozen, not releasable, not evaluation-ready** | §19.4; §12.2 "Name mismatches", FR-INF-004, FR-ACC-003, FR-INF-008 | **Obtained — PM (PD-B)** |
| **G-13.am** | **Nine candidates examined and NOT authored**, each with the admission test it failed recorded; none rejected, none approved | **NOT AUTHORED — CANDIDATES** | §19.5; G-13.12, §15.4 C-a…C-d, BR-009, BR-017 | **No — nothing to approve; each needs its blocker resolved first** |
| **G-13.an** | **N-TEXT** — the minimum semantic normalisation for a `text` attribute: **casing is not meaning; whitespace run length and edge whitespace are not meaning; nothing else is folded**; the raw value is retained and is what the user sees | **APPROVED — 7 Sep 2026 (PD-B, §21, D-05.11)** *(proposed in the T1 completion pass)* | §20.3; FR-INF-008, AR-DET-003, AR-DET-008, G-13.5, G-13.6, G-13.3, BR-004, BR-009, BR-016 | **Obtained — PM (PD-B)** |
| **G-13.ao** | **T3 partially resolved**: settled for casing and spacing; **dates and numeric precision remain TBD**, and every widening of N-TEXT is evaluation-dependent | **THE SETTLED PART (casing, spacing) APPROVED — 7 Sep 2026 (PD-B, §21).** Dates and numeric precision remain TBD; every widening evaluation-dependent (D-02 §11.6) | §20.3; §15.3 T3; D-02 §11.6 | **Obtained for the settled part — PM (PD-B)** |
| **G-13.ap** | **A per-subject reading of X17** — the scope-instance rule required before the first attribute of that subject enters a version — is **recorded and NOT taken** | **PROPOSED — NOT ADOPTED** | §20.5; G-13.15, T12, FR-ACC-003 | **Yes — PM (PD-D)** |

---

**Verification performed before completion**

| Check | Result |
| --- | --- |
| The file exists | **Yes** — `backend/docs/SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md` |
| Every claim about an existing requirement is traceable to `step3.pdf` | **Yes** — §2 and §3.3 carry requirement IDs; §3.2 reports full-text search counts |
| Any actual attribute presented as an existing requirement | **No.** §19's T1 pass authors `person.full_name` as **proposed content requiring PM approval**, grounded in §12.2 and labelled a product decision throughout. The specification itself still names no attribute (§19.3) |
| **T1 — entries authored** | **One:** `person.full_name`, as `v0.1-draft` **proposed content**. Nine candidates examined and **not** authored, each with the test it failed recorded (§19.5) |
| **T1 — properties per entry** | **Seven. No eighth property; scope appears only inside property 6** |
| **T1 — unsupported properties invented** | **No.** Property 5 reads **UNRESOLVED (T3)** and property 7 reads **TBD (G-14/G-15)** rather than being filled. Property 4 is labelled an **inference** from FR-INF-008's categories, not a stated requirement |
| **T1 — G-12 candidates approved** | **No.** One concept and identifier carried into an independently evidenced entry (§19.4.1); G-12's type, normalisation, multiplicity and applicability for it are **not** adopted. C-a…C-d remain open |
| **T1 — readiness claimed** | **None.** No entry is evaluation-ready or implementation-ready. `person.aadhaar_number` and `person.pan_number` are recorded **NOT EVALUATION-READY**, per C-c |
| **T1 — gate or gap moved** | **No.** **G-13-A NOT MET**, **G-13-B NOT MET**, **REQUIREMENTS GAP G-13 OPEN**. *At the T1 completion pass, X6 was advanced but unmet and X7 was the binding blocker.* **After PD-B (7 Sep 2026, §21): X7/X8/X10/X18 MET for `v0.1-draft`; the binding gate-A blockers are now X2/X4/X6 (PD-C, G-19), X17 (PD-D, G-13.15) and X11 (PD-E, G-29).** |
| **PD-B — recorded** | **Yes — APPROVED 7 September 2026** (§21; register D-05.11). Approves exactly three things: the entry `person.full_name` as `v0.1-draft`, its one-attribute scope, and N-TEXT |
| **PD-B — evidence** | **Read against `backend/step3.pdf`:** FR-INF-004 + P-06 (name is the worked conflict case), FR-INF-008 ("casing, spacing … without altering meaning"), the deterministic-and-reversible normalisation requirement + AR-DET-008, FR-ACC-003 (single-person record), BR-004/009/016, and approved G-13.3/G-13.5/G-13.6/G-13.12 |
| **PD-B — eighth property / tier assigned** | **No, and No.** Seven properties; property 7 stays **TBD by design** (G-14/G-15, gate B). No sensitivity tier assigned |
| **PD-B — G-13.15 / G-19 / G-29 resolved** | **No, No, No.** PD-D, PD-C and PD-E are not taken; the property list is not frozen |
| **PD-B — N-TEXT scope** | **Casing and spacing only.** Unicode/diacritics/transliteration/punctuation-folding/token-reordering/alias-matching/edit-distance/thresholds remain **undecided**; every widening is evaluation-dependent (D-02 §11.6) and re-approval-bound (G-13.5) |
| **PD-B — gap or specification touched** | **No.** **G-13 OPEN**; `backend/step3.pdf` unamended; no production code, schema, migration, dependency, corpus, or evaluation tooling touched |
| **T1 — G-13.15 / T12, G-14 / G-15, G-19 resolved** | **No, no, and no.** FR-ACC-003's single-person record is recorded as an observation about MVP scope and expressly **not** as a scope-instance resolution rule (§19.4.1) |
| Any actual field, or any passport / PAN / marksheet field, defined | **No** |
| G-12 resolved | **No** — §15.2 scopes it out; §13.2 lists what G-13 must not decide |
| G-13 silently resolved | **No** — §15.1 was approved explicitly by Product Management on 5 September 2026 and its revision explicitly on 6 September 2026; the vocabulary's contents remain T1 and exit criterion X6, not a decision |
| G-13 approval scope | **Shape only.** §15.1 approved 5 Sep 2026, its revision approved 6 Sep 2026 (D-05.6, D-05.8); **REQUIREMENTS GAP G-13 remains OPEN**; no attribute created; `step3.pdf` unamended (G-13.13) |
| **Approval recorded, 6 September 2026 — what it covers** | **Exactly five: G-13.2** (property 6 → scope-keyed cardinality), **G-13.5** (comparison within a scope instance), **G-13.9** (release-time narrowing, G-13-A / G-13-B split), **G-13.15** (new; the scope-instance *rule* stays unresolved), **G-13.11** (trigger clarification only, not a reopened decision) |
| **Approval recorded — what it does not do** | **Closes no gap** (G-13 OPEN), **meets no gate** (G-13-A NOT MET, G-13-B NOT MET), resolves neither **G-19** nor **G-14/G-15**, approves none of the ten G-12 candidates, and amends no line of `backend/step3.pdf` |
| **Exit criteria affected by the approval** | **X1 only — now MET.** X2, X3, X4, X6, X7, X8, X9, X10, X11, X12, X13, X14, X15, X16, X17, X18 are unchanged and unmet |
| **Revision — decisions reopened** | **Exactly three, each named: G-13.2** (property 6 only), **G-13.5** (comparison function), **G-13.9** (when the untiered bar applies). Each carried **REVISED — REQUIRES APPROVAL** and each was **APPROVED 6 September 2026 (D-05.8)**. **G-13.11 is clarified, not reopened** — its decision wording is unchanged and only its trigger is disambiguated |
| **Revision — G-13.3 preserved** | **Yes.** Not reopened, not reworded. Identity remains established by the field→attribute mapping alone; a scope key qualifies *which values are compared*, never *what is the same attribute* |
| **Revision — eighth property introduced** | **No.** The count is **seven** in §9.1, §13.1, G-13.2 and §18 X4. Property 6's *domain* widened; the "exactly these seven properties, and no others" clause is retained verbatim |
| **Revision — decisions left untouched** | **Ten:** G-13.1, G-13.3, G-13.4, G-13.6, G-13.7, G-13.8, G-13.10, G-13.12, G-13.13, G-13.14 — wording preserved exactly. **G-13.11** makes eleven whose *wording* is preserved; its **trigger** alone is clarified against the two-gate model, adding no prohibition and lifting none before G-13-A |
| **Revision — new decision added** | **One:** **G-13.15**, which *records* the scope-instance resolution question and **deliberately does not answer it** (five candidates listed, two excluded by approved decisions or by FR-INF-004, none selected) |
| **Revision — G-14 / G-15 resolved** | **No.** No tier assigned, no rule written, no default chosen. The revision changes only **when** the untiered bar bites. Register D-06.4's existing recommendation is cited **with its cost** and is **not adopted** |
| **Revision — sensitivity tier assigned to anything** | **No** |
| **Revision — scope-instance model chosen** | **No** — G-13.15 and §15.3 T12 leave it open |
| **Revision — G-12 candidate attributes** | **DRAFT CANDIDATE SET only** (§15.4). Not approved, not adopted, not repaired. Challenges **C-a, C-b, C-c, C-d** restated and left open; X18 makes discharging them a gate-A criterion |
| **Revision — vocabulary ownership** | **Unchanged.** G-13 owns the vocabulary and its contents (T1, X6, G-13.8, §13.2); G-12 owns the mapping of attributes to document types (§13.1's interface contract, §15.2) |
| **Revision — approved decision presented as a specification amendment** | **No.** G-13.13 restated in the header, §15 preamble and X16: neither the approval nor the revision amends `backend/step3.pdf`, and REQUIREMENTS GAP G-13 stays open |
| **Revision — D-02 modified** | **No.** §11.4.1's fourth false-conflict attribution category is **recorded for D-02's owner**, not applied |
| **Revision — G-12 document modified** | **No.** §15.4 refers to its candidate set; it does not edit it |
| **Revision — new G-number invented** | **No.** G-13.15 is a decision ID in this document's own series, not a gap ID; §15.4 and §11.4.1 assign none |
| Decision register updated | **Yes, on approval** — D-05.6 (approval), D-05.7 (unresolved dependencies), D-05.4/D-05.5 annotations, the D-05 row of the FINAL DECISION REGISTER, §1 item 2, the §4 G-13 gap row, and the closing next-step list. **G-13.g1 still awaits a numbered §4 entry from that document's owner** |
| `SPRINT_4_G12_FIELD_DEFINITIONS.md` modified | **No** — §16.2's corrections are recorded, not applied |
| G-02 approved governance respected | **Yes** — §14.2 and G-13.14 defer to it; nothing here alters it |
| V1–V7 accepted uncritically | **No** — two reassigned, two split, one citation corrected (§4.1) |
| `step3.pdf` modified | **No** |
| Production code, schema, migrations, dependencies touched | **No** |
| Documents collected or created / OCR installed or run | **0 / No** |
| Commit or push performed | **No** |
