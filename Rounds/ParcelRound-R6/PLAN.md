# Round 6: ParcelRound brought to the method as practised (plan of record, draft 3)

Drafted 2026-10-02 by the lead (one Claude session, Opus 5.5). Logan settled
its four shaping questions. The plan goes past a verifier, then to him for
approval, before any commit to ParcelRound. Every default names what it was
derived from, so a reader can tell a principle being applied from the lead's
own judgement: the HonestHarness requirements' H16.1, applied by hand.

**Draft 2 answers verifier-plan's first check of draft 1.** It found 9
defects that would have changed what the round adopts or broken something,
and about 25 smaller ones. All are accepted. The material changes:

- **The templates are no longer split across four parcels.** brief.md and
  checklists.md each needed rules from all four, which breaks METHOD §2's own
  rule (M:81-83). They are now one wave-2 parcel, compiled from the merged
  METHOD.md, round 2's rules included.
- **Passages that other repositories quote are held word for word and exactly
  once, by the gate.** This covers loganw.dev's patterns, and HonestFramework's
  verbatim quotes of METHOD.md §5-§6 and README step 4.
- **The run-reuse adaptation no longer weakens the rule it replaces.** The
  author's own run is never reused, and the clean re-run of anything doubted
  stays.
- **The classification is corrected**:
  - CS3#18 and CS4#23 are now pending, because their practised parts are adopted under other ids;
  - CS3#17 is "in part", because its CI clause was never practised;
  - CS5#9 is origin-only.
- **Two dropped safeguards are now restored**: the three read moments, and the
  lead's cross-parcel read.
- **A privacy check runs before any push.**

**Draft 3 answers verifier-plan's re-check of draft 2.** It confirmed the
classification and 27 of its first findings answered, and found 10 more
defects. All are accepted. The changes:

- **Three items go beyond the four answers, and go to Logan by name**: B9, S2
  and S3 (see "Beyond the four answers").
- **P5 keeps template guidance METHOD.md does not state.** It marks that
  guidance as such and adds none of its own, rather than deleting correct
  rules.
- **Check 9 runs loganw.dev's own patterns as loganw.dev runs them**, instead
  of a whitespace-normalised count, which a rewrap could pass.
- **Check 2 is tightened, and its limits stated**:
  - `obs k` resolves only where a case study numbers its observations;
  - a named citation must open a heading or a bold-marked item;
  - an incident outside the case studies is cited as a Markdown link.
- **Check 10:**
  - keys its known exception per archive member and per domain, with a
    personal domain held only by its hash;
  - reads secret-shaped tokens too;
  - its commit-message branch now has a control.
- **P3's incident sentence is corrected**: the round-5 lead broke its plan's
  rule, and did not use the exemption.
- **ADOPTION.md is regenerated for this draft.** It has 113 rows, and a rule
  split across two sections names both headings.

The gate as built for this draft is `scratchpad\r6-p0-next\tools\check_method.py`.
On the base tree with ADOPTION.md, all 10 checks pass, and all 11 controls are
caught, the commit-message control included.

**After approval: verifier-P0's findings (2026-10-02, from 17:44).** P0 landed
at `a5c0494`, and verifier-P0 said NOT READY, with six defects. All are
accepted, and the ledger's lead.md records the rulings. What changed against
this draft:

- **ADOPTION.md's line numbers name their commit** ("both at `49a9266`"), and
  check 4 holds that every line number does.
- **The gate closes each gap as a class**, and its docstring states what
  remains, by the behaviour conceded. The changes:
  - links: wrapped, by definition, and exact case, with anchors;
  - citations: wrapped, every item resolving, and the archived ledgers pinned
    by hash;
  - proposals: the B, R and S ids are held;
  - refs: every section number in METHOD.md, README, ADOPTION.md and the
    templates;
  - quoted: loganw.dev's patterns, 28 in its page modules and (after verifier-P0's second
    pass) one in its relations.json, 29 in all, which replaces "Not listed"
    below, and the rendered text as well as the written;
  - privacy: HEAD's history, nested archives, file and member names, decoded
    text, and paths in commit messages; a file it cannot read fails; the path
    concession is pinned to the five archived ledgers; its output never
    prints what it refuses.
- **The record a cited time resolves against is the archived ledger's
  Markdown**, not its entry headings alone. METHOD.md's own citation of
  round 2's 11:47, when the suite started, written in the body of the 11:48
  entry, needs it. The old gate passed that citation only because case
  study 2's own wrapped citation leaked into its record.
- **The ledger holds no absolute path.** The briefs name `<repos>` and
  `<scratch>`, which each dispatch message defines.

## The order

Logan, 2026-10-02, verbatim: "Fold the gaps in, then we can perform a round
against ParcelRound (updating with the case study findings that were
practiced but not recorded) to get it to the current approach." The aim, same
message: "an ideal outcome is a system in which the core principles, once
hardened into the system itself, can effectively steer the model in the
authors original intentions without their significant feedback and more
importantly without cheating to still pass after things get harder."

## Logan's decisions (2026-10-02, verbatim, through the question tool)

| question | answer | derived from (as put; the full questions are in the appendix) |
|---|---|---|
| Scope | "Everything practised (Recommended)" | the order, read as "the current approach"; the survey |
| Departures | "Restore safeguards (Recommended)" | M:227-228 and M:440-444; HonestFramework §9; the aim |
| Models | "Sonnet / Opus (Recommended)" | SPEC decision 24; CS5:381-384 |
| New files | "Adoption file + gate (Recommended)" | HonestFramework §4, §3 and §10; CS4 obs 32 |

All four answers were the lead's defaults, which is the pattern of the
requirements' §3.4 and H16, recorded here as data. Where the verifier found the
classification wrong, the corrected one follows the rule Logan chose.

### Approved (2026-10-02, between 16:56:37 and 17:04:27 -0700, two clock readings bracketing the answer)

Logan, verbatim, through the question tool:
- on B9, "Adopt B9 (Recommended)";
- on S2, "Allow S2 with R5 (Recommended)";
- on S3, "Allow S3 with the test (Recommended)";
- on the plan, "Approve; P0 verifier rechecks (Recommended)".

So P0's verifier also re-reads draft 3's answers to the plan verifier's second
check. Every answer again took the lead's default, which is recorded as data
for H16.

### Beyond the four answers (to Logan by name)

The verifier found that draft 2 widened the answers in three places. Each is
put to Logan by name, with its default and its derivation:

| item | what it does | not covered because | default | derived from |
|---|---|---|---|---|
| **B9** | the owner's standing rules carried from round to round, into each plan's "How it is held" | the Scope option named six cft additions; B9 was not among them | adopt | practised in three rounds (REV7 lead:24-29, LANG lead:9, S6 lead:29). It is also the mechanism by which an owner's decision steers without being asked again, which is the aim |
| **S2** | the ledger's rules carried in every brief, the three read moments included, in place of a ledger README | the Departures option named four adaptations; S2 relaxes the template's README rule | adopt, with R5 as its condition | practised from the fixes round on (the survey's B7); its condition keeps the pull floor (M:381-386) |
| **S3** | the runtime tells the lead of escalations, in place of a watch | not among the four adaptations; it relaxes M:446-501's watch | adopt, with the channel watched to work as its condition | cft-fp256's lead kept no watch in the cert round (its lead.md:951); the condition (a test escalation at dispatch) is the lead's judgement |

## What the tree has (read 2026-10-02, read-only)

- **ParcelRound and its pending work.**
  - main is `8767e23` (2026-09-26), the same as origin/main.
  - METHOD.md: 798 lines, §§1-8, headings at lines 23, 79, 155, 301, 505, 590, 678 and 765. It last changed at `9b18e35` (2026-09-16).
  - The templates last changed on 2026-09-11, and carry none of round 2's adopted rules. For example, brief.md:12-15 names the base exactly, against M:149-151's "at or after".
  - There is no gate and no CI. The .gitignore comment (lines 6-8) calls the ledger "scaffolding, never history".
- **The round-5 branch.** `round5-case-study` (`49a9266`) is unpushed and a one-commit fast-forward of main.
  - It is checked out in a worktree in the loganw.dev session's scratchpad, idle since 2026-09-30 05:35. This round never touches that worktree.
  - CS5's "What carries forward" batch went past verifier-close in loganw.dev. That verifier said NOT READY on three earlier versions of the close entry (LVAL:1782-1806), and `d093ba6` answers its side note on `80c9f32`. The text read records no READY on the pushed version. Both commits are on loganw.dev's origin/main.
- **Others read this repository.**
  - **loganw.dev, at its pin, by regular expression; each pattern must match exactly once** (its facts.py:433-445).
    - README.md: the opening sentence; "## Is this for you?"; the "**Don't**" sentence; the "Two agents" sentence; "**twelve corrections from five parcels … corrected its brief**"; and *"Report anything you found that this brief got wrong."*
    - METHOD.md: "## 1. The one failure mode"; "The failure is that **the work between the parcels belongs to nobody**…"; and "**Exactly one file owns each shared fact; everyone else includes it.**"
  - **HonestFramework, through unpinned links**, presents these as word for word or "worth copying verbatim":
    - README step 4, "**Merge serially, run the full suite after each one, and read the log rather than the exit code.**" (WITH-PARCELROUND.md:36);
    - M:507, "**A gate that cannot fail is not a gate**";
    - M:585-586, "A control described but not run is worth nothing, so ask for its output";
    - M:600-601, "**re-run the gate itself**, from a clean build, rather than trust pasted output";
    - M:611-613, "**It must NOT fix anything.** A verifier that edits …";
    - M:621-624, "Require it to state what it actually ran, command by command, and make **"found nothing" an acceptable, unpenalised answer**" (its METHOD.md:305-306, 735-751).
  - **Also**: moth-quantum links "ParcelRound METHOD §2" (live), StoryDocs reads METHOD.md at `9b18e35`, and the HonestHarness requirements cite PR §1-§8 at `8767e23`.
  - **So**: §§1-8 keep their numbers and titles, and every passage above stays word for word and appears exactly once. The gate holds both (checks 8 and 9).
- **The evidence of practice** is the survey (practice-survey.md: 54 proposals, Table B, the departures).
  - Much of it is cft-fp256's gitignored `Data/runs/`, not public. Its docs/VALIDATION.md and docs/ROADMAP.md are public and pinned.
  - **The brief-errors line** is absent from all 37 parcel briefs, and both survey briefs, written in cft-fp256 since 2026-09-25, as read on 2026-10-02 at about 16:00.
    - The rule governs parcel briefs (M:227-228, §3), and the verifier briefs never carried it: 55 then, 56 by 16:44. Step 6 is live and still adding briefs.
- **Privacy.** Every commit in ParcelRound's history is authored with the owner's address. Commit metadata is public, and new commits add nothing new there. In files, the published `archive/round4-ledger.zip` (`b1e5956`) holds that address four times. Removing it needs a history rewrite, which is Logan's to decide (see "For Logan"). Round 5's archive holds only the public contact and example addresses.

## What it is not

- Not a rewrite: each section keeps its voice (a rule, the incident behind it, its citation, no invented illustrations).
- Not the adoption of anything unpractised: 15 proposals stay pending (below).
- Not an edit to any case study, except a dated postscript to CS5.
- Not a change to any passage another repository quotes.
- Not a push. GitHub moves only at Logan's word.

## Scope, by decision

### The 54 proposals of case studies 3-5

**Adopt (32):**

| case study | ids |
|---|---|
| CS3 | #1, #2, #3, #4, #5, #7, #9, #10, #11, #12 |
| CS4 | #1, #2, #3, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #15, #16, #17, #18, #20, #21 |
| CS5 | #1, #7, #10 |

**Adopt the practised part (7):**

| id | the practised part, and nothing more |
|---|---|
| CS3#6 | the lead watches the escalation channel continuously |
| CS3#8 | the lead's grants and rulings are on the verifier's list |
| CS3#13 | the round's cost reported as processed tokens, read from transcripts, as CS4:250-258 and CS5:290-333 did |
| CS3#14 | what the owner wants to see first, asked and recorded |
| CS3#16 | reuse under S6's conditions |
| CS3#17 | without its CI clause |
| CS4#4 | a figure the docs quote has a script in the tree |

**Pending (15):**

| ids | why pending |
|---|---|
| CS3#15, CS4#22 | no practice found |
| CS4#19; CS5#2, #3, #4, #5, #6, #9, #11, #12, #13 | practised only in the round that proposed them. For CS5#9, the only later use is the same session's front-page change that evening, which the lead rules part of round 5's practice |
| CS5#8 | not practised |
| CS3#18 | its practised parts are adopted as B17 and CS3#11 |
| CS4#23 | its practised part is the lead's small fixes past a verifier, adopted as CS3#7 and CS5#1 |

These counts (32 / 7 / 15) refine the survey's (34 / 8 / 9 / 3) by rulings the
verifier asked for; each ruling is stated in ADOPTION.md's row.

### Practices nobody proposed (the survey's Table B)

- **Logan's own rules:**
  - B3, the send-back rule, with its clause "A sentence that claims more than is true is restated at the merge, not left standing" (ODE lead:1057-1072);
  - B4, long runs handed back to the lead (REV7 lead:15);
  - resume notes at a pause, which are CS4#11 (S56 lead:380).
- **cft-fp256's additions practised in three or more rounds:**
  - B1, a verifier on the plan of record;
  - B8, the owner's decisions kept verbatim;
  - B9, the owner's standing rules carried round to round;
  - B10, merges re-made by the integration verifier;
  - B13, design first;
  - B14, the lead's own slips in every record;
  - B15, ledgers kept as the round's record;
  - B17, read-only surveyors before a plan.
- **Not adopted, each with a row in ADOPTION.md:**
  - B11, the plan restated before its verifier: practised once;
  - B12, the plan of record's sections: a project convention, and a template candidate;
  - B16, machine etiquette: project-level.

### Safeguards restored

| id | restoration | where |
|---|---|---|
| R1 | every **parcel** brief asks for "anything you found that the brief got wrong" (M:227-228). Verifier briefs keep their own open question, the "Anything else" item of templates/verifier.md's "Specific things to attack". Wave-1 text cites template sections, never template line numbers, since P5 moves the lines | — |
| R2 | a verifier forms its own view before it reads a parcel's self-report. M:440-444 is kept as written | — |
| R3 | the summary to the owner carries the cost, read from transcripts. M:704-707 is kept | — |
| R4 | the lead reads every author's file before each merge and at each wave boundary, so the cross-parcel view survives whatever replaces the whole-directory watch | M:463-469's purpose |
| R5 | the three read moments stay the floor, whatever carries the push | M:331-334; "push PLUS pull, never instead", M:381-386 |

### Adaptations allowed, with their conditions

| id | adaptation | conditions |
|---|---|---|
| S1 | the runtime's messages in place of `urgent/` | the ledger entry comes before the message; the brief says how to escalate without finishing ("message the lead and wait", FIX Q4:30); verifiers get only the lead's messages |
| S2 | the ledger's rules in every brief, in place of a README | every brief carries them, the three read moments (R5) included |
| S3 | the runtime tells the lead of escalations, in place of a watch | the channel is watched to work: a test escalation at dispatch must reach the lead; the record says how the lead learned of each escalation |
| S4 | one round branch | P0 lands on it before any parcel starts, and every worktree is cut from it. This qualifies M:107-108; it does not remove it. A gate runs after each merge, each merge is re-made, and main moves only to verified tips |
| S5 | parcels own the documents that describe their code | the documents that state the project's claims stay the lead's; every claim in a parcel-written document is on its verifier's list (CS3#9; round 3's six false-sentence defects, CS3:684-688) |
| S6 | reuse of a run instead of a fresh one | the run was made by someone other than the author of the work being verified. A parcel's verifier may reuse a long run the lead made for that parcel (B4); the verifier of the lead's own work may not reuse the lead's run (as FIX's F4 did, F4:69). Inputs must be identical, the hashes of the binaries the run used included. The verifier re-runs from clean anything it doubts. The full suite at the round branch's tip before main moves never reuses. M:600-601 stays word for word, with the exception written beside it |

## The shape

1. **This plan goes past a verifier** (B1), and then to Logan.
2. **P0, the lead's**, lands on a local branch `round6` cut from `round5-case-study`, before any parcel starts (S4). A verifier checks it before dispatch (CS4#1).
3. **Wave 1: four parcels, METHOD.md only**, one section group each, each with its own verifier.
4. **Wave 2: P5, the four templates**, compiled from the merged METHOD.md, with its own verifier.
5. **The merges are serial and the lead's.** The gate runs after each one.
6. **The lead's own work**:
   - README, .gitignore and ADOPTION.md's statuses;
   - CASE-STUDY-6.md, written from the ledger: its proposals get pending rows, and the gate declares its count;
   - a verifier on the integration and the record (CS3#7, CS5#1).
7. **main fast-forwards to `round6`** after the final gate and READY. The push is Logan's.

## P0

- **The base, and CS5's postscript.**
  - `round6` = `49a9266`.
  - One commit adds a dated postscript to CS5 on its "What carries forward" items, worded as above, plus the archive's push status once known.
- **ADOPTION.md** (new): one table holding every row.
  - The rows:
    - the 89 proposals of case studies 2-5, CS2#26 dated `868f95e`;
    - B1, B3, B4, B8, B9, B10, B13, B14, B15 and B17 (adopted);
    - B11, B12 and B16 (not adopted, each with its reason);
    - R1-R5 and S1-S6.
  - The columns: id · proposal · type · status · evidence · METHOD heading · template · parcel.
  - It is the current adoption state. A case study's heading records the state when it was written, and is not updated.
- **`archive/round6-practice-survey.md`**: the survey, with repository-relative paths (no `C:\Users` path), and `docs/` restored to cft-fp256's VALIDATION.md and ROADMAP.md paths. Its evidence column cites cft-fp256's public VALIDATION.md lines wherever the practice is recorded there.
- **tools/check_method.py** (new, standard library only).
  - Run as `python tools/check_method.py`, or `--control`, which plants one fault per check in a copy and requires each to be caught. Each check, and each of its limits stated by the behaviour it concedes:
    1. **links**: every relative link resolves.
    2. **citations**: every case-study citation in METHOD.md and templates/ resolves to its round's record.
       - The record is the case study's text, its own bracketed citations aside, and the round's archived ledger's entry headings. Round 2's lives only there; for example, M:575's 21:44 is round 2's lead.md entry.
       - The forms read: `[CASE-STUDY-n, …]`; bare stamps (round 2's in METHOD.md); `08:2x` and ranges; `§n`; and a heading or bold-marked item of the case study by its opening words (for example "the card day", a bold timeline entry); and "the ledger" for the archived ledger itself.
       - `obs k` resolves only under a heading where the case study numbers its observations: "What the method predicted, and what happened" in CS4 and CS5, and "Observations from the second round" in CS4. CS3 is cited by stamp or `§n`.
       - An incident recorded outside the case studies is cited as a Markdown link, which check 1 resolves. Two examples: `[round 6's survey, B3](archive/round6-practice-survey.md)`, and a link to cft-fp256's public docs/VALIDATION.md at a pinned commit.
       - Limits: a stamp of the right minute and the wrong event passes; a named citation passes if it opens any heading or bold item, right or wrong.
    3. **proposals**: every proposal in a case study's list has exactly one ADOPTION.md row.
       - The counts are declared, 35 / 18 / 23 / 13, plus CS6's at the round's end.
       - It counts top-level bold bullets plus bold-led paragraphs that are not whole-line section labels; CS3's eighteenth is such a paragraph (CS3:732).
       - Limit: a row with a wrong status passes.
    4. **anchors**: every row marked adopted names METHOD.md headings that exist; a rule split across two sections names both, separated by ` ; `. Limit: a row whose rule never landed under its heading passes.
    5. **refs**: every METHOD section a template cites exists. It reads the templates' own spellings, across line breaks: `[METHOD.md](../METHOD.md)` then `§3`, `section 4`, `§6`. Its control plants the wrapped form.
    6. **readme**: README links every case study and template.
    7. **brieferr**: templates/brief.md's report section contains "got wrong". Limit: the clause kept where nothing asks it (negated, or moved within the section) passes, so verifiers check it by name. A respelled clause fails it.
    8. **sections**: §§1-8 keep their headings, word for word.
    9. **quoted**: each passage other repositories quote must still match once.
       - loganw.dev's eleven patterns are run as loganw.dev runs them, copied verbatim from its page modules: `re.finditer(pattern, text, re.M)`, exactly one match. A rewrap that breaks one breaks this, and the control plants such a rewrap.
       - HonestFramework's six quotations are held as words (whitespace normalised), exactly once, since HonestFramework rewraps them in its own lines.
       - Not listed: loganw.dev's patterns on CASE-STUDY-2.md and -4.md. They are safe only because this round edits no case study they read; CS5's postscript is in a file loganw.dev doesn't read.
       - (Revised after verifier-P0: loganw.dev also reads CASE-STUDY-3.md, with two patterns, and LICENSE, with one, which this sentence missed. All 29 of its patterns through facts.prose() are now held: 28 from its page modules, and one from its relations.json, which verifier-P0's second pass found.)
    10. **privacy**: no email address, absolute personal path or secret-shaped token, in any file, archive member or commit message, beyond what is allowed.
        - Allowed addresses: the co-author trailer's, the public contact, and the reserved example domains (`.example`, `.invalid`, `.test`, `example.com` and the like).
        - The archived ledgers' personal paths are records and pass. Every other file, `archive/round6-practice-survey.md` included, is checked for paths.
        - `archive/round4-ledger.zip`'s addresses are a known exception, held per member and per domain with their counts. Your domain is held only by its SHA-256, and the third party's public contact at amazon.com is named.
        - Any address beyond the exception fails. An exception whose count no longer holds fails as stale.
        - Its commit-message branch has its own control, run in a throwaway repository.
        - Limit: a secret of a shape the check doesn't list passes, so secrets are also on every verifier's list by name.
  - **Built and tested in scratch** (`scratchpad\r6-p0-next\tools\check_method.py`): on the base tree with draft 3's ADOPTION.md and the relativised survey, 10 of 10 checks pass and 11 of 11 controls are caught.
- **METHOD.md's preamble** gets the citation convention for rounds 3-6 and a pointer to ADOPTION.md. Nothing else in METHOD.md changes in P0.
- **README** (the lead's): the table gains ADOPTION.md, tools/ and the front door. Step 4 of "the five-minute version" stays word for word, since HonestFramework quotes it. Step 3 changes only if S1 makes it untrue, and then only so that it stays true; HonestFramework paraphrases it (WITH-PARCELROUND.md:35).
- **.gitignore**: the comment on the ledger follows B15.
- **The round's ledger README is written fresh, stating this round's rules.** A copy of templates/ledger.md would command `urgent/` watchers and deletion, which this round does not use.

## Wave 1: METHOD.md only

Each parcel owns its sections by heading range, and touches no template. For
each of its rows in ADOPTION.md, it writes the rule, the incident behind it,
and its citation, in the section's voice.

### P1: §1-§3

- **§1:** read-only surveyors before a plan (B17). M:23 and M:26-27 stay word for word.
- **§1-§2:**
  - M:41 (in §1) stays word for word;
  - P0 past a verifier before the parcels that read it (CS4#1);
  - a measured trap becomes the next seam's refusal (CS4#2);
  - a tool's check that no stage runs is flagged (CS4#3);
  - CS4#4's practised part;
  - M:107-108 qualified for the round branch (S4).
- **§3, the brief's content:**
  - fast-forward to the base and check its SHA, and never switch another session's branch (CS3#17's practised part);
  - name a control by the property that makes it bite (CS4#5);
  - a scratch directory per agent, and no secrets (CS4#6);
  - the READY standard stated in the brief (CS4#7).
- **§3, the agent's own work:**
  - "what I did not do" is a claim (CS4#8);
  - an agent stops its own background work before reporting, which completes M:254-280 (CS5#10's agent half);
  - design first (B13);
  - parcels may own the documents that describe their code (S5's brief side).
- **R1:** the brief-errors line, with the cft-fp256 drift as its incident: 37 parcel briefs. The incident is cited as a Markdown link to round 6's survey, the form check 2 allows for evidence outside the case studies.

### P2: §4

- **Stamps** are substituted, in every brief. Correct "every guess ran ahead of the clock" with CS3:358-360 (CS3#2).
- **Questions** for the lead go through the escalation channel (CS3#3).
- **The ledger as record**: archived with its timestamps, and kept as the round's record (CS3#4, B15).
- **Watches**: re-arm and do a full read when a watch dies (CS3#5); the lead watches the escalation channel (CS3#6's practised part); arm it with the first dispatch (CS4#9); one watch at a time (CS4#10).
- **At a pause**, each agent records where it is (CS4#11).
- **Decisions** go in the ledger before the message (CS4#12).
- **Restored**: R2 (M:440-444, kept), R4 and R5.
- **Allowed**: S1, S2 and S3.

### P3: §5-§6

- **§5, gates:**
  - a gate that reads source text is a stated limit (CS4#13);
  - a limit is stated by the behaviour it concedes (CS4#14);
  - the lead's fixes go back to their verifier (CS4#15);
  - a control names its rule and restores its bytes exactly (CS5#7).
- **§5, the lead's own code:** the seam commits and fixes go past a verifier all round (CS3#7 and CS5#1, code half).
  - M:550-554's "where it is more than a line" goes, so the rule binds every commit.
  - The incident is round 5's: its plan had the rule with no exemption, yet the lead pushed eight substantial commits of its own past its own gate (an email gate, the list of edges, the ledger as a source), and a verifier then found gate-kind defects in three (CS5:110-125).
- **§6, what the verifier attacks:**
  - the lead's grants (CS3#8's practised part);
  - every claim in comments and docs (CS3#9);
  - side notes as a step (CS3#10).
- **§6, limits and claims:**
  - a stated limit is tested by an evading fault (CS4#16);
  - domain and quantifier are claims (CS4#17);
  - a figure carries its definition (CS4#18).
- **§6, runs and verdicts:**
  - B3, the send-back rule, with its restate clause and its classes;
  - S6, with CS3#16's practised part, beside M:600-601, which stays as written;
  - R2 cross-referenced from §6.
- **The quoted passages** at M:507, 585-586, 600-601, 611-613 and 621-624 stay word for word.

### P4: §7-§8

- **§7, the lead's records:** the lead's records go past a verifier, all round (CS3#7 and CS5#1, records half). Also in §7: B1, B8, B9, B10 and B14.
- **§7, the round itself:**
  - freeze what is audited (CS3#11);
  - check the gate budget against the merged diff (CS3#12);
  - what the owner wants to see first, asked and recorded (CS3#14's practised part);
  - a mid-round seam change against every open branch (CS4#20);
  - prepare the merge while the verifier works (CS4#21);
  - the lead checks for agents' leftovers (CS5#10's lead half).
- **§7, adaptations and restorations:**
  - long runs handed back (B4);
  - the round branch (S4's §7 side);
  - claims documents the lead's (S5);
  - R3, with CS3#13's practised part.
- **§8:** a send-back to an agent that cannot be resumed becomes a newly briefed agent, given its brief, final report, ledger file and worktree (CS3#1). M:786-790 stays, with this as its exception. Resuming the same agent remained the common practice (R4a lead:182, 344; ODE lead:581-583).

## Wave 2: P5, the four templates

- **Compiled from the merged METHOD.md**: every rule a template adds or changes is one METHOD.md states, and names its section. The gate's refs check holds the references.
- **The templates' own guidance is kept.** The templates already carry practical guidance METHOD.md states nowhere, for example:
  - "Keep it dense";
  - "stop and report … rather than inventing a different design";
  - "the regression this parcel is most likely to cause";
  - "Build only inside your own worktree";
  - "Seeded with whatever the lead already knows";
  - the verifier's "canonical past failure";
  - the ledger's entry format.

  P5 keeps it, marked as the template's own guidance, adds none, and deletes none unless METHOD.md now contradicts it. It lists those lines in its report as candidates for METHOD.md, which are Logan's to adopt. Deleting correct guidance would be a regression.
- **Brought up to the whole METHOD.md**, round 2's rules included:
  - the base "at or after" (M:149-151);
  - substituted stamps;
  - the staging and long-run rules.
- **The round's own changes**:
  - R1 in brief.md;
  - S1-S3 replace the `urgent/` watcher text;
  - "delete the ledger" goes;
  - the verifier template keeps "anything else", and gains R2, S6's conditions and the gate's limits by name. Naming a gate's limits on the verifier's list is how CS4#13 and CS4#16 are practised, and both are adopted. CS5#4, the general rule, stays pending.

## For every parcel

- **Must not touch**:
  - another parcel's sections;
  - README, ADOPTION.md, tools/ and .gitignore (the lead's);
  - any case study;
  - any quoted passage. A parcel that needs to change one escalates: it is another repository's, so Logan's.
- **Negative control, in a copy, never in the tree** (verifier.md:39-41):
  - run `--control`;
  - plant one unresolvable citation in a copy, and show the gate name it;
  - report both outputs.
- **First ledger entry: the intent echo**, compared by the lead before the first edit (a trial of H16.5). It states:
  - what the brief asks;
  - what the parcel owns and what it must not touch;
  - its control;
  - what would count as failing.
- **The report**:
  - the rows applied, each with its anchor;
  - the rows not applied, and why;
  - anything the brief got wrong.

### The traps

- **P1:** a rule in METHOD.md that brief.md lacks reaches nobody. That mechanism, measured on the ledger template, is CS3:355-362. So P1 writes §3 as the source P5 compiles from.
- **P2:**
  - write one escalation rule by its purpose and conditions, not two and not none;
  - S1 must not swallow R5;
  - the "urgent channel" passages HonestFramework paraphrases (WITH-PARCELROUND.md:35) must stay true in substance.
- **P3:**
  - the send-back rule makes "known limit" the place a cheat would hide, so CS4#14 and #16 must bind it;
  - "behaviour, not spelling" must not be written as a list of spellings;
  - M:600-601 and its neighbours are quoted elsewhere.
- **P4:** in four rounds of five the lead's own work reached main with no verifier (the HonestHarness requirements, §5.2). "All round" must bind merges and records, with P3 binding code.
- **P5:** a template rule METHOD.md doesn't state is a second source of truth. Each line names its section.

### Each verifier, on Opus

It forms its own view before reading the parcel's report (R2), and attacks:

1. each adopted rule against its proposal, incident and evidence;
2. a rule that claims more than its case study;
3. scope, by `git diff --stat` against the ownership;
4. a pending item written as adopted;
5. an invented illustration;
6. the gate's limits, by name: citations of the wrong event, wrong statuses, anchors without rules, and the brief-errors clause kept but not asked;
7. privacy, by name: no address or personal path in the parcel's diff or its ledger file;
8. the quoted passages;
9. anything else.

Light planted faults: one or two per parcel verifier, in a copy of the parcel's
tip, with the key under the three-commit protocol, and the tip kept out of the
ledger until the verifier reports.

## How it is held

- **Stamps** come from `date`.
- **The lead's work:** its code goes past a verifier (P3's §5 rule), and so do its records and integration (P4's §7).
  - The one exception is the last commit, which adds `archive/round6-ledger.zip` holding the final verifier's report.
  - That commit is checked mechanically instead: each archived file must hash equal to its working copy.
- **The ledger comes first:** every decision and message is in the ledger before it is sent.
- **Scratch:** each agent has its own scratch directory, and no secret or personal data goes in any brief or ledger. The privacy check (10) holds addresses, personal paths and secret-shaped tokens before main moves. A secret of another shape is outside it, so every verifier checks for secrets by name.
- **READY** is stated in every brief.
- **Verifiers:**
  - must not fix anything, and "found nothing" is acceptable;
  - report when the list is exhausted;
  - read a committed SHA;
  - get only the lead's messages.
- **Every agent:**
  - "what I did not do" is a claim, and the lead audits each worktree after each agent;
  - stops its background work before reporting;
  - records where it is at a pause.
- **Models:** each agent's model is read from its transcript.
- **The send-back rule** is Logan's, of 2026-09-27 (ODE lead:1057-1072): only a regression or a wrong answer sends work back; anything else merges as a recorded known limit, and a sentence that claims too much is restated at the merge. For this round, in the lead's mapping, after the steps-5-and-6 round's form (verifier-W1:58-64):
  - a wrong answer is a rule that misstates its source, or an item adopted that the scope excludes;
  - a regression is a correct rule removed, or a quoted passage broken.
- **Dry-run notes:** every rule the lead applies by hand goes in harness-notes.md.

## The ledger and workspaces

- **The ledger:** `<repos>/parcelround-r6-ledger/`, outside every worktree. (`<repos>` is the owner's
  local directory of repositories; each dispatch message defines it.)
  - One file per author, append only, and a fresh README stating this round's rules.
  - Escalation uses the runtime's messages, ledger entry first. A test escalation at dispatch shows the channel works.
  - At the end it is archived as `archive/round6-ledger.zip`, after the privacy check (10).
- **The worktrees:** `<repos>/parcelround-worktrees/{P1,…,P5}`.
  - Each is cut from `round6`: P1-P4 at P0's tip, P5 at wave 1's merge.
  - Each is checked before dispatch: `git remote -v`, `git log -1`, and a probe for a string only its base contains.

## Decisions at their defaults unless Logan says otherwise

| # | decision | default | derived from |
|---|---|---|---|
| 5 | Base: CS5 merged in, with its postscript | yes | Logan, 2026-09-30: "Archive the notes into ParcelRound with a case study doc regarding this round" |
| 6 | Planted faults | light, one or two per parcel verifier | loganw.dev SPEC decision 20 ("can be light on this project", meaning loganw.dev's prose round), extended to this prose round by the lead's judgement; HonestFramework §9 |
| 7 | The record | CASE-STUDY-6.md, short, from the ledger, verified | CS5#11 (practised in round 5); every round since round 1 |
| 8 | Push to GitHub | held until Logan says | the requirements' H10.2 |
| 9 | Deleting the round-5 ledger's working copy and its worktree | held until Logan says | CS5:440-441; deletions are the owner's |
| 10 | The intent echo | on | the lead's judgement: one ledger entry per parcel |

## For Logan, outside this round

1. **The published round-4 archive** holds your personal address four times. It adds nothing beyond the commits' author field, which carries it on every ParcelRound commit, but it breaks the rule round 5 applied to files. Removing it needs a history rewrite and a force push. Your call; this round only stops new ones.
2. **HonestFramework quotes ParcelRound through unpinned links.** This round keeps every quoted passage word for word, but HonestFramework's paraphrases of §2, §4 and §6 (WITH-PARCELROUND.md:32-38) will describe the method as it was. Re-reading them after this round lands would be a change to HonestFramework, so it's yours to schedule.
3. **When loganw.dev's ParcelRound pin moves**, its patterns re-read the passages above. The gate's check 9 is what keeps each one matching exactly once.

## Time and cost (an estimate, not a measurement)

- **Time:** P0 and its verifier, one to two hours; wave 1, about an hour; wave 2, about an hour; then the merges and the record. Several hours of wall clock.
- **Checking share in earlier rounds**, each by its own measure:

  | round | checking share |
  |---|---|
  | 2 | its verifiers were 38% of the agents' tokens, from the agent cards (CS2) |
  | 3 | every checking role was 47.4% of output (CS3) |
  | 4 | its verifiers were 42% of the agents' output (CS4) |
  | 5 | its verifiers were 57.8% of the agents' output: 431,537 of 746,520. Counting the lead's output too, that is 21.3% (CS5:292-310) |

  This round's share will be read from its transcripts.

## Appendix: the four questions as put (2026-10-02)

1. **Scope.** "Which practised material should round 6 write into ParcelRound's METHOD.md and templates?"
   - **Everything practised (Recommended)**:
     - adopt the 36 proposals practised in a later round, plus the practised part of 7 more;
     - add your own recorded rules (send-back rule, long runs handed to the lead, resume notes, decisions kept verbatim);
     - add cft-fp256's additions practised in 3+ rounds: a verifier on the plan, design-first approvals, merge-tree re-makes, the lead's own slips, ledgers kept as records, read-only surveyors.

     Never-practised proposals stay pending. Derived from: the order read as "the current approach", and the survey's evidence. The counts were later corrected to 34 + 8, and then refined to 32 + 7 by draft 2's rulings.
   - **Proposals and your rules**: cft-fp256's other habits wait for a case study of their own.
   - **Practised proposals only**: the strict reading.
2. **Departures.** "Where cft-fp256's practice replaced a METHOD rule, what should METHOD say?"
   - **Restore safeguards (Recommended)**:
     - restore the brief-errors line and the verifier's independent first view;
     - record as allowed shapes, with conditions, the adaptations that keep a rule's purpose: direct messages (ledger entry first), one round branch, parcels owning their code's docs, reuse of identical-input long runs.

     Derived from: M:227-228 and M:440-444, HonestFramework §9, and the aim.
   - **Record practice as is.**
   - **Keep METHOD, list drift.**
3. **Models.** "Models for round 6's agents?"
   - **Sonnet / Opus (Recommended)**: parcels on Sonnet; every verifier, and the lead, on Opus; each agent's model read from its transcript. Derived from: SPEC decision 24, and CS5:381-384.
   - **All Opus.**
   - **Sonnet / Fable**: a small test of verifier independence (H15.3).
4. **New files.** "New files in ParcelRound: an adoption record and a small gate?"
   - **Adoption file + gate (Recommended)**: derived from HonestFramework §4, §3 and §10, and CS4 obs 32.
   - **Adoption file only.**
   - **Neither.**
