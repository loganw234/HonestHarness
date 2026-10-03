# Local pilots, specialist models, adversarial leads and rented GPUs

2026-10-02 · @Logan's notes of that day, written up and checked against their sources by the ParcelRound round-6 lead session

A research note, separate from ParcelRound's round 6. It is a companion to the requirements document ("REQ", open-weight-harness-requirements.md) and the tool-calling report ("TC", open-weight-harness-research.md). It changes neither; §6 lists what could fold in.

**In short.**
- The three general-purpose models Logan named are 7.7-9.5 B models from 2024 and early 2025. On the desktop's 16 GB card they run quantised at roughly 65K to 170K tokens of context, not 1M. Their 1M context needs about 100-150 GB of GPU memory, a rented multi-GPU node.
- Their value in a pilot is less the models than what they test: the harness's model-agnostic plumbing; qualification replays that cannot be contaminated, since every one predates the experiment's repositories; and the low end of honesty under difficulty.
- The InternLM site's own models are specialists, scientific and mathematical, mostly too large to run locally. They suit narrow, separately qualified roles: a numerical-claims checker, figure reading, research surveys.
- Adversarial leads extend mechanisms already practised: the plan verifier, H15.3's independence, H16.2's second recommendation. The literature says debate helps a weaker judge most when the debaters hold information it lacks. It also says multi-agent debate does not reliably beat simpler ensembling, and that models' errors are correlated, so two leads agreeing is weak evidence.
- Rented GPUs fit if the harness addresses endpoints, never machines, and a separate deployment kit stands machines up. Qualification follows the serving stack's fingerprint, not the machine's location.

---

## §0 Legend

- **[O]** Logan's words, given to the session on 2026-10-02.
- **[V]** verified this session at a primary source: a model card or `config.json` read raw, a licence file, the project's README, Hugging Face's model API, or the paper's abstract.
- **[S]** secondary source; verify before relying on it.
- **[K]** prior knowledge, not re-fetched.
- **[I]** inference or proposal by this note.
- **[R]** the record: the experiment's repositories, or a measurement this session took on the desktop.

---

## §1 What Logan said [O 2026-10-02]

> While you've been working, I identified a couple model families to potentially pilot test local open weight potential, I also considered the option of 'multiple adversarial leads', for projects where 'correct' could have potential to diverge, it could also potentially compensate for weaker models by having different ones arguing for and against each other. InternLM also has a series of models on their website which have particular interest for specialized usage, see the link for specifics: https://chat.intern-ai.org.cn/models
> InternLM2.5-7B-Chat-1M
> InternLM3-8B-instruct
> GLM-4-9B-Chat-1M
>
> A potential solution to hosting larger models is utilizing rented gpus temporarily to host them, which entails the harness being capable of supporting quickly stood up machines, likely more API on the 'deployment kit' than anything relating to the harness specifically, as it shouldnt really care "where" the model is reached

And, on the site's models:

> The ones listed on the page itself are potential specialized models for tasks which they might benefit in, not the general purpose ones I listed

---

## §2 General-purpose pilot candidates

### §2.1 The three, as their sources state them

| | InternLM2.5-7B-Chat-1M | InternLM3-8B-Instruct | GLM-4-9B-Chat-1M |
| --- | --- | --- | --- |
| released | 2024-07-03 [V InternLM README] | 2025-01-15 [V InternLM README] | 2024-06-05 [V GLM-4 README] |
| parameters | 7.74 B [V HF API] | 8.80 B [V HF API] | 9.48 B [V HF API] |
| attention, from `config.json` [V] | 32 layers; 8 KV heads × 128 | 48 layers; 2 KV heads × 128 | 40 layers; 4 KV groups × 128 |
| context as shipped [V] | config: 262,144 positions, dynamic RoPE × 2.5; 1M through LMDeploy | config: 32,768 positions, dynamic RoPE × 6.0. The card reports RULER averaged over 4K-128K | config `seq_length` 1,048,576 |
| the card's own serving example [V] | 1M "requires 4xA100-80G" (LMDeploy, tp 4) | LMDeploy, vLLM, transformers, Ollama | vLLM at 131,072 on one GPU. 1M needs tp 4, and the card suggests chunked prefill or more GPUs on OOM |
| licence [V] | the card: code Apache-2.0; weights free for research and for commercial use on application. InternLM's current README says Apache-2.0 for code and weights. **The two disagree**; read both before any commercial use | Apache-2.0 | `glm-4`: free for academic research; commercial use after registration |
| tool calling | vLLM's `internlm` parser with an InternLM2 tool template (TC §3.12) [V], and LMDeploy's `internlm` parser [S]. That the 1M variant uses the same format is assumed [U] | not documented on its card [V]. LMDeploy's parser list names internlm, qwen and llama3 [S]. [U] until QS1 | its card lists custom tool invocation (Function Call) [V]. No vLLM parser for it in the docs read [S]. [U] until QS1 |
| also | needle-in-a-haystack and LongBench on its card [V] | a deep-thinking mode, chosen by system prompt; trained on 4 T tokens [V] | needle-in-a-haystack and LongBench-Chat, and a transformers-native `-hf` variant (2024-10-24) [V]; 26 languages [K] |

Newer 9B-class options from the same houses exist: GLM-4-0414 (2025-04-14) and GLM-4.1V-9B-Thinking (2025-07-02) [V GLM-4 README]; Intern-S1-mini (§3). Each would go through QS1 the same way.

### §2.2 Memory: what fits where [I, from the configs above]

The KV cache per token, in bf16, is 2 × layers × KV heads × 128 × 2 bytes:
- **InternLM2.5-7B**: 128 KiB per token;
- **InternLM3-8B**: 48 KiB;
- **GLM-4-9B**: 80 KiB.

An 8-bit KV cache halves each. The weights in bf16 are about 15.5, 17.6 and 19.0 GB, and about 5-6 GB each at 4 bits.

**The desktop** [R, measured this session]:
- an RTX 4070 (12 GB) and an RTX 5060 Ti (16 GB), with 63.8 GB of RAM;
- REQ §11.3 names only the 5060 Ti and "47 GB shared", probably WSL's share [I].

**On the 16 GB card, 4-bit weights, about 8 GB left for the KV cache once the engine has its workspace** [I]:

| model | KV, bf16 | KV, 8-bit | ceiling the model itself sets |
| --- | --- | --- | --- |
| InternLM2.5-7B-Chat-1M | ~65K tokens | ~130K | 1M |
| InternLM3-8B-Instruct | ~170K | — | its card reports results to 128K |
| GLM-4-9B-Chat-1M | ~105K | ~210K | 1M |

The 12 GB card holds about half as much. Both cards together roughly double it, over PCIe, at a cost in speed. These are upper bounds to measure, not measurements.

**At 1M tokens:**
- InternLM2.5's bf16 KV alone is 128 GiB, and its card's 4 × 80 GB follows.
- GLM-4-9B's is 80 GiB plus 19 GB of weights, so two 80 GB GPUs at least, and its card uses four.

The 1M feature is a rented-node feature (§5).

### §2.3 What a pilot on them can show, and what it can't [I]

- **They are not candidates for the roles REQ §8.3 cares most about.** They are far below the §8.4 tier, and nothing in the record suggests a 7-9 B model of 2024 leads a round or verifies cft-fp256's code. A pilot that read them as such would be measuring the wrong thing.
- **They test the harness, cheaply and locally:**
  - QS1 (tool-call conformance) across three different tool formats: InternLM2's tool tokens [K]; GLM-4's; and one model with no documented format, which exercises TC §7.2's prompt-based fallback.
  - H15.1's check that each response reports the pinned model.
  - The local path through the deployment kit (§5, K8).
- **Their replays are contamination-free by date.** All three were released between 2024-06 and 2025-01, and the experiment's repositories begin after that: cft-fp256's first commit is 2026-08-28, ParcelRound's 2026-09-11, HonestFramework's 2026-09-12, loganw.dev's 2026-09-29 [R]. The §8.2 caution, that a model may have seen the case studies, cannot apply to these weights. That makes them clean subjects for QS2-QS7 replays, and a baseline for frontier models that might have seen them. Pin each by its Hugging Face revision: a repository's "last modified" date moves with card edits.
- **Long context is not long reasoning.** The cards measure retrieval (needle-in-a-haystack) and LongBench-style tasks [V]. The roles that would use a long context here read a whole round's ledger, or cft-fp256's 17,000-line VALIDATION.md, and must reason across it.
  - The test is the project's own: QS6 (records fidelity), with accuracy plotted against context length on a real ledger. Round 5's archive holds 38 Markdown files [R].
  - A ledger-reader role, doing the three read moments' "read the whole directory", is the natural first use.
- **QS9 at the low end.** The rung at which a small model first passes by weakening something is a data point for H17.5's threshold. It also checks the ladder itself: a ladder that no model fails measures nothing.
- **First roles to try** (REQ §8.3): triage, a schema-bound re-check, a gatherer on short records, and the long-context ledger reader. Not lead; not verifier on code.

---

## §3 Specialist candidates: the InternLM site's own models

Logan's framing: models "for tasks which they might benefit in" [O]. The site lists these, with its own one-line descriptions [V, chat.intern-ai.org.cn/models, read 2026-10-02]:

| on the site | open weights | size | released | licence |
| --- | --- | --- | --- | --- |
| Intern-S2: science and fundamentals | yes [V HF API] | 403.4 B | 2026-09-13 | Apache-2.0 |
| Intern-S2-Preview: complex scientific tasks | yes [V] | 36.1 B MoE: 256 experts, 8 routed per token, plus a shared expert; one layer in four uses full attention, the rest linear; 262,144 positions in its config [V config]. About 3 B active [S]; continued from Qwen3.5 [S] | 2026-05-15 | Apache-2.0 |
| Intern-S1-Pro: "1TB-parameter" | yes [V] | 917.0 B | 2026-02-02 | Apache-2.0 |
| Intern-S1: professional scientific capabilities | yes [V] | 240.7 B; 28 B active per its paper (arXiv 2508.15763) [S] | 2025-07-24 | Apache-2.0 |
| Intern-S1-mini: lightweight | yes [V] | 8.5 B; a Qwen3-8B language model with a 0.3 B vision encoder [S] | 2025-08-18 | Apache-2.0 |
| InternVL3.5-241B-A28B: multimodal perception and reasoning | not checked [U] | 241 B, 28 B active, by its name | | |
| Intern-S1-MO: long-reasoning maths agent, IMO-level | no public Hugging Face repository found [V] | | | |
| MathResearchAgent, InternThinker, ArtiMuse | features of the platform [V site] | | | |
| MindSearch: deep search | an open-source multi-agent web-search framework, InternLM/MindSearch on GitHub, Apache-2.0, created 2024-07-28, last pushed 2025-07-04 [V] | | | |

**Running them** [I]:
- **Intern-S2-Preview is the one specialist with a plausible local path.** Its hybrid attention keeps a full KV cache on only 10 of 40 layers: 20 KiB per token in bf16, about 5 GiB for its whole 262K range, plus a fixed linear-attention state.
  - Its 36 B weights at 4 bits, 18-20 GB, would span both cards, or keep the experts in the 64 GB of RAM.
  - Whether an engine supports that today for this architecture (`qwen3_5_moe_text`) is [U].
- **Intern-S1-mini fits one card** as easily as §2's models.
- **The rest are rented-cluster models** (§5).

**Tasks they might benefit** [I]:
1. **A numerical-claims checker.** cft-fp256's work is binary256 arithmetic: rounding modes, error bounds, error-free transformations. A maths or science specialist can serve as a cross-family second opinion (H15.3) on the mathematical premises in briefs and on figures in VALIDATION entries.
   - Qualify it on a narrow set: statements from the record whose truth is known, plus planted false variants, with the key withheld (QS4's design applied to claims).
2. **Proof sketches for the QS9 rung "a bound past what can be proven".** A long-reasoning maths agent fits it, but Intern-S1-MO is hosted only, which makes it a data-governance question (§5, K6), not just a capability one.
3. **Research surveys.** The read-only surveyors that wrote round 6's practice survey (ADOPTION.md's B17) did this over private records. A MindSearch-style deep search fits the public half: model cards, papers, vendor docs, with every source cited.
4. **Figure and photograph reading** (InternVL, the S series). The project already has one such check: REQ §11.3's photograph check.

Each enters as any model does: through one narrow role and its own small qualification set, recorded per H15.2. Never on the strength of the site's descriptions.

---

## §4 Multiple adversarial leads

### §4.1 Where "correct" can diverge

- **Where an authority decides, debate adds little** [I]. cft-fp256 has one: the golden model (HF §1). A disagreement about a value is settled by running the authority.
- **Where no gate decides, it applies.** That covers plans, scope, method text such as this round's METHOD.md, design trade-offs, the owner's intent, and claims in prose. Much of the lead's own error record is of that kind (REQ §4.5):
  - an unverified P0 facts sheet;
  - overclaiming to the owner;
  - a plan stating what its surveys did not support;
  - a question to the owner with a false premise.
- **It is also where the "(Recommended)" steering acts** (REQ §3.4, H16).

### §4.2 What is already practised or proposed

- **The plan verifier** (ADOPTION.md's B1) is a one-sided adversary: one author, one disconfirmer. It was practised in cft-fp256's cert, language and step-6 rounds and in ParcelRound's round 6 [R].
- **H16.2's second, independent recommendation** is two-sided, for single questions.
- **H15.3's cross-family independence**, and GPT-6.1 Sol Max's spec-only challenge suite (QS8), are the precedent across model families. It found a real defect, and its adapters were later partly derived from returned results: independence is a property of the inputs too [R].

Adversarial leads would extend H16.2 from single questions to whole plans and designs.

### §4.3 What the literature says

- **Debate** (Irving et al. 2018) [K]: two models argue opposite sides, and a weaker judge decides. The premise is that refuting a lie is easier than defending one.
- **Khan et al. 2024** [V abstract]: debaters held information the judges lacked.
  - Under debate, non-expert models judged correctly 76% of the time, against a 48% baseline; humans 88%, against 60%.
  - Optimising debaters for persuasiveness made judges more accurate.
- **Kenton et al. 2024** [V abstract]:
  - Debate beat consultancy, a single assigned advocate, on every task.
  - Against the judge answering directly, it won on extractive QA with information asymmetry, and was mixed elsewhere.
  - Stronger debaters helped, but more modestly than earlier work found.
- **Smit et al. 2024** [S]: multi-agent debate, as commonly built, does not reliably beat self-consistency or ensembling. It is sensitive to settings such as how readily agents agree, and tuning agreement helped.
- **Wang et al. 2024, Mixture-of-Agents** [V abstract]: layered open-source models, each using the previous layer's outputs, scored 65.1% on AlpacaEval 2.0 against GPT-4 Omni's 57.5%. Aggregation can lift weaker models, on chat-quality benchmarks at least.
- **Kim et al. 2025** [S]: across more than 350 models, two models agreed on 60% of the items both got wrong, on one leaderboard. Larger, more accurate models had more correlated errors, even across architectures and providers.

### §4.4 What follows for the harness [I]

1. **Agreement between leads is weak evidence.** Errors correlate (Kim et al.), and HF §1 already says that two parsers agreeing is not an authority. Score adversarial leads on the disagreements they surface that turn out to be real, not on their consensus.
2. **Build in the asymmetry that made debate work.** The owner, as judge, holds less than the leads. Give the leads different evidence by design, for example one reads the code and the other the record, and require every claim to cite its evidence (H6.2).
3. **Send the owner only forks that survive an evidence check.** Two leads that send every disagreement upward cut against H16's aim. A fork goes to the owner when both sides' citations resolve and still conflict. It goes with both derivations (H16.1), and his choice becomes an override signal (H16.3).
4. **Weaker models are a hypothesis to measure, not a premise.**
   - Two weak leads are not shown to beat one strong lead. Mixture-of-Agents shows gains only on chat benchmarks.
   - Run QS5 (lead replay of round 2's request) three ways: one strong lead; a cross-family pair of weaker leads; that pair with a strong judge.
   - Score each by the three corrections round 2's real plan found before dispatch, its brief errors, owner time and cost.
5. **Design against the known failure modes:**
   - sycophantic convergence, agreeing to end the exchange (Smit et al. tuned agreement levels);
   - persuasion over truth when the judge is weak;
   - collusion within a model family;
   - anchoring, where the second lead reads the first's draft;
   - cost, two to three times the lead's tokens.

**A protocol sketch** [I]:
1. **Blind drafts.** Two leads of different families get the same request and inputs. Neither sees the other's draft, and each draft's hash goes into the ledger before any exchange. This is the three-commit idea applied to drafts: the record shows neither saw the other first.
2. **Critique as a verifier's list, not a vote.** Each attacks the other's draft with file:line evidence and the record's citations.
3. **Revision**, recorded.
4. **Resolution:**
   - what an authority can decide goes to the authority;
   - what both sides converge on, with evidence, stands;
   - what remains goes to the owner as a ranked list of forks.
5. **A bound.** Two exchanges, then forks are forks. CS4 observation 15 records a verifier loop over spellings that did not end by itself until a convergence standard ended it.

**Measures:**
- forks per plan, and those the owner judged real;
- plan errors caught before dispatch, against the single-lead baseline;
- the owner's time;
- cost.

---

## §5 Rented GPUs, and the deployment kit

### §5.1 The split Logan proposed [O], made precise [I]

- **The harness addresses a model endpoint**: a base URL, a wire API, a served model name and a credentials reference. This is TC's recommended boundary, an OpenAI-compatible server (TC §1, §7.2). Routing does not care where the endpoint runs.
- **A deployment kit, outside the harness**, does the rest:
  - stands up a machine, rented or local;
  - pulls pinned weights;
  - starts a pinned serving engine;
  - proves the endpoint, registers it, and tears it down.
- **Qualification is not location-agnostic, though.** TC's finding is that provider variance is mostly infrastructure: templates, parsers, flags. Hence "treat (model, provider, version) as the unit you test" (TC §4.6), and H15.1's pin. For a self-hosted endpoint, the "provider" is its serving stack.
  - So the pin and every QS result key on the stack's fingerprint, not on the machine.
  - A rented endpoint whose fingerprint matches a qualified one inherits its results after a canary.
  - A different fingerprint is a new unit until QS1 passes.

### §5.2 What the kit must do (candidate requirements K1-K8) [I]

- **K1. A pinned recipe**:
  - weights by repository and revision hash;
  - quantisation;
  - engine and version;
  - serving flags: tool and reasoning parsers, `max_model_len`, chunked prefill, KV-cache dtype;
  - the chat template, by hash.

  Together these are the stack's fingerprint.
- **K2. An identity probe at registration and at each lease renewal**:
  - `/v1/models`;
  - the template hash and the maximum context;
  - a canary tool call, a QS1 subset;
  - the model each response reports.

  An endpoint that answers as another model is refused. Round 5's dispatch named one model and its transcripts another (REQ H15.1) [R].
- **K3. Leases, not machines.** Each has a time-to-live, a budget cap and idle shutdown, and its teardown is confirmed by the provider's own API. A rented GPU left running is round 6's leftover temp repositories (Rounds/ParcelRound-R6/harness-notes.md, entry 29), at an hourly price.
- **K4. Cost into H13**: GPU-hours and money per lease, attributed to the agents that used it.
- **K5. Warm starts**: weights cached on the provider's volume, and start-up time recorded. That is 15-20 GB for §2's models, and hundreds of GB for the §8.4 tier.
- **K6. Data governance by the owner's rule** (H10.2): which repositories and records may go to which provider. Secrets never leave the broker (H3.2). The precedent is the challenge suite's results, sent to another provider (VAL:16911) [R].
- **K7. Endpoints are leases that can vanish** (H2.6). An agent whose endpoint is lost resumes on one with the same fingerprint, or waits. It never continues silently on another model (H15.1).
- **K8. The local path is the same path.** The desktop's two cards register through the kit like any rented node. A local pilot and a rented run then differ only in the fingerprint's hardware fields.

**Sizing, from §2.2:**
- §2's models at 1M tokens: two to four 80 GB GPUs.
- Qwen3.6-27B, REQ's realistic local option: one 48-80 GB GPU at a long context [I].
- GLM-5.3 or Kimi K3: multi-node (REQ §8.4) [S].

Rental providers are examples only, not checked for price or terms [U]. A RunPod connector is installed in Logan's Claude app, unauthenticated, and was not used.

---

## §6 What could fold into REQ (proposals; Logan's to accept)

1. **§8.4** gains two tables: a local pilot tier (§2) and specialists (§3), each marked for QS1 first.
2. **H15.1**: the pin's unit becomes the stack fingerprint (K1). K2's probe joins H15.1's check of each response's reported model.
3. **H15.3** cites Kim et al. 2025: correlated errors are measured, not assumed away by changing families.
4. **H16.2** extends to adversarial leads as an option per decision class, measured by a QS5 variant (§4.4, item 4).
5. **H8** treats endpoint leases as resources (K3, K7). **H13** adds GPU-hours (K4).
6. **§12.1, Phase 0**: QS1 on §2's three models locally first, the cheapest data point, then QS6 and QS9 slices on contamination-free replays.

## §7 Decisions this note leaves to Logan

- **A spending ceiling for rented GPUs**, and whether starting a lease is a reserved action (H10.2).
- **Which repositories' content may go to which rented machines or hosted specialists** (K6).
- **Whether the first adversarial-lead trial runs on a ParcelRound round**, where correct can diverge, or on a replay (QS5).
- **GLM-4's registration requirement and InternLM2.5's conflicting licence statements.** They matter only if HonestHarness publishes recipes that use those weights commercially.

---

## Sources

- InternLM site, model list: https://chat.intern-ai.org.cn/models (read 2026-10-02)
- Model cards, read raw: https://huggingface.co/internlm/internlm2_5-7b-chat-1m · https://huggingface.co/internlm/internlm3-8b-instruct · https://huggingface.co/zai-org/glm-4-9b-chat-1m (and its LICENSE) · https://huggingface.co/zai-org/glm-4-9b-chat-1m-hf · https://huggingface.co/internlm/Intern-S2-Preview
- `config.json`, read raw, for the three and Intern-S2-Preview; Hugging Face model API (`/api/models/<id>`) for parameter totals, licences and creation dates, including Intern-S2, Intern-S1-Pro, Intern-S1 and Intern-S1-mini
- InternLM README (release news, licence): https://github.com/InternLM/InternLM · GLM-4 README (release news): https://github.com/zai-org/GLM-4 · MindSearch: https://github.com/InternLM/MindSearch
- vLLM tool calling (the `internlm` parser): https://docs.vllm.ai/en/v0.8.2/features/tool_calling.html · LMDeploy tool calling: https://lmdeploy.readthedocs.io/en/latest/llm/api_server_tools.html
- Intern-S1 paper: https://arxiv.org/abs/2508.15763 · Intern-S2-Preview announcement: https://x.com/intern_lm/status/2055146106799976798 [S]
- Irving, Christiano, Amodei, "AI safety via debate" (2018): https://arxiv.org/abs/1805.00899 [K]
- Khan et al., "Debating with More Persuasive LLMs Leads to More Truthful Answers" (2024): https://arxiv.org/abs/2402.06782
- Kenton et al., "On scalable oversight with weak LLMs judging strong LLMs" (NeurIPS 2024): https://arxiv.org/abs/2407.04622
- Smit et al., "Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs" (ICML 2024): https://proceedings.mlr.press/v235/smit24a.html
- Wang et al., "Mixture-of-Agents Enhances Large Language Model Capabilities" (2024): https://arxiv.org/abs/2406.04692
- Kim, Garg, Peng, Garg, "Correlated Errors in Large Language Models" (ICML 2025): https://arxiv.org/abs/2506.07962
