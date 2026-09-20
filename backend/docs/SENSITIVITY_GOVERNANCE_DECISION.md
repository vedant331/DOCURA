# Sensitivity Governance — A-5 (D-A5 RESOLVED)

**Status: RESOLVED and applied.** The owner approved the tier assignment below; it is applied
through the existing config + extension seam (`canonical_attributes.demo.toml` `sensitivity` ↔
`extension/src/demo.js` `DEMO_TIERS`), driving the existing review/approval/masking machinery. This
document records the requirement, the implementation, the approved decision, and its consequences.
It still does not infer tiers from general privacy knowledge — the assignment is the owner's.

Authoritative sources: `step3.pdf` (FR-INF-007, FR-FLD-003/004, FR-SENS-001…006, FR-APR-005,
BR-005/006/007/020, AR-AST-007, assumption A-5) and `docs/SPRINT_4_DECISION_REGISTER.md` (D-06,
G-14/G-15).

## A. Explicit requirements from step3.pdf
- **FR-INF-007** (MVP MUST): *every attribute* carries a sensitivity classification of **routine /
  sensitive / consequential**. (Traces to document-02 "Table 13.1" *by id* — see §C.)
- **FR-SENS-001** (MVP MUST): maintain the three-tier classification for **both** stored attributes
  and detected form fields.
- **FR-FLD-003** (MVP MUST): each field is classified before any value is placed in it.
- **FR-FLD-004 / BR-006** (MVP MUST): legal declarations, agreements, and consent controls **are**
  marked **consequential** — this is the one tier assignment step3.pdf fixes, and it is about
  *field controls*, not the person/identity attributes.
- **FR-SENS-002 / BR-005**: sensitive information is never placed into a form without explicit,
  per-disclosure approval.
- **FR-SENS-004**: sensitive values are masked in DOCURA's own interface by default, revealed only
  on user action.
- **FR-SENS-005 / BR-007**: an approval is scoped to one field, one form, one session; never
  inherited or generalised.
- **FR-SENS-006 / BR-020 / AR-AST-007**: the user may **raise** an attribute's sensitivity; the
  **consequential floor** can never be lowered by any actor; assisted components may add a
  classification, never remove one.
- **FR-APR-005**: no control approves consequential items in bulk or in advance.
- **NFR-MNT-004**: sensitivity rules are maintainable as a reviewable list, not scattered in code.

## B. Current implemented backend behavior
- The three-tier framework exists; production **classifies nothing**: the injected seams
  (`noApprovedSensitivityTier`, `noApprovedDeclarationClassification`) return **`unknown`**.
- `unknown` is treated as the **conservative floor**: DOCURA refuses to disclose a value it cannot
  classify — it does **not** silently treat unknown as routine, nor invent "sensitive".
- Approval is **per-instance, exact-scope, one-time**; unapproved sensitive values are masked out of
  review surfaces (matching FR-SENS-002/004/005).
- Raise-only / consequential-floor invariants are structural.
- The chatbot never receives raw attribute values (its context is value-free), so no tier decision
  is required for it to remain safe today.

## C. What A-5 leaves undecided
- **A-5** ("the sensitivity boundary is wrong / must be set by users, not us") means the **specific
  tier assignment for each attribute is not settled.**
- **Decision-register D-06**: "their sensitivity tier is **not fixed in `step3.pdf`**" (Aadhaar/PAN,
  and by extension every attribute).
- Document-02 **Table 13.1** (cited by FR-INF-007/FR-SENS-001 *by id*) lists working examples
  ("Name, date of birth, education history, marks, addresses"; "Government identifier numbers, bank
  details, signature images, …") but the register records it as **"an explicitly ASM-tagged working
  sensitivity classification for research purposes, tied to untested assumption A-5 … a list of
  sensitivity examples, not a field definition, and must not be promoted into one."** It is
  therefore **not** authoritative and is **not** adopted here.

## D. Approved decision (D-A5) — applied
step3.pdf determines none of the attribute tiers (A-5); the owner assigned them as below.
**Un-tiered default = sensitive.** ✔ marks the approved tier per attribute (applied in config +
extension). The declaration/consent *control* row is the one step3.pdf already fixed.

### Decision table (existing canonical vocabulary only)

| Attribute / Field | Routine | Sensitive | Consequential | Current Status | Owner Decision |
|---|---|---|---|---|---|
| person.full_name | ✔ | | | applied | **routine** |
| person.date_of_birth | | ✔ | | applied | **sensitive** |
| person.age | ✔ | | | applied | **routine** |
| person.email | | ✔ | | applied | **sensitive** |
| person.phone | | ✔ | | applied | **sensitive** |
| person.address | | ✔ | | applied | **sensitive** |
| identity.pan_number | | | ✔ | applied | **consequential** |
| identity.aadhaar_number | | | ✔ | applied | **consequential** |
| *(any un-tiered future attribute)* | | ✔ (default) | | applied | **sensitive (default)** |
| *declaration / consent control (field)* | never | never | **FIXED: consequential** | enforced (BR-006/FR-FLD-004) | already determined |

Notes (non-authoritative, for the owner's reference only, must not be treated as decisions):
- Document-02 Table 13.1 *examples* would touch: name, date_of_birth, address, education/marks
  (→ its "personal/education" examples) and government identifier numbers (PAN/Aadhaar → its
  "identifier numbers" examples). These are **examples tied to A-5**, not assignments.
- The extension **DEMO** build uses a demo-only default (`dob`, `pan`, `aadhaar` → approval-gated).
  This is **demo/evaluation only**, explicitly non-authoritative, and does not bind production.
- Register **G-15** notes a default posture ("an un-tiered attribute treated as sensitive/approval")
  for the controlled MVP; whether that becomes the production default is itself part of this A-5
  decision.

## E. Consequences of each decision (which behaviors each tier controls)
Each attribute's chosen tier affects these behaviors (today all are held at the safe floor):

| Tier chosen | Autofill | Reveal / masking | Approval | Chatbot responses | Document display |
|---|---|---|---|---|---|
| **routine** | may auto-fill when confidence permits (BR-001, still TBD) | value shown normally | none required | value could be stated if a value-exposing path is later added | shown normally |
| **sensitive** | never without per-instance approval (BR-005) | masked by default, reveal on action (FR-SENS-004) | explicit, exact-scope, one-time (FR-SENS-005/BR-007) | value withheld unless approved path exists | masked by default |
| **consequential** | never auto-acted (BR-006); floor cannot be lowered (BR-020) | masked; treated as highest protection | never approved in bulk/advance (FR-APR-005) | never disclosed/acted | masked, flagged |
| **unknown (today)** | never auto-fills | not disclosed | n/a (refuses to disclose) | value never exposed | not disclosed |

**Scope of impact (now applied):** the approved tiers drive **autofill** (routine auto-fills;
sensitive/consequential wait) and **approval + reveal/masking** in the extension review/fill flow.
**Chatbot** remains value-free by construction (its context never contains attribute values, so it
respects every tier without exposing values). **Document/record display** value-masking in the
frontend record view (FR-SENS-004, MVP SHOULD) is a bounded follow-up — surface the tier on the
record API and have the frontend mask accordingly; the extension review surface already masks
per tier.

## Engineering mechanism (applied via config, not hardcoded per site)
- Single config record: `config/vocabulary/canonical_attributes.demo.toml` `sensitivity`; extension
  runtime mirror: `extension/src/demo.js` `DEMO_TIERS` (+ `DEMO_DEFAULT_TIER = "sensitive"`), the
  same mirror convention the alias lists use. Consumed by the injected `classifyTier` /
  `classifyDeclaration` seams and `fieldAutomation`. Raise-only + consequential-floor invariants
  hold structurally (no lowering path exists).

**Status:** **D-A5 RESOLVED and applied.** The approved tiers are in force (default sensitive). The
only remaining gate for *production* disclosure/auto-fill is the separate **BR-001 threshold**
(UNSET, S-6). The frontend record-view value masking is a documented bounded follow-up.
