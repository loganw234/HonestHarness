# Harness notes, the muse-softfloat study

Each note gives what the lead did by hand, and what would make it a mechanism.
- The lead wrote them at the study's close, from the ledger. Each cites its entries by time on 2026-11-08, unless dated otherwise. A time is an entry of the lead's `lead.md`, unless the note names an agent's own file.
- This is draft 3. Draft 2 took verifier-N's pass 1, and draft 3 takes its pass 2 (`reports/verifier-N.md`). The lead made draft 3's changes and checked each by command, since verifier-N's passes were spent (14:24:39).
- The report's section "What running this study showed about the methods" covers the methods. These notes cover the harness and the lead's own practice.

1. **The harness refuses a subagent's report file.**
   - Claude Code refused four writes:
     - verifier-PL's `report.md` (08:30:26);
     - P2's and P3's `ANALYSIS.md` (P2's own file, 09:34:00; 09:34:05);
     - P1's, with a draft in P1's scratch directory (09:41:11).
   - The agents could write their scripts and tables. Only report-like prose was refused (09:34:05). An Edit to an existing file was accepted, for P3's own one-line correction (10:06:34).
   - So each parcel sent its text as messages in numbered parts. The lead built each file from them and recorded its hash (09:36:39, 09:38:17 and 09:41:11). It removed only each part's header line, and joined the parts with one blank line.
   - Each parcel read back the file the lead wrote, by its hash (P3's own file, 09:46:32; P1's, 09:47:27; P2's, 09:51:12). P1 and P2 checked its structure and sections, not each byte against their messages.
   - P3 then changed one line before it committed, a correction it disclosed (09:48:41).
   - The revisions took the same road.
     - P1 and P2 sent their changed lines. The lead applied each one where its old text occurred exactly once (10:07:34, 10:10:17).
     - P3 edited its own file (10:06:34).
   - **Mechanism:** a write grant for the agent's own report path, its scratch drafts included. Or a tool that writes a message's text to a named file, applies a parcel's line changes, and returns the file's hash each time.
2. **A fence by instruction was crossed twice by traversal.**
   - verifier-PL's `find` was the first (08:30:26). The README then had searches name their directories (08:37:28).
   - P2's recursive `git ls-tree` was the second (09:31:32), and the pathspec rule followed.
   - Both agents disclosed it themselves, and neither read content. But the pathspec still works only if each agent chooses to use it.
   - **Mechanism:** agents read the library through a copy whose tree omits the fenced folders, so no listing can reach them.
3. **A shared ledger can expose the planting style.**
   - A planted-copy verifier's findings, in its own ledger file, describe its copy's plants.
   - The other verifiers were told to read only `lead.md`, the README and their own parcel's file. So the style was fenced from them by instruction alone (10:00:16). No entry records a verifier reading another's file.
   - The lead also held every grading and send-back until the last planted-copy verifier had reported (10:00:16).
   - **Mechanism:** each planted-copy verifier's ledger file stays unreadable to the others until the reveal.
4. **Writable files in Temp do not last.**
   - Round 2's old scratch directory had lost every writable file within about two weeks.
   - This session's scratch sits in the same Temp tree. So in its first hour the study moved its durable files to the ledger and to the lead's own folder outside Temp (08:19:53).
   - **Mechanism:** a study's README names its durable places from the start, and scratch holds only what can be lost.
5. **The reinstalled Miniconda breaks the tests through `SSL_CERT_FILE`.**
   - Its activation script sets the variable to a file that a Windows install lacks, and two tests failed on it (round 2's ledger, 2026-10-26 10:04:27).
   - The lead's entries name the variable as removed for its gates in S0. 08:11:55 sets the rule, and the gate entries run from 08:17:33 to 14:20:38.
   - The parcels' common brief gives them the same command (`briefs/_common.md`). P1's and P3's ledger files name it as a next step, but no parcel's record of a gate says how the gate ran (14:24:39).
   - **Mechanism:** before the tests, the gate checks that `SSL_CERT_FILE`, if set, names a file that exists, and refuses with that reason if not.
6. **The gate outran the shell tool's limit.**
   - Earlier, a gate ran detached, by the lead's slip of backgrounding it twice. Its end was then waited on by a polling loop on its log (11:03:40).
   - At `23b0267` its tests took 11 min 43 s, past the tool's 10 minutes, and the tool moved the run to the background (13:16:42). The lead waited for its notice and started no second run.
   - The gates after that ran in the background from the start (13:39:25 and 13:56:42).
   - **Mechanism:** the gate runs in the background by default and reports by notice. Or it has a quick mode for commits that change only text, which prints the checks it skipped.
7. **A verifier quoted a fragment of the owner's home path.**
   - verifier-C wrote it in its ledger file as a search pattern (its entry of 12:46:17), and flagged it itself (12:46:31).
   - Neither this repository's privacy patterns nor ParcelRound's find anything on that line. The ledger is append-only, so the archived copy carries the line redacted (13:02:05).
   - **Mechanism:** a ledger-append tool that refuses an entry with the owner's name beside a path word.
8. **The lead's account of its own comparison overclaimed.**
   - Its draft 1 listed two findings as found only by the Claude audits, which the Muse audits had found too.
   - Its ledger entry said it mapped the audits' High and Medium findings. It mapped every High, but not every Medium.
   - The lead found both while checking verifier-C's findings (13:02:05):
     - the first by reading P2's whole table;
     - the second by a script over the audit copies.
   - **Mechanism:** keep the crosswalk of finding IDs as data, and compute every "only" or "all" claim from it.
9. **A count was given the wrong name.**
   - The 12:28:59 entry gave "2 and 4 times". By the counts the lead recorded at 13:02:05, those are matching lines: one report has 4 matching lines and 5 matches.
   - The lead's account of its commands came after both counts, at 14:06:42: `grep -c` for the lines, and `grep -o` piped to `wc -l` for the matches. No entry records the command of the 12:28:59 count.
   - **Mechanism:** each count is recorded with its command, when it is made.
10. **A context compaction fell between a report's arrival and its filing.**
    - The lead recovered verifier-C's first report, verbatim, from the session's own transcript, to file it (13:39:25).
    - **Mechanism:** each report is filed verbatim the moment it arrives, before any other step.
11. **The lead wrote into the tree its gate was reading.**
    - It wrote `harness-notes.md` into S0 while S0's gate ran, and moved it out during the tests (13:39:25).
    - The gate's privacy count showed that it had not read the file.
    - **Mechanism:** the gate checks a snapshot of the tree it is given, or refuses if the tree changes during its run.
12. **The planted copies were built and keyed by the lead's own script.**
    - The lead's `make_copy.py` built each copy (09:48:41, 09:50:30 and 09:52:36):
      - a `--no-local` clone of `study-muse` alone, with no remote;
      - one commit on the base, and no object of the parcel's commit.
    - The script exits with "CHECK FAILED" unless the files that differ from the parcel's commit are exactly the planted ones (14:24:39). The entries record the counts it found: 3 of 38 files for P3, 2 of 42 for P1, and 3 of 28 for P2.
    - The lead recorded each key's hash here before dispatch, and kept the keys in its own folder until the last planted-copy verifier had reported.
    - **Mechanism:** the method's own tool builds the copy, checks it, and commits the key's hash, in one step.
13. **The lead lifted a fence for itself.**
    - After the report's draft 3, the lead lifted the fence on the Claude audit reports for itself alone (11:12:13).
    - It found the reports on GitHub only, and asked Logan before downloading them (11:13:44). He approved (12:22:43).
    - **Mechanism:** a tool checks a fence's lifting condition, such as a recorded READY. And a fetch runs only on the owner's recorded approval.
