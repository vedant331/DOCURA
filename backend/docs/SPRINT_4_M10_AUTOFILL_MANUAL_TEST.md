# DOCURA — Sprint 4 M10 Safe Autofill: Manual Test

Proves the contract **canonical attribute → approved mapping → interpretation → policy →
real DOM fill**, end to end, for `person.full_name`. No OCR, no AI (M10 §18/§19).

## Setup

1. **Backend** on `http://127.0.0.1:8000` (`uvicorn app.main:app --reload`) with its Postgres up.
2. **Frontend** (`npm run dev`) — used to create the account and see the record.
3. **Extension** — load `extension/` unpacked in Chrome.
4. **Mock form** — serve the M10 fixture over http, e.g. from `extension/test/fixtures/`:
   `python -m http.server 8080` → open `http://127.0.0.1:8080/mock-form-m10.html`.
5. **A `person.full_name` value on the test user's record.** OCR is still blocked (S-6), so seed
   it as a **test DB state only** (never production seed data): insert an extraction run +
   `person.full_name` observation for the user, exactly as `backend/tests/test_record_api.py`
   (`test_authenticated_user_retrieves_full_name_with_provenance`) constructs it. Confirm via the
   web app's **My Record** page, or `GET /record/attributes` with the user's token.

## Scenario A — user HAS data (the headline path)

1. Sign into the extension popup (same account).
2. Open `mock-form-m10.html`.
3. Click **Activate on this page** → green banner + badge **ON**; a backend form session is created.
4. The **Full name** field (`#full_name`) is **automatically filled** with the record value
   (green outline). Verify in devtools: `document.getElementById('full_name').value` equals it.
5. Provenance is attached: `#full_name` carries `data-docura-filled`, `data-docura-attribute`
   (`person.full_name`), `data-docura-source-document`; `globalThis.__docuraFills` lists the fill
   with its source document/run/page.
6. The **declaration** checkbox (`#field_declaration`) is **unticked** and untouched.
7. The **unknown** field (`#unknown_text`) and the **ambiguous** pair are **empty/untouched**.
8. Click **Stop DOCURA** → banner/badge gone; `globalThis.__docuraFills`/`__docuraWatcher` are
   `null`. The value DOCURA placed is **left in the field** (EC-017) — stop clears DOCURA's state,
   not your form.

## Scenario B — user has NO data

1. Use a user whose record has no `person.full_name` (or an empty record).
2. Open the form, Activate.
3. **Full name is NOT filled** (empty, no outline). `globalThis.__docuraFillPlan` shows the
   field `action: "unavailable"`; `__docuraFills` is empty.
4. Nothing is guessed or faked. Direct the user to upload documents (web app → Documents).

> **M12-D3 update.** The fixture now also has a **Date of birth** field (`#date_of_birth` → `person.date_of_birth`), which is **consent-gated** (G-15 default). Seed `person.date_of_birth` in the test record and it behaves exactly like the sensitive field below: not auto-filled, appears in the popup's approval list, fills only after a one-time approval. So Scenario C's popup may list two items (`sensitive_full_name` and `date_of_birth`); approving one does not approve the other.

## Scenario C — sensitive field (approval gate)

1. With a `person.full_name` value present, open the form and Activate.
2. The **sensitive** field (`#sensitive_full_name`) is **NOT auto-filled**; its plan entry is
   `approval_required`.
3. Open the extension popup → **Approve disclosure** lists `person.full_name → sensitive_full_name`.
4. Click **Approve once** → only that field fills.
5. Confirm the approval did **not** carry: re-activating a fresh session, or a different field/value,
   requires approval again (the ledger is per-session, one-time, exact-scope — BR-005/BR-007).

## What proves the acceptance criteria

- **A** Full name travels backend record → extension → real DOM field. **B** no-data → honest
  unavailable. **C** unknown untouched. **D** ambiguous not auto-filled. **E** conflict not
  auto-resolved. **F** sensitive requires explicit one-time approval. **G** declaration untouched.
  **H** provenance on the filled field. **I** record is token-scoped (backend enforces ownership).
  **J** no OCR/AI introduced.
