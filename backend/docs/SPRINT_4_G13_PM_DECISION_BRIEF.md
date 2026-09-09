# DOCURA — Sprint 4 G-13 Gate-A PM Decision Brief

## The four Product Management decisions that finish G-13 gate A

| Field | Value |
| --- | --- |
| Document | Sprint 4 G-13 Gate-A PM Decision Brief |
| Status | Awaiting Product Management decisions (PD-A, PD-C, PD-D, PD-E) |
| Date | 8 September 2026 |
| Authoritative source | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0 |
| Depends on | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md), [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md), [`SPRINT_4_G12_FIELD_DEFINITIONS.md`](SPRINT_4_G12_FIELD_DEFINITIONS.md) |
| Out of scope | Taking any of these decisions. This brief lays them out; approval is Product Management's under G-13.1. No code, schema, migration, dependency, or specification line is changed by this document. |

---

## 0. Why this brief exists, and what it is not

The G-13 canonical attribute vocabulary reached a clean stopping point on 7 September 2026: **PD-B** approved `v0.1-draft` — its one entry `person.full_name`, its one-attribute scope, and the text normalisation rule **N-TEXT**. That approval met exit criteria **X7, X8, X10 and X18** for `v0.1-draft` and **nothing else**.

Gate **G-13-A** (structural completeness) is still **NOT MET**. Per G-13 §20.6, exactly **four Product Management decisions** stand between the vocabulary and gate A, and **none of them needs a corpus, an OCR engine, or a study** — they need a product owner:

| Decision | In one line | Register / G-13 home |
| --- | --- | --- |
| **PD-A** | How is an address represented — one text value, or a structured object (and which components)? | G-12 §18.3 |
| **PD-C** | Is FR-ACC-004's *profile* the same thing as FR-INF-001's *structured record*? (gap **G-19**) | Register D-08.2 |
| **PD-D** | The scope-instance resolution rule (gap **G-13.15** / T12) — pick a derivation, or narrow X17 per-subject | G-13 §20.6, §15.3 T12 |
| **PD-E** | Where does an extracted value that maps to **no** canonical attribute go? (gap **G-29**) | G-13 §12.4, register §4 |

**Label taxonomy** (as in the register): **REQUIREMENT** = stated in `step3.pdf`; **RECOMMENDATION** = this brief's engineering advice, with no requirement status until you approve it; **PRODUCT DECISION** = yours to take.

Each section below states the question, quotes the requirements that bound it, lays out the live options with their costs, gives a **RECOMMENDATION**, and records exactly what taking the decision unblocks and what it does not.

---

# PD-A — The representation of an address

## The question
`person.postal_address`'s existence is **entailed** by the requirements — §7.1 groups a supported document type under *"Identity and **address** — Aadhaar, PAN, address proof"*, and **FR-OCR-004** (MUST) requires a defined field set to be extracted for every supported type, which would be vacuous if the record held no address concept (G-13 §20.2). What is **undecided** is its shape: **one text string, or a structured object — and if structured, which components.**

## What the specification says
- **FR-OCR-004** (MVP MUST): a defined field set is extracted per supported type. *Requires* an address concept; *names* no fields for it.
- **FR-FILL-001 / FR-FILL-002**: forms are filled by matching stored information to form fields. Real forms request address **in parts** (line, city, state, PIN/postal code) — the specification does not enumerate them.
- **FR-INF-008 / FR-INF-004**: normalisation and conflict detection operate on the stored value. A whole-string address makes both coarse.
- **C-b** (G-13 §15.4): the address candidate has **no data type and no normalisation rule**. Authoring it silently as `text` would "repair C-b silently, which §15.4 and X18 forbid" — hence this must be an explicit PM decision, not an engineering default.

## Options

| # | Option | What it buys | What it costs |
| --- | --- | --- | --- |
| **A1** | **Single `text` value** — the address as one printed string | Simplest. **N-TEXT** applies directly, so it is authorable the moment you choose it. One attribute, one tier. | Cannot be decomposed to fill part-wise form fields (FR-FILL-002). FR-INF-004 would raise **false conflicts** on trivial order/formatting differences N-TEXT cannot fold ("12 MG Rd" vs "12, M.G. Road"). One coarse sensitivity tier for the whole thing. |
| **A2** | **Structured object** — named components (e.g. line(s), locality, city, district, state, PIN/postal code, country) | Matches how forms ask (FR-FILL-002). Per-component normalisation, conflict detection, multiplicity, and sensitivity tier. A PIN can be tiered differently from a street line. | The component set is **not in `step3.pdf`**; choosing it in the abstract is domain knowledge, which **BR-009** cautions against. Each component is its own canonical attribute → multiplies authoring and later G-14/G-15 tiering work. |
| **A3** | **Hybrid** — retain the raw as-printed address (G-13.6 already requires the raw value) **and** a structured decomposition for filling and comparison | Most capable: raw for display/provenance, structure for filling and per-component conflicts. | Highest authoring cost, and still needs the A2 component set decided. Two representations to keep consistent. |

## RECOMMENDATION
The correct **shape** is a structured object (A2/A3), because FR-FILL-002 asks for address in parts and a single string defeats both filling and clean conflict detection. But the **component set must not be invented here** — it should be drawn from the one artefact the requirements already promise and that needs no corpus, engine, or study: the **§10 / ASM-002 controlled mock form's field inventory** (the same artefact C-a identifies as the real unblocker for the education attributes). 

Concretely: **decide A2 (structured), and populate its components from the mock-form field inventory.** If a provisional value is needed before that inventory exists, **A1 + retained raw** is the only choice that foreclosures nothing — it can be promoted to A2 later without data loss because the raw address is retained — but it cannot satisfy part-wise filling in the interim, and that limitation should be stated rather than discovered.

## What deciding PD-A unblocks
- Discharges **C-b** (and *only* this decision does).
- Makes `person.postal_address` authorable as a vocabulary entry (its existence is already entailed; only its representation blocks it).

## What PD-A does not do
- It does not author the entry, assign it a sensitivity tier (that is property 7 / G-14–G-15, gate G-13-B), or approve any other candidate.
- Choosing A1 does not bar a later move to A2; choosing A2 does not oblige immediate authoring.

---

# PD-C — Is the profile the same as the structured record? (G-19)

## The question
Two MVP requirements describe what looks like one thing, in two modules, without stating their relationship:

> **FR-ACC-004** (MUST, trace N-01): "maintain a **user profile of canonical personal attributes** derived from documents and editable by the user."

> **FR-INF-001** (MUST, trace N-01): "maintain a **structured record** of the user's personal information, assembled from all processed documents."

Both trace to N-01, both are document-derived, both are user-editable. **Nothing in `step3.pdf` distinguishes them** — so either they are one concept named twice (a duplication §15's "Non-duplicated" criterion denies), or two concepts whose difference is undefined. This is **REQUIREMENTS GAP G-19**.

## Why it is on the gate-A critical path
Per G-13 §20.6, PD-C unblocks **X2**, then **X4** — and **the property list / shape freezes once, at X4, after G-19**. Nothing attribute-shaped should be frozen until this is answered, because **T5** notes G-19 may add a property to the G-13.2 seven-property shape. PD-C is therefore the decision most likely to change the shape itself.

## Options

| # | Option | Consequence |
| --- | --- | --- |
| **C1** | **One store, two views** — a single set of canonical attributes (the FR-ACC-004 profile) whose values are supported by per-document observations (the FR-INF-001 record). The profile is the *resolved view* over the observations, not a second copy. | Gives FR-INF-003 (user correction becomes authoritative), FR-INF-006 (authoritative value + retained alternatives), and AC-US-005-1 (no authoritative value during a conflict) a single coherent home. No duplication. |
| **C2** | **Two independent concepts** — the profile is a user-owned record that extraction only *proposes* into; the structured record is the raw per-document assembly, kept separate. | A materially different, larger model. Only correct if you intend the profile to be independently user-owned rather than a resolved view. Must be stated **before** either is built. |

## RECOMMENDATION
**C1 — one store, two views.** It is the reading that makes the downstream requirements (FR-INF-003/006, AC-US-005-1) coherent without inventing a second copy, and it matches the register's D-08.2 recommendation. **But this is genuinely yours to confirm:** if you intend an independent, user-owned profile that extraction merely proposes into (C2), that is a different data model and must be said now, because X4 freezes the shape once.

## What deciding PD-C unblocks
- **X2**, then **X4** (the shape freeze), then **X6** becomes reachable (X6 is gated on X4 and X17).

## What PD-C does not do
- It does not by itself close G-19 in `step3.pdf` (that needs the §11 Containment-Rule amendment, X16); it is a product decision standing beside the spec.
- It does not author any attribute or resolve the scope-instance question (PD-D).

---

# PD-D — The scope-instance resolution rule (G-13.15 / T12)

## The question
The revised property 6 is a **scope-keyed cardinality**: *how many values an attribute holds, and per what subject*. This lets FR-INF-004 separate "two documents disagree about one person's name" (a conflict) from "two values describing two different subjects" (not a conflict). For that separation to be **deterministic** (AR-DET-008), the system must resolve, at comparison time, *which scope instance* a value belongs to. **G-13.15 fixed the constraint** — the rule is PM's, deterministic, and never derived from an extracted content value — but **left the rule itself unresolved** (T12, exit criterion **X17**).

You have two ways to satisfy X17, and either finishes this decision.

## Option set 1 — pick a derivation now
Five candidate derivations were recorded; **two are already excluded** on requirement grounds:

| Candidate | Deterministic? | Status |
| --- | --- | --- |
| Derived from the document's **classified type** (FR-OCR-002/003) | Yes | **Live.** But two qualifications sharing one type collapse together; couples scope to §7.1's provisional type set (ASM-001), and G-10 merging types reintroduces the collapse. |
| **Declared per type in the G-12 mapping** | Yes | **Live.** Keeps the type coupling inside G-12, where §7.1's provisionality already lives. |
| A **user-designated** grouping | Yes, once designated | **Live**, but beyond anything `step3.pdf` requires — new scope. |
| Derived from an **extracted content value** naming the subject | **No** | **Excluded** by G-13.3 (no identity by value similarity) and AR-AST-007 (no self-escalation). |
| Derived from the **source document's identity** | Yes | **Excluded**: two documents would never share a scope instance, so FR-INF-004 would detect nothing, ever — determinism achieved by making the requirement vacuous. |

## Option set 2 — narrow X17 per-subject (the lighter path)
X17 can be read **per-subject rather than per-version**: *the scope-instance rule is required before the first attribute of that subject enters a version.* `v0.1-draft` holds one `person`-scoped attribute, and **FR-ACC-003** makes the record single-person — so on this reading `v0.1-draft` needs no scope-instance rule at all, and X17 binds later, at the first `qualification`-scoped entry. This narrowing is itself a change to an approved exit criterion, hence it is **PD-D's to approve**.

## RECOMMENDATION
**Approve the per-subject narrowing of X17 (Option set 2).** It unblocks gate A for `v0.1-draft` immediately, and it does so **without inventing a scope-instance model for values that do not yet exist** — which is precisely the invention G-13.15 was created to prevent. The substantive derivation choice then binds when there is finally something scoped that way (the first `qualification` attribute), and at that point the natural home is **"declared per type in the G-12 mapping"** (Option set 1, row 2), because it keeps the provisional type-coupling contained where §7.1's provisionality already lives. So: **take Option set 2 now; signal a lean toward "declared per type in the G-12 mapping" for when a qualification-scoped attribute is authored.**

## What deciding PD-D unblocks
- **X17**, then **X15** (subject to X15's separate dependency below).
- With PD-C's **X4**, it clears the two gates that hold **X6** for `v0.1-draft`.

## What PD-D does not do
- The per-subject narrowing does **not** choose a derivation; it defers that to the first non-`person` subject.
- **X15** additionally requires the "fourth false-conflict attribution category" from D-02 §11.4.1, which is **owed by the D-02 document's owner** — not one of these four PM decisions. Flag it so the critical path is honest.

---

# PD-E — Where does an unmapped extracted value go? (G-29)

## The question
`step3.pdf` defines an explicit "I do not know" outcome at **two** levels — document type ("unrecognised": FR-OCR-002, AR-AST-002) and form field ("unknown": FR-FLD-006, AR-AST-003). It defines **no third path** for a value that is **read cleanly from a document but corresponds to no canonical attribute**. That is **REQUIREMENTS GAP G-29**. **G-13.7 (approved) already excluded one answer** — such a value is **never coerced** into the nearest-looking attribute (barred by BR-009, BR-016, EC-003, AR-AST-007). What remains is its destination: **discard, retain outside the record, or surface to the user.**

## Why it matters now
With one attribute in the vocabulary, **almost every readable value is unmapped**, so this is not an edge case at MVP — it is the common case. And it carries a privacy consequence: **FR-INF-007** requires every attribute to carry a sensitivity tier, so a value that never becomes an attribute is **unclassified personal data with no tier**. **BR-017 / NFR-PRIV-001** put the burden of proof on *inclusion* (minimality). **D-02 §11.7** already warns "the evaluation must not assume that every readable value is a value to be extracted."

## Options

| # | Option | What it buys | What it costs |
| --- | --- | --- | --- |
| **E1** | **Discard** — the unmapped value is not retained at all | Strongest privacy/minimality (NFR-PRIV-001, BR-017); nothing unclassified accumulates; aligns with "fail towards inaction" (BR-016). **No information is permanently lost** — Sprint 3 retains the original file, so a later vocabulary can recover the value by reprocessing (FR-OCR-010). | The record stays sparse until the vocabulary grows; a value the user might have wanted is not surfaced until then. |
| **E2** | **Retain outside the structured record** — held against the extraction run/observations, not in the profile | Could be mapped later without re-OCR when the vocabulary grows. | This **is** the §12.3 hazard: unclassified personal data sitting in the system. Needs a default tier + retention policy first, which pulls in **G-14/G-15** and D-02 retention — so it cannot be clean until those are decided. |
| **E3** | **Surface to the user** — present the unmapped value; let the user map, keep, or discard it | Most aligned with the product principle "ask about ambiguity"; keeps the human in control (consent). | **No MVP requirement defines this UI path**, and its destination depends on **G-27** (the manual-entry destination, itself an open gap). Adds product surface not yet specified. |

## RECOMMENDATION
For MVP, **E1 — discard.** The original document is always retained, so discard loses nothing permanently: when the vocabulary later gains the relevant attribute, reprocessing re-reads the value. E1 is the only option that avoids accumulating untiered personal data (the §12.3 / FR-INF-007 hazard) while honouring NFR-PRIV-001 minimality and BR-016/BR-017 — and it needs no dependent decision to be safe. **E2** only becomes clean once a default tier and retention are set (G-14/G-15); **E3** is the best long-term fit for DOCURA's "ask about ambiguity" principle but has no MVP requirement and waits on G-27. Recommend **E1 now, with E3 as the post-MVP direction** once the tier and manual-entry paths exist.

## What deciding PD-E unblocks
- **X11** (the unmapped-value destination criterion).

## What PD-E does not do
- It does not close G-29 in `step3.pdf` (needs the §11 amendment), and it does not decide the manual-entry destination (G-27) or any sensitivity tier.

---

# How the four fit together — decision order and the path to gate A

**PD-B (done, 7 Sep) + these four are the whole of gate A's PM dependency.** Their unblocks:

| Decision | Directly unblocks | On the critical path to G-13-A? |
| --- | --- | --- |
| **PD-C** (G-19) | X2 → **X4** (shape freeze) → enables X6 | **Yes — decide first.** X4 freezes the shape once; T5 says G-19 may add a property, so nothing should freeze before it. |
| **PD-D** (X17) | **X17** → X15; with X4, clears X6's two gates for `v0.1-draft` | **Yes.** Recommended path (per-subject narrowing) needs no scope model invented. |
| **PD-A** (address) | discharges **C-b**; makes `person.postal_address` authorable | Not strictly required for `v0.1-draft`'s single entry, but required before a second attribute is authored. |
| **PD-E** (G-29) | **X11** | Required for gate A; independent of the others. |

**Still outside these four (so gate A does not rest on you alone):**
- **X13 / X14 / X12** — engineering acts: hold the vocabulary as versioned configuration. Ready to build once the shape is frozen (post-PD-C).
- **X15** — additionally needs D-02 §11.4.1's fourth false-conflict category, **owed by the D-02 owner**.
- **X16** — the `step3.pdf` §11 Containment-Rule amendment that closes the gap itself; this is gap closure, distinct from gate A.

**One thing not to do** (carried from the register): do **not** set a provisional confidence threshold to "unblock" anything. AR-AST-008 forbids it — "before any threshold is set" — and none of these four decisions touches a threshold.

---

# How to record your decision

Reply with your choice per decision — e.g. *"PD-A: A2 with components from the mock form; PD-C: C1; PD-D: narrow X17 per-subject; PD-E: E1."* On your approval I will:
1. Add a **PD-C … PD-E approval section** to [`SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md`](SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md) (mirroring §21's PD-B format), and re-classify the affected gate-A criteria (X2, X4, X6, X11, X15, X17).
2. Record them in [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) as **D-05.12** and update the D-05 readiness lines and the §4 gap rows (G-19, G-29, G-13.15).
3. State honestly which gate-A criteria remain (X13/X14 engineering, X15's D-02 dependency, X16 amendment) so the "G-13-A MET / NOT MET" line stays accurate.

*Nothing in this brief amends `backend/step3.pdf`, approves any attribute, assigns any sensitivity tier, or changes any code, schema, migration, or dependency. It lays out four decisions; taking them is Product Management's under G-13.1.*
