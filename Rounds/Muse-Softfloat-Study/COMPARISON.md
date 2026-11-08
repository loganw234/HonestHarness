# The comparison: three Claude audits, the Muse audits, the case report, and this study

2026-11-08. This file was written after the report's draft 3 (`6002f90`) was verified. This is draft 3. Both of verifier-C's passes are in `reports/verifier-C.md`.
- **Draft 2** took verifier-C's pass 1 on draft 1 (`bc058e5`): five wrong items, five restates and ten notes.
  - It also fixed three errors the lead found while checking them: two items it had listed as found only by the Claude audits, and the Muse column's scope.
- **Draft 3** takes verifier-C's pass 2 on draft 2 (`23b0267`): one restate and four notes.
  - The lead fixed them and checked each line by command, since verifier-C's passes were spent.
- **The order.** The lead read the three Claude audit reports then, for the first time. It lifted the fence for itself alone (the ledger, 11:12:13), and fetched the reports at Logan's approval (12:22:43). Of the study's other agents, only the comparison's verifier, verifier-C, has read them.
- **Its sources:**
  - the three reports, at the branch tips below;
  - P2's table of the Muse audits' findings (`parcels/P2/data/escapes.csv`): the full audit's 43 findings and the adherence audits' 36 slips;
  - the case report;
  - this study's report.

  A finding is named by its report's own ID. The Muse audits' findings are named by P2's IDs: `M`, `S`, `N` and `T` for the full audit, and `A` for the adherence audits' slips. Outside the Muse column, a slip is written "P2's A01" and so on, so that it is not read as one of Claude audit A's IDs, which are written "A H1" and so on.

## The audits

| | When, and at what | Who | How |
|---|---|---|---|
| **Claude audit A**: `claude/affectionate-curie-lrfomb` (`e8e77d7`), `docs/AUDIT-2026-10-31.md` | 2026-10-31, at `main` `a2241fc` (2026-10-30) | A Claude Code lead with seven reading subagents | A Linux container. Its own oracles: hardware differentials over 160 million cases, 17.2 billion F16C conversions, character conversions against CPython, the Clause 9 functions against mpmath. 2 High, 18 Medium, 23 Low, 8 observations |
| **Claude audit B**: `claude/gifted-hawking-w4r6fu` (`9db8763`), `audit-2026-10-31/REPORT.md` | 2026-10-31, at `a2241fc` | A Claude lead with eleven audit agents | A Linux container with Berkeley SoftFloat and TestFloat 3e, MPFR, exact arithmetic and stock REBOUND: about 1.5 × 10^10 differential checks. 1 High, 14 Medium, 10 Low, 1 Info |
| **Claude audit C**: `claude/loving-carson-qmwhhz` (`f2ed688`), `docs/audit/2026-10-31-audit-report.md` | 2026-10-31, at `a2241fc` | A Claude Code lead with seven review agents | A Linux container: about 388 million checks by the lead, about 1.1 billion by the agents, exhaustive binary16 add, mul and div, and mutation probes. 2 High, 9 Medium, then Low and Info |
| **The Muse full audit**: `<muse>/scratch/audit-full/REPORT.md` | 2026-11-01, at `a49991f`, after the seal | Eight read-only auditors: the library's on Wonder, the rest on Spark | Identify-only, inspection, no board flashing, with the Claude reports fenced. 43 findings: 4 major, 2 major-suspected, 22 minor, 15 nits (P2 §Task 2) |
| **The Muse adherence audits**: `<muse>/scratch/audit-adherence-2`, `-final` and `-seal` (P2's `A2`, `AF` and `AS`) | 2026-10-28 at `7c3819c`, 2026-10-29 at `bc807e6`, and 2026-11-01 at the seal, `751d1d6` | A read-only auditor each | Audits of the methods in the record, not of the code. 36 slips (P2's `A01` to `A36`) |
| **The Muse case report** | 2026-11-01 or 02, at `a49991f` | The Muse lead | The lead's own account: 17 observations and 18 proposals |
| **This study** | 2026-11-08, at `b78af18` | Three Sonnet parcels, Haiku verifiers and an Opus lead | It read the record. It did not audit the code or run an oracle |

**The audits are independent in one direction.**
- The three Claude audits ran the same day on the same commit, each in its own container.
- The Muse round was fenced from them: the Muse lead's ledger l856 ("three Claude audit branches exist, not to be looked into") and l881. So where a Muse audit or the case report reaches a Claude audit's finding, it reached it independently.
- The other direction does not hold. The Claude audits had the Muse round's audit bundle, and A H1 cites the final adherence audit's report from it. Where a Claude finding meets an earlier adherence slip, the Claude side may have started from it.

## What the three Claude audits say, in their own summaries

All three put the library's arithmetic in good shape. Each wrote its own oracles, none found a wrong result for ordinary inputs, and all three place the weight of their findings elsewhere:
- **A:** "in claims, gates and record-keeping, not in the arithmetic";
- **B:** "in the machinery around the evidence";
- **C:** "in the verification story around the library, not in the library".

That is this study's reading of the Muse record, reached from the record alone (the report, Q3 and Q6). For ordinary inputs, the audits show the arithmetic half far more strongly than this study could, by billions of independent checks.

## What every side found

The Muse column cites P2's IDs. This study's column cites the report's questions and P2's IDs.

| Finding | Claude A | Claude B | Claude C | Muse audits | Case report | This study |
|---|---|---|---|---|---|---|
| The README's "gated against Berkeley TestFloat" claim, which no gate executes | H2, M15 | F-04 | H1 | M1 (major) | obs 8, its P9 | Q3: the sharpest escape |
| The site's interval hash and timing, stale after the wave 6 restamp | M5 | F-07 | L11 | M2 (major) | obs 9, its P10 | Q3: among the F1 escapes |
| A rounding argument out of the enum (value 5) silently accepted | L1 | F-18 | L2 | M3 (major) | Not an observation: in its disposition of the full audit (l342-347) | Not an escape (M3): verifier-w5attr raised it, and verifier-w5aug cleared it |
| Evidence paths outside the gate (workloads, site, bench capture) | M4 | F-15 | | Loosely, M4 (major): a committed bench budget its capture window cannot complete | obs 11, its P12 | Q3 |
| The board lock, check-then-create | L16 | F-20 | | N8 (minor) | obs 14, its P15 | Q3: the "stale lock" escape (N9) |
| `data.json`'s base stamp naming a tree without its counted rows | L18 | | L11 | N17 (minor) | obs 10, its P11 | Q3: an F1 escape (N17) |
| Post-verdict fixes merged without a re-check | M14 | | | A27, the seal adherence audit's slip | obs 3, its P4 | Q4; P2's A27 |
| The public claims about the verification protocol, against the record: a verifier before every merge, and the defects pre-ledgered | H1 | F-17 (a) | L12 | A16 and A32 on the claims; A01, A02, A03 and A06 on the record | | Q1: about 30 of 44 lead commits unverified (P2's A02); Q3: P2's A16 and A32 among the 24 slips the record had not raised |
| Media taking most of the clone | L19 | F-09 | L13 | N22 (minor) | | Q3: an escape, in no family |

**Three rows have an entry in every column:** the Berkeley sentence, the stale site interval and the rounding value. In those rows, two kinds of cell are not independent of the full audit:
- this study's cells, which come from P2's table of the Muse audits' findings;
- the case report's rounding cell, which is its disposition of the full audit's findings.

**On the protocol row, the earliest Muse audits came first.**
- **The first adherence audit** (P2's `A2`, 2026-10-28) found the README's universal claim false (P2's A16). It also found the record behind it:
  - Wave 1's merges came before their verdicts (P2's A01);
  - the IAS15 Pico firmware parcel was merged with no verifier (P2's A03), and with no planted copy. The Muse lead's ledger says so at l303: "No planted-copy verification was run for this branch";
  - about 30 of 44 lead commits had no named verifier (P2's A02);
  - key hashes were not committed before dispatch in Waves 1 to 5 (P2's A06).
- **The final adherence audit** (2026-10-29) graded the universal claim "STILL OPEN". A H1 cites that grade from the bundle.
- **The seal audit's slip, P2's A32,** came after the Claude audits.
- **A H1 adds a count of its own:** for 120 of 160 plants, no key hash was committed before the grades landed.

## What only the Claude audits found

None of the Muse audits, the case report or this study found these. That is by P2's table of the Muse audits' 43 findings and 36 slips, and by the case report's observations.

- **The gate has no external anchor.** The manifest and the expected counts are regenerated by the same run that checks them, so deleting or weakening committed vectors still passes:
  - B F-01 (High): 411,213 down to 343,077 vectors, still PASS;
  - C H2 (High): about 82,000 vectors removed, still PASS;
  - A M2: the same cause, shown with a stale binary rather than deleted vectors.

  It goes to the project's thesis that the gate is the product. Neither the Muse audits nor the case report names it.
- **Controls weaker than their names.**
  - A count-mismatch control that refuses without its mutation: A M1, B F-06, C M2.
  - A CI sanitize job that goes green with no sanitizer: A L15, C M1. The Muse full audit's N6 has the same shape on another control: the symbol scan skips by name and returns success on hosts without `arm-none-eabi-gcc`.
  - MPFR deciders wrong on LP64 hosts, so the binary64 oracle path cannot run on Linux or in CI: A M3, B F-06, C M7.
  - Tier 2 vectors that let gross mutants pass: C M9. B F-05 measures the whole suite instead: 80 % of injected defects caught, with the gaps named.
- **The library's edges.** Each needs pathological input or a non-default target:
  - a wrong value for decimal or hex inputs of about 100,000 digits: A M8, B F-02, C L4;
  - double rounding beyond 20 digits: A L5, B F-13, C L3;
  - a stack beyond the pico-sdk's 2 KiB default: about 2.4 KiB for the Pico example's decimal converter in A's measure, and about 3 KB worst case in B's (A M7, B F-12, C L5);
  - a buffer overflow in the test tooling's `hash_result`: B F-03, C M5;
  - an off-by-one in the wide arithmetic's normalisation, whose stated error bounds still hold with margin: A M18, B F-25, C L9.

  Audit A counts two of these as real library defects: the long inputs (M8) and the stack (M7).
- **Licensing and hygiene:**
  - GPL REBOUND fragments in an MIT-labelled script: A M6, B F-08, C M8;
  - the published wasm carrying local Windows paths: A L18, B F-15, C M8.
- **The record's integrity:**
  - **Planted sentences landed as accepted brief corrections:** A M10. See below.
  - **Ledger entries extended in place under earlier timestamps:** A M11.
    - A says the project's auditors never opened the lead's ledger. P2 found that the first adherence audit read its headings and sampled its bodies; the final and seal audits say they never opened it.
    - The adherence audits did find in-place edits elsewhere: passes rows restated after a push (P2's A14), and a pushed RECORD paragraph reflowed (P2's A36).
  - **The frozen bundle silently dropped the KissFFT trail:** A M12, C M6.
- **What the plant score measures** (A O1). Plants on the lead's own work were missed 4 of 25 times, against 3 of 135 on parcel work.

## What the Muse side found that the Claude audits could not

- **The wrong-tree verifier attempt** (the case report's observation 1; this study's P1 §5). It happened on 2026-11-01, the day after the Claude audits (the Muse lead's ledger, the entry at l874-876).
- **The process seen from inside** (the case report's observations 5 to 7, 12 and 16):
  - reports lost in the channel;
  - dead attempts, and processes that outlived their agent;
  - worktree path assumptions;
  - asset rights.

  None of these is in the Claude audits' findings lists.
- **The Ziv final stage's silent fallback,** the Muse full audit's major-suspected S5. Audit A covers the neighbouring ground (its M18 and O2) but not this finding.

## What the comparison shows about this study

- **Its scope.** It read the record and did not audit the code or run an oracle, as its plan said. The gate's anchoring, the controls, the deciders, the library's edges and the licensing were outside its reach.
- **Its main reading holds,** and the audits confirm it far more strongly than the study could: the arithmetic held on ordinary inputs, and the claims and the record did not. The audits also found defects at the library's edges, listed above, which a reading of the record could not reach.
- **It missed one record-integrity error within its reach,** which changes a figure in its report.
  - **Audit A's M10,** checked by the lead by command at `b78af18`: the brief corrections in rows 17, 18 and 19 of `docs/metrics/corrections.jsonl` are verifier-sf2's planted faults #4, #3 and #2 (`plants.jsonl` rows 59, 58 and 57). They are the inflated op count, the flipped owner pin and the denied ties-to-away mode. A's own counts are at `a2241fc`, where the metric had 22 rows; rows 17 to 19 read the same at both commits.
  - **The Muse record** landed them as accepted corrections. P2 took them, as `CJ17` to `CJ19`, for genuine errors in the lead's SF-2 draft.
  - **So the report's Q4 overcounted.** Of the 47 error rows, 42 are the lead's own genuine errors: P2's 45 lead-owned rows, by the owner column of `data/lead_errors.csv`, less `CJ17` to `CJ19`. The 3 plants are not, though the lead's landing of them as corrections is a record error of its own. Q4 says so from draft 4.
- **Its report left out the IAS15 parcel's unverified merge** until draft 5.
  - P2's table has it, as the first adherence audit's slip, P2's `A03`. The round itself had raised it: the merge body disclosed it.
  - P2's clause table has no row for a parcel merged without verification, and its nearest clause, C085 (the lead's own work), is marked skipped.
  - The report's draft 5 names it in Q1.

## What it says about the methods and the roles

- **The Claude audits found a High in the gate itself that no Muse check found: the gate has no external anchor** (B F-01 and C H2 at High, A M2 at Medium).
  - It escaped the round's planted copies, three adherence audits, the full audit and the case report.
  - The other High in the table, the Berkeley claim (A H2, C H1; B F-04 at Medium), the Muse full audit found too (M1), and so did the case report (observation 8).
  - The Claude audits differ from the Muse full audit in two ways at once:
    - **tooling:** Linux containers with Berkeley, MPFR and ARM tools, mutation testing and oracles at billions of cases;
    - **model:** Claude leads with Claude agents, against eight auditors on Wonder and Spark working by inspection, with no board flashing.
  - The record cannot separate the two. Which mattered is not shown.
- **Not reading the lead's ledger in full has a cost the methods do not name.**
  - The final and seal adherence audits say they never opened it, and the first read its headings and sampled its bodies (P2's Limits). The full audit's report does not say.
  - Audit A checked its entries against the commits, and found entries extended under earlier stamps (M11).
- **The three Claude audits agree with each other closely,** though they ran separately on the same commit.
  - All three found the anchoring's cause (A by a stale binary, B and C by deleting vectors), the Berkeley claim, the LP64 deciders and the GPL fragments.
  - They share a model family and a lead-with-agents process, so the agreement shows a consistent method, not independent confirmation. This study re-ran none of their checks.
- **For HonestHarness.** These audits' claimed defects at `a2241fc` are faults the study's plants could not supply (the report, Q2). This study did not verify them.
  - A suite in the shape of QS3, which measured recall on recorded send-backs, could ask candidate verifier models to find them in the same tree. It would grade against the audits' findings once each is confirmed.
  - That would measure the role on real faults, not on one lead's planting.

## Limits

- **The mapping is the lead's reading** of the three reports' summaries and findings sections. Their evidence logs and appendices were not read. Each row cites its finding IDs so another reader can check it.
- **It is a selection.** It maps the findings the lead matched across the sources, not every finding of each audit.
  - It cites every High, and 14 of A's 18 Medium findings, 11 of B's 14 and 7 of C's 9.
  - Most Lows are unmapped. Some meet Muse nits, such as C L12's width and timing drift (P2's T1 and T6).
- **The commits differ.** The Claude audits read `a2241fc` (2026-10-30), and the Muse full audit `a49991f` (2026-11-01). A finding fixed or introduced between them does not line up.
- **"Not found" on the Muse side** means not in P2's table of the Muse audits' 43 findings and 36 slips, nor in the case report's observations. It does not mean the round never noticed.
- **The comparison's verifier** is given the three reports as copies in a folder outside the ledger, `<repos>/honestharness-muse-claude-audits/`, with their hashes recorded in the ledger.
  - The folder is not published. Two of the reports carry the owner's home-path fragments, on 2 and 4 lines (2 and 5 matches) by a grep, so they are not archived with this study.
  - They can be read on their branches of the library's GitHub repository.
