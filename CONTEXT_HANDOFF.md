# DOCURA — Context Handoff (Sprint 4, through M19)

Self-contained handoff for a fresh Claude session. Read this + `TODO.md` + `DECISIONS.md` +
`STATE.json` and you can continue without the prior conversation. Companion docs live in
`backend/docs/` (SPRINT_4_*.md) and `extension/docs/` (SPRINT_4_M16/M17/M18*.md).

## 0. TL;DR of current state

- Three-part product: **backend** (FastAPI + async SQLAlchemy + PostgreSQL + Alembic),
  **frontend** (React + Vite + TypeScript), **browser extension** (Manifest V3, vanilla ES
  modules, zero runtime deps).
- Tests currently green: **backend 476 passed / 0 skipped** with PostgreSQL; **extension 167
  passed** (`node --test`); **frontend 44 passed** + typecheck clean.
- **Real OCR is intentionally BLOCKED** (study S-6): no engine selected, no corpus. Production
  extraction uses `UnconfiguredExtractor` (fails honestly). Everything downstream of extraction
  is built and works, fed by a dev test-record seed.
- Only **two** canonical attributes exist: `person.full_name` (approved, auto-fill) and
  `person.date_of_birth` (authored M12, consent-gated). **Do not add more** (governance-blocked).
- **HEAD = `d68ce15`** ("feat: add S6 corpus and evaluation harness"). **There is uncommitted
  work in the working tree** (M9 action endpoint, M12 vocab v0.2 + repoint, several docs). See §8.
- Standing rule every milestone used: **do not commit or push** unless the user explicitly says so.

## 1. Project objective

DOCURA is a personal document-intelligence MVP. A user uploads their identity/education
documents; DOCURA extracts structured information (canonical attributes with provenance +
confidence) into an authoritative per-user **record**; a browser extension then, on an
explicitly activated form, **safely auto-fills** form fields from that record — filling routine
approved fields automatically, gating sensitive ones behind one-time per-disclosure approval,
leaving unknown/ambiguous/conflicting/declaration fields untouched, and **never submitting** the
form (control is handed back to the user). The backend is the source of truth; the extension is
the execution surface; the frontend is the user's web app (vault, record, activity, settings,
form-session views).

The MVP is demonstrated against a **controlled mock MCA-style form** (team-constructed).

## 2. Architecture

### Backend (`backend/`)
- FastAPI app (`app/main.py`, `create_app`), routers in `app/api/`, services in `app/services/`,
  ORM models in `app/db/models.py`, Pydantic schemas in `app/schemas/`, errors in
  `app/core/errors.py` (each `DocuraError` carries an HTTP `status_code`, problem+json).
- Async SQLAlchemy over PostgreSQL (native UUID). Alembic migrations; **single head
  `d4e5f6a7b8c9`** (no new migrations were needed across M9–M19).
- Durable document processing: `processing_jobs` table + worker (one job per document).
- **Extractor seam** (`app/services/extraction.py`): `DocumentExtractor` Protocol +
  `TextRegion/TextBlock/ExtractedPage/ExtractionResult` + `UnconfiguredExtractor` +
  `build_document_extractor(settings)` (the ONLY plug point; returns `UnconfiguredExtractor`
  today). **Invariant, enforced by `tests/test_extraction.py`: only `extraction.py` may name a
  concrete extractor** — no other `app/**` file may contain the string `UnconfiguredExtractor`.
- Record derivation (`app/services/current_record.py`): folds observations across extraction
  runs into current values with states **available / ambiguous / conflict** (conflict is
  surfaced, never auto-resolved).
- Canonical vocabulary config (product-owned): `backend/config/vocabulary/` — current version
  `canonical_attributes.v0.2-draft.toml` (2 entries; `releasable = false`). Loaded by
  `current_record.py` and `field_extraction.py`.
- Ownership: every user-owned query filters by `user_id` in the WHERE clause (NFR-SEC-003);
  404s are oracle-avoiding.

### Backend HTTP API (all authenticated + owner-scoped)
- `POST /auth/{register,login,logout}`, `GET/POST /auth/sessions`, `/auth/sessions/revoke-all`,
  `/auth/password-reset/{request,confirm}`; `GET /users/me`.
- `GET/POST/DELETE /documents`, `…/{id}`, `…/{id}/content`, `…/{id}/reprocess`,
  `GET /documents/limits`.
- `GET /record/attributes`, `GET /record/attributes/{canonical_identifier}`.
- `POST/GET /form-sessions`, `GET …/{id}`, `POST …/{id}/hand-back`, `POST …/{id}/stop`,
  `GET …/{id}/actions`, and **`POST …/{id}/actions`** (M9/M15 — record an in-session action;
  owner-scoped, ACTIVE-session-only, in-session action types only, validated refs, no values).

### Extension (`extension/`, Manifest V3)
Pipeline (all in the isolated content-script world; token stays in the service worker):
```
detect.js (value-free field metadata incl. M17 label/aria/placeholder/title)
  → interpret.js (M18 provider architecture: interpretField → resolved|ambiguous|unknown)
  → mapping.js (resolveField = meaning; fieldAutomation = policy; isControlledForm = boundary)
  → retrieval.js (does the record hold that attribute's value?)
  → autofill.js (computeFillPlan → applyFillPlan: real DOM writes for approved routine fields;
    approval-gated for sensitive; provenance data-attrs; audit-action builders)
  → content.js (wires it; fetches record via worker; runs fills; reports audit actions;
    popup-driven one-time sensitive approval)
```
- `background.js` (service worker): holds the bearer token in `chrome.storage.session`
  (never exposed to the page); handles popup + content messages: getState, signIn, signOut,
  activate, stop, getRecord (token-scoped fetch of `/record/attributes`), reportPending,
  approve, recordAction (whitelisted → `POST …/actions`).
- `popup.html`/`popup.js`: sign-in, activate/stop, and a "Approve disclosure — one field at a
  time" section for sensitive fields.
- `api.js`: login/me/logout/createSession/stopSession/getRecord/recordAction.
- Tests: Node's built-in `node --test`, hand-rolled DOM fakes, **zero deps**.

### Frontend (`frontend/`)
React + Vite + TS. Auth + AppShell + Command Center + Documents (+ detail) + My Record +
Activity + Settings + Form-session pages (readiness/review/approval). Reads the backend API;
shows honest "not connected" seams where the backend can't provide data. Scripts: `npm test`
(vitest), `npm run typecheck` (== lint, `tsc --noEmit`), `npm run build`, `npm run dev`.

## 3. Milestone history (what was implemented)

- **M9** — Integration audit + first backend seam for the extension to record actions
  (`POST /form-sessions/{id}/actions`). Frontend E2E checklist (`SPRINT_4_M9_E2E_CHECKLIST.md`).
- **M10** — Safe autofill: `person.full_name` auto-fills the controlled form from the record;
  extension record access via worker; provenance; `mock-form-m10.html`;
  `SPRINT_4_M10_AUTOFILL_MANUAL_TEST.md`.
- **M11** — Controlled-form mapping is deterministic + controlled-form-scoped (M11-D5,
  `isControlledForm("mca-mock")`); concluded expansion beyond `full_name` is blocked;
  `SPRINT_4_M11_CONTROLLED_FORM_MAPPING.md`.
- **M12** — Approved (PM: "Approve M12-D3") **G-15 default = sensitive** for the controlled MVP
  + authored **`person.date_of_birth`** as vocab **v0.2-draft** (N-DATE rule; tier TBD),
  consent-gated. Register entry D-05.16; `SPRINT_4_M12_G13_G14_G15_DECISION.md`.
- **M13** — (folder-wise part of M10/M12 autofill for DOB approval flow; validated.)
- **M14** — S-6 audit: corpus absent → BLOCKED; `SPRINT_4_M14_S6_OCR_EVALUATION.md`.
- **M15** — Extension → backend action-audit integration (records fill/approval_request/
  approval_decision; value-free; fire-and-forget). Backend endpoint verified against Postgres.
- **M16** — Generic field-interpretation foundation (`interpret.js`): alias matching,
  normalization, `resolved|ambiguous|unknown`. `extension/docs/SPRINT_4_M16_*`.
- **M17** — DOM semantic metadata capture (`detect.js`): value-free `label`, `ariaLabel`,
  `ariaLabelledBy`, `placeholder`, `title`; interpreter source priority. Browser-validated with
  `mock-form-m17-labels.html`. `extension/docs/SPRINT_4_M17_*`.
- **M18** — Interpreter **provider architecture**: `interpretField` selects a provider, runs it
  defensively, validates output against the released vocabulary (unsupported/malformed/throw/
  out-of-range → safe unknown). `extension/docs/SPRINT_4_M18_*`.
- **M19** — S-6 **corpus + evaluation harness** (`app/evaluation/`): manifest, annotations,
  validator, ingestion, held-out protection, engine adapter contract (candidate names only,
  none installed), evaluation runner + D-02 metrics + result format; CLIs
  `scripts/s6_ingest.py`, `scripts/s6_evaluate.py`. `SPRINT_4_M19_S6_CORPUS_AND_EVALUATION.md`.
- **Dev seed** — `scripts/dev_seed_record.py` seeded the manual-test user's record (see §7).

## 4. Requirements & constraints (do not violate)

- **Do NOT bypass S-6**: no OCR engine selection/installation, no fabricated extraction/eval
  evidence, no synthetic corpus presented as real. Production stays on `UnconfiguredExtractor`.
- **Do NOT add released canonical attributes** beyond `person.full_name` and
  `person.date_of_birth`. Adding any needs G-13-A authoring + a normalisation rule + a G-14/G-15
  tier + PM approval. Email/phone/gender are NOT candidates (gender explicitly rejected in G-12).
- **Do NOT change G-13/G-14/G-15 decisions.** G-13-B (releasable) is NOT MET (tiers TBD; blocked
  on assumption A-5 / studies S-1, S-4). Vocabulary `releasable = false`.
- **Do NOT generalize autofill to arbitrary sites.** Autofill fires only on the controlled form
  (`isControlledForm`, form id `mca-mock`).
- **Do NOT implement an LLM / external AI / embeddings / vector DB / network OCR.**
- **Do NOT move the auth token into content scripts.** Token lives only in the service worker.
- **Do NOT send field values / page HTML / page text / passwords to the backend.** Detection,
  interpretation, and audit are value-free; audit `detail` carries the canonical id only.
- **Never auto-fill declarations/consent; never submit a form.**
- Keep the extraction-module invariant: only `app/services/extraction.py` names a concrete
  extractor (guard test `test_only_the_extraction_module_may_know_about_engines`).

## 5. Environment & tooling

- OS: Windows 11; shell used: Git Bash (some PowerShell). Repo root: `C:\Users\Vedant\DOCURA`.
- **PostgreSQL** via `backend/docker-compose.yml` (image postgres:16-alpine), host port **5433**,
  container `docura-postgres`. Credentials come from `backend/.env` (gitignored):
  `POSTGRES_USER=docura`, `POSTGRES_PASSWORD=docura_local_dev`, `POSTGRES_DB=docura`.
  DBs: **`docura`** (dev/app) and **`docura_test`** (tests). Docker Desktop must be running;
  it can take a few minutes to start.
- Backend Python venv: `backend/.venv/` (use `backend/.venv/Scripts/<tool>.exe`). Python 3.x,
  mypy strict, ruff line-length 100 (`[tool.ruff] src=["app","tests"]`, `[tool.mypy]
  files=["app","tests"] strict=true`). Test DB env var: `TEST_DATABASE_URL` (DB-backed tests
  **skip** — never fail — when unset; they RUN when set).
- `var/` is gitignored (document vault storage + S-6 corpus live here; never committed).
- Frontend: Node + npm in `frontend/`. Extension: Node in `extension/` (`node --test`, no deps).

## 6. Key commands

Backend (from `backend/`, with Docker + Postgres up):
```bash
docker compose up -d                     # start Postgres (:5433)
docker exec docura-postgres createdb -U docura docura_test   # once, if missing
export TEST_DATABASE_URL="postgresql://docura:docura_local_dev@localhost:5433/docura_test"
.venv/Scripts/ruff.exe check app tests scripts
.venv/Scripts/mypy.exe app tests
.venv/Scripts/alembic.exe heads          # must be a single head: d4e5f6a7b8c9
.venv/Scripts/pytest.exe -p no:cacheprovider     # full suite (476 passed with Postgres)
```
Extension (from `extension/`): `node --test`  ·  `node --check src/<file>.js`
Frontend (from `frontend/`): `npm run typecheck`  ·  `npm test`  ·  `npm run build`
Run the backend app: `backend/.venv/Scripts/python.exe -m app.main` (uvicorn on :8000; health
at `GET /health`).
S-6 harness (dev): `.venv/Scripts/python.exe -m scripts.s6_ingest …` / `… -m scripts.s6_evaluate --root var/s6_corpus --engine unconfigured`.
Dev record seed: `.venv/Scripts/python.exe -m scripts.dev_seed_record`.

## 7. Manual-test / dev-seed state (conversation-only info)

- Manual test user: **`vedantskadam24@gmail.com`** (exists in the dev `docura` DB). Its record
  was seeded (via `scripts/dev_seed_record.py`, which reuses the real observation chain, engine
  marked `dev-manual-seed`, not OCR): `person.full_name = "Vedant Santosh Kadam"`,
  `person.date_of_birth = "2007-03-24"`. Verified through `GET /record/attributes`.
- The controlled form's id is **`mca-mock`** — only forms with this id are auto-filled.
  Fixtures: `extension/test/fixtures/mock-form-m10.html` (info-bearing, mca-mock),
  `mock-form.html` (M9 L-STRUCT), `mock-form-m17-labels.html` (opaque-id label-only, form id
  `demo-application-form` → NOT auto-filled; for metadata inspection via
  `globalThis.__docuraForms` in the DOCURA content-script console context).
- The user's own account email in tooling context is `gaurangsk84@gmail.com` (unrelated to the
  seeded test user; use only for authorship/attribution).

## 8. Git / uncommitted state (IMPORTANT — do not lose)

- HEAD = `d68ce15 feat: add S6 corpus and evaluation harness`; prior: `3ccdf7a` (M18 provider),
  `d59d2ba` (M17 metadata). So M17/M18/M19 extension+eval code IS committed.
- **Uncommitted working-tree changes remain** (M9–M16 backend + some extension). Run
  `git status` to see them; the notable ones and why they exist:
  - `backend/app/api/form_sessions.py`, `app/services/form_session.py`, `app/core/errors.py`,
    `app/schemas/form_session.py` — the M9/M15 `POST /form-sessions/{id}/actions` endpoint +
    `append_client_action` + `FormActionCreate` + `FormActionNotFoundError`.
  - `backend/config/vocabulary/canonical_attributes.v0.2-draft.toml` (untracked) +
    `app/services/current_record.py` + `app/services/field_extraction.py` (repointed to v0.2) +
    `tests/test_vocabulary_config.py` (2 entries) + `docs/SPRINT_4_DECISION_REGISTER.md` (D-05.16)
    + `docs/SPRINT_4_G13_CANONICAL_ATTRIBUTE_VOCABULARY.md` (§23) — the M12 `person.date_of_birth`.
  - `backend/tests/{test_current_record,test_field_extraction,test_record_api,
    test_attribute_observations}.py` — repointed to v0.2-draft.
  - `extension/src/popup.html`, `popup.js` — M10 approval UI.
  - `extension/test/interpret.test.js` — M16/M17 tests.
  - Untracked docs/scripts/fixtures: `BACKEND_MVP_COMPLETION.md`, `SPRINT_4_M9/M10/M11/M12/M14`
    docs, `scripts/dev_seed_record.py`, `mock-form*.html`, `integration.test.js`.
  - `.claude/settings.json` (local settings; not part of the product).
- **These uncommitted changes are required for the current green test state** (e.g., the v0.2
  vocab is referenced by services + tests; the action endpoint is referenced by M15 tests). A
  fresh session should NOT `git stash`/discard them. Commit only if the user asks.

## 9. Bugs/errors encountered this session & resolutions

1. **Full-suite flaky isolation (rare):** one full-Postgres run showed "4 failed, 2 errors"
   with "Email already registered"/cross-user 404s in unrelated files; did NOT reproduce across
   4 subsequent full runs. Root cause: pre-existing pytest-asyncio/asyncpg loop-isolation
   fragility at full-suite scale (not our code — every test passes in isolation and in file
   groups). **Not fixed** (unreproducible; shotgunning shared conftest is riskier than the
   flake). Recommended future fix: session-scoped event loop or `NullPool` in the `db_engine`
   fixture — only after a reliable repro. If a full run shows scattered isolation failures,
   re-run before treating them as real.
2. **M15 contract test** `test_no_endpoint_lets_a_client_forge_history` failed after adding
   `POST …/actions` (it asserted no action-post endpoint existed). Fixed by updating it to a
   write-surface assertion (`test_the_form_session_write_surface_is_exactly_intended`) that
   includes `/actions` and still guards against unexpected write routes — intent preserved, not
   weakened. (This fix is committed at/around HEAD.)
3. **M19 guard test** `test_only_the_extraction_module_may_know_about_engines` failed because
   `app/evaluation/engines.py` (and two docstrings) named `UnconfiguredExtractor`. Fixed by
   having `engines.build_engine(name, settings)` obtain the unconfigured extractor via
   `build_document_extractor(settings)` (never naming the concrete class) and rewording
   docstrings. Guard intent preserved.
4. **`Settings()` in a unit test** raised pydantic validation errors (needs env not present).
   Fixed by constructing a self-contained `Settings(environment=TEST, database_url="…dummy…",
   document_storage_root=tmp_path/…)` in `tests/test_s6_evaluation.py` (no DB connection made).
5. **Docker Desktop** was down twice across the session; restart it and wait for
   `docker info` to succeed, then `docker compose up -d`, then recreate `docura_test` if missing.

## 10. Remaining tasks / exact next step

There is **no in-flight coding task**. M19 is complete and green. See `TODO.md` for the full
list. The two big blockers are external (S-6 corpus collection; G-14/G-15 sensitivity tiers).

**Exact next step:** wait for the user's next instruction. If they ask to continue DOCURA work,
the most likely candidates (all currently blocked or optional) are:
- Commit the uncommitted M9–M16 working-tree changes (only if the user asks).
- Any new milestone the user specifies. Do NOT self-start engine selection, new attributes, or
  OCR — all blocked.
Before any backend work: `docker compose up -d`, set `TEST_DATABASE_URL`, confirm `pytest` green
and a single Alembic head.

## 11. Assumptions that must NOT be changed

- `UnconfiguredExtractor` remains the production extractor until S-6 completes and governance
  approves an engine.
- Exactly two canonical attributes are released/authored; the vocabulary is `releasable = false`.
- Autofill is controlled-form-only (`mca-mock`); routine `full_name` auto, `date_of_birth`
  consent-gated; declarations never touched; DOCURA never submits.
- Token stays in the service worker; detection/interpretation/audit are value-free.
- Single Alembic head `d4e5f6a7b8c9`; no schema change was needed for M9–M19 (the action
  endpoint reuses the existing `form_actions` table).
- Approvals are one-time, exact-scope, session-only, never persisted (BR-007).
