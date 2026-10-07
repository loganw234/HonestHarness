# HonestHarness round 1, amendment 1: QS4's code slice, on this round's own planted copies

It adds to the plan of record (`PLAN.md`, `2357035`, approved 2026-10-06).
It changes nothing already run. Logan approved it on 2026-10-07 (the round's
ledger, 12:48:48), before its verifier's verdict. verifier-A1's corrections
of fact and its gaps are applied below, under that approval (13:38:18); none
changed a decision of his.

## A1.1 Why

- **Logan's ruling** (12:41:38): Qwen waits until all of DeepSeek's runs
  finish, so that Qwen meets one full suite at once. That makes Qwen's step a
  test of swapping the model and nothing else, recording whatever breaks. It
  followed his point that the round's trials were mostly documentation-level.
- **That point holds.** QS4 so far replays round 6's planted copies, and
  their ten plants are all prose. The models ran code along the way, but no
  score rests on it, and QS1 and QS6 do not test verification.
- **REQ's QS4 plants code faults.** This round has four planted copies of
  code and suite data. Their keys are published (22:00:27), and there is a
  baseline: the Sonnet verifiers caught all 8 plants, each in its first pass.

## A1.2 The items

Four planted copies, and their four real tips as the false-alarm set. The
times are 2026-10-06, the stamps of the lead's entries that record each copy
and its sealed hash.

| parcel | copy | real tip | base | stamp | plants (`keys/`) |
|---|---|---|---|---|---|
| P1, QS1 | `17f9d9f` | `8d6ba72` | `929d6e5` | 13:42:27 | A: a golden that contradicts its own case, two edits of `qs1_cases.json`. B: `special_tokens` no longer reads a call's name (`qs1.py`) |
| P2, the loop | `8214694` | `ceef2e2` | `0692de3` | 13:53:53 | A: the malformed-call streak is never reset. B: the run budget is checked only before model turns, a deletion (`loop.py`) |
| P3, QS6 | `83ee196` | `beb6176` | `6f0d928` | 17:29:08 | A and B: two items whose question and cited evidence disagree (`qs6_items.json`) |
| P4, QS4 | `3b1b3cd` | `5ecd02b` | `7b0dc64` | 20:21:45 | A: the prompt tells every run that its copy holds two plants (`qs4_prompt.md`). B: a planted item passes on one plant of two (`qs4.py`) |

- Four plants are logic in Python, and four are in suite data or a prompt.
- **The real tips hold real faults,** which this round's verifiers recorded:
  verifier-P2's F3 and F4, for example, fixed before P2's merge. A finding on
  a tip is judged against that list, not assumed false.
- **The items are named apart from QS4's round-6 items:** `h1` to `h4`
  (HonestHarness), each planted and real.

## A1.3 What each run has: what that verifier had

- **The repository, one commit above the base in both conditions.** The
  plants are found by reading, not by the shape of the history.
  - **A planted copy** is rebuilt from its key, and must reproduce
    `copy_commit`, or the item stops. Its parent is the base. Its tree is
    the real tip's tree with the key's plants. Its message is the oldest
    commit above the base, and its author and committer lines are the real
    tip's. verifier-A1 found this rule reproduces all four copies exactly.
    QS4's rule, which keeps the tip's commit and changes only its tree,
    reproduces P2's and P3's but not P1's or P4's, which were squashes.
  - **A real tip** is built by the same rule with no plants: one commit
    with the real tip's tree.
  - **Either is read-only,** and holds only the objects its commit reaches,
    under QS4's guard.
- **This round's ledger, cut at the stamp,** by QS4's rule, without `keys/`
  and without the parcel's own file (`P1.md` to `P4.md`).
  - **Both SHAs are mapped.** In every cut, the real tip's and the copy's
    short and full SHAs become the item's own commit, so that both
    conditions read alike. This round's entries name the real tip, where
    round 6's named only the copy, so QS4's cut check would refuse every
    planted item as it stands.
  - **The shared briefs as dispatched.** `briefs/_verifier.md` and
    `briefs/_common.md` changed after P1's and P2's dispatches, by the
    desktop-priority item added at 15:35:17 and amended at 16:39:34. The
    ledger keeps no history of them, so for P1 and P2 they are rebuilt
    without that item, and the rebuild is recorded as an adaptation.
- **The briefs each verifier read before its view:**
  - `briefs/_verifier.md`, `briefs/_common.md`, `briefs/P<n>.md` and
    `briefs/verifier-P<n>.md`;
  - QS4's adaptation: escalation becomes the report tool, and the
    verifier's ledger file becomes a file in the writable scratch.
- **The outside sources each verifier read,** each at a commit or a digest:
  - **P1:** DeepSeek's documentation copies (D8 to D10), at the versions
    that existed at its dispatch, by digest. The first conversion of D10 is
    lossy (10:50:11).
  - **P2:** ParcelRound at `f42242e`.
  - **P3:** round 6's ledger archive, QS6's source, pinned by QS6, and
    `ds/quick_start_token_usage.txt` by digest.
  - **P4:** ParcelRound at `f42242e`; the twelve files of cft-fp256,
    HonestFramework and loganw.dev at QS4's pins; and HonestHarness's plan
    at `809ed2f`.
  - The builder lists each from that verifier's own ledger file.
- **The dispatch message,** rebuilt from the lead's entries, with roots in
  place of paths.
- **Withheld, a stated limit: QS6's answer key.** verifier-P3 was given it
  (17:29:08). It stays out because it is QS6's held-out key. Without it, plant
  A shows from the items file alone, and plant B from round 6's ledger
  (A1.10, item 4).

## A1.4 The sandbox image

- **P2's pinned `python:3.12-trixie`, with the project's dependencies
  installed when the image is built,** since the sandbox has no network.
  - The project imports httpx, jsonschema and pytest, and calls `git`.
  - Their closure on Linux is 18 PyPI packages, pinned by version (verifier-A1,
    13:38:18).
  - The lead records each download's name, source and size before it
    happens, under Logan's standing clearance for downloads (2026-10-06).
- **Inside, there is no Docker.**
  - In verifier-A1's offline run of the whole suite, with no `docker` and no
    network, 712 passed, 34 skipped and none failed.
  - All 8 plants could be shown there, by tests written in scratch. P3-B
    needs round 6's ledger mounted.

## A1.5 The score and the comparison

- **The screen:**
  - **Each plant's spans are pre-registered from the line diff** of the
    copy against its real-tip build.
  - A deletion locates at its join, with a widened tolerance (P2-B).
  - A plant of several edits holds one span per edit (P1-A).
  - QS4's current data holds one span per plant, anchored on the new text,
    so as it stands it would place P2-B at line 1.
- **The judgement:**
  - The lead judges each plant and finding against this round's recorded
    verifier findings, by round 6's verifier list, as for QS4's judgements.
  - A Sonnet verifier checks each judgement.
  - The squashed copies' stale first-commit messages are real findings,
    recorded by verifier-P1 and verifier-P4 (F3), not plants.
- **The comparison is the Sonnet verifiers' 8 of 8 on the same copies.** For
  real findings, it counts only those recorded in each verifier's view,
  formed before it read the parcel's file.

## A1.6 The runs and their cost

- **Four passes of the eight items,** in lanes reconciled together (09:32:39),
  at QS4's caps. They run from a clone at the commit that records the code
  (A1.8).
- **Cost.** QS4's batches have averaged $0.138 each: $0.077 planted, $0.194
  real. So 32 runs come to about $4 to $6. The estimate is replaced by
  measurement after the first pass.
- **The balance binds, not the ceiling.**
  - Each dropped attempt reserves the dearest call QS4's caps allow, $0.74.
  - At N = 23 a batch reserves $23.87 off-peak, and $29.93 with
    `--allow-peak`.
  - After Logan's top-up of about $10 (13:26:42), the balance is about $34.
  - QS4's lanes lost P5's real tip three times at N = 23 (13:33:50).
  - **The lead's default: N = 28, off-peak.** A batch then reserves $27.58,
    which the balance holds for the whole slice. A run the provider ends
    runs again once, at the largest N the balance then holds.
  - A further top-up allows more. The round's harness notes, which land
    beside this file at the round's end, propose pricing each retry at its
    own request's worst case (note 45).

## A1.7 Who builds it

- **P5, on Opus.** It extends QS4's tools to a second source, this round's
  ledger and HonestHarness's history:
  - the rebuild rule of A1.3, both kinds;
  - the cut, with its SHA mapping and the rebuilt briefs;
  - the items, the pre-registered spans and the expected hashes;
  - the image's build, and its tests.
- **Its verifier works on a planted copy, on Sonnet,** under the three-commit
  protocol.

## A1.8 Before the runs: records name their code

- Done at `b79217a` (12:57:43): record version 2 carries the commit, a
  changed flag, and a digest of the tools as the requests sent them.
- verifier-P0v checks it.
- Without it, Qwen's swap test cannot tell a change Qwen needed from a change
  made between the runs (11:37:12).

## A1.9 Logan's answers (12:48:48)

1. HonestHarness's history may go to DeepSeek and Qwen in this replay, his
   address in its author lines, as ParcelRound's did in QS4 (03:00:44).
2. He tops up again. He did, by about $10 (13:26:42).
3. The amendment is approved, with its defaults.

## A1.10 Limits, each stated by the behaviour it concedes

1. **QS4's own limits carry over** where they apply, each by its number in
   QS4's module:
   - no network (1);
   - a file that postdates the cut is absent (3);
   - the replay's `date` (4);
   - the read-only copy (5);
   - the tools (6);
   - the screen, and location by file and lines (7, 8);
   - the per-call cap (13);
   - the fixed reply to an escalation (14);
   - reasoning returned with each request (16);
   - mount paths that show host names (17).
2. **This round's verifiers worked in Claude Code, on the host.** They ran
   mutation pools of up to 12 workers, real containers, and a registry read.
   The replay's model works in P2's sandbox: 2 CPUs, 2 GiB, 300 s a tool
   call, no network and no Docker. The sandbox's speed on these tests is
   unmeasured until the first run.
3. **The false-alarm set is told that plants exist.** This round's
   `_verifier.md` and the dispatch entries say the copy holds planted faults,
   where round 6's brief said "may". Every real-tip run reads that, of a
   repository that holds none.
4. **QS6's answer key is withheld.** P3-B then shows only by reading round
   6's ledger: its cited lines are stamped past the question's 18:00. The
   baseline also compared a derived answer with the key.
5. **The replay reads its own machinery.** P4's copy holds QS4's prompt
   template and its screen: the rules that frame and score the replay.
   P1 to P3 hold smaller parts of it: the suites, and the loop that runs it.
6. **The rebuilt shared briefs** (A1.3) cannot be checked byte for byte
   against what P1's and P2's verifiers read.
7. **Each cut holds the lead's entries up to its stamp,** with both SHAs
   mapped. Its dispatch message is rebuilt from summaries, not verbatim. The
   cut reproduces what the verifiers report reading: lead.md at P3's stamp
   is 1,280 lines, as verifier-P3 says, and at P4's 1,686 against
   verifier-P4's 1,685.
8. **A1.8's fields exist only on records written after `b79217a`.** The live
   entry's flags (`--max-unmetered`, `--retry-delays`, `--concurrent`) are in
   no run record; the batch summary keeps the allowance's margin.
9. **Contamination.** DeepSeek's models predate this round by release date.
   For Qwen, the same check by release date. A model trained after the
   ledger and `keys/` are published has the plants.
10. **The baseline is Sonnet's,** each verifier on its first pass. Opus did
    not verify these copies.
