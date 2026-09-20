# S-6 Corpus — Gaps and Next-Intake Plan

> **Expansion attempt (latest): STOPPED AT THE EVIDENCE BOUNDARY.** A corpus-expansion pass found
> **no additional real, consented documents** in the repository/environment beyond the 3 already
> ingested (all one subject). Per the S-6 rules, no documents/annotations were fabricated, no
> synthetic evidence was created, no engine was selected, and BR-001 stays UNSET. The corpus is
> unchanged and still VALID; the intake tooling/workflow is ready. The blocker is now purely the
> availability of real documents from more subjects — a human-supplied artifact. See "Exact next
> human action" at the end of this file.

Companion to `S6_OCR_EVALUATION_REPORT.md`. Records what the current real corpus contains, what it
lacks for a defensible S-6 evaluation, and how to add real documents. **No corpus sizes here are
official requirements** — `step3.pdf` states none. Numbers below are clearly-labelled engineering
proposals only. No documents or ground truth are fabricated.

## Authoritative constraints (from step3.pdf)
- **AR-AST-008 (MVP MUST):** assisted components evaluated against a **held-out corpus of real,
  imperfect documents** *before any threshold is set*.
- **§7.1 / ASM-001:** a candidate type ships with structured extraction only if it "can meet the
  review threshold **on real documents**" (S-6); otherwise it becomes store-and-search only.
- **BR-001:** automatic-action threshold is TBD, to be validated by S-6.
- No corpus size, subject count, or per-type count is specified by the requirements.

## Current corpus composition (`var/s6_corpus/`, version `v0`)
| dimension | current state |
|---|---|
| subjects/persons | **1** (all three documents are the same person) |
| documents | 3 |
| pages | 4 |
| document types | 3: `aadhaar` (1), `pan` (1), `marksheet_12` (1) |
| multi-page coverage | 1 doc (marksheet, 2 pages) |
| splits | `held_out` = 3; `development` = **0**; `train` = 0 |
| annotations | 3/3 valid; 8 expected fields |
| degradation variety | not recorded / minimal (personal_owned scans) |
| consent / de-id | consented + deidentified (per manifest) |
| raw sources | `s6_sources/` and `var/` gitignored |

## Gaps blocking a defensible evaluation
1. **Single subject.** One person cannot show generalisation; results are anecdotal.
2. **One document per type.** No per-type replication → no per-type reliability estimate (ASM-001).
3. **Empty `development` split.** Nothing to tune/calibrate on without touching held-out.
4. **No degradation spread.** Missing skew/rotation, blur/compression, low-resolution, uneven
   lighting/shadow, multi-source variety that AR-AST-008's "imperfect" implies.
5. **Engine comparison incomplete.** Only Tesseract is reproducible in this environment (Windows,
   Python 3.14, no GPU; PaddleOCR/EasyOCR/docTR uninstallable here).
6. **Methodology (RESOLVED — PATH B):** strict whole-block/page exact-match is authoritative;
   containment/value-read is a separate, non-authoritative diagnostic (report §3c). No longer a gap.

## Engineering proposal (NOT a requirement)
Purely as a target to make the strict metric statistically meaningful and cover ASM-001 per type:
- **≥ 3–5 subjects**, none overlapping between `development` and `held_out`.
- **≥ 5–10 real documents per candidate type** you intend to ship extraction for
  (`aadhaar`, `pan`, `address_proof`, `marksheet_10`, `marksheet_12`, `semester_result`,
  `degree_certificate`).
- A realistic **imperfection spread** (genuine scans/phone photos: skew, blur, compression, low
  resolution, uneven lighting) rather than only clean copies.
- A sealed **held-out** split plus a separate **development** split; no subject or checksum crosses
  splits.

## Intake procedure (already built — see `S6_CORPUS_INTAKE.md`)
1. Place real, consented, de-identified documents in `s6_sources/` (gitignored).
2. Ingest each: `python -m scripts.s6_ingest --root var/s6_corpus --source <file> --id <type_seq>
   --document-type <type> --source-category <note> --consent consented --split <development|held_out>
   --deid deidentified --page-count <n>`.
3. Annotate `annotations/<id>.json` with real ground truth at the granularity chosen by the §3b
   methodology decision. **Never edit annotations to raise a score.**
4. Validate: `python -m scripts.s6_validate --root var/s6_corpus` (must print VALID).
5. Evaluate held-out: `python -m scripts.s6_evaluate --root var/s6_corpus --engine tesseract
   --split held_out --write`.

## Invariants to preserve on every intake
- corpus validator passes; no duplicate ids; no checksum leakage; no held-out leakage.
- consent + de-identification recorded truthfully; person grouping tracked.
- raw sources remain gitignored; no personal values in committed files, logs, or results.
- strict metric stays authoritative; containment stays diagnostic; BR-001 stays unset;
  production stays `UnconfiguredExtractor` until the evidence legitimately supports otherwise.

## Exact next human action (evidence boundary)
The only remaining blocker is real data, which cannot be created here:
1. Collect **real, consented, de-identified** documents from **≥3 additional subjects** (engineering
   proposal, not a step3.pdf requirement), spanning the candidate types you intend to ship
   (Aadhaar, PAN, address proof, 10th/12th marksheet, semester result, degree certificate, etc.),
   with genuine variation (phone photos, skew, blur, compression, low-res, multi-page).
2. Place them in `backend/s6_sources/` (gitignored), then ingest each with `scripts.s6_ingest`
   using a **person-level split** (all of one subject's documents in the SAME split; a sealed
   `held_out` and a separate `development`).
3. Annotate from the printed documents (approved canonical vocabulary; strict authoritative metric
   per PATH B; never OCR output as ground truth; never edit annotations to raise scores).
4. `scripts.s6_validate --root var/s6_corpus` must print VALID (no duplicate ids/checksums, no
   held-out leakage).
5. Then run `scripts.s6_evaluate` on `held_out` and record the versioned results.

Until step 1 is provided, S-6 remains blocked on external evidence; engine selection and BR-001
stay open by design.
