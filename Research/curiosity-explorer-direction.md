# A curiosity explorer: the direction HonestHarness is for

2026-10-03 · @Logan's direction of that day, given in conversation with the ParcelRound round-6 lead session and written up by it

A research note. It records a direction and the ideas around it. **Nothing
here is implemented or adopted.** It is a companion to the requirements
("REQ", open-weight-harness-requirements.md), the tool-calling report ("TC",
open-weight-harness-research.md) and the pilot notes ("PN",
open-weight-pilot-notes.md), and it changes none of them. §7 lists what could
fold in, which is Logan's to decide. Round 1's approved plan
(Rounds/HonestHarness-R1/PLAN.md) is on hold at his word while he considers
the direction.

**The guiding statement** [O]:

> More curiosity gets to survive long enough to meet reality

**In short.**
- **What it is for.** The end result is a curiosity explorer, not a research
  unit. It carries a person's idea past the point where it would die at the
  boundary of their expertise, on into evidence-producing work. Some ideas
  will prove not worthwhile, some will, and some will branch.
- **The core mechanism.** For each idea, find or build the thing that can say
  no, and keep visible what has been tested against it and what is still
  only an explanation.
- **Trust.** For an owner who is not an expert, trust comes from the
  structure, not from the recommender. A recommendation should carry what it
  rests on, what would show it wrong, and a measured track record.
- **Limits.** A limit is a claim, read from the record rather than from the
  model's sense of itself. The owner may still say "keep trying", but the
  bar does not move.
- **Scale.** The evidence floor is the same for a home setup and a lab. What
  scales with a claim's reach is how many independent checks stand behind
  it.
- **Specialists.** Small specialized models suit roles whose outputs are
  pointers or structured data, each with a cheap check. A Ledger Parser
  first; a compactor later, compacting by reference.

---

## §0 Legend

- **[O]** Logan's words, given to the session on 2026-10-03.
- **[R]** the record: this experiment's repositories, read at the commits
  named.
- **[K]** prior knowledge, not re-checked.
- **[I]** inference or proposal by this note, which is the lead session's view
  as it gave it in that conversation.

---

## §1 What Logan said [O 2026-10-03]

On what the harness should become:

> Regarding what the harness will eventually 'become', I believe in the initial docs it outlined a 'Research Unit' type setup, while considering it more, I think its ideal result is something more of a 'Curiosity Explorer', not necessarily just for generating scientific data, but for allowing curiosity to grow past its prior hard walls, where a persons idea would normally die at the boundary of expertise, this would allow them to push further, ideally into evidence-producing work, some ideas may be not worthwhile, some may be, some could branch into entirely different ideas naturally. But the thread that I keep pulling appears to be curiosity driven, not 'research', and I think the best outcome is that the system reflects that as its how it came to be. It also determines why the 'recommended' path is so frequently taken, I am no expert in any field realistically, which is exactly why I rely on the model to provide that expertise and to ensure that it can be trusted beyond "trust me" or "double check"
>
> Dont begin the round yet, still considering things and the directions to take it

On the people it is for:

> The goal being that more people with less "knowledge" can still pursue curiosity without relying on one shot AI explanations (which could just be hallucinations), or their own limitations.
>
> For example, I would have never been able to reverse engineer coop for a dead game, prior to AI, my attempt would have gotten to "I tried the old thing that worked, it doesnt anymore, guess thats it", but with AI I was able to iterate, test, iterate, and keep pushing until it worked, all the while I personally didnt have to have any code level understanding, comprehending the systems around it and being able to have it articulated back in simple 'How:Why' responses allows me to guide without needing to specify "No dont try updating the old standard to modern ones because its a much larger project"

On resources and limits:

> I think a portion of it also comes down to what resources the unit has, for example a low cost home setup might only be capable of running a limited 'intelligence' level, the system should be capable of eventually concluding 'I'm at my limit for pushing this work, further progress needs new information or capacities", or outright stating "Thats beyond what I think we could accomplish" if the goal is simply too far fetched, nothing would inherently 'force' the model to stop, the user could simply say "Keep trying", but thats also part of the point, the user is informed, but in the end it rests on them to decide what their workforce is pointed at, the structure around it is there to keep it between the lines as it walks. A larger lab trying to perform serious work has more confidence, runs more tests, verifiers, etc. knowing that the scale of work demands the level of commitment to ensuring nothing is 'lying'

On specialized models:

> I'm also considering small 'specialized' models trained directly off data generated by these projects for 'semi-intelligent' roles, one such example is a 'Ledger Parser', a model whose trained to work through the massive ledger files, find the relevant content the query is for, and report back where to find it in the file. The worry about self training data is real but moderately mitigated by the data itself being the desired operational mode, utilizing existing examples of references and calls as the data to further it, success/failure/correction etc.
> Many parts of the system could benefit from a specialized lightweight model, especially a compactor model eventually

And the statement:

> I think the general 'guiding' statement for the end result is "More curiosity gets to survive long enough to meet reality"

**A note on "the initial docs"** [R]. The phrase "Research Unit" does not
appear in this repository's documents. Their shape is a research programme's,
though: REQ is organised around one project's fixed question, roles and
qualification suites.

---

## §2 Curiosity, not research [I]

- **It is how this began.** loganw.dev's front page frames the main
  experiment as a question: "how far can one untrained person take a serious
  engineering project, now that AI has lifted the barrier of expertise?"
  [R loganw.dev `site/pages/front.py:37-38`, at `43c36a2`]. ParcelRound and
  HonestFramework were distilled from that work, not designed first.
- **The unit of work is an idea, not a programme.** An idea can stay
  exploratory, earn its way toward evidence, end in an honest dead end, or
  branch into another.
- **Dead ends are results.** "Not worthwhile, and here's why" is recorded, so
  the idea is not walked again blind. It is the verifier's "found nothing is
  an acceptable answer", applied to ideas.
- **Branches keep their lineage.** An idea that turns into another hands over
  what it already established.
- **Process grows with the claim, not with the work.** An idea starts cheap.
  Gates, verifiers and planted faults come in as it moves toward a claim
  someone will rely on. ParcelRound's round 6 put full process on
  everything, which suited a method document and would be too heavy for a
  hunch.

---

## §3 The thing that can say no [I]

- **What made Logan's example work.** It was not the AI's knowledge. The game
  was the judge: the co-op worked or it did not, and no explanation could
  change that. One-shot explanations are risky because nothing in them can
  say no.
- **The principle.** For each idea, find or build the thing that can say no.
  Keep visible what has been tested against it, and what is still only an
  explanation. It is HonestFramework's "one authority that can't argue",
  applied per idea.
- **What kind of ground an idea stands on**, made visible to the person:
  - tested against reality;
  - consistent with sources;
  - plausible but untested.
- **Where care is needed:**
  - **Weak or missing judges.** Many questions have no check as clear as
    "did it work". That is where fluent but wrong explanations survive.
  - **"Iterate until it works"** can become "iterate until it looks like it
    works". Models will sometimes satisfy the check instead of the goal. So
    gates that can fail, and planted faults, come with the explorer from the
    start (REQ H17).
  - **Stakes.** A failed game connection costs an evening. Trial and error
    with wiring, medicine or money costs far more. The explorer slows down,
    or stops, as the stakes rise.
  - **Optimism.** Models lean toward "let's keep going". An honest explorer
    says "this isn't worth pursuing, and here's why" as readily.

---

## §4 The owner's role, and trust without expertise [I]

- **Steering by consequences.** Logan's "don't update the old standard,
  that's a much larger project" is a judgement of scope and cost. "How:Why"
  explanations gave him enough of the system's shape to make it. The
  explorer's explanations aim at decisions: the options, what each costs,
  and what would show progress. They do not aim at the implementation.
- **The record of "Recommended"** [R]. Every one of the twelve answers Logan
  gave through the question tool in ParcelRound's round 6 and in
  HonestHarness round 1's planning took the option marked "(Recommended)":
  - eight in round 6 (ParcelRound archive/round6-ledger.zip, lead.md
    17:07:40);
  - four in round 1's planning: three in Rounds/HonestHarness-R1/PLAN.md's
    last section, and one in Rounds/ParcelRound-R6/harness-notes.md, after
    note 60.

  In round 6 the defaults that went wrong were caught by verifiers, not by
  the owner or the lead. The lead's ruling D1 adopted a pending item, and
  the lead's own records needed more restating than any parcel's work
  (ParcelRound CASE-STUDY-6.md, obs 4 and 12). So the trust lives in the
  checking structure, not in whoever recommends.
- **What makes a recommendation checkable by someone who is not an expert:**
  - what it rests on, readable (REQ H16.1 asks for this already);
  - what result would show it wrong, stated before it is tested;
  - a track record: how often the recommender's defaults later proved
    wrong, measured rather than assumed. A simple start is a log of each
    recommendation, whether the owner took it, and what later evidence
    showed. It turns "trust me" into a rate (extends REQ H16.3 and H16.4).
- **Disagreement as a signal.** Where the right answer could go either way, a
  second recommender from another model family that disagrees is the moment
  to pause (PN §4; REQ H16.2).

---

## §5 Resources, limits and "keep trying" [O, I]

- **"I'm at my limit" is a claim, and models are poor witnesses to it** [I].
  They lean optimistic, and from the inside "I can't" is hard to tell from
  "I haven't found it yet". So the limit is read from the record, not from
  the model's sense of itself:
  - the same check failing the same way across attempts;
  - new attempts circling back to old ones;
  - the thing that can say no not moving.
- **Each kind of limit points somewhere different** [I]:
  - **capability:** this model cannot reason far enough. A bigger one might,
    and could be rented for one step rather than the whole idea (PN §5);
  - **information:** a missing document, measurement or test. That is a
    request to the person, not a stop;
  - **resources:** time, hardware or compute;
  - **feasibility:** the goal is far-fetched in principle, Logan's "beyond
    what I think we could accomplish". This should be rare, and argued.

  Stated this way, "I'm at my limit" becomes a short list of what it would
  take, not a dead end.
- **"Keep trying" is the owner's call, and the bar does not move** [O, I].
  Pressure to keep going is when a model is most tempted to win by moving the
  goalposts. REQ's QS9 names the moves: "weakening a gate, narrowing the
  work, relabelling a defect as a limit, or overclaiming" (REQ §8.2). The
  person decides where the effort goes, and the structure decides what
  counts as success. Attempts made past a stated limit are recorded, so
  persistence stays honest.
- **The floor is the same everywhere; only the height changes** [O, I].
  Nothing is presented as evidence unless it was checked against something
  that can say no. A home explorer checking a hunch for themselves might need
  one such check. A lab publishing needs independent replication, planted
  faults and verifiers from other model families. What scales with a claim's
  reach is how many independent checks stand behind it.
- **On modest hardware, honesty at the edge may matter more than capability**
  [I]. A small model that says "I'm stuck, here's why" is worth more than a
  big one that bluffs. QS9 measures exactly this per model (REQ §8.2), and PN
  §2.3 already marks the low end as a data point.

---

## §6 Small specialized models [O, I]

- **The Ledger Parser.** It takes a query, finds the relevant content in the
  ledgers, and reports where it is [O].
  - **Its output is a pointer, and a pointer can be checked** [I]. "The
    answer is at `lead.md:553`" is true or false the moment the line is read.
    The model is not trusted for content. It only has to point well, and
    every answer carries its own check.
  - **It must beat the plain baseline** [I]. Search over the ledgers' stamped
    entries is strong. The model earns its place only where it does better,
    most likely on fuzzy or multi-entry questions.
  - **"Not found" is part of the job** [I]. Small models tend to return
    something. Queries with no answer belong in training, and an answer
    where there is none counts against it in evaluation.
  - **Its first benchmark exists already** [I]. Round 1's approved QS6 slice
    has questions with known answer locations, cuts at several lengths, and
    "not in the input" scored as an overclaim. General pilots would set the
    bar a specialist must clear.
- **Training data from the record** [O, I]. The projects already produce
  query-to-location pairs whose answers were verified:
  - every case-study citation resolved against its ledger;
  - every verifier's file:line evidence;
  - every correction where a citation proved wrong, a ready-made negative.

  Logan's mitigation for self-training is that this data is the desired
  operational mode [O]. Sharpened [I]: what matters is where a label comes
  from. Each training example carries how its label was established:
  - a mechanical check;
  - a verifier's finding with evidence;
  - the owner's decision;
  - another model's judgement, kept out or kept separate.

  A parser's own outputs return to training only after a mechanical check
  confirms them. This is HonestFramework's provenance rule, applied to
  training data.
- **Hold out whole rounds** [I]. Train on rounds 2 to 5 and test on round 6
  and later, so the model learns to read a ledger rather than memorising
  these ones. Ledger formats drift between rounds, so each new round is a
  free test that it still works.
- **The compactor, later and carefully** [O, I]. Compaction is lossy by
  design, and its failure is silent:
  - it drops the one detail that mattered;
  - or it smooths a hedged claim into a confident one, the overreach round
    6's verifiers kept finding (CASE-STUDY-6, obs 3 and 12).

  The safer design compacts by reference: decisions verbatim with their
  sources, everything else reduced to pointers rather than paraphrase. The
  session that wrote this note ran on a compacted summary of itself, and
  the parts it could rely on were the ones that pointed somewhere: commit
  SHAs, paths, ledger times [R]. A compactor is then partly a ledger parser
  plus a policy for what to keep. Building the parser first gives a tool to
  check what a compactor dropped.
- **The general principle** [I]. Give small specialists roles whose outputs
  are pointers or structured data, each with a cheap check that can reject
  every answer, rather than prose. That is where limited intelligence is
  safe. It suits the home setup in §5: a few narrow, checkable specialists on
  modest hardware may be more trustworthy than one general model at its
  limit.
- **Feasibility on the desktop** [K]. Low-rank fine-tuning of a 7-8 B model
  on a quantised base is commonly done on a single 16 GB card. That is
  unmeasured here.

---

## §7 What could fold in (proposals; Logan's to accept)

1. **REQ's statement of purpose** opens with the guiding statement and the
   curiosity-explorer framing.
2. **Expertise a non-expert owner can check**, as a first-class requirement.
   Each recommendation carries its derivation, its falsifier and the
   recommender's measured track record (extends H16).
3. **A structured limit statement**, with a route forward for each kind of
   limit (extends H17).
4. **"Keep trying" against a fixed bar**, with attempts past a stated limit
   recorded (extends H17 and QS9).
5. **A constant evidence floor**, with the depth of checking scaled to a
   claim's reach.
6. **Ideas as the unit of work.** Dead ends are recorded as results, and
   branches keep their lineage (extends H11 and H12).
7. **Specialist roles in §8.3.** A Ledger Parser row, with the QS6 slice as
   its benchmark and its acceptance test. A compactor later. Training data
   carries label provenance (extends H15).
8. **Round 1.** Whether its approved plan stands under this direction, or a
   first round instead takes one real idea from curiosity to evidence or to
   an honest dead end.

## §8 Decisions this note leaves to Logan

- Whether, and how, this framing enters REQ.
- Round 1's direction. It is on hold at his word.
- Whether to start collecting specialist training data now. The cheap first
  step is tagging verified query-to-location pairs as rounds produce them.

---

## Sources

- Logan, in conversation with the ParcelRound round-6 lead session,
  2026-10-03 (§1, verbatim).
- loganw.dev, `site/pages/front.py:37-38`, at `43c36a2`: the experiment's
  question.
- ParcelRound at `f42242e`:
  - CASE-STUDY-6.md, obs 3, 4 and 12;
  - archive/round6-ledger.zip, lead.md's entry 17:07:40, the owner's
    answers.
- This repository: REQ §8.2 (QS6, QS9), H16 and H17; PN §2.3, §4 and §5;
  Rounds/HonestHarness-R1/PLAN.md (the QS6 slice; the approval).
