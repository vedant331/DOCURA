# DOCURA — Sprint 4 Decision Register

## Sprint 4: OCR & Document Understanding (FR-OCR / FR-INF)

| Field | Value |
| --- | --- |
| Document | Sprint 4 Decision Register |
| Status | Draft for Product Management review |
| Date | 1 September 2026 |
| Authoritative source | `backend/step3.pdf` — DOCURA 03, Requirements Specification, v1.0 (25 August 2026) |
| Secondary reference (cited, never authoritative) | DOCURA 02 — Problem & User Research v1.0 (`Phase1-Research/step2.pdf`), cited only where §1/§2 of the specification traces to it by ID |
| Preceding sprints | Sprint 1 (foundation) PASS · Sprint 2 (authentication) PASS · Sprint 3 (document vault) PASS, manually verified, committed |
| Purpose | Record every architecture, product, and requirements decision that must be resolved before Sprint 4 implementation begins |
| Out of scope | Implementation of any kind. No code, tests, migrations, dependencies, configuration, schema, OCR, workers, APIs, or UI were changed to produce this document. |

---

# 0. How to read this register

## 0.1 The evidence rule

Every statement here is one of the labelled kinds below, and each is labelled. Nothing is asserted as a requirement unless it appears in `backend/step3.pdf`. Where the specification is silent, the silence is recorded as a gap rather than filled with a plausible answer.

## 0.2 Label taxonomy

| Label | Meaning | Who resolves it |
| --- | --- | --- |
| **REQUIREMENT** | Stated in the Requirements Specification. Quoted or cited by ID. Not negotiable by engineering. | Already decided — implement it |
| **RECOMMENDATION** | This register's engineering advice. Has no requirement status until approved. | Engineering proposes, PM notes |
| **ARCHITECTURE DECISION** | A choice about *how* a requirement is met. The specification deliberately leaves it open (§6 Selection Principle: "Technology selection belongs to document 04"). | Architecture / Step 4 |
| **PRODUCT DECISION** | A choice about *what the product does* that the specification does not settle. Cannot be made by engineering. | Product Management |
| **ASSUMPTION** | Something this register had to suppose in order to reason. Must be confirmed or corrected. | PM confirms |
| **REQUIREMENTS GAP** | The specification requires an outcome but does not define what is needed to produce it. Needs a specification amendment (§11 Containment Rule: a change is made "with a new version number"). | PM amends `step3.pdf` |
| **DECISION REQUIRED** | An open question, not yet classified as architecture or product until someone owns it. | Named in each entry |
| **PRODUCT DECISION — APPROVED** | A **PRODUCT DECISION** that has since been taken and recorded. Binding on implementation as a project decision. It does **not** amend `step3.pdf`, and it does not convert any **REQUIREMENTS GAP** it sits beside into a settled requirement. | Already decided — implement it |

## 0.3 What the specification says Sprint 4 is

Sprint 4 delivers the two modules that turn stored files into structured information:

| Module | §1 reference | MVP requirements |
| --- | --- | --- |
| FR-OCR — OCR & Document Understanding | §1.4 | FR-OCR-001 … FR-OCR-010 (10 MVP, 2 FUTURE) |
| FR-INF — Structured Information | §1.5 | FR-INF-001 … FR-INF-009 (9 MVP, 1 FUTURE) |

Supporting automation requirements: AR-DET-003, AR-DET-005, AR-DET-008, AR-AST-001, AR-AST-002, AR-AST-006, AR-AST-007, AR-AST-008.
Supporting non-functional requirements: NFR-PERF-002, NFR-REL-002, NFR-REL-005, NFR-SCL-002, NFR-SEC-002, NFR-SEC-003, NFR-PRIV-002, NFR-PRIV-006, NFR-PRIV-007, NFR-MNT-001, NFR-MNT-002, NFR-MNT-004, NFR-OBS-001, NFR-OBS-004, NFR-ERR-001 … NFR-ERR-005.
Stories: US-003, US-004, US-005. Demonstration steps: D2 and D3 of Table 10.1. Governing edge cases: EC-001, EC-002, EC-003, EC-004.

## 0.4 What Sprint 3 already established

Sprint 3 is the substrate Sprint 4 builds on, and its deliberate omissions are the shape Sprint 4 must fill: authenticated upload; PDF/JPG/PNG validation; upload limits; vault listing; document metadata; original-file download; SHA-256 integrity; per-user ownership isolation; deletion; local filesystem storage behind a storage port; document tests; migration. The `documents` table carries `status` with exactly the five FR-UPL-005 states, and `document_type` with only `unclassified` — no extracted text, no confidence, no attributes.

---

# D-00 — The standing contingency: assumption A-7

**Why this comes first.** Every other decision in this register is downstream of it, and it is not an engineering decision at all.

### REQUIREMENT — what the specification says

§12.3, *Requirements dependent on untested assumptions*, states of the listed requirements: **"These requirements are specified but must not be committed to build until their supporting assumption reports."** The table entry reads:

| Assumption | If it fails | Requirements affected |
| --- | --- | --- |
| A-7 | "Extraction is unreliable on real scans; thresholds may exclude most automatic action." | **FR-OCR-004 … 006, BR-001** |

§15, *Condition for exiting requirements engineering*: "This specification is complete enough to proceed to architecture... **It is not complete enough to commit to a build of the requirement sets in §12.3.**"

§15 also records the completion criterion *Consistent with the research* as **Partially met**: "document 02 contains no validated findings. Five assumptions (A-1, A-2, A-5, A-7, A-8) remain untested and are load-bearing."

### What this means for Sprint 4

FR-OCR-004 (extract the defined field set), FR-OCR-005 (per-field confidence), FR-OCR-006 (withhold below the review threshold), and BR-001 (the automatic-action threshold) are formally **not committable to build** until study S-6 reports. That is the specification's own instruction, not this register's caution.

It does **not** suspend the whole sprint. FR-OCR-001 (text extraction), FR-OCR-002/003 (classification and its confidence), FR-OCR-008 (multi-page as one document), FR-OCR-009 (failure handling), FR-OCR-010 (reprocessing), and the FR-INF record, conflict, correction, and history requirements are not named in §12.3.

### DECISION REQUIRED — D-00

| Option | Description | Consequence |
| --- | --- | --- |
| 1 — Full sprint | Build FR-OCR-004/005/006 anyway | A documented deviation from §12.3 |
| 2 — Split sprint (A-7-independent envelope) | Build the pipeline, job durability, status transitions, failure/retry paths, text extraction, classification, provenance, and the withholding *mechanism*; leave field definitions and threshold values unset | FR-OCR-004/005/006 satisfied structurally, completed when S-6 reports |
| 3 — Suspend Sprint 4 | Wait for S-6 | Delivery stalls; §15 advises against sequencing studies before architecture work |

**RECOMMENDATION:** Option 2. It is the only option that respects §12.3 without stalling delivery, and it is consistent with §15's instruction that studies "should run in parallel with architecture work, not after it." It also matches how Sprint 3 was built — the vault deliberately withheld the extraction data model rather than guessing at it.

**Owner:** Product Management (this is a scope-commitment decision, not an engineering one).
**Blocking status:** **BLOCKING** for the sprint's shape. Everything below assumes Option 2 unless PM decides otherwise.

---

# D-01 — OCR / processing architecture

## D-01.0 What the specification actually constrains

The specification does not name a technology, and says so explicitly.

> **§6, SELECTION PRINCIPLE** — "This document specifies what each layer must guarantee, not what technology provides it. Any component may be replaced provided its replacement meets the same guarantees: a confidence value that means what BR-001 assumes, the ability to return 'unknown', and explainability to the user. **Technology selection belongs to document 04.**"

**This is therefore an ARCHITECTURE DECISION, not a REQUIREMENTS GAP.** The specification has deliberately left it open and named the document that closes it. What the specification *does* impose are the guarantees any candidate must meet.

### REQUIREMENT — the constraint set every option is measured against

| ID | Requirement (as specified) | What it constrains in an OCR choice |
| --- | --- | --- |
| FR-OCR-001 | "The system shall extract machine-readable text from each uploaded document." | Must handle PDF, JPG, PNG (FR-UPL-001), including image-only PDFs |
| FR-OCR-002 | "shall classify each document into a supported document type, or as unrecognised" | Must be able to decline to classify — see AR-AST-002 |
| FR-OCR-003 | "shall record a confidence value for the classification" | The classifier must emit a confidence, not just a label |
| FR-OCR-004 | "For each supported document type, the system shall extract the defined set of information fields for that type." | Field-level extraction, driven by configuration (NFR-MNT-001) |
| FR-OCR-005 | "shall record a confidence value for every extracted field **independently of the document-level confidence**" | Per-field confidence is mandatory. The hardest constraint on candidate engines. |
| FR-OCR-007 | "shall show each extracted value alongside the region of the source document it was read from" (SHOULD) | The engine must return source geometry, or the design must recover it |
| AR-AST-001 | "Text extraction ... shall produce, for each extracted value, a confidence measure **usable by BR-001**" | The confidence must be comparable against a threshold — a number with stable meaning |
| AR-AST-002 | "shall be able to return 'unrecognised' rather than a forced choice" | Abstention must be a real output, not a post-hoc filter |
| AR-AST-006 | "Every assisted output shall be explainable to the user in terms of the source it came from." | Provenance must survive the engine boundary |
| AR-AST-007 | "may lower a confidence, never raise it, and may add a sensitivity classification, never remove one" | Monotonicity constraint on any post-processing |
| AR-AST-008 | "shall be evaluated against a held-out corpus of real, imperfect documents **before any threshold is set**" | The choice cannot be finalised before evaluation. See D-02. |
| NFR-MNT-001 | "Supported document types and their extractable fields shall be definable as configuration, so adding a type does not require re-engineering." | Rules out an engine whose types are baked into a model only the vendor can change |
| NFR-MNT-002 | "Confidence thresholds shall be externally configurable and changeable without a code release." | Thresholds live outside the engine |
| NFR-PRIV-002 | "A user's documents and extracted information **shall not be used to train shared models**, and shall not be readable by other users under any circumstance." | A hard contractual constraint on any external provider |
| NFR-PRIV-006 | "Any processing performed outside the user's device shall be disclosed in plain language before the user's first upload." | A disclosure obligation, not a prohibition. See D-07. |
| NFR-SEC-002 | "Documents and extracted information shall be encrypted at rest." | Constrains where bytes and extracted text may live. See D-10. |
| NFR-PERF-002 | "Document processing shall be asynchronous; the user shall never be blocked waiting for it" | Latency is not a functional constraint; throughput and failure behaviour are. See D-09. |
| NFR-SCL-002 | "Document processing load shall be able to grow independently of interactive traffic." (SHOULD) | The engine must be separable from the request path |

## D-01.1 Option A — Local / on-device OCR

*Definition used here:* extraction runs on the end user's own machine — in the browser (WASM), in the extension, or in a desktop component — and the server never sees document bytes for processing purposes.

| Dimension | Assessment |
| --- | --- |
| **Advantages** | Strongest possible privacy position: document contents need never leave the device for processing. Trivially satisfies NFR-PRIV-002 (nothing to train on). Removes per-document processing cost. Removes an entire class of provider-outage failure. |
| **Disadvantages** | Accuracy of browser-runnable engines on real, imperfect scans is materially below server-class engines — aggravating the A-7 risk directly. Model download size and cold start are borne by the user. No control over the user's CPU/memory. Multi-page PDF processing (FR-OCR-008) is slow on a laptop. Classification (FR-OCR-002) and field extraction (FR-OCR-004) generally need larger models than an in-browser runtime can carry. |
| **Privacy implications** | Best of all options. NFR-PRIV-006 disclosure would still be required for whatever else is off-device (storage, validation), but the disclosure would be narrower. |
| **Operational implications** | Nothing to operate — but nothing to observe either. NFR-OBS-001 (aggregate confidence distributions) and NFR-OBS-004 (failure context) become client-reported telemetry, which reintroduces a privacy surface constrained by NFR-PRIV-007. |
| **Scalability** | Perfect horizontal scaling by construction. NFR-SCL-002 becomes vacuous. |
| **Maintainability** | Poor against NFR-MNT-001: shipping a new document type means shipping a new client build to every user. |
| **Replaceability** | Poor. The engine is welded to the client distribution channel. |
| **Requirement risks** | Conflicts with **Sprint 3 as built and verified** — the vault already receives, validates, checksums, and stores bytes server-side. Choosing Option A leaves processing on-device while storage is off-device, an architecture the specification never describes. Highest risk to FR-OCR-005 (credible per-field confidence) and to AR-AST-008 (evaluating a client-side engine across a device population is materially harder). |

**Verdict:** Not viable as the MVP primary path. Retain as the technical foundation for NFR-PRIV-008 (FUTURE, horizon H5).

## D-01.2 Option B — Self-hosted OCR (DOCURA's own infrastructure)

*Definition used here:* an open-source or self-operated engine (for example a Tesseract-, PaddleOCR-, or docTR-class engine, plus a self-hosted classifier/extractor) running on infrastructure DOCURA controls. **This is still "outside the user's device" and therefore still triggers NFR-PRIV-006.**

| Dimension | Assessment |
| --- | --- |
| **Advantages** | Documents never leave DOCURA's trust boundary — no third-party processor to contract with, audit, or disclose by name. NFR-PRIV-002 is satisfied by construction: there is no shared model being trained. Full control of versioning, so an AR-AST-008 evaluation stays valid until DOCURA itself changes the engine. Cost is predictable and does not scale with per-page fees, which matters for reprocessing (FR-OCR-010). Deterministic re-runs support NFR-REL-005. |
| **Disadvantages** | DOCURA carries the entire accuracy problem — precisely the risk A-7 names. Classification and field extraction are *not* provided by an OCR engine; they must be built, which is substantially larger than "run OCR". Operating GPU or high-CPU workers is real infrastructure work. |
| **Privacy implications** | Strong. Only DOCURA processes. The NFR-PRIV-006 disclosure is simple and honest: processing happens on DOCURA's servers. |
| **Operational implications** | Highest of the three server-side options: model artefacts, worker images, resource sizing, engine upgrades, and re-evaluation after every upgrade (AR-AST-008 implies re-evaluation whenever the assisted component changes). |
| **Scalability** | Good against NFR-SCL-002 — workers scale independently of the API. Seasonal peaks (NFR-SCL-001) mean paying for idle capacity or accepting queue depth. |
| **Maintainability** | Good against NFR-MNT-001 *if* field definitions stay in configuration outside the engine; poor if a new document type requires retraining. |
| **Replaceability** | Good, provided the engine sits behind an internal port in the manner of Sprint 3's storage abstraction. |
| **Requirement risks** | Primary risk is to FR-OCR-004/005 quality — A-7 itself. Secondary risk: an OCR engine's character-level confidences are not the same thing as a *field-level* confidence "usable by BR-001" (AR-AST-001). The mapping between them must be designed and evaluated, and is easy to get wrong in a way that looks rigorous. |

## D-01.3 Option C — External OCR / AI provider

*Definition used here:* document bytes or page images are sent to a third-party document-AI or multimodal model API, which returns text, a type, fields, and possibly confidences.

| Dimension | Assessment |
| --- | --- |
| **Advantages** | Highest achievable accuracy on messy real-world scans for the least build effort — the option most likely to make A-7 report favourably. Classification and field extraction arrive as part of the capability rather than as separate projects. Adding a document type can be a schema or prompt change, which suits NFR-MNT-001 well. No model operations. |
| **Disadvantages** | User identity documents leave DOCURA's control. Per-page cost scales with usage *and with reprocessing* (FR-OCR-010), making re-runs a budget question rather than a free operation. Provider version drift silently invalidates a completed AR-AST-008 evaluation. Provider outage becomes a DOCURA processing outage. |
| **Privacy implications** | The weakest position, and the one requiring the most contractual work. **NFR-PRIV-002 makes a no-training, no-retention commitment a hard procurement requirement, not a preference.** NFR-PRIV-006 disclosure must state that processing occurs off-device with a third party. NFR-SEC-002 needs an answer for data in the provider's transient custody. NFR-PRIV-003 (deletion within a stated period) must extend to the provider's copies. |
| **Operational implications** | Lowest infrastructure burden, highest vendor-management burden: contracts, data-processing agreements, region pinning, rate limits, retries, cost controls. |
| **Scalability** | Excellent against NFR-SCL-002 and NFR-SCL-001 — elastic by default, subject to provider rate limits. |
| **Maintainability** | Excellent for adding types; poor for stability, because the component can change beneath a completed evaluation. |
| **Replaceability** | Good at the code level (behind a port), poor at the evidence level — switching providers invalidates the AR-AST-008 evaluation and the calibrated thresholds derived from it. |
| **Requirement risks** | **AR-AST-001 is the sharpest risk.** Many general multimodal models do not emit a calibrated per-field confidence; a self-reported "confidence" from a generative model is not a confidence measure "usable by BR-001", and treating it as one would violate the substance of BR-002 and AR-AST-007 while appearing compliant. **AR-AST-002** (must be able to return "unrecognised") must be verified rather than assumed — models are biased toward answering. |

## D-01.4 Option D — Hybrid

*Definition used here:* deterministic extraction first (an embedded PDF text layer where one exists), then an assisted engine only where deterministic extraction is insufficient; and/or a self-hosted baseline with an external provider as a configurable alternative behind one internal interface.

| Dimension | Assessment |
| --- | --- |
| **Advantages** | Honours §6.1: "Where deterministic logic is sufficient, it must be used. Using a probabilistic method for a solvable problem introduces avoidable error and destroys explainability." A digitally generated PDF marksheet needs no OCR at all. Reduces per-document external cost and privacy exposure to the subset that genuinely needs it. Lets AR-AST-008 evaluate two candidate engines against one corpus and choose on evidence rather than prediction. |
| **Disadvantages** | Two paths to build, test, and reason about. Confidence semantics differ between a deterministic text layer (effectively certain) and an assisted engine (probabilistic); the fusion rule must be explicit and must respect AR-AST-007 ("may lower a confidence, never raise it"). More configuration surface. |
| **Privacy implications** | Better than pure Option C, worse than pure Option B, and *variable per document* — itself a disclosure complication under NFR-PRIV-006, because the honest disclosure becomes "some documents are processed by a third party". |
| **Operational implications** | Moderate. Two code paths, one queue, one port. |
| **Scalability** | As for whichever engine is selected; the deterministic path removes load entirely for a subset of documents. |
| **Maintainability** | Best of the four *if* the routing rule is configuration rather than code. |
| **Replaceability** | Best of the four — a port with two implementations is the definition of replaceable, and it is exactly the pattern Sprint 3 already used for document storage. |
| **Requirement risks** | Complexity may outrun the sprint. The fusion of two confidence scales may produce a number that satisfies BR-001 syntactically but not meaningfully. |

## D-01.5 RECOMMENDATION — D-01

**RECOMMENDATION (not a requirement, and not to be read as one):**

1. **Adopt Option D in its narrow form** — one internal extraction port with (a) a deterministic path for documents carrying a usable embedded text layer, and (b) exactly one assisted implementation selected by configuration.
2. **Do not select the assisted engine in this register.** AR-AST-008 requires evaluation "before any threshold is set"; the same evidence should select the engine. Evaluate at least one self-hosted (Option B) and one external (Option C) candidate against the D-02 corpus, and record the outcome in Step 4 — System Architecture, per §6's Selection Principle.
3. **Make the port a first-class boundary**, mirroring `app/services/storage.py`. The specification's replaceability guarantee (§6) is only real if a substitution requires no change outside the port.
4. **Treat AR-AST-001 as an eligibility gate on the engine:** a candidate that cannot produce a per-field confidence with stable meaning is not eligible, however accurate it is.

**This recommendation is not an existing requirement.** The specification requires the guarantees in D-01.0; it does not require a hybrid, a port, or any particular engine.

**Owner:** Architecture (Step 4), with PM sign-off on the privacy posture if an external provider is chosen.
**Blocking status:** **BLOCKING** for FR-OCR-001 … 005. Not blocking for job, status, failure, and provenance work.

## D-01.6 NFR-PRIV-008 — does the specification exclude on-device processing?

**REQUIREMENT — what the text says:**

> **NFR-PRIV-008** (FUTURE, WON'T): "The system shall offer a mode in which processing occurs entirely on the user's device, with reduced capability."

> **§10.3, Explicitly not in the MVP:** "On-device-only processing mode and offline access — architecturally significant; deferred deliberately. NFR-PRIV-008, NFR-AVL-003."

> **§11, Horizon H5 (Trust maturity)** — unlocked when "the sensitivity boundary is settled by evidence (A-5) and interruption cost is measured" — lists "on-device processing mode" among its capabilities.

**Analysis.** Read precisely, NFR-PRIV-008 defers *a user-facing mode*: an option the user selects, in which processing is *entirely* on-device, and in exchange accepts *reduced capability*. Three things follow.

1. It does **not** say processing must occur off-device. It says DOCURA need not *offer the user the choice* of a fully-local mode in the MVP.
2. It does **not** address whether an individual processing step may run on the device as an implementation detail invisible to the user.
3. NFR-PRIV-006 ("Any processing performed outside the user's device shall be disclosed") presupposes that *some* processing is expected to occur off-device, but does not require it either. It is a disclosure duty conditional on a fact the specification never fixes.

**Conclusion: this is a REQUIREMENTS GAP, not an exclusion (G-01).** The specification nowhere states where MVP processing occurs. It defers a *mode* and imposes a *disclosure* — neither of which is a statement of baseline architecture.

**Practical consequence:** the gap is currently masked, because Sprint 3 as built and verified already performs server-side processing (validation, checksumming, storage). The MVP's de facto answer is "off-device", arrived at by implementation rather than by requirement.

**RECOMMENDATION:** amend `step3.pdf` to state the MVP processing location explicitly — as a new NFR-PRIV requirement, or as a clarifying note on NFR-PRIV-006 — so that the disclosure obligation has a defined subject.

**Owner:** Product Management.
**Blocking status:** **NOT BLOCKING** for implementation (the de facto answer is workable). **BLOCKING** for the wording of the NFR-PRIV-006 disclosure — see D-07.

---
# D-02 — Held-out document corpus (AR-AST-008)

| Field | Value |
| --- | --- |
| **G-02 status** | **APPROVED** — 3 September 2026 |
| Approved policy | [`SPRINT_4_G02_CORPUS_GOVERNANCE.md`](SPRINT_4_G02_CORPUS_GOVERNANCE.md) — the approved corpus governance policy for this project |
| What was approved | The fourteen proposed governance decisions G-02.1 … G-02.14 in that document |
| What was **not** approved | Nothing in `step3.pdf` changed. No unresolved requirement was filled. See D-02.6. |
| Evaluation plan | [`SPRINT_4_D02_OCR_EVALUATION_PLAN.md`](SPRINT_4_D02_OCR_EVALUATION_PLAN.md) — the evaluation method the corpus serves |

**The approval settles governance, not evidence.** D-02's blocking status is unchanged: the corpus does not exist, the evaluation has not run, and BR-001, the review threshold, and the §7.1 type set remain undetermined. What the approval removes is the governance obstacle to *starting* — entry gates E1–E7 of the evaluation plan. See D-02.5 for what is now binding and D-02.6 for what remains unresolved.

## D-02.1 REQUIREMENT — what the specification actually says

> **AR-AST-008** (MVP): "Assisted components shall be evaluated against a held-out corpus of real, imperfect documents before any threshold is set."

Four obligations are stated in that one sentence, and each is load-bearing:

| Obligation | Words that carry it | Consequence |
| --- | --- | --- |
| The corpus must be **held out** | "held-out" | It must not be the material used to build, tune, or prompt-engineer the extractor |
| The documents must be **real** | "real" | Synthetic or template-generated documents do not satisfy it |
| The documents must be **imperfect** | "imperfect" | A corpus of clean scans does not satisfy it |
| Evaluation must precede thresholds | "before any threshold is set" | BR-001 and the review threshold cannot be assigned first and validated later |

Supporting requirement text elsewhere in the specification:

- **§7.1**: "Final inclusion of each type is subject to the extraction evaluation in study S-6; a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only rather than shipped as unreliable." — *The corpus decides the MVP document-type set.*
- **BR-001**: "Threshold value: TBD — to be validated (study S-6)."
- **FR-OCR-012**: "MVP set: TBD — to be validated against a real document corpus (study S-6)."
- **ASM-001** (Appendix A): the MVP type set is an assumption, to be settled by "Study S-6 extraction evaluation on a real corpus."
- **§12.3 / A-7**: extraction reliability on real scans is untested and load-bearing for FR-OCR-004…006 and BR-001.
- **NFR-PRIV-002**: "A user's documents and extracted information shall not be used to train shared models, and shall not be readable by other users under any circumstance."

Document 02 (cited because §7.1, BR-001 and FR-OCR-012 name study S-6 by ID) describes S-6 as: *"Comprehension evaluation on real scans — n/a, technical — answers A-7 — output: accuracy baseline and confidence-threshold guidance."*

## D-02.2 What the specification does NOT say

The specification names the corpus obligation and nothing else about it. In particular it gives **no** corpus size, **no** acquisition method, **no** consent model, **no** retention or destruction rule, **no** access-control rule for the team, **no** definition of "imperfect", **no** per-type coverage minimum, **no** pass/fail criterion, and **no** owner.

**No corpus size is stated anywhere in `step3.pdf`, and none is proposed in this register.**

## D-02.3 Decision table

| # | Area | Status | What is open | Owner |
| --- | --- | --- | --- | --- |
| D-02.a | **Corpus ownership** | **PRODUCT DECISION — APPROVED** (G-02.4, G-02.11) | **Resolved.** A named Corpus Custodian owns the corpus and its lifecycle; a named Held-Out Custodian owns the held-out split. Authorisation for a second purpose is bound by the consent scope of G-02.2 — a new purpose requires new consent. *Original question:* who owns the corpus as an asset — the company, the study, or the individual contributors — and who may authorise its use for a second purpose (e.g. re-evaluating a new engine later). | PM + Legal |
| D-02.b | **Consent** | **PRODUCT DECISION — APPROVED** (G-02.2, G-02.3, G-02.10) | **Resolved.** Explicit, informed, purpose-bound, recorded, withdrawable opt-in consent with eight required elements, obtained before collection and unbundled from terms of service; separate lifecycle disclosure is mandatory. **Automatic ingestion of production/user-uploaded documents is prohibited.** The underlying **REQUIREMENTS GAP (G-02)** in `step3.pdf` is *not* closed — the policy is a project decision, not a specification amendment. *Original finding:* AR-AST-008 requires *real* documents. If they come from real people, consent is required; the specification contains no requirement covering the internal use of user documents for evaluation. NFR-PRIV-002 forbids training on user documents and forbids cross-user readability, but is silent on team evaluation access. A consent text, scope, and withdrawal path must be specified. | PM + Legal |
| D-02.c | **Privacy** | **PRODUCT DECISION — APPROVED** (G-02.4) | **Resolved for team access:** four roles under least privilege, named individuals, time- and purpose-bound, logged, revocable, with contributor identity withheld from Annotator and Evaluator roles. The **REQUIREMENTS GAP (G-02)** stands: whether NFR-PRIV-002 binds the team remains unstated in `step3.pdf`. *Original finding:* NFR-PRIV-002's "shall not be readable by other users under any circumstance" plainly binds users to users. Whether it binds the DOCURA team is not stated. An evaluation corpus is, by definition, readable by the team. This must be settled explicitly rather than by interpretation. | PM + Legal |
| D-02.d | **Acquisition** | **PRODUCT DECISION — APPROVED** (G-02.1) | **Resolved.** Contribution is limited to adults contributing their own documents through a dedicated process outside product signup. **The MVP minors limitation is in force** and is a stated limitation of the evaluation. Representativeness of whatever source is used must be stated in the report (G-02.14). *Original options:* volunteer donation, a paid panel, staff-and-family documents, or public-record documents. Each has a different consent and representativeness profile. Note document 02's own warning about S-1: "Any study that substitutes dummy data will produce a false positive on our riskiest assumption." | PM |
| D-02.e | **Retention** | **PRODUCT DECISION — APPROVED** (G-02.8) — **durations remain TBD** | **Lifecycle resolved:** seven stages with five destruction triggers (superseded, maximum period, withdrawal, abandonment, consent scope exhausted). **No duration was approved, because none was proposed** — every duration remains **TBD** pending product/privacy and legal input, and must not be invented. *Original finding:* NFR-PRIV-003 sets a deletion obligation for *user* documents with a period marked TBD. It does not cover a corpus held for evaluation. A retention period and its justification must be stated. | PM + Legal |
| D-02.f | **Destruction** | **PRODUCT DECISION — APPROVED in structure** (G-02.9) — **method BLOCKED** | **Resolved:** copies to be destroyed are enumerated (including ground truth and annotation working copies), a second person verifies, and a value-free destruction record is retained. **The destruction method remains BLOCKED by G-22 (key management absent), G-23 (encryption boundary undefined), and G-24 (crypto-erasure unaddressed)** and must not be specified until those close. *Original finding:* no destruction requirement exists for evaluation material. Needs: destruction trigger, method, verification, and evidence. | PM + Legal |
| D-02.g | **Development / evaluation separation** | **REQUIREMENT** (AR-AST-008 "held-out") + **PRODUCT DECISION — APPROVED** on mechanism (G-02.11, G-02.12) | **Mechanism resolved:** a named Held-Out Custodian who does not configure, tune, or select extraction; and six anti-leakage controls — separate access scope, sealed split fixed before any engine is installed, split by person, a real development set, single-run discipline, and logged and disclosed access. Where team size prevents the separation, that is a stated limitation, not a dropped control. *Original finding:* the requirement is stated; the mechanism is not. Open: whether a separate development set is also collected, who may see the held-out set, and how leakage is prevented and evidenced. | Engineering + PM |
| D-02.h | **Document-type coverage** | **DECISION REQUIRED**, dependent on D-04 | §7.1 makes inclusion of each candidate type conditional on this evaluation, so every candidate type must appear — but the specification gives no per-type minimum. Types with no defined fields (D-05) cannot be evaluated for extraction at all, only for classification. | PM + Engineering |
| D-02.i | **Imperfect scans** | **REQUIREMENT** (AR-AST-008 "imperfect") + **DECISION REQUIRED** on definition | EC-002 gives the behavioural anchor: "Poor-quality document — extract what is legible, mark low-confidence fields for review". "Imperfect" is not defined: skew, glare, shadow, low DPI, phone photographs, photocopies of photocopies, cropped edges, stamps and overprints, mixed orientation. The taxonomy is a decision. | Engineering proposes, PM approves |
| D-02.j | **Multi-page documents** | **REQUIREMENT** (FR-OCR-008: "shall process multi-page documents as a single document"; AC-US-003-4 uses a five-page example) | The corpus must contain multi-page documents, including ones where a field appears on a later page. Count and page-depth are open. | Engineering + PM |
| D-02.k | **Low-quality documents** | See D-02.i | Distinguish "low quality but legible" (EC-002 — extract, mark for review) from "not legible at all" (EC-001 — fail honestly). The corpus must contain both, because they exercise different requirements. | Engineering |
| D-02.l | **Failure cases** | **REQUIREMENT** (FR-OCR-009, EC-001) | The corpus must include documents on which extraction is *expected* to fail, so that the retain-original / state-the-reason / offer-retry-and-manual-entry path is evaluated, not just the happy path. | Engineering |
| D-02.m | **Conflicting documents** | **REQUIREMENT** (FR-INF-004, EC-004, AC-US-005-1) | Conflict detection is deterministic (AR-DET-008), but it can only be evaluated if the corpus contains document *sets* per person where two documents disagree on the same attribute — e.g. a name spelled differently on two certificates (pain P-06). This is a corpus-*structure* requirement: documents must be grouped by person, not pooled. | Engineering + PM |
| D-02.n | **Unclassified documents** | **REQUIREMENT** (FR-OCR-002 "or as unrecognised"; AC-US-003-3; EC-003; §7.1 "Other") | The corpus must contain out-of-set documents, so that the classifier's ability to decline is measured. A classifier that never returns "unrecognised" would pass an in-set-only evaluation and violate AR-AST-002 in production. | Engineering |
| D-02.o | **Evaluation evidence** | **PRODUCT DECISION — APPROVED in part** (G-02.13) — **reviewer and pass criterion still DECISION REQUIRED** | **Resolved:** what evidence may outlive the corpus is now defined — aggregates, provenance, manifest, access log, destruction record — with document content, extracted values, ground-truth values, and illustrative examples excluded. This is what makes a bounded retention period survivable. **Still open:** who reviews and signs the report, where it is retained, and what a passing result is (the last belongs to D-03 and §7.1, not to G-02). | PM + Engineering |
| D-02.p | **Re-evaluation trigger** | **REQUIREMENTS GAP (G-03)** | AR-AST-008 is silent on what happens when the assisted component changes (a new engine version, a new provider model). Thresholds calibrated against engine v1 are not evidence for engine v2. | PM |

## D-02.4 RECOMMENDATION — D-02

1. **Treat the corpus as a product deliverable with a named owner**, not as a testing task. It gates §7.1, BR-001, D-03, D-04, and D-05 simultaneously.
2. **Group corpus documents by synthetic person**, not as a flat pool — otherwise FR-INF-004 conflict detection cannot be evaluated at all (D-02.m).
3. **Define "pass" per document type before running the evaluation**, so §7.1's "moved to store-and-search only" rule can be applied on evidence rather than on argument after the fact.
4. **Record the evaluation as a versioned artefact** naming engine, engine version, corpus version, date, and per-type results — because D-02.p means it will need to be repeated.
5. **Do not size the corpus in this register.** The specification gives no number; a number invented here would acquire false authority.

**Blocking status:** **BLOCKING — EVALUATION REQUIRED** for BR-001, the review threshold, the final MVP type set (§7.1), and FR-OCR-004/005/006 under §12.3. *Unchanged by the G-02 approval — see D-02.5.*

## D-02.5 PRODUCT DECISION — APPROVED — corpus governance (G-02)

**Approved 3 September 2026.** The proposed governance decisions G-02.1 … G-02.14 in [`SPRINT_4_G02_CORPUS_GOVERNANCE.md`](SPRINT_4_G02_CORPUS_GOVERNANCE.md) are approved as product/privacy decisions for this project. That document is the authority on their detail; this entry records the decision and its boundaries.

### What is now binding

| # | Approved decision | Register reference |
| --- | --- | --- |
| 1 | **Automatic ingestion of production/user-uploaded documents into the evaluation corpus is prohibited.** A user document may enter the corpus only through a separate affirmative opt-in act that is not a precondition for any product function. | D-02.b |
| 2 | **Evaluation-corpus contribution requires explicit opt-in consent** — informed, purpose-bound, recorded, withdrawable, unbundled from terms of service, obtained before collection — **with separate lifecycle disclosure**: the contributor is told that a corpus copy has its own retention and destruction schedule, distinct from any DOCURA vault copy. | D-02.b |
| 3 | **Contribution is limited to adults contributing their own documents.** **The MVP minors limitation remains in force**, and the resulting narrowing of the corpus is a stated limitation of the evaluation, not a silent one. | D-02.d |
| 4 | **Corpus access follows the approved governance document** — four roles under least privilege, named individuals, time- and purpose-bound access with no standing access, append-only value-free access logging, no bulk export, contributor identity withheld from Annotator and Evaluator roles. | D-02.c |
| 5 | **Corpus storage and isolation follow the approved governance document** — a single designated corpus store inside DOCURA's trust boundary, **mandatorily isolated from production document storage**, with the evaluation harness holding no production storage credentials. | D-02.e, D-10 |
| 6 | **Held-out controls follow the approved governance document** — a named Held-Out Custodian who does not configure, tune, or select extraction, and the six anti-leakage controls of G-02.12. | D-02.g |
| 7 | **Retention operates as a defined lifecycle with destruction triggers**, and **all durations remain TBD**. | D-02.e |
| 8 | **Document images are not redacted**, because redaction would invalidate the evaluation AR-AST-008 requires; minimization applies to contributor identity, manifests, logs, and reports instead. | D-02.f, D-06 |
| 9 | **Synthetic documents may never substitute for the real held-out evaluation.** They are permitted for harness development and the development set only, with an immutable real/synthetic marker and no blended figures. | D-02.d |

### What the approval does **not** do

1. **It does not amend `step3.pdf`.** Per §0.2 and the §11 Containment Rule, a specification change requires a new version number. The approved policy is a project decision that sits *beside* the specification.
2. **It does not close REQUIREMENTS GAP G-02.** The specification still contains no requirement governing an evaluation corpus. The gap remains open in §Gap inventory, and closing it requires the amendment recorded there.
3. **It does not unblock D-02.** The corpus does not exist, the evaluation has not run, and BR-001, the review threshold, and the §7.1 type set remain undetermined. The approval removes the *governance* obstacle to starting — entry gates E1–E7 of the evaluation plan — and nothing else.
4. **It does not resolve D-02.h, D-02.i, D-02.j, or D-02.p**, which are corpus-composition and re-evaluation questions, not governance questions.

## D-02.6 Dependencies that remain unresolved

**These must not be silently converted into implementation requirements.** Each is recorded here because the approval deliberately left it open.

| Dependency | Status | Effect |
| --- | --- | --- |
| **Corpus storage encryption** | **REQUIREMENTS GAP — G-21** | "Encrypted at rest" has no threat model in `step3.pdf`. The corpus encryption standard cannot be specified by citing NFR-SEC-002. |
| **Key management** | **REQUIREMENTS GAP — G-22** | Entirely absent from the specification. No key policy may be inherited or invented. |
| **Encryption / custody boundary** | **REQUIREMENTS GAP — G-23** | Backups, replicas, logs, temporary artefacts, and external processor custody are undefined — and an evaluation run creates all of them. |
| **Destruction method** | **BLOCKED by G-22, G-23, G-24** | The structure is approved (D-02.f); the method is not, and must not be specified until these close. |
| **Derived-artefact redaction scope** | **BLOCKED by G-12** | With no field definitions for any document type, what the product will never extract is not yet determinable. The interim rule is the approved G-02.7; scope is revisited when G-12 closes. |
| **Security-event recording** | **REQUIREMENTS GAP — G-26** | Corpus access logging is an approved *project control*, not an inherited requirement. Its product-wide counterpart remains a gap. |
| **Re-evaluation trigger** | **REQUIREMENTS GAP — G-03** | D-02.p. Determines whether re-evaluation reuses the corpus, which in turn fixes the consent scope of G-02.2. |
| **Sensitivity classification rules** | **REQUIREMENTS GAP — G-14, G-15, G-16** | Protection cannot be graduated by sensitivity, which is why the approved policy protects the whole corpus at the highest level available. |
| **Retention durations** | **TBD** | No duration was proposed and none was approved. |
| **Consent-record retention period** | **TBD** | Legal input required. |
| **Report reviewer, signer, and retention location** | **DECISION REQUIRED** | D-02.o. |

**Amendments that should follow, per the approved document's own §15.3:** raising evaluation-corpus governance (G-02), the re-evaluation trigger (G-03), security-event recording (G-26), and the definition of the artefact that proves AR-AST-008 was met (D-02.o) as specification amendments. Until then, the gaps stand as gaps.

---

# D-03 — Confidence model and thresholds

## D-03.1 REQUIREMENT — what is explicitly defined

| ID | Requirement | Kind |
| --- | --- | --- |
| FR-OCR-003 | "The system shall record a confidence value for the classification." | Document-level confidence — MUST |
| FR-OCR-005 | "The system shall record a confidence value for every extracted field **independently of the document-level confidence**." | Field-level confidence — MUST |
| FR-OCR-006 | "Extracted fields below the review threshold shall be marked as needing user review and shall not be used for automatic filling." | Review threshold — MUST |
| FR-INF-002 | "Every attribute value shall reference the document it came from and the confidence with which it was read." | Confidence travels with the attribute, not only with the extraction — MUST |
| BR-001 | "An action may be taken automatically only when the confidence of **both** the field interpretation **and** the source value meets or exceeds the automatic-action threshold. Threshold value: TBD — to be validated (study S-6)." | Automatic-action threshold — non-configurable rule, TBD value |
| BR-002 | "Information extracted below the review threshold is never used for automatic action, regardless of how well it matches a field." | Confidence floor |
| AR-DET-004 | "Threshold comparison and the act-or-ask decision shall be deterministic given a confidence value." | The comparison is deterministic — MVP |
| AR-AST-007 | "No assisted component shall be permitted to escalate its own authority — it may lower a confidence, never raise it, and may add a sensitivity classification, never remove one." | Monotonicity — MVP |
| AR-AST-008 | "…evaluated against a held-out corpus… **before any threshold is set**." | Ordering constraint — MVP |
| NFR-MNT-002 | "Confidence thresholds shall be externally configurable and changeable without a code release." | Configuration, not constants — MUST |
| NFR-OBS-001 | "The system shall measure extraction and field-interpretation confidence distributions in aggregate, without retaining the underlying values." | Observability — MUST |
| AC-US-003-2 | "…every extracted field is shown with its own confidence indication." | Field confidence is user-visible |
| AC-US-004-4 | "GIVEN an extracted value below the review threshold, WHEN the record is used for filling, THEN that value is never placed automatically." | The withholding behaviour is testable without the number |

**Two distinct thresholds exist in the specification**: the **review threshold** (BR-002, FR-OCR-006) and the **automatic-action threshold** (BR-001). They are named separately and used for different purposes.

## D-03.2 What is missing

| # | Gap | Detail |
| --- | --- | --- |
| G-04 | **Numeric values** | Both thresholds are undefined. BR-001 is explicitly "TBD — to be validated (study S-6)". The review threshold carries no TBD marker anywhere, yet no value is given — it is simply undefined. **No number is proposed in this register.** |
| G-05 | **Relationship between the two thresholds** | The specification never states whether the review threshold is below, equal to, or independent of the automatic-action threshold. The logic of BR-002 ("never used for automatic action") implies review ≤ automatic, but implication is not specification. |
| G-06 | **Confidence semantics and scale** | Nothing states what a confidence value *is*: its range, whether it is a probability, whether values from the classifier and from field extraction are on the same scale, or whether values from two different engines are comparable. AR-AST-001 requires it to be "usable by BR-001", which presumes a stable meaning the specification never defines. |
| G-07 | **Global or per-document-type thresholds** | Not addressed. §7.1's rule ("a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only") reads most naturally as a single global review threshold applied per type — but it does not say so. |
| — | **Interaction of document-level and field-level confidence** | FR-OCR-005 makes them independent. Nothing states whether a low *classification* confidence should suppress or discount field values extracted under that classification. Not specified. |
| — | **Missing-value semantics** | Nothing states what confidence attaches to a field the extractor did not find, or whether "absent" and "found with low confidence" are distinguishable. FR-AMB-001 treats "the required information is absent" as a separate ambiguity condition from low confidence, which suggests they must be distinguishable — but that is inference from a Sprint-5 requirement. |

## D-03.3 What can be implemented structurally now

These follow from requirements that do not depend on the numbers:

- Persist a **classification confidence** (FR-OCR-003) and a **per-field confidence** (FR-OCR-005) as separate values.
- Carry confidence onto the attribute together with its source document (FR-INF-002).
- Implement threshold comparison as a **deterministic, single-place function** (AR-DET-004) that reads its values from configuration (NFR-MNT-002) — not from constants, and not from the database schema.
- Implement the **needs-review marking** and the withholding behaviour (FR-OCR-006, BR-002), which is testable at the threshold without knowing the number, exactly as §4's preamble describes: "the criterion tests the behaviour at the threshold rather than the number itself."
- Enforce **monotonicity** (AR-AST-007): any post-processing step may only lower a confidence. This is a structural invariant, best enforced at the write boundary so that no later component can raise a stored value.
- Emit **aggregate confidence distributions** without underlying values (NFR-OBS-001).

## D-03.4 What requires evaluation

- Both threshold values (BR-001, FR-OCR-006), per AR-AST-008 and study S-6.
- Whether a single global threshold is defensible across all types, or whether per-type thresholds are needed — a question only the corpus results can answer.
- Whether the chosen engine's confidence is calibrated enough for a threshold to mean anything (AR-AST-001).

## D-03.5 What requires a product decision

- **Global vs per-document-type thresholds (G-07).** This is a product decision informed by evaluation, not a pure engineering choice: per-type thresholds mean the same nominal confidence produces different behaviour for an Aadhaar than for a marksheet, which is defensible but must be a deliberate choice. **RECOMMENDATION:** design the configuration to permit a per-type override over a global default, so the decision can be *deferred* without a schema or code change (this satisfies NFR-MNT-002 either way); but do not populate any per-type value until evaluation justifies it.
- **What the user is shown.** AC-US-003-2 requires "its own confidence indication" — whether that is a number, a band, or a flag is not specified. **PRODUCT DECISION**, and one with a trust dimension: an unexplained "0.71" invites false precision.
- **Behaviour when confidence is absent entirely** (engine returns no confidence for a field). BR-016 ("fail towards inaction") and BR-009 point to treating it as below threshold. **RECOMMENDATION:** treat missing confidence as below every threshold. Not currently a requirement.

## D-03.6 How evaluation should inform threshold selection

**RECOMMENDATION (not a requirement):** the evaluation should produce, per document type and per field, the distribution of confidence values against ground-truth correctness, so that a threshold can be chosen by its *consequence* — the rate at which a wrong value would be placed automatically — rather than by its appearance. §12.3's failure mode for A-7 ("thresholds may exclude most automatic action") is a legitimate outcome to discover, and BR-002 plus BR-016 mean the correct response to a poor distribution is a *higher* threshold and more asking, never a lower one to preserve a demo.

**Blocking status:** **BLOCKED — EVALUATION REQUIRED** for the values; **READY** for the structure.

---

# D-04 — Document types

## D-04.1 REQUIREMENT — exactly what §7.1 says

> **§7.1 Supported document types — MVP**
>
> "The MVP supports a defined set of types. Any document outside the set is still stored and searchable, but its information is not extracted into the structured record. The set is deliberately narrow so that extraction quality can be evaluated honestly before it is widened.
>
> Final inclusion of each type is subject to the extraction evaluation in study S-6; a type whose extraction cannot meet the review threshold on real documents shall be moved to store-and-search only rather than shipped as unreliable.
>
> - Identity and address — Aadhaar, PAN, address proof.
> - Education — 10th marksheet, 12th marksheet, semester result, degree certificate.
> - Application assets — photograph, signature, student ID, hall ticket, resume.
> - Other — stored and searchable as an unclassified document, no structured extraction. **ASM-001**"

Related requirements: FR-OCR-002 (classify into a supported type "or as unrecognised"); AR-AST-002 (must be able to return "unrecognised" rather than a forced choice); FR-DOC-002 ("Each document shall carry a document type, assigned automatically and correctable by the user"); EC-003 ("If the type is clear, store it as that type. If unclear, store as unclassified and ask. Never force it into an expected slot"); AC-US-003-3 (unclassified, user asked to identify, "no type is assumed"); ASM-001 (the type set is an assumption settled by S-6); NFR-USE-005 ("Product language shall name things as users do — 'marksheet', 'photograph', 'declaration' — not as the system models them").

## D-04.2 Classification of the twelve candidate types

| Type | Group | Named in §7.1 | Status per the specification |
| --- | --- | --- | --- |
| Aadhaar | Identity and address | Yes | **Provisional** — inclusion conditional on S-6 |
| PAN | Identity and address | Yes | **Provisional** — conditional on S-6 |
| Address proof | Identity and address | Yes | **Provisional**, and additionally **UNRESOLVED AS A DEFINITION** — see D-04.4 |
| 10th marksheet | Education | Yes | **Provisional** — conditional on S-6 |
| 12th marksheet | Education | Yes | **Provisional** — conditional on S-6 |
| Semester result | Education | Yes | **Provisional**, and **NAME UNRESOLVED** — see D-04.5 |
| Degree certificate | Education | Yes | **Provisional** — conditional on S-6 |
| Photograph | Application assets | Yes | **Provisional**, and **EXTRACTION SCOPE UNDEFINED** — see D-04.6 |
| Signature | Application assets | Yes | **Provisional**, and **EXTRACTION SCOPE UNDEFINED** — see D-04.6 |
| Student ID | Application assets | Yes | **Provisional** — conditional on S-6 |
| Hall ticket | Application assets | Yes | **Provisional** — conditional on S-6 |
| Resume | Application assets | Yes | **Provisional** — conditional on S-6, and see D-04.7 |
| *Other / unclassified* | Other | Yes | **Explicitly supported as a storage state** — store and search, no structured extraction. This is the one entry §7.1 states unconditionally. |

**There are no "explicitly supported" extraction types in the specification.** Every one of the twelve is conditional on S-6 by the plain text of §7.1 and by ASM-001. The only unconditional entry is the *unclassified* fallback. This is the single most important finding of D-04, and it is why the register does not present an MVP type set.

## D-04.3 Types requiring evaluation

All twelve, per §7.1 and ASM-001. Two distinct evaluation questions apply to each, and the specification distinguishes them:

1. **Can it be classified?** (FR-OCR-002, FR-OCR-003, AR-AST-002.)
2. **Can its fields be extracted at or above the review threshold?** (§7.1's demotion rule, FR-OCR-004/005.)

A type may pass (1) and fail (2). §7.1's remedy for that case is explicit: "moved to store-and-search only rather than shipped as unreliable" — which is a *different state* from *unclassified*, because the document still has a known type. **The specification does not define this third state in the data model or in FR-DOC-002.** Registered as **G-08**.

## D-04.4 Unresolved type definitions

| Type | What is unresolved |
| --- | --- |
| **Address proof** | Not a document; a *category* of documents (utility bill, bank statement, rent agreement, passport, ration card, …). The specification never enumerates what qualifies. A classifier cannot be built against an undefined class, and FR-OCR-004 cannot define "the defined set of information fields" for a class whose members have different layouts. **REQUIREMENTS GAP (G-09).** |
| **Student ID** | Institution-specific with no common layout. Whether the MVP targets any student ID or a bounded set is unstated. **DECISION REQUIRED.** |
| **Hall ticket** | Examination-body-specific and, in practice, single-use and time-bound. Whether it is an extraction target or an attachment-only asset is unstated. **DECISION REQUIRED.** |
| **Semester result** | See D-04.5. |
| **Photograph / signature** | See D-04.6. |
| **Resume** | See D-04.7. |
| **Aadhaar / PAN** | The types themselves are unambiguous; their *field sets* are not defined (D-05), and their sensitivity tier is not fixed in `step3.pdf` (D-06). |

## D-04.5 "Semester result" vs "semester marksheet" — equivalent or unresolved?

The specification uses two different names:

- **§7.1** lists the type as **"semester result"**.
- **AC-US-003-1** reads: "GIVEN the user has uploaded a **semester marksheet**, WHEN DOCURA processes it successfully, THEN the document appears in the vault classified as **a marksheet** with its extracted information attached."
- **NFR-USE-005** requires product language to "name things as users do — 'marksheet', 'photograph', 'declaration' — not as the system models them."

**Finding: UNRESOLVED (G-10).** Three readings are possible and the specification does not choose between them: (a) they are the same type under two names; (b) "semester result" is a distinct type from the 10th/12th marksheets; (c) "marksheet" in AC-US-003-1 is a *family* covering 10th, 12th, and semester documents, and the acceptance criterion is testing family-level classification.

The distinction is not cosmetic. Under reading (c), classifying a semester document as "10th marksheet" would still pass AC-US-003-1 — which would make the criterion weaker than it appears. Under readings (a) and (b) it would fail. **This must be resolved before the acceptance criterion can be turned into a test**, and NFR-USE-005 means the user-facing name should be settled at the same time.

**Owner:** Product Management. **Blocking status:** **BLOCKING** for D-12's mapping of AC-US-003-1 and for the type vocabulary.

## D-04.6 Do photograph and signature have structured information requirements?

**What the specification says:** §7.1 lists both under "Application assets" and states, of the *set* as a whole, that supported types have their information extracted. It says nothing about what information a photograph or a signature contains.

**What can be observed from the rest of the specification:**
- FR-MATCH-006 requires constraint-compliant *copies* (format, size, dimensions) — a photograph's product value is as an attachment, which is deterministic work (AR-DET-002), not extraction.
- FR-INF-007 requires *every attribute* to carry a sensitivity classification — which only bites if these types produce attributes at all.
- Document 02's Table 13.1 (cited by FR-INF-007 and FR-SENS-001 by ID) lists "signature images" among its *sensitive* examples — a signature is treated as sensitive material, not as a source of text.

**Finding: REQUIREMENTS GAP (G-11).** The specification does not state whether photograph and signature are extraction targets (with a defined field set under FR-OCR-004) or classification-and-attachment-only assets. Both readings are consistent with §7.1.

**RECOMMENDATION (not a requirement):** treat photograph and signature as **classified but non-extracting** types — they are classified (FR-OCR-002), carry metadata, and participate in document matching, but define no information fields under FR-OCR-004. This is the reading most consistent with BR-009 and with §6.1's rule against using probabilistic methods where nothing needs interpreting. **It requires PM approval; it is not what the specification says today.**

## D-04.7 Resume

A resume is user-authored, free-form, and unbounded in layout. Extracting "the defined set of information fields" (FR-OCR-004) from it is a materially different problem from extracting from a structured certificate, and the specification does not acknowledge the difference. **DECISION REQUIRED:** is resume an extraction type, or a store-and-search type? Note that §7.1's demotion rule already provides the mechanism if evaluation says the latter.

## D-04.8 What is NOT being decided here

**This register does not finalise the MVP document-type set.** §7.1 makes that determination the output of study S-6, and ASM-001 records it as an open assumption. Any list of "the MVP types" produced before that evaluation would be an invention with the appearance of a requirement.

**Blocking status:** **BLOCKED — EVALUATION REQUIRED** for the final set; **BLOCKED — REQUIREMENTS GAP** for address proof (G-09), the semester naming (G-10), photograph/signature scope (G-11), and the store-and-search-only state (G-08).

---
# D-05 — Field definitions (FR-OCR-004)

## D-05.1 REQUIREMENT — the obligation

> **FR-OCR-004** (MVP, MUST, trace L2): "For each supported document type, the system shall extract **the defined set of information fields** for that type."

The requirement is written as though the field sets are defined elsewhere. Two other requirements depend on their existence:

- **NFR-MNT-001** (MUST): "Supported document types and their extractable fields shall be definable as configuration, so adding a type does not require re-engineering." — *the field sets are configuration, so the specification is right not to embed them in code; but configuration still has to be authored by someone.*
- **FR-INF-001** (MUST): "The system shall maintain a structured record of the user's personal information, assembled from all processed documents."

## D-05.2 Finding

**A complete search of `backend/step3.pdf` finds no field definition for any document type.** The specification defines the *obligation* to extract a defined field set and the *mechanism* by which field sets are maintained (configuration), but never states the sets themselves, and never points to a document that does. §7.1 lists type names only.

The nearest field-like nouns anywhere in the specification are:
- **FR-INF-008**: "dates, casing, spacing, and numeric precision" — these are normalisation *categories*, not fields.
- **P-06 "Detail mismatch"** and §13.1 — a name mismatch between documents is named as a pain, which implies a name attribute exists, but does not define one.
- **EC-019** — "the same attribute is requested twice in one form" — implies attribute identity, does not define attributes.
- Document 02's Table 13.1 lists "Name, date of birth, education history, marks, addresses" and "Government identifier numbers, bank details, signature images, category and income details" — but that table is an explicitly **ASM**-tagged *working sensitivity classification for research purposes*, tied to untested assumption A-5. **It is a list of sensitivity examples, not a field definition, and must not be promoted into one.**

**No fields are invented in this register.**

## D-05.3 Field-definition table

| Document type | Fields explicitly defined by the specification | Fields missing | Decision required | Blocking status |
| --- | --- | --- | --- | --- |
| Aadhaar | **None** | The entire set | Which fields; which are mandatory vs optional; format and normalisation rule per field; sensitivity tier per field (D-06); whether the identifier number is stored at all, masked, or stored in part | **BLOCKING** — FR-OCR-004 cannot be implemented for this type |
| PAN | **None** | The entire set | As above | **BLOCKING** |
| Address proof | **None** | The entire set — and the class itself is undefined (G-09) | What documents qualify as address proof, before any field can be defined | **BLOCKING** (doubly) |
| 10th marksheet | **None** | The entire set | Which fields; how per-subject marks are represented (repeating group vs flat fields); whether aggregate/percentage is extracted or derived | **BLOCKING** |
| 12th marksheet | **None** | The entire set | As above | **BLOCKING** |
| Semester result | **None** | The entire set — and the type name is unresolved (G-10) | Naming first, then fields | **BLOCKING** |
| Degree certificate | **None** | The entire set | Which fields; how degree/major/class are represented | **BLOCKING** |
| Photograph | **None** | Unknown — the specification does not say whether any exist (G-11) | Whether this type extracts at all (D-04.6) | **BLOCKING** until D-04.6 is answered |
| Signature | **None** | Unknown (G-11) | Whether this type extracts at all (D-04.6) | **BLOCKING** until D-04.6 is answered |
| Student ID | **None** | The entire set | Whether a bounded institution set is targeted (D-04.4) | **BLOCKING** |
| Hall ticket | **None** | The entire set | Whether it is an extraction type at all (D-04.4) | **BLOCKING** |
| Resume | **None** | The entire set | Whether it is an extraction type at all (D-04.7) | **BLOCKING** |
| Unclassified / Other | **N/A — §7.1 states no structured extraction** | None | None | **READY** — this is the one type whose extraction behaviour is fully specified: none |

**Summary: FR-OCR-004 is unimplementable as written, for every type, until field definitions are authored and approved.** This is not a difficulty of engineering; it is an absence in the requirements. Registered as **G-12 — the single largest gap in the Sprint 4 requirement set.**

## D-05.4 The canonical attribute vocabulary

Several requirements presuppose a **shared vocabulary of attributes**, independent of any one document, without which they cannot function:

| Requirement | Why it needs a canonical vocabulary |
| --- | --- |
| **FR-INF-001** — "a structured record of the user's personal information, assembled from all processed documents" | "Assembled from all documents" requires knowing that a field on document A and a field on document B are the *same* attribute |
| **FR-INF-004** — "detect when two documents give different values for the same attribute" | Conflict detection is impossible without attribute identity. This is the hard dependency. |
| **FR-INF-007** — "Every attribute shall carry a sensitivity classification" | Tiers are assigned to attributes, so attributes must be enumerable |
| **FR-INF-008** — deterministic normalisation of "dates, casing, spacing, and numeric precision" | Normalisation rules are per-attribute-type; "compare after normalising" presupposes knowing which normaliser applies |
| **FR-ACC-004** — "a user profile of **canonical personal attributes** derived from documents" | The word *canonical* appears here and nowhere else; the specification names the concept without defining its contents |
| **FR-SRCH-003** — "search by attribute value" | Requires addressable attributes |
| **EC-019** — the same attribute requested twice in one form | Requires attribute identity across form fields |

**Finding: the canonical attribute vocabulary does not exist in the specification (G-13).** FR-ACC-004 names it — "canonical personal attributes" — and no section enumerates it. **No vocabulary is proposed here.**

**Consequence:** FR-INF-004 (conflict detection, MUST) and FR-INF-005/006 are blocked on the same gap as FR-OCR-004, and so is US-005 in full. The mapping from a document's fields to canonical attributes is a *second* artefact beyond the per-type field sets, and the specification defines neither.

*The **shape** of that artefact has since been settled by an approved product decision — see **D-05.6**. The finding above is unchanged: the specification still enumerates no attribute, and the vocabulary's contents still do not exist.*

## D-05.5 RECOMMENDATION — D-05

1. **Author two artefacts, in this order:** (i) the canonical attribute vocabulary (attribute name, meaning, value type, normalisation rule, sensitivity tier); (ii) per-type field sets, each field mapping to one canonical attribute or explicitly to none.
2. **Hold both as configuration**, as NFR-MNT-001 requires, and treat the vocabulary as a reviewed, versioned artefact — because FR-INF-007 sensitivity tiers and FR-INF-008 normalisation rules attach to it, and NFR-MNT-004 requires sensitivity rules to be "a reviewable list, not scattered through the implementation".
3. **Do not derive the vocabulary from whatever the chosen engine happens to return.** That would invert §6's Selection Principle and make replacing the engine a data migration.
4. **PM owns the content; engineering owns the format.** These are product artefacts that determine what DOCURA knows about a person.

**Blocking status:** **BLOCKED — REQUIREMENTS GAP** (G-12, G-13). Blocks FR-OCR-004, FR-OCR-005 in substance, FR-INF-001, FR-INF-004, FR-INF-005, FR-INF-006, FR-INF-008, and US-005 entirely. *Unchanged by the G-13 approval — see D-05.6.*

## D-05.6 PRODUCT DECISION — APPROVED — canonical attribute vocabulary (G-13)

> **REVISION APPROVED — 6 September 2026 (D-05.8).** Three of the fourteen approved decisions below were **revised and the revisions are now approved**: **G-13.2** (item 2), **G-13.5** (item 5), **G-13.9** (item 9). A new **G-13.15** is **approved** (item 14). **Item 11**'s decision wording is unchanged; its **trigger** is clarified to **G-13-A** and that clarification is approved. **G-13.3 (item 3) is NOT reopened**, and **no eighth property is added**. See **D-05.8** for the revision record and [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) for its derivation. Items 1, 3, 4, 6, 7, 8, 10, 12, 13 stand exactly as approved. **Approving all of this closes no gap: REQUIREMENTS GAP G-13 remains OPEN in §4.**

**Approved 5 September 2026.** The proposed decisions G-13.1 … G-13.14 in [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) are approved as product decisions for this project. That document is the authority on their detail; this entry records the decision and its boundaries.

**G-13 status: APPROVED.** The approved canonical attribute vocabulary definition is documented in `backend/docs/SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`.

### What is now binding

| # | Approved decision | Register reference |
| --- | --- | --- |
| 1 | **The canonical attribute vocabulary is a single reviewed, versioned artefact owned by Product Management and held as configuration.** Recorded explicitly: **NFR-MNT-001 names "types and their extractable fields" and does not name attributes**, so this decision is a new product decision rather than an application of that requirement. *This supersedes the citation in D-05.5 item 2, which attributed the vocabulary's configuration home to NFR-MNT-001.* | D-05.4, D-05.5 |
| 2 | **The minimum canonical attribute definition contains exactly seven properties: identifier, display label, semantic definition, data type, normalisation rule, multiplicity, sensitivity tier slot.** Two are existing requirements — the normalisation rule (FR-INF-008, "normalise attribute formats") and the sensitivity tier slot (FR-INF-007, "every attribute shall carry"). Five are new product decisions. **REVISED AND THE REVISION APPROVED 6 Sep 2026:** the multiplicity property is redefined from `single \| repeating` to a **scope-keyed cardinality** — how many values, and per what subject. **The count remains seven and no eighth property is added**; the "exactly these seven, and no others" clause is retained. See D-05.8. | D-05.4, D-06, **D-05.8** |
| 3 | **"The same attribute" (FR-INF-004) means: two values map to the same canonical attribute identifier.** Identity is established by the field-to-attribute mapping alone — never by label similarity, value similarity, or position. Grounded in AR-DET-008 (detection must be deterministic), BR-009, BR-004, AR-AST-007. | D-05.4, D-12.3 |
| 4 | **Attribute identifiers are stable and never reused.** A display-label change does not change the identifier; a meaning change requires a new identifier. | D-05.4 |
| 5 | **Per-attribute normalisation rules are vocabulary content, and the normalised form is the comparison function for FR-INF-004.** A change to any normalisation rule is a change to conflict-detection behaviour: it requires re-approval and invalidates prior evaluation evidence for the affected attributes. **REVISED AND THE REVISION APPROVED 6 Sep 2026:** the comparison function operates **within a scope instance** — two values are compared only where they share both the canonical attribute identifier **and** the scope instance — and the re-approval consequence extends to scope rules. See D-05.8. | D-03, D-08.4, G-03, **D-05.8** |
| 6 | **The raw extracted value is retained alongside its normalised form**, as the minimum way to satisfy AR-DET-003's "deterministic and **reversible**". | D-08.1 |
| 7 | **An extracted value that maps to no canonical attribute is never coerced into the nearest-looking attribute and does not enter the structured record as one.** Its destination remains undecided. | See D-05.7 |
| 8 | **The vocabulary is authored and approved before the per-type field sets, and no entry may be created by engineering or derived from an engine's output** (§6 Selection Principle). Confirms the D-05.5 ordering. | D-05.5, D-01 |
| 9 | **Every attribute carries a sensitivity tier slot and none may be published without a tier.** The rules that populate it and the default tier remain delegated to G-14 and G-15. **REVISED AND THE NARROWING APPROVED 6 Sep 2026:** the bar is narrowed to **release** — no attribute reaches implementation, stored production data, or any surface that discloses or fills a value without an assigned tier, while a version may be approved **structurally** with tier slots present and TBD and marked **NOT RELEASABLE**. Closure splits into **G-13-A** (structural) and **G-13-B** (releasable). **G-14 and G-15 are not resolved by the revision.** See D-05.8. | D-06, **D-05.8** |
| 10 | **The vocabulary is versioned, and every evaluation run and stored attribute value records the version it was produced under.** | D-02.4, G-03 |
| 11 | **No placeholder, illustrative, or temporary attribute may enter code, configuration, schema, migrations, test fixtures, or evaluation tooling until the vocabulary's contents exist** (BR-009; §11 Containment Rule). **TRIGGER CLARIFIED AND THE CLARIFICATION APPROVED 6 Sep 2026:** “until the contents exist” means **until G-13-A**; approved gate-A content is not a placeholder within this decision's meaning, while entry into production code, schema, migrations and stored production data stays barred until **G-13-B**. The decision's wording is unchanged and nothing is permitted before G-13-A. | D-08, **D-05.8** |
| 12 | **The vocabulary is authored to the minimum that serves a requirement which consumes it**, each attribute justifiable against a named requirement (BR-017, NFR-PRIV-001). | D-11 |
| 13 | **Stage-1 evaluation — OCR text quality, classification, failure behaviour, engine eligibility, and normalisation *determinism* — is not blocked by G-13** and may proceed once the corpus exists under the approved G-02 governance. | D-02.4, D-02.5 |
| 14 | **APPROVED 6 Sep 2026 (G-13.15).** *What is approved is the constraint, not the rule — the rule itself remains unresolved (D-05.7, G-13 §15.3 T12, §18 X17).* The rule resolving a value's **scope instance** is a Product Management decision, recorded in the vocabulary version, **deterministic and never derived from an extracted content value**. Constrained by AR-DET-008, approved item 3, and AR-AST-007; **none of them supplies it, and the revision does not choose it.** | **D-05.8** |

### What the approval does **not** do

1. **It does not amend `step3.pdf`.** Per §0.2 and the §11 Containment Rule, a specification change requires a new version number. The approved definition is a project decision that sits *beside* the specification.
2. **It does not close REQUIREMENTS GAP G-13.** The specification still contains no canonical attribute; "canonical" appears once in thirty-nine pages and is never elaborated. The gap remains open in §4, and closing it requires the amendment recorded there.
3. **It does not create a single attribute.** What is approved is the **shape** of a definition and the rules governing it. **The vocabulary's contents do not exist and remain to be authored by Product Management.** Every readiness status in this register that reads **BLOCKED — REQUIREMENTS GAP (G-13)** therefore stands unchanged.
4. **It does not resolve G-12.** Which attributes exist for each document type — and which fields on which type map to them — remains G-12's, per [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md), which is analysed and **not** approved.
5. **It does not define any document-specific field.** G-13 defines *how* a concept is represented, never *which* concepts a document type contains.
6. **It does not move provenance or confidence into the attribute definition.** Both remain **value-level** properties: FR-INF-002 attaches provenance and confidence to "every attribute **value**"; FR-OCR-005 attaches confidence to each extracted field value. Their scale and semantics remain **G-06**.
7. **It does not bring aliases or document-type applicability into the vocabulary.** Both remain **G-12** concerns — the document-specific label is absorbed by G-12's field-to-attribute mapping, and applicability is derivable from it.
8. **It does not resolve G-14, G-15, G-19, or G-20**, and it does not settle any TBD listed in D-05.7.
9. **Nor does the 6 September revision (D-05.8).** It amends three approved decisions and adds one; it creates no attribute, assigns no sensitivity tier, chooses no scope-instance model, approves none of the ten candidate attributes drafted in G-12 §15, and does not amend `step3.pdf`.

## D-05.7 Dependencies that remain unresolved

**These must not be silently converted into implementation requirements.** Each is recorded here because the approval deliberately left it open.

| Dependency | Status | Effect |
| --- | --- | --- |
| **The vocabulary's contents** — which attributes exist | **TBD — T1 authoring pass run 6 Sep 2026 (D-05.9), completed the same day (D-05.10); `v0.1-draft` holds one proposed entry whose properties 1–6 are now complete and whose tier is TBD by design — still unapproved** | Approved decision 2 fixes the shape of an entry. **One entry is now proposed and nine candidates are not authored (D-05.9); no entry is approved and none is gate-A complete.** Nothing attribute-shaped may be built (approved decision 11). **The ten attributes drafted in G-12 §15 are a DRAFT CANDIDATE SET, not content** — four challenges stand against them (D-05.8). |
| **The scope-instance resolution rule** | **TBD — G-13.15 APPROVED 6 Sep 2026; the rule itself is still undecided** | The revised decision 2 declares a scope *subject*; the *instance* must still be resolved deterministically at comparison time. Two of five candidate derivations are excluded by approved decision 3, AR-AST-007, or FR-INF-004 itself. **None is selected.** See D-05.8. |
| **Per-attribute normalisation rules** | **PARTIALLY RESOLVED — casing and spacing APPROVED 7 Sep 2026 (N-TEXT, PD-B, D-05.11); dates and numeric precision remain TBD** | `step3.pdf` names four categories — dates, casing, spacing, numeric precision — and states no rule for any of them. **N-TEXT** supplies the minimum semantic rule for **casing and spacing** on a `text` attribute, drawn from FR-INF-008's own "without altering meaning" clause; **dates and numeric precision remain TBD** because no date-typed or numeric attribute is authored. Each remaining rule, and every widening of N-TEXT, is a conflict-detection behaviour decision under approved decision 5. |
| **"spacing" (FR-INF-008) vs "whitespace" (AR-DET-003)** | **TBD** | The specification uses two words for what appears to be one normalisation category. Resolvable only by amendment. |
| **Destination of an unmapped extracted value** | **REQUIREMENTS GAP — G-29** *(numbered 6 Sep 2026, D-05.10; the destination itself is still undecided — PD-E)* | Approved decision 7 forbids coercion and does not supply the destination. `step3.pdf` provides an "unknown" outcome at document-type level (FR-OCR-002) and form-field level (FR-FLD-006) and none at attribute level. Recorded in the approved document as **G-13.g1**; **a numbered entry in §4 is owed by the owner of this register.** Related to, and distinct from, G-27 and G-08. |
| **Profile vs structured record** | **REQUIREMENTS GAP — G-19** | Upstream of the approved shape: if FR-ACC-004's profile and FR-INF-001's structured record are two stores rather than two views, an eighth property may be owed. See D-08.2. **The 6 Sep revision does not consume that slot** — it redefines the existing multiplicity property rather than adding one. Because the property list freezes once (G-13 §18 X4), G-19's answer and the revision should land in a single revision event. See D-05.8. |
| **Duplicate attribute entry** | **REQUIREMENTS GAP — G-20** | Downstream. If the identity chosen is `(document, canonical attribute, normalised value)`, it inherits approved decision 5's re-approval consequence. See D-08.4. |
| **Sensitivity assignment rules and default tier** | **REQUIREMENTS GAP — G-14, G-15** | Populate the tier slot required by approved decision 9. Both depend on untested assumption **A-5**. **Under the revised decision 9 these gate G-13-B only** — not G-13-A, and therefore **not G-12 authoring or ground-truth annotation** — so they may proceed in parallel. **Unresolved; the revision resolves neither.** See D-05.8. |
| **Manual-entry destination** | **REQUIREMENTS GAP — G-27** | Unchanged; depends on G-12 as well. |
| **Which history a change or resolution is written to** | **REQUIREMENTS GAP — G-28** | Unchanged by this approval. |
| **Confidence scale and semantics** | **REQUIREMENTS GAP — G-06** | Independent of G-13; confidence is a value-level property. |
| **BR-001 / BR-002 threshold values** | **BLOCKED — EVALUATION REQUIRED**; gaps G-04, G-05, G-07 | Unchanged. |
| **Per-type field definitions** | **REQUIREMENTS GAP — G-12** | Now unblocked *for authoring*: the vocabulary shape exists to map to. Still requires the vocabulary's contents, and G-12 itself is analysed and not approved. **Gated on G-13-A, not G-13-B** (D-05.8). Its own type-boundary dependencies — **G-09, G-10, G-11, D-04.4** (student ID, hall ticket) and **D-04.7** (resume) — are **G-12's alone and do not gate the vocabulary**, so they run in parallel. |

**Amendment that should follow, per the approved document's §18 X16:** raising the canonical attribute vocabulary (G-13) — and the unmapped-value behaviour recorded above — as specification amendments under §11's Containment Rule. Until then, the gaps stand as gaps.

## D-05.8 PRODUCT DECISION — APPROVED — 6 September 2026 — the G-13 revision: G-13.2, G-13.5, G-13.9; new G-13.15; G-13.11 trigger clarified

**Status: PRODUCT DECISION — APPROVED 6 September 2026.** Approved by Product Management and binding on implementation as a project decision. Approval covers exactly five items and nothing else:

| # | Approved 6 September 2026 | What it is |
| --- | --- | --- |
| 1 | **G-13.2** — property 6 revised to a **scope-keyed cardinality** | Revision to an approved decision. Count stays **seven**; no eighth property |
| 2 | **G-13.5** — the FR-INF-004 comparison operates **within a scope instance** | Revision to an approved decision. Scope rules inherit the re-approval consequence |
| 3 | **G-13.9** — the untiered bar narrowed to **release**; closure split into **G-13-A** / **G-13-B** | Revision to an approved decision. Decides *when* the bar applies, never *what* a tier is |
| 4 | **G-13.15** — the scope-instance rule is PM's, deterministic, never derived from an extracted content value | New decision. **The rule itself is deliberately left unresolved** |
| 5 | **G-13.11** — trigger clarified to **G-13-A** | **Clarification only; the decision's wording is unchanged and it is not a reopened decision** |

**PRODUCT DECISION — APPROVED is not REQUIREMENTS GAP — CLOSED.** These five are project decisions standing beside `backend/step3.pdf`. **REQUIREMENTS GAP G-13 remains OPEN** in §4; **G-13-A is NOT MET** and **G-13-B is NOT MET**; **G-19**, **G-14** and **G-15** are unresolved; the ten G-12 candidate attributes are **not approved**; and `step3.pdf` is unamended.

**Driver.** The G-12 critical review returned **NOT READY — DEPENDENCY MUST BE RESOLVED FIRST** with three blockers, and [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) derived the minimum revision that answers them. The revised wording lives in [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) §15.1; this entry records the decision and its boundaries.

### Exactly which approved decisions are reopened

| Approved decision | Reopened? | Change | Why |
| --- | --- | --- | --- |
| **G-13.2** (item 2) | **YES — property 6 only** | Multiplicity redefined from `single \| repeating` to a **scope-keyed cardinality**: how many values, per what subject. **Count stays seven; no eighth property**; the "exactly these seven, and no others" clause retained | The property's own approved justification is that FR-INF-004 "cannot otherwise distinguish 'two documents disagree' from 'this attribute legitimately holds two values'". A two-value domain cannot express it: `single` makes three qualifications' years a permanent false conflict, `repeating` suppresses genuine disagreements too |
| **G-13.5** (item 5) | **YES — one qualifying phrase** | The FR-INF-004 comparison function becomes the normalised form **within a scope instance**; scope rules inherit the re-approval and evidence-invalidation consequence | **AR-DET-008** is preserved — the comparison stays a deterministic function. Determinism was never the defect; the wrong thing was being determined |
| **G-13.9** (item 9) | **YES — scope of the bar** | Narrowed from "no attribute published without a tier" to "no attribute **released** without a tier"; closure split into **G-13-A** (structural, NOT RELEASABLE) and **G-13-B** (releasable) | FR-INF-007 and FR-SENS-001 bind the system, not an analysis artefact. The original wording put studies **S-1/S-4** and assumption **A-5** on the critical path of G-12 authoring, annotation and evaluation design. **Nothing in `step3.pdf` requires that** |
| **G-13.3** (item 3) | **NO — explicitly preserved** | Unchanged and not reworded | Identity remains established by the field→attribute mapping alone. A scope key qualifies *which values are compared*; it never establishes identity by label, value, proximity or position |
| Items 1, 4, 6, 7, 8, 10, 12, 13 | **NO** | Wording preserved exactly | Not implicated |
| **Item 11** (G-13.11 — no placeholder attribute until closure) | **NO — clarified, not reopened** | Decision wording unchanged. Its **“until G-13 closes” trigger is clarified to mean G-13-A**, and approved gate-A content is recorded as not a placeholder within its meaning | The two-gate split made the trigger ambiguous, and it is the clause governing whether ground-truth annotation may reference attributes at gate A. The clarification adds no prohibition and lifts none before G-13-A; entry into production code, schema, migrations and stored production data stays barred until **G-13-B**, because an attribute whose tier reads TBD does not satisfy **FR-INF-007** |

**New, not a reopening:** **G-13.15** (item 14) records the scope-instance resolution question, lists five candidate derivations, excludes two on requirement grounds, and **selects none**.

**Citation note.** Gate B is grounded on **FR-INF-007** (MUST — an attribute whose tier reads TBD does not satisfy it, so it may not exist in the running system) with **FR-SENS-002 / BR-005** governing disclosure of a tiered value to a form. **FR-FILL-001**'s “and the field is classified routine” is a separate condition on the **detected form field**, classified under **FR-FLD-003**; **FR-SENS-001** keeps the attribute and form-field classifications distinct. The two must not be conflated.

### The problem being solved, and why it is a requirements problem

A person legitimately holds several qualifications, each with its own year of passing, awarding body, result and roll number. Under approved item 3 plus approved item 5, three documents supplying three values for one canonical attribute is a conflict **by construction**, though nothing disagrees. Verified consequence chain, every step from `step3.pdf`:

**FR-INF-004** fires → **AR-DET-008** makes it fire every time → **FR-INF-005** surfaces it → **BR-004** forbids resolving it by rule → **EC-004** marks every field needing that attribute ambiguous → **FR-AMB-001** blocks autofill → **FR-INF-006**'s only clearing path makes the user designate one value authoritative and demotes the other two to "alternatives".

**The product's only conflict-clearing path destroys correct data, for every user holding more than one qualification.**

**Scope collapse is a fourth source of false conflict**, distinct from extraction error, normalisation, and genuine document variance. **D-02 §11.6's attribution taxonomy carries only those three** and would file every instance under "genuine document variance" — the category that reads as no action needed. **A fourth category, *scope-model error*, is owed by that document's owner. This register does not modify D-02.**

### What the revision explicitly does **not** do

1. **It does not create, approve, name, or adopt any attribute.** The ten drafted in G-12 §15 remain a **DRAFT CANDIDATE SET** (G-13 §15.4) with four challenges standing: the FR-FILL-001 consumer justification does not discriminate; six of ten fail G-12's own "definable now" test; the two identifier-number candidates are gated by the unresolved "stored at all, masked, or in part" question at D-05.3 and D-02 §11.7; and one candidate's semantic definition is by page position rather than meaning. **None of the four is repaired.**
2. **It does not resolve G-14 or G-15**, assign any sensitivity tier, write any classification rule, or choose a default. It changes only **when** the untiered bar applies. D-06.4's existing default-to-*sensitive* recommendation is cited **with its cost** and is **not adopted**: under **FR-SENS-002** and **BR-005** a blanket *sensitive* default would require explicit per-instance approval for every value, so nothing would be placed automatically. **§10.1 step D7 becomes unrunnable; step D11 remains runnable**, since it exercises the sensitive-approval path itself — what is lost is the contrast between them. *(**FR-FILL-001**'s "classified routine" condition governs the **detected form field** under **FR-FLD-003**, not the stored attribute's tier — **FR-SENS-001** keeps the two classifications separate.)*
3. **It does not choose the scope-instance resolution model** (item 14 / G-13.15).
4. **It does not add an eighth property**, and does not consume the eighth-property slot **G-19** may still require.
5. **It does not close REQUIREMENTS GAP G-13**, which stays open in §4 and still needs the §11 Containment Rule amendment.
6. **It does not amend `step3.pdf`.** G-13.13 is unchanged: this is a project decision beside the specification, never a change to it.
7. **It does not change vocabulary ownership.** **G-13 owns the canonical vocabulary and its contents** (G-13 §15.3 T1, §18 X6, approved item 8, §13.2); **G-12 owns the mapping of approved attributes to document types**.
8. **It does not resolve G-09, G-10, G-11, D-04.4 or D-04.7.** Those gate **G-12** and not the vocabulary, and now run in parallel with vocabulary authoring.
9. **It touches no production code, schema, migration, dependency, fixture or evaluation tooling** — approved item 11 still forbids that until the contents exist.

### The two gates

| Gate | Reached when | Unblocks | Gated on |
| --- | --- | --- | --- |
| **G-13-A** — structural | Shape frozen; properties 1–6 complete for every attribute; tier slot present and **TBD**; version marked **NOT RELEASABLE** | **G-12 authoring** · D-02 **L6/L7** annotation and its design · D-02 **§11.6** evaluation design | **G-19** · the property-6 revision · **G-13.15** · the G-13.12 minimality test · G-13 §18 X18 |
| **G-13-B** — releasable | Every tier assigned | Implementation of FR-INF-001…009 · production storage of attribute values · **automatic placement of any value into a form** (**FR-INF-007** primary; **FR-SENS-002 / BR-005** for disclosure) | **G-14, G-15** (A-5; studies S-1, S-4) |

**Current status: neither gate reached. G-13-A — NOT MET. G-13-B — NOT MET.** The 6 September approval settles the *decisions* that gate A depends on (G-13 §18 **X1 — MET**); **X2, X3, X4, X6–X8, X10–X15, X17, X18 remain unmet**, and the vocabulary's contents still do not exist.

### Owners

| Item | Owner |
| --- | --- |
| G-13.2, G-13.5 revisions | Product Management · Architecture |
| G-13.9 narrowing and the two gates | Product Management · Privacy |
| G-13.11 trigger clarification — the trigger is **G-13-A** | Product Management · Engineering |
| G-13.15 — scope-instance resolution rule | Product Management · Architecture |
| G-19, so the shape can freeze once | Product Management · Architecture |
| D-02 §11.6's fourth attribution category | Owner of `SPRINT_4_D02_OCR_EVALUATION_PLAN.md` |
| §4 gap entries for **G-13.g1** and G-12's candidate gaps | Owner of this register — **no G-number is invented by the revision** |


---

## D-05.9 T1 — VOCABULARY CONTENTS AUTHORED — 6 September 2026 — PROPOSED, NOT APPROVED

**Status: T1 AUTHORING PASS COMPLETE — CONTENT PROPOSED, NOT APPROVED.** The authored content lives in [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§19**; this entry records the state. **Nothing here is binding.** **G-13-A remains NOT MET, G-13-B remains NOT MET, and REQUIREMENTS GAP G-13 remains OPEN in §4.**

**What T1 was.** D-05.7 records the vocabulary's contents as *"TBD — authoring owed by PM"*. The authoring pass ran the ten G-12 candidates, and the specification itself, against an admission test built only from approved decisions — **G-13.12** (a discriminating consuming requirement), **G-13.2** with **X6/X7/X8** (property completeness), **G-13.3** and **C-d** (definitional precision), **X18** (challenges discharged), and **BR-017 / NFR-PRIV-001** (minimality and prior safety decisions).

**The governing finding.** A second full-text search of `backend/step3.pdf` — this time for personal data rather than for the vocabulary's structural terms — returns **one** occurrence of a named personal datum in thirty-nine pages: **§12.2**, the prioritisation rationale for **FR-INF-004**, *"Name mismatches (P-06) are a silent disqualifier."* *Aadhaar* and *PAN* appear once each, in **§7.1**, as **document types**. *address* appears once as a document-type grouping label. *date of birth*, *birth*, *roll*, *board*, *university*, *qualification*, *percentage* and *CGPA* appear **zero** times.

### The result

| Outcome | Count | Detail |
| --- | --- | --- |
| **Authored** as vocabulary version **`v0.1-draft`** | **1** | `person.full_name` — all seven properties present; **property 5 UNRESOLVED (T3)**, **property 7 TBD (G-14/G-15)**. **Not gate-A complete, not evaluation-ready, not implementation-ready, not approved** |
| **Not authored — remain candidates** | **9** | `person.date_of_birth`, `person.postal_address`, `person.aadhaar_number`, `person.pan_number`, `education.awarding_body`, `education.qualification_name`, `education.year_of_passing`, `education.aggregate_result`, `education.roll_number` |
| **Approved** | **0** | Approval of content is **PM's** under approved item 1 |

**Why only one was authored.** Nine candidates fail an admission test on evidence, not on preference. Seven fail **T-a** — no requirement in `step3.pdf` names them, and their only named consumer is **FR-FILL-001**, which **C-a** already records as non-discriminating. `person.postal_address` fails **T-b** — no data type and no normalisation rule (**C-b**, G-12 §18.3). `education.aggregate_result` fails **T-c** — defined by page position rather than meaning (**C-d**, G-12 §18.5). `person.aadhaar_number` and `person.pan_number` fail **T-e** — a prior safety decision, **D-05.3** and **D-02 §11.7**, governs whether the value may exist at all.

**What this does not do.**

1. **It approves no attribute**, and does not approve, adopt, or repair the ten G-12 candidates. **C-a, C-b, C-c and C-d stand.** One concept and identifier are carried into an entry authored on independently stated evidence; G-12's data type, normalisation, multiplicity and applicability for it are **not** adopted.
2. **It adds no eighth property** and introduces no scope property. Scope appears only inside the approved property 6.
3. **It does not resolve G-13.15 / T12.** **FR-ACC-003**'s single-person record is recorded as an observation about MVP scope, expressly **not** as a scope-instance resolution rule.
4. **It does not resolve G-14 or G-15** or assign any tier. The version is **NOT RELEASABLE**.
5. **It does not resolve G-19**, and therefore does not freeze the property list (**X4**).
6. **It does not resolve T3.** No normalisation rule exists for any category, so **X7** is unmet and **no entry is gate-A complete** — including the one authored.
7. **It does not close REQUIREMENTS GAP G-13** and does not amend `step3.pdf`.
8. **It claims no readiness.** It records `person.aadhaar_number` and `person.pan_number` as **NOT EVALUATION-READY**, overriding G-12 §19.1's rating for both, as **C-c** requires.
9. **It touches no production code, schema, migration, dependency, fixture, or evaluation tooling** — approved item 11's trigger is **G-13-A**, which is not met.

### G-13-A after T1 — what still blocks it

| Blocker | Criterion | Owner | Note |
| --- | --- | --- | --- |
| **The §10 / ASM-002 mock-form field inventory** | X10, X18 (C-a) | Product Management | **The cheapest open blocker in the set** — a team-constructed artefact needing no corpus and no study. It is the evidence that would discriminate for nine candidates |
| **Normalisation rules (T3)** | **X7** | Product Management, informed by D-02 §11.6 | **The binding constraint on the one authored entry.** G-12's N1–N5 are candidates in an unapproved document and are not adopted |
| **G-19 — profile vs structured record** | X2, X4 | Product Management · Architecture | The shape freezes **once**; freezing before G-19 is the one irreversible error available here |
| **G-13.15 / T12 — scope-instance rule** | X17 | Product Management · Architecture | Not exercised by the authored entry; required before any `qualification`-scoped entry can be compared |
| **G-13.g1 — unmapped-value destination** | X3, X11 | Owner of this register, then PM · Privacy | With one entry in the vocabulary, almost every readable value is unmapped |
| **D-05.3 / D-02 §11.7 — identifier storage** | Admission of two candidates | Product Management · Privacy | Safety-relevant; also gates **G-02 §8.6**'s derived-artefact redaction scope |
| **G-14, G-15 (A-5; S-1, S-4)** | X9 — **gate B only** | Product Management · Privacy | Does **not** gate G-13-A |

**G-12 after T1: still not unblocked in practice.** Its gate is **G-13-A**, and G-13-A is not met. Authoring a per-type field set requires vocabulary contents to map to; `v0.1-draft` holds **one** entry, and that entry is not complete. G-12 remains **ANALYSED, NOT APPROVED**.

---

## D-05.10 T1 COMPLETION PASS — 6 September 2026 — PROPOSED, NOT APPROVED

**Status: PROPOSED CONTENT — REQUIRES PRODUCT MANAGEMENT APPROVAL.** The work is in [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§20**. **G-13-A remains NOT MET. G-13-B remains NOT MET. REQUIREMENTS GAP G-13 remains OPEN in §4.**

**Purpose.** Take every remaining gate-A criterion and resolve the ones that existing evidence can settle — `step3.pdf` read semantically, the fifteen approved G-13 decisions, recorded project decisions, and G-12's candidate evidence — and, for the rest, name exactly the product decision required. **No requirement is invented and no new decision branch is created.**

### What this pass resolved

| # | Resolved | How |
| --- | --- | --- |
| 1 | **§15.3 T3 — for the two categories that apply to a text attribute.** Recorded as **N-TEXT**: *casing is not meaning; whitespace run length and edge whitespace are not meaning; **nothing else is folded**; the raw as-printed value is retained and is what the user sees* | Entirely from **FR-INF-008** (which states that casing and spacing may be normalised *without altering meaning*), **AR-DET-003**, **AR-DET-008**, and approved **G-13.3**, **G-13.5**, **G-13.6**, with **BR-004 / BR-009 / BR-016** forcing the conservative third clause. **Dates and numeric precision are NOT stated** — no date-typed or numeric attribute is authored |
| 2 | **Exit criterion X3** | **G-13.g1** — the destination of an extracted value that maps to no canonical attribute — is now recorded in §4 as gap **G-29**, the entry this register already listed as owed to its owner |
| 3 | **Exit criterion X5** | **G-13.3** is approved and states identity as a lookup through the field→attribute mapping, with label, value, proximity and position expressly excluded — applicable by an author without judgement |
| 4 | **X7, X8, X10 and X18 for `v0.1-draft`** — *on approval of this pass* | Properties 1–6 of the one entry are now complete; X7 reads *"where applicable"*; X10 is satisfied because §12.2 justifies the only entry; X18 is conditional on a challenged candidate **entering** the version, and none does |

**Semantic re-examination of the ten candidates.** All ten were re-examined against the requirements' *meaning* rather than their wording. **The outcome is unchanged — one attribute — and two reasons changed, both recorded:**

- **`person.postal_address`: existence is entailed after all.** §7.1's own grouping label is *"Identity and **address** — Aadhaar, PAN, address proof"*, and **FR-OCR-004** (MUST) requires a defined field set to be extracted for every supported type. The earlier statement that no evidence existed was too strong and is corrected. **It is still not authored**: the specification supplies no data type and no normalisation rule, and G-12 §18.3's component-set question is unresolved. **C-b is not repaired.**
- **Two entailments the specification makes and does not discharge**, recorded as concrete material for the **X16** amendment: **AC-US-008-4** with FR-INF-008's *dates* category entails that **at least one date-typed attribute exists**, and names none; **AC-US-003-1** with **FR-OCR-004** entails that the **education types have extractable fields**, and names none.

### The decisions required to finish gate A — five, all PM's, none needing a corpus or a study

| # | Decision | Unblocks |
| --- | --- | --- |
| **PD-A** | **The representation of an address** — one text value, or a structured object and which components (G-12 §18.3) | `person.postal_address` becomes authorable; **C-b** discharged |
| **PD-B** | **Approve `v0.1-draft`** — its contents, its **one-attribute scope**, and **N-TEXT** — **APPROVED 7 Sep 2026 (D-05.11)** | **X7, X8, X10, X18 now MET; X6 gated on X4/X17; X12 decision-dependency discharged** |
| **PD-C** | **G-19** — is FR-ACC-004's profile the same thing as FR-INF-001's structured record (D-08.2) | **X2**, then **X4** — the shape freezes once |
| **PD-D** | **G-13.15** — select a scope-instance derivation, **or** approve the per-subject reading of X17 recorded in §20.5 | **X17**, then **X15** |
| **PD-E** | **The unmapped-value destination** — gap **G-29** | **X11** |

**G-14 and G-15 are deliberately absent:** they gate **G-13-B** only.

### What this pass does not do

1. **It approves nothing** — N-TEXT, the completed entry and the X17 reading are proposals; approval of content is PM's under approved item 1.
2. **It marks no gate met.** **G-13-A NOT MET · G-13-B NOT MET.**
3. **It does not close REQUIREMENTS GAP G-13** and **does not amend `step3.pdf`**. A project decision beside the specification is not a change to it.
4. **It adds no eighth property**, introduces no scope property, and **does not resolve G-13.15** — the X17 reading is a proposal about a criterion's applicability, not a scope model.
5. **It does not resolve G-19** and does not freeze the property list.
6. **It does not resolve G-14 or G-15** and assigns no tier.
7. **It approves none of the ten G-12 candidates and repairs none of C-a…C-d.**
8. **It resolves T3 only where an authored attribute makes a rule applicable.** Any widening of N-TEXT is **evaluation-dependent** under D-02 §11.6.
9. **It touches no production code, schema, migration, dependency, fixture, corpus, OCR engine, or evaluation tooling.**

---

## D-05.11 PD-B — PRODUCT DECISION — APPROVED — 7 September 2026

**Status: APPROVED.** Product Management approves **PD-B** (named in D-05.10 and G-13 §20.6): **`v0.1-draft`'s contents, its one-attribute scope, and N-TEXT.** The approved content lives in [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§21**. **This is a PRODUCT DECISION — APPROVED standing beside `backend/step3.pdf`; it is not REQUIREMENTS GAP — CLOSED.**

### What is approved — exactly three things

| # | Approved | Grounding |
| --- | --- | --- |
| 1 | **The one entry `person.full_name`** as vocabulary version **`v0.1-draft`** — properties 1–6 complete, **property 7 (sensitivity tier) TBD by design** (slot present and empty; content is G-14/G-15, gate G-13-B) | **§12.2** / **P-06** make name comparison the worked justification for **FR-INF-004** (MUST) |
| 2 | **The one-attribute scope** — `v0.1-draft` holds this entry and no other on present evidence | **G-13.12** (approved) puts the burden of proof on *including* an attribute; each of the nine other candidates carries a recorded blocker (C-a…C-d, a prior identifier-storage safety decision, or an undecided data type) |
| 3 | **N-TEXT** — for a `text` attribute: **casing differences do not change value identity; edge whitespace and whitespace-run length do not change meaning; no other folding is assumed; the raw as-printed value is retained and shown to the user** | **FR-INF-008** ("casing, spacing … without altering meaning"), the deterministic-and-**reversible** normalisation requirement, **AR-DET-008**, and approved **G-13.3 / G-13.5 / G-13.6**, with **BR-004 / BR-009 / BR-016** forcing "nothing else is folded" |

### What the approval does

- **Satisfies G-13 exit criteria X7, X8, X10 and X18 for `v0.1-draft`** (G-13 §18, §20.5, §21.2).
- **Advances X6** — its contents and scope are approved — **without meeting it**: X6 stays gated on **X4** (G-19) and **X17** (G-13.15). **Discharges the PD-B decision-dependency of X12**, whose remaining step is an engineering act.

### What the approval does NOT do

1. **It does not close REQUIREMENTS GAP G-13** (still OPEN in §4) and **does not amend `step3.pdf`** (G-13.13, §11 Containment Rule).
2. **It does not meet a gate. G-13-A remains NOT MET; G-13-B remains NOT MET.** Four gate-A PM decisions remain: **PD-A** (address representation), **PD-C** (G-19), **PD-D** (G-13.15), **PD-E** (G-29 destination).
3. **It assigns no sensitivity tier** and does not resolve **G-14 or G-15**.
4. **It resolves neither G-19 nor G-13.15 nor G-29,** does not freeze the property list, and **adds no eighth property and no scope property** (count stays seven).
5. **It approves none of the nine other candidates**, repairs none of C-a…C-d, and does not make the PD-A address decision.
6. **It widens N-TEXT no further than casing and spacing** — dates and numeric precision remain TBD; every widening is evaluation-dependent (D-02 §11.6) and re-approval-bound (G-13.5).
7. **It touches no production code, schema, migration, dependency, fixture, corpus, OCR engine, or evaluation tooling.**

**Owner:** Product Management. **G-14 and G-15 are deliberately absent** — they gate G-13-B only.

---

## D-05.12 PD-A, PD-C, PD-D, PD-E — PRODUCT DECISIONS — APPROVED — 8 September 2026

**Status: APPROVED.** Product Management approves the four remaining gate-A decisions named in D-05.11 item 2 and laid out in [`SPRINT_4_G13_PM_DECISION_BRIEF.md`](SPRINT_4_G13_PM_DECISION_BRIEF.md); the approval record lives in [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§22**. **These are PRODUCT DECISIONS — APPROVED standing beside `backend/step3.pdf`; they are not REQUIREMENTS GAP — CLOSED.** With PD-B they complete every Product-Management-owned gate-A criterion.

### What is approved — exactly four decisions

| # | Approved | Grounding |
| --- | --- | --- |
| **PD-A** | **Structured address.** `person.postal_address` is a **structured object**, not one text value; **its component set is derived only from the §10/ASM-002 mock-form field inventory — none invented.** Shape decided; components pending that artefact | §7.1 *"Identity and address"* + **FR-OCR-004** (MUST) entail an address concept; **FR-FILL-002** asks fields in parts; discharges **C-b** |
| **PD-C** | **G-19 — one store, two views.** The **FR-ACC-004** profile is the **resolved view** over per-document **FR-INF-001** observations, not a second copy | Register **D-08.2**; gives FR-INF-003/006 and AC-US-005-1 a coherent home; a data-model relation that adds **no eighth property** to the seven-property shape |
| **PD-D** | **G-13.15 / X17 — narrowed per-subject.** The scope-instance rule is required before the first attribute of a subject enters a version; `v0.1-draft`'s single `person`-scoped attribute (record single-person under **FR-ACC-003**) needs none. The `qualification` derivation is deferred to the first such attribute and to the **G-12 mapping** | §20.5 narrowing taken; constrained by **AR-DET-008**, **G-13.15**; invents no scope model |
| **PD-E** | **G-29 — discard unmapped values for MVP.** A value mapping to no canonical attribute is not retained; the **original document is retained** (Sprint 3) as the recovery source, recoverable by **FR-OCR-010** reprocessing. Coercion stays barred (**G-13.7**) | **BR-016**, **BR-017 / NFR-PRIV-001** (minimality); avoids untiered personal data (FR-INF-007 / G-13 §12.3) |

### What the approval does — gate-A criteria satisfied

- **PD-C** satisfies **X2** (G-19 answered) and **X4** (the seven-property shape freezes; C1 adds no property).
- **PD-D** satisfies **X17** for `v0.1-draft` (per-subject narrowing).
- **PD-E** satisfies **X11** (unmapped-value destination).
- With X4, X5 and X17 met, **X6 becomes MET** for `v0.1-draft`, which in turn makes **X13** (G-12 authorable) and **X14** (D-02 L6/L7 annotatable) MET. **X8** is MET (its X4/X6/X17 gates now met). **PD-A** discharges **C-b** and makes `person.postal_address` authorable; it authors no entry.

### G-13-A recalculated

**G-13-A: NOT YET MET.** Gate-A criteria **X1–X8, X10, X11, X13, X14, X17, X18 are MET** (X6/X7/X8/X17/X18 for `v0.1-draft`). **Two remain, neither a PM decision:**

| Remaining | Owner | What it is |
| --- | --- | --- |
| ~~**X12**~~ | Engineering | **MET the same day — D-05.13:** held as `config/vocabulary/canonical_attributes.v0.1-draft.toml` (versioned), validated by 13 passing tests |
| **X15** | D-02 owner | The **fourth false-conflict attribution category** (D-02 §11.4.1) needed to make the §11.6 evaluation designable |

**X12 was completed the same day (D-05.13); X15 is now the sole remaining gate-A criterion. When it closes, G-13-A is MET. No further PM decision is required for gate A.** **G-13-B remains separately blocked** on G-14/G-15 (property 7) and §12.3's A-5/A-7.

### What the approval does NOT do

1. **It closes no requirements gap.** **G-13 remains OPEN** in §4; **G-19** and **G-29** are answered as product decisions but their `step3.pdf` amendment (X16) is not made — by instruction.
2. **It meets no gate** (X12, X15 outstanding) and **does not meet G-13-B**.
3. **It creates no attribute beyond `v0.1-draft`**; the nine candidates stay unauthored and **C-a…C-d stay open** (X18 reopens on any addition). PD-A decides the address *shape* only.
4. **It assigns no sensitivity tier** (property 7 TBD; G-14/G-15 untouched) and **chooses no `qualification` scope-instance derivation** and **no address component set**.
5. **It amends no line of `backend/step3.pdf`** and **touches no production code, schema, migration, dependency, fixture, corpus, OCR engine, or evaluation tooling.** No commit or push.

**Owner:** Product Management.

---

## D-05.13 X12 — VOCABULARY HELD AS VERSIONED CONFIGURATION — MET — 8 September 2026

**Status: MET.** G-13 exit criterion **X12** — *"the artefact is held as configuration and versioned"* (G-13.1, G-13.10) — is satisfied. This is an **engineering act, not a PM decision**: **G-13.11 does not bar it**, its post-gate-A bar being production code, schema, migrations and stored production data, whereas **configuration is where G-13.1 and G-13.10 place the artefact**. The detailed record is [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§22.6**.

| What | Where |
| --- | --- |
| **Configuration artefact** | `backend/config/vocabulary/canonical_attributes.v0.1-draft.toml` — TOML (repo convention; stdlib-readable via `tomllib`, no new dependency). Versioned: `vocabulary_version = "v0.1-draft"` (also in the filename); `releasable = false` (G-13.9, tiers TBD). Holds **exactly** `v0.1-draft`: the one entry `person.full_name`, seven properties in order, **no eighth property**, property 7 (`sensitivity_tier`) **TBD by design**, scope-keyed cardinality (`one` per `person`), and **N-TEXT** referenced by property 5 |
| **Validation** | `backend/tests/test_vocabulary_config.py` — 13 tests: structural validity, version/filename agreement, not-releasable, one-entry scope, exactly the seven property keys, `person.full_name` values preserved verbatim, property 6 = *one per person*, property 7 = TBD slot present-and-empty, N-TEXT's four approved semantics, and guards against silent N-TEXT widening or added rule/tier content. **All 13 pass.** |

**What it does NOT do.** It **touches no production code** — the artefact is configuration, the tests are test code, and **D-01's extraction interface (`app/services/extraction.py`) is untouched and not wired to it**. It **resolves no gap** (G-14/G-15, G-19, G-29, G-13.15 stand as their already-approved decisions leave them), **adds no attribute**, and **amends no line of `backend/step3.pdf`**. No commit or push.

**Recalculated G-13-A status (at the time X12 was recorded).** Gate-A criteria **X1–X8, X10, X11, X12, X13, X14, X17, X18 were MET**; **X15 was then the sole remaining gate-A criterion**. **X15 was closed the same day — D-05.14 — making G-13-A MET.** **G-13-B** remains separately blocked on G-14/G-15 (property 7) and §12.3's A-5/A-7.

**Owner:** Engineering (the act); the content was approved earlier (D-05.11, D-05.12).

---

## D-05.14 X15 — CLOSED; G-13-A — MET — 8 September 2026

**Status: X15 MET → G-13-A MET.** The final gate-A criterion, **X15** (*"D-02 §11.6 conflict-detection evaluation becomes designable against a real subject"*), is satisfied. The **fourth false-conflict attribution category** it required — **scope-model error (scope collapse)** — is now applied at **D-02 §11.6.1**, sourced from the analysis recorded at G-13 [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) **§11.4.1 / §22.7**.

| What | Detail |
| --- | --- |
| **Fourth attribution category** | **scope-model error (scope collapse)** — a false conflict where two values map to the **same canonical attribute but different scope instances of its subject** (G-13.2 property 6), told apart from genuine document variance by the **L6/L7** scope-instance annotation. Added at **D-02 §11.6.1** as a fourth cause beside extraction error, normalisation, and genuine document variance. **No new evaluation methodology introduced** — the §11.4.1 analysis is applied. |
| **Designable against a real subject** | `v0.1-draft`'s `person.full_name` is `person`-scoped in a single-person record (**FR-ACC-003**); scope collapse cannot arise for it, so §11.6 is designable against that subject now. The scope-instance annotation binds when a `qualification`-scoped attribute enters (**PD-D**). |

**G-13-A: MET (8 September 2026).** All gate-A criteria are satisfied: **X1–X8, X10, X11, X12, X13, X14, X17, X18**.

**What G-13-A being MET unblocks:** **G-12** field-set authoring; the **design and annotation** of the §11 field-extraction and §11.6 conflict-detection evaluations (D-02 L6/L7). It does **not** unblock their *execution* (needs the vocabulary's contents and G-12), the **BR-001** threshold (needs G-04–G-07 and the evaluation), or the **§7.1** type-inclusion decision (needs per-type results).

**What remains open — unchanged by this:**
- **G-13-B — NOT MET:** property-7 sensitivity tiers are **TBD** (**G-14 / G-15**); §12.3's **A-5 / A-7** gate any build. **G-14 / G-15 are not resolved here.**
- **REQUIREMENTS GAP G-13 — OPEN:** the `step3.pdf` §11 Containment-Rule amendment (**X16**) is still owed; `step3.pdf` is unchanged.
- **G-12 — its own gaps stand:** type boundaries (**G-09 / G-10 / G-11**), the four challenges **C-a…C-d**, and the **§10 / ASM-002 mock-form field inventory**. G-13-A unblocks G-12's *authoring*, not its completion.

**No production code, no approved vocabulary content, and no line of `backend/step3.pdf` changed. No commit or push.**

**Owner:** Engineering / the D-02 document owner (the act); content approved earlier (D-05.11, D-05.12).

---

## D-05.15 §10 / ASM-002 MOCK-FORM FIELD INVENTORY — SCAFFOLD RECORDED; L-INFO OWED — 8 September 2026

**Status: the named artefact now exists as a scaffold; its information content is still owed.** The **§10 / ASM-002 mock-form field inventory** — the input D-05.14 lists as still-open for G-12, that G-13 §15.4 **C-a** / register row **U5** name as the discriminating-consumer evidence, and that **PD-A** (D-05.12) defers its address component set to — has been authored as the named project artefact [`SPRINT_4_MOCK_FORM_FIELD_INVENTORY.md`](SPRINT_4_MOCK_FORM_FIELD_INVENTORY.md). This entry records that act and its exact reach. It approves no vocabulary attribute, no field definition, and no sensitivity tier.

**What the artefact records.** `step3.pdf` §10 fixes the mock form's **structure** — full coverage of the seven FR-FLD-007 field types and the behavioural slots the demonstration journey (Table 10.1, D5–D13) must exercise — and fixes **none of its information content**. Under **ASM-002** the form is *constructed by the team*; its settlement path is **Study S-3 form teardown**. The artefact therefore separates two layers and records only what evidence supports:

| Layer | What it is | Status |
| --- | --- | --- |
| **L-STRUCT** — field-type & behaviour coverage (artefact §3, slots S1–S10) | Which of the seven form-field types appear and which extension behaviours the form must exercise | **RECORDED against `step3.pdf` evidence (MF1 MET)** |
| **L-INFO** — the information each field requests (artefact §4) | The semantic labels a real MCA-style application carries | **OWED — team construction / Study S-3 (MF2 NOT MET); not invented here** |

**Inventory conditions (artefact §9):** **MF1 MET**; **MF2, MF3, MF4 NOT MET** — all wait on the team constructing the form (or running S-3), which needs no corpus, OCR engine, or study.

**Consequence for C-a (§15.4 / U5).** C-a's discriminating evidence lives in **L-INFO**, which does not yet exist. So C-a is discharged only where an attribute has a discriminating consumer *independent of the mock form* — i.e. `person.full_name` alone (already approved, PD-B). For the **nine mock-form-dependent candidates** (`person.postal_address` and the five `education.*`, plus the identifier and address rows blocked upstream), **C-a stays open**; the artefact makes the evidence path precise and bounds its cost, but does not discharge it.

**Consequence for PD-A (D-05.12).** PD-A approved the address *shape* (A2, structured object) with its component set to be "derived only from the §10/ASM-002 mock-form field inventory — none invented." This artefact is that inventory; because L-INFO (artefact §4.1) is still owed, **the address component set remains pending**. This does **not** reopen PD-A — it identifies the exact input PD-A defers to.

**What this does not do.** Adds no canonical vocabulary entry; approves none of the ten G-12 candidates; repairs none of C-a…C-d; changes no approved G-13 shape; sets no sensitivity tier or threshold; closes neither REQUIREMENTS GAP G-12 nor G-13; touches no production code, schema, migration, dependency, fixture, or `backend/step3.pdf`. **No commit, no push.**

**Owner:** Engineering (the artefact — an evidence record); the **team** owns MF2 (construct the form / run S-3); PM owns any decision the populated §4.1 later enables.

---

# D-06 — Sensitivity rules

## D-06.1 REQUIREMENT — what is explicitly defined in `step3.pdf`

| ID | Requirement | Note |
| --- | --- | --- |
| FR-INF-007 | "Every attribute shall carry a sensitivity classification of **routine, sensitive, or consequential**." (MUST) | Trace: §02 Table 13.1 |
| FR-SENS-001 | "The system shall maintain the three-tier sensitivity classification for **both stored attributes and detected form fields**." (MUST) | Trace: §02 Table 13.1 |
| FR-SENS-004 | "Sensitive values shall be **masked in DOCURA's own interface by default** and revealed only on user action." (SHOULD) | The only masking requirement in the specification |
| FR-SENS-006 | "The user shall be able to **raise** the sensitivity of an attribute. **Lowering the consequential tier shall not be possible for any user.**" (SHOULD) | Trace: BR-006, A-5 |
| BR-020 | "An attribute or field classified consequential can never be reclassified downward by any actor." | Sensitivity floor |
| AR-DET-005 | "Sensitivity classification shall be driven by a **reviewable rule set**, not inferred per session." (MVP) | Deterministic, not per-session inference |
| AR-AST-007 | An assisted component "may add a sensitivity classification, never remove one." | Monotonicity |
| NFR-MNT-004 | "Sensitivity classification rules shall be maintainable as a **reviewable list**, not scattered through the implementation." (SHOULD) | Where the rules live |
| NFR-PRIV-007 | "Diagnostic and analytics data shall exclude document contents and extracted personal values." (MUST) | Constrains logging of any tier |

**So the specification defines: the three tier names, that every attribute carries one, that the rule set is deterministic and reviewable, that classification can only be raised, that consequential is a floor, and that sensitive values are masked by default in DOCURA's interface.**

## D-06.2 What is missing

| # | Gap |
| --- | --- |
| **G-14** | **The classification rules themselves are not in `step3.pdf`.** FR-INF-007 and FR-SENS-001 trace to "§02 Table 13.1" — a table in document 02, which is labelled "**WORKING** SENSITIVITY CLASSIFICATION", is tagged **ASM**, gives *examples* rather than rules, and is immediately qualified: "The boundary between routine and sensitive is the most important unresolved question in this document… **This boundary must be set by users, not by us** — it is assumption A-5." §12.3 confirms A-5 is untested and that FR-SENS-001…006 and NFR-USE-002 depend on it. **The rules therefore do not exist in a settled form in either document.** |
| **G-15** | **No default tier** is specified for an attribute that no rule covers. |
| **G-16** | **Document-level sensitivity is undefined.** FR-SENS-001 covers "stored attributes and detected form fields" — documents are not mentioned. Yet FR-MATCH-009 ("A document classified sensitive shall be attached only after explicit per-instance approval") and EC-011 ("Sensitive document requested") both presuppose that documents carry a tier. Nothing states how a document's tier is derived — from its type, from the most sensitive attribute it yields, or from an independent rule. |
| — | **Scope of masking is undefined.** FR-SENS-004 says "in DOCURA's own interface". Whether the API may return unmasked values to its own front end (with masking applied client-side), or must mask at the boundary, is not stated. For a backend sprint this is the operative question. |
| — | **What "revealed only on user action" requires of the backend** — a separate reveal request, an audit entry for reveals, or neither — is not stated. FR-AUD-001…003 record DOCURA's actions on forms, not the user's reads. |

## D-06.3 What can be implemented structurally

- A three-value sensitivity tier on every attribute (FR-INF-007) — the tier *names* are specified, so the enum is safe to model.
- Tier assignment driven by a **configuration-held, reviewable rule list** (AR-DET-005, NFR-MNT-004) — the mechanism is required even though the content is not settled.
- **Raise-only enforcement** at the write boundary (FR-SENS-006, BR-020, AR-AST-007). This is a structural invariant and is fully specified.
- Exclusion of extracted personal values from diagnostics and logs (NFR-PRIV-007) — Sprint 3's redaction processor in `app/core/logging.py` is the existing precedent.

## D-06.4 What requires product / requirements approval

- **The rule list itself (G-14).** It cannot be written by engineering, is tied to canonical attributes (G-13), and is formally dependent on assumption A-5 and studies S-1 and S-4.
- **The default tier (G-15).** **RECOMMENDATION:** default to **sensitive** for any attribute with no rule. BR-016 ("fail towards inaction") and BR-009 both point that way, and AR-AST-007's asymmetry (may add, never remove) shows the specification's direction of travel. *This is a recommendation, not a requirement.*
- **Document-level tier derivation (G-16).**
- **Masking boundary.** **RECOMMENDATION:** mask at the API boundary and require an explicit, separately authorised reveal, so that the guarantee does not depend on client behaviour. Note this is stronger than FR-SENS-004, which is a SHOULD and speaks only of the interface.

**Blocking status:** **BLOCKED — REQUIREMENTS GAP** for the rules (G-14, G-15, G-16); **BLOCKED — EVALUATION REQUIRED** in that A-5 (studies S-1, S-4) is the specification's own means of settling the boundary; **READY** for the tier field, the raise-only invariant, and the configuration mechanism.

---

# D-07 — Off-device processing disclosure (NFR-PRIV-006)

## D-07.1 REQUIREMENT — the exact text

> **NFR-PRIV-006** (MVP, MUST): "Any processing performed outside the user's device shall be disclosed in plain language before the user's first upload."

> **§9, Table 9.1, Consent row**: "Never automated. Activation required before reading any page. **Off-device processing disclosed before first upload.**" — Requirements: BR-006, BR-014, FR-EXT-003/004, NFR-PRIV-006.

## D-07.2 When the requirement applies

The trigger has two parts, and both are in the text:

1. **Condition:** *any* processing performed outside the user's device. Not "AI processing", not "third-party processing" — any processing.
2. **Timing:** before the user's **first** upload. The obligation attaches once, at the start of the relationship, not per document.

**Interpretation issue.** The specification does not define "processing". Under a plain reading, Sprint 3 as built already performs processing outside the user's device: file-type and size validation, SHA-256 checksumming, duplicate detection, and storage all occur on DOCURA's server. On that reading **the NFR-PRIV-006 obligation is already live and already unmet, as of Sprint 3, independently of anything Sprint 4 adds.**

A narrower reading — that "processing" means the extraction and interpretation of document *content* — would place the trigger at Sprint 4.

**Finding: the ambiguity is a REQUIREMENTS GAP (G-17)**, and it is the same gap as G-01 seen from the other side: the specification never fixes where MVP processing occurs, so the disclosure's subject is undefined. **RECOMMENDATION:** adopt the broad reading. BR-019 ("no absolute claims") and NFR-SEC-008 ("Security statements shall describe specific measures and their limits") both push toward candour, and a disclosure that omits server-side storage in order to be narrowly true would be the kind of statement those rules exist to prevent.

## D-07.3 Does the Sprint 3 upload flow need modification?

- **Under the broad reading: yes, and it needed it in Sprint 3.** The disclosure must be presented before the first upload, which is an upload-flow concern, not an extraction concern.
- **Under the narrow reading: yes at Sprint 4**, because Sprint 4 is the point at which document *content* is processed off-device.
- **Either way, what changes at Sprint 4 is the disclosure's content, not the existence of the obligation** — and it changes materially if D-01 selects an external provider (Option C or D), because the disclosure must then say that a third party processes documents.

**Note on sprint scope:** the disclosure surface is user-facing, and no DOCURA UI exists yet. The backend-side question is narrower and is stated in D-07.5.

## D-07.4 Must the user acknowledge anything?

**No — the specification does not require acknowledgement.** NFR-PRIV-006 requires *disclosure*, not consent, not acknowledgement, and not a control the user must operate. This is a deliberate distinction elsewhere in the document: where the specification wants an explicit user act it says so plainly (FR-SENS-002 "explicit approval", FR-INT-001 "explicitly activating", FR-ACC-007 "an explicit confirmation that states what will be destroyed"). NFR-PRIV-006 uses none of that language.

**No UI behaviour is invented here.** How the disclosure appears — a screen, a panel, a link, a step in onboarding — is not specified and is a **PRODUCT DECISION**.

## D-07.5 Must acknowledgement be persisted?

**The specification does not require it.** No requirement in `step3.pdf` obliges the system to record that the disclosure was shown or accepted. FR-AUD-001…006 concern DOCURA's actions in form sessions, not consent records.

**RECOMMENDATION (not a requirement):** persist a minimal record — disclosure version identifier and timestamp, per user. Reasons: (a) if the disclosure's content changes when an external provider is introduced, there is otherwise no way to know which text a given user saw; (b) NFR-SEC-009 anticipates independent security review, which will ask; (c) the cost is one small table. **DECISION REQUIRED** — this would be a new obligation beyond NFR-PRIV-006, and creating it silently would be exactly the sort of unrequested scope this register exists to prevent.

## D-07.6 What the specification actually requires — summary

| Question | Answer from `step3.pdf` |
| --- | --- |
| Disclosure required? | **Yes** — NFR-PRIV-006, MVP, MUST |
| In what form? | "In plain language". No further constraint. |
| When? | "Before the user's first upload" |
| Of what? | "Any processing performed outside the user's device" — subject undefined (G-17) |
| Acknowledgement required? | **Not required** — the specification does not say so |
| Persistence required? | **Not required** — the specification does not say so |
| Re-disclosure when processing changes? | **Not addressed** — REQUIREMENTS GAP (G-18) |
| Specific UI? | **Not specified** — product decision |

**Blocking status:** **NOT BLOCKING** for Sprint 4 backend implementation. **BLOCKING** for any release that accepts real documents, and the disclosure text is **BLOCKED** on D-01 (its content depends on whether a third party processes documents).

---

# D-08 — Data model decisions

**This section does not design a schema.** It identifies the concepts the requirements force into existence, and the decisions that must be made before any of them is modelled. Sprint 3 set the precedent deliberately: `app/db/models.py` records that extraction output was left unmodelled because "modelling their output before the extractor exists would fix a shape around requirements whose thresholds are still TBD."

## D-08.1 Required data concepts and their sources

| Concept | Required by | Status | Unresolved decisions |
| --- | --- | --- | --- |
| **Extracted text** | FR-OCR-001 (MUST); FR-SRCH-002 requires it to be searchable | REQUIREMENT | Granularity (whole document, per page, per block); whether page and position are retained; interaction with NFR-SEC-002 encryption (D-10) and with FR-SRCH-004 "the location within it where the match occurred" |
| **Document classification** | FR-OCR-002, FR-DOC-002 | REQUIREMENT | Whether the assigned type and a user correction to it are separate values (FR-DOC-002 makes the type "correctable by the user", and BR-012 gives user values precedence); relation to the store-and-search-only state (G-08) |
| **Classification confidence** | FR-OCR-003 | REQUIREMENT | Scale and semantics (G-06); whether it is retained after a user correction |
| **Extracted attributes** | FR-OCR-004, FR-INF-001 | REQUIREMENT, **blocked by G-12/G-13** | Everything about their identity — see D-05 |
| **Field confidence** | FR-OCR-005 ("independently of the document-level confidence") | REQUIREMENT | Missing-confidence semantics (D-03.5) |
| **Source document** | FR-INF-002 ("Every attribute value shall reference the document it came from"), BR-010 | REQUIREMENT | None material — this is a plain reference |
| **Source region** | FR-OCR-007 (SHOULD), AC-US-004-1 (source *and* region shown), AR-AST-006 | REQUIREMENT (SHOULD) | Representation: page number plus bounding box in which coordinate space; what is stored when the engine returns no geometry; whether a region is required for a *user-corrected* value (it cannot be) |
| **Needs-review flag** | FR-OCR-006, BR-002 | REQUIREMENT | Whether it is stored or derived by comparing confidence to the current threshold. **RECOMMENDATION:** derive it, because NFR-MNT-002 allows the threshold to change without a code release, and a stored flag would silently become stale. |
| **Sensitivity tier** | FR-INF-007, FR-SENS-001 | REQUIREMENT (structure), **blocked by G-14** for content | Where it is stored: on the attribute instance or on the canonical attribute definition. Raise-only (FR-SENS-006, BR-020) implies a per-user override must be storable. |
| **Authoritative value** | FR-INF-003 ("a user-supplied value shall become authoritative over any extracted value"), FR-INF-006, BR-012 | REQUIREMENT | How authority is represented; what happens when no value is authoritative (AC-US-005-1 requires exactly that state during an unresolved conflict) |
| **Alternatives** | FR-INF-006 ("retain the alternatives"), AC-US-005-3 | REQUIREMENT | How long alternatives are retained; whether a superseded extraction remains an alternative after reprocessing |
| **Conflicts** | FR-INF-004/005, AR-DET-008, EC-004 | REQUIREMENT | What constitutes "different values" — requires the normalisation rules of FR-INF-008, which require the canonical vocabulary (G-13). Also: conflict lifecycle (open → resolved), and whether resolving a conflict then re-opens if a third document disagrees |
| **Change history** | FR-INF-009 (SHOULD, "including who or what changed it"), FR-AUD-005 (not user-editable) | REQUIREMENT | Whether attribute history is the same store as form-session history (FR-AUD-*) or a separate one. They have different subjects; **RECOMMENDATION:** separate. |
| **Canonical personal profile** | FR-ACC-004, FR-INF-001 | REQUIREMENT, **and the relationship between the two is a GAP** | See D-08.2 |
| **Processing job state** | FR-UPL-005 (the five states), NFR-PERF-002, NFR-REL-002 | REQUIREMENT | Whether the job is a distinct entity from the document's status. See D-08.4 and D-09. |
| **Processing failure** | FR-OCR-009 ("retain the original file, state what failed"), EC-001, NFR-ERR-001/003 | REQUIREMENT | What a failure reason is made of, and how it is stated to the user without exposing internals (NFR-ERR-004) |
| **Retry** | FR-OCR-009 ("offer a retry"), NFR-ERR-005 | REQUIREMENT | Whether retry is user-initiated only or also automatic. **The specification only names a user-facing retry**; automatic retry is not required and is an ARCHITECTURE DECISION (see D-09). Retry count and backoff are unspecified. |
| **Reprocessing** | FR-OCR-010 (SHOULD, user-requested) | REQUIREMENT | Whether reprocessing supersedes or appends observations; interaction with corrections (AC-US-004-3) |
| **Idempotency** | NFR-REL-005 (SHOULD): "Repeating the same operation on the same input shall not produce duplicate documents or duplicate attribute entries" | REQUIREMENT | See D-08.4 |
| **User corrections** | FR-INF-003, AC-US-004-2, AC-US-004-3, BR-012 | REQUIREMENT | See D-08.3 |

## D-08.2 Profile vs attributes

**Two requirements describe what appears to be one thing, in different modules, without stating their relationship:**

> **FR-ACC-004** (MVP, MUST, trace N-01): "The system shall maintain a user profile of **canonical personal attributes** derived from documents and editable by the user."

> **FR-INF-001** (MVP, MUST, trace N-01): "The system shall maintain a **structured record** of the user's personal information, assembled from all processed documents."

Both trace to N-01. Both are derived from documents. Both are user-editable (FR-INF-003 supplies the editability for the second). Nothing in the specification distinguishes them.

**Finding: REQUIREMENTS GAP (G-19).** Either these are one concept named twice — a duplication the specification's own §15 "Non-duplicated" criterion claims not to contain — or they are two, and the difference is undefined.

**RECOMMENDATION (not a requirement):** treat them as **one store with two views**: a single set of canonical attributes (the FR-ACC-004 profile) whose values are supported by per-document observations (the FR-INF-001 record). The profile is then not a second copy but the resolved view over the observations, which also gives FR-INF-003, FR-INF-006, and AC-US-005-1 somewhere coherent to attach. **Requires PM confirmation** — if PM intends the profile to be an independent, user-owned record that extraction merely proposes into, that is a materially different model, and it must be said before either is built.

## D-08.3 Correction persistence across reprocessing

**This is a REQUIREMENT, and one of the sharpest in the sprint:**

> **AC-US-004-3**: "GIVEN a value the user has corrected, WHEN the document is later reprocessed, THEN the user's value is **retained and is not overwritten by extraction**."

> **FR-INF-003**: "a user-supplied value shall become authoritative over any extracted value."
> **BR-012** (User precedence): "A value entered or corrected by the user always takes precedence over an extracted value and **is never overwritten automatically**."

**Structural consequence — this is forced by the requirements, not chosen:** an extraction result and a user's value cannot occupy the same storage slot. If reprocessing writes into the same place the correction lives, AC-US-004-3 fails. The model must separate:

- **observations** — what a given extraction run read from a given document, with its confidence and region; superseded by later runs;
- **the authoritative value** — what the user's record says, which a user correction sets and which extraction may only *propose* into when no user value exists.

**Remaining DECISION REQUIRED:** what a *new* extraction result that differs from a user's correction should do. Three readings are consistent with the specification: (a) silently retained as an alternative (FR-INF-006 retains alternatives); (b) raised as a conflict (FR-INF-004 speaks of "two documents", so a document-vs-user disagreement is arguably out of its scope); (c) discarded. **RECOMMENDATION:** (a) — retain as an alternative and do not raise a conflict, because BR-012 has already settled the precedence and raising a conflict would re-ask a question the user has answered. **This is not specified; PM must decide.**

## D-08.4 Attribute-level idempotency

> **NFR-REL-005** (MVP, SHOULD): "Repeating the same operation on the same input shall not produce duplicate documents or **duplicate attribute entries**."

The document half is already solved: Sprint 3's unique index on `(user_id, checksum_sha256)` makes duplicate documents impossible at the database level. The attribute half is not, and it is harder.

**REQUIREMENTS GAP (G-20): the specification never defines when two attribute entries are "duplicates".** Candidate identities, none of which the specification chooses between:

| Candidate identity | Consequence |
| --- | --- |
| (document, canonical attribute) | One value per attribute per document. Cannot represent a document that legitimately contains two values for one attribute (two addresses on a bank statement). |
| (document, canonical attribute, occurrence) | Handles repetition, but "occurrence" must be stable across re-runs, which is exactly what an OCR re-run does not guarantee. |
| (document, canonical attribute, extraction run) | Never collides, but then re-running *always* creates new rows, so NFR-REL-005 is not satisfied by identity at all — it must be satisfied by superseding. |
| (document, canonical attribute, normalised value) | Uses FR-INF-008 normalisation as the identity function. Requires the normalisation rules, which require the vocabulary (G-13). |

**RECOMMENDATION (not a requirement):** make extraction **run-scoped and superseding** — each run produces a complete observation set for that document, and the previous run's set is superseded rather than merged. Idempotency is then a property of the *run*, keyed on (document, engine version, configuration version), which is checkable before work begins and satisfies NFR-REL-005 without needing a stable per-attribute identity. **PM/architecture must confirm**, because it implies retaining superseded observation sets or accepting their loss — which touches FR-INF-006 (retain the alternatives) and FR-INF-009 (change history).

**Blocking status:** **BLOCKED — REQUIREMENTS GAP** for G-19 and G-20; blocked by G-12/G-13 for anything attribute-shaped; **READY** for job, status, failure, and provenance concepts.

---
# D-09 — Asynchronous processing

## D-09.1 REQUIREMENT — the four requirements that constrain the choice

| ID | Requirement | Priority | What it forces |
| --- | --- | --- | --- |
| **NFR-PERF-002** | "Document processing shall be asynchronous; the user shall never be blocked waiting for it and shall be able to continue using the application." | MVP **MUST** | Processing must not occur in the upload request. Non-negotiable. |
| **NFR-REL-002** | "Interrupted document processing shall be recoverable; **the uploaded original shall never be lost because processing failed**." | MVP **MUST** | Two obligations: the original survives (Sprint 3 already satisfies this — the file is written and committed before any processing exists), and interrupted processing is *recoverable*, which means work-in-flight must survive the interruption. |
| **NFR-REL-005** | "Repeating the same operation on the same input shall not produce duplicate documents or duplicate attribute entries." | MVP SHOULD | Redelivery must not double-write. See D-08.4. |
| **NFR-SCL-002** | "Document processing load shall be able to grow independently of interactive traffic." | MVP SHOULD | Processing capacity must be separately scalable from the API. |

Supporting: FR-UPL-005 (the five visible states: queued, processing, ready, needs review, failed); FR-OCR-009 (retain original, state the failure, offer retry and manual entry); FR-OCR-010 (user-requested reprocessing); NFR-ERR-003 (partial success reported as partial); NFR-SCL-001 (strongly seasonal demand).

## D-09.2 Option comparison

### Option A — In-process background task (e.g. framework background tasks / an in-process worker thread)

| Dimension | Assessment |
| --- | --- |
| Reliability | **Fails NFR-REL-002.** Work in flight lives only in the process. A deploy, a crash, or an autoscaler terminating an instance loses it. |
| Restart behaviour | A document is left at `processing` with nothing that will ever advance it. That state is a lie to the user, which NFR-ERR-002 and BR-016 both weigh against. |
| Idempotency | No natural mechanism; nothing re-delivers, so there is nothing to deduplicate — but nothing recovers either. |
| Scalability | **Fails NFR-SCL-002.** Processing capacity is the API's capacity by construction. |
| Operational complexity | Lowest. No new component. |
| Suitability for DOCURA | **Not suitable.** It satisfies only NFR-PERF-002, the easiest of the four. |

### Option B — Durable job table plus a worker process

| Dimension | Assessment |
| --- | --- |
| Reliability | **Satisfies NFR-REL-002.** The job is a committed database row. If a worker dies, the claim expires and the job is picked up again. Nothing in flight is lost with a process. |
| Restart behaviour | Jobs resume after a restart with no operator action. A stuck claim is visible as data, which is also what makes FR-UPL-005's `processing` state honest. |
| Idempotency | Natural home: an attempt counter, a claim token, and a unique key on the job (see D-08.4). Supports NFR-REL-005 directly. |
| Scalability | **Satisfies NFR-SCL-002.** Workers are a separate process and scale independently; PostgreSQL `SELECT … FOR UPDATE SKIP LOCKED` makes multiple workers safe without a broker. |
| Operational complexity | Moderate: one additional long-running process and one table. No new infrastructure dependency — the database is already there, already backed up, already in the migration story. |
| Suitability for DOCURA | **Highest.** It is the smallest architecture that satisfies all four requirements, and it keeps job state inspectable with the same tools as the rest of the record. |

### Option C — External queue or broker (Redis/RabbitMQ/SQS-class, or a task framework over one)

| Dimension | Assessment |
| --- | --- |
| Reliability | Satisfies NFR-REL-002 if the broker is durable and acknowledgements are configured correctly. Introduces a second store that can disagree with the database — a job can be acknowledged while its transaction rolled back, or vice versa. |
| Restart behaviour | Good, subject to correct acknowledgement semantics. |
| Idempotency | Most brokers are at-least-once, so deduplication is *mandatory*, not optional — the same work as Option B, plus broker semantics. |
| Scalability | Excellent, and beyond what NFR-SCL-002 (a SHOULD) asks for at MVP volumes. |
| Operational complexity | Highest: another service to deploy, secure, monitor, back up, and reason about during incidents; and NFR-SEC-002 now has a second data-at-rest surface if payloads carry anything sensitive. |
| Suitability for DOCURA | Premature. It solves throughput problems the MVP does not have, at the cost of a distributed-consistency problem it would then have. |

### Option D — Other appropriate architectures considered

| Variant | Assessment |
| --- | --- |
| **Transactional outbox + worker** | Effectively Option B with a stricter write discipline. Worth adopting *within* Option B: create the job in the same transaction as the document row, so a document can never exist without its job. Recommended as a detail, not a separate option. |
| **Database `LISTEN/NOTIFY` wake-up over a polling worker** | An optimisation to Option B that reduces idle latency. Must remain an optimisation: correctness has to survive a missed notification, so polling stays as the floor. |
| **Serverless function per document** | Satisfies NFR-SCL-002 and NFR-PERF-002; complicates NFR-REL-002 (retry semantics are the platform's, not DOCURA's) and adds a deployment surface. Reasonable later; unjustified now. |
| **Synchronous processing with a longer request** | Directly violates NFR-PERF-002. Excluded. |

## D-09.3 RECOMMENDATION — D-09

**Option B — a durable job table with a separate worker process, jobs created in the same transaction as the document, claimed with `SKIP LOCKED`, and retried with a bounded attempt count.**

This is the smallest architecture that genuinely satisfies all four requirements. Option A fails two of them outright; Option C satisfies them at a cost the MVP has no reason to pay, and adds a consistency problem.

Two design notes that follow from the requirements rather than from preference:

1. **Job state and document status are not the same thing.** FR-UPL-005 defines five *user-visible* states; a job additionally has attempts, claims, timing, and errors that the user should never see (NFR-ERR-004). **RECOMMENDATION:** model them separately and derive the document's status from the job's, so that FR-UPL-005 stays exactly the five states the requirement names — the discipline Sprint 3 already applied to `DocumentStatus`. **DECISION REQUIRED** — this is a real modelling choice with a maintenance cost.
2. **Automatic retry is not required.** FR-OCR-009 requires that the system "offer a retry" — a user-facing affordance. Retrying automatically on a transient failure is sensible, but it is an **ARCHITECTURE DECISION**, and the retry ceiling, backoff, and the point at which a document becomes `failed` are unspecified in the requirements.

**Blocking status:** **BLOCKED — ARCHITECTURE DECISION REQUIRED**, but the decision is small, well-supported by the requirements, and can be taken immediately. It does not depend on D-00, D-01, or the evaluation. **This is the part of Sprint 4 most ready to proceed.**

## D-09.4 DECISION — Option B adopted — 8 September 2026

**Status: DECIDED (engineering). Option B is adopted and implemented as the first Sprint 4 coding milestone.** This closes the D-09.3 "ARCHITECTURE DECISION REQUIRED" hold. It is an **engineering** decision — it needs no Product Management input and no evaluation evidence — recorded here for the same audit trail as every other decision. It reopens nothing: D-00, D-01, G-12, G-13, G-14/G-15, and the S-6 evaluation are untouched.

**Consistency check against `backend/step3.pdf` and prior decisions.** Option B satisfies each constraining requirement without inventing any: **NFR-PERF-002** (processing off the request path — a worker outside the API), **NFR-REL-002** (a durable, committed job row survives restart; the original is already preserved by Sprint 3), **NFR-REL-005** (one job per document via a unique key — redelivery cannot double-write), **NFR-SCL-002** (the worker is a separate process, independently scalable). It stays behind the existing **D-01** extraction port (`app/services/extraction.py`), so no OCR engine, field set (**G-12**), threshold (**BR-001**), or sensitivity tier (**G-14/G-15**) is selected or assumed. `backend/step3.pdf` is unchanged.

**The two D-09.3 design notes, resolved:**

| Note | Resolution as built |
| --- | --- |
| 1 — job state ≠ document status | **Adopted.** A new `processing_jobs` table carries the internal machinery (state, attempts, claim time, internal error). `Document.status` stays exactly the five **FR-UPL-005** states; the pipeline derives it from job outcome. Internal error text lives on the job and is never returned to a user (**NFR-ERR-004**); a **user-facing** `documents.failure_reason` carries the "state what failed" half of **FR-OCR-009**. |
| 2 — automatic retry ceiling | **Bounded automatic retry.** A failed attempt is retried until a configured ceiling (`worker_max_attempts`, default 3), after which the document becomes `failed`. The retry is engineering's choice under NFR-ERR-005; the ceiling, claim-reclaim timeout, and poll interval are configuration (**NFR-MNT-004** posture), not requirements. |

**What is built (this milestone):** the `processing_jobs` table + migration; a job created **in the same transaction** as the document (transactional outbox, D-09.2 Option D note); worker claim via `SELECT … FOR UPDATE SKIP LOCKED` with stale-claim reclaim; bounded retry; the five status transitions; **FR-OCR-009** failure state + reason; **FR-OCR-010** user-requested reprocessing; a worker entrypoint/loop. The `UnconfiguredExtractor` remains in place, so the failure path is exercisable end-to-end today.

**What is deliberately NOT built (unchanged by this decision):** no OCR engine (D-01, evaluation-dependent), no field extraction (**G-12** / FR-OCR-004), no confidence thresholds (**BR-001**), no sensitivity tiers (**G-14/G-15**), no conflict detection (FR-INF-004). On success the pipeline records `ready` and does not yet persist extracted content — there is no field/text model to hold it, and authoring one is FR-OCR-004 / FR-INF work.

**Owner:** Engineering. **No `backend/step3.pdf` change, no G-14/G-15 change, no commit or push as part of recording this decision.**

---

# D-10 — Security / encryption

## D-10.1 REQUIREMENT — what the specification actually requires

| ID | Requirement | Priority |
| --- | --- | --- |
| **NFR-SEC-002** | "**Documents and extracted information** shall be encrypted at rest." | MVP MUST |
| NFR-SEC-001 | "All data in transit shall be encrypted using current industry-standard transport security." | MVP MUST |
| NFR-SEC-003 | "Every request for a document or attribute shall be authorised against the requesting user's identity; ownership shall never be inferred from an identifier supplied by the client." | MVP MUST |
| NFR-SEC-007 | "Document access links shall be time-limited and single-purpose; a link shall not grant standing access." | MVP MUST |
| NFR-SEC-008 | "The system shall not claim to be unbreachable… Security statements shall describe specific measures and their limits." | MVP MUST |
| NFR-SEC-009 | "The product shall undergo independent security review before any release to users outside the team." | MVP SHOULD |
| NFR-PRIV-002 | Not used to train shared models; not readable by other users under any circumstance. | MVP MUST |
| NFR-PRIV-003 | "Deletion… shall remove the document, its extracted information, and its derived copies within a stated period. Period: TBD." | MVP MUST |
| §9, Table 9.1 | "Secure handling — Encryption in transit and at rest; time-limited, single-purpose document access." | — |
| §7.1 lifecycle, Access control | "authorise every access…; encrypt at rest and in transit." | — |

**The whole of the encryption-at-rest requirement is the eleven words of NFR-SEC-002.** That is the complete text. Note two things it does say, precisely: it names **extracted information** as well as documents — so Sprint 4's new data is squarely in scope — and it does not qualify "at rest" in any way.

## D-10.2 What the specification does NOT define

| # | Gap |
| --- | --- |
| **G-21** | **What "encrypted at rest" means.** Full-disk or volume encryption, storage-service-managed encryption, application-level envelope encryption, or column-level encryption all satisfy the sentence as written and differ enormously in what they protect against. Without a stated threat model there is no way to test NFR-SEC-002 — which sits awkwardly against §15's "Testable" criterion. |
| **G-22** | **Key management is entirely absent.** No requirement in `step3.pdf` mentions keys: not generation, storage, separation from data, rotation, escrow, or destruction. **No key-management design is proposed in this register**, because there is nothing to derive one from. |
| **G-23** | **The encryption boundary is undefined.** Whether database backups, replicas, logs, temporary files created during processing, and any external processor's transient copies fall inside "at rest" is not stated. Processing inherently creates intermediate artefacts — decoded page images, text buffers — and the specification does not address them. |
| **G-24** | **Deletion and encryption are not connected.** NFR-PRIV-003 requires removal "within a stated period" (TBD). Whether crypto-erasure counts as removal is unaddressed. |
| — | **Storage backend.** Not specified anywhere, correctly — that is Step 4's decision under §6's Selection Principle. Sprint 3 already made the right structural move: `app/services/storage.py` defines a `DocumentStorage` port and documents that its local filesystem implementation "provides no encryption at rest, so a deployment that must satisfy NFR-SEC-002 either mounts an encrypted volume underneath it or substitutes a backend that encrypts." **This means NFR-SEC-002 is currently unmet in the default local configuration — an existing, known, documented gap inherited from Sprint 3, not one Sprint 4 introduces.** |

## D-10.3 The constraint the requirements create between encryption and search

This is the substantive engineering finding of D-10, and it is forced by two MUST requirements pulling against each other:

- **NFR-SEC-002** requires **extracted information** to be encrypted at rest.
- **FR-SRCH-002** (MVP, MUST): "The user shall be able to search **the extracted text** of all documents."
- **FR-SRCH-003** (MVP, SHOULD): "The user shall be able to search **by attribute value** and receive the supporting document."
- **FR-SRCH-004** (MVP, SHOULD): results "shall identify the document and the location within it where the match occurred."

Naive application-level encryption of the extracted-text column makes FR-SRCH-002 impossible: an encrypted column cannot be indexed or searched by the database. The options are all consequential, and none is chosen by the specification: encrypt at the storage layer beneath the database (search works, protection is against media theft only); encrypt in the application and search over a separately protected index (search works, the index becomes a second copy that NFR-PRIV-003 must also delete); or use a searchable-encryption scheme (leaks patterns, adds significant complexity, and would itself need security review under NFR-SEC-009).

**This tension is not visible from NFR-SEC-002 alone, and Sprint 4 is where it becomes concrete**, because Sprint 4 is what creates the extracted text.

## D-10.4 RECOMMENDATION — D-10

1. **Ask PM/Security to state the threat model** NFR-SEC-002 is meant to defeat, and amend the specification with it (G-21). Everything else follows from that sentence, and nothing can be tested without it.
2. **Do not invent a key-management design.** State the gap (G-22) and let Step 4 — System Architecture — resolve it with security input, per §6.
3. **Resolve the search/encryption tension explicitly and record the decision**, rather than letting it be settled implicitly by whichever of FR-SRCH-002 or NFR-SEC-002 is implemented first.
4. **Keep the storage port as the encryption seam** (the Sprint 3 pattern), so the decision remains substitutable.
5. **Note NFR-SEC-009** — independent security review before release outside the team — and §10.3's SCOPE CONDITION: "Two exclusions — two-factor authentication and independent security review — must be closed before any user outside a controlled pilot stores a real identity document." **This directly constrains D-02: acquiring a corpus of real identity documents from real people is arguably exactly the situation that condition describes.**

**Blocking status:** **BLOCKED — REQUIREMENTS GAP** (G-21 … G-24) for a defensible encryption design; **NOT BLOCKING** for building the extraction pipeline, provided the encryption seam is not designed out.

---

# D-11 — Observability

## D-11.1 REQUIREMENT — what is required for Sprint 4

| ID | Requirement | Applies to Sprint 4? |
| --- | --- | --- |
| **NFR-OBS-001** (MUST) | "The system shall measure extraction and field-interpretation confidence distributions **in aggregate, without retaining the underlying values**." | **Yes** — the extraction half is Sprint 4's |
| **NFR-OBS-004** (MUST) | "Failures in detection, extraction, or matching shall be recorded with enough context to diagnose them, **and without personal values**." | **Yes** — the extraction half is Sprint 4's |
| NFR-OBS-002 (MUST) | "measure how often it acts, asks, and declines to act" | Partly — "declines to act" includes withholding a below-threshold value (FR-OCR-006); the act/ask counters belong to the filling loop |
| NFR-OBS-003 (MUST) | "measure user override rate on automatically filled fields as the primary indicator of silent error" | No — form filling, a later sprint. But note FR-INF-003 corrections are the same signal for extraction, and the specification does not require measuring *those*. |
| NFR-OBS-005 (SHOULD) | onboarding abandonment by stage, to test A-6 | No |
| **NFR-PRIV-007** (MUST) | "Diagnostic and analytics data shall exclude document contents and extracted personal values." | **Yes — the binding constraint on all of the above** |
| NFR-ERR-004 (SHOULD) | "Errors shall never expose internal identifiers, stack traces, or infrastructure detail to the user." | Yes |
| NFR-ERR-001 (MUST) | "Every error message shall state what went wrong and what the user can do next." | Yes — FR-OCR-009 requires the failure reason to be stated |
| NFR-ERR-003 (MUST) | "Partial success shall be reported as partial, itemising what succeeded and what did not." | Yes — EC-002 (poor-quality document) is precisely a partial success |
| FR-AUD-001…006 | The history of DOCURA's actions in form sessions | **No** — FR-AUD is about form-filling actions. Extraction history is FR-INF-009, a different requirement with a different subject. |

**The requirement pair that defines the difficulty:** NFR-OBS-004 demands "enough context to diagnose", and NFR-PRIV-007 forbids the personal values that would usually constitute that context. Sprint 3 already met this pattern — `app/core/logging.py` applies redaction before anything reaches a sink, and its module docstring records that the two obligations "pull against each other".

## D-11.2 What the specification does NOT specify

| Area | Status |
| --- | --- |
| **Processing events** | No requirement obliges an event to be emitted per state transition. FR-UPL-005 requires the status to be *shown*; it says nothing about logging. **Not specified.** |
| **Retries** | No observability requirement mentions retries at all. **Not specified** (G-25). |
| **Operational log format, levels, destinations, retention** | **Not specified.** Engineering's choice, constrained only by NFR-PRIV-007. |
| **Security-relevant events** | **REQUIREMENTS GAP (G-26).** No requirement in `step3.pdf` obliges the recording of authentication, authorisation-failure, or access events. NFR-OBS-004 covers detection/extraction/matching failures — not security events. FR-AUD covers DOCURA's form actions, not access to the vault. For a product holding identity documents this is a genuine gap, and NFR-SEC-009's independent review will raise it. |
| **Request correlation** | **Not specified** by any requirement. Sprint 3 nevertheless implements request IDs (`app/core/errors.py` returns `request_id` in error bodies) — an engineering practice ahead of the requirements, which is fine and should be noted as such rather than back-justified as compliance. |
| **Sensitive data in logs** | **Specified** — NFR-PRIV-007 (MUST), reinforced by NFR-OBS-001 ("without retaining the underlying values") and NFR-OBS-004 ("without personal values"). This is the one part of D-11 that is fully determined. |
| **Where aggregate metrics live** | **Not specified.** NFR-OBS-001 requires measurement, not a mechanism. |

## D-11.3 Assessment

**No logging changes are proposed or made here.** For Sprint 4, the observability position is:

- **Required and implementable now:** confidence distributions in aggregate with no underlying values (NFR-OBS-001); failure records with diagnostic context and no personal values (NFR-OBS-004); user-facing failure reasons that state what to do next without internals (NFR-ERR-001, NFR-ERR-004); partial success reported as partial (NFR-ERR-003).
- **Required but not yet specified in mechanism:** where aggregate measurements are stored and how they are read.
- **Gaps needing amendment:** retry observability (G-25); security-event logging (G-26).

**RECOMMENDATION:** extend the existing redaction discipline to every new extraction code path rather than building a second logging mechanism, and treat "may this value appear in a log?" as a property of the canonical attribute definition (D-05.4) once that vocabulary exists — which makes NFR-PRIV-007 enforceable by construction rather than by review.

**Blocking status:** **NOT BLOCKING.** No observability question prevents Sprint 4 from starting.

---

# D-12 — Acceptance criteria: US-003, US-004, US-005

**The criteria below are reproduced from §4 of the specification without alteration.** Nothing is weakened, rewritten, or summarised; the mapping columns are additive.

## D-12.1 US-003 — Have documents read and understood automatically

> **US-003** (MVP, MUST): "As a student, I want DOCURA to read my documents and pull out the information inside them, so that my records become usable data instead of pictures I have to read myself." *Traces: RC-1 · L2 · N-01.* Requirements per Table 3.1: FR-OCR-001…009.

| AC | Criterion (verbatim) | Requirement | Dependency | Decision | Evaluation | Implementation |
| --- | --- | --- | --- | --- | --- | --- |
| **AC-US-003-1** | "GIVEN the user has uploaded a semester marksheet, WHEN DOCURA processes it successfully, THEN the document appears in the vault classified as a marksheet with its extracted information attached." | FR-OCR-002, FR-OCR-003, FR-OCR-004, FR-DOC-002 | D-01 (engine), D-04 (type set), D-05 (fields) | **D-04.5 (G-10) — "semester marksheet" vs §7.1's "semester result" must be resolved before this can be written as a test**; D-05 field set | **Yes** — §7.1 makes inclusion of this type conditional on S-6 | Classifier, extractor, attribute persistence |
| **AC-US-003-2** | "GIVEN a processed document, WHEN the user views it, THEN every extracted field is shown with its own confidence indication." | FR-OCR-005, FR-OCR-003 | D-03 (confidence model) | How confidence is presented (D-03.5, product decision) | Not for the mechanism; yes for the values | Per-field confidence stored and exposed by the API |
| **AC-US-003-3** | "GIVEN a document whose type cannot be determined confidently, WHEN processing completes, THEN it is stored as unclassified, the user is asked to identify it, and no type is assumed." | FR-OCR-002, AR-AST-002, EC-003, FR-DOC-002 | D-03 (a classification threshold is implied by "confidently"), D-01 (engine must be able to abstain) | Which threshold governs classification — the specification names a *review* threshold and an *automatic-action* threshold, and does not say which applies to classification (**part of G-05**) | **Yes** — D-02.n: the corpus must contain out-of-set documents or abstention is never measured | `unclassified` state (already modelled in Sprint 3), plus the ask path |
| **AC-US-003-4** | "GIVEN a document of five pages, WHEN it is processed, THEN it is stored as one document and information from every page is available." | FR-OCR-008 | D-01 (multi-page handling), D-08 (extracted-text granularity) | Whether page provenance is retained per value (ties to FR-OCR-007 and D-08's source-region decision) | **Yes** — D-02.j: the corpus must contain multi-page documents | Multi-page pipeline, per-page text retention |
| **AC-US-003-5** | "GIVEN processing fails, WHEN the user views the document, THEN the original file is still present and downloadable, the failure reason is stated, and both retry and manual entry are offered." | FR-OCR-009, EC-001, NFR-REL-002, NFR-ERR-001, NFR-ERR-005 | D-09 (job/failure state) | **Manual entry is an unresolved surface** — FR-OCR-009 requires "a manual-entry path", and no requirement defines what manual entry writes to when the field definitions do not exist (D-05). Registered as **G-27**. | No | Failure state, reason, retry endpoint, manual-entry path |

**Note on AC-US-003-5:** the original-file half is **already satisfied by Sprint 3** — the file is stored and downloadable independently of any processing. The failure-reason and retry halves are Sprint 4's, and the manual-entry half is blocked by the field-definition gap.

## D-12.2 US-004 — See and correct what DOCURA understood

> **US-004** (MVP, MUST): "As a careful applicant, I want to see exactly what DOCURA read from each document and correct anything that is wrong, so that I can trust what it will later put into my forms." *Traces: N-05 · A-7 · R-4.* Requirements per Table 3.1: FR-OCR-007, FR-INF-002/003.

| AC | Criterion (verbatim) | Requirement | Dependency | Decision | Evaluation | Implementation |
| --- | --- | --- | --- | --- | --- | --- |
| **AC-US-004-1** | "GIVEN a processed document, WHEN the user opens an extracted value, THEN the source document and the region the value was read from are shown." | FR-OCR-007 (SHOULD), FR-INF-002, AR-AST-006, BR-010 | D-01 (the engine must return geometry), D-08 (region representation) | **Region representation is undefined** (D-08.1) — coordinate space, page reference, and what is stored when the engine returns no geometry | No | Region capture and exposure |
| **AC-US-004-2** | "GIVEN an incorrect extracted value, WHEN the user corrects it, THEN the corrected value becomes authoritative and is used for all subsequent form filling." | FR-INF-003, BR-012 | D-05 (attributes must exist to be corrected), D-08.2 (profile vs attributes) | G-19 — what the corrected value is authoritative *within* | No | Correction endpoint, authoritative-value model |
| **AC-US-004-3** | "GIVEN a value the user has corrected, WHEN the document is later reprocessed, THEN the user's value is retained and is not overwritten by extraction." | BR-012, FR-INF-003, FR-OCR-010 | D-08.3 | What a *differing* new extraction does — retain as alternative, raise a conflict, or discard (D-08.3) | No | Observation/authoritative-value separation. **This criterion is the strongest single constraint on the Sprint 4 data model.** |
| **AC-US-004-4** | "GIVEN an extracted value below the review threshold, WHEN the record is used for filling, THEN that value is never placed automatically." | FR-OCR-006, BR-002 | D-03 (threshold), and the filling loop is a later sprint | Whether `needs_review` is stored or derived (D-08.1) | **Yes** — the threshold value comes from S-6 | The withholding mechanism is testable at the threshold now, per §4's preamble; the *filling* half is a later sprint |

## D-12.3 US-005 — Resolve conflicting information between documents

> **US-005** (MVP, MUST) — Table 3.1: "Resolve conflicting information between documents." Requirements: FR-INF-004/005/006.

| AC | Criterion (verbatim) | Requirement | Dependency | Decision | Evaluation | Implementation |
| --- | --- | --- | --- | --- | --- | --- |
| **AC-US-005-1** | "GIVEN two documents give different values for the same attribute, WHEN processing completes, THEN a conflict is raised and neither value is marked authoritative." | FR-INF-004, AR-DET-008, BR-004, EC-004 | **D-05 (G-13, canonical vocabulary) — "the same attribute" has no definition without it**; FR-INF-008 normalisation rules | What counts as "different" after normalisation (D-08.1); the "no authoritative value" state must be representable | **Yes** — D-02.m: without person-grouped conflicting documents in the corpus, this is never evaluated | Deterministic conflict detection; a conflict entity |
| **AC-US-005-2** | "GIVEN an unresolved conflict on an attribute, WHEN a form requests that attribute, THEN DOCURA treats the field as ambiguous and asks rather than choosing." | FR-INF-005, FR-AMB-001, BR-003, BR-004 | The form loop is a later sprint | None for Sprint 4 beyond exposing conflict state | No | Sprint 4 must expose unresolved-conflict state so the later loop can honour it |
| **AC-US-005-3** | "GIVEN the user resolves a conflict, WHEN the resolution is saved, THEN the chosen value becomes authoritative, the alternative is retained, and the decision appears in history." | FR-INF-005, FR-INF-006, FR-INF-009, FR-AUD-005 | D-08 (alternatives, history) | Which history store the decision appears in — attribute history (FR-INF-009, SHOULD) or session history (FR-AUD, a different subject). **The specification does not say** (G-28). | No | Resolution endpoint, alternative retention, history entry |

## D-12.4 Cross-cutting note

**No criterion above is weakened, and none is marked "not applicable".** Where a criterion cannot yet be turned into a test, the cause is named: a gap (G-10, G-13, G-27, G-28), a decision (D-03, D-08), or an evaluation (S-6 / AR-AST-008). US-005 is the story most completely blocked — every one of its criteria depends on the canonical attribute vocabulary that does not exist.

---
# FINAL DECISION REGISTER

| ID | Decision / Question | Relevant Requirement | What the Specification Says | What Is Missing | Options | Recommendation | Blocking Status | Owner / Approval Required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **D-00** | Does Sprint 4 build the A-7-dependent requirements before study S-6 reports? | §12.3, §15, A-7, FR-OCR-004/005/006, BR-001 | "must not be committed to build until their supporting assumption reports" | Nothing — the specification is clear; a scope decision is owed | 1 Full sprint · 2 Split sprint · 3 Suspend | **Option 2** — build the A-7-independent envelope | **BLOCKING** (sprint shape) | Product Management |
| **D-01** | Which OCR / processing architecture? | FR-OCR-001…005/007, AR-AST-001/002/006/007/008, NFR-MNT-001/002, NFR-PRIV-002/006, NFR-SEC-002, NFR-PERF-002, NFR-SCL-002 | Guarantees only; "Technology selection belongs to document 04" (§6) | The selection itself, and the evaluation that should inform it | A on-device · B self-hosted · C external · D hybrid | **Option D (narrow)** behind one extraction port; choose the assisted engine on evaluation evidence, not now | **BLOCKING** for FR-OCR-001…005 | Architecture (Step 4); PM for privacy posture if external |
| **D-01a** | Does NFR-PRIV-008 exclude on-device processing as an implementation choice? | NFR-PRIV-008, NFR-PRIV-006, §10.3, §11 H5 | Defers a *user-facing mode* of entirely-on-device processing with reduced capability | Any statement of where MVP processing actually occurs | Broad reading · narrow reading · amend | **REQUIREMENTS GAP (G-01)** — amend the specification to state the MVP processing location | Not blocking implementation; **BLOCKING** the NFR-PRIV-006 disclosure text | Product Management |
| **D-02** | How is the held-out corpus obtained, governed, and destroyed? | AR-AST-008, §7.1, ASM-001, BR-001, A-7, NFR-PRIV-002 | Real, imperfect, held-out, before any threshold is set | Size, ownership, consent, acquisition, retention, destruction, coverage, pass criteria, evidence artefact, re-evaluation trigger | Volunteer · paid panel · staff · public-record | Treat as a product deliverable with a named owner; group documents by person; define "pass" before running. **No size proposed.** | **BLOCKING — EVALUATION REQUIRED** | PM + Legal + Engineering |
| **D-03** | What is the confidence model, and what are the thresholds? | FR-OCR-003/005/006, BR-001, BR-002, AR-DET-004, AR-AST-007/008, NFR-MNT-002, NFR-OBS-001 | Two named thresholds; deterministic comparison; externally configurable; confidence never raised; evaluation first | Both values; their relationship; scale and semantics; global vs per-type; document-vs-field interaction; missing-value semantics | Global · per-type · per-type override on a global default | Build the structure now; allow a per-type override but populate none; derive both values from evaluation. **No numbers proposed.** | **BLOCKED — EVALUATION REQUIRED** for values; **READY** for structure | PM (presentation, global vs per-type); Engineering (structure) |
| **D-04** | What is the MVP document-type set? | §7.1, ASM-001, FR-OCR-002, FR-DOC-002, AR-AST-002, EC-003, NFR-USE-005 | Twelve candidate types plus an unclassified fallback; "Final inclusion of each type is subject to the extraction evaluation in study S-6" | Which types survive evaluation; definitions for address proof, student ID, hall ticket; the "store-and-search only" state | Confirm all · reduce · defer | **Do not finalise the set.** Only the unclassified fallback is unconditional. | **BLOCKED — EVALUATION REQUIRED**; plus gaps G-08…G-11 | Product Management |
| **D-04a** | Are "semester result" and "semester marksheet" the same type? | §7.1 vs AC-US-003-1, NFR-USE-005 | §7.1 says "semester result"; AC-US-003-1 says "semester marksheet… classified as a marksheet" | Which of three readings is intended | Same · distinct · family | **REQUIREMENTS GAP (G-10)** — resolve before AC-US-003-1 becomes a test | **BLOCKING** for AC-US-003-1 | Product Management |
| **D-04b** | Do photograph and signature have information requirements? | §7.1, FR-OCR-004, FR-INF-007, FR-MATCH-006 | Lists both as supported types; says nothing about their fields | Whether they extract at all | Extract · classify-and-attach only | **Classify-and-attach only** — requires PM approval; **REQUIREMENTS GAP (G-11)** | **BLOCKING** for their field sets | Product Management |
| **D-05** | What are the per-type field definitions and the canonical attribute vocabulary? | FR-OCR-004, FR-INF-001/004/007/008, FR-ACC-004, NFR-MNT-001 | That a "defined set of information fields" exists per type, and that types and fields are configuration | **Every field, for every type, and the entire canonical vocabulary** | Author now · author after evaluation · derive from the engine | Author the vocabulary first, then per-type field sets, both as reviewed configuration. **Never derive from the engine.** **No fields invented.** | **BLOCKING — REQUIREMENTS GAP (G-12, G-13).** The largest gap in the sprint. **G-13's *shape* APPROVED 5 September 2026 (D-05.6), REVISED 6 September 2026 and the revision APPROVED 6 September 2026 (D-05.8: G-13.2, G-13.5, G-13.9; new G-13.15; G-13.11's trigger clarified). *Contents:* PD-B APPROVED 7 September 2026 (D-05.11) — `v0.1-draft` (one entry, one-attribute scope, N-TEXT). PD-A, PD-C, PD-D, PD-E APPROVED 8 September 2026 (D-05.12); X12 MET the same day (D-05.13); X15 CLOSED the same day (D-05.14). **G-13-A is MET (8 Sep 2026).** The rest of the vocabulary contents and all of G-12 remain outstanding.** G-12 authoring was gated on **G-13-A**, which is now MET, so **G-12 authoring is unblocked** — its own gaps (G-09/G-10/G-11, C-a…C-d, the mock-form inventory) still stand. | Product Management (content); Engineering (format) |
| **D-06** | What are the sensitivity classification rules? | FR-INF-007, FR-SENS-001/004/006, BR-020, AR-DET-005, AR-AST-007, NFR-MNT-004 | Three tier names; every attribute carries one; reviewable deterministic rule set; raise-only; consequential is a floor; sensitive values masked by default | The rules themselves; the default tier; document-level tier derivation; the masking boundary | Adopt doc 02's working table · author new rules · wait for A-5 | Build tier, raise-only invariant, and the configuration mechanism now. **Do not adopt doc 02 Table 13.1 as rules** — it is ASM-tagged, example-based, and A-5 says the boundary "must be set by users, not by us". Default unmapped attributes to *sensitive*. | **BLOCKED — REQUIREMENTS GAP (G-14…G-16)** and **EVALUATION REQUIRED** (A-5, S-1/S-4) | Product Management |
| **D-07** | When and how must off-device processing be disclosed? | NFR-PRIV-006, §9 Table 9.1 | Disclosure in plain language before the user's first upload | The definition of "processing"; whether Sprint 3 already triggers it; re-disclosure on change | Broad reading · narrow reading | Adopt the broad reading; **no acknowledgement and no persistence are required by the specification**; recommend recording disclosure version + timestamp as a *new, approved* obligation | **NOT BLOCKING** for backend work; **BLOCKING** before real documents are accepted | Product Management |
| **D-08** | What data concepts does Sprint 4 need, and how do profile, corrections, and idempotency work? | FR-OCR-001…010, FR-INF-001…009, FR-ACC-004, NFR-REL-005, AC-US-004-3 | The concepts, individually | The relationship between FR-ACC-004 and FR-INF-001; attribute-entry identity; behaviour of a new extraction that differs from a correction | See D-08.2 / D-08.3 / D-08.4 | One store, two views; observations separate from authoritative values; run-scoped superseding extraction | **BLOCKED — REQUIREMENTS GAP (G-19, G-20)**; blocked by G-12/G-13 for attributes | PM (G-19, correction semantics); Architecture (G-20) |
| **D-09** | Which asynchronous processing architecture? | NFR-PERF-002, NFR-REL-002, NFR-REL-005, NFR-SCL-002, FR-UPL-005 | Async, recoverable, idempotent, independently scalable | The mechanism | A in-process · B durable job table + worker · C external queue · D other | **Option B** — the smallest architecture that satisfies all four. Model job state separately from FR-UPL-005 document status. | **BLOCKED — ARCHITECTURE DECISION REQUIRED**, but resolvable immediately | Architecture |
| **D-10** | What does encryption at rest actually require? | NFR-SEC-002, NFR-SEC-007, NFR-PRIV-003, FR-SRCH-002/003 | "Documents and extracted information shall be encrypted at rest" — eleven words, no qualification | Threat model; key management; the encryption boundary; the relationship to deletion; resolution of the search/encryption tension | Volume · storage-service · application envelope · searchable scheme | Obtain a threat model before designing; keep the storage port as the seam; **do not invent a key-management design** | **BLOCKED — REQUIREMENTS GAP (G-21…G-24)** for a defensible design; not blocking pipeline work | PM + Security; Architecture (Step 4) |
| **D-11** | What observability does Sprint 4 owe? | NFR-OBS-001/004, NFR-PRIV-007, NFR-ERR-001/003/004 | Aggregate confidence distributions without underlying values; failures with diagnostic context and no personal values | Processing-event and retry observability; security-event logging; request correlation; retention; metric storage | — | Extend Sprint 3's redaction discipline; make "loggable" a property of the canonical attribute definition | **NOT BLOCKING**; gaps G-25, G-26 recorded | Engineering; PM for G-26 |
| **D-12** | Are US-003/004/005 acceptance criteria implementable as written? | US-003, US-004, US-005 and their criteria | All twelve criteria, reproduced unaltered above | Test-readiness for AC-US-003-1 (G-10), AC-US-003-5 manual entry (G-27), all of US-005 (G-13), AC-US-005-3 history location (G-28) | — | Preserve all criteria as written; resolve the named gaps rather than adjusting the criteria | **BLOCKING** where named | Product Management |

---

# 1. MUST DECIDE BEFORE CODING

Every item here must be resolved before Sprint 4 implementation begins. Items marked *(engineering-resolvable)* need a decision but not a specification amendment.

| # | Decision | Register entry | Owner | Why it cannot wait |
| --- | --- | --- | --- | --- |
| 1 | **Sprint shape under §12.3 / A-7** — full sprint, split sprint, or suspend | D-00 | PM | Determines what is in the sprint at all. Every other item is scoped by it. |
| 2 | **Canonical attribute vocabulary** — *definition **APPROVED** (D-05.6); **contents still owed*** | D-05.4, **D-05.6** (G-13) | PM | FR-INF-001/004/005/006/008 and all of US-005 are unimplementable without it. Nothing attribute-shaped can be modelled. The approved seven-property shape gives authoring a target; no attribute exists yet. **Revision APPROVED 6 Sep 2026 (D-05.8): property 6 is a scope-keyed cardinality, still seven properties, no eighth; closure splits into G-13-A and G-13-B. Neither gate is met.** **T1 authoring run 6 Sep 2026 (D-05.9) and completed the same day (D-05.10): one entry proposed as `v0.1-draft`, nine candidates not authored. N-TEXT now supplies the normalisation rule, so properties 1–6 are complete. PD-B APPROVED 7 Sep 2026 (D-05.11): `v0.1-draft`, its one-attribute scope, and N-TEXT.** **PD-A, PD-C, PD-D, PD-E APPROVED 8 Sep 2026 (D-05.12): X2, X4, X6, X8, X11, X13, X14, X17 now MET for `v0.1-draft` — every PM-owned gate-A criterion is met. X12 was MET the same day (D-05.13). X15 was closed the same day (D-05.14) by applying the fourth false-conflict attribution category at D-02 §11.6.1. **G-13-A is MET (8 Sep 2026).** G-13-B remains NOT MET (G-14/G-15; A-5/A-7); the gap stays OPEN pending the §11 amendment (X16).** |
| 3 | **Per-type field definitions** | D-05 (G-12) | PM | FR-OCR-004 is unimplementable as written for every type. |
| 4 | **Extraction architecture and the extraction port** *(engineering-resolvable, Step 4)* | D-01 | Architecture | Determines the shape of every interface Sprint 4 writes, and whether a third party sees documents. |
| 5 | **Asynchronous processing architecture** *(engineering-resolvable)* | D-09 | Architecture | The first thing built. Choosing wrongly (Option A) fails NFR-REL-002 and NFR-SCL-002 silently. |
| 6 | **Profile vs attributes** — one store or two | D-08.2 (G-19) | PM | Determines the central data model. Cannot be reversed cheaply once data exists. |
| 7 | **Correction vs re-extraction semantics** — what a differing new extraction does | D-08.3 | PM | AC-US-004-3 is testable only once this is answered. |
| 8 | **Attribute-entry identity for idempotency** *(engineering-resolvable)* | D-08.4 (G-20) | Architecture | NFR-REL-005 has no meaning for attributes until "duplicate" is defined. |
| 9 | **"Semester result" vs "semester marksheet"** | D-04.5 (G-10) | PM | AC-US-003-1 cannot become a test. |
| 10 | **Photograph and signature: extraction targets or not** | D-04.6 (G-11) | PM | Determines whether two of twelve types need field definitions at all. |
| 11 | **Address proof: what qualifies** | D-04.4 (G-09) | PM | A classifier cannot be built against an undefined class. |
| 12 | **Sensitivity rule list and default tier** | D-06 (G-14, G-15) | PM | FR-INF-007 requires *every* attribute to carry a tier from the moment attributes exist. |
| 13 | **Corpus governance: consent, ownership, retention, destruction** | D-02 (G-02) | PM + Legal | Real documents cannot be collected before this is settled. It gates the evaluation, which gates the thresholds. |
| 14 | **Encryption threat model for extracted information** | D-10 (G-21) | PM + Security | Extracted text is created in this sprint; retrofitting encryption after it exists is a migration. |
| 15 | **Search vs encryption resolution** | D-10.3 | Architecture + Security | FR-SRCH-002 (MUST) and NFR-SEC-002 (MUST) constrain the same column. |
| 16 | **Store-and-search-only state for a demoted type** | D-04.3 (G-08) | PM | §7.1 requires the state; the data model has nowhere to put it. |

---

# 2. CAN IMPLEMENT WITHOUT DECIDING

Only items explicitly supported by the requirements and free of unresolved dependencies appear here. Each cites the requirement that authorises it.

| # | Item | Authorising requirement | Note |
| --- | --- | --- | --- |
| 1 | **Durable processing-job persistence** — a job created with the document, surviving restart | NFR-REL-002, NFR-PERF-002 | Independent of which engine runs. Depends on D-09 only for the mechanism, and the mechanism is engineering's to choose. |
| 2 | **Processing status transitions across exactly the five FR-UPL-005 states** | FR-UPL-005 | The five states are named in the requirement and already modelled in `DocumentStatus`. No new state may be invented. |
| 3 | **Original-file preservation across processing failure** | NFR-REL-002, FR-OCR-009, EC-001 | Already satisfied by Sprint 3; must be preserved, and tested, not rebuilt. |
| 4 | **Failure recording with a stated reason, and a user-facing retry affordance** | FR-OCR-009, NFR-ERR-001, NFR-ERR-005, EC-001 | Reason text must not expose internals (NFR-ERR-004). |
| 5 | **User-requested reprocessing entry point** | FR-OCR-010 | The *effect* of reprocessing on stored values depends on D-08.3; the request path does not. |
| 6 | **Deterministic threshold-comparison function reading externally configurable values** | AR-DET-004, NFR-MNT-002 | Implementable with the values unset — §4's preamble explicitly contemplates testing behaviour at the threshold rather than the number. |
| 7 | **Confidence-never-raised invariant enforced at the write boundary** | AR-AST-007 | Fully specified, no dependencies. |
| 8 | **Sensitivity raise-only and consequential-floor invariants** | FR-SENS-006, BR-020, AR-AST-007 | The invariants are specified even though the rules that assign tiers are not. |
| 9 | **Classification confidence and per-field confidence stored as independent values** | FR-OCR-003, FR-OCR-005 | The independence is explicit in FR-OCR-005. |
| 10 | **Attribute → source-document reference** | FR-INF-002, BR-010 | The reference is specified; only the attribute's identity is blocked. |
| 11 | **Configuration-driven type and field definition mechanism (the loader, not the content)** | NFR-MNT-001 | The requirement mandates the mechanism. Content is D-05. |
| 12 | **Multi-page documents processed as one document** | FR-OCR-008, AC-US-003-4 | Structural, engine-independent. |
| 13 | **Unclassified as an honest outcome, with no type assumed** | FR-OCR-002, AR-AST-002, EC-003, AC-US-003-3 | The one §7.1 type behaviour that is unconditional. Already modelled in Sprint 3's `DocumentType`. |
| 14 | **Redaction of extracted values from logs and diagnostics** | NFR-PRIV-007, NFR-OBS-004 | Extends Sprint 3's existing redaction processor. |
| 15 | **Aggregate confidence-distribution measurement without underlying values** | NFR-OBS-001 | Required, and independent of the threshold values. |
| 16 | **Partial-success reporting** | NFR-ERR-003, EC-002 | "Extract what is legible, mark low-confidence fields for review" is specified behaviour. |
| 17 | **Per-user isolation on every new table and query** | NFR-SEC-003, FR-ACC-003, NFR-PRIV-002 | Sprint 3's established pattern — ownership narrows the query, never validates after the fact. |

**Not on this list, and deliberately so:** anything that stores an attribute value, anything that assigns a document type from the candidate set, anything that assigns a sensitivity tier, and anything that sets a threshold number.

---

# 3. BLOCKED UNTIL EVALUATION

Everything dependent on AR-AST-008, study S-6, assumption A-7, or assumption A-5.

| # | Item | Blocked by | Requirement affected |
| --- | --- | --- | --- |
| 1 | **The automatic-action threshold value** | AR-AST-008 ("before any threshold is set"), S-6 | BR-001, FR-FILL-001, FR-DRP-003, FR-MATCH-003 |
| 2 | **The review threshold value** | AR-AST-008, S-6 | FR-OCR-006, BR-002, AC-US-004-4 |
| 3 | **Final MVP document-type set** | §7.1 ("Final inclusion of each type is subject to the extraction evaluation in study S-6"), ASM-001 | FR-OCR-002, FR-OCR-004, §7.1 |
| 4 | **Whether thresholds are global or per-type** | S-6 distributions | NFR-MNT-002, BR-001 |
| 5 | **Committing FR-OCR-004, FR-OCR-005, FR-OCR-006 and BR-001 to build** | §12.3, A-7 | Named explicitly in §12.3 |
| 6 | **Selection of the assisted engine** | AR-AST-008 (evaluation should select as well as calibrate) | D-01, §6 Selection Principle |
| 7 | **Whether any given type is demoted to store-and-search only** | §7.1 demotion rule | §7.1, G-08 |
| 8 | **The routine/sensitive boundary** | A-5, studies S-1 and S-4 ("This boundary must be set by users, not by us") | FR-SENS-001…006, FR-INF-007, NFR-USE-002 |
| 9 | **Classification abstention rate — does the classifier actually return "unrecognised"?** | AR-AST-008, corpus item D-02.n | AR-AST-002, AC-US-003-3 |
| 10 | **Conflict-detection efficacy** | Corpus item D-02.m (person-grouped conflicting documents) | FR-INF-004, AC-US-005-1 |
| 11 | **Whether the engine's confidence is calibrated enough to be "usable by BR-001"** | AR-AST-008 | AR-AST-001, BR-001 |
| 12 | **Re-evaluation after any engine or provider version change** | G-03 — not currently required, and should be | AR-AST-008 |

---

# 4. REQUIREMENTS GAPS THAT NEED SPECIFICATION AMENDMENT

Genuine gaps that engineering cannot safely close alone. Each requires a change to `step3.pdf` under §11's Containment Rule ("an explicit scope change recorded in this document with a new version number").

| ID | Gap | Affected requirements | Why engineering cannot close it |
| --- | --- | --- | --- |
| **G-01** | The MVP processing location is never stated. NFR-PRIV-008 defers a *mode*, not the baseline. | NFR-PRIV-006, NFR-PRIV-008 | It defines the subject of a mandatory user disclosure |
| **G-02** | No requirement governs the collection, consent, retention, destruction, or team-readability of a real-document evaluation corpus. **Governance APPROVED as a project decision (D-02.5, [`SPRINT_4_G02_CORPUS_GOVERNANCE.md`](SPRINT_4_G02_CORPUS_GOVERNANCE.md)) — the gap in `step3.pdf` remains open and still needs the amendment.** | AR-AST-008, NFR-PRIV-002, NFR-PRIV-003 | Consent and privacy obligations toward real people |
| **G-03** | No re-evaluation trigger when an assisted component changes version. | AR-AST-008 | Determines when calibrated thresholds cease to be evidence |
| **G-04** | Neither threshold has a value; the review threshold carries no TBD marker and no study reference. | BR-001, BR-002, FR-OCR-006 | Product risk decision informed by evaluation |
| **G-05** | The relationship between the review and automatic-action thresholds is never stated, nor which governs classification. | BR-001, BR-002, FR-OCR-003/006, AC-US-003-3 | Changes system behaviour, not implementation |
| **G-06** | Confidence has no defined scale, semantics, or cross-component comparability. | AR-AST-001, FR-OCR-003/005, BR-001 | Makes BR-001 untestable as written |
| **G-07** | Global vs per-document-type thresholds is unaddressed. | NFR-MNT-002, BR-001, §7.1 | Product decision about differential behaviour |
| **G-08** | The "store-and-search only" state a demoted type falls into is not defined as a document state. | §7.1, FR-DOC-002, FR-OCR-002 | A user-visible state the specification requires but never models |
| **G-09** | "Address proof" is a category, not a document type, and its members are never enumerated. | §7.1, FR-OCR-002, FR-OCR-004 | Product scope decision |
| **G-10** | "Semester result" (§7.1) and "semester marksheet" (AC-US-003-1) are used for what may or may not be one type. | §7.1, AC-US-003-1, NFR-USE-005 | Changes the meaning of an acceptance criterion |
| **G-11** | Whether photograph and signature have structured information requirements is never stated. | §7.1, FR-OCR-004, FR-INF-007 | Determines whether extraction applies at all |
| **G-12** | **No field definitions exist for any document type.** | FR-OCR-004, FR-OCR-005, NFR-MNT-001 | Defines what DOCURA reads from a person's identity documents |
| **G-13** | **The canonical attribute vocabulary does not exist**, though FR-ACC-004 names it. **Definition APPROVED as a product decision (D-05.6, [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md)) — the approval fixes the seven-property shape only; no attribute exists, and the gap in `step3.pdf` remains open and still needs the amendment. REVISED 6 September 2026 and the revision APPROVED 6 September 2026 — D-05.8 (G-13.2, G-13.5, G-13.9; new G-13.15; G-13.11's trigger clarified); G-13.3 preserved, no eighth property. **T1 contents authoring run 6 September 2026 — D-05.9: `v0.1-draft`, one proposed entry, nine candidates not authored. Completed D-05.10 (N-TEXT). PD-B APPROVED 7 September 2026 — D-05.11: the one entry, its one-attribute scope, and N-TEXT; this approves T1 content only and closes no gap. PD-A, PD-C, PD-D, PD-E APPROVED 8 September 2026 — D-05.12; X12 MET the same day — D-05.13; X15 CLOSED the same day — D-05.14 (fourth false-conflict attribution category applied at D-02 §11.6.1). **G-13-A is MET (8 Sep 2026).** The gap is still not closed — the §11 amendment (X16) is owed, and G-13-B (G-14/G-15) remains NOT MET.**** | FR-ACC-004, FR-INF-001/004/007/008, FR-SRCH-003, EC-019 | Defines what DOCURA knows about a person |
| **G-14** | The sensitivity classification rules are not in `step3.pdf`; the referenced §02 Table 13.1 is an ASM-tagged working classification whose boundary A-5 says must be set by users. | FR-INF-007, FR-SENS-001, AR-DET-005, NFR-MNT-004 | Determines when the product interrupts a user |
| **G-15** | No default sensitivity tier for an attribute no rule covers. | FR-INF-007 | Safety-relevant default |
| **G-16** | Document-level sensitivity is presupposed by FR-MATCH-009 and EC-011 but defined nowhere. | FR-SENS-001, FR-MATCH-009, EC-011 | Determines when approval is required for an attachment |
| **G-17** | "Processing" in NFR-PRIV-006 is undefined, so it is unclear whether the obligation was already triggered at Sprint 3. | NFR-PRIV-006 | Determines whether a mandatory disclosure is currently outstanding |
| **G-18** | No re-disclosure requirement when the processing arrangement changes. | NFR-PRIV-006 | User-facing honesty obligation |
| **G-19** | FR-ACC-004's "profile" and FR-INF-001's "structured record" are never distinguished or unified. **ANSWERED as a product decision 8 Sep 2026 (PD-C, D-05.12): one store, two views — the profile is the resolved view over per-document observations; no eighth property added. The `step3.pdf` amendment (X16) is still owed, so the gap stays OPEN.** | FR-ACC-004, FR-INF-001, FR-INF-003 | Defines the central data model |
| **G-20** | "Duplicate attribute entries" is never defined, so NFR-REL-005 has no attribute-level meaning. | NFR-REL-005 | Determines reprocessing semantics |
| **G-21** | "Encrypted at rest" has no threat model, so NFR-SEC-002 cannot be tested. | NFR-SEC-002, §15 "Testable" | Security posture decision |
| **G-22** | Key management is entirely absent from the specification. | NFR-SEC-002 | Cannot be invented; needs security ownership |
| **G-23** | The encryption boundary (backups, replicas, logs, temporary processing artefacts, external processor custody) is undefined. | NFR-SEC-002, NFR-PRIV-003 | Determines the real protection achieved |
| **G-24** | Whether crypto-erasure satisfies NFR-PRIV-003 deletion is unaddressed, and the deletion period remains TBD. | NFR-PRIV-003, NFR-SEC-002 | Legal and product decision |
| **G-25** | Retry behaviour has no observability requirement. | NFR-OBS-004, FR-OCR-009 | Operational visibility gap |
| **G-26** | No requirement obliges the recording of security-relevant events (authentication, authorisation failure, vault access). | NFR-OBS-004, NFR-SEC-009 | Serious for a product holding identity documents |
| **G-27** | The "manual-entry path" of FR-OCR-009 has no defined destination while field definitions do not exist. | FR-OCR-009, AC-US-003-5, FR-OCR-004 | Depends on G-12/G-13 |
| **G-28** | AC-US-005-3 requires a conflict resolution to "appear in history" without saying which history — FR-INF-009 or FR-AUD. | AC-US-005-3, FR-INF-009, FR-AUD-005 | Determines where a user looks for it |
| **G-29** | **No behaviour is defined for an extracted value that maps to no canonical attribute.** The specification provides an "unknown" outcome at document-type level (FR-OCR-002) and at form-field level (FR-FLD-006) and none at attribute level. **Raised as G-13.g1** in G-13 §12.4 and D-05.7; **numbered here 6 September 2026**, which satisfies G-13 §18 **X3**. G-13.7 (approved) excludes coercion. **DESTINATION DECIDED 8 Sep 2026 (PD-E, D-05.12): discard for MVP — the value is not retained; the original document (Sprint 3) is the recovery source, recoverable by FR-OCR-010 reprocessing once the vocabulary gains the attribute. The `step3.pdf` amendment (X16) is still owed, so the gap stays OPEN.** | FR-OCR-002, FR-FLD-006, FR-INF-001, BR-009, BR-016, BR-017, NFR-PRIV-001 | **Destination now decided (discard); the numbered gap remains OPEN pending the amendment** |

---

# IMPLEMENTATION READINESS MATRIX

Statuses: **READY FOR IMPLEMENTATION** · **BLOCKED — REQUIREMENTS GAP** · **BLOCKED — EVALUATION REQUIRED** · **BLOCKED — ARCHITECTURE DECISION REQUIRED** · **TBD**

Nothing below is marked READY merely because it is technically easy.

## Functional — FR-OCR

| Requirement ID | Requirement | Status |
| --- | --- | --- |
| FR-OCR-001 | Extract machine-readable text from each uploaded document | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-01) |
| FR-OCR-002 | Classify into a supported type, or as unrecognised | **BLOCKED — REQUIREMENTS GAP** (G-09, G-10, G-11) and **EVALUATION REQUIRED** (§7.1). *The unrecognised/unclassified half alone is READY.* |
| FR-OCR-003 | Record a confidence value for the classification | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-01); storage of the value is READY |
| FR-OCR-004 | Extract the defined field set per supported type | **BLOCKED — REQUIREMENTS GAP** (G-12, G-13); also §12.3 A-7 |
| FR-OCR-005 | Per-field confidence, independent of document-level | **BLOCKED — REQUIREMENTS GAP** (G-06, G-12); the independent-storage structure is READY |
| FR-OCR-006 | Below the review threshold → needs review, not used for automatic filling | **BLOCKED — EVALUATION REQUIRED** (G-04); the withholding mechanism is READY |
| FR-OCR-007 | Show each value alongside its source region | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (region representation, D-08.1) |
| FR-OCR-008 | Multi-page documents processed as one document | **READY FOR IMPLEMENTATION** |
| FR-OCR-009 | On failure: retain original, state what failed, offer retry and manual entry | **BLOCKED — REQUIREMENTS GAP** (G-27, manual-entry destination). *Retain-original, reason, and retry are READY.* |
| FR-OCR-010 | User-requested reprocessing | **BLOCKED — REQUIREMENTS GAP** (G-20, and D-08.3 semantics). *The request path is READY.* |
| FR-OCR-011 | Handwritten content | **N/A — FUTURE / WON'T** |
| FR-OCR-012 | Additional scripts and languages | **N/A — FUTURE / WON'T** |

## Functional — FR-INF

| Requirement ID | Requirement | Status |
| --- | --- | --- |
| FR-INF-001 | Maintain a structured record assembled from all processed documents | **BLOCKED — REQUIREMENTS GAP** (G-13, G-19) |
| FR-INF-002 | Every attribute references its source document and confidence | **BLOCKED — REQUIREMENTS GAP** (G-13); the reference structure is READY |
| FR-INF-003 | User correction becomes authoritative | **BLOCKED — REQUIREMENTS GAP** (G-13, G-19) |
| FR-INF-004 | Detect when two documents give different values for the same attribute | **BLOCKED — REQUIREMENTS GAP** (G-13 — "the same attribute" is undefined) |
| FR-INF-005 | Present conflicts; never resolve automatically | **BLOCKED — REQUIREMENTS GAP** (G-13). *The never-resolve-automatically rule is absolute and READY as an invariant.* |
| FR-INF-006 | Record the designated authoritative value; retain alternatives | **BLOCKED — REQUIREMENTS GAP** (G-13, G-19) |
| FR-INF-007 | Every attribute carries a sensitivity classification | **BLOCKED — REQUIREMENTS GAP** (G-14, G-15) and **EVALUATION REQUIRED** (A-5). *The tier field and raise-only invariant are READY.* |
| FR-INF-008 | Deterministic normalisation of formats without altering meaning | **BLOCKED — REQUIREMENTS GAP** (G-13 — per-attribute normalisation rules) |
| FR-INF-009 | Record change history, including who or what changed it | **BLOCKED — REQUIREMENTS GAP** (G-28, and G-13 for the subject) |
| FR-INF-010 | Indicate missing commonly required information | **N/A — FUTURE / WON'T** |

## Functional — carried into Sprint 4 from adjacent modules

| Requirement ID | Requirement | Status |
| --- | --- | --- |
| FR-UPL-005 | Per-document status: queued, processing, ready, needs review, failed | **READY FOR IMPLEMENTATION** (states already modelled; transitions are Sprint 4's) |
| FR-DOC-002 | Type assigned automatically, correctable by the user | **BLOCKED — REQUIREMENTS GAP** (G-08, G-10). *The user-correction path is READY once the type vocabulary exists.* |
| FR-DOC-001 | Vault listing with type, date added, processing status | **READY FOR IMPLEMENTATION** (delivered in Sprint 3; status now becomes dynamic) |
| FR-SRCH-002 | Search the extracted text of all documents | **BLOCKED — REQUIREMENTS GAP** (G-21, G-23 — the search/encryption tension, D-10.3) |
| FR-ACC-004 | User profile of canonical personal attributes | **BLOCKED — REQUIREMENTS GAP** (G-13, G-19) |

## Automation requirements

| Requirement ID | Requirement | Status |
| --- | --- | --- |
| AR-DET-003 | Deterministic, reversible value normalisation | **BLOCKED — REQUIREMENTS GAP** (G-13) |
| AR-DET-004 | Deterministic threshold comparison and act-or-ask | **READY FOR IMPLEMENTATION** (mechanism; values are D-03) |
| AR-DET-005 | Sensitivity driven by a reviewable rule set, not per-session inference | **BLOCKED — REQUIREMENTS GAP** (G-14). *The mechanism is READY.* |
| AR-DET-008 | Deterministic conflict detection; resolution never automated | **BLOCKED — REQUIREMENTS GAP** (G-13) for detection; **READY** for the never-automate invariant |
| AR-AST-001 | Per-value confidence usable by BR-001 | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-01) and **EVALUATION REQUIRED** (calibration) |
| AR-AST-002 | Classification can return "unrecognised" | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-01); **EVALUATION REQUIRED** to prove abstention |
| AR-AST-006 | Every assisted output explainable in terms of its source | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-01, provenance across the engine boundary) |
| AR-AST-007 | Never raise a confidence; never remove a sensitivity classification | **READY FOR IMPLEMENTATION** |
| AR-AST-008 | Evaluation against a held-out corpus before any threshold is set | **BLOCKED — REQUIREMENTS GAP** (G-02) then **EVALUATION REQUIRED** |

## Non-functional

| Requirement ID | Requirement | Status |
| --- | --- | --- |
| NFR-PERF-002 | Processing asynchronous; user never blocked | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-09; decision is immediately resolvable) |
| NFR-REL-002 | Interrupted processing recoverable; original never lost | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-09). *The original-never-lost half is already satisfied.* |
| NFR-REL-005 | No duplicate documents or duplicate attribute entries | **BLOCKED — REQUIREMENTS GAP** (G-20). *The document half is already satisfied by Sprint 3.* |
| NFR-SCL-002 | Processing load grows independently of interactive traffic | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (D-09) |
| NFR-SEC-002 | Documents and extracted information encrypted at rest | **BLOCKED — REQUIREMENTS GAP** (G-21, G-22, G-23) |
| NFR-SEC-003 | Every access authorised against the requesting user | **READY FOR IMPLEMENTATION** (Sprint 3 pattern extends to new tables) |
| NFR-PRIV-002 | No training on user documents; no cross-user readability | **BLOCKED — ARCHITECTURE DECISION REQUIRED** (contractual, if D-01 selects an external provider) |
| NFR-PRIV-006 | Off-device processing disclosed before first upload | **BLOCKED — REQUIREMENTS GAP** (G-01, G-17, G-18) |
| NFR-PRIV-007 | Diagnostics exclude document contents and extracted personal values | **READY FOR IMPLEMENTATION** |
| NFR-MNT-001 | Types and extractable fields definable as configuration | **BLOCKED — REQUIREMENTS GAP** (G-12) for content; **READY** for the mechanism |
| NFR-MNT-002 | Thresholds externally configurable without a code release | **READY FOR IMPLEMENTATION** (mechanism); values **BLOCKED — EVALUATION REQUIRED** |
| NFR-MNT-004 | Sensitivity rules maintainable as a reviewable list | **BLOCKED — REQUIREMENTS GAP** (G-14) for content; **READY** for the mechanism |
| NFR-OBS-001 | Aggregate confidence distributions without underlying values | **READY FOR IMPLEMENTATION** |
| NFR-OBS-004 | Failures recorded with diagnostic context, without personal values | **READY FOR IMPLEMENTATION** |
| NFR-ERR-001 | Errors state what went wrong and what to do next | **READY FOR IMPLEMENTATION** |
| NFR-ERR-002 | Fail towards inaction | **READY FOR IMPLEMENTATION** |
| NFR-ERR-003 | Partial success reported as partial | **READY FOR IMPLEMENTATION** |
| NFR-ERR-004 | No internal identifiers or stack traces exposed to the user | **READY FOR IMPLEMENTATION** |
| NFR-ERR-005 | Retry offered in place | **READY FOR IMPLEMENTATION** |

## Business rules in scope

| Requirement ID | Rule | Status |
| --- | --- | --- |
| BR-001 | Automatic action only at or above the automatic-action threshold | **BLOCKED — EVALUATION REQUIRED** (G-04); §12.3 |
| BR-002 | Below the review threshold, never used for automatic action | **BLOCKED — EVALUATION REQUIRED** for the value; **READY** for the mechanism |
| BR-004 | Conflicts surfaced, never resolved by rule, recency, or preference | **BLOCKED — REQUIREMENTS GAP** (G-13) for detection; **READY** as an invariant |
| BR-012 | User precedence; never overwritten automatically | **BLOCKED — REQUIREMENTS GAP** (G-19) for the model; the invariant itself is specified |
| BR-013 | Stored original never modified | **READY FOR IMPLEMENTATION** (already satisfied by Sprint 3; must be preserved) |
| BR-016 | Fail towards inaction | **READY FOR IMPLEMENTATION** |

## Stories

| ID | Story | Status |
| --- | --- | --- |
| US-003 | Have documents read and understood automatically | **BLOCKED — REQUIREMENTS GAP** (G-10, G-12, G-27) and **EVALUATION REQUIRED** |
| US-004 | See and correct what DOCURA understood | **BLOCKED — REQUIREMENTS GAP** (G-13, G-19) |
| US-005 | Resolve conflicting information between documents | **BLOCKED — REQUIREMENTS GAP** (G-13) — blocked in full |

---

# SPRINT 4 IMPLEMENTATION READINESS

## Is Sprint 4 ready to implement?

**No — not as a complete sprint.** Sprint 4 cannot be implemented as specified today, for two independent reasons:

1. **The specification's own instruction.** §12.3 states that FR-OCR-004, FR-OCR-005, FR-OCR-006 and BR-001 "must not be committed to build until their supporting assumption reports" (A-7, study S-6). That is a requirement about the process of building, and it has not been satisfied.
2. **The requirements needed to build them do not exist.** FR-OCR-004 requires "the defined set of information fields" for each supported type, and no field set is defined anywhere in `step3.pdf` for any type (G-12). FR-INF-004 requires detecting when two documents disagree about "the same attribute", and no canonical attribute vocabulary exists (G-13). These are not thresholds awaiting a number; they are the substance of what the system is meant to read and store.

**A substantial, coherent part of Sprint 4 is ready.** The processing pipeline as an engineering artefact — durable jobs, worker execution, the five FR-UPL-005 status transitions, failure capture, retry, original preservation, reprocessing entry, the deterministic threshold-comparison mechanism, the confidence-never-raised and sensitivity-raise-only invariants, redaction, aggregate confidence measurement, and per-user isolation — depends on none of the unresolved gaps. This is the A-7-independent envelope described in D-00 Option 2, and it is genuinely ready.

## What decisions remain

- **Product Management:** sprint shape under §12.3 (D-00); canonical attribute vocabulary (G-13); per-type field definitions (G-12); profile vs attributes (G-19); correction-vs-re-extraction semantics (D-08.3); semester naming (G-10); photograph/signature scope (G-11); address-proof definition (G-09); sensitivity rules and default tier (G-14, G-15); document-level sensitivity (G-16); the store-and-search-only state (G-08); corpus governance with Legal (G-02); disclosure obligations (G-01, G-17, G-18); security-event logging (G-26).
- **Architecture (Step 4):** the extraction architecture and its port (D-01); the asynchronous processing architecture (D-09); attribute-entry identity (G-20); source-region representation; the encryption design once its threat model exists (D-10).
- **Security:** the NFR-SEC-002 threat model (G-21), key management (G-22), the encryption boundary (G-23), and the search-versus-encryption resolution (D-10.3).

## What evaluations remain

- **Study S-6 — comprehension evaluation on real scans**, satisfying AR-AST-008, which must precede any threshold being set, and which also determines the final MVP document-type set under §7.1 and settles assumption A-7 for §12.3.
- **Studies S-1 and S-4** — the routine/sensitive boundary (assumption A-5), which the research document states "must be set by users, not by us", and on which FR-SENS-001…006 depend.
- **Engine calibration** — confirming that the selected engine's confidence is meaningful enough for BR-001, and that it will actually return "unrecognised" (AR-AST-002).

## What requirements amendments remain

Twenty-eight gaps, G-01 to G-28, are recorded in section 4. The four that block the most work are: **G-12** (no field definitions), **G-13** (no canonical attribute vocabulary), **G-14** (no sensitivity rules), and **G-21/G-22** (no encryption threat model or key management). Each requires an amendment to `step3.pdf` under §11's Containment Rule, not an engineering workaround.

## What the next concrete step should be

**Take the D-00 decision first**, because it scopes everything else. If PM chooses Option 2 — the recommended split — then, in order:

1. **PM authors the canonical attribute vocabulary (G-13), then the per-type field definitions (G-12)**, as reviewed configuration artefacts. Nothing attribute-shaped can be built before these exist, and they are the long pole. **The vocabulary's definition is now approved (D-05.6) and its revision approved (D-05.8): authoring writes entries against the seven-property shape, whose property 6 becomes a scope-keyed cardinality. The contents remain the outstanding work, and approved decision 11 forbids a placeholder standing in for them. **G-13-A is now MET (8 September 2026, D-05.14): G-12 authoring is unblocked** — its own gaps (G-09/G-10/G-11, C-a…C-d, the mock-form field inventory) still stand. G-14/G-15 gate G-13-B and may proceed in parallel.**
2. **In parallel, PM and Legal settle corpus governance (G-02)** and commission study S-6, since AR-AST-008 gates every threshold and the final type set, and no amount of engineering shortens that path.
3. **In parallel, engineering implements the A-7-independent envelope** — the durable job architecture of D-09 Option B, status transitions, failure and retry paths, and the invariants listed in section 2. This is real, testable progress that no pending decision invalidates.
4. **Architecture records the D-01 extraction decision in Step 4**, keeping the engine behind a port so that the evaluation, when it reports, can choose the implementation rather than being presented with one.
5. **Security states the NFR-SEC-002 threat model (G-21) before extracted text exists**, because encryption applied after the data is created is a migration rather than a design.

**One thing not to do:** do not set a provisional threshold "to unblock development". AR-AST-008 forbids it in terms — "before any threshold is set" — and a placeholder number in a configuration file is the most likely way an unvalidated value reaches a real document.

---

*End of Sprint 4 Decision Register. Prepared against `backend/step3.pdf` (DOCURA 03 — Requirements Specification v1.0, 39 pages, read in full). No application code, tests, migrations, dependencies, configuration, or schema were modified in producing this document.*
