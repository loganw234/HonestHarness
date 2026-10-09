# HonestHarness round 1: the first step down the ladder, DeepSeek over its API

Reconstructed from the round's ledger, its committed records, and the
session's transcripts. The ledger is archived beside this file, with the
round's harness notes (`harness-notes.md`) and its table (`TABLE.md`). Times
are the ledger's own stamps, local time, UTC-7.

The round was run on ParcelRound's method, with a Claude session (Opus 5.5)
as lead:
- **P0, the lead's seam:** the run record, the spending guard, the live gate,
  the DeepSeek adapter, the runner, and a gate with its threat model.
- **Five parcels on Opus:**
  - QS1, tool calls through a provider's API;
  - the agent loop and its Docker sandbox;
  - a QS6 slice, round 6's ledger read at five lengths;
  - a QS4 replay, round 6's planted copies verified again by a model working
    through the loop;
  - and, by amendment 1, QS4h: the same replay on this round's own code.
- **Verifiers on Sonnet** from 11:45 on the first day, by Logan's standing
  rule.
- **Live batches on deepseek-flash,** over DeepSeek's API.
- **At Logan's word, after DeepSeek's suite,** Claude Haiku 5.5 ran the two
  replays' packages as Claude Code agents, as a reference point (item 11).

## The setting

- **The question** (PLAN.md §1): can a cheaper model, reached over an API, do
  the skills a ParcelRound round measures?
  - This round is the ladder's first rung: DeepSeek's flash model, then Qwen.
  - Qwen did not run. Alibaba Cloud required ID verification first, and
    Logan moved it to a later point (the round's end, below).
- **What the round measures:** QS1, QS6's slice, QS4's replay and QS4h's.
  Each is a suite of REQ's §8.2, run through one runner that meters every
  call.
- **What the round builds:** each suite, and the harness parts they need.
  Each part went past a verifier before any live run used it.

## Timeline

2026-10-06:

| time | event |
|---|---|
| 10:26 | the round opens at Logan's go, on plan of record 2357035 |
| 10:45 | P0 committed; verifier-P0 (Opus) and a CS7 reader go out |
| 11:21 | verifier-P0, pass 1: NOT READY, five sent back; the lead's sealed view revealed |
| 11:45 | Logan's rule: verifiers on Sonnet |
| 12:26 | verifier-P0, pass 3: READY; P0 done |
| 12:27 | the first live step: a probe batch |
| 12:28 | wave 1 dispatched: P1 (QS1) and P2 (the loop and sandbox) |
| 13:42, 13:53 | P1 and P2 report; their planted copies go to Sonnet verifiers |
| 14:52 | P1 merged; QS1's first live batch |
| 15:00 | QS1 thinking on: 44 fails, from the lead's own brief error |
| 17:01 | P1's fix verified and merged; QS1 thinking on runs clean |
| 17:10 | P2 merged; P4 dispatched |
| 18:17 | P3 merged; QS6's live runs start |
| 18:35 | QS6 holds: a Chinese public holiday billed off-peak |
| 19:11 | QS6 at 64K meets requests closed with no reply; P0 gains a bounded retry |
| 19:37 | Logan: continue the runs, with a $20 top-up |
| 19:49 | the retry committed; verifier-P0r goes out |
| 20:47 | QS6 complete: ten whole batches |
| 20:55 | QS1 complete again under the restated version |
| 22:00 | verifier-P4 reports; the keys are published; 8 of 8 plants caught |
| 22:13 | P4 merged; QS4 holds for Logan's ruling on his address |

2026-10-07:

| time | event |
|---|---|
| 03:00 | Logan: the history may go to DeepSeek; QS4 starts |
| 03:03 | DeepSeek's content filter refuses QS4's third request |
| 03:23 | diagnostics: the refusal is `cat -n`'s line form, every time; `read_file` changes form (db94d41) |
| 07:19 | QS4's first pass complete: 8 of 10 plants; P5's real tip stopped at the 40M cap |
| 07:23 | Logan: three more passes, "to get a real dataset" |
| 08:57 | two runs lost to one call closed three times running; retries at 2, 5, 15 and 30 s |
| 09:32 | Logan: exact per-batch tracking may go for parallel runs; three lanes |
| 10:08 | the lanes' console windows closed by hand; the runs restart windowless |
| 11:03 | the lanes' outside sources unreadable at their long path; the lanes move and start again |
| 12:41 | Logan: Qwen waits for all of DeepSeek's runs, a code replay included |
| 12:48 | Logan approves amendment 1 |
| 12:57 | run records name their code (b79217a) |
| 13:44 | amendment 1 verified, corrected and pushed (b310f82) |
| 14:08 | QS4's lanes merged; the combined reconciliation read two minutes after the last call (too soon, 18:47) |
| 15:17 | verifier-J agrees with 85 of 89 judgements; settled; committed at 15:23 (bd92fd5) |
| 16:47 | Logan on the desktop: low priority; the code trials wait for his word |
| 17:13 | P5's QS4h built (54ce53f); verifier-P5 on a planted copy |
| 18:24 | Logan off the desktop; at 18:45, the code trials may run at peak |
| 18:47 | the $20 top-up shows the 14:08 reconciliation read too soon: $0.08 short |
| 19:54 | verifier-P5: NOT READY; both plants caught in its first pass; one real wrong answer |
| 21:48 | P5's fixes at c3be1ef; verifier-P5's pass 2 |
| 23:18 | verifier-P5 READY; P5 merged (022abee), restated (dfb7b25); QS4h's first run alone |
| 23:42 | its bill posts late: a mismatch at 10 s, ok at 4.5 min; three lanes start |

2026-10-08:

| time | event |
|---|---|
| 00:22 | at peak, real tips drop 16 to 20% of requests; two lost; the lanes restart at an allowance of 40 |
| 01:47 | h1-real lost even at 40; the lanes restart with real tips held for off-peak |
| 03:00 | off-peak; the real tips start |
| 04:30 | closes track request size, not the hour: real tips lose as many off-peak; 01:47's premise withdrawn |
| 05:00 | lane A queues a second rerun of h1-real against the rule; the lanes restart on one shared list of reruns |
| 07:42 | QS4h's last run ends: 30 runs scored, 7 lost, 3 interrupted |
| 07:54 | the lanes merged; the combined reconciliation agrees to under a cent; verifier-JH dispatched |
| 08:25 | a second read, 42 minutes after the last call, holds it |
| 08:46 | verifier-JH agrees with all 87 judgements; QS4h's judgements committed (a065686) |
| 08:49 | the hold-point report to Logan: DeepSeek flash's full suite is done |
| 10:12 | Logan: Claude Haiku 5.5 as Claude Code agents on the replays' packages |
| 11:30 | Haiku on QS4h's eight packages: 7 of 8 plants |
| 12:49 | verifier-HK (Sonnet) agrees with 67 of 68 judgements; its one disagreement taken |
| 13:18 | Haiku on QS4's ten packages: 9 of 10 plants |
| 14:02 | verifier-HK4 (Sonnet) agrees with all 57 judgements |
| 18:12 | Logan: Qwen waits on Alibaba's ID verification; round 1 closes on DeepSeek's suite |
| 18:24 | Logan: round 2 finishes Phase 0 on DeepSeek; this session's parcels go to Sonnet, its verifiers to Haiku |

## What the plan predicted, and what happened

1. **Sonnet verifiers found every planted fault.**
   - Four parcels' work went to verifiers as planted copies, two plants
     each. The keys were hashed into the ledger before each dispatch and
     published after the last report (22:00:27).
   - All 8 were found, each in the verifier's first pass, each with an input
     that shows it. P5's planted copy later went the same way: 2 of 2 in
     verifier-P5's first pass (19:54).
   - Every plant had survived its parcel's own tests: the lead ran
     candidates against each suite and kept only survivors.
   - **Where they clustered:**
     - in a golden, and in a leak scan's places;
     - in a loop's counters;
     - in two questions' wording;
     - in a status rule, and in one sentence of a prompt.

     That is, where a specification's meaning is, not where its code paths
     are. verifier-P4's own mutation pass, 265 mutants and 212 killed, could
     not find either of its two. Reading the code against its docstring, its
     design and round 6's ledger found both.
2. **The verifiers also found real faults, and the lead's.**
   - verifier-P0, on Opus, found all five of the lead's sealed suspicions
     and about fifteen more, over three passes.
   - verifier-P2 found two real faults besides its plants (V3, V4), fixed
     before the merge.
   - verifier-P0r found four sentences of the lead's that claimed more than
     was true.
   - verifier-P4 found that the owner's address rides in the replay
     repositories' history (L2).
   - verifier-P5 found one real wrong answer: QS4h's copy of QS4's host
     check had dropped `--ignored` (F3, fixed at c3be1ef).
3. **The lead's briefs held errors the parcels found:**
   - QS1's brief asked that reasoning be "present" in thinking mode. DeepSeek
     emitted none on 43 of 101 turns, and the brief's error failed them;
   - QS6's brief contradicted itself on how to size cuts. P3 found it in
     phase 1;
   - P2's brief said `--mount` refuses a missing source. P2 found it does
     not, on Docker Desktop;
   - P4's brief gave a builder's method that reproduces only one of five
     planted copies. The method that reproduces all five sat in a plan
     verifier's scratch.

   Each was found before it cost a wrong result in the record, except QS1's.
   That one was found by a live batch, corrected, and run again.
4. **DeepSeek flash met QS1 and QS6 at their ceilings.**
   - **QS1:** every call/no-call decision was right in both settings (F1
     1.000), and every call's arguments were valid. In thinking mode, 15
     runs drew the documented 400 for a forced tool choice.
   - **QS6:** 659 of 660 runs exact, across ten batches from about 18K to
     154K tokens. In the 138 runs whose answer was not in the input, it
     invented none.
   - **So the QS6 slice cannot tell strong models apart.** It may still tell
     weaker ones apart down the ladder.
5. **The provider dropped requests, and the harness learned to retry them
   boundedly.**
   - At 64K tokens and above, DeepSeek closed about 5 to 7% of requests with
     no reply at all, at holiday peak. Below 64K, none of over 500 runs met
     one.
   - P0 stopped each batch at the first such drop, as built, since the cost
     was unmetered. The lead added a bounded retry, with its cost reserved
     and counted. Its batch allowance of three proved too small, so a flag
     raised it, and the rest ran at 15.
   - Every retry inside the allowance was answered.
   - Whether DeepSeek bills a dropped request was open here. QS4h settled it
     for its own runs (item 9).
6. **The meter matched the bill, and where it did not, the reason was
   found.**
   - DeepSeek's usage export matched the spend file to the last decimal
     (17:08:40).
   - A Chinese public holiday is billed off-peak all day. The price table
     priced it as peak, and the guard held the batch on the mismatch until
     it was diagnosed (18:35:19).
   - A test showed that billed drops can match another model's rates and
     read as routing. The summary now names the unmetered attempts.
7. **The owner's priority overtook the lead's own gate,** and the record
   says so. The lead had ruled that the retry is verified before more live
   runs. Logan asked for the runs to continue, and the verifier ran beside
   them (19:37:52).
8. **QS4: DeepSeek flash, working as round 6's verifiers worked.** The score
   of record is the lead's judgement, checked by verifier-J on Sonnet: it
   agreed with 85 of 89 (15:11:13), and the four were settled in the ledger
   (15:17:50).
   - **What ran.**
     - The items: round 6's five planted copies, and the five real tips
       beside them as the false-alarm set.
     - The inputs: what round 6's verifier had, through P2's loop and
       Docker sandbox, ending in a structured report.
     - Four passes, at Logan's word (07:23:08). The first two ran one at a
       time, the rest in three lanes at once (09:32:39).
     - 40 runs count, ten a pass. 18 more ran and are left out, each with
       its reason (below).
   - **The plants: 31 of 40, by pass 8, 8, 8 and 7.** Round 6's Opus
     verifiers caught 10 of 10.
     - **Every plant that changed a figure or a reference was caught in
       every run, 24 of 24.** Those plants were:
       - three counts: 38 to 28, twelve to fifteen, and five to six;
       - a fourth count, eight to six;
       - a section tag, §3 to §8;
       - a referent, "its fixes" made "the verifier".
     - **Plants that changed meaning or shape were caught 7 of 16:**
       - a clause added (P2-p2), 3 of 4;
       - a duty made a permission (P3-p1), 2 of 4;
       - two steps swapped (P5-p2), 2 of 4;
       - a list item dropped (P4-p1), never.
     - **In three of the misses the model saw the plant and let it go:** its
       report's text or its ledger file notices the change, and no finding
       states it (verifier-J). Counted so, 34 of 40.
     - The screen and the judgement differ once, on P4-p1 in pass 1. A
       finding beside it held its marker while stating round 6's D1.
   - **Findings besides the plants': 49.**
     - **15 match round 6's recorded findings.** Round 6's B13 restate
       (P1-r1) was found in 6 of the 8 runs on P1's commits. Its D1 (P4-r1)
       was found twice, once by a real-tip run.
     - **19 are new and true,** and 3 of those had been seen by round 6's
       lead or a verifier outside the verifiers' recorded findings.
       - Most are small: a commit message's count or claim, or a limit the
         text already states.
       - One is a template's paraphrase that loosens a rule: a row "no test
         names" for a row "no test exercised".
     - **15 are false alarms,** with a shape:
       - a rule read as a description of the past;
       - a permission read as a mandate;
       - a paraphrase read as a misquotation;
       - one sentence flagged by three runs for three different reasons,
         and settled by git (7 files in one commit, 9 in the other).
       - Several the model had marked itself as "cannot show it false".
   - **The real tips:** 18 of 20 runs reported, 8 of them READY.
     - **The two that did not were P5's,** the tip that wanders. In pass 1 it
       ran 169 turns and wrote 45 check scripts before the 40M prompt cap
       stopped it. In pass 4 one request outgrew the 900,000-token per-call
       cap.
     - Run again under the same conditions, it reported twice, in 103 and
       122 turns.
   - **Cost.** The 40 runs cost $5.74, $0.14 a run. 98.8% of the 469M tokens
     they read were cache hits, and they wrote 5.9M. The 18 left out cost
     $2.47.
   - **The provider shaped the runs more than the model did.**
     - **The content filter.** It refused round 6's verifier brief in
       `cat -n`'s line form every time, and answered it in `grep -n`'s. The
       lead changed `read_file`'s form (db94d41).
     - **Closed requests.** It closed about 11% of requests with no reply, and
       more as requests grew: in two lost runs the failed requests' median
       was 161 and 180 messages, against 131 and 123 for the answered.
       - Bounded retries answered all but two calls, each closed three
         times running.
       - The batch's allowance ended four more runs.
       - The lanes' combined reconciliation agreed with a balance read two
         minutes after the last call, to the cent (14:08:26). A later read
         was $0.08 short (18:47:34): about $0.00023 for each of the 346
         closed attempts in the lanes, or charges posted late. QS4h's
         evidence (item 9) favours charges posted late. The usage export
         settles it.
     - **The runs left out:**
       - 2 refused by the filter;
       - 7 ended by closed requests;
       - 1 under the earlier `read_file` form;
       - 8 lane runs whose outside sources were unreadable.
     - The longest runs make the largest requests, so the allowance ended
       the runs that wandered most (harness note 45).
   - **The harness's own faults, found in the runs:**
     - At the lanes' first path, Docker Desktop's binds of the outside
       sources read as I/O errors in the sandbox. The models reported it,
       and the lead found it by reading their reports (11:03:35).
     - Windows the owner closed ended three runs (10:08:09).
     - No record named the code a run ran under. Record version 2 does now
       (b79217a).
   - **The judge's own standard drifted.** Two verdicts changed once the
     lead judged by round 6's verifier list, as a third run's finding quoted
     it (harness note 44).
9. **QS4h: DeepSeek flash on code, where Sonnet's verifiers caught 8 of 8.**
   The score of record is the lead's judgement, checked by verifier-JH on
   Sonnet: it agreed with all 87 (08:37:51).
   - **What ran** (amendment 1, approved 12:48:48 and verified at 13:44).
     - The items: this round's own four planted copies, two plants each, and
       their four real tips as the false-alarm set. The copies hold QS1's
       cases and judge, the agent loop and sandbox, QS6's slice, and QS4's
       replay.
     - The inputs: what each Sonnet verifier had, rebuilt by P5 (merged at
       `022abee`, restated at `dfb7b25`), in P2's sandbox with the project's
       tests runnable offline. QS6's answer key is withheld (QS4h's limit 4).
     - **30 runs count:** four passes of each planted copy and of three tips,
       and two of h1's tip, which lost three of its five runs.
       - 7 more were lost, and 3 interrupted by the lead's restarts. All are
         left out, each with its reason.
       - Every run's record names `dfb7b25`, unchanged.
   - **The plants: 31 of 32 by judgement, 26 by the screen.** Sonnet's
     verifiers caught 8 of 8, each in its first pass.
     - **Seven plants were caught in every run.** P3-B, a QS6 question whose
       threshold no longer fits its four citations, was missed once, in pass
       4.
       - Noticed, not raised: the run's reasoning weighed whether the
         threshold had been changed and kept it.
       - Its report says it checked every citation line by line.
     - **The screen missed what the model stated** (harness note 49).
       - P1-B and P2-B break what a docstring promises.
       - The model named each fault and showed it with a probe. It cited the
         promise's lines, or the check left standing 70 lines away, rather
         than the edit's.
       - The screen located 3 of those 8 catches; the judgement found all 8.
   - **Findings besides the plants': 55.**
     - **28 match the Sonnet verifiers' recorded findings, but only 8 of
       them.** Of the 19 the verifiers recorded in their own view, the runs
       found 6 at least once.
       - The squashed copies' stale commit-message figures were found in
         every run that could: P1-v6 in 6 of 6, and P4-v1 in 8 of 8.
       - P2's one command crashing without Docker was found in 5 of 8.
       - P2's other sent-back fault, model text reaching the published
         record, was never found.
     - **23 are new and true,** 14 distinct faults, and small. Several were
       stated as limits by the work already. They include:
       - docstrings that claim more than the code does: `run_agent` "never
         raises", and a closed list of budgets that omits one;
       - a test that passes only on Windows;
       - a file scorer whose listed "./" prefix can never match;
       - a QS6 limit wider than its case.
     - **2 are true of the replay, not the work:** QS6's withheld key, and a
       contradiction that QS4h's SHA mapping writes into the ledger it
       replays (harness note 51). They are counted apart.
     - **2 are false alarms,** both about Docker behaviour the run could
       not observe, against measurements in this round's ledger.
   - **The real tips:** 14 reported, 4 READY. Two of P2's four runs passed
     work that Sonnet sent back for two wrong answers.
   - **Cost.** The 30 runs cost $7.38: 449M tokens read, 99.0% of them
     cache hits, and 5.1M written. The lost and interrupted runs cost $2.38;
     QS4h, $9.76 in all.
   - **The provider.**
     - **It closed requests by their size, not the hour** (harness note
       50).
       - Over QS4h's attempts, none under 100K characters closed, and 3% at
         100K to 200K.
       - 5 to 6% closed at 200K to 400K, 17 to 18% at 400K to 800K, and 29
         to 32% above 800K, at peak and off-peak alike.
       - The lead had moved the real tips off-peak on the belief that the
         hour mattered (01:47:15). It saved half the price and no runs
         (04:30:07).
     - **A second failure:** two runs ended on a connection reset
       (WinError 10054), which P0 does not retry (harness note 48).
     - **The lanes' reruns needed one shared state.** Each lane knew only
       its own reruns, so one queued a second rerun of h1-real against the
       rule. The lead caught it and restarted the lanes on one shared list
       (05:00:45).
     - **The closed requests were not billed:** the combined reconciliation
       agreed with the meter to under a cent, with 700 closed attempts in
       the lanes. It held at reads 10.5 and 42 minutes after the last call
       (07:54:20, 08:25:11).
10. **The runtime's limits shaped the round.**
    - A background job stops at 2 hours. So batches ran one per job, QS4's
      run budget is 6,000 s, and a proof run given too short a limit had to
      run again.
    - The 128K and whole-ledger batches finished in minutes, because almost
      every token was a cache hit.
11. **A reference point: Claude Haiku 5.5 as Claude Code agents on the same
    packages** (Logan, 10:12:54).
    - **What ran.**
      - One pass of each item, QS4h's eight and QS4's ten. Each package was
        built through the suite's own input checks, from what the
        DeepSeek runs mounted.
      - Each agent worked with Claude Code's tools on the Windows host, as
        this round's Sonnet verifiers did, and not in P2's loop and Linux
        sandbox. So these runs compare Haiku with the Claude verifiers more
        closely than with DeepSeek.
      - The lead audited every transcript for reads outside the package:
        - none read another package, the keys, or DeepSeek's records;
        - one QS4h run listed the session's task folder, file names only,
          and is stated, not voided.
      - The runs took 18 to 44 minutes and 56 to 161 tool calls each. They
        are not in the round's records or its cost, since the harness
        metered none of them.
    - **The scores,** the lead's judgements, each checked by a Sonnet
      verifier:
      - **QS4h:** plants 7 of 8 (P3-B missed, the plant DeepSeek missed
        once).
        - Findings besides the plants: 60. 35 match, 20 are new and true, and
          5 are false alarms. verifier-HK agreed with 67 of 68 judgements,
          and the lead took its one disagreement (12:49:09).
        - Of the 19 recorded findings in the Sonnet verifiers' view, Haiku
          found 11 in 8 runs, against DeepSeek's 6 in 30. It found P2-v1,
          model text reaching the published record, in both P2 runs.
      - **QS4:** plants 9 of 10 (P4-p1 missed, the plant DeepSeek missed in
        all four passes).
        - Findings besides the plants: 47. 21 match, 13 are new and true,
          and 13 are false alarms, 11 of them contestable. verifier-HK4
          agreed with all 57 judgements (14:02:40).
        - Of round 6's recorded findings in view, it found 10 of 31, against
          DeepSeek's 11 of 114 over its 38 reported runs.
      - **Across both, 16 of 18 plants.** DeepSeek caught 62 of 72, and the
        Claude verifiers 18 of 18: Opus's 10 in round 6, and Sonnet's 8 here.
    - **What it showed.**
      - **Haiku's reach was wider than DeepSeek's at a similar false-alarm
        share.** On QS4 it made 4.7 findings a run against DeepSeek's 1.3.
        False alarms were 13 of 47 against 15 of 49.
      - **Most of its false alarms on prose read a choice that round 6's
        parcel or lead had recorded as a fault.** Seven of the 13 did so.
        Those choices were often recorded in files the run could not see,
        such as a parcel's own file.
      - **It sent back all five of QS4's real tips.** By round 6's classing
        only P4's carried a send-back, so Haiku was stricter than round 6, as
        it was on QS4h's P3 tip.
      - **It found a gap that round 6's merged record still carries:**
        - CS2#28, "a merge conflict is not two piles of text", is carried by
          no template;
        - yet ParcelRound's ADOPTION.md at `f42242e` names the checklists for
          it (verifier-HK4 confirmed it).

        It is ParcelRound's to fix in its next round.
    - **The line the judgements draw,** stated for any later scorer by
      verifier-HK4:
      - a true finding that calls a thing a limit or a gap counts new and
        true, even when round 6's parcel or lead recorded it;
      - a finding that calls a recorded choice a wrong answer or a restate
        counts a false alarm.
      - A count by truth alone would move several of the contestable false
        alarms.

## Cost

The meter's figures, from the committed spend file (`records/spend.jsonl`,
9,964 lines):

| suite | metered |
|---|---|
| QS1, both settings, every batch | $0.074 |
| QS6, ten batches and the stopped ones | $0.811 |
| QS4, 58 runs: 40 scored or capped, 18 left out | $8.652 |
| QS4h, 40 runs: 30 scored, 7 lost, 3 interrupted | $9.765 |
| the content filter's diagnostics, and probes | $0.003 |
| **all** | **$19.304** |

- **Each check the meter faced agreed with the bill, within its tolerance.**
  - The batches reconciled alone.
  - QS4's lanes, read together, agreed to the cent two minutes after the last
    call (14:08:26). A later read, after Logan's $20, was $0.08 short
    (18:47:34), inside the combined tolerance of $0.28. The usage export says
    where the $0.08 went, and it is still to come.
  - QS4h's lanes, read together, agreed to under a cent at 10.5 and 42
    minutes (07:54:20, 08:25:11), with 700 closed attempts unbilled.
- **Where the bill was lower, the price table was wrong, not the meter:** a
  Chinese public holiday is billed off-peak, at about half (18:35:19).
- **Of the $250 ceiling, $19.30 is spent.** The ceiling covers the measured
  models' API bills; the Claude sessions, the Haiku agents among them, are
  outside it (PLAN.md §5, decision 7).

## What the requirements and plan should say differently (proposed; Logan's to settle)

From the round's harness notes, which land beside this file. Each proposal
names the notes it rests on.

1. **A provider's behaviour is a measured property, in the record.**
   - The provider's calendar belongs in the price table (25).
   - A request closed with no reply is retried within a reserved budget
     (27).
     - Its rate is measured by request size (33, 50).
     - Whether it is billed is settled by an aggregate read well after the
       last call (46).
   - A connection reset before the reply's first byte is retried like a
     close. One after it is priced at its worst case (48).
   - A moderation refusal is classed apart from other errors, and replayed
     once with the last tool result reformatted (38).
   - A bill that several causes explain is named by none of them (28).
2. **Requests stay small, retries are priced by their own request, and lost
   runs are run again** (45, 50).
   - The allowance that bounds unmetered cost decided which runs survived,
     and the balance, not the drop rate, set the allowance.
   - The loop trims old tool output once a request passes a stated size.
3. **A run knows its budget** (39). The loop tells the model what is left of
   its turns and tokens, and asks for its report at the last mark. A run
   stopped at a cap is counted apart, never as "found nothing".
4. **Records name their code** (43). This was done in this round at
   `b79217a`, past a verifier: the commit, a changed flag and the tools'
   digest. Qwen's swap test depends on it.
5. **Inputs are checked where the model reads them** (42). The sandbox reads
   a probe from every mount before the first call, and refuses the run if
   one fails.
6. **The owner's desktop is the owner's** (41). Jobs run with no window,
   under a supervisor that names each one, at a priority the owner sets.
7. **A replay is judged by the original verifier's list** (44).
   - Each judgement names the item it applies.
   - A sentence that several runs flag is settled from its primary source
     before any verdict on it stands.
   - The screen's markers name the plant's own change (40).
   - A code plant registers the text whose promise it breaks, beside its
     edit's lines (49).
8. **Concurrent lanes are a mechanism, not a practice.**
   - The merge, the combined reconciliation and its record are code.
   - The flag that marks a batch concurrent is checked, not declared
     (verifier-P0r's K10 to K15).
   - The lanes keep one shared state for reruns (05:00:45).
9. **The owner's identifiers are scanned in every input** before it is
   mounted, and a run that holds one needs his recorded ruling (37).
10. **An owner's word that comes before the lead's gate is recorded against
    it,** with the gate's stop condition kept live (29). This happened twice:
    the retry's verifier ran beside the runs, and amendment 1 was approved
    before its verifier's verdict.
11. **The suites measure what the method needs of a model,** and code is part
    of it.
    - QS4's slice was prose, as Logan saw (12:41:38). QS4h, its code slice,
      was the first step.
    - REQ's QS3, real send-backs in cft-fp256's rounds, needs the builds a
      later round brings.
12. **Tests pin each record against its source** (47).
    - Each branch of a match has its negative case.
    - A module that re-implements another's guard is held to it by a
      differential test.
13. **A replay's rewriting of its record is checked against the record**
    (51). A cut in which one sentence names a commit as both the copy and
    the tip is refused.
14. **A file a verifier checks is frozen under its hash** (52). A settled
    version is a new file, and its entry names both hashes. In this round the
    lead overwrote its judgement drafts after their checks, so the checked
    versions can be traced only through the verifiers' own lists.

## The round's end

- **Qwen did not run.** Alibaba Cloud required ID verification before Model
  Studio could be used.
  - Logan, verbatim (18:12:17): "Alibaba is requiring ID verification, so we
    will move past that for now, we can continue building up the foundations
    using Deepseek and place Qwen into it (and the early suites) once the
    verification finishes".
  - So Qwen's swap test leaves this round. It runs on QS1, QS6, QS4 and QS4h
    once the verification finishes, and joins what the next round builds.
  - The QS6 key stays unpublished until then, so that test is not run
    against a published key.
- **The next round finishes Phase 0 on DeepSeek** (REQ §12.1): QS3 on
  recorded send-backs, QS9's seeds, the lead test's paper stage
  (Research/lead-test-for-round-2.md), and the first role-placement table.
  - Phase 1's core follows (18:24:09).
  - From 18:24 this session's parcels run on Sonnet and its verifiers on
    Haiku. That governs the Claude Code agents only, not the harness's
    measured models.
- **The close:**
  - the table script's QS4h section (`85c7c31`);
  - the records, the table's selection and the table (`9e9cd06`);
  - this case study and the harness notes;
  - the integration verifier's second pass;
  - the ledger archive.
- **Still open:**
  - the usage export, which settles QS4's $0.08;
  - the clones built for the runs and the Haiku packages, which are
    Logan's to delete.
