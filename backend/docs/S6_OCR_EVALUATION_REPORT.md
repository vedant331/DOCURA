# S-6 OCR Evaluation Report

Authoritative requirements source: `backend/step3.pdf`. This report records measured evidence
only; it invents no requirements, thresholds, pass criteria, corpus data, or ground truth. **No
real personal values (name, DOB, Aadhaar, PAN, address) appear here** — only document types,
field identifiers, aggregate counts, and match/similarity signals, per the value-free rule.

> **Corpus-expansion pass (latest): no new real evidence available.** An expansion attempt found
> no additional real, consented documents in the environment beyond the 3 already ingested (one
> subject). Nothing was fabricated; the corpus, ground truth, strict metric, engine, and BR-001 are
> unchanged. The baseline below still stands. Remaining blocker + next action: `S6_NEXT_CORPUS_PLAN.md`.

## 1. Corpus used
Local held-out corpus at `backend/var/s6_corpus/` (gitignored; never committed), version `v0`:

| id | type | pages | split | consent | de-id | source |
|---|---|---|---|---|---|---|
| aadhaar_001 | aadhaar | 1 | held_out | consented | deidentified | personal_owned |
| pan_001 | pan | 1 | held_out | consented | deidentified | personal_owned |
| marksheet_12_001 | marksheet_12 | 2 | held_out | consented | deidentified | personal_owned |

3 documents, 4 pages, **all from the same person**, all held-out. `scripts.s6_validate` reports
the corpus **VALID**. Ground truth is now **real** (8 expected fields total).

## 2. Ground-truth status
The three annotation files now contain **real transcribed text** (owner-supplied), replacing the
earlier placeholders. Treated as authoritative and **not modified** in this evaluation. 8 expected
fields: aadhaar_001 (3: full_name, date_of_birth, aadhaar_number), pan_001 (2: full_name,
pan_number), marksheet_12_001 (3: full_name + 2 untagged page values).

## 3. Baseline result (engine `tesseract 5.5.3.20260724`, config `default`, split `held_out`)
| metric | value |
|---|---|
| documents | 3 |
| pages | 4 |
| processing_failure_rate | 0.0 |
| page_success_rate | 1.0 |
| field_exact_match_accuracy | **0.25** |
| normalized_field_accuracy | **0.25** |
| missing_field_rate | **0.75** |
| region_availability | null (annotations carry no regions) |
| incorrect_field_rate / classification_accuracy / confidence_calibration | null (TBD by design) |

Per document: aadhaar_001 1/3, pan_001 1/2, marksheet_12_001 0/3 matched.

## 3a. Metric status: strict (authoritative) vs containment (diagnostic only)
Two distinct numbers appear in this report and **must not be conflated**:

- **Strict field exact-match / normalized accuracy — the authoritative S-6 metric.**
  `metrics.score_document` credits a field only when the expected text **equals** a whole OCR
  block or the page text. Baseline: **exact 0.25, normalized 0.25** (missing 0.75). This is the
  metric S-6 acceptance is judged on. It was **not** modified, loosened, or replaced.
- **Containment / value-read rate — a diagnostic only.** A count of how many ground-truth values
  appear *as a substring* anywhere in the OCR output. Baseline: **8/8**. It exists solely to
  explain *why* the strict metric is low (the values are read but embedded in longer lines). It is
  **not** an S-6 metric, is **not** substituted for the strict metric, does not change any strict
  number, and does **not** count toward S-6 acceptance. Short values make substring signals
  fragile, which is one reason it is diagnostic rather than authoritative.

In short: the strict metric stays 0.25/0.25 and remains the number of record; containment 8/8 is
context that identifies the cause, nothing more.

### 3b. Methodology decision (line vs value granularity) — NOT decided here
`step3.pdf` specifies *what* extraction must do (FR-OCR-004/005: extract the defined field set with
per-field confidence; §7.1/ASM-001: a type must "meet the review threshold on real documents" via
S-6) but is **silent on the string-matching granularity** of the S-6 field metric. The matching
rule lives in `metrics.score_document` and cites the **D-02 §8.2** methodology. So how the strict
metric should treat a value that OCR emits *inside a longer line* is a genuine, unresolved
**methodology decision** — it is not fixed by the requirements, and is deliberately **not invented
here**. Two deterministic paths:

- **PATH A — keep strict whole-block/page equality authoritative; constrain annotation granularity.**
  The metric is unchanged. Ground-truth `text` must be transcribed at the granularity the OCR
  emits (the line as read), not at value granularity. Pro: zero code change, no risk of false
  positives. Con: annotators must know how the engine segments lines; re-annotation of existing
  files (at line granularity, not to inflate scores) would be needed.
- **PATH B — keep strict equality authoritative AND add a formally-specified, separate containment
  field-read diagnostic.** The strict metric stays the number of record; a distinct, named
  containment metric is added to the harness and reported alongside it (never substituted). Pro:
  captures true recognition ability without weakening the authoritative metric. Con: a small,
  deliberate harness change, and containment must be specified carefully (short values are fragile).

**Who decides:** the S-6 / D-02 methodology owner. This report does not choose between A and B, does
not change the authoritative metric, and does not rewrite annotations. Until the owner decides, the
strict 0.25 stands as the authoritative result and containment 8/8 stands as diagnostic context.

### 3c. Decision D-OCR-METRIC — RESOLVED: PATH B
**Owner decision (approved):** **PATH B.** The strict whole-block/page field exact-match remains
the **authoritative** S-6 metric; normalized accuracy and missing-field rate derive from it.
Containment/value-read is **retained as a separate, explicitly non-authoritative diagnostic** and
is never substituted for the strict metric. Existing ground-truth annotations are **preserved** and
not rewritten. A formally-specified containment metric (with a minimum-length guard and defined
normalization) may be added to the harness in a later task as an explicitly-labelled diagnostic; the
strict metric and ground truth stay untouched. This changes no strict number, sets no threshold,
and selects no engine. The two paths that were on the table are recorded below for provenance.


Current evidence: strict exact-match 0.25, normalized 0.25, missing 0.75, containment/value-read
**8/8** — i.e. every ground-truth value is present, but 6 of 8 sit *inside* larger OCR blocks so the
whole-block/page metric scores them missing. `step3.pdf` (AR-AST-008: "evaluated against a held-out
corpus of real, imperfect documents before any threshold is set") does **not** specify the matching
granularity, so the requirements do **not** determine the path — the owner must choose. Neither
path changes the strict metric's authority or the existing ground truth.

**PATH A — strict whole-block/page equality remains authoritative; fix annotation granularity.**
- *Measures:* whether the expected string appears as a **complete recognized unit** (a whole OCR
  block or the page text) — recognition **and** segmentation together.
- *Does NOT measure:* whether a value was read correctly when it is embedded in a longer line
  (those score as missing even though OCR read them).
- *Consequences for annotation:* future ground truth must be transcribed at the **line-as-emitted**
  granularity; existing annotations would need re-doing at that granularity (to match the metric,
  **not** to raise scores).
- *Consequences for comparing OCR configs:* config comparisons stay dominated by **segmentation**
  differences (as observed: strict swung 0.0→0.5 across PSM modes while value-read stayed 8/8), so
  the strict number remains a noisy basis for engine/config comparison at small corpus sizes.
- *Approval required:* owner approves the annotation convention; **no code change**.

**PATH B — strict metric unchanged as authoritative; ADD a formal containment diagnostic.**
- *Measures (new diagnostic):* whether the normalized expected value **appears anywhere** in the
  OCR output (recognition, independent of segmentation) — reported **alongside**, never replacing,
  the strict metric.
- *Does NOT measure:* exact positional/segmentation correctness (that stays the strict metric's
  job); and containment is **fragile for very short values** (a 4–5 char value can match by
  coincidence), so its methodology must bound minimum length / define normalization explicitly.
- *Consequences for annotation:* value-granularity annotations become directly usable by the
  diagnostic; existing ground truth can stay as-is.
- *Consequences for comparing OCR configs:* gives a **recognition-focused** comparison signal less
  sensitive to segmentation, while the strict metric remains the authoritative acceptance number.
- *Approval required:* owner approves adding a **new, separately-named** harness metric and its
  written methodology (a small, deliberate `metrics` addition in a later task); the strict metric
  and ground truth are untouched.

**Not changed by this document:** the strict metric, its authority, the ground truth, and the code.
Only the owner's choice (A or B) unblocks the annotation/methodology direction for the next S-6 cycle.

## 4. Per-field failure analysis (PII-safe)
For every expected field I compared normalized ground truth against the OCR output using the
evaluator's own logic **plus** containment/similarity signals. Values are never shown.

| doc | field | evaluator match | GT is substring of an OCR block/page? | best whole-block sim | cause |
|---|---|---|---|---|---|
| aadhaar_001 | identity.aadhaar_number | **MATCH** | yes | 1.00 | value is its own OCR line |
| aadhaar_001 | person.full_name | miss | **yes** | 0.95 | OCR read it; embedded in a longer line |
| aadhaar_001 | person.date_of_birth | miss | **yes** | 0.24 | OCR read it; embedded in a longer line |
| pan_001 | person.full_name | **MATCH** | yes | 1.00 | value is its own OCR line |
| pan_001 | identity.pan_number | miss | **yes** | 0.87 | OCR read it; embedded in a longer line |
| marksheet_12_001 | person.full_name (p1) | miss | **yes** | 0.52 | OCR read it; embedded in a longer line |
| marksheet_12_001 | untagged (p1) | miss | **yes** | 0.47 | OCR read it; embedded in a longer line |
| marksheet_12_001 | untagged (p2) | miss | **yes** | 0.45 | OCR read it; embedded in a longer line |

**Key finding:** all 8 ground-truth values are present in the OCR output — the 2 "matched" ones as
standalone lines, the other 6 **as substrings inside longer OCR lines** (e.g. a label + value on
one line). The evaluator scores a field only when the expected text **equals an entire OCR block
or the page text** (`metrics.score_document`: `expected.text in {block texts} ∪ {page text}`), so a
value annotated at *value granularity* that OCR emitted inside a *line-granularity* block is
counted missing even though it was read correctly.

- exact-match == normalized-match (0.25): the two matches were exact; normalization changed nothing.
- **incorrect** fields: the evaluator does not expose an incorrect-field metric (`incorrect_field_rate`
  is null by design), and none of the misses were OCR misreads — they were reads not credited by
  whole-unit matching.

## 5. Concrete causes of the 75% missing-field rate
Ruled **in**: evaluator **matching granularity** (whole-block/page equality) vs **annotation
granularity** (field values). Ruled **out** by evidence:
- Tesseract recognition — **not** the cause: containment "value-read" rate is **8/8** at baseline.
- Image quality / preprocessing — **not** the cause: values are already read (see §6).
- Page/PDF handling — fine: page_success 1.0; the 2-page PDF produced 2 pages, 40 blocks.
- Field-extraction logic — not involved: the S-6 harness scores raw OCR text, not the field extractor.
- Implementation bug — **none**: the evaluator computes its defined metric correctly (verified by
  a synthetic control scoring 1.0 on correct GT, and by the existing tests in
  `tests/test_s6_evaluation.py`).

## 6. Configurations / preprocessing evaluated (same held-out corpus)
Existing repo knobs: `pdf_scale` (PDF rasterization scale) and `languages`. No image preprocessing
exists in the repo. Variants below were run **eval-only** (injected reader / constructor param) with
**no production code change**, using only already-installed libraries (Pillow, pytesseract,
pypdfium2). "value-read" is a containment diagnostic (GT substring present in OCR), **not** an S-6
metric.

All configs: engine `tesseract 5.5.3.20260724`, corpus `v0`, split `held_out`, 3 documents, 4
pages. Strict exact/normalized are the authoritative numbers; value-read is diagnostic only (§3a).

| config | preprocessing | exact | normalized | missing | proc-fail | page-succ | region | value-read |
|---|---|---|---|---|---|---|---|---|
| C0_baseline | none | 0.25 | 0.25 | 0.75 | 0.0 | 1.0 | null | **8/8** |
| C1_pdf_scale_3x | PDF rasterized ×3 | 0.25 | 0.25 | 0.75 | 0.0 | 1.0 | null | 8/8 |
| C2_img_gray_2x | grayscale + ×2 + autocontrast (images) | 0.375 | 0.375 | 0.625 | 0.0 | 1.0 | null | 8/8 |
| C3_img_gray_3x | grayscale + ×3 (images) | 0.125 | 0.125 | 0.875 | 0.0 | 1.0 | null | 6/8 |
| C4_img_psm6 | Tesseract `--psm 6` (images) | 0.0 | 0.0 | 1.0 | 0.0 | 1.0 | null | 8/8 |
| C5_img_psm11 | Tesseract `--psm 11` (images) | 0.5 | 0.5 | 0.5 | 0.0 | 1.0 | null | 8/8 |

**Interpretation:** the strict metric swings from **0.0 (psm 6) to 0.5 (psm 11)** by changing only
page-segmentation, while **value-read stays 8/8** — i.e. OCR reads the same values regardless; the
number moves purely with *segmentation* (which values happen to land as their own block). On 8
fields from 3 documents this is **noise, not signal**: no configuration is called "better", because
the measured evidence cannot support that conclusion at this corpus size. `pdf_scale` had no effect
on the strict metric here. **No engine other than Tesseract is reproducible** in this environment
(Windows, Python 3.14, no GPU; PaddleOCR/EasyOCR/docTR are not installable — no cp3.14/GPU wheels,
numpy/opencv absent), so the engine comparison is **not** complete; only Tesseract was benchmarked.

## 7. Implementation bug discovered and fixed
**None.** No production or evaluation code was changed. Changing the evaluator to substring-matching
would raise the number but (a) modify S-6 methodology to improve the benchmark (out of scope), and
(b) risk false positives on short values (the ≤5-char fields already show fragile substring signals).
Whether the S-6 field metric should credit line-embedded values is a **methodology decision** (D-02
§8.2), left to the owner — not silently altered here.

## 8. Regression tests added
**None** — no code changed, and the relevant behavior is already covered:
`tests/test_s6_evaluation.py::test_score_document_counts_matches_missing_and_region` (present GT
matched, absent GT → missing) and `::test_runner_with_synthetic_engine_scores_and_is_pii_free`
(end-to-end scoring is correct and PII-free); rasterization/adapter covered by
`tests/test_pdf_rasterization.py` and `tests/test_ocr_candidate_adapter.py`.

## 9. Limitations of the current 3-document corpus
- **Too small and non-independent** for any statistical claim: 3 documents, 8 fields, **one person**,
  **n = 1 per document type**. AR-AST-008 needs a held-out corpus of *real, imperfect* documents
  (plural, varied) before a threshold is set.
- No degradation variety (skew/blur/lighting/multi-source) and no per-type replication.
- The strict metric is **confounded by matching granularity** here, so it under-reports OCR's true
  field-reading ability (which is ~100% by containment). Until annotation/metric granularity is
  reconciled, the strict accuracy number is not a faithful measure of extraction quality on this set.

## 10. Is the evidence sufficient for engine selection?
**No.** With one document per type, a single subject, and a metric confounded by granularity, there
is no basis to select a production engine or compare engines. What the evidence *does* establish:
the pipeline runs end-to-end on real held-out documents with zero failures, and Tesseract reads
100% of the annotated values on this set. What it does **not** establish: field-correctness at
scale, per-type reliability (ASM-001), or any threshold-supporting distribution.

## 11. BR-001 threshold
**Remains UNSET.** No automatic-action or review threshold was set (AR-AST-008 requires adequate
real held-out evidence first, which this 3-document set does not provide).

## 12. Production engine
**Remains UNSELECTED.** Production extraction is still `UnconfiguredExtractor`. Tesseract was run
only as an evaluation candidate behind the seam; no production OCR or automatic filling was enabled.

## 13. Reproducibility
The evaluation is deterministic: two consecutive `run_evaluation` calls on the default config
produced **identical** overall metrics. Every run emits a versioned, PII-free result JSON under
`var/s6_corpus/results/` (`<timestamp>_<engine>_<run_id>.json`) capturing engine, version, config
id, corpus version, split, counts, metrics, per-document rows, failures, and environment. The
authoritative baseline result for this checkpoint is the most recent `..._tesseract_...json`.

## 14. Remaining evidence gaps
See `docs/S6_NEXT_CORPUS_PLAN.md`. Summary: single subject; one document per type; no
`development` split; no degradation spread; engine comparison incomplete (only Tesseract is
reproducible here); and the line-vs-value methodology decision (§3b) is open. None of these can be
closed with fabricated data.

## 15. Manual end-to-end OCR test readiness
The OCR text-extraction path is ready for manual end-to-end testing **as an evaluation candidate**
(not production): OCR produces text from real documents, multi-page works, output reaches the
evaluator, ground truth loads, matching is deterministic and reproducible, results are versioned,
held-out isolation holds, and raw sources are gitignored. Production extraction remains
`UnconfiguredExtractor`; manual testing exercises the Tesseract **candidate** via the evaluation
scripts / `DOCURA_OCR_ENGINE=tesseract`, never production auto-fill.

---

### Reproduce
```bash
cd backend
.venv/Scripts/python.exe -m scripts.s6_validate --root var/s6_corpus
.venv/Scripts/python.exe -m scripts.s6_evaluate --root var/s6_corpus --engine tesseract --split held_out --write
```
(The config/preprocessing variants in §6 were run via an eval-only script that injects a Pillow
preprocessing reader / `pdf_scale` into the existing `TesseractExtractor`; nothing in `app/` or
`ocr_candidates/` was modified.)

### Best-supported next action (strictly from the evidence)
1. **Reconcile annotation vs metric granularity first** — it is the actual cause of the 75% miss,
   not OCR. Either (a) annotate expected text at the granularity the metric matches (the OCR line as
   emitted), or (b) make a *methodology* decision (D-02 owner) to add a containment-based field-read
   metric alongside the strict one. Do this before reading anything into accuracy numbers.
2. **Then expand the corpus** — multiple real documents per MVP type, multiple subjects, realistic
   degradation — because engine selection and the BR-001 threshold (AR-AST-008) cannot be justified
   on 3 single-subject documents regardless of the metric.
No production engine selection, no threshold, and no preprocessing adoption are warranted yet.
