# MVP vs Future

**Step 4 · Document 18 of 20** — Where the line sits, and how it is held.

---

## 1. The rule that governs this document

> **Step 3 §11, Containment Rule.** A future requirement becomes an MVP requirement only through an explicit scope
> change recorded in this document with a new version number. Discovering during build that a future capability "is
> needed anyway" is a signal to re-examine the MVP definition — **not a licence to widen it silently.**

Step 4 introduces no new capability. Every use case and every diagram is marked, and each Future item is bound to
the unlocking condition Step 3 §11 assigns it.

---

## 2. Summary

| | MVP | Future | Total |
|---|---|---|---|
| **Use cases** | 28 | 13 | 41 |
| **Diagrams** | 23 | 0 | 23 |
| **Flow documents** | 13 | 0 | 13 |

No diagram depicts a Future capability as though it were available. Where a Future item is shown at all — the
out-of-boundary actors in Diagram 01, the Future cluster in Diagram 02 — it is drawn dashed and labelled FUTURE.

---

## 3. MVP use cases — all 28

| ID | Name | Priority |
|---|---|---|
| UC-001 | Create Account and Authenticate | MUST |
| UC-002 | Install and Connect the Browser Extension | MUST |
| UC-003 | Manage Active Sessions | SHOULD |
| UC-004 | Export the Complete Record | SHOULD |
| UC-005 | Delete Account and All Data | MUST |
| UC-006 | Upload Documents to the Vault | MUST |
| UC-007 | Process and Understand a Document | MUST |
| UC-008 | Review and Correct Extracted Information | MUST |
| UC-009 | Resolve Conflicting Information | MUST |
| UC-010 | Manage Documents in the Vault | MUST |
| UC-011 | Delete a Document | MUST |
| UC-012 | Search the Record and Retrieve a Document | MUST |
| UC-013 | Activate DOCURA on a Form | MUST |
| UC-014 | Detect the Form and Enumerate Fields | MUST |
| UC-015 | Derive Requirements and Present the Readiness Summary | SHOULD † |
| UC-016 | Interpret Field Meaning and Classify Sensitivity | MUST |
| UC-017 | Fill a High-Confidence Routine Field | MUST |
| UC-018 | Resolve a Dropdown, Radio, or Checkbox | MUST |
| UC-019 | Handle an Ambiguous Field | MUST |
| UC-020 | Match and Prepare a Required Document | MUST |
| UC-021 | Approve a Sensitive Disclosure | MUST |
| UC-022 | Leave Declarations and Consent to the User | MUST |
| UC-023 | Edit or Clear a DOCURA-Filled Value | MUST |
| UC-024 | Stop DOCURA | MUST |
| UC-025 | Review the Completed Form | MUST |
| UC-026 | Hand Back for User Submission | MUST |
| UC-027 | View Session History | SHOULD |
| UC-028 | Raise the Sensitivity of an Attribute | SHOULD |

**24 MUST, 4 SHOULD.** † UC-015's priority is disputed — see [Q4-01](questions-and-conflicts.md).

Step 3 §12.1 explains the high MUST proportion, and it applies equally here: "a consequence of the product thesis
rather than weak prioritisation: the confidence, ambiguity, sensitivity, and consent behaviours are what distinguish
DOCURA from an autofill tool, and a demonstration that omits them demonstrates a different product."

---

## 4. Future use cases, by horizon

| Horizon | Unlocking condition | Use cases |
|---|---|---|
| **H1** — Immediately after MVP | The MVP loop demonstrably works **and** A-1 and A-2 have reported favourably | UC-029 camera capture · UC-031 remembered answers · UC-032 receipt capture and review export · UC-036 two-factor authentication |
| **H2** — Surface expansion | A-8 reports where applications are actually completed | UC-039 mobile browsers · UC-040 multi-select and custom widgets · UC-041 embedded frames |
| **H3** — Comprehension expansion | Extraction quality on the MVP type set is proven against real documents | Handwritten content, additional scripts and languages, additional document types, derived document assembly *(FR-OCR-011/012, FR-MATCH-011 — no use case specified, per §1)* |
| **H4** — Vault maturity | Users maintain records across more than one application season | UC-030 cloud and locker import · UC-034 natural-language search · UC-037 application contexts |
| **H5** — Trust maturity | The sensitivity boundary is settled by evidence (A-5) **and** interruption cost is measured | UC-035 reviewed bulk approval · UC-038 learning from corrections |
| **H6** — Beyond the individual | The single-user model is proven **and** a consent architecture is designed for third parties | UC-033 delegated and family access · UC-037 proactive deadline awareness |

---

## 5. Explicit MVP exclusions, and where a flow might have leaked

Step 3 §10.3 lists each exclusion as a decision. This table records where the corresponding Step 4 flow could
plausibly have widened, and confirms it did not.

| Excluded | Requirement | Where the flow could have leaked | What the flow actually does |
|---|---|---|---|
| Mobile browser support | FR-EXT-008 | Extension lifecycle | Desktop only; mobile shown as out-of-boundary in Diagram 01 |
| Camera capture, cloud / locker import | FR-UPL-008/009/010 | Document intake | Local file upload only; import sources drawn dashed and labelled FUTURE |
| Handwritten and non-MVP-language documents | FR-OCR-011/012 | Document lifecycle | Not depicted; unsupported types fall to store-and-search |
| **Cross-session learning, remembered answers** | FR-FLD-010, FR-AMB-008 | **Ambiguity flow** | The reuse node reads *"same session only"*; §7 of that document states every session starts from the record, not from history |
| Multi-select, custom widgets, frames, async lists | FR-FLD-008/009, FR-FRM-008, FR-DRP-009 | Dropdown and detection flows | Reported as unsupported (EC-010) rather than partially handled |
| Delegated or family access | FR-ACC-010 | Actors | Persona 3 explicitly excluded; one record, one owner |
| **Bulk approval of sensitive disclosures** | FR-APR-006 | **Sensitive flow** | Approval is drawn per-instance; §4 states no bulk control exists |
| Submission receipt capture, review export | FR-SUB-005, FR-REV-007 | Review and submission | The flow ends at USER SUBMITS; nothing after it is depicted |
| Natural-language search, completeness indicators, collections, expiry detection | FR-SRCH-006, FR-INF-010, FR-DOC-009/010 | Search, document lifecycle | Search shown as type / label / text / attribute only; expiry left to the user's primary designation |
| On-device-only processing, offline access | NFR-PRIV-008, NFR-AVL-003 | System context | Not depicted |
| Two-factor authentication | FR-ACC-009 | Account flows | Single factor in UC-001; 2FA is UC-036 |

**Two near-misses worth naming.** Remembered answers (FR-AMB-008) and bulk approval (FR-APR-006) are the two Future
capabilities that would most naturally have crept into a well-meaning flow — the first because reuse feels like
efficiency, the second because it reduces interruption. Both are excluded, and both are excluded for the same
reason: Step 3 §12.2 calls remembering an answer "a form of assumed consent", and bulk approval a relaxation of
BR-007. Efficiency is not a sufficient argument against a consent rule.

---

## 6. The scope condition that must travel with this step

Step 3 §10 attaches a condition to the MVP that Step 4 restates rather than dilutes:

> **The MVP as scoped here demonstrates the product thesis end to end. It is not a public release.** Two exclusions
> — **two-factor authentication** and **independent security review** — must be closed before any user outside a
> controlled pilot stores a real identity document. Treating the demonstration MVP as launchable is the most likely
> way this scope decision causes harm.

Nothing in these 28 use cases changes that. UC-001 specifies single-factor authentication because that is MVP scope;
it does not imply the MVP is shippable to real users with real documents.
