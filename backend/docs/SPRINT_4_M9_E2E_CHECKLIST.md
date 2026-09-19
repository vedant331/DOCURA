# DOCURA — Sprint 4 M9 End-to-End Integration: Manual Checklist

This is the manual demonstration of the MVP journey against the controlled mock form.
Each step records the **expected result** and, where a **frozen decision** blocks a real
result, says so explicitly. A visible "not available yet" state is the correct outcome —
never a fabricated success (M9 §15).

## Setup

1. **Backend** — from `backend/`: start the API on `http://127.0.0.1:8000`
   (e.g. `uvicorn app.main:app --reload`). A Postgres DB per `backend/config` must be up.
2. **Frontend** — from `frontend/`: `npm run dev`, open the printed URL. `VITE_API_BASE`
   must point at the backend (default `http://127.0.0.1:8000`).
3. **Extension** — load `extension/` as an unpacked extension in Chrome
   (`chrome://extensions` → Developer mode → Load unpacked). It already lists
   `http://127.0.0.1:8000/*` in `host_permissions`.
4. **Mock form** — serve `extension/test/fixtures/mock-form.html` over http so the content
   script's module imports work cleanly, e.g. from `extension/test/fixtures/`:
   `python -m http.server 8080` then open `http://127.0.0.1:8080/mock-form.html`.
   (Opening via `file://` also works only if the extension has "Allow access to file URLs".)

## Blocker legend

- **OK** — works end to end with real data.
- **OK (honest seam)** — works and correctly shows an honest "not available" / "nothing
  done" state; this is a pass, not a failure.
- **BLOCKED: S-6** — real OCR cannot be selected until the S-6 held-out evaluation runs
  (D-02). No extraction → the structured record is empty.
- **BLOCKED: G-12/G-13** — no approved form-field→canonical-attribute mapping exists
  (mock-form L-INFO is owed), so no field maps, and nothing can be filled/matched even if
  the record were populated.

## Checklist

| # | Step | Expected result | Status |
|---|------|-----------------|--------|
| 1 | Sign in (web app) | Authenticated app opens at the Command Center | **OK** |
| 2 | Open Command Center | Landing surface; document state shown | **OK** |
| 3 | Upload a supported document (PDF/JPG/PNG) | Appears in vault, status `queued`/`processing` | **OK** |
| 4 | Verify vault state | Document listed with type, size, date, status | **OK** |
| 5 | Verify processing state | Real backend status shown (no invented %); likely settles to `failed`/`needs_review` with a reason | **OK** — processing runs; extraction content is **BLOCKED: S-6** |
| 6 | Verify extracted/structured info | My Record / Document Detail show extracted attributes if any | **OK (honest seam)** — record is empty (**BLOCKED: S-6**); UI shows "no extracted information yet" |
| 7 | Open the controlled mock form | `mock-form.html` loads with all seven field types | **OK** |
| 8 | Activate extension explicitly (popup → Activate) | Backend `POST /form-sessions` creates a session; green in-page banner appears; toolbar badge shows **ON** | **OK** |
| 9 | Verify active indicator | Green "DOCURA is active" banner + popup shows Active + session id | **OK** |
| 10 | Verify form detection | In page devtools console: `globalThis.__docuraForms` lists the detected form and fields | **OK** |
| 11 | Verify field enumeration | `__docuraForms.forms[0].fields` enumerates all 14 fillable fields (submit excluded) with types, required flags, constraints | **OK** |
| 12 | Verify readiness summary | `globalThis.__docuraReadiness.summary` shows total=14, every field `unknown`, `documentsRequired>=1`, `ready:false` | **OK (honest seam)** — nothing maps (**BLOCKED: G-12/G-13**) |
| 13 | Verify safe information mapping | `globalThis.__docuraRetrieval` shows every field `unknown`; no value chosen | **OK (honest seam)** — **BLOCKED: G-12/G-13** |
| 14 | Verify automatic fill where supported | No field is auto-filled anywhere on the page | **OK (honest seam)** — no approved mapping/threshold + empty record; nothing is filled. Correct safe behaviour. |
| 15 | Verify unknown field remains untouched | All fields remain untouched (status `unknown`) | **OK** |
| 16 | Verify ambiguity asks the user | The duplicated `field_ambiguous` pair is detected; `__docuraRetrieval` would surface candidates — never auto-choose | **OK (honest seam)** — no mapping, so it stays `unknown`; nothing is auto-resolved. **BLOCKED: G-12/G-13** |
| 17 | Verify conflict does not auto-resolve | No value is selected among competing observations | **OK (honest seam)** — record empty; nothing resolved. **BLOCKED: S-6** |
| 18 | Verify document matching | `globalThis.__docuraMatching` shows the file field as `unresolved` | **OK (honest seam)** — no approved matcher; nothing auto-selected. **BLOCKED: G-12/G-13** |
| 19 | Verify document constraints/preparation | The file field's `accept` + `data-max-size` constraints are captured in detection | **OK** (constraints read); preparation is **BLOCKED: G-12/G-13** |
| 20 | Verify sensitive approval | `globalThis.__docuraReview` shows nothing `disclosable` (no tier assigned); no blanket approval possible | **OK (honest seam)** — tiers unassigned (G-14). Nothing is disclosed. |
| 21 | Verify declaration remains untouched | `field_declaration` checkbox is never ticked by DOCURA | **OK** — DOCURA never operates a declaration (BR-006) |
| 22 | Verify final review (web app) | Open the Form Session → Review tab for this session | **OK (honest seam)** — web shows session state + hand-back; per-field review lives in the extension (not bridged) and says so |
| 23 | Verify outstanding blockers | Review does not falsely report "0 blockers"; shows "blockers tracked in session" when it cannot enumerate them | **OK** |
| 24 | Hand back (web app Form Session → "Hand back to me") | Backend `POST /form-sessions/{id}/hand-back`; session state → `handed_back` | **OK** |
| 25 | Verify DOCURA does not submit | No submit control is ever operated by DOCURA, on the form or elsewhere | **OK** — by construction; there is no submit code path |

## What a reviewer should conclude

- **Real integration that works:** authentication, document upload → vault → web display,
  explicit activation → backend session → web visibility, session lifecycle (activate /
  stop / hand-back), owner-scoped isolation, read-only audit, and value-free form detection
  with constraint/required capture.
- **Blocked by frozen decisions (correctly, not hidden):** extraction content (S-6), and
  all field interpretation / fill / matching / preparation / sensitive disclosure
  (G-12/G-13, G-14, G-20). The pipeline runs end to end and **safely does nothing** it is
  not yet licensed to do.
- **No fabrication anywhere:** no OCR result, confidence, mapping, match, approval, fill, or
  submission is invented.
