# S-6 Corpus Intake Guide (human steps)

This is the checklist for **manually supplying the one remaining S-6 input**: a consented,
de-identified, **held-out corpus of real, imperfect MVP-type documents with ground-truth
annotations** (requirement **AR-AST-008**, step3.pdf p.26). Everything else for S-6 is already
built (corpus model, ingestion, validation, held-out protection, field-correctness metrics,
engine seam, reproducible scripts).

Nothing here changes OCR behavior, enables production OCR, or sets the BR-001 threshold. Adding
this corpus is what will *let* those decisions be made later, on evidence.

> **This guide and the templates are committed. The corpus itself is NEVER committed.**
> Everything under `backend/var/` is gitignored (`backend/.gitignore` line 14). Real documents,
> annotations, and the manifest with real checksums stay on your machine only.

---

## 1. Folder structure (already scaffolded)

```
backend/var/s6_corpus/            # gitignored root — never committed
├── manifest.json                 # the machine-readable index (starts as {"version":"v0","items":[]})
├── documents/                    # source document files: <id>.<ext>  (pdf/png/jpg/jpeg)
├── annotations/                  # ground truth:          <id>.json
└── results/                      # evaluation outputs (written by scripts.s6_evaluate)
```

- One document = one file in `documents/` = one entry in `manifest.json` = (if annotated) one
  file in `annotations/`. The `id` links all three.
- Splits are a **field on each manifest item** (`train` / `development` / `held_out`), not
  separate folders — that is what lets the harness detect held-out leakage by checksum.

The `manifest.json` is normally **written for you** by the ingest command (§6); you rarely edit
it by hand.

---

## 2. What document types are needed

Use only the candidate MVP types the requirements' §7.1 lists (the harness rejects anything
else). `document_type` must be exactly one of:

`aadhaar`, `pan`, `address_proof`, `marksheet_10`, `marksheet_12`, `semester_result`,
`degree_certificate`, `photograph`, `signature`, `student_id`, `hall_ticket`, `resume`, `other`.

Aim for a handful of **real** documents per type you care about (identity/address and the
education marksheets are the highest value). S-6 decides, per type, whether extraction is
reliable enough to ship structured extraction (ASM-001) — so cover the types you want shipped.

## 3. What makes a document "real" and "imperfect"

S-6 explicitly needs **real, imperfect** documents — not clean synthetic renders. Prefer genuine
documents that were actually produced/scanned in the wild, and include realistic degradation:

- scanned (not born-digital) where possible; phone-camera photos of paper are ideal
- mild skew / rotation, uneven lighting, shadow, background noise
- lower-resolution scans, JPEG compression, mild blur
- dense vs sparse layouts, different fonts/sizes, multi-page PDFs, crop variation

Record the degradation you know about in `source_category` (free text, e.g.
`scan_lowres`, `photo_skew`, `volunteer_clean`) so results can be read per condition later.
Do **not** manufacture unrealistic damage just to add coverage.

## 4. De-identification (required)

Before a document enters `documents/`, redact anything that identifies a real person **beyond
the fields under evaluation**, unless you have explicit consent for the raw document. Practical
rule: keep the fields you will annotate legible; black-box faces, signatures, and unrelated
identifiers. Set `deidentification_status` to:

- `deidentified` — PII removed/redacted (preferred)
- `raw` — original, only if consent explicitly permits keeping it
- `not_applicable` — e.g. a `photograph`/`signature` sample with no textual PII

Never send any document to a cloud OCR API, LLM, analytics, or telemetry endpoint. S-6 runs
entirely locally.

## 5. Consent

Every real document needs a lawful basis to use it for evaluation. Set `consent_status`:

- `consented` — the person gave permission for evaluation use (preferred; keep your own record)
- `pending` — collected but consent not yet confirmed (do **not** put in `held_out`)
- `withdrawn` — consent withdrawn → remove the document; do not evaluate it
- `not_applicable` — no personal data involved

Do not use random real people's personal documents without consent.

## 6. Naming, IDs, and ingesting a document

- **`id`** must match `[A-Za-z0-9_-]+`. Convention: `<type>_<seq>`, e.g. `aadhaar_001`,
  `marksheet_10_003`. The id is the filename stem in `documents/` and `annotations/`.
- Let the ingest tool assign the file location and compute the checksum — don't copy files in by
  hand. It copies the original (never moves/alters it), rejects a duplicate id, and rejects a
  document whose checksum already exists (so the same file can't sit in two splits):

```bash
cd backend
.venv/Scripts/python.exe -m scripts.s6_ingest \
  --root var/s6_corpus --source /path/to/real_doc.pdf --id aadhaar_001 \
  --document-type aadhaar --source-category volunteer_scan \
  --consent consented --split held_out --deid deidentified --page-count 1
```

Manifest item fields (for reference; ingest fills these):

| field | meaning | allowed |
|---|---|---|
| `id` | stable id / filename stem | `[A-Za-z0-9_-]+` |
| `document_type` | §7.1 candidate type | list in §2 |
| `page_count` | pages in the document | integer ≥ 1 |
| `source_category` | provenance / degradation note | free text |
| `consent_status` | see §5 | `consented` `pending` `withdrawn` `not_applicable` |
| `annotation_status` | see §7 | `annotated` `pending` `not_applicable` |
| `split` | see §8 | `train` `development` `held_out` |
| `deidentification_status` | see §4 | `deidentified` `raw` `not_applicable` |
| `checksum_sha256` | computed by ingest | — |
| `excluded_reason` | set to skip an item without deleting it | text or omit |

## 7. Ground-truth annotations

For each document you want scored, create `annotations/<id>.json`. Copy
`docs/s6_corpus_templates/annotation.template.json`, then set `document_id` to the item id and
list every value you expect the OCR to read, **transcribed exactly as printed** on the document.
See `docs/s6_corpus_templates/annotation.example.json` for a filled illustration (synthetic
placeholders — do not copy it into `var/`).

- `text` (required): the string exactly as it appears on the page.
- `page` (required): 1-based page number.
- `canonical_identifier` (optional): tag a value with an approved attribute for per-field
  analysis. Use **only** the existing canonical vocabulary:
  `person.full_name`, `person.date_of_birth`, `person.age`, `person.email`, `person.phone`,
  `person.address`, `identity.pan_number`, `identity.aadhaar_number`.
  (`person.full_name` and `person.date_of_birth` are the production-released attributes today,
  in `config/vocabulary/canonical_attributes.v0.2-draft.toml`; the rest are demo-scope. Tag what
  you can — S-6's core metric is OCR **text** correctness, and `canonical_identifier` is optional.)
- `region` (optional): `{x, y, width, height}` as page-relative fractions (0..1) of the value's
  box, if you can mark it. The harness evaluates region *availability*, not exact geometry.

After annotating, set that item's `annotation_status` to `annotated` (re-ingest is not needed —
edit the value in `manifest.json`, or ingest with `--annotation-status annotated`). A validation
error will remind you if an `annotated` item is missing its annotation file.

## 8. Splits and sealing the held-out set

- `train` / `development` — for any tuning (engine/config/preprocessing/threshold work).
- `held_out` — the **sealed** evaluation set. Assign `--split held_out` at ingest.

Sealing rules (enforced by the harness + your discipline):
- The same document (checksum) may **not** appear in `held_out` and any other split — validation
  fails with a "held-out leakage" error.
- Tuning code paths call `items_for_tuning()`, which **refuses** to return held-out items.
- Run `scripts.s6_evaluate --split held_out` **only at the end**, once, after all tuning is done
  on `development`. Never look at held-out documents while tuning.
- A rough split guide: keep enough per type in `held_out` to be meaningful, and do all iteration
  on `development`.

## 9. What must NEVER be committed to git

- Anything under `backend/var/` — documents, annotations, `manifest.json` (it carries real
  checksums), and `results/`. It is already gitignored; do not force-add it.
- No document bytes, OCR text, or extracted PII in any committed file, log, or result artifact.
- If you keep a consent log, keep it **outside** the repo.

Committed (fine): this guide and the `docs/s6_corpus_templates/` templates (placeholders only).

## 10. Validate before you evaluate

Check a manually supplied corpus is valid — **no OCR, no threshold, read-only**:

```bash
cd backend
.venv/Scripts/python.exe -m scripts.s6_validate --root var/s6_corpus
```

It reports item counts per split/annotation status and lists **every** problem (invalid enum,
missing document file, checksum mismatch, missing annotation for an `annotated` item, duplicate
id/checksum, held-out leakage). Fix all problems until it prints `VALID`.

Pre-evaluation checklist:
- [ ] every intended document ingested (`documents/<id>.<ext>` present)
- [ ] `manifest.json` valid; every non-excluded item's checksum matches its file
- [ ] every scored document has `annotations/<id>.json` and `annotation_status: annotated`
- [ ] `consent_status` and `deidentification_status` set truthfully per item
- [ ] held-out items are genuinely unseen during tuning; no checksum crosses splits
- [ ] `scripts.s6_validate` prints `VALID`

## 11. Run S-6 (after the corpus is valid)

Tuning happens on `development`; the final measurement is the sealed `held_out` split:

```bash
cd backend
# Tesseract is the only reproducible local engine in this environment (Windows, no GPU).
.venv/Scripts/python.exe -m scripts.s6_evaluate \
  --root var/s6_corpus --engine tesseract --split development
.venv/Scripts/python.exe -m scripts.s6_evaluate \
  --root var/s6_corpus --engine tesseract --split held_out --write
```

Results (counts/rates only, no PII) are printed and, with `--write`, saved under
`var/s6_corpus/results/`. The BR-001 automatic-action threshold is still **not** set by this run
— setting it is a separate, evidence-based governance decision (AR-AST-008) that you make after
reading these measured results.
