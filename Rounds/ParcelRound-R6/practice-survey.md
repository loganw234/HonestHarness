# Which proposals were practised: the survey of 2026-10-02

A fact-gatherer agent wrote this on 2026-10-02, read-only, for round 6's plan.
The lead re-read these of its claims at their sources:
- the send-back rule's origin (ODE lead.md:1055-1060);
- "no Monitor" (CERT lead.md:951);
- verifiers reading the parcel's ledger (S56 briefs/verifier-W1.md:13);
- parcels owning their docs (S56 briefs/S1.md:46-56);
- main moving once per round (ODE lead.md:1523);
- the brief-errors line absent from all 37 cft-fp256 parcel briefs since 2026-09-25 (a grep of every `Data/runs/*/briefs/*.md` under several phrasings; the 55 verifier briefs never carried it);
- round 5's dispatch as "sonnet" (loganw-dev-ledger lead.md:275);
- SPEC decision 19 (loganw.dev SPEC.md:143-144).

The other rows are the agent's reading, cited so they can be checked.

**Path key.**
- `M` is ParcelRound METHOD.md; `T/` is its templates.
- `R4a` and `R4b` are round 4's first and second ledgers, from `archive/round4-ledger.zip` and `round4-second-ledger.zip`.
- `P` is loganw.dev `docs/ROUND1.md`; `SPEC` and `LVAL` are that repository's `docs/SPEC.md` and `docs/VALIDATION.md`; `L` is `loganw-dev-ledger/`, loganw.dev's round ledger, local.
- cft-fp256's round directories, under `Data\runs\`: ODE (2026-09-25), CERT (09-28), REV7 (09-29), AUD (09-29), FIX (09-30), S56 (09-30), LANG (10-01), S6 (10-02, live).
- `RM` and `VAL` are cft-fp256's `docs/ROADMAP.md` and `docs/VALIDATION.md` at `4190a47`.
- "ODE lead:1057" means that round's `ledger/lead.md:1057`, and "S56 b/S1:25" means `briefs/S1.md:25`.

## Summary

| case study | practised in a later round | in part | only in the round that proposed it | no evidence | total |
|---|---:|---:|---:|---:|---:|
| CS3 | 11 | 6 | 0 | 1 | 18 |
| CS4 | 19 | 2 | 1 | 1 | 23 |
| CS5 | 4 | 0 | 8 | 1 | 13 |
| all | 34 | 8 | 9 | 3 | 54 |

**Corrected 2026-10-02 15:43 by the lead**, on a verifier's finding. The agent counted CS4#19 and CS4#23 as practised in a later round. But round 4's second round (R4b) is where both were proposed: observations 29 and 31 sit under "Observations from the second round" (CS4:225-246). By the survey's own text, #19 was later replaced by verifying the work instead, so it counts as origin-only. #23 is practised later only in part, in the fixes round, so it counts as in part. The agent first wrote 36 / 7 / 8 / 3.

For round 5, the owner applied CS3 and CS4 by decision: SPEC decision 19, with 26 of the 41 listed as rules in force. 25 of them are at P:136-189, and CS3#4 is at P:200-201. Not among them:
- CS3: #1, #5 (only in part, via P:148), #6, and #12 to #18 (#17 is in b/_common but not in the plan);
- CS4: #3, #4, #19, #22 and #23.

## Table A: the 54 proposals

**CS3** (`CASE-STUDY-3.md`)

| id | proposal | type | § | practised? (evidence) | conflicts |
|---|---|---|---|---|---|
| CS3#1 L633 | Brief a send-back as a new agent when it can't be resumed; give the fixer the report, ledger and worktree | reversal | §8/§3 | **yes**, S56 only: lead:500-508; b/S1-sendback:1-9 ("its ledger is your memory"); S3- and S4-sendback briefs. Other rounds resumed the same agent: R4a lead:182, 344; ODE lead:581-583 (SendMessage); L lead:516, 529 | reverses M:786-790 |
| CS3#2 L638 | The stamp rule in T/ledger and in every brief, fixers' included; typed stamps err in both directions | reinforcement | §4 | **yes**, but the template never changed. R4a README:50-52 (it repeats the old "ahead" claim), b/P1:83, b/P2:106, b/P3:98; P:164, 198; L README:45-49 ("missed in both directions"); L b/_common:98; ODE 7/7 briefs (b/verifier-V4:67); AUD README:3; every later cft brief; a fixer's brief at S56 b/S1-sendback:62. A lapse at ODE lead:182-190 | corrects M:349-352 |
| CS3#3 L644 | A parcel's question for the lead goes in urgent/, and the brief says so | reinforcement | §4 | **yes** in R5: P:165, L README:66, b/_common:96-97; used in L urgent/P2-film-thread-door.md and P4-snapshot-…md. REV7 used it (urgent/P2-proposals.md:1-2). R4a has the template text only (README:77-80). From AUD on, replaced by the ledger plus direct messages (B6) | none |
| CS3#4 L650 | Archive the ledger from the working copy, keeping its timestamps | extension | §4 | **yes**: the round-4 zip has 14 entries with 13 distinct original mtimes; the round-5 zip has 38 entries with 33; L README:5-6; P:200-201. cft never archived; it keeps the working copies (ODE README:62-69) | none |
| CS3#5 L657 | A watch's expiry is when to re-arm and do a full read | reinforcement | §4 | **yes** in R5: P:147-149; L lead:31-32, 69; b/_common:94-95. **Partly** in R4a: lead:71-72 (re-armed an hour late). **No** in cft: ODE lead:584; CERT lead:951 | none |
| CS3#6 L661 | The lead watches urgent/ continuously and reads the rest at set points | reversal | §4 | **partly**, in R5 only and not as a rule: L lead:26, 31, 446, 870, 69. R4a watched the whole directory (lead:333-336). cft dropped urgent/ | reverses M:463-469; T/check:65-68; T/ledger:115-116 |
| CS3#7 L672 | The lead's seam commits and its records (VALIDATION entry, commit messages) go past a verifier before main moves | reinforcement + new | §5/§7 | **yes, strongly.** R4a lead:471-484. R5 P:153-154, broken at L lead:626 and remedied by b/verifier-seam:17-24, 209-210; L lead:956, 1142; LVAL:1782, 1887. ODE lead:1071, 1444-1457, push 1523. VAL:15647, 15851. RM:3862, 4046-4047, 4543-4544. FIX VAL:16352-16356, 16441-16444. S56 lead:129, 806. LANG lead:318-328. S6 lead:326-328, 727, 841-877. Final-seam briefs: ODE V10:5; REV7 R6:7, 62; FIX F4:7; S56 W6:7; LANG VI:7, VI2:12; S6 VI1:14 | none |
| CS3#8 L679 | A verifier's list includes the lead's grants and rulings made after dispatch | new | §6 | **partly.** R5 P:173-174, and b/verifier-seam:183 attacks a grant (L lead:465). In cft they are required reading, not items to attack: S56 b/verifier-W1:13, W2:14, W3:15; LANG VL1:17, VL3:25; FIX F2:15; AUD A2:17; S6 VR8:15 | none |
| CS3#9 L683 | "Check every claim in a comment, doc or commit message" is on every verifier's list | extension | §6 | **yes**: R4a lead:435-438; P:173-174; L b/verifier-P0:166, b/verifier-seam:209-210; in at least 39 of 54 cft verifier briefs (ODE V9:132, CERT C2:64, REV7 R1:38, S56 W1:41, LANG VL1:58) | none |
| CS3#10 L689 | Side notes get a step of their own, every round | new | §6 | **yes** in R5: P:181; b/_common:236; b/verifier-P0:207; L lead:1148-1193; LVAL:1907. **Partly** in cft: there is no side-notes field, but every finding is labelled (a), (b) or other, and "other" is restated or recorded as a known limit (ODE lead:1071-1075; VAL:15492…17153) | none |
| CS3#11 L694 | Freeze what is audited | new | §7 | **yes**: R4a verifier-P0:5, 420, 717 (fresh clones); P:16-17, 182-183; L lead:33-34; b/verifier-parcel:50-56. Every cft verifier brief but one names a frozen tree (ODE lead:1038, S56 W1:15, LANG VL1:21); drafts are frozen too (LANG lead:321) | none |
| CS3#12 L696 | Check the gate budget against the merged diff for each batch, and say why main moved on a FAIL | relaxation + extension | §7 | **yes** in cft: CERT lead:1030, 1155; AUD lead:615; ODE lead:1373; FIX VAL:16446-16459; RM:4851 | relaxes M:694-699 |
| CS3#13 L701 | Report processed tokens beside the harness figure, in the final report | new + reinforcement | §7 | **partly**, in case studies only: CS4:248-262, CS5:290-333. No later ledger or VALIDATION entry records any cost | modifies M:704-705 |
| CS3#14 L705 | Settle at kickoff what the owner wants to see first | extension | §7 | **partly**: asked and recorded, often mid-round. R4a lead:82-89; R4b lead:11-15; L lead:231, 1217-1225; REV7 lead:5; ODE lead:1360-1370, 1554; CERT lead:134; LANG lead:8; S6 lead:23, 216-224 | none |
| CS3#15 L713 | Decide per round whether the lead sits between verdict and fix | new | §8 | **no evidence.** The lead sat between verdict and fix every time (ODE lead:1019-1036; S56 lead:362-371) | none |
| CS3#16 L719 | A verifier may reuse a run with identical inputs | relaxation | §6 | **partly**: FIX b/verifier-F4:69 (reuse by run id and commit); ODE b/verifier-V4:35 ("read, do not rerun") | relaxes M:600-601, 608-609; T/verifier:37-38 |
| CS3#17 L725 | Fast-forward to the base and check its SHA; never switch another session's branch; watch CI for "cancelled" | reinforcement | §3 | **yes, except the CI part**: b/_common:12-21; b/verifier-parcel:63-66; CERT b/P1c:16, b/P2c:10, b/P3b:10; ODE lead:1370; REV7 lead:29 | none |
| CS3#18 L732 | A sweep is a round | extension / replacement | §7 | **partly**: no sweep ran later. Read-only surveyors worked at a fixed SHA before a verified plan: CERT lead:17; LANG lead:7, 11-18; S6 surveys/README:3-5 | replaces M:701-703 for a standalone sweep |

**CS4** (`CASE-STUDY-4.md`)

| id | proposal | type | § | practised? | conflicts |
|---|---|---|---|---|---|
| CS4#1 L305 | The lead's P0 goes past a verifier before the parcels that read it; others need not wait | extension (+ relaxation) | §2 | **yes**: R4a lead:33-61; SPEC:141-142; P:14-17, 145-146; L lead:3-39, 418-435. cft verified the plan (CERT, LANG, S6), not the seam commits before the parcels: S56 lead:1 then 129; REV7 lead:34; AUD lead:23 | none |
| CS4#2 L309 | A trap one round measures goes into the next seam as a refusal | extension | §2 | **yes**: R4b verifier-P0:121-122; P:169; LVAL:1219 | none |
| CS4#3 L312 | A tool's check that no stage runs is flagged | extension | §2 | **yes**: R4b lead:68; FIX VAL:16471; RM:4041-4043; S56 lead:372-377 | none |
| CS4#4 L314 | A spike states its cases; a quoted figure has a script in the tree | new | §2 | **partly**: S56 b/S2:39 only | none |
| CS4#5 L318 | Name a control by the property that makes it bite, or run it first | extension | §3 | **yes** in R5: P:167-168; b/_common:212-214; b/P4:192. cft names specific plants (S56 b/S1:40-45) but states no rule | none |
| CS4#6 L321 | Name each agent's scratch directory; no secrets in agents' directories | new | §3 | **yes**: R4a urgent/lead-shared-scratchpad.md:1-16 (its origin); P:160-161; L README:51-52; b/_common:103-108; CERT b/P3b:48; S56 W1:68; LANG VL1:21 | none |
| CS4#7 L323 | The READY standard is stated before the first pass | new | §3 | **yes** in R5: P:162-163, 203-212; b/verifier-parcel:92-98. In R4a only from the third pass (lead:362-376). cft replaced it with the owner's send-back rule (S56 W1:58-64) | none |
| CS4#8 L325 | "What I did not do" is a claim; the lead checks its tree after every agent | extension | §3 | **yes**: R4a lead:35-38 (its origin); P:155-156; b/verifier-parcel:99; ODE V9:183; S56 W1:85, lead:502 | none |
| CS4#9 L329 | The lead arms its watch with its first dispatch | reinforcement | §4 | **yes** in R5: P:147-149; L lead:26, 31-32, 870. **No** in cft (CERT lead:951) | none |
| CS4#10 L331 | Re-arm on expiry, keep the snapshot, one watch at a time on its own files | extension | §4 | **yes**: R4a lead:71-72, 331-341 (its origin); P:147-149; L lead:31-32 | none |
| CS4#11 L333 | When a pause is announced, each agent records where it is | new | §4 | **yes**: R4a lead:157-169, P1:27-40; R4b lead:25-31; P:166; L README:54-55; ODE lead:540-585, 997-1007; S56 lead:378-415, with the owner's words at 380 | none |
| CS4#12 L334 | The lead's decisions go in the ledger first, then the message | reinforcement | §4 | **yes** in R4a (lead:409-410, 428) and R5 (P:150). cft records every decision it messages (AUD lead:45, 67, 86; S6 b/verifier-VR8:26), but not their order | none |
| CS4#13 L338 | A gate that reads source text is a stated limit; the guarantee is a check of behaviour | extension | §5 | **yes**: R4a lead:362-376; P:175-176 | none |
| CS4#14 L342 | A limit is stated by the behaviour it concedes | new | §5 | **yes**: R4a lead:507-513; P:175-176 | none |
| CS4#15 L344 | The lead's fixes go back to the same verifier, which picks its own faults | extension | §5 | **yes**: R4a lead:111-131, 480-482; P:151-152; L lead:244-418; S56 lead:388, W1:21, W4:21, W5:40 | none |
| CS4#16 L349 | A stated limit is tested: the verifier's evading fault must land inside it | new | §6 | **yes** in R4a and R5: R4a lead:417-419, 466-468; P:177-178; b/verifier-parcel:97-98; L lead:1144. **None** in cft | none |
| CS4#17 L351 | A claim's domain and quantifier are claims | extension | §6 | **yes** in R5: P:179-180; b/_common:164-165; b/verifier-parcel:117-118 | none |
| CS4#18 L353 | A figure crossing into docs carries its definition, or is re-measured | new | §6 | **yes** in R5 (P:179-180); **partly** in cft (FIX b/verifier-F4:60-62; ODE lead:1454) | none |
| CS4#19 L355 | Work after the verifier's cut is stated as unverified | new | §6 | **origin only** (corrected): practised in R4b, which is where it was proposed (lead:33-42, 83-84; verifier-P0:31, 168). Later replaced by verifying that work instead (L lead:1191-1193; cft's final-seam briefs, e.g. ODE V10:18) | none |
| CS4#20 L360 | A seam changed mid-round is checked against every open branch | new | §7 | **yes**: R4a lead:209-217; P:187; L lead:859-861, 926-928 | none |
| CS4#21 L362 | Prepare the merge while the verifier works; the verdict still gates main | new | §7 | **yes**: R4a lead:449-458; P:188-189; REV7 lead:103; S56 lead:611; AUD lead:189 | none |
| CS4#22 L364 | A claim in two places is corrected in one; the docstring points to the document | reinforcement | §7 | **no evidence** as stated; the same idea for site content in R5 (b/P4:15, b/P5:43-44, L lead:1070-1087) | none |
| CS4#23 L367 | A lead-only round is a shape of its own | new | §7-§8 | **partly** (corrected): R4b is its origin (README:3-4, lead:1-86). Later, partly in FIX (lead:15, 50; VAL:16352-16353) | none |

**CS5** (`CASE-STUDY-5.md`, branch `round5-case-study`)

| id | proposal | type | § | practised? | conflicts |
|---|---|---|---|---|---|
| CS5#1 L343 | The lead's seam commits and records go past a verifier, all round | reinforcement | §2 | **yes**, as CS3#7. After CS5: LVAL:1887; S56 lead:129, 806; LANG lead:318-328; S6 lead:727, 841-877 | none |
| CS5#2 L346 | After a seam change, the lead checks its own controls' assumptions | new | §2 | origin round only (L lead:919-922) | none |
| CS5#3 L351 | No brief holds the owner's personal data; a privacy gate holds the rule | new | §3 | origin round only (b/verifier-parcel:86-89; b/_common:172-174; L lead:603, 874) | none |
| CS5#4 L354 | A rule the brief states and no gate reads goes on the verifier's checklist by name | new | §3 | origin round only (b/verifier-parcel:37-39, 154-156) | none |
| CS5#5 L358 | Hold rendered text to a subset both readers agree on | extension | §5 | origin round (b/_common:182-191; L lead:793; LVAL:1393) | none |
| CS5#6 L361 | Pin the parser's version in one file the desktop and CI both read | new | §5 | origin round (loganw.dev `.python-version`; site.yml:49; verify/run.sh:96-100) | none |
| CS5#7 L363 | A control names its rule, and restores the bytes it planted over exactly | new | §5 | **yes**: L lead:783, 845-848; earlier in RM:3671-3674 (09-28); S56 b/S1:40; R4b lead:53-54 | none |
| CS5#8 L367 | A planted control's parcel tip stays out of the ledger | extension | §6 | **no** (L lead:499, 932 named the tip; no planted controls later) | none |
| CS5#9 L369 | The record names the level at which each shape was measured | new | §6 | **yes** in loganw.dev: LVAL:1680, and after CS5 at 1737, 1883. Not in cft | none |
| CS5#10 L371 | Agents stop their background work before reporting; the lead checks for leftovers | new | §6 | **yes, and before CS5**: CERT b/P3b:48, b/verifier-C6:74, b/verifier-C7:60; ODE V9:183; S56 W1:68, 85; L lead:1237-1239 | none |
| CS5#11 L376 | The case study is written from the ledger and checked by someone else before its push | extension | end of round | origin only (L lead:1248, 1292-1330) | none |
| CS5#12 L381 | A smaller model for work in sentences | observation | — | origin only (SPEC:163-167, the owner's words; P:143-144) | none |
| CS5#13 L385 | Take each agent's model from its transcript | new | §7 | origin only (CS5:316-321) | tension with M:704-705 |

## Table B: practices in neither METHOD.md nor the 54 proposals

| # | practice | rounds, with file:line | level | owner's words |
|---|---|---|---|---|
| B1 | A verifier on the plan of record before code or approval | CERT lead:17, 20-113; RM:3421-3424; VAL:15649-15658. LANG lead:19-55, b/verifier-P1:9. S6 lead:116, 137-214; RM:4596-4600, 4899-4904. **Not** in REV7 (lead:34), AUD (lead:23), FIX or S56 (lead:1) | method | approval asked after the verifier: LANG lead:51-55; S6 lead:216-219 |
| B3 | The send-back rule: only a regression or a wrong answer sends work back; anything else merges as a recorded known limit | ODE lead:1055-1076 (the lead's proposal, 1073); VAL:15274-15275, 15647, 15851, 16164; RM:3867, 4054, 4544, 4672-4673. In briefs from REV7 on (S56 15/15, S6 18/19), e.g. S56 b/verifier-W1:58-64. "Known limits… (Logan's rule)" in every entry | method | ODE lead:1057: "Agreed with the only regression or wrong answer being send backs" |
| B4 | Agents test quickly and hand long runs back to the lead | REV7 lead:15-18, b/P1:61, 69; RM:3863-3866, 4048, 4146-4149; VAL:15842, 16165. Quoted verbatim in REV7 11/11, AUD 7/7, FIX 6/6, S56 12/15, LANG 5/14 and S6 9/19 briefs; FIX b/verifier-F4:69 | method (motivated by the shared desktop) | REV7 lead:15: "…dont have the individual agents all run the full suites, have them hand back large runs to you to monitor rather than them, but they should still verify and test as much as they can quickly…" |
| B6 | Direct messages replace `urgent/`, in both directions | ODE lead:582; REV7 lead:768; AUD lead:45, 67, 86, 247-268; FIX b/Q4:30; S56 b/S1:25, lead:381; LANG b/L1:40; S6 b/verifier-VR8:26. No `urgent/` from AUD on; the lead's own watch was gone by CERT (lead:951) | method | — |
| B7 | No ledger README | none in FIX, S56, LANG or S6; AUD's is three lines. The rules moved into each brief (S56 b/S1:77-80) | method | — |
| B8 | "Logan's decisions this round", recorded verbatim | VAL:15637-15647, 15836-15851, 16162-16166, 16349-16351; RM:3464-3475, 4579-4594; LANG lead:53-55; S6 lead:111-114, 218-222; SPEC:81 onward; L lead:1217-1225 | method | throughout |
| B9 | The owner's standing rules carried from round to round | REV7 lead:24-29; LANG lead:9; S6 lead:29; plans' "How it is held" (RM:3861-3868, 4045-4055, 4141-4149, 4540-4548). The plans name or paraphrase the rules; only the testing rule is quoted verbatim, and that only in briefs. cft's CLAUDE.md carries none | method mechanism; the rules partly project-level | — |
| B10 | Each merge re-made with `git merge-tree` by the integration verifier, to expose hand resolutions | REV7 lead:1409-1412; FIX VAL:16437; S56 lead:699, 810; LANG lead:328 | method | — |
| B11 | The plan restated by the lead before its verifier | once: S6 lead:127-137; once for a record draft: LANG lead:320 | method, not yet a habit | — |
| B12 | The plan of record's sections: what exists; for Logan, then approved; the parcels; the lead's own; how it is held; what it is not; order; a "Built" block added afterwards | RM:3426, 3778, 3910, 4227, 4604; 3464, 4568, 4899; 3812, 3945, 4445, 4672; 4027, 4506; 3861, 4045, 4141, 4540 (none in S6); 3870, 4057, 4127, 4550, 4854; 3760, 3878, 4071, 4170 | project convention; could become a template | — |
| B13 | Design first: the parcel stops, and the lead approves before it builds | REV7 b/P1:30, b/P2:36; AUD b/P1:21, 67; FIX b/Q4:28-30; S56 b/S1:23-30, b/S3:29-31, b/S4:23-25; LANG b/L1:38-40, b/L2:54; S6 b/CV2:76. Approvals: AUD lead:43-101, S56 lead:45, 97, LANG lead:84, 120 | method | — |
| B14 | "The lead's own slips" in every round's record | VAL:15582, 15798, 16083, 16336, 16487-16500, 16663, 16839, 17030, 17172; checked by the integration verifier (FIX b/verifier-F4:61) | method | — |
| B15 | The ledger kept as the round's record and cited by the docs | ODE README:62-69 ("KEPT, not deleted"), lead:1520; CERT README:3-8; REV7 README:3-8; VAL:15635, 15834, 16160, 16352 | method | — |
| B16 | No intentional load on the machine; one run at a time, niced, `docker ps` first | ODE lead:587-602; "Load, and the machine" in every entry; RM:3863-3866, 4049-4050 | project | ODE lead:589-591: "Request V6 not perform the CPU load task if its intentionally loading the machine…" |
| B17 | Read-only surveyors before a plan | CERT lead:17; LANG lead:11-18; S6 lead:31, surveys/README:3-5 | method (part of CS3#18) | — |

The survey's B2 (a verifier on each round's record draft) is CS3#7 and CS5#1, and its B5 (resume notes at a pause) is CS4#11.

## Where later practice departs from METHOD.md and the templates

| METHOD.md or template says | later practice | where |
|---|---|---|
| delete the ledger, or archive it when the case study cites it by time (M:494-498; T/ledger:11-13; T/check:100-101) | cft keeps every round's ledger as its record | B15 |
| `urgent/` and watchers (M:365-445; T/ledger:62-122; T/brief:38-45; T/check:56-61) | abandoned in cft from AUD on | B6 |
| the lead watches the whole directory (M:446-501; T/check:65-68) | the cert round's lead kept none; the rev7 round's read the ledger through one; from the audit round on, the ledgers do not say (corrected by the lead) | ODE lead:584; CERT lead:951; REV7 lead:768; S56 lead:386 |
| read the ledger at three moments (M:331-334; T/brief:33-36) | later cft parcel briefs say only "append only" | S56 b/S1:77-80 |
| a ledger README (T/ledger:3-5; T/check:53) | absent from FIX on | B7 |
| "anything you found that the brief got wrong" (M:227-228, "the highest-yield sentence in the whole system"; T/brief:114-115; T/check:40) | **in none of the 37 cft parcel briefs since 2026-09-25** (the 55 verifier briefs never carried it); rounds 4 and 5 kept it (R4a b/P1:99; L b/_common:233) | the lead's grep, 2026-10-02 |
| verifiers re-run the gate and the rest themselves (M:600-601, 608-609; T/verifier:37-38) | relaxed by B4 | FIX b/verifier-F4:69 |
| a send-back needs no re-brief (M:786-790) | S56 re-dispatched fresh agents | CS3#1 |
| published docs are the lead's alone (M:691-693; T/brief:74-75) | cft parcels write their own docs; only VALIDATION, ROADMAP and CLAUDE.md stay the lead's | S56 b/S1:46-56 |
| a staging branch per merge, main moving on each verdict (M:694-699) | a round branch; main moves at the round's end or at milestones, not per merge (corrected by the lead: the cert round pushed a hotfix first, the language round twice) | ODE lead:1523; CERT lead:354, 1182; LANG lead:367, 700; S6 lead:727 |
| P0 pushed before any parcel (M:107-108) | parcels branch from an unpushed round branch | LANG lead:49; S6 lead:214 |
| parcels' self-reports kept from a verifier until it forms its own view (M:440-444) | verifier briefs start with the parcel's whole ledger | S56 b/verifier-W1:13 |
| cost from the agent cards, in the summary to the owner (M:704-707) | no later round records any cost | — |
| verdicts: confirmed / defect / not determined (T/verifier:91-96) | kept, and each finding is also labelled (a), (b) or other | B3 |

## Retracted or superseded

- CS3#13 is partly superseded by CS4:250-258, which uses only the processed figure.
- CS4#13 is qualified by CS5:154-157 and CS5#5: an allowlist drawn where two parsers agree did hold.
- CS3#7 and CS4#1 are widened by CS5#1 ("all round, not only P0") and carried to the case study by CS5#11.
- No case study retracted CS3#1, #3 or #6. cft simply dropped `urgent/`.

## Caveats (the survey's own)

- No transcripts were read: the final reports to the owner and the dispatch messages are unknown.
- S6 is live: its brief count rose from 16 to 19 during the survey, so the counts are as of about 14:30.
- R4b evidence comes from its ledger, not from the Quantum-Film repository.
