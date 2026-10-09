# Harness notes, HonestHarness round 1

Each note: what the lead did by hand, and what would make it a mechanism.
Written by the lead as the round ran. The case study's proposals name the
notes they rest on.

1. **Fixtures typed by hand were wrong.** Three of the guard's expected
   costs (1.416, 0.708, 0.00534) were mistyped; the code disagreed, and
   independent hand arithmetic gave 2.016, 1.008, 0.005324. A fixture holds
   only where two computations agree. Mechanism: fixtures carry their
   derivation (rates times tokens, written out), and the gate recomputes it
   with a second, independent routine.
2. **A realistic test found a runner bug.** The first routing test used
   usage beyond its caps; making it realistic showed a mid-batch guard
   refusal raising instead of stopping. Mechanism: test fixtures drawn from
   recorded shapes, never invented sizes.
3. **A lossy doc copy.** `ds/chat_completion.txt` dropped collapsed parts of
   D10, `tool_choice`'s rule among them; the html held it. A verifier judging
   the adapter against the txt could have called a documented rule
   unsupported. Mechanism: doc copies are made by one converter that keeps
   every text node, and checked by counting field names in source and copy.
4. **A correction that was itself wrong.** Correcting a line number, the
   lead took the first "required" line in the file (31) instead of the one
   before the quote (463). A value read by command is only as good as the
   command's selection. Mechanism: a citation tool that finds a quotation's
   span by exact match over joined text and prints the range with its text.
5. **`grep -c` exits 1 on zero matches**, which stopped an `&&` chain before
   a ledger append. It failed safe, and only the missing echo showed it.
   Mechanism: a ledger-append tool that reports success or failure itself.
6. **Test escalations arrived within a minute of dispatch**, with no watch
   armed (S3 holds again, as in round 6).
7. **A verifier's first heading printed the date format** instead of the
   time (a doubled % in its printf). It corrected it with the file's
   modification time. Mechanism: a ledger-append tool that stamps entries
   itself, so no agent composes the stamp.
8. **The runtime's token figure is not usage.** The lead recorded a
   notification's token count as "usage"; CS7 (L469-474, per the reader)
   found it is context size at the run's end. Mechanism: usage is counted
   from transcripts by script, never read off a notification.
9. **Findings ahead of the report.** verifier-P0 sent shared-code findings
   by message before finishing, as the ledger asks ("never hold a problem
   back"). It believed wave 1 was designing; the lead's entry corrected it.
   Mechanism: the harness tells each agent what is dispatched, from the
   dispatch record, not from the briefs directory.
10. **The lead's sealed view.** The lead hashed its own suspicions about P0
    after dispatch and revealed them after the report: the verifier found all
    five, among the twenty findings of its first pass (11:21:04). Mechanism: the harness seals the author's
    view at dispatch and scores the verifier against it, as it does plants.
11. **Model placement by the owner's standing rule.** At 11:45 Logan set
    verifiers on Sonnet "going forward". One verifier was then mid-pass on
    Opus. The lead let it finish, since a resume is not a dispatch, and
    routed every later verifier dispatch to Sonnet by hand. Mechanism: a role
    table (parcel, verifier, integration verifier, reader), with each role's
    model as the owner's dated config. Every dispatch reads its model from
    that table and records it, and a change takes effect at the next
    dispatch, never mid-pass. At 11:51 Logan refined it: a running verifier
    stays on its model until it finishes, later passes included, because its
    context is cached and resuming is simpler. So the table holds a running
    agent's model until that agent finishes, not only for its current pass.
12. **The heredoc trap recurred for the lead,** though its own notes and
    every brief name it. A schema pattern edited through a Python heredoc in
    Bash lost one level of backslashes. It happened to stay correct, and a
    test (an id ending in a newline) is what showed that, not the note. This
    is CS7's finding again: "What worked was not the note but the guard"
    (CS7 L366). Mechanism: file edits go through a tool that takes the bytes
    as given. The shell is for running commands, never for carrying file
    content.
13. **The verifier's budget, by the owner's rule.** P0 took three passes.
    Pass 1 sent back five; pass 2, two narrow leftovers of those fixes;
    pass 3 is the last in the budget. Each fix was proven by removing it in
    a copy and seeing a test fail (replant scripts), before the verifier
    saw it. Mechanism: the harness runs "remove the fix, see the test fail"
    for every sent-back item, as part of accepting a fix.
14. **A parcel's design phase found a seam defect.** P2, reading P0 in
    phase 1, found that Context recorded requests by reference (a suite
    appending to one list rewrote its own transcript). It sent the finding
    by message before its design, needing no answer. The lead fixed it on
    round1 before either parcel built, and each go message fast-forwards
    the parcel's commit-free branch to the fix. Mechanism: phase 1's reading
    of the seam is a review, and its findings are routed to the seam's
    owner before any parcel builds on the seam.
15. **Planting faults that a parcel's own tests miss is hard work,** and
    that is good news about the parcels. P1's tests pinned trigger counts.
    P2's pinned every docker flag, exec argument, mount refusal, token and
    budget. The lead's first P2 plant (dropping `timeout -k`) was caught by a
    test, and a second had to be found among semantics no test held: a
    counter reset, and a budget checked per turn but not per call. Each
    plant was proven to survive the parcel's full suite before the copy was
    built. Mechanism: the harness runs the parcel's suite against each
    candidate plant and keeps only the survivors, and records how many
    candidates the tests caught. That count is itself a measure of the
    parcel's tests.
16. **A brief carried a reader's prior knowledge as fact.** "--mount
    refuses a missing source" came from cs7-reader, marked by the reader as
    its own prior knowledge, not CS7's. The lead put it in P2's brief, and P2
    disproved it by probe on this desktop. Mechanism: a brief's claims carry
    their source, and the harness flags a claim sourced "prior" for a probe
    before dispatch.
17. **The estimate and the bound, against the bill.** QS1 off, live: the
    plan's estimate was $0.26 and P1's reservation $1.3326192, and it
    billed $0.0086. The estimate assumed 4K in and 2K out per call; the
    model averaged about 890 in, 81% from cache, and 52 out. A bound 155
    times the bill is safe, but on a $12.51 balance it decides which
    batches fit, QS4's most of all. Mechanism: after each batch the harness
    proposes caps from measured percentiles, with their margin stated. The
    owner or lead accepts them, and the record names the caps every run
    used.
18. **Hiding the grading costs coordination.** The rule that keys stay out
    of the ledger until the round's last planted-copy verifier reports
    (CS6#3) meant the lead could not say why P1 merged despite two
    sent-back findings, nor tell P2 plainly which findings not to fix.
    Every sentence that resolves a verifier finding without a fix implies a
    plant. Mechanism: the harness grades plants in a sealed channel. It
    sends the parcel a fix list made of the non-plant findings only, and
    the shared ledger shows only "findings resolved per the key" until the
    round's last planted-copy verifier reports.
19. **A suite's assertion went beyond the docs it cites, and only the
    live run showed it.** The lead's brief said "in thinking mode,
    reasoning_content is present". D8 promises no such thing, and DeepSeek
    returned an empty field with 0 reasoning tokens on 43 of 101 turns. QS1
    built what the brief said, and its verifier checked QS1 against that
    brief, so neither could see the overreach. Mechanism: every assertion
    carries its source sentence. A check before dispatch flags an assertion
    whose sentence does not entail it, and any assertion that fails at a
    high rate on its first live batch is reviewed before the result counts.
20. **A fix opened a path the old error had hidden.** While QS1 failed
    every empty-reasoning turn, no request ever carried such a turn back.
    Correcting the check would have sent one, without its field, into D8's
    400 on every streamed multi-turn item. P1 saw it while making the fix,
    before any live call, and put it to the lead, whose seam it was. The
    lead fixed it in P0 within minutes. Mechanism: a fix that widens what
    reaches the provider is checked for the requests it newly makes, against
    the provider's documented refusals. The harness can list those refusals
    as rules it checks against each outgoing request before sending.
21. **The lead's own sentence was restated twice in one hour.** At 15:00:40
    it wrote that D8 "does not say the field is never empty", and swapped
    the streamed and non-streamed counts. Both went from its ledger into
    P1's code comments and P1's ledger, and a fresh scoped verifier caught
    both. The values in its script's output were right; the sentence built
    from them was wrong. Mechanism: the harness writes count tables from the
    script's own output, labels included, never retyped. A claim about what
    a doc "does not say" is checked against the doc's prose, not only its
    field reference.
22. **The provider's usage export is the meter's exact second source.**
    DeepSeek's hourly CSVs matched the spend file to the last of 16
    decimals, and token for token, over three hours and four batches. The
    balance, at two decimals, cannot say that much, and lags by minutes. The
    export also showed that refused 400s are neither billed nor counted.
    Mechanism: the harness pulls, or asks the owner for, the usage export
    after each batch. It reconciles per hour and per token type, and treats
    the balance as a coarse tripwire only. The export names the account
    and a masked key, so it stays local, and only the comparison is
    published.
23. **Where a suite's tests leave room, a plant goes into its data.**
    P3's scorer pinned every rule. All seven candidate code plants were
    caught, and so was a prompt edit, since the cuts pin the prompt's
    length. What survived were two question edits that contradict their own
    cited evidence and their key: R09 asks about verifier-P1's file while
    citing verifier-P0's, and L06's time bound excludes an entry it cites.
    The key check still passed: it checks evidence positions, not what the
    question means. Mechanism: the harness runs candidate plants, keeps the
    survivors, and reports where the survivors cluster. That is where the
    tests stop, here at the meaning of the data. Questions need a check that
    their wording entails what their evidence answers.
24. **A method that worked was in a verifier's scratch, not in the brief.**
    Draft 4's verifier reproduced all five planted copies by copying each
    real tip's commit header and replacing only its tree. P4's brief
    described the original builder's method. P4 reported that four of five
    copies did not rebuild by it (P4.md 17:45:13). The lead answered with
    the plan verifier's method, 5 of 5 (17:47:24). Ninety seconds later P4
    found the fault in its own probe, and the brief's method held too
    (17:48:54). Mechanism: when a claim of reproduction goes into a plan,
    the harness keeps the method that reproduced it beside the claim, and a
    parcel's failure to reproduce is checked against that method before
    anything changes.
25. **The provider's calendar is part of the price table.** DeepSeek bills
    every hour of a Chinese public holiday off-peak. The table priced
    2026-10-07 01:20 UTC as peak, so the meter over-counted two QS6 batches
    by double. The guard held the next batch on the mismatch, and the
    diagnosis took one line of D2 and the balance's arithmetic.
    verifier-P0 had stated this exact case as K7 at 11:18. Mechanism: the
    price table carries the provider's holiday calendar, from a cited
    source. Until it does, the harness refuses peak runs on dates it cannot
    classify, and reconciles by the usage export, which names the billed
    rate.
26. **A queued run outlived its runner's limit.** The lead queued QS6's last
    batches behind a 2h22m wait under a 2-hour background cap. It saw the
    clash and stopped the queue before it ran, so nothing was cut mid-batch.
    Mechanism: the harness's scheduler, not a sleeping shell, starts batches
    at window openings, and never starts a batch it cannot finish within its
    own time limit.
27. **A provider closed requests with no reply, and each stopped a batch.**
    At peak, DeepSeek closed 2 of about 31 requests of 64K tokens 18 to 25 s
    in, with no reply at all. P0 stopped each batch, as built, since the
    cost was unmetered. The lead wrote a bounded retry (7b0dc64): twice a
    call, three failed attempts a batch, the cost reserved and counted.
    Mechanism: the transport layer classes a failure by whether any reply
    began. None began: retry, within a budget the reservation already
    covers. Part of one arrived: stop, since the meter cannot see it. Every
    attempt goes in the record.
28. **A billed drop can read as routing.** In a test, three billed drops and
    one metered call matched the same batch priced at v4-pro's rates,
    within tolerance. The reconciliation said `matches:deepseek-v4-pro`.
    That was still not ok, so the next batch was held, but the label named
    the wrong cause. Mechanism: reconciliation lists every explanation that
    fits the bill (unmetered attempts, routing, holiday rates), and names
    none when several fit.
29. **The owner's priority overtook the lead's own gate.** The lead ruled
    that a verifier checks the retry before more live runs (19:11:24). Then
    Logan asked for the runs to continue, so the verifier ran beside them
    (19:37:52). Mechanism: a gate the lead sets carries its risk and what
    would stop the work. An owner's override is recorded against it, with
    that stop condition kept live.
30. **A proof run hit its job limit, and its output was lost.** The lead
    gave the removal proof a 10-minute background limit. It needed about
    15, and its output was buffered through a pipe, so nothing survived and
    it ran again. Mechanism: long jobs write unbuffered progress to a file,
    and the harness sets each job's limit from measured durations.
31. **A top-up during a batch would void that batch's reconciliation.**
    Logan announced a $20 top-up as runs were about to start. The lead
    waited for a probe's opening balance to show it (32.36). Mechanism: an
    announced top-up pauses batch starts until a balance read shows it,
    since the provider sends no top-up event.
32. **QS4's worst case outgrew the balance at peak.** The retry's margin
    took QS4's reservation with peak allowed to $15.10, against a $12.36
    balance, so QS4 could start only off-peak until Logan topped up.
    Mechanism: the harness prices each queued suite's reservation against
    the balance ahead of time, and asks the owner for a top-up before the
    queue reaches a suite that cannot start.
33. **A guard's constant met the provider's real failure rate.** P0's batch
    allowance of three dropped attempts was the lead's guess. Live,
    DeepSeek dropped about 5 to 7% of requests at 64K tokens and above, and
    none of over 500 below 64K. So 66-run batches stopped at their third
    drop. The lead added a per-batch flag (fcbc67d), and ran the rest at 15.
    Every retry before the batches' limits was answered. Mechanism: each
    guard constant carries its basis. The harness measures each provider's
    failure rate by context size, sets allowances from it, and the
    reservation follows.
34. **A time budget checked before each call can overrun by one call.** P4
    pointed out that its 6,000 s run budget is checked before each call. So
    the last call, a 300 s tool call or a streamed reply of about five
    minutes, can run past it. The lead kept 6,000 s within the 2-hour job
    limit, with the overrun counted. Mechanism: a budget bounds the elapsed
    time including the call in flight. Each call's own timeout is clamped
    to what remains.
35. **A squashed planted copy carries its first commit's message.** P4's
    copy took 9a85a15's message, which states a reservation that 5ecd02b
    later corrected. verifier-P4 found the stale figure (F3): the copy's
    message disagreed with its own tree. Mechanism: the planted-copy builder
    composes the copy's message from every commit it squashes, in order, or
    states which one it took, and the verifier is told.
36. **Sonnet verifiers caught 8 of 8 plants, each in its first pass.**
    Every plant had survived its parcel's own tests: they were chosen so
    that only reading finds them (22:00:27). The two that
    verifier-P4's own mutation pass could not find were found by reading
    the code against its docstring, its design and round 6's ledger.
    Mechanism: the harness selects plants by survival, and measures a
    verifier's yield against them. A verifier's mutation pass is a
    complement to reading against the specification, never a substitute.
37. **The owner's address rides in a public repository's history.** QS4's
    replay repositories hold ParcelRound's history, whose author lines
    carry Logan's address, and a model's `git log` would send it to the
    provider. K6 allowed every repository's content, but no limit named
    this. P4 noted it in its own file; verifier-P4 raised it as L2; and the
    lead asked Logan before any run. Mechanism: the harness scans every
    input it mounts for the owner's identifiers, from a configured list. A
    run whose inputs hold one needs the owner's ruling recorded first.
38. **A provider's content filter refused a tool's output format.** DeepSeek
    refused two QS4 runs' third request with HTTP 400 "Content Exists
    Risk", each just after `read_file` returned round 6's verifier brief.
    Two diagnostic batches, eleven requests in all, found it deterministic:
    the brief numbered as `cat -n` numbers it was refused every time; the
    same text unnumbered, or numbered as `grep -n` numbers it, was
    answered. Its trigger lies in the brief's later lines in that form;
    which line, or why, is unknown. The lead changed `read_file` to `grep
    -n`'s form (db94d41). A refused request costs nothing, but it ends the
    run. Mechanism: the harness classes a provider's moderation refusal
    apart from other 400s. It records the refusal, and replays the
    refused request once with the latest tool result reformatted, so a
    run is not lost to a format. The provider's filter becomes a measured
    property of the provider, with its own rate in the table.
39. **A run that does not converge spends its whole cap, and the model
    never knows.** P5's real tip ran 169 turns and wrote 45 check scripts,
    with requests growing to 487K tokens. Then QS4's 40M prompt cap stopped
    it, with no report. Round 6's Opus verifier did the same job in 22.6M
    tokens, and reported. Nothing in QS4's prompt or P2's loop tells the
    model what is left of its turns, time or tokens. Mechanism: the loop
    tells the agent its remaining budget at set fractions, and asks for a
    report at the last one. Runs that end at a cap are counted apart.
40. **The screen counts a marker said for another reason.** P4's planted
    copy scored 2 of 2 by the screen. One finding near plant P4-p1 held its
    one-word marker, "records", while stating round 6's D1, not the
    plant. QS4's limit 7 names that case, and the lead's reading is the
    score of record for that reason. Mechanism: a marker set names the
    plant's own change, never a word its passage shares with its
    neighbours. The harness tests each set against round 6's recorded
    findings near the plant before any run.
41. **A detached run on the owner's desktop showed a window the owner
    closed.** The lead started QS4's lanes with no console, so each run got a
    console window of its own on Logan's screen. Logan closed the three, and
    the runs ended mid-way, with no summary. Their metered spend survived
    in the spend files. Mechanism: the harness runs every job with no
    window, under a supervisor that names each job, and shows the owner
    one status page, never a terminal.
42. **A mount that the input check passed was unreadable in the sandbox.**
    QS4's lanes ran from clones under a long scratch path. There, Docker
    Desktop's binds of the outside sources gave "Input/output error"
    inside the container, while the host-side hash check passed and the
    other mounts read. The models said so in their reports. The lead
    found it only by reading them, after eight finished runs. Mechanism: before a
    run's first model call, the sandbox reads a probe file from every
    mount, and refuses the run if any read fails. A run's inputs are
    checked where the model sees them, not only where the harness does.
43. **No record names the code a run ran under.** The lead changed
    `read_file`'s line format between two QS4 runs (db94d41), and no field
    of either record moved. `harness_version` is a constant, 0.1.0, and
    QS4's version digests its items, prompt, expected hashes and its own
    module, not P2's loop or sandbox. So the one run under the earlier form
    is told apart only by its time against the commit's, from the ledger.
    Mechanism: each record carries the commit of the code that ran, a flag
    for changes outside the records, and a digest of the tools' text as
    the model saw it. A batch from a changed tree is refused, or marked.
44. **The judge's standard drifted from the original verifier's.** The lead
    judged QS4's findings from its own sense of a fault. Two runs flagged a
    rule whose incident dropped "the lead built", and the lead called the
    first a false alarm: nothing outside the record's set was shown. The
    third's statement quoted round 6's verifier brief, whose list counts
    "a domain, quantifier or count wider than the record's" as a restate.
    By that list the finding is true, and so is half of another the lead
    had called false. Two verdicts changed. Another sentence, flagged by
    three runs for three different reasons, needed git to settle: 7 files
    in one commit, 9 in the other. Mechanism: a replay's judge works from
    the original verifier's list, and each judgement names the item it
    applies. A sentence flagged by several runs is settled from its
    primary source before any verdict on it stands.
45. **The allowance that bounds unmetered cost chose which runs survived.**
    QS4's lanes allowed 23 attempts closed with no reply a batch. Four runs
    met it, three of them P5's real tip and one P3's (14:08:26), at 16 to
    18% of their attempts against about 9% overall. Their late requests were
    the largest, and larger requests drop more: in one, the failed requests'
    median was 161 messages, against 131 answered (13:26:42). So the runs that the
    allowance ended were the ones that wandered. A dataset trimmed by it
    leans to shorter runs. The allowance was set by the balance, not the
    rate. Each dropped attempt reserves the dearest call QS4's caps allow,
    $0.74 at 900,000 tokens, though a real one was a fraction of that,
    mostly cache hits. Mechanism: the margin for a retried attempt is
    priced at that request's own worst case, known when it is sent, and
    the run's budget, not a count, bounds the retries. A run the provider
    ends is run again until it completes, and the case study counts the
    attempts it took.
46. **A reconciliation closed too soon reads a bill not yet posted.**
    Whether DeepSeek bills a request it closes with no reply was open from
    the first drop (note 27), and no batch alone could say: its tolerance
    held a few drops' worth. The lanes' combined reconciliation set 3,074
    metered lines against the balance and Logan's $10, and agreed to the
    cent, so the lead concluded that the 346 closed attempts were not billed
    (14:08:26). Its closing read was two minutes after the last call. After
    Logan's next top-up, the balance was $0.08 short of the sum (18:47:34).
    That is about $0.00023 for each closed attempt, or charges posted late,
    or use outside the harness. The conclusion was withdrawn: the aggregate
    can settle such a question only once the bill has posted. Mechanism:
    the harness keeps a running reconciliation over every batch since the
    last top-up. It closes a period only with a balance read well after
    the last call, and confirms the read with the next one. Each open
    billing question is held as a hypothesis with its expected effect. The
    question stays open here: QS4h's reads point to no charge (07:54:20,
    08:25:11), and the usage export has not confirmed it.
47. **Thorough tests still left two doors, and a re-implementation drifted.**
    P5's 70 tests pinned nearly every guard of its code slice. The lead's
    two plants went where they did not reach:
    - two of verifier-P4's recorded findings with their in-view marks
      swapped, where a test pinned only each parcel's count;
    - a match's fallback widened so that a finding anywhere in a file
      matched a recorded finding with lines, where no test held the
      negative case.
    Both survived the tests with the real inputs present, and the gate.
    verifier-P5 caught both in its first pass, by checking every record
    against its source and reading the code against QS4's own rule.
    P5's one real fault (F3) was of the same family: QS4h's copy of
    QS4's host check dropped `--ignored`, and the guard weakened without
    a word. Mechanism:
    - data tests pin each record against its source, not aggregates;
    - each branch of a match has its negative case;
    - a module that re-implements another's guard is held to it by a
      differential test over the same inputs.
48. **A new failure the retry does not cover.** QS4h's h3-real run ended
    at turn 132 on "ReadError: [Errno 10054] An existing connection was
    forcibly closed by the remote host". Across QS4's and QS4h's
    thousands of calls so far, it was the first connection reset, among
    hundreds of closes with no reply. P0 retries only a request the server closed before any reply.
    Every other transport error ends the run, by design, since a reply
    may have begun and its cost cannot be metered. So 132 turns, $0.50 at
    peak, were lost to one reset. A second reset ended an h4-planted run
    at turn 106 of 126 attempts (2026-10-08 02:13), so two of QS4h's
    first 15 runs, both at peak. Mechanism: the transport records whether
    any byte of the reply arrived. A reset before the first byte is
    retried like a close. One after it ends the run, and its request is
    priced at its worst case in the reservation, so the meter can account
    for what may have been billed.
49. **In code, a fault is found where it is promised, not where it is
    made.** QS4h's screen locates a plant by the lines its edit touched.
    P1-B and P2-B are code changes that break what a docstring says. In
    three of the slice's first runs, the model stated each fault exactly,
    with a probe that showed it. It cited the docstring's lines, or the
    one check left standing 70 lines away, not the edit. The screen missed
    them, and the lead's judgement caught them: by screen 6 of 8 in pass
    1, by judgement 8 of 8. Over the four passes the screen located P1-B
    and P2-B in 3 of their 8 catches. QS4h's limit 8 had named the case for a
    deletion. It holds for any code plant whose fault is a broken promise.
    Mechanism: each code plant pre-registers the spans of the text it
    contradicts, the docstring or the design, beside its edit's, and a
    deletion registers the block that should hold what was removed. The
    markers still decide whether the fault is stated.
50. **The provider closes requests by their size, not by the hour.** The
    lead moved QS4h's real tips off-peak on the belief that Beijing's
    afternoon raised DeepSeek's closes (lead.md 01:47:15). Measured over
    QS4h's first 2,640 attempts (04:30:07), the rate rose with the
    request, the same at either hour: none under 100K characters, 3% at
    100K to 200K, 5 to 6% at 200K to 400K, 17 to 18% at 400K to 800K,
    and 29 to 32% above 800K. Real tips make the largest requests, so
    they lost about 21% at both hours. The move saved half the price and
    no runs. Mechanism: the run record keeps each attempt's request size
    and outcome, failed ones included, and the close rate is reported by
    size before any rule about time is made. The loop keeps its requests
    small, trimming old tool output to a summary once a request passes a
    stated size, and a retry's reserve is priced at its own size (45).
51. **A replay's own rewriting can contradict the record it replays.**
    QS4h maps every abbreviation of a parcel's tip and of its planted copy
    to the item's own commit, so the planted and real conditions read
    alike. Where the lead's entry names both commits, the mapped entry
    says the copy is the parcel's own tip, beside "P3's own commit was
    checked absent". A real-tip run read the contradiction and asked the
    lead which commit it held (its transcript, 2026-10-08 06:01). It cannot tell the
    conditions apart, since both read the same, but a verifier is asked
    to trust a record that disagrees with itself. Mechanism: the mapping
    rewrites to two distinct placeholders, one for the copy and one for
    the tip, each bound to the item's commit only where the original
    named the copy, and the cut's check refuses a cut in which one
    sentence names a commit as both.
52. **A file a verifier checked was overwritten by its settled version.**
    The lead recorded the SHA-256 of each judgements draft when its
    verifier was dispatched (2026-10-07 14:10:01; 2026-10-08 07:54:20,
    12:11:23 and 13:18:10). After each check it rebuilt the draft in
    place, with the settled verdicts and `checked_by` set. So no recorded
    hash matches a file now, and the drafts as checked cannot be shown.
    The committed verdicts can still be traced through each verifier's
    own list and the settlement entries, but only by reading both.
    Mechanism: a file sent to a verifier is frozen under its hash, and
    the harness refuses to overwrite it. A settled version is a new file,
    whose entry names both hashes and the changes between them. This is
    METHOD.md's "freeze what is audited" (CS3#11), applied to the lead's
    own scratch.
