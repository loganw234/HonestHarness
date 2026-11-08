# P1: the measurements (muse-softfloat study)

Parcel P1, branch `study-muse-p1`. It answers Q2 and supplies the figures for Q5, Q6 and the comparison with earlier rounds. Written by P1 (Claude Sonnet 5.5); the lead filed this file from P1's text.

**Roots.** `<repos>` holds the repositories; `<muse>` is `<repos>/Muse-Softfloat`; `<scratch>` is P1's scratch directory. No absolute path appears in this parcel.

**Sources, at their commits.**
- LIB: `<muse>/muse-softfloat` at `b78af1801d3e2bd123fed82d933414af661a9e9a` (read with `git show`, `git log`, `git rev-list`).
- TOY: `<muse>/muse-softfloat-toy` at `084f98b29e292d0674dfa4eb9fe119c3990c726d`.
- ParcelRound at `f42242e`, and `CASE-STUDY-7.md` at `894d125`. HonestHarness `main`. The round-2 ledger directory `<repos>/honestharness-r2-ledger/`.
- Files outside git: `<muse>/ledger/lead.md` and the verifiers' ledger files, `<muse>/scratch/<verifier>/report*`, `<muse>/scratch/lead/keys/` (keys only), and `<muse>/scratch/toy1/`, `toy2/` (the toy verifier reports its verdict rows name).

**How every figure was made.** Each figure comes from a script in `scripts/`, run as `python -I scripts/<name>.py --repos <repos>`; `run_all.py` runs them in order (keycheck, keyfiles, figures, classify, recall, sample, toy_sample, regrade_join, passes_check, attempts, earlier, check_alt, make_tables). Tables are in `data/`; `data/tables.md` renders the main ones and the tables below are copied from it. Eight files in `data/` are my hand readings of the sources and are read, not remade: `class_input.csv`, `model_map.csv`, `regrade_input.csv`, `toy_regrade_input.csv`, `findings.csv`, `sent_back_evidence.csv`, `attempts_input.csv`, `earlier_input.csv`. Where I counted by reading, the text says so.

---

## 0. Answer to Q2, in short

- **Recall.** On the library's 195 plants the verifiers caught 187 (0.959, Wilson 95% 0.921 to 0.979). 185 rows can be tied to muse-spark-1.3: 178 caught (0.962). 10 rows have no recorded model: 9 caught. (T7, T8.)
- **Where the 8 misses fall.** None in code (87 of 87 caught). 4 in claims in docs (56 of 60), 2 in test data (32 of 34), 2 in metadata or provenance (6 of 8; too few to rank). (T6.) The toy round graded 220 of 220 plants caught, per copy, with no shape.
- **Trust in the lead's grading.** From a seeded sample of 38 library plants (all 8 misses and 30 catches) graded blind from hash-verified keys and the verifiers' own reports, 36 agree with the lead, 2 I grade "unclear" (not comparable), and none is overturned. Agreement shows consistency with the verifiers' reports, not how hard the plants were.
- **Genuine findings and send-backs.** I enumerated 35 findings that were not plants. The record's a and b counts tie out for 43 of 46 passes and are explained for the other 3. Of the 15 `sent_back` rows I find a documented post-verdict revision after 8 and none after 7; the erratum implies 7 and 8 (section 4.3).
- **Limits that matter.** Nothing here measures how hard the plants were: the lead planted, chose the shapes and graded. The toy's keys were not available, so the toy has no per-plant class and no key-based re-grade.

---

## 1. Task 1: the figures, recomputed

Script `scripts/figures.py` (outputs `data/figures.json`, `data/agents_without_rows.csv`); second route `scripts/check_alt.py`. Sources: the seven `docs/metrics/*.jsonl` files at LIB, and TOY `docs/metrics/plants.jsonl` and `docs/RECORD.md`.

### 1.1 Rows and commits

- Row counts (figures.json `library_row_counts`): usage 128, passes 131, plants 195, briefs 50, corrections 24, escalations 23, fetches 5.
- LIB: 221 commits (`git rev-list --count`); first 2026-10-26 10:50:22; last 2026-11-03 04:18:39 by author date (04:20:16 by committer date). TOY: 224 commits, 2026-11-03 20:05:02 to 2026-11-07 16:39:34.

### 1.2 Tokens (usage.jsonl, one row per agent, 128 agents)

Input, output and cached are the rows' fields. The record does not say whether cached tokens are part of input (no row has cached above input, and RECORD.md, HARNESS.md and the extractor script state no inclusion rule), so the total is input plus output and does not add cached. Totals (figures.json `tokens_total`): input plus output 1,418,065,198; cached 1,379,156,504.

**T1 by model**

| model | usage rows | input | output | input+output | cached |
|---|---|---|---|---|---|
| muse-spark-1.3 | 59 | 677,616,961 | 3,289,230 | 680,906,191 | 664,524,584 |
| muse-wonder-full-1.0 | 69 | 733,186,697 | 3,972,310 | 737,159,007 | 714,631,920 |

**T2 by role** (the role is the one in the agent's passes rows; every usage agent has a passes row)

| role | usage rows | input | output | input+output |
|---|---|---|---|---|
| author | 28 | 485,845,099 | 2,244,302 | 488,089,401 |
| author+fixer | 1 | 7,101,595 | 47,604 | 7,149,199 |
| fixer | 3 | 14,778,009 | 71,247 | 14,849,256 |
| surveyor | 50 | 276,331,105 | 1,976,661 | 278,307,766 |
| verifier | 46 | 626,747,850 | 2,921,726 | 629,669,576 |

### 1.3 Passes

**T3 passes by wave and role** (131 rows: author 31, fixer 4, surveyor 50, verifier 46; no row has the role `integration`)

| wave | author | fixer | surveyor | verifier |
|---|---|---|---|---|
| polish | 0 | 0 | 10 | 1 |
| wave0 | 1 | 0 | 16 | 10 |
| wave1 | 2 | 2 | 1 | 5 |
| wave2 | 2 | 0 | 2 | 2 |
| wave3 | 2 | 0 | 3 | 1 |
| wave4 | 4 | 0 | 6 | 6 |
| wave5 | 11 | 1 | 8 | 14 |
| wave6 | 9 | 1 | 4 | 7 |

**Verifier verdicts.** NOT READY 37, READY 9 (46 passes). By the model in the agent's usage row: muse-spark-1.3 43 passes, muse-wonder-full-1.0 3. The three Wonder verifier passes carry no plant rows.

**T4 verifier passes by wave, with the record's a and b** (totals a 109, b 78). The kit's classes: (a) a regression, (b) a wrong answer, which includes a sentence that claims more than is true; a note is a third class and is not counted (kit `ROLES.md` line 100, `GLOSSARY.md` lines 27-28; `METRICS.md` line 30 counts them as `a` and `b`).

| wave | verifier passes | a | b |
|---|---|---|---|
| polish | 1 | 4 | 0 |
| wave0 | 10 | 0 | 14 |
| wave1 | 5 | 4 | 7 |
| wave2 | 2 | 4 | 7 |
| wave3 | 1 | 1 | 4 |
| wave4 | 6 | 12 | 14 |
| wave5 | 14 | 55 | 24 |
| wave6 | 7 | 29 | 8 |

### 1.4 The two readings the record's erratum requires (`docs/RECORD.md` from line 1004)

- **`sent_back`.** 15 rows are true. The erratum says 8 early rows carry true where the planted verdict was not a parcel revision round, and reads `sent_back` as true only on proven revision rounds. It does not name its 8. My own row-by-row reading is in section 4.3.
- **`checked_by: integration`.** 65 plants rows carry it (rows 1 to 65 of plants.jsonl: wave1 10, wave2 10, wave3 5, wave4 25, wave5 10, readme 5). No passes row has role `integration`, and the erratum says the role never ran; I read the 65 as run by the lead.

### 1.5 Plants, briefs, corrections, escalations, fetches

- **Plants:** 195 rows, 187 caught and 8 missed; `graded_by` is "lead" in all 195; 39 verifiers; 39 distinct `key_sha256`; 174 rows carry a note.
- **T5 plants by wave.** The labels `readme`, `site`, `polish` and `postseal` are not numbered waves; I use them as the metrics give them.

| wave | plants | caught | missed |
|---|---|---|---|
| polish | 5 | 4 | 1 |
| postseal | 25 | 25 | 0 |
| readme | 10 | 9 | 1 |
| site | 10 | 10 | 0 |
| wave1 | 10 | 9 | 1 |
| wave2 | 10 | 10 | 0 |
| wave3 | 5 | 5 | 0 |
| wave4 | 25 | 25 | 0 |
| wave5 | 50 | 46 | 4 |
| wave6 | 45 | 44 | 1 |

- **Briefs:** 50 rows. **Corrections:** 24 rows, all `accepted: true`. **Fetches:** 5 rows.
- **T11 escalations:** 23 rows, all by the file channel; 11 tests and 12 real. Time from sent to answered, in seconds:

| kind | n | answered | unanswered | min | median | max |
|---|---|---|---|---|---|---|
| test | 11 | 6 | 5 | 19 | 179 | 438 |
| real | 12 | 12 | 0 | 38 | 141.5 | 3864 |

  The 5 unanswered rows are all tests (video-final in wave 3 and four tier-2 study agents in wave 4); they carry no `answered` field.

### 1.6 Agents with no usage or passes row (T12, `data/agents_without_rows.csv`)

17 agents that appear in the briefs, corrections, escalations or plants rows have neither a usage row nor a passes row: `auditor-adherence-seal`; `lead-polish1` and `lead-seam`; seven parcels (`parcel-psbench`, `-psbench2`, `-psciwindows`, `-psedge`, `-psreadme`, `-w6captions`, `-w6metrics`); and seven verifiers (`verifier-psbench`, `-psbench2`, `-psciwindows`, `-psedge`, `-psreadme`, `-w6captions`, `-w6metrics`), which hold 35 plant rows, 5 each.

What the record says of why:
- `docs/RECORD.md` at LIB lines 1286-1288: "the seal sessions after the metrics cutoff (the two seal parcels, their two verifiers, this auditor) are unrowed in usage/passes by design and named here". That covers `parcel-w6captions`, `parcel-w6metrics`, `verifier-w6captions`, `verifier-w6metrics` and `auditor-adherence-seal`.
- For the five post-seal agents and their verifiers (psbench, psbench2, psciwindows, psedge, psreadme) I found no sentence of their own. They fall after the same cutoff (RECORD.md line 1326: metrics "refreshed ... at the seal-parcel cutoff"); that they are unrowed for that reason is my inference.
- `lead-seam` and `lead-polish1` appear only as brief authors (believed: the lead under another label).
- None of the 7 verifiers has a passes row either, so passes gives no second route to their model.
- The full audit's eight auditors have no usage row (the lead's ledger entry of 2026-11-08 08:54:32 cites `<muse>/scratch/audit-full/REPORT.md` line 4 for their models; I did not open that report).

### 1.7 The toy's metrics (TOY `docs/metrics/plants.jsonl`, README, `docs/RECORD.md`)

- 90 rows: 44 `dispatched`, 44 `verdict`, 2 `lead_trim`. The 44 dispatched rows hold 44 distinct copy heads and 44 distinct key hashes.
- The 44 verdict rows hold 220 plants, 220 caught, and each names a verifier report under `scratch/toy1/` or `scratch/toy2/`. 18 verdict rows list `extra_findings`, 26 in all. No row has a shape or a per-plant grade.
- Parcels by prefix (figures.json `parcels_by_prefix`): toy1 15, toy2 12, toy3 3, toy4 8, toy5 6.
- `docs/RECORD.md` (410 lines) states two cumulatives, "180/180 across 36 parcels" and "200/200 across 41 parcels", and "75 planted defects, 75 caught" for the first 15 cartridges. It never uses "missed", "not caught" or "uncaught". Its last cumulative lags the file by 3 parcels (15 plants).
- The metrics README says the key stays "in workspace scratch" and only its SHA-256 is committed before dispatch.

### 1.8 The plan's section 4 first-look figures

`figures.json` holds `plan_s4_check`, 41 figures with the plan's (or the lead's first look) value and my recomputed value. All 41 agree; `plan_s4_disagreements` is empty. One wrinkle: the plan's library last-commit time "04:18" is the author date (04:18:39); the committer date is 04:20:16. Nothing in section 4 needed correcting.

---

## 2. Task 2: the plant classes

### 2.1 The rubric, in full

**Principle.** Class a plant by the artifact it altered (where the altered text lives), not by its effect. Decide by the first rule that applies. The class is assigned from the row's `shape` and `note`; where they do not decide, the hash-verified key's altered-file path decides (section 2.2).

**Classes**
- **code:** library or tool source that runs or builds: `src/`, `include/`, `compat/`, firmware and board code (`board/`), host tools (`tools/`), runners and gate scripts (`tools/run.sh`, `examples/*/build.sh`), CI workflow files, build files (CMake), and the tables that feed shipped headers (`tables/*.tsv`). A generator whose output ships in the library (coefficients, tables) is code.
- **test data:** material that checks the code: committed vectors and their expected values or flags, the generators and pools that make vectors, reference or oracle code used only to make or check vectors, fixtures (a canary program that exists only to be run by a test), expected-output files, and frozen expectation catalogues.
- **claim in docs:** prose that asserts something about the project: README, studies, `docs/*.md`, site pages and captions, popups' text, caption files, documentation comments inside source. A number stated in such prose belongs here, even though it is a number.
- **metadata or provenance:** labels, stamps, hashes, SHAs, manifests, wave or pass fields, dates, attributions, claim-gate tokens used as labels, and counts of counts. It applies where the altered thing is a descriptor of the record's own artifacts, not a sentence of prose and not a computed result.
- **record arithmetic:** tallies and totals in `docs/RECORD.md` or `docs/metrics` whose altered value is a figure (a token count, a sum, a score).
- **other:** the altered artifact fits none of the above. It must carry a reason naming the closest class. If more than 10 percent of rows land here the rubric is leaky.

**Tie-break rules** (each row logs the rule that fired, `plants_classed.csv` column `tiebreak`)
- **TB1, location beats wording:** if the key gives the altered file, class by its path (`src/ include/ tools/ board/ .github/` = code; `tests/vectors/ tests/gen_* demo/expected-*` = test data; README, `docs/`, `site/` content = claim in docs; metrics files = metadata or record arithmetic by TB4).
- **TB2, generator or oracle:** one used only to make or check vectors is test data; one whose output ships (coefficients, header tables) is code.
- **TB3, a number in prose:** a number inside README, site or study prose is claim in docs; the same number inside RECORD.md or metrics is record arithmetic if it is a computed total, otherwise metadata.
- **TB4, descriptor versus figure:** an altered hash, SHA, date, name, wave field or "N files exist" statement in the record or metrics is metadata or provenance; an altered sum, rate or token figure there is record arithmetic.
- **TB5, gate scripts (narrowed on first use):** a gate or runner script (`tools/run.sh`, a CI workflow, `build.sh`) is tool source, so code, even when its logic is a test control. A canary program that exists only to be run by a test is test data (a fixture).
- **TB6, pins and decisions:** a pin or decision recorded in prose is claim in docs; the same value in a manifest or pin file is metadata.
- **TB7, last resort:** take the class of the artifact the verifier would have had to open to find the fault; the row is marked for review.
- **TB8, site and film code (added on first use):** inside `site/app.js`, a displayed label or caption is claim in docs and control flow is code. Film popup constants in `video/` source are code by TB1 although their effect is a wrong displayed figure.
- **TB9, comments (added on first use):** a prose comment inside a source file is claim in docs.

TB5 was narrowed, and TB8 and TB9 added, on the first application, in phase 2. The phase 1 design's TB5 put runner logic under test data, which would have put the CI plants there. No result depends on the change except the class counts.

### 2.2 How the classing was applied

- `scripts/keyfiles.py` reads the 39 hash-verified keys and writes, for every row, the key's altered file (`data/key_plants.csv`). For 176 rows the key's shape text equals the row's; for 19 the wording differs (rows 49, 51, 52, 55-60, 66, 67, 69, 74, 81, 181-185). I took the row's `shape` as the plant's identity and the key's file as its location. Every key holds five plants.
- I wrote the classing by hand from shape and note (`data/class_input.csv`; 147 rows decided on the shape, 48 on the key's file path). `scripts/classify.py` joins it, writes `plants_class_blind.csv` with no grade column, and flags the rows where my class differs from a path-only rule. `scripts/recall.py` joins the grades afterwards. So the classes were written before any grade was joined; the notes of some rows mention the grade, so the classing is blind to the grade field and not to the notes.
- No keyword layer was built (the phase 1 design said it would be): the key names the file for all 195 rows, so hand classing plus the path flag was more direct.
- Every row has a one-line reason (`plants_classed.csv`, column `reason`).

**Counts.** code 87, claim in docs 60, test data 34, metadata or provenance 8, other 3, record arithmetic 3 (sum 195; "other" is 1.5 percent).

**Tie-break rows.** 70 rows logged a rule: TB2 21, TB1 15, TB4 11, TB3 9, TB7 5, TB5 4, TB8 2, TB9 2, TB6 1. 27 rows differ from the path-only rule (listed by `classify.py`, each with its reason). The ones another reader might class otherwise:
- TB7: rows 120 (a sample vector's expectation in `site/vectors-sample.json`), 136 and 140 (pinned expectation constants inside `examples/*/main.c`), 143 (a skip message in `tools/run.sh`), 192 (a deck operand against its caption).
- TB1 over the shape: row 8 (the shape reads like a test; the key puts the change in `src/msf64.c`) and rows 156-160 (film constants in `video/segments/gitvisual.py`).
- TB9: rows 124 (a comment in `src/msf_math.c`) and 130 (a header comment in `board/interval_workload.h`). TB6: row 58 (an owner pin in a study).
- None of the five TB7 rows is a miss, so recall by class would move by at most one caught row in test data or claim in docs.

### 2.3 Recall

From `scripts/recall.py` over `data/plants_classed.csv`; second route in `check_alt.py` (counts by class agree). The interval is the Wilson 95 percent score interval. A cell with n under 10 is marked and not ranked.

**T6 by class**

| class | n | caught | missed | recall | Wilson 95% |
|---|---|---|---|---|---|
| code | 87 | 87 | 0 | 1.000 | 0.958 to 1.0 |
| claim in docs | 60 | 56 | 4 | 0.933 | 0.841 to 0.974 |
| test data | 34 | 32 | 2 | 0.941 | 0.809 to 0.984 |
| metadata or provenance | 8 | 6 | 2 | 0.750 | 0.409 to 0.929 (n under 10) |
| other | 3 | 3 | 0 | 1.000 | 0.438 to 1.0 (n under 10) |
| record arithmetic | 3 | 3 | 0 | 1.000 | 0.438 to 1.0 (n under 10) |

**The 8 misses** (each is also a re-grade row, section 3): row 5 (wave1, verifier-w1f32, test data); 54 (readme, verifier-readme, claim in docs); 56 and 60 (wave5, verifier-sf2, claim in docs); 73 (wave5, verifier-w5alg1, test data); 114 (wave5, verifier-w5metrics, metadata); 124 (polish, verifier-polish1, claim in docs); 170 (wave6, verifier-w6metrics, metadata).

**T9 by wave**

| wave | n | caught | missed | recall | Wilson 95% |
|---|---|---|---|---|---|
| wave5 | 50 | 46 | 4 | 0.920 | 0.812 to 0.968 |
| wave6 | 45 | 44 | 1 | 0.978 | 0.884 to 0.996 |
| postseal | 25 | 25 | 0 | 1.000 | 0.867 to 1.0 |
| wave4 | 25 | 25 | 0 | 1.000 | 0.867 to 1.0 |
| readme | 10 | 9 | 1 | 0.900 | 0.596 to 0.982 |
| site | 10 | 10 | 0 | 1.000 | 0.722 to 1.0 |
| wave1 | 10 | 9 | 1 | 0.900 | 0.596 to 0.982 |
| wave2 | 10 | 10 | 0 | 1.000 | 0.722 to 1.0 |
| polish | 5 | 4 | 1 | 0.800 | 0.376 to 0.964 (n under 10) |
| wave3 | 5 | 5 | 0 | 1.000 | 0.566 to 1.0 (n under 10) |

**By verifier** (`recall_by_verifier.csv`; 39 verifiers, every cell n = 5, so none is ranked): 32 verifiers caught 5 of 5; verifier-sf2 caught 3 of 5; verifier-polish1, -readme, -w1f32, -w5alg1, -w5metrics and -w6metrics caught 4 of 5.

**By verifier model.** The model is the one in the verifier's usage row; for the 7 verifiers with no usage row it is the one the ledger names (`data/model_map.csv`, mapping only an unambiguous "Spark" to muse-spark-1.3), else "not recorded".

| model | n | caught | missed | recall | Wilson 95% |
|---|---|---|---|---|---|
| muse-spark-1.3 | 185 | 178 | 7 | 0.962 | 0.924 to 0.982 |
| not recorded | 10 | 9 | 1 | 0.900 | 0.596 to 0.982 |

- Spark from usage rows only: 160 rows, 153 caught (0.956). Spark by usage rows plus ledger lines: 185, 178.
- Ledger lines used: `<muse>/ledger/lead.md` line 866 ("both Spark verifiers": psbench, psciwindows), line 871 (psreadme), line 876 (psbench2: attempt B, verifier-psbench2b), line 891 (psedge). `verifier-w6captions` and `verifier-w6metrics` are "not recorded": lead.md line 856 and RECORD.md lines 1239 and 1241 name no model for them.
- muse-wonder-full-1.0 has no plant rows as a verifier, so Wonder's recall as verifier cannot be measured.

**By project.** Library 187 of 195 (0.959, 0.921 to 0.979). Toy 220 of 220 (1.000, 0.983 to 1.0), per copy: five plants in each of 44 copies.

### 2.4 The toy's plants

The toy's rows carry no shape and no per-plant grade, so the toy cannot be classed, and its recall by class cannot be given. Its keys are not available: the 44 toy key hashes match none of the 78 files in `<muse>/scratch/lead/keys/` (`data/keycheck.csv`), and neither the toy's metrics README nor its RECORD.md names a key folder. Per the lead's ruling I read only the verifier reports its verdict rows name. The lead's ledger lists a copy's plants in prose for toy1-carousel only (`<muse>/ledger/lead.md` line 937): a figure-8 initial-condition digit, a Lagrange showing length, a removed memset, a hard-coded 240, and a proof length; these are constants and logic in a cartridge's code. For the other 43 copies the plant classes are "not recorded".

---

## 3. Task 3: the re-grade sample

Scripts: `keycheck.py`, `sample.py`, `toy_sample.py`, `regrade_join.py`. Outputs: `data/keycheck.csv`, `sample_blind.csv`, `regrade_input.csv`, `regrade.csv`, `toy_sample_blind.csv`, `toy_regrade_input.csv`.

### 3.1 The keys

- `<muse>/scratch/lead/keys/` holds 78 files: 39 `key-*.json` and 39 `*-draft.json`. I opened no draft.
- Each file's sha256 was compared with the rows' `key_sha256`. 39 `key-*.json` files match; all 39 library hashes are found as files (second route `sha256sum` and `comm`: the same 39). No `key-*.json` is unmatched, so there is no key finding. The 39 drafts match no row and are reported as unmatched drafts, not findings (the lead's ruling).
- `docs/metrics/plant_keys.sha256` at LIB holds 15 hashes; all 15 are among the files; they cover 75 plants rows and 2 of the 8 misses.
- The 44 toy key hashes: none is among the files.

### 3.2 Tying rows to attempts

Rows are tied to attempts by `key_sha256`, not by name. The 5 rows named `verifier-psbench2` all carry key `0305f97a` (copy `2412360`) and hold attempt B's grades (`verifier-psbench2b`, `<muse>/ledger/lead.md` line 876); the voided attempt A has no plants rows. The 5 rows named `verifier-psbench` carry `c7e98cc5` (copy `a4f500d`), all caught, from the first post-seal bench parcel. The record counts them in its cumulative (lead.md line 866; RECORD.md line 1396, "Cumulative plants 182/190 (post-seal 20/20)"); I found no sentence calling them void or superseded.

### 3.3 The sample (seed 20261108, in `scripts/common.py`)

- All 8 misses, and 30 catches. The 30 are allocated across the plants' wave labels in proportion to each label's catches (floor, minimum 1, remainders by largest remainder): polish 2, postseal 4, readme 1, site 1, wave1 1, wave2 1, wave3 2, wave4 4, wave5 7, wave6 7. Within a label the choice is round-robin across the rubric's classes in a seeded random order. The 30 by class: claim in docs 9, code 8, test data 7, metadata 3, record arithmetic 2, other 1. Strata recounted with `grep -c` (8 miss rows, 30 catch rows, the same per-wave counts).
- Toy: 10 of the 44 copies drawn with the same seed (`toy_sample.py`).

### 3.4 Method and result

- `sample.py` wrote `sample_blind.csv` with no lead grade. For each sampled plant I read the hash-verified key's altered file and old/new text (never copied into this repository) and the verifier's own report or ledger file, and wrote my grade with file and line to `regrade_input.csv`. Only then did `regrade_join.py` attach the lead's grade.
- **Agreement: 36 of 38 identical.** Misses: 6 of 8 missed by my reading too. Catches: 30 of 30 caught by my reading too. Every sampled key is hash-verified.
- **Two rows I grade "unclear"; they are the only differences.**
  - **L05, verifier-sf2 plant 5 (a refused pow/powr softened to a priced deferral).** The lead graded it missed. The report's U7 names the exact planted text as "unsourced" but says the deferral matches SF-1 section 7 (`<muse>/scratch/verifier-sf2/report.md` lines 166-170). The text was raised, not called a contradiction.
  - **L07, verifier-w5metrics plant 4 (a fabricated `answered` stamp).** The lead graded it missed. The report names the row as UNRESOLVED U1 and says it is "not a fabrication finding" (`<muse>/scratch/verifier-w5metrics/report.md` lines 88-100, 189).
- **Six misses I confirm:** L01 polish1 plant 4 (the report reconciles the planted "all four" sentence, report line 26); L02 readme plant 4 (the deferred list is marked "Agree", line 27); L03 w1f32 plant 5 (the report names 16 differing lines and calls them "benign drift", lines 100-105); L04 sf2 plant 1 (it recomputes "855 - correct", line 26); L06 w5alg1 plant 3 (no sign of the generator edit, lines 21 and 104); L08 w6metrics plant 5 (a coverage note finds no gap, lines 74-76).
- **No disagreement overturns a catch.** Both unclear rows are misses where the verifier raised the item at a weaker level than a finding. If they counted as caught, recall would be 189 of 195 (0.969): an upper bound on this sample's effect.
- **Limit, as the lead set it:** agreement shows consistency with the verifiers' reports, not how hard the plants were. All 30 sampled catches name the plant's own file and value; the open question is a report that names a symptom, which is what the two unclear rows are.

### 3.5 Toy sample

The toy has no key available, so there is no key-based re-grade. For the 10 drawn copies I compared the number of defects each verifier report names with the lead's 5 plants plus its listed extra findings (counted by reading). All 10 are consistent: seven reports name five defects and the row lists no extras; toy1-carousel names five plants plus one extra (D6); toy1-input names 9 defects against 5 plants + 3 extras (one further item is labelled minor); toy1-timebank names 8 against 5 + 3. Only toy1-carousel has the lead's list of its five plants, and the report's D1 to D5 match it one by one. This check cannot detect a plant the lead counted as caught that the report did not name: it is a count check, not a re-grade.

---

## 4. Task 4: the genuine findings

Script `passes_check.py` (reads `findings.csv`, `sent_back_evidence.csv`, passes and plants). Outputs: `data/findings.csv`, `data/pass_counts.csv`, `data/sent_back_evidence.csv`.

### 4.1 The findings I enumerated

35 non-plant findings, by hand from the verifiers' ledger files (`<muse>/ledger/verifier-*.md`), their `report.md` files and the lead's grading lines. Each row of `findings.csv` gives the finding, its kit class (a or b, and whether the verifier tagged it), my rubric class, its disposition and its source.
- 14 are from the five non-plant NOT READY passes (passes lines 8, 13, 16, 42, 43; all kit class b, all claim in docs). Their disposition is "restated in place" or a redraft (RECORD.md chain tables, lines 34-37 and 200-203; the rechecks passed them).
- 19 are from 11 plant passes that had a surplus of findings over caught plants (passes lines 25, 26, 32, 67, 71, 87, 94, 96, 98, 116, 131).
- 2 are from `verifier-psreadme` (no passes row; `lead.md` line 871; fixed in `56ba4a9`).
- 1 is a note (polish1's out-of-scope observation, lead.md line 746; the record does not count it).

Dispositions are: sent back (the pass is a documented revision round), restated, rejected (lead.md line 178 calls verifier-w1f32's (a) findings copy artifacts), or "not recorded" where I found no sentence. Two findings sit in the planted copies' own commit messages (verifier-w1f64 and verifier-w2xf) and are probably consequences of the plants; I could not confirm that from the record.

### 4.2 The record's a and b against what I found

`pass_counts.csv`: for each of the 46 verifier passes, the row's a+b, the plants caught, my genuine findings, and whether a+b minus genuine equals the plants caught.
- **43 of 46 passes tie exactly.**
- **3 are explained:** verifier-w4trig (a3 b3 = 6; one plant, the sign of `r_neg`, is counted twice because it also broke the -Werror build; lead.md line 561 says "no non-plant defect"); verifier-w5readme3 (a7 b1 = 8; two plants each span two findings, F3+F6 and F5+F7, so 7 findings cover 5 plants, and F8 is genuine); verifier-w6examples (a2 b2 = 4; one finding, F1, covers two plants, the wrong constant in both `main.c` files).
- I found no pass whose a or b contradicts the verifier's own list.
- **Limit.** 17 plant passes have a+b equal to the plants caught. I did not enumerate their findings from their reports; "0 genuine" for them rests on the record's counts and, for a few, on lead.md saying the findings were exactly the plants (w6filmretime, line 836; w5aug, line 691). It is a consistency result, not a recount.
- **A tag against the definition.** verifier-w2xf tagged a false claim about a replay count as (a); by `GLOSSARY.md` lines 27-28 a false claim is (b).
- Where the kit class is not itemised in the verifier's file, `kit_class_basis` says it is my reading.

### 4.3 Send-backs

`sent_back` is true on 15 rows (passes lines 8, 13, 16, 25, 26, 32, 33, 37, 42, 43, 67, 71, 87, 110, 116). `data/sent_back_evidence.csv` gives, per row, whether a revision followed and the evidence.
- **Revision followed (8):** lines 8 and 13 (Phase 0 scaffold, "twice - the lead restated its own prose each time", RECORD.md lines 36-37); 16 (the Wave 0 entry, "once - restated in place before push"); 42 and 43 (SF-0, "twice"); 67, 71 and 87 (post-verdict commits `d87c87c`, `f3eea91`, `a41f026` that verifier-w5metrics sourced; passes line 88 is a fixer pass 2 on the same work as 87).
- **No revision found (7):** lines 25, 26, 32, 33, 37 (planted copies in waves 1 to 3; RECORD.md lines 389-392: the push gate held "until grading left no genuine send-back"), 110, 116 (planted copies; for 110 the one real observation was fixed pre-merge and is not a revision of the verdict; for 116 I found no post-verdict commit named, which is not proof there was none).
- **Against the erratum.** The erratum implies 7 proven and 8 not. My split is 8 and 7. It does not name its 8, so I cannot say which of my 8 it would drop. Lines 8, 13, 16, 42 and 43 are the lead's own text restated in place, not parcel revisions; read strictly as "parcel revision round" the proven count is 3 (lines 67, 71, 87) or fewer. I report all three readings and choose none.

---

## 5. Task 5: voided and redone attempts

Script `attempts.py`; `data/attempts_input.csv` is my reading, `data/attempts.csv` adds the checks (10 of 10 cited phrases found on their lines of `<muse>/ledger/lead.md`).

| id | what | what was graded again |
|---|---|---|
| A1 | verifier-psbench2 (attempt A), the comparison bench: returned CLEAN but had verified the real worktree, not the planted copy (`lead.md` line 876; RECORD.md line 1390, "First verifier attempt void") | nothing; it stands only as an accidental direct re-measure of the real branch (sinks exact, medians within 0.05%) |
| A2 | verifier-psbench2b (attempt B), provenance-gated, caught 5 of 5; payload recovered from its session log after the compact return came back empty (lead.md line 876; RECORD.md line 1396) | the 5 rows named `verifier-psbench2` (key `0305f97a`) hold B's grades |
| A3 | verifier-psbench, the first post-seal bench: 5 of 5, key `c7e98cc5`; not voided; counted in the cumulative (lead.md line 866) | as graded |
| A4 | verifier-w5exp2 attempt 1 died unreported; attempt 2 found exactly the 5 plants (lead.md line 676; RECORD.md lines 889-891) | attempt 2 only |
| A5 | parcel-w6captions first attempt died on a provider quota 429; a Spark retry re-derived everything (lead.md line 856) | the parcel was redone; its verifier then caught 5 of 5 on copy `c537e0d` |
| A6 | the SF-1 verification was stopped before any verdict and restarted on a revised text (lead.md line 429) | no findings consumed; the restarted pass is passes line 54 |
| A7 | plant.py refused draft plants whose new text already matched the real tip; replaced before dispatch (lead.md lines 640, 761) | no verifier ran on the refused drafts |
| A8 | a union-semantics check ran in MSYS bash without git on PATH and printed a false "identical"; discarded (lead.md line 333) | the lead's own check |
| A9 | toy4-shepherd's first agent ended mid-work; a second finished it (lead.md line 975) | the planted copy was verified once, 5 of 5 |
| A10 | a toy follow-up to a completed child arrived tool-less; a fresh fixer was used (lead.md line 1000) | not planted work |

By key hash: `verifier-psbench`, `-psbench2` and `-psbench2b` have neither a usage nor a passes row; `verifier-w5exp2` has one of each (believed to cover both sessions, from verifier-w5metrics' F1). Board-run first attempts (lead.md lines 537, 573, 597, 655, 951, 968) are execution retries; nothing was graded on them. The 39 unmatched `*-draft.json` key files are consistent with A7 (superseded drafts); I did not open them, so that is an inference from their names and their hash mismatch. verifier-PL2's note said lead.md line 876 calls the first bench run's records superseded; I did not find those words there.

---

## 6. Task 6: earlier rounds

Script `earlier.py`; `data/earlier_rounds.csv` (each cell has a source). Read at commits: ParcelRound `f42242e` (CASE-STUDY.md and -2 to -6), `CASE-STUDY-7.md` at `894d125`; HonestHarness `main`, `Rounds/HonestHarness-R1/`; `<repos>/honestharness-r2-ledger/`. A figure the record does not give is "not recorded".

### 6.1 Rounds with no planted copies

| round | lines matching "plant" in its case study | reading |
|---|---|---|
| ParcelRound 1 | 0 | none |
| ParcelRound 2 | 0 | none |
| ParcelRound 3 | 6 | the owner decided "no planted faults" (CASE-STUDY-3 line 149); 32 planted controls tested the docs gate (29 of 29 mutations killed): gate mutations, not planted copies |
| ParcelRound 7 | 0 | none (read at `894d125`) |

### 6.2 Rounds with planted copies, as their records state them

| round | harness | lead | parcels | verifiers | planter, grader | plants | caught | missed | shapes of the misses |
|---|---|---|---|---|---|---|---|---|---|
| ParcelRound 4 | a Claude session (harness name not stated) | Opus 5.5 | Opus 5.5 | Opus 5.5 | the lead planted faults to test its own gates; one resumed verifier planted its own | not recorded as a recall figure | not recorded | not recorded | not recorded |
| ParcelRound 5 | a Claude session | Opus 5.5 | Sonnet 5 | Sonnet 5 (the parcels' verifiers); Opus 5.5 (the lead's code) | lead, lead | 4 | 4 | 0 | none |
| ParcelRound 6 | a Claude session | Opus 5.5 | Sonnet 5.5 (five) | Opus 5.5 | lead, lead | 10 | 10 | 0 | none |
| HonestHarness R1 (its own copies) | a Claude session as lead; live batches over a DeepSeek API | Opus 5.5 | Opus (five) | Sonnet | lead, lead | 10 | 10 | 0 | none |
| HonestHarness R2 | not recorded in the lines read | not recorded in the lines read | Sonnet | Haiku | lead, lead | 12 | 11 | 1 | a value left out of a list of encodings (big-endian UTF-16 in a search function; the parcel's tests did not reach it) |

Sources:
- ParcelRound 4: `CASE-STUDY-4.md` line 45 (models) and its observations (planted faults tested gates; no planted copy of a parcel's work went to a verifier).
- ParcelRound 5: `CASE-STUDY-5.md` lines 31-34 (models) and 158-166 ("Planted controls caught 2 of 2, twice"). The shapes (claim in docs): a paraphrase adding a phrase, an unsourced superlative, a rule of engagement misquoted ("within a day" for "in days"), an unsourced sentence.
- ParcelRound 6: `CASE-STUDY-6.md` lines 48-49 (models) and 152-164. Wave 1: each copy held a figure transcribed wrong and a rule changed against its source (widened, narrowed, made optional, or a pending item written as adopted); wave 2: a template line tagged with a section that does not hold its rule, and an escalation order reversed. `archive/round6-ledger.zip` holds 5 keys with 10 plants (counted by `earlier.py`).
- HonestHarness R1: `CASE-STUDY.md` lines 118-123 ("Sonnet verifiers found every planted fault": 8 of 8, and P5's copy 2 of 2). Its archived keys hold 5 files and 12 key rows, because two plants are each recorded as an "edit 1 of 2 / edit 2 of 2" pair, giving 10 plants (my reading of the key shapes).
- HonestHarness R2: `lead.md` lines 1062-1075 (7 of 8), 2496 (2 of 2) and 2762 (11 of 12). Its archived keys hold 6 files with 18 rows, which I did not reconcile with the 12 graded plants (some keys hold more than a copy's two plants, for example the A3 items).

### 6.3 HonestHarness R1 as a reference point for weaker verifiers (its QS4 replay)

HonestHarness R1 ran other models as verifiers on ParcelRound round 6's planted copies (`CASE-STUDY.md` line 220): DeepSeek flash caught 31 of 40 plant-runs (by passes 8, 8, 8, 7); plants that changed a figure or a reference were caught 24 of 24, plants that changed meaning or shape 7 of 16, and a dropped list item never. Round 6's own Opus verifiers caught 10 of 10. These are model tests, not a round's verification; the lead there judged the runs.

### 6.4 Comparison with muse-softfloat

| comparison | made? | confounds |
|---|---|---|
| headline recall, library round (187/195, 0.959) with ParcelRound 5 and 6 (4/4, 10/10) | with caveats, as ranges only | the earlier rounds' plants were 2 per copy, in prose; the library round's were 5 per copy across code, data and prose; the earlier verifiers were Claude Opus or Sonnet; the planters differ (an Opus lead each time; here Wonder); the work differs (a method's own documents against a softfloat library); n of 4 and 10 gives intervals far wider than the library round's |
| library round with HonestHarness R2 (11/12, Haiku verifiers) | with caveats | R2's plants are 2 per copy and mixed code and brief errors; the verifiers were Haiku; the planter an Opus-class lead (not recorded in the lines I read); n = 12 |
| library round with HonestHarness R1 (10/10, Sonnet verifiers) | with caveats | as above; Sonnet verifiers, 2 plants per copy |
| recall by plant class across rounds | left out | the earlier rounds record no class; their plants are almost all prose, so the code and test-data cells have no counterpart |
| recall by wave, verifier or model across rounds | left out | different taxonomies; n of 2 to 12 per cell |
| the toy round (220/220, per copy) with any round | left out | five plants per copy graded as a count; no shape, no key; the planter and grader are the same lead as the library round, and the toy's grading cannot be checked at plant level |
| DeepSeek flash on round 6's plants (31/40) with Spark on the library's plants (178/185) | left out | different plants, planters, harness (an API loop in a sandbox) and grader (the HonestHarness R1 lead, checked by a Sonnet verifier); runs, not copies |
| tokens or cost per verifier pass across rounds | left out | the earlier records do not give tokens by role in a comparable form |

What I will stand behind: muse-spark-1.3 as verifier caught 0.96 of the lead's plants, including every code plant (87 of 87), and its 8 misses are all in docs, test data and metadata. I believe the earlier rounds' figures for Claude verifiers (10/10, 8/8, 11/12) are not distinguishable from it at the sizes involved, but the confounds above mean the sample cannot show it.

---

## 7. Spot checks (two routes for each table)

- **Row counts, tokens, passes, plants, sent_back, escalations, classes, toy rows (25 checks).** `scripts/check_alt.py` recounts from the raw jsonl text with `str.count` and regular expressions, without a json parse of the rows; all 25 agree with `figures.py` and `recall.py`. Examples: tokens input+output regex sum 1,418,065,198 and cached 1,379,156,504; `"grade": "caught"` 187 and `"grade": "missed"` 8; `"sent_back":true` 15; `"role":"verifier"` 46; `"checked_by": "integration"` 65.
- **Keys.** `sha256sum` over the 78 key files, intersected (`comm`) with the 39 distinct `key_sha256` values: 39; hashlib gave the same 39.
- **Sample strata.** `grep -c` on `sample_blind.csv`: 8 miss rows, 30 catch rows; per-wave counts wave5 7, wave6 7, postseal 4, wave4 4 equal the allocation.
- **Re-grade agreement.** `awk` over `regrade.csv`: yes 36, "not comparable (unclear)" 2, as `regrade_join.py` printed.
- **Escalation latency.** `date -d` on the parcel-f64 real rows: 38 s and 2465 s, the same as the script's.
- **Cited lines.** `sed -n 876p` of `lead.md` holds "ATTEMPT A VOID"; RECORD.md line 1390 holds "First verifier attempt void". `attempts.py` and `earlier.py` check every cited phrase on its line (10 of 10 and 7 of 7).

---

## 8. Limits

1. **How hard the plants were.** The lead planted, chose the shapes and graded. The re-grade sample shows consistency with the verifiers' reports, not difficulty. Each verifier has only 5 plants, so no verifier-level difference is ranked.
2. **The model of 10 plant rows is not recorded** (verifier-w6captions and verifier-w6metrics). Spark's recall is 0.962 with the ledger-named rows and 0.956 on usage rows alone. Wonder as verifier has no plant rows.
3. **The toy** has no per-plant shape and no key available; its classes, its recall by class and a key-based re-grade are not available. The 10-copy check is a count check.
4. **Genuine findings** were enumerated for the 29 passes whose a+b exceeds their caught plants or that had no plants; the 17 passes whose a+b equals the caught plants were not recounted from their reports. The kit class per finding is the verifier's tag or my reading; the passes rows give counts only. Some dispositions are "not recorded".
5. **The send-back split** rests on my reading; the erratum names no rows.
6. **Classing is judgment.** 70 rows logged a tie-break; 5 are marked for review (TB7). Recall by class would move by at most one caught row in test data or claim in docs.
7. **Earlier rounds.** Rounds 4 and 5 are graded in prose, and I read their plant counts by reading. ParcelRound 4 gives no recall figure. R2's lead model and harness were not found in the lines I read.
8. **Another session may be working in `<muse>`.** Files outside git were read as they stood on 2026-11-08.

## 9. What the brief or plan got wrong, or left soft

- **The brief's "up to 10 graded plants" for the toy.** The toy has no per-plant grade; I sampled copies and compared counts.
- **The plan's section 4** is correct on all 41 figures I recomputed; only its "04:18" is an author date (the committer date is 04:20:16).
- **verifier-PL2's note** that lead.md line 876 calls the first bench run superseded did not hold when I read the line.
- **The 7 verifiers with no usage row also have no passes row** (the brief did not say).
- **ParcelRound 4 has 20 lines matching "plant", but no planted copy went to a verifier.** The plan's "ParcelRound rounds 4 to 6" is right for 5 and 6; round 4's plants were gate tests.
- **The erratum's 7 and 8** are not reproducible from the record; my split is 8 and 7.
- **The 39 drafts in the keys folder** are unmatched drafts, not findings (the lead's ruling).
- **Departures from my phase 1 design, none changing a result:** no keyword layer for classing; TB5 narrowed and TB8 and TB9 added on first use; the key's file path was used for 48 rows, not only for rows the shape could not decide; the toy was checked by count only.

## 10. Boundaries

- No fenced path (`audit-bundle*`, the Claude audit reports) was opened, listed or searched. My git use at LIB was `show`, `log` and `rev-list` only; I ran no recursive `ls-tree` or `git grep`.
- I read the keys folder (hash-matched keys only; drafts not opened) and the verifier reports of the sampled verifiers by name. I read `<muse>/scratch/toy1/` and `toy2/` files named in the toy's verdict rows, nothing else under `scratch/lead/`. I listed `<muse>/scratch/` at one level and named `<muse>/scratch/verifier-*` folders.
- No file under `<muse>` was written. I started no background process.
