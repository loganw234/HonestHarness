# Harness notes, the muse-softfloat study

Each note gives what the lead did by hand, and what would make it a mechanism.
- The lead wrote them at the study's close, from the ledger, and each cites its entries by time on 2026-11-08 unless dated otherwise.
- The report's section "What running this study showed about the methods" covers the methods. These notes cover the harness and the lead's own practice.

1. **The harness refuses a subagent's report file.**
   - Claude Code refused verifier-PL's `report.md` (08:30:26) and P3's `ANALYSIS.md` (09:34:05).
   - So each parcel sent its text as messages in numbered parts. The lead wrote each file verbatim and recorded its hash, and the parcel read it back (09:36:39, 09:38:17 and 09:41:11).
   - **Mechanism:** a write grant for the agent's own report path. Or a tool that writes a message's text verbatim to a named file and returns its hash.
2. **A fence by instruction was crossed twice by traversal.**
   - verifier-PL's `find` was the first (08:30:26). The README then had searches name their directories (08:37:28).
   - P2's recursive `git ls-tree` was the second (09:31:32), and the pathspec rule followed.
   - Both agents disclosed it themselves, and neither read content. But the pathspec still works only if each agent chooses to use it.
   - **Mechanism:** agents read the library through a copy whose tree omits the fenced folders, so no listing can reach them.
3. **The shared ledger exposes the planting style.**
   - A planted-copy verifier's findings describe its copy's plants to any other verifier that reads them.
   - So the lead held every grading and send-back until the last planted-copy verifier had reported (10:00:16).
   - **Mechanism:** each planted-copy verifier's ledger file stays unreadable to the others until the reveal.
4. **Writable files in Temp do not last.**
   - Round 2's old scratch directory had lost every writable file within about two weeks.
   - This session's scratch sits in the same Temp tree. So in its first hour the study moved its durable files to the ledger and to the lead's own folder outside Temp (08:19:53).
   - **Mechanism:** a study's README names its durable places from the start, and scratch holds only what can be lost.
5. **The reinstalled Miniconda breaks the tests through `SSL_CERT_FILE`.**
   - Its activation script sets the variable to a file that a Windows install lacks, and two tests failed on it (round 2's ledger, 2026-10-26 10:04:27).
   - Every gate of this study ran with the variable removed by name.
   - **Mechanism:** before the tests, the gate checks that `SSL_CERT_FILE`, if set, names a file that exists, and refuses with that reason if not.
6. **The gate outran the shell tool's limit.**
   - At `23b0267` its tests took 11 min 43 s, past the tool's 10 minutes, and the tool moved the run to the background (13:16:42).
   - The lead waited for its notice and started no second run. The next gate ran in the background from the start.
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
9. **Two counts of the same thing disagreed.**
   - `grep -c` counts lines and `grep -o` counts matches. For one report they gave 4 and 5 (13:02:05).
   - **Mechanism:** each count is recorded with its command.
10. **A context compaction fell between a report's arrival and its filing.**
    - The lead recovered verifier-C's first report, verbatim, from the session's own transcript, to file it. The ledger's entry for these notes says how.
    - **Mechanism:** each report is filed verbatim the moment it arrives, before any other step.
