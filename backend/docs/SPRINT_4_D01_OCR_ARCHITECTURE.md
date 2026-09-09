# Sprint 4 — D-01: OCR / Extraction Architecture

| Field | Value |
| --- | --- |
| Decision | **D-01 — self-hosted extraction, behind a replaceable interface** |
| Companion decision | **D-00 — Option 2, split Sprint 4** (build the A-7-independent envelope now) |
| OCR engine | **TBD — pending held-out evaluation** (AR-AST-008, study S-6) |
| Status | Architecture implemented. No engine installed. No pipeline built. |
| Authoritative requirements | `backend/step3.pdf` — DOCURA 03, Requirements Specification v1.0 |
| Related | [`SPRINT_4_DECISION_REGISTER.md`](SPRINT_4_DECISION_REGISTER.md) — the full analysis this implements one decision from |

---

## 1. The decision

**D-01 selects a self-hosted extraction architecture with a replaceable extraction interface.** Documents are processed inside DOCURA's own trust boundary; no third-party OCR or AI service is contacted.

**D-01 does not select an engine.** That is deliberate, and it is what the specification requires:

> **AR-AST-008** (MVP): "Assisted components shall be evaluated against a held-out corpus of real, imperfect documents **before any threshold is set**."

> **§6, Selection Principle**: "This document specifies what each layer must guarantee, not what technology provides it. Any component may be replaced provided its replacement meets the same guarantees... **Technology selection belongs to document 04.**"

The engine is therefore recorded throughout as:

> **TBD — pending held-out evaluation**

## 2. What was built

```
Document (Sprint 3 vault: bytes + metadata)
    ↓
Document processing                    ← not built yet (D-09)
    ↓
DocumentExtractor  (Protocol)          ← app/services/extraction.py
    ↓
Concrete extractor                     ← UnconfiguredExtractor today; the chosen engine later
    ↓
ExtractionResult                       ← engine-neutral: pages, text, regions, confidences, metadata
```

One module, `app/services/extraction.py`, holds all of it:

| Component | What it is |
| --- | --- |
| `DocumentExtractor` | The port. A runtime-checkable `Protocol` with `name`, `version`, `is_available()`, and `extract(source, *, content_type)`. |
| `ExtractionResult` | What every engine returns: ordered `pages`, the `engine` and `engine_version` that produced it, and engine-neutral `metadata`. `text` and `page_count` are derived, so whole-document text can never disagree with per-page text. |
| `ExtractedPage` | One page: 1-based `number`, `text`, optional `blocks`, optional page `confidence`. |
| `TextBlock` | A run of text with an optional `region` and an optional `confidence`. A unit of *text*, never a unit of *meaning*. |
| `TextRegion` | Page-relative fractional coordinates (`page`, `x`, `y`, `width`, `height`), validated on construction. |
| `UnconfiguredExtractor` | The placeholder. Reports `is_available() is False` and raises `ExtractionNotConfiguredError` from `extract()`. |
| `build_document_extractor(settings)` | The single plug point, mirroring `build_document_storage`. |

Two error classes were added to `app/core/errors.py`: `DocumentExtractionError` (the failure class FR-OCR-009 paths will catch) and `ExtractionNotConfiguredError`, its subclass, meaning "no engine is installed yet".

The extractor is constructed once in `create_app` and put on `app.state.document_extractor`, and `app.api.deps.get_document_extractor` resolves it — exactly the pattern Sprint 3 established for `DocumentStorage`. **No endpoint depends on it yet.**

## 3. Why the interface exists

1. **The specification demands replaceability.** §6 says any component may be replaced provided its replacement meets the same guarantees. That is only true in practice if exactly one module knows which engine is installed.
2. **The engine must be chosen on evidence, not on prediction.** AR-AST-008 requires evaluation against real, imperfect documents before any threshold is set. The evaluation should also choose the engine — which means the code has to exist before the choice does.
3. **A wrong choice must stay cheap.** Assumption A-7 ("Document comprehension is accurate enough on real-world scans to be trusted") is untested. If the first engine fails the evaluation, replacing it is a change to `build_document_extractor` and one new class.
4. **Confidence and provenance are requirements, not engine features.** FR-OCR-005 requires a per-field confidence independent of the document-level one, FR-OCR-007 requires the source region, and AR-AST-006 requires every assisted output to be explainable by its source. Putting these in the *result type* means an engine that cannot supply them is visibly non-compliant rather than quietly accommodated.

### The placeholder refuses; it does not pretend

`UnconfiguredExtractor` raises. It does not return empty text, and it does not read the document stream at all (a test asserts this by handing it a stream that fails on read).

Empty text would be indistinguishable from a genuinely unreadable document, and fabricated text would be worse: AR-AST-008's evaluation is meaningless if any part of the system can manufacture a result. BR-016 — "when any component fails or is uncertain, the correct behaviour is to do nothing and inform the user" — points the same way.

## 4. What is deliberately NOT decided

Everything below is a separate decision or is evaluation-dependent. None of it appears in the code.

| Not decided | Requirement | Where it is tracked |
| --- | --- | --- |
| The OCR engine | §6, AR-AST-008 | **TBD — pending held-out evaluation** |
| Document-type field definitions | FR-OCR-004 | D-05 (gaps G-12, G-13) |
| The canonical attribute vocabulary | FR-ACC-004, FR-INF-004 | D-05 (gap G-13) |
| Review threshold and automatic-action threshold | FR-OCR-006, BR-001, BR-002 | D-03 — a confidence is *carried* here and compared nowhere |
| Global vs per-document-type thresholds | NFR-MNT-002 | D-03 (gap G-07) |
| Sensitivity classification rules | FR-INF-007, FR-SENS-001 | D-06 (gap G-14) |
| The final MVP document-type set | §7.1, ASM-001 | D-04 |
| Document classification | FR-OCR-002, AR-AST-002 | A separate assisted component; it will get its own port |
| The extracted-information data model | FR-INF-001…009 | D-08 |
| Durable jobs, workers, retries | NFR-PERF-002, NFR-REL-002 | D-09 |
| Encryption and key management | NFR-SEC-002 | D-10 (gaps G-21, G-22) |
| Off-device processing disclosure | NFR-PRIV-006 | D-07 |

Nothing was added to the database schema, no migration was written, and no API contract changed.

**Engine selection is not configurable yet, on purpose.** A setting whose only valid value is `none` would describe a choice that has not been made. When the evaluation names an engine, selection becomes a change to `build_document_extractor` — and a configuration key at that point, if more than one engine is retained.

## 5. Where the engine gets plugged in

```python
# app/services/extraction.py
def build_document_extractor(settings: Settings) -> DocumentExtractor:
    ...
```

One function. Adding an engine means:

1. Add its implementation class beside `UnconfiguredExtractor`, in this module and nowhere else.
2. Add its runtime dependency to `pyproject.toml` — **not before the evaluation selects it**.
3. Select it in `build_document_extractor`.

Nothing above `app/services/extraction.py` changes. A test enforces the boundary: no module under `app/` may import a known OCR engine or hosted AI provider, and only `extraction.py` may name a concrete extractor.

An engine is eligible only if it can meet the guarantees the port encodes:

- a per-value confidence with stable meaning — **AR-AST-001** ("usable by BR-001");
- the ability to return nothing rather than a forced answer — **AR-AST-002**;
- provenance sufficient to explain a value by its source — **AR-AST-006**, **FR-OCR-007**;
- multi-page documents handled as one document — **FR-OCR-008**;
- operation entirely within DOCURA's own infrastructure — the self-hosted half of D-01.

An engine that is accurate but cannot produce a meaningful confidence is **not eligible**, however well it scores.

## 6. How this supports evaluating multiple engines

- **Two engines can be run over the same corpus through one interface**, with no other code aware of the difference — which is what makes a comparison a comparison rather than two separate integrations.
- **`ExtractionResult` records `engine` and `engine_version`.** A threshold calibrated against one engine version is not evidence for another (gap G-03 in the decision register), so every result carries the identity of what produced it.
- **`metadata` carries engine-neutral run facts** — timings, engine settings — and never document content or extracted personal values (NFR-PRIV-007).
- **`is_available()` separates "no engine" from "extraction failed"**, so an evaluation harness cannot mistake an unconfigured environment for a poor result.
- **Regions are page-relative fractions, not pixels.** An engine reading a 200-DPI scan and one reading a PDF text layer do not agree on a unit; they do agree on "a third of the way down the page". Without this, region output from two engines would not be comparable.

## 7. Privacy and security posture

- **No external transmission.** Nothing in this change contacts a network service, and no hosted provider dependency exists. D-01's self-hosted choice is enforced by the dependency test, not merely stated.
- **No document contents are logged.** The only log line added is at construction: it records that no engine is configured, and nothing about any document.
- **The placeholder never reads document bytes.**
- **Encryption is unaffected and unresolved.** NFR-SEC-002 covers "documents and extracted information"; nothing here persists extracted information, so the gap recorded as G-21/G-22 is neither closed nor widened.

## 8. Status summary

| Item | Status |
| --- | --- |
| Extraction interface | **Implemented** |
| Engine-neutral result type | **Implemented** |
| Placeholder that refuses honestly | **Implemented** |
| Injection and substitution | **Implemented** |
| OCR engine | **TBD — pending held-out evaluation** |
| Processing pipeline (D-09) | Not started |
| Extracted-information model (D-08) | Not started |
| Field definitions, thresholds, sensitivity rules | Not started — blocked on D-03, D-05, D-06 |
| Sprint 3 document vault | Unchanged |
