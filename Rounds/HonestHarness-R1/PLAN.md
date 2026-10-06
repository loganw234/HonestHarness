# HonestHarness round 1: the first step down the ladder, DeepSeek over its API (plan of record, draft 5)

Drafted 2026-10-06 by the lead (one Claude session, Opus 5.5).
**Approved by Logan on 2026-10-06, with every default**, in the last
section. The round has not begun: it begins when he says go. Every default
names its derivation.

## History

- **Drafts 1 to 3** planned Phase 0 on three local 7-9 B pilot models
  through Ollama. Each draft went past a verifier (Opus 5.5), and Logan
  approved draft 3 on 2026-10-03 with every default (git: `52b1bd9`, this
  file's last section).
- **On 2026-10-03** Logan also said "Dont begin the round yet, still
  considering things and the directions to take it", and set the harness's
  purpose: "More curiosity gets to survive long enough to meet reality"
  (Research/curiosity-explorer-direction.md).
- **On 2026-10-06** he moved the first tests up the ladder (§1), and decided
  the data, provider and spending questions verbatim (§3). This draft
  replaces draft 3's candidates, providers and data rule. What draft 3 got
  right is kept here: QS1's full TC §7.8 cases, the QS6 slice's design, the
  run record, the controls, and how the round is held.
- **Draft 4** went past the verifier. It found the provider facts almost all
  accurate, the arithmetic right, and seven things to fix.
  - Its identity check could not tell DeepSeek's two models apart.
  - Its replay's inputs held the plants' answers.
  - The replay's cost had no bound.
  - It wrote the lead's reading of the ceiling's reach as Logan's
    decision.
  - It missed a DeepSeek limit on multi-turn tool calls, and got one fact
    wrong.
  - The sandbox image needs git.

  This draft answers each.

**Sources:**
- `REQ`: Research/open-weight-harness-requirements.md;
- `TC`: Research/open-weight-harness-research.md;
- `PN`: Research/open-weight-pilot-notes.md;
- `CX`: Research/curiosity-explorer-direction.md;
- `CS6`: ParcelRound's CASE-STUDY-6.md at `f42242e`;
- `D1` to `D20`: DeepSeek's API docs, and `Q1` to `Q27`: Alibaba Cloud Model
  Studio's, as listed under Sources at the end. All were read 2026-10-06 by
  a fact-gathering agent of this session, read-only.
- `[prior]`: prior knowledge, not read this round, for P0 or P2 to confirm.

## §1 The question

REQ §12.1 asks for Phase 0 before any orchestrator is built: measure which
models can hold which roles, "days, not weeks". Its output is "a first
role-placement table with numbers, recorded with date, model, provider and
prompt version (H15.2)".

Logan's direction of 2026-10-06 sets where to start:

> I think the outset testing may need more 'potential' with the first model tests, possibly a cheap frontier API model, like Deepseek or Qwen? Operating as a 'step down' from the Claude models utilized to discover the methods and approaches. I feel the step down more gradually will uncover things at a better pacing than trying to jump straight to the bottom of the ladder.

**The ladder** (the lead's statement of it, accepted in conversation):

| rung | models | what it is for |
|---|---|---|
| 0 | Claude Opus 5.5 and Sonnet 5.5 | the reference. ParcelRound's round 6 is its record: ten of ten planted faults caught by Opus verifiers (CS6 obs 5). |
| 1 | DeepSeek's API first, then Qwen's | **this round** |
| 2 | mid-size open weights, around 30 B, local or rented | a later round |
| 3 | the 7-9 B local pilots (PN §2) | the floor: honesty at the edge (CX §5), and specialist roles (CX §6) |

**Why step down gradually** (the lead's reasons, given in that conversation):
- **One variable at a time.** Going from Claude to a 7-9 B local model
  changes capability, vendor, tool format, serving stack, quantisation and
  context at once, so a failure cannot be traced to any one of them. Rung 1
  keeps capability roughly in range and changes the vendor and family.
- **The first question is whether the method is Claude-shaped.**
  Everything so far was discovered on Claude: following long briefs closely,
  writing ledger entries in a set shape, accepting "found nothing", stopping
  when told. Rung 1 shows which rules are mechanisms and which rest on one
  model's disposition. That is what HonestHarness exists to find.
- **The instrument is tested before it judges.** Round 6's gate went past a
  verifier six times before it held: four passes, and two scoped
  re-checks (CS6 obs 1, 2 and 8). A new harness will have bugs too.
  Against a strong model a failure is more likely the harness's, which is
  the order to find them in.

## §2 What this round produces

- **`qs/`, a Python package.** A suite interface and a runner that reach any
  OpenAI-compatible endpoint, writing one record per item run. DeepSeek is
  the first provider in its registry, and Qwen the second.
- **The spending guard.** Every call is metered from the API's own usage
  fields, priced from a pinned price table, and reconciled against the
  provider's reported balance. A run whose projected cost would cross what
  is left of the ceiling is refused before it starts (§3; REQ H8.6, H13.1).
- **QS1** on DeepSeek, with TC §7.8's cases, assertions and both metrics.
- **The QS6 slice** on round 6's ledger, at lengths up to the whole ledger,
  which DeepSeek's 1M context holds (§4).
- **If decision 1 is (b): the agent loop, with its sandbox, and a QS4
  slice.** The slice replays round 6's five planted copies, plus their five
  unplanted commits, with a DeepSeek verifier, and compares it with the Opus
  verifiers' record (§6, wave 2).
- **Then Qwen**, at a hold point: the same suites against Model Studio,
  once DeepSeek's results are in and Logan says go (§7).
- **The table**, computed by script from the run records, and this round's
  case study.

**Not this round:**
- rungs 2 and 3: the local pilots wait their turn;
- QS2, QS3 and QS9, which need build environments, recorded send-backs, or
  Logan's word on cft-fp256's `Data/runs/` (REQ §8.2);
- REQ §12.6's worker-loop base. This round's loop is the minimum the QS4
  slice needs, and its choice is part of the measured tooling: a judge's
  rate belongs to "model, prompt and tooling together" (REQ:1131).

## §3 Logan's decisions of 2026-10-06, verbatim

> All data is freely open to providers used, at this stage data privacy isn’t a major concern, individuals in the future will make that decision on their end with the model choice they make. We can utilize Deepseek as the pilot test and Qwen once deepseek is working, especially for their low cache costs. Spending ceiling for now being $250, amount can change based on results, will not go down from there for the pilot testing

What they settle:
- **K6** (PN §5.2): every repository's content may go to the providers used.
- **The order:** DeepSeek is the pilot, and Qwen follows once DeepSeek works.
- **The ceiling: $250 for the pilot testing.** It may rise with results, and
  will not go down. Two questions about its reach are Logan's, and are
  decision 7:
  - whether it covers only the measured models' API bills. That is the
    lead's reading, which would put the Claude sessions building the
    harness outside it;
  - whether Qwen falls inside it.

What they leave to Logan's own hands, and never the lead's:
- creating the provider accounts, accepting their terms, and topping up;
- creating each API key, and setting it as an environment variable the
  harness reads (`DEEPSEEK_API_KEY`; Qwen's at its hold point).

No key ever enters a file, commit, log, ledger entry or message. The gate's
privacy scan includes the key shapes, with a control for each.

## §4 What the round rests on (read 2026-10-06)

**DeepSeek's API** [D1-D20]:
- **Models.**
  - Two model names, `deepseek-flash` and `deepseek-v4-pro`, map to
    DeepSeek-V4.1-Flash and DeepSeek-V4-Pro-0813 [D2, D10]. Both have open
    weights under MIT [D20].
  - **The docs disagree** about `deepseek-v4-pro`. The 2026-09-10 news post
    says its requests route to V4.1-Flash from 2026-09-14 [D5]. The change
    log says V4 Pro continues at its own prices [D4], and the pricing page
    still lists it [D2]. The live API is the judge (§6, P0).
  - **By DeepSeek's own account, V4.1-Flash is the stronger model.** Its
    change log gives Terminal-Bench 2.1 scores of 90.6 against 87.9 [D4],
    and its news post says "Tests by multiple parties put V4.1-Flash ahead
    of V4-Pro" [D5]. These are the maker's claims. On them, pro is the
    older and weaker model, at three to seven times flash's price.
- **Context and output.** 1M tokens of context, and up to 384K of output
  [D2, D17].
- **Tool calling.**
  - Both models call tools, in thinking mode too [D9].
  - `tool_choice` takes none, auto, required or a named function. Required
    and named return a 400 error in thinking mode [D10].
  - There is no `parallel_tool_calls` parameter in Chat Completions; auto
    may call several tools [D10].
  - Strict schemas are a beta, on `/beta` only [D9].
  - `response_format` is `text` or `json_object`, with no JSON schema
    [D10, D16].
- **Thinking.**
  - On by default, at effort high. It is set with `thinking` in the request
    body, and `reasoning_effort` takes low, high or max [D8, D10].
  - **With tools, `reasoning_content` must be passed back on every later
    turn, or the API returns 400** [D8].
  - **Sampling.** In thinking mode, temperature has no effect, and `top_p`
    below 0.95 is treated as 0.95. In non-thinking mode, temperature
    applies, from 0 to 2, and `top_p` is fixed at 1.0 [D8, D10].
  - **Tool calls cannot be inserted mid-conversation** in Chat Completions
    [D9]. In thinking mode with tools, an earlier assistant turn without
    its `reasoning_content` returns 400 [D8].
- **Caching** is automatic and best-effort [D11]. Each response reports
  `prompt_cache_hit_tokens` and `prompt_cache_miss_tokens` [D10, D11].
- **Prices**, in USD per 1M tokens, off-peak / peak [D2]:

  | model | cache hit | cache miss | output |
  |---|---|---|---|
  | deepseek-flash | 0.003 / 0.006 | 0.15 / 0.30 | 0.60 / 1.20 |
  | deepseek-v4-pro | 0.022 / 0.044 | 0.66 / 1.32 | 1.98 / 3.96 |

  Peak hours are 01:00-04:00 and 06:00-10:00 UTC, Monday to Friday,
  excluding Chinese public holidays. Off-peak rates are half the peak rates
  [D2]. In Pacific daylight time that is 18:00-21:00 and 23:00-03:00, from
  Sunday evening to Friday morning, until daylight time ends on
  2026-11-01. The conversion is the lead's, and the runner works in UTC.
- **Versions.** No dated snapshots exist, and names are upgraded in place
  [D2, D4, D17]. Each response reports `model` and `system_fingerprint`
  [D10], but neither identifies the model:
  - D10's example responses report `"model": "deepseek-flash"`, the
    alias, so `model` likely names the alias sent;
  - the fingerprint is "the backend configuration", and D10's two examples
    show two different fingerprints for the same alias.

  The model list gives each id a display name [D17].
- **Billing** is prepaid. An empty balance returns 402, and `GET
  /user/balance` reports what is left [D2, D13, D18]. Top-ups do not expire
  and can be refunded [D19]. Concurrency is 2,500 per account on flash and
  500 on pro [D12].
- **Training cutoff.** DeepSeek states none. V4-Pro-0813 was released on
  2026-08-13 and V4.1-Flash on 2026-09-10 [D4, D6]. ParcelRound's first
  commit is 2026-09-11 (PN §2.3), so by date neither model can have seen its
  record. An in-place upgrade could change that. Whether the fingerprint
  would show it is measured, not assumed (§6, P0).

**Qwen on Model Studio, for the hold point** [Q1-Q27]:
- **Models.** qwen3.8-max, qwen3.8-flash and qwen3.7-plus, each with a 1M
  context [Q2-Q5].
  - qwen3.8-max has a dated snapshot, `-0902` [Q3], and qwen3.7-plus equals
    its `2026-05-26` snapshot [Q5]. qwen3.8-flash has none [Q4].
  - A snapshot's rate limit can be far lower: 60 requests a minute for
    qwen3.7-plus's [Q16].
- **Billing.** Implicit cache hits cost 10.7-20% of input, against
  DeepSeek's 2-3.3% [Q9, the lead's arithmetic]. On the flash tiers that is
  $0.016 per 1M tokens against $0.003.
  - Logan chose Qwen "especially for their low cache costs". Qwen's cache is
    cheap against its own input, but DeepSeek's is cheaper still. Qwen's
    place on the ladder is a second model family.
  - Billing is post-paid, with a monthly budget stop that acts after a
    delay [Q19, Q20].
- **The endpoint.** Singapore, with a workspace ID in the URL; a key works
  only in its own region [Q10, Q11]. Thinking is on by default, and
  `preserve_thinking` asks for every turn's reasoning back [Q10, Q14].
- **Training cutoff.** None is stated [Q10].

**This desktop:**
- Python 3.12.9, and Docker Desktop.
- The local images belong to other projects. A sandbox for the agent loop
  needs an image with Python and git, which is a download (§5, decision 5).

## §5 Decisions for Logan, each with its options and the lead's default

1. **Scope.**
   - (a) QS1 and the QS6 slice on DeepSeek, then Qwen. Smaller, with no
     agent loop.
   - (b) Those, plus the agent loop and the QS4 replay of round 6's planted
     copies. *Default*: it asks rung 1's real question, whether the method
     works in a role on a non-Claude model, against Claude's 10 of 10.
     QS1 and QS6 alone mostly test plumbing.
2. **Models.**
   - (a) `deepseek-flash` only. *Default*: by DeepSeek's own account it is
     the newer and stronger model (§4). It is also the cheapest.
   - (b) Both, adding `deepseek-v4-pro` as an older-generation comparison.
     Pro costs three to seven times as much per token type (output 3.3x,
     cache miss 4.4x, cache hit 7.3x). Whether it is still served as its
     own model is settled live first (§6, P0).
3. **Thinking.**
   - (a) QS1 and QS6 in both thinking and non-thinking modes. The agent
     loop, which uses tools, in thinking mode, the API's default.
     *Default*: thinking changes what tool calls are allowed (§4), so QS1
     must see both.
   - (b) Thinking mode only, everywhere.
4. **Topping up.** Your action, in your account.
   - (a) Top up in steps: $25 first, then more as the measured spend
     warrants, up to the ceiling. *Default*: a prepaid balance is a hard cap
     at the provider's end, so a runaway loop cannot pass the step. The
     harness's guard is a second layer.
     - Off-peak (decision 6(a)), $25 covers the first measurements on flash
       at their worst. QS1 and QS6 together cost at most about $7.80, and
       one capped QS4 run at most $6.30, about $14 in all (§7). At peak the
       same worst case is about $28, over the step, and the prepaid balance
       would stop it.
   - (b) Top up the full $250 at once.
5. **The sandbox image** (if 1(b)): a container with no network and
   read-only mounts, from an image with Python and git, since round 6's
   gate drives git. It is either the full official Python image, which
   includes git [prior], or the slim one with git added at build time.
   Either is a download. P2 states which, with its size, before any pull,
   and the pull waits for your yes.
   - (a) Yes, when P2 asks. *Default*.
   - (b) No sandbox: the loop runs its shell tool unconfined. *Not
     recommended*: a verifier's tool calls would run with your account's
     access to the desktop.
6. **When runs happen.**
   - (a) Batches run in DeepSeek's off-peak hours, which cover most of
     your daytime and halve the price. *Default*: the same work for half
     the spend.
   - (b) Any time.

7. **The ceiling's reach** (§3).
   - Does the $250 cover only the measured models' API bills, with the
     Claude sessions building the harness outside it? *Lead's reading:*
     yes. Logan's words do not say.
   - Does Qwen fall inside the $250, or have its own? *Lead's reading:*
     inside, since "for the pilot testing" sits beside "Qwen once deepseek
     is working".

**Carried from draft 3's approval, unchanged:**
- the round's parcels on Opus (draft 3, decision 6);
- numbers only, with placement thresholds yours to set after (draft 3,
  decision 7).

Draft 3's decisions on the local pilots, on Ollama and on loading the
desktop's GPUs do not apply to this round. API runs load no local GPU.

## §6 The seam (P0) and the parcels

**P0, the lead's, before any parcel.** It lands on the round branch, and its
verifier reads it before dispatch (METHOD §2, §7).
- **The suite interface and runner** that every suite implements, and
  per-parcel file lists so no two parcels touch a file (METHOD §2).
- **The run record, one JSON line per item run:**
  - its date and time, and its suite, item and repeat ids;
  - the provider, base URL and model name sent;
  - the `model` and `system_fingerprint` each response reports [D10];
  - the thinking setting and effort;
  - the sampling settings sent, marked where the API ignores them [D8];
  - the harness and prompt versions;
  - usage: cache-hit, cache-miss and reasoning tokens, and output tokens
    [D10];
  - the price table applied (its source URL and date), the rate period
    (peak or off-peak), and the call's computed cost;
  - the outcome, and the transcript's hash.
- **The identity check.** At each batch's start, the runner reads the
  provider's model list and records each id's display name [D17]. Each
  response's `model` and `system_fingerprint` are recorded too.
  - **The fingerprint is not used as a tripwire yet.** Two fingerprints
    appear for one alias in DeepSeek's own examples [D10]. Its stability is
    measured over the first batches. Only if it holds steady does a change
    within a batch mark the later runs.
  - **The billing signature tells the models apart.** Requests routed to
    V4.1-Flash are billed at its rates [D5]. So the guard's reconciliation
    tests each batch's balance change against each model's price table.
    One that matches the other model's table is a routing finding, not a
    meter fault. Under 2(b), that settles whether `deepseek-v4-pro` is
    still its own model.
  - **A stated limit:** a hosted API cannot prove which weights it served,
    and DeepSeek offers no pinned versions [D4]. Model Studio sells a pinned
    `deepseek-v4-pro-0813` [Q8], a later comparison if drift becomes a
    question.
- **The spending guard:**
  - each call's cost is computed from its usage and the pinned price table;
  - the total is kept in a spend file;
  - the provider's balance is read before and after each batch, and the
    computed and billed amounts must agree within a tolerance. A
    disagreement stops the batch: the meter is itself checked against
    something that can say no. P0 confirms, with its first live calls:
    - the balance's currency, which the price table must match [D18];
    - its precision, two decimals in D18's example, against per-call
      costs of a fraction of a cent. The reconciliation is per batch,
      never per call;
    - how long the balance takes to update;
    - that no top-up lands mid-batch. A jump voids that batch's
      reconciliation rather than failing it;
  - a run is refused if its projected cost, estimated from the suite's
    token budget, would cross what is left of the ceiling;
  - a control shows each refusal fire.
- **The gate, `tools/check.py`, with its threat model stated before its
  first verifier pass** (CS6#1, practised). It runs:
  - the unit tests;
  - the records against their schema;
  - the guard's arithmetic, against recorded fixtures;
  - a privacy scan with HonestHarness's own rules, carrying none of
    ParcelRound's exceptions. It includes the providers' key shapes;
  - a control for each check.
- **The provider adapter.** It handles what the OpenAI format does not
  [D8-D11]:
  - DeepSeek's `thinking` parameter;
  - passing `reasoning_content` back with tools;
  - DeepSeek's extra finish reasons, and its keep-alive lines in a stream;
  - usage arriving on the last chunk.
- **Live calls only in live mode.** The client refuses any provider host
  unless the runner is started with `--live` and a spend reservation. It
  reads the key only then, and a control shows the refusal fire.
  - Parcels' tests run against local fake endpoints, so a parcel cannot call
    a paid API by accident. That is the threat the gate guards against.
  - A key in the user environment is visible to every session on the
    desktop, so deliberate misuse is outside the threat model, and stated
    as such.

  Qwen's differences are added at its hold point: the workspace URL,
  `enable_thinking` and `preserve_thinking`, and `cache_control` [Q9-Q14].

**Wave 1, after P0. Each parcel builds and tests against scripted fake
endpoints and calls no paid API. Live runs are the lead's, after the merge.**
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

    A `tool_choice` that DeepSeek documents as refused in thinking mode is
    expected to return 400. The suite records that as a documented
    behaviour, not a model failure.

    Multi-turn cases carry the model's own earlier turns, with their
    reasoning, not hand-written ones: DeepSeek accepts no tool calls
    inserted mid-conversation [D9], and in thinking mode a turn without
    its reasoning returns 400 [D8]. One hand-written history is kept as a
    case in each mode. Its result is recorded as it happens: thinking
    mode's 400 is documented [D8], and for non-thinking mode D9 says only
    "does not support".
  - **The assertions:** name and arguments; no special tokens in content;
    reasoning separated; IDs round-trip; `finish_reason`, DeepSeek's extra
    values included.
  - **The metrics:** schema accuracy, and trigger similarity against the
    goldens.
  - **The goldens** are written by hand from the provider's documented
    format, never recorded from a model under test (METHOD §5).
  - **The controls:** a fake endpoint that breaks each assertion, which the
    suite must fail, and a conformant one, which it must pass.
- **P2 (if 1(b)), the agent loop and its sandbox.**
  - The model is reached by the runner, on the host. Its tool calls run in a
    container with no network and read-only mounts of exactly what a
    verifier was given, plus a writable scratch.
  - The loop records every message.
  - It handles the thinking rules above.
  - It stops at a turn and token budget the runner sets.
  - Its controls:
    - a tool call that tries the network fails;
    - a write outside the scratch fails;
    - a call past the budget is refused;
    - git and Python run inside, and round 6's gate runs in a mounted
      copy.
  - A run its budget stops is recorded as stopped, never as "found
    nothing".

**Wave 2, after P0 and wave 1:**
- **P3, the QS6 slice.** Draft 3's design, unchanged except for its cuts.
  - **Cuts.** The ledger as of a cut time T is every entry stamped at or
    before T, in stamp order.
    - An unstamped file, the README or a brief, enters a cut only if its
      kept modification time in the archive is at or before T.
    - `keys/` is never included.
    - Cuts come to about 16K, 32K, 64K and 128K tokens, plus the whole
      ledger, about 139K tokens. All of them fit DeepSeek's 1M context.
      Sizes are counted by the API's reported prompt tokens.
  - **Items.** About twenty, each with its ledger file and line.
    - A length set, answerable in the smallest cut and asked at every cut.
    - A reach set, answerable only at larger cuts.
    - "Not in the input" keys where a cut lacks the evidence, and per-cut
      keys for straddling counts.
  - **The key** is built from the ledger alone and checked by a verifier
    before any run. Its hash is committed before the first run.
  - **The score** is by script on an answer field: exact, wrong,
    overclaim, dropped unit, or no answer. A claim beyond the item is not
    scored, which is a stated limit.
  - **The controls:** the key scores 100%, and a planted wrong answer, an
    overclaim and a dropped unit each score as such.
- **P4 (if 1(b)), the QS4 replay of round 6's planted copies.**
  - **Inputs, rebuilt from public sources.**
    - Each planted copy is rebuilt from ParcelRound's parcel commit and the
      key in `archive/round6-ledger.zip`. It must reproduce the key's
      recorded `copy_commit` SHA, or the replay stops. Draft 4's verifier
      rebuilt all five, and each reproduced its SHA.
    - The replay's repository holds only objects reachable from the copy
      commit. No later history goes in, so neither the archive with its
      keys nor CASE-STUDY-6 is there.
    - The ledger is cut at the verifier's dispatch time, without `keys/`,
      and without the parcel's own file. That file holds the parcel's
      design, a reference copy a candidate could diff against to find
      every plant (CS6 obs 5, CS6#4).
    - verifier-P5's cut, at 00:23, holds the lead's 22:53:58 and 23:06:11
      entries, which graded wave 1 and described its plants. Its original
      read them before forming a view, and said so (CS6 obs 6). The replay
      keeps them, for the same conditions, and reports P5's result
      separately.
    - The brief comes from the archive, adapted where the sandbox differs.
      Escalation becomes a report tool, and the verifier's own ledger file
      becomes a file in the writable scratch, since the ledger is a
      read-only mount. The adaptation is recorded as the prompt version.
    - The dispatch message is reconstructed, with roots in place of paths.
  - **The false-alarm set** is the five parcels' real tips. They hold the
    real findings round 6's verifiers recorded, so a finding there is
    judged against that list, not assumed false.
  - **The score:**
    - A plant is caught when a finding cites its location and states the
      fault: the source's value against the plant's, or the contradiction
      the plant creates. The location is matched by script. The fault
      statement is judged by the lead and checked by a verifier. In a
      control, a report that cites the line without naming the fault
      scores as a miss.
    - Other findings are matched against round 6's recorded findings by
      the lead, with a verifier checking each match. That adjudication is
      judgement, recorded as such, which is a stated limit.
  - **The comparison:** detection against the Opus verifiers' 10 of 10.
    Each Opus verifier had recorded both its plants in a view formed before
    it read the parcel's file (CS6 obs 5), so for the plants the replay's
    inputs are the same. That is not so for real findings. Some came from
    the parcel's file after the view, such as verifier-P5's on P5's
    coverage claim. The real-findings comparison counts only those
    recorded before the view, and marks the rest.
  - **Contamination:** both DeepSeek models predate ParcelRound by release
    date (§4), so they cannot have seen these plants unless upgraded in
    place since.

**Then the lead:**
- runs each suite on each (model, provider) pair in batches, one run at a
  time, under decisions 4 and 6;
- revises the cost estimate from each batch's measured spend before the
  next;
- reports DeepSeek's results to Logan: **the hold point for Qwen**;
- has the table computed by script from the records;
- writes the case study.

The lead's own code commits go past a verifier like a parcel's (METHOD §7).

## §7 Spend estimate (the lead's arithmetic, to be replaced by measurement)

Prices are §4's off-peak rates; peak doubles each figure. Assumptions are
stated, and the guard holds the ceiling whatever the estimate says.

- **QS1**, per thinking setting: 35 cases times 3 repeats, about 4K input
  and 2K output per call.
  - flash: about $0.19, so $0.38 for both modes;
  - pro, under 2(b): about $0.70 per mode.
- **The QS6 slice**, per setting: 60 prompts per cut (20 items times 3
  repeats), across cuts totalling about 379K tokens. That is about 22.7M
  prompt tokens, mostly cache hits on the shared ledger prefix, and about
  0.45M output.
  - flash: about $0.40, or $3.70 if no prompt hit the cache. Both modes come
    to about $0.80, and at most $7.40;
  - pro, under 2(b): about $1.60 per mode, or $16 with no hits.
- **The QS4 replay.** Round 6's Opus verifiers read 16.6M to 22.6M tokens
  and wrote 45K to 68K each (CS6's cost table).
  - **Every run is capped** at 40M tokens read and 0.5M output, which bounds
    its worst case. With no cache hits, a run costs at most $6.30 on flash
    off-peak, and $27.39 on pro.
  - **Caching is not a bound.** DeepSeek calls it best-effort [D11]. At 90%
    hits, a run is about $1.00 on flash and $4.40 on pro.
  - **One pass over the ten commits**, five planted and five not, on flash:
    about $10 expected, $63 at worst. On pro it is $274 at worst, more than
    the ceiling. So pro's replay, under 2(b), runs only once flash's
    measured hit rate and tokens show it fits.
  - **The first QS4 step is a single flash run.** Its measured tokens and hit
    rate replace these assumptions before the other nine run.
- **One full pass on flash, all suites:** about $11 expected, and about $71
  at worst, off-peak.

## §8 How it is held

- **Logan's rules, carried:**
  - the send-back rule (B3);
  - long runs handed to the lead (B4);
  - a resume note at a pause (CS4#11);
  - decisions recorded verbatim (B8);
  - on the desktop, one run at a time, and `docker ps` before any container
    (B16).
- **The repository is public.**
  - No absolute path, address or key goes in any file, commit or ledger
    entry. Places are named by roots each dispatch defines (CS6#7,
    practised).
  - Run records are published. Transcripts are kept local, gitignored, with
    their hashes in the records.
  - The privacy scan runs before every push.
- **Every value in an entry is read from the command that produced it**
  (CS6#8, practised).
- **Planted faults on every parcel's verifier, under the three-commit
  protocol.**
  - Each key's hash goes in the ledger before dispatch.
  - Keys, and any description of their plants, stay out of the ledger until
    the round's last planted-copy verifier reports (CS6#3).
  - Each verifier forms its view before it reads the parcel's file (CS6#4).
- **The integration verifier** remakes every merge and reads the lead's own
  work (CS6 obs 12).
- **Dry-run notes.** The lead logs every rule it applies by hand in this
  round's harness notes.
- **Recommendations carry their derivation** (H16.1). This plan's defaults
  name theirs, and every default Logan takes is recorded, as CX §4 proposes.

## §9 The ledger and workspaces

- **The ledger:** `<repos>/honestharness-r1-ledger/`, outside every worktree.
  - One file per author, append only.
  - Escalation by the runtime's messages, entry first, with a test
    escalation at dispatch.
  - It is archived beside the case study at the end, after its privacy
    check.
- **The worktrees:** `<repos>/honestharness-worktrees/{P0,P1,P2,P3,P4}`, cut
  from a round branch.
- `<repos>` and `<scratch>` are defined in each dispatch message.

## §10 Risks

- **The docs' contradiction about `deepseek-v4-pro`.** The live check
  settles it before any measurement counts.
- **In-place upgrades mid-round.** They may not show at all. The fingerprint
  serves as a tripwire only once its stability is measured. The model
  list's display names and the billing signature are the checks until
  then. A batch found to span an upgrade is split at it.
- **Thinking-mode rules.** A harness that forgets to pass reasoning back
  gets 400s, not wrong answers, so the failure is loud. QS1 confirms it.
- **The guard's own arithmetic.** Reconciling it against the balance checks
  it every batch.
- **A verifier loop that runs long.** The turn and token budgets stop it,
  and the guard refuses what the ceiling cannot cover. A capped run can
  stop short of a finding, so it is recorded as stopped, and the cap is
  raised only on measured need.
- **Few items** give wide uncertainty. Every rate is stated with its count.
- **Contamination by in-place upgrade.** At best a change is detected. What
  changed cannot be seen, and that is stated with every result.

## Sources

Read 2026-10-06, read-only, by this session's fact-gathering agent.

**DeepSeek:**
- D1 api-docs.deepseek.com/
- D2 api-docs.deepseek.com/quick_start/pricing
- D3 api-docs.deepseek.com/zh-cn/quick_start/pricing
- D4 api-docs.deepseek.com/updates
- D5 api-docs.deepseek.com/news/news260910
- D6 api-docs.deepseek.com/news/news260813
- D7 api-docs.deepseek.com/news/news260424
- D8 api-docs.deepseek.com/guides/thinking_mode
- D9 api-docs.deepseek.com/guides/tool_calls
- D10 api-docs.deepseek.com/api/create-chat-completion
- D11 api-docs.deepseek.com/guides/kv_cache
- D12 api-docs.deepseek.com/quick_start/rate_limit
- D13 api-docs.deepseek.com/quick_start/error_codes
- D14 api-docs.deepseek.com/guides/responses_api
- D15 api-docs.deepseek.com/guides/anthropic_api
- D16 api-docs.deepseek.com/guides/json_mode
- D17 api-docs.deepseek.com/api/list-models
- D18 api-docs.deepseek.com/api/get-user-balance
- D19 static.deepseek.com/faq/index.html?lang=en#/category/4
- D20 huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash and huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813 (model cards)

**Alibaba Cloud Model Studio** (Q1 to Q23 are under
alibabacloud.com/help/en/model-studio/):
- Q1 /models
- Q2 /text-generation-model
- Q3 /qwen3-8-max
- Q4 /qwen3-8-flash
- Q5 /qwen3-7-plus
- Q6 /qwen3-7-flash
- Q7 /qwen3-8-2-4t-a95b and /qwen3-8-27b
- Q8 /model-pricing
- Q9 /context-cache
- Q10 /qwen-api-via-openai-chat-completions
- Q11 /compatibility-of-openai-with-dashscope
- Q12 /regions
- Q13 /qwen-function-calling
- Q14 /deep-thinking
- Q15 /qwen-structured-output
- Q16 /rate-limit
- Q17 /quota-management
- Q18 /new-free-quota
- Q19 /bill-query-and-cost-management
- Q20 /budget-management
- Q21 /error-code
- Q22 /model-depreciation
- Q23 /newly-released-models
- Q24 alibabacloud.com/en/notice/detail (notices 2074, 2037 and 2009)
- Q25 huggingface.co/Qwen (the Qwen3.8 model cards)
- Q26 qwencloud.com and docs.qwencloud.com
- Q27 docs.litellm.ai/docs/providers/qwencloud (secondary)

## Approved (2026-10-06, between 09:53:12 and 10:05:35 -0700, two clock readings bracketing the answer)

The lower reading is the plan's last edit before it went to Logan, and the
upper is the lead's clock on receiving his answers. Logan, verbatim, through
the question tool:
- on scope, "Add the replay (Recommended)": decision 1(b);
- on models, "Flash only (Recommended)": decision 2(a);
- on the ceiling, "API bills, Qwen inside (Recommended)": decision 7. The
  $250 covers what the measured models' APIs bill, Qwen included, and not
  the Claude sessions building the harness;
- on the plan, "Approve with defaults (Recommended)". That covers decisions
  3(a), 4(a), 5(a) and 6(a), and what is carried from draft 3.

Every answer again took the lead's default, which is recorded as data for
H16, and for the track record CX §4 proposes.

**Not yet begun.** These stay Logan's, whenever he is ready:
- creating the DeepSeek account and accepting its terms;
- the first $25 top-up;
- setting `DEEPSEEK_API_KEY`.

The round begins at his go, with P0.
