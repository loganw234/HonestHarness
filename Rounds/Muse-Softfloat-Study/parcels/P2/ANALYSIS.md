# P2: transfer, escapes and the lead (the library round)

Scope: the library round only. Sources are named by key: `K` = `docs/KICKOFF.md`, `H` = `docs/HARNESS.md`,
`R` = `docs/RECORD.md` (library, at `b78af18` unless `a49991f` is named); `L` = `<muse>/ledger/lead.md`;
`A2`, `AF`, `AS` = the Muse adherence audits (`scratch/audit-adherence-2`, `-final`, `-seal`), cited by the line of
the section they sit in; `REPORT` = `<muse>/scratch/audit-full/REPORT.md`. Every figure below comes from a script in
`scripts/` (run with `python -I`, roots as arguments); the tables are in `data/`. Where I judged, the judgement is in a
curated input file in `scripts/` (`*_curated.txt`, `adherence_slips.txt`, ...), and the scripts check what they can
(cited lines exist and hold the quoted fragment; every finding has a verdict).

## Task 1: the clause table (Q1)

**The method copies.** `scripts/method_copies.py` compares the kit's copies with the sources at the pins
(`data/method_copies.csv`). They do not all match byte for byte: ParcelRound `METHOD.md` differs at 24 lines (first at
line 107), HonestFramework `METHOD.md` at line 248, `WITH-PARCELROUND.md` at line 3 and `FAILURE-MODES.md` at line 352,
one line each. `ADOPTION.md` and `ADOPTING.md` are identical. Line counts are equal in all six, so a line number cites
either copy. The differences fit the kit's own rewrite rules R1 to R6 (`START-HERE.md:112-120`); I did not diff each line
against its rule.

**The list.** `data/clauses.csv`: **171 clauses** from the 15 texts (3,704 lines; `scripts/extract_candidates.py` found 638
candidate lines; I curated them by hand into `scripts/clauses_curated.txt` and `scripts/build_clauses.py` checks every row).
That is above the brief's 40 to 120 because I counted each planted-protocol step, each verifier duty and each standing rule
as its own clause. Dedupe, as the lead ruled: an obligation is listed once at the kit's line with the method's line in
`also_in`. The rows cite **176 distinct file lines** (139 in the kit's ten own files, 37 in the five method files); with the
`also_in` lines the list covers **255**.

| marking | rows |
|---|---|
| done as written | 75 |
| adapted | 35 |
| skipped | 6 |
| not applicable | 6 |
| unknown | 49 |

- **Skipped (6),** each with its reason as the record gives it: the clean-room rule that no clone sits beside the workspace
  (C110, impossible on the desktop, disclosed at `K:111-115`); the owner's fingerprint audit (C115, waived, `K:196-198`);
  the planted-copy rule that the copy leaves reach after its verifier reports (C056); the one-reveal-at-the-end rule
  (C060, practised per wave, no owner decision recorded); the READY definition in later briefs (C033); and the rule that the
  lead's own work goes past a verifier (C085, about 30 of 44 lead commits did not, `A2:32`). For C033, C056, C060 and C085
  the record gives no reason.
- **Adapted (35)** include the escalation channel (file channel, because a child cannot message the lead mid-run, `H` rows
  2 to 3), the integration verifier (a role that never ran; the lead ran `git merge-tree` and the rows were relabelled
  "lead-merge", `A2:271`, `AF:90`), key hashes before dispatch (ledger only for Waves 1 to 5, hash-only commits from
  Wave 6, `AS:93`), the stamp rule (the kit's `ledger.sh` was "sanctioned, not only", `H` row 13), models (Wonder for lead
  and parcels, Spark for verifiers) and the standing push permission (`L:36`).
- **Unknown (49)** are mostly acts only a parcel's or verifier's own report would show (reading the ledger at three moments,
  disclosing a crossing, not weakening an assertion). I sampled three verifier ledgers (`verifier-w4seam`, `-w4interval`,
  `-w4trig`) for the verifier duties and marked those DONE on that sample. I did not read the other verifier and parcel
  reports in full. C130 (the board lock) moved from done to unknown: the lead's own entries say board runs were under the lock (12 mentions of board.lock in lead.md), but the seal audit finds no ledger/board.lock and no parcel or verifier ledger citing it (`audit-adherence-seal/report.md` l158-162), so the act rests on the lead's word alone.
- **Reliance outside the 15 texts (not clauses, as the lead ruled).** The round leaned on obligations that live in the kit's
  `tools/` and `templates/`: `tools/plant.py` (the copies and their checks, `WORKFLOW.md:127-158`), `tools/ledger.sh`,
  `tools/round_metrics.py` (`AF:69`: selftest 43/0), and the templates for briefs and verifiers (`B w1-f32` follows the brief
  template's last line). The ten-point list in `A2:3` shows the auditor read those too.

**The harness fallbacks.** `data/harness.csv`, one row for each of the 14 rows of the kit's `HARNESS.md` table, joined with the
round's filled table (`scripts/harness_table.py`). Held: worktrees (the kit's fallback, row 1), file channel with a limit
(row 2), the transcript and extractor (row 6), the board (row 9), harness context (row 11). Failed natively with the fallback
held: resuming an agent (row 4; four of four follow-ups lost their write grant, so re-checks went to fresh agents). Held with
a limit: the usage log (row 7; passes and usage rows froze at 39 for Waves 4 to 5 until repaired, `A2:142`, `AF:69`). Fallback
held, no contact found: the network policy (row 8; none existed, the audits' tree scans found nothing). Partly held: the
remote (row 10; three parcel branches pushed, not main, `AS:207`), scratch isolation (row 12; the record states the limit and
`A2:71` finds graded plant shapes sat in `plants.jsonl` inside later copies), the clock (row 13). Unknown: the background
watch (row 3; `L:19` calls the wake path "untested"), subagents (row 5), session ends (row 14).

## Task 2: the escapes (Q3)

`data/full_audit_findings.csv` (`scripts/parse_full_audit.py`): `REPORT.md` holds **43 findings** (4 major, 2 major-suspected,
22 minor, 15 nits). The area files beside it hold more detail; I classed the consolidated list and did not itemize them.
For each finding `scripts/search_record.py` searched the round's own record before the audit (`L` before the full-audit
heading, `R` at `a49991f`, 146 verifier, parcel, rechecker and study files; no auditor file, nothing fenced), with terms
taken from the finding (`scripts/escape_terms.txt`, results in `data/escape_search.csv`). A hit was a lead to read, not a
verdict. `data/escapes.csv` holds my verdict for the 43 and for 36 slips from the three adherence audits.

| Full audit, 43 findings | raised | partly | examined and passed | not raised |
|---|---|---|---|---|
| major (4) | 0 | 1 | 1 | 2 |
| major-suspected (2) | 0 | 1 | 0 | 1 |
| minor (22) | 4 | 2 | 0 | 16 |
| nits (15) | 2 | 0 | 0 | 13 |
| all | 6 | 4 | 1 | 32 |

**33 of 43 are escapes** (not raised, or examined and passed; "partly" is not counted). 16 of them had no search hit at all.

- **M1 is the sharpest.** `scratch/verifier-readme/report.md:18` checked the README sentence "gated against Berkeley
  TestFloat 3e, MPFR, or an exact reference" against the COVERAGE `authority` column and marked it Agree. `tools/run.sh`
  at `a49991f` has no line naming TestFloat or Berkeley. Family C3 (declared configuration instead of executed work);
  the mechanism was "check every claim in a comment, a document or a commit message" (`ROLES.md:91`) and HF section 3. The verifier read the declared
  authority, not what the gate runs.
- **M2** (stale site figures after the Wave 6 restamp): family F1/F2; mechanism HF section 4 and ParcelRound's "a figure
  the documents quote has a script in the tree" (`METHOD.md:228`). The restamp was by hand across README, BOARD and demo.
- **M4** (the committed bench path): C3. The 60 s window is in the code (`board/read_until.py:37`).
- **M3 and S5** are partly raised: `scratch/verifier-w5attr/report.md:41` named the same default-arm hazard in another context, the
  augmented-parcel verifier cleared the cast case (`scratch/verifier-w5aug/report.md:120`); the test-only counters were disclosed as a design fact.
- Escapes by family (all 33): F1 14 (the list kept in several places), C3 5, F2 2, E1 2, and 10 where no family fits
  (races, supply chain, stale lock). Mechanisms are named in `escapes.csv`.
- **Adherence-audit slips (36 rows):** 24 not raised by the round's own record before the audit, 2 partly, 10 raised (the
  lead's self-records or disclosures, such as `L:181`, `L:565-575`, the merge-body disclosures). FAILURE-MODES.md fits these
  process slips poorly, and many carry "none fits".

**Limits.** A no-hit search shows only that my terms did not match. The final and seal adherence audits say they never opened `lead.md`
(`audit-adherence-final/report.md` l12, `audit-adherence-seal/report.md` l11); the first read its 101 headings and sampled its bodies
(`audit-adherence-2/report.md` l25). So their "not raised" calls rest on narrower sources than mine, most of all in the later two audits;
for these 36 rows I rely on the auditors' own accounts of what the round had recorded except where I give a `lead.md` line.
Judgements on the 43 are mine.

## Task 3: the lead's errors (Q4)

`data/lead_errors.csv` (`scripts/build_lead_errors.py`): 47 rows: all 24 of `corrections.jsonl` plus 23 more (E01 to E23) from
`L`, `R` and the audits. Git facts (is the named commit an ancestor of main, of the seal `751d1d6`) are computed.

- **The brief's premise is wrong for 2 of 24 rows.** Row 22 is a double-counted total in a study agent's report; row 23 is a
  parcel's own document error found by its verifier. Of the 22 lead rows: 11 are brief faults, 4 the lead's own code or tool
  (rows 4 to 7, in P0, `23a740f`), 1 SF-0 text, 5 the SF-2 draft (rows 17 to 21), 1 the lead's merge body and RECORD count.
- **Who caught them** (the `by` field): rows 1 to 16 parcels, 17 to 21 verifier-sf2, 22 parcel-w5metrics, 23 a verifier, 24 the
  seal auditor. Of the other 23: the phase-0 and wave-0 verifiers, the rechecker, the wave auditors and adherence audits, and
  the lead itself (E02, E06, E07, E08, E14, E17, E18, E20); E01 was caught by verifier-phase0.
- **Reached main or the seal.** The tininess defect and the `eq` mapping (rows 4 to 6) and a smoke control (row 7) were in P0,
  an ancestor of main, until `53acb1a` and `b37fb12`, both ancestors of the seal, so fixed before it. Brief faults did not
  reach main as far as the rows show. Record and claim faults did reach main and several stand at the seal as history with an
  erratum or appendix (E09 `4ceffa9`, E10, E15, E21, E22). The Phase 0 text errors (E01 to E03) were restated before the push.
- **ParcelRound round 6 observation 12** (`CASE-STUDY-6.md` at `f42242e`, lines 254-276): nine of the lead's own sentences
  claimed more than their sources, and its restates overreached the same way. **This round shows the same pattern:** in
  Phase 0 two restatements in a row each kept or added a false claim (`L:27`, `L:34`: "when restating, delete claims, do not
  add them"), then the Wave 2 "every commit has a same-step entry" (E09), and the README and HARNESS universals (E11, E12).
  It differs in who caught it: no integration verifier ran (`A2:271`), so the phase-0 verifier, the wave auditors and the
  adherence audits did. Confounds: a different lead model, a record that is mostly the lead's own text, and no count of the
  lead's sentences, so I do not compare rates.

## Task 4: the case report against the record (Q5, first half)

`data/case_report_claims.csv` (`scripts/case_report_checks.py` measures, `scripts/build_case_report.py` joins my verdicts):
**79 checkable claims** across the setting (14), the 17 observations (all 17 have at least one) and the cost table (12).
The report has 17 observations (`grep -c` of its numbered headings) and 18 proposals; I did not judge the proposals.

| result | claims |
|---|---|
| holds | 45 |
| partly | 12 |
| doesn't hold | 1 |
| unverifiable | 21 |

- **Holds, by recount:** the cost table's tokens (1,418,065,198 = 1,410,803,658 + 7,261,540, recomputed from 128 usage rows),
  190 planted and 182 caught (Wave 6 44/45, post-seal 20/20), 849 rows (783 and 66), 49 briefs rows, RECORD 1,400 lines at `a49991f` (1,418 at `b78af18`),
  216 of 216 commits with a Co-Authored-By line, the 228 Berkeley-named COVERAGE rows (117 + 111), 5 of 5 on the valid bench
  attempt, and the Wave 6 miss being a wave-label shape.
- **Doesn't hold (1):** "the final adherence audit graded the lead/parcel distinction; it ran once, at the end" (obs 4):
  the first adherence audit graded it on 10-28 (`A2:32`) and three adherence audits ran.
- **Partly (12)** include: the gate costs (cost table): the record shows standard at 54 s (`lead.md` l127) and 76 s (`scratch/audit-full/REPORT.md` l16), and no 55 s; "hash-first plant keys were never gamed across 190 plants" (obs 17): hash-first covers 70 of 190
  rows (`plant_keys.sha256`), and absence cannot show "never gamed"; "the README said each row is gated against Berkeley"
  (obs 8): the README names three alternatives; "every brief carried a memory ceiling" (obs 7): 18 of 101 brief files contain
  the phrase; "never reopened" (obs 17): the SF-2 P1 gloss was re-asked (`L:643-645`); "metrics from session records rather
  than transcripts" (obs 0): `H` calls the same files transcripts.
- **Unverifiable (21):** claims whose evidence is in session logs or unopened scratch (the dead attempt's scripts, the
  spilled reports, the 9.5-hour parcel, the UNC path), claims about the lead's habits, and claims inside the fenced bundle
  (the bundle's 1,841 files, 8.6 MB, and its CRLF manifest). The fence is the reason for 3.
- The ~90 worktrees (obs 1) cannot be recovered for the report's date: the workspace now lists 138 entries.

## Spot checks (second route for each table)

| table | figure | route 1 | route 2 |
|---|---|---|---|
| clauses.csv | 171 rows, marks 75/35/6/6/49 | `build_clauses.py` | `csv` read + `sort | uniq -c`: 171; 35 ADAPTED, 75 DONE, 6 NA, 6 SKIPPED, 49 UNKNOWN |
| clauses.csv | cited lines | `build_clauses.py` fragment check | `sed -n` on C018 (`WORKFLOW.md:26`), C088, C110, C130, C154: each line holds the clause |
| escapes.csv | 22 minor, 15 nits | `parse_full_audit.py` | `awk` over `REPORT.md` bullets under "Minor" and "Nits": 22 and 15; `grep -c '^[1-6]\. '`: 6 majors |
| lead_errors.csv | 24 corrections rows | `build_lead_errors.py` | `git show b78af18:docs/metrics/corrections.jsonl | grep -c .`: 24 |
| case_report | 17 observations | `case_report_claims.csv` covers 1 to 17 | `grep -c -E '^[0-9]+\. \*\*'` on the report: 17 |
| case_report | 1,418,065,198 tokens | `case_report_checks.py` sum of input and output | `grep -o` + `awk` over `usage.jsonl` at `a49991f`: 1418065198 |

## Limits and what the brief got wrong

- Curation is judgement. The 171 clauses are my reading of what counts as one obligation, and the marks are my reading of
  the record; the check scripts prove the citations, not the marks.
- 49 clauses are UNKNOWN; most need parcel and verifier reports I did not read in full.
- The escape search proves only that my terms did not match. The area files of the full audit hold detail I did not itemize.
- I rely on the adherence audits' own accounts for several marks and escapes (marked "A2", "AF", "AS"); the first sampled `lead.md`,
  the final and seal audits did not open it.
- Brief errors: "match byte for byte" is false for four of six method copies; the clause count came to 171, not 40 to 120;
  "every corrections row is a fault in a brief, so the lead's" is false for 2 of 24 rows; the plan's "audit files" glob and the
  fenced folders (see the fence entry in my ledger).
- One boundary touch, disclosed: a whole-tree `git ls-tree -r` walked the fenced folders and printed two counts by top-level
  name (no file name or content). I did not use them; the lead ruled no touch (`lead.md` 09:31:32). The tree claim (obs 18)
  was then counted by listing each non-fenced root entry on its own.
