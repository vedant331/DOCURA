# DOCURA — G-13 Revision Analysis

| Field | Value |
| --- | --- |
| Trigger | **G-12 CRITICAL REVIEW — NOT READY — DEPENDENCY MUST BE RESOLVED FIRST.** Blockers D1 (vocabulary ownership), D2 (sensitivity dependency), D3 (qualification scoping) |
| Gap | **G-13 — canonical attribute vocabulary.** Shape approved 5 September 2026 (register **D-05.6**); **contents do not exist**; gap remains **OPEN** |
| Status of this document | **ANALYSIS ONLY — NOTHING APPROVED.** Every new product decision carries **PROPOSED DECISION — REQUIRES APPROVAL** |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0, 25 August 2026 |
| Documents read | `step3.pdf` · `SPRINT_4_DECISION_REGISTER.md` · `SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md` · `SPRINT_4_G12_FIELD_DEFINITIONS.md` · `SPRINT_4_D02_OCR_EVALUATION_PLAN.md` · `SPRINT_4_G02_CORPUS_GOVERNANCE.md` |
| Documents modified | **None.** `SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md` is **not** edited by this analysis; neither is G-12, the register, or `step3.pdf` |
| Attributes finalised | **None.** The ten attributes in G-12 §15 are treated throughout as a **DRAFT CANDIDATE SET**, not as approved content |
| Sensitivity rules invented | **None.** G-14 and G-15 are not resolved here |
| Documents collected | **0** |
| OCR installed / run | **No** |
| Production code modified | **No** |
| Committed / pushed | **No** |

---

## 1. Purpose

### 1.1 The question this document answers

**What is the minimum revision to the approved G-13 decision that allows G-12 to author per-document field sets without creating semantic conflicts?**

"Minimum" is load-bearing. G-13.1…G-13.14 were approved on 5 September 2026 and are binding project decisions. Every clause this analysis proposes to change is a cost: it invalidates a review that already happened. So the analysis works in the other direction from the usual one — it starts by asking *what can stay*, and proposes a change only where an approved clause is demonstrably unable to carry a requirement.

### 1.2 What this document does not do

It does not author an attribute, approve one, or finalise the ten drafted in G-12 §15. It does not resolve **G-14**, **G-15**, **G-19**, **G-20**, **G-09**, **G-10**, **G-11**, or **D-04.4/D-04.7**. It does not edit the G-13 document, the G-12 document, the decision register, or `step3.pdf`. It does not touch code, schema, migrations, fixtures, or evaluation tooling — **G-13.11 (approved) forbids that until G-13 closes, and G-13 has not closed.**

### 1.3 One finding that reframes the whole exercise

The G-12 review characterised D3 as "reopening an approved decision." **That characterisation is too strong, and the evidence is in G-13's own exit criteria.**

> **G-13 §18, X4** — "The seven-property shape (G-13.2) approved **and frozen for a version**" · Depends on **X1, X2** · **Not met**
> **G-13 §18, X2** — "**G-19** answered: whether FR-ACC-004's profile and FR-INF-001's structured record are one thing or two" · **Not met** — *"may add a property to X4"*
> **G-13 §16.1** — G-19 is "**the one dependency that could change G-13.2's shape.** If they are two stores rather than two views, the vocabulary may need an eighth property… G-13 should not close before G-19 is answered, or should close with that risk recorded"

**G-13.2 is approved but explicitly not frozen, and its freeze already waits on an unanswered question that G-13 itself says may add a property.** The scoping problem therefore does not force open a closed door. It arrives during an amendment window G-13 deliberately left open, and it arrives alongside a second candidate change to the same property list.

The practical consequence is the single most useful scheduling finding in this document: **there is one shape-revision event, not two.** G-19's answer and the scope decision must land in the same revision, or the shape will be amended twice and frozen once — invalidating whichever review came first.

---

## 2. Current Approved G-13 Decision

### 2.1 What was approved, and what was not

Register **D-05.6**, 5 September 2026. The approval is narrower than it is often read as being. G-13 §15's own preamble states it:

> "The approval **does not amend `backend/step3.pdf`** (G-13.13), **does not close REQUIREMENTS GAP G-13**, and **creates no attribute**: what is approved is the shape of a definition, not its contents."

Register line 1066 states the same from the register side: *"Canonical attribute vocabulary — definition **APPROVED** (D-05.6); **contents still owed**."*

| | Status |
| --- | --- |
| G-13.1 … G-13.14 as product decisions | **APPROVED** — binding |
| The seven-property shape as a *frozen* version | **NOT frozen** — G-13 §18 X4, pending X2 (G-19) |
| The vocabulary's contents | **DO NOT EXIST** — G-13 §15.3 T1; §18 X6 not met |
| REQUIREMENTS GAP G-13 | **OPEN** |
| `step3.pdf` | **Unamended** (G-13.13) |

### 2.2 The seven properties

| # | Property | Basis in `step3.pdf` |
| --- | --- | --- |
| 1 | Canonical identifier | **New product decision.** Not in the specification |
| 2 | Display label | New, supported by NFR-USE-005 (SHOULD) |
| 3 | Semantic definition | **New product decision** |
| 4 | Data type | **New product decision** |
| 5 | Normalisation rule reference | **EXISTING REQUIREMENT** — FR-INF-008 "normalise attribute formats"; AR-DET-003 |
| 6 | Multiplicity — single or repeating | **New product decision** |
| 7 | Sensitivity tier | **EXISTING REQUIREMENT (slot)** — FR-INF-007 "Every attribute shall carry…" |

**Two of seven are existing requirements. Five are new product decisions.** That ratio matters for §8: amending a new product decision costs a review cycle; amending an existing requirement costs a specification amendment under §11's Containment Rule.

### 2.3 The four approved clauses this analysis has to work against

These are the constraints, quoted, because every option in §8 either satisfies them or amends them.

**G-13.2** — "Each canonical attribute shall carry **exactly these seven properties, and no others**."

**G-13.3** *(the pivotal decision)* — "'The same attribute' (FR-INF-004) shall mean: **two values map to the same canonical attribute identifier.** Identity shall be established by the field→attribute mapping alone — never by label similarity, never by value similarity, never by proximity or position on a document."

**G-13.5** — "Per-attribute normalisation rules shall be part of the vocabulary, and **the normalised form shall be the comparison function used for FR-INF-004**."

**G-13.9** — "Every canonical attribute shall carry a sensitivity tier slot, and **no attribute shall be published in the vocabulary without a tier.**"

### 2.4 The approved clause that already reaches the problem

**G-13 §9, property 8** — the reasoning that put multiplicity in the shape:

> "**Not defined in step3.pdf.** Necessary because **FR-INF-004 cannot otherwise distinguish 'two documents disagree' (a conflict, BR-004) from 'this attribute legitimately holds two values' (not a conflict)**. Getting this wrong produces either false conflicts — which D-02 §11.6 identifies as the failure mode that satisfies FR-INF-004 literally while making the product unusable — or silently missed ones."

**This is a verbatim statement of the scoping problem, written before the scoping problem was found, in the justification for the property that fails to solve it.** §6 returns to this; it is the reason the recommended revision is small.

---

## 3. D1 — Vocabulary Ownership

### 3.1 The question

G-12 §15 contains a ten-attribute canonical registry and G-12 §17.1's **G-12.P1** asks Product Management to adopt it "as the initial **vocabulary content**." G-13 defines the shape. Which artefact should own contents?

### 3.2 This is already settled by approved decisions — it is not an open design question

The answer does not require a new ownership model. It requires noticing that four approved or recorded statements already give one, and that G-12 Part II diverged from it.

| Source | Statement | Status |
| --- | --- | --- |
| **G-13 §15.3 T1** | "**The vocabulary's actual contents — which attributes exist**" · settled by "PM authoring **against G-13.2's shape** and G-13.12's minimality test" | Approved framing |
| **G-13 §18 X6** | "**The vocabulary authored**: every attribute carries all seven properties, none blank" — **a G-13 exit criterion** | Approved framing |
| **G-13.8** | "The vocabulary shall be authored and approved **before** the per-type field sets" | **APPROVED** |
| **G-13 §13.2** | G-13 **must not** decide "which attributes a marksheet, a PAN card, or any other document contains" | Approved framing |
| **Register line 1066** | "definition **APPROVED** (D-05.6); **contents still owed**" | Recorded |

**Contents are G-13's. Type membership is G-12's.** G-13 §13.1 states the interface between them in one line: *"each G-12 field maps to exactly ONE canonical attribute, or explicitly NONE."*

### 3.3 What G-12 Part II actually did, and why it broke

G-12 Part II authored the contents inside the G-12 artefact. Two consequences follow mechanically:

1. **The approval order required by G-13.8 became unexecutable.** G-12 §17.1 puts **G-12.P1** (the vocabulary) and **G-12.P12** (the per-type field sets) in one approval batch. "Vocabulary approved before field sets" cannot be satisfied by a single batch containing both.
2. **The field→attribute mapping degenerated to the identity function.** With no per-type field identifiers, every field *is* its attribute. The "or explicitly NONE" half of the interface contract is never exercised — which is exactly where **G-13.7** and candidate gap **G-13.g1** (the unmapped-value destination) live, and where G-12 §17.2's ten deliberate exclusions would otherwise be visible.

### 3.4 The three candidate ownership models, evaluated

**Model 1 — G-13 owns contents; G-12 owns type→attribute mapping.** *(the approved model)*

Requirement support: **FR-INF-004**'s subject is explicitly cross-document ("two documents give different values for the same attribute"), so attribute identity must exist independently of any one type. **FR-ACC-004** calls the profile "canonical personal attributes" with no type qualifier. **FR-INF-001** assembles "from all processed documents." A vocabulary owned per-type cannot serve any of the three.

Second, and decisively: **§7.1's type set is provisional.** **ASM-001** registers it as untested, and §7.1's own demotion rule can move a type to store-and-search-only on S-6 evidence. Anchoring the vocabulary to types makes the vocabulary demotable with them. **G-13 §9 property 9 already rejected precisely this coupling** when it excluded document-type applicability from the shape — "it would also couple the vocabulary to the §7.1 type set, which is provisional under ASM-001 and subject to S-6 demotion."

**Model 2 — G-12 owns both.** Rejected. It fails all three requirements above, contradicts approved **G-13.8**, and inherits the ASM-001 coupling. It also has no answer for `person.full_name`, which appears on nine types and belongs to none of them.

**Model 3 — one merged artefact.** Rejected. G-13 §13.1's interface contract has meaning only if the two sides can differ. Merging makes the mapping the identity function — which is the exact collapse observed in §3.3 above, adopted deliberately rather than by accident.

### 3.5 Recommendation

**G-13R.1 — PROPOSED DECISION — REQUIRES APPROVAL**
**The approved ownership model stands unchanged: G-13 owns the canonical attribute vocabulary including its contents; G-12 owns the mapping of approved canonical attributes to document types, with each per-type field mapping to exactly one attribute or explicitly to none.**
*Basis:* G-13 §15.3 T1, §18 X6, §13.2, and approved **G-13.8**; FR-INF-004's cross-document subject; ASM-001's provisional type set.
*This is a restoration, not a new decision.* No new ownership model is required, and none is proposed.

**G-13R.2 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-12 §15 (the ten-attribute registry) and G-12 §17.1 items P1–P11 and P13–P14 shall be transferred to the G-13 artefact as a DRAFT CANDIDATE SET, and withdrawn from G-12's approval scope. G-12 retains P12 (per-type mapping), P15, P16, P17 and the §17.2 exclusions.**
*Basis:* G-13R.1. *Effect:* restores G-13.8's approval order and re-creates the field↔attribute distinction the interface contract needs.
*Not decided here:* whether any of the ten attributes survives (§4, §9.4).

**G-13R.3 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-12 shall reinstate per-type field identifiers distinct from canonical attribute identifiers, so that a field may map to an attribute or explicitly to none.**
*Basis:* G-13 §13.1's interface contract; **G-13.7** and **G-13.g1** have no expression without it; G-12.4's own nine-property shape already requires both properties separately.

---

## 4. D2 — Sensitivity Dependency

### 4.1 What the specification fixes, and what it does not

Verified against `step3.pdf`:

| Fixed | Reference |
| --- | --- |
| Three tier names; every attribute carries one | FR-INF-007 (MUST) |
| Classification maintained for stored attributes **and** form fields | FR-SENS-001 (MUST) |
| Sensitivity is raise-only by a user; the consequential tier cannot be lowered by any user | FR-SENS-006 (SHOULD) |
| An attribute or field classified consequential can never be reclassified downward by any actor | BR-020 |
| An assisted component "may add a sensitivity classification, never remove one" | AR-AST-007 |
| Classification is driven by a **reviewable rule set**, not inferred per session | AR-DET-005 |
| Rules maintainable as a reviewable list | NFR-MNT-004 (SHOULD) |
| A **sensitive** value requires explicit per-instance approval before disclosure | FR-SENS-002 (MUST), BR-005 |
| Autofill requires the field be classified **routine** | **FR-FILL-001 (MUST)** |

**Not fixed:** any tier for any attribute. Both requirements that would carry content — FR-INF-007 and FR-SENS-001 — trace to **`§02 Table 13.1`**, which is **not reproduced in `step3.pdf`**. Register D-06.2 quotes document 02's own qualification of that table:

> "The boundary between routine and sensitive is the most important unresolved question in this document… **This boundary must be set by users, not by us** — it is assumption **A-5**."

**The referenced source disclaims its own authority.** G-12 §15.1's universal TBD is therefore correct, and better grounded than G-12 states.

### 4.2 The cost of the current G-13.9 wording

**G-13.9** forbids publishing an attribute without a tier. G-13 §18 **X6** requires "all seven properties, **none blank**" and **X9** requires a tier on every attribute. Read together: **G-13 cannot close until G-14 and G-15 close.**

G-14/G-15 are gated on **A-5**, which document 02 says must be settled by users, and which register D-06.4 routes to **studies S-1 and S-4**. So under the current wording the dependency chain is:

```
studies S-1 / S-4  →  A-5  →  G-14 / G-15  →  G-13 closure  →  G-12 authoring
                                                           →  L6 / L7 annotation
                                                           →  D-02 §11.6 and §11
```

**A user-research study sits on the critical path of every field-extraction activity in the sprint.** Nothing in `step3.pdf` requires that. **G-13.9 is a self-imposed product decision**, and it is the only thing putting A-5 there.

### 4.3 Is the constraint doing necessary work?

Yes — but not the work its current wording does. Its purpose is to prevent an untiered attribute reaching a surface where **FR-SENS-002**'s per-instance approval gate would be silently bypassed. That is a real and important protection.

It is a protection against **release**, not against **authoring**. G-12 §19.3 established the distinction correctly and it survives scrutiny: **evaluation readiness does not require a tier** (ground-truth annotation records what a document says; it discloses nothing to a form), while **implementation readiness does**. FR-INF-007 and FR-SENS-001 bind *the system*; neither binds an analysis artefact.

### 4.4 The interim-default route, and why it is not free

Register **D-06.4** already holds a recommendation for G-15: *default to **sensitive** for any attribute with no rule*, grounded in BR-016 ("fail towards inaction") and AR-AST-007's asymmetry. Adopting it would leave no tier blank and satisfy G-13.9 verbatim.

Two costs, both verified:

1. **It disables autofill entirely, for as long as it stands.** **FR-FILL-001 (MUST)** fills only where "the field is classified **routine**." With every attribute defaulted to *sensitive*, **no value is autofillable**, and every disclosure routes through FR-SENS-002's per-instance approval. Demonstration steps **D7** ("Routine fields above threshold filled") and, in substance, **D11** become unrunnable. The MVP demonstration journey in §10.1 cannot complete.
2. **Reversing it later is constrained, though not prohibited.** BR-020's floor bites only at *consequential*, so *sensitive → routine* is not barred outright. But **FR-SENS-006** bars a user from lowering, and **AR-AST-007** bars an assisted component from removing a classification. Only a Product Management change to the AR-DET-005 rule set could lower it. The direction of travel in the specification is monotone-up, so an interim default that is intended to be lowered later must say so explicitly at the point it is adopted, or it will read as a floor.

**Recorded, not recommended.** It is a live option and PM should see its price.

### 4.5 Recommendation

**G-13R.4 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-13.9 shall be narrowed, not repealed, to read in substance: every canonical attribute shall carry a sensitivity tier slot; no attribute shall be released to implementation, to stored production data, or to any surface that discloses or fills a value, without an assigned tier. A vocabulary version may be approved structurally with tiers marked TBD, provided the version is marked NOT RELEASABLE and G-13 closure remains gated on G-14 and G-15.**
*Basis:* FR-INF-007 and FR-SENS-001 bind the system, not an analysis artefact; FR-SENS-002's protection attaches at disclosure; G-12 §19.3's evaluation/implementation split.
*Amends:* **approved decision G-13.9** — identified explicitly as a reopening in §10.
*Effect:* takes studies S-1/S-4 and assumption A-5 off the critical path for G-12 authoring, ground-truth annotation, and D-02 §11 design. They remain on the critical path for the **build** and for **any autofill**, which is where the protection belongs.

**G-13R.5 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-13 closure shall be split into two named gates.**

| Gate | Content | Unblocks | Gated on |
| --- | --- | --- | --- |
| **G-13-A — structurally complete** | Shape frozen; every attribute carries properties 1–6; property 7 present and TBD; version marked **NOT RELEASABLE** | G-12 authoring · L6/L7 annotation design · D-02 §11.6 design | G-19, the scope revision, §18.7, the G-13.12 minimality re-test |
| **G-13-B — releasable** | Every tier assigned | Implementation of FR-INF-001…009 · any autofill under FR-FILL-001 · production storage | **G-14, G-15** (A-5; studies S-1/S-4) |

*Basis:* §4.3; G-12 §19.3. *Note:* this does not weaken G-13.11 — no placeholder attribute enters code, schema, migrations, fixtures, or evaluation tooling before **G-13-A** is approved.

**Explicitly not decided here:** any tier, for any attribute; any classification rule; the default tier. **G-14 and G-15 are untouched.**

---

## 5. D3 — Scope / Context Problem

### 5.1 The problem, restated precisely

A person legitimately holds several qualifications. `education.year_of_passing` has one value for the 10th qualification, another for the 12th, another for a degree. These are not disagreements.

But **G-13.3 (approved)** fixes identity as *the same canonical attribute identifier*, established by the mapping alone. **G-13.5 (approved)** fixes the comparison function as *the normalised form*. So three documents supplying three different normalised values for one identifier is, by construction, a conflict.

### 5.2 Verified consequence chain

This is not a modelling nicety. Each step is quoted from `step3.pdf`.

| Step | Requirement | Text |
| --- | --- | --- |
| 1 | **FR-INF-004** (MUST) | "detect when two documents give different values for the same attribute" → **fires** |
| 2 | **AR-DET-008** (MVP) | detection "shall be deterministic" → **fires every time, for every such person** |
| 3 | **FR-INF-005** (MUST) | "Detected conflicts shall be presented to the user for resolution. The system shall not resolve a conflict automatically." → **surfaced** |
| 4 | **BR-004** | "may not resolve it by rule, recency, or preference" → **no automatic escape exists** |
| 5 | **EC-004** | "Raise a conflict, mark neither authoritative, and **treat any field needing that attribute as ambiguous until the user resolves it**" |
| 6 | **FR-AMB-001** (MUST) | a field is ambiguous when "source documents conflict" → **autofill blocked for that field** |
| 7 | **FR-INF-006** (MUST) | "record which value the user designated authoritative and retain the alternatives" |

**Step 7 is the sharpest point.** To clear the conflict the user must designate **one** year of passing authoritative across three distinct qualifications. The other two are demoted to "alternatives." The product's only conflict-clearing path **destroys correct data**, and it does so for every user holding more than one qualification — that is, for the entire target population of an education-document product.

Steps 5–6 mean that until they do, **every form field asking for a year of passing, an awarding body, a result, or a roll number is permanently ambiguous.**

### 5.3 A consequence for D-02 that has not been recorded anywhere

**D-02 §11.6** defines the measure that makes conflict-detection evaluation worth running:

> **False-conflict source attribution** — "For each false conflict: was the cause **extraction error, normalisation, or genuine document variance**?"
>
> "Detection is deterministic under AR-DET-008 — it cannot be 'improved' by choosing a better engine. So **a false conflict is always evidence about extraction or normalisation.**"

**That premise fails under scope collapse.** A scope-collapse false conflict is caused by neither extraction nor normalisation — both worked perfectly — and it is not "genuine document variance" either, since the documents do not vary about anything. It is a **fourth cause**, and D-02 §11.6's three-way taxonomy would misattribute every instance of it as "genuine document variance", which is the bucket that reads as *no action needed*.

So the scoping gap does not merely produce bad product behaviour. **It silently disarms the measure designed to detect bad product behaviour.** D-02 §11.6 needs a fourth attribution category, and that is a D-02 revision this analysis does not make.

### 5.4 Where can scope live? Four locations, each tested

**Location A — on the attribute definition** (an eighth property, e.g. `scope: person | qualification`).

The definition can say *what kind* of subject an attribute describes. It cannot say *which* subject a particular value describes — one definition serves many values. So A declares the scope **type** and supplies no **instance**, and the comparison in FR-INF-004 needs the instance.
**Necessary information, insufficient alone.**

**Location B — on the extracted value** (each value carries a scope key; FR-INF-004 compares within a key).

This is where the instance must live — FR-INF-002 already establishes that provenance is a property of the *value*, and G-13 §9 property 11 already classifies value-level facts as out of the definition.

The hard part is **how the key is derived**, and AR-DET-008's determinism constrains it:

- **Key = source document identity.** Deterministic — and **fatal**: two documents never share a key, so FR-INF-004 detects nothing, ever. It satisfies determinism by making the requirement vacuous.
- **Key = an extracted content value** (the qualification named on the document). This makes conflict identity depend on extraction accuracy, and it is identity established by **value similarity** — which **G-13.3 explicitly prohibits** ("never by value similarity"). **AR-AST-007** additionally forbids an assisted component escalating its own authority, which is what letting a probabilistic read decide conflict identity would do. **Excluded by approved decision.**
- **Key = the document's classified type.** Deterministic; produced by FR-OCR-002/003, which the product already owes; needs no content extraction. **Viable — this is Location C.**

**Location C — in the document-type mapping** (G-12 declares, per type, the scope instance its values belong to).

10th marksheet → scope instance *secondary*; 12th marksheet → *senior-secondary*; degree certificate → *degree*. FR-INF-004 then compares `education.year_of_passing` only within a scope instance. Two 10th marksheets (an original and a reissue) still conflict correctly. A hall ticket's roll number and its corresponding marksheet's roll number **also** need to compare — so the hall ticket must map to the same scope instance as the examination it admits to, which the type alone does not determine.

Three ceilings, stated:
1. **Two degrees collapse.** A BSc and an MSc both classify as *degree certificate* and share a scope instance — the false conflict returns for that person.
2. **It couples scope to the §7.1 type set**, which is provisional (ASM-001) and demotable — the coupling G-13 §9 property 9 rejected for a different property.
3. **G-10 can break it.** Under register D-04.5's reading (c) — "marksheet" is a *family* covering 10th, 12th and semester — the three collapse into one type and therefore one scope instance, and the problem returns in full.

**Location D — remove education concepts from the vocabulary**, leaving them as per-type fields mapping to no attribute (G-12.4's "explicitly none").

Tested and **closed by requirement**. `step3.pdf` §8's capability table records, for *Match user information*: **"From the structured record only. No inference…"** (FR-FILL-001/002). A value outside the structured record cannot be filled. And anything inside the record is an *attribute* — FR-INF-002 binds "every attribute value", FR-INF-007 binds "every attribute". So education values cannot simultaneously be fillable and not be attributes. Removing them from the vocabulary removes the entire education use case, and re-admitting them requires amending FR-INF-004's applicability — **a specification amendment under §11's Containment Rule, not a G-13 revision.**

### 5.5 Multiplicity, examined directly

Could the approved property 6 absorb this by setting the education attributes to *repeating*?

**No, and G-13's own reasoning says why.** §9 property 8 gives multiplicity exactly one job: to distinguish *"two documents disagree"* from *"this attribute legitimately holds two values."* Setting *repeating* suppresses the false conflicts **and the true ones together** — two documents disagreeing about the *same* qualification's year become two legitimate values, and FR-INF-004 goes silent on a real disagreement. §9 property 8 names that outcome itself: "or silently missed ones."

`single | repeating` is a **one-bit answer to a grouping question**. It can say *how many*, and cannot say *how many per what*. G-12 §14.0.2 reached the same conclusion and is correct.

**But this is the important part:** the failure is not that the shape lacks a property for this. It is that **property 6 was defined too narrowly for the purpose G-13 §9 explicitly gave it.** The property is already in the right place, already justified by the right requirement, and already aimed at exactly this failure mode. It was given a two-value domain when the job needs a keyed one.

That finding is what makes the recommended revision small, and it is derived from G-13's own text rather than assumed.

### 5.6 Effect on each named requirement

| Requirement | Effect if unresolved | Effect under the §9 recommendation |
| --- | --- | --- |
| **FR-INF-004** | Fires on every multi-qualification person; a permanent false conflict per education attribute | Compares within a scope instance; fires only on genuine disagreement |
| **BR-004** | No escape — resolution by rule is prohibited, so the false conflict cannot be cleared automatically | Unchanged and unweakened; fewer conflicts reach it, none by rule |
| **FR-INF-005** | Every such conflict must be surfaced; the user is asked to resolve a non-question | Unchanged; surfaces only real disagreements |
| **AR-DET-008** | Satisfied — determinism is not the problem; the wrong thing is determined | Preserved: the scope key is derived from classification, not from a probabilistic read |
| **D-02 §11.6** | Attribution taxonomy misclassifies scope collapse as "genuine document variance" (§5.3) | Needs a fourth attribution category regardless — flagged, not fixed here |
| **Multiplicity** | Cannot express the constraint; both settings are wrong (§5.5) | Widened to carry it |
| **Conflict detection overall** | Satisfies FR-INF-004 literally while making the product unusable — the exact failure D-02 §11.6 exists to expose | Restored to detecting disagreement |
| **FR-INF-006** | The clearing path destroys two correct values out of three (§5.2 step 7) | No longer reached for scope-distinct values |
| **EC-004 / FR-AMB-001** | Every education form field permanently ambiguous; autofill blocked | Cleared |

### 5.7 The connection to G-19 that changes the sequencing

**G-19** asks whether FR-ACC-004's *profile* and FR-INF-001's *structured record* are two stores or two views. G-13 §16.1 records that if they are two stores, "the vocabulary may need an eighth property stating **which store** an attribute belongs to."

The two questions are not the same, but they are the same question asked twice:

- **FR-ACC-004** — "a user profile of **canonical personal attributes**" — the subject is *the person*.
- **`education.year_of_passing`** — the subject is *a (person, qualification) pair*.

Store membership is a binary; qualification scope is a grouping key with cardinality greater than one. **They are different properties.** But both are answers to "what is a value an assertion *about*?", and a scope model that names the subject makes store membership derivable from it (person-scoped → profile; anything else → record only), whereas the reverse is not true.

**Two conclusions, and the second is the schedule-critical one:**
1. Whether one property serves both is a real design question and **is not decided here** — it depends on G-19's answer, which does not exist.
2. **Both changes touch the same property list, and G-13 §18 X4 freezes that list once.** They must land in one revision. Sequencing the scope revision before G-19 would freeze a shape that G-19 may immediately reopen.

---

## 6. Impact on the Seven-Property Shape

### 6.1 The four outcomes, tested rather than assumed

**Outcome A — seven properties sufficient; scope represented elsewhere.**
**Rejected.** Scope must be expressible in the definition, because the definition is what an author consults when mapping a field and what the comparison function is built from. §5.4 Location A shows the definition must at least declare the scope **type**; no existing property declares it. Semantic definition is prose and does not change the comparison function, which **G-13.5** fixes as the normalised form. Data type describes the value, not its subject. So A is unavailable — **unless** the scope type is folded into an existing property, which is outcome C.

**Outcome B — an eighth property is required.**
**Available, and not minimal.** A `scope` property would work. But it duplicates the job **G-13 §9 property 8 already assigns to multiplicity** — separating a conflict from two legitimate values — leaving two properties responsible for one question and two places for them to disagree. G-13 §9 rejected three candidate properties on exactly that reasoning (aliases: "a second place to be wrong"; document-type applicability: "derivable, duplicated, and a second place to be wrong"). Applying G-13's own stated test to G-13's own shape rules B out as the *first* choice.

Note also that B is the outcome G-19 may independently force, for a different property. If G-19 returns "two stores", the shape gains a store property regardless — and it should not gain a scope property as well if one widened property covers the scope job.

**Outcome C — an existing property is redefined.**
**Recommended.** Property 6 widens from `single | repeating` to a **scope-keyed cardinality**: *one value per <scope>*, where `<scope>` names the subject the attribute describes. `person.full_name` → *single per person*. `education.year_of_passing` → *single per qualification*.

Why this is the minimum:
- The **property count is unchanged**, so G-13.2's structure survives; only the wording "single or repeating" and the phrase "exactly these seven properties, and no others" need touching, and the second only to confirm it still holds.
- The property is **already justified by the right requirement** for exactly this failure (§2.4).
- It **declares the scope type**, discharging Location A.
- It leaves the scope **instance** at value level, which is where FR-INF-002 already puts value-level facts.
- It keeps `repeating` expressible as *many per <scope>*, so nothing the approved domain could say is lost.

**Outcome D — another model.**
Two were tested. **Redefining G-13.3's identity relation** to include a scope key is strictly larger than C — it reopens the decision G-13 §17 calls "the pivotal decision" and the one with the most downstream review attached. **Removing education attributes from the vocabulary** (§5.4 Location D) is closed by FR-FILL-001's structured-record-only constraint and would require a specification amendment. Neither is minimal.

### 6.2 What must change, exactly

Assuming outcome C, the revision touches **two approved clauses and no others**:

| Approved clause | Change | Size |
| --- | --- | --- |
| **G-13.2**, property 6 row | "Multiplicity — single or repeating" → a scope-keyed cardinality | **Wording of one row.** Property count unchanged; the "exactly these seven, and no others" clause survives intact |
| **G-13.5** | The comparison function for FR-INF-004 becomes the normalised form **within a scope instance**, not the normalised form alone | **One qualifying phrase.** The re-approval and evidence-invalidation consequence attached to G-13.5 is unchanged and now correctly covers scope-rule changes too |

**Not touched:** G-13.1, **G-13.3** *(identity is still by attribute identifier via the mapping — the scope key qualifies the comparison, it does not establish identity by similarity)*, G-13.4, G-13.6, G-13.7, G-13.8, G-13.10, G-13.11, G-13.12, G-13.13, G-13.14. **Ten of fourteen approved decisions survive untouched**, plus G-13.9 which §4 addresses separately for an unrelated reason.

### 6.3 What outcome C does not do

It does not say **how a scope instance is resolved**. That is a genuinely open decision with the three candidate derivations of §5.4 Location B, one of which (value similarity) is already excluded by G-13.3. It must be decided; it must not be decided here.

---

## 7. Impact on G-12

### 7.1 Structural

| G-12 element | Disposition under this analysis |
| --- | --- |
| §1–§13 (requirements analysis) | **Unaffected.** The finding — `step3.pdf` defines zero information fields — stands |
| §15 registry, §17.1 P1–P11, P13–P14 | **Transferred to G-13 as a DRAFT CANDIDATE SET** (G-13R.2) |
| §17.1 P12 (per-type field sets) | **Stays in G-12** — this is G-12's substance |
| §17.1 P15, P16, P17 and §17.2 exclusions | **Stay in G-12.** §17.2 is a per-type authoring output and the register's answer to G-02 §8.6 |
| §14 per-type tables | **Re-authored** after G-13-A, as *field* definitions with field identifiers mapping to approved attributes or explicitly to none (G-13R.3) |
| §14.0.2, §18.1 | **Discharged** by the G-13 revision, not by G-12 |
| §18.2, §18.3, §18.4, §18.5 | **Move to G-13** with the attributes they qualify — each is a normalisation or data-type question, which G-13.2 properties 4 and 5 own |
| §18.6 (presence unevidenced) | **Stays in G-12** — required/optional is per type, G-13 §13.2 excludes it from G-13 |
| §18.7 (identifier storage) | **Upstream of G-13-A** for two candidate attributes — see §7.3 |
| §18.8 (unmapped-value destination) | **G-13.g1**, already registered as a candidate gap; G-13R.3 restores the construct that expresses it |

### 7.2 The multiplicity TBDs resolve on transfer

G-12 §19.1 rates six of ten attributes NOT EVALUATION-READY; **five of the six fail on the single §18.1 scoping gap**, expressed as multiplicity TBD. Under outcome C those five gain a multiplicity — *single per qualification* — as soon as the shape revision lands. The sixth, `person.postal_address`, fails on §18.3 (no data type) and is unaffected by the scope revision.

### 7.3 Two G-12 findings that must not be lost in the transfer

**(a) The identifier-storage decision is upstream of the vocabulary, not downstream.** D-02 §11.7 (safety-relevant) and register D-05.3 leave open "whether the identifier number is stored at all, masked, or stored in part". If the answer is *not stored*, `person.aadhaar_number` and `person.pan_number` **should not exist as attributes at all** — so §18.7 gates their entry into the vocabulary, not merely their implementation. G-12 §19.1 rated both **EVALUATION-READY**, which would authorise annotators to transcribe them into ground truth before the decision that governs them, and while G-02 §8.6 states that derived-artefact redaction scope "cannot be answered today". **Both must be NOT EVALUATION-READY until §18.7 resolves.**

**(b) The consumer test needs evidence that exists today.** G-13.12 (approved) requires each attribute to be "justifiable against a named requirement". G-12's named consumer for eight of ten attributes is **FR-FILL-001**, which is a *gate* on filling and enumerates nothing — it admits every candidate equally. The discriminating claims ("an application form's education block asks for the awarding body") are not in `step3.pdf`.

The evidence that would discriminate **is obtainable now and needs no corpus**: `step3.pdf` §10 states the MVP is demonstrated against "a controlled mock application form — an MCA-style application **constructed by the team**" (**ASM-002**). Its field inventory is a team artefact, not a requirements gap. It is the missing input to the G-13.12 minimality test.

**G-13R.6 — PROPOSED DECISION — REQUIRES APPROVAL**
**The field inventory of the §10 / ASM-002 controlled mock form shall be documented as a named project artefact and used as the consumer evidence for the G-13.12 minimality test.**
*Basis:* G-13.12 (approved) requires a named consuming requirement; FR-FILL-001 does not discriminate; §10 makes the form a team artefact. *Not a requirement:* `step3.pdf` does not enumerate the form's fields and does not oblige anyone to.

### 7.4 Sequencing effect

G-12 authoring is blocked on **G-13-A**, not on G-13-B. Under G-13R.4/G-13R.5, G-14 and G-15 no longer block G-12. The type-boundary decisions (**G-09**, **G-10**, **G-11**, **D-04.4** for student ID and hall ticket, **D-04.7** for resume) block **G-12** but **not** the vocabulary — G-13 §9 property 9 deliberately decoupled the vocabulary from the type set — so they run in parallel with vocabulary authoring rather than ahead of it.

---

## 8. Candidate Revision Options

Four coherent packages. Each is complete; they are alternatives, not a menu.

### Option 1 — Minimum revision: widen multiplicity

Redefine G-13.2 property 6 to a scope-keyed cardinality; qualify G-13.5's comparison function by scope instance; narrow G-13.9 to release-time; split closure into G-13-A / G-13-B.

| | |
| --- | --- |
| **Approved clauses reopened** | G-13.2 (one row), G-13.5 (one phrase), G-13.9 (scope of the prohibition) |
| **Approved clauses surviving** | 11 of 14, including **G-13.3** |
| **Property count** | Unchanged at seven |
| **Pros** | Smallest diff to an approved artefact. Property 6's own justification (§2.4) already names this failure. Nothing the approved domain could express is lost. Leaves room for G-19's property without pre-empting it |
| **Cons** | Property 6 now carries two ideas (subject and cardinality). Still requires a separate decision on scope-instance resolution |
| **Risk** | If G-19 returns "two stores", the shape gains an eighth property anyway — but Option 1 does not conflict with that |

### Option 2 — Eighth property: explicit `scope`

Add `scope` as property 8; leave multiplicity as `single | repeating` interpreted within a scope.

| | |
| --- | --- |
| **Approved clauses reopened** | G-13.2 (the "exactly seven, and no others" clause **and** the property list), G-13.5, G-13.9 |
| **Pros** | Cleanest conceptual separation. Most legible to a future author. Aligns with G-13 §16.1's own anticipation of an eighth property |
| **Cons** | Two properties answer one question — the duplication test G-13 §9 used to reject three other candidates. Breaks the "and no others" clause outright rather than widening a row |
| **Risk** | If G-19 also adds a property, the shape reaches nine, and two of them (`scope`, `store`) are correlated — the derivable-duplication G-13 §9 property 9 warned about |

### Option 3 — Unified subject model

A single property naming the **subject** an attribute asserts about (`person`, `qualification`, …), from which both scope grouping **and** G-19's store membership are derived.

| | |
| --- | --- |
| **Approved clauses reopened** | G-13.2, G-13.5, G-13.9, and **G-19 is pulled into scope** |
| **Pros** | Answers both open shape questions with one property. Strongest conceptual grounding — FR-ACC-004's "canonical **personal** attributes" is itself a subject statement |
| **Cons** | **Cannot be specified before G-19 is answered.** Larger review surface. Risks designing a general model for two known cases |
| **Risk** | Scope creep into G-19, which has its own owner and its own register entry (D-08.2) |

### Option 4 — Defer: freeze nothing, record the risk

Take no shape decision now. Author the vocabulary with multiplicity TBD for scope-affected attributes, as G-12 §15 already does, and revisit after G-19.

| | |
| --- | --- |
| **Approved clauses reopened** | G-13.9 only |
| **Pros** | Smallest governance action. Honest about G-19's absence |
| **Cons** | **Does not unblock anything.** G-13 §18 X8 requires multiplicity on every attribute, so **G-13-A cannot be reached**; therefore G-12 cannot be authored, and L4–L7 stay unannotatable. Five of ten candidate attributes stay NOT EVALUATION-READY |
| **Risk** | Sprint 4's field-extraction track remains blocked for the duration of G-19, with no compensating work unblocked |

### Comparison

| | Opt 1 | Opt 2 | Opt 3 | Opt 4 |
| --- | --- | --- | --- | --- |
| Approved clauses reopened | 3 | 3 (one more severely) | 3 + G-19 | 1 |
| Property count after | 7 | 8 | 7 | 7 |
| G-13-A reachable before G-19? | **Yes**¹ | **Yes**¹ | **No** | **No** |
| Survives G-19 = "two stores"? | Yes, +1 property | Yes, +1 property (→9) | Yes, by construction | n/a |
| Duplicated responsibility | Low | **Medium** | Lowest | n/a |
| G-12 unblocked | **Yes** | **Yes** | Later | **No** |

¹ Reachable in principle. **§5.7 recommends against it**: X4 freezes the property list once, and freezing before G-19 risks an immediate second amendment.

---

## 9. Recommended Minimum Revision

### 9.1 The recommendation

**Option 1, sequenced behind G-19's answer.**

Option 1 is the smallest change that carries the requirement. §5.7's finding says the *timing* should not be as early as Option 1 alone permits: the property list is frozen once (X4), so G-19's answer and the scope revision belong in one revision event. Taking Option 1's content with Option 3's timing costs a wait on G-19 and buys one freeze instead of two.

If G-19 cannot be answered on the sprint's timescale, the fallback is Option 1 on its own with the risk recorded — which is exactly the escape G-13 §16.1 already contemplates for G-19 ("or should close with that risk recorded"). That is a Product Management call, not an engineering one, and it is listed at **A6** in §10.

### 9.2 The proposed revisions

**G-13R.7 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-13.2's property 6 shall be redefined from "Multiplicity — single or repeating" to a scope-keyed cardinality: how many values the attribute may hold, and per what subject. The property count remains seven and G-13.2's "exactly these seven properties, and no others" clause is retained unchanged.**
*Basis:* **G-13 §9, property 8** — the property's own approved justification is "FR-INF-004 cannot otherwise distinguish 'two documents disagree' from 'this attribute legitimately holds two values'", which is a verbatim statement of the failure it currently cannot express (§2.4, §5.5). FR-INF-004, AR-DET-008, BR-004, FR-INF-005, EC-004, FR-AMB-001.
*Reopens:* **approved decision G-13.2**, one row.
*Explicitly not decided:* the set of admissible subjects. `person` and `qualification` are the two the evidence to date demands; whether others are needed is an authoring question for G-13's contents.

**G-13R.8 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-13.5's comparison function for FR-INF-004 shall be the normalised form within a scope instance, rather than the normalised form alone. G-13.5's existing consequence — that a change to the comparison behaviour requires re-approval and invalidates prior evaluation evidence for the affected attributes — shall extend to scope rules.**
*Basis:* FR-INF-004's subject is two documents; AR-DET-008 requires determinism; G-13.5 already treats the comparison function as a conflict-detection behaviour decision.
*Reopens:* **approved decision G-13.5**, one qualifying phrase.
*Note:* **G-13.3 is NOT reopened.** Identity remains established by the field→attribute mapping alone. A scope key qualifies *which values are compared*; it never establishes identity by label, value, proximity or position.

**G-13R.9 — PROPOSED DECISION — REQUIRES APPROVAL**
**The rule by which a value's scope instance is resolved shall be a Product Management decision recorded in the vocabulary revision, and shall be deterministic without reference to any extracted content value.**
*Basis:* AR-DET-008 (determinism); **G-13.3** prohibits identity by value similarity; **AR-AST-007** forbids an assisted component escalating its own authority.
*Candidates, none selected here:* (i) derived from the document's classified type (FR-OCR-002/003) — deterministic, cheap, with the three ceilings named in §5.4 Location C; (ii) declared per type in the G-12 mapping — the same mechanism, owned by G-12; (iii) a user-designated qualification grouping — outside anything `step3.pdf` requires, and new scope.
**This is the one place a resolution could most easily be invented. It is not invented here.**

**G-13R.10 — PROPOSED DECISION — REQUIRES APPROVAL**
**G-19 shall be answered before the seven-property shape is frozen under G-13 §18 X4, and the scope revision and any G-19-driven property change shall land in one revision event.**
*Basis:* §5.7; G-13 §16.1; G-13 §18 X4 depends on X2. *Fallback, requiring explicit PM acceptance:* freeze without G-19 and record the risk, per G-13 §16.1's own alternative.

**G-13R.11 — PROPOSED DECISION — REQUIRES APPROVAL — for D-02, not for G-13**
**D-02 §11.6's false-conflict source attribution shall gain a fourth category — scope-model error — distinct from extraction error, normalisation, and genuine document variance.**
*Basis:* §5.3. Without it the measure misfiles every scope-collapse conflict under "genuine document variance", the category that reads as requiring no action.
*Owner:* the D-02 document's owner. **This analysis does not modify D-02.**

### 9.3 What survives untouched

**G-13.1, G-13.3, G-13.4, G-13.6, G-13.7, G-13.8, G-13.10, G-13.11, G-13.12, G-13.13, G-13.14** — eleven of fourteen approved decisions, including the pivotal identity decision. **G-13.2** loses one row's wording; **G-13.5** gains one qualifying phrase; **G-13.9** is narrowed in scope for the unrelated reason in §4.

### 9.4 The ten candidate attributes

**Not approved, not finalised, not endorsed.** They transfer to G-13 as a **DRAFT CANDIDATE SET** under G-13R.2 and must be re-tested before any of them enters a vocabulary version:

1. Re-tested against **G-13.12** using the §10/ASM-002 mock-form inventory (G-13R.6) — the current FR-FILL-001 justification does not discriminate (§7.3b).
2. Re-tested against G-13's admission tests. G-12 §14.0 asserts all ten passed its "definable now" test; **six demonstrably did not** — `person.postal_address` has no data type and no normalisation rule, and five education attributes had no multiplicity. Outcome C supplies multiplicity for the five; `person.postal_address` remains undefinable until G-12 §18.3 resolves.
3. `person.aadhaar_number` and `person.pan_number` gated on **§18.7** before entering the vocabulary at all (§7.3a).
4. `education.aggregate_result` re-examined against **G-13.2 property 3** — its semantic definition is by page position ("the overall result… as printed on the document"), which is not prose "precise enough that two authors mapping two documents agree" when a marksheet prints both a percentage and a division. G-12 §18.5 concedes it cannot be meaningfully compared, so FR-INF-004 over it is inoperative as defined.

---

## 10. Approval Dependencies

| # | What must be approved or resolved | Owner | Why it cannot be skipped |
| --- | --- | --- | --- |
| **A1** | **G-13R.1, G-13R.2, G-13R.3** — ownership restored; registry transferred; field identifiers reinstated | Product Management | Without them approved decision **G-13.8**'s ordering stays unexecutable and the field→attribute interface stays degenerate |
| **A2** | **G-13R.4, G-13R.5** — G-13.9 narrowed; closure split into G-13-A / G-13-B | Product Management · Privacy | **Reopens approved G-13.9.** Otherwise studies S-1/S-4 and assumption A-5 sit on the critical path of every field-extraction activity in the sprint |
| **A3** | **G-13R.7, G-13R.8** — multiplicity widened; comparison function scoped | Product Management · Architecture | **Reopens approved G-13.2 and G-13.5.** Without them FR-INF-004 raises a permanent false conflict per education attribute per user, and EC-004 makes every education form field permanently ambiguous |
| **A4** | **G-13R.9** — the scope-instance resolution rule | Product Management | The one place a model could be invented. Constrained by AR-DET-008, G-13.3 and AR-AST-007; not selected here |
| **A5** | **G-19** — profile vs structured record | Product Management · Architecture | **G-13 §18 X4** makes the shape freeze depend on it, and G-13 §16.1 says it may add a property |
| **A6** | Whether to freeze the shape **without** G-19, accepting the recorded risk | Product Management | G-13 §16.1's own alternative. A schedule/risk trade, not an engineering call |
| **A7** | **G-13R.6** — the mock-form field inventory as consumer evidence | Product Management | **G-13.12** (approved) requires a named consuming requirement; FR-FILL-001 does not discriminate |
| **A8** | **§18.7** — whether the identifier numbers are stored at all, masked, or in part | Product Management · Privacy | Safety-relevant; gates two candidate attributes' **entry into the vocabulary**, not merely their implementation |
| **A9** | **G-14** and **G-15** | Product Management | Gate **G-13-B** only, under A2. **Not resolved here.** Gated on A-5, studies S-1/S-4 |
| **A10** | **G-09**, **G-10**, **G-11**, **D-04.4** (student ID, hall ticket), **D-04.7** (resume) | Product Management | Gate **G-12**, not the vocabulary. D-04.4's two entries are recorded **DECISION REQUIRED** and were not treated as dependencies in G-12 Part II |
| **A11** | **G-13R.11** — D-02 §11.6's fourth attribution category | Owner of `SPRINT_4_D02_OCR_EVALUATION_PLAN.md` | Without it the measure that would detect scope collapse misfiles it as no-action |
| **A12** | Register entries: this revision, **G-13.g1**, and G-12 §18's candidate gaps | Owner of the decision register | **No G-number is invented here** |
| **A13** | Whether the G-13 document is revised in place under a new version, or superseded | Product Management | G-13.10 (approved) requires versioning; **this analysis edits no document** |
| **A14** | **§11 Containment Rule** amendment to `step3.pdf`, or formal acceptance of the divergence | Product Management | **G-13.13** (approved): approval is never an amendment to the specification |

---

## 11. Proposed Revised Decision Sequence

### 11.1 Derivation

The sequence below is derived from constraints, not chosen. Each edge cites the approved decision or requirement that creates it.

| Edge | Source |
| --- | --- |
| G-19 → shape freeze | **G-13 §18 X4** depends on X2; **G-13 §16.1** |
| Shape revision → vocabulary contents | **G-13 §15.3 T1** — contents are authored *against* the shape |
| §18.7 → contents (two attributes) | If not stored, the attribute should not exist (§7.3a) |
| Mock-form inventory → contents | **G-13.12** (approved) minimality test needs a discriminating consumer |
| Vocabulary contents → G-12 mapping | **G-13.8** (approved) |
| G-13-A → L6/L7 annotation | **D-02 §7.1** attributes L6/L7 to G-13; **G-13.11** bars evaluation tooling before closure |
| G-12 mapping → L4/L5 annotation | **D-02 §7.1** attributes L4/L5 to G-12 |
| G-09/G-10/G-11/D-04.4/D-04.7 → G-12 mapping **only** | **G-13 §9 property 9** decouples the vocabulary from the type set |
| G-14/G-15 → G-13-B → build & autofill | **FR-INF-007**, **FR-SENS-002**, **FR-FILL-001** ("classified routine") |
| Corpus → presence evidence → required/optional | G-12 §18.6; **AR-AST-008** |
| Nothing → stage-1 D-02 | **G-13.14** and **G-02** both approved; independent roots |

### 11.2 The sequence

```
RUNNING NOW — blocked by nothing in this analysis
  ├── G-02 corpus collection            (APPROVED governance; G-13.14)
  └── D-02 stage 1: OCR quality · classification · failure behaviour ·
      engine eligibility · normalisation determinism

PARALLEL TRACKS — all may start immediately

  TRACK A — SHAPE                      TRACK C — SENSITIVITY (long pole)
    G-19 answered            [A5]        studies S-1 / S-4  →  A-5
      ↓                                    ↓
    ONE revision event:                  G-14 · G-15                    [A9]
      · scope (G-13R.7/R8/R9) [A3,A4]      ↓
      · any G-19 property                (feeds G-13-B only)
      ↓
    G-13.2 amended · X4 FREEZE

  TRACK D — TYPE BOUNDARIES            TRACK E — CONSUMER EVIDENCE
    G-09 · G-10 · G-11                   mock-form field inventory      [A7]
    D-04.4 (student ID, hall ticket)     (§10 / ASM-002 — no corpus needed)
    D-04.7 (resume)          [A10]
    (feeds G-12 only)

  TRACK B — VOCABULARY CONTENT   ← needs A(freeze) + E + §18.7 [A8]
    ownership restored, registry transferred          [A1]
      ↓
    draft candidate set re-tested vs G-13.12 and the admission tests
      ↓
    contents authored: properties 1–6 complete; property 7 = TBD
      ↓
    ══ GATE G-13-A — structurally complete, NOT RELEASABLE ══        [A2]
        unblocks:  G-12 authoring · L6/L7 design · D-02 §11.6 design

  TRACK F — G-12               ← needs G-13-A + Track D
    per-type field sets: field identifiers → attribute or explicitly none
    + missing-value semantics (question G / R5, absent from G-12 Part II)
    + data-type FORMAT (the half of G-12.4 property 5 not delivered)
    + required/optional marked TBD — HYPOTHESIS
      ↓
    L4/L5 annotatable · presence pass over the collected corpus
      ↓
    required/optional confirmed from evidence  ·  G-02 §8.6 redaction revisit
      ↓
    D-02 stage 2: field extraction · calibration · BR-001 threshold
      ↓
    §7.1 per-type inclusion / demotion

  ══ GATE G-13-B — releasable ══   ← Track C
      unblocks:  build of FR-INF-001…009 · any autofill under FR-FILL-001
                 · production storage of attribute values
```

### 11.3 What this sequence buys

| Change | Effect |
| --- | --- |
| G-14/G-15 moved off the G-12 critical path (A2) | Studies S-1/S-4 and assumption A-5 no longer gate field authoring, ground-truth design, or evaluation design — only the build and autofill |
| Type boundaries run parallel to vocabulary authoring | G-09/G-10/G-11/D-04.4/D-04.7 gate G-12 only; **G-13 §9 property 9** already decoupled the vocabulary from the type set |
| Mock-form inventory needs no corpus | The G-13.12 minimality re-test can start today |
| One shape-freeze event | Avoids amending and re-reviewing the property list twice |
| Stage-1 D-02 and corpus collection untouched | Both approved as independent roots; nothing here delays them |

### 11.4 What remains genuinely blocked, and by what

| Blocked | By |
| --- | --- |
| Build of FR-INF-001…009; any autofill | **G-14 / G-15** (A-5, studies S-1/S-4) — gate G-13-B |
| BR-001 / BR-002 threshold | **G-04, G-05, G-06, G-07** *and* the stage-2 evaluation. **AR-AST-008** requires evaluation before any threshold is set |
| §7.1 type inclusion / demotion | Per-type extraction results — study **S-6** |
| Whether extraction justifies FR-OCR-004 at all | §12.3, assumption **A-7** |
| Required/optional as fact | Corpus presence evidence (G-12 §18.6) |
| `person.postal_address` | G-12 §18.3 — no data type; unaffected by the scope revision |
| Destination of an unmapped value | **G-13.g1** / **G-27** |

---

## 12. G-13 Revision Exit Criteria

The revision is complete when **all** hold. Ordered by dependency. These are criteria for the **revision**, not for G-13 closure — G-13 §18's X1–X16 continue to govern that, with X4, X8 and X9 reinterpreted by R1–R12 below.

| # | Exit criterion | Depends on | Status today |
| --- | --- | --- | --- |
| **R1** | **G-13R.1 … G-13R.11** approved, or explicitly rejected with alternatives recorded | This document | **Not met — awaiting decision** |
| **R2** | **G-19** answered, or the freeze-without-G-19 risk explicitly accepted by PM | A5, A6 | **Not met** |
| **R3** | **G-13.2** amended: property 6 redefined; the seven-property count and the "and no others" clause confirmed | R1, R2 | **Not met** |
| **R4** | **G-13.5** amended: comparison function qualified by scope instance; the re-approval consequence extended to scope rules | R1 | **Not met** |
| **R5** | **G-13.9** amended: narrowed to release-time; **G-13-A / G-13-B** gates defined | R1 | **Not met** |
| **R6** | **G-13R.9** decided: the scope-instance resolution rule, deterministic and not derived from extracted content | R3 | **Not met** |
| **R7** | The amended shape **frozen** under a new vocabulary version (G-13.10) | R3, R4, R5, R6 | **Not met** |
| **R8** | Ownership restored: G-12 §15 and §17.1 P1–P11, P13–P14 transferred to G-13 as a **DRAFT CANDIDATE SET**; G-12 field identifiers reinstated | A1 | **Not met** |
| **R9** | Mock-form field inventory documented and the candidate set re-tested against **G-13.12** | A7, R8 | **Not met** |
| **R10** | **§18.7** answered; `person.aadhaar_number` and `person.pan_number` admitted, narrowed, or withdrawn **before** entering the vocabulary | A8 | **Not met** |
| **R11** | Every candidate attribute carries a scope-keyed multiplicity; **`person.postal_address`** carries a data type and normalisation rule, or is withdrawn | R7, R9, G-12 §18.3 | **Not met** |
| **R12** | **`education.aggregate_result`** re-tested against G-13.2 property 3, and either redefined or withdrawn | R9 | **Not met** |
| **R13** | **GATE G-13-A** declared: properties 1–6 complete for every attribute, property 7 present and TBD, version marked **NOT RELEASABLE** | R7, R9–R12 | **Not met** |
| **R14** | **D-02 §11.6** gains the fourth false-conflict attribution category | A11 | **Not met** |
| **R15** | Register updated by its owner: this revision, **G-13.g1**, and G-12 §18's candidate gaps carry IDs | A12 | **Not met** |
| **R16** | Decided whether the G-13 document is revised in place under a new version or superseded | A13 | **Not met** |
| **R17** | **G-14** and **G-15** closed; every tier assigned; **GATE G-13-B** declared | A9 | **Not met — outside this revision** |
| **R18** | `step3.pdf` amended under **§11's Containment Rule**, or the divergence formally accepted and recorded | R1–R13 | **Not met** |

**What the revision does and does not unblock.** R1–R13 reach **G-13-A**, which unblocks G-12 authoring, L6/L7 annotation design, and D-02 §11.6 design. They do **not** unblock: the build of FR-INF-001…009 or any autofill (R17); L4/L5 (needs G-12 closure); the BR-001 threshold (needs G-04, G-05, G-06, G-07 and the evaluation); §7.1 type inclusion (needs per-type results); or the FR-OCR-004 build (§12.3 additionally gates on **A-5** and **A-7**).

---

**Verification performed before completion**

| Check | Result |
| --- | --- |
| Every requirement quotation traced to `step3.pdf` | **Yes** — FR-INF-001…008, FR-ACC-004, FR-FILL-001, FR-SENS-001/002/006, FR-AMB-001, FR-OCR-002/003, BR-004, BR-020, AR-DET-003/005/008, AR-AST-007/008, EC-004, NFR-MNT-001/004, NFR-PRIV-001, §7.1, §8, §10, ASM-001, ASM-002, A-5, A-7 all read in context |
| Any attribute approved or finalised | **No.** The ten remain a **DRAFT CANDIDATE SET**; four are challenged in §9.4 |
| Any sensitivity tier assigned or rule invented | **No.** G-14 and G-15 untouched; register D-06.4's existing recommendation is cited with its cost, not adopted |
| Any scope-instance resolution model chosen | **No** — G-13R.9 states three candidates and selects none |
| Approved decisions reopened, and named | **Yes, three, each named explicitly:** **G-13.2** (property 6 row), **G-13.5** (comparison function), **G-13.9** (scope of the publication bar). **Eleven of fourteen survive untouched, including G-13.3** |
| New product decisions labelled | **Yes** — G-13R.1 … G-13R.11, every one **PROPOSED DECISION — REQUIRES APPROVAL** |
| Anything marked APPROVED | **No** |
| `SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md` modified | **No** |
| `SPRINT_4_G12_FIELD_DEFINITIONS.md` modified | **No** |
| `SPRINT_4_D02_OCR_EVALUATION_PLAN.md` modified | **No** — G-13R.11 is a recommendation to its owner |
| `SPRINT_4_DECISION_REGISTER.md` modified | **No** — no G-number invented; A12 leaves IDs to the register's owner |
| G-02 approved governance altered | **No** |
| G-19, G-20, G-14, G-15, G-09, G-10, G-11, D-04.4, D-04.7 resolved | **No** — each recorded as a dependency with an owner |
| `step3.pdf` modified | **No** |
| Production code, schema, migrations, dependencies, fixtures, evaluation tooling touched | **No** — **G-13.11** observed |
| Documents collected / OCR installed or run | **0 / No** |
| Committed or pushed | **No** |
