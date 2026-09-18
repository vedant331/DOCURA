# DOCURA — Sprint 4 M20: Self-Hosted OCR Candidate Adapter (smoke test only)

| Field | Value |
| --- | --- |
| Type | Adapter / smoke-test milestone (NOT engine selection) |
| Candidate | **Tesseract** (via `pytesseract` + `Pillow`) — technical smoke testing only |
| Production engine selected | **No.** Selection remains blocked on S-6 (D-02 / AR-AST-008 / M14). |
| Production extractor | **Unchanged — `UnconfiguredExtractor`.** `build_document_extractor` still returns it. |
| Code changed | `ocr_candidates/` (new, outside `app`), `app/evaluation/engines.py` (lazy candidate wiring), `pyproject.toml` (pytest `pythonpath`, mypy config), tests + this doc |
| Verification | ruff clean · mypy clean (78 files) · **pytest 490 passed / 1 skipped** with PostgreSQL · single Alembic head `d4e5f6a7b8c9` |
| Not committed | Per standing rule — the user commits. |

> **Candidate used for technical smoke testing only; production selection remains blocked on S-6.**

## 1. What this milestone is (and is not)

M14 concluded S-6 is **BLOCKED**: no held-out corpus of real, consented, imperfect documents
exists, so no engine may be evaluated or selected and no threshold may be set. M19 built the
evaluation harness (corpus model, validator, held-out protection, runner, metrics) with nothing
real to run.

M20 fills the *last mechanical gap*: it proves the harness can invoke a **real** OCR engine
behind the existing `DocumentExtractor` seam. It implements **one** candidate adapter
(Tesseract) and exercises `document → adapter → ExtractionResult`.

It is **not** engine selection. A working adapter is evidence that the seam can carry a real
engine — nothing about whether Tesseract is *good enough*. That judgement needs the S-6 corpus
and the D-02 evaluation, which do not exist.

## 2. Candidate choice

From the M14 candidate list (`app.evaluation.engines.CANDIDATE_ENGINES = tesseract, paddleocr,
easyocr, doctr`), **Tesseract** was chosen for the adapter because it is the lightest engine
that satisfies the seam's needs and the privacy constraint:

- self-hosted / offline, Apache-2.0 (no cloud, no vendor consent needed — §7 / D-02 §5.5);
- word-level bounding boxes **and** per-word confidence (feeds `TextRegion` + `TextBlock.confidence`);
- pure-Python client (`pytesseract`) shelling out to a local binary — no `torch`/`paddle`
  (EasyOCR/PaddleOCR/docTR each pull heavyweight ML runtimes).

This is an **adapter-implementation** choice, not a production selection. PaddleOCR/docTR may
still win the eventual S-6 evaluation; adding their adapters later is the same shape of change.

## 3. Architecture

```
ocr_candidates/                         # NEW top-level package, DELIBERATELY outside app/
  __init__.py
  tesseract_adapter.py                  # the only place pytesseract/Pillow is imported

app/evaluation/engines.py               # build_engine("tesseract") → adapter, lazily imported
app/services/extraction.py              # UNCHANGED seam + UnconfiguredExtractor (production)
```

Why outside `app/`: `app/services/extraction.py` owns the invariant *"no engine may be imported
outside this module,"* enforced by three guard tests in `tests/test_extraction.py`
(no OCR provider imported under `app`, no OCR library declared as a dependency, only
`extraction.py` names a concrete extractor). A candidate adapter must import an OCR library, so
it cannot live under `app/`. Keeping it in a sibling `ocr_candidates/` package satisfies every
guard and keeps engine knowledge fully isolated. The package is dev/eval-only: it is not in
`[tool.setuptools.packages.find] include`, so it is never shipped, and nothing under `app`
imports it except one **lazy, function-level** import inside `build_engine`.

## 4. Extraction contract

The adapter implements the existing `DocumentExtractor` Protocol and returns the existing models
— no second abstraction:

- `name = "tesseract"`, `version` = the installed Tesseract version (or `"unknown"`/`"stub"`).
- `is_available()` — True only when `pytesseract` imports **and** the Tesseract binary answers
  `get_tesseract_version()` (or when a test `word_reader` is injected). It lets a caller tell
  "not installed" from "extraction failed" without provoking an exception.
- `extract(source, *, content_type)` → `ExtractionResult` with one `ExtractedPage`, whose
  `TextBlock`s carry text, a page-relative `TextRegion`, and confidence.

Two seams keep it testable and isolated:

- `result_from_words(...)` — a **pure** mapping from engine word-boxes to `ExtractionResult`
  (pixels → page-relative fractions, confidence 0..100 → 0..1, non-word/-1 rows dropped, boxes
  clamped to the page). No OCR dependency, so the contract is unit-tested without the binary.
- `word_reader` — an optional injected callable standing in for the real `pytesseract` call, so
  the adapter (and the M19 runner driving it) run deterministically in CI without Tesseract.

## 5. Configuration

No production default changes. Production extraction is wired in `app/main` via
`build_document_extractor(settings)` → `UnconfiguredExtractor` (unchanged). The candidate is
reachable **only** through the evaluation/dev path `app.evaluation.engines.build_engine(name,
settings)`:

- `build_engine("unconfigured", …)` → the production plug point (always-failing).
- `build_engine("tesseract", …)` → the adapter **iff its dependency is installed**; otherwise
  `EngineNotInstalledError`. It never silently degrades to a working-looking engine.
- every other candidate name → `EngineNotInstalledError` (unchanged).

There is no environment switch that activates OCR in production. Installing `pytesseract` +
Tesseract only affects the evaluation/dev builder and the smoke tests.

## 6. Input handling

Tesseract reads images. The adapter accepts `image/png` and `image/jpeg` (plus `tiff`), the
formats Tesseract handles directly. **PDF is deliberately unsupported**: Tesseract does not
rasterize PDFs, and adding that would mean another system dependency (poppler/pdf2image), out of
scope for a smoke adapter. A PDF (or any other type) is an honest `DocumentExtractionError`, not
a silent empty result. One image is modelled as one page (`FR-OCR-008` shape preserved);
multi-page PDF handling is future work behind the same seam.

The seam is read-only over the caller-owned stream; the original file is never modified
(`FR-OCR-009`).

## 7. Failure semantics

Every failure path converts to the seam's existing `DocumentExtractionError` (a
`ServiceUnavailableError`; `BR-016` "do nothing rather than proceed"):

| Situation | Behaviour |
| --- | --- |
| `pytesseract`/`Pillow` not installed | `DocumentExtractionError` ("adapter is not installed") |
| unsupported content type (e.g. PDF) | `DocumentExtractionError` (images only) |
| bytes not a valid image | `DocumentExtractionError` |
| engine crash / `TesseractNotFoundError` | `DocumentExtractionError`, engine internals not echoed (`NFR-ERR-004`) |
| malformed engine output (missing columns / non-numeric) | `DocumentExtractionError` — never a silent empty success |

## 8. Privacy

- Execution is **local**: `pytesseract` runs the Tesseract **binary as a subprocess**. No cloud
  OCR, no external OCR API, no vendor.
- **No network calls** — asserted by a test that makes `socket.socket` raise during `extract`
  and confirms extraction still succeeds.
- No document text is logged. `ExtractionResult.metadata` carries only engine-neutral counts
  (`word_count`), never content or a personal value (`NFR-PRIV-007`). Error messages carry no
  document content or engine internals.

## 9. Smoke test vs S-6 evaluation

| | Technical smoke test (M20) | S-6 evaluation (blocked) |
| --- | --- | --- |
| Input | synthetic/stub, generated in-test | real, consented, imperfect documents under G-02 |
| Ground truth | trivial, to check wiring | annotated by custodians, held-out split sealed |
| Output | proves `document → adapter → ExtractionResult` | accuracy/failure/calibration metrics (D-02 §8) |
| Meaning | the seam can carry a real engine | whether an engine is good enough to select |
| Thresholds | **none set** | produced by the evaluation (BR-001, G-04) |

The M19-runner smoke test (`test_the_m19_runner_can_drive_the_candidate_adapter`) runs the
adapter through `run_evaluation` over a **synthetic** one-image corpus with an injected reader.
It checks wiring and that results stay PII-free — it is **not** an OCR score and is not S-6
evidence.

## 10. Tests (`tests/test_ocr_candidate_adapter.py`, 15 tests)

Construction & protocol conformance · pure-mapper contract (fractions, confidence scaling,
region, dropped non-words) · extract through the seam · single-image-is-one-page · realistic TSV
parsing · missing dependency · engine crash · malformed output · unsupported PDF · **no network
calls** · `build_engine("tesseract")` refuses when uninstalled · **production builder still
returns the unconfigured extractor** · M19 runner drives the adapter (PII-free) · **real
Tesseract end-to-end** (runs when installed; **skipped** in this environment — no binary).

Verification (this environment: Python 3.14, no Tesseract binary):
`ruff` clean · `mypy` clean · `pytest` **490 passed, 1 skipped** with PostgreSQL · single Alembic
head. The one skip is the real-engine test, honestly gated on `is_available()`.

## 11. Production safety check

- `build_document_extractor(settings)` returns `UnconfiguredExtractor` (`name="unconfigured"`,
  `is_available() == False`) — asserted by `test_production_builder_still_returns_the_unconfigured_extractor`
  and the existing `tests/test_extraction.py`.
- No production request path can invoke the candidate: the only wiring is
  `app.evaluation.engines.build_engine`, used by the dev CLI / tests, and it raises
  `EngineNotInstalledError` unless the operator has explicitly installed Tesseract.
- The three engine-isolation guards in `tests/test_extraction.py` still pass.

## 12. Exact prerequisites for production selection (unchanged from M14 §10)

1. **Collect the S-6 corpus** under G-02 governance (real, consented, de-identified, grouped by
   person, all candidate types, imperfect scans + failure + out-of-set cases). *The binding blocker.*
2. **Run D-02 stage 1** across ≥1 self-hosted candidate (this adapter makes Tesseract a runnable
   one; add a PaddleOCR/docTR adapter the same way) using the M19 harness; keep the held-out
   split sealed.
3. **Select the engine on evidence**, move the chosen adapter behind `build_document_extractor`,
   and set the review + automatic-action thresholds as configuration (NFR-MNT-002) from the
   observed distributions.
4. **Run stage 2** once G-12 field sets and G-14/G-15 tiers close (field calibration, BR-001).

*No production behaviour changed. No engine selected. No threshold set. No commit or push.*
