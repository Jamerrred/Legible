# Agent harnesses and what they teach (research date 2026-11-04)

Method: quick pass (time-boxed), page summaries via a fetch tool that summarises pages. Star counts are from the pages fetched on 2026-11-04. "Source states" = from the page; "Inference" = mine. Not verified: anything marked so; I did not clone or run any repo.

## Pi (badlogic/pi-mono, now shown as earendil-works/pi)
- Repo: https://github.com/badlogic/pi-mono (page identified itself as earendil-works/pi). MIT. ~120k stars, 15.4k forks. TypeScript monorepo (language inferred from npm build commands).
- Packages: pi-ai (unified multi-provider LLM API), pi-agent-core (agent runtime), coding agent CLI, plus tui/telemetry/durable packages.
- Loop (source: https://github.com/badlogic/pi-mono/tree/main/packages/agent): `Agent` class plus low-level `agentLoop()`. Emits events (agent_start, turn_start, message_*, tool_execution_*, turn_end, agent_end). Hooks: `transformContext` (prune/inject), `convertToLlm`, `prepareRequest`, `finishTurn` (continue or end). `steer()` and `followUp()` queues.
- Tools: `AgentTool` with name, description, JSON-schema `parameters`, `execute(...)`. Throw to signal failure; return `terminate: true` to end the run.
- Design rules (Zechner post, https://mariozechner.at/posts/2025-11-30-pi-coding-agent/): system prompt plus tools under ~1,000 tokens; four core tools (read, write, edit, bash); no MCP (cites one server using ~13.7k tokens up front); no subagents ("black boxes", poor visibility); no permission prompts (container instead); tool results split into LLM text and a separate UI part; plans in plain files (PLAN.md); every interaction should be inspectable; sessions in a documented, post-processable format, HTML export, headless JSON/RPC mode.
- Fit for a web agent: good loop and event stream, TypeScript only. Inference: easy to wrap, but our browser layer is Python, so we'd need a bridge (RPC or CLI tool calls).

## OpenCode (anomalyco/opencode, formerly sst/opencode)
- Repo: https://github.com/anomalyco/opencode. MIT. ~224.5k stars, 30.2k forks. Language not shown on the page I read.
- Source states: built-in `build` agent (full access) and `plan` agent (read-only, denies edits, asks before bash); a `general` subagent invoked with `@general`.
- Not verified: loop internals, tool definition API, compaction, sessions, SDK/server (README did not cover them). Inference: it is a coding product first; heavy for a small web agent.

## LangChain: harness anatomy, LangGraph, Deep Agents
- Post: https://www.langchain.com/blog/the-anatomy-of-an-agent-harness. Definition: "If you're not the model, you're the harness." Components: filesystem, bash/code execution, sandboxes, memory files (AGENTS.md), context-rot management (compaction, offloading big tool outputs to files, progressive skills), long-horizon aids (planning, verification hooks).
- Deep Agents: https://github.com/langchain-ai/deepagents. MIT. ~31.0k stars. Python (JS version exists). Built-ins: planning, filesystem with pluggable backends, subagents with isolated context; context management summarises and offloads tool output to disk. Permissions: human-in-the-loop approve/edit/reject; "trust the LLM", enforce limits at tool/sandbox level. Tracing through LangSmith.
- Not verified: LangGraph repo stats and details (not fetched).
- Inference: Python, tracing built in via LangSmith (a hosted service dependency), but pulls in a lot of coding-agent baggage (filesystem, planning) that a read-only web agent mostly doesn't need.

## Claude Agent SDK and Anthropic tool runner
- Python SDK: https://github.com/anthropics/claude-agent-sdk-python. MIT licence plus Anthropic Commercial Terms apply. ~8.4k stars. Bundles the Claude Code CLI (it runs as a subprocess; inferred from CLINotFound/ProcessError types and `cli_path`).
- Custom tools: `@tool` functions in an in-process MCP server. Hooks (PreToolUse etc.) via `ClaudeSDKClient`. Permissions: `allowed_tools`, `disallowed_tools`, `permission_mode`, `can_use_tool`. Default toolset is the full Claude Code set (Bash, Write...), so a web agent must restrict it. Subagents exist; details not read. Claude-only models (inference).
- Tool runner: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner. Beta. Docs say use the manual loop when you need human approval, custom logging or conditional execution. Supports compaction via server-side `context_management`.

## Anthropic engineering posts
- Building effective agents (https://www.anthropic.com/engineering/building-effective-agents): start with direct API calls; frameworks can hide prompts/responses; workflows for fixed paths, agents when the model must decide; clear stop conditions; invest in the agent-computer interface; make tools hard to misuse.
- Context engineering (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): minimal, non-overlapping tools; compaction near the limit (clearing old tool results is the safest form); structured notes outside context; subagents return condensed summaries; just-in-time retrieval via lightweight references.
- Writing tools for agents (https://www.anthropic.com/engineering/writing-tools-for-agents): few high-impact tools, merge multi-step calls; namespace tools; return human-readable high-signal fields not raw IDs; concise vs detailed response enum; paginate/truncate (Claude Code caps tool output at 25k tokens) and tell the agent how to narrow; errors say how to fix; evaluate on realistic multi-step tasks and track tokens, tool calls, errors.

## OpenAI
- Agents SDK: https://github.com/openai/openai-agents-python. MIT. ~30.5k stars. Python. Tools (functions, MCP, hosted), handoffs/agents-as-tools, guardrails, built-in tracing, sessions. Provider-agnostic (Chat Completions, LiteLLM, "100+ LLMs"). Loop internals not described on the page.
- Harness engineering post: https://openai.com/index/harness-engineering (11 Feb 2026, Ryan Lopopolo). I only saw a search summary, not the post: env design over code writing; Chrome DevTools wired in so agent can reproduce bugs; context is scarce, a giant instruction file crowds out the task. Treat as second-hand.

## Hugging Face smolagents
- https://github.com/huggingface/smolagents. Apache-2.0. ~30.2k stars. Python. `CodeAgent` (model writes Python actions, ReAct loop, ends with `final_answer`) or `ToolCallingAgent` (JSON actions). Tools from MCP, LangChain or Hub. Ships a `webagent` CLI on helium. Tracing not mentioned on the page.

## browser-use (the likely browser layer)
- https://github.com/browser-use/browser-use. MIT. ~120k stars. Python 3.11+. `Agent(task, llm, browser)`, `await agent.run()`; custom tools via `@tools.action`; `ChatAnthropic` etc.; `agent.save_history('file.json')`, `history.final_result()`. Inference: it has its own internal loop, so the consumer agent should call it as a tool ("delegate browser work"), not nest loops.

## Comparison

| Option | Lang | Licence | Stars | Loop control | Tracing/logs | Fit for small web agent |
|---|---|---|---|---|---|---|
| Hand-written loop on model API | Python | n/a | n/a | Total | Whatever we write | High |
| Claude Agent SDK | Py/TS | MIT + terms | 8.4k | Medium (CLI subprocess) | Hooks, transcripts | Medium; coding toolset to strip |
| Pi | TS | MIT | ~120k | High, small | Event stream, session files | Medium; TS vs Python browser |
| OpenCode | TS (not verified) | MIT | ~224k | Low | Not verified | Low |
| Deep Agents / LangGraph | Py/JS | MIT | ~31k | Medium | LangSmith | Medium; heavy |
| OpenAI Agents SDK | Py | MIT | ~30k | Medium | Built-in tracing | Medium-high, multi-provider |
| smolagents | Py | Apache-2.0 | ~30k | Medium | Not stated | Medium |
| Anthropic tool runner | Multi | SDK | n/a | Low (manual loop for logging) | Manual | Medium |

## Lessons on building a tool loop
1. The loop is small: call model, run tool calls, append results, stop on no tool call or a `final_answer`/terminate signal. Both Pi and Anthropic say start simple.
2. Keep tools few and non-overlapping; merge multi-step actions; namespace them (search_web, read_page, browse_task, report).
3. Return concise, high-signal results with a concise/detailed switch; cap size, and say how to narrow. Offload big page text to files or refs and return a handle (just-in-time retrieval).
4. Errors should tell the model what to do next.
5. Short system prompt; modern models need little. Pi's is under 1k tokens.
6. Context: clear old tool results first, summarise only near the limit; keep notes/plan in a file.
7. Subagents: useful for isolating context and returning summaries (Anthropic, Deep Agents); Pi rejects them for visibility. For us the browser task is the natural subagent.
8. Log everything: an event per turn, tool call and result, tokens, to JSONL. Anthropic's tool runner docs themselves point to the manual loop for custom logging.
9. Permissions: for a read-only web agent, enforce by tool allowlist, not prompts.
10. Evaluate on realistic multi-step tasks, tracking tokens, tool calls, errors (Anthropic).

## Recommendation
Primary: (a) a hand-written tool loop in Python on the model API (~150-300 lines), with browser-use called as one tool. Reasons: same language as browser-use; the task has a handful of tools; full control of the JSONL run log so runs are comparable across models; no coding-agent baggage; frameworks hide prompts (Anthropic). Use provider SDK or LiteLLM for model swap. Borrow Pi's event shape (turn_start, tool_execution_*, turn_end) and Anthropic's tool-design rules.

Runner-up: OpenAI Agents SDK (Python, MIT, provider-agnostic, built-in tracing, agents-as-tools), if we'd rather not own the loop. Claude Agent SDK is third: strong but Claude-only and CLI-subprocess based, which fits the later back-office agent better than a model-neutral stand-in for Muse/Grok.

Caveat: recommendation is inference from README-level reading; no code was run.
