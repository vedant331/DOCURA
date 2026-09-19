# DOCURA — Chatbot Backend Foundation

An **additive** orchestration layer over the existing DOCURA services. It is a controlled,
task-oriented assistant — **not** a generic LLM agent — and it changes no existing domain logic
(OCR, extraction, record, form sessions, approval, extension, safety are untouched).

## Architecture

```
Chat API (app/api/chat.py)
   → Conversation layer (app/services/conversation.py)      persistence, owner-scoped
   → Task Orchestrator (app/services/chatbot/orchestrator.py)
        → Intent layer (chatbot/intent.py + chatbot/llm.py) deterministic, or configured LLM + fallback
        → Requirements provider (chatbot/requirements.py)   authoritative-source seam (unconfigured)
        → Readiness engine (chatbot/readiness.py)           requirements × record/documents
        → DOCURA domain services (reused):
             current_record.build_current_record            structured record
             document_service.list_documents                vault
   → Response composer → structured assistant message
```

The orchestrator **calls existing services**; it never touches the database directly for domain
data and never mutates documents/records. It is not coupled to any LLM vendor.

## Conversation API (all authenticated, owner-scoped, problem+json errors)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/conversations` | Create a conversation |
| GET | `/conversations` | List the caller's conversations |
| GET | `/conversations/{id}` | Read one (404 if not owned) |
| PATCH | `/conversations/{id}` | Rename |
| DELETE | `/conversations/{id}` | Delete (cascades messages only) |
| POST | `/conversations/{id}/messages` | Send a message → runs orchestration, returns the user + assistant messages |
| GET | `/conversations/{id}/messages` | List messages (paginated) |

Ownership is a `WHERE user_id = …` clause; a guessed id belonging to another account is a 404.

## Message model

`conversation_messages`: `id, conversation_id, role (user/assistant/system), message_type
(text/requirements/document_status/readiness/question/approval/action/error), content (text),
data (JSONB, value-free structured blocks), created_at`. No third-party form content, no raw
sensitive values, no secrets are stored.

## Task / intent model

`TaskType`: `ASK_REQUIREMENTS, CHECK_DOCUMENTS, CHECK_READINESS, FILL_FORM, DOCUMENT_MATCH,
EXPLAIN_BLOCKER, GENERAL_DOCURA_HELP, UNKNOWN`. `Intent` = `{task_type, confidence, entities,
reason, method}`. `IntentProvider` is a seam with two implementations:

- `DeterministicIntentProvider` — transparent keyword/phrase matching, no LLM, no network,
  reports the phrase it matched, returns `UNKNOWN` rather than guessing. This is the default.
- `LlmIntentProvider` (`chatbot/llm.py`) — a real, **vendor-independent** language-understanding
  layer used only when an LLM is configured. It classifies into the *same* `TaskType`s and
  extracts entities; it is **not** the source of truth and cannot touch the DB/documents, approve,
  submit, or override safety. It requires structured JSON output
  (`{task_type, confidence, entities, reason, needs_clarification}`), validates it (unknown/invalid
  task → `UNKNOWN`; confidence clamped to `[0,1]`; entities coerced to trimmed strings;
  `needs_clarification` → `UNKNOWN`, never a guess), and **wraps the deterministic provider as its
  fallback**. On any provider failure (timeout, 429, 5xx, auth, network, malformed JSON) it does
  **not fabricate** — it falls back to deterministic understanding and marks the intent `method`
  with `:fallback:`. Vendor independence: it speaks the OpenAI-compatible `/chat/completions` shape
  over plain HTTP (`httpx`), so any vendor/gateway works via `DOCURA_LLM_BASE_URL` and no vendor SDK
  is imported.

`select_intent_provider(settings)` returns the LLM provider (with deterministic fallback) when
`settings.llm_configured`, else the deterministic provider directly. Classification runs in a
thread (`asyncio.to_thread`) so a blocking LLM call never stalls the event loop.

**The LLM never answers government/application requirements from its training knowledge.** Those
flow only through the `RequirementsProvider` seam (below); the LLM's role stops at understanding
*what the user is asking*.

## Requirements provider (authoritative-source seam)

DOCURA does **not** invent government/application requirements. `RequirementsProvider` is the
seam; the production default `UnconfiguredRequirementsProvider` reports `UNAVAILABLE` and never
fabricates documents, information, or a source. `RequirementSet` carries `status` (VERIFIED /
UNAVAILABLE / AMBIGUOUS / STALE), `source`, `retrieved_at`, and typed items. A real integration
(a configured, identifiable source that records its retrieval time and marks stale/uncertain
data) drops in at `build_requirements_provider(settings)`.

## Readiness engine

`compute_readiness(db, user_id, requirement_set)` computes per-item status from the user's own
record (`build_current_record`) and vault (`list_documents`), reusing DOCURA's safety semantics:
`AVAILABLE` (a single agreed value), `NEEDS_REVIEW` (the record marks it ambiguous/conflicting —
never auto-resolved), `MISSING`, `UNKNOWN` (no way to verify — never guessed). A document
requirement stays `UNKNOWN` when documents exist (type classification is S-6-blocked) or
`MISSING` when the vault is empty. References are canonical ids, never values.

## Safety integration

The chatbot reuses, and never weakens, the existing invariants: it does not guess (unknown →
untouched), does not auto-resolve conflicts (surfaced as needs-review), never accepts
declarations/consent, never inherits approvals, and **never fills or submits a form**. A
`FILL_FORM` request returns an ACTION pointing to the existing extension/form-session flow
(explicit activation, per-instance approval, no submission). There is no submission endpoint
anywhere in the backend (asserted by test).

## Privacy

User-isolated; conversation delete removes only its messages (never documents/record/sessions).
Messages store statuses/references, not raw values; logs stay value-free. Conversation history
is not a second copy of the vault. Context is task-specific (check-documents pulls document
metadata; readiness pulls the relevant record) — data minimisation.

## Configuration

The LLM is **off by default** and env-driven (no hard-coded keys/models/URLs, no committed
secrets):

| Env var | Default | Meaning |
| --- | --- | --- |
| `DOCURA_LLM_PROVIDER` | `none` | `none` = deterministic only; `openai_compatible` = call the configured endpoint for intent only |
| `DOCURA_LLM_MODEL` | `""` | Model id (non-secret) |
| `DOCURA_LLM_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible base URL (any vendor/gateway) |
| `DOCURA_LLM_API_KEY` | unset | `SecretStr`; never logged |
| `DOCURA_LLM_TIMEOUT_SECONDS` | `12.0` | Per-request timeout (bounded `0 < t ≤ 60`), no retries |

`settings.llm_configured` is true only when provider ≠ `none` **and** a key **and** a model are
set. Three states, all exposed internally without leaking secrets (via the intent `method`):

1. **Disabled / unconfigured** → `DeterministicIntentProvider` (`method` = `deterministic-keyword-v1`).
2. **Configured and reachable** → `LlmIntentProvider` (`method` = `<provider>:<model>`).
3. **Configured but unavailable** (any failure) → controlled deterministic fallback
   (`method` = `<provider>:fallback:deterministic-keyword-v1`).

The requirements provider is selected the same way and defaults to unconfigured (`UNAVAILABLE`).

### Logging / errors

Logging is value-free: provider, model id, task category, latency, success/failure category,
and whether the fallback was used — **never** message contents, history, document text, personal
values, or the API key. Provider errors are caught by exception category (never the raw payload,
auth header, or stack trace); the user-facing degradation is a transparent deterministic answer.

### Testing

`tests/test_llm_intent.py` covers provider selection, structured-output validation
(valid/malformed/unknown-task/invalid-confidence/missing-fields/needs-clarification), entity
sanitisation, failure→fallback for every error category, data-minimisation (only system + the
message are sent; history is bounded), and safety (an out-of-enum "task" reduces to `UNKNOWN`; no
submission capability exists). It uses a **fake completion function** — **no real/paid API call
runs in the suite**. `scripts/llm_smoke.py` is a separate manual one-request smoke test that runs
only when a provider is configured.

## Known limitations

- **External-provider dependency:** the LLM intent provider is implemented and vendor-independent,
  but is only active when configured; unconfigured or on failure, understanding degrades to the
  deterministic provider (never fabricated). The authoritative requirements source is still a seam
  (`UNAVAILABLE` until configured) — the LLM deliberately does **not** substitute its training
  knowledge for it.
- **Requirement / product blockers:** document-type classification (S-6/OCR) is needed before
  readiness can verify specific required document *types* and before DOCURA_MATCH is more than a
  pointer; per-document-type field sets and additional canonical attributes remain blocked
  (G-12/G-13-B). None of these are faked.
- **Streaming** is intentionally not implemented (request/response first).
