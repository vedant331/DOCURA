# Final Product Decisions — RESOLVED

Both decisions below have been **decided by the owner and applied**. This document records the
resolutions. Details live in `SENSITIVITY_GOVERNANCE_DECISION.md` and `S6_OCR_EVALUATION_REPORT.md`
(§3b/§3c).

- **D-A5 (sensitivity tiers): RESOLVED** — approved tier table applied (see D-A5 below).
- **D-OCR-METRIC (metric granularity): RESOLVED — PATH B** (strict metric authoritative; containment
  retained as a separate, non-authoritative diagnostic).

---

## D-A5 — Sensitivity tier assignment — RESOLVED
- **Resolution (approved):** full_name = routine; age = routine; date_of_birth = sensitive;
  email = sensitive; phone = sensitive; address = sensitive; pan_number = consequential;
  aadhaar_number = consequential. **Un-tiered default = sensitive.** Applied via the config +
  extension seam (`canonical_attributes.demo.toml` `sensitivity` ↔ `extension/src/demo.js`
  `DEMO_TIERS`); routine → auto-fill, sensitive/consequential → per-instance approval + masking,
  consequential pinned at the BR-020 floor; declaration/consent controls remain never-accepted.
- **Exact question (as posed):** For each supported canonical attribute, which tier applies —
  **routine / sensitive / consequential** (or explicitly defer)? And: does an un-tiered attribute
  default to *sensitive* (approval) or *routine* in production?
- **Relevant requirement IDs:** FR-INF-007, FR-SENS-001, FR-FLD-003/004, FR-SENS-002/004/005/006,
  FR-APR-005, BR-005, BR-006, BR-007, BR-020, AR-AST-007; assumption **A-5**; register **D-06**,
  G-14/G-15. (Document-02 Table 13.1 is examples tied to A-5, **not** authoritative.)
- **Current implementation:** production classifies every attribute **`unknown`** and refuses to
  disclose (conservative floor). Only the declaration/consent **control** is fixed *consequential*
  (BR-006/FR-FLD-004). Approval is per-instance/exact-scope/one-time; masking + raise-only + floor
  are enforced.
- **Available options:** per attribute, assign routine | sensitive | consequential | defer; plus
  choose the un-tiered **default** (sensitive-by-default vs routine-by-default).
- **What changes if chosen:** affects **autofill, reveal/masking, approval prompts, chatbot
  disclosure, and document display** for that attribute (see the consequences table in the
  sensitivity pack). Nothing changes until a follow-up implementation task injects the policy.
- **Blocks S-6?** **No** — S-6 (OCR text extraction quality) does not depend on tier assignment.
- **Blocks production?** **Yes for production auto-fill/disclosure of those attributes.** With tiers
  `unknown`, DOCURA safely refuses to disclose; production disclosure needs this decision (and,
  separately, the BR-001 threshold).

## D-OCR-METRIC — S-6 field-metric granularity — RESOLVED (PATH B)
- **Resolution (approved):** **PATH B** — the strict whole-block/page field exact-match stays the
  authoritative metric (normalized accuracy and missing-field rate derive from it); containment/
  value-read is retained as a **separate, explicitly non-authoritative diagnostic**. Ground truth is
  preserved and not rewritten. Documented in `S6_OCR_EVALUATION_REPORT.md` §3c. (No production OCR
  engine selected; BR-001 stays UNSET.)
- **Exact question (as posed):** Keep the strict whole-block/page metric authoritative and **fix annotation
  granularity** (PATH A), or keep the strict metric unchanged and **add a formal, separately-named
  containment/value-read diagnostic** (PATH B)?
- **Relevant requirement IDs:** AR-AST-008; §7.1/ASM-001; BR-001 (threshold TBD via S-6). step3.pdf
  is **silent** on matching granularity (metric lives in `metrics.score_document`, cites D-02 §8.2).
- **Current implementation:** strict exact/normalized = 0.25 (authoritative); containment 8/8
  (diagnostic only, not substituted). Values are read but embedded in longer OCR lines.
- **Available options:** PATH A (annotation convention change; no code) or PATH B (add a new,
  methodology-defined diagnostic metric; strict metric + ground truth untouched).
- **What changes if chosen:** the annotation/methodology direction for the next S-6 cycle and how
  OCR configurations are compared (see §3c for what each path does and does not measure). No change
  to the strict metric's authority or the ground truth in either case.
- **Blocks S-6?** **Yes** — a meaningful next S-6 evaluation needs the granularity settled so the
  numbers are interpretable; today the strict number is segmentation-noise-dominated at this size.
- **Blocks production?** **No directly**, but production OCR selection ultimately depends on S-6,
  which this decision gates.

---

## Summary
| Decision | Status | Blocks S-6? | Blocks production? | Requirements determine it? |
|---|---|---|---|---|
| D-A5 (sensitivity tiers) | **RESOLVED + applied** | No | No longer (policy applied; production disclosure still needs BR-001) | No — owner decided (A-5) |
| D-OCR-METRIC (metric granularity) | **RESOLVED (PATH B)** | No longer | No (indirect via S-6) | No — owner decided (D-02 §8.2) |

**After both decisions:** the next S-6 cycle can be annotated/measured consistently (D-OCR-METRIC),
and a follow-up implementation task can inject the approved sensitivity policy (D-A5). Neither
decision touches **BR-001** (stays UNSET), the **production extractor** (`UnconfiguredExtractor`),
the OCR engine selection, or the existing S-6 ground truth — those remain gated on the larger real
corpus and evidence described in `S6_NEXT_CORPUS_PLAN.md`.
