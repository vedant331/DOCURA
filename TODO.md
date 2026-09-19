# DOCURA — TODO (as of M19, 2026-09-17)

Priority: **P1** = do next when unblocked · **P2** = should · **P3** = later/optional.
Blocked items name their blocker. Nothing here is in-flight; M19 is complete and green.

## Completed
- [x] M9 — E2E integration audit + `POST /form-sessions/{id}/actions` backend seam.
- [x] M10 — Safe autofill of `person.full_name` into the controlled form; worker-mediated
      record access; provenance data-attrs; manual-test doc + `mock-form-m10.html`.
- [x] M11 — Deterministic controlled-form-scoped mapping (`isControlledForm`); expansion beyond
      `full_name` concluded BLOCKED.
- [x] M12 — G-15 default=sensitive adopted for controlled MVP (PM-approved M12-D3);
      `person.date_of_birth` authored as vocab v0.2-draft (consent-gated, tier TBD).
- [x] M14 — S-6 OCR evaluation audit → BLOCKED (no corpus); extractor seam confirmed ready.
- [x] M15 — Extension→backend value-free action audit integration; endpoint verified vs Postgres.
- [x] M16 — Generic field-interpretation foundation (resolved/ambiguous/unknown).
- [x] M17 — DOM semantic metadata capture (label/aria/placeholder/title, value-free); browser-validated.
- [x] M18 — Interpreter provider architecture with defensive validation vs released vocabulary.
- [x] M19 — S-6 corpus + evaluation harness (`app/evaluation/`, CLIs, 17 tests).
- [x] Dev seed — test record for `vedantskadam24@gmail.com`.
- [x] Context handoff package (this set of files).

## In progress
- [ ] (none)

## Remaining — housekeeping (unblocked)
- [ ] **P2** Commit the uncommitted M9–M16 working-tree changes (see CONTEXT_HANDOFF §8).
      **Only when the user says so** — the standing rule is do-not-commit. Suggested grouping:
      one commit for the M9/M15 action endpoint, one for M12 `person.date_of_birth` vocab v0.2,
      one for docs/fixtures/seed script.
- [ ] **P3** Full-suite async isolation flake: add a reliable repro, then consider a
      session-scoped event loop or `NullPool` in the `db_engine` fixture. Do NOT change shared
      fixtures without a repro (CONTEXT_HANDOFF §9.1).

## Remaining — governance-blocked (do NOT self-start)
- [ ] **P1(external)** S-6 real corpus collection (consented, de-identified, split-sealed) →
      then run the M19 harness → then select an OCR engine on evidence (D-02 / G-02).
      Blocker: no corpus exists; blocked on data collection + governance approval.
- [ ] **P1(external)** Resolve G-14/G-15 sensitivity tiers (currently TBD) → flip vocabulary
      `releasable` where justified. Blocker: assumption A-5, studies S-1 / S-4.
- [ ] **P2(external)** Any new released canonical attribute. Blocker: needs G-13-A authoring +
      normalization rule + G-14/G-15 tier + PM approval. (Email/phone/gender are NOT candidates.)
- [ ] **P2(external)** BR-001 acceptance threshold (currently TBD, G-04).

## Known optional frontend work (mentioned, not a committed milestone)
- [ ] **P3** "DOCURA Frontend — Complete UI Build" was scoped in-conversation (routes, shell,
      form-session flows, backend integration, then visual refinement). Not started as its own
      milestone. Start only on explicit user instruction.

## Exact next step
Wait for the user's next instruction. Do not start any milestone, engine selection, new
attribute, or OCR work autonomously — all are blocked or user-directed. Before any backend work:
start Docker + Postgres, set `TEST_DATABASE_URL`, confirm green pytest + single Alembic head.
