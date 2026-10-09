# HonestHarness

A harness for running [ParcelRound](https://github.com/loganw234/ParcelRound)
and [HonestFramework](https://github.com/loganw234/HonestFramework) on
open-weight models. Its core is a non-LLM orchestrator that turns the rules
agents now have to remember into mechanisms they cannot route around.

**Status: research, with its first code.** This repository holds the
requirements, the research behind them, and the record of rounds run by hand
that test them. Since round 1 it also holds `qs/`, the qualification suites'
runner, described below.

## What is here

- [Research/open-weight-harness-requirements.md](Research/open-weight-harness-requirements.md):
  the requirements, H1 to H17, derived from the record of cft-fp256's rounds.
  It covers how models are placed and how autonomy follows enforcement.
- [Research/open-weight-harness-research.md](Research/open-weight-harness-research.md):
  tool-calling formats, protocols and serving for open-weight models, as of
  2026-10-01.
- [Research/open-weight-pilot-notes.md](Research/open-weight-pilot-notes.md):
  local pilot models, specialist models, adversarial leads and rented GPUs,
  as of 2026-10-02.
- [Research/curiosity-explorer-direction.md](Research/curiosity-explorer-direction.md):
  the direction the harness is for, "More curiosity gets to survive long
  enough to meet reality". It covers trust for an owner who is not an
  expert, limits and "keep trying", and small specialized models, as
  considerations of 2026-10-03, none implemented.
- [Research/lead-test-for-round-2.md](Research/lead-test-for-round-2.md):
  a lead test for round 2, extending REQ's QS5. Its first stage, the lead on
  paper, needs only round 1's code. Its second, the lead operating, needs
  harness mechanisms not built yet. A proposal of 2026-10-06, none of it
  implemented.
- [Rounds/ParcelRound-R6/](Rounds/ParcelRound-R6/): ParcelRound's round 6,
  run by hand by a Claude session as lead. It holds:
  - the round's plan of record;
  - the practice survey the plan rested on;
  - the harness notes, which list every rule the lead applied by hand, with
    the requirement that would make it a mechanism.
- [Rounds/HonestHarness-R1/](Rounds/HonestHarness-R1/): HonestHarness's
  round 1, closed 2026-10-08. It measured DeepSeek's flash model over its API
  on four suites. It holds:
  - the plan of record and its amendment;
  - the case study, and the table drawn by script from the committed
    records;
  - the harness notes;
  - the round's ledger, archived with a manifest.
- [Rounds/HonestHarness-R2/PLAN.md](Rounds/HonestHarness-R2/PLAN.md): round
  2's plan of record, approved 2026-10-08 and not yet begun. It finishes
  Phase 0 on DeepSeek, with three measurements and the first role-placement
  table:
  - verifying recorded defects;
  - honesty when a task becomes infeasible;
  - the lead on paper.

## The code

`qs/` is the first code: the qualification suites' runner, which measures a
model through any OpenAI-compatible endpoint and records every number against
the stack that produced it. Round 1 built it, and its plan and case study are
in [Rounds/HonestHarness-R1/](Rounds/HonestHarness-R1/).

- **The front door.** `python tools/check.py` runs the gate: the tests, the
  records' schema, the spending guard's arithmetic, privacy and the live
  gate. `python tools/check.py --control` shows each check fail on a planted
  fault.
- **Live mode.** `tools/live.py` is the only place live mode is switched on,
  and only the round's lead runs it. Every batch passes the spending guard
  first.
- **Tests** use `qs/fake.py`, a local endpoint that never forwards anywhere.

## The other repositories

- **[ParcelRound](https://github.com/loganw234/ParcelRound)**: the method for
  splitting one body of work across several coding agents at once. Its
  METHOD.md, case studies and ledgers are the rules a harness has to hold.
- **[HonestFramework](https://github.com/loganw234/HonestFramework)**: a
  framework for AI-written projects whose claims do not depend on the AI.
- **[cft-fp256](https://github.com/loganw234/cft-fp256)**: the project whose
  rounds the requirements are derived from. Its public record is
  `docs/VALIDATION.md`.

## Licence

MIT. See [LICENSE](LICENSE).
