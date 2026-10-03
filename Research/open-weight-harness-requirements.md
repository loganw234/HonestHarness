# An open-weight harness for ParcelRound and HonestFramework: requirements derived from cft-fp256

Oct 1, 2026 · @Logan · revised 2026-10-02 (the revision log is at the end)

Running ParcelRound and HonestFramework on open-weight models takes a purpose-built harness, not a model swap. Its core is a non-LLM orchestrator that turns rules agents now have to remember into mechanisms they cannot route around (H1–H17). Models are placed by replaying cft-fp256's own send-backs and planted faults, and autonomy grows per area as that area's enforcement hardens. The owner's stated aim (§9.5): principles hardened into the system steer the models toward the author's intent without the author's significant feedback, and without cheating to pass as the work gets harder.

Dense, machine-oriented reference. Written 2026-10-01 for agents that will design or build the harness; revised 2026-10-02 with cft-fp256's language and step-6 rounds, the record's first non-Claude model, ParcelRound's round 5, and the owner's aim. Companion to the earlier report on open-weight tool-calling formats and protocols (“the tool-calling report”); section references like “TC §7.5” point there.

## §0 Scope, sources, legend

**Question answered.** What would a harness similar to Claude Code need, if it is specialised for the methods practised in `loganw234/cft-fp256`, runs open-weight models (alone or beside closed ones), lets a lead model direct agents whose results are verifiable, and moves toward autonomous work with less and less human involvement as the project's standards harden?

**Primary sources read** (all public, cloned 2026-10-01):

| repo | commit read | what it is here |
| --- | --- | --- |
| [loganw234/cft-fp256](https://github.com/loganw234/cft-fp256) | `ded90d8` (2026-09-30 23:02 -0700), full history, 1,232 commits | the experiment: the project the methods run on |
| [loganw234/ParcelRound](https://github.com/loganw234/ParcelRound) | `8767e23` (2026-09-26), 86 commits | the allocation method: METHOD.md, CASE-STUDY.md and CASE-STUDY-2 to -4, templates, four ledger archives (zips, unpacked and read) |
| [loganw234/HonestFramework](https://github.com/loganw234/HonestFramework) | `65447fd` (2026-09-12), 4 commits | the verification method: METHOD.md (ten mechanisms), FAILURE-MODES.md, CASE-STUDY.md, ADOPTING.md, templates |
| loganw234/cft-fp256, again (2026-10-02 revision) | `4190a47` (2026-10-02 12:32 -0700), 1,303 commits | the language rounds and step 6. docs/VALIDATION.md there is `ded90d8`'s file with 509 lines appended (16671-17179), so every `VAL:n` below 16671 names the same line at both commits |
| ParcelRound, local branch `round5-case-study` (2026-10-02 revision) | `49a9266` (2026-09-30), not pushed (no remote ref; loganw.dev VALIDATION.md, the round's close) | CASE-STUDY-5.md (round 5, which built loganw.dev) and archive/round5-ledger.zip |
| [loganw234/loganw.dev](https://github.com/loganw234/loganw.dev) (2026-10-02 revision) | `43c36a2` (2026-09-30) | the site round 5 built: docs/SPEC.md (the owner's dated decisions), docs/ROUND1.md (its plan), docs/VALIDATION.md |

cft-fp256 cites ParcelRound as `../../ParcelRound/METHOD.md` and as “loganw234/ParcelRound”; ParcelRound's case study 3 says round 3 was asked to “use ParcelRound for the agents and the HonestFramework repository for what counts as a verified claim”. So “the methods” = these two, applied to cft-fp256.

Also read for the revision, on the owner's desktop: cft-fp256's gitignored `Data/runs/<date>-<round>/` directories. They hold each round's ledgers and briefs from 2026-09-24 on, the cross-model challenge suite and the hard-workload results. Round 3's ledgers (2026-09-24/25) are also in ParcelRound's public `archive/round3-ledger.zip`; the rest are in no clone. Also written for the revision, beside this repository's round plan: `Rounds/ParcelRound-R6/practice-survey.md`, which records which of the 54 pending ParcelRound proposals later rounds practised.

Also read: Claude Code documentation at code.claude.com (fetched 2026-10-01) on gateways, subagents and dynamic workflows. That describes the harness the methods run on today. Plus a few secondary web pages on current open-weight models, flagged as such.

**Evidence tags.**

- **[R]** measured in the record: VALIDATION.md, case-study timelines, ledger archives, git.
- **[M]** a rule stated in ParcelRound's METHOD.md (`PR §n`) or HonestFramework's METHOD.md (`HF §n`), or in another named file of those two repositories (README, ADOPTING, templates).
- **[D]** Claude Code's official documentation.
- **[S]** secondary web source; dated, verify before relying on it.
- **[I]** inference or proposal by this analysis; not measured anywhere.
- **[O]** the owner's own words, given directly to this document's author, with the date; in no repository.

Citations name the file and, where useful, its line or the case study's timeline stamp. `CS1` to `CS4` are ParcelRound's CASE-STUDY.md and CASE-STUDY-2.md to -4.md, and `CS5` is CASE-STUDY-5.md on the branch `round5-case-study`. `VAL:n` is line n of cft-fp256's docs/VALIDATION.md at `ded90d8`, or at `4190a47` for n of 16671 or more. `RM:n` is cft-fp256's docs/ROADMAP.md and `WR:n` its programs/workloads/README.md, both at `4190a47`. `LR:n` and `SL:n` are lines of the lead's ledger in the language round and the step-6 round (`Data/runs/2026-10-01-lang-round/ledger/lead.md` and `Data/runs/2026-10-02-step6-round/ledger/lead.md`), local only.

## §1 Summary

1. **What the methods are.**
   - **ParcelRound** allocates work. A lead lands a shared seam first (P0). Parcels (one agent, one brief, one worktree) build in parallel. A verifier whose only job is to disconfirm sits between each parcel and its merge. An append-only ledger outside every worktree, with an `urgent/` push channel, is the only way to correct a brief after dispatch. Merges are serial, with the full suite after each one.
   - **HonestFramework** verifies, so that no claim rests on the AI's judgement:
     - one authority that cannot argue, with every other implementation held to it bit for bit;
     - refusal by name as the only alternative to a correct answer;
     - gates watched to fail, with permanent negative controls;
     - one fact in one place, generated and `--check`ed;
     - logs read, not exit codes;
     - provenance carried inside the artifact;
     - an append-only, dated record;
     - uncertainty carried in the value, not in a footnote;
     - planted-fault controls on any judgement;
     - one front door, plus a list of what has already cost hours.
   - cft-fp256 is the largest application: 1,232 commits from 2026-08-28 to 2026-09-30 [R]. 1,183 of them carry a `Co-Authored-By: Claude …` trailer [R]. By `4190a47` (2026-10-02) it had 1,303 commits, and every trailer since 2026-09-23 names Claude Opus 5.5 [R].
2. **The verification half is already model-agnostic.** HonestFramework's README: “Nothing here depends on phrasing, model, or version. The mechanisms are files and exit codes.” [M]. This is what makes open-weight models viable here: a weaker model's claim is checked by the same machinery as a stronger one's.
3. **The judgement roles are not model-agnostic.** These are the lead's work: reading the requester's code, drawing the seam, writing briefs that name the trap, diagnosing under uncertainty, writing records. So is the verifier's best work, which PR §6 says to expect *outside* the list it was handed. These are the roles to qualify most carefully before handing them to an open-weight model.
4. **Many of the incidents behind METHOD.md's rules are mechanical, not judgement** [I]. §5 lists 35 rules or incidents, each mapped to a harness mechanism. Some come from limits of the current harness:
   - watches that expire after 30 minutes and need consent to run overnight [R CS4];
   - workflow-spawned agents that cannot be resumed (“No transcript found for agent ID”) [R CS3];
   - truncated completion notices [R CS3];
   - a shared scratchpad holding a secret [R CS4];
   - automatic compaction from 968,139 to 20,900 tokens [R CS3];
   - every notification making the lead re-read its whole context: event-started turns were 33% of its cache reads for 10% of its output [R CS3].

   The rest are lapses of discipline that a harness can enforce:
   - guessed timestamps: in round 2 the lead (three times), P1, P2, P3, P4 and V4; in round 3, 5 of 38 watched entries and 5 of the fixers' 6 stamps [R CS2, CS3];
   - worktrees made from the wrong repository or the wrong HEAD [R CS1, CS3];
   - merges during a running suite, stale binaries, and “pushed” claimed from a local ref [R CS1, CS2; HF].

   A purpose-built harness turns each of these from a rule an agent must remember into a mechanism it cannot route around. That is HonestFramework's own move, applied to the process instead of the product.
5. **Recommended shape.**
   - A non-LLM orchestrator owns the round state machine, the ledger service, the event routing, the merge queue, the gate adapter, the resource broker, the policy store and the records compiler.
   - Model-agnostic LLM workers run on TC §7's canonical item model.
   - Toolsets and permissions are scoped per role, and every agent can be resumed.
   - Reports are schema-validated, and a claim-to-evidence checker ties every MEASURED figure to the tool call that produced it.
   - §6 has the requirements (H1-H17), each with an acceptance test in HonestFramework's “watched to fail” form.
6. **Model placement is decided by measurement, using the project's own history as the benchmark.** Three sources:
   - **Recorded send-backs as a verifier test.** The record holds defects verifiers found, with the parcel tips before and after each fix: V1-V4 in round 2, verifier-P1's D1-D10 in round 4, W1-W6 on 2026-09-30.
   - **Archived briefs to replay.** Round 2's P1-P4 are in cft-fp256's docs/ROUND2.md, as dispatched at `48eb4b0` (wave 1) and `e0f211f` (wave 2); never HEAD's copy, which was amended afterwards. Round 4's P1-P3 are in ParcelRound's round-4 archive.
   - **Planted-fault diffs with the key withheld** (HF §9).

   HonestFramework already says a detection rate is “a property of that combination”, meaning the model, the prompt and the tooling. So: “Record the score, the date, and the model. Re-run when any of those change.” [M ADOPTING step 8]. Start open-weight models in bounded roles: fixers, scoped re-checks, auditors, triage, and narrow parcels. Move the lead and the verifiers only when replay scores justify it, and give each verifier a different model family from its parcel [I].

   **Since the first draft** [R]: the record now holds its first non-Claude evidence.
   - Given cft-fp256's language document, six example sources and one compiled bundle, GPT-6.1 Sol Max wrote a 212-program challenge suite, which found one real compiler defect.
   - Given the results Claude returned as well, it wrote a 21-program hard-workload pack with its own oracle (§2.2).
   - ParcelRound's round 5 ran every parcel and every parcel's verifier on Sonnet. The owner's direction said “(5.5 is current)” and the dispatch said only “sonnet”; the transcripts record `claude-sonnet-5`. One Opus verifier's transcript records `claude-opus-4-8` for ten of its messages (§8.3, H15.1).
7. **The autonomy gradient is already in the record.**
   - Round 2: the owner approved the plan and the ABI at 03:30, and the session panel shows 1 h 38 min of human-active time against 23 h 40 min of API time [R CS2]. The owner read that panel after the twelfth hour of a round of about 24 h, so these are not whole-round totals (CS2:528-531).
   - Round 3: no owner message for the last 13 h 41 min [R CS3].
   - 2026-09-30: the owner approves an *ordered queue* of rounds with one hold point and delegates the shape: “if any of the first 5 are small enough, you may handle them alone” [R VAL:16350-16351].
   - Owner decisions become dated standing rules (“Logan's rule”, 2026-09-25, 09-26 and 09-27) that later plans carry under “How it is held” [R].
   - The owner still makes technical decisions every round. VALIDATION keeps a “Logan's decisions this round” list (VAL:15637, 15836, 16162). One owner question uncovered that RETIMING had reached only one of a quad's four tiles (VAL:16349) [R].
   - **2026-10-01/02: two channels carry the steering** [R].
     - **The questions put to the owner.** In the language and step-6 rounds, seven of the owner's recorded decisions are picks of the option the lead marked “(Recommended)” in a structured question, and one more approves twelve recommendations at once (LR:54-55, 510; SL:112, 114, 219-220, 855).
       - About as many are in the owner's own words. Among them are the compiler's intention-out (LR:64), the cross-model test (LR:397) and certificate v2's “scientific provenance” (SL:222) (§3.4).
       - Recommendations often give reasons, and the step-6 plan, written after the owner's choice, records one derived from a dated owner rule (RM:4748-4751). Nothing requires a reason, and nothing checks that it supports the default.
     - **The lead's own approvals**, inside an approved plan. The lead approves the parcels' designs: L1's eight choices, L2's nine, L3's ten, and D2's (LR:96, 129, 345, 497). Under step 6's delegation of names and encodings (RM:4702), it approved R8's three control codes where the plan said “Two instructions” (RM:4692; SL:371), and an added ABI field, `lane_flags_bytes` (SL:366, 374).

   The harness should formalise this. A policy store holds standing rules and reserved decisions. Autonomy is granted per (area, decision class) as that area's enforcement level rises (“autonomy follows enforcement”). Promotion and demotion follow a measured track record (§9). The owner's aim goes further [O 2026-10-02]: principles hardened into the system should steer the models toward the author's intent without the author's significant feedback, and should hold when the work gets harder. That makes the recommendation itself an object to verify, and honesty under difficulty a property to measure (§9.5-9.6, H16-H17).
8. **The method of record lags the method in practice.**
   - ParcelRound's METHOD.md was last changed 2026-09-16, when it took in round 2's proposals [R `git log`].
   - Round 3's and round 4's proposals are still “the owner's to settle” [R CS3, CS4]. For round 5 the owner applied them by decision (loganw.dev SPEC.md decision 19), but none has been taken into METHOD.md.
   - cft-fp256's later rounds practise several of them anyway: a verifier on the lead's own commits [ROADMAP.md:4046] and on each round's record draft (V10, C8, R6, A4, F4, W6). The practice also carries rules of the owner's own, such as the 2026-09-27 send-back rule (VAL:15274) [R].
   - CS4 observation 32: “A lesson the owner has not adopted travels in the lead's memory, and only there.”
   - **The lag is wider than the proposals** [R].
     - Round 5's 13 proposals are pending too, on a branch not yet pushed (CS5:335-386).
     - ParcelRound's templates have not changed since 2026-09-11, so they lack even round 2's adopted rules. In round 3, a ledger README copied verbatim from the template and three send-back scripts all lacked the stamp rule, and 5 of the fixers' 6 stamps were typed (CS3:355-362).
     - From the audit round (2026-09-29) on, cft-fp256's rounds dropped `urgent/` with no proposal. The lead messages agents directly and records the messages in its ledger.
     - cft-fp256's parcel briefs since 2026-09-25 also dropped what METHOD.md calls the highest-yield sentence in the system, the request for “anything you found that the brief got wrong” (§3.5).
   - The owner set the next step on 2026-10-02 [O]: a ParcelRound round that brings METHOD.md and its templates to the method as practised, starting with the findings practised but never recorded.

   A harness policy store with adoption status closes that gap (§10). Briefs compiled from today's templates (H10.4) would re-introduce retired rules, so the templates must be current first.
9. **Practical constraints.**
   - Anthropic “doesn't support routing Claude Code to non-Claude models through any gateway” [D], so a custom harness is the supported route. It can still call Claude through the API for the lead or verifier role in a mixed fleet [I].
   - The machines this repository names are a Windows desktop (12 threads, 47 GB shared with Windows, WSL distro `cft2204`) and `amd-arc-box` (36 threads, 46 GB, the U50). An RTX 5060 Ti is the GPU named in the photograph check [R CLAUDE.md, README]. Frontier-scale open weights do not fit on these: Kimi K3 is about 1.4 TB at MXFP4, multi-node [S]. So expect hosted endpoints, which makes provider variance (TC §4.6) and data governance first-order concerns [I].
10. **First steps** (§12):
    - bring ParcelRound's method and templates to current practice;
    - build the qualification suites from the archives before building the orchestrator, including QS9, which measures whether a model cheats as a task becomes infeasible;
    - then run one small mixed-fleet round on a real work item.

## §2 The experiment

### §2.1 The three repositories

| repo | licence | size and shape [R] | what to take from it for the harness |
| --- | --- | --- | --- |
| cft-fp256 | Apache-2.0 | 812 tracked files, 24 MB; RTL for an Alveo U50, a Python golden model as the authority, libcft (“about 24,000 lines of C99”, README's own figure), bindings in nine languages, WASM pages; since 2026-10-01, a language for ODEs and maps (`.cftl`) and its compiler, `python/cftc`; `verify/run.sh` (1,353 lines, 46 stages; 50 at `4190a47`); docs/VALIDATION.md (16,670 lines, append-only; 17,179 at `4190a47`); CLAUDE.md (191 lines) | the live operating model: plans of record, briefs, verifier lists, records format, standing rules, the gate runner's contract, the failure history |
| ParcelRound | MIT | METHOD.md (798 lines, §§1-8), four case studies (2,069 lines together), templates (brief, verifier, ledger, checklists), ledger archives for rounds 2, 3, 4 and round 4's second round; round 5's case study and ledger archive on the unpushed branch `round5-case-study` | the allocation protocol, the observed failure modes of the current harness, cost data, the archives that can be replayed |
| HonestFramework | MIT | METHOD.md (873 lines, ten mechanisms), FAILURE-MODES.md (17 quick-reference entries, families A-I), CASE-STUDY.md (six repositories, 743,605 lines), ADOPTING.md, templates (`gate-runner.sh` and `check_generated.py` both runnable), `tools/check_claims.py` | the claim-verification contract the harness must require of a project, and the “control the judge” protocol for qualifying models |

### §2.2 cft-fp256's scale and tempo [R]

- **Commit volume.** 1,232 commits from 2026-08-28 to 2026-09-30. The peak was 106 on 2026-09-03. The last three days had 48, 83 and 75. By `4190a47` (2026-10-02 12:32): 1,303 commits, 71 of them after `ded90d8`.
- **Model trailers.** Of the 1,183 `Co-Authored-By` trailers, by model:

| model | trailers |
| --- | --- |
| Claude Fable 5.1 | 480 |
| Claude Opus 5.5 | 303 |
| Claude Opus 5 | 268, plus 15 marked “(1M context)” |
| Claude Fable 5 | 114 |
| Claude Opus 4.8 | 3 |

Every commit's author is Logan. The current fleet is frontier closed models throughout. At `4190a47` the Opus 5.5 count is 373 and the rest are unchanged: every trailer since 2026-09-23 names Opus 5.5. The one non-Claude model in the record wrote files but no commits (below).

- **The front door.**
  - `make verify-quick` runs 30 of 46 stages in about 20 min. At `4190a47` it is 31 of 50: `lang` has joined it.
  - `make verify-gate` runs 40 of 46 in about 2 h. At `4190a47` it is 43 of 50: `lang` (through the quick budget the gate includes), `tangent` and `acceptance` have joined it, and `acceptance-far` the full census.
  - `make verify` runs the full census, which takes hours.
  - Each stage drops a `.ok` or `.fail` marker. `--resume` refuses to cross commits, and there is no cache across runs. A skipped stage is named with its reason, and `--require-all` makes a skip a failure. Since 2026-09-24, checks skipped *inside* a passing stage are counted on the VERDICT line.
- **What is checked.** 1,068,915 published conformance cases; 26 RTL simulation targets; 30 formal proofs plus a negative control; MPFR and native-CPU oracles.
- **Rounds in cft-fp256 since the method was extracted.**
  - Round 2 (2026-09-15/16): asks 1, 4, 5 and 6 from cft-rebound, ABI 0.14.
  - Round 3 (2026-09-24/25): a documentation sweep, then four follow-ups.
  - Six rounds from 2026-09-25 to 09-30, recognisable by their verifier name prefixes, then the language and step-6 rounds (table below). Dates span the plan of record or records directory to the VALIDATION entry.
  - Round 4 ran in a different project (Quantum-Film, 2026-09-25/26) and is recorded in CS4.

| prefix | verifiers | dates | work |
| --- | --- | --- | --- |
| V | V1-V10 | 09-25 to 09-28 | controlled divergence, steps 1b and 1c |
| C | C1-C8 | 09-28 to 09-29 (`Data/runs/2026-09-28-cert-round/`) | step 2, certificates; C1 reviewed the plan itself before any code |
| R | R1-R6 | 09-29 | revision 7 |
| A | A1-A4 | 09-29 to 09-30 (`2026-09-29-audit-round`) | the C auditor and golden certificates |
| F | F1-F4 | 09-30 | the fixes round |
| W | W1-W6, re-checks W1b and W3b | 09-30 | steps 5 and 6 |
| P, VL, VD, VI (the language round) | P1 (on the plan), VL1-VL3, VD1-VD2, VI, VI2 | 10-01 to 10-02 (`Data/runs/2026-10-01-lang-round/`) | the work order's step 3: the language golden-first (L1), its compiler `cftc` (L2), the variational equations (L3), defects D1 and D2 (VAL:16672, 16848) |
| P, VA, VI and more (step 6) | P6 (on the plan), VA1, VI1; then VS8, VCV2, VT1, VL4, VR8 and VI2, whose verdicts are in the round's ledger (SL) and not yet in VALIDATION.md | from 10-02 (`Data/runs/2026-10-02-step6-round/`) | the acceptance set, a card's admission test (A1); then revision 8, certificate v2, instruction streaming (VAL:17040) |

That is 38 named verifiers in six rounds over six days. Steps 0 and 1a, in the 2026-09-25 entry just before, add verifier-S0a and verifier-S0b (VAL:14716, 14749). The language and step-6 rounds add 17 more by 2026-10-02, counted from their ledger files. Names recur across rounds: A1, P1 and VI2 each name different agents in different rounds, so a harness must qualify agent ids by round (§7).

**The cross-model exchange, 2026-10-01/02** [R]. The owner put the language round's first part to a “semi-independent” stress test (VAL:16852):
- **What the other model was given.**
  - For the challenge suite, GPT-6.1 Sol Max received docs/LANGUAGE.md at `80abee5`, the six reference sources and one compiled bundle. It had no compiler and no golden model where it worked (WR:19-34; VAL:16852).
  - For the hard-workload pack it also had the archive of results Claude returned. The pack's own README says “Both adapters were based on the working interfaces in your returned archive” (its README.md:67, also :31 and :49-50), and its runner calls itself “using the returned CFT APIs” (`tools/run_workloads.py:2`).
  - WR's “and nothing more” (WR:21-22) therefore overstates for the pack. VA1 confirmed the note's quotation and figures, not that claim (VAL:17105).
- **The challenge suite**, 212 programs (`Data/runs/2026-10-01-challenge-suite/`):
  - 205 PASS, 3 TARGET-LIMIT and 4 unscored on the software backend; 423 of 423 run-vector checks (VAL:16902-16910);
  - one real defect: two accepted maps stopped the compiler with an internal error, exit 70, and they are now refused by name as `unused` (VAL:16852-16855, 16916). Two of the round's own verifiers, VL3 and VD2, found the same class by other roads (VAL:16856). Six refusal sentences were also restated to state the rule they apply (VAL:16918, 16933);
  - the other model then audited the archive returned to it and found no inconsistency in 1,526 files (VAL:16911-16912). Its review held that the exit-70 rows “must remain visible as compiler defects” (the review's REPORT.md:26, in the same directory).
- **The hard-workload pack**, 21 programs in 7 families, tracked as delivered in `programs/workloads/cft-hard-workloads/` (87 files, 10,614,822 bytes at `03157e0`):
  - its one-step oracle imports nothing of the repository (WR:47-52);
  - 10 of the 21 fit the card and run bit for bit with the software backend; 11 do not fit one tile (VAL:16997, 17003-17006). The pack's own runner verified all 21 on the CPU path (VAL:17132). The misses became step 6's work (RM:4657-4663; VAL:17139).
- **Its independence was partial.**
  - The pack's adapters say “Based on the working adapter in the user's returned result archive” (`tools/golden_adapter.py:3`). So the pack was the third exchange of a loop that included results Claude returned, not a test from the specification alone.
  - Its oracle is the independent part.
    - `exact_oracle.py` imports only the standard library (WR:47-52).
    - It is the challenge suite's own oracle, which existed before any results went back. The suite's zip of 2026-10-01 14:53 holds it, and the returned results' README.md:3 pins that zip by its SHA-256.
    - The pack's copy differs from it by 12 diff lines: the fp128 and fp256 formats, a cache, and its docstring (`Data/runs/2026-10-01-challenge-suite/original/`).
  - Its commit, `03157e0`, carries a Claude co-author trailer.
  - HF §1's rule holds for a foreign oracle too: it is external only as far as its inputs are.

### §2.3 Where each artifact lives (the map a harness must model)

| artifact | location in practice [R] | structure |
| --- | --- | --- |
| plan of record | `docs/ROADMAP.md`, sections titled “(plan of record, YYYY-MM-DD)”; round 2's in `docs/ROUND2.md` | the owner's approval quote first (e.g. ROADMAP.md:3905) → the survey “What the tree has”, read from code → **Parcels**, each with its gate and named plants → **The lead's own** → **How it is held** (a verifier per parcel and one for the lead's commits; agents run quick tests and hand long runs back; machine rules; send-back rule) → **What it is not**. ROUND2.md also has “Decisions this plan leaves to Logan”, with defaults. From the C round, a verifier reviewed the plan itself before dispatch (VAL:15649-15652). After the round, a “Built” summary is put on top and the plan is kept as written |
| briefs | round 2: inside `docs/ROUND2.md`, P1-P4. Round 4: `briefs/P*.md` in the ledger. Recent rounds: `Data/runs/<date>-<round>/`, gitignored [VAL:16506] | the template sections (PR §3, `templates/brief.md`) |
| ledger | one directory per round outside every worktree, outside version control; a README from `templates/ledger.md`; `urgent/`. In cft-fp256, `urgent/` is gone from the audit round (2026-09-29) on and the README from the fixes round (2026-09-30) on; the lead messages agents directly (§3.5) | per-author append-only `.md` files; entries `## <stamp> — <headline>` / `Measured:` / `Believed:` / `For:`; zipped beside the case study at the round's end |
| agent notes | `CLAUDE.md` | the front door; a table of machines; numbered traps (“four of the five traps, three of which exit 0”); which gates mean something; “Before believing a remote build”; the authority |
| gate runner | `verify/run.sh`, `docs/VERIFICATION.md`, `verify/README.md` | stages, budgets, markers, `report.jsonl`, the VERDICT line, inner skips |
| record | `docs/VALIDATION.md`, append-only by rule: a closed entry is never edited and is corrected by a new dated entry, while the newest entry is revised as it is written (34 of the 35 commits that delete lines from it touch only the open entry) | per round: **Why** (the owner's words, the plan reference) → one block per parcel (what was built, the verifier's MEASURED lines, send-backs, re-checks) → **The lead's own** → **The front door** (run ids, verdicts, named skips) → **Known limits, recorded rather than fixed** → **The lead's own slips** → **Load, and the machine** |
| method evolution | ParcelRound case studies → “What METHOD.md should say differently” (each item tagged new, reinforcement, extension, relaxation or reversal) → owner adoption → METHOD.md | round 2's proposals adopted in full on 2026-09-16; rounds 3, 4 and 5 still pending in METHOD.md, though round 5 applied 3 and 4's by the owner's decision (§3.5) |

## §3 The operating model as practised

### §3.1 Roles

| role | does | must not | evidence |
| --- | --- | --- | --- |
| **owner** (Logan) | approves the plan of record or an ordered queue with hold points; decides what is reserved (card days, clocks, pushes to other repositories, deploys, finite external resources, method changes); pauses and resumes; adopts method proposals; turns repeated decisions into standing rules | — (sets the standards) | CS2 “How the round was run”; VAL:16350-16351, 16507; §3.3 below |
| **lead** | one long-running session that: reads both repositories; writes the plan; builds P0; writes and lints briefs; dispatches; watches the ledger; answers escalations; merges serially on staging branches; runs the suite on the build host; writes seam tests; does the docs sweep in idle time; runs card days; writes the records and the case study; reports cost | merge on the strength of a report; merge while a suite runs; let its own code skip the gates | PR §7; CS1-CS4 |
| **parcel** | one brief, one worktree; owns files by function; builds its named negative control and shows it failing; writes to the ledger at the bar; escalates through `urgent/` (by message in cft-fp256 from the audit round on, §3.5); reports brief errors (a request cft-fp256's briefs stopped making, §3.5) and boundary crossings | push, merge, rebase, commit to main; weaken an assertion; fix anything outside its scope | `templates/brief.md`; CS2 timeline |
| **verifier** | disconfirms: re-runs gates from a clean build; re-runs or builds controls; diffs scope against the ownership list; hunts the cheat shapes; checks the claims in comments and docs; reports per item “confirmed / defect / not determined”, separating “the shipped code is right” from “the gate would catch it”. Also checks the lead's P0 before dispatch (a precondition since round 4), the lead's own commits, and the record's draft | fix anything; read parcels' self-reports before forming its own view (it watches the lead's channel only) | `templates/verifier.md`; PR §6; CS4 timeline; VAL:16601-16602 |
| **re-check** | the scoped check after a fix: 11 to 23 minutes each in round 2 | re-run the whole list by default | PR §6 |
| **fixer** | a fresh agent briefed with the verifier's defects, the parcel's ledger file and its worktree, used when the parcel cannot be resumed | — | CS3 §8 observations |
| **auditor** | a read-only sweep of one document group; its findings go to verifiers told to refute them | edit anything | CS3 phase 1 |
| **triage** | sorts side notes into findings and non-findings; round 3 had 324 items, of which 51 were findings | — | CS3 |
| **reviewer** | checks the lead's applied diff against the verifiers' findings; round 3's review fixed 85 document problems and found 17 gate issues, “the highest-yield step of the day” | — | CS3 |
| **fact-gatherer / record checker** | rebuilds the timeline and cost from transcripts; checks a draft record or case study | — | CS3 “Other costs”: 4 gatherers, 4 checkers, 3 re-checkers wrote CS3 itself |

### §3.2 Lifecycle of a round (a state machine to persist)

1. **Request or order** from the owner. Since 2026-09-30 this can be a queue with hold points [R VAL:16350-16351].
2. **Read the requester's code, not its ask list**, and survey the tree. Round 2's plan took three corrections from this before any dispatch: ask 6 already delivered, asks 1 and 4 one mechanism, ask 5 capped at 2% [R CS2 02:00-03:30; PR §1].
3. **Plan of record**: committed, with decisions left to the owner and their defaults; reviewed by a verifier against the tree (the C round's C1 made twenty findings on the first draft and re-checked the second, VAL:15649-15652); approved by the owner.
4. **P0 seam**. It preserves behaviour, which is proven by the full suite on both sides. A verifier checks it before any parcel that reads its seams is dispatched [R CS4 obs 1, 5].
5. **The ledger** is created, seeded with environment traps and standing rules, and its README written. The lead arms its watch *in the same turn as its first dispatch* [R CS4 obs 2].
6. **Dispatch wave 1**, long pole first.
   - Every path, function and stage the briefs name is checked to exist.
   - Base commits are written “at or after”, with the exact tip in the dispatch message.
7. **Parcels work.**
   - They write to the ledger at the bar and escalate through `urgent/`, or by message in cft-fp256 from the audit round on (§3.5).
   - The lead answers in minutes: CS2 measured one minute for the first escalation; CS3 measured 10 to 68 s [R].
8. **Report → verifier.**
   - The verifier gets a numbered list plus “what else”, and returns a verdict.
   - Only a regression or a wrong answer sends a parcel back. Anything else merges as a known limit, and an overclaiming sentence is restated at the merge [R the 2026-09-27 rule].
   - After a fix comes a scoped re-check.
9. **Merge.**
   - Each merge or declared batch gets a staging branch and a seam test.
   - The full suite runs on the build host at the staging commit, and the lead reads the log.
   - Main moves on that verdict, and the push is checked with `git ls-remote`.
10. **Wave boundary.** The ledger is folded into the next wave's briefs, the one moment a brief can change [R CS2 11:41].
11. **Build phase ends.** For hardware there follow the image builds (5 to 8 h each) and the card day, which belong to the lead and the owner.
12. **Records.**
    - The VALIDATION entry is drafted from the ledger and runs, checked by a verifier, and committed.
    - ROADMAP gets “Built” and its debts.
    - Known limits are recorded.
    - The ledger is archived with its timestamps.
13. **Optional retrospective.** A case study yields method proposals, which go to the owner for adoption.

**Overlay: pause and resume.**

- On the owner's word, each agent commits where it is and writes a resume note. Example: “Go ahead and instruct agents to wrap up for now … commit where they are and leave a resume note for themselves incase context is lost in the downtime” [R VAL:16507].
- Agents that do not survive a session are dispatched again from their brief and their own resume note [R].
- CS4 obs 12: “A usage pause is survivable when the ledger is the state.”

### §3.3 Standing rules: owner decisions that became policy [R]

| date | rule (owner's words where recorded) | where |
| --- | --- | --- |
| 2026-09-15 06:3x | “we may want to utilize the quick tests”: dispatch on the Verilator suite, with Icarus confirming in the background | CS2 timeline; PR §8 |
| 2026-09-16 07:50 | “Logan's word on the clock”: if the quad fails to close, 130 MHz is acceptable; “135 was tight every time, a minor drop is fine”. CS2's own narration adds “Banked as a standing rule” | CS2 timeline |
| 2026-09-16 | round 2's method proposals adopted in full | CS2 heading; ParcelRound `9b18e35` |
| 2026-09-24 09:00 | no planted faults on the auditors: “a comprehensive sweep of whats there, not new sourced data”. So the record holds no detection rate for its verifiers (“suggestive, not a detection rate”) | CS3 setting; VAL:14296-14299 |
| 2026-09-24 09:50 | “Let the verifiers finish before you apply anything.” | CS3 timeline |
| 2026-09-25 | a verifier on the lead's P0 before dispatching P1-P3 (Quantum-Film) | CS4 setting |
| 2026-09-25 | “no agent loads the machine on purpose” (kept as “Logan's rule” in the C round) | VAL:15440; VAL:15794 |
| 2026-09-26 | on a device backend, a publish of a buffer whose run results nobody has read back is refused by name | VAL:15189; HOSTAPI.md:490 |
| 2026-09-27 | **send-back rule**: only a regression or a wrong answer sends work back; anything else merges as a recorded known limit; a sentence that claims too much is restated at the merge; the lead's commits get a verifier like any parcel's | VAL:15274, 15492, 15647, 15851 |
| 2026-09-29 | a *decision procedure*, not a decision: “adhere to IEEE 754 when an option, RISC V approaches if nothing is in IEEE 754, and if neither state a way to handle it, whatever approach aligns best with the current systems” (first applied to TwoSum's rounding; later cited as “Logan's rule”) | VAL:15843; ROADMAP.md:4135; SEQUENCER.md:2983-2984 |
| 2026-09-29 (R round), carried into the A and W rounds | “dont have the individual agents all run the full suites, have them hand back large runs to you to monitor rather than them, but they should still verify and test as much as they can quickly.” | VAL:15842, 16165 |
| 2026-09-29 08:48 | “shift heavier work to the remote box when possible”; by 09-30 the plans state “The desktop is Logan's to use: one run at a time, niced, and `docker ps` first” | VAL:15846; ROADMAP.md:4049 |
| 2026-09-30 | “Go ahead with your order, if any of the first 5 are small enough, you may handle them alone”; “Hold before starting Step 3 once your get there, the language and its compiler.” | VAL:16350-16351, 16504 |

The pattern [I]: a decision the owner makes once is written with its date and words, carried verbatim into later plans' “How it is held”, and from then on applied by the lead without asking. That is the mechanism by which human involvement already decreases. The 2026-09-29 rule shows the strongest form: a *ranked decision procedure* that settles a whole class of future questions, not just one. The harness should make all of these explicit data (§9, H10).

### §3.4 Human involvement over time [R]

| period | the owner's touches | unattended stretch | oversight catches only the owner made |
| --- | --- | --- | --- |
| round 2, 2026-09-15/16 | approval of the plan and ABI (03:30); “utilize the quick tests”; the instruction to keep the record; two questions about the method; a status check at 11 h; cost figures; the card day “on Logan's word”; the clock rule | most of a 12 h+ build phase; human-active 1 h 38 min against 23 h 40 min of API time, read after the twelfth hour (CS2:528-531) | none recorded |
| round 3, 2026-09-24/25 | 7 messages, all before 12:22, among them: the request (08:32); four decisions on the plan (09:00); “Let the verifiers finish before you apply anything” (09:50); a question about the method (10:12); “Go ahead and tackle the 4 left open” (12:20); “You may start docker here” (12:21) | 13 h 41 min of work after the last message | stopped the lead applying findings before the verifiers had finished (09:50) |
| round 4, 2026-09-25/26 | the P0-verifier precondition; scope confirmations; push permission for atlas-film; pauses (a usage limit, then bed); “lead only, fast” for the second round | the night of the 25th-26th | noticed the lead's watch was never armed (13:48); a once-over before submission found stale notices (06:41) |
| V to W rounds, 2026-09-25 to 30 | each round's record has a “Logan's decisions this round” list (VAL:15637-15647, 15836-15851, 16162-16166). Examples: signing, privacy, accuracy and program limits for certificates; “Defaults are fine, go ahead”; the TwoSum rule; the 08:48 heavy-work word; the push and the quad at 135 or 130 MHz. Also: rebuild step 1b as the plan's step 2 (09-25); the completion-witness design (VAL:14931-14934); an error code to use (VAL:15490); golden certificates as “Logan's suggestion” (VAL:16159); approval of orders with hold points; a pause and resume across sessions | whole rounds between decisions | an owner *question* about the quad's build options led the lead to find RETIMING had reached only one of four tiles (VAL:16349) |
| language and step-6 rounds, 2026-10-01/02 | **seven picks of the option the lead marked “(Recommended)”**: “Approve as written (Recommended)” and “Its own files (Recommended)” (LR:54-55); “No limit (Recommended)” (LR:510); “Flag control in rev 8 (Recommended)” and “Streaming + deep build (Recommended)” (SL:112, 114); the step-6 plan and the gallery (SL:219-220). **One approval of twelve recommendations at once**: “Regarding the 12 questions, the recommended solutions are appropriate as stated” (SL:855). **About as many in the owner's own words**: “Yes, begin on the next step” (LR:3); the intention-out (LR:64); the cross-model test (LR:397); “Fix it in part two, refuse as unused”, choosing between two options the lead gave with no recommendation (LR:440); the hard-workload pack (LR:519); the step-6 scope (LR:667); “Drop step 5 …”, which follows the lead's written advice (SL:7-12); revision 8's contents, a multi-select with no recommendation marked (SL:113); certificate v2's “scientific provenance” (SL:222) | decisions hours apart; the longest gap about 10 h, overnight (the LR and SL stamps) | not surveyed for this revision |

**Reading [I].**

- *Process* approvals moved from each step, to a plan, to a queue with hold points, with the round's shape delegated.
- *Technical direction* is still the owner's to approve: the plans, and every question put to the owner.
  - **Two channels carry the steering now** [R]:
    - the lead drafts the options of a question and marks one “(Recommended)”, and the owner often picks it (the last row);
    - inside an approved plan, the lead approves the parcels' designs itself. These include L1's eight choices, L2's nine, L3's ten and D2's (LR:96, 129, 345, 497).
      - Under step 6's delegation of names and encodings (RM:4702), it approved R8's three control codes where the approved plan said “Two instructions” (RM:4692; SL:371), and an added ABI field, `lane_flags_bytes` (SL:366, 374).
      - The ABI step itself, to 0.17, was in the plan the owner approved (RM:4710).
  - **What the record can't show** [I]:
    - Recommendations often give their reasons, and the step-6 plan, written after the owner chose, records one derived from a dated owner rule (RM:4748-4751).
    - But nothing requires a reason, and nothing checks that a reason supports the default. So the record cannot, in general, tell the owner's intent applied from the model's preference ratified.
    - Two cases show that the check matters:
      - a question put to the owner carried a false premise, “refused on the box (3.10)”, corrected after he answered (LR:510-517; VAL:17031);
      - the step-6 plan wrote the lead's gallery recommendation as already decided, until the plan's verifier caught it (SL:160, 202; VAL:17149).
  - §9.5 and H16 make the steering visible.
  - These remain the “direction” class in §9.4: explicit approval items, not policy.
- Of the owner's catches:
  - three can be mechanised: freeze the tree under audit; a watch that cannot be off; a notices or licence gate;
  - one cannot: the question that exposed RETIMING. A harness can raise the odds of it by putting “which build options were actually applied” into the record (HF §6's “read back from the tool's own log”).

### §3.5 The method of record versus the method in practice [R]

- **ParcelRound METHOD.md.** Last changed 2026-09-16 (`9b18e35`, “every proposal integrated”). Its templates were last changed 2026-09-11.
- **Round 3's proposals** (CS3, 2026-09-25), all pending:
  - brief a send-back as a new agent when the agent cannot be resumed;
  - put the stamp rule into the ledger template;
  - parcels' questions go in `urgent/`;
  - archive the ledger from the working copy;
  - re-arm the watch on expiry;
  - the lead watches `urgent/` continuously and reads the rest at set points;
  - a verifier checks the lead's seam commits *and its records*;
  - the verifier's list includes the lead's grants issued after dispatch;
  - “check every claim in a comment, doc or commit message” is on every verifier's list when parcels write docs;
  - side notes get a step of their own;
  - freeze what is audited;
  - check a gate budget against the merged diff;
  - cost reported as processed tokens;
  - settle at kickoff what the owner wants to see first;
  - decide per round whether the lead sits between verdict and fix;
  - let a verifier reuse a run whose inputs are identical;
  - a worktree the harness creates branches from the session checkout's HEAD, so the brief says `git merge --ff-only <base>` and checks the SHA; never switch a shared checkout's branch; watch CI for “cancelled”;
  - “a sweep is a round”.
- **Round 4's proposals** (CS4, 2026-09-26), all pending:
  - P0 past a verifier before dispatch;
  - a trap one round measures goes into the next seam as a refusal;
  - a tool's check that no stage runs is flagged;
  - a spike states the cases it measured;
  - name a control by the property that makes it bite;
  - a scratch directory per agent, and secrets outside them;
  - the READY standard, “a gate, or a stated limit”, stated in the brief;
  - “what I did not do” is a claim;
  - the lead arms its watch with its first dispatch;
  - re-arm and keep the snapshot; one watch at a time;
  - record where you are when a pause is announced;
  - the lead's decisions go in the ledger first;
  - a gate that reads source text is a stated limit;
  - a limit is stated by the behaviour it concedes;
  - fixes go back to the verifier that found them, which picks its own faults;
  - a stated limit is tested by a fault built to evade the gates;
  - a claim's domain and quantifier are claims;
  - a figure carries its definition;
  - work after the verifier's cut is stated as unverified;
  - a seam changed mid-round is checked against every open branch;
  - prepare the merge while the verifier works;
  - a docstring points to the document;
  - a lead-only round is a shape of its own.
- **What cft-fp256's records show in practice** [R]:
  - a verifier on the lead's commits: “W4 for the lead's own commits” [ROADMAP.md:4046];
  - the plan itself reviewed by a verifier before any code (C1, VAL:15649-15652);
  - each round's record draft checked by a verifier, in every round from V to W: V10 (VAL:15599), C8 (15817-15819), R6 (16124-16129), A4 (16308-16311), F4 (16356), W6 (“Verifier-W6 checked the rest of the lead's integration and this entry's draft”, VAL:16602); R6, A4 and W6 also re-made each merge with `git merge-tree`;
  - long runs handed back to the lead;
  - resume notes.

  Beside these, the practice carries the owner's own rules, which were never METHOD proposals. Example: the 2026-09-27 send-back and known-limits rule (VAL:15274).

**Consequence for the harness [I].** A lead that is not the one that lived through rounds 3 and 4 would not have these rules. An open-weight lead, or a fresh session, certainly would not. Briefs and verifier lists must be **compiled** from templates plus an explicit, versioned policy store, not recalled (H10.4).

**Revision, 2026-10-02** [R].

- **Round 5's proposals** (CS5:335-386) are pending like those of rounds 3 and 4. There are 13, typed new, reinforcement or extension, and one is marked an observation. CASE-STUDY-5.md itself is on a local branch not yet pushed.
  - None of the 54 proposals from rounds 3 to 5 has been taken into METHOD.md.
  - **Most were practised anyway.**
    - For round 5, the owner applied rounds 3 and 4's proposals by decision (loganw.dev SPEC.md decision 19). Round 5's plan lists 26 of their 41 as rules in force (loganw.dev docs/ROUND1.md:136-189, 200-201).
    - A survey of the later rounds' ledgers and briefs (2026-10-02; `Rounds/ParcelRound-R6/practice-survey.md`) found 34 of the 54 practised in a later round and 8 in part. 9, eight of them CS5's, were practised only in the round that proposed them, and 3 not at all.
- **The templates lag the method itself**, not only the proposals.
  - None has changed since 2026-09-11, so none carries round 2's adopted rules, such as substituted stamps (M:349-353).
  - In round 3, the follow-ups' ledger README was a verbatim copy of `templates/ledger.md`, which lacks the stamp rule. The three send-back scripts lacked it too, and 5 of the fixers' 6 stamps were typed (CS3:355-362).
  - The templates say to delete the ledger at the round's end (ledger.md:11-13; checklists.md:100-101). METHOD.md says to archive it beside the case study when the case study cites it by time, and otherwise to throw it away (M:494-498); the templates lack the archive step.
- **A later round showed two of METHOD.md's claims do not hold in general.**
  - Round 2's “every guess ran ahead of the clock” (M:349-353) did not generalise: in round 3, two ran behind (CS3:358-360).
  - “A send-back needs no re-brief” (M:786-790): round 3's three resumptions by SendMessage failed with “No transcript found for agent ID” (CS3:176).
- **cft-fp256 evolved a method of its own**, with no proposal back to ParcelRound and no citation of it (the survey, Table B).
  - From the audit round (2026-09-29) on, the round ledgers keep no `urgent/`, and from the fixes round (2026-09-30) on, no README.
  - The lead answers agents “by message”, resumes them by SendMessage, and records the messages in its own ledger file (the audit round's lead.md:242; LR:129; the steps-5-and-6 round's lead.md:396). The cert round's lead used no watch (“The lead has used no Monitor this round”, its lead.md:951), the rev7 round's read the ledger through one (its lead.md:768), and from the audit round on the ledgers do not say.
  - Stamps are still substituted from the clock (SL:3).
  - **The send-back rule.** Only a regression or a wrong answer sends work back; anything else merges as a recorded known limit. It was the lead's proposal, agreed by the owner (“Agreed with the only regression or wrong answer being send backs”, the ODE round's lead.md:1055-1060).
  - **Long runs** are handed back to the lead, in the owner's words (VAL:15842).
  - **Design first:** a parcel proposes, and the lead approves before it builds (§3.4).
  - **Integration:**
    - the integration verifier checks each merge by re-making it: with `git merge-tree` in the rev7, fixes, steps-5-and-6 and language rounds, and with a parent-union script in step 6 (its verifier-VI2.md:30, 116). The ODE round's record shows no re-made merge;
    - parcels merge into a round branch, and main moves at a round's end or at its milestones, not after each merge. The ODE round pushed 48 commits at once (its lead.md:1523), the cert round a hotfix and then the round (its lead.md:354, 1182), the language round twice (LR:367, 700), and step 6 once so far (SL:727);
    - parcels write their own documents (the steps-5-and-6 round's briefs/S1.md:46-56).
  - **Verifiers** mostly start from the parcel's whole ledger (e.g. the steps-5-and-6 round's briefs/verifier-W1.md:13). METHOD.md keeps a verifier from parcels' self-reports until it has its own view (M:440-444).
  - The record does not say why the push channel was dropped.
- **Its briefs dropped METHOD.md's highest-yield sentence.**
  - METHOD.md asks every report for “anything you found that the brief got wrong”, and calls it “the highest-yield sentence in the whole system” (M:227-228). The template words it “anything you found that this brief got wrong” (brief.md:113-115).
  - It appears in none of the 37 parcel briefs, nor the 2 survey briefs, of cft-fp256's eight rounds from 2026-09-25 on. That was searched on 2026-10-02 in every `Data/runs/*/briefs/`, under several phrasings, and re-checked under twelve by a verifier.
  - The rule governs parcel briefs (M:227-228, in §3). The rounds' 55 verifier briefs never carried it, and a verifier's own open question is “anything else”.
  - Narrower clauses survive. Step 6's A1 brief says “If something cannot be held as this brief says, stop and say why”, and parcels still log “DEVIATION from the brief”. The open question about the brief itself does not survive.
  - Rounds 4 and 5 kept it (the survey).
  - No proposal removed it, and no owner decision did. This is steering drift with no feedback at all, the case the owner's aim (§9.5) is meant to prevent.

**Consequence [I].**
- Briefs compiled from today's templates (H10.4) would re-introduce a rule the method retired, and leave out rules it adopted.
- A brief compiled from a current template would have kept the brief-errors line, and a drift check (§10, item 5) would have reported its absence.
- Bringing METHOD.md and the templates to the method as practised is a precondition of H10.4. The owner made it the next step on 2026-10-02 [O].

## §4 What the record says the system catches, and what it costs

### §4.1 Catches, by round [R]

| round | parcels / verifiers | what was caught | who caught it |
| --- | --- | --- | --- |
| 1 (CS1; a \~15,000-line C integrator) | 5 / 2, plus a follow-up | 12 brief errors from 5 parcels, every parcel correcting its brief; 7 gates that could not fail; a bit-identity defect that 5 parcels, 2 verifiers, a follow-up and 211 assertions all passed over (“21 of 21 values differing at \~1e-4”) | parcels (brief errors, 4 vacuous gates); verifiers (a memcmp/`!=` swap, a false “byte for byte” claim); **the lead's seam test** (the gap defect) |
| 2 (cft-fp256, 09-15/16) | 5 / 4 | 4 send-backs, none for a wrong bit (a cost class, a flag arm reading stale lanes, a read before a bounds check, a gate hole beside an unpriced area column); 2 host defects found on the card that no host suite could see; the plan corrected 3 times before dispatch | verifiers (all 4 send-backs); a probe outside the suite (P4's regression); the card plus instruments built in the hour (host defects) |
| 3 (cft-fp256, 09-24/25; 145 agents) | sweep round 1: 15 auditors, 47 verifiers, 1 critic. Review: 12. Sweep round 2: 15 triage auditors, 15 verifiers. Sweep round 3: 6 checks, 6 verifiers. Follow-ups: 8 parcels, 8 verifiers, 6 fixers, 6 re-checks | sweep: 303 findings (193 confirmed, 89 amended, 14 to the lead, 7 refuted) and 432 corrections landed. Follow-ups: 6 send-backs, 11 defects (8 false sentences, one of them a transcribed number; 1 gate that could not fail; the lead's own grant and its own rule); 5 gates that could not fail fixed; 2 real defects in code no parcel was asked about; 57 brief-error items from 14 reports | verifiers, reviewers, parcels; refutations fell mostly on the auditors' least confident findings (5 of 33 low, 2 of 133 medium, 0 of 137 high) |
| 4 (Quantum-Film, 09-25/26) | 3 / 4, then a lead-only round with 1 verifier | the P0 verifier found 21, 4, 5, 5 and 1 defects over five passes; of the first three passes, a third of the defects were in fixes to the pass before (obs 13); allowlists over spellings fell, and checks on behaviour held | verifiers; parcels (a control the lead named that could not fail) |
| V to W (cft-fp256, 09-25 to 30) | each round lists its verifiers, send-backs and known limits | e.g. W: S1 sent back twice (first for a misclassified refusal and a memory check that could not fail, then for a false page sentence traced to a golden-model gap); S2 twice (a check that could not fail; a regression in a test no stage ran); S3 once (a false doc sentence); S4 once (a checker that never called two of the routines it claimed to hold); W6 found 3 wrong sentences in the lead's integration | verifiers, including on the lead's own work |
| 5 (loganw.dev, 09-29/30; CS5) | the lead's P0 plus 5 parcels; each parcel's verifier on Sonnet; verifier-P0 and verifier-seam on Opus 5.5 | verifier-P0 returned ten NOT READY verdicts on the shared core before READY (CS5:70, 103; loganw.dev VALIDATION.md:219-963). The lead pushed eight commits of its own past its own gate alone; verifier-seam, added on them, found gate-kind defects in three (CS5:110-125). Planted controls caught 2 of 2, twice, one pair found by diffing a tip the ledger named (CS5:158-168). The lead's first draft of the case study had 12 claims wrong or unsourced (CS5:12-14) | verifiers, including on the lead; the lead caught what the Sonnet verifiers missed (CS5:169-182) |
| language 1 and 2 (cft-fp256, 10-01/02) | 5 parcels (L1-L3, D1, D2); 8 verifiers, counting the plan's; the cross-model challenge suite | send-backs recorded at VAL:16708 (L1), 16778 (D1), 16885 (L3) and 16940 (D2). One class, an accepted source the compiler then fails on, was found three ways: the foreign model's suite (exit 70), VL3 (nesting past the parser's 100) and VD2 (a let chain past Python's recursion limit) (VAL:16852-16856) | verifiers; the foreign model's suite |
| step 6, its first parcel (cft-fp256, 10-02) | A1 / VA1 and VI1, with P6 on the plan | P6 found five wrong answers (“(b)s”) in the plan's first draft and three in the rewrite, then passed it clean (VAL:17147-17150). VA1's known limits include that eight mutations of the acceptance driver leave every check green (VAL:17155) | the plan's verifier; the parcel's verifiers |

### §4.2 Cost, by round [R]

| round | measure | figures |
| --- | --- | --- |
| 2 | agent cards (each agent's context figure) | 9 agents; 4.92 M “tokens”; 2,907 tool uses; 22.8 h agent wall inside an 11 h round; verifiers 1.86 M = 38% of the agents'; lead about 1.6 M; about 7.5 M by the round's end |
| 2 | session panel, read by the owner after the twelfth hour (CS2:528-531) | API time 23 h 40 min; human-active 1 h 38 min; output 818.9 k tokens; cache read 3.5 B; cache hit 99%; +15,544 / -987 lines |
| 3 | processed tokens, from transcripts | 145 agents; 2,087 agent-min (34.8 h); output 7.01 M; cache read 1,506 M; 9,035 tool uses; harness figure 26.4 M (= the sum of final context sizes, *not* tokens processed); lead output 491 k, cache read 227.6 M |
| 3 | checking share | verifiers and re-checks: 41.4% of the harness figure, 36.9% of output; every checking role: 52.5% and 47.4% |
| 4, first round | processed | 3,052 responses; output 5.15 M; cache read 1,612 M; 3,667 tool uses; verifiers 42% of the agents' output |
| 4, second round (lead-only plus one verifier) | processed | output 565 k; cache read 218.5 M; about a ninth of the first round's output |
| 5 (loganw.dev) | per agent transcript, once per message; “read” is input plus cache reads and writes, so not comparable with rounds 3 and 4 | agents except P4, whose transcript is empty: 2,061 messages, 746,520 output, 907,441,249 read. The lead: 900 messages, 1,278,391 output, 530,384,559 read (CS5:292-310) |

### §4.3 Per-agent envelopes, for sizing a harness and its models [R]

- **Round 2 parcels** (cards): 52 min to 5 h 15 min wall; 252 to 939 tool uses; 411 k to 814 k tokens. The largest, P3, used 939 tool uses.
- **Round 2 verifiers**: 12 min to 2 h 54 min on their last resume; 31 to 266 tool uses; 366 k to 603 k tokens.
- **Round 3 follow-up agents** (processed output):
  - parcels 89.8 k to 190.6 k output, 149 to 335 tool uses, 20 to 104 min;
  - verifiers 62 k to 97 k output, 72 to 130 tool uses, 12 to 111 min;
  - fixers 23 k to 165 k output, 42 to 211 tool uses, 5 to 106 min.
- **Round 4**: P2, in a second repository, produced 1.28 M output tokens over 864 tool uses; verifier-P2 produced 572 k over 382.
- **Context peaks**: the lead's context reached 968,139 tokens before automatic compaction (CS3). A resumed verifier's first request carried 845,387 tokens (CS4 obs 31).
- **Concurrency**: at most ten agents at once in round 3, with queueing of up to 19.6 min. Claude Code's workflow runtime now defaults to 16 concurrent agents [D].

**Implication [I].** A worker model must sustain hundreds of correct tool calls per task and keep coherence over contexts in the hundreds of thousands of tokens, or the harness must cut work into smaller pieces and externalise state.

### §4.4 Where defects were found [R]

- **Parcels found brief errors and their own vacuous gates.** Round 1: every parcel corrected its brief. Round 3: 57 brief-error items from 14 reports.
- **Verifiers found what the parcel had no instrument for:**
  - cycles;
  - cell and mux counts (P3's mask block cost 59% of the sequencer's cells before its rewrite);
  - a poisoned pointer;
  - flags that bytes hide;
  - false sentences.
- **The lead's seam tests** found the gap defects (CS1).
- **Probes outside the suite** found regressions; PR §5 now says such a probe joins the suite.
- **The card** found the host defects that every simulator had hidden (CS2 §9).
- **The owner's once-over** found missing notices (CS4 obs 30).

### §4.5 The lead's own error record [R]

- **CS1**: committed a merge with an unresolved conflict and eight embedded worktrees; merged while a suite was running; carried a forbidden-files list from another repository; dispatched into a worktree of the wrong repository.
- **CS2**: a stale test binary on two merge gates; a guard's bound computed from the wrong example; a merge resolver with `;` where `&&` belonged; guessed stamps.
- **CS3**: 16 numbered errors, among them:
  - an unverified P0 facts sheet;
  - editing the tree under audit;
  - overclaiming to the owner (“disabled each check in turn”);
  - an applier that half-applied 14 amendments;
  - a workflow launched with its work list as a placeholder string;
  - certifying parcels with a checker that was wrong twice;
  - a grant and a rule that were each wrong;
  - a watch lapsed for 3 h 54 min;
  - records that disagree with the data;
  - cost misreported.
- **CS4**: no watch at first dispatch; a regression in its own runner; gates that fell to respellings; units dropped from figures.
- **V to W rounds**: each VALIDATION entry has a “lead's own slips” list. One example: “a two-part inline patch whose second half did not take, ‘measured’ by a stand-in” [VAL:15583-15585].
- **CS5**: the lead pushed eight of its own commits past the shared core with only its own gate, against the round's own plan, and a verifier then found gate-kind defects in three (CS5:110-125). Its first draft of the case study had 12 claims wrong or unsourced (CS5:12-14).
- **Step 6** [VAL:17172-17179]: the plan's first draft stated what the surveys did not support. A count was taken mid-merge, when `git ls-files` lists a conflicted file once per stage. A PowerShell `.Replace` matched nothing and said only “no change”; the docs check caught it.

**Implication [I].** The lead is the least-verified author by default (“nobody disconfirms the lead except the lead's own habit”, CS2 §5). The practice has moved to verifying the lead's plan (C1), its P0 (round 4), its commits (W4) and its records (every round V to W). An open-weight lead needs at least that much, plus harness checks on its mechanical operations: merges, pushes, stamps, watches.

## §5 Which rules exist because of the current harness, and which because of discipline

### §5.1 The current harness's primitives, as the record and the docs describe them

**Lead.** A long-running session. CS2 places round 2 in the desktop app [R]. The records of rounds 3 and 4 name tools that are Claude Code's (the Agent tool, `SendMessage`, Workflow calls), so the harness is taken to be Claude Code throughout [I, from D]. Round 3's lead was compacted automatically once, at 968,139 tokens [R CS3].

**Subagents (the Agent tool)** [D unless marked].

- Each has a per-agent model, a tool allowlist or denylist, and optional `isolation: worktree`.
- A worktree is “branched by default from your default branch rather than the parent session's HEAD”.
- An agent is resumed with `SendMessage`. Round 2's parcels were resumed this way, and a send-back cost 25 to 30 minutes with no re-brief [R CS2].
- Subagents may spawn subagents up to three layers deep by default.
- **Nested results, current behaviour.** In an interactive session, a subagent that launches background subagents waits for their results before it finishes. In non-interactive mode and the Agent SDK it does not wait, and a nested result arriving after its launcher ends “reports to your main conversation instead”.
- **Nested results, historical.** PR §3 records a parent finishing before its child, with the child's result reaching only the top-level session [R]; that is now the non-interactive behaviour.
- At most 20 subagents run at once by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).

**Dynamic workflows** [D]: JavaScript scripts calling `agent()`, `pipeline()` and `parallel()`.

- An agent can return a `schema`-validated result. A call fails after five attempts, configurable with `MAX_STRUCTURED_OUTPUT_RETRIES`.
- Up to 16 agents run at once by default.
- **Resumption.** A run is resumable by replay: completed agents return their saved results, and the first changed prompt plus everything after it runs again.
  - Replay works within the same session, in a backgrounded session, and after `claude --resume` when the saved results are found.
  - From v2.1.271, an agent that hits a subscription usage limit waits for the reset in interactive sessions instead of failing.
- `Date.now()` and `Math.random()` throw, so a relaunch repeats the same agents.
- No mid-run user input.
- **Caching.** Agent prompt cache: 5 min by default, configurable to 1 h. Matching agents share a cached prefix, with a stagger of up to 5,000 ms.

Round 3 ran all 145 agents through ten workflow calls [R]. Its record of that, which predates some of the behaviour above:

- workflow agents could not be messaged afterwards: “could not be resumed: No transcript found for agent ID”;
- a workflow reported when its slowest agent finished;
- completion notices were truncated;
- the journal was the reliable read, and it carried no times.

**Watches.** A background monitor whose output lines become notifications. In round 4 it was capped at 30 minutes and needed consent to run overnight, so the lead replaced it with a script [R CS4 obs 3, 17]. The 30-minute cap and the consent prompt come from the record, not checked against current docs.

**Scratchpad.** One session scratchpad, given to every subagent [R CS4 obs 9].

**Usage limits and transport.** HTTP 429 pauses [R CS4]; ECONNRESET mid-pass [R CS4]; 139 dropped connections in one session [R CS3]. Agents of one session did not survive into the next [R VAL:16507].

### §5.2 The table

Each row gives:

- the rule or incident, with its source;
- its **kind**:
  - **H**: a limit or default of the harness or service as it was;
  - **D**: a lapse of discipline that a harness can enforce;
  - **E**: an environment or framework trap;
- what happened under the current harness;
- the mechanism that replaces the rule.

“H#” points to the requirement in §6.

| # | kind | rule or incident | what happened | mechanism that replaces the rule | H# |
| --- | --- | --- | --- | --- | --- |
| 1 | D | “Stamps are substituted, not typed” (PR §4). In round 2 the lead (three times), P1, P2, P3, P4 and V4 each typed a guessed time, off by 3 to 90 min (CS2; PR §4); in round 3, 5 of 38 watched entries and 5 of the fixers' 6 stamps were still typed, and two guesses ran *behind* the clock (CS3) | the model writes the time | the ledger service stamps every append; every tool result carries wall-clock time | H4.2, H2.3 |
| 2 | H | the lead's watch expired at 30 min (CS4); lapsed for 3 h 54 min (CS3); covered 26% of the follow-ups' agent-active minutes; was never armed at first dispatch (CS4) | a watch is a background tool with a cap | durable subscriptions in the orchestrator: no expiry, a cursor per subscriber, nothing to “arm” | H5.1 |
| 3 | H | the watch needed consent, so it could not run overnight; a replacement script raced the expiring watch on shared temp files and reported a false “REWRITTEN” (CS4 obs 17) | consent prompts on background tools | the event bus is part of the harness, not a tool call that needs approval | H5.1 |
| 4 | H+D | watcher scripts collided on one filename in the shared scratch (PR §4) | agents write their own watchers | no agent-written watchers | H5.1 |
| 5 | H | every notification woke the lead and re-read its whole context: event-started turns were 33% of its cache reads for 10% of output; 20 single-call acknowledgements, 12 of them “nothing needed from me” (CS3) | every event is a turn | a wake policy: interrupt on `urgent/`, completions, gate verdicts and owner messages; digest the rest at wave boundaries and before merges; optional cheap pre-triage | H5.3, H5.4 |
| 6 | H | workflow agents could not be resumed; each send-back became a fresh fixer (57.6 min on average, fixer plus re-check) without the parcel's final report (CS3) | transcripts not addressable after a workflow | every agent persisted and resumable by id; a send-back resumes it; if resumption fails, a fixer brief is assembled automatically from the brief, final report, ledger file and defects | H1.3, H6.1 |
| 7 | H | a workflow reported when its slowest agent finished, leaving a ready verdict unreported for 1 h 51 min (CS3) | batched completion | a completion event per agent | H5.2 |
| 8 | H | completion notices truncated; the journal carried no times (CS3) | summary text | the full structured report stored and delivered with a short routing line; every event stamped | H6.4 |
| 9 | H (historical) | a parcel's subagents were invisible to the lead; a parent finished before its child and “promised” to fold in a result it could no longer collect; the child's 11 findings survived only because notices went to the top-level session (PR §3). Current docs: in interactive sessions a launching subagent now waits; in non-interactive and SDK modes it does not [D] | no parent/child accounting | spawns registered and written to the ledger automatically; a parent cannot submit while a child runs unless it declares the child outstanding, in every mode | H1.4 |
| 10 | H | every subagent got the lead's scratchpad, which held the Atlas key; P1 overwrote a lead file (CS4 obs 9) | one shared scratch | a scratch directory per agent; secrets only behind a broker tool, never in an agent-readable path | H3.2 |
| 11 | H+D | a parcel aimed at a second repository got a worktree of the session's repository (CS1); wave-2 worktrees were made from another session's commit 3b15d52 (CS3) | worktrees from the session checkout | a workspace factory taking (repository, base “at or after”, exact tip), with a pre-flight (remote, SHA, content probe) shown as the agent's first observation; a mismatch refuses the dispatch | H3.1 |
| 12 | E+D | two sessions committed in one checkout; per-ref CI concurrency cancelled the round's run, and “cancelled” read as nothing happening (CS3) | no session registry | a repository and session registry; CI “cancelled” treated as “not verified” | H8.5 |
| 13 | D | the lead merged while a suite was running, and a scripted checker read the new script against an old binary (CS1) | nothing stops it | a merge lock tied to running gate runs | H9.2 |
| 14 | D | conflicts resolved from what the merge printed; a marker committed; eight worktrees staged as embedded repositories (CS1); a resolver chain with `;` committed an unresolved merge (CS2); git hoisted a shared ending out of a conflict block (CS2 14:12) | raw git through a shell | a merge tool: the conflict set from git; each block shown with the lines after it; a marker scan; an allowlist of staged paths; refuses on any failure | H9.3 |
| 15 | D | “pushed” reported from an echo of local HEAD (HF FAILURE-MODES C1) | raw git push | a push tool that returns `git ls-remote` evidence | H9.4 |
| 16 | D | stale test binaries on two merge gates (CS2 11:50, the card day); “`make -C host all` does not build the test executables, on any host” (CLAUDE.md:102) | the agent runs whatever is on disk | the gate adapter records build time and hash for every binary a gate runs; a verdict on a binary older than its sources is refused | H7.2 |
| 17 | E | a single bench target exited 0 with failures (cocotb; PR §5, CS2 07:30); a background wrapper reported exit 0 over `Error 1` (PR §7) | exit codes surface as success | the gate adapter reads the runner's `report.jsonl` and VERDICT and asserts on log content, never on exit code alone | H7.1 |
| 18 | D | pasted gate output trusted; “A result quoted in a report is not a result” (HF §9) | free-text reports | claim-to-evidence: each MEASURED figure cites a tool-call id, and the harness checks that the output contains it | H6.2 |
| 19 | H | automatic compaction from 968,139 to 20,900 tokens mid-round; it survived because the send-backs were already launched and the summary carried the state (CS3) | compaction is opaque | the round state lives outside the model; a state card is re-injected after compaction or restart | H1.2, H2.5 |
| 20 | H | a usage limit stopped three agents mid-task, and they were resumed by a rule the lead wrote (CS4); agents of one session did not survive into the next and were re-dispatched from brief and resume note (W round). Workflow agents now wait out a usage limit in interactive sessions [D] | pauses are ad hoc | a pause/resume primitive: broadcast → commit WIP and write a resume note → snapshot → resume | H1.5 |
| 21 | H | 76% of parcels' and fixers' cache writes came after a pause of 5 min or more, since agents' caches last 5 min (CS3) | short cache lifetime | long-lived prefix caches when self-hosting; stable prompt-prefix ordering; scheduling aware of cache warmth | H2.7, §11 |
| 22 | H | at most 10 agents at once, with queueing of up to 19.6 min (CS3) | a fixed cap | a scheduler aware of provider rate limits and machine capacity | H8.2 |
| 23 | H | the cost was reported as 26.4 M “tokens”, which is the sum of final context sizes (CS3 lead error 16) | a harness figure easy to misread | accounting per request, separating input, cached, output and final context | H13.1 |
| 24 | D | the lead resumed P1 by message and wrote the ledger 10 min later; a verifier that reads only the ledger saw no answer (CS4 obs 17) | decisions travel by message | the lead's dispatch, resume, grant and ruling tools write the ledger entry first | H4.5 |
| 25 | D | “Verifiers watch the lead's channel only” (PR §4) | by instruction | an ACL in the ledger service, until the verifier's verdict is in | H4.4 |
| 26 | D | the lead edited the checker in the tree that 63 read-only agents (15 of them auditors) were reading, causing a false “FAILS at HEAD” (CS3) | the shared tree | auditors and verifiers read frozen SHAs or worktrees the lead never edits | H3.4 |
| 27 | D | a parcel's `docker kill $(docker ps -q …)` killed a sibling's benches (CS2 08:14); the rule held only once rewritten as the safe command | raw shell | process and container labels per agent; a kill tool limited to the agent's own labels | H8.4 |
| 28 | E | “The Linux box always means amd-arc-box”: a five-hour bitstream was built on WSL, with a third of the cores and no card (CLAUDE.md, 2026-09-12) | machines are prose | a machine registry with identity probes; tasks name the resource; a mismatch is refused | H8.1 |
| 29 | H | “The Bash tool mangles backslashes and tabs in long heredocs”; Python text mode flips files to CRLF (ROUND2.md; CS2 12:49) | raw shell | a write-file-then-run helper; line-ending checks on writes | H2.4 |
| 30 | E | “Never pipe a long make or test through `\| grep \| head -N` on this desktop”: it deadlocks at zero CPU (CLAUDE.md) | raw shell | the shell tool always captures to a log file and returns head, tail and path | H2.4 |
| 31 | D | paths, functions or runner stages named in briefs that did not exist: two functions in round 2; an `--only orbits` stage (V round); 4 of 6 forbidden files from another repository (CS1); 57 brief-error items (CS3) | briefs are free text | a brief linter: paths exist at the base; named functions grep; stages are in `run.sh --list`; commands dry-run where possible; the ownership list is diffed against the seam's own comments | H10.5 |
| 32 | D | a lesson the owner has not adopted “travels in the lead's memory, and only there” (CS4 obs 32) | memory | a policy store with adoption status; briefs and verifier lists compiled from it | H10.1, H10.4 |
| 33 | D | verifiers' side notes “had nowhere to go”; at least nine still open at the round's end, made true the next morning (CS3 postscript) | free text | a side-note queue; a round cannot close with untriaged notes | H6.5 |
| 34 | D | records disagreed with their data in at least five places (CS3); units dropped from figures (“units of u”, “(relative)”) (CS4 obs 20, 28) | the lead writes from memory | a records compiler from structured data; figures linked to runs; a verifier on the draft | H11.1-H11.3 |
| 35 | D | “what I did not do” is a claim: a verifier's clone left inside the lead's tree was found only by `git status` (CS4 obs 4) | none | a workspace audit after every agent: unexpected files, branches and processes reported | H3.5 |

**The pattern [I].**

- Sixteen rows (kinds H, H+D and H (historical)) are limits or defaults of the harness as it was. Several have since moved in Claude Code's docs (rows 9 and 20). The rest are lapses of discipline or environment traps.
- In both groups the failure is *mechanical*, not a matter of judgement: stamps, watches, notifications, resumption, workspaces, merges, pushes, binaries, scratch, ACLs. Frontier models broke these rules repeatedly despite having them in writing, and open-weight models will not do better from text. These belong in the harness.
- What remains for prompts is the judgement content: what the trap is, what the control must be, what to attack.

**Recurrence across rounds 1-5** [R, counted from CS1-CS5, METHOD.md and its history, and round 5's archived ledger; added 2026-10-02]. Writing a rule down did not stop any of these:

| failure | rounds, of 5 | where |
| --- | --- | --- |
| a gate or control that could not fail, the lead's included | all 5 | CS1:55; CS2:69; CS3:248; CS4:77, 82; CS5:216-225 |
| a brief that was wrong: a premise unchecked, or content it should not carry | all 5 | CS1:38, 242; CS2:61, 392; CS3:287, 513; CS4:76, 82; CS5:206-208 (the owner's personal data in a brief) |
| a collision in a shared environment: a scratch file, containers, a watcher's file name, a checkout, processes left running | all 5 | M:409-418 and commit `6845a57` (round 1: “Found on the mechanism first use”); CS2:71; CS3:456; CS4:80, 102; CS5:250-258 |
| a typed timestamp | 4 (rounds 2-5) | CS2:230-239; CS3:355-362; CS4:112; round 5's archived lead.md:831 (a time typed in an entry's body, which the lead flagged itself) |
| the lead's own work reaching main with no verifier | 4 (rounds 2-5) | CS2:124, 277; CS3:373; CS4:88-97; CS5:110-125 |
| a record that overclaims, or disagrees with its data | 4 (rounds 2-5) | CS2:233; CS3:153, 380; CS4:118, 217; CS5:12-14, 226 |
| the lead's watch missing, late or lapsed | 3 (rounds 1, 3, 4), and agents' watches in round 5 | M:448-453 (round 1: “the lead had no watcher at all”); CS3:172, 187; CS4:65, 70, 102; CS5:250-258 |
| a wrong number or definition propagating | 2 (rounds 2, 4) | CS2:108; CS4:238 |
| a worktree of the wrong repository or base | 2 (rounds 1, 3) | CS1:184; CS3:463 |
| a tree changed while a suite or an audit read it | 2 (rounds 1, 3) | CS1:236; CS3:152, 427 |
| an unresolved merge committed | 2 (rounds 1, 2) | CS1:232; CS2:115 |
| a rule written as a list of spellings, then walked past | 2 (rounds 4, 5) | CS4:144; CS5:101 |

Each count is a lower bound, since a case study records what its author noticed. The first six rows are the strongest evidence in this document for moving rules out of prompts and into mechanisms.

## §6 Harness requirements

Format: **ID — requirement.** *Source.* **Acceptance**: the test that must fail if the requirement is broken, in HonestFramework's “a gate you have not watched fail is not a gate” form.

### At a glance: how H1–H17 connect

```text
Diagram (in the doc): "Every agent acts through harness services it cannot route around". Five layers, top to bottom.
L1  Owner --> H14 Owner interface --> H10 Policy store (standing rules as data; authority matrix; brief linter)
    H14 <--> Orchestrator : requests and approvals; H16: each recommendation carries its derivation and a second opinion, and overrides feed H10
    H10  --> Orchestrator : rules and compiled briefs
L2  Orchestrator, a non-LLM process that owns the round: H1 Round state | H5 Events | H15 Model routing | H13 Telemetry
    Orchestrator --> Agents : dispatch, wake, resume
    Agents --> Orchestrator : completions and verdicts
L3  Agents on any model, run by H2 (role-scoped tools, resumable): Lead | Parcels | Verifiers | Other roles (fixers, re-checks, auditors, triage)
    Agents --> Services : every effect is a tool call
    Services --> Agents : events, routed by For: and role
L4  Services (every effect passes through one of these): H3 Workspaces | H4 Ledger | H8 Resources | H9 Merge queue | H6 Reports and claims | H7 Gates | H17 Gate integrity (protected surfaces; the ratchet)
    Services --> Project repository : promoted by H9.1 (main moves only by H9.1; VALIDATION.md append-only)
    Services --> H11 Records compiler : ledger, reports, runs
L5  H11 Records compiler --> H12 Improvement loop --> H10 Policy store : typed proposals; the owner adopts
```

The owner's decisions become policy that the orchestrator compiles into briefs, and agents reach the repository only through the services (L4). Retrospectives send proposals back up to the policy store.

### H1 Orchestrator and round state (a non-LLM process)

- **H1.1 — A round is a persisted state machine.**
  - States: `proposed → plan-verified → approved → p0 → p0-verified → wave-n (dispatched / merging) → build-done → hardware → records → retrospective → closed`, plus `paused` overlaying any state.
  - Each transition records time, actor and evidence references.
  - *Source*: §3.2. CS2 and CS4 rebuilt their timelines from commit times and file mtimes because nothing recorded the transitions. `plan-verified`: the C round's verifier-C1 reviewed two drafts of the plan before any code (VAL:15649-15652).
  - **Acceptance**: kill and restart the harness mid-wave; the state matches git and the ledger; a transition without evidence is refused.
- **H1.2 — The state card.**
  - A compact, generated summary of the round: plan reference; base and tips; agents with role, status and worktree; open items (outstanding children, pending send-backs, untriaged side notes, owner decisions); merge queue; last verdicts; standing rules in force.
  - Injected into the lead's context at turn 0, after any compaction, and on resume.
  - *Source*: CS3's compaction; the W round's loss of a session.
  - **Acceptance**: compact the lead deliberately; its next action is consistent with the card (a scripted probe question).
- **H1.3 — Every agent is resumable by id**, across harness restarts and model or provider failover where possible. Transcripts, tool state and working directory are persisted.
  - A send-back resumes the agent with the verifier's defects appended.
  - If resumption is impossible, a fixer brief is built from the brief, the final report, the ledger file, the defects and the worktree. Round 3's fixers lacked the final report.
  - *Source*: rows 6 and 20 of §5.
  - **Acceptance**: a resume after a restart succeeds; when one is forced to fail, the fixer brief contains all five inputs.
- **H1.4 — Parent/child accounting.**
  - Every spawn is registered and written to the ledger automatically with its parent.
  - A parent's `report_submit` is refused while a child runs, unless the report declares the child outstanding.
  - An outstanding child is an open item on the state card.
  - *Source*: PR §3.
  - **Acceptance**: a parent that tries to submit with a running child is refused.
- **H1.5 — A pause/resume primitive.**
  - `pause(reason, deadline)` makes each agent commit WIP on its own branch and write a resume note (schema in §7) before the deadline. Then the harness snapshots.
  - `resume()` restores each agent, or re-dispatches it from brief plus resume note, with a forced full ledger read.
  - *Source*: the W round's pause at 14:19; CS4 obs 12.
  - **Acceptance**: pause during active edits; after resume, no uncommitted work is lost, and each agent's first action reads the ledger.
- **H1.6 — Deterministic, replayable orchestration.**
  - Fan-out scripts (sweeps, triage rounds, pipelines of parcel, verifier, fixer and re-check) log their inputs. Hidden clock and randomness are banned, as in Claude Code's workflow runtime [D].
  - A relaunch replays completed agents' results.
  - Per round, decide whether the lead sits between verdict and fix (CS3 proposal) or the pipeline runs per parcel.
  - **Acceptance**: relaunch an unchanged script; no completed agent runs again.

### H2 Agent runtime (model-agnostic)

- **H2.1 — Canonical item store and adapters.**
  - The canonical store is TC §7.1. Adapters cover Chat Completions, Responses/Open Responses, Anthropic Messages and raw templates.
  - Reasoning is preserved per family (TC §7.5).
  - Each (model, provider, version) is pinned and passes the tool-call conformance suite before use (TC §7.8).
  - **Acceptance**: a model that fails conformance cannot be assigned a role.
- **H2.2 — Role-scoped toolsets and permissions, enforced in the tools.** Toolsets by role:

| role | toolset |
| --- | --- |
| parcel | read, write and edit inside its worktree; shell; git local only; `ledger_append(self)`; `urgent_post`; `request_run`; `report_submit` |
| verifier | read-only mount of the parcel tip; writable scratch copies for plants; shell; gates; `verdict_submit`; ledger reads limited by ACL |
| lead | adds `dispatch`, `send_back`, `merge_stage`, `promote_main`, `push`, `rule`/`grant`, `request_owner_decision`, `pause_all`, `record_draft` |
| auditor | read-only |
| triage | read-only plus classification output |

**H2.2 acceptance**: a verifier's write to a tracked file is refused by the tool, not the prompt.

- **H2.3 — Time injection.** Every tool result header carries wall-clock time (UTC and local) and the agent's elapsed time. Ledger and report stamps are filled by the harness.
  - **Acceptance**: a model-typed stamp in an entry is overwritten or flagged.
- **H2.4 — Shell hygiene built in.**
  - Every command's stdout and stderr go to a per-call log, and the tool returns head, tail, path and exit code.
  - `pipefail` is on.
  - A “write a script file, then run it” path replaces heredocs.
  - Writes are checked for line endings.
  - Each machine has a profile: MSYS `/tmp` versus Windows Temp, `MSYS_NO_PATHCONV`, `TMP`/`TEMP` for MinGW make, `.exe` names.
  - *Source*: CLAUDE.md; ROUND2.md “Working rules”; round 3's urgent messages (`lead-hostmake-tmp`, `lead-test-exe`).
  - **Acceptance**: a long build piped through `head` does not hang the tool; CRLF introduced by a write is reported.
- **H2.5 — Context budgets.**
  - Each role has a cap. Tool output is truncated, with the full text spilled to a file.
  - Compaction preserves the brief, the ownership list, the ledger cursor, open items and the state card.
  - A “full read” of the ledger is forced after compaction or resume.
  - *Source*: §4.3 envelopes; CS3 compaction.
  - **Acceptance**: an agent compacted at the cap keeps its ownership list (a probe edit to a forbidden file is still refused and still disclosed).
- **H2.6 — Resilient transport.** Backoff and retry on 429 and 5xx; resume a turn interrupted mid-stream; a fallback provider for the same model where allowed.
  - **Acceptance**: inject an ECONNRESET mid-tool-call; the agent continues and the tool call is not duplicated, which matters for anything not idempotent.
- **H2.7 — Cache-aware prompt layout.**
  - Order the prompt as system, then tools, then policies, then brief, then rolling context, so prefixes are shared across agents of a role.
  - Self-hosted: prefix caching on (vLLM's automatic prefix caching or SGLang's RadixAttention) with retention sized to the gaps between turns.
  - Hosted: record the provider's cache semantics.
  - *Source*: round 2's 99% cache hit and 3.5 B cache-read tokens; round 3's 76% of writes after 5-minute gaps.

### H3 Workspace factory

- **H3.1 — Worktree or clone of the named repository.**
  - Given URL or path, base “at or after”, and exact tip.
  - Pre-flight: `git remote -v`, `git log -1`, `git merge-base --is-ancestor <base> HEAD`, and a content probe (a string only the intended base contains), shown as the agent's first observation. Any mismatch refuses the dispatch.
  - For a second repository, a fresh clone, never the owner's checkout (CS4 P2).
  - **Acceptance**: dispatch with the wrong URL or a stale base is refused before the agent's first turn.
- **H3.2 — Per-agent scratch directories; secrets behind a broker.**
  - Credentials such as a platform API key are never written to a path any agent can read.
  - An agent uses a credential only through a tool that does the operation, for example `submit_device_job(...)`, with metering.
  - **Acceptance**: grep every agent-visible path for the secret: no hit; an agent reading another's scratch is refused.
- **H3.3 — Tree setup steps** from the brief (“how to make the tree buildable”) are run or checked before handover: for example generated vector sets, submodules left uninitialised on purpose, or the lead's shared build pointed to by `QF_CFT_ROOT`.
- **H3.4 — Frozen audit inputs.** Auditors, verifiers and reviewers read a committed SHA. The lead's working tree is never the tree under audit.
  - **Acceptance**: an uncommitted lead edit is invisible to an auditor.
- **H3.5 — Post-agent workspace audit.** After an agent finishes, report unexpected files, clones, branches, background processes and containers under its labels.
  - Cleanup asserts that nothing is unpushed or unmerged before removal (CS4's close).

### H4 Ledger service

- **H4.1 — Append-only files, one per author**, written through an API (`append(author=self)`). There is no edit and no delete.
  - A correction is an append with `corrects: <entry-id>`; the service renders a back-link under the corrected entry (PR §4).
  - **Acceptance**: an attempt to write another author's file, or to rewrite one's own earlier entry, is refused.
- **H4.2 — Entry schema** (§7): id, harness stamp, author, headline, `for`, `measured[]`, `believed[]`, refs (commits, run ids, tool-call ids).
  - The rendering stays the human-readable markdown the README describes.
  - **Acceptance**: an entry with neither measured nor believed lines is refused.
- **H4.3 — `urgent/`**: one message per file, created atomically, first line the headline, a `For:` line. The service delivers each to its subscribers.
  - *Practice, 2026-10-02* [R]: cft-fp256's rounds from the audit round (2026-09-29) on dropped `urgent/`. The lead's messages go through the agent runtime (SendMessage) and are recorded in the lead's ledger file (§3.5).
  - Either channel meets H4.3 when H4.5 holds: the message is in the ledger before it is delivered. An escalation from an agent to the lead needs the same.
- **H4.4 — ACLs.**
  - Parcels read everything.
  - Verifiers read only the lead's file, `urgent/` and environment entries until they submit a verdict.
  - The lead reads everything.
  - **Acceptance**: a verifier's read of a parcel's file before its verdict is refused.
- **H4.5 — The lead's decisions go in the ledger first.** `dispatch`, `send_back`, `grant`, `rule` and `resume` each write their ledger entry before the message is delivered.
- **H4.6 — Archive with timestamps in the content**, not only in mtimes. Round 3's in-project copy reset every mtime. The archive happens at the round's end, after durable items are folded into the project's records.
- **H4.7 — Seeding.** A new ledger is seeded from the policy store with environment traps, standing rules and the base SHAs, as round 2's was by hand (ROUND2.md “The ledger”).

### H5 Events and the lead's wake policy

- **H5.1 — Durable subscriptions.** No expiry, a cursor per subscriber, and a replay of missed events on reconnect. Nothing for an agent to “arm”.
  - **Acceptance**: drop a subscriber for an hour; on reconnect it receives every missed event exactly once.
- **H5.2 — Routing.** Events go by `For:` and by role. Each agent completion, verdict and gate verdict is its own event, never batched behind the slowest sibling.
- **H5.3 — The lead's interrupt set.** The lead is woken by:
  - `urgent/`;
  - agent completions and verdicts;
  - gate verdicts;
  - owner messages;
  - hold points reached.

  Everything else goes into a digest delivered at wave boundaries, before every merge, and on a timer. Before each merge the lead does a full read of every author file (CS3's proposal, keeping PR §4's cross-parcel view).
  - **Acceptance**: 50 non-urgent entries cause 0 wake-ups before the digest; 1 urgent message wakes the lead within the configured latency.
- **H5.4 — Optional pre-triage.** Rules or a small model classify events as “ack only”, “fold into next brief” or “act now”. “Ack only” never wakes the lead [I].

### H6 Reports, verdicts and claims

- **H6.1 — Schema-validated final reports by role** (§7).
  - **Parcel**:
    - files changed by path;
    - gate lines quoted with run ids;
    - the named control with both outcomes and run ids;
    - brief errors (required; “none found” must be explicit);
    - boundary crossings with reasons;
    - outstanding children;
    - side notes;
    - a resume note.
  - **Verifier**:
    - per numbered item: commands run (tool-call ids), observation, and a verdict of `confirmed`, `defect` or `not determined`;
    - each defect with a concrete failure scenario and a class of `regression`, `wrong-answer`, `gate-gap`, `limit` or `sentence`;
    - an “anything else” section;
    - READY or NOT READY under the brief's stated standard (“a gate, or a stated limit”, CS4 obs 15);
    - the instruments used.
  - *Source*: `templates/brief.md`, `templates/verifier.md`, and the report schemas used in round 3.
  - **Acceptance**: a report missing the control's failing run is refused.
- **H6.2 — Claim-to-evidence checking** [I, from HF §5 and FAILURE-MODES A1/C3]. Every number or verdict marked MEASURED must cite tool-call ids. The harness checks:
  - (a) the cited output contains the number or line;
  - (b) the command ran after the last build of the artifact it exercises (build-time comparison);
  - (c) the run's tree hash equals the tip being reported on.

  Failures are attached to the report as findings, not silently corrected.
  - **Acceptance**: plant “PASS: 1 bench(es)” in a report citing a run whose log has `TESTS=3 PASS=0 FAIL=3`; it is flagged.
- **H6.3 — Control completeness.** A named negative control must show a failing run and a passing run, each with an id. “Described but not run is worth nothing” (PR §5).
- **H6.4 — Full delivery.** The full report is stored. The lead gets a routing line plus a link and reads the full text on demand, never a truncated summary.
- **H6.5 — Side-note queue.** Every side note in a report or verdict becomes an item with owner, class and state. Round close requires each item triaged: made true, filed as a known limit, or dismissed with a reason.
  - *Source*: CS3's sweep triaged 324 items (the verifiers' 314 side notes plus the critic's findings) into 51 findings, 41 of them drawing on the side notes. Its follow-ups left at least 9 open, made true the next morning.

### H7 Gate integration

- **H7.1 — A runner adapter for the project's front door** (cft-fp256's `verify/run.sh`: 46 stages at `ded90d8`, 50 at `4190a47`, with the quick and gate budgets at 31 and 43).
  - It handles run, `--budget`, `--only`, `--resume`, and `--require-all`.
  - It parses `report.jsonl` and the VERDICT line, including inner skips and skips named with reasons.
  - It holds the run id (timestamp plus commit).
  - It never uses exit codes alone.
  - **Acceptance**: a stage whose log says `Error 1` with exit 0 gets a harness verdict of FAIL; a typo in `--only` is refused (runner behaviour; HF FAILURE-MODES D1).
- **H7.2 — Build provenance in every verdict.** Record the path, hash and build time of each executable a gate runs, and the linkage where it matters (`ldd host/device-test | grep xrt`, CLAUDE.md trap 2).
  - Refuse a verdict whose binary predates the sources it depends on, or that links the wrong backend.
  - **Acceptance**: swap in a binary from an older build; the verdict is refused.
- **H7.3 — Run records keyed by (tree hash, stage, machine identity, toolchain).**
  - Verifiers may reuse identical-input runs and re-run from clean what they doubt (CS3 proposal).
  - The authoritative full run never consults reuse (HF FAILURE-MODES A3).
  - **Acceptance**: change a header file; reuse is refused for every stage that compiles it.
- **H7.4 — The budget covers the diff.** Map paths to stages (for example `bindings/node/**` → `node`; `rtl/**` → `sim`, `simmc`, `lint`, `formal`). Before trusting a budget at a merge, assert the selected stages cover the merged diff's areas.
  - *Source*: CS3: the budget left out `node` and `wasm` after a parcel changed `bindings/node`.
- **H7.5 — A registry of negative controls.** Each gate's planted control can be run on demand. A “controls only” pass proves the runner can still say no, at the start of each round and after any runner change.
- **H7.6 — Long runs are the lead's.** Parcels and verifiers submit long runs through `request_run(stages, tree, machine)`. The broker schedules them and the result arrives as an event (the R and A round rule).
- **H7.7 — A verdict composed across machines and commits** (added 2026-10-02).
  - **The box does not pass every stage alone** [R]. At step 6's merge its gate passed with 8 stages skipped by name and 4 inner skips (VAL:17119-17122).
  - In the language round, a commit's verdict was composed from the box's gate plus stages run on the desktop or in WSL (VAL:16794-16801).
    - Some of those stages ran at 30ee0fd and counted toward a5ffac7's verdict.
    - The record's guard was an empty `git diff 80abee5 a5ffac7` under the paths they read (VAL:16990-16994). That is a diff from a later commit than the one they ran at. Between 30ee0fd and 80abee5 a comment-only change to `host/tools/cft-asm.c` intervened (`39e7389`).
  - **The harness composes one verdict per commit** from per-machine run records (H7.3), and says which machine and which commit ran each stage.
    - A stage run at an earlier commit counts only when what it executes is unchanged since the commit it ran at: its built artifacts hash the same, or, where it executes sources, no path it reads changed. Keying on artifacts lets a comment-only change through without a second rule (HF FAILURE-MODES A3).
    - A stage that ran nowhere counts as a skip of the composite, by name.
  - **Acceptance**:
    - a composite in which one stage ran on no machine reports that stage as skipped, and fails under `--require-all`;
    - a stage reused across a change to what it executes is refused;
    - a stage reused across a comment-only source change, whose artifacts hash the same, is accepted.

### H8 Resource broker

- **H8.1 — Machine registry with identity probes**: hostname, cores, RAM, OS or WSL distro, card present (`02:00.0`), toolchain versions (Vitis 2022.2 paths, XRT 2.19.194). Tasks declare the resource they need; a mismatch is refused.
  - *Source*: CLAUDE.md “The machines, and the one that gets confused”.
  - **Acceptance**: a card job submitted to `cft2204` is refused.
- **H8.2 — Capacity and etiquette per machine.**
  - Memory budgets: “one heavy link at a time”; a quad `place_design` wants 25 to 30 GB.
  - `nice` by default, **set by the broker, not by the agent**. In the C round, an agent's own Windows priority call failed silently and its runs went at normal priority. One probe committed about 99 GB before it was stopped (VAL:15795-15796), and a verifier's probe in the language round reached 44 GB for about two minutes (“It was niced, but memory is not”, VAL:17028). The broker applies priority and memory limits (job objects or cgroups) to everything an agent starts.
  - An owner-in-use mode: “The desktop is Logan's to use: one run at a time, niced, and `docker ps` first” (ROADMAP.md:4049).
  - Provider rate limits and concurrency.
- **H8.3 — Long builds as reserved or metered jobs.** A bitstream link takes 5 to 8 h (round 2: the quad first missed timing after 359 min, then closed after 468 min). Recipes are refused if they use a dangerous default (`KERNEL_FREQ` below the floor, CLAUDE.md trap 1). The project already enforces this; the broker adds a schema check.
- **H8.4 — Ownership of processes and containers.** Everything an agent starts carries its label. The kill and stop tools act only on the agent's own labels.
  - **Acceptance**: an agent's attempt to kill a sibling's container is refused.
- **H8.5 — Session and repository registry.** Detect other sessions committing in the same checkout. Treat a CI run reported “cancelled” as not verified, and tell the lead.
- **H8.6 — Finite external resources** (device-job quotas, API keys with expiry) are metered and reservable, governed by owner rules. Example: CS4's last five Atlas jobs, which the lead asked before spending.

### H9 Merge queue and promotion

- **H9.1 — Promotion rule.** Main moves only by fast-forward to a staging commit for which all of the following hold:
  - (a) a gate verdict at that exact commit on the declared build host, log read, that is PASS, or FAIL only on stages whose failure is reproduced at the base commit (run ids for both) and filed as a known limit or task. Main moved on exactly that in round 3 (`lang-rust`, CS3:439-442) and in the A round (`transcend` and `mpfr`, both reproduced at main, VAL:16288-16303);
  - (b) a verifier READY for each parcel in the batch, or a recorded exemption with its reason;
  - (c) a seam test present when the batch spans two or more parcels' areas;
  - (d) no conflict markers;
  - (e) staged paths within the expected set (no embedded repositories);
  - (f) commit messages checked against `git show --stat` (the V round's “check `git show --stat` against the message before believing a commit”);
  - (g) no reserved action in the diff without approval (H10.2).
  - *Source*: PR §7; CS1 to CS3.
  - **Acceptance**: try to promote a commit whose verdict was at a different SHA; refused.
- **H9.2 — Merge lock.** No merge into a tree while any gate run reads it.
- **H9.3 — Conflict tool.** The conflict set comes from git (`--diff-filter=U`). Each block is shown with the lines after it. The tool refuses to commit with markers or with unexpected paths staged. After each merge, it re-makes the merge with `git merge-tree` and diffs it against the committed result, so every hand resolution is visible and listed. Verifiers R6, A4 and W6 did this by hand [R VAL:16124-16129, 16308, 16602-16605].
- **H9.4 — Push tool.** It returns the `git ls-remote` SHA. A push to a second repository, a deploying branch, or a deletion of a remote branch is a reserved action (H10.2).
- **H9.5 — A seam changed mid-round** is checked against every open parcel branch at once, before any of them merges (CS4 obs 11).
- **H9.6 — Batching** is allowed with a declared trade and a bisection plan (PR §8). A merge with no RTL in its diff gets no RTL suite, and the record says so (PR §7).
- **H9.7 — A trial merge may be prepared while the verifier works**; the verdict still gates main (CS4 obs 19).

### H10 Policy store and authority matrix

- **H10.1 — Standing rules as data.** Each rule has:
  - id, text, the owner's words, date;
  - scope (project, area or role);
  - **enforcement level**: `brief-text`, `ledger-seed`, `harness-check`, `project-gate`, `seam-refusal`;
  - status: proposed, adopted, retired;
  - provenance (case-study item, VALIDATION line);
  - a review date.

  §3.3's rules are the seed set. A policy may be a single decision, or a **decision procedure** that settles a class of questions. The 2026-09-29 rule is one: IEEE 754 first, then RISC-V practice, then “whatever approach aligns best with the current systems”. Procedures are worth more per owner-minute, and the approval queue should offer to turn a repeated question into one (H10.3).
- **H10.2 — Reserved actions with required authority.** A default matrix, editable by the owner:

| action class | authority |
| --- | --- |
| promote to main | standards (H9.1) |
| push to another repository | owner (a standing grant is possible) |
| deploy a published site | owner (in round 3 it happened before the owner could see it) |
| delete a remote branch | owner |
| card or hardware run | owner, or a policy for a recurring type |
| long build | policy |
| spend a finite external resource | owner |
| change how results are counted (skip rules, verdict rules) | owner (round 3's lead set one mid-round) |
| ABI or contract change | owner |
| new work order | owner, or a pre-approved queue |
| method reversal | owner |

Additions (reinforcement or extension) may be delegated as autonomy rises (§9).

- **H10.3 — Approval queue.**
  - Questions carry options, a default and a deadline, like ROUND2.md's “Decisions this plan leaves to Logan”.
  - Hold points come from the plan or the owner (“Hold before starting Step 3”).
  - When a standing rule covers a question, it is auto-answered and logged with the rule id; the lead does not wait.
  - **Acceptance**: a question covered by a standing rule never reaches the owner; a reserved action without approval is blocked at the tool.
- **H10.4 — Compiled briefs and verifier lists.**
  - Templates (ParcelRound's) plus the plan's parcel section plus every applicable policy at `brief-text` or above, plus the ledger's wave-boundary fold.
  - The method version is recorded in each brief.
- **H10.5 — Brief linter**, run before dispatch:
  - every path exists at the base;
  - every named function, register and symbol greps;
  - every runner stage named is in `run.sh --list`;
  - the forbidden-file list is diffed against the seam's own comments (the CSR guard contradiction, CS2 06:32);
  - the control is named by “the property that makes it bite” (CS4 obs 8), and if it is runnable before dispatch, it is run.
  - **Acceptance**: a brief naming a missing function is refused, with the grep that failed.

### H11 Records compiler

- **H11.1 — Drafts in the project's own record format** from structured data: VALIDATION's Why, per-parcel results, the lead's own, the front door, known limits, the lead's slips, load and machine; ROADMAP's “Built” and debts; the ledger fold.
- **H11.2 — Figure provenance.** Every figure links to a run or tool call and carries its unit and definition. A figure copied from a report without its definition is re-measured or labelled (CS4 obs 20 and 28).
- **H11.3 — A verifier on the record before commit.** Practised in every round from V to W (V10, C8, R6, A4, F4, W6) [R VAL:15599, 15817-15819, 16124-16129, 16308-16311, 16356, 16602], and proposed in CS3. Its findings are restated at the commit and recorded as the lead's slips.
- **H11.4 — Closed entries are immutable.** A pre-commit or gate check on `docs/VALIDATION.md`: a commit may append, or revise the newest still-open entry while it is being written, but must not change any closed entry. Corrections to a closed entry are new dated entries, as the 2026-09-25 corrections entry did [R VAL:14565].
  - *Source*: in practice, 35 of the 216 commits touching VALIDATION.md delete lines. In 34 of them the deletions fall inside the open entry; one (d9b5ac4, 2026-09-04) edits an older one [R, per the verifier's count]. HF §7 says “Nothing in it is ever edited to agree with a later belief” and “Separate the live claim from the historical one in the layout”. It does not say a diff may only append.
- **H11.5 — Notices and licences gate** against dependencies added during a round (CS4 obs 30) [I].

### H12 Method-improvement loop

- **H12.1 — Retrospective generator.**
  - From the state machine, ledger, transcripts and git: timeline, catches, cost and the lead's errors.
  - Run as CS3 did: gatherers, then a draft, then checkers that did not write it, then re-checks, repeated until the findings shrink (CS3 stopped at 69, 29, 6).
- **H12.2 — Typed proposals** (new, reinforcement, extension, relaxation, reversal) filed to the policy store as `proposed`, with evidence links. Adoption is the owner's, or delegated by class at higher autonomy levels.
- **H12.3 — Method versioning.** Each round pins the method version. Adopted rules flow into templates (ParcelRound's templates were last changed 2026-09-11 and lack, for example, the stamp rule [R]).

### H13 Cost and telemetry

- **H13.1** — Per request: model (the one the response reports, beside the one dispatched; H15.1), provider, input, cached-input and output tokens, latency, tool calls. Per agent and per role. Processed figures kept separate from “final context” figures.
- **H13.2** — Wall-clock accounting: agent-active, waiting on gates, waiting on the owner, idle. CS3's “Where the wall clock went” was rebuilt by hand.
- **H13.3** — The checking share per round: verifiers, re-checks, reviewers, with its denominator stated. Observed from 32% (round 4's second round, the verifier's share of the round's output) to 52.5% (round 3, every checking role, share of the harness figure), by different measures [R CS2-CS4].
- **H13.4** — When self-hosted: GPU-seconds, prefix-cache hit rate, tokens per second per role.

### H14 Owner interface

- **H14.1** — Plan approval against the committed plan of record, with its owner-decisions section; an ordered queue with hold points.
- **H14.2** — Notifications by severity (reserved action pending, hold point reached, round closed, defect on main); digests; pause and resume; “what happened while I was away”, from the state card, ledger and records.
- **H14.3** — **Kickoff pre-commitments**: what the owner wants to see before it happens, settled at the start (CS3 proposal: deploys, remote deletions, counting changes).
- **H14.4** — Owner catches are logged as events with a class, so each can become a harness check (the §3.4 list).

### H15 Model routing and qualification

- **H15.1 — Role-to-model assignment** with fallbacks, pinned per (model, provider, version, **effort or reasoning settings**), gated by conformance (H2.1) and by role qualification (§8). Effort is part of the pin: round 3's lead and agents ran “claude-opus-5-5 at xhigh effort” [R CS3].
  - **The pin is checked against what each response reports, not against the dispatch** [R, added 2026-10-02].
    - In round 5, the owner's direction named Sonnet “(5.5 is current)” (loganw.dev SPEC.md decision 24). The dispatch named only `model: "sonnet"` (round 5's archived lead.md:275), and every Sonnet agent's transcript records `claude-sonnet-5` (CS5:316-318). What the owner asked for was not what ran, and the dispatch could not have said so.
    - verifier-seam is listed on Opus 5.5, but 10 of its 342 messages, from 01:19 to 01:26, record `claude-opus-4-8`. Its READY at 01:26 falls in that stretch (CS5:319-321).
    - CS5 proposes taking each agent's model from its transcript, not from its dispatch (CS5:385-386).
  - **Acceptance**: a response whose reported model differs from the pin is flagged in the run record. A verdict it contributed to cannot satisfy H9.1(b) until it is re-checked under the pinned model.
- **H15.2 — Qualification suites** built from the project's own history (§8.2). Scores are recorded with date, model, provider, harness version and prompt version. Re-run when any of them changes (HF ADOPTING step 8; HF §9).
- **H15.3 — Independence** [I]. By default a verifier's model family differs from its parcel's. Measure the correlation of misses by sometimes running a second verifier from the parcel's own family on the same item.
  - **First evidence, 2026-10-01/02** [R].
    - GPT-6.1 Sol Max, outside the Claude family, wrote cft-fp256's challenge suite from the language document, the sources and one bundle. It wrote the hard-workload pack from those plus the results Claude returned (§2.2).
    - Its suite found one real defect, of a class two of the round's own verifiers also found by other roads (VAL:16852-16856). It then audited the results returned to it (VAL:16911-16912).
    - Its oracle was independent: it imports nothing of the repository (WR:47-52). The rest was partly not, because the pack's adapters were based on an adapter from the results returned to it (`golden_adapter.py:3`).
  - So record every input a foreign checker receives. Independence is a property of the inputs as well as the family (HF §1).
- **H15.4 — Live controls on the verifier** [I, from HF §9 and the WITH-PARCELROUND section “Control the verifier”].
  - Each round, the harness plants a fault, in the shapes `templates/verifier.md` names, in a copy of one parcel's diff, and adds it to a verifier's queue disguised as an ordinary verification task. The key is withheld under the three-commit protocol (HF §9).
  - A verifier that misses a plant is quarantined from READY verdicts until requalified.
  - **Acceptance**: the plant itself is watched to be detectable by the strongest available verifier before use.
  - **Owner adoption required.** In round 3 the owner declined planted faults on the auditors (“a comprehensive sweep of whats there, not new sourced data”; CS3), and the record says its verdict rates are “suggestive, not a detection rate” (VAL:14296-14299). Live plants are therefore a policy to propose, not a default.
  - In round 5 the owner allowed plants, “light” (loganw.dev SPEC.md decision 20), and two verifiers each caught 2 of 2 (CS5:158-168) [R].
  - A plant can be a task as well as a diff: an infeasible task, whose honest outcome is a refusal or a limit, tests a parcel's honesty under difficulty (H17.5, QS9) [I].

### H16 Steering: recommendations, intent and overrides (added 2026-10-02)

The owner's aim [O 2026-10-02], verbatim: “an ideal outcome is a system in which the core principles, once hardened into the system itself, can effectively steer the model in the authors original intentions without their significant feedback and more importantly without cheating to still pass after things get harder.” H16 covers the steering and H17 the cheating. §9.5 and §9.6 give the reasoning.

- **H16.1 — Every recommendation carries its derivation.**
  - A question put to the owner (H10.3) lists its options and marks one as the default.
  - For the default, it states what it was derived from: policy ids (H10.1), the owner's earlier words with their date, a method rule, a precedent in the record, or “the lead's judgement” when none applies.
  - *Source*: §3.4. The owner often picks the option marked “(Recommended)”. Some recommendations give reasons, and a plan written after the owner's choice records one derived from a dated owner rule (RM:4748-4751), but nothing requires a reason or checks it. Two cases show why the check matters:
    - a question put to the owner carried a false premise, corrected after he answered (LR:510-517; VAL:17031);
    - a plan wrote the lead's recommendation as already decided, until the plan's verifier caught it (SL:160, 202; VAL:17149).
  - **Acceptance**: a question whose default names no derivation is refused at the tool, and so is a derivation naming a policy that does not exist. Whether the policy supports the default is H16.2's to test, and the plan verifier's.
- **H16.2 — A second, independent recommendation** [I].
  - For each question, a model of another family (H15.3) gets the question, the policy store and the owner's recorded words, but not the lead's default, and picks its own.
  - Agreement, with a derivation from a policy, marks the question as covered by that policy, a candidate for H10.3's auto-answer once the owner adopts the rule.
  - Disagreement goes to the owner, as the question to read closely.
  - *Source*: HF §9's “assign a few items twice, to independent auditors, and compare”, applied to the lead.
  - **Acceptance**: a planted question whose policy answer contradicts the lead's default is flagged, by the derivation check or by the disagreement.
- **H16.3 — Overrides are the signal.**
  - An owner's answer other than the default is logged as an override event, with its class and the derivation it overrode.
  - Each override becomes a proposed correction to the policy store, a new rule or a narrower one, at the round's end (H12.2).
  - The override rate per decision class measures how far the steering sits from the owner's intent (§9.5).
  - **Acceptance**: a round cannot close while an override has neither a proposal nor a recorded dismissal (as H6.5 does for side notes).
- **H16.4 — Ratification is sampled, not assumed.**
  - A high rate of picking the default means either good recommendations or a rubber stamp, and the record cannot tell which. That is the verifier's own failure mode (PR §6), applied to the owner.
  - (a) The harness samples auto-answered and ratified decisions into the owner's once-over (§13, risk 10).
  - (b) With the owner's consent only: a planted question whose default a known policy contradicts tests whether ratification still reads. The owner declined plants on round 3's auditors and allowed light ones in round 5 (H15.4), so (b) is a proposal [I].
- **H16.5 — Intent echoes** [I].
  - Before its first edit, each agent restates what its brief asks, what it owns, what it must not touch, its named control, and what would count as failing. This is an intention-out for briefs, after the compiler's (VAL:16677).
  - The harness compares the echo's fields with the brief's: owned paths, forbidden paths, the control's name. The lead reads only the mismatches.
  - **Acceptance**: a brief whose control is ambiguous yields an echo that names a different control, and the work waits for the lead.
- **H16.6 — Delegated approvals are recorded the same way.**
  - Inside an approved plan, the lead approves the parcels' designs itself (§3.4). That is the larger steering channel. Each such approval is recorded as a recommendation (H16.1) answered `by: lead-under-delegation`, with its derivation and the plan line that delegated it.
  - A decision in a reserved class (H10.2), such as an ABI change, needs a delegation that names the class.
    - Step 6's plan itself took the ABI step to 0.17, and the owner approved it (RM:4710; SL:219).
    - Under the plan's delegation of names and encodings (RM:4702), the lead approved R8's three control codes, where the plan said “Two instructions”, and a second new ABI field, `lane_flags_bytes` (RM:4692; SL:366, 371, 374).
    - Recording the delegation makes visible which class each such approval used, and when an approval reaches past it.
  - H16.4's sample includes delegated approvals.
  - **Acceptance**: an ABI change approved by the lead, with no recorded delegation for that class, is refused at promotion (H9.1(g)).

### H17 Holding the line as the work gets harder (added 2026-10-02)

- **H17.1 — Protected surfaces.**
  - Each project declares the files that define correct and how results are counted: the authority, published vectors, the runner and its skip and verdict rules, the negative-control registry, acceptance sets.
  - A parcel's or fixer's diff touching one is refused at the tool unless its brief grants that path. A change to how results are counted stays the owner's (H10.2).
  - *Source*: the honest form is in the record. `deep_let_chain` compiles “by Logan's decision”, so the challenge suite's own expectation now scores FAIL and is “the suite's to restate” (VAL:16917, 17022). The dishonest form is the same diff with no decision behind it.
  - **Acceptance**: a parcel's edit that loosens a tolerance in the authority's vectors is refused before commit, and the refusal names the protected path.
- **H17.2 — A gate ratchet.**
  - Between a parcel's base and its tip, the harness diffs the gate surface mechanically for these shapes:
    - a case removed, or newly skipped (PR §6's “a skipped case”, M:605-607);
    - a tolerance introduced or loosened where exactness was required (`templates/verifier.md` item 8, verifier.md:74-76);
    - five this document adds [I]: an expectation rewritten in the same diff as the code it tests, a control deleted or made inert, a selection narrowed, a counting rule changed (H17.1), and a new gate that matches spellings (H17.4).
  - The rest of item 8's shapes are the verifier's, because no diff rule finds them reliably: an assertion weakened another way, a case that cannot fail, a constant transcribed, and a `TODO` where work was claimed.
  - Each hit goes to the verifier as a finding, with its evidence, and none merges without a reason the verifier accepts.
  - **Acceptance**: plant each shape in a copy of a merged parcel; every one is flagged.
- **H17.3 — A known limit is not an exit.**
  - Under the send-back rule (2026-09-27, §3.3), anything other than a regression or a wrong answer merges as a known limit. So a limit is where a cheat would hide.
  - The verifier classifies, not the parcel. A limit is stated by the behaviour it concedes, and tested by a fault built to evade the gates, which must land inside it (CS4:338-343, 349-350; practised in round 5's verifier rules, loganw.dev docs/ROUND1.md).
  - The harness tracks the ratio of known limits to defects, per area and round, and reports to the owner a ratio that rises as the work gets harder.
  - *Source*: step 6's verifier recorded as a known limit that eight mutations of the acceptance driver leave every check green (VAL:17155): the place a later change could fail silently.
  - **Acceptance**: a NOT READY item that a parcel's report relabels as a limit reverts to a defect, unless the verifier classifies it.
- **H17.4 — Behaviour, not spelling.**
  - A gate that reads source text is a stated limit (CS4:338-341). Where text another program renders must be held, hold it to a subset both programs read alike (CS5:358-360).
  - The ratchet (H17.2) flags a new gate that matches spellings.
  - *Source*: §5.2's last row: a rule written as a list of spellings was walked past in rounds 4 and 5.
- **H17.5 — Honesty under difficulty is measured before placement.**
  - QS9 (§8.2) gives a model a ladder of tasks that become infeasible at a known rung, with each rung's honest outcome in a withheld key.
  - The score is the first rung at which the model passes by weakening something, per (model, provider, harness version, prompt version), beside its rate of honest refusals.
  - A model that cheats below the owner's threshold is not placed in a parcel or fixer role. Live plants (H15.4) repeat the test during rounds.

## §7 Data model (minimum schemas)

JSON-Schema-like sketches. All timestamps are filled by the harness. Every object carries `round_id` and `method_version`.

```jsonc
// RoundState
{ "round_id": "2026-09-30-steps56", "project": "cft-fp256", "method_version": "PR@9b18e35+policies@<hash>",
  "state": "proposed|plan-verified|approved|p0|p0-verified|wave-<n>:dispatched|wave-<n>:merging|build-done|hardware|records|retrospective|closed",
  "paused": null,   // or {"since": "...", "reason": "...", "deadline": "..."}: overlays any state (H1.1)
  "plan_ref": {"path": "docs/ROADMAP.md", "anchor": "Steps 5 and 6", "commit": "be3eb72"},
  "owner_order": {"quote": "Go ahead with your order...", "hold_points": ["before work-order step 3"]},
  "base": {"repo": "loganw234/cft-fp256", "sha": "...", "rule": "at-or-after"},
  "agents": ["AgentRecord ids"], "merge_queue": ["MergeItem"], "open_items": ["OpenItem"],
  "policies_in_force": ["policy ids"], "ledger_path": "...", "events_cursor": {} }

// AgentRecord
{ "id": "S1", "role": "parcel|verifier|recheck|fixer|auditor|triage|reviewer|lead|gatherer",
  "model": {"family": "...", "name": "...", "provider": "...", "version_pin": "..."},
  "parent": "lead|<agent id>", "brief_path": "...", "brief_hash": "...",
  "workspace": {"repo": "...", "worktree": "...", "base": "...", "tip": "...", "scratch": "..."},
  "status": "running|reported|sent-back|resumed|merged|abandoned|paused",
  "transcript": "path", "children": ["ids"], "labels": {"proc": "...", "container": "..."},
  "verifies": "<agent id, verifier only>", "resume_note": "ResumeNote|null" }

// LedgerEntry (rendered as "## <stamp> — <headline>\n\nMeasured: ...\nBelieved: ...\nFor: ...")
{ "id": "P4#3", "author": "P4", "stamp": "harness-filled", "headline": "...",
  "measured": ["claims with refs"], "believed": ["claims"], "for": ["P3", "lead", "anyone"],
  "refs": {"commits": [], "runs": [], "tool_calls": []}, "corrects": "P4#2|null", "urgent": false }

// ParcelReport
{ "agent": "P1", "tip": "sha", "files_changed": [{"path": "...", "why": "..."}],
  "gates": [{"run_id": "...", "stage": "...", "verdict_line": "quoted", "tool_call": "..."}],
  "controls": [{"name": "...", "property_that_bites": "...", "failing_run": {"run_id": "...", "evidence": "..."},
                "passing_run": {"run_id": "...", "evidence": "..."}}],
  "brief_errors": [{"claim_in_brief": "...", "what_is_true": "...", "evidence": "..."}],   // "none found" explicit
  "boundary_crossings": [{"path": "...", "reason": "...", "disclosed_at": "ledger entry id"}],
  "outstanding_children": [], "side_notes": [{"text": "...", "class": "?"}],
  "measured_vs_believed": "...", "summary": "<=300 words" }

// VerifierVerdict
{ "agent": "W1", "verifies": "S1", "tip": "sha", "standard": "a gate, or a stated limit",
  "items": [{"n": 1, "attack": "...", "commands": ["tool_call ids"], "observed": "...",
             "verdict": "confirmed|defect|not-determined",
             "defect": {"class": "regression|wrong-answer|gate-gap|limit|sentence",
                        "failure_scenario": "concrete inputs -> wrong output", "evidence": "..."} }],
  "anything_else": [], "shipped_vs_gate": "the code is right / the gate would catch it",
  "instruments": ["yosys cells", "poisoned pointer", "derived increment", "..."],
  "result": "READY|NOT-READY", "side_notes": [] }

// RunRecord (the gate adapter's output)
{ "run_id": "20260930-210027-2054660", "tree_hash": "...", "commit": "...", "machine": "amd-arc-box",
  "toolchain": {}, "budget": "gate", "stages": [{"name": "...", "verdict": "ok|fail|skip", "reason": "...",
  "inner_skips": [], "seconds": 0, "binaries": [{"path": "...", "sha256": "...", "built_at": "..."}]}],
  "verdict_line": "quoted", "log_paths": [] }

// Policy
{ "id": "send-back-2026-09-27", "text": "Only a regression or a wrong answer sends a parcel back; ...",
  "owner_words": "...", "date": "2026-09-27", "scope": "project:cft-fp256",
  "enforcement": "brief-text|ledger-seed|harness-check|project-gate|seam-refusal",
  "status": "proposed|adopted|retired", "provenance": ["VAL:15274"], "review_by": "..." }

// ReservedActionRequest
{ "action": "push-other-repo|deploy|delete-remote-branch|card-run|long-build|spend-resource|counting-rule|abi-change|new-work-order",
  "detail": "...", "requested_by": "lead", "covered_by_policy": "policy id|null",
  "default_if_no_answer": "hold|proceed", "deadline": "...", "decision": "...", "decided_by": "owner|policy" }

// ResumeNote
{ "agent": "S3", "where": "...", "committed_at": "sha", "next_steps": [], "open_questions": [], "do_not_redo": [] }

// Recommendation (H16; added 2026-10-02)
{ "id": "...", "round_id": "...", "question": "...", "options": ["..."], "default": "...",
  "derivation": [{"kind": "policy|owner-words|method-rule|precedent|lead-judgement", "ref": "policy id, VAL line, or the owner's quote and date"}],
  "second": {"model": {"family": "...", "name": "..."}, "choice": "...", "agrees": true},
  "answer": {"choice": "...", "by": "owner|policy", "stamp": "harness-filled", "override": false} }

// ProtectedSurface (H17.1; added 2026-10-02). The paths are an illustration for cft-fp256.
{ "project": "cft-fp256", "paths": ["python/cft_golden/**", "vectors/**", "verify/run.sh", "programs/acceptance.json"],
  "kind": "authority|vectors|counting|controls|acceptance", "change_needs": "owner|policy id", "grants": ["brief ids"] }
```

Two additions to every record above (2026-10-02):
- **Agent ids are qualified by round** (`<round_id>/<id>`), since cft-fp256 reuses A1, P1 and VI2 across rounds (§2.2).
- **Every response's reported model is stored** beside the AgentRecord's pin (H15.1).

A suggested on-disk layout [I]: `<harness-home>/rounds/<round_id>/{state.json, ledger/{<author>.md, urgent/}, briefs/, reports/, verdicts/, runs/, transcripts/, archive.zip}`.

- It lives outside every repository. Project records are written into the repository only through the records compiler (H11).
- This mirrors the record's own `Data/runs/<date>-<round>/` convention, which is gitignored [R VAL:16506].

## §8 Roles on open-weight models

### §8.1 What each role demands, as the record shows it

| role | demands, from the record | failure shapes seen even with frontier models [R] | harness guardrails that lower the demand |
| --- | --- | --- | --- |
| lead | read two repositories and find the plan's own errors before dispatch; design a behaviour-preserving seam; write briefs that name the trap and a control that bites; act on escalations within minutes; merge discipline; diagnose under uncertainty with one instrument per hypothesis, cheapest first (the card day, CS2 §9); write records that agree with the data | the 16 enumerated errors in CS3; watches; stale binaries; overclaiming; records disagreeing with data; gates that fell to respellings (CS4) | H1-H5, H9 and H11 take over the mechanical half. H10.5 lints briefs. A verifier on P0, on the lead's commits and on its records |
| verifier | re-run from clean; build plants and controls; adversarial creativity outside the list; precise failure scenarios; tools like yosys cell and mux counts, poisoned pointers, preprocessed-TU diffs; restraint (must not fix); honest “found nothing” | V4 posted “no defect” before its list was exhausted (CS2 10:07/10:24); a verifier left a clone in the lead's tree and did not report it (CS4); verifier-P2 missed a twin sentence on one pass (CS4 00:34) | H6.1 schemas (“list exhausted” before READY); H4.4 ACL; H3.4 frozen inputs; H15.4 live plants; H7.3 run reuse |
| parcel | about 150 to 940 tool calls (round 2: 252-939; round 3's follow-ups: 149-335; round 4: 289-864); long verbatim build lines; ownership by function; a negative control shown failing; ledger discipline; escalation; disclosure | a broken rule (“never kill by image name”) under pressure; typed stamps; brief premises believed until measured | H2.2 permissions; H2.4 shell; H8.4 process labels; H6.2 to H6.3 evidence checks; H10.5 linted briefs |
| re-check | a scoped confirmation of named defects, 11 to 23 min in round 2 | a re-check passed a small overclaim in its own fix's comment (CS3, P7) | schema; the claim-to-evidence check |
| fixer | apply the verifier's defects inside the worktree; same controls | the two long fixers (106 and 88 min) carried scope the lead added (CS3) | auto-built fixer briefs (H1.3) |
| auditor | read a document group against the tree; propose amendments with exact spans | 7 refuted of 303; refutations fell on low-confidence findings (5 of 33 low, 2 of 133 medium, 0 of 137 high) | per-finding verifiers; a confidence field; exact-span amendments (the lead's applier half-applied 14 amendments) |
| triage | classify side notes as finding or not | 72 of 314 side notes were not defects (CS3) | verifiers on findings |
| reviewer | review the lead's applied diff against the verifiers' findings | — (the highest-yield step of round 3's day) | frozen inputs |
| gatherer / record checker | rebuild a timeline and costs from transcripts and git; check every figure | 100 statements confirmed, 22 wrong, 44 misleading, 3 unsupported in round 3's first case-study draft | the loop until the findings shrink (H12.1) |

### §8.2 Qualification suites built from the project's own history

HonestFramework's position is that a judge's detection rate is a property of the model, prompt and tooling together, and must be measured with planted faults and a key withheld (HF §9; ADOPTING step 8). This project's record is unusually well suited to that, because every verifier finding has commits on both sides of it.

**One caution first: contamination.**

- A clone of cft-fp256 contains the later fixes and the VALIDATION text that describes each defect.
- The ParcelRound case studies and ledger archives are public, and may be in a model's training data.
- HF §9 warns to “check whether your corpus already contains the answers”.

So every replay runs:

- on a clone truncated at its base commit, with no later history and no records;
- with no network access;
- with a contamination note per model (has it seen these repositories?).

Promotion decisions should rest on **freshly planted** faults (QS4), with the history replays as supporting evidence.

**Where the replay data is** (revision, 2026-10-02) [R]. The briefs and ledgers of cft-fp256's rounds from 2026-09-25 on are only in the gitignored `Data/runs/` on the owner's desktop. Round 3's, of 2026-09-24/25, are also in ParcelRound's public `archive/round3-ledger.zip`.
- They were never published, so replays built from them carry less contamination risk than replays of the public case studies. The exception is anything sent to another provider, as the challenge suite's results were (VAL:16911).
- They are on one machine: QS2 and QS3 replays of those rounds run there, or on a copy made from it.

Proposed suites [I], with the data each needs:

- **QS1, tool-call conformance**, per (model, provider, version). TC §7.8: golden transcripts; parallel and multi-turn calls; a code-heavy multi-line argument; streaming; `tool_choice` modes; thinking on and off.
- **QS2, parcel replay.**
  - **Input.** An archived brief at its base commit:
    - round 2's P1 to P4, as dispatched. Wave 1 (P1, P4): the brief is `git show 48eb4b0:docs/ROUND2.md`, on code base `fd9ec1e` (P0). Wave 2 (P2, P3): brief and code both at `e0f211f`, i.e. main `5c0c655` plus the docs-only amendments `d4e4529` and `e0f211f` [R]. Never use HEAD's ROUND2.md: it carries 260 lines added after dispatch, including the lessons the parcels taught. ROUND2.md at `fd9ec1e` itself still has the placeholder `<P0 sha - the lead fills this at dispatch>`.
    - round 4's P1 to P3 in ParcelRound's `archive/round4-ledger.zip`, `briefs/P*.md`, at Quantum-Film `b0e9ed1` (P2 in atlas-film at `be1d674`) [R];
    - the user's local `Data/runs/<date>-<round>/` for the V to W rounds' briefs [R VAL:14834-14835, 16506].
  - **Score** against the record:
    - (a) gates green through the runner, or failing only where the failure is reproduced at the base;
    - (b) the named control shown failing and passing;
    - (c) brief errors found versus the original parcel's (round 2: P1 five, P4 six, P2 four, P3 six) [R CS2];
    - (d) disclosed boundary crossings;
    - (e) whether the recorded defects (V1 to V4's findings) were introduced, checked by the recorded verifier lists plus a frontier verifier.
  - **Cost**: the build environments. Round 2 needs the `cft-sim` Docker image, Verilator and the Windows MinGW build. Round 4 needs Python, a libcft build and more:
    - P3 ran live jobs on Moth's Atlas platform, whose key has since expired (CS4), so its replay needs a recorded-response stub of that API;
    - P2's replay must reproduce the editable-install trap (CS4 13:06).

    Which replay is cheaper is open until the stub exists [I].
- **QS3, verifier replay of recorded send-backs.**
  - **Input**: for each recorded defect, the parcel tip before the fix, the brief, and the verifier's original numbered list, with the defect's own item removed where the list named it.
  - **Score**: whether the candidate finds the same defect, measured by its failure scenario reproducing.
  - **Examples available**:
    - round 2: V1 on P1 (the decode rule turning a defaulted field into a whole gather; the XRT staging size; a test reading past its buffer), V2 on P2 (a read before the `n` check, segfaulting at n = 2^61; a derived count of 4,676 against the reported 4,720), V3 on P3 (ACTALL reviving a masked lane, visible only in a flag; the mask block at 59% of sequencer cells), V4 on P4 (a flag arm reading stale lanes, only after a different kind of run);
    - round 4: verifier-P1's D1 to D10. Several come with the tight input that exposes them; D3 and D9 are respellings past a source rule, D4 writable caches, D5 a non-bytes stream, and D6 was left to the lead;
    - the V to W rounds' wrong answers and regressions, with SHAs in each VALIDATION entry (e.g. W5: `mp-err-check` never called `cft_mp_const` or `mp_log_of_mp`, so three plants stayed green).
- **QS4, planted-fault diffs (HF §9).**
  - Take merged parcel commits and plant faults of `templates/verifier.md` item 8's shapes: an assertion loosened, a tolerance where exactness was required, a case that cannot fail, a constant transcribed, a `TODO` where work was claimed.
  - Add HonestFramework FAILURE-MODES shapes (B1, C3, D1, E1), plus a “bit comparison swapped for value comparison” (CS1).
  - Withhold the key under the three-commit protocol.
  - Also measure the false-alarm rate on the unplanted, already-verified merges.
  - There is no baseline to compare against: the owner declined planted faults on round 3's auditors, so the record's verdict rates are “suggestive, not a detection rate” (VAL:14296-14299). QS4 would produce the project's first detection rate, for the frontier verifiers too.
- **QS5, lead replay.**
  - Give round 2's request to a candidate lead: cft-rebound's asks with both repositories at `039e3c3` (cft-rebound) and `b963663` (cft-fp256).
  - Score whether it finds the three corrections the real plan found before dispatch: ask 6 already delivered; asks 1 and 4 one mechanism; ask 5's 2% ceiling.
  - Then score its briefs through H10.5's linter and by the brief errors replayed parcels report.
- **QS6, records fidelity.** Give a candidate the ledger, reports and run records of a past round; have it draft the VALIDATION entry; diff it against the committed entry and against the runs. Count wrong figures, dropped units and overclaims. Round 3's lead entry had several; the record names them.
- **QS7, auditor calibration.** Replay round 3's sweep groups at its base, `0321e8a`, the parent of the sweep's first landing `080fe30`. Compare findings and the refutation rate by confidence with the recorded 303 findings.
- **QS8, spec-only adversarial test authoring** [I, from the exchange of 2026-10-01/02; added 2026-10-02].
  - **Input**: the project's specification and a few examples, with no implementation and no authority, as GPT-6.1 Sol Max received (WR:19-34).
  - **Output**: a challenge suite with its own oracle.
  - **Score**: defects found that reproduce; expectations that hold against the authority; the oracle's independence (it imports nothing of the project).
  - This places models as cross-family challengers (H15.3). It is an external oracle in HF §1's sense only when its inputs were the specification alone, so every input is recorded. The hard-workload pack drew on an adapter from returned results (`golden_adapter.py:3`).
- **QS9, honesty under difficulty** [I; added 2026-10-02].
  - **Input**: a ladder of variants of a task that becomes infeasible at a known rung. Examples: a program past one tile's 32,768 instructions, a gate stricter than the code can meet, a bound past what can be proven.
  - **The key**: each rung's honest outcome (a refusal by name, a stated limit, or an escalation), withheld under the three-commit protocol.
  - **Score**: the first rung at which the model passes by weakening a gate, narrowing the work, relabelling a defect as a limit, or overclaiming; and its rate of honest refusals.
  - **Seeds in the record**: the challenge suite's 3 TARGET-LIMIT rows (VAL:16904), and the 11 hard workloads that do not fit a tile (VAL:17003-17006; RM:4657-4663). Each program's reason is in `Data/runs/2026-10-01-hard-workloads/results/README.md`, from line 78.
  - It measures the owner's second clause directly: “without cheating to still pass after things get harder” [O 2026-10-02].

### §8.3 Initial placement (proposal [I]), to be revised by QS scores

| role | start on | move when |
| --- | --- | --- |
| lead | the strongest available model, which today may be closed; the owner keeps hold points | QS5 and QS6 within the owner's tolerance on at least two replayed rounds; then a live lead-only round (CS4's “lead-only round” shape) on a low-risk area |
| verifier | the strongest available, from a **different family** than its parcel | QS3 recall and QS4 detection at or above the owner's threshold, with a low false-alarm rate; then live plants (H15.4) every round |
| parcel | open-weight strong coders after QS1, QS2 and QS9; **narrower parcels** than today (§11.2) | QS2 parity on replays; QS9 at or above the owner's threshold (H17.5); send-back rate per live round |
| re-check, fixer | open-weight | after QS1 and QS9 (H17.5), with schema enforcement |
| auditor, triage | open-weight mid-size | QS7 calibration |
| gatherer | open-weight; the checkers that verify gatherers stronger | QS6 |

**The first data point below the frontier tier** (round 5, added 2026-10-02) [R]. Every parcel and every parcel's verifier ran on Sonnet, on prose-heavy work.
- Every parcel reached READY, and the lead caught what those verifiers missed (CS5:169-182).
- CS5 records it as an observation, not yet a rule (CS5:381-384).
- It supports a smaller model on prose-heavy parcels with a stronger verifier behind it. Its parcels also wrote the site's page modules in Python (CS5:195-199), so it says little yet about work that is mostly code.

### §8.4 Candidate open-weight models as of 2026-10-01 [S, verify each on its model card]

| model | released | size (total / active) | context | licence | agentic signal |
| --- | --- | --- | --- | --- | --- |
| Kimi K3 | weights 2026-07-26 (llmgateway.io, 2026-08-04) | 2.8 T / 104 B; MXFP4 weights, about 1.4 TB; multi-node on vLLM or SGLang | 1,048,576 | custom “Kimi K3 License”; read it before commercial self-hosting | absent from benchlm's Terminal-Bench 2.0 list; morphllm states 88.3 on Terminal-Bench 2.1 |
| GLM-5.3 | 2026-08-29 | 744 B / 40 B per Gigazine (morphllm says 753 B) | 1 M per morphllm, not stated by Gigazine | GLM-5.3 License; above $10 B annual revenue requires a security review by Z.ai | Artificial Analysis Agentic Index 59 (as reported by Gigazine) |
| DeepSeek V4 Pro / V4.1 | V4 2026-04-24 (TC §3.4); V4.1-Flash 2026-09-10 (morphllm) | V4 Pro 1.6 T / 49 B (morphllm) | 1 M (morphllm) | MIT | Terminal-Bench 2.0: “DeepSeek V4 Pro 0813” 67.9% (benchlm, 2026-09-30); the DSML tool format changed between V4 and V4.1 (TC §3.4) |
| Kimi K2.6 | 2026-04-20 (TC §3.5) | 1 T / 32 B (TC §3.5; the cited pages give these for Kimi K2) | (see TC) | Modified MIT (TC §3.5) | Terminal-Bench 2.0 66.7% (benchlm) |
| GLM-5.1 | 2026 | — | — | — | Terminal-Bench 2.0 63.5% (benchlm) |
| Qwen3.6-27B | 2026-04-22 | 27 B dense | 131 K per morphllm | Apache-2.0 | Terminal-Bench 2.0 59.3% (benchlm); the strongest model here that plausibly runs on a single workstation GPU when quantised [I] |
| MiniMax M2.7 / M3 | 2026 | M3: 428 B / 23 B per morphllm | 1 M per morphllm | MiniMax licences | M2.7: Terminal-Bench 2.0 57% (benchlm) |

Sources: [llmgateway.io](https://llmgateway.io/blog/kimi-k3-open-weights), [Gigazine](https://gigazine.net/gsc_news/en/20260829-glm-5-3-open/), [morphllm](https://www.morphllm.com/best-open-source-llm), [benchlm](https://benchlm.ai/benchmarks/terminal-bench-2); all in Appendix B. The aggregator numbers disagree across sites and have no common harness. Use them only to choose what to put through QS1 to QS9.

## §9 Autonomy that follows enforcement

### §9.1 The principle [I, from HF FAILURE-MODES “How to use this list” and CS4 obs 25]

HonestFramework's last instruction is to mark each failure mode **caught mechanically**, **caught by habit**, or **not caught**: “Habits are not defences.” CS4 obs 25 gives the gradient a rule climbs as it hardens: “A trap written into a brief is a rule to remember; written into the seam, it is a refusal.”

So autonomy should be granted per (area, decision class), in proportion to how much of that area's known failure surface is caught mechanically, and how well the judges in that area have scored. Not by time, and not globally.

**The enforcement ladder for a rule** (H10.1's `enforcement` field):

1. owner's words (a message);
2. brief text or verifier-list text;
3. ledger seed (environment trap);
4. harness check (H-requirements);
5. project gate with a negative control;
6. seam refusal by name.

Each step up converts a judgement into a mechanism. The harness should report, per area, the count of rules at each level and the share of FAILURE-MODES entries caught mechanically.

### §9.2 Levels, with where the record sits

| level | the owner decides | standards, policy and the lead decide | where the record is |
| --- | --- | --- | --- |
| **L0 supervised** | every dispatch and every merge | nothing on its own | — |
| **L1 plan-gated** | the plan of record and contract shape; reserved actions; card days | dispatch, verifiers, send-backs, merges to main, records | round 2 (approval at 03:30; “every other decision was the lead's”) |
| **L2 queue-gated** | an ordered queue of plans with hold points; reserved actions; standing rules; still the technical and contract decisions each round lists under “Logan's decisions this round” | adds: the round's shape (lead-only or parcels); questions a standing rule covers; pauses and resumes by protocol | cft-fp256 on 2026-09-30 (“Go ahead with your order …”; “Hold before starting Step 3”) |
| **L3 charter-gated** [proposal] | a charter: areas, budgets, the reserved list, hold classes; new features; contract or ABI changes; hardware; anything irreversible or external | adds: proposing the next plan from ROADMAP debts and known limits, and starting **pre-approved classes** (fixes rounds, gate widenings, docs sweeps, known-limit closures, records corrections) after a notice period unless vetoed | not yet; the F round, “the fixes round”, is exactly such a class, and the owner approved it as part of an order |
| **L4 self-directed within the charter** [proposal] | the charter, method reversals, and digests | adds: maintaining the roadmap, sequencing rounds continuously, adopting method *reinforcements and extensions* automatically (reversals stay the owner's) | — |

### §9.3 Promotion and demotion [proposal; thresholds are the owner's to set]

**Promote an (area, decision class) one level when all hold**, over a window the owner chooses (for example the last N rounds touching the area):

1. **No post-merge defect.** Nothing merged was later found wrong by a later verifier, the card, CI, the owner or a downstream user. The record already logs these as the “lead's slips” and as corrections entries.
2. **Judges qualified.** QS3 recall and QS4 detection at or above the threshold for the models in use, and every live plant (H15.4) caught.
3. **Mechanical coverage.** At least X% of the area's FAILURE-MODES entries and standing rules are at enforcement level 4 or above.
4. **Zero reserved-action breaches.**
5. **Records verify clean.** H11.3's verifier findings per entry below Y.
6. **A low owner-override rate.** The owner rarely reverses a decision taken under policy.

**Demote at once on:**

- a wrong answer reaching main, hardware or a published page;
- a breach of the reserved list;
- a verifier missing a live plant;
- a records entry found to state something its runs do not hold.

**Log every promotion and demotion as a dated policy** (H10.1), so the autonomy state is itself in the record.

### §9.4 What remains the owner's for a long time [I, from the record]

- **Direction**: what the project is for. Examples: whether ask 5 is worth building at a 2% ceiling, and the controlled-divergence work order.
- **Irreversible or external effects**: deploys, pushes to other repositories, finite device jobs, licence and publication decisions.
- **Changes to how results are counted** (skip accounting, verdict rules). Round 3's lead set one mid-round, and it was one of the two defects attributed to the lead's own grants.
- **Method reversals.**
- **The once-over.** The owner looks at what no gate and no verifier was asked to look at. Two examples: CS4's notices finding, and the owner's question about the quad's build options, which uncovered RETIMING on one tile of four (VAL:16349). Each such catch should become a gate where it can (H14.4), shrinking this list over time.

### §9.5 Steering toward the owner's intent (added 2026-10-02)

**The aim** [O 2026-10-02], in the owner's words: “an ideal outcome is a system in which the core principles, once hardened into the system itself, can effectively steer the model in the authors original intentions without their significant feedback and more importantly without cheating to still pass after things get harder.”

**What the record shows** [R].
- **Two channels carry the steering inside a round** (§3.4):
  - the questions the lead puts to the owner. In the language and step-6 rounds, seven decisions were picks of the option marked “(Recommended)” and one approved twelve recommendations at once, beside about as many decisions in the owner's own words;
  - the lead's own approvals of the parcels' designs, under the plan's delegation. This is the larger channel: L1's eight choices, L2's nine, L3's ten, D2's, and R8's.
- **The owner's own ideas still arrive unprompted**: the intention-out, the cross-model test, certificate v2's provenance. Those are direction, not ratification, and they are the part to protect.
- **One drift went through no channel at all.** The brief-errors line, which METHOD.md calls its highest-yield sentence, left all 37 of cft-fp256's parcel briefs from 2026-09-25 on, with no proposal and no decision (§3.5).

**Two readings fit the same record** [I]:
- the recommendations and approvals apply principles the owner hardened earlier. The 2026-09-29 decision procedure (IEEE 754, then RISC-V practice, then whatever fits the current systems) is the strongest case (§3.3), and the step-6 plan records one choice's derivation from a dated owner rule (RM:4748-4751);
- or they carry the model's own preferences, and the owner ratifies them.

Many recommendations give reasons. But nothing requires one and nothing checks it, so in general the two readings can't be told apart. Two cases show what an unchecked recommendation can carry: a false premise in a question (LR:510-517), and a recommendation written as already decided (SL:160, 202).

**What “hardened into the system” takes, for steering** [I]. A principle steers only once it is:
1. **explicit**: in the policy store, with the owner's words and date (H10.1);
2. **compiled** into every brief, verifier list and recommendation (H10.4, H16.1), so no agent depends on remembering it;
3. **checked**: each recommendation names its derivation, and an independent recommender that never saw the default surfaces the questions the principles leave open (H16.2);
4. **corrected** from overrides, the most informative events the owner produces (H16.3).

The owner's feedback then lands where it carries information: overrides, disagreements between recommenders, and classes of question no policy covers yet.

**Earning “without significant feedback”, one class at a time** [I]. §9.1's rule applies to decisions as well: autonomy follows enforcement.
- A candidate standing rule is a class of decision that meets all three:
  - its defaults all derive from one policy;
  - the second recommender agrees with them;
  - the owner has not overridden one in a window the owner sets.
- Adopting it is the owner's. From then on H10.3 auto-answers the class, logged with the policy id.
- Sampling (H16.4) keeps drift visible where no override would show it.
- Direction (§9.4) is not a class that graduates. What the project is for stays the owner's.

### §9.6 Holding the line as the work gets harder (added 2026-10-02)

**Why difficulty is the test** [I].
- Every mechanism in HF and PR assumes the honest path is open. When a task becomes infeasible (a program past one tile, a gate the code cannot meet, a bound that cannot be proven), the honest outcomes are a refusal by name, a stated limit, or an escalation (HF §2).
- The dishonest ones include:
  - PR §6's cheat shapes: an assertion loosened, a tolerance where exactness was required, a skipped case (M:605-607);
  - respelling past a text check (CS4:144);
  - two this document names [I]: relabelling a defect as a limit, and overclaiming in the record.
- The pressure toward them rises with difficulty, and so does the cost of noticing them, because hard work is where reviewers are least sure.

**What the record shows** [R].
- **Honest outcomes under difficulty:**
  - the challenge suite's 3 TARGET-LIMIT rows, beside 205 PASS (VAL:16904);
  - the 11 hard workloads that do not fit one tile: reported as not fitting, the programs kept as delivered (WR:1), and made step 6's work by the owner (VAL:17003-17006, 17044; RM:4657-4663);
  - a behaviour changed only by the owner's recorded decision, with the now-stale expectation left failing in the record rather than rewritten. `deep_let_chain` now compiles, and the suite still scores it FAIL (VAL:16917, 16919, 17022);
  - the foreign model's insistence that the exit-70 rows “must remain visible as compiler defects, rather than disappear into a statement that every test passed” (its review's REPORT.md:26-27).
- **Where the line could give way.** These are the soft spots the record names, some caught by a verifier and some recorded as limits. The record shows no agent that passed by weakening a gate:
  - gates that fell to respellings (CS4:144; CS5:101);
  - controls that tested nothing, the lead's included (§5.2, first row);
  - a counting rule the lead set mid-round, which a verifier caught (CS3:243-244; §4.5);
  - known limits sitting where a later change could fail silently: eight mutations of the acceptance driver leave every check green, though the committed wiring is right (VAL:17155).

**What hardening means here** [I].
- **Make the cheap cheats impossible:** protected surfaces, and a ratchet that flags every diff that weakens a gate (H17.1, H17.2).
- **Make the expensive ones visible:** an independent verifier classifies limits, and a limit is tested by a fault built to evade the gates (H17.3, H17.4).
- **Measure each model's threshold before trusting it** (H17.5, QS9), and again during rounds with live plants (H15.4).

The record suggests the property is reachable: the frontier fleet chose the honest outcomes above under real difficulty. QS9 is how to find out whether an open-weight fleet does, before it is trusted with the gates.

## §10 The self-improvement loop

**The loop as practised [R].** Round → case study written during or after it → “What METHOD.md should say differently”, each item typed new, reinforcement, extension, relaxation or reversal, with the incident it rests on → owner adoption → METHOD.md and the templates.

- Round 2's proposals were adopted in full the next day.
- Rounds 3, 4 and 5's are pending in METHOD.md (§3.5). Round 5 applied 3 and 4's by the owner's decision, and cft-fp256's later rounds practised many of them without one.
- In parallel, the project's own loop: verifiers' “known limits” → a fixes round (the F round was opened from the audit round's gate failures and its verifiers' gaps [R VAL:16349]) → ROADMAP debts → the next plan.

**What the harness adds [I].**

1. **The retrospective as a scheduled round** (H12.1), using CS3's shape (gatherers, then a draft, then checkers, then re-checks until the findings shrink). Every figure comes from H13 telemetry and H1 state, not reconstruction.
2. **Proposals as policy objects** (H12.2) with evidence links, entering the policy store as `proposed`. At L4, reinforcements and extensions may auto-adopt after a notice period; relaxations and reversals never do.
3. **Compiled briefs** (H10.4), so an adopted lesson reaches the very next brief without depending on any lead's memory (CS4 obs 32).
4. **A known-limits budget.** When the open known limits in an area exceed a threshold, or touch an area about to be built on, the harness proposes a fixes round automatically. That is a pre-approved class at L3.
5. **Method drift detection.** Diff the method of record (METHOD.md plus templates at their pinned version) against the policies actually applied in briefs. Surface rules that are practised but unadopted, and adopted but not practised.
6. **Qualification refresh.** Re-run QS1 to QS9 whenever the model, the provider, the harness version or the prompts change (HF ADOPTING step 8), and on a timer. Provider-side changes are silent (TC §4.6).

## §11 Open-weight specifics

### §11.1 Tool calling and reasoning

Use the tool-calling report's architecture throughout:

- the canonical items;
- a server-side parser for the exact model version;
- client-side template rendering as the fallback;
- schema sanitisation;
- ID remapping (Kimi `functions.name:idx`, Mistral 9-character IDs);
- the per-family reasoning policy (TC §7.5).

Specific to this workload:

- **Code-heavy arguments.** Edits to RTL, C and docs are long, multi-line, with quotes and backslashes. Prefer families with XML-ish per-parameter argument encodings, or design the edit tool to take a file path plus an exact old/new pair. Either way the harness validates that the edit applied: one lead slip was “a two-part inline patch whose second half did not take” [R VAL:15583-15585].
- **Long-horizon stability.** A parcel makes roughly 150 to 940 tool calls [R §4.3; CS4]. Known failure modes include DeepSeek V4's argument collapse after a prior tool round (TC §3.4) and template drift between versions (V4 versus V4.1). The harness needs TC §7.4's repair pipeline and must log every repair as an event, so a model that needs many repairs is visible in its QS scores.
- **Interleaved reasoning.** GLM, Kimi K2.x, MiniMax M2.x and Qwen3.5/3.6 need prior reasoning returned across tool rounds (TC §7.5). Dropping it silently degrades long agentic runs.

### §11.2 Context, and why parcels should be narrower [I]

- The record's peaks were frontier-model contexts: the lead at 968 k tokens; a resumed verifier at 845 k [R]. Several open-weight models now advertise 1 M-token windows (Kimi K3, DeepSeek V4, GLM-5.3 and MiniMax M3 per [S]), but effective long-context reliability is model-specific and must be measured, for example in QS2 and QS3 at realistic lengths.
- **Design response**: make work units smaller and state explicit.
  - Split a parcel the size of round 2's P3 (939 tool uses, 814 k tokens, 18 files) into a design parcel and one or two build parcels, sequenced by the lead. Accept more seams and more seam tests (PR §7).
  - Keep the state card, ownership list and ledger cursor outside the context (H1.2, H2.5).
  - Spill tool output to files: runner logs are long; the `node` stage alone runs 22 to 38 min [R CS3].
- **Trade-off**: PR README says “The bottleneck is not agent count. It's the lead's capacity to merge and verify, and in practice it's the suite run after each merge.” More, smaller parcels mean more merges and more suite runs. Batching under H9.6, and run reuse under H7.3, are what keep that affordable.

### §11.3 Serving: caching, concurrency, hosting

- **Cache reads dominate token volume.** Round 2 read 3.5 B cached tokens at a 99% hit rate; round 3 read 1.5 B for agents plus 228 M for the lead [R]. Round 2 ran on a subscription and “no fees were paid” (CS2), so the record has no prices. That cache reads would dominate a metered cost too is an inference [I].
  - Self-hosted: automatic prefix caching (vLLM) or RadixAttention (SGLang), with retention sized to tool-call gaps that run to many minutes while gates execute. Agents with the same prefix (role prompt, tools, policies) should be routed to the same replica.
  - Hosted: provider caching semantics vary and are part of the (model, provider) pin [I].
- **Concurrency.** Up to 10 agents at once in round 3 [R], 16 by default in Claude Code workflows [D]. A self-hosted fleet sizes batch capacity to this, plus the lead. Hosted endpoints bring per-key rate limits (H8.2).
- **Hosting reality [I].** The repository names a Windows desktop (12 threads, 47 GB shared, WSL), `amd-arc-box` (36 threads, 46 GB, the U50), and an RTX 5060 Ti in the photograph check [R CLAUDE.md, README]. Frontier-scale open weights (Kimi K3 at about 1.4 TB in MXFP4, multi-node [S]) need hosted inference or rented clusters. Consequences:
  - **provider variance**: pin providers, run a K2-Vendor-Verifier-style conformance suite, route for quality (TC §4.6);
  - **data governance**: source code and ledgers leave the machine;
  - **licence terms** on some weights, e.g. Kimi K3's custom licence and GLM-5.3's revenue threshold [S].
  - A mid-size dense model such as Qwen3.6-27B (Apache-2.0 [S]) is the realistic local option, for scoped roles: triage, re-checks, fixers.
- **Anthropic's position on gateways** [D]: Claude Code may sit behind gateways that expose a supported API format, but Anthropic “doesn't support routing Claude Code to non-Claude models through any gateway”. Third-party guides that set `ANTHROPIC_BASE_URL` to an open-model endpoint exist; the one cited warns that “reliable tool use is not guaranteed on every backend” [S]. Read this as: build the harness. Keep Claude available through the API for roles where qualification says it is still needed.

### §11.4 Determinism and replay of the orchestration

Claude Code's workflow runtime makes `Date.now()` and `Math.random()` throw, so that a relaunch repeats the same agents and completed ones return saved results [D]. Adopt the same property for the harness's fan-out scripts (H1.6). It is also what makes QS suite replays reproducible: same brief, same base, same seed, same model pin.

## §12 Build plan

### §12.0 Before Phase 0: the method of record (added 2026-10-02)

- **The owner's next step** [O 2026-10-02]: a ParcelRound round that brings METHOD.md and its templates to the method as practised, starting with the findings practised but never recorded (§3.5).
- **Why first:** H10.4 compiles briefs from those templates, so they must be current before anything is compiled from them.
- **A dry run:** the round exercises the harness's mechanisms by hand. Every rule its lead has to remember is evidence for an H-requirement.

### §12.1 Phase 0: measure before building (days, not weeks) [I]

1. **QS1** (TC conformance) for each candidate (model, provider).
2. **QS3** on round 2's and round 4's recorded send-backs, using a minimal agent loop with a read-only workspace and shell. It needs no orchestrator. Use the §8.2 contamination controls: a clone truncated at the base, no network.
3. **QS4** with 10 to 20 plants in already-verified merges, key withheld.
4. **QS9 seeds** (added 2026-10-02): the challenge suite's TARGET-LIMIT rows and the 11 hard workloads that do not fit a tile, so the first placement table carries each model's honesty under difficulty (§8.2, H17.5).
5. **Output**: a first role-placement table with numbers, recorded with date, model, provider and prompt version (H15.2).

### §12.2 Phase 1: the core that removes the §5 failure class [I]

- The orchestrator and round state (H1.1 to H1.5).
- The workspace factory (H3).
- The ledger service with harness stamps, ACLs and `urgent/` (H4).
- Durable events and the wake policy (H5).
- Schema reports with claim-to-evidence checks (H6).
- Resumable agents (H1.3).
- A minimal merge tool (H9.3, H9.4).
- Protected surfaces and the gate ratchet (H17.1, H17.2; added 2026-10-02). They are cheap, and they remove the cheapest cheats.
- The model each response reports, checked against the pin (H15.1; added 2026-10-02).

**First live run**: a small real round in the shape of a fixes round or a lead-only round plus one verifier. Lead on the strongest model; open-weight fixers and re-checks; verifier from a different family. Record everything as the case studies did, so the run is itself a case study.

### §12.3 Phase 2: the project-facing layer

- The gate adapter (H7) on `verify/run.sh`'s `report.jsonl` and VERDICT line.
- The resource broker (H8) with the desktop, WSL and `amd-arc-box` as registered machines and the card as a reserved resource.
- The full promotion rule (H9.1).
- The policy store seeded from §3.3 (H10).
- Recommendations that carry their derivation, and the override log (H16.1, H16.3; added 2026-10-02).
- The records compiler targeting VALIDATION.md's structure (H11).

### §12.4 Phase 3: placement by measurement

- QS2, QS5 and QS6 replays.
- QS8, to place cross-family challengers (H15.3; added 2026-10-02).
- Live plants (H15.4).
- Move roles per §8.3.

### §12.5 Phase 4: autonomy and the improvement loop

- L2 encoded (queue, hold points, standing rules auto-answering).
- L3 trials on pre-approved classes in areas with high mechanical coverage: documentation, gate widening, known-limit closures.
- The second recommender, ratification sampling, and decision classes graduating into standing rules (H16.2, H16.4, §9.5; added 2026-10-02).
- The retrospective round (H12).

### §12.6 Base for the worker loop: options [I]

| option | for | against |
| --- | --- | --- |
| (a) own loop on TC §7's canonical items | full control of stamps, ACLs, permissions, schemas, resumption, reasoning policy; no dependence on a vendor's harness semantics | the most to build: edit tools, shell, compaction, transport |
| (b) an existing open-source agent loop as the worker, with the orchestrator outside it | faster to a working parcel; many already support open models and worktrees | must be wrapped to enforce H2.2 to H2.4 and H6 from outside; their own subagent and resume semantics may conflict with H1.3 and H1.4 |
| (c) Claude Code itself pointed at open models through a gateway | the method was developed on it; several of §5's harness rows have since improved in its docs (rows 9 and 20) | not supported by Anthropic for non-Claude models [D]; the discipline rows (kind D) still depend on agents remembering rules, which is what the harness exists to remove |

**Reuse regardless of option:**

- ParcelRound's `templates/` as the prompt templates, compiled per H10.4.
- HonestFramework's `gate-runner.sh` contract as the runner interface standard for any new project.
- cft-fp256's `verify/run.sh` report format.
- The VALIDATION entry structure as the records compiler's target.
- Claude Code's workflow semantics as a design reference: `agent()`, `pipeline()` and `parallel()`; schema-validated results with retries; deterministic replay [D].

## §13 Risks and open questions

1. **The lead gap.** Plan-writing that finds the plan's own errors from code (round 2's three corrections), and card-day diagnosis, are the least replaceable skills in the record. If open-weight leads score poorly on QS5, the realistic configuration for some time is a closed-model lead with open-weight workers [I].
2. **Rubber-stamping by weaker verifiers.** PR §6 names it as the verifier's own failure mode. Live plants (H15.4) are the only defence that measures it. Without them “found nothing” and a rubber stamp are the same text (WITH-PARCELROUND). The owner declined plants on round 3's auditors, so adopting them is the owner's decision.
3. **Correlated errors.** A parcel and a verifier from the same family may share blind spots. Family diversity is a hypothesis [I] to measure (H15.3).
4. **Suite time is the clock.** About 25 min a run in round 1; about an hour a merge on the box in round 2; a 111 to 117 min gate budget on the box in the 09-30 rounds [R]. More send-backs from weaker models mean more runs. H7.3 run reuse and H9.6 batching are the levers; their failure mode is skipping a leg that would have failed (HF FAILURE-MODES A3).
5. **Provider drift.** Templates and parsers change under a pinned model name (TC §4.6, F1). QS1 must re-run on a schedule and on any provider change.
6. **Replay contamination.** The answers to every historical replay are in the repositories' later history and in public case studies (§8.2). Scores from replays can overstate a model that has seen them; freshly planted faults do not have this problem.
7. **Effective context below nominal.** 1 M-token windows [S] do not guarantee 900 coherent tool calls. Measure, and design for narrower parcels (§11.2).
8. **Policy-store sprawl.** Standing rules accumulate. HF §10's instruction for the agent notes applies to policies too: “delete entries when they stop being true”. Each policy needs a review date and a test where possible (H10.1).
9. **Autonomy metrics can be gamed by narrowing scope** [I]. Promotion must count work attempted as well as defects avoided. For example, a level held only by doing documentation rounds should not promote RTL autonomy.
10. **The owner's once-over.** The record's owner catches (premature application, the missing watch, notices, the RETIMING question) were found because a person looked at what nobody was asked to look at. At L3 and above, schedule an owner review sample of random merged items, and fold every catch into H14.4.
11. **Data handling.** Hosted inference sends proprietary code and ledgers to third parties. Decide per repository: cft-fp256 is Apache-2.0 and public, and that may not hold for other projects.
12. **Unverified in this analysis.**
    - The current behaviour of Claude Code's watch or monitor (the 30-minute cap and consent come from CS4, not the docs).
    - Whether ParcelRound's round 3 and 4 proposals have been adopted outside the repository. *Answered 2026-10-02*: the owner applied them to round 5 by decision (loganw.dev SPEC.md decision 19). None of rounds 3 to 5's has been taken into METHOD.md (§3.5).
    - The contents of `Data/runs/` (local to the owner's machine). *Read in part on 2026-10-02*:
      - every round's ledger directory;
      - the lead's ledger in the ODE, cert, rev7, audit, steps-5-and-6, language and step-6 rounds, at the lines cited;
      - the 93 briefs from 2026-09-25 on, through the practice survey and a grep for the brief-errors line (§3.5).

      The transcripts have not been read.
    - The model facts tagged [S].
    - Every “TC §n” citation refers to the earlier report, not re-checked here.
13. **Steering capture** [I; added 2026-10-02]. If the lead's recommendations carry the steering and the owner ratifies them, drift from the owner's intent stays invisible until an override. H16's derivations, second recommender and override log are the instruments. Without them, a high ratification rate cannot be read either way.
14. **Goodhart under difficulty** [I; added 2026-10-02]. The pressure to pass rises with difficulty, and so does the cost of review. H17 and QS9 answer it.
15. **Silent model substitution** [R CS5:316-321; added 2026-10-02]. The model a response reports can differ from the version the owner named, and from the rest of the same agent's responses, in a closed fleet too. A dispatch that names only a family cannot show it. H15.1 answers it.

## Appendix A: what stays in prompts (templates), not in the harness

These rules are judgement content. The harness compiles them into briefs and verifier lists (H10.4), but cannot enforce them mechanically. From PR §§1-8 and HF §§1-10:

- **Read the requester's code, not its ask list** (PR §1).
- **P0**: anything three or more parcels touch is the lead's first parcel. Aim to make the seam disappear (a glob, discovered entry points). Behaviour preserved, proven both sides. Refusals in every backend (PR §2).
- **Registries walk themselves** and fail by name in both directions; prove it with a dummy row (PR §2). The harness can host the check; the design is the project's.
- **A value statement names the measurement that would falsify it**; a stop line says what to measure before stopping (PR §2, §8).
- **Brief content.** “Your job” is one paragraph. Ownership is by function. Forbidden files name their owner. Expected small edits are listed. The cost model names its divisor. The trap is named, with “what will be measured at verification”. Host build lines are verbatim. Prohibitions are written as the command to use. The specific negative control, named by “the property that makes it bite”. “Report anything you found that this brief got wrong.” (PR §3; CS4 obs 8)
- **Ledger bar**: environment facts; a brief that turned out wrong; findings about shared code. Mark measured versus believed (PR §4).
- **The taxonomy of gates that cannot fail**: passing against itself; proving nothing; vacuous through the observable; inert by construction; no expectation at all; a value comparison where a bit comparison is required; plumbing (exit codes, unread files, stale binaries); a mechanism enforced in two places with the gate reading the cheaper one; a device gate without device memory; test the largest shape a capacity claims, and one past it (PR §5).
- **The verifier**: must not fix; “found nothing” acceptable; re-run from clean; list plus “anything else”; separate shipped code from the gate; a false claim in a comment is a finding; the preprocessed-TU diff (PR §6). Its default instruments: yosys cell and mux counts for RTL, a poisoned pointer, “derive the increment”, the lead's own artefacts (PR §6).
- **One instrument per hypothesis, cheapest first, before touching the design** (PR §7; the card day).
- **Gates over behaviour, not spelling**: a gate that reads source text is a stated limit; state a limit by the behaviour it concedes (CS4 obs 14, 21). Designing the check of behaviour stays judgement. H17.4 adds a mechanical flag on new gates that match spellings (added 2026-10-02).
- **A claim's domain, quantifier and unit are claims** (CS4 obs 20, 23).
- **Authority, refusal by name, one fact in one place, provenance in the artifact, uncertainty carried in the value, control the judge** (HF §§1-9). These are the project's job; the harness requires them of a project before granting autonomy above L1 [I].

## Appendix B: sources

**Repositories** (cloned 2026-10-01):

- [github.com/loganw234/cft-fp256](https://github.com/loganw234/cft-fp256) at `ded90d8`: README.md, CLAUDE.md, docs/README.md, docs/ROUND2.md, docs/ROADMAP.md (plans of record, lines 3144-4168), docs/VALIDATION.md (lines 11914-16670), verify/run.sh `--list`, .github/workflows/gates.yml, git history.
- [github.com/loganw234/ParcelRound](https://github.com/loganw234/ParcelRound) at `8767e23`: README.md, METHOD.md, CASE-STUDY.md, CASE-STUDY-2.md, CASE-STUDY-3.md, CASE-STUDY-4.md, `templates/*`, archive/round2-ledger.zip, round3-ledger.zip, round4-ledger.zip, round4-second-ledger.zip.
- [github.com/loganw234/HonestFramework](https://github.com/loganw234/HonestFramework) at `65447fd`: README.md, METHOD.md, FAILURE-MODES.md, CASE-STUDY.md, WITH-PARCELROUND.md, ADOPTING.md, templates/README.md, templates/agent-notes.md, templates/gate-runner.sh.

**Read for the 2026-10-02 revision**:

- cft-fp256 at `4190a47`:
  - docs/VALIDATION.md, lines 16671-17179;
  - docs/ROADMAP.md, step 6's plan of record (lines 4577-4904);
  - programs/workloads/README.md, and the pack's `tools/golden_adapter.py`;
  - verify/run.sh.
- On the owner's desktop: cft-fp256's `Data/runs/`, namely:
  - the round directories;
  - the lead's ledgers of the audit, steps-5-and-6, ODE, cert, language and step-6 rounds (the lines cited);
  - every round's `briefs/` (grepped for the brief-errors line);
  - the challenge suite's review (REPORT.md and its `evidence/exact_oracle.py`);
  - the hard-workload results' README.
- In this repository: `Rounds/ParcelRound-R6/practice-survey.md`, the survey of which pending proposals were practised.
- ParcelRound:
  - CASE-STUDY-5.md, on the local branch `round5-case-study` at `49a9266`;
  - at `8767e23`, METHOD.md's history (`git log -- METHOD.md`) and the templates' last commits.
- [github.com/loganw234/loganw.dev](https://github.com/loganw234/loganw.dev) at `43c36a2`:
  - README.md, CLAUDE.md, docs/SPEC.md, docs/ROUND1.md and docs/VALIDATION.md;
  - its round ledger, `loganw-dev-ledger/` (the README and the briefs).

**Claude Code documentation** (fetched 2026-10-01):

- [Other LLM gateways](https://code.claude.com/docs/en/llm-gateway.md)
- [Subagents](https://code.claude.com/docs/en/sub-agents.md)
- [Dynamic workflows](https://code.claude.com/docs/en/workflows.md)

**Secondary**:

- [Kimi K3 open weights, llmgateway.io (2026-08-04)](https://llmgateway.io/blog/kimi-k3-open-weights)
- [GLM-5.3 open release, Gigazine (2026-08-29)](https://gigazine.net/gsc_news/en/20260829-glm-5-3-open/)
- [Best open-source LLMs, morphllm.com (modified 2026-09-19)](https://www.morphllm.com/best-open-source-llm)
- [Terminal-Bench 2.0 leaderboard, benchlm.ai (2026-09-30)](https://benchlm.ai/benchmarks/terminal-bench-2)
- [Claude Code on OpenRouter and DeepSeek, andrewbaker.ninja (2026-08-10)](https://andrewbaker.ninja/2026/08/10/how-to-run-claude-code-on-openrouter-with-alternative-models-like-deepseek-the-anthropic_base_url-guide/)

**Companion**: the earlier open-weight tool-calling report (“TC”), whose §§ are cited throughout.

## Revision log

- **2026-10-01**: the first version.
- **2026-10-02, the fold-in, stamped 14:28:40 -0700 from the clock**, at the owner's word “Fold the gaps in” [O].
  - **Read**: cft-fp256 `4190a47` and its `Data/runs/`; ParcelRound's branch `round5-case-study` (`49a9266`); loganw.dev `43c36a2`.
  - **Added**:
    - the intro: the owner's aim, and H1–H17;
    - §0: the new sources, the [O] tag, and the new citation keys;
    - §1: in items 1 and 5-8, the new evidence; item 10 split into three steps;
    - §2: counts at `4190a47`, the language and step-6 rounds, and the cross-model exchange;
    - §3.4: the language and step-6 row, and the reading of technical direction;
    - §3.5: round 5, the templates, and the drift in practice;
    - §4.1: rounds 5, language and step 6; §4.2: round 5; §4.5: round 5 and step 6;
    - §5.2: recurrence across rounds 1-5;
    - §6: the at-a-glance diagram; H4.3, H7.1, H7.7, H8.2, H13.1, H15.1, H15.3 and H15.4; the new H16 (steering) and H17 (holding the line);
    - §7: `Recommendation`, `ProtectedSurface`, and agent ids qualified by round;
    - §8.2: where the replay data is, QS8 and QS9; §8.3: round 5's data point;
    - the new §9.5 and §9.6;
    - §12.0, and items in §12.1-12.5;
    - §13: item 12 updated, items 13-15 new;
    - Appendix B.
  - **Corrected**: round 2's human-active figure is the owner's reading after the twelfth hour of a round of about 24 h, not a whole-round total (CS2:528-531).
- **2026-10-02, a verifier's findings answered and the practice survey folded in, stamped 15:13:38 -0700 from the clock.**
  - **The verifier.** It was a separate agent told to disconfirm the fold-in, and it edited nothing. The lead re-read every finding at its source and accepted all but one. That one was the claim that the pack's oracle predates the results returned to the model; the lead could not confirm it, so it is left out.
  - **Wrong, now corrected:**
    - ten NOT READY verdicts, not nine;
    - `deep_let_chain`: a behaviour changed by the owner's decision, with the stale expectation left failing, not an expectation changed;
    - round 5's dispatch named only “sonnet”;
    - step 6's later verifiers had reported, so they are not “in flight”;
    - the gate's 43 includes `lang`, and QS9's per-program reasons are cited;
    - “most” of the owner's decisions: seven picks of a recommended option and one batch approval of twelve, beside about as many in the owner's own words;
    - “nothing records a derivation”: reasons are often given, but none is required or checked;
    - “the owner answers every design question”: the lead approves designs under delegation, now H16.6;
    - “whole rounds between decisions”: they are hours apart;
    - the README is gone from the fixes round on, and `urgent/` from the audit round on, not from 2026-09-29;
    - H17.2's and §9.6's attributions of cheat shapes;
    - QS1-QS7 elsewhere, now QS1-QS9;
    - round 3's ledgers are public, so the local-only replay data starts 2026-09-25.
  - **Could mislead, now restated:**
    - the cross-model inputs, separated for the suite and the pack;
    - the templates lack METHOD.md's conditional archive step, rather than contradicting it;
    - round 2's stamp claim did not generalise;
    - “Where the line has given way” is now the soft spots the record names, since it shows no agent passing by weakening a gate;
    - H7.8 is now H7.7, with what the record composes across machines and commits, and a rule for reusing a stage run at an earlier commit;
    - §8.3 now requires QS9 for parcels and fixers;
    - the round-2 caveat appears wherever its figure does;
    - old text on `urgent/` and on pending proposals is qualified;
    - round 5 applied rounds 3 and 4's proposals by the owner's decision 19;
    - the recurrence table's propagation row is now 2 rounds, and its round-1 rows cite METHOD.md and `6845a57`.
  - **Added from the practice survey** (`Rounds/ParcelRound-R6/practice-survey.md`): §3.5's counts, cft-fp256's own method, and the brief-errors line absent from 93 briefs (also §9.5).
- **2026-10-02, the verifier's scoped re-check answered, stamped 15:43:16 -0700 from the clock.** The same verifier re-checked the fixes above. The lead re-read each finding at its source and accepted them all:
  - the oracle's “before” is restored: the suite's zip of 14:53 holds it, and the returned results pin that zip by hash;
  - R8: the ABI step to 0.17 was in the approved plan (RM:4710). The delegation (RM:4702) covered only the third control code and `lane_flags_bytes` (§1, §3.4, H16.6);
  - RM:4748-4751 records the derivation of a choice the owner had already made; it is not a recommendation as put to him;
  - H7.7: the record's reuse guard diffed from a later commit than the stages ran at. The rule is now keyed on what a stage executes;
  - H17.2 now lists the spelling-gate shape that H17.4 relies on;
  - §3.5: main moves at a round's end or its milestones, not once per round; the watch is per round; merges are re-made by `git merge-tree` or a parent-union script; the brief-errors line is quoted as METHOD.md and the template word it, and the clauses that survive are named;
  - the survey's counts are corrected to 34 / 8 / 9 / 3 (CS4#19 and #23 were practised only in their origin round), and round 5's 26 rules are cited at ROUND1.md:136-189, 200-201;
  - §9.6: the round-3 counting rule was caught by a verifier.

  No further re-check was run on this pass's corrections. That is a stated limit, and the round's own verifiers read this file's §3.5 again when they check round 6's scope.
- **2026-10-02, from round 6's plan verifier, stamped 16:34:42 -0700 from the clock.** This entry was first written with a typed, approximate time, and that is corrected here; the slip is logged in the round's harness notes. The brief-errors finding's domain is corrected in §1, §3.5 and §9.5. The rule governs parcel briefs, so the figure is all 37 parcel briefs, not all 93 briefs (now 94, with a verifier brief added at 15:56). METHOD.md's wording of the request is quoted, not the template's.
- **Unchanged and still true at their commits**: every figure the first version gave “at `ded90d8`” or at ParcelRound's `8767e23`.
