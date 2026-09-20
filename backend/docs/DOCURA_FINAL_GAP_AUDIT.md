# DOCURA Final Gap Audit (post manual E2E)

Repository-wide audit of every remaining requirement against `backend/step3.pdf` (authoritative),
the current architecture, the engineering reports (`S6_OCR_EVALUATION_REPORT.md`,
`S6_NEXT_CORPUS_PLAN.md`, `S6_CORPUS_INTAKE.md`), the automated suites, and the manual E2E
evidence supplied by the owner. **No code, annotations, thresholds, or engine selection were
changed to produce this audit.** No requirements were invented; where a requirement is
underspecified in `step3.pdf`, it is marked as a decision, not resolved here.

## Method & evidence base
- Requirement inventory extracted from `step3.pdf` (≈259 IDs across FR/NFR/AR/BR families).
- Automated coverage verified this session: **backend 617 tests (green)**, **extension 188 (green)**,
  frontend suite (green), `ruff`/`mypy` clean.
- Manual E2E confirmed by owner: auth, upload/vault, candidate OCR flow, record creation,
  chatbot+Gemini, Google Forms detection/autofill, approval/safety boundaries, no-submit boundary,
  export/search basics.

## Categories
- **A — COMPLETE**: implemented + tested (automated and/or manual).
- **B — ENGINEERING WORK**: implementable now, no new product decision or external evidence needed.
- **C — PRODUCT/PM DECISION**: requirement underspecified in `step3.pdf` (marked TBD / blocked on an assumption).
- **D — EXTERNAL EVIDENCE**: needs a real corpus / study / security evidence before it can be met.
- **E — FUTURE / OUT OF MVP**: `step3.pdf` marks it FUTURE / WON'T.

---

## A — COMPLETE (implemented + tested)
Grouped by family; representative IDs and their evidence. These do **not** block production or demo.

| Family (IDs) | Current implementation | Evidence |
|---|---|---|
| Auth FR-* (register/login/session/reset) | `auth_service.py`, `/auth`; password reset delivery | `test_auth`, `test_auth_logging`, `test_password_reset`, `test_reset_delivery`, `test_register_http`; manual E2E |
| Upload & validation FR-UPL-001..007 | `document_service.py`, `document_validation.py`, `/documents` | `test_documents`, `test_processing`; manual E2E |
| Vault / retrieval / versioning FR-DOC-001..006 | `document_service.py`, storage | `test_documents`, `test_storage`; manual E2E |
| OCR pipeline plumbing FR-OCR-001/007/008/009 | seam `extraction.py`, `pdf_rasterizer`, Tesseract **candidate** adapter, blocks/pages/regions, safe failure | `test_extraction`, `test_pdf_rasterization`, `test_ocr_candidate_adapter`, `test_dev_ocr_upload`; manual candidate flow |
| Structured record FR-INF-001/002/003/004/005/006/008 | `current_record.py` (derivation, provenance, confidence, conflict-surfacing, dup dedup, normalization) | `test_current_record`, `test_current_record_dedup`, `test_record_api`, `test_attribute_observations` |
| Classification FR-OCR-002/003 + AR-AST-002 | `classification.py` (type + confidence, "unrecognised") | `test_classification` |
| Search (filename + attribute) FR-SRCH-001/003/004 | `search.py`, `/search` | `test_search_and_export`; manual E2E |
| Export & account FR-ACC-006/007, deletion | `/record/export`, account deletion | `test_search_and_export`, `test_account_deletion` |
| Audit FR-AUD-001..006 | audit actions (extension→worker→backend), value-free | `test_document_logging`, `test_auth_logging`, `test_extension_backend_contract` |
| Chatbot + Gemini FR-* (conversational record access) | `services/chatbot/*`, `/conversations`, intent seam | `test_chatbot`, `test_llm_intent`; manual E2E |
| Extension: activation, detection, interpretation, mapping, retrieval, fill, approval, no-submit FR-EXT/FR-FRM/FR-FLD/FR-FILL/FR-DRP/FR-REV/FR-SENS/FR-APR/FR-SUB | content/detect/interpret/mapping/retrieval/autofill/sensitivity/session; Google Forms adapter | extension suite (188): `detect`, `interpret`, `mapping`, `retrieval`, `autofill`, `sensitivity`, `session`, `googleForms`, `integration`; `test_form_sessions`; manual E2E |
| Safety business rules BR-002..BR-020 | enforced across record/extension/approval | above suites; manual approval + no-submit E2E |

---

## B — ENGINEERING WORK (doable now, no decision/evidence needed)
**None identified that block MVP.** Every remaining functional gap is contingent on a decision
(C) or external evidence (D), not on code that could simply be written today. The one small,
clearly-optional item:

| ID | Current | Missing piece | Category | Blocks? |
|---|---|---|---|---|
| FR-SRCH-005 (filter by type & date) | search by filename + attribute value only | add type/date filters to `/search` | B (but MVP **COULD**, not MUST) | No |

---

## C — PRODUCT / PM DECISION (underspecified in step3.pdf)
| ID | Current implementation | Exact missing piece | Blocks? |
|---|---|---|---|
| FR-INF-007 / FR-FLD-003 / FR-SENS-001 (sensitivity tier per attribute & field) | 3-tier framework + per-instance approval implemented; production classifies every tier as `unknown` | The **tier assignment content** — which attributes/fields are routine/sensitive/consequential. Blocked on **assumption A-5** ("this boundary must be set by users, not us"). A decision (or study S-4) is required. | Demo: no. Production auto-fill of sensitive data: yes. |
| OCR strict-metric granularity (report §3b, PATH A vs B) | strict whole-block metric authoritative; containment diagnostic separate | Decide line-granularity annotation (A) vs adding a formal containment field-read metric (B). Owner: S-6 / D-02 methodology. | Blocks meaningful reading of S-6 accuracy numbers. |
| NFR-AVL-001 (availability target) | none | a published target "before public release" | Pre-public-release only |
| NFR-SCL-003 (per-user record size limits) | none | defined/communicated limits | Pre-public-release only |
| FR-DOC-008 (deletion grace period) | deletion implemented | the **period value** (TBD) | Pre-public-release only |
| FR-MATCH-006/007/010 (preparation "quality floor") | copy/convert paths exist | the **quality-floor value** (TBD) | Feature-completion of prep only |

## C/D — study-validated numeric targets (decision informed by a study)
| ID | Missing | Study |
|---|---|---|
| NFR-PERF-* (session length / stall targets) | target values | S-2 / S-5 |
| NFR-USE-002 (interruption budget) | budget value | S-4 / S-5 |

---

## D — EXTERNAL EVIDENCE (needs real corpus / study / security evidence)
| ID | Current implementation | Exact missing piece | Blocks? |
|---|---|---|---|
| BR-001 (automatic-action threshold) | unset by design | validated threshold from **S-6** on a real held-out corpus | Blocks production auto-fill; not demo |
| FR-OCR-004/005 (extract defined field set per type, per-field confidence) | controlled slice (`person.full_name`, `person.date_of_birth`) + confidence plumbing; full set gated | per-type extraction validated on real documents (S-6 / ASM-001) | Blocks production extraction breadth |
| FR-OCR-006 (mark below-review-threshold values) | plumbing present | the review threshold (tied to BR-001/S-6) | Blocks production confidence-gating |
| AR-AST-008 (held-out eval before thresholds) | full harness built; run on 3 real docs | a **larger real, imperfect, multi-subject corpus** (current: 3 docs, 1 subject) | Blocks engine selection & thresholds |
| Production OCR engine selection (D-02) | `UnconfiguredExtractor`; Tesseract is candidate only | evidence sufficient to select; only Tesseract reproducible here → comparison incomplete | Blocks production OCR |
| FR-SRCH-002 (search extracted text) | not implemented — **no production extracted text exists** (OCR unselected) | production OCR must be enabled first (⇒ S-6), then index blocks | MVP MUST, but chained to OCR evidence |
| ASM-001 (MVP type inclusion) | candidate type set defined | S-6 result per type | Blocks final type scope |

Security evidence (S-6 is OCR; other assurance items): standard pre-release security review/pen-test
evidence is not a `step3.pdf` functional requirement and is out of this functional audit's scope.

---

## E — FUTURE / OUT OF MVP (step3.pdf marks FUTURE / WON'T)
FR-OCR-011 (handwriting), FR-OCR-012 (scripts/languages beyond MVP), FR-INF-010 (missing-info
prompts), FR-SRCH-006 (natural-language query), FR-AMB-008, FR-FLD-008/009/010 (cross-session
learning etc.), FR-FRM-008 (embedded frames), FR-EXT-008, FR-DRP-* future, FR-REV-007,
FR-SUB-005, FR-APR-006, FR-AUD-007, FR-ACC-009/010, FR-DOC-009/010, FR-UPL-008/009.
**Count: 20 requirement IDs.** None block MVP demo or production.

---

## Summary counts (by requirement ID)
Counted exactly for B/C/D/E from enumeration above; A is the remaining MVP-scope requirements
across the families in the A table (verified by the cited suites + manual E2E).

| Category | Count | Notes |
|---|---|---|
| **A — COMPLETE** | ~200 | the bulk of MVP MUST/SHOULD functional + all safety BR-002..020 |
| **B — ENGINEERING WORK** | **1** | FR-SRCH-005 only, and it is MVP **COULD** (optional) |
| **C — PRODUCT/PM DECISION** | **~8** | sensitivity tier assignment (3 IDs), OCR metric granularity, 4 TBD targets |
| **D — EXTERNAL EVIDENCE** | **~7** | BR-001, FR-OCR-004/005/006, FR-SRCH-002, engine selection, AR-AST-008/ASM-001 |
| **E — FUTURE** | **20** | enumerated above |

(Counts are requirement-ID tallies; A is approximate because it aggregates uniformly-complete
families — every non-A item is enumerated explicitly so the classification is auditable.)

---

## Final answers
1. **COMPLETE count:** ~200 MVP requirement IDs (all listed A families; verified by 617 backend +
   188 extension + frontend tests and manual E2E).
2. **ENGINEERING WORK count:** **1** — FR-SRCH-005 (type/date search filter), and it is MVP COULD, not MUST.
3. **PM DECISION count:** **~8** — chiefly the sensitivity tier assignment (A-5) and the OCR
   strict-metric granularity (PATH A/B); plus 4 pre-release TBD targets.
4. **EXTERNAL EVIDENCE count:** **~7** — all in the OCR/S-6 chain (threshold, per-type extraction,
   engine selection, extracted-text search, larger real corpus).
5. **FUTURE count:** **20** — enumerated in section E.
6. **Exact next engineering task (if one genuinely exists):** **None that is MVP-blocking.** The
   only pure-engineering item is optional (FR-SRCH-005). FR-SRCH-002 is *not* pure engineering —
   it is blocked on production OCR (D). So there is **no code that should be written next** to
   advance the MVP; the next real work is a decision + evidence, not code.
7. **Decisions you must make:** (a) the **sensitivity tier boundary** (A-5) — which attributes/
   fields are routine vs sensitive vs consequential; (b) the **OCR strict-metric granularity**
   (PATH A: line-granularity annotations, or PATH B: add a formal containment metric); (c) the
   pre-release TBD targets (availability, size limits, deletion grace period) — only if moving to
   public release.
8. **Evidence/documents still required:** a **larger real, imperfect, multi-subject S-6 corpus**
   with ground truth (current: 3 docs, 1 subject) → then the S-6 result sets the BR-001 threshold,
   the production OCR engine, per-type inclusion (ASM-001), and unblocks extracted-text search
   (FR-SRCH-002). No other engine is reproducible in this environment, so the engine comparison
   cannot be completed here.
9. **Ready for final demo/documentation?** **Yes for demo/documentation.** Every manually-tested
   flow works, safety boundaries hold, and the architecture is complete. The MVP is demoable and
   documentable today; production *auto-fill of extracted values* is the only capability held back,
   and it is held back correctly (BR-001 unset, OCR unselected) pending S-6 evidence.
10. **Should any code be written next?** **No.** No MVP-blocking engineering task exists. The next
    steps are a PM decision (A-5 sensitivity boundary; metric granularity) and external evidence
    (larger real S-6 corpus). Writing code before those would be premature and, for thresholds/
    engine selection, would violate AR-AST-008 and BR-001.

**Guardrails honored:** no requirements invented, no scope invented, no product decision silently
resolved, no code/annotation/threshold changed, no production OCR engine selected. Not committed,
not pushed.
