# DOCURA — Sprint 4 M19: S-6 Corpus and Evaluation Harness

| Field | Value |
| --- | --- |
| Type | Evaluation infrastructure (backend, dev/eval only) |
| Status | Corpus model, manifest, annotations, validator, ingestion, held-out protection, engine adapter contract, evaluation runner, and result format implemented. **No** OCR engine selected or installed; **no** corpus created; **no** production behaviour changed. |
| Scope | `backend/app/evaluation/` + `backend/scripts/s6_*.py`. Not wired into `app.main`. Production extraction stays on `UnconfiguredExtractor`. |

## 1. Relationship to D-02 / M14 / G-02

This milestone builds the repository infrastructure D-02 (the OCR evaluation plan) describes and
M14 confirmed was missing, so the S-6 evaluation can be run **once a real, consented,
G-02-governed corpus exists**. It reuses D-02's methodology and terminology and does not create a
second methodology. It does **not** resolve S-6: no engine is chosen, no corpus is collected, no
thresholds are set (AR-AST-008 forbids setting thresholds before the evaluation), and no evidence
is fabricated. G-02 governs how a real corpus is collected/consented; this harness only registers
and evaluates whatever governance approves.

## 2. Corpus layout

Default root `var/s6_corpus/` (`var/` is gitignored — real documents never enter source control):

```
<root>/manifest.json          # machine-readable manifest (app/evaluation/corpus.py)
<root>/documents/<id>.<ext>   # source documents (local only, never committed)
<root>/annotations/<id>.json  # ground-truth annotations
<root>/results/               # evaluation result files (runner.write_result)
```

Splits are a **manifest field** (`train | development | held_out`), not separate trees, so one
document is one file with one checksum — which is what makes held-out leakage detectable.

## 3. Manifest schema

Top level: `{ "version", "items": [ … ] }`. Each item (`CorpusItem`): `id`, `document_type`,
`page_count`, `source_category`, `consent_status`, `annotation_status`, `split`,
`deidentification_status`, `checksum_sha256`, optional `excluded_reason`. It carries **no**
document content and no unnecessary PII. `document_type` must be one of the CANDIDATE §7.1
categories — note §7.1's shipped set is TBD (S-6 decides it), so these are candidates, not an
approved set.

## 4. Annotation schema

`<root>/annotations/<id>.json`: `{ "document_id", "expected": [ { "text", "page",
"canonical_identifier"?, "region"? } ] }`. `region` (x, y, width, height page-relative fractions)
is optional — D-02 evaluates region **availability**, not geometry. `canonical_identifier` is
optional and, when present, should be a released attribute; annotation data is kept entirely
separate from the production record. Ground truth is what a document is expected to yield — not a
user's stored value.

## 5. Split rules & held-out protection (§7)

- `items_for_evaluation(corpus)` → the `held_out` split only; read by the evaluation runner.
- `items_for_tuning(corpus)` → `train` + `development`; **never** `held_out`.
- `guard_no_held_out(items)` raises `HeldOutAccessError` if a tuning/development path is handed a
  held-out item — the enforced invariant for tuning/rule/alias/threshold/provider-selection work.
- The validator flags **leakage**: the same document (checksum) appearing in `held_out` and any
  other split.

## 6. Corpus validation (§5)

`validate_corpus(corpus, root)` returns every problem found (empty = valid); `ensure_valid`
raises. It checks: required fields, valid split/type/consent/annotation/deid enums, duplicate
ids, duplicate checksums, held-out leakage, missing document files, **checksum mismatch** between
manifest and file, and missing/malformed annotations for annotated items. It fails loudly and
never silently repairs evaluation data.

## 7. Ingestion (§6)

`ingest_document(...)` (and `scripts/s6_ingest.py`) registers one document: computes its
checksum, validates governance metadata, rejects a duplicate id or checksum, **copies** (never
moves) the original into `<root>/documents/`, and records the manifest item. It is dev/eval only
— it never writes to the production document vault and never commits documents to git.

## 8. Engine adapter contract (§8)

Candidate engines run through the **existing** `DocumentExtractor` seam. `CANDIDATE_ENGINES`
lists names only (`tesseract`, `paddleocr`, `easyocr`, `doctr`). `build_engine(name)` returns
`UnconfiguredExtractor` for `unconfigured` and raises `EngineNotInstalledError` for every real
candidate — none is installed or selected in this milestone. A candidate becomes runnable only by
adding its `DocumentExtractor` adapter once S-6 and governance permit.

## 9. Evaluation runner (§9) & metrics

`run_evaluation(corpus, root, engine, ...)` validates the corpus, runs the engine over the
evaluation split, compares to ground truth, and returns an `EvaluationResult`. With
`UnconfiguredExtractor` it records honest processing failures — it never manufactures OCR output.
Metrics (`metrics.py`, following D-02 §8.2, measured values only): field exact-match accuracy,
normalized field accuracy, missing-field rate, region availability, page success rate, and
processing failure rate — overall and per document type. `incorrect_field_rate`,
`classification_accuracy`, and `confidence_calibration` are reported as `None` (TBD) because they
need a field-extractor / classifier / engine confidences (D-02 §19 stage 2). **No target
thresholds are invented.**

## 10. Result format (§10)

`EvaluationResult`: `run_id`, `corpus_version`, `split`, `engine_name`, `engine_version`,
`config_id`, `timestamp`, `document_count`, `page_count`, `metrics`, `per_document` (counts + ids
only — never extracted text or values), `failures`, `missing_or_invalid_annotations`,
`environment` (python version, platform, engine). Persisted under `<root>/results/`. Tests assert
the serialized result contains no expected/extracted value (PII-free).

## 11. Privacy / security (§11)

Corpus data stays local under `var/` (gitignored); no production storage; no external/cloud OCR;
no external API calls; documents never committed; results and logs carry counts/ids, not text.
Cloud OCR remains excluded unless governance explicitly changes that.

## 12. What this milestone does NOT decide

It does not select or install an OCR engine, create or collect a corpus, set any threshold,
classify documents, add any canonical attribute, change G-13/G-14/G-15, or alter production
extraction. Synthetic structural fixtures in the tests are harness tests, **not** S-6 evidence.

## 13. Exact prerequisites for production OCR implementation

1. Collect a real, consented, **G-02-governed** corpus and ingest it (splits sealed).
2. Add a `DocumentExtractor` adapter for ≥1 candidate engine.
3. Run `run_evaluation` over the held-out split; record results.
4. Select an engine and set the review + automatic-action thresholds **as configuration**, on the
   evidence (NFR-MNT-002; AR-AST-008; BR-001).
5. Wire the selected engine in `build_document_extractor` (the existing plug point). Only then
   does production leave `UnconfiguredExtractor`. Stage-2 field metrics additionally require G-12
   field sets and G-14/G-15.
