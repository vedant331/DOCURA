# DOCURA — 04 · Use Cases & User Flows

**Document** Use Cases & User Flows
**Product** DOCURA — personal document intelligence layer
**Version** 1.0 — Draft for alignment
**Owner** Product Management
**Date** 26 August 2026
**Source of truth** `Research/step1.pdf` (01 — Product Vision), `Research/step2.pdf` (02 — Problem & User Research), `Research/step3.pdf` (03 — Requirements Specification)
**Followed by** 05 — (not started; Step 4 stops here)

---

## What this document set is

Step 4 defines **how DOCURA behaves from the user's perspective** and **how the actors interact**. It converts the
157 functional and 57 non-functional requirements of Step 3 into 41 use cases and 17 validated flows, and shows
exactly where the product's governing rule takes effect:

> **Automate certainty. Ask about ambiguity. Never automate consent.**

Nothing here introduces new functionality. Every use case, branch, and decision point traces to an identifier that
already exists in Steps 1–3. Where Steps 1–3 are silent or disagree, the issue is recorded in
[`questions-and-conflicts.md`](questions-and-conflicts.md) rather than resolved by invention.

## What this document set is *not*

It is not architecture, not a data model, not an API design, not a UI design, and not a delivery plan. Those follow
as separate steps. Where a flow names a "layer", it is a **responsibility boundary taken from Step 3 §6**, not a
component.

---

## Reading order

| # | File | What it gives you |
|---|---|---|
| 1 | [`actors-and-boundaries.md`](actors-and-boundaries.md) | Who and what interacts with DOCURA; the system boundary; the terminology contract used by every diagram |
| 2 | [`use-case-catalogue.md`](use-case-catalogue.md) | All 41 use cases — 28 MVP, 13 Future — with actors, requirements, and purpose |
| 3 | [`detailed-use-cases.md`](detailed-use-cases.md) | Full 11-part specification for each of the 28 MVP use cases |
| 4 | [`master-user-flow.md`](master-user-flow.md) | The complete MVP journey, upload through user submission |
| 5 | [`document-lifecycle.md`](document-lifecycle.md) | Upload → validation → OCR → extraction → review → storage → retrieval → deletion, with failure paths |
| 6 | [`extension-flow.md`](extension-flow.md) | The browser extension lifecycle, activation through hand-back |
| 7 | [`autofill-decision-flow.md`](autofill-decision-flow.md) | The per-field decision: observe → understand → match → confidence → sensitivity → act or ask → verify |
| 8 | [`dropdown-flow.md`](dropdown-flow.md) | Option matching for dropdowns, radio groups, and checkboxes |
| 9 | [`ambiguity-flow.md`](ambiguity-flow.md) | What happens when more than one reasonable answer exists |
| 10 | [`document-matching-flow.md`](document-matching-flow.md) | Form requirement → candidate documents → preparation → attachment |
| 11 | [`sensitive-information-flow.md`](sensitive-information-flow.md) | Per-instance approval for sensitive disclosure |
| 12 | [`legal-consent-flow.md`](legal-consent-flow.md) | Declarations and consent — the boundary automation never crosses |
| 13 | [`review-submission-flow.md`](review-submission-flow.md) | Final review, hand-back, and **USER SUBMITS** |
| 14 | [`error-flows.md`](error-flows.md) | The 20 edge cases of Step 3 §14 as specified behaviour, plus the generic error path |
| 15 | [`human-in-the-loop.md`](human-in-the-loop.md) | Every point where a human decision is mandatory, and why |
| 16 | [`primary-user-journey.md`](primary-user-journey.md) | The journey of Persona 1, *The Applicant in Season* |
| 17 | [`requirements-traceability.md`](requirements-traceability.md) | Use case → story → requirement → rule → criterion, plus coverage gaps |
| 18 | [`mvp-and-future.md`](mvp-and-future.md) | The MVP / Future line, and how it is held |
| 19 | [`quality-review.md`](quality-review.md) | Formal review of this step against 15 checks |
| 20 | [`questions-and-conflicts.md`](questions-and-conflicts.md) | What Steps 1–3 do not settle, and what it costs to leave it unsettled |

## Diagrams

All 17 Mermaid sources live in [`diagrams/`](diagrams/) as `.mmd` files and are embedded in the documents above.
They are validated by Mermaid's own parser — see [`diagrams/README.md`](diagrams/README.md) and
[`tools/`](tools/) for the render and validation pipeline.

## Identifier conventions

| Pattern | Meaning | Introduced by |
|---|---|---|
| `UC-nnn` | Use case | **This step** |
| `FR-<MOD>-nnn`, `NFR-<CAT>-nnn` | Requirement | Step 3 §1, §2 |
| `US-nnn`, `AC-US-nnn-n` | User story, acceptance criterion | Step 3 §3, §4 |
| `BR-nnn` | Business rule | Step 3 §5 |
| `AR-DET/AST/AGT-nnn` | Automation requirement | Step 3 §6 |
| `EC-nnn` | Edge case | Step 3 §14 |
| `P-nn`, `N-nn`, `S-n`, `RC-n`, `A-n`, `R-n` | Pain, need, journey stage, root cause, assumption, risk | Step 2 |
| `Q4-nn` | Question / conflict raised by **this step** | **This step** |

**No identifier outside `UC-nnn` and `Q4-nn` was invented here.** Every other ID cited in this document set exists
in Steps 1–3 and can be checked against them.
