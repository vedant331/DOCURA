# DOCURA — Backend MVP Completion

Snapshot of the DOCURA backend after the M15 completion pass (17 Sep 2026). It states
what is COMPLETE, PARTIAL, BLOCKED, or INTENTIONALLY UNAVAILABLE, and records the one
capability implemented in this pass: **owner-scoped recording of in-session form actions**
(closing the M9 gap so extension fills/approvals become auditable).

## 1. Architecture

- **FastAPI** app (`app/main.py`) with routers under `app/api/`, business logic in
  `app/services/`, ORM models in `app/db/models.py`, Pydantic schemas in `app/schemas/`.
- **Async SQLAlchemy** over **PostgreSQL** (native UUID); migrations via **Alembic**
  (single head `d4e5f6a7b8c9`).
- **Durable document processing**: a `processing_jobs` table + worker (D-09.4 Option B),
  not an in-request task — survives restarts, retryable, one job per document.
- **Replaceable extraction seam** (`app/services/extraction.py`): `DocumentExtractor`
  protocol + `TextRegion/TextBlock/ExtractedPage/ExtractionResult`; `UnconfiguredExtractor`
  is the honest default until an engine is approved (S-6).
- **Layered ownership**: every user-owned query carries `user_id` in the `WHERE` clause
  (NFR-SEC-003); ownership is never inferred from a client-supplied id.
- **Errors**: `DocuraError` subclasses carry an HTTP `status_code` and render as
  problem+json; 404s are oracle-avoiding (missing vs not-owned are indistinguishable).

## 2. Capability inventory

| Capability | State | Notes |
| --- | --- | --- |
| Auth (register/login/logout/sessions/reset), `/users/me` | **COMPLETE** | Bearer token; shared by web app + extension |
| **Account deletion (`DELETE /users/me`)** | **COMPLETE** | FR-ACC-006/007/008, NFR-PRIV-003: explicit-confirmation (echo account email), owner-only, DB cascade removes documents/extracted info/derived rows/sessions/form history, storage originals deleted; no values logged. NFR-PRIV-003 *period* is TBD (deletion is immediate, which satisfies "within a stated period"). |
| Documents (upload/list/get/content/reprocess/delete, limits) | **COMPLETE** | Original preserved; owner-scoped |
| Document processing lifecycle (queued→processing→ready/needs_review/failed) | **COMPLETE** | Durable job, retry, `failure_reason`, no duplicate-processing race |
| Extraction seam + persistence (runs/pages/blocks/regions) | **COMPLETE (ready, engineless)** | Awaits an approved engine (S-6) |
| Classification | **PARTIAL** | Service + unrecognised outcome exist; unevaluable without corpus |
| Attribute observations (value + provenance + confidence) | **COMPLETE** | Populated only once an extractor emits (S-6) |
| Current record derivation (available/ambiguous/conflict) | **COMPLETE** | Conflict surfaced, never resolved (G-20) |
| Canonical record API + field lookup | **COMPLETE** | `GET /record/attributes` and `/{canonical_identifier}` |
| Canonical vocabulary (v0.2-draft: full_name, date_of_birth) | **COMPLETE (not releasable)** | Tiers TBD (G-14/G-15); G-13-B not met |
| Form-session lifecycle (active/handed_back/stopped/expired) | **COMPLETE** | hand-back never submits (BR-008) |
| Form-session audit — lifecycle | **COMPLETE** | hand_back/stop recorded internally |
| **Form-session audit — in-session actions (fill/select/attach/ask/approval/override)** | **COMPLETE (new this pass)** | `POST /form-sessions/{id}/actions`, owner-scoped, no values |
| Document matching | **BLOCKED** | Needs document classification (OCR/S-6) + approved upload-field requirements; today every document is unclassified |
| Attachment preparation (derived copies) | **BLOCKED** | Downstream of matching; also needs an image-transform decision (FR-MATCH-006/007/010) |
| Sensitive approval persistence | **INTENTIONALLY UNAVAILABLE** | BR-007: approvals are one-time, session-scoped, never persisted. The backend records only the audit *decision* (approval_decision action) |
| Review assembly (field-level) | **INTENTIONALLY UNAVAILABLE (backend)** | Field/readiness data lives in the extension's isolated world (not bridged); the web review = session state + audit + record |
| OCR engine | **BLOCKED — S-6** | Corpus does not exist (M14) |

## 3. Completed this pass — in-session action recording

**Endpoint:** `POST /form-sessions/{session_id}/actions` → 201 `FormActionResponse`.
The extension is DOCURA's execution surface; fills, selections, attachments, questions,
and approval decisions happen on the page, and this endpoint makes them part of the
user's owner-scoped audit (FR-AUD-001…003). It is deliberately narrow and forgery-resistant:

- Only the caller's own **ACTIVE** session (history of an ended session is immutable).
- Only **in-session** action types — `fill, select, attach, ask, answer, approval_request,
  approval_decision, override`; the lifecycle transitions `hand_back`/`stop` are **rejected**
  (they have their own endpoints and move state).
- Every referenced id validated as the caller's own: `document_id` (owner-scoped vault
  query), `observation_id` (run→document→user chain), `reverses_action_id` (must be an
  earlier action of the same session).
- **No field value or form content stored** — only a field handle, provenance references,
  and DOCURA's own short note (FR-AUD-006, NFR-PRIV-007).

This revises M1's "no client-posted history" stance, which had deferred these to "later
milestones": with filling now built in the extension (M10/M13), FR-AUD-001…003 are
otherwise unsatisfiable, and owner-scoping removes the forgery concern (a user can only
append to their own session's history).

## 4. API inventory

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/auth/register` `/auth/login` `/auth/logout` | Account + session |
| GET/POST | `/auth/sessions` `/auth/sessions/revoke-all` | Session management |
| POST | `/auth/password-reset/request` `/auth/password-reset/confirm` | Reset |
| GET | `/users/me` | Authenticated account |
| DELETE | `/users/me` | Delete the account + all data (FR-ACC-006/007/008), explicit-confirmation |
| POST/GET/GET/PATCH/DELETE | `/conversations` `…/{id}` | Chatbot conversations (additive layer; see CHATBOT_BACKEND.md) |
| POST/GET | `/conversations/{id}/messages` | Send a message (orchestrated) / list history |
| GET/POST/DELETE | `/documents` `…/{id}` `…/{id}/content` `…/{id}/reprocess` `/documents/limits` | Vault |
| GET | `/record/attributes` `/record/attributes/{canonical_identifier}` | Structured record + field lookup |
| POST/GET | `/form-sessions` `…/{id}` | Session activate/list/read |
| POST | `/form-sessions/{id}/hand-back` `…/{id}/stop` | Lifecycle |
| GET | `/form-sessions/{id}/actions` | Read history |
| **POST** | **`/form-sessions/{id}/actions`** | **Record an in-session action (new)** |

All authenticated, owner-scoped, typed request/response, problem+json errors.

## 5. Entity relationships

```
User 1──* Document 1──1 ProcessingJob
                 └──* ExtractionRun 1──* ExtractionPage 1──* ExtractionBlock
                                                              └─ region (x,y,w,h)
ExtractionBlock 1──* AttributeObservation  (canonical_identifier, value, confidence)
User 1──* FormSession 1──* FormAction  (action_type, outcome, field_ref,
                                        source_document_id?, source_observation_id?,
                                        reverses_action_id?, detail?)
Canonical vocabulary: config/vocabulary/canonical_attributes.v0.2-draft.toml (referenced by id only)
```

## 6. Data flow (where prerequisites exist)

```
USER → AUTH → UPLOAD DOCUMENT → PROCESSING JOB → EXTRACTOR SEAM (engine: S-6 blocked)
     → EXTRACTION PERSISTENCE → CANONICAL OBSERVATION → CURRENT RECORD
     → CANONICAL LOOKUP (/record/attributes) → EXTENSION
     → FORM SESSION → [matching/preparation: blocked] → APPROVAL (session-scoped)
     → in-session actions recorded (/actions) → REVIEW (session+audit+record) → HAND-BACK
```
Today the record is populated by test fixtures (no engine); everything downstream of the
record is real and exercised.

## 7. Extension contracts (backend side)

- Auth: `POST /auth/login` (bearer), `GET /users/me`, `POST /auth/logout`. Token lives in
  the service worker only — never sent to the page.
- Session: `POST /form-sessions` (activate), `POST /form-sessions/{id}/stop`,
  `POST /form-sessions/{id}/hand-back`.
- Record: `GET /record/attributes` (worker fetches; values cross into the isolated world
  for filling, token does not).
- **Audit (new, optional for the extension to adopt):** `POST /form-sessions/{id}/actions`
  to record a fill/approval/etc. The extension is not rewritten in this pass; the endpoint
  is ready for it and is already consumed for display by the web app's Activity view via
  `GET …/actions`.

## 8. Document-processing flow
Upload validates type/size/checksum and stores the original → a `processing_jobs` row is
created (one per document) → the worker moves the document `queued→processing` → invokes
the extractor seam → on success persists runs/pages/blocks/observations and sets
`ready`/`needs_review`; on failure sets `failed` with a non-technical `failure_reason`,
preserves the original, and offers `/reprocess`. (FR-OCR-008 one-document-many-pages and
FR-OCR-009 failure behaviour are implemented structurally.)

## 9. Record flow
Observations across runs are derived on read into the current record: agreeing values →
one **available** value; a single source with several values → **ambiguous**; distinct
values across documents → **conflict** (surfaced, never auto-resolved — G-20). The record
API returns value + observations (document/page/region/confidence). N-TEXT/N-DATE
normalisation decide agreement; nothing is folded beyond the approved rules.

## 10. Matching / preparation flow (BLOCKED)
Matching (upload field → candidate documents) and preparation (derived, constraint-meeting
copies) live in the extension's deterministic modules and cannot be made authoritative in
the backend yet: every stored document is `unclassified` (no OCR to classify types), and
the approved upload-field requirements do not exist. Recorded as blocked; the `attach`
action can already reference an owned document once the extension selects one.

## 11. Approval flow
Per BR-005/BR-007, a sensitive disclosure approval is one-time, exact-scope, and **never
persisted or generalised** — it lives in the extension's session ledger (M13). The backend
representation is the **audit record** of the decision (`approval_decision` action via the
new endpoint), not a reusable approval store (which would violate BR-007).

## 12. Review / hand-back flow
The web review is assembled from real backend state: session lifecycle + the audit trail
(now including in-session actions) + the record. The backend does not claim "zero blockers"
— field-level readiness is the extension's, and the web app shows an honest seam for it.
Hand-back marks the session `handed_back`, records the audit action, and **never submits**
the external form (BR-008); there is no endpoint that could.

## 13. Security / ownership
Every user-owned resource (documents, record attributes, sessions, actions, referenced
documents/observations) is filtered by `user_id` in the query. The new endpoint validates
`document_id`, `observation_id`, and `reverses_action_id` as the caller's own before
recording. No raw personal value is stored in audit or logged in diagnostics.

## 14. Intentionally blocked / unavailable
- **OCR engine + supported document/field set** — S-6 corpus absent (M14).
- **Automatic-action threshold (BR-001)** — TBD/G-04; produced by the S-6 evaluation.
- **Additional canonical attributes** — G-13-B (tiers, G-14/G-15) not met; only full_name
  (auto) and date_of_birth (consent-gated) authored.
- **Backend matching/preparation** — blocked on classification + form-field requirements.
- **Persisted approvals** — deliberately never persisted (BR-007).

## 15. OCR / S-6 dependency
The entire "real document → structured record" upstream is gated on the S-6 held-out
corpus, which does not exist and requires a G-02-governed, consented, real-world collection
(M14, D-02.7). The seam and everything downstream are ready; an approved engine drops in
behind `DocumentExtractor` with no backend redesign.
```
