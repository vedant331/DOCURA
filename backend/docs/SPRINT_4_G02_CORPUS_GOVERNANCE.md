# DOCURA — Sprint 4 G-02 Corpus Governance

| Field | Value |
| --- | --- |
| Gap | **G-02 — no requirement governs the collection, consent, retention, destruction, or team-readability of a real-document evaluation corpus** |
| Status | **APPROVED — 3 September 2026.** The fourteen decisions G-02.1 … G-02.14 are approved as product/privacy decisions for this project. Nothing here is an existing requirement unless explicitly cited as one, and the approval does **not** amend `backend/step3.pdf`. |
| Approval record | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) — D-02.5 (what is binding) and D-02.6 (what remains unresolved) |
| Retained label | Each decision keeps its **PROPOSED DECISION — REQUIRES APPROVAL** marker as the record of *what was put forward and approved*. Read those markers as **approved**; they are not still pending. |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0 |
| Related | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) — D-02.b/c/e/f, gaps G-02, G-14…G-16, G-21…G-24, G-26 |
| Related | [`SPRINT_4_D02_OCR_EVALUATION_PLAN.md`](SPRINT_4_D02_OCR_EVALUATION_PLAN.md) — §5, §16, and entry gates E1–E7 |
| Documents collected | **0** |
| Production code modified | **No** |

---

## 1. Purpose

### 1.1 What this document is for

**AR-AST-008** requires an evaluation corpus of *real, imperfect documents*. For DOCURA, "real documents" means real people's Aadhaar cards, PAN cards, marksheets, and address proofs. The specification requires their collection in one requirement and governs their handling in **none**.

This document proposes the **minimum safe governance policy** that would allow that corpus to be created. It resolves G-02 by proposal, not by fiat: every decision below is labelled and requires approval before it takes effect.

### 1.2 The three-way separation this document maintains

The task brief asks for a strict separation, and it is maintained throughout:

| Category | Marking | Meaning |
| --- | --- | --- |
| What the specification **requires** | **EXISTING REQUIREMENT** + requirement ID | Quoted from `backend/step3.pdf`. Binding today. |
| What the specification **leaves undefined** | **REQUIREMENTS GAP** + gap ID | An absence. Cannot be closed by engineering judgement. |
| What is **newly proposed here** | **PROPOSED DECISION — REQUIRES APPROVAL** | A new product/privacy decision. Not binding until approved. |

**No proposal in this document is presented as an existing requirement, and `backend/step3.pdf` is not amended.** Where a proposal would need to become a requirement to be enforceable, §15 says so.

### 1.3 What this document does not do

It does not collect documents, create example identity documents, use existing user uploads as evaluation data, copy documents from storage, install or run OCR, modify application code, create migrations, add dependencies, commit, or push. **This is governance documentation only.**

### 1.4 The design principle behind the proposals

Two defaults govern every recommendation, and both are argued from existing requirements rather than asserted:

1. **Explicit consent over inferred consent.** **BR-006** and **BR-007** make consent non-configurable and non-transferable in the product; **BR-008** and **BR-009** are stated as unchangeable. A product whose founding rule is *"Never automate consent"* cannot treat a user's decision to store a document as agreement to a second, unrelated purpose.

2. **Data minimization over convenience.** **NFR-PRIV-001** — "The system shall collect only information required to deliver a function the user has requested" — is the specification's own minimization rule. The corpus is the one place in the project where minimization and the requirement to collect real documents pull in opposite directions, so the tension must be resolved deliberately at every step rather than resolved once in favour of collection.

---

## 2. Existing Requirements

Everything in this section is **EXISTING REQUIREMENT**, quoted from `backend/step3.pdf`.

### 2.1 The requirement that creates the problem

> **AR-AST-008** (MVP): "Assisted components shall be evaluated against a held-out corpus of **real, imperfect** documents before any threshold is set."

Supporting text that makes the corpus unavoidable rather than optional:

- **§7.1**: "Final inclusion of each type is subject to the extraction evaluation in study S-6; a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only rather than shipped as unreliable."
- **BR-001**: "Threshold value: TBD — to be validated (study S-6)."
- **FR-OCR-012**: "MVP set: TBD — to be validated against a real document corpus (study S-6)."
- **ASM-001**: settled by "Study S-6 extraction evaluation on a real corpus."

### 2.2 Privacy requirements that bear on the corpus

| ID | Text | Bearing |
| --- | --- | --- |
| **NFR-PRIV-001** | "The system shall collect only information required to deliver a function the user has requested." | The minimization rule. A corpus is not a function a contributor requested. |
| **NFR-PRIV-002** | "A user's documents and extracted information **shall not be used to train shared models**, and shall not be readable by other users under any circumstance." | First half binds the corpus absolutely. Second half binds users to users; team reach is undefined. |
| **NFR-PRIV-003** | "Deletion requested by the user shall remove the document, its extracted information, and its derived copies within a stated period. **Period: TBD — to be validated against legal requirements.**" | Establishes that deletion reaches *derived copies* — the concept the corpus needs, applied to a subject it does not cover. |
| **NFR-PRIV-005** | "The system shall not sell, share, or disclose user information to third parties for their own purposes." | Constrains any external candidate engine (§7.4). |
| **NFR-PRIV-006** | "Any processing performed outside the user's device shall be disclosed in plain language before the user's first upload." | Governs disclosure if an externally hosted engine is evaluated. |
| **NFR-PRIV-007** | "Diagnostic and analytics data shall exclude document contents and extracted personal values." | Governs harness logs and the evaluation report (§8.4, §13). |

### 2.3 Deletion and account requirements — the decisive ones for G-02.3

| ID | Text | Bearing |
| --- | --- | --- |
| **FR-ACC-007** (MUST) | "The user shall be able to **delete their account and all associated data**, after an explicit confirmation that states what will be destroyed." | "All associated data" admits no carve-out. A corpus copy of a user's document that survived account deletion would breach this. |
| **FR-DOC-007** (MUST) | "The user shall be able to delete a document, with a confirmation that **names the information that will be lost with it**." | A confirmation cannot name what will be lost if a copy persists elsewhere under a different lifecycle. |
| **FR-DOC-008** (SHOULD) | "Deleted documents shall be recoverable for a defined grace period before permanent destruction. Period: TBD — to be validated." | Establishes a deletion lifecycle for product documents; none exists for corpus documents. |
| **FR-ACC-006** (SHOULD) | "The user shall be able to export their complete record — documents and extracted information — in an openable format." | An export that omits a corpus copy would misrepresent what is held. |

**This cluster is the strongest requirements-grounded constraint in the whole of G-02**, and §4.3 turns it into a decision.

### 2.4 Security requirements that bear on corpus handling

| ID | Text | Bearing |
| --- | --- | --- |
| **NFR-SEC-001** | "All data in transit shall be encrypted using current industry-standard transport security." | Any transfer of corpus documents. |
| **NFR-SEC-002** | "Documents and extracted information shall be encrypted at rest." | Applies to the product's storage; meaning undefined (G-21…G-24). |
| **NFR-SEC-003** | "Every request for a document or attribute shall be authorised against the requesting user's identity; **ownership shall never be inferred from an identifier supplied by the client**." | Written for a model where every document has an owning user. Corpus documents have contributors, not owning users (§6.1). |
| **NFR-SEC-007** | "Document access links shall be time-limited and single-purpose; a link shall not grant standing access." | A directly transferable principle for corpus access (§6.4). |
| **NFR-SEC-008** | "The system shall not claim to be unbreachable in any user-facing or internal material. Security statements shall describe specific measures and their limits." | Governs how this document describes its own controls (§14.7). |
| **NFR-SEC-009** (SHOULD) | "The product shall undergo independent security review before any release to users outside the team." | Whether corpus handling is in scope is a decision (§15). |

### 2.5 Observability and audit requirements

| ID | Text | Bearing |
| --- | --- | --- |
| **NFR-OBS-004** | "Failures in detection, extraction, or matching shall be recorded with enough context to diagnose them, **and without personal values**." | The value-free logging rule the corpus harness must follow. |
| **FR-AUD-005** | "History entries shall not be editable by the user; corrections are recorded as new entries." | An append-only principle, transferable to the corpus register (§6.5). |
| **FR-AUD-006** | "History shall record DOCURA's own actions and the fields they affected. It shall not store the full contents of the third-party form." | Precedent for "record the action, not the content" — the pattern §13 applies to evaluation evidence. |

### 2.6 Business rules that shape the consent model

| ID | Rule |
| --- | --- |
| **BR-005** | "Sensitive information is never disclosed to a form without explicit approval for that specific disclosure." |
| **BR-006** | "DOCURA never accepts a legal declaration, agreement, or consent control." *(stated as non-configurable)* |
| **BR-007** | Approval for one field/form/session does not carry to another — as reflected in **FR-SENS-005**: "Approval granted for one field in one form shall not carry to any other field, form, or session." |
| **BR-016** | As summarised in §14: "fail towards inaction and tell the user." |

**BR-007's principle — an approval does not generalise beyond what it was given for — is the single most transferable rule in the specification for consent design**, and §5 builds on it.

### 2.7 Sensitivity classification — exists as a requirement, not as rules

> **FR-INF-007** (MUST): "Every attribute shall carry a sensitivity classification of routine, sensitive, or consequential."
> **FR-SENS-001** (MUST): "The system shall maintain the three-tier sensitivity classification for both stored attributes and detected form fields."

Both trace to "§02 Table 13.1". Per **G-14**, that table is an **ASM**-tagged *"WORKING SENSITIVITY CLASSIFICATION"* giving examples rather than rules, explicitly qualified as *"This boundary must be set by users, not by us — it is assumption A-5"*, and §12.3 confirms A-5 is untested.

**Consequence for G-02: corpus protection cannot be derived from the sensitivity model, because the model does not exist in settled form.** See §8.2.

---

## 3. Requirements Gap

### 3.1 The gap, stated precisely

**REQUIREMENTS GAP — G-02:** *No requirement governs the collection, consent, retention, destruction, or team-readability of a real-document evaluation corpus.*

Every privacy requirement in `backend/step3.pdf` concerns a **user's** documents held for the **user's** benefit. A corpus of real documents held for the **team's** benefit is a different activity with a different beneficiary, and the requirement set does not reach it.

### 3.2 What is undefined

| # | Undefined | Nearest requirement, and why it does not reach |
| --- | --- | --- |
| 1 | Who may contribute documents | None. FR-ACC governs account holders, not contributors. |
| 2 | What consent is required for evaluation use | None. BR-005/BR-007 govern disclosure *to forms*, not collection for evaluation. |
| 3 | Whether user uploads may enter the corpus | None directly — but FR-ACC-007 and NFR-PRIV-002 constrain it heavily (§4.3). |
| 4 | Who on the team may read corpus documents | NFR-PRIV-002 binds *users* to *users*. Team reach undefined — **G-02** / D-02.c. |
| 5 | Where corpus documents may be stored | NFR-SEC-002 requires encryption at rest but does not define it — **G-21**. |
| 6 | Whether the corpus is isolated from production storage | None. |
| 7 | What must be redacted | None. And field definitions do not exist — **G-12** — so "what is needed" is unknowable today. |
| 8 | How long the corpus is retained | NFR-PRIV-003 covers user documents, and its own period is **TBD**. |
| 9 | How corpus documents are destroyed | None. Method, verification, and evidence all absent — D-02.f. |
| 10 | What happens on withdrawal of consent | None. |
| 11 | Who controls the held-out portion | AR-AST-008 requires "held-out"; the mechanism is undefined — D-02.g. |
| 12 | How held-out leakage is prevented and evidenced | None. |
| 13 | What evidence may outlive the corpus | None. AR-AST-008 names no artefact — D-02.o. |
| 14 | Whether synthetic documents may supplement | AR-AST-008 requires *real*; supplementation is unaddressed. |

### 3.3 Gaps inherited from elsewhere that block a *final* decision here

Per the brief's instruction to identify rather than invent such dependencies:

| Gap | Content | What it blocks in this document |
| --- | --- | --- |
| **G-21** | "Encrypted at rest" has no threat model | §7.3 cannot state the encryption standard by inheritance |
| **G-22** | **Key management is entirely absent** from the specification | §7.3, §9.4 — no key policy can be inherited; crypto-erasure cannot be specified |
| **G-23** | The encryption boundary — backups, replicas, logs, temporary artefacts, external processor custody — is undefined | §7.5, §9.3 — an evaluation run creates all of these |
| **G-24** | Whether crypto-erasure satisfies deletion is unaddressed; period TBD | §9.4 destruction method |
| **G-26** | No requirement obliges recording security-relevant events | §6.5 — corpus access logging is *proposed*, not inherited |
| **G-14/15/16** | Sensitivity rules absent; no default tier; document-level sensitivity undefined | §8.2 — protection level cannot be graduated by sensitivity |
| **G-12** | **No field definitions exist for any document type** | §8.3 — what is "needed" for evaluation is not yet determinable, so redaction scope cannot be finalised |
| **G-03** | No re-evaluation trigger when a component version changes | §9.2 — retention duration depends on whether re-evaluation reuses the corpus |

---

## 4. Proposed Governance Decisions

This section states each decision in summary. Sections 5–13 give the reasoning and the operative detail.

### 4.1 G-02.1 — Who may contribute documents?

**PROPOSED DECISION — REQUIRES APPROVAL**

Contribution is permitted only from an **adult contributing their own documents**, through a **dedicated contribution process that is not part of the product's signup or upload flow**, under the explicit consent of §5.

| Permitted | Not permitted |
| --- | --- |
| An adult contributing documents that are their own | A person contributing another person's documents |
| A team member, family member, or volunteer, on the same consent terms as any other contributor — with the representativeness limitation of §12.4 stated in the report | Anyone under the age of majority — see below |
| A paid panel participant, if approved as an acquisition method | Contribution as a condition of using DOCURA, or bundled into signup |

**Minors — APPROVED, and specifically flagged.** DOCURA's target user is a student applying to institutions, and §7.1's type set includes 10th and 12th marksheets — documents whose holders are frequently below the age of majority. **Minors are excluded from contribution at MVP**, because valid consent from a minor requires a guardian-consent framework that no requirement in `backend/step3.pdf` establishes, and inventing one here would be exactly the overreach §1.2 forbids. This narrows the corpus, and **that narrowing is a stated limitation of the evaluation** — it must appear in every evaluation report under §12.4, not only here. **The MVP minors limitation remains in force** until a guardian-consent framework is separately specified and approved.

**Reasoning from existing requirements.** **NFR-PRIV-001**'s minimization rule means contribution must be a distinct, purposeful act rather than a side effect of using the product. **BR-007**'s principle — that an approval does not carry beyond what it was given for — means using the product cannot imply agreement to contribute.

### 4.2 G-02.2 — What consent is required?

**PROPOSED DECISION — REQUIRES APPROVAL**

A document may enter the corpus only under **explicit, informed, purpose-bound, recorded, withdrawable consent** obtained *before* collection, containing the eight elements of §5.3. Consent may not be bundled with the product's terms of service, may not be a checkbox default, and does not generalise to purposes it did not name.

**Reasoning.** **NFR-PRIV-006** sets the specification's own standard for what a disclosure to a user must be — "in plain language" and "before the user's first upload". **BR-007** and **FR-SENS-005** establish that an approval is bound to the specific thing it was given for. **NFR-PRIV-002**'s training prohibition must appear in the consent because it is an existing binding requirement the contributor is entitled to rely on.

### 4.3 G-02.3 — Can production/user-uploaded documents automatically enter the corpus?

**PROPOSED DECISION — REQUIRES APPROVAL: NO. NEVER AUTOMATICALLY. UNDER ANY CONFIGURATION.**

This is the strongest recommendation in this document, and unlike most of the others it is **almost entirely derivable from existing requirements** rather than from preference:

| # | Existing requirement | Why automatic ingestion breaches or undermines it |
| --- | --- | --- |
| 1 | **FR-ACC-007** (MUST) — "delete their account **and all associated data**" | A corpus copy taken from a user's upload is associated data. If it survives account deletion, FR-ACC-007 is breached. If it does not survive, the corpus is silently destroyed by ordinary user behaviour and cannot support reproducibility (§13). **There is no configuration in which both hold.** |
| 2 | **FR-DOC-007** (MUST) — deletion "with a confirmation that **names the information that will be lost**" | The confirmation cannot honestly name what is lost if a copy persists under a separate lifecycle the user was never told about. |
| 3 | **NFR-PRIV-001** (MUST) — collect only what is "required to deliver a function the user has requested" | The user requested storage and form-filling. They did not request that their identity documents become evaluation material for the team. |
| 4 | **NFR-PRIV-002** (MUST) — "shall not be readable by other users under any circumstance" | Team readability of a user's documents is at best undefined (G-02) and at worst a breach. Automatic ingestion resolves that ambiguity in the least safe direction, by default, invisibly. |
| 5 | **FR-ACC-006** (SHOULD) — export of "their complete record" | An export that omits a corpus copy misrepresents what is held about the user. |
| 6 | **BR-006/BR-007** (non-configurable) — the consent principle | Automatic ingestion is assumed consent. §12.2 of the specification rejects even *cross-session learning* on precisely this ground: "remembering an answer is a form of assumed consent." Ingesting the document itself is a larger step of the same kind. |

**The narrow permitted path — PROPOSED DECISION — REQUIRES APPROVAL.** A user's document may enter the corpus **only** when all of the following hold:

1. the user performs a **separate affirmative act**, distinct in time and interface from upload, that does nothing else;
2. the act is **not** a precondition for any product function, and refusing it changes nothing about their experience;
3. the full §5.3 consent is presented and recorded at that moment;
4. the resulting corpus item is a **governed copy under this policy**, with its own lifecycle — and the user is told, in plain language, that it will be retained and destroyed on the corpus's schedule rather than their vault's;
5. withdrawal (§10) and account deletion (**FR-ACC-007**) both reach that copy.

**Point 4 is the honest core of it.** Once the copy exists, it cannot both serve reproducibility and vanish on the user's ordinary deletion. The only defensible resolution is to tell the contributor that plainly at the moment of consent — which is what §5.3(g) requires — rather than to resolve it silently either way afterwards.

**PROPOSED DECISION — REQUIRES APPROVAL:** until this path is approved and built, **no production document enters the corpus by any mechanism**, and the evaluation corpus is sourced entirely through the §5 contribution process.

### 4.4 G-02.4 — Who may access corpus documents?

**PROPOSED DECISION — REQUIRES APPROVAL.** Access is by **named individual against a named role**, on least privilege, time-bound, logged, and revoked when the role ends. Four roles, with the held-out separation of §11 enforced through them. Detail in §6.

### 4.5 G-02.5 — Where may corpus documents be stored?

**PROPOSED DECISION — REQUIRES APPROVAL.** In a **single designated corpus store inside DOCURA's own trust boundary**, encrypted at rest and in transit, with an enumerated location list. No personal devices, no general-purpose cloud drives, no messaging or chat tools, no ticketing systems. Detail in §7. **Blocked from final form by G-21 and G-22.**

### 4.6 G-02.6 — Must the corpus be isolated from production storage?

**PROPOSED DECISION — REQUIRES APPROVAL: YES. MANDATORY.** Detail and reasoning in §7.2.

### 4.7 G-02.7 — What should be redacted?

**PROPOSED DECISION — REQUIRES APPROVAL.** **Do not redact the document images**, because doing so would invalidate the evaluation AR-AST-008 requires. Minimize everywhere else instead — contributor identity, derived artefacts, logs, and reports. Detail in §8. **Final redaction scope is blocked by G-12.**

### 4.8 G-02.8 — How should retention work?

**PROPOSED DECISION — REQUIRES APPROVAL.** A defined seven-stage lifecycle with **trigger-based** transitions. **Duration: TBD — requires product/privacy and legal approval.** No duration is invented. Detail in §9.

### 4.9 G-02.9 — How must corpus documents be destroyed?

**PROPOSED DECISION — REQUIRES APPROVAL.** Enumerated copies, a defined method, verification, and a retained destruction record. Detail in §9.3–§9.5. **Method is blocked by G-22, G-23, G-24.**

### 4.10 G-02.10 — What happens on withdrawal?

**PROPOSED DECISION — REQUIRES APPROVAL.** Honoured without justification; documents and derived artefacts destroyed; the corpus is re-versioned; **affected prior results are marked no longer fully reproducible rather than silently re-versioned**; aggregate evidence may be retained because it contains no personal values. Detail in §10.

### 4.11 G-02.11 — Who controls the held-out portion?

**PROPOSED DECISION — REQUIRES APPROVAL.** A named **Held-Out Custodian**, who must not be a person who configures, tunes, or selects extraction. Detail in §11.

### 4.12 G-02.12 — How is tuning against the held-out set prevented?

**PROPOSED DECISION — REQUIRES APPROVAL.** Six controls combining separation, sealing, single-run discipline, pre-fixed criteria, logging, and disclosure. Detail in §11.3.

### 4.13 G-02.13 — What evidence may outlive the corpus?

**PROPOSED DECISION — REQUIRES APPROVAL.** Aggregates, counts, distributions, provenance, and manifests — **never document content, extracted values, or ground-truth values**. Detail in §13.

### 4.14 G-02.14 — May synthetic documents supplement the corpus?

**PROPOSED DECISION — REQUIRES APPROVAL.** Yes for harness development and the development set; **never as a substitute for the real held-out evaluation**, which **AR-AST-008 requires to be real**. Detail in §12.

---

## 5. Consent

### 5.1 What is binding today

**EXISTING REQUIREMENT — NFR-PRIV-002:** "A user's documents and extracted information **shall not be used to train shared models**." This half of NFR-PRIV-002 is unambiguous and binds the corpus absolutely, whatever else is decided. It is not a proposal and cannot be consented away.

**EXISTING REQUIREMENT — NFR-PRIV-006** establishes the standard for disclosure: "in plain language", "before the user's first upload". The plain-language standard is transferable; the trigger point is not, because contribution is not an upload.

Everything else in §5 is proposed.

### 5.2 Why explicit consent, argued from the specification

The specification's product principle is stated in §5 of `step3.pdf` as *"Automate certainty. Ask about ambiguity. Never automate consent."* — encoded in BR-001 to BR-009 and declared non-configurable.

Three consequences for corpus consent:

1. **BR-007 / FR-SENS-005**: an approval "shall not carry to any other field, form, or session." Consent is scoped to what it named. A consent to store cannot become a consent to evaluate.
2. **§12.2** rejects cross-session learning as WON'T because "remembering an answer is a form of assumed consent" — and notes it "requires the sensitivity boundary from A-5 first." If remembering an *answer* needs that, retaining a *document* for a second purpose needs at least as much.
3. **BR-016**: "fail towards inaction and tell the user." Where consent scope is unclear, the specification's own disposition is to do nothing and say so.

### 5.3 Required consent elements

**PROPOSED DECISION — REQUIRES APPROVAL.** A document may enter the corpus only under a recorded consent containing all eight elements:

| # | Element | Content | Basis |
| --- | --- | --- | --- |
| **a** | **Purpose** | That the documents will be used to evaluate how accurately software reads documents, in plain language | NFR-PRIV-006's standard |
| **b** | **Scope of use** | Which evaluations are covered — this one only, or future re-evaluations. **DECISION REQUIRED**, driven by G-03 | BR-007's non-generalisation principle |
| **c** | **Recipients** | Every party that will receive the documents, including any external candidate engine, by name | NFR-PRIV-005, NFR-PRIV-006 |
| **d** | **Access** | Which roles inside the team may read the documents (§6.2) | Least privilege; D-02.c |
| **e** | **Training prohibition** | An explicit statement that documents will not be used to train models | **EXISTING REQUIREMENT — NFR-PRIV-002** |
| **f** | **Retention** | How long documents are kept, on what trigger, and how they are destroyed. **Duration TBD** (§9.2) | NFR-PRIV-003's structure, applied to a subject it does not cover |
| **g** | **Lifecycle distinctness** | That a corpus copy has its own retention and destruction schedule, distinct from any DOCURA vault copy | §4.3, point 4 — the honesty requirement |
| **h** | **Withdrawal** | How to withdraw, what is destroyed, what aggregate evidence is retained, and the effect on recorded results | §10 |

### 5.4 Consent form and timing

**PROPOSED DECISION — REQUIRES APPROVAL**

| Rule | Reason |
| --- | --- |
| Consent is obtained **before** collection, never retrospectively | A document already collected cannot be un-seen; retrospective consent is a formality over an accomplished act |
| Consent is a **separate document**, not a clause in terms of service | Bundling defeats the informed element |
| Consent is **opt-in by affirmative act** — no pre-ticked boxes, no default-on | BR-006's principle: consent is never automated |
| Consent is **recorded** with contributor identity, date, version of the consent text, and the document set it covers | Required to honour §10 withdrawal and to prove scope |
| A **new purpose requires new consent** | BR-007's non-generalisation |
| Refusal costs the contributor nothing | Otherwise the consent is coerced, and NFR-PRIV-001's minimization is nominal |

### 5.5 Scope boundary that consent cannot cross

**PROPOSED DECISION — REQUIRES APPROVAL.** No consent may authorise:

- use of the documents to train, fine-tune, or adapt any model — **NFR-PRIV-002 forbids it, and it is not the contributor's to waive on the product's behalf**;
- disclosure to a third party for that party's own purposes — **NFR-PRIV-005**;
- transfer of the documents into production user storage — §7.2;
- retention beyond the approved destruction trigger — §9.

### 5.6 Consent records are themselves personal data

**PROPOSED DECISION — REQUIRES APPROVAL.** Consent records contain contributor identity and must be:

- stored **separately** from the documents, linked only by the pseudonymous corpus identifier of §8.5;
- accessible only to the Corpus Custodian role (§6.2);
- retained after document destruction **only** for as long as needed to evidence that consent existed and was honoured — **duration TBD, legal input required** (§15).

This separation is what allows the documents to carry no contributor name while withdrawal (§10) remains actionable.

---

## 6. Corpus Access

### 6.1 Why NFR-SEC-003 does not answer this

**EXISTING REQUIREMENT — NFR-SEC-003:** "Every request for a document or attribute shall be authorised against the requesting user's identity; ownership shall never be inferred from an identifier supplied by the client."

NFR-SEC-003 assumes every document has an **owning user** whose identity authorises access. Corpus documents have a **contributor**, who is not the accessor and never accesses them. The requirement's *principle* — authorise every access against the accessor's identity, never infer authority from a supplied identifier — transfers cleanly. Its *mechanism* does not.

**PROPOSED DECISION — REQUIRES APPROVAL:** corpus access is authorised against the accessor's identity and role, never against a supplied corpus or document identifier. Knowing a corpus document's identifier confers no access.

### 6.2 Roles — least privilege

**PROPOSED DECISION — REQUIRES APPROVAL.** Four roles. A person may hold more than one **except** where §11.2 forbids the combination.

| Role | May access | May not access | Purpose |
| --- | --- | --- | --- |
| **Corpus Custodian** | Consent records; corpus manifest; all documents | — | Collection, lifecycle, destruction, withdrawal |
| **Annotator** | Documents assigned for annotation; ground truth they author | Consent records; contributor identity | Produces ground truth (D-02 §7) |
| **Evaluator** | Development set; evaluation outputs; aggregate results | Consent records; contributor identity; **held-out set** unless also Held-Out Custodian | Runs and analyses evaluations |
| **Held-Out Custodian** | The held-out split and its results | — | Controls the held-out set (§11) |

**Nobody has standing access to everything by default, including the project lead.** Access is granted to a role, and to a named person for a period.

### 6.3 Access rules

**PROPOSED DECISION — REQUIRES APPROVAL**

| Rule | Basis |
| --- | --- |
| Access is granted to **named individuals**, not to a team, group, or shared account | Least privilege; auditability |
| Access is **time-bound** and expires; renewal is an explicit act | **NFR-SEC-007**'s principle: "a link shall not grant standing access" |
| Access is **purpose-bound** — annotation access does not confer evaluation access | **NFR-SEC-007**: "single-purpose" |
| Access is **revoked** when the role ends, without waiting for expiry | Least privilege |
| Access is **logged** (§6.5) | Proposed — **G-26** means no requirement obliges it |
| **No bulk export.** Documents are viewed in place through the corpus store | Every export is an uncontrolled copy outside the boundary (**G-23**) |
| **No copies to personal devices or personal accounts**, under any circumstance | §7.4 |
| Contributor identity is not exposed to Annotator or Evaluator roles | Data minimization, **NFR-PRIV-001**'s principle |

### 6.4 Time-limited, single-purpose access — a directly transferable requirement

**EXISTING REQUIREMENT — NFR-SEC-007:** "Document access links shall be time-limited and single-purpose; a link shall not grant standing access."

NFR-SEC-007 is written for the product's document access, and its property is exactly what corpus access needs. **PROPOSED DECISION — REQUIRES APPROVAL:** corpus document access follows the same rule — time-limited, single-purpose, no standing access — so that the corpus is not held to a *weaker* standard than the vault it exists to make safe.

### 6.5 Access logging and auditability

**REQUIREMENTS GAP — G-26:** *"No requirement obliges the recording of security-relevant events (authentication, authorisation failure, vault access)."* The register describes this absence as "serious for a product handling identity documents."

**PROPOSED DECISION — REQUIRES APPROVAL.** Every corpus access is recorded: who, when, which documents, under which role and purpose. The log is:

- **append-only** — following **FR-AUD-005**'s principle, "History entries shall not be editable... corrections are recorded as new entries";
- **value-free** — it records that a document was accessed, never its content, per **NFR-OBS-004** and **NFR-PRIV-007**;
- **retained after document destruction** as evidence that the policy was followed (§13.3);
- **reviewed** — held-out access in particular is reviewed by the Held-Out Custodian (§11.3).

Because this control is proposed rather than inherited, §15 flags that it should become a requirement if approved.

---

## 7. Storage and Isolation

### 7.1 G-02.5 — permitted storage locations

**PROPOSED DECISION — REQUIRES APPROVAL.** Corpus documents exist in exactly **one designated corpus store**, inside DOCURA's own trust boundary, and nowhere else.

| Permitted | Forbidden |
| --- | --- |
| The designated corpus store | Production document storage (§7.2) |
| A designated annotation working area **inside** the same boundary, subject to §7.5 | Personal devices, personal cloud accounts, personal email |
| — | General-purpose cloud drives and file-sharing services |
| — | Messaging, chat, or ticketing systems — including screenshots pasted into them |
| — | Developer laptops as ad-hoc working copies |
| — | Any external service not named in the §5.3(c) consent |

**Reasoning.** **D-01** established that documents are processed inside DOCURA's own trust boundary, with no third-party service contacted, and that the boundary is enforced by test rather than merely stated. The corpus is the most concentrated identity-document holding the project will have; holding it to a weaker standard than the pipeline it exists to evaluate would be incoherent.

### 7.2 G-02.6 — isolation from production storage: mandatory

**PROPOSED DECISION — REQUIRES APPROVAL: the corpus store is physically and logically separate from production document storage.** Not a folder, not a flag, not a tenant — a separate store.

| # | Reason | Existing requirement |
| --- | --- | --- |
| 1 | Corpus documents have **no owning user**, so NFR-SEC-003's per-user authorisation model has no subject for them. Placing them in a store whose entire access model is per-user creates objects the model cannot express. | **NFR-SEC-003** |
| 2 | Product documents are governed by user-triggered deletion (**FR-DOC-007/008**) and account deletion (**FR-ACC-007**). Corpus documents are governed by §9's lifecycle. **Two incompatible lifecycles in one store will be reconciled wrongly**, in one direction or the other. | **FR-ACC-007**, **FR-DOC-007/008** |
| 3 | A corpus document appearing in a user's vault — through a query defect, a restore, or an export — would breach NFR-PRIV-002 unambiguously. Isolation makes that failure mode structurally impossible rather than merely unlikely. | **NFR-PRIV-002** |
| 4 | **FR-ACC-006** requires a user's export to be their "complete record". A store containing non-user documents complicates the correctness of every such export. | **FR-ACC-006** |
| 5 | The evaluation harness is not production code (D-02 §14.5). It must never hold write access to production storage. | D-01 / D-02 boundary |

**PROPOSED DECISION — REQUIRES APPROVAL:** the evaluation harness has **no** production storage credentials, in any environment. Not read, not write.

### 7.3 Encryption — required, but not specifiable by inheritance

**EXISTING REQUIREMENTS:**
- **NFR-SEC-001** — "All data in transit shall be encrypted using current industry-standard transport security."
- **NFR-SEC-002** — "Documents and extracted information shall be encrypted at rest."

**PROPOSED DECISION — REQUIRES APPROVAL:** the corpus store applies encryption at rest and in transit at least equal to production.

**BLOCKED — dependency, not invention.** Per the brief's instruction to identify rather than invent:

| Gap | Effect |
| --- | --- |
| **G-21** | "Encrypted at rest" has no threat model. Full-disk, storage-service-managed, application-level envelope, and column-level encryption all satisfy the words differently. **The corpus's encryption standard cannot be specified by citing NFR-SEC-002.** |
| **G-22** | **Key management is entirely absent** from the specification — no generation, storage, separation from data, rotation, escrow, or destruction. **No key policy can be inherited, and none is invented here.** |

**Consequence:** §7.3 cannot reach final form until G-21 and G-22 are closed by security ownership. This is a **hard dependency on E6** (D-02 §19.2), not a detail to settle during collection.

### 7.4 External processing

**EXISTING REQUIREMENTS — NFR-PRIV-005**, **NFR-PRIV-006**.

**PROPOSED DECISION — REQUIRES APPROVAL.** Corpus documents may leave the boundary **only** when all hold:

1. the recipient is named in the §5.3(c) consent obtained **before** collection;
2. the recipient's terms exclude training on submitted content — **NFR-PRIV-002**;
3. the recipient's retention is established and reconciled with §9 — noting **G-23** leaves external processor custody undefined;
4. transport encryption per **NFR-SEC-001**;
5. the transfer is recorded in the access log (§6.5).

**PROPOSED DECISION — REQUIRES APPROVAL:** if an external candidate engine would require a consent scope contributors were not offered, **it is not evaluated on the real corpus.** Evaluating it "just to see" would be precisely the disclosure the consent did not cover, and it cannot be undone.

### 7.5 Derived artefacts inherit the boundary

**REQUIREMENTS GAP — G-23:** the encryption boundary — backups, replicas, logs, temporary artefacts, external processor custody — is undefined. **An evaluation run creates all of these as a matter of course.**

**PROPOSED DECISION — REQUIRES APPROVAL.** Every artefact below is inside the corpus boundary, inherits its controls, and is enumerated for destruction (§9.3):

| Artefact | Contains | Treatment |
| --- | --- | --- |
| Extraction output — text, fields, regions | Personal values | Corpus-level protection; destroyed with the corpus |
| **Ground truth annotations** | Personal values, **labelled and indexed** — arguably the most exposed artefact in the project | Corpus-level protection; destroyed with the corpus |
| Annotation working copies | Personal values | Enumerated and destroyed; **G-23** does not cover them |
| Harness logs | **Must contain no values** — NFR-PRIV-007, NFR-OBS-004 | Value-free by construction (§8.4) |
| Temporary processing artefacts | Personal values | Destroyed at end of run, not at end of retention |
| Evaluation report | Aggregates only (§13) | May outlive the corpus |
| Access log | No values (§6.5) | Retained as evidence |
| Consent records | Contributor identity | Stored separately (§5.6) |

---

## 8. Redaction and Data Minimization

### 8.1 The central tension, stated honestly

**The instinct to redact identity documents is right, and applying it to the corpus images would break the requirement the corpus exists to satisfy.**

**EXISTING REQUIREMENT — AR-AST-008** requires *real, imperfect* documents. Redacting a document image:

- alters the page — which is the artefact whose imperfection is under evaluation;
- removes or obscures the very values whose extraction accuracy is being measured;
- introduces a modification that is not one of the real-world degradations of D-02 §4.4, so results would describe a document population that does not exist;
- would, if the redaction covers identifiers, make it impossible to measure extraction on exactly the field types §7.1's document set is composed of.

A corpus of redacted documents is a **synthetic corpus wearing a real document's layout**, and §12 explains why that cannot discharge AR-AST-008.

### 8.2 Why the sensitivity model cannot govern this either

**REQUIREMENTS GAP — G-14, G-15, G-16.** The natural approach — redact by sensitivity tier — is unavailable. The classification rules are not in `step3.pdf`; §02 Table 13.1 is ASM-tagged, gives examples rather than rules, and is tied to untested assumption **A-5**, whose own text says the boundary "must be set by users, not by us". **G-15** adds that no default tier exists; **G-16** that document-level sensitivity — which is what a corpus actually holds — is undefined entirely.

**PROPOSED DECISION — REQUIRES APPROVAL:** because protection cannot be graduated by sensitivity, **the entire corpus is treated at the highest protection level the team can apply**, on the ground that it contains identity documents. This is a conservative default chosen *because* the specification offers no basis for a graduated one — not a claim that graduation is unnecessary. It is revisited when A-5 reports.

### 8.3 G-02.7 — what is and is not redacted

**PROPOSED DECISION — REQUIRES APPROVAL**

| Layer | Rule | Reason |
| --- | --- | --- |
| **Document image / file** | **No redaction.** Retained exactly as contributed | AR-AST-008 requires real, imperfect documents (§8.1) |
| **Contributor identity** | **Separated.** Documents carry a pseudonymous corpus ID only (§8.5) | NFR-PRIV-001's minimization applied where it costs nothing |
| **Corpus manifest** | Structural properties only — type, page count, degradation conditions, person group, split. **No values** | Minimization |
| **Harness logs** | **No document content, no extracted values, no ground-truth values** | **EXISTING REQUIREMENT — NFR-PRIV-007, NFR-OBS-004** |
| **Failure records** | Failure class and structural context — page, region, condition. **Never the value** | **NFR-OBS-004**: "with enough context to diagnose them, and without personal values" |
| **Evaluation report** | Aggregates and counts only (§13) | **NFR-PRIV-007** |
| **Screenshots, tickets, chat, email** | **Corpus content never appears in any of them** | §7.1 |

**The principle: minimize everywhere the evaluation does not need fidelity, and nowhere it does.** The document image is the one place fidelity is the requirement.

### 8.4 Value-free diagnostics — an existing requirement, not a proposal

**EXISTING REQUIREMENT — NFR-PRIV-007:** "Diagnostic and analytics data shall exclude document contents and extracted personal values."
**EXISTING REQUIREMENT — NFR-OBS-004:** failures recorded "with enough context to diagnose them, **and without personal values**."

**FR-AUD-006** provides the pattern: record "DOCURA's own actions and the fields they affected", not "the full contents". Applied here: **record what happened, never what it said.**

Diagnosis remains possible because the corpus document is available in place, to an authorised role, under §6 — so the recorded log does not need to carry the value in order for a failure to be investigated.

### 8.5 Pseudonymous identification

**PROPOSED DECISION — REQUIRES APPROVAL.**

- Each contributor receives a **pseudonymous corpus identifier**. Each document receives a pseudonymous document identifier.
- The mapping between corpus identifier and contributor identity lives **only** in the consent record store (§5.6), accessible only to the Corpus Custodian.
- Annotators and Evaluators work entirely against pseudonymous identifiers.
- The person-grouping D-02 §4.6 requires for conflict detection is expressed through the **corpus identifier**, so **FR-INF-004** evaluation is fully supported without exposing identity.

This is the one place where minimization and evaluation fidelity do not conflict at all, and it should be taken.

### 8.6 What cannot be decided yet

**REQUIREMENTS GAP — G-12:** no field definitions exist for any document type.

A question this section would otherwise answer — *are there values in these documents that the product will never extract, and that could therefore be excluded from derived artefacts?* — **cannot be answered today**, because there is no defined field set that says what is extracted.

The register's D-05.3 raises the concrete instance: for Aadhaar, "whether the identifier number is stored at all, masked, or stored in part" is unresolved.

**PROPOSED DECISION — REQUIRES APPROVAL:** the interim rule is §8.3 as stated — no image redaction, minimize elsewhere. **Redaction scope for derived artefacts is revisited when G-12 closes**, and that revisit is listed as an exit criterion in §16.

---

## 9. Retention and Destruction

### 9.1 What exists and what does not

**EXISTING REQUIREMENT — NFR-PRIV-003:** "Deletion requested by the user shall remove the document, its extracted information, and its derived copies within a stated period. **Period: TBD — to be validated against legal requirements.**"

Two things to note: it governs **user** documents, not a corpus; and **its own period is TBD in the specification**. Nothing about corpus retention can be inherited from it — but its *structure* is instructive, because it reaches "extracted information" and "derived copies", which is exactly the reach §9.3 needs.

**REQUIREMENTS GAP — G-02** covers corpus retention and destruction entirely. **D-02.e/f** assign both to PM + Legal.

### 9.2 G-02.8 — the retention lifecycle

**PROPOSED DECISION — REQUIRES APPROVAL.** Retention is defined as a **lifecycle with triggers**, and **all durations are TBD**. Per the brief's instruction, **no duration is invented**.

| Stage | State | Entry trigger | Exit trigger | Duration |
| --- | --- | --- | --- | --- |
| **0. Pre-collection** | No document exists | — | Consent recorded (§5) | — |
| **1. Collected** | Document in corpus store, unannotated | Consent + collection | Annotation begins | **TBD** — a maximum before annotation is a proposed control |
| **2. Annotated** | Ground truth attached | Annotation complete | Split assigned | **TBD** |
| **3. Split** | Assigned to development or held-out, sealed (§11) | Split fixed, before any engine installed | Evaluation begins | **TBD** |
| **4. Evaluation active** | In use for a running evaluation | Evaluation begins | Evaluation report accepted | Duration of the evaluation |
| **5. Retention hold** | Retained to support reproducibility and possible re-evaluation | Report accepted | Destruction trigger below | **TBD — the decisive open duration** |
| **6. Destruction pending** | Scheduled, copies enumerated | Destruction trigger met | Destruction verified | **TBD** — short by design |
| **7. Destroyed** | Only §13 evidence remains | Destruction verified | — | — |

**PROPOSED DESTRUCTION TRIGGERS — REQUIRES APPROVAL.** Whichever occurs first:

| # | Trigger | Reason |
| --- | --- | --- |
| T1 | The evaluation the corpus supports is **superseded** — a later evaluation on a later corpus becomes the basis for the live thresholds | The corpus's purpose has ended |
| T2 | A **fixed maximum retention period** from collection is reached | **TBD — requires product/privacy and legal approval** |
| T3 | The contributor **withdraws consent** — for their documents only | §10 |
| T4 | The evaluation is **abandoned** | Purpose ended |
| T5 | The consent's stated scope is **exhausted** — e.g. consent covered one evaluation and that evaluation is complete | §5.3(b), BR-007's non-generalisation |

**Why triggers and not a bare duration.** **G-03** — "No re-evaluation trigger when an assisted component changes version" — means the corpus's useful life is genuinely uncertain: thresholds calibrated against one engine version are not evidence for another, so the corpus may be needed again on a schedule nobody can predict today. A duration alone would either destroy the corpus while it is still the sole evidence for a live threshold, or retain it indefinitely on the strength of a hypothetical. **T1 ties destruction to the evidence's actual obsolescence, and T2 caps it regardless.**

**The tension is real and must be resolved by approval, not by drafting:** a short retention period and a re-evaluation obligation pull in opposite directions. §13 is what makes a short period survivable — the aggregate evidence outlives the documents.

### 9.3 G-02.9 — copies to be destroyed

**PROPOSED DECISION — REQUIRES APPROVAL.** Destruction reaches **every** artefact of §7.5, enumerated before destruction begins:

| # | Artefact | Note |
| --- | --- | --- |
| 1 | Document files in the corpus store | The obvious one |
| 2 | **Ground truth annotations** | Contains personal values in labelled form — **must not be overlooked because it is "just metadata"** |
| 3 | Extraction outputs — text, fields, regions | Contains personal values |
| 4 | Annotation working copies | **G-23** does not cover them; they must be enumerated explicitly or they will survive |
| 5 | Temporary processing artefacts | Should already be destroyed per §7.5 |
| 6 | Backups and replicas of 1–5 | **Blocked by G-23** — the encryption/storage boundary is undefined |
| 7 | External processor copies, if any | **Blocked by G-23**; contractually dependent per §7.4 |

**Explicitly NOT destroyed** (§13): the aggregate evaluation report, provenance record, corpus manifest, access log, destruction record, and consent records — none of which contain document content or personal values, except the consent records, which are governed by §5.6.

### 9.4 Destruction method

**PROPOSED DECISION — REQUIRES APPROVAL, BLOCKED FROM FINAL FORM.**

**REQUIREMENTS GAP — G-24:** "Whether crypto-erasure satisfies NFR-PRIV-003 deletion is unaddressed, and the deletion period remains TBD."
**REQUIREMENTS GAP — G-22:** key management is entirely absent — so a crypto-erasure method cannot be specified even if it were approved.

Per the brief's instruction: **this dependency is identified, not invented.** The method must be chosen by security ownership together with G-21/G-22/G-24, and the following is a placeholder structure, not a chosen method:

| Element | Status |
| --- | --- |
| Method — secure erasure, crypto-erasure, or media destruction | **DECISION REQUIRED**, blocked by **G-22**, **G-24** |
| Whether crypto-erasure counts as destruction | **REQUIREMENTS GAP — G-24** |
| Backup and replica reach | **REQUIREMENTS GAP — G-23** |
| Verification method | **DECISION REQUIRED** |
| Who performs and who verifies | **PROPOSED**: Corpus Custodian performs; a second named person verifies |

### 9.5 Destruction evidence

**PROPOSED DECISION — REQUIRES APPROVAL.** A **destruction record** is created and retained, containing: what was destroyed by identifier, the copy enumeration of §9.3, the trigger invoked, the method, the date, who performed it, who verified it.

It contains **no document content and no personal values**, so it survives destruction under §13. Following **FR-AUD-005**'s principle, it is append-only.

**Without this record, "destroyed" is as unfalsifiable as "evaluated" is without D-02.o.** That symmetry is the reason it is proposed.

---

## 10. Consent Withdrawal

### 10.1 The right to withdraw

**PROPOSED DECISION — REQUIRES APPROVAL.** A contributor may withdraw consent **at any time, without giving a reason, and without any consequence to them**. Withdrawal is stage T3 in §9.2.

**Reasoning.** **FR-ACC-007** and **FR-DOC-007** give users an unconditional right to delete their data from the product. A contributor who has given more — real identity documents, for the team's benefit rather than their own — cannot coherently have less.

### 10.2 What withdrawal does

**PROPOSED DECISION — REQUIRES APPROVAL**

| Step | Action | Timing |
| --- | --- | --- |
| 1 | Withdrawal recorded in the consent record store (§5.6) | Immediately |
| 2 | Contributor's documents removed from all active use — no further evaluation, no further annotation | Immediately |
| 3 | Documents and **all derived artefacts** (§9.3, items 1–5) destroyed | **Within a stated period — TBD** |
| 4 | Corpus **re-versioned**, with the withdrawal recorded as the reason | At destruction |
| 5 | Affected prior results marked per §10.3 | At re-versioning |
| 6 | Withdrawal confirmed to the contributor, stating what was destroyed and what aggregate evidence was retained | On completion |

**Period: TBD.** NFR-PRIV-003's analogous period is itself "TBD — to be validated against legal requirements", so no period is inherited and **none is invented**. **DECISION REQUIRED — PM + Legal.**

### 10.3 Withdrawal and reproducibility — the honest handling

Withdrawal after a result has been recorded means **the corpus version that produced that result no longer exists in full**. Two dishonest responses are available and both are rejected:

| Rejected response | Why |
| --- | --- |
| Retain the documents to preserve reproducibility | Makes withdrawal conditional on the team's convenience. Not withdrawal. |
| Destroy them and silently re-version the corpus as if nothing changed | The recorded result would then cite a corpus version that never produced it — a fabricated provenance chain |

**PROPOSED DECISION — REQUIRES APPROVAL:**

1. The documents are **destroyed**. Withdrawal is unconditional.
2. The corpus is **re-versioned**, and the withdrawal is recorded as the reason in the provenance record.
3. Any evaluation result produced against the prior version is **marked "no longer fully reproducible — corpus altered by consent withdrawal"**, and retains its original corpus version reference.
4. The result is **not** deleted and **not** silently restated. It remains valid evidence of what was measured, annotated with the fact that the measurement can no longer be repeated exactly.

This follows **FR-AUD-005**'s principle directly: "History entries shall not be editable by the user; corrections are recorded as new entries." **The correction is an annotation, never an edit.**

### 10.4 What survives withdrawal

**PROPOSED DECISION — REQUIRES APPROVAL.** Aggregate evidence (§13) may be retained after withdrawal, because it contains no document content, no personal values, and nothing attributable to the contributor. **This must be stated in the consent (§5.3(h)) before collection** — a contributor is entitled to know, at the moment they consent, that aggregate results computed while their document was present will not be recomputed away.

The **consent record itself** is retained per §5.6, including the withdrawal, as the evidence that the withdrawal was honoured. **Retention period TBD — legal input required.**

### 10.5 Withdrawal must be operable

**PROPOSED DECISION — REQUIRES APPROVAL.** A withdrawal path that exists on paper and cannot be executed is not a control. Before collection begins:

- the contact route for withdrawal is stated in the consent and is monitored;
- the corpus identifier mapping (§8.5) is sufficient to locate every artefact belonging to one contributor — **if it is not, the corpus structure is wrong and must be fixed before collection**;
- the Corpus Custodian role has authority and access to execute destruction without further approval.

---

## 11. Held-Out Set Control

### 11.1 What the specification requires

**EXISTING REQUIREMENT — AR-AST-008:** "...evaluated against a **held-out** corpus of real, imperfect documents before any threshold is set."

The requirement is stated. **The mechanism is not — D-02.g.** Everything in §11 is proposed.

### 11.2 G-02.11 — who controls the held-out portion

**PROPOSED DECISION — REQUIRES APPROVAL.** A named **Held-Out Custodian** controls the held-out split.

| Rule | Reason |
| --- | --- |
| The Held-Out Custodian is a **named individual**, recorded | Accountability |
| They **must not** be a person who configures, tunes, prompts, or selects extraction | A person who tunes and holds the answer key cannot demonstrate that they did not use it |
| They may hold the Corpus Custodian role | No conflict — neither role tunes extraction |
| They **may not** hold the Evaluator role while that Evaluator configures candidates | The prohibited combination |
| They authorise and record every held-out access | §11.3 |
| They hold the sealed split assignment | §11.3 control 2 |

**PROPOSED DECISION — REQUIRES APPROVAL:** if the team is too small for this separation, **that fact is recorded as a stated limitation of the evaluation** (D-02 §14.6) rather than the separation being quietly dropped. **NFR-SEC-008**'s principle — describe specific measures *and their limits* — applies directly.

### 11.3 G-02.12 — preventing tuning against the held-out set

**PROPOSED DECISION — REQUIRES APPROVAL.** Six controls, procedural and technical together, because either alone is insufficient:

| # | Control | Mechanism |
| --- | --- | --- |
| **1** | **Separate storage and separate access** | The held-out split is a distinct access scope. An Evaluator configuring candidates is not granted it. Not a naming convention — an access boundary. |
| **2** | **Sealed split, fixed before any engine is installed** | Split assignment is recorded and hashed as part of the corpus version (D-02 §4.10) before any candidate exists. A split fixed after an engine is installed cannot be shown to be independent of it. |
| **3** | **Split by person, never by document** | The corpus is person-grouped (D-02 §4.6). Splitting by document would place one person's documents on both sides, leaking layout, issuing authority, and — for conflict detection — the very attribute values under test. |
| **4** | **A real development set exists** | The most effective anti-leakage control is that developers have adequate material they *are* allowed to use. A team with no development set will use the held-out set; the policy will lose. |
| **5** | **Single-run discipline** | The held-out set is used once per candidate configuration. Re-running after a configuration change is a **new evaluation**, recorded as such, and it consumes independence — which may mean it is not available. |
| **6** | **Logged and disclosed access** | Every held-out access is logged (§6.5), reviewed by the Held-Out Custodian, and **disclosed in the evaluation report**. If held-out material was seen before the run, the report says so. |

### 11.4 The specific hazard this guards against

D-02 §6.4 identifies it: **§7.1 makes document-type inclusion conditional on this evaluation.** An unfavourable per-type result creates direct pressure to re-run with adjusted configuration until the type passes.

That is **selection on the held-out set**, and it destroys the evidence value of the entire evaluation — including for the types that passed first time.

**PROPOSED DECISION — REQUIRES APPROVAL:** the per-type pass criterion is fixed **before** the held-out run, and a type that fails is demoted per §7.1 rather than retried. Authority to approve an exception rests with the Held-Out Custodian jointly with PM, and any exception is recorded in the report.

### 11.5 Held-out status degrades and that must be said

**REQUIREMENTS GAP — G-03.** A held-out set is held out **once**. After the first evaluation, the team has seen its results; a second evaluation of a new engine version against the same corpus is weaker evidence, and the specification never acknowledges this.

**PROPOSED DECISION — REQUIRES APPROVAL:** every re-evaluation against a previously used corpus states the reduced independence as a limitation. **Whether re-evaluation reuses the corpus (accepting degraded independence) or requires fresh material (accepting recurring collection and consent cost) is a DECISION REQUIRED with a real budget consequence**, and it should be taken now rather than at the moment an engine upgrade is proposed — because it determines the §5.3(b) consent scope, which must be fixed before collection.

---

## 12. Synthetic Data

### 12.1 The requirement is preserved without qualification

**EXISTING REQUIREMENT — AR-AST-008:** "Assisted components shall be evaluated against a held-out corpus of **real, imperfect** documents before any threshold is set."

**PROPOSED DECISION — REQUIRES APPROVAL, stated as a prohibition:**

> **Synthetic documents may never substitute for the real-document evaluation AR-AST-008 requires.** No count of synthetic documents, however realistic, discharges AR-AST-008. No result computed on synthetic documents may be reported as satisfying it.

The register records document 02's warning about the sibling study S-1: *"Any study that substitutes dummy data will produce a false positive on our riskiest assumption."* **A-7 — extraction reliability on real scans — is that assumption.** A synthetic evaluation would report success precisely where the risk lives.

### 12.2 G-02.14 — where synthetic documents are permitted

**PROPOSED DECISION — REQUIRES APPROVAL.** Synthetic and team-authored documents are permitted, and useful, in four places — none of which is the held-out evaluation:

| Use | Permitted | Reason |
| --- | --- | --- |
| **Harness development** — building and debugging the evaluation instrument | **Yes** | The harness should be working before it touches real documents. This *reduces* real-document exposure. |
| **Development set material** — extraction configuration, pre-processing choices | **Yes** | Directly supports control 4 of §11.3: give developers material they are allowed to use |
| **Pipeline smoke tests** | **Yes** | No evaluation claim is made |
| **Filling gaps in the held-out corpus** — a type or condition the real corpus lacks | **NO** | This is substitution, and it is the failure mode §12.1 prohibits |
| **Any reported evaluation result** | **NO** | AR-AST-008 |

**Note the second row's value:** a well-supplied synthetic development set is not a concession to the policy — it is one of the controls that makes held-out separation survivable in practice.

### 12.3 Mandatory separation and disclosure

**PROPOSED DECISION — REQUIRES APPROVAL**

1. Synthetic documents are **stored separately** from the real corpus and are **never** admitted into the held-out split.
2. Every document in the corpus carries an immutable **real / synthetic** marker in the manifest, assigned at ingestion.
3. Every evaluation report states its corpus composition, and **all AR-AST-008 conclusions are computed on real documents only.**
4. Where a candidate is exercised on synthetic material, those results are reported in a **separate, clearly labelled section**, never merged into the real-document results.
5. **A report may not present a blended figure.** A single number combining real and synthetic results would be exactly the silent substitution §12.1 prohibits, achieved by arithmetic instead of by policy.

### 12.4 Representativeness applies to real documents too

**PROPOSED DECISION — REQUIRES APPROVAL.** The real / synthetic marker is necessary but not sufficient. A corpus of real documents drawn entirely from the team and their families is real *and* unrepresentative — likely narrow in issuing authority, language, and capture quality.

Every report states how the corpus was acquired and what population it does and does not represent. **An evaluation that overstates its own generality is worse than none**, because it will be cited as evidence for a threshold protecting real applications. This is **NFR-SEC-008**'s principle — measures *and their limits* — applied to evaluation claims.

---

## 13. Evaluation Evidence Retention

### 13.1 Why this section is what makes short retention possible

**REQUIREMENTS GAP — D-02.o:** AR-AST-008 requires the evaluation to happen but does not say what artefact proves it happened, who reviews it, or where it is retained. **Without a defined artefact, "evaluated" is unfalsifiable.**

The design goal follows directly: **the evidence must be able to outlive the documents.** If proving AR-AST-008 required retaining the corpus, retention would be unbounded and destruction would conflict with compliance. Because the evidence is aggregate, it does not.

### 13.2 G-02.13 — what may be retained after destruction

**PROPOSED DECISION — REQUIRES APPROVAL**

| Retained | Contains | Basis |
| --- | --- | --- |
| **Evaluation report** — metrics, distributions, per-type and per-condition results, threshold sweep | Aggregates and counts only | **NFR-PRIV-007**; **NFR-OBS-001**'s aggregate-without-underlying-values pattern |
| **Provenance record** — corpus version, split, ground-truth version, engine and version, harness version, date, operator | Identifiers and versions | D-02 §14.2 |
| **Corpus manifest** — document identifiers, type, page count, degradation conditions, person group, split, real/synthetic marker | Structural properties. **No content, no values** | §8.3 |
| **Access log** | Who accessed what, when. **No values** | §6.5 |
| **Destruction record** | What was destroyed, method, verification | §9.5 |
| **Consent records** | Contributor identity — governed separately by §5.6 | §5.6; retention **TBD** |
| **Inter-annotator agreement statistics** | Aggregate agreement rates | D-02 §7.6 |
| **Limitations statement** | Prose | §12.4 |

### 13.3 What may never be retained after destruction

**PROPOSED DECISION — REQUIRES APPROVAL.** None of the following survives destruction, in any artefact, for any reason:

- document images, files, or excerpts;
- extracted text or extracted field values;
- **ground truth values** — the most likely thing to be retained by accident, because it looks like structured evaluation data rather than personal data;
- contributor identity linked to documents;
- example failures containing real values — **including "just one illustrative example" in a report**.

**The last exclusion is load-bearing.** A report containing illustrative examples becomes a small corpus of its own, forfeits the property that makes §13 work, and quietly reintroduces indefinite retention of personal values through the back door.

**NFR-OBS-001** shows the specification already reasoning this way for production: measure "confidence distributions in aggregate, **without retaining the underlying values**." §13 applies the same pattern to evaluation.

### 13.4 The report's own governance

**PROPOSED DECISION — REQUIRES APPROVAL.** Because the report outlives the corpus and is the sole evidence for AR-AST-008:

- it is **versioned** and **retained** at a defined location, per D-02 §14.3;
- it is **reviewed and signed** — **DECISION REQUIRED: by whom** (D-02.o);
- it states which requirements **could not** be evaluated and which gap blocked each — **an honest report of a blocked evaluation is evidence; a silent omission is not**;
- it states whether held-out status was preserved (§11.3, control 6);
- following **FR-AUD-005**'s principle, a superseded report is **annotated, never edited or deleted**.

---

## 14. Security and Privacy Dependencies

This section addresses each area named in the brief, and marks where an unresolved requirement prevents a final decision.

### 14.1 Least privilege

| Element | Status |
| --- | --- |
| Role-based access, four roles | **PROPOSED** — §6.2 |
| Named individuals, no shared accounts | **PROPOSED** — §6.3 |
| Time-bound, purpose-bound, no standing access | **PROPOSED**, on **NFR-SEC-007**'s principle — §6.4 |
| Held-out separation enforced through roles | **PROPOSED** — §11.2 |
| No bulk export | **PROPOSED** — §6.3 |

**No blocking dependency.** This is decidable now.

### 14.2 Data minimization

| Element | Status |
| --- | --- |
| Collect only what the evaluation needs; contribution is a distinct act | **PROPOSED**, on **NFR-PRIV-001** — §4.1, §4.3 |
| No image redaction — fidelity is the requirement | **PROPOSED** — §8.1 |
| Pseudonymous identifiers; identity separated from documents | **PROPOSED** — §8.5 |
| Manifests, logs, and reports carry no values | **EXISTING REQUIREMENT** — NFR-PRIV-007, NFR-OBS-004 — §8.4 |
| Derived-artefact redaction scope | **BLOCKED — G-12.** Interim rule in §8.3; revisit at G-12 closure |

### 14.3 Sensitive information in logs

**EXISTING REQUIREMENTS — NFR-PRIV-007, NFR-OBS-004.** These are binding today and need no new decision: no document contents, no extracted personal values, in any diagnostic or failure record. **FR-AUD-006**'s "record the action, not the contents" is the pattern.

**No blocking dependency.**

### 14.4 Encryption at rest

**EXISTING REQUIREMENT — NFR-SEC-002**, plus **NFR-SEC-001** in transit.

**BLOCKED — G-21, G-22, G-23.** The requirement is binding; its content is undefined; key management is entirely absent. **Per the brief, this dependency is identified rather than invented: no encryption standard, key policy, or crypto-erasure method is specified in this document.** §7.3 and §9.4 cannot reach final form until security ownership closes these gaps — which is **entry gate E6** in D-02 §19.2.

### 14.5 External / off-device processing

**EXISTING REQUIREMENTS — NFR-PRIV-005, NFR-PRIV-006.** Proposals in §7.4 and §5.3(c): recipient named in consent before collection; training excluded by terms; retention reconciled; transport encrypted; transfer logged; and if the consent scope does not cover the recipient, **the candidate is not evaluated on the real corpus**.

**Partially blocked — G-17** (what "processing" means in NFR-PRIV-006 is undefined) and **G-23** (external processor custody undefined).

### 14.6 Deletion

**EXISTING REQUIREMENTS — NFR-PRIV-003** (structure, period TBD), **FR-ACC-007**, **FR-DOC-007/008**.

**PROPOSED:** the lifecycle and triggers of §9.2, the copy enumeration of §9.3, and the destruction record of §9.5.

**BLOCKED — G-24** (crypto-erasure), **G-22** (keys), **G-23** (backup reach). **All durations TBD.**

### 14.7 Access control

**EXISTING REQUIREMENT — NFR-SEC-003**, whose *principle* transfers (authorise the accessor, never infer authority from a supplied identifier) but whose *mechanism* does not, because corpus documents have no owning user (§6.1).

**PROPOSED:** §6 in full, plus mandatory isolation from production storage (§7.2) so that the two access models are never asked to coexist in one store.

**No blocking dependency**, given isolation.

### 14.8 Auditability

**REQUIREMENTS GAP — G-26:** no requirement obliges recording security-relevant events at all.

**PROPOSED:** append-only, value-free access logging (§6.5), following **FR-AUD-005**'s non-editable principle; the destruction record (§9.5); and the provenance record (§13.2).

**These are proposals, not inherited controls**, and §15 flags that G-26 should be closed as a requirement in its own right — its scope is the whole product, not only the corpus.

### 14.9 Honest description of these controls

**EXISTING REQUIREMENT — NFR-SEC-008:** "The system shall not claim to be unbreachable in any user-facing or internal material. Security statements shall describe specific measures and their limits."

Applied to this document: **the controls proposed here sit inside a requirements gap.** They are not inherited from an approved security model, because the specification contains none for evaluation material. Presenting them as settled would be the overclaiming NFR-SEC-008 prohibits. **The corpus security model requires security ownership and approval before collection begins.**

---

## 15. Decisions Requiring Product/Privacy Approval

### 15.1 Blocking — corpus collection cannot begin until these are approved

**Status: B1–B16 APPROVED, 3 September 2026**, with two exceptions that remain blocked by unresolved requirements and were **not** approved: **B12** (retention durations — all remain **TBD**) and **B15** (corpus security model — blocked by G-21, G-22, G-23). The table below is retained as the record of what was decided and by whom.

| # | Decision | Owner | Section |
| --- | --- | --- | --- |
| B1 | Contributor eligibility, **including the exclusion of minors** | PM + Legal | §4.1 |
| B2 | Consent text and the eight required elements | PM + Legal | §5.3 |
| B3 | Consent scope — this evaluation only, or future re-evaluations | PM + Legal | §5.3(b), §11.5 |
| B4 | Recipient scope — whether external candidate engines are permitted at all | PM + Legal | §7.4 |
| B5 | Whether NFR-PRIV-002's readability prohibition binds the team | PM + Legal | §6, D-02.c |
| B6 | Acquisition method | PM | D-02.d |
| B7 | Role definitions and access model | PM + Engineering | §6.2 |
| B8 | Named Corpus Custodian and named Held-Out Custodian | PM | §6.2, §11.2 |
| B9 | Mandatory isolation from production storage | Engineering + PM | §7.2 |
| B10 | **Prohibition on automatic ingestion of user documents** | PM + Legal | §4.3 |
| B11 | Retention lifecycle and destruction triggers | PM + Legal | §9.2 |
| B12 | **Retention durations — all TBD** | PM + Legal | §9.2 |
| B13 | Destruction method, verification, and evidence | Security + PM + Legal | §9.4 |
| B14 | Withdrawal process and period | PM + Legal | §10 |
| B15 | Corpus security model, **blocked by G-21/G-22/G-23** | Security ownership | §7.3, §14.4 |
| B16 | Whether corpus handling is in NFR-SEC-009's independent review scope | PM + Security | §2.4 |

### 15.2 Non-blocking — required before the corresponding activity

| # | Decision | Required before | Section |
| --- | --- | --- | --- |
| N1 | Derived-artefact redaction scope, **blocked by G-12** | Field-extraction evaluation | §8.6 |
| N2 | Whether confidence calibration constitutes "training" under NFR-PRIV-002 | Any calibration | D-02 §5.4 |
| N3 | Held-out reuse vs fresh collection on re-evaluation | **Consent drafting** — it fixes §5.3(b) | §11.5 |
| N4 | Report reviewer, signer, and retention location | Report acceptance | §13.4 |
| N5 | Consent-record retention period | Consent drafting | §5.6 |
| N6 | Synthetic-material policy for the development set | Development work | §12.2 |

### 15.3 Proposals that should become requirements if approved

Per §1.2, a policy that is not a requirement is not enforceable by the specification. If approved, the following should be raised as amendments rather than left as documentation:

| Proposal | Would close |
| --- | --- |
| Evaluation-corpus governance — consent, access, retention, destruction, withdrawal | **G-02** |
| Re-evaluation trigger when an assisted component changes version | **G-03** |
| Security-event recording — **scope is the whole product, not only the corpus** | **G-26** |
| Definition of the evaluation artefact that proves AR-AST-008 was met | **D-02.o** |

### 15.4 Explicit non-amendment

**`backend/step3.pdf` is not amended by this document.** Nothing here changes a requirement, a release marking, a MoSCoW priority, or the containment rule of §11. Every proposal is external to the specification until adopted through its own change process — which §12's containment rule describes as requiring "a new version number".

---

## 16. G-02 Exit Criteria

### 16.1 Exit criteria for this document

| # | Criterion | Status |
| --- | --- | --- |
| 1 | All fourteen G-02 sub-decisions addressed with an explicit recommendation | **Met** — §4 |
| 2 | Existing requirements separated from proposals throughout | **Met** — §1.2, §2, labelling |
| 3 | Every proposal labelled **PROPOSED DECISION — REQUIRES APPROVAL** | **Met** |
| 4 | Every recommendation justified from existing requirements where possible | **Met** — §4.3 in particular |
| 5 | **No retention duration invented**; lifecycle defined with durations TBD | **Met** — §9.2 |
| 6 | AR-AST-008's real-document requirement preserved against synthetic substitution | **Met** — §12 |
| 7 | Security/privacy areas from the brief each addressed | **Met** — §14 |
| 8 | Blocking dependencies identified, not invented | **Met** — G-12, G-21…G-24, G-26, G-03 |
| 9 | `step3.pdf` not amended | **Met** — §15.4 |
| 10 | Approval table | **Met** — §16.3 |
| 11 | Reviewed and approved by PM, Legal, and Security | **Met — approved 3 September 2026** |

**G-02 is APPROVED as a project decision by this document, recorded at D-02.5 of the decision register.** It is **not** closed as a *gap*: the specification amendments of §15.3 have not been raised, so G-02 remains open in the register's requirements-gap inventory. The approval settles governance; it does not settle the requirement.

### 16.2 What unblocks on approval

| On approval of | D-02 entry gate unblocked |
| --- | --- |
| B1, B2, B3, B6 | **E1** consent model, **E3** acquisition |
| B8 | **E2** corpus ownership |
| B11, B12, B13 | **E4** retention and destruction |
| B5, B7 | **E5** team access model |
| B15 *(blocked on G-21/G-22)* | **E6** corpus security model |
| B4 | **E7** recipient scope |

**All of E1–E7 are gated by this document.** With them approved, corpus collection may begin; annotation gates (E8–E11) and the field-extraction gates (E12–E15, blocked on G-12/G-13) remain separate and unaffected.

### 16.3 Approval table

| ID | Proposed decision | Reason | Approval required |
| --- | --- | --- | --- |
| **G-02.1** | Contribution limited to adults contributing their own documents, via a dedicated process outside product signup; minors excluded at MVP | NFR-PRIV-001 minimization; BR-007 non-generalisation; no guardian-consent framework exists in the specification | PM + Legal |
| **G-02.2** | Explicit, informed, purpose-bound, recorded, withdrawable consent with eight required elements, obtained before collection, unbundled from terms of service | NFR-PRIV-006's plain-language standard; BR-006/BR-007 consent principle; NFR-PRIV-002 training prohibition must be stated | PM + Legal |
| **G-02.3** | **User documents never enter the corpus automatically.** Opt-in only, via a separate affirmative act, with the distinct corpus lifecycle disclosed at consent | FR-ACC-007 "all associated data"; FR-DOC-007 confirmation must name what is lost; NFR-PRIV-001; NFR-PRIV-002; FR-ACC-006; BR-006/BR-007 | PM + Legal |
| **G-02.4** | Four roles, least privilege, named individuals, time- and purpose-bound, logged, revocable; contributor identity withheld from Annotator and Evaluator | NFR-SEC-003's principle (mechanism does not transfer); NFR-SEC-007 no standing access; G-26 means logging is proposed | PM + Engineering |
| **G-02.5** | One designated corpus store inside DOCURA's trust boundary; enumerated permitted locations; no personal devices, cloud drives, chat, or ticketing | D-01 self-hosted boundary; NFR-SEC-001/002; **final form blocked by G-21, G-22** | Security + Engineering |
| **G-02.6** | **Mandatory isolation from production document storage**; harness holds no production credentials | Incompatible deletion lifecycles (FR-ACC-007, FR-DOC-007/008); NFR-SEC-003 has no owning user for corpus documents; NFR-PRIV-002 leak prevention; FR-ACC-006 export correctness | PM + Engineering |
| **G-02.7** | **No redaction of document images**; minimize contributor identity, manifests, logs, and reports instead; pseudonymous identifiers | AR-AST-008 requires real, imperfect documents; NFR-PRIV-007 and NFR-OBS-004 bind derived artefacts; **derived-artefact scope blocked by G-12**; graduated protection blocked by G-14/15/16 | PM + Legal + Engineering |
| **G-02.8** | Seven-stage lifecycle with five destruction triggers; **all durations TBD** | NFR-PRIV-003 does not cover a corpus and its own period is TBD; G-03 makes useful life genuinely uncertain; no duration invented | PM + Legal |
| **G-02.9** | Enumerated copies including ground truth and working copies; defined method; verification by a second person; retained destruction record | NFR-PRIV-003's reach to derived copies; FR-AUD-005 append-only principle; **method blocked by G-22, G-23, G-24** | Security + PM + Legal |
| **G-02.10** | Withdrawal honoured unconditionally; documents and derived artefacts destroyed; corpus re-versioned; **prior results annotated as no longer fully reproducible, never edited or deleted**; aggregates retained and disclosed at consent | FR-ACC-007 / FR-DOC-007 give users an unconditional deletion right; FR-AUD-005 corrections are new entries, not edits | PM + Legal |
| **G-02.11** | Named Held-Out Custodian who does not configure, tune, or select extraction; team-size limitations stated rather than the separation dropped | AR-AST-008 "held-out"; NFR-SEC-008 principle — describe measures and their limits | PM + Engineering |
| **G-02.12** | Six controls: separate access scope; sealed split fixed before any engine is installed; split by person; a real development set; single-run discipline; logged and disclosed access | AR-AST-008; §7.1 creates direct pressure to re-run until a type passes (D-02 §6.4) | PM + Engineering |
| **G-02.13** | Aggregates, provenance, manifest, access log, destruction record, and consent records may outlive the corpus; **no content, extracted values, ground-truth values, or illustrative examples** | NFR-PRIV-007; NFR-OBS-001's aggregate-without-values pattern; FR-AUD-006 record-the-action pattern; makes short retention survivable | PM + Engineering |
| **G-02.14** | Synthetic permitted for harness development and the development set; **never as a substitute for the real held-out evaluation**; immutable real/synthetic marker; no blended figures | **AR-AST-008 requires real, imperfect documents**; substituting dummy data produces a false positive on A-7, the riskiest assumption | PM + Engineering |

---

## 17. Status

| Item | Status |
| --- | --- |
| G-02 governance policy | **APPROVED** — 3 September 2026 |
| Documents collected | **0** |
| Corpus | **Does not exist.** Collection blocked on B1–B16 |
| Consent text | **Not drafted.** Elements specified in §5.3; drafting is PM + Legal |
| Contributor identities held | **None** |
| Production documents used as evaluation data | **None**, and §4.3 proposes that none ever be, absent explicit opt-in |
| Corpus security model | **Blocked** — G-21, G-22, G-23 |
| Retention durations | **TBD** — none invented |
| Destruction method | **Blocked** — G-22, G-24 |
| `backend/step3.pdf` | **Unamended** |
| Production code | **Unmodified** |
| Database schema | **Unchanged** |
| Migrations | **None** |
| Dependencies added | **None** |
| OCR engine | **TBD — pending held-out evaluation** |
