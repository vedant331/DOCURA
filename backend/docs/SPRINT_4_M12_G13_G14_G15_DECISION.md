# DOCURA — Sprint 4 M12: G-13-B / G-14 / G-15 Controlled-MVP Decision

| Field | Value |
| --- | --- |
| Type | Governance / evidence / decision milestone (no implementation) |
| Status | **M12-D3 APPROVED by PM (17 Sep 2026) and implemented** — see the UPDATE box below. The analysis in §1–§12 records the state *before* that approval and is retained unchanged. |

> **UPDATE — M12-D3 APPROVED, 17 September 2026.** Product Management approved M12-D3. Implemented: (1) the **G-15 controlled-MVP default = sensitive** policy (un-tiered attribute → consent-gated, applied at the mapping layer, no tier written); (2) **`person.date_of_birth` authored** as vocabulary **`v0.2-draft`** (properties 1–6; new **N-DATE** rule; tier TBD). The extension now fills a **second** field — `date_of_birth`, **consent-gated** — while `full_name` stays auto (M10-D2 exception). Recorded in the register at **D-05.16**. **G-13-B stays NOT MET** and the vocabulary stays **NOT RELEASABLE** (both tiers still TBD); no G-14 tier content was asserted, and A-5 / S-1 / S-4 remain the settlers of the routine/sensitive boundary. See §13 M12-D3 for the implemented specifics.
| Authority | `canonical_attributes.v0.1-draft.toml`, `SPRINT_4_DECISION_REGISTER.md` (D-05.6/.8/.9, D-06.1–.5), `SPRINT_4_G12_FIELD_DEFINITIONS.md`, `SPRINT_4_G13_*`, `step3.pdf` §1.5/§1.15/§12.3, M10/M11 decision docs |
| Rule applied | M12 §15 (no approval without existing authority), §10 (OCR separate), §16 (no impl change if nothing passes) |
| Code changed | **None.** No attribute authored/approved; `v0.1-draft.toml` and the extension are untouched. |

## 1. Executive conclusion

The single attribute `person.full_name` is the only one DOCURA may auto-fill today, and M12 does **not** unblock any additional auto-fill. The blocker is **not** missing analysis — it is two **PM/study decisions** the repository explicitly reserves:

- **G-14 tier *content*** (which attribute is routine/sensitive/consequential) is assigned to **users via assumption A-5**, settled by **studies S-1 and S-4** — untested and load-bearing (§12.3). Its *framework* is already frozen (D-06.5) but carries no per-attribute value.
- **G-15 default tier** for an attribute no rule covers is an unresolved **PM decision** (recommendation on file: default to *sensitive*; not adopted).

Because **G-13-B** ("automatic placement of any value into a form") requires *every attribute to carry an assigned tier*, and no tier content exists, **G-13-B remains NOT MET** for every attribute — including `person.full_name`. M10 fills `full_name` under a documented **controlled-form exception (M10-D2)**: FR-FILL-001's "routine" condition classifies the **detected form field** (FR-FLD-003), which is kept separate from the stored attribute's tier (FR-SENS-001; register D-05.8 line 685). That exception is narrow and already documented; M12 neither widens nor weakens it.

**The most useful expansion available without any study (A-5)** is not more auto-fill — it is routing additional *authored* attributes through the **existing per-disclosure approval path** (treating them as sensitive-by-default per the G-15 recommendation). That needs a PM decision + minimal authoring, not evaluation evidence. See §9 and M12-D3.

## 2. Current approved mapping state

| Attribute | Authored (G-13-A) | Approved | Auto-fill today | Mechanism |
| --- | --- | --- | --- | --- |
| `person.full_name` | Yes (`v0.1-draft`, PD-B) | Yes | **Yes** | Controlled-form field classified routine (M10-D2); attribute tier TBD caveat documented |

Nothing else is authored or approved (register D-05.9: "nine candidates are not authored").

## 3. G-13-B dependency analysis

- **What it gates (D-05.8):** implementation of FR-INF-001…009, production storage of attribute values, and **automatic placement of any value into a form** (FR-INF-007 primary; FR-SENS-002/BR-005 for disclosure).
- **Conditions:** every attribute in the released version carries an **assigned** sensitivity tier (property 7 non-TBD).
- **Depends on:** **G-14** (tier content) and **G-15** (default tier), which depend on **A-5** and **studies S-1, S-4**; plus §12.3's A-5/A-7 gate on any build.
- **Unresolved?** Yes — G-13-B is **NOT MET** and, per D-06.5 §Effect, must not be marked MET; freezing the G-14 framework did not supply a single tier value.
- **Legitimate controlled-MVP exception?** One exists and is already in use: **M10-D2** — classify the **detected form field** routine (a distinct unit from the attribute tier, FR-SENS-001) for the team-constructed controlled form. It is not a general licence; it does not assign an attribute tier; and extending it to a new attribute is itself a PM decision (§15).
- **Verdict:** **BLOCKED — G-13-B.** Unblock path in §11.

## 4. G-14 dependency analysis

- **Framework (D-06.5 §A) — FROZEN / closed:** three tiers (routine, sensitive, consequential); two classified units held separate (**attribute** and **detected form field**); raise-only + consequential-floor invariants (FR-SENS-006, BR-020, AR-AST-007); assignment as a deterministic, reviewable, configuration-held rule list (AR-DET-005); masking-by-default + per-disclosure approval as behaviours of the *sensitive* tier (FR-SENS-002/004, BR-005/007).
- **Content (D-06.5 §D) — BLOCKED:** which attribute/field gets which tier is the routine/sensitive boundary the spec assigns to users — **A-5**, settled by **S-1/S-4**. "No mapping such as Aadhaar=consequential / PAN=sensitive / DOB=sensitive is created — `step3.pdf` supports none."
- **Controlled-MVP consequence:** the framework is enough to (a) classify **form fields** and (b) run the **sensitive-approval path** — both already built (M10). It is **not** enough to declare any attribute *routine*, which is what auto-fill (no approval) needs.

## 5. G-15 dependency analysis

- **What it controls:** the **default tier** for an attribute no G-14 rule covers.
- **Status:** unresolved **PM decision**. On-file **recommendation** (D-06.4): default to **sensitive** (BR-016 fail-toward-inaction, BR-009, AR-AST-007 raise-only) — *a recommendation, not a requirement; not adopted.*
- **Consequence if adopted (register line 685):** a blanket *sensitive* default routes every uncovered attribute's value through per-disclosure approval — so it can be **disclosed with consent**, never silently auto-filled. This is safe and useful, and needs **no study**.
- **Consequence if left unset:** no uncovered attribute may be released at all (property 7 stays TBD) → G-13-B stays blocked for everything but the one exception.

## 6. Candidate attribute matrix (all G-12 candidates actually in the artifacts)

| Candidate | G-12 | G-13 authored | Approved | G-14 tier | G-15 | MVP consumer | Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `person.full_name` | defined | **Yes** | **Yes** (PD-B) | content TBD | — (entry exists) | FR-FILL-001, FR-INF-004 | **Usable** (auto via M10-D2) |
| `person.date_of_birth` | candidate | No | No (proposed) | TBD | TBD | FR-FILL-001 | Blocked: author + **date normalisation rule (N3) TBD** + tier |
| `person.postal_address` | candidate | No (shape PD-A) | shape only | TBD | TBD | FR-FILL-001 | Blocked: **components owed (C-b/L-INFO)** + author + tier |
| `person.aadhaar_number` | candidate | No | No | TBD | TBD | product purpose | Blocked: **C-c** identifier-storage (D-05.3) |
| `person.pan_number` | candidate | No | No | TBD | TBD | product purpose | Blocked: **C-c** |
| `education.awarding_body` | candidate | No | No | TBD | TBD | FR-FILL-001 | Blocked: **C-a** (consumer via owed L-INFO) |
| `education.year_of_passing` | candidate | No | No | TBD | TBD | FR-FILL-001 | Blocked: **C-a** |
| `education.aggregate_result` | candidate | No | No | TBD | TBD | FR-FILL-001 | Blocked: **C-a + C-d** + numeric-precision norm TBD |
| `education.roll_number` | candidate | No | No | TBD | TBD | FR-FILL-001, FR-INF-004 | Blocked: **C-a** |
| `education.qualification_name` | candidate | No | No | TBD | TBD | FR-FILL-001 | Blocked: **C-a** + scope-instance rule (G-13.15) |
| gender / category / nationality / blood group | **REJECTED** | — | — | — | — | none | **Rejected** — no MVP consumer (G-12) |
| email / phone / mobile | **not a candidate** | — | — | — | — | none | **Not present** in any artifact |

## 7. Evidence currently available
- `person.full_name`: full G-13-A authoring, PD-B approval, N-TEXT normalisation, documented consumers — sufficient (already usable).
- The **G-14 framework** (tiers, units, invariants, reviewable-list mechanism) — frozen and reusable.
- The **controlled-form field-classification** mechanism and the **per-disclosure approval** path — built and tested (M10).

## 8. Evidence / decisions missing (per candidate)
- **date_of_birth:** G-13-A authoring; an approved **date normalisation rule** (a G-13.5 conflict-detection decision, evaluation-dependent, D-02 §11.6); a tier (G-14 content or a G-15 default).
- **postal_address:** the **component set** (C-b/L-INFO, owed by team form construction), then authoring per component + tiers.
- **aadhaar/pan:** the **identifier-storage decision C-c** (D-05.3).
- **education.\*:** discharge **C-a** (record the controlled form's L-INFO consumer), plus authoring, numeric/scope-instance rules, and tiers.
- **All attributes, for auto-fill (no approval):** a **routine** tier assignment → **A-5 / S-1 / S-4** (blocked) or a PM controlled-MVP routine exception.

## 9. Minimum recommended controlled-MVP set

**No study-free path expands *auto-fill*.** The minimum, honest, useful expansion is via the **approval path**:

- **Keep** `person.full_name` auto-fill (M10-D2).
- **Enable one additional attribute through the approval path** — recommended **`person.date_of_birth`** (strongest consumer evidence, single-value, a plain `date`) — treated **sensitive-by-default** so it discloses only with per-instance approval.
- This requires the PM to (a) **adopt G-15 default = sensitive for the controlled MVP** (M12-D3), and (b) **author `person.date_of_birth`** including a minimal date normalisation rule. It needs **no OCR and no A-5 study**: the value is supplied as a test record fixture (as `full_name` is), and consent-gated disclosure sidesteps the routine-tier question entirely.

If the PM will not author a normalisation rule or adopt the default, the correct outcome is **no expansion** — `full_name` only.

## 10. Explicitly rejected / still-blocked
- **Rejected (G-12):** gender, category, nationality, blood group — no MVP consumer.
- **Not candidates at all:** email, phone/mobile — absent from every artifact; adding them would be invention (BR-009).
- **Still blocked:** date_of_birth, postal_address, aadhaar/pan, all five education attributes — for the reasons in §6/§8.

## 11. Exact unblock path
1. **PM decision — G-15 default tier** (adopt *sensitive*): unblocks the **approval path** for any authored attribute with no study. *(M12-D3, PM DECISION REQUIRED.)*
2. **Author the target attribute** (G-13-A properties 1–6) incl. its normalisation rule — for `date_of_birth`, a date rule (G-13.5 decision).
3. **For true auto-fill (no consent) of routine info:** resolve **G-14 content** via **A-5 / studies S-1, S-4**, then meet **G-13-B**. This is the only path to "safe info → automatic fill" beyond `full_name`, and it is study-gated.
4. **Per-attribute prerequisites:** C-b (address components), C-c (identifiers), C-a (education consumers) as applicable.

## 12. Impact on M13
- **If PM adopts M12-D3(a) + authors `date_of_birth`:** M13 is small and safe — add a `date_of_birth → person.date_of_birth` entry to `extension/src/mapping.js` with automation **`approval`** (reusing the M10 approval path and DOM-fill), add a test record fixture and a controlled-form field, and tests. No new mechanism, no OCR, no study.
- **If no PM decision:** M13 cannot add autofill fields; it would be documentation only. The safety contract and the single auto-fill (`full_name`) remain exactly as M10/M11 left them.

## 13. Decision records
- **M12-D1 — Auto-fill set unchanged:** `person.full_name` only. No additional attribute is approved for auto-fill; the evidence does not support it (§15).
- **M12-D2 — G-14 framework is frozen and sufficient for classification + the approval path; G-14 tier *content* and G-15 default remain unresolved (A-5 / S-1 / S-4; PM).** G-13-B stays NOT MET. No register status changes.
- **M12-D3 — APPROVED 17 Sep 2026 (register D-05.16).** PM adopted **G-15 default = sensitive for the controlled MVP** and authorised authoring **`person.date_of_birth`**. **Implemented:**
  - Vocabulary **`v0.2-draft`** (`config/vocabulary/canonical_attributes.v0.2-draft.toml`): adds `person.date_of_birth` (data type `date`, rule **N-DATE**, multiplicity person/one, **tier TBD**) alongside `person.full_name`; `v0.1-draft` retained immutable. Runtime loaders (`current_record.py`, `field_extraction.py`) and the vocabulary/record tests repointed to v0.2-draft; guard tests updated (now exactly two entries, two rules, both tiers TBD, still not releasable).
  - **G-15 default policy** encoded at the mapping layer: an un-tiered attribute → `approval` automation (consent-gated), with `full_name` the documented `auto` exception (M10-D2).
  - Extension: `mapping.js` adds `date_of_birth → person.date_of_birth` (automation `approval`); the controlled fixture gains a `date_of_birth` input; tests prove the consent gate (approval_required → exact-scope approval → real date-input fill).
  - **No tier content asserted** (A-5 reserves it); **G-13-B stays NOT MET**; `releasable = false`; `step3.pdf` unamended.
- **M12-D4 — No implementation change and no register/vocabulary change** (§14/§16): nothing is newly approved, so `v0.1-draft.toml`, the register status lines, and the extension are untouched. Historical decisions preserved.

*No line of `step3.pdf` is amended. No commit or push.*
