# HonestHarness round 1: Phase 0's first slice, QS1 and a QS6 slice on the local pilots (plan of record, draft 3)

Drafted 2026-10-03 by the lead (one Claude session, Opus 5.5), after ParcelRound's
round 6 closed. **Approved by Logan on 2026-10-03, with every default** (the
last section). Draft 1 and draft 2 each went past a verifier (Opus 5.5).
- **Draft 1.** Five wrong claims, six claims wider than their sources, and
  eighteen gaps. The suites it named were not REQ's QS3 and QS4, and it
  measured the pilots, beyond QS1, only as verifiers, a role PN §2.3 does
  not name for them ("Not lead; not verifier on code").
- **Draft 2.** It re-scoped and answered most of those findings. It also had
  two wrong claims and fifteen gaps of its own, chiefly a QS6 slice that was
  not yet defined and two checks that could not fail.

This draft answers both reports, and the verifier's third report on it (its
QS6 points Q1 to Q5, and small restates), in one edit pass. The verifier's
scoped check of that pass found five lines still to fix, and said the plan
is ready for Logan once they are; they are fixed here, with the smaller
items it named. Where an answer is partial or deferred, it says so.
Every default names its derivation.

**Sources:**
- `REQ`: Research/open-weight-harness-requirements.md;
- `TC`: Research/open-weight-harness-research.md;
- `PN`: Research/open-weight-pilot-notes.md;
- `CS6`: ParcelRound's CASE-STUDY-6.md at `f42242e`;
- `[prior]`: the lead's or the verifier's prior knowledge of a tool, not read
  this round. Each one is for P2 to confirm.

## The question

REQ §12.1 asks for Phase 0 before any orchestrator is built: measure which
models can hold which roles, "days, not weeks". Its output is "a first
role-placement table with numbers, recorded with date, model, provider and
prompt version (H15.2)".

PN, written for the three local pilots, narrows where to start.
- **§2.3:** they "are not candidates for the roles REQ §8.3 cares most
  about". Their first roles to try are "triage, a schema-bound re-check, a
  gatherer on short records, and the long-context ledger reader. Not lead;
  not verifier on code."
- **§6 item 6** proposes Phase 0's order: "QS1 on §2's three models locally
  first, the cheapest data point, then QS6 and QS9 slices on
  contamination-free replays". It is a proposal still Logan's to accept.

This round takes PN's first two steps by default:
- **QS1, tool-call conformance**, per (model, provider, version), the unit TC
  §4.6 says to test;
- **a QS6 slice.**

It defers the third step. QS9 scores "the first rung at which the model
passes by weakening a gate, narrowing the work, relabelling a defect as a
limit, or overclaiming" (REQ §8.2). In the lead's judgement that needs a
model acting on the work it is graded on, in the isolated loop round 2
designs. REQ's ladder also has rungs that are not code ("a bound past what
can be proven"), which a later round may slice without the loop.

**The QS6 slice is narrower than REQ's QS6.**
- REQ's has a candidate draft a whole record entry from "the ledger, reports
  and run records", diffed against the committed entry and the runs.
- This slice asks named questions of the ledger alone, at several lengths.
- It bears most on PN's long-context ledger reader, which is not yet a row of
  REQ §8.3. Of the gatherer, REQ's QS6 role (REQ §8.3), it measures only
  reading.

**What the table can place.**
- QS1 is the prerequisite for every role (REQ H2.1).
- Placement needs the owner's thresholds (REQ:1260), which decision 7 puts
  to Logan. Without them the table reports numbers and places nothing.
- PN's other two first roles stay unplaceable this round whatever the
  thresholds: re-check needs QS9 (REQ:1208), and triage needs QS7
  (REQ:1209).

## What this round produces

- **`qs/`**, a Python package: a suite interface and a runner, against an
  OpenAI-compatible endpoint and Ollama's native API, writing one record per
  item run.
- **QS1**, with TC §7.8's cases, assertions and both of its metrics.
- **The QS6 slice** on round 6's ledger.
- **The deployment kit's local part**: K1, K2 and K8 of PN §5.2. PN offers
  K1 to K8 as candidate requirements for the kit, which sits outside the
  harness (PN §5.1). PN §6 proposes folding K1, K2, K3, K4 and K7 into
  REQ, which is Logan's to accept.
- **The table**, computed by script from the run records, and this round's
  case study.

## What it does not do, and why

- **No QS3, QS4 or QS9.** QS3 and QS4 need an agent loop with an isolated
  workspace, and in the lead's judgement QS9 does too (above).
  - A replay of round 6's verifiers needs four repositories at pinned
    commits and a writable scratch.
  - No sandbox image for this exists yet. The images here (cft-sim,
    emsdk, cft-vitis2022) belong to other projects.
  - Fresh plants also need storage that is never published.
  - These are round 2's design.
- **QS9's local seeds need Logan's word.** QS9's seeds are partly public:
  the hard-workload pack is in cft-fp256's `programs/workloads/`, and some
  seed lines are in VALIDATION.md and ROADMAP.md (REQ:183, 1198). The
  challenge suite itself, and each hard program's reason, are local to
  cft-fp256's `Data/runs/` (REQ:179, 1198). What may leave that directory is
  Logan's to say when QS9 is planned.
- **No QS2, and no QS3 on recorded send-backs.** They replay cft-fp256's
  round 2, which needs Verilator, MinGW and the cft-sim image (REQ §8.2);
  the image is present here. They also replay round 4, run in Quantum-Film, which
  needs Python and a libcft build.
- **No rented GPUs, and no cloud models.** No spending ceiling is set (PN
  §7), and no content leaves the desktop (K6).
- **No worker-loop base is chosen** (REQ §12.6). QS1's runner supplies tool
  results itself, and the QS6 slice is a single long prompt.

## What the round rests on (read 2026-10-03, read-only, unless marked)

- **Hardware:**
  - an RTX 4070 (12,282 MiB) and an RTX 5060 Ti (16,311 MiB), driver 591.86;
  - Python 3.12.9;
  - the C: drive has 67 GB free, and Ollama's model store is there.
- **What fits.** PN §2.2 estimates, as inference and as "upper bounds to
  measure", that each pilot's 4-bit weights fit one card. It puts
  InternLM2.5's context at about 65K tokens on the 16 GB card with a bf16
  KV cache, and about half that on the 12 GB card. The 1M contexts do not
  fit.
- **Serving.**
  - Ollama 0.32.0 is installed. Its local models include `glm4:9b`: chatglm,
    9.4B parameters, a 131,072-token context, Q4_0, tool-capable (`ollama
    show`). That is not the 1M variant.
  - LM Studio is installed. Its CLI woke a local server when the lead ran it
    once, and the lead stopped that server. Its having no native model
    digest is [prior].
  - Docker Desktop is installed. vLLM and LMDeploy are not, in the Windows
    Python.
- **The user environment** sets `OLLAMA_CONTEXT_LENGTH=32768` and
  `OLLAMA_KEEP_ALIVE=60m`. If Ollama's server inherits them, it truncates
  past 32K tokens and keeps a model in VRAM for an hour after use.
- **Ollama's API** [prior]:
  - responses echo the requested model's name, so a name proves nothing;
  - its native API takes a per-request `num_ctx` option, and a model's
    digest and template can be read from the server;
  - its OpenAI-compatible endpoint may not honour `keep_alive`.
- **The pilots** (PN §2.1), InternLM2.5-7B-Chat-1M, InternLM3-8B-instruct
  and GLM-4-9B-Chat-1M, are not pulled. They were released between 2024-06
  and 2025-01, before any of the experiment's repositories began (PN §2.3),
  so no replay here can be in their training data. Their tool formats
  differ:
  - vLLM's docs give an `internlm` parser for InternLM2.5, and PN marks the
    1M variant's format as assumed;
  - InternLM3's card documents no tool format, and lists Ollama among its
    stacks;
  - GLM-4-9B-Chat-1M's card documents its own function-call format, and PN
    found no vLLM parser for it.
- **QS6's seed: round 6's archived ledger.** It is 27 files, about 555 KB,
  or roughly 139K tokens at 4 bytes per token. PN puts InternLM3 at about
  170K tokens on the 16 GB card, beyond the 128K its card reports; whether
  any candidate holds the whole ledger is P2's to measure.
  - Round 6 was published on 2026-10-03, together with round 5's record,
    which had been on an unpushed branch.
  - The archive holds no personal path or address; ParcelRound's gate holds
    it to that.
  - Round 4's and round 5's archives do hold personal paths, which
    ParcelRound's gate excuses by name. No text of theirs goes into a
    published file here.

## Decisions for Logan, each with its options and the lead's default

1. **The first slice.**
   - (a) PN §6's first two steps, QS1 then a QS6 slice, on the pilots.
     *Default*: the cheapest data point, local, inside PN §2.3's roles. QS9,
     PN's third step, waits for round 2's loop, in the lead's judgement.
   - (b) REQ §12.1 as written: QS1, QS3, QS4 and QS9 seeds. Bigger, and it
     needs the isolation and storage design first.
   - (c) QS1 only, then decide.
2. **Candidates.**
   - (a) The three pilots, pulled and pinned, plus `glm4:9b` as a local 128K
     reference. *Default*: PN §2.1, and what is here.
   - (b) The pilots only.
   - (c) Also a larger local model. `qwen3.6:27b`, which REQ §8.4 names, is
     listed at 17 GB and fits neither card alone, so it would mean
     splitting a model across both cards or offloading it.
3. **Providers.**
   - (a) Ollama only, each model pinned by digest. *Default*: one provider
     avoids confounding models with stacks. It cannot separate a model's
     failure from Ollama's, and the table says so.
   - (b) Ollama and LM Studio, loading the same GGUF file, checked by hash.
   - (c) Also vLLM in Docker. It needs an image download, and quantised
     weights. The pilots' bf16 weights, 15.5 to 19.0 GB (PN §2.2), exceed the
     12 GB card. On the 16 GB card the smallest just fits and leaves too
     little room for context. Its documented parser covers InternLM2.5
     only.
4. **Load on your desktop.** "The desktop is Logan's to use: one run at a
   time, niced, and `docker ps` first", and no agent loads it on purpose
   (REQ:270, 275).
   - (a) Runs only when you say the desktop is free. One model at a time,
     loaded once per batch and unloaded after it. *Default*: the standing
     rule. At idle the RTX 4070 holds about 2 GB for Windows' shell and
     desktop processes, which leaves about 10 GB for a model. "Niced"
     reaches only the harness's own process: the GPU work runs in Ollama's
     server.
   - (b) Unattended runs inside a window you set.
5. **Downloads and licences.** Pulling the pilots is about 15 to 20 GB of
   weights from Hugging Face or Ollama's library. Each pull's source and
   size are listed by P2, and put to you before it runs. PN §7 flags GLM-4's
   registration requirement and InternLM2.5's conflicting licence
   statements.
   - (a) Publish the recipes, each with its licence linked and an
     evaluation-only note. *Default*: PN §7 says these "matter only if
     HonestHarness publishes recipes that use those weights commercially",
     and this use is evaluation.
   - (b) Keep the recipes unpublished.
6. **The round's own agents.**
   - **The record so far.**
     - Round 6 put parcels on Sonnet on the strength of round 5 and of
       SPEC decision 24.
     - Round 5's Sonnet parcels did prose-heavy work, and also wrote the
       site's page modules in Python. REQ §8.3 reads that as saying
       "little yet about work that is mostly code".
     - This round's parcels write code.
   - **The options:**
     - (a) Sonnet parcels with Opus verifiers and planted faults on every
       verifier. Cheaper: Sonnet parcels produced about 43% of round 6's
       output tokens (CS6).
     - (b) Opus parcels. *Default*: the evidence for Sonnet on code is
       thin.

   Each agent's model is read from its transcript, and its effort too where
   the transcript records it. Round 6 read only the model.
7. **Placement thresholds** (REQ:1260; H17.5's QS9 threshold).
   - (a) Numbers only this round; you set thresholds after seeing them.
     *Default*: they are yours, and there is no measurement yet to set them
     against.
   - (b) Set them now.

## The seam (P0) and the parcels

**P0, the lead's, before any parcel.** It lands on the round branch, and its
verifier reads it before dispatch (METHOD §2, §7).
- **The suite interface and runner** that every suite implements.
- **Per-parcel file lists**, so no two parcels touch a file (METHOD §2).
- **The run record, one JSON line per item run.**
  - Its date and time, and its suite, item and repeat ids.
  - The stack fingerprint (PN §5.2 K1, H15.1):
    - the model's digest and template hash, read from the server on each
      run;
    - the Hugging Face revision where there is one;
    - the provider, and its engine version;
    - the serving flags, quantisation, KV dtype and context length;
    - the sampling settings and reasoning setting;
    - the GPU, as read during the run. How a run is placed on a card is
      [prior]: Ollama's server picks it. P2 confirms how to place a run
      on a card, and how to read which card served it.
    - the harness version and prompt version.
  - The prompt's token count, by the model's own tokenizer client-side, at a
    pinned revision, against the context. Also the server's own count of
    the prompt, where it reports one ([prior] for Ollama, for P2 to
    confirm). The two counts can differ slightly with no truncation, so a
    tolerance is set from P2's measurements. A mismatch beyond it marks
    the run as a server that applied a different context, and a control
    exercises the mark. Then whether it was truncated, the outcome, and
    the transcript's hash.
- **The identity check.** The digest and template hash read from the server
  must equal the registry's pin, or the run fails before it starts (H15.1).
  The name a response reports proves nothing on Ollama. A control points the
  registry at another model's digest and shows the check fail.
- **The endpoint registry**, one entry per (model, provider, version).
- **The gate, `tools/check.py`, with its threat model stated before its
  first verifier pass** (CS6#1, practised here). It runs:
  - the unit tests;
  - the records against their schema;
  - a privacy scan with HonestHarness's own rules, carrying none of
    ParcelRound's exceptions;
  - a control for each check, the truncation flag's included: a prompt
    built past the context must be marked.

**Wave 1, after P0. No parcel loads a model while another does.**
- **P1, QS1 (TC §7.8).**
  - **The cases:**
    - single and parallel calls;
    - multi-turn calls;
    - a code-heavy multi-line argument with quotes and backslashes;
    - Unicode, empty arguments, nested objects and enums;
    - no call at all;
    - each `tool_choice` mode;
    - streaming and not;
    - thinking on and off.
  - **The assertions:** name and arguments; no special tokens in content;
    reasoning separated; IDs round-trip; `finish_reason`.
  - **The metrics:** schema accuracy, and trigger similarity against the
    goldens: whether the model calls a tool where the golden does, and the
    same one.
  - **The goldens** are written by hand from each family's documented
    format. They are never recorded from a model under test, since a check
    recorded from its subject passes against itself (METHOD §5).
  - The fallback for a model with no documented format follows TC §7.2.
  - **P1 builds and tests against a scripted fake endpoint, and loads no
    model.** Its controls are a fake that breaks each assertion, which the
    suite must fail, and a conformant fake, which it must pass. Live runs
    are the lead's, after the merge.
  - The suite re-runs on any change to the template, engine or provider (TC
    §7.8).
- **P2, the deployment kit, local** (K1, K2, K8). The only parcel that loads
  models. For each candidate:
  - the pull command, source, size and licence, put to Logan before any
    pull;
  - the pinned digest or revision, and the tokenizer files for client-side
    counting;
  - the identity check above, confirmed live;
  - the context each candidate holds on each card, measured with a
    per-request context option, never by changing the server's settings.
    If placing a run on a chosen card needs a server setting, P2 reports
    it and the lead asks Logan;
  - load once per batch, and unload after it;
  - a health check, and the registry entry.

  It records what does not fit, rather than forcing it, and confirms or
  corrects each [prior] above.

**Wave 2, after P0 and P2: P3, the QS6 slice.**
- **Cuts.** The ledger as of a cut time T is every entry stamped at or
  before T, across all files, in stamp order: a read moment's view.
  - An unstamped file, the README or a brief, enters a cut only if its
    kept modification time in the archive is at or before the cut's time.
    Two briefs were written after every cut, and hold answers: P5's at
    22:57:04 and the integration verifier's at 23:16:42. A brief's final
    text is all the archive keeps.
  - `keys/` is never included: it holds the plants' answers.
  - Cuts come to about 16K, 32K and 64K tokens by each model's tokenizer,
    and the whole ledger, where P2 measured them to fit. P3 measures each
    cut's time and size. There is no 8K cut: the README and briefs alone
    come to about 12K tokens.
  - The cuts are nested, so a bigger cut also holds more answers. By the
    verifier's estimate, even a 64K cut ends before the round's first
    planted-fault grading, at 22:53:58.
- **Items.** About twenty named questions whose answers the ledger itself
  holds, each with its ledger file and line. Some are counts across files,
  not only single facts, since PN asks for reasoning across the ledger.
  - **The length set.** Most items are answerable inside the smallest cut,
    and asked at every cut. The same questions with more around them
    measure the effect of length, which a growing set of answers would
    not.
  - **The reach set.** The rest are answerable only at larger cuts.
  - An item whose evidence lies after a cut has the key "not in the
    input" at that cut.
  - A count whose evidence straddles a cut has, as its key, the count of
    what the cut holds, stated per cut.
- **The key.** It is built by the lead from the ledger alone, not from
  CS6's transcript-derived figures or commit times. A verifier checks it
  before any run, and its hash is committed before the first run (the
  three-commit protocol).
- **The score**, per item and cut, by script. A model asked for an answer
  field gives one, and normalising parses numbers, keeps their units,
  writes times as HH:MM:SS and folds names' case. The classes:
  - **exact**: the normalised answer matches;
  - **wrong**;
  - **overclaim**: an answer where the key is "not in the input";
  - **dropped unit**: a figure without the unit or qualifier the key has;
  - **no answer**: no parseable answer field.

  A claim beyond the item, in free text around the answer field, is not
  scored: no script can, and this is a stated limit of the slice.
  Accuracy on the length set is plotted against cut size (PN §2.3), and
  each set's accuracy is reported over the items answerable at each cut.
- **The controls:** the key itself scores 100%; a planted wrong answer, a
  planted overclaim and a dropped unit each score as such.

**Then the lead:**
- runs each suite on each pinned (model, provider, version), one batch at a
  time, under decision 4;
- has the table computed by script from the records;
- writes the case study.

The lead's own code commits (the runner, the table code) go past a verifier
like a parcel's (METHOD §7).

## How it is held

- **Logan's rules, carried:**
  - the send-back rule (B3);
  - long runs handed to the lead (B4);
  - a resume note at a pause (CS4#11);
  - decisions recorded verbatim, a cft-fp256 practice (B8);
  - the desktop rule of decision 4 (B16, REQ:270, 275).
- **The repository is public.**
  - No absolute path, address or token goes in any file, commit or ledger
    entry. Places are named by roots each dispatch defines (CS6#7,
    practised).
  - Run records are published. Transcripts stay local, gitignored, with
    their hashes in the records.
  - The privacy scan runs before every push.
- **Every value in an entry is read from the command that produced it**
  (CS6#8, practised), and every time a record cites is checked against its
  source by script.
- **Planted faults on every parcel's verifier, under the three-commit
  protocol.**
  - Each key's hash goes in the ledger before dispatch (HF §9; CS6's
    setting).
  - Keys, and any description of their plants, stay out of the ledger until
    the round's last planted-copy verifier reports (CS6#3).
  - Each verifier forms its view before it reads the parcel's file (CS6#4).
- **The integration verifier** remakes every merge and reads the lead's own
  work. In round 6 that work needed the most restating (CS6 obs 12).
- **Dry-run notes.** The lead logs every rule it applies by hand in this
  round's harness notes, as round 6 did.

## The ledger and workspaces

- **The ledger:** `<repos>/honestharness-r1-ledger/`, outside every worktree.
  - One file per author, append only.
  - Escalation by the runtime's messages, entry first, with a test
    escalation at dispatch.
  - It is archived beside the case study at the end, after its privacy
    check.
- **The worktrees:** `<repos>/honestharness-worktrees/{P0,P1,P2,P3}`, cut
  from a round branch.
- `<repos>` and `<scratch>` are defined in each dispatch message.

## Run budget (inference, to be measured)

- **QS1:** about 35 cases, times four candidates, times three repeats at
  fixed sampling: about 420 short calls. Four loads in all, one per
  candidate's batch.
- **QS6:** up to four cuts, times about twenty items, times four candidates,
  times three repeats: at most about 960 prompts, fewer where a cut does not
  fit. The longest take a few minutes each.
- **Together:** an hour or two of GPU time for QS1, and up to a day for QS6,
  run in batches when the desktop is free. That is "days, not weeks".

## Risks

- **A pilot that cannot call tools at all** scores zero on QS1. The table
  records why: the format, the template, or the truncation.
- **Silent truncation.** If the server inherits the user environment, its
  context is 32K. Counting is client-side, and a truncated run is marked,
  not scored.
- **Few items** give wide uncertainty. Every rate is stated with its count.
- **GPU contention** with other sessions on this desktop is held by decision
  4.
- **Stacks the pilots document go unmeasured** under 3(a). QS1's numbers
  belong to Ollama's stack, and the table says so.

## Not decided here

- QS3, QS4 and QS9: round 2, with the isolated loop, plant storage, and
  Logan's word on `Data/runs/`.
- The worker-loop base (REQ §12.6). Its choice becomes part of the measured
  tooling: a judge's rate belongs to "model, prompt and tooling together"
  (REQ:1131).
- PN §6's proposals for REQ, and PN §7's adversarial-lead trial.

## Approved (2026-10-03, between 02:29:26 and 04:06:22 -0700, two clock readings bracketing the answer)

The lower reading is the plan's last edit before it went to Logan, and the
upper is the lead's clock on receiving his answers. Logan, verbatim, through
the question tool:
- on the first slice, "QS1 + QS6 slice (Recommended)";
- on the round's agents, "Opus parcels (Recommended)";
- on the plan, "Approve with defaults (Recommended)". That covers decisions
  2 to 5 and 7: the three pilots plus `glm4:9b`; Ollama only; runs only when
  he says the desktop is free; each pull put to him first; recipes published
  with licence links and an evaluation-only note; numbers only, with
  thresholds his to set after.

Every answer again took the lead's default, which is recorded as data for
H16. The next step is P0. Nothing is pulled or loaded until Logan says so.
