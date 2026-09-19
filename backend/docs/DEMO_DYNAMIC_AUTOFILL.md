# DOCURA — Dynamic Document → Form Autofill (LOCAL DEMO)

> **Dynamic demo mode demonstrates the intended DOCURA interaction. Production attribute release
> and OCR selection remain subject to the project's existing governance/evaluation decisions.**

This demo shows the whole product loop on a local machine:

```
upload PDF → OCR (Tesseract) → dynamic key/value extraction → structured record
   → open a realistic web form → interpret each field by its LABEL (not its id/name)
   → look up the record value → safety check → fill / ask / approval / untouched
```

It is built **entirely on the existing pipeline** — no new architecture. It is enabled by two
explicit dev/evaluation flags and is **off by default**; production behaviour is unchanged.

## What the demo adds (all behind flags, all reversible)

| Piece | Where | Flag |
| --- | --- | --- |
| Real OCR on uploads | `build_document_extractor` (M23) | `DOCURA_OCR_ENGINE=tesseract` |
| Dynamic key/value extraction of 8 common attributes | `DemoFieldExtractor` + `canonical_attributes.demo.toml` | `DOCURA_DEMO_MODE=true` |
| Dynamic web-field interpretation by label + safe fill | extension `src/demo.js` | `DEMO_MODE` in `src/demo.js` |

Demo attributes (DEMO only — **not** G-13-released): `person.full_name`, `person.date_of_birth`,
`person.age`, `person.email`, `person.phone`, `person.address`, `identity.pan_number`,
`identity.aadhaar_number`. Sensitivity (demo default): `date_of_birth`, `pan_number`,
`aadhaar_number` are **sensitive** (require per-disclosure approval); the rest are routine.

## How it works (reuses existing seams)

- **Extraction** — the OCR `ExtractionResult` (M20/M21) is fed to `DemoFieldExtractor`, which
  finds labelled key/value pairs (`Label: Value`, `Label - Value`, `Label Value`, and a
  label-only line followed by its value) using the **data-driven synonym table** in
  `canonical_attributes.demo.toml`. Exact alias match only — no fuzzy guessing. Dates normalise
  to ISO. Values come from OCR; nothing is hard-coded. Each becomes an `AttributeObservation`
  through the existing service, preserving `document → run → page → block/region → confidence`.
- **Interpretation** — the extension reads M17 semantic metadata (label, aria-label,
  aria-labelledby, placeholder, title, name, id) and resolves meaning with the demo synonym
  vocabulary in `src/demo.js`. Meaning comes from the **accessible label**, so meaningless
  ids/names (`name="z77"`) still resolve. Ambiguous/unknown → untouched (no guessing).
- **Safety** — the existing `computeReview`/`computeFillPlan` decide per field:
  routine+available → **fill**; sensitive → **approval required** (then fill after explicit,
  exact-scope, one-time approval); unknown → **untouched**; declaration/consent → **never**;
  record ambiguity/conflict → **ask**; submit → **never**. Audit records each action **without
  the value**.

Derived age: **not synthesised.** An `AttributeObservation` represents a value *read from a
document*; computing age from DOB and storing it would misrepresent a derived value as a document
fact (and needs a schema/governance change out of scope here). So `person.age` is populated only
when the document states it explicitly; otherwise it is simply unavailable.

## Manual demo — exact steps

1. **Start PostgreSQL:** from `backend/`, `docker compose up -d` (wait until healthy).
2. **Configure demo mode** in `backend/.env`:
   ```
   DOCURA_OCR_ENGINE=tesseract
   DOCURA_DEMO_MODE=true
   ```
   (Candidate deps must be installed in the venv: `pip install pytesseract Pillow pypdfium2`
   plus the Tesseract binary on PATH.)
3. **Start the backend API:** from `backend/`, `.venv/Scripts/python.exe -m app.main`.
4. **Start the processing worker** (separate process — required, see M23 debug):
   `.venv/Scripts/python.exe -m app.worker`.
5. **Enable the extension demo:** set `export const DEMO_MODE = true;` in
   `extension/src/demo.js`, then load the unpacked extension (`chrome://extensions` → Load
   unpacked → `extension/`).
6. **Start the frontend:** from `frontend/`, `npm run dev`.
7. **Log in** (or register) in the frontend.
8. **Upload** a personal-information PDF whose fields are labelled (e.g. `Full Name: …`,
   `Date of Birth: …`, `PAN Number: …`, `Aadhaar Number: …`, `Email: …`, `Phone: …`,
   `Address: …`, `Age: …`). Wait for status **READY** (the worker processes it).
9. **Open My Record** — confirm the extracted attributes appear with provenance (document, page,
   region, confidence).
10. **Open the realistic form:** `extension/test/fixtures/demo-realistic-form.html` (its field
    ids/names are deliberately meaningless; meaning is only in the labels).
11. **Activate DOCURA** on that page (extension popup → Activate).
12. **Observe:** routine fields (name, email, phone, address) fill automatically; sensitive
    fields (DOB, PAN, Aadhaar) show as **approval required**; the unknown field
    ("Favourite Colour") and the declaration checkbox stay **untouched**.
13. **Approve** a sensitive field in the popup (one at a time).
14. **Verify** the sensitive value fills **only after** its approval, and only that exact field.
15. **Verify** no submit is ever operated and declarations are never touched.
16. **Check Activity / audit** — actions are recorded as field handle + canonical id (+ owned
    source document for a fill), **never** the value.

## Rollback / disable

- Backend: remove `DOCURA_OCR_ENGINE` and `DOCURA_DEMO_MODE` from `.env` (or set demo false) and
  restart the API + worker → back to `UnconfiguredExtractor` and the 2-attribute controlled
  extractor.
- Extension: set `DEMO_MODE = false` in `src/demo.js` and reload → back to controlled-form-only
  behaviour.

## Production safety

- **Default is unchanged.** `build_document_extractor()` → `UnconfiguredExtractor`;
  `build_field_extractor()` → the controlled 2-attribute extractor; the extension resolves only
  the controlled form. None of the demo flags is set by default.
- The demo attributes are **not production-released** (the demo vocabulary is `releasable=false`,
  `demo_only=true`), the demo sensitivity tiers are demo defaults (not the A-5/G-14 user-set
  tiers), and no OCR engine is selected for production.

## What remains subject to governance / S-6

Production attribute release (G-13/G-14/G-15), OCR engine selection and thresholds (S-6 / D-02 /
AR-AST-008), and the real-portal field-interpretation ruleset. The demo shows the *intended
interaction*; it does not resolve those decisions.

## Tests

- Backend `tests/test_demo_extraction.py`: dynamic extraction of all 8 attributes from OCR
  (synthetic + real Tesseract), synonyms/separators, label-only+value lines, bad-date rejection,
  provenance/confidence, and that the builder uses the demo extractor **only** under demo mode.
- Extension `test/demo.test.js`: label-driven resolution over **meaningless ids/names**, tier +
  declaration classification, and the full safety decision set (routine fill, sensitive approval
  then fill, unknown/declaration untouched, ambiguity → ask, audit value-free) — driven through
  the same `computeFillPlan` the content script uses.
- Fixture: `extension/test/fixtures/demo-realistic-form.html`.

Full suite status: backend **542 passed / 0 skipped** (PostgreSQL), extension **174 passed**,
frontend **44 passed** + typecheck clean; ruff + mypy clean.
