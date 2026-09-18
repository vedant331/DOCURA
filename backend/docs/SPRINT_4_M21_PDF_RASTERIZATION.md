# DOCURA — Sprint 4 M21: PDF Rasterization for the OCR Candidate Path

| Field | Value |
| --- | --- |
| Type | Candidate-path capability (NOT production OCR, NOT engine selection) |
| PDF renderer | **pypdfium2** (bundles Google PDFium) — self-contained pip wheel, no system binary, permissive licence |
| Dependency posture | Candidate/evaluation-only, installed out-of-band, **not** declared in `pyproject.toml` |
| Production extractor | **Unchanged — `UnconfiguredExtractor`.** `build_document_extractor` still returns it. |
| Code changed | `ocr_candidates/pdf_rasterizer.py` (new), `ocr_candidates/tesseract_adapter.py` (PDF path), `pyproject.toml` (mypy override), tests + this doc |
| Verification | ruff clean · mypy clean (79 files) · **pytest 507 passed / 0 skipped** with PostgreSQL · single Alembic head `d4e5f6a7b8c9` |
| Not committed | Per standing rule — the user commits. |

## 1. Why PDF rasterization is needed

M20 gave the Tesseract candidate a working path for image inputs (PNG/JPEG/TIFF). But real
identity/education documents are frequently **scanned PDFs**, and Tesseract does not read PDFs —
it reads raster images. Without a rasterization step the candidate cannot technically process the
document type S-6 will most need. M21 adds a **local** PDF → page-image step so a PDF flows
through the *same* `DocumentExtractor` seam as an image, one `ExtractedPage` per PDF page.

This is a **technical candidate capability**, not production OCR and not engine selection.
Production still resolves to `UnconfiguredExtractor`; the S-6 held-out evaluation (D-02 /
AR-AST-008 / M14) remains the gate for selecting any engine or setting any threshold.

## 2. Flow

```
image/png · image/jpeg · image/tiff
    └─► Tesseract directly ──────────────► 1 ExtractedPage

application/pdf
    └─► pdf_rasterizer.rasterize_pdf  (pypdfium2, local, in-memory)
          └─► one PIL image per page, in page order
                └─► Tesseract per page
                      └─► result_from_pages → ExtractionResult (N ExtractedPages, ordered)
```

Modules:

- `ocr_candidates/pdf_rasterizer.py` — **only** rasterization (PDF bytes → list of page images).
  No OCR, no field interpretation, no record access, no DOM, no network. Renderer isolated here.
- `ocr_candidates/tesseract_adapter.py` — routes by content type, OCRs each page image, and maps
  to the existing result models. `_read_pages_with_tesseract` bridges rasterizer → OCR.

Both live **outside** the `app` package (the M20 boundary), imported lazily, so no OCR/renderer
knowledge enters the application's import surface (invariant in `app.services.extraction`,
enforced by `tests/test_extraction.py` and an M21 test that scans `app/` for `pypdfium2`/`pytesseract`).

## 3. Dependency decision

`pypdfium2` (and `pytesseract`/`Pillow` from M20) are **not** declared in `pyproject.toml`, in any
group. Rationale, consistent with M20:

- The whole `ocr_candidates` path is dev/evaluation-only; production never imports it.
- The engine-dependency guard `test_no_ocr_engine_is_declared_as_a_dependency` keeps OCR
  providers out of the manifest so no engine can quietly become part of the build. `pypdfium2`
  is a renderer, not an OCR provider, so it would not trip that guard — but declaring only the
  renderer while the OCR deps stay out-of-band would be inconsistent and misleading. All
  candidate dependencies are therefore installed **out-of-band** into the dev/eval `.venv`
  (`pip install pypdfium2 pytesseract Pillow` + the Tesseract binary) and imported lazily; each
  is an honest `DocumentExtractionError` when absent.
- mypy: `pypdfium2`/`pytesseract`/`PIL` are added to the `ignore_missing_imports` override (they
  ship no stubs and are undeclared). No production default or dependency changed.

## 4. Page handling

- One `ExtractedPage` per PDF page; page numbers are 1-based and strictly increasing
  (`enumerate(..., start=1)`), preserving source order (`FR-OCR-008` — one document, many pages).
- Page pixel dimensions are exposed by the rasterizer and used to normalize every bounding box to
  page-relative fractions (no engine pixel units cross the seam).
- Render scale defaults to ~2.0 (≈144 DPI) — an operational knob, not a requirement value.

## 5. Result contract

Unchanged models — `ExtractionResult` / `ExtractedPage` / `TextBlock` / `TextRegion`. No second
schema. Per page: page number, text, and `TextBlock`s with a normalized `TextRegion` and
per-word confidence where Tesseract supplies it. `metadata` carries only engine-neutral counts
(`word_count`, `page_count`), never content or a personal value (`NFR-PRIV-007`).

## 6. Error handling

Every failure converts to the existing `DocumentExtractionError` (`BR-016` — do nothing rather
than proceed); never a silent empty-but-successful result, and no PDF content in messages
(`NFR-ERR-004`):

| Situation | Behaviour |
| --- | --- |
| missing renderer (`pypdfium2`) | `DocumentExtractionError` ("rasterizer not installed") |
| missing Tesseract (`pytesseract`/binary) | `DocumentExtractionError` ("adapter not installed") |
| empty PDF (0 bytes) | `DocumentExtractionError` |
| PDF with no pages | `DocumentExtractionError` |
| malformed / encrypted / unsupported PDF | `DocumentExtractionError` (opened-for-render failure) |
| a page will not rasterize | `DocumentExtractionError`; partial images closed, not returned |
| Tesseract fails on a page | `DocumentExtractionError` (existing OCR failure path) |
| unsupported content type (e.g. `text/plain`) | `DocumentExtractionError` |

## 7. Cleanup & original integrity

- The original PDF bytes are only **read**, never modified.
- Rendering is **in-memory**: page images are PIL objects, never written to disk — so there are
  no temporary files to leak.
- Handles are closed **deterministically**: each page handle in a `finally`, the PDFium document
  in an outer `finally`, and rendered PIL images are closed by the adapter after OCR (and by the
  rasterizer if a later page fails). Covered by a test that forces a mid-render failure and
  asserts both the page and document handles were closed.
- Rasterized images are never stored as user documents.

## 8. Privacy / local-only

All rendering and OCR run locally (PDFium in-process; Tesseract as a local subprocess). No cloud
service, no HTTP, no external OCR API. Extracted text and page images are never logged. A test
makes `socket.socket` raise across a real PDF extract and confirms extraction still succeeds —
the path opens no network socket.

## 9. M19 integration

The M19 runner already dispatches `engine.extract(handle, content_type=_content_type_for(path))`;
a `.pdf` corpus document now resolves to `application/pdf` and flows through the adapter's PDF
path to the existing metrics. Proven by `test_the_m19_runner_can_drive_the_candidate_on_a_pdf_item`
(deterministic injected page reader; PII-free result asserted). This is a **wiring / smoke**
check — **not** S-6 evidence, no threshold set, no engine selected.

## 10. Technical candidate support vs production OCR

A PDF the candidate can now read is evidence the **seam can carry** rasterized PDFs — nothing
about whether Tesseract is accurate enough to select. Production document uploads do **not** hit
this path: the only wiring is `app.evaluation.engines.build_engine` (dev CLI / tests), and
production extraction stays on `UnconfiguredExtractor`.

## 11. Production safety check

- `build_document_extractor(settings)` → `UnconfiguredExtractor` (`name="unconfigured"`,
  `is_available() == False`) — asserted in both `tests/test_ocr_candidate_adapter.py` and
  `tests/test_pdf_rasterization.py`, plus the `tests/test_extraction.py` guards.
- No normal upload request invokes Tesseract or the rasterizer; both are reachable only through
  the evaluation/dev builder, which still refuses unless the operator installed the candidate.

## 12. Tests (`tests/test_pdf_rasterization.py`, 13 tests)

Rasterizer happy path (multi-page, ordered, dimensions) · empty PDF · malformed PDF · missing
renderer dependency · deterministic handle cleanup on render failure · `result_from_pages`
order/structure/confidence · adapter PDF path via injected page reader · missing Tesseract on the
PDF path · **real multi-page Tesseract end-to-end** (rasterize + OCR, order preserved) · **no
network calls** on the real PDF path · production builder still unconfigured · no `app/` module
imports the renderer/OCR · M19 runner drives the candidate on a PDF item (PII-free).

Verification (Python 3.14; Tesseract 5.5.3 + pytesseract 0.3.13 + Pillow + pypdfium2 5.13.0
installed): ruff clean · mypy clean (79 files) · **pytest 507 passed, 0 skipped** with
PostgreSQL · single Alembic head `d4e5f6a7b8c9`.

## 13. Remaining S-6 prerequisites (unchanged)

1. Collect the S-6 corpus under G-02 governance (real, consented, de-identified, grouped by
   person, all candidate types, imperfect scans + failure + out-of-set cases) — the binding blocker.
2. Run D-02 stage-1 across ≥1 self-hosted candidate via the M19 harness; keep the held-out split sealed.
3. Select the engine on evidence, move the chosen adapter behind `build_document_extractor`, set
   review + automatic-action thresholds as configuration (NFR-MNT-002).
4. Run stage-2 once G-12 field sets and G-14/G-15 tiers close.

*No production behaviour changed. No engine selected. No threshold set. No commit or push.*
