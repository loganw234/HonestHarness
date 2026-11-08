# P3: the case report's proposals P1 to P18 against the methods' text, and the toy round's practice

Every figure below is made by a script in `scripts/` (run with `python -I`, taking
`--repos` and `--scratch`) and written to `data/`. A claim names its row or its
file and line. Paths are written `<repos>`, `<scratch>` and `<muse>`.

Sources, read at commits (`GIT_OPTIONAL_LOCKS=0`; `git show`, `log`, `rev-list`,
`branch`) or as files: ParcelRound at `f42242e` and its branch `case-study-7` at
`894d125`; HonestFramework at `65447fd`; the kit under
`<muse>/softfloat-bootstrap-kit/`; the library at `b78af18` (`docs/KICKOFF.md` and
`docs/RECORD.md` only; no recursive listing of it); the toy at `084f98b`;
`<muse>/ledger/lead.md`; `<muse>/scratch/toy1` and `toy2` (the folders the toy's
`plants.jsonl` names; only the verifier reports and the plant-dispatch commit
messages); HonestHarness `main` at `b69ed76` and `round2` at `8e392dd`; round 1's
archived ledger zip; round 2's ledger directory (`lead.md`, the parcels' and
verifiers' files; not `keys/`, `briefs/`, `drafts/`, `reports/`, and the stackdump
only listed).

## 1. The scale

Each proposal is split into 3 or 4 clauses (`scripts/clauses.json`, written before
any search hit was read). Each clause is marked by the strongest place that carries it:

| Mark | Meaning |
|---|---|
| RULE-M | a rule in a method file (METHOD, ADOPTION, ADOPTING, FAILURE-MODES, WITH-PARCELROUND, templates) |
| RULE-K | a rule in the kit only |
| ADVICE | in a method file as advice, an example or a default, with no must or never; "paraphrase = yes" where the words differ |
| PART | the clause is partly there; the row says what is missing |
| CASE | only an observation or proposal in a case study, or a pending row of `ADOPTION.md` |
| NEWER | only above the pin (`CASE-STUDY-7.md` at `894d125`) |
| ABSENT | none of the above, after two searches |

The proposal's mark is derived by `scripts/check_marks.py`: RULE or RULE (kit)
if every counted clause is a rule; PARTIAL if one clause is RULE, ADVICE or PART
and another is not; CASE-ONLY, NEWER-ONLY or ABSENT otherwise. Six "context"
clauses (the base a label names, or the setting) are shown but not counted
(`clauses.json`, `_context`; amended before any mark was read).

The marks are my readings. What the scripts guarantee: every cited line holds its
quote (41 cited lines in `data/marks.csv`, 0 failures), and the derivation is
mechanical (`scripts/recount.py` re-derives it by another method: 18 proposals,
no disagreement).

## 2. Task 1: the proposals against the text

Counts (`check_marks.py`, `data/proposal_marks.csv`): **ABSENT 3** (P1, P7, P16),
**CASE-ONLY 1** (P6), **PARTIAL 14**, RULE 0, NEWER-ONLY 0. No proposal is
wholly in a rule; 3 of 18 are wholly absent. The table gives the case report's
label (`data/proposals_raw.csv`) beside mine. Clause detail is `data/clause_marks.csv`;
the quotes and lines are `data/marks.csv`.

| P | Report's label | Mark at the pins | Present (rule, advice or part) | Case only | Absent | Label check |
|---|---|---|---|---|---|---|
| 1 | new | ABSENT | | | all four | agrees |
| 2 | new | PARTIAL | c2: the kit's `plant.py make` copy has "no remote, no refs and no route back" (`KIT:WORKFLOW.md` l131) | c4 (CS6 l160; CS6#4 pending) | c1 allowlist, c3 | overstated |
| 3 | extension | PARTIAL | c2: "check every field that can carry it" (`HF:METHOD.md` l630), about quotation caps | c1 (CS6 l166, a label plant) | c3 | has a base |
| 4 | new | PARTIAL | c1, c3: "The scoped re-check after a fix is the default" (`PR:METHOD.md` l1092); fixes "go back to that verifier" (l940) | c4 (CS4#19 pending) | c2 independence | overstated |
| 5 | extension | PARTIAL | c1: "Derive counts and name lists; never transcribe them" (`PR:METHOD.md` l64), code scope | c2 (CS6#8 pending) | c3, c4 | has a base |
| 6 | new | CASE-ONLY | | c3 (CS3 l717: read the journal, the notice is truncated) | c1, c2 | agrees |
| 7 | new | ABSENT | | | all three | agrees |
| 8 | extension | PARTIAL | c4: "Stop your own background work before you report" (l438); c3 (pause record, l532) | | c1 ceilings | has a base |
| 9 | extension | PARTIAL | c1 (HF FAILURE-MODES C3, METHOD l514, l584); c2 (a sentence that "claims more than is true" is restated, l1126) | | c3 | has a base |
| 10 | extension | PARTIAL | c3: generated copies get a `--check` (`HF:METHOD.md` l350) | | c1 registry | has a base |
| 11 | new | PARTIAL | c1: kit tables name a digest of each input (`KIT:METRICS.md` l39) | | c2 (adjacent), c3 | overstated |
| 12 | reinforcement | PARTIAL | c2: "A figure the documents quote has a script in the tree" (`PR:METHOD.md` l228; CS4#4) | | c3 | has a base, but see 4 |
| 13 | adoption | PARTIAL | c1, c3: the kit carries it, "places by roots each dispatch defines" (`KIT:WORKFLOW.md` l24); CS6#7 is pending | | c2 | has a base |
| 14 | extension | PARTIAL | c1: tree hashes across MSYS and Linux (`HF:METHOD.md` l479) | | c2, c3, c4 | has a base |
| 15 | new | PARTIAL | c1, c3 part: `KIT:BOARD.md` has a lock file and day-1 details | | c2 | overstated |
| 16 | reinforcement | ABSENT | | | c1, c3 | base not found |
| 17 | new | PARTIAL | c1, c2 part: `PROVENANCE.md` for data (`HF:METHOD.md` l127); "record its licence" (`KIT:CLEAN-ROOM.md` l34) | | c3 | overstated |
| 18 | new | PARTIAL | c1 part: "Run the front door from a clean clone" (`HF:METHOD.md` l838) | | c2, c3 | overstated |

Label check (`check_marks.py`): of the 9 proposals labelled "new", 3 agree (P1, P6,
P7) and 6 are overstated, because a clause is already a rule, advice or a part
(P2, P4, P11, P15, P17, P18). "Overstated" means a clause exists, not that the
proposal is already in the text: every PARTIAL proposal has at least one clause absent.

### What the texts already said, in four patterns

1. **The kit often had the clause the report calls new.** P2 (the copy with no
   route to the real tip), P13 (roots) and P15 (a lock file) are kit text.
   `KIT:WORKFLOW.md` l124 says the kit's CS5#8, CS6#4 and CS6#3 steps are ones
   `ADOPTION.md` "still holds as pending". So the kit carried the method's pending
   rows. `ADOPTION.md` rows CS6#4 (l152), CS6#7 (l155) and CS6#8 (l156) are pending and
   are the same ideas as P1's view-first neighbour, P13 and P5.
2. **Some bases the report names are not the nearest text.** P12 names the front-door
   rule (`HF:METHOD.md` l789, about one command); its nearest text is
   `PR:METHOD.md` l228 (a script in the tree for any quoted figure). P8 names
   "time-boxes", which have no hit in ParcelRound or HonestFramework at the pins:
   the time box is a kit rule (`KIT:WORKFLOW.md` l178, `KIT:OWNER.md` l94). P16
   (reinforcement) has no matching rule: `KIT:METRICS.md` l34-35 makes the plants
   table at the round's last entry, the opposite practice.
3. **P4's scoped re-check is a method rule.** I first marked P4 c1 absent. The loose
   second search found `PR:METHOD.md` l1092 and `templates/verifier.md` l45 ("scope it
   to the fix"). What is not in the text is an *independent* checker (l940 sends the
   fix back to the same verifier) and the diff since a copy was verified. Case study 7
   (`CASE-STUDY-7.md` l543, outside the kit) proposes the scope, a smaller model and a budget.
4. **The method has the neighbour, not the act.** P1 (provenance first) has the
   view-first rule (`KIT:ROLES.md` l93) and the lead-side HEAD check at the reveal
   (`plant.py` l289-290), but no verifier-side HEAD quote. P9 has the failure mode
   (declared against executed work) and the restate rule, but no recorded mode
   per authority.

### The round had it, and did it use it? (`data/kit_use.csv`, 11 rows)

Where a clause was kit or method text, the round's record (`KICKOFF.md`, `RECORD.md`
at `b78af18`, `<muse>/ledger/lead.md`) shows: USED 4 (P2 c2, P4 c1, P9 c2, P11 c1),
PARTLY 4 (P8 c2, P13 c3, P15 c1, P15 c3), NOT USED 1 (P13 c1: the root
names `<repos>` and `<scratch>` do not appear in those three files), NOT SHOWN 2
(P8 c4, P17 c2). The count by script is in the file; the rows give each line.
Whether the round "paid for" skipping P13 is P2's step 4, not mine.

### The methods' newer commits (`data/newer_refs.csv`, `scripts/newer.py`)

- HonestFramework: 0 commits reachable from a local ref and not from `65447fd`.
- ParcelRound: 2, both on `case-study-7` (`8b6d6d4`, `894d125`, 2026-10-05); they add
  only `CASE-STUDY-7.md` and `archive/round7-cost-scripts.zip`. `METHOD.md` and
  `ADOPTION.md` are unchanged at `894d125` (the diff names only those two files).
- `CASE-STUDY-7.md` lists nine proposals (l522-583). Reading them: item 4 repeats P4's
  scoped re-check (scope, model, budget); item 3 is near P5's recount (the lead's
  restatements read their constants from the code at the time of writing). The other
  seven do not match a P1 to P18 clause. So: **no proposal has entered a method text
  since the pins**; two have a neighbour in a case study written after them.

## 3. Task 2: the toy round (`data/toy_practice.csv`, `data/toy_provenance.csv`)

Counts: PRACTISED 4 (P1, P6, P8, P16), PARTLY 9 (P2, P3, P4, P5, P7, P9, P10, P12, P15),
SILENT 5 (P11, P13, P14, P17, P18), by `toy_round` in `data/proposals.csv`. The strongest evidence:

- **P1 practised.** The toy's metrics README: "provenance gate: it must quote the
  copy's HEAD" (`TOY:docs/metrics/README.md` l14). `scripts/toy_provenance.py` read all 44
  verifier reports named in the toy's `plants.jsonl`: **44 of 44** quote their own
  `copy_head`, the first quote at line 3 to 21 (median 7), 41 within the first 15 lines.
  Second route: `grep -c -F` of each 40-character head in its report: 44 of 44.
  `verify-carousel.md` l2 reads "Provenance (checked first, re-checked last)". The
  copy-only line was not measured.
- **P6 practised.** The Wave T1 briefs were "report-file-first to scratch/toy1/"
  (`<muse>/ledger/lead.md` l901); all 44 verdict rows name a report file and all 44 exist.
- **P8 practised in the two ways shown.** The same dispatch had "<3 GB child-command ceilings" (l901);
  the board capture window was raised as the registry grew (`TOY:docs/RECORD.md` l115-119).
  Process ownership and checkpointing are not shown.
- **P16 practised for the plant ledger.** Key hash committed before the verifier is
  dispatched, the verdict row completed at the merge (README l9-18). The toy keeps only a plant ledger.
- **P4 in part.** "Lead merge fixes, each delta-checked" (RECORD l231), by the lead, not
  by an independent checker.
- **P2 in part, not strongly.** The toy fences its ledger from the verifier "by name"
  (README l15), which the proposal calls the weaker form.

The toy's own briefs are not a readable file: the toy's record names `scratch/toy1` and
`scratch/toy2`, which hold the lead's commit-message drafts (`msg-plant-*.txt`, a plant
ledger's commit message), the verifiers' reports and scripts, but no brief. The briefs'
features are known only from the lead's entries (l901, l935). So any "per-field checks in
a brief" (P3) or "roots in a dispatch" (P13) is SILENT or PARTLY for want of the brief, not
shown to be absent. The toy's `plants.jsonl` has 90 rows, 44 dispatched and 44 verdict
rows (5 plants each, all caught) and 2 `lead_trim`; it has no per-plant shapes.

## 4. Task 3: HonestHarness rounds 1 and 2 (`data/honestharness_rounds.csv`)

Marks by proposal: ADOPTED 4 (P1, P4, P6, P13), BOTH 4 (P2, P5, P7, P8), MET 2 (P9, P10),
NEITHER 6 (P3, P11, P12, P14, P16, P18), NOT APPLICABLE 2 (P15, P17). Highlights, each with
its line in the file:

- **P1, P2 adopted in round 1.** Round 1's verifiers recorded the copy's HEAD and its
  parent (`verifier-P1.md` l9) and checked the copy held "one parent, no ref, remote, branch"
  (`verifier-P5.md` l101). One verifier ran a git command in the real checkout and disclosed it (`verifier-P3.md` l166).
- **P5 met in round 1:** the lead's "hand-typed golden count of 44, which was 38"
  (`lead.md` l696), recounted by script.
- **P6:** round 1's reports arrived as final messages (`lead.md` l184); round 2 filed them
  "verbatim, each from the agent's final message" (round 2 `lead.md` l1060). No spilled or
  truncated report was found by the stems.
- **P8:** "I started no background process" (round 1 `P1.md` l407); round 2 met a leftover
  QS9 sandbox (`lead.md` l555) and a stray `grep.exe.stackdump` in the ledger root (l6321).
- **P7:** round 1's parcel named its own first run "void" in an entry heading (`P4.md` l605).
- **P13 adopted:** round 1's plan names `<repos>` roots (`PLAN.md` l568).

Rounds 1 and 2 had no bench hardware (P15), no music, images or fonts (P17), and no public
judge map (P18), so those three proposals mark NOT APPLICABLE or NEITHER there.

## 5. Findings for other parcels, and what the brief or plan got wrong

- **For P2 (step 4):** P13's "adoption of round 6's clause, which this round skipped" matches
  the kit text (`KIT:WORKFLOW.md` l23-25) and the round's record (no root names in
  `KICKOFF.md`, `RECORD.md`, `lead.md`); the verdict on "paid for" is theirs. P16's "adopted
  mid-round after the owner's correction": I found no rule it reinforces.
- **For P1:** the toy's `plants.jsonl` has `copy_head` on its dispatch rows (44), which the
  library's file lacks. `KIT:METRICS.md` l34-35 puts the plants table at the round's last entry.
- **The brief's labels:** the brief says the case report labels are "new, reinforcement or
  extension"; P13's label is "adoption". I kept it as the report wrote it.
- **The brief's note on the local ParcelRound checkout** (37 commits behind the pin): I read
  only at SHAs; `git rev-list --all --not f42242e` gives 2 commits, both on `case-study-7`.
- **Plan §6 P3 item 1** names "templates" and "case studies" as places but not how to treat a
  case study; I treated one as a lower tier (CASE). Not an error.
- **Two sources the plan lists were not usable as stated:** the toy's briefs (above), and round 2's
  case-study draft (lost with an old scratch, per the lead).

## 6. Checks on my own figures

| Table | Route 1 | Route 2 |
|---|---|---|
| 18 proposals | `proposals.py`: 18 rows, ids P1 to P18 in order | `grep -c -E '^- \*\*P[0-9]+\.'` of the case report: 18 |
| Marks by proposal | `check_marks.py`: ABSENT 3, PARTIAL 14, CASE-ONLY 1 | `recount.py`: the same, no disagreement |
| 41 cited lines in `marks.csv` | `check_marks.py`: 0 failures | `sed -n` of 10 lines (`PR:METHOD.md` l438, l940, l1092, l1301; `PR:ADOPTION.md` l152, l155; `HF:METHOD.md` l630, l838; `KIT:WORKFLOW.md` l24, l178): each reads as quoted |
| Toy HEAD quotes | `toy_provenance.py`: 44 of 44 | `grep -c -F` per report: 44 of 44; `grep -c '"copy_head"'` of the plants file: 44 rows |
| 34 other citations | `cite_check.py`: 0 failures | control: with one quote and one line altered in a copy, `cite_check.py` reports 2 failures and exits 1 |
| Blind re-mark (seed 1: P2, P3, P5, P8, P9) | first-pass marks | `data/remark.csv`: a `git grep` route agrees on the proposal mark in 4 of 5 (P5 disagrees); on clauses it was narrower than reading, missing one clause each in P3, P5 and P9 |

The re-mark tests consistency of my reading, not correctness, and I made it after the
first pass, so it is not blind in the strict sense.

## 7. Limits

- The marks are readings of text by one agent. A different reader may mark a clause ADVICE
  rather than RULE-M or the reverse; the file and line are given so a reader can.
- Negative searches are against named stems. The first pass missed P4's rule; the loose
  second pass (`scripts/loose.py`, `data/loose_searches.csv`, 548 lines listed, read in
  part: P1, P2, P3, P4, P5, P6, P7, P11 and P16 in full; the larger lists for P8, P9, P10,
  P12, P13, P17, P18 sampled) corrected it and found `HF:METHOD.md` l630 for P3. An ABSENT
  mark means no hit in both stem sets and the reading, not a proof.
- The kit's `method/` folder holds copies of the method files; I read the pinned SHAs instead and
  did not diff the two.
- The `ADOPTION.md` registry shows the adoption state at `f42242e`; it is the method's own
  list, and I count a pending row as CASE.
- Task 2 reads the toy's lead entries as the toy's record; they are Muse's lead's account.
  The toy briefs and the verifiers' prompts are not readable.
- Task 3's scan is by stems over about 31,000 lines; I read the samples that the highlights
  quote, not every hit (3,915 candidate lines in `data/hh_candidates.csv`).
- Library recursion: no recursive listing or search of the library repository was made; only
  `git show` of named files (`docs/KICKOFF.md`, `docs/RECORD.md`).

## 8. Reproduce

    python -I scripts/proposals.py --repos <repos> --scratch <scratch>
    python -I scripts/corpus.py --repos <repos> --scratch <scratch>
    python -I scripts/locate.py --repos <repos> --scratch <scratch>
    python -I scripts/newer.py --repos <repos> --scratch <scratch>
    python -I scripts/check_marks.py --repos <repos> --scratch <scratch>
    python -I scripts/loose.py --repos <repos> --scratch <scratch>
    python -I scripts/recount.py
    python -I scripts/toy_scan.py --repos <repos> --scratch <scratch>
    python -I scripts/toy_provenance.py --repos <repos> --scratch <scratch>
    python -I scripts/hh_scan.py --repos <repos> --scratch <scratch>
    python -I scripts/cite_check.py --repos <repos> --scratch <scratch>
    python -I scripts/assemble.py --repos <repos> --scratch <scratch>

`marks.csv`, `kit_use.csv`, `toy_practice.csv`, `honestharness_rounds.csv` and
`remark.csv` are made by hand; the scripts check them.
