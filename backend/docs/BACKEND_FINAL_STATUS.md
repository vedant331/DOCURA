# DOCURA Backend — Final Status

Point-in-time status after the final backend engineering pass. It separates **engineering-complete**
functionality from what is **blocked by product or external evidence**. Nothing blocked is called
complete.

## ENGINEERING-COMPLETE
- **Auth**: registration, login, sessions, password reset (delivery + tokens).
- **Vault**: upload, validation, retrieval, deletion; owner isolation enforced in every query.
- **Processing pipeline**: OCR seam, PDF rasterization, Tesseract **candidate** adapter, structured
  record derivation, provenance, confidence plumbing, classification, conflict surfacing,
  duplicate-observation dedup.
- **Search**: filename + attribute-value search, **type/date filters (FR-SRCH-005)**, owner-scoped.
- **Export & account**: record export, account deletion — owner-scoped.
- **Form sessions**: backend + approval plumbing; no-submit boundary.
- **Audit**: value-free audit records.
- **Chatbot (dynamic)**: conversation/message CRUD; intent understanding (LLM or deterministic);
  task orchestration over the user's real, owner-scoped context; **grounded LLM response narration**
  with a guaranteed deterministic, context-aware fallback; multi-turn history; strict data
  minimisation; no-submit boundary preserved.
- **Sensitivity engineering support**: tiers represented; raise-only + consequential-floor
  invariants; per-instance approval; unknown-safe conservative floor; injected policy seam ready
  (see `SENSITIVITY_GOVERNANCE_DECISION.md`).
- **S-6 tooling**: corpus model, validation, held-out isolation, field-correctness metrics,
  reproducible evaluation scripts.

## Chatbot capabilities
- Answers from the authenticated user's **actual** state: documents (names/status/count), readiness,
  requirements (only when an authoritative source exists — never fabricated).
- Multi-turn: prior conversation turns (bounded, text-only) inform intent and the reply.
- Grounded: the LLM composes natural replies **only** from the handler's structured context; on any
  provider failure it returns the deterministic, still-context-aware message (e.g. it names the
  user's documents rather than a generic line).
- Honest about unknowns; never claims a fill/submit happened; never invents documents/requirements/
  values; never exposes sensitive values (they are not in the context it receives).

## Security / privacy posture
- Every conversation/message/document/record/form-session/search/export route is authenticated and
  owner-scoped (identity from the session, never a client id).
- LLM payloads contain only the user's message, a bounded slice of prior message text, and the
  handler's value-free structured context — never the raw record's sensitive values, document bytes,
  or secrets. The API key is read from settings and never returned or logged.
- Logs are value-free (no names/DOB/PAN/Aadhaar/addresses/emails/phones/OCR text).
- `.env` and `s6_sources/` and `var/` are gitignored; no secrets or raw personal documents in VCS.

## Tests
- Backend: **638 tests, green** (added: 12 search-filter, 9 chatbot-dynamic; earlier: field-extraction
  precision, current-record dedup).
- `ruff` clean; `mypy` clean (60 source files). Single Alembic head; app factory imports and builds.

## Product decisions — RESOLVED
- **D-A5 (sensitivity tiers): RESOLVED + applied** — approved tiers in force via config + extension
  (full_name/age routine; dob/email/phone/address sensitive; PAN/Aadhaar consequential; default
  sensitive). See `SENSITIVITY_GOVERNANCE_DECISION.md`.
- **D-OCR-METRIC: RESOLVED (PATH B)** — strict metric authoritative; containment retained as a
  non-authoritative diagnostic. See `S6_OCR_EVALUATION_REPORT.md` §3c.

## Remaining blockers (external evidence only)
- **External evidence (S-6):** a larger real, imperfect, multi-subject OCR corpus with ground truth
  → then engine selection, per-type inclusion, and the BR-001 threshold.
- **Bounded follow-up (not blocking):** frontend record-view value masking (FR-SENS-004, MVP SHOULD)
  — surface the tier on the record API and have the frontend mask; the extension review surface
  already masks per tier.

## OCR / threshold / production-extractor status
- **Production extractor:** `UnconfiguredExtractor` (unchanged). Tesseract remains a **candidate**
  (dev opt-in `DOCURA_OCR_ENGINE=tesseract`, explicitly *not* a production selection).
- **BR-001 automatic-action threshold:** **UNSET**.
- **Review threshold:** **UNSET**.
- Extracted-text search (FR-SRCH-002) stays gated on production OCR (no production extracted text
  exists yet).

**Bottom line:** all currently implementable backend engineering work is complete; only product and
external-evidence blockers remain, and they are documented above rather than resolved silently.
