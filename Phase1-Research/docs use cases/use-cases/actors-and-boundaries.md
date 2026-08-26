# Actors & System Boundary

**Step 4 · Document 1 of 20** — Source of truth: Steps 1–3. Every actor below is justified by an approved
requirement; none is invented for narrative convenience.

---

## 1. How actors were chosen

An actor is anything **outside a use case** that exchanges something with it. Step 3 §6 already divides DOCURA's
intelligence into three layers by *what kind of certainty each can offer*, and states that this separation "is a
requirement, not an implementation note: it determines where errors are possible, and therefore where a human must
remain in the loop." That sentence is why the layers appear here as **responsibility boundaries** — the flows in
this step have to say which layer may act and which may only advise.

> **These layers are not architecture.** They are named responsibilities taken directly from Step 3 §6.1–6.3. Which
> components implement them, and how, belongs to Step 5 and beyond.

Two candidate actors were considered and **rejected**:

| Rejected | Why |
|---|---|
| "OCR Engine", "Database", "Model provider" | Internal implementation, not a Step 4 concern. Step 3 §6 explicitly says "This document specifies what each layer must guarantee, not what technology provides it." |
| "Institution / reviewer at the far end" | Nothing in Steps 1–3 gives DOCURA any interaction with the receiving institution. The form is where DOCURA's world ends. |

---

## 2. Actor catalogue

### 2.1 Primary actor

| Actor | Who it is | What it does | Source |
|---|---|---|---|
| **User** | A single individual with one account. In the MVP this is Persona 1, *The Applicant in Season* — a final-year undergraduate. | Uploads documents, corrects what was read, resolves conflicts, activates DOCURA on a form, answers ambiguities, approves or denies sensitive disclosures, completes declarations, reviews, and **submits**. | Step 2 §08 Persona 1; Step 3 FR-ACC-003 (one record, one owner) |

There is exactly **one** human actor in the MVP. Step 3 FR-ACC-003 states that "each record shall belong to exactly
one user. No shared, delegated, or multi-person records exist in MVP." Personas 2 and 3 from Step 2 are real users
of the product but introduce no distinct MVP actor.

### 2.2 Supporting actors — inside the system boundary

| Actor | Responsibility | May be trusted for | Must never be used for | Source |
|---|---|---|---|---|
| **DOCURA** (the application) | The vault, the structured record, search, account and session, history. | Holding and serving what the user owns. | — | FR-ACC, FR-DOC, FR-UPL, FR-INF, FR-SRCH, FR-AUD |
| **DOCURA Extension** | Activation, form detection, field understanding, filling, prompting, review, hand-back. | Everything that touches a third-party page — but only after explicit activation. | Reading any page the user has not activated. | FR-EXT, FR-FRM, FR-FLD, FR-FILL, FR-DRP, FR-AMB, FR-MATCH, FR-APR, FR-REV, FR-SUB |
| **Document Intelligence Layer** | Reads documents: text extraction, classification, per-field extraction, confidence. Conflict *detection*. | Reading documents and classifying document type — always with a confidence, always able to return "unrecognised". | Deciding anything the user has not been given the chance to see and correct. Conflict *resolution* is never automated at all. | AR-AST-001/002, AR-DET-008 |
| **Form Intelligence Layer** | Reads forms: field meaning, semantic option matching, document-to-field matching. | Producing ranked candidate lists with confidences, and returning "unknown". | Producing a single forced answer. Escalating its own authority. | AR-AST-003/004/005/007 |
| **Decision & Policy Engine** | The act-or-ask decision. Threshold comparison, sensitivity classification, declaration detection. | Deterministic threshold and tier decisions given a confidence value. | Interpretation of meaning — that is the assisted layers' job, not its own. | AR-DET-004/005/006, BR-001…BR-009 |
| **Action Executor** | The only component that changes the outside world. | Placing a value, selecting an option, attaching a document — and nothing else. | Navigating, submitting, dismissing dialogs, or altering the page beyond the field it is filling. | AR-AGT-001/004 |

### 2.3 External systems

| Actor | Role | Boundary rule | Source |
|---|---|---|---|
| **External Form** | The third-party page being completed. In the MVP this is a **controlled mock MCA-style application form built by the team** — chosen so the demonstration is reproducible and can include every field type deliberately. | DOCURA reads its structure only after activation, writes only into fields, and **never operates its submit control**. | Step 3 §10, ASM-002, BR-008, BR-014 |
| **Web Browser** | Hosts the extension and grants its permissions. | The extension requests the *narrowest* permissions that allow its function, and justifies each in user-facing language. | FR-EXT-001, NFR-SEC-006 |

### 2.4 Off-stage actors — real, but with no MVP use case

| Actor | Interest | Why no use case | Source |
|---|---|---|---|
| **Independent Security Reviewer** | Must review the product before any release to users outside the team. | An organisational gate, not a product interaction. Recorded here so it is not forgotten — Step 3 §10.3 names it as one of two exclusions that **must close** before a real identity document is stored by a real user. | NFR-SEC-009 |
| **DOCURA Product & Operations** | Tunes confidence thresholds without a code release; reads aggregate confidence, act/ask/decline, and override-rate metrics. | Configuration and observability, not a user-facing flow. | NFR-MNT-001/002/004, NFR-OBS-001…005 |

### 2.5 Outside the MVP boundary — FUTURE only

| Actor | Unlocked by | Requirement |
|---|---|---|
| Government Document Locker | Horizon H4 — vault maturity | FR-UPL-010 |
| Cloud Storage / Email | Horizon H4 | FR-UPL-009 |
| Delegate / Family Member (Persona 3) | Horizon H6 — a consent architecture designed for third parties | FR-ACC-010 |
| Mobile Browser | Horizon H2 — pending assumption A-8 | FR-EXT-008 |

---

## 3. System context

<!--DIAGRAM:01-system-context-->

### 3.1 Diagram key — node to requirement

| Node | Requirements |
|---|---|
| Account and Session | FR-ACC-001/002/005/008, NFR-SEC-004/005 |
| Document Vault | FR-UPL-001…007, FR-DOC-001…008 |
| Document Intelligence | AR-AST-001/002, AR-DET-008, FR-OCR-001…010 |
| Structured Record | FR-INF-001…009, FR-SENS-001 |
| Search and Retrieval | FR-SRCH-001…005, FR-DOC-004, NFR-SEC-007 |
| History and Audit | FR-AUD-001…006 |
| Activation Gate | FR-EXT-003/004/005, BR-014 |
| Form Intelligence | AR-AST-003/004/005, FR-FLD-001/002, FR-FRM-001…007 |
| Decision and Policy Engine | AR-DET-004/005/006, BR-001…BR-009 |
| Action Executor | AR-AGT-001…006, FR-FILL, FR-DRP, FR-MATCH |
| Prompt Surface | FR-AMB-002…005, FR-APR-001/002, FR-REV-001…006 |
| Web Browser | FR-EXT-001, NFR-SEC-006 |
| External Form | Step 3 §10, ASM-002 |

---

## 4. Where the boundary is drawn, and why it matters

Three boundary rules do most of the work in this product. Each is a business rule, not a setting.

**The activation boundary — BR-014.** DOCURA reads a page only after the user activates it *on that page*. There is
no passive or background observation. Before activation the extension is not "idle and watching"; it is reading
nothing, logging nothing, and transmitting nothing (FR-EXT-004). This is why every extension flow in this step
begins with a dormant state rather than a detection state.

**The action boundary — AR-AGT-001.** The Action Executor may do exactly three things: place a value, select an
option, attach a document. It may not navigate, submit, dismiss a dialog, or alter the page in any other way
(AR-AGT-004). Anything a flow shows DOCURA "doing" to the form must be one of those three, or it is out of bounds.

**The consent boundary — BR-006 and BR-008.** Declarations, agreements, consent controls, and final submission sit
structurally outside automation. Step 3 names BR-006, BR-008 and BR-009 the **non-negotiable set**, and says that a
request to relax any of them "is a request to change the product's identity, and must be escalated as such rather
than handled as a configuration change." No flow in Step 4 crosses this line, and no flow offers a setting that
would.

---

## 5. Terminology contract

Every diagram and document in this step uses these four names and no synonyms. Renaming them between diagrams was
listed as a defect in the Step 4 brief, and the quality review checks for it.

| Term | Means | Never called |
|---|---|---|
| **User** | The single human account holder. | "the applicant", "the customer", "the end user" |
| **DOCURA** | The application — vault, record, search, account, history. | "the app", "the backend", "the platform", "the system" |
| **DOCURA Extension** | The browser extension. | "the plugin", "the add-on", "the client" |
| **External Form** | The third-party page being completed. | "the website", "the portal", "the target" |

Supporting layer names — **Document Intelligence**, **Form Intelligence**, **Decision & Policy Engine**, **Action
Executor** — are used only where a flow must say which responsibility is acting.

### 5.1 Colour contract

The three accent hues come from Step 1 §09, where each owns exactly one concept. Step 4 reuses them so the visual
system and the decision system stay the same system. Per Step 1's own accessibility constraint, **colour is never
the sole signal** — every node is also labelled.

| Colour | Meaning in every Step 4 diagram | Step 1 concept |
|---|---|---|
| Teal `#4FC8A5` | DOCURA acts — certainty, verified, safely automated | Certainty |
| Amber `#E8A33D` | The user decides — a question is open | Ambiguity |
| Violet `#9A8CF0` | The consent boundary — a mandatory stop | Consent |
| Ivory `#EFEAE0` | A user action or a user-owned artefact | Illumination |
| Rose `#F6D6D6` | A failure path, or DOCURA declining to act | *(added in Step 4 for failure paths, which Step 1 does not colour)* |
