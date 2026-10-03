# HonestHarness

A harness for running [ParcelRound](https://github.com/loganw234/ParcelRound)
and [HonestFramework](https://github.com/loganw234/HonestFramework) on
open-weight models. Its core is a non-LLM orchestrator that turns the rules
agents now have to remember into mechanisms they cannot route around.

**Status: research.** There is no code yet. This repository holds the
requirements, the research behind them, and the record of rounds run by hand
that test them.

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
- [Rounds/ParcelRound-R6/](Rounds/ParcelRound-R6/): ParcelRound's round 6,
  run by hand by a Claude session as lead. It holds:
  - the round's plan of record;
  - the practice survey the plan rested on;
  - the harness notes, which list every rule the lead applied by hand, with
    the requirement that would make it a mechanism.

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
