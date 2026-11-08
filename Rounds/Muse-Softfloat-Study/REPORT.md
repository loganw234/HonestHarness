# How muse-softfloat ran the methods (HonestHarness study, report)

2026-11-08. The lead is Claude Opus 5.5, in Claude Code. The plan of record is `PLAN.md` beside this file (`5197b2a`).

This is draft 5.
- **Draft 2** took verifier-R's pass 1 on draft 1 (`35873c2`): no wrong figure, 8 restates and 9 notes (`reports/verifier-R.md`).
- **Draft 3** takes verifier-R's pass 2, which found five small new faults and no wrong figure.
  - The lead fixed them and checked each line by command, since verifier-R's passes were spent.
  - It also writes the case report's proposals as "proposal P2" and so on, so they cannot be read as this study's parcels P1 to P3.
- **Draft 4** corrects Q4's count of the lead's errors, after the comparison (`COMPARISON.md`) found 3 planted faults counted among them.
- **Draft 5** takes verifier-C's pass 1 on the comparison and draft 4 (`reports/verifier-C.md`).
  - Q4's first lines now carry the corrected count, and its source.
  - Q1 names the IAS15 parcel's unverified merge, which the comparison found missing from this report.

This report answers the plan's six questions from three parcels' analyses, which sit beside it. Each analysis was verified twice, once on a planted copy and once on its fix:

| Parcel | Analysis | Covers | Final commit |
|---|---|---|---|
| P1 | `parcels/P1/ANALYSIS.md` | the measurements | `83a1889` |
| P2 | `parcels/P2/ANALYSIS.md` | transfer, the escapes and the lead | `06f1a45` |
| P3 | `parcels/P3/ANALYSIS.md` | the proposals | `5c8f4f9` |

A citation such as "P1 §2.3" names a section of one of them. Every figure here comes from one of three places:
- a parcel's analysis, with its script and source;
- the parcels' final commits, read by the lead by command;
- the Muse record, cited where the figure is used.

The study's ledger, archived beside this report, holds every step. The lead's model is the one its harness gives it, which the study's briefs have every agent take from its own system prompt.

## The answers, in brief

- **Q1, transfer.** The methods ran mostly as written.
  - Of 171 obligations in the kit's 15 method texts:
    - 75 were done as written and 35 adapted;
    - 6 were skipped and 6 did not apply;
    - for 49 the record cannot show either way.
  - The skipped include the rule that the lead's own work goes past a verifier: about 30 of 44 lead commits did not.
  - Outside the clause table, one parcel, the IAS15 workload's Pico firmware, was merged with no verifier.
  - The harness forced one real fallback, resuming an agent. All four follow-ups lost their write grant, so fresh agents took over.
  - The kit already held clauses of three of the case report's later proposals:
    - two it labels new: a copy with no route back to the real branch, and a board lock;
    - one it calls an adoption: defining the roots in every dispatch. The round did not use that one.
- **Q2, verification by a smaller model.** muse-spark-1.3 caught 178 of the 185 plants tied to it (0.962).
  - That counts 25 rows whose model the ledger names. On usage rows alone, it caught 153 of 160 (0.956).
  - All 87 code plants were caught: 86 tied to Spark, and 1 to a verifier whose model is not recorded.
  - Spark's 7 misses were all outside code: in claims in docs, test data and metadata.
  - A blind re-grade of 38 plants agreed with the lead on 36, and 2 were unclear. None was overturned.
  - The plants were the Wonder lead's, chosen and graded by it. So this is recall on that lead's planting, not on real defects.
- **Q3, escapes.** Of the full audit's 43 findings, 33 escaped the round's own verification: 32 were never raised, and 1 was examined and passed.
  - The largest family is a fact kept in several places and restamped in only some (14).
  - Next is declared configuration standing in for executed work (5).
  - The full audit found no defect in the shipped math surface.
  - A search for a finding that comes back empty shows only that its terms did not match.
- **Q4, the lead.** Of 47 error rows, 42 are the lead's own genuine errors: P2's 45 lead-owned rows, less 3 planted faults the Muse record landed as corrections (see the comparison). Its own prose was the least-verified text, which is the same pattern ParcelRound's round 6 recorded under an Opus lead.
- **Q5, the case report.**
  - **Its claims:** of 79 checkable claims, 45 hold, 12 partly, 1 does not, and 21 cannot be checked from the files read.
  - **Its 18 proposals:** none is already a full rule in the methods at the kit's pins, 14 are there in part, 3 are absent, and 1 sits only in a case study.
  - **Its "new" labels:** 6 of the 9 proposals it labels "new" have a clause already in the texts.
  - **The toy round** fully practised 1 of the proposals and partly practised 12.
- **Q6, roles.** This is field evidence, not a measurement.
  - A smaller verifier model caught every code plant. Its misses fell in claims in docs, test data and metadata.
  - Two of those misses were values the verifier saw and accepted.
  - A similar shape appears in this study's own Haiku verifiers, and in HonestHarness round 1's replay of DeepSeek flash.
  - The lead's weakness in its own text appears with both a Muse lead and an Opus lead.

## The setting

muse-softfloat is an IEEE 754-2019 softfloat library for the RP2040.
- **Its size:** 849 instantiations, 783 in Tier 1 and 66 in Tier 2 (P2's CR01, recounted at `a49991f`).
- **Its window:** a hackathon that ran to 2026-11-04 (`docs/KICKOFF.md` l144 at `b78af18`).
- **Its seal:** `v1.0.0` on 2026-11-01 (P2's CR02).
- **The harness:** Muse Code.
- **The models:**
  - muse-wonder-full-1.0 was the lead and ran most parcels;
  - muse-spark-1.3 ran 43 of the 46 verifier passes (P1 §1.3).
- **The methods:** a frozen kit pinned ParcelRound at `f42242e` and HonestFramework at `65447fd`.
- **The tracking** is unusually complete: one JSONL row per event (plan §4; P1 §1). It records:
  - 1,418,065,198 tokens, input plus output, over 128 usage rows;
  - 131 passes;
  - 195 plants;
  - 50 briefs;
  - 24 brief corrections;
  - 23 escalations.

  The usage and pass rows stop at a metrics cutoff. 17 named agents have neither (P1 §1.6).
- **A follow-on "toy" round** used the same methods on a new project from 2026-11-03 to 2026-11-07. It is in 224 commits and 90 plant rows.

## Q1: how the methods transferred

**The method copies.** 4 of the 6 method files the kit shipped differ from their sources at the pins (P2 §Task 1):
- ParcelRound's `METHOD.md`, in 24 lines;
- HonestFramework's `METHOD.md`, `WITH-PARCELROUND.md` and `FAILURE-MODES.md`, one line each.

The differences fit the kit's own rewrite rules. The lines were not checked one by one against them.

**The obligations.** P2 listed 171 obligations from the kit's 15 texts, each with its line, and marked each against the round's record.

| Mark | Count |
|---|---|
| done as written | 75 |
| adapted | 35 |
| skipped | 6 |
| not applicable | 6 |
| unknown | 49 |

- **The six skipped:**
  - the clean-room rule that no clone sits beside the workspace, impossible on the desktop and disclosed;
  - the owner's fingerprint audit, waived;
  - the rule that a copy leaves reach once its verifier reports;
  - the single reveal at the round's end (the round revealed after each wave instead);
  - the READY definition in later briefs;
  - the rule that the lead's own work goes past a verifier.

  The record gives no reason for the last four.
- **One skip is outside the clause table.** The `ias15-pico` parcel, the IAS15 workload's Pico firmware, was merged at `d9718cf` with no verifier and no planted copy (the Muse lead's ledger l303).
  - Its merge body disclosed it, and the adherence audit A2 listed it as a slip (P2's `A03`).
  - P2's clause table has no clause for a parcel merged unverified.
- **The 35 adapted** include:
  - escalation by a file channel, because a child agent cannot message the lead mid-run;
  - an integration verifier that never ran: the lead merged by `git merge-tree` and relabelled the rows;
  - key hashes kept in the ledger only, until hash-only commits began in wave 6.
- **Most of the 49 unknown** are acts that only a parcel's or a verifier's own report would show.

**The harness.** P2 matched each of the kit's 14 harness rows against the round's filled table.
- **One mechanism failed natively, with its fallback holding.** Resuming an agent lost its write grant four times in four tries, so re-checks went to fresh agents.
- **One held with a limit.** The usage log's rows froze for waves 4 and 5 until they were repaired.
- **One was only partly held, and it touches verification.** The plant ledger, with the shapes of graded plants, sat inside later planted copies (P2 §Task 1, harness row 12). So a later verifier could read earlier plants.

**Lessons the kit had and the round did not use.**
- Of the 11 kit or method clauses P3 traced into the round's record:

  | Use | Clauses |
  |---|---|
  | used | 4 |
  | partly | 4 |
  | not used | 1 |
  | not shown | 2 |

- **The one not used** is the rule that every dispatch defines its roots (`<repos>`, `<scratch>`). It was in the kit (`WORKFLOW.md` l24), and the record carries no root names (P3 §2).
- **The case report's observation 12** describes the cost of skipping it: two parcels each invented the same override to reach the ledger. P2 could not check that claim from the files it read (its CR48). The report's P13 proposes the clause the kit already had.

## Q2: verification by a smaller model

**Recall** on the library's 195 plants, all planted and graded by the lead (P1 §2):

| Class of plant | Plants | Caught |
|---|---|---|
| code | 87 | 87 |
| claim in docs | 60 | 56 |
| test data | 34 | 32 |
| metadata or provenance | 8 | 6 |
| other | 3 | 3 |
| record arithmetic | 3 | 3 |
| **all** | **195** | **187** (0.959; Wilson 95% 0.921 to 0.979) |

- **By model:** 185 rows are tied to muse-spark-1.3, and 178 of them were caught (0.962).
  - Those 185 include 25 rows whose model the Muse lead's ledger names.
  - On usage rows alone, Spark caught 153 of 160 (0.956).
  - 10 rows have no recorded model, and 9 of them were caught.
- **Wonder as verifier:** it ran 3 passes and holds no plant rows, so it cannot be measured.

**The misses.** All 8 are outside code.
- **4 are claims in docs:**
  - a count and a refusal dropped from the README;
  - an inventory sum inflated, which the verifier repeated;
  - a refusal softened into a deferral;
  - a count reverted.
- **2 are test data:** a boundary value weakened in a generator, and an exact decider dropping boundary results.
- **2 are metadata:** a stamp fabricated, and a wave label changed.

**Two of the misses were values the verifier saw and accepted.** The library's `plants.jsonl` at `b78af18` records them, in the notes of its rows 56 and 5:
- the inflated sum, which the verifier "repeated" in its own recomputation and endorsed;
- the generator's drift, which it saw and "filed benign".

**The wave-label miss was a counting habit.** By row 170's note, verifier-w6metrics "counted appended agents by expected list ... without checking per-row wave fields", which is the case report's observation 2.

**The lead's grading.** P1 re-graded a seeded sample of 38 plants: all 8 misses and 30 catches. It worked blind, from hash-verified keys and the verifiers' own reports.
- 36 agree with the lead.
- 2 are unclear: misses where the verifier raised the item at a weaker level than a finding.
- None is overturned.

If both unclear plants counted as caught, recall would be 189 of 195. The sample shows the grades are consistent with the verifiers' reports. It cannot show how hard the plants were.

**Genuine findings and send-backs.**
- **Findings:** P1 enumerated 35 findings that were not plants. The record's counts of findings by class tie out for 43 of the 46 verifier passes, and are explained for the other 3.
- **Send-backs:** 15 pass rows mark a send-back.
  - **The erratum** (`docs/RECORD.md` from l1004) says 8 of them were not parcel revision rounds. That leaves 7, and it names none.
  - **P1's reading runs the other way:** a documented revision followed 8, and none followed 7.
  - **Strictly,** 5 of those 8 were the lead's own prose restated in place, so at most 3 were parcel revision rounds (P1 §4.3).

**Attempts.** P1 tabulated 10 attempts that the record voids or redoes (P1 §5).
- **The plainest** is the comparison bench's first verifier. It returned CLEAN after checking the real branch, not the copy.
- **Its successor** was required to quote the copy's HEAD before any check counted, and it caught 5 of 5.

**The toy round.** It graded 220 of 220 plants caught, counted per copy, with no shape and no key that the study could read (P1 §2.4). It cannot be classed or re-graded.

**Earlier rounds with planted copies** (P1 §6):

| Round | Verifiers | Caught |
|---|---|---|
| ParcelRound 5 | Sonnet | 4 of 4 |
| ParcelRound 6 | Opus | 10 of 10 |
| HonestHarness round 1 | Sonnet | 10 of 10 |
| HonestHarness round 2 | Haiku | 11 of 12 |

- **ParcelRound 4's plants** tested its gates; no planted copy went to a verifier.
- **These rounds' plants were 2 a copy** and almost all prose. The library round's were 5 a copy, across code, data and prose. The planters and the work differ as well.
- **So no ranking is made.** P1 believes the Claude rounds' figures are not distinguishable from Spark's at these sizes, and says the sample cannot show it either way.

## Q3: what escaped

P2 searched the round's own record, from before the full audit, for each of the audit's 43 findings (P2 §Task 2):

| Result | Findings |
|---|---|
| raised | 6 |
| partly raised | 4 |
| examined and passed | 1 |
| not raised | 32 |

- **33 escaped:** the 32 not raised, and the 1 examined and passed.
- **By HonestFramework's failure families,** the escapes are:
  - a fact kept in several places and restamped in only some (F1), 14;
  - declared configuration instead of executed work (C3), 5;
  - F2, 2;
  - E1, 2;
  - 10 that fit no family, including races, supply chain and a stale lock.
- **The sharpest is the audit's M1.** A verifier checked the README's sentence that each row is "gated against" Berkeley TestFloat. It checked against the coverage table's authority column, and marked it Agree. The committed gate names neither TestFloat nor Berkeley.
- **Of 36 slips the adherence audits found,** the round's own record had not raised 24.

**The limits P2 states on these counts:**
- A search that comes back empty shows only that its terms did not match. 16 of the 33 escapes had no hit at all.
- For the slips, P2 relies partly on the auditors' own accounts of what the round had recorded. The final and seal audits never opened the lead's ledger.

The full audit found no defect in the shipped math surface (`<muse>/scratch/audit-full/REPORT.md`, "Verdict shape"). The escapes were in what the record and the docs said about the work: claims that had outlived the mechanism or the number behind them.

## Q4: the lead's own errors

P2 found 47 error rows, 45 of them the lead's by their owner column (P2 §Task 3). 42 of those are the lead's own genuine errors, as the correction below explains:
- all 24 of the brief corrections, 22 of them owned by the lead and 19 its own genuine errors: 11 faults in briefs, 4 in its own code or tools, and 4 in its own texts (P2 counts 7 texts; 3 are plants);
- 23 more, from the ledger, the record and the audits.

**A correction, from the comparison.** Three of the 7 "text" rows are not errors in the lead's work.
- **What they are:** corrections rows 17 to 19, in the SF-2 draft, are verifier-sf2's planted faults #4, #3 and #2 (`plants.jsonl` rows 59, 58 and 57). The Muse record landed them as accepted brief corrections.
- **Who found it:** Claude audit A's M10, and the lead checked it by command at `b78af18`.
- **What it changes:** the lead's own genuine errors are 42 of the 47 rows. That is P2's 45 lead-owned rows in `data/lead_errors.csv`, less `CJ17` to `CJ19`. No P2 file records 42, since P2 counted the three as errors.
- **Landing the 3 plants as corrections** is a record error of the lead's besides (`COMPARISON.md`).

**Who caught them:** parcels, verifiers, the audits, and the lead itself (eight times).
- **The lead's own code or tool faults in its first phase** (correction rows 4 to 7, among them a smoke control) were fixed before the seal.
- **Faults in the record and the claims** reached `main`, and several stand at the seal as history with an erratum.

**The pattern is round 6's observation 12.** ParcelRound's round 6, under an Opus lead, found the lead's own sentences claiming more than their sources, and its restatements overreaching the same way. This round shows the same pattern: in its first phase, two restatements in a row each kept or added a false claim.

The confounds stop any comparison of rates: a different lead model, a record written mostly by the lead, and no count of the lead's sentences.

## Q5: the case report and its proposals

**Its claims.** P2 checked the report's 79 checkable claims against the record (P2 §Task 4):

| Result | Claims |
|---|---|
| holds | 45 |
| partly | 12 |
| does not hold | 1 |
| unverifiable | 21 |

- **The one that does not hold** says the adherence audit that graded the lead/parcel distinction "ran once, at the end". Three ran, and the first graded it on 10-28.
- **The partly true** include:
  - "hash-first plant keys were never gamed": hash-first covers 70 of the 190 plants at the report's commit;
  - "every brief carried a memory ceiling": 18 of 101 brief files do.

**Its 18 proposals,** marked clause by clause against the methods' text at the kit's pins (P3 §2):

| Mark | Proposals |
|---|---|
| partly present | 14 |
| absent | 3 (proposals P1, P7, P16) |
| only in a case study | 1 (proposal P6) |
| already a full rule | 0 |

- **The "new" labels.** Of the 9 the report labels "new", 6 have a clause already present as a rule, as advice or in part.
- **The kit already held a clause of proposal P2** (the copy with no route back) **and of proposal P15** (the board lock), both labelled new. It also held a clause of proposal P13 (the roots), which the report labels an adoption.
- **Since the pins,** no proposal has entered a method text.
  - The only commits above the pins are two on ParcelRound's `case-study-7` branch. They add a case study and a zip, and change no method text.
  - That case study repeats P4's scoped re-check.

**The toy round** (P3 §3):
- It fully practised 1 proposal (proposal P6), partly practised 12, and was silent on 5.
- It took up proposal P1's provenance gate in part. All 44 of its verifier reports quote their copy's HEAD, but the copy-only line is not shown.

**HonestHarness's own rounds** (P3 §4). For the 18 proposals, rounds 1 and 2:
- had already adopted the practice for 4;
- met the failure and adopted the practice for 4;
- met the failure only for 2;
- did neither for 6;
- found 2 not applicable.

## Q6: what this says about roles (field evidence, not a row of the table)

What the record supports:
- **A smaller model held the verifier role for this round's plants.**
  - muse-spark-1.3 caught 178 of the 185 plants tied to it (0.962), or 153 of 160 (0.956) on usage rows alone.
  - All 87 code plants were caught.
  - The misses were all outside code, by the artifact each plant altered: claims in docs, test data and metadata.
  - Two were values the verifier saw and accepted: a sum it recomputed and endorsed wrong, and a regeneration drift it filed as benign.
- **A similar shape appears in two other settings.**
  - This study's Haiku verifiers caught 14 of 15 plants. Their miss was a prose sentence false against its parcel's own tables.
  - HonestHarness round 1's replay caught DeepSeek flash 24 of 24 on plants that changed a figure or a reference, against 7 of 16 on plants that changed meaning or shape (P1 §6.3).

  The planters, plants and harnesses differ across the three. Together they suggest the weakest ground is where a verifier must judge prose against its sources, or catch a slip it repeats in its own recomputation (row 56). That is a recurring pattern, not a measurement.
- **The lead role's weak point was its own text,** for a Muse lead as for an Opus one (Q4).
  - The escapes were claims about the work: kept in several places, restamped by hand, or resting on declared configuration (Q3).
  - The case report's P9 and P10 are written for those cases: an authority's execution mode, and a registry of load-bearing literals. Whether they would have caught them is not tested here.
- **Structure worked where it was enforced.**
  - The wrong-tree attempt was exposed because its scripts were kept (`<muse>/ledger/lead.md` l876). Its successor passed a provenance gate (P1 §5).
  - The record also credits hash-first keys and bit-identical workload proofs:
    - hash-first keys covered 70 of the 190 plants at the case report's commit (P2 §Task 4);
    - this study did not re-run the workload proofs.

What it cannot support:
- a ranking of muse-spark-1.3 against Claude verifiers;
- the plants' difficulty;
- any claim about the Muse models outside this harness and this round.

**For HonestHarness's table.** A measurement would replay the library round's 39 planted copies against verifier models at a fixed protocol, as round 1's QS4 replayed ParcelRound round 6's copies. It would grade by the keys, with recall by class. What is on record for it:
- **The keys** sit in the Muse lead's scratch folder, each matched to its plants rows by hash (P1 §3.1).
- **The plants' classes** are in P1's `data/`.
- **Whether each planted copy's repository still exists** was not checked.
- **The toy round's keys** were not found.

## What running this study showed about the methods

The study ran the same methods with Claude agents: three Sonnet parcels, Haiku verifiers and an Opus lead. So it is a small second sample.

- **Planted copies.** The three verifiers caught 14 of 15 plants (`reports/grading-wave1.md`).
  - The two plants in scripts were both caught by re-running: an interval at 90 percent instead of 95, and a check made unable to fail.
  - The one miss is a sentence false against the parcel's own tables.
- **Genuine findings.** The verifiers found real errors in all three analyses:
  - P1: 4 wrong figures or attributions, and 2 restates;
  - P2: 3 wrong answers, 2 restates and 5 citation notes;
  - P3: 2 wrong citations and 9 restates.

  Their second passes left P1 READY, one restate in P2 and two in P3. The lead checked those last changes, since the passes were spent.
- **The fence by instruction did not hold by itself.** Two agents walked the fenced folders by recursive listing. Both disclosed it, and neither read content (the ledger, 08:30:26 and 09:31:32). This is the case report's observation 1, and the reason for its P2.
  - A pathspec rule then gave the fence a mechanical form for git listings.
  - Agents still had to choose to use it, so the fence stayed short of the allowlist the case report's P2 asks for.
- **A shared ledger exposes the planting style.** One verifier's findings describe its copy's plants to any verifier that reads them. The study held every grading until the last planted-copy verifier had reported. muse-softfloat's own audit found the same leak, through the plant ledger inside later copies (P2 §Task 1, harness row 12).
- **The report channel.** This harness refuses a subagent's report file. Three parcels and one verifier met the refusal.
  - The parcels sent their analyses as text. The lead wrote each file verbatim, and recorded its hash, and the parcel read it back.
  - So the case report's P6 depends on the harness.
- **The provenance-first rule** was reordered once. A small verifier wrote its provenance entry after its first checks, and said so.
- **The gate's privacy check** stopped one parcel's commit on an absolute path copied into a data file. Another parcel scrubbed the owner's address from its data before the gate.
- **The lead's own text was again the least verified.**
  - The plan's verifiers found 4 wrong facts in its draft 1, one in its draft 2, and restates in each draft, including draft 3.
  - Its "ParcelRound rounds 4 to 6" was wrong for round 4 (P1 §6).
  - Its send-back list cited table "T8" for T7.
  - It once sent a message before its ledger entry, and once wrote to `/tmp`.

  That is the case report's P5, met here.
- **The environment.** A temp cleanup emptied the lead's older scratch folder within about two weeks, taking round 2's case study draft with it. The lead believes the cleanup was Windows', but has not confirmed it. This study kept its durable files in the ledger and a folder of the lead's, outside Temp.

## Limits

- **The plants measure recall on one lead's planting.** Nothing here measures how hard they were.
- **The marks are judgement.** P2's clause marks, P3's proposal marks, and P1's classes and re-grade are readings. Each is cited by line so another reader can re-mark it, and each was checked by a verifier, not proven.
- **Field evidence, not a controlled comparison.** The earlier rounds' figures differ in planter, plants per copy, work and models.
- **The toy round** could not be classed or re-graded: it has no per-plant shapes and no keys the study could read.
- **The Muse records were read as they stood on 2026-11-08.** Their two repositories were read at commits. Their other files were read as found, and another session may still be working there.
- **The Claude audit reports** were fenced from this study until its draft 3 was verified.
  - They sit on three branches of the library on GitHub, not in its `audit-bundle/` as the plan had thought.
  - The comparison with them is `COMPARISON.md`, written after.
- **The Muse session transcripts** were not read, by Logan's choice. The usage figures are the project's own extraction.
