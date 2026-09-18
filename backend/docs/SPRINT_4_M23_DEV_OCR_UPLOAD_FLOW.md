# DOCURA — Sprint 4 M23: Dev-Only OCR Activation for the Normal Upload Flow

> **This enables local technical testing of the OCR candidate. It does not select Tesseract as
> the production OCR engine.**

| Field | Value |
| --- | --- |
| Type | Dev/evaluation opt-in (NOT production OCR activation, NOT engine selection) |
| Configuration | `DOCURA_OCR_ENGINE` — `unconfigured` (default) or `tesseract` |
| Default / production | **`UnconfiguredExtractor`** — `build_document_extractor()` unchanged by default |
| Code changed | `app/core/config.py` (`OcrEngine` enum + `ocr_engine` field), `app/services/extraction.py` (builder honors the opt-in), tests + this doc |
| Verification | ruff clean · mypy clean (81 files) · **pytest 534 passed / 0 skipped** with PostgreSQL · single Alembic head `d4e5f6a7b8c9` |
| Not committed | Per standing rule — the user commits. |

## 1. Why this exists

M20–M22 built and proved the local OCR candidate path (Tesseract adapter, PDF rasterization,
OCR → controlled field extraction → record), but the normal document-processing worker still
runs `UnconfiguredExtractor`, so an ordinary uploaded PDF never reaches Tesseract. M23 adds a
**single, explicit, dev/evaluation-only switch** so the *existing* pipeline can run the candidate
locally for technical testing — without a second endpoint, a second pipeline, or any change to
the production default.

## 2. Configuration

One setting, following the existing `DOCURA_`-prefixed pydantic-settings convention:

```
DOCURA_OCR_ENGINE=unconfigured   # default — production posture, no engine selected
DOCURA_OCR_ENGINE=tesseract      # dev/evaluation opt-in — run the M20/M21 candidate locally
```

It is a validated enum (`app.core.config.OcrEngine`). An unrecognised value (e.g. `paddleocr`)
fails at settings load with the existing `ConfigurationError`, never a silent fallback.

## 3. Default behavior

Unset (or `unconfigured`) → `build_document_extractor()` returns `UnconfiguredExtractor`, exactly
as before. The repo `.env` does not set the variable, so the default applies in every normal run;
confirmed at runtime (`ocr_engine default = unconfigured | extractor = unconfigured`).

## 4. Normal upload flow (with the opt-in)

No new endpoint or pipeline. With `DOCURA_OCR_ENGINE=tesseract` the *existing* flow becomes:

```
POST /documents → document stored (status queued) + ProcessingJob
  → worker claims job (status processing)
  → build_document_extractor(settings) → Tesseract candidate
  → PDF rasterization (pypdfium2, local)
  → ExtractionResult (line blocks + regions + confidence)
  → persist extraction run (existing extraction_store)
  → controlled field extraction (existing seam: person.full_name, person.date_of_birth)
  → AttributeObservation (existing service)
  → current record (existing derivation)
  → status ready
```

Only the extractor the worker constructs changes; every other stage is the code that already
existed (`app/services/processing.py`, unchanged).

## 5. Tesseract candidate path

`build_document_extractor(settings)` lazily imports `ocr_candidates.tesseract_adapter` (outside
the `app` package), so no OCR-library knowledge enters the application's import surface — the
engine-isolation guards (`tests/test_extraction.py`) still hold, and only `extraction.py` names a
concrete extractor. If the opt-in is set but the candidate's dependency is not installed,
`build_document_extractor` raises `ConfigurationError` (loud, not a silent fallback).

## 6. Document status

Existing statuses only: `queued → processing → ready` on success; on a processing failure the
existing `_record_failure` path applies (retry up to `worker_max_attempts`, then `failed` with a
user-facing reason). No new status, and **no `needs_review` logic was added** — that requires the
BR-001 review threshold, which is TBD and blocked on S-6, so a successful dev run reaches `ready`,
the correct existing outcome.

## 7. Record provenance

Values flow through the normal observation chain with full provenance retained:
`document → extraction run → page → block/region → AttributeObservation → current record`. The
integration test asserts `observation.source_block.page.run.document_id == document_id`. The dev
seed script (`scripts/dev_seed_record.py`) is **not** used by this flow — the record is populated
from real OCR output.

## 8. No value hard-coding

Neither the config nor the extractor contains `"Vedant Santosh Kadam"` or `"2007-03-24"`. The
integration test authors a synthetic PDF and asserts those values come back **from OCR**; the
extraction logic is the deterministic M22 label/date extractor, which reads whatever the document
says.

## 9. Production safety

- Default `build_document_extractor()` → `UnconfiguredExtractor` (`is_available() == False`).
- `test_default_upload_does_not_invoke_tesseract`: with the default settings, a normal upload is
  processed, the document ends `failed`, and **no extraction run and no observation** exist —
  proving the default path never invokes Tesseract.
- The opt-in is the only way to reach the candidate; production selection (`build_document_extractor`
  defaulting to a real engine) remains blocked on S-6.

## 10. Privacy

Unchanged and preserved: all OCR and rasterization are local (Tesseract subprocess, PDFium
in-process); no cloud OCR, no HTTP/external OCR APIs; no extracted text or page image is logged
(the builder logs only the engine name and a reason string). Rasterized page images are in-memory
and closed deterministically (M21).

## 11. Cleanup / rollback (disable)

- **Disable:** unset `DOCURA_OCR_ENGINE` (or set it to `unconfigured`) and restart the worker/API.
  The pipeline reverts to `UnconfiguredExtractor` immediately; nothing else changes.
- No temporary rasterized images are written to disk (in-memory only). Tests author synthetic
  PDFs in-memory and use unique bytes per run to avoid dedup collisions; they use isolated test
  users and the standard DB fixtures, so there is no stale artifact or test-user pollution.

## 12. How to test manually (local dev)

1. Ensure the candidate deps are installed in the venv (out-of-band): `pip install pytesseract
   Pillow pypdfium2` and the Tesseract binary on PATH.
2. Start the stack with the opt-in, e.g. `DOCURA_OCR_ENGINE=tesseract` in the environment, then
   run the API and `python -m app.worker`.
3. `POST /documents` with a PDF, then read the document status and `GET /record/attributes` —
   `person.full_name` / `person.date_of_birth` appear when present in the document.
4. To confirm production behavior, unset the variable and repeat: uploads end `failed` (no engine)
   and the record is not populated.

## 13. S-6 limitation

This is technical testing of the candidate, not evaluation. No S-6 corpus exists, no engine is
selected, and no threshold is set. Production selection still requires: (1) the S-6 corpus under
G-02; (2) D-02 stage-1 across ≥1 candidate via the M19 harness; (3) selecting the engine on
evidence and making `build_document_extractor` default to it, with thresholds as configuration;
(4) D-02 stage-2 once G-12/G-14/G-15 close.

*No production default changed. No engine selected. No threshold set. No new attribute. No commit or push.*
