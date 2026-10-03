# Open-Weight LLM Tool-Calling: Formats, Protocols and a Model-Agnostic Harness Reference (state as of 2026-10-01)

**TL;DR**
- Most reliable cross-model design: the harness sends OpenAI-style JSON-Schema tools to an OpenAI-compatible server (vLLM/SGLang/llama.cpp/Ollama/hosted) that does model-specific template rendering and parsing. Internally keep a Responses/Open Responses-shaped item model that preserves `tool_call_id` and reasoning verbatim. Gate every (model × provider × version) on conformance tests: most real failures come from templates, parsers and providers, not models.
- The model layer has no single standard. Hermes `<tool_call>{json}</tool_call>` plus OpenAI JSON Schema definitions are the baseline. 2025–2026 frontier families moved to XML-ish per-parameter encodings that avoid JSON-escaping code: Qwen3-Coder/3.5/3.6 `<function=…><parameter=…>`, GLM `<arg_key>/<arg_value>`, MiniMax `<invoke>`, DeepSeek V4 DSML. Others use bespoke token grammars: gpt-oss Harmony, Kimi section tokens, Gemma 4 `<|tool_call>`, Mistral `[TOOL_CALLS]name[ARGS]`.
- Reasoning models need interleaved thinking preserved across tool rounds (GLM, Kimi K2.x, MiniMax M2.x, Qwen3.5/3.6, Gemma 4 within a turn, gpt-oss within a tool loop). Stripping reasoning, mangling IDs or losing `add_generation_prompt` silently degrades accuracy. Constrained decoding (vLLM structural tags/`strict`, Gemini VALIDATED, OpenAI/Anthropic strict) secures syntax but not semantics.

---

## §0 Legend
- [V] verified this session from a primary or near-primary source.
- [S] secondary source.
- [K] long-published format from prior knowledge, not re-fetched; byte-verify against the current `chat_template.jinja`.
- [U] unverified or fast-moving.

---

## §1 Executive summary

**Stack (bottom→top):**
1. Model chat template and special tokens. Non-portable.
2. Runtime that renders `tools=[…]` and parses output: vLLM/SGLang `--tool-call-parser`, llama.cpp `--jinja`, Ollama renderers/parsers.
3. Wire API: OpenAI Chat Completions (dominant for open weights), Responses/Open Responses (rising), Anthropic Messages (also served by llama.cpp and vLLM), Gemini, Bedrock Converse.
4. Tool supply: MCP, OpenAPI-as-tools, UTCP, code-mode.
5. Agent/UX: A2A, Agent Client Protocol, AG-UI, AGENTS.md, Agent Skills.

**De facto standards:**
- **Definitions** use the `{"type":"function","function":{name,description,parameters}}` shape. Nearly every open-weight template accepts it via `apply_chat_template(tools=…)` and re-renders it as JSON, TypeScript (Harmony), Gemma `declaration:` blocks or Mistral `[AVAILABLE_TOOLS]` [V].
- **Wire calls** use `tool_calls[{id,type,function:{name,arguments:<JSON string>}}]`, with results sent as `role:"tool"` + `tool_call_id`.
- **Model output** falls into three clusters:
  - JSON-in-tags: Hermes, Llama 3.1, Mistral, Kimi args, Harmony args.
  - XML-ish per-parameter: Qwen3-Coder/3.5/3.6, GLM, MiniMax, DeepSeek V4.
  - Pythonic: Llama 3.2/4, Olmo 3, ToolACE.
- **Why XML-ish:** raw per-parameter values avoid escaping multi-line code inside one JSON string. The cost is that typing moves to the schema; parsers must coerce types, and a string `"007"` must stay a string [V].\[1\] DSML adds `string="true|false"`, and Gemma 4 uses a `<|"|>` string-delimiter token for the same reason [V].\[2\]\[3\]

**Recommended architecture:**
- **Canonical store:** typed items (`message`, `reasoning`, `function_call{call_id,name,arguments}`, `function_call_output`).
- **Default transport:** Chat Completions against a server with the correct tool and reasoning parsers.
- **Alternate adapters:**
  - Responses/Open Responses.
  - Anthropic Messages.
  - Raw-template: render the official template or encoder client-side, call `/v1/completions`, parse per family.
  - Prompt-based fallback with lenient parse and repair.
- **Also:** constrained decoding, schema sanitization, a per-family reasoning policy, and a K2-Vendor-Verifier-style conformance suite.

---

## §2 Master comparison table

| Family (current) | Tool defs | Call syntax | Result | IDs | Parallel | Reasoning | vLLM | SGLang | llama.cpp | Ollama | Quirks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Llama 3.1/3.3 | prompt JSON [K] | `{"name","parameters"}`; built-ins `<\|python_tag\|>` [K] | `ipython` [K] | none | no [V] | – | `llama3_json` [V] | `llama3` [V] | native [V] | yes | arrays as strings [V] |
| Llama 3.2 | prompt | pythonic, no delimiters [V] | ipython | none | yes | – | `pythonic` [V] | `pythonic` [V] | yes | yes | small models fail format [V] |
| Llama 4 | prompt | pythonic recommended [V] | tool | none | yes [V] | – | `llama4_pythonic` [V] | `llama4` [V] | [K] | yes | |
| Qwen2.5/Qwen3 | `<tools>` JSON [K] | Hermes `<tool_call>{json}` [V] | `<tool_response>` [K] | server | yes | `<think>` [V] | `hermes` [V] | `qwen` (`qwen25` deprecated) [V] | native [V] | yes | |
| Qwen3-Coder, Qwen3.5 (Feb 2026), Qwen3.6 | system XML-ish [S] | `<tool_call><function=N><parameter=K>V</parameter></function></tool_call>` [V] | tool | server | yes | `preserve_thinking` [S] | `qwen3_xml`/`qwen3_coder` [V] | `qwen3_coder` [V] | `--jinja` [S] | had wrong-format bug [V] | untyped values; fenced-code false positives [V] |
| Mistral ≤v7 | `[AVAILABLE_TOOLS]` [V] | `[TOOL_CALLS] [{name,arguments,id}]` [V] | `[TOOL_RESULTS] id [TOOL_CONTENT]…` [V] | 9-char [V] | yes (7B weak) [V] | – | `mistral` [V] | `mistral` [V] | native [V] | yes | template throws on bad IDs [V] |
| Mistral v11/v13+ (Magistral, Devstral 2, Ministral 3, Large 3) | same | `[TOOL_CALLS]name{args}` / `name[ARGS]{args}` [V] | same | 9-char | repeat `[TOOL_CALLS]` [V] | v13 `[THINK]` [V] | `mistral` [V] | `mistral` | [K] | [K] | no terminator [V] |
| DeepSeek V3/R1-0528 | system | `<｜tool▁call▁begin｜>function<｜tool▁sep｜>N` + json fence [K] | `<｜tool▁outputs▁begin｜>` [K] | none | yes | R1 `<think>` | `deepseek_v3` [V] | `deepseekv3` [V] | native [V] | yes | |
| DeepSeek V3.1/V3.2 | system | `N<｜tool▁sep｜>{json}` [K] | same | none | yes | hybrid | `deepseek_v31` [V] | `deepseekv31`, `deepseekv32` [V] | [K] | [K] | |
| DeepSeek V4 Pro/Flash (2026-04-24), V4.1 | `tools` on system/developer; **no Jinja template** [V] | DSML `<｜DSML｜tool_calls><｜DSML｜invoke name><｜DSML｜parameter name string>` [V]; V4.1 `<｜DSML｜ calls>` [V] | tags in user msg [V] | none | yes [V] | `thinking_mode` [V] | `deepseek_v4` encoder [V] | `deepseekv4` [S] | V4 tpl; V4.1 PR [S] | [U] | must set parser [V]; arg collapse [S] |
| Kimi K2/K2-Thinking/K2.5/K2.6 (2026-04-20)/K2.7 Code | system JSON [K] | `<\|tool_calls_section_begin\|><\|tool_call_begin\|>functions.N:i<\|tool_call_argument_begin\|>{json}<\|tool_call_end\|>…` [V] | tool [V] | `functions.{name}:{idx}` [V] | yes | `preserve_thinking` [S] | `kimi_k2` [V] | `kimi_k2` [V] | [K] | [K] | bad history IDs leak tokens [V] |
| GLM-4.5/4.6/4.7, GLM-5 (Feb 2026), 5.1, 5.2 (2026-06-13), 5.3 | system JSON [V] | `<tool_call>N<arg_key>K</arg_key><arg_value>V</arg_value></tool_call>` [S/K] | `<\|observation\|>` [K] | server | yes | interleaved; `clear_thinking:false` [V] | `glm45`, `glm47` [V] | `glm`/`glm45`/`glm47` [V] | [K] | parser bug [V] | literal `</tool_call>` in value [V] |
| gpt-oss-20b/120b | developer TS `namespace functions` [V] | `<\|channel\|>commentary to=functions.N <\|constrain\|>json<\|message\|>{…}<\|call\|>` [V] | `<\|start\|>functions.N to=assistant…` [V] | server | multiple per turn [K] | keep analysis in tool loop [K] | `openai` [V] | `gpt-oss` [V] | native [K] | yes | recipient placement [V] |
| Gemma 4 (2026-04-02) | `<\|tool>declaration:N{…}<tool\|>` [V] | `<\|tool_call>call:N{k:<\|"\|>v<\|"\|>}<tool_call\|>` [V/S] | `<\|tool_response>…` (stop) [V] | none | [U] | keep thoughts between calls [V] | [U] | [U] | binding bug [S] | [K] | |
| Gemma 2/3/3n | prompt-only [K] | instructed | user | none | – | – | custom | – | generic [V] | tpl | |
| FunctionGemma 270M | template | `<start_function_call>call:N{k:<escape>v<escape>}<end_function_call>` [V] | tpl | none | [U] | – | `functiongemma` [V] | [U] | [U] | [U] | fine-tune intended [V] |
| Granite 3.x/4.x | template | `<\|tool_call\|>[…]` [S] | tool | server | yes [V] | – | `granite`, `granite4`, `granite-20b-fc` [V] | [U] | native [V] | [K] | |
| Cohere Command A Reasoning/A+ (05-2026) | template | [U] | tool | [U] | [U] | reasoning parser | `cohere_command3/4` [V] | [U] | R7B native [V] | [K] | needs `cohere_melody` [V] |
| MiniMax M2/M2.1/M2.5/M2.7 | system `# Tools` [V] | `<minimax:tool_call><invoke name><parameter name>V</parameter></invoke>` [V] | tool | server | yes [V] | keep `<think>` [V/S] | `minimax_m2` [S] | `minimax-m2` [V] | [U] | [U] | |
| Hermes 2 Pro/3 | `<tools>` [K] | `<tool_call>{json}` [K] | `<tool_response>` [K] | none | yes | – | `hermes` [V] | [U] | tpl override [V] | yes | 2 Theta degraded [V] |
| Olmo 3 | template | `<function_calls>` newline pythonic [V] | tpl | none | yes [V] | Think | `olmo3` [V] | [U] | [U] | [U] | accepts `true/null` [V] |
| Others | | | | | | | `xlam`, `internlm`, `jamba`, `hunyuan_a13b`, `longcat`, `gigachat3`, `apertus`, `mimo` [V] | `step3`, `apertus2509` [V] | | | §3.12 |

---

## §3 Per-family spec entries

### §3.1 Llama
**JSON calls (3.1/3.3) [K]:**
```
{"name": "get_weather", "parameters": {"city": "Paris"}}<|eot_id|>
<|python_tag|>brave_search.call(query="...")<|eom_id|>
```
- Built-ins require `Environment: ipython` in the system prompt, and results come back in the `ipython` role [K].
- vLLM flags: `--tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.1_json.jinja`. It states "Parallel tool calls are not supported for Llama 3" and that built-in python tool calling is not supported [V].\[4\]

**Pythonic (3.2) [V]:**
```
[get_weather(city='San Francisco', metric='celsius'), get_weather(city='Seattle', metric='celsius')]
```
- Limitation: the model "must not generate both text and tool calls in the same generation".\[4\]
- Llama 4: use `llama4_pythonic` with `tool_chat_template_llama4_pythonic.jinja`.\[4\]
- No 2026 Meta open-weight successor was verified [U].

### §3.2 Qwen
**Qwen2.5/Qwen3** use Hermes-style calls ("the chat template … has already included support for the Hermes-style tool use"):\[4\]\[5\]
```
vllm serve Qwen/Qwen3-8B --enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser deepseek_r1
```
```
<tool_call>
{"name": "get_weather", "arguments": {"city": "Paris"}}
</tool_call>
```
**Qwen3-Coder / Qwen3.5 / Qwen3.6** use the XML format [V]. Qwen3.5 "was trained on the Qwen3-Coder XML format" (Ollama #14493).\[6\]
```
<tool_call>
<function=read_file>
<parameter=path>
notes.txt
</parameter>
<parameter=limit>
5
</parameter>
</function>
</tool_call>
```
**Parser behaviour:**
- Coerce types from the schema.
- Tolerate a missing `</parameter>` and truncation.\[1\]
- vLLM's `qwen3coder_tool_parser` falls back to Python `eval()` [V]; this is a security hazard.\[7\]
- Prefer `qwen3_xml` on vLLM: users report `qwen3_coder` failures on long inputs that disappear with `qwen3_xml` [V].\[8\] Use `qwen3_coder` on SGLang.

**Known bugs [V]:**
- vLLM #57541: a `<tool_call>` inside fenced code is treated as a real call.\[9\]
- Ollama Qwen3.5 was mapped to the Hermes JSON renderer/parser.\[6\]
- The same Ollama renderer omitted `</think>` on thinking+tool-call turns.\[6\]

**Versions:** Qwen3.5 open weights shipped Feb 2026 [S]. Qwen3.6-Plus, 3.7 and 3.8-Max are proprietary [S].\[10\] Open-weight availability of later Qwen releases varies by checkpoint [U].

### §3.3 Mistral (mistral-common)
**v7 raw string [V]** (mistral-common 1.5.0):\[11\]
```
[AVAILABLE_TOOLS] [{"type": "function", "function": {"name": "get_current_weather", ...}}][/AVAILABLE_TOOLS][INST] What's the weather like today in Paris[/INST][TOOL_CALLS] [{"name": "weather", "arguments": {"location": "Paris", "format": "celsius"}, "id": "bbc5b7ede"}][TOOL_RESULTS] bbc5b7ede[TOOL_CONTENT] 24 degrees celsius[/TOOL_RESULTS]
```
**Later tokenizer versions [V]:**
- v11+: `content[BOT]tool_name1{args}[BOT]tool_name2{args}`.\[12\]
- v13 (Ministral 3 / Devstral Small 2, Dec 2025): `'[TOOL_CALLS]' + name + '[ARGS]' + arguments`, plus `[THINK]`/`[/THINK]` tokens.\[13\]\[14\]

**IDs [V]:** the HF template "requires tool call IDs that are exactly 9 digits … an exception is thrown". vLLM ships a truncating template and `tool_chat_template_mistral_parallel.jinja`. Default serving mode is `--tokenizer_mode mistral --config_format mistral --load_format mistral`.\[4\]

**Bugs [V]:**
- mistral-common #345: malformed v11+ output raises the wrong exceptions; `[ARGS]null` becomes `{}`.\[15\]
- mistral-common #309: malformed v2–v7 output returns HTTP 500.\[16\]
- vLLM PR #59308: hardens pre-v11 parsing.\[17\]

### §3.4 DeepSeek
**V3/R1-0528 [K]:**
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>get_weather
```json
{"city":"Paris"}
```<｜tool▁call▁end｜><｜tool▁calls▁end｜>
```
- V3.1 [K] drops `function` and the code fence: `<｜tool▁call▁begin｜>NAME<｜tool▁sep｜>{json}<｜tool▁call▁end｜>`.
- vLLM uses `deepseek_v3`/`deepseek_v31` with example templates [V]. SGLang maps V3.1 and V3.2-Exp to `deepseekv31` and V3.2 to `deepseekv32` [V].\[4\]\[18\]

**V4 [V]** (Pro 1.6T/49B active, Flash 284B/13B active, MIT, 1M context), from the official `encoding/README.md`:\[2\]\[19\]
```
<｜DSML｜tool_calls>
<｜DSML｜invoke name="function_name">
<｜DSML｜parameter name="param" string="true">string_value</｜DSML｜parameter>
<｜DSML｜parameter name="count" string="false">5</｜DSML｜parameter>
</｜DSML｜invoke>
</｜DSML｜tool_calls><｜end▁of▁sentence｜>
```
- Tools are defined on the system or developer message. Results are wrapped in tags inside user messages.\[2\]
- V4 "ships no chat template". vLLM uses `deepseek_v4_encoding` (`thinking_mode` "chat"|"thinking").\[20\]\[21\]
- In SGLang, a server launched without `--tool-call-parser deepseekv4` returns DSML verbatim as content (PR #34050).\[21\]

**V4.1 [V]:** "DSML tag names use a leading space" (`<｜DSML｜ calls>`, `<｜DSML｜ invoke>`, `<｜DSML｜ parameter>`); namespaced tools look like `search::lookup`.\[22\] A V4 parser does not recognise V4.1 output [S].\[23\]

**Community reports [S]:**
- After any prior tool round, V4-Flash-Vision-Exp "frequently (≈80–100% in our measurements)" collapses arguments into a single `arguments` parameter.\[24\]
- Lookalike tokens such as `<||DSML||…>` appear and should be normalized.\[25\]
- A 2-bit V4-Flash test scored native DSML 98% vs a Hermes workaround 82%, mostly due to parallel calls.\[26\]

### §3.5 Kimi
**Raw string [V]:**
```
<|tool_calls_section_begin|><|tool_call_begin|>functions.get_weather:0<|tool_call_argument_begin|>{"city": "Beijing"}<|tool_call_end|><|tool_calls_section_end|>
```
- Assistant turns are primed with `…<|im_assistant|>assistant<|im_middle|>`.\[27\]

**IDs [V]:** "K2 expects the ID to follow the format functions.func_name:idx … idx is a global counter that starts at 0".\[28\]
- Violations surface as "special tokens like '<|tool_call_begin|>' in the 'content' field … due to incorrect tool-call ID".\[28\]
- Moonshot's API "automatically renames all historical tool call IDs" (vLLM blog, 2025-10-28).\[29\]
- Parser regexes should allow whitespace (`functions.glob: 1`) [S].\[30\]

**Thinking:** K2.5/K2.6 use `preserve_thinking:true` [S].\[31\]

**Versions:** K2 (Jul 2025), K2 Thinking (Nov 2025), K2.5 (Jan 2026), K2.6 (2026-04-20, 1T/32B active, Modified MIT), K2.7 Code (2026-06-16) [S].\[32\]\[33\] Kimi K3 is [U]; SGLang has a `kimi_k3` encoder.\[21\]

### §3.6 GLM
```
<tool_call>get_weather
<arg_key>city</arg_key>
<arg_value>Beijing</arg_value>
</tool_call>
```
**Values:** string values are written verbatim, so a literal `</tool_call>` inside a value ends the call in Ollama's parser (#18659) [V].\[34\] Non-string values are JSON-encoded [K].

**Thinking [V]:**
- "Thinking is activated by default in GLM-5.3 GLM-5.3-FLASH GLM-5.2 GLM-5.1 GLM-5 GLM-4.7".\[35\]
- GLM-5.3 uses forced thinking.\[35\]
- "Thinking blocks should be explicitly preserved and returned together with the tool results."\[35\]
- Preserved thinking is `clear_thinking:false`, passed in `chat_template_kwargs` when self-hosted or in the `thinking` object on the Z.ai API. GLM-4.7's card says SGLang only at release.\[36\]\[37\]
- Together: blocks "must exactly match the original sequence".\[38\]

**Parsers [V]:**
- vLLM: `glm45` (4.5/4.6), `glm47` (4.7/Flash).\[4\]
- SGLang: `glm`/`glm45`, with `glm47` on newer builds (GLM-5.3 deploy uses `--reasoning-parser glm45 --tool-call-parser glm47`).\[39\]\[40\]

### §3.7 gpt-oss (Harmony) [V]
```
<|start|>system<|message|>…Reasoning: high
# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'.<|end|>
<|start|>developer<|message|># Instructions
…
# Tools
## functions
namespace functions {
// Gets the current weather in the provided location.
type get_current_weather = (_: {
// The city and state, e.g. San Francisco, CA
location: string,
format?: "celsius" | "fahrenheit", // default: celsius
}) => any;
} // namespace functions<|end|>
<|start|>assistant<|channel|>analysis<|message|>Need to use function get_current_weather.<|end|><|start|>assistant<|channel|>commentary to=functions.get_current_weather <|constrain|>json<|message|>{"location":"San Francisco"}<|call|>
<|start|>functions.get_current_weather to=assistant<|channel|>commentary<|message|>{"sunny": true, "temperature": 20}<|end|>
```
**Channels:** function tools are triggered on commentary and built-ins (`browser`, `python`) on analysis. `<|call|>` is a stop token.\[41\]\[42\]\[43\]

**CoT retention [K]:** drop prior analysis after a `final` message; keep it within an unfinished tool loop.

**Quirks [V]:**
- The HF template renders past calls as `<|start|>assistant to=functions.x<|channel|>commentary`, a different recipient placement than the model generates. Accept both.\[42\]\[44\]
- A commentary preamble can come before the call.\[42\]\[45\]
- vLLM #58825: a stray `commentary to=assistant` header was parsed as a tool call.\[46\]

**Parsers:** vLLM `openai`, SGLang `gpt-oss`, renderer `openai-harmony`.\[4\]\[18\]

### §3.8 Gemma
**Gemma 4 [V]** (2026-04-02, Apache-2.0):\[47\]
- Turn tokens: `<|turn>`/`<turn|>`, with roles `system`/`user`/`model`.\[3\]
- Six tool tokens: `<|tool>`/`<tool|>`, `<|tool_call>`/`<tool_call|>`, `<|tool_response>`/`<tool_response|>`. `<|tool_response>` is an additional stop sequence.\[3\]
- `<|"|>` delimits **all string values**.\[3\]
- Thinking: `<|think|>` in the system turn turns it on; output appears as `<|channel>thought…<channel|>`. "If a single model turn involves function or tool calls, thoughts must NOT be removed between the function calls."\[3\]
```
<|turn>system
<|think|>You are a helpful assistant.<|tool>declaration:get_current_temperature{…}<tool|><turn|>
<|turn>user
…<turn|>
<|turn>model
<|tool_call>call:get_current_temperature{location:<|"|>London<|"|>}<tool_call|><|tool_response>response:get_current_temperature{temperature:15}<tool_response|>The temperature is…<turn|>
```
- The `call:`/`response:` body is inferred [S]; verify against the template.
- llama-cpp-python returned raw tool tokens in `content` (#2227) [S].\[48\]

**Gemma 2/3/3n:** prompt-based only [K].

**FunctionGemma [V]:** `<start_function_call>call:get_weather{location:<escape>London<escape>}<end_function_call>`; vLLM `functiongemma`; intended for fine-tuning.\[4\]

### §3.9 MiniMax [V]
```
<minimax:tool_call>
<invoke name="search_web">
<parameter name="query_tag">["technology", "events"]</parameter>
<parameter name="query_list">["\"OpenAI\" \"latest\" \"release\""]</parameter>
</invoke>
</minimax:tool_call>
```
- The system turn uses `]~!b[]~b]system` with a `# Tools` section.\[49\]
- M2, M2.1, M2.5 and M2.7 share the same syntax.\[50\]\[51\]
- Interleaved `<think>` must be kept in history. On the API, `reasoning_split=True` moves thinking into `reasoning_details`.\[52\]\[53\]
- vLLM: `--tool-call-parser minimax_m2 --reasoning-parser minimax_m2_append_think` [S].\[53\]
- MiniMax-M3 appears in the API docs; its open weights are [U].\[52\]

### §3.10 Granite, Cohere, Hermes, Olmo 3 [V unless marked]
- **Granite:** vLLM `granite4` (4.0), `granite` (3.1; "Parallel function calls are supported"), `granite-20b-fc`.\[4\] llama.cpp has a native Granite 4.1 example.\[54\]
- **Cohere:** `cohere_command3` (command-a-reasoning-08-2025), `cohere_command4` (command-a-plus-05-2026, North-Mini-Code-1.0); requires `cohere_melody`.\[4\]
- **Hermes [K]:** `<tools>` JSON in the system prompt, `<tool_call>{json}</tool_call>` output, `<tool_response>` results. vLLM notes Hermes 2 Theta has "degraded tool call quality".\[4\]
- **Olmo 3:**
```
<function_calls>
get_weather(city="Paris")
get_weather(city="Rome")
</function_calls>
```

### §3.11 Phi, Nemotron
- Phi-4-mini: `phi4_mini_json` (vLLM 0.8.3) [V].\[55\] llama.cpp treats phi-4 as generic [V].\[54\]
- Nemotron 3 Nano/Super are 2026 releases [S].\[56\] vllm-mlx has a `nemotron` parser [S].\[57\] The exact format is [U]; older releases used `<TOOLCALL>[…]</TOOLCALL>` [K/U].

### §3.12 Smaller/specialized
- **xLAM [V]:** vLLM `xlam` accepts JSON arrays, `<think>`-wrapped calls, fenced JSON, and `[TOOL_CALLS]`/`<tool_call>`, with Llama- and Qwen-based example templates.\[4\]
- **vLLM parsers [V]:** ToolACE-8B (pythonic), InternLM2.5 `internlm`, Jamba 1.5 `jamba`, Hunyuan-A13B `hunyuan_a13b`, LongCat-Flash `longcat`, GigaChat3 `gigachat3`, Apertus `apertus`, MiMo-V2.6 `mimo`.\[4\]
- **SGLang [V]:** Step-3 `step3`.\[18\]
- **llama.cpp native [V]:** Functionary v3.2, Firefunction v2.\[54\]
- **Not verified [U]:** Gorilla OpenFunctions, ERNIE 4.5, Seed-OSS, SmolLM3, EXAONE, Falcon, Ling/Ring, Hermes 4. Most of these are Hermes-style or prompt-based; check each template.

---

## §4 Inference server reference

### §4.1 vLLM (latest docs) [V]
**Flags:**
- `--enable-auto-tool-choice`, `--tool-call-parser`, `--tool-parser-plugin`, `--chat-template`, `--reasoning-parser`.\[4\]
- `--exclude-tools-when-tool-choice-none`.\[4\]
- `--tool-strict-level {auto,function,parameter}`.\[4\]
- `VLLM_ENFORCE_STRICT_TOOL_CALLING` (default true).\[4\]

**`tool_choice`:** supports auto, `required` (≥0.8.3), none and named.\[4\]
- Named and required use structured outputs (FSM compile latency on first use). "You are guaranteed a validly-parsable function call - not a high-quality one."\[4\]

| tool_choice | Obligation | Structural tag |
|---|---|---|
| named | call it | always |
| required | ≥1 call | always |
| auto | optional | if any tool `strict:true` or strict level raised |
| none | disabled | disabled |

**Strict mode:**
- The call envelope is constrained whenever a structural tag applies. Arguments are pinned only for `strict:true` tools or under `parameter`.\[4\]
- "Most OpenAI-compatible clients and agent frameworks never set `strict` … malformed markup can leak into the response". `--tool-strict-level function` addresses this.\[4\]
- `strict` works on Chat, Responses and Anthropic Messages.\[4\]
- Recommended schema style: `additionalProperties:false`, all properties required, optional fields as `["string","null"]`.\[4\]

**Parser names:** `hermes`, `mistral`, `llama3_json`, `llama4_pythonic`, `pythonic`, `granite`, `granite4`, `granite-20b-fc`, `internlm`, `jamba`, `xlam`, `deepseek_v3`, `deepseek_v31`, `openai`, `kimi_k2`, `hunyuan_a13b`, `cohere_command3/4`, `longcat`, `glm45`, `glm47`, `functiongemma`, `qwen3_xml`, `mimo`, `olmo3`, `gigachat3`, `apertus`.\[4\] Also in use: `qwen3_coder`, `minimax_m2` [S].
- A declarative `vllm.parser` streaming engine is replacing the regex parsers.

**Plugins:** a `ToolParser` implements `adjust_request` (e.g., `skip_special_tokens=False`), `extract_tool_calls` and `extract_tool_calls_streaming(previous_text, current_text, delta_text, …token_ids…)`, and registers via `ToolParserManager.register_lazy_module`.\[4\]

**Other:** Responses (incl. MCP tools), Anthropic Messages, an Interleaved Thinking page, Claude Code/Codex integrations, and `vllm bench serve` with BFCL data.\[4\]\[58\] Grammar backends are xgrammar (default), guidance and outlines [K].

### §4.2 SGLang [V]
**Documented names:** `apertus2509`, `deepseekv3`, `deepseekv31`, `deepseekv32`, `glm`, `gpt-oss`, `kimi_k2`, `llama3`, `llama4`, `mistral`, `pythonic`, `qwen`, `qwen3_coder`, `step3`.\[18\]

**Accepted in 0.5.6.post2:** also `glm45`, `qwen25` (deprecated) and `minimax-m2`. Newer builds add `glm47`;\[18\]\[39\]\[40\] `deepseekv4` is [S].

**Defaults:** "`--reasoning-parser` and `--tool-call-parser` both default to None, not 'auto'". Always set both.\[39\]

**Encoders:** non-Jinja encoders exist for DeepSeek V3.2/V4 and Kimi K3.\[21\] Grammars use xgrammar/outlines/llguidance [K].

### §4.3 llama.cpp [V]
- "OpenAI-style function calling is supported with the `--jinja` flag (and may require a `--chat-template-file` override …)".\[59\]
- "Generic tool call is supported when the template isn't recognized … (`Chat format: Generic` in the logs)"; generic mode "may consume more tokens and be less efficient".\[54\]\[60\]
- Native formats include Qwen2.5, Mistral Nemo, Llama 3.3, Granite 4.1, Functionary, Hermes (with override), Firefunction, Command R7B and DeepSeek R1 distills.\[54\]
- An Anthropic-compatible `/v1/messages` exists (tools require `--jinja`).\[59\]
- `--reasoning-format deepseek` extracts reasoning.\[61\]\[62\]
- Internals: in-house Jinja engine, PEG parser, autoparser, tool-call grammars; lazy grammars trigger on the call opener [K].
- The template embedded in a GGUF can lag upstream [S].\[23\]

### §4.4 Ollama [V]
- Each registry model declares a Go `renderer` and `parser` (e.g., `qwen3.5`, `glm-4.7`).\[6\]
- A wrong mapping silently breaks tools (#14493).\[6\]
- Parsers match literal delimiters (#18659).\[34\]

### §4.5 Others
- LM Studio made `/v1/responses` Open Responses-compliant on launch day [V]. Open WebUI has experimental Open Responses support [V].\[63\]\[64\]
- vllm-mlx, mlx-lm/mlx-vlm (Harmony PRs), OpenVINO GenAI (adding a Qwen3-Coder parser) and NVIDIA Dynamo have their own parsers [S].\[1\]\[57\]\[65\]\[66\]\[67\] mlx_lm "silently drops the tools array" when the template lacks tool support [S].\[26\]
- TGI, TensorRT-LLM/NIM, LMDeploy, LocalAI, TabbyAPI and KoboldCpp were not re-verified [U].
- **transformers [K]:** `apply_chat_template(messages, tools=[…], add_generation_prompt=True, **kwargs)`. Tools can be Python functions converted by `get_json_schema` from type hints and docstrings. Calls go in `tool_calls`; results use `role:"tool"`.

### §4.6 Hosted-provider variance
**Moonshot K2 Vendor Verifier [V/S]:**
- Built because "Kimi K2 performance is inconsistent across API vendors".\[68\]
- Coverage grew from 9 to 12 providers in Oct 2025; Moonshot's @Kimi_Moonshot post on X said: "We've updated the providers counts from 9 to 12, and open-sourced more data entries". A later run covered 18 providers for kimi-k2-0905 (2025-10-23) [S].
- Metrics: ToolCall-Trigger Similarity and Schema Accuracy.\[69\]
- It has since been extended as the Kimi Vendor Verifier (KVV), which Moonshot's blog "Rebuilding the 'Chain of Trust'" says was open-sourced "alongside the release of the Kimi K2.6 model". The suite includes "K2VV ToolCall: Measures trigger consistency (F1) and JSON Schema accuracy" along with vision and agentic tasks.
- An anecdote from Hacker News user foundry27 (thread 47838703) claims "AWS Bedrock… has crippling defects in its serving stack for Kimi's K2 and K2.5 models that cause 20%-30% of attempts to emit tool calls to instead silently end the conversation (with no token output)" [S/U].

**vLLM × K2 (2025-10-28) [V]:**
- Moonshot API: 1286 calls, 0 schema errors.\[27\]
- vLLM 0.11.0 baseline: 248 tool finishes, 218 successful.\[27\]
- Causes:
  1. `add_generation_prompt` was dropped because it was only accepted via `**kwargs`.\[27\]
  2. `''` content became `[{'type':'text','text':''}]` and rendered literally.\[27\]
  3. The parser was too strict on non-conforming IDs.\[27\]
- After fixes: 1325 triggered, 1007 successful, 318 schema errors, F1 83.57%, schema accuracy 76.00%. The post also says "218 to 971", which is internally inconsistent.\[27\]
- The remaining errors were calls to undeclared tools. Moonshot's API uses a constrained-decoding "Enforcer" that vLLM lacked.\[27\]

**OpenRouter [V]:**
- `:exacto` (2025-10-22) is a set of curated providers.\[70\]\[71\] OpenRouter's Auto Exacto blog says "Exacto showed a 10-20% increase in scores across Tau2Bench and LiveMCPBench compared to default routing".
- **Auto Exacto** (2026-03-12) is "on by default for tool-calling requests". It re-ranks providers about every 5 min using throughput, tool-call telemetry ("JSON validity, schema compliance, tool name accuracy") and benchmarks (TauBench, GPQA-Diamond).\[70\]\[72\]
- OpenRouter's Auto Exacto blog (2026-03-12) gives per-model results: "GLM-5 and GLM-4.7 tool call error rate dropped by 88% and 80%"; "gpt-oss-120b error rate dropped by 36%, from 5.6% to 3.5%"; "DeepSeek V3.2 tool call error rates dropped by 16%". Price sort or `:floor` opts out.

**Implications:**
- Treat (model, provider, version) as the unit you test.
- Pin providers or use quality routing.
- Run canaries.
- Log raw output.
- Expect the worst accuracy in the first weeks after a release ("particularly when a model is only a few weeks old").\[70\]

---

## §5 API schema mapping

| Concept | OpenAI Chat | Responses / Open Responses | Anthropic | Gemini | Bedrock Converse | MCP |
|---|---|---|---|---|---|---|
| Tool def | `{type:"function",function:{name,description,parameters,strict?}}` | `{type:"function",name,description,parameters,strict}`; `custom` (grammar) | `{name,description,input_schema,strict?,defer_loading?,input_examples?,allowed_callers?}`; server tools | `functionDeclarations[{name,description,parameters\|parametersJsonSchema}]` | `toolSpec{name,description,inputSchema{json}}` | `Tool{name,title?,description,inputSchema,outputSchema?,annotations?,icons?}` |
| Choice | `auto\|none\|required\|{function:{name}}`, `parallel_tool_calls` | same + `allowed_tools` | `{type:auto\|any\|tool\|none}`, `disable_parallel_tool_use` | `mode AUTO\|ANY\|NONE\|VALIDATED`, `allowedFunctionNames` | `{auto}\|{any}\|{tool}` | host-side |
| Call | `tool_calls[{id,function:{name,arguments:str}}]` | `function_call{call_id,name,arguments:str}` | `tool_use{id,name,input:obj}` | `functionCall{name,args:obj,id?}` | `toolUse{toolUseId,name,input}` | `tools/call{name,arguments:obj}` |
| Result | `{role:"tool",tool_call_id,content}` | `function_call_output{call_id,output}` | `tool_result{tool_use_id,content,is_error?}` | `functionResponse{name,response}` | `toolResult{toolUseId,content,status?}` | `CallToolResult{content,structuredContent?,isError}` |
| Reasoning | non-standard `reasoning_content`/`reasoning` | `reasoning` items | `thinking`+`signature` | `thoughtSignature` | `reasoningContent` | – |
| Streaming | `delta.tool_calls[{index,id?,function{name?,arguments}}]` | semantic events (`function_call_arguments.delta`) | `input_json_delta`; fine-grained streaming | streamed parts | `contentBlockDelta.toolUse.input` | Tasks ext |
| Schema | JSON Schema subset; strict subset | same | JSON Schema; strict | OpenAPI-subset or JSON Schema | JSON Schema | full 2020-12 (2026-07-28) |

Table cells are [K] unless confirmed in §5.1–5.4.

**§5.1 OpenAI strict [V/S]:**
- "Structured Outputs supports a subset of the JSON Schema language."\[73\]
- "All fields must be required"; optional fields are emulated with a null union.\[73\]
- "`additionalProperties: false` must always be set".\[73\]
- `anyOf` subschemas must follow the subset. Definitions and recursion are supported.\[73\]
- Unsupported: `allOf`, `not`, `dependentRequired`, `dependentSchemas`, `if/then/else` [S].\[74\]\[75\]
- Limits: "up to 5000 object properties total, with up to 10 levels of nesting" and "up to 1000 enum values" [S]. The root must be an object [S].\[75\]\[76\]
- Responses `custom` tools accept Lark or regex grammars [K].

**§5.2 Gemini modes [V]:**
- "AUTO: Default mode when only function_declarations tool enabled."\[77\]
- "ANY: … constrained to always predict a function call and ensures function schema adherence." Very large or deeply nested schemas may be rejected.\[77\]
- "NONE: … prohibited from making function calls."\[77\]
- "VALIDATED: Default mode for tool combination … reduces malformed function calls (compared to AUTO mode)". Vertex adds that from Gemini 3 it "also enforces the presence of required parameters".\[77\]\[78\]
- The Interactions API uses lowercase `auto|any|none|validated`.\[79\]

**§5.3 Anthropic [V/S]:**
- `strict:true` gives schema-guaranteed inputs.
- Tool search: `tool_search_tool_regex_20251119`/`_bm25_20251119` with `defer_loading:true` on other tools. Deferring every tool returns 400. Custom search tools return `tool_reference` blocks. Beta headers: `advanced-tool-use-2025-11-20`, `tool-search-tool-2025-10-19`.\[80\]\[81\]\[82\]
- Programmatic tool calling: `allowed_callers:["code_execution_20250825"]`. Reported to be incompatible with `strict`, forced `tool_choice` and `disable_parallel_tool_use` [S].\[83\]\[84\]
- `input_examples` [S].\[83\]

**§5.4 Open Responses [V]:**
- "An open-source specification … inspired by the OpenAI Responses API". It defines "Items as the atomic unit of context, with clear state machines", "Semantic streaming events", and extensibility for provider-specific items.\[85\]
- Ships dated OpenAPI releases and compliance tests, plus an optional WebSocket transport. Supersets count as compliant.\[85\]\[86\]
- Implementations: LM Studio, Open WebUI,\[63\]\[64\] and vLLM's Responses endpoint.

**§5.5 Streaming [K]:**
- Accumulate deltas by `index`; parse only at the end.
- Servers vary: the name may arrive late, `{` may arrive as its own delta (vLLM `qwen3_xml`) [V], and `finish_reason` may be `stop` even when tool_calls are present.\[87\]

---

## §6 Higher-level protocols

```
UX:            AG-UI (agent↔frontend) | Agent Client Protocol (editor↔agent)
Agent↔agent:   A2A (absorbed IBM ACP 2025-08-29; in AAIF 2026-08)
Files:         AGENTS.md | Agent Skills (SKILL.md)
Tool supply:   MCP | OpenAPI-as-tools | UTCP | code-mode
HARNESS:       canonical items, adapters, validation, policy
Wire:          OpenAI Chat | Responses/Open Responses | Anthropic | Gemini | Bedrock
Runtime:       vLLM | SGLang | llama.cpp | Ollama | hosted (template+parser)
Model:         chat template + special tokens
```
MCP never reaches the model. The harness converts MCP `Tool` objects into wire tool definitions and model calls into `tools/call`.

**MCP versions:**
- **2024-11-05:** JSON-RPC; tools/resources/prompts; stdio and HTTP+SSE [S].\[88\]
- **2025-03-26:** Streamable HTTP, OAuth 2.1 [S],\[88\] and tool annotations `readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint` [K].
- **2025-06-18:** removed JSON-RPC batching; structured output (`outputSchema`/`structuredContent`); elicitation [V/S].\[88\]\[89\]
- **2025-11-25 [V]:**
  - OIDC discovery, icons, incremental consent.\[90\]
  - Tool-name guidance (SEP-986).\[90\]
  - URL-mode elicitation.\[90\]
  - Tool calling in sampling (SEP-1577).\[90\]
  - Client ID Metadata Documents.\[90\]
  - Experimental tasks (SEP-1686).\[90\]\[91\]
  - "Input validation errors should be returned as Tool Execution Errors rather than Protocol Errors to enable model self-correction (SEP-1303)".\[90\]
  - Governance (SEP-932).\[90\]
- **2026-07-28 (current; RC 2026-05-21) [V]:**
  - Stateless core: the `initialize` handshake (SEP-2575) and `Mcp-Session-Id` (SEP-2567) are removed. Version, client info and capabilities travel in `_meta`, and `server/discover` is new.\[92\]
  - Required `Mcp-Method`/`Mcp-Name` headers.\[92\]
  - Multi Round-Trip Requests (`resultType:"input_required"`, `requestState`).\[92\]
  - `ttlMs`/`cacheScope`; W3C trace context.\[92\]
  - Extensions framework, including MCP Apps and the **Tasks extension** (`tasks/get/update/cancel`; `tasks/list` removed).\[92\]
  - Roots, Sampling and Logging deprecated.\[92\]
  - **Full JSON Schema 2020-12 for `inputSchema`/`outputSchema`**: root stays `type:"object"`, but `oneOf/anyOf/allOf`, conditionals and `$ref/$defs` are allowed; external `$ref` must not be auto-dereferenced.\[92\]
  - Error `-32002`→`-32602`.\[92\]
  - `iss` validation (RFC 9207).\[92\]
- **Governance [V]:** the Linux Foundation formed the Agentic AI Foundation (AAIF) on 2025-12-09 with MCP, goose and AGENTS.md. A2A joined in Aug 2026.\[93\]\[94\] The MCP Registry and `.mcpb` bundles exist [S].
- **Consequence:** because MCP schemas may now contain features many open-weight templates, grammars and providers reject, a sanitizer (§7.6) is mandatory.

**Others:**
- **A2A:** agent cards, task delegation [V].\[94\]
- **Agent Client Protocol (Zed) [K]:** JSON-RPC over stdio between editor and agent. Not to be confused with IBM ACP.
- **AG-UI [K]:** frontend event stream including tool-call start/args/end.
- **Agent Skills [K]:** `SKILL.md` folders loaded progressively; needs only file and shell tools.
- **UTCP [K/U]:** direct-call manuals.
- **OpenAPI-as-tools:** watch tool count and `$ref`/`oneOf`.
- **Code-as-action [K]:** CodeAct, smolagents `CodeAgent`, "code execution with MCP". These need one `execute_code` tool and a sandbox, making them the most format-robust option for open weights.

---

## §7 Recommended harness architecture

### §7.1 Canonical items
```jsonc
{"type":"message","role":"system|developer|user|assistant","content":[{"type":"text","text":"…"}]}
{"type":"reasoning","id":"rs_1","text":"…","encrypted":null,"signature":null}
{"type":"function_call","call_id":"c_0001","name":"read_file","arguments":"{\"path\":\"a.txt\"}","provider_ids":{"kimi":"functions.read_file:0","mistral":"Ab3dE9fG1"}}
{"type":"function_call_output","call_id":"c_0001","output":"…","is_error":false}
```
- A tool definition is `{name, description, input_schema (2020-12), output_schema?, annotations, examples?}`.
- Store the raw assistant text where available.

### §7.2 Adapters and decision tree
```
Closed API → native adapter (+strict).
Open weights:
1. Server has parser for exact model version AND conformance suite passes → Chat Completions/Responses native tools (+strict/structural tags).
2. Else, if /v1/completions reachable → render official template/encoder client-side (chat_template.jinja, DeepSeek encoding.py, openai-harmony, mistral-common) + per-family parser (+guided decoding).
3. Else / no tool training → prompt fallback: Hermes JSON for ChatML/Qwen lineage; pythonic for Llama 3.2/4; Qwen3-Coder XML for code models; single execute_code tool for strong coders; constrain with JSON-schema/regex/Lark if supported.
4. >~30 tools or MCP fan-out → client-side tool search/deferred loading or code-mode.
```
- **Why native first:** in the K2 investigation, client-side templating "resolved the majority of failures". BFCL finds some models cannot emit foreign formats at all ("watt-tool-70B is unable to correctly output JSON format function calls"; CoALM-70B fails with tag requirements) [V].\[27\]\[95\]

### §7.3 Constrained decoding
- **Options:** vLLM named/required/`strict`/`--tool-strict-level`; SGLang/llama.cpp grammars; Gemini ANY/VALIDATED; OpenAI/Anthropic strict. Client-side: Outlines, Guidance, xgrammar, Instructor (validate and retry), BAML (schema-aligned parsing).
- Constrain the model's **native** envelope; structural tags do this.
- Restrict tool names to the declared set, as Moonshot's Enforcer does.\[27\]
- Syntactic validity does not mean semantic correctness.

### §7.4 Streaming, validation, repair
- Accumulate streamed calls by index and execute only complete calls.
- Run the reasoning parser before the tool parser, and never JSON-parse reasoning ("Never run JSON parsing over the thinking trace", Together) [V].\[96\]
- **Leak recovery:** if `content` contains `<|tool_call_begin|>`, `<tool_call>`, `<｜DSML｜`, `<minimax:tool_call>`, `[TOOL_CALLS]` or `<|start|>assistant`, parse client-side and log a provider defect.
- **Repair pipeline:**
  1. Run json-repair.
  2. Validate against the full schema.
  3. Coerce types (string→int, stringified arrays→arrays).
  4. Unwrap DSML `arguments` collapse.
  5. Reject unknown tool names.
  6. Return validation errors as **tool-result errors** with the JSON pointer and expected type (per MCP SEP-1303's rationale).
  7. Allow at most 2–3 retries.

### §7.5 Reasoning policy

| Family | Rule |
|---|---|
| GLM 4.5→5.3 | return reasoning with tool results; agents: `clear_thinking:false`, exact blocks [V] |
| Kimi K2-Thinking/K2.5/K2.6 | keep across tool loop; `preserve_thinking:true` [S] |
| MiniMax M2.x | keep `<think>`/`reasoning_details` verbatim [V/S] |
| Qwen3.5/3.6 | `preserve_thinking:true` for agents [S] |
| gpt-oss | keep analysis inside unfinished tool loop; drop after `final` [K] |
| Gemma 4 | never remove thoughts between calls within a turn [V] |
| DeepSeek V4 | use encoder `thinking_mode` [V] |
| Anthropic/Gemini | return `thinking`+`signature` / `thoughtSignature` unchanged [K] |

Store reasoning losslessly, never edit it, and let the adapter apply this table.

### §7.6 Schema sanitization (portable profile)
- Root `type:object` with `properties` and `required` always present.
- Inline local `$ref`/`$defs`; never fetch external refs; flatten recursion for non-OpenAI targets.
- Merge `allOf`; turn `oneOf` into `anyOf`. If unions are unsupported, split the tool or string-encode the field.
- Drop `if/then/else`, `not`, `dependent*`, `patternProperties`, `unevaluated*`, `format` and `default`; move their meaning into `description`.
- Strict targets: every property required, optional fields as `["T","null"]`, `additionalProperties:false`. Non-strict open-weight targets keep optional fields optional.
- Enums: string values, ≤1000 total.
- Nesting ≤5 for small models (OpenAI allows 10).
- Names: `^[a-zA-Z0-9_-]{1,64}$` with no dots (Kimi splits on `.`).\[97\] Map MCP namespacing such as `server::tool` to `server__tool`.
- Put units, formats and examples in descriptions, since templates render descriptions as comments or JSON.
- Keep the full schema for validation.

### §7.7 IDs and history
- Mint canonical IDs and remap per provider:
  - Mistral: 9 alphanumeric characters.
  - Kimi: regenerate `functions.{name}:{global_idx}` across the whole history on every request.\[28\]\[29\]
  - Anthropic: echo `toolu_…`.
- Give exactly one result per call, in order. Synthesize "cancelled" results for aborted calls.
- Prefer `null` or omitted content on call-only assistant turns, and test it (K2 issue 2).\[27\]
- Make sure `add_generation_prompt=True` reaches the template (K2 issue 1).\[27\]
- Keep tool declarations stable across turns; history with undeclared tools causes hallucinated calls.\[27\]

### §7.8 Testing
- **Golden transcripts per family:**
  - Single and parallel calls.
  - Multi-turn with prior calls in history.
  - Code-heavy multi-line argument with quotes and backslashes.
  - Unicode, empty args, nested objects, enums.
  - A no-call case.
  - `tool_choice` required/named/none.
  - Streaming and non-streaming.
  - Thinking on and off.
- **Assertions:** name and args, no special tokens in content, reasoning separated, IDs round-trip, `finish_reason`.
- **Metrics:** K2VV-style trigger similarity vs a reference and schema accuracy. Also BFCL AST subsets, τ²-bench, and MCP suites (MCP-Bench, MCPMark, MCP-Universe, LiveMCPBench, MCP-Atlas [U]).
- Re-run on every template, runtime or provider change.

### §7.9 Execution and security
- Per-tool timeouts. Idempotency keys for side-effecting tools; MCP annotations are hints only. Retry only idempotent tools.
- Long-running work: MCP Tasks extension, or explicit handles passed as arguments (the MCP 2026 blog's `basket_id` pattern).\[92\]
- Treat tool output as untrusted:
  - Wrap it in delimiters.
  - Strip control tokens (`<|im_start|>`, `<tool_call>`, `<｜DSML｜`, `<|start|>`).
  - Never let it change permissions.
- Sandbox code and shell tools with no ambient credentials. Require human approval for destructive tools.
- Avoid parsers that `eval()` model output.

### §7.10 Compatibility checklist
1. Tool parser and reasoning parser set (SGLang defaults to none).
2. Template pinned to an HF commit; GGUF template matches upstream.
3. `add_generation_prompt` honored and empty-content handling tested.
4. ID remap configured.
5. Reasoning policy configured.
6. Sanitizer profile chosen.
7. Streaming deltas verified.
8. Parallel calls verified, or disabled.
9. `required`/named `tool_choice` verified.
10. Leak recovery enabled and raw output logged.
11. Quantization level recorded and suite re-run.
12. Provider pinned or quality-routed; canary suite scheduled.

---

## §8 Failure modes

| # | Failure | Evidence | Mitigation |
|---|---|---|---|
| F1 | Wrong parser/renderer for version | Ollama Qwen3.5 [V]; DeepSeek V4.1 vs V4 [S]; SGLang no parser → DSML in content [V] | version-pinned registry; tests |
| F2 | Template kwargs dropped | K2 `add_generation_prompt` [V] | raw-template probe; fixed templates |
| F3 | Content normalization | `''`→list rendered literally [V] | null/omit |
| F4 | Bad history IDs | Kimi `search:2`, `call_<hex>` [V] | per-family ID remap |
| F5 | Mistral ID length | template exception [V] | 9-char IDs |
| F6 | Delimiter inside values | GLM `</tool_call>` [V]; Qwen fenced code [V] | constrained envelope; stateful parser |
| F7 | Reasoning stripped | GLM/Kimi/MiniMax guidance [V/S] | §7.5 |
| F8 | Reasoning leaks | Ollama missing `</think>` [V] | correct reasoning parser |
| F9 | Format collapse after round 1 | DeepSeek V4-Flash-Vision 80–100% [S] | unwrap; strict args |
| F10 | Lookalike tokens | `<||DSML||>` [S] | normalize |
| F11 | Undeclared tools called | K2 on vLLM [V] | name constraint; reject |
| F12 | Type slips | Llama arrays-as-strings [V] | schema coercion |
| F13 | Small models fail format | Llama 3.2 [V]; FunctionGemma [V] | constrain; fine-tune |
| F14 | Provider variance | K2VV; OpenRouter Auto Exacto: GLM-5 −88%, GLM-4.7 −80%, gpt-oss-120b −36%, DeepSeek V3.2 −16% tool-call errors [V] | pin; Exacto; canaries |
| F15 | Quantization | 2-bit still 98% native [S]; unspecified quants [S] | record + retest |
| F16 | Streaming quirks | split `{` deltas [V] | index accumulation |
| F17 | Bindings ignore tools | llama-cpp-python Gemma 4; mlx_lm [S] | leak recovery |
| F18 | Harmony headers | vLLM #58825 [V] | accept both placements; validate recipient |
| F19 | Rich MCP schemas | 2026-07-28 2020-12 [V] | sanitizer |
| F20 | Tools sent with `none` | vLLM default [V] | exclude flag |

---

## §9 Evidence summary
- **BFCL v4 (Jul 2025) [V]:**
  - Categories include AST, live, multi-turn, web search, memory and format sensitivity (26 configurations × 200 cases).\[98\]
  - Format sensitivity is "only supported for prompt (non-FC) models".\[99\]
  - Models are "generally\[95\] robust to prompt format and style variations", but return format and tool-call tags break some models.
  - Secondary figures: GLM-4.5 (FC) 70.85 overall / 65.62 format sensitivity; xLAM-2-8b-fc-r 70.50 multi-turn [S].
  - Papers often run both FC (via vLLM parsers) and Prompt mode and report the best (arXiv 2605.07731) [V]. Neither mode dominates.
- **Infrastructure dominates:** the vLLM K2 numbers, plus OpenRouter's Auto Exacto per-model drops in tool-call error rates (GLM-5 88%, GLM-4.7 80%, gpt-oss-120b 36% from 5.6% to 3.5%, DeepSeek V3.2 16%) [V].
- **Native format:** DSML 98% vs Hermes 82% (one community test) [S].
- **"Notation Matters" (arXiv 2605.29676):** studies token-optimized serialization inside BFCL; numbers not captured [U].
- **τ²-bench/Terminal-Bench 2:** run with Preserved Thinking per the GLM-4.7 card [V].
- **Vendor SWE-bench:** Together AI's DeepSeek V4 Pro page lists "80.6% SWE-Bench Verified, 76.2% SWE-Bench Multilingual, 55.4% SWE-Bench Pro"; V4-Flash-Max 79.0% [S]. These are vendor-reported, not harness-controlled.
- **Tool count:** Anthropic Engineering's "Introducing advanced tool use" reports that with tool search, "Total context consumption: ~8.7K tokens, preserving 95% of context window". Loading 50+ MCP tools upfront costs "~77K tokens before any work begins" [V].
- **Not captured [U]:** ACEBench, NESTFUL, ComplexFuncBench, When2Call, the MCP benchmarks, controlled JSON/XML/code comparisons, constrained-decoding-vs-reasoning studies, quantization ablations.

---

## §10 Open questions / fast-moving
1. Parser names drift across releases: `qwen3_xml` vs `qwen3_coder`; `glm`/`glm45`/`glm47`; `deepseekv4`. Check `--help` on the deployed version.
2. Expect more DSML-style micro-revisions like V4 vs V4.1. Prefer vendor encoders over hand-written templates.
3. Formats for Kimi K3, later Qwen open weights, MiniMax M3, Mistral Large 3/Medium 3.5, Hermes 4 and Nemotron 3 are unverified.
4. MCP clients and servers will straddle 2025-11-25 sessions and the 2026-07-28 stateless revision for months; the Tasks lifecycle has breaking changes.
5. Reasoning round-trip fields are not standardized (`reasoning_content`, `reasoning`, `reasoning_details`). Open Responses is the likely convergence point.
6. Structural tags (2026) are new and implemented per parser. Grammar-forcing a non-native envelope may hurt accuracy.
7. The Gemma 4 call body and its parallel-call behavior need template confirmation.
8. Provider-variance data is mostly self-reported by Moonshot and OpenRouter.

## §11 Caveats
- Sources are attributed inline by name, issue/PR number and date, per output rules. Primary sources:
  - vLLM tool-calling docs; SGLang tool-parser docs and PRs #34050/#40497.
  - llama.cpp function-calling docs.
  - DeepSeek V4/V4.1 `encoding/README.md`; Kimi `tool_call_guidance.md`; MiniMax-M2.7 guide; Gemma 4 prompt-formatting doc; OpenAI Harmony cookbook; Z.ai thinking docs; mistral-common.
  - MCP changelogs and the 2026-07-28 RC blog; Open Responses spec.
  - OpenRouter blogs; vLLM K2 blog; BFCL v4 blogs; OpenAI/Gemini/Anthropic docs.
- Family release facts marked [S]/[U] come from aggregators. [K] strings must be byte-verified against current templates before use in parsers.

## Sources

1. [Tool call parser for the Qwen3-Coder XML format (Qwen3-Coder, Qwen3.5, Qwen3.6) · Issue #4543 · openvinotoolkit/openvino.genai](https://github.com/openvinotoolkit/openvino.genai/issues/4543)
2. [encoding/README.md · deepseek-ai/DeepSeek-V4-Pro at main](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md)
3. [Gemma 4 Prompt Formatting | Google AI for Developers](https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4)
4. [vllm/docs/features/tool\_calling.md at main · vllm-project/vllm](https://github.com/vllm-project/vllm/blob/main/docs/features/tool_calling.md)
5. [Function Calling - Qwen](https://qwen.readthedocs.io/en/latest/framework/function_call.html)
6. [Qwen 3.5 27B: Tool calling completely non-functional and repetition penalties silently ignored · Issue #14493 · ollama/ollama](https://github.com/ollama/ollama/issues/14493)
7. [qwen3coder tool parser](https://huggingface.co/QuantTrio/Qwen3-Coder-30B-A3B-Instruct-GPTQ-Int8/blob/main/qwen3coder_tool_parser.py)
8. [Qwen/Qwen3-Coder-Next · recommended vllm tool call parser?](https://huggingface.co/Qwen/Qwen3-Coder-Next/discussions/17)
9. [\[Bug\]: Qwen3 parser treats \<tool\_call\> inside fenced code blocks as a real tool call · Issue #57541 · vllm-project/vllm](https://github.com/vllm-project/vllm/issues/57541)
10. [Qwen](https://en.wikipedia.org/wiki/Qwen)
11. [Release 1.5.0 - Mistral Tokenizer v7 (new System Prompt + Fn calling) · mistralai/mistral-common](https://github.com/mistralai/mistral-common/releases/tag/v1.5.0)
12. [mistral\_tool\_parser - vLLM](https://docs.vllm.ai/en/latest/api/vllm/tool_parsers/mistral_tool_parser/)
13. [mistral - vLLM](https://docs.vllm.ai/en/latest/api/vllm/parser/mistral/)
14. [mistral\_tool\_parser - vllm-mlx](https://vllm-mlx.is-a.dev/reference/api/vllm_mlx/tool_parsers/mistral_tool_parser/)
15. [Issue · mistralai/mistral-common](https://github.com/mistralai/mistral-common/issues/345)
16. [\[BUG: Malformed v2-v7 tool call outputs crash \`\_decode\_tool\_calls\` with \`TypeError\`/\`KeyError\` (HTTP 500 in experimental app)\] · Issue #309 · mistralai/mistral-common](https://github.com/mistralai/mistral-common/issues/309)
17. [\[Bugfix\]\[Parser\] Mistral pre-v11: don't fail requests on unexpected tool call JSON by sfeng33 · Pull Request #59308 · vllm-project/vllm](https://github.com/vllm-project/vllm/pull/59308)
18. [Tool Parser — SGLang](https://docs.sglang.io/advanced_features/tool_parser.html)
19. [GLM-5.2 vs DeepSeek V4 vs Kimi K2.6: 62% SWE Pro \[2026\]](https://tech-insider.org/glm-5-2-vs-deepseek-v4-vs-kimi-k2-2026/)
20. [deepseek\_v4\_encoding - vLLM](https://docs.vllm.ai/en/latest/api/vllm/tokenizers/deepseek_v4_encoding/)
21. [Default the tool-call parser when dsv4/dsv32 encoding is used by guptaishaan · Pull Request #34050 · sgl-project/sglang](https://github.com/sgl-project/sglang/pull/34050)
22. [encoding/README.md · deepseek-ai/DeepSeek-V4.1-Flash at main](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/encoding/README.md)
23. [chat: DeepSeek V4.1 renders DSML tag names with a leading space by midagedev · Pull Request #4 · vcruz305/llama.cpp](https://github.com/vcruz305/llama.cpp/pull/4)
24. [deepseek-ai/DeepSeek-V4-Flash-Vision-Exp · sglang/vllm Tool call Error: invalid arguments: missing required property](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-Vision-Exp/discussions/13)
25. [deepseek-ai/DeepSeek-V4-Pro · DeepSeek model output sometimes contains DSML tool-call markup](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/discussions/209)
26. [deepseek-ai/DeepSeek-V4-Flash · Add chat template](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/discussions/16)
27. [Chasing 100% Accuracy: A Deep Dive into Debugging Kimi K2's Tool-Calling on vLLM](https://blog.vllm.ai/2025/10/28/Kimi-K2-Accuracy.html)
28. [docs/tool\_call\_guidance.md · moonshotai/Kimi-K2-Thinking at main](https://huggingface.co/moonshotai/Kimi-K2-Thinking/blob/main/docs/tool_call_guidance.md)
29. [Chasing 100% Accuracy: A Deep Dive into Debugging Kimi K2's Tool-Calling on vLLM](https://vllm.ai/blog/2025-10-28-kimi-k2-accuracy)
30. [Add \`kimi\_k2\` Tool Call Parser for Kimi K2/K2.5 Models · Issue #174 · cubist38/mlx-openai-server](https://github.com/cubist38/mlx-openai-server/issues/174)
31. [Chat template kwargs - Featherless.ai](https://featherless.ai/docs/chat-template-kwargs)
32. [Best Open-Source LLM in May 2026: Llama 4 vs Qwen 3.5 vs DeepSeek V4 vs Gemma 4 vs Mistral Medium 3.5](https://codersera.com/blog/best-open-source-llm-2026-llama-4-qwen-3-5-deepseek-v4-gemma-4-mistral/)
33. [Kimi (chatbot)](<https://en.wikipedia.org/wiki/Kimi_(chatbot)>)
34. [glm-4.7: \`\</tool\_call\>\` inside an \`\<arg\_value\>\` ends the tool call early; the rest of the argument leaks into content · Issue #18659 · ollama/ollama](https://github.com/ollama/ollama/issues/18659)
35. [Thinking Mode - Overview - Z.AI DEVELOPER DOCUMENT](https://docs.z.ai/guides/capabilities/thinking-mode)
36. [zai-org/GLM-4.7 · Hugging Face](https://huggingface.co/zai-org/GLM-4.7)
37. [GLM Thinking Mode: Reasoning Effort and When to Turn It Off](https://glm-ai.chat/docs/glm-thinking-mode/)
38. [GLM-5.2 quickstart - Together AI docs](https://docs.together.ai/docs/glm-5.2-quickstart)
39. [\[Docs\] GLM-5.3 cookbook: pass the reasoning/tool-call parsers in every deploy command by b8zhong · Pull Request #40497 · sgl-project/sglang](https://github.com/sgl-project/sglang/pull/40497)
40. [\[Ask for help\] How to deploy GLM-4.7 · Issue #15860 · sgl-project/sglang](https://github.com/sgl-project/sglang/issues/15860)
41. [OpenAI Harmony Response Format](https://developers.openai.com/cookbook/articles/openai-harmony)
42. [MLX server: split gpt-oss's Harmony channels by egonSchiele · Pull Request #1122 · egonSchiele/agency-lang](https://github.com/egonSchiele/agency-lang/pull/1122)
43. [OpenAI Harmony Format Specification - imos laboratory](https://imoz.jp/scraps/202604_harmony.en.html)
44. [openai/gpt-oss-20b · Tool Calling in Chat Template](https://huggingface.co/openai/gpt-oss-20b/discussions/160)
45. [ChatML vs Harmony: Understanding the new Format from OpenAI 🔍](https://huggingface.co/blog/kuotient/chatml-vs-harmony)
46. [\[Bug\]: gpt-oss (HarmonyParser): a stray 'commentary to=assistant' header is returned as a tool call named 'assistant\<|channel|\>analysis' · Issue #58825 · vllm-project/vllm](https://github.com/vllm-project/vllm/issues/58825)
47. [Gemma (language model)](<https://en.wikipedia.org/wiki/Gemma_(language_model)>)
48. [Gemma 4 tool calls returned as raw native tokens in \`content\` instead of \`tool\_calls\` · Issue #2227 · abetlen/llama-cpp-python](https://github.com/abetlen/llama-cpp-python/issues/2227)
49. [docs/tool\_calling\_guide\_cn.md · MiniMaxAI/MiniMax-M2 at main](https://huggingface.co/MiniMaxAI/MiniMax-M2/blob/main/docs/tool_calling_guide_cn.md)
50. [MiniMax-M2.7/docs/tool\_calling\_guide.md at main · MiniMax-AI/MiniMax-M2.7](https://github.com/MiniMax-AI/MiniMax-M2.7/blob/main/docs/tool_calling_guide.md)
51. [update: tool calling guide · MiniMaxAI/MiniMax-M2.5 at 5fb9455](https://huggingface.co/MiniMaxAI/MiniMax-M2.5/commit/5fb9455421adc47f561f139d4e925b4c88c44367)
52. [Tool Use & Interleaved Thinking - Models - MiniMax API Docs](https://platform.minimax.io/docs/guides/text-m3-function-call)
53. [MiniMax-M2: MoE Model for Agentic and Coding Capabilities](https://www.digitalocean.com/community/tutorials/minimax-m2-moe-model-agentic-coding)
54. [llama.cpp/docs/function-calling.md at master · ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)
55. [OpenAI-Compatible Server — vLLM](https://docs.vllm.ai/en/v0.8.3/serving/openai_compatible_server.html)
56. [GitHub - xigh/open-weight-models: Curated list of open-weight AI models with commercially exploitable licenses, verified benchmarks, and no EU restrictions. · GitHub](https://github.com/xigh/open-weight-models)
57. [vllm-mlx/docs/guides/tool-calling.md at main · waybarrios/vllm-mlx](https://github.com/waybarrios/vllm-mlx/blob/main/docs/guides/tool-calling.md)
58. [Tool Calling - vLLM](https://docs.vllm.ai/en/latest/features/tool_calling/)
59. [llama.cpp/tools/server/README.md at master · ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
60. [docs/function-calling.md · b5246 · USTC-OS-Lab / llama.cpp · GitLab](https://git.ustc.edu.cn/ustc-os-lab/llama.cpp/-/blob/b5246/docs/function-calling.md)
61. [Troubleshooting llama.cpp Tool Calls](https://netclaw.dev/troubleshooting/llama-cpp/)
62. [llama.cpp - Qwen](https://qwen.readthedocs.io/en/latest/run_locally/llama.cpp.html)
63. [Open Responses with local models via LM Studio](https://lmstudio.ai/blog/openresponses)
64. [Open Responses / Open WebUI](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-open-responses/)
65. [gpt-oss: parse harmony channels into reasoning and content by Lazarus-931 · Pull Request #2329 · Blaizzy/mlx-vlm](https://github.com/Blaizzy/mlx-vlm/pull/2329)
66. [kimi\_tool\_parser - vllm-mlx](https://vllm-mlx.is-a.dev/reference/api/vllm_mlx/tool_parsers/kimi_tool_parser/)
67. [Tool Call Parsing (Dynamo)](https://docs.nvidia.com/dynamo/v1.1.1/user-guides/tool-calling/tool-call-parsing-dynamo)
68. [K2-Vendor-Verifier Now Includes "Kimi K2 Thinking"](https://platform.kimi.ai/blog/posts/K2_Vendor_Verifier_Newsletter)
69. [K2 Vendor Verifier: Ensuring Reliable Tool Calls for Kimi K2](https://www.xugj520.cn/en/archives/k2-vendor-verifier-tool-calls.html)
70. [""Auto Exacto" is now live, and on by default for tool-calling ...](https://x.com/OpenRouter/status/2032127261709676991)
71. [Provider Variance: Introducing Exacto — OpenRouter Blog](https://openrouter.ai/blog/announcements/provider-variance-introducing-exacto/)
72. [Auto Exacto: Adaptive Quality Routing, On by Default — OpenRouter Blog](https://openrouter.ai/blog/announcements/auto-exacto/)
73. [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
74. [feat: fix openai/unsupported-composition by merging allOf branches by YasinzHyper · Pull Request #6 · YasinzHyper/schemafit](https://github.com/YasinzHyper/schemafit/pull/6)
75. [The Structured Outputs API: response\_format, JSON Schema and Strict Mode (2026)](https://prompt-architects.com/blog/648-structured-outputs-and-response-format)
76. [Structured Outputs with the OpenAI API - ChatAI Guide](https://chatai.guide/api/structured-outputs/)
77. [Function calling with the Gemini API](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)
78. [Introduction to function calling](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling)
79. [Function calling with the Gemini API - Google AI for Developers](https://ai.google.dev/gemini-api/docs/interactions/function-calling)
80. [Anthropic Claude tool use - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use.html)
81. [Tool Search](https://docs.litellm.ai/docs/providers/anthropic_tool_search)
82. [Anthropic Tool Search Explained: BM25, Regex & the Advanced Tool Use Header](https://growthmethod.com/anthropic-tool-search/)
83. [Anthropic Tool Input Examples](https://docs.litellm.ai/docs/providers/anthropic_tool_input_examples)
84. [Tool Search vs Programmatic Tool Calling in Claude](https://www.carlosaragon.online/blog/tool-search-vs-programmatic-tool-calling)
85. [GitHub - openresponses/openresponses · GitHub](https://github.com/openresponses/openresponses)
86. [Specification](https://www.openresponses.org/specification)
87. [github.com](https://github.com/vllm-project/vllm/pull/26345)
88. [Model Context Protocol Specification Version Timeline - Version-by-Version Changes and Adoption Milestones](https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html)
89. [Specification](https://modelcontextprotocol.info/specification/)
90. [Key Changes - Model Context Protocol](https://modelcontextprotocol.io/specification/2025-11-25/changelog)
91. [Tasks - Model Context Protocol](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)
92. [The 2026-07-28 MCP Specification Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
93. [Linux Foundation Announces the Formation of the Agentic AI Foundation… - Agentic AI Foundation (AAIF)](https://aaif.io/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation-aaif-anchored-by-new-project-contributions-including-model-context-protocol-mcp-goose-and-agents-md/)
94. [Agent2Agent Joins The Agentic AI Foundation Alongside MCP](https://www.forbes.com/sites/janakirammsv/2026/08/19/agent2agent-joins-the-agentic-ai-foundation-alongside-mcp/)
95. [BFCL V4 • Format Sensitivity](https://gorilla.cs.berkeley.edu/blogs/17_bfcl_v4_prompt_variation.html)
96. [GLM-5.3 quickstart - Together AI docs](https://docs.together.ai/docs/glm-5.3-quickstart)
97. [Kimi-K2/docs/tool\_call\_guidance.md at main · MoonshotAI/Kimi-K2](https://github.com/MoonshotAI/Kimi-K2/blob/main/docs/tool_call_guidance.md)
98. [BFCL V4 • Agentic Part 1: Web Search](https://gorilla.cs.berkeley.edu/blogs/15_bfcl_v4_web_search.html)
99. [Berkeley Function Calling Leaderboard (BFCL) V4](https://gorilla.cs.berkeley.edu/leaderboard.html)
