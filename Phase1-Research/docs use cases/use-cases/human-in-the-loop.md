# Human-in-the-Loop Map

**Step 4 · Document 15 of 20** — Every point where a human decision is mandatory, and the rule that puts it there.

**Source:** Step 3 §6.4 Table 6.2, plus BR-008.

---

## 1. These are not error paths

Step 3 §6.4 is explicit about how to read this map:

> These are the moments where a human is required by design. **They are not error paths; they are the product
> working correctly.**

A product that reached the end of a form with zero human decisions would not be a better DOCURA. It would be a
different product — the "autonomous form-filling agent" Step 1 §06 explicitly positions against, which "optimises
for completion, so it guesses under ambiguity and treats consent as one more field."

---

## 2. The map

<!--DIAGRAM:14-human-in-the-loop-->

---

## 3. The three categories, distinguished

The brief asks that automated action, user decision, and mandatory stop be clearly distinguished. They differ in
**who can change the outcome**:

| Category | Who decides | Can automation ever do it? | Colour |
|---|---|---|---|
| **AUTOMATED ACTION** | DOCURA, within thresholds | Yes — that is the point | Teal `#4FC8A5` |
| **USER DECISION** | The user, after DOCURA prepares the choice | **No** — but DOCURA does everything up to the decision | Amber `#E8A33D` |
| **MANDATORY STOP** | The user, personally | **Never, at any confidence level, under any setting** | Violet `#9A8CF0` |

The difference between the second and third is the difference between *DOCURA cannot decide this* and *DOCURA is
not permitted to decide this*. H1–H4 could in principle be automated by a more confident system and are held back
by policy about uncertainty. S1 and S2 could never be automated by any system, however certain — they are about
authorship, not accuracy.

---

## 4. The six mandatory points

Reproduced from Step 3 §6.4 Table 6.2, with the Step 4 use case that specifies each.

| Point | Trigger | Rule | Use case | Category |
|---|---|---|---|---|
| **H1 · Extraction review** | Any value below the review threshold | BR-002 | UC-008 | User decision |
| **H2 · Conflict resolution** | Documents disagree about the same attribute | BR-004 | UC-009 | User decision |
| **H3 · Ambiguity answer** | Multiple plausible values, options, or documents | BR-003 | UC-019 | User decision |
| **H4 · Sensitive disclosure** | A field or document classified sensitive | BR-005, BR-007 | UC-021 | User decision |
| **S1 · Declaration and consent** | Any consequential control | BR-006 | UC-022 | **Mandatory stop** |
| **S2 · Final submission** | **Always** | BR-008 | UC-026 | **Mandatory stop** |

### The trigger for S2 is "Always"

Every other row has a condition. S2's trigger, as Step 3 writes it, is the single word **Always**. There is no state
of the world in which submission does not require the user.

---

## 5. Two further points where the user *may* intervene

These are not mandatory — DOCURA proceeds without them — but they must always be available, so the map shows them.

| Point | Guarantee | Rule | Use case |
|---|---|---|---|
| **Edit or clear any DOCURA-filled value** | Every automated action must be reversible by the user **before submission**; a user value is never overwritten automatically | BR-012, BR-015 | UC-023 |
| **Stop DOCURA** | All activity ceases at once; placed values remain; a fresh activation is required to resume | FR-EXT-006 | UC-024 |

---

## 6. Where each point sits in the journey

| Phase | Automated | Human decision | Mandatory stop |
|---|---|---|---|
| **Building the record** | OCR, classification, extraction, confidence scoring, conflict **detection**, deterministic normalisation | **H1** extraction review · **H2** conflict resolution | — |
| **Understanding the form** | Field enumeration, meaning interpretation, sensitivity classification, candidate ranking | — | — |
| **Acting on the form** | Filling routine fields above threshold, selecting one confident option, preparing and attaching documents | **H3** ambiguity · **H4** sensitive disclosure | **S1** declarations and consent |
| **Closing** | Assembling the review summary, recording history | *(user may edit or stop)* | **S2** final submission |

Note that **conflict detection is automated but conflict resolution is not** (AR-DET-008: "Conflict detection
between documents shall be deterministic; conflict resolution shall never be automated at all"). The same split
appears at H3: DOCURA produces the ranked candidate list, and the user picks from it.

---

## 7. The layer rule underneath the map

Step 3 §6 separates DOCURA's intelligence by what kind of certainty each layer offers. The map is a direct
consequence of the third column below.

| Layer | Nature | May be trusted for | **Must never be used for** |
|---|---|---|---|
| **AR-DET** · Deterministic | Same input always gives the same output. Verifiable by inspection. | Format conversion, resizing, validation, normalisation, threshold comparison, classification of known field patterns | Anything requiring **interpretation of meaning** |
| **AR-AST** · AI-assisted | Probabilistic. Produces a best interpretation with a confidence. **Can be wrong plausibly.** | Reading documents, classifying type, interpreting field meaning, matching values to options semantically | Deciding anything **the user has not been given the chance to see and correct** |
| **AR-AGT** · Agentic | Acts on the world. Consequences leave the product and reach an institution. | Placing values, selecting options, attaching documents — **strictly within threshold and sensitivity limits** | **Consent, declarations, submission,** and any action the user cannot see and reverse |

"Can be wrong plausibly" is the phrase that generates H1–H4. A plausible-but-wrong output is not caught by the
system that produced it, so it must be caught by a person — which is why every AR-AST output is either shown for
correction (H1, H2), presented as a choice (H3), or gated by approval (H4).

---

## 8. Measuring whether this is working

Step 3 requires the philosophy to be **evaluated rather than assumed**:

| Metric | Requirement | What it tells us |
|---|---|---|
| How often DOCURA acts, asks, and declines to act | NFR-OBS-002 | Whether the act/ask balance matches the philosophy |
| User **override rate** on automatically filled fields | NFR-OBS-003 | **The primary indicator of silent error** — every override is a case where DOCURA was confident and wrong |
| Extraction and field-interpretation confidence distributions, in aggregate | NFR-OBS-001 | Whether thresholds are set in the right place |
| Number of interruptions vs number of genuinely ambiguous or sensitive items | NFR-USE-002 | Whether asking has become nagging (risk R-3) |

The two failure directions are named in Step 2 §13.2: "Interrupt too often and the product is slower than typing;
interrupt too rarely and it violates the principle it was built on." Both metrics above exist to detect which way
the product is drifting — and the boundary itself must be set by users (assumption **A-5**), not by the team.
