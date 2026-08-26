# Primary User Journey

**Step 4 · Document 16 of 20** — One application, end to end, for the approved primary persona.

---

## 1. The persona — as approved, not reinvented

This journey uses **Persona 1 from Step 2 §08**, unchanged. No new persona is introduced.

> ### The Applicant in Season
>
> **Context** — Final-year undergraduate student. Applying to internships, postgraduate programmes, and at least two
> scholarships in the same three-month window.
>
> **Document set** — Aadhaar, PAN, 10th and 12th marksheets, six semester results, student ID, photograph,
> signature, category and income certificates, resume, several course certificates.
>
> **Current behaviour** — Keeps a WhatsApp self-chat and a phone folder of scans. Re-crops the photograph for each
> portal. Asks a parent for details that are not memorised.
>
> **Primary goal** — Submit every application before its deadline without an error that disqualifies them.
>
> **Biggest fear** — Discovering after the deadline that something was wrong, mismatched, or never uploaded.
>
> **Success looks like** — Finishing an application in one sitting and feeling certain it is correct.
>
> *"I know I have it somewhere — I just don't know which version they want."*

Step 2 is careful about the status of this persona, and so is this document: personas there "are design instruments,
not research subjects. They are composite constructions… They must be revised — or discarded — after the first
research round." The emotion scores below are therefore **hypothesised**, not measured — assumption-tagged exactly
as Step 2 tags them.

The beachhead recommendation — final-year undergraduates — is itself assumption **A-3**, untested.

---

## 2. The journey

### Part 1 — Building the record, and opening the form

<!--DIAGRAM:15-primary-user-journey-->

### Part 2 — DOCURA acts, and DOCURA asks

<!--DIAGRAM:15b-primary-user-journey-part2-->

### Part 3 — Authorship, review, and submission

<!--DIAGRAM:15c-primary-user-journey-part3-->

---

## 3. The journey in full

Mapped against the current-state stages S1–S9 from Step 2 Table 10.1, so the change is visible rather than asserted.

| Stage | User goal | User action | DOCURA response | Emotion / friction | Decision point | Outcome |
|---|---|---|---|---|---|---|
| **S1 · Trigger** | Not miss the deadline | Hears about it late, from a group chat | *(none — outside DOCURA's control initially)* | Pressure; preparation time already compressed | — | Starts with less time than they need |
| **S3 · Gathering** | Stop hunting for files | Uploads marksheets, ID, photograph and signature in one action | Accepts, validates, queues with per-document status | **Relief** — the slowest, most frustrating stage collapses | — | Documents in one place, once |
| **S3 · Understanding** | Records that are usable, not just stored | Waits — briefly, and not blocked | OCR, classifies, extracts, scores each field | Curiosity, then trust | — | A machine-readable version of themselves |
| **S3 · Review** | Be sure it read things right | Sees one roll number flagged low-confidence | Shows the value **against the region it was read from** | Mild friction, offset by visible honesty | **H1 · Extraction review** | Corrected once, authoritative thereafter |
| **S3 · Conflict** | Not be disqualified by a spelling | Sees that two documents disagree on their name | Raises the conflict; marks **neither** authoritative | Surprise, then reassurance — P-06 is a silent disqualifier they did not know they had | **H2 · Conflict resolution** | One value chosen; the alternative retained |
| **S2 · Requirements** | Know what this form needs | Opens the mock form and **activates DOCURA** | Shows the readiness summary: needed, held, missing | **Relief** — requirements up front instead of at submission | — | Knows the shape of the task before starting |
| **S2 · Gap found** | No surprises at the end | Reads that the income certificate is missing | Names it as missing **before filling begins** | Frustration — but early, and actionable | — | Can fetch it while there is still time |
| **S5 · Data entry** | Stop retyping the same forty facts | Watches | Fills name, date of birth, marks — marked, traceable, reversible | **The core relief** — P-02, the highest-volume pain | — | Minutes instead of an evening |
| **S5 · Verification** | Trust it without re-checking everything | Clicks a filled value | Shows the source document | Trust consolidating | — | Does not re-verify by hand — the time saving survives |
| **S5 · Dropdown** | Not pick the wrong board | Watches | Matches by meaning; exactly one option clears the threshold | Quiet confidence | — | P-04 avoided silently and correctly |
| **S4 · Preparation** | Not be rejected on a file size | Watches | Produces a constraint-compliant **copy**; original untouched | **Relief** — P-03 and P-12, purely mechanical work, gone | — | No cropping, no compressing, no renaming |
| **S6 · Ambiguity** | Not guess | Is asked which of two category certificates applies | Presents both, with sources, and **why it could not decide** | Friction — the intended kind. A visible question is cheaper than an invisible mistake | **H3 · Ambiguity answer** | Right certificate chosen in one step |
| **S6 · Sensitivity** | Keep control of what is revealed | Is asked to approve disclosing the government identifier | Shows the exact value and the receiving field | Alertness, then trust — "it asked me, it did not decide for me" | **H4 · Sensitive disclosure** | One disclosure approved, scoped to that field |
| **S7 · Declaration** | Agree to what they actually read | Notices the declaration checkbox untouched | Identifies it, explains it, **does not tick it** | Surprise, then respect | **S1 · Mandatory stop** | The user ticks it personally, having read it |
| **S8 · Review** | Stop re-reading the form three times | Reads the review summary | Outstanding first; then values, methods, sources, attachments, approvals | **The second core relief** — P-07 | — | One verifiable pass replaces anxious proofreading |
| **S8 · Gap closed** | Complete the application | Uploads the income certificate manually | Reflects it in the summary | Satisfaction | — | Nothing outstanding |
| **S8 · Submission** | Own the moment of commitment | Presses submit | **Stops.** States that submission is theirs | **Confidence** — N-06, justified rather than hoped for | **S2 · Mandatory stop** | **USER SUBMITS** |
| **S9 · Aftermath** | Not carry the doubt | Checks the session history later | Shows every action, question, approval — and **no claim** about whether they submitted | Calm | — | P-07 closed; the loop does not restart |

---

## 4. What changed, measured against the pains

Step 2 §10 found that **time is lost mainly at S3, S4 and S5, while confidence is lost mainly at S6 and S8** — and
that these are not the same stages. This journey addresses both, and the two are measured separately (RO-5).

| Pain | Freq / Sev | Where this journey addresses it |
|---|---|---|
| **P-01** Cannot find the right version | H / H | Upload once; search the record (UC-012) |
| **P-02** Re-entering the same details | H / M | Automatic filling of routine fields (UC-017) |
| **P-03** Format and size rejections | H / H | Constraint-compliant preparation (UC-020) |
| **P-04** Dropdown options that do not match | H / H | Semantic matching, and asking when two are plausible (UC-018, UC-019) |
| **P-05** Which of several similar documents | M / H | Candidate documents shown distinguishably (UC-020) |
| **P-06** Name and detail mismatches | M / H | Conflict detection and user resolution (UC-009) |
| **P-07** Anxiety that something was missed | H / M | Review summary and session history (UC-025, UC-027) |
| **P-08** Session timeouts, lost progress | M / H | Placed values preserved; nothing reverted (EC-014, EC-016) |
| **P-09** Needing another person for a detail | M / M | Search over one's own record (UC-012) |
| **P-10** Signing declarations without reading | H / M | Made **clearer, never faster** (UC-022) |
| **P-11** Confirmations becoming lost documents | M / M | **Deferred in full** — FR-SUB-005, UC-032, horizon H1 |
| **P-12** Preparing the same document per portal | M / M | Preparation from the stored original each time (UC-020) |

Eleven of twelve pains are addressed in the MVP journey. P-11 is the one deliberately deferred, and Step 3 §13
records that deferral explicitly.

---

## 5. Where friction is intentional

Three moments in this journey are *slower* than an autonomous form-filler would be. Each is intentional, and each
traces to a rule rather than a limitation:

| Moment | Cost | Why it is worth it |
|---|---|---|
| Being asked about the category certificate | One interruption | "A confident guess is worse than a question" on an application with a deadline — Step 3 §4.2, BR-003 |
| Approving the identifier disclosure | One interruption | "A single unexpected autofill of a sensitive field can end adoption permanently" — Step 2 §13.1, BR-005 |
| Ticking the declaration personally | One manual action | The user's agreement must be something they decided — US-013, BR-006 |

Whether users experience these as care or as failure is assumption **A-2**, which Step 2 rates **fatal if wrong**.
Study S-5 — a prototype comparing a version that asks against one that silently decides — is designed to settle it,
and Step 3 §12.3 holds all of FR-AMB and FR-APR-001 pending that result.

---

## 6. Personas not used here

Persona 2 (**The Early-Career Professional**) and Persona 3 (**The Household Document Manager**) are real and
approved, but neither is the MVP journey. Persona 3 in particular introduces multi-person records, delegated access,
and third-party consent — which Step 2 defers deliberately, because "solving them early would force consent
architecture decisions before the single-user model is proven." FR-ACC-003 makes this a requirement: one record, one
owner, no delegation in MVP. Delegated access is UC-033, horizon H6.
