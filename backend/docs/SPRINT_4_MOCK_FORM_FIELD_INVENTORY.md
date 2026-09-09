# DOCURA — Sprint 4 §10 / ASM-002 Mock-Form Field Inventory

| Field | Value |
| --- | --- |
| Artefact | **The §10 / ASM-002 controlled mock-form field inventory** — the named project artefact that G-13 §15.4 **C-a**, register **D-05.14**, and **PD-A** each name as an owed input |
| Status | **SCAFFOLD — STRUCTURE EVIDENCED, INFORMATION CONTENT OWED.** Nothing here approves a vocabulary attribute, a field definition, or a sensitivity tier. |
| Created | 8 September 2026, after **G-13-A** was declared **MET** (register D-05.14), which unblocked G-12 *authoring* |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0, 25 August 2026 — **§10, §8 Table 8.1, ASM-002**, and the requirement families the demonstration journey (Table 10.1) cites |
| Related | [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) · [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) (§15.4 C-a) · [`SPRINT_4_G13_REVISION_ANALYSIS.md`](SPRINT_4_G13_REVISION_ANALYSIS.md) (G-13R.6) · [`SPRINT_4_G13_PM_DECISION_BRIEF.md`](SPRINT_4_G13_PM_DECISION_BRIEF.md) (PD-A) · [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) (D-05.14, D-05.15) |
| What this is | An evidence-backed record of **what `step3.pdf` actually constrains about the mock form** — its field-type coverage and its behavioural slots — plus an explicit statement of **what it leaves to the team to construct**. |
| What this is **not** | It is **not** the constructed mock form, and it does **not** enumerate the information fields the form requests. `step3.pdf` names none, and none is invented here. |

---

## 1. Why this artefact exists

**FR-OCR-004** (MVP, MUST) requires "the defined set of information fields" per document type; **FR-FILL-001** fills form fields "from the structured record only". Several G-13 candidate attributes claim a form consumes them — but **FR-FILL-001 admits every candidate equally** and therefore *discriminates nothing*. That is exactly **C-a** (G-13 §15.4): nine of the ten G-12 candidate attributes have **no discriminating consumer**, and the evidence that would supply one is *the field inventory of the mock application form* — the artefact `step3.pdf` §10 promises but does not enumerate.

Register **D-05.14** (8 Sep 2026) records **G-13-A — MET**, which unblocks G-12 *authoring*, and lists as still-open for G-12 "the four challenges **C-a…C-d**, and the **§10 / ASM-002 mock-form field inventory**." This document resolves the *dependency* on that inventory to the extent repository and `step3.pdf` evidence allows, and states precisely what remains owed.

### 1.1 The exact §10 / ASM-002 text

> **§10 (MVP Scope):** "The MVP is demonstrated end to end against a controlled mock application form — an MCA-style application **constructed by the team**. A controlled form is used because it makes the demonstration reproducible and lets us **include every field type deliberately**, rather than depending on a live portal that may change mid-demonstration. **ASM-002**"

> **ASM-002 (Appendix A):** "A controlled mock form is an adequate MVP demonstration surface; results on it will broadly hold on real portals." · Affects **§10** · Settled by "**Study S-3 form teardown**, then a shadow run against a real portal before claiming generality."

Two facts follow, and both are load-bearing:

1. The mock form is **constructed by the team** — it is a *project artefact*, not a requirements object. `step3.pdf` obliges no one to enumerate its fields, and does not.
2. What `step3.pdf` deliberately fixes about it is that it includes **every field type** (the seven of FR-FLD-007), so that the demonstration exercises every extension behaviour. It fixes the form's **structure**, never its **information content**.

---

## 2. The two layers of a "field inventory", and which one the evidence supports

| Layer | What it is | In `step3.pdf`? | Status here |
| --- | --- | --- | --- |
| **L-STRUCT — field-type & behaviour coverage** | Which of the seven form-field *types* appear, and which extension *behaviours* the form must exercise (fill, dropdown, ambiguity, match, approval, declaration) | **Yes** — §10 Table 10.1 (D5–D13), §8 Table 8.1, FR-FLD-007 | **§3 — EVIDENCED** |
| **L-INFO — information-field content** | *What personal information each field requests* (the semantic labels a real MCA-style application carries) | **No** — named nowhere | **§4 — OWED (team construction / S-3), NOT INVENTED HERE** |

**C-a's discriminating evidence lives in L-INFO, and L-INFO does not exist and cannot be derived from `step3.pdf`.** This document supplies L-STRUCT (a genuine G-12 authoring input and a guardrail for the team) and records L-INFO as explicitly owed. See §5 for the consequence.

---

## 3. L-STRUCT — what `step3.pdf` requires the mock form to contain (EVIDENCED)

Every row is traceable to `step3.pdf`. These are **form-field types and behavioural slots**, not information fields. A slot describes a role the form must contain at least once so a demonstration step is observable; it does **not** name what the field asks for.

| # | Slot the form must contain | Field type(s) | Demonstration step | Requirements |
| --- | --- | --- | --- | --- |
| S1 | **Full coverage of the seven MVP field types**, each with **declared constraints and a required flag** | text · number · date · dropdown · radio · checkbox · file-upload | D5 ("All seven MVP field types enumerated with declared constraints and required flags") | FR-FLD-007 · FR-FRM-001/002/003/004 · §8 Table 8.1 · §10 ("include every field type deliberately") |
| S2 | At least one **routine field above threshold** that is filled and **reformatted to the field's declared constraints** | text / date / number | D7 | FR-FILL-001…005 · FR-FILL-002 (reformat to declared constraints) · AC-4 (a date field with a declared format reformatted without altering the date) |
| S3 | At least one **static dropdown** matched to a single high-confidence value | dropdown | D8 | FR-DRP-001…003 |
| S4 | At least one **dependent dropdown** that is **re-read after its controller changes** | dropdown (dependent) | D8 | FR-DRP-002/003/008 |
| S5 | A **radio group** treated as single-choice under dropdown thresholds | radio | §8 Table 8.1 | FR-DRP-006 |
| S6 | A **routine checkbox** | checkbox | §8 Table 8.1 | FR-DRP-007 |
| S7 | At least one **deliberately ambiguous field** that triggers a prompt showing candidates, sources, and the reason | any interpretable type | D9 | FR-AMB-001…004 · (EC-019 gives one ambiguity shape: "the same attribute requested twice in one form") |
| S8 | At least one **file-upload field** with **declared size/format constraints** for document matching | file-upload | D10 | FR-MATCH-001…008 · FR-FRM-004 (declared accepted types / size limits) |
| S9 | At least one **sensitive field** requiring explicit, itemised approval before it is filled | any | D11 | FR-SENS-002/003 · FR-APR-001…004 |
| S10 | At least one **declaration checkbox**, classified **consequential** and demonstrably **left untouched** | checkbox (declaration) | D12 | FR-FLD-004 · FR-DRP-007 · BR-006 |

### 3.1 What S1–S10 fix and what they do not

- They fix that the form is **type-complete** (S1) and that it exercises **fill (S2), static and dependent dropdowns (S3/S4), radio (S5), routine checkbox (S6), ambiguity (S7), document matching (S8), sensitive-field approval (S9), and a consequential declaration (S10)**.
- They **do not name a single information field**. No row says the form asks for a name, a date of birth, an address component, a board, a year, a roll number, or any other datum. `step3.pdf` names none of these in a form context; searching it for *board*, *university*, *qualification*, *roll*, *percentage*, *CGPA*, *PIN*, *postal* returns nothing in the demonstration surface (consistent with G-13 §19.3).

---

## 4. L-INFO — the information content (OWED; NOT INVENTED HERE)

**`step3.pdf` enumerates none of the information the mock form requests.** Under ASM-002 the form is *constructed by the team*, and ASM-002's own settlement path is a **Study S-3 form teardown** — i.e. the real inventory would be obtained by tearing down a real MCA-style application, which has not happened. Therefore:

- The information-field content is a **team construction decision**, recorded here as **TBD**.
- It is **not** derivable from `step3.pdf`, and inventing it — from domain knowledge of what an application form "usually" asks — is exactly the invention **BR-009** and **G-13.11** forbid, and would fabricate the very discriminating evidence **C-a** demands.
- When the team constructs the form (or runs the S-3 teardown), the resulting field list should be recorded **in §4.1 below**, at which point each entry becomes factual consumer evidence for the G-13.12 minimality test.

### 4.1 Information fields the mock form requests

> **TBD — owed by the team's construction of the form (ASM-002 / Study S-3).** Populate this table only from the constructed form or an S-3 teardown; never from domain assumption. Each populated entry must record the form-field type it uses (an S1–S10 slot), the constraints it declares, and its required flag — none of which is invented here.

| Form field (as the form labels it) | Slot (S1–S10) | Declared constraints | Required? | Provenance |
| --- | --- | --- | --- | --- |
| *(none recorded — awaiting construction)* | — | — | — | — |

---

## 5. Consequence for C-a and the ten G-13 candidate attributes

The mock form is the consumer that would tell an *entailed* attribute from a *plausible* one. Because L-INFO is still owed, C-a is discharged only where an attribute has a **discriminating consumer independent of the mock form**.

| Candidate attribute (G-12 §15) | Independent discriminating consumer? | C-a status after this artefact |
| --- | --- | --- |
| `person.full_name` | **Yes** — §12.2 / P-06 name mismatch is the worked justification for FR-INF-004; already approved as `v0.1-draft` (PD-B) | **Discharged** (was already, for this one entry) |
| `person.postal_address` | Existence entailed by §7.1 "Identity and address" + FR-OCR-004 (PD-A); **components** need L-INFO | **Partly** — shape decided (PD-A A2); **component set owed by L-INFO**; also blocked by **C-b** |
| `person.aadhaar_number` · `person.pan_number` | The document's product purpose, but blocked upstream | **Not C-a's blocker** — blocked by **C-c** / identifier-storage decision (D-05.3, D-02 §11.7) |
| `education.awarding_body` · `education.year_of_passing` · `education.aggregate_result` · `education.roll_number` · `education.qualification_name` | **No** — *board / university / qualification / roll / percentage / CGPA* appear **zero** times in `step3.pdf`; their only cited consumer is FR-FILL-001, which does not discriminate | **STILL OWED** — L-INFO is precisely the evidence these need; additionally `education.aggregate_result` carries **C-d** |

**Net effect on C-a:** the *framework* is now in place and its evidence path is named and bounded, but the **discriminating content for the nine mock-form-dependent candidates remains owed** — by a team form-construction act, not by any further reading of `step3.pdf`. C-a is therefore **not discharged** by this artefact for those nine; it is made precise and its cost re-confirmed as "team construction, no corpus / engine / study" (register U5).

---

## 6. Consequence for PD-A (the address component set)

**PD-A** approved the address *shape* as a structured object (A2), with its components to be "**derived only from the §10/ASM-002 mock-form field inventory — none invented**" (register D-05.12 / brief §PD-A). This artefact is that inventory. Because §4 (L-INFO) is still owed, **the address component set remains pending** — `person.postal_address` has data type "structured object" but its components are **TBD** until the form's address field(s) are recorded in §4.1. This does not reopen PD-A; it identifies the exact input PD-A defers to.

---

## 7. The three concepts this artefact keeps separate

Per the G-12 disambiguation (§1.4) and G-13's scope, three concepts are **not** collapsed here:

| Concept | Lives where | This artefact |
| --- | --- | --- |
| **Form field** — an input on the third-party (mock) page | §8, FR-FRM/FR-FLD/FR-FILL/FR-DRP/FR-MATCH | **Enumerated structurally (§3); content owed (§4)** |
| **Document information field** — a value read out of a stored document | FR-OCR-004, per-type field sets | **Out of scope — G-12's, and not authored here** |
| **Canonical attribute** — what DOCURA knows about a person across documents | FR-ACC-004, G-13 vocabulary | **Out of scope — G-13's; no entry added or approved here** |

The mock form's information fields (§4, once constructed) are the **consumers** that justify a *canonical attribute*, which a *document information field* then maps to. Keeping the three distinct is what lets an entry in §4.1 discharge C-a for a specific attribute without redefining either of the other two artefacts.

---

## 8. What this artefact does not do

- It adds **no** canonical vocabulary entry, approves none of the ten G-12 candidates, and repairs none of **C-a…C-d**.
- It does **not** change the approved seven-property **G-13** shape, and adds no eighth or scope property.
- It resolves **none** of G-09, G-10, G-11, D-04.4, D-04.7, C-b, C-c, C-d, §18.7, G-14, G-15.
- It sets **no** sensitivity tier, **no** confidence threshold, and touches **no** production code, schema, migration, dependency, fixture, or `backend/step3.pdf`.
- It does **not** close REQUIREMENTS GAP G-12 or G-13; it prepares a G-12 authoring input and states the residual blocker.

---

## 9. Status of the inventory itself

| # | Condition | Status |
| --- | --- | --- |
| **MF1** | L-STRUCT recorded against `step3.pdf` evidence (§3) | **MET** |
| **MF2** | L-INFO (§4.1) populated from the constructed form or an S-3 teardown | **NOT MET — form not constructed** |
| **MF3** | PD-A address component set derived from MF2 | **NOT MET — depends on MF2** |
| **MF4** | Adopted as the G-13.12 minimality consumer evidence (G-13R.6 approved) | **NOT MET — G-13R.6 is PROPOSED, and MF2 is its content** |

**Until MF2 closes, C-a stays open for the nine mock-form-dependent candidates, and G-12 is partially — not fully — authorable.** MF2 needs no corpus, OCR engine, or study; it needs the team to construct the demonstration form (ASM-002) or run Study S-3.
