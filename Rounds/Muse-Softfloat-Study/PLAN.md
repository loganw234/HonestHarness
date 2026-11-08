# HonestHarness: how muse-softfloat ran the methods (plan of record, draft 2)

Draft 2, 2026-11-08. The lead is Claude Opus 5.5, in Claude Code. The study
begins only at Logan's approval and go. Its ledger is
`<repos>/honestharness-muse-ledger/`.

## History

- **Draft 1** (`227c553`) went to verifier-PL, on Haiku. It came back NOT
  READY (the ledger, 08:30:26):
  - four facts were wrong: the send-back count, the key check, which earlier
    rounds had planted copies, and recall by model;
  - five sentences said more than their sources;
  - six notes.
- **Draft 2** takes all of them. Each was checked first by the lead's own
  command. Draft 2 also tightens the fence on searches, and records that the
  harness refused a subagent's report file.

## §1 The question

Logan, 2026-11-08, verbatim:

> Lets go ahead and pick up work on this again, while I was busy I entered
> another hackathon which had the dual purpose of being a generalization test
> of the methods, rather than continuing model tests, lets take a look at how
> muse-softfloat handled the methods. Significantly more tracking was done
> with this one from the start, so it should be a thorough source of data
> from a 'weaker' model family than Opus level alot of the prior samples came
> from.

muse-softfloat ran ParcelRound and HonestFramework from a frozen bootstrap
kit. Four things changed at once:
- **The harness:** Muse Code, in place of Claude Code.
- **The models,** from Meta's Muse family:
  - muse-wonder-full-1.0 was the lead and ran most parcels;
  - muse-spark-1.3 ran 43 of the 46 verifier passes, and muse-wonder-full-1.0
    ran the other 3. This counts by the model in each agent's usage row.
- **The domain:** an IEEE 754-2019 softfloat library, with hardware in the
  loop.
- **A fixed window:** the hackathon's, which ended 2026-11-04
  (`docs/KICKOFF.md` line 144). The kit's own calendar was "not strict"
  (line 43).

In Logan's words, "a lot of the prior samples" came from Opus-level models.
The study asks what this run says about the methods when the harness, the
models and the domain change.

**The questions:**
- **Q1, transfer.** Which of the kit's method clauses did the round carry out
  as written? Which did it adapt, and how? Which did it skip? Where did the
  harness force a fallback?
- **Q2, verification by a smaller model.** How did muse-spark-1.3 do as the
  verifier?
  - **Its recall on the planted faults,** by the shape of the fault, by wave
    and by project.
    - The model comes from the verifier's usage row, or from the ledger
      where there is no row.
    - 7 verifiers, holding 35 plant rows, have no usage row.
  - **Its genuine findings,** and the send-backs they caused.
    - The record's erratum (`docs/RECORD.md` from line 1004) reads
      `sent_back` as true only on proven revision rounds.
    - 8 of the 15 rows marked true were not revision rounds.
  - **The attempt voided** because it checked the wrong tree.

  How far can the lead's grading be trusted? A re-grade sample answers that.
- **Q3, escapes.** What reached the seal unflagged? That covers the final
  audit's findings and the adherence audits' slips. Each is sorted into
  HonestFramework's failure families, with the mechanism that should have
  caught it.
- **Q4, the lead.** What did the lead get wrong, in its own text and in its
  actions, and what caught each error?
- **Q5, the case report.** Do the Muse lead's checkable claims hold against
  the record? For each of its 18 proposals:
  - Is it new? Is it already in the methods' text, as a rule or only in a
    case study? Is it there in part?
  - Did the round have it in the kit and leave it unused?
  - Did the toy round adopt it?
- **Q6, roles.** What does this evidence support about placing a Muse-class
  model as verifier, as parcel and as lead? It is stated as field evidence
  beside HonestHarness's measured table, not as a row of that table.

Earlier rounds are compared only where the data line up. Each comparison
names its confounds: who planted the faults, who graded them, what kind of
work it was, and which models held which roles.

## §2 What the study produces

The work goes on the branch `study-muse`, cut from HonestHarness main
(`b69ed76`), in `Rounds/Muse-Softfloat-Study/`:
- **`PLAN.md`:** this file, once approved.
- **`parcels/`:** each parcel's analysis in Markdown, with its scripts and the
  tables it derived. Every number can be reproduced by a command from a named
  commit or file.
- **`REPORT.md`:** the lead's answers to Q1-Q6. Each claim is sourced, and its
  limits are stated.
- **The comparison:** written after the report's draft is verified and the
  fence on the Claude audit reports is lifted. It sets out what those audits
  found, what this study found and what the Muse lead's case report found,
  with the overlaps and the gaps.
- **The ledger,** archived beside the report at the end, as rounds 1 and 2
  were.

The study is published, merged to main and pushed, only after Logan's OK,
because it quotes records outside HonestHarness. Round 2's branch, `round2`,
is untouched. The study's files and round 2's do not overlap.

## §3 Logan's decisions of 2026-11-08, verbatim

He answered through the question tool:
- "Where should the muse-softfloat study land?": "HonestHarness, published
  (Recommended)".
- "The Claude audit reports in audit-bundle/ were fenced from the Muse agents.
  How should this study treat them?": "Fenced until my draft (Recommended)".
- "Beyond the hackathon round's record, metrics, ledgers and audits, which
  sources should the study cover?": "The toy follow-on,Prior rounds' plant
  data". The option he did not choose was the raw Muse transcripts.

## §4 The sources, measured 2026-11-08

`<muse>` is `<repos>/Muse-Softfloat`. It is a workspace folder, not a
repository.

| Source | Where | State read |
|---|---|---|
| The library repository | `<muse>/muse-softfloat` (github.com/loganw234/muse-softfloat) | `main` at `b78af18`: 221 commits, 2026-10-26 10:50 to 2026-11-03 04:18. Tag `v1.0.0` at `957fdae` |
| Its metrics | `docs/metrics/*.jsonl` at `b78af18` | usage 128 rows, passes 131, plants 195, briefs 50, corrections 24, escalations 23, fetches 5 |
| Its record | `docs/RECORD.md`, `docs/KICKOFF.md`, `docs/HARNESS.md`, `docs/studies/SF-0.md` to `SF-2.md` at `b78af18` | |
| The toy repository | `<muse>/muse-softfloat-toy` | `main` at `084f98b`: 224 commits, 2026-11-03 20:05 to 2026-11-07 16:39. `docs/RECORD.md` is 410 lines. `docs/metrics/plants.jsonl` has 90 rows, in a different schema: two rows for each of 44 parcel copies, plus 2 `lead_trim` rows. It is graded per copy, with no shape for each plant (verifier-PL) |
| The workspace ledger | `<muse>/ledger/` | 118 top-level files. `lead.md` is 1,012 lines; its last heading is at line 889 (2026-11-02), and the toy round's entries follow it without headings. `briefs/` holds 101 files and `urgent/` 14 |
| The audits | `<muse>/ledger/auditor-*.md`; `<muse>/scratch/` folders `audit-full/`, `audit-adherence-2/`, `audit-adherence-final/`, `audit-adherence-seal/`, `audit-wave1/`, `audit-wave2/` and `audit-final/` | The adherence audits graded ADHERENT WITH SLIPS at `7c3819c` (10-28), `bc807e6` (10-29) and `751d1d6` (the seal, 11-01). The full identify-only audit ran at `a49991f` (11-01). The auditors are Muse agents, by their usage rows |
| The case report | `<muse>/CASE-REPORT-muse-softfloat.md` | Dated 2026-11-01 in the lead's ledger (`lead.md` line 884); the file was last modified 2026-11-02. It cites `a49991f`, five commits before `main` |
| The kit | `<muse>/softfloat-bootstrap-kit/` | `MANIFEST.txt` pins ParcelRound `f42242e`, HonestFramework `65447fd`, QRO-Crate `8afeede` and cft-fp256 `39f9801` |
| The plant keys | `<muse>/scratch/lead/keys/` | 78 files. The plants rows hold 39 distinct `key_sha256` values, and each matches one of those files. `docs/metrics/plant_keys.sha256` holds 15 hashes, covering 75 of the 195 rows. Each key is checked against its rows' `key_sha256` before use, with `plant_keys.sha256` as a partial second check |
| Earlier rounds with planted copies | ParcelRound at `f42242e`: rounds 4 to 6. Rounds 4 and 5 are graded in their case studies' prose, and round 6's archive holds its keys. HonestHarness round 1 (its archive on main) and round 2 (`<repos>/honestharness-r2-ledger/`, with keys in `keys/`) | Read at commits. ParcelRound's rounds 1 to 3 had no planted copies, and nor did round 7 (`CASE-STUDY-7.md`, on the branch `case-study-7` at `894d125`, outside the kit) |
| HonestFramework | `<repos>/HonestFramework` at `65447fd` | The kit's pin |

**The first look,** from the lead's script over the metrics at `b78af18`
(the study recomputes all of it):
- 187 of 195 plants were graded caught. The lead graded every plant.
- There were 46 verifier passes, 37 NOT READY and 9 READY.
  - 15 rows mark `sent_back` as true.
  - The record's erratum reads 8 of those as not revision rounds.
- 1,418,065,198 tokens, input plus output as the rows give them, over 128
  usage rows.
  - muse-wonder-full-1.0 has 69 rows and muse-spark-1.3 has 59.
  - The rows' cached tokens, 1,379,156,504 in all, are part of input: no row's
    cached count exceeds its input. They are not added again.

## §5 Rules and fences

- **The sources are read-only.**
  - Nothing under `<muse>` is written, moved or deleted.
  - Its repositories are read at commits, with `git show`, `git log`,
    `git ls-tree`, `git cat-file` or `git archive`, each with
    `GIT_OPTIONAL_LOCKS=0`. Never `git status`, checkout, fetch, or anything
    that writes: another session may be working there.
  - Sibling repositories are read the same way. Never `<repos>/cft-worktrees/`
    and never any `Data/runs/`.
- **The fence, by Logan's decision.** Until the lead's draft is verified and
  the lead lifts the fence in `lead.md`, no agent opens, lists or searches
  `audit-bundle/` or `audit-bundle-v2/` at any commit, or any branch, file or
  bundle that holds the Claude audit reports. After that, only the lead reads
  them, for the comparison.
- **Searches name their directories.** Never run `find` or `grep -r` from
  `<muse>` or from the library repository's root, because both trees hold
  the fenced folders. This was tightened after verifier-PL's pass 1, the
  ledger at 08:30:26.
- **Never read:** the IEEE 754 text (`754-2019.pdf`), the media files, and the
  Muse session transcripts, which Logan's decision leaves out of scope.
- **The lead's folder,** `<repos>/honestharness-muse-lead/`, holds the lead's
  drafts and keys. No agent reads it.
- **Privacy.**
  - No absolute path, owner address or key goes in any committed file or
    ledger entry.
  - Quotes from the Muse records are short and attributed.
  - HonestHarness's gate, with its privacy check, holds before each commit,
    and a privacy scan runs before the push.
- **Values come from commands.** Every figure in a parcel's analysis or in the
  report names the command or script that produced it and the commit or file
  it read.
- **Two practices adopted from the case report, as a test of them:**
  - its P1: a verifier's first ledger entry quotes its copy's HEAD and one
    line that only the copy holds;
  - its P6, amended to fit this harness: every agent writes its findings in
    its ledger file first, and its report comes back as its final message.
    The lead files that message verbatim in the ledger's `reports/`. Claude
    Code refused verifier-PL's report file and asked for the findings as text
    instead, which is a data point on P6.

## §6 The work

### Wave 1: three parcels, in parallel

The parcels run on Sonnet. Each works on its own branch in its own worktree,
and adds files only under `Rounds/Muse-Softfloat-Study/parcels/<id>/`.

**P1, the measurements.** It answers Q2, and supplies the figures for Q5 and
Q6 and the comparison with earlier rounds.
1. Recompute every figure in both projects' metrics from the rows at the
   named commits.
2. Class every plant's shape with a written rubric. The classes are code;
   test data; a claim in the docs; metadata or provenance; record
   arithmetic; and other.
   - Each plant is listed with its class and the reason for it.
   - Recall is given by class, wave, verifier, model and project.
   - The toy's rows are graded per copy, with no shape for each plant. Its
     classes come from its keys and its verifiers' reports, as far as they
     allow. Where they don't, P1 says so.
3. Re-grade a sample: all 8 misses and a stratified sample of 30 catches.
   - Each is re-graded from its key and from the verifier's own report or
     ledger. The key's hash is checked first, against its rows'
     `key_sha256`.
   - The result is the sample's agreement with the lead's grades.
   - The 65 rows marked `checked_by: integration` are read as run by the
     lead, as the record's erratum says.
4. The genuine findings: each verifier pass's non-plant findings, with their
   class and disposition (sent back, restated, or limit).
   - They come from the passes rows and the verifiers' ledgers.
   - Send-backs count only proven revision rounds.
5. The voided attempt, and any other attempt the record voids or redoes.
   Plant rows are tied to attempts by `key_sha256`: the comparison bench's
   voided attempt A shares its verifier's name with attempt B.
6. Earlier rounds with planted copies: ParcelRound rounds 4 to 6, and
   HonestHarness rounds 1 and 2. For each, the plant counts, the recall, and
   the shapes of the misses, with the models given by role and who planted
   and who graded. Rounds 1 to 3 and 7 are named as having no planted copies.

**P2, transfer, escapes and the lead.** It answers Q1, Q3 and Q4, and checks
the case report against the record for Q5. It covers the library round.
1. A clause table from the kit's method files. Each clause is marked done as
   written, adapted (and how), or skipped (and why), with its source in the
   round's record.
2. The escapes: every finding of the full audit and the adherence audits
   that the round's own verification did not raise. Each is classed by
   `FAILURE-MODES.md`'s families, with the mechanism that should have caught
   it.
3. The lead's errors, from `corrections.jsonl`, the slips the audits
   attribute to the lead, and the ledger, with what caught each.
4. The case report's checkable claims, checked against the record. This step
   comes after items 1-3, so the report's framing does not lead them.

**P3, the proposals.** It answers the second half of Q5, and covers the toy
round's practice.
1. For each of P1-P18: where the methods at the kit's pins already say it,
   or say it in part, or not at all. The places to look are METHOD.md's
   rules, ADOPTION or ADOPTING, the templates, and the case studies. Also
   whether the method repositories' current heads, read at commit, say more.
2. Which proposals the toy round put into practice, from its record and its
   plants rows.
3. For each proposal, whether HonestHarness's own rounds met the same
   failure, from the records of rounds 1 and 2, as a check on how general it
   is.

### Verification

The verifiers run on Haiku, under ParcelRound's planted-copy protocol as
round 2 ran it.
- **Each parcel's analysis goes to a verifier as a copy,** holding faults the
  lead planted: wrong figures, misclassed rows, misattributed sources and
  overclaims.
  - The key's hash goes in `lead.md` before dispatch.
  - Keys stay out of the ledger until the last planted-copy verifier reports.
  - Copies are separate clones with no remote and no ref to the parcel's
    branch.
- **The verifier re-runs the parcel's scripts** and checks each claim
  against its source.
  - A claim that is false against its source is a wrong answer, and it is
    sent back.
  - A claim stronger than its evidence is restated at the merge.
  - The rest are limits.
- **Two passes at most.** A re-check after a fix is scoped to the fix.
- **The lead's report draft,** and later the comparison, each go to a scoped
  verifier.

### Wave 2: the lead

1. Merge each parcel once its verifier finds it READY.
2. Write `REPORT.md`, and send it to its verifier.
3. Lift the fence, write the comparison, and send it to its verifier.
4. Archive the ledger.
5. Ask for Logan's OK. Then merge to main, run the privacy scan, and push.

## §7 Budget

The study makes no API calls; the agents run on the subscription.
- Wave 1 is 3 parcels and 3 verifiers.
- Wave 2 adds 2 scoped verifiers.
- Re-checks are added as needed, for about 10 agent runs in all.

The account's weekly usage limit can stop an agent mid-pass. It resumes by
message after the reset, as in round 2.

## §8 Risks

- **The record is the Muse lead's,** and its framing can lead ours. Parcels
  build their tables from rows and primary entries before they read the case
  report.
- **The plant data are the lead's.** Recall measures Spark against Wonder's
  planting and Wonder's grading. The re-grade sample checks the grading.
  Nothing here checks how hard the plants were, and the report states that as
  a limit.
- **Comparisons across rounds are confounded.** Planters, the work, the number
  of plants per copy and the models all differ. Each comparison names its
  confounds, or it is not made.
- **The ledger is large:** `lead.md` is 1,012 lines and there are 118 files.
  Parcels search by script and cite lines, rather than summarising from
  reading.
- **Another session may be working in `<muse>`.** Reading at commits keeps its
  uncommitted state out of the study. The files outside git are read as they
  stand on the day, and their sizes and hashes are recorded.
- **A verifier may reach the parcel's branch instead of its copy,** as in the
  case report's observation 1. Copies are separate clones, and the provenance
  entry is checked before any grade counts.

## §9 Order

1. This plan, draft 1, goes to a plan verifier on Haiku.
2. Logan's approval.
3. Wave 1.
4. Wave 2.
5. Logan's OK to publish.
