# DOCURA — Sprint 4 M22: OCR Output → Structured Record (controlled attributes)

| Field | Value |
| --- | --- |
| Type | Candidate-path capability (NOT production OCR, NOT engine selection) |
| Scope | Turn an OCR `ExtractionResult` into `AttributeObservation`s for the two approved attributes, feeding the existing current-record derivation |
| Attributes | `person.full_name` (N-TEXT) and `person.date_of_birth` (N-DATE) — **only** these |
| Production extractor | **Unchanged — `UnconfiguredExtractor`.** `build_document_extractor` still returns it. |
| Code changed | `app/services/field_extraction.py` (broadened name match + DOB extractor + composite), `ocr_candidates/tesseract_adapter.py` (line-level blocks), tests + this doc |
| Verification | ruff clean · mypy clean (80 files) · **pytest 528 passed / 0 skipped** with PostgreSQL · single Alembic head `d4e5f6a7b8c9` |
| Not committed | Per standing rule — the user commits. |

## 1. Flow

```
document → [OCR: Tesseract candidate + PDF rasterizer]        (M20/M21, candidate path)
        → ExtractionResult (pages → line blocks → regions → confidence)
        → build_extraction_run  (persist, existing extraction_store)
        → [Field extraction: ControlledFieldExtractor]        (this milestone)
        → CandidateObservation → AttributeObservation         (existing observation service)
        → current_record.build_current_record / get_current_value   (existing derivation)
```

The three layers stay distinct and are **not** collapsed: OCR produces *text*; the field
extractor decides a block's text *is* a named attribute's value; the record derives the *current*
value across a user's documents. No new observation model or record model was introduced — the
existing `AttributeObservation` and current-record derivation are reused unchanged.

## 2. Supported controlled attributes

Only the two currently released/authored attributes, read from the versioned vocabulary
(`config/vocabulary/canonical_attributes.v0.2-draft.toml`) by identifier:

- `person.full_name` (data type text, rule **N-TEXT**)
- `person.date_of_birth` (data type date, rule **N-DATE**)

No new canonical attribute is added; G-12/G-13/G-14/G-15 are untouched. Email, phone, address,
PAN, Aadhaar, age, etc. are **not** released, so no observation is ever created for them.

## 3. Enabling change: line-level OCR blocks

Raw Tesseract output is word-level; a value like "Vedant Santosh Kadam" spans several word
blocks, but `AttributeObservation` references **one** source block. So the Tesseract adapter now
aggregates words into **line-level blocks** (grouped by Tesseract's block/paragraph/line
numbering): each line's text is the space-joined words, its region is the union of the word
boxes, and its confidence is the mean of the words' OCR confidences (a measured value, never
invented). A labelled table row ("Full Name Vedant Santosh Kadam") therefore becomes one block
with one region and one provenance handle. This lives only in the candidate adapter's real OCR
path (`ocr_candidates/`); the injected test seams and production remain untouched.

## 4. Full-name extraction

`FullNameFieldExtractor` recognises `person.full_name` from a single block matching
`(full name | name) [sep?] <value>`, where the separator (`:` / `-`) is now **optional** so a
whitespace-separated table row is recognised in addition to the earlier `Name: X` / `Full Name -
X` forms. The value is the text after the label; an empty value yields nothing. It is
document-type-agnostic (the draft evidence lists the attribute across all candidate types) and
emits nothing if the vocabulary no longer defines the attribute. The value is **extracted from
the OCR result** — no expected production value is hard-coded.

## 5. Date-of-birth extraction & normalisation

`DateOfBirthFieldExtractor` recognises `person.date_of_birth` from a block matching
`date of birth [sep?] <value>` and normalises the value to canonical ISO `YYYY-MM-DD` (N-DATE).
Only two surface forms — justified by the current controlled evidence — are accepted:

- `D[D] <MonthName> YYYY` (English month names only; e.g. "24 March 2007" → `2007-03-24`)
- ISO `YYYY-MM-DD` (already canonical)

Anything else — an unsupported surface form, or a well-formed shape that is **not a real calendar
date** (e.g. "31 February 2007") — returns **no observation**. Nothing is guessed: no
locale-ambiguous DD/MM inference, no two-digit-year completion, no multilingual month parsing
(all explicitly excluded by the vocabulary's N-DATE rule). The extracted value is not hard-coded.

## 6. Provenance

Every observation keeps exact provenance through the existing model: `source_block → page → run
→ document`. The source block is the line block the value was read from, and its normalized
region (page-relative fractions) is retained, so a value is traceable back to
document → extraction run → page → block/region for later review/correction. No provenance is
discarded.

## 7. Confidence handling

Each observation carries the **source block's OCR confidence unchanged** (the line's mean
word confidence), or `None` where the engine reported none — never a fabricated number. The
architecture has no separate probabilistic field-extraction confidence (the extractor is
deterministic), so none is invented or equated with OCR confidence. No automatic-action
threshold is set, and OCR confidence is **not** converted into autofill authorization — BR-001
and the safety thresholds remain governed separately and blocked on S-6/G-04.

## 8. Ambiguity & conflict

The extractors never select between candidates. Multiple matching blocks produce multiple
candidates, stored side by side. The existing current-record derivation then:

- folds values that **agree** under the attribute's approved normalisation into one value
  (N-TEXT for names; N-DATE dates agree when they denote the same calendar date — stored ISO
  makes agreeing dates identical);
- marks the attribute **ambiguous** (value `None`, all candidates retained) when they disagree.

No newest-wins, highest-confidence-wins, or preferred-source rule was added (none is approved,
G-20). Tests cover multiple candidate names and conflicting DOBs — both are preserved.

## 9. Unsupported attributes

Lines such as Email, Phone, Address, PAN, Aadhaar, Age, or unrelated captions produce **no**
observations, because no released canonical attribute covers them. Unsupported information stays
outside the released structured record; no vocabulary entry is added.

## 10. Processing pipeline / wiring

The processing worker already accepts an injected OCR `extractor` and an optional
`field_extractor` (`app/services/processing.py`). Production (`app/worker.py`) builds
`build_document_extractor(settings)` (→ `UnconfiguredExtractor`) and `build_field_extractor()`;
because the unconfigured engine fails, **no run is produced and the field extractor never runs**
in production. The candidate path is reached only by injecting `TesseractExtractor` in
evaluation/dev/tests. `build_field_extractor()` now returns the controlled composite, which is
harmless in production (never reached) and adds no attribute. **No ordinary upload invokes
Tesseract.**

## 11. Technical test vs S-6

The integration test (`tests/test_ocr_to_record.py::TestRealOcrToRecord`) runs the **real** local
candidate (rasterize a synthetic PDF → Tesseract → record) and asserts
`person.full_name = "Vedant Santosh Kadam"`, `person.date_of_birth = "2007-03-24"`, and exact
provenance. It is explicitly labelled **NOT S-6 EVIDENCE**: the PDF is synthetic, the values are
the project's synthetic test data, and nothing sets a threshold or selects an engine. Accuracy on
real documents remains what S-6 must measure.

## 12. Privacy

Extracted personal values are not logged (production logging stays metadata-oriented; the
adapter/rasterizer log nothing about content). Tests may inspect values because their fixtures
are synthetic. All OCR is local; no OCR text is sent externally; no cloud OCR.

## 13. Production safety check

- `build_document_extractor(settings)` → `UnconfiguredExtractor` (`is_available() == False`),
  confirmed at runtime and by tests.
- No production path invokes Tesseract or the field extractor on real content (the worker's OCR
  is unconfigured → no run → no field extraction).

## 14. Tests

- `tests/test_ocr_to_record.py` (21 tests): both attributes extracted from table rows; DOB
  normalisation (supported forms); missing name / missing DOB; malformed/unsupported dates (no
  guess); multiple candidate names preserved; conflicting DOBs preserved; unsupported
  Email/Phone/Address/PAN/Aadhaar/unrelated lines produce nothing; and the DB-backed **real
  OCR → record** integration with provenance + measured confidence.
- Existing `tests/test_field_extraction.py`, `test_ocr_candidate_adapter.py`,
  `test_pdf_rasterization.py` continue to pass unchanged.

Verification: ruff clean · mypy clean (80 files) · **pytest 528 passed, 0 skipped** with
PostgreSQL · single Alembic head `d4e5f6a7b8c9`.

## 15. Remaining S-6 prerequisites (unchanged)

1. Collect the S-6 corpus under G-02 governance — the binding blocker.
2. Run D-02 stage-1 across ≥1 self-hosted candidate via the M19 harness; keep the held-out split sealed.
3. Select the engine on evidence, move the chosen adapter behind `build_document_extractor`, set
   review + automatic-action thresholds as configuration (NFR-MNT-002).
4. Run stage-2 once G-12 field sets and G-14/G-15 tiers close; a type-aware/evaluated field
   extractor then replaces the deterministic slice behind the same seam.

*No production behaviour changed. No engine selected. No threshold set. No new attribute. No commit or push.*
