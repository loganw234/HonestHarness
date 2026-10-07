# A lead test for round 2: QS5, and what the harness must provide first

2026-10-06 · written by HonestHarness round 1's lead session, at Logan's
request in conversation

A research note: a proposal for round 2's plan. **Nothing here is implemented
or adopted.** It extends QS5, "lead replay", in the requirements ("REQ",
open-weight-harness-requirements.md:1183-1186), and changes no other
document. What round 2 takes from it is Logan's to decide.

**In short.**
- **Why.** The lead is the role REQ calls least replaceable. A lead score says
  whether a cheaper model can run a round, or only work inside one.
- **Two stages.** First the lead on paper: planning, triage and brief review,
  which today's runner and agent loop can measure. Then the lead operating:
  dispatching, merging and holding, which needs mechanisms the harness does
  not have yet.
- **The record already holds keys.** Rounds 6 and 7 and HonestHarness round 1
  hold the lead's decisions, and the errors later found in them.

---

## 1. Why a lead test

- **REQ's own risk list puts the lead first.** "Plan-writing that finds the
  plan's own errors from code (round 2's three corrections), and card-day
  diagnosis, are the least replaceable skills in the record" (REQ:1484).
- **REQ §8.1 lists what the role demands** (REQ:1119):
  - read two repositories and find the plan's own errors before dispatch;
  - design a behaviour-preserving seam;
  - write briefs that name the trap, and a control that bites;
  - act on escalations within minutes;
  - merge discipline;
  - diagnose under uncertainty;
  - write records that agree with the data.
- **REQ's placement table** (§8.3, REQ:1205) moves the lead off the strongest
  model only when QS5 and QS6 hold on two replayed rounds, and then after a
  live lead-only round.
- **Round 1 measures QS1, a QS6 slice and a QS4 replay.** Those are worker,
  reader and verifier skills. None of them is the lead's.

## 2. What QS5 says now

REQ:1183-1186:
1. Give a candidate lead round 2's request: cft-rebound's asks, with both
   repositories pinned.
2. Score whether it finds the three corrections the real plan found before
   dispatch.
3. Score its briefs with H10.5's linter, and by the brief errors replayed
   parcels report.

It is one scenario, and partly judged. The proposal keeps it as the core, and
adds tests a script can score.

## 3. Two stages

**Logan's point (2026-10-06, in conversation):** testing a lead properly needs
more of the harness's mechanical structure than exists yet. A lead acts. It
dispatches agents and messages them. It keeps a ledger, merges, runs gates,
builds planted copies, and stops at the owner's hold points.

Today the lead applies those as rules by hand. Each is listed, with the
mechanism that would hold it, in the harness notes: sixty from ParcelRound's
round 6 (Rounds/ParcelRound-R6/harness-notes.md), and round 1's, which go in
beside its case study. REQ already names the lead's tools: `dispatch`,
`send_back`, `merge_stage`, `promote_main`, `push`, `rule`/`grant`,
`request_owner_decision`, `pause_all` and `record_draft` (H2.2, REQ:674),
over H1's non-LLM orchestrator.

### Stage A: the lead on paper

This stage needs only `qs/` and round 1's agent loop, with read-only mounts.

- **A1, plan replay.** QS5 as REQ gives it.
- **A2, verifier-report triage.**
  - **Input:** real verifier reports from ParcelRound's rounds 6 and 7 and
    from HonestHarness round 1. Every round 1 verifier classed each of its
    findings in its own ledger file.
  - **Task:** the candidate classes each finding under the send-back rule:
    sent back, merged as a known limit, or restated at the merge.
  - **Key:** the class the lead recorded, corrected where the record later
    showed it wrong.
  - **Score:** by script, with any judged case stated as judged.
- **A3, brief review with real errors.** The candidate gets draft briefs
  holding errors that round 1's agents found in the lead's own briefs:
  - **QS1's brief** asked that `reasoning_content` be "present" in thinking
    mode. Live, DeepSeek emitted none on 43 of 101 turns. P1 built the brief
    as written, and a live batch showed the overreach (round 1's ledger,
    `lead.md` 15:00:40 and 17:01:40).
  - **QS6's brief** said to size cuts by P0's estimate, and gave the sizes by
    bytes/4. P3 found the contradiction in phase 1 (`lead.md` 15:25:54).
  - **P2's brief** said `--mount` refuses a missing source. P2 found by probe
    that it does not, on Docker Desktop (`lead.md` 13:53:53).

  More are planted beside them under the three-commit protocol, as round 1's
  code plants were. The score is whether the candidate names each error
  together with its evidence.
- **A4, decomposition.**
  - **Input:** a body of work and its seam.
  - **Task:** the candidate splits the work into parcels.
  - **Score:** a script checks the parcels' file lists for overlap and for
    coverage.

### Stage B: the lead operating

This stage needs mechanisms that are not built yet.

- **Tools the harness provides,** never the candidate's own shell:
  - dispatch, with a role, a model and a brief;
  - messages;
  - a ledger append that stamps itself;
  - worktrees, and merges checked with `merge-tree`;
  - gate runs;
  - planted-copy builds;
  - the owner's hold points.
- **A replay world.** Parcels' and verifiers' recorded outputs from a past
  round are served back deterministically. A candidate's decisions are then
  scored against the record: a flight simulator, not a live round.
- **The scores:**
  - send-back decisions, and restates made at merges;
  - hold points taken;
  - values read from commands against values typed;
  - the ledger's own corrections.

Stage B comes before REQ's live lead-only round, which stays the last step.

## 4. Keys and protocol

- **Each key is built from the record.**
- **A verifier checks it before any run,** and its hash is committed before
  the first run.
- **The key itself is committed after scoring.**
- **A score that rests on judgement is recorded as judgement.**

## 5. What it cannot measure

Some of a lead's skill is judgement sustained over hours:
- when to end a verifier loop;
- catching its own slip hours later;
- keeping the owner's hold points in a live round.

Neither stage shows those. Only the live lead-only round does.

## 6. Sources

- **REQ:** §8.1 (REQ:1119), QS5 (REQ:1183-1186), §8.3 (REQ:1205), §13.1
  (REQ:1484), and H2.2 (REQ:674).
- **Round 1's ledger,** archived beside its case study at the round's end.
  The entries cited above are in `lead.md`.
- **The harness notes:** Rounds/ParcelRound-R6/harness-notes.md, and round
  1's, which go in beside its case study.
