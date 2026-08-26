# Questions & Conflicts to Resolve

**Step 4 · Document 19 of 20** — What Steps 1–3 do not settle, what it costs to leave it unsettled, and what Step 4
did in the meantime.

**Nothing here was resolved silently.** Where Step 4 had to proceed, it did so using a tie-break rule that Steps 1–3
supply — Step 3 §5: *"Where a requirement and a rule appear to conflict, the rule governs."* Every such case is
marked **Proceeded under** below, with the authority cited.

`Q4-nn` identifiers are introduced by this step.

---

## Q4-01 — FR-INT-003 is marked SHOULD but is required by MUST-level work

| | |
|---|---|
| **Type** | Conflict inside Step 3 |
| **Severity** | Medium — affects whether UC-015 can be dropped under schedule pressure |

**Issue.** The readiness summary (FR-INT-003) is marked **MVP / SHOULD** in Step 3 §1.7, and §12.2 reinforces this:
"the core loop is demonstrable without it. It is the first SHOULD to promote if capacity allows." But four
MUST-level artefacts depend on it existing:

- **US-007** (MVP MUST) — "I want DOCURA to tell me up front what the form needs and whether I have it"
- **AC-US-007-2** — "a readiness summary lists what the form requires, what is available in the record, and what is missing"
- **AC-US-007-3** — a missing document "is listed as missing before any filling begins"
- **D4** in the §10.1 demonstration journey — "readiness summary shown" is a required observable
- **EC-005** — a missing document must be reported "at the readiness summary, before filling begins"

**Source.** Step 3 §1.7 (FR-INT-003), §3 Table 3.1 (US-007), §4 (AC-US-007-2/3), §10.1 (D4), §12.2, §14 (EC-005).

**Why it matters.** If FR-INT-003 is deferred under schedule pressure, US-007 cannot pass its own acceptance
criteria, D4 cannot be demonstrated, and EC-005's required behaviour has nowhere to happen. A SHOULD that three
MUSTs depend on is effectively a MUST that is labelled as optional — which is how features get dropped by accident.

**Suggested decision.** Promote FR-INT-003 to **MVP / MUST**. The alternative — relaxing AC-US-007-2/3 and D4 —
would remove the product's answer to need N-04 and journey stage S2, which Step 2 rates as a *high* opportunity.

**Impact if unresolved.** UC-015 remains ambiguous in status. A team under pressure may drop it, discover at
demonstration time that D4 fails, and rebuild it late.

**Proceeded under.** Step 4 specifies UC-015 in full and marks it `SHOULD †` with this conflict flagged inline.

---

## Q4-02 — Does session history retain sensitive values in full?

| | |
|---|---|
| **Type** | Gap — requirements pull in opposite directions |
| **Severity** | **High** — a privacy and security question |

**Issue.** FR-AUD-001 requires the system to record "every value DOCURA placed". For a field classified sensitive,
that means a sensitive value — a government identifier, bank detail, or signature — is written into history. But:

- **BR-017** requires DOCURA to store "what it needs to serve a function the user asked for, and no more"
- **NFR-PRIV-001** limits collection to what a requested function requires
- **FR-SENS-004** requires sensitive values to be masked in DOCURA's own interface by default
- **FR-AUD-006** says history records DOCURA's actions and the fields they affected, and "shall not store the full contents of the third-party form"

**Source.** Step 3 FR-AUD-001, FR-AUD-006, FR-SENS-004, BR-017, NFR-PRIV-001.

**Why it matters.** Three readings are possible and they have materially different security postures: history stores
the **literal value**; history stores a **masked** form; or history stores a **reference** to the attribute and its
source, with the value resolved on demand under the same masking rules. The third preserves traceability (BR-010)
at the lowest retention cost, but Steps 1–3 do not say so.

**Suggested decision.** Record the **attribute reference, its source document, and the receiving field** — not the
literal value. This satisfies FR-AUD-001's purpose (accounting for what DOCURA did), BR-010 (traceability), BR-017,
and FR-SENS-004 simultaneously. Confirm before any real identity document is stored.

**Impact if unresolved.** A design decision with privacy consequences gets made implicitly by whoever implements
FR-AUD-001 first.

**Proceeded under.** UC-027 specifies history without asserting a storage form, and carries this note inline.

---

## Q4-02b — EC-019 and BR-007 collide on a sensitive attribute requested twice

| | |
|---|---|
| **Type** | Conflict inside Step 3 |
| **Severity** | Medium |

**Issue.** EC-019 requires that where the same attribute is requested twice in one form, DOCURA "fill both
consistently from the same authoritative value." BR-007 requires that an approval apply to "exactly one disclosure,
in one field, in one form, in one session", and FR-SENS-005 that approval "granted for one field in one form shall
not carry to any other field." For a **sensitive** attribute the two cannot both be satisfied by one approval.

**Source.** Step 3 §14 EC-019; §5 BR-007; §1.15 FR-SENS-005.

**Why it matters.** It determines how many times a user is interrupted for the same identifier on one form — which
feeds directly into risk R-3 (interruption fatigue) and NFR-USE-002's interruption budget.

**Suggested decision.** Two approvals. Confirm that "consistently" in EC-019 means *the same value is used*, not
*one approval covers both*.

**Impact if unresolved.** Either a rule violation (one approval used twice) or an unexpected double interruption.

**Proceeded under.** Step 3 §5 — *the rule governs*. BR-007 wins; UC-021 and
[`sensitive-information-flow.md`](sensitive-information-flow.md) §5 specify two approvals.

---

## Q4-03 — FR-DRP-007 is silent on sensitive checkboxes

| | |
|---|---|
| **Type** | Gap |
| **Severity** | Low — derivable, but not stated |

**Issue.** FR-DRP-007 reads: "A checkbox shall be set automatically only where it is classified routine. Checkboxes
classified consequential shall never be set by DOCURA." The **sensitive** tier is not mentioned.

**Source.** Step 3 §1.12 FR-DRP-007; §1.15 FR-SENS-002; §5 BR-005.

**Why it matters.** A checkbox can carry sensitive meaning — for example one that declares a category or income
status. Read literally, FR-DRP-007's "only where routine" would forbid setting it at all; read against FR-SENS-002,
it may be set after per-instance approval.

**Suggested decision.** Amend FR-DRP-007 to name all three tiers explicitly: routine → set; sensitive → set only
after per-instance approval; consequential → never.

**Impact if unresolved.** Low. Either reading is safe — the conservative one refuses, the derived one asks. Neither
guesses.

**Proceeded under.** FR-SENS-002 and BR-005 — sensitive checkboxes require approval. Marked as a derivation in
[`dropdown-flow.md`](dropdown-flow.md) §5.

---

## Q4-04 — Three MVP requirements have no user story

| | |
|---|---|
| **Type** | Traceability gap |
| **Severity** | Low to Medium |

**Issue.** FR-EXT-001 and FR-EXT-002 (install and account binding, both MUST) and FR-ACC-008 (view and revoke
sessions, SHOULD) appear in no user story in Step 3 Table 3.1, and have no acceptance criteria.

**Source.** Step 3 §1.8 FR-EXT-001/002, §1.1 FR-ACC-008, §3 Table 3.1.

**Why it matters.** FR-EXT-001/002 are prerequisites for every extension story — nothing in US-007…US-016 can
happen without them. FR-ACC-008 is a user-facing security capability with no test.

**Suggested decision.** Accept as intentional for FR-EXT-001/002 (Step 3 §3 says stories exist only where they
capture "a distinct user outcome"), but add acceptance criteria so they are testable. Add a story for FR-ACC-008.

**Impact if unresolved.** MUST requirements with no test. Low product risk, real verification risk.

**Proceeded under.** UC-002 and UC-003 specify them, marked ⚠ in the traceability matrix.

---

## Q4-05 — FR-SENS-006 has no story and no acceptance criterion

| | |
|---|---|
| **Type** | Traceability gap |
| **Severity** | Low |

**Issue.** "The user shall be able to raise the sensitivity of an attribute. Lowering the consequential tier shall
not be possible for any user" (MVP / SHOULD) appears in no story and has no criteria. It is also the only
user-facing control over the sensitivity boundary — the very boundary Step 2 says "must be set by users, not by us".

**Source.** Step 3 §1.15 FR-SENS-006; Step 2 §13.2, assumption A-5.

**Why it matters.** If A-5 reports that users disagree with DOCURA's routine/sensitive boundary, this control is the
only MVP mechanism through which they can act on that disagreement. Its priority may be understated.

**Suggested decision.** Add acceptance criteria. Reconsider the priority once S-4 (card sort of field sensitivity)
reports.

**Impact if unresolved.** A control users may need in order to trust the product ships untested.

**Proceeded under.** UC-028 specifies it, marked SHOULD as Step 3 has it.

---

## Q4-06 — Four MVP user stories have no acceptance criteria

| | |
|---|---|
| **Type** | Gap in Step 3 |
| **Severity** | Medium |

**Issue.** Step 3 §4 defines criteria for fifteen of the twenty MVP stories. **US-001** (create an account and sign
in securely — MUST), **US-006** (find a document or a fact quickly — MUST), **US-017** (see what DOCURA did —
SHOULD) and **US-020** (export everything — SHOULD) have none.

**Source.** Step 3 §3 Table 3.1 vs §4.

**Why it matters.** Step 3 §15 assesses "Testable" as *partially met* and attributes the shortfall to TBD
thresholds, not to missing criteria. Two MUST stories with no criteria is a different and unrecorded gap.

**Suggested decision.** Write criteria for all four before build. They are straightforward — none depends on a TBD
threshold.

**Impact if unresolved.** Two MUST stories cannot be verified as done.

**Proceeded under.** UC-001, UC-004, UC-012 and UC-027 record `AC: none defined` rather than inventing criteria.

---

## Q4-07 — AC-US-003-3 asserts a prompt that no requirement specifies

| | |
|---|---|
| **Type** | Requirement / criterion mismatch |
| **Severity** | Low |

**Issue.** AC-US-003-3 states that for a document whose type cannot be determined confidently, "it is stored as
unclassified, **the user is asked to identify it**, and no type is assumed." No functional requirement obliges
DOCURA to *ask*. FR-OCR-002 requires classification or "unrecognised"; FR-DOC-002 says the type is "correctable by
the user" — which is a passive capability, not a prompt.

**Source.** Step 3 §4 AC-US-003-3; §1.4 FR-OCR-002; §1.2 FR-DOC-002.

**Why it matters.** "Correctable" and "the user is asked" are different behaviours with different interruption
costs. A vault of fifty documents that prompts for each unclassified one behaves very differently from one that
flags them for later.

**Suggested decision.** Add a requirement stating whether unclassified documents generate an active prompt or a
passive *needs review* flag. Given NFR-USE-002's interruption budget, the passive flag is the likelier intent.

**Impact if unresolved.** An acceptance criterion that cannot be traced to a requirement — and a possible source of
interruption fatigue.

**Proceeded under.** UC-007 alternative flow A1 follows AC-US-003-3 and notes the mismatch inline.

---

## Q4-08 — "Information absent" is classed as ambiguity but cannot be prompted as one

| | |
|---|---|
| **Type** | Internal tension in Step 3 |
| **Severity** | Medium — affects the ambiguity flow's shape |

**Issue.** FR-AMB-001 lists four ambiguity conditions, the fourth being "the required information is absent". But
FR-AMB-002 requires an ambiguity prompt to "state the field, **the candidates**, the source of each candidate, and
why DOCURA could not decide" — and absence produces no candidates. Meanwhile BR-009 and EC-005 require missing
information to be **reported**, not asked about.

**Source.** Step 3 §1.13 FR-AMB-001/002; §5 BR-009; §14 EC-005.

**Why it matters.** It determines whether a missing attribute produces an in-form prompt (an interruption) or a
review-summary entry (a report). At scale on a sparsely populated record, that is the difference between a usable
product and a nagging one — risk R-3.

**Suggested decision.** Split FR-AMB-001's fourth condition out: absence is an **outstanding item**, not an
ambiguity. Keep it in the review summary and the readiness summary, not in the ambiguity prompt queue.

**Impact if unresolved.** Either a prompt with an empty candidate list, or a silent divergence between the four
stated conditions and three implemented ones.

**Proceeded under.** Step 3 §5 — *the rule governs*. BR-009 and EC-005 win; absence is reported, not prompted.
Specified in UC-019 exception E1 and [`ambiguity-flow.md`](ambiguity-flow.md) §3.

---

## Q4-09 — Two MUST behaviours have no demonstration step

| | |
|---|---|
| **Type** | Gap between §10.1 and §1 |
| **Severity** | Medium |

**Issue.** The fourteen-step demonstration journey D1–D14 does not stage **conflict resolution** (UC-009,
FR-INF-004/005/006, MUST) or **stopping DOCURA** (UC-024, FR-EXT-006, MUST) — nor UC-001…UC-005, UC-010, UC-011,
UC-012, UC-023, UC-027, UC-028.

**Source.** Step 3 §10.1 Table 10.1 vs §1.5, §1.8.

**Why it matters.** Conflict handling is one of the four mandatory human-decision points (Table 6.2) and Step 3
§12.2 calls conflict detection cheap to build and damaging to omit: "Name mismatches (P-06) are a silent
disqualifier." Stopping is the user's primary control. A demonstration that omits both shows the product's
automation but not two of its guarantees.

**Suggested decision.** Add a D-step for conflict resolution and one for stopping mid-session. Both are cheap to
stage on a controlled mock form.

**Impact if unresolved.** The MVP demonstration under-represents exactly the behaviours that differentiate DOCURA.

**Proceeded under.** UC-009 and UC-024 are specified in full; the gap is recorded in
[`use-case-catalogue.md`](use-case-catalogue.md) §5.

---

## Q4-10 — Is a hand-back recorded when the user submits mid-action?

| | |
|---|---|
| **Type** | Gap |
| **Severity** | Low |

**Issue.** FR-SUB-004 requires DOCURA to "record that the session reached the hand-back point". EC-018 describes the
user submitting while DOCURA is mid-action, in which case **the session ends without ever reaching hand-back**.
What history records in that case is unspecified.

**Source.** Step 3 §1.18 FR-SUB-004; §14 EC-018.

**Why it matters.** Minor, but it is a claim about a user action that DOCURA did not observe — the exact thing
FR-SUB-004's second clause forbids.

**Suggested decision.** Record *session ended before hand-back*, and make no claim about submission — consistent
with FR-SUB-004's existing prohibition.

**Impact if unresolved.** An ambiguous history entry in a rare case.

**Proceeded under.** UC-026 alternative flow A2 records the gap inline.

---

## Q4-11 — Every confidence-dependent flow rests on six TBD parameters

| | |
|---|---|
| **Type** | Open parameter, not a conflict |
| **Severity** | Medium — bounded and already tracked by Step 3 |

**Issue.** Six numbers that shape the flows in this step are *TBD — to be validated*:

| Parameter | Requirement | Set by |
|---|---|---|
| Automatic-action threshold | BR-001 | Study S-6 |
| Review threshold | BR-002 | Study S-6 |
| Quality floor | FR-MATCH-010 | To be validated |
| Deletion grace period | FR-DOC-008 | To be validated |
| Session-expiry period | NFR-SEC-005 | Study S-2 |
| Interruption budget | NFR-USE-002 | Study S-4 |

**Why it matters.** These determine how often DOCURA acts versus asks — the balance the entire product rests on. Set
too low and R-4 (silent comprehension errors) bites; too high and R-3 (interruption fatigue) does.

**Suggested decision.** None needed from Step 4. Confirm they remain externally configurable without a code release
(NFR-MNT-002), so they can be tuned after S-4 and S-6 rather than re-engineered.

**Impact if unresolved.** None for this step's correctness. Every flow tests **behaviour at the threshold**, never a
value — exactly as Step 3 §4 does.

---

## Q4-12 — A Vision-level capability is deferred to FUTURE

| | |
|---|---|
| **Type** | Step 1 vs Step 3 scope tension |
| **Severity** | Low — informational |

**Issue.** Step 1 §03 describes the second of DOCURA's three parts as "**Search over one's own life** — the user can
ask their own record questions **in plain language**." Step 3 makes natural-language query (FR-SRCH-006) **FUTURE /
WON'T**, delivering type, label, text and attribute search instead.

**Source.** Step 1 §03; Step 3 §1.6 FR-SRCH-006, §11 horizon H4.

**Why it matters.** Not a contradiction — a vision describes a destination and an MVP a first step — but it is the
one place where a capability stated as a *core part* of the product in Step 1 is absent from the MVP. Worth being
deliberate about when describing the MVP to anyone who has read the vision.

**Suggested decision.** No change. Note it in MVP communications so the gap between the vision's language and the
MVP's capability is not discovered by a stakeholder mid-demonstration.

**Impact if unresolved.** Expectation mismatch only.

**Proceeded under.** UC-012 specifies MVP search; UC-034 records the natural-language version as FUTURE.

---

## Summary

| ID | Issue | Type | Severity | Blocks Step 4? |
|---|---|---|---|---|
| Q4-01 | FR-INT-003 SHOULD vs MUST dependents | Conflict | Medium | No |
| Q4-02 | Sensitive values in history | Gap | **High** | No |
| Q4-02b | EC-019 vs BR-007 | Conflict | Medium | No |
| Q4-03 | Sensitive checkboxes unaddressed | Gap | Low | No |
| Q4-04 | FR-EXT-001/002, FR-ACC-008 have no story | Traceability | Low–Medium | No |
| Q4-05 | FR-SENS-006 has no story or criteria | Traceability | Low | No |
| Q4-06 | Four MVP stories have no criteria | Gap | Medium | No |
| Q4-07 | AC-US-003-3 asserts an unspecified prompt | Mismatch | Low | No |
| Q4-08 | Absence classed as ambiguity | Tension | Medium | No |
| Q4-09 | Two MUST behaviours undemonstrated | Gap | Medium | No |
| Q4-10 | Hand-back record under EC-018 | Gap | Low | No |
| Q4-11 | Six TBD parameters | Open parameter | Medium | No |
| Q4-12 | NL search in Vision, FUTURE in Step 3 | Scope tension | Low | No |

**None of these blocked Step 4.** Each was either resolvable by a tie-break rule that Steps 1–3 supply, or narrow
enough to specify around and flag. The two most worth a decision before build are **Q4-02** (sensitive values in
history — a privacy posture) and **Q4-01** (the readiness summary's priority — a scope risk).
