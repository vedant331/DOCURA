# DOCURA — Sprint 4 M14: S-6 OCR / Document-Understanding Evaluation

| Field | Value |
| --- | --- |
| Type | Evidence / evaluation milestone (S-6 / AR-AST-008) |
| Outcome | **E — BLOCKED, MORE CORPUS REQUIRED.** The held-out corpus does not exist; it cannot be legitimately created here. No engine is selected; no threshold is set. |
| Authority | `step3.pdf` (FR-OCR-001…010, AR-AST-008, BR-001/002, §7.1, §12.3 A-7), `SPRINT_4_D02_OCR_EVALUATION_PLAN.md`, `SPRINT_4_G02_CORPUS_GOVERNANCE.md`, `SPRINT_4_G12_FIELD_DEFINITIONS.md`, `SPRINT_4_G13_*`, `app/services/extraction.py`, M10–M13 docs |
| Rule applied | M14 §1 (evaluate, don't just "make OCR work"), §3 (audit, don't assume), §7 (privacy), §19 (no LLM), **§24 (stop at the blocker; don't fake it)** |
| Code changed | **None.** No engine installed, no corpus created, no threshold set, extractor seam untouched. |

## 1. Executive conclusion

Everything **downstream** of extraction is built and proven — the extractor seam, extraction persistence, classification, attribute observations, the derived structured record, and the M10/M13 autofill path (`person.full_name` auto-fill; `person.date_of_birth` consent-gated). The **only** missing piece for real document understanding is an **evaluated, approved extraction engine**, and that is blocked at the very first prerequisite: **AR-AST-008's held-out corpus of real, imperfect documents does not exist.**

S-6 cannot be run, and its blocker is not an engineering choice I can make. Per D-02, the corpus must be **real** documents from **consenting adults** collected through the **G-02-governed** process; D-02.4 warns that "any study that substitutes dummy data will produce a false positive on our riskiest assumption," and M14 §3/§24 forbid inventing one. So no engine may be selected (D-02 §6: selecting before evaluation "produces a threshold that merely describes whatever the chosen engine happens to do"), and no threshold may be set (AR-AST-008: "before any threshold is set").

## 2. S-6 audit (§3 — verified, not assumed)

| # | Question | Finding |
| --- | --- | --- |
| A | Held-out corpus exists? | **No.** Repository scan found no corpus/ground-truth/document store — only `step3.pdf` (the spec). |
| B | Location? | None. |
| C | Document types represented? | None — no documents. |
| D | Ground truth? | None. |
| E | Metrics defined? | **Yes, as method (D-02 §8.2)** — field exact-match, normalised accuracy, missing/incorrect rates, classification accuracy, confidence calibration, region accuracy, page/failure handling. **No target values** (targets would be thresholds; AR-AST-008 forbids setting them first). |
| F | Thresholds TBD? | **Yes** — BR-001 automatic-action threshold and the review threshold (G-04) are TBD; NFR-MNT-002 makes them configuration, produced by the evaluation. |
| G | Candidate engines permitted? | Self-hosted only for identity documents (privacy §7; D-02 §5.5 requires consent naming any external vendor — not obtained). None installed; D-01 left the port unselected by design. |
| H | Classification requirements? | FR-OCR-002/003, AR-AST-002 — classify supported types, with a **mandatory "unrecognised" outcome**. Seam supports it; unevaluable without a corpus. |
| I | Field sets per type? | **Not authored** beyond `person.full_name` and `person.date_of_birth` (v0.2-draft). The per-type FR-OCR-004 field sets are G-12 candidates, not approved. |
| J | Blocked by G-12/G-13? | **Yes** — stage-2 (field extraction, calibration, §7.1 type inclusion) is gated on G-12 authoring and G-14/G-15 tiers. |

## 3. Corpus & governance

- **Corpus:** absent. AR-AST-008 requires real, imperfect documents; §4.3 requires every candidate type present, grouped by person (so FR-INF-004 conflict detection is evaluable), including failure cases and out-of-set documents.
- **Governance (G-02, APPROVED structure):** consent (eight elements, purpose-bound, unbundled), named Corpus + Held-Out Custodians, least-privilege access, retention lifecycle (durations TBD), destruction structure (method BLOCKED by G-21–G-24). **Automatic ingestion of user-uploaded documents is prohibited.** The governance exists; the **collection has not been performed**.
- **Consequence:** building the corpus is a **real-world, consented data-collection operation**, not something reproducible in this repository. This is the binding blocker.

## 4. Candidate engines (§6 — on paper; none installed, none selected)

Assessed from published capabilities against the seam's needs (regions + per-token confidence + multipage + offline). **This is not a selection** — selection requires the held-out evaluation (D-02 §6).

| Engine | Offline/self-host | Regions (boxes) | Confidence | Multipage | License | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Tesseract | Yes | Yes (hOCR/TSV) | Word-level | Per-page loop | Apache-2.0 | Mature printed OCR; no layout/field understanding — needs post-processing to the field level |
| PaddleOCR (PP-OCR/PP-Structure) | Yes | Yes (det boxes) | Rec score | Per-page | Apache-2.0 | Strong detection + layout; heavier deps; GPU optional |
| EasyOCR | Yes | Yes | Yes | Per-page | Apache-2.0 | PyTorch dependency (large) |
| docTR / Surya | Yes | Yes | Yes | Per-page | Apache-2.0/GPL-varies | Modern; heavier; check licence per component |
| Cloud (Textract / Document AI / Azure) | **No** | Yes | Yes | Yes | Commercial | **EXCLUDED for identity docs** — privacy §7 + D-02 §5.5 vendor-named consent not obtained |

All self-hosted candidates satisfy the privacy constraint. **None can be chosen without the evaluation.** Note (D-02 §2.2, AR-AST-001): engine character/word confidence is **not** the same as field-level confidence usable by BR-001 — the mapping must itself be designed and evaluated.

## 5. Field-definition matrix (§5 — from G-12/G-13, not invented)

| Document type | Field | Canonical attribute | Evidence | Status |
| --- | --- | --- | --- | --- |
| Aadhaar / PAN / marksheets / degree / student ID / hall ticket | Name | `person.full_name` | Authored & approved (v0.2-draft, PD-B) | **APPROVED** (definition); **NOT EXTRACTED** (no engine/corpus) |
| Aadhaar / PAN / 10th / 12th marksheet | Date of birth | `person.date_of_birth` | Authored (v0.2-draft, M12-D3), tier TBD | **PROVISIONAL** (authored, not released; G-13-B not met); **NOT EXTRACTED** |
| Aadhaar / PAN | Identifier number | `person.aadhaar_number` / `person.pan_number` | G-12 candidate | **BLOCKED** (C-c identifier-storage, D-05.3) |
| address proof | Address (components) | `person.postal_address` | Shape approved (PD-A); components owed | **BLOCKED / MISSING DEFINITION** (C-b, L-INFO) |
| marksheets / degree | board, year, result, roll, qualification | `education.*` (5) | G-12 candidates | **BLOCKED** (C-a; no discriminating consumer yet) |
| photograph / signature | (image asset) | — | §8 asset, not a text field | **NOT APPLICABLE** to OCR field extraction |
| resume / others | — | — | store-and-search only | **NOT EXTRACTED** (unclassified/searchable, §7.1 "Other") |

Even the two authored attributes are **NOT EXTRACTED** today: extraction needs an engine (blocked) and the record is populated only by test fixtures.

## 6. Requirement traceability (§23)

| Requirement | Status | Reason |
| --- | --- | --- |
| **FR-OCR-001** (extract machine-readable text) | **BLOCKED** | No engine; seam ready (`extract()`), `UnconfiguredExtractor` fails honestly |
| **FR-OCR-002** (classify or unrecognised) | **PARTIAL** | Classification service + unrecognised outcome exist; unevaluable without corpus |
| **FR-OCR-003** (classification) | **PARTIAL** | Same as above |
| **FR-OCR-004** (defined field set per type) | **BLOCKED** | Field sets unauthored beyond full_name/date_of_birth (G-12); no extractor |
| **FR-OCR-005** (per-field confidence) | **PARTIAL** | Model carries per-block confidence; no engine to populate it |
| **FR-OCR-006** (below-review-threshold → review, no auto-fill) | **BLOCKED** | Review threshold is TBD (G-04); the evaluation produces it. Downstream `needs_review` state + the M10 policy (only "available" auto-fills) already enforce the *behaviour* |
| **FR-OCR-007** (source-region traceability) | **PARTIAL** | `TextRegion` provenance modelled end-to-end (record API returns region); no engine to emit it |
| **FR-OCR-008** (multi-page as one document) | **IMPLEMENTED (structurally)** | `ExtractionResult.pages` is one document across pages; `page_count`/`text` aggregate; unexercised without an engine |
| **FR-OCR-009** (failure preserves original, states reason, retry/manual) | **IMPLEMENTED** | Upload keeps the original; `failed`/`needs_review` states + `failure_reason` + `/reprocess` exist and are surfaced in the UI |
| **FR-OCR-010** | **PARTIAL/N-A** | Depends on engine output; seam ready |
| **BR-001** (automatic-action threshold) | **BLOCKED** | Value TBD (G-04); AR-AST-008 forbids setting before evaluation |
| **BR-002** (never auto-act below review threshold) | **IMPLEMENTED (behaviour)** | M10 policy auto-fills only backend-"available" values; sensitive/consent-gated otherwise |
| **A-7** (extraction may be unreliable on real scans) | **UNTESTED** | This is exactly what S-6 measures; untestable without the corpus |
| **S-6** (comprehension evaluation) | **BLOCKED** | Corpus absent |
| **G-10** (marksheet type boundary) | **OPEN** | Type taxonomy dependency; unresolved |
| **G-12** (per-type field definitions) | **PARTIAL** | Only full_name/date_of_birth authored |
| **G-13** (canonical vocabulary) | **PARTIAL** | v0.2-draft, two entries, not releasable (G-13-B) |

## 7. Confidence, source-region, multi-page, failure — results

- **Confidence / source-region / multi-page:** **no measured results** — no engine, no corpus. The *mechanisms* exist (per-block confidence, `TextRegion`, one-document-many-pages) and are ready to receive engine output. Document vs field confidence are kept separate by the model, and BR-001's use of confidence stays blocked on G-04 regardless of any engine's numbers (§11).
- **Failure:** the failure *behaviour* (FR-OCR-009) is implemented and testable independent of an engine — the `UnconfiguredExtractor` raising a clear, stack-trace-free failure is exactly the path a real engine's failure would take, and the document keeps its original + retry.

## 8. What can still be completed (and what was)

- **Completed here:** the S-6 re-audit; candidate-engine capability comparison; field-definition matrix; full FR-OCR traceability; confirmation the extractor seam and the whole downstream pipeline are ready; this report; register pointer D-02.7.
- **Deliberately NOT done (would be fabrication or premature):** installing/selecting an engine; creating a corpus or synthetic ground truth; setting any threshold; building an evaluation harness with nothing to run it on (its design is fixed in D-02 §8 — it is the first engineering task once the corpus exists, not before).

## 9. Decision status (§22)

**Outcome E — BLOCKED, MORE CORPUS REQUIRED.** No engine APPROVED; no document type APPROVED or demoted; evaluation not run. Recorded in the register at **D-02.7**. No approval forced.

## 10. Exact next step (the unblock path, in order)

1. **Collect the S-6 corpus** under G-02 governance (named Custodians, consented real documents from adults, grouped by person, all candidate types, imperfect scans, failure + out-of-set cases). *Real-world operation — the binding blocker.*
2. **Run D-02 stage 1** (OCR quality, classification, failure behaviour, engine eligibility) across ≥1 self-hosted candidate (e.g. Tesseract and one of PaddleOCR/docTR) using the D-02 §8 harness; keep the held-out split sealed.
3. **Select the engine on evidence**, implement it behind `DocumentExtractor` (the seam is ready), and set the review + automatic-action thresholds as **configuration** (NFR-MNT-002) from the observed distributions.
4. **Run stage 2** once G-12 field sets and G-14/G-15 tiers close: per-type inclusion (§7.1 demote-or-ship), field calibration, BR-001 threshold. Extracted `person.full_name` / `person.date_of_birth` observations then flow through the **existing** record → M10/M13 autofill path with **no new autofill logic**.

*No line of `step3.pdf` amended. No commit or push.*
