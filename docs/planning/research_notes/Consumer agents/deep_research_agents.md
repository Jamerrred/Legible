# Deep research agents: how they are built

Read on 2026-11-04 via page fetches (summarised by a fetch tool, not read raw). "Source says" = stated on the page. "Inference" = mine. Star counts are from the repo page on that date.

## Anthropic multi-agent research system
Source: https://www.anthropic.com/engineering/multi-agent-research-system
- Loop: lead agent (Opus 4) analyses the query, makes a plan, spawns subagents (Sonnet 4) that search in parallel, then decides if more research is needed. A separate CitationAgent adds citations at the end.
- Subagent brief: objective, output format, guidance on tools/sources, task boundaries. Vague briefs caused duplicate searches and gaps.
- Search vs read: subagents start with short broad queries, then narrow, using interleaved thinking to judge results. Page reading is not described in detail.
- Context: lead saves its plan to memory (context over 200k tokens is truncated). Subagents have separate windows and return condensed findings. Big outputs can go to external storage, passing references back.
- Stopping: lead exits when it judges it has enough. Effort-scaling rules are written in the prompt: simple fact = 1 agent, 3-10 tool calls; comparison = 2-4 subagents, 10-15 calls each; complex = 10+ subagents.
- Evidence: CitationAgent pass. Evals judge citation accuracy and source quality.
- Evals: ~20 real-usage queries to start; an LLM judge scores accuracy, citation accuracy, completeness, source quality, tool efficiency in one call (0-1 plus pass/fail); human testing caught agents preferring SEO content farms.
- Admitted failures: 50 subagents for simple queries; endless search for nonexistent sources; distracting updates between agents; errors compound; non-determinism; synchronous lead blocks; poor fit for coding.
- Numbers: agents ~4x chat tokens, multi-agent ~15x. Token use explained 80% of BrowseComp variance. Multi-agent beat single Opus 4 by 90.2% on their internal eval.

## LangChain open_deep_research
Repo: https://github.com/langchain-ai/open_deep_research (12.7k stars, archived/read-only, 2026-11-04). Blog: https://www.langchain.com/blog/open-deep-research
- Loop (blog): scope (ask clarifying questions, condense chat into a research brief) -> research (supervisor delegates) -> write (one LLM call from brief + findings).
- Subagents: supervisor splits only if topics are independent; each sub-agent gets only its sub-topic (not the whole brief), own context, loops over search/MCP tools. Supervisor can launch follow-ups to fill gaps.
- Search vs read: Tavily default; a cheap model (gpt-4.1-mini default) summarises search results before the researcher sees them (repo page).
- Compression: sub-agent writes a cited answer to its sub-question, dropping failed calls and junk; a dedicated compression model role exists.
- Stopping: supervisor decides; page does not give iteration caps (they live in configuration.py, which I did not read).
- Evals: Deep Research Bench (100 PhD-level tasks, LLM judge RACE). Defaults 0.4309 at ~$46; GPT-5 config 0.4943. Blog gives no eval method and lists evals in the hot path as open.
- Lessons/failures (blog): parallel report writing came out disjointed, so write in one pass; multi-agent only where work parallelises; context clash and token bloat from raw tool output.

## LangChain deepagents
Repo: https://github.com/langchain-ai/deepagents (about 31k stars, 2026-11-04)
- Source says: a general agent harness with planning, a filesystem (read/write/edit, pluggable backends), sub-agents with isolated context, shell, memory, human approval, skills, MCP tools. Summarises long threads and offloads tool output to disk. Credits Claude Code as inspiration.
- I did not verify the specific todo tool or the default prompt text. Stopping rules, citation handling and evals not covered on the page.

## GPT Researcher
Repo: https://github.com/assafelovic/gpt-researcher (30.5k stars, 2026-11-04)
- Loop: planner generates research questions; execution agents scrape per question; each source is summarised and tracked; publisher aggregates into a report (2,000+ words, 20+ sources claimed). Deep Research mode is a recursive tree with depth/breadth settings.
- Search vs read: separate crawler/scraper step per question, with JS-enabled scraping.
- Context: relevance filter before the LLM. Their own benchmark (28 tasks, same sources replayed): kept-passage relevance Jev 73%, BM25 51%, embeddings 46%. No filter cost 65% more but gave the broadest reports. Self-reported; I did not check method.
- Evidence: source tracking per resource.
- Admitted limits: "as-is", not for academic use, bias reduced not eliminated. Deep mode ~5 min, ~$0.40 per run.

## dzhng/deep-research
Repo: https://github.com/dzhng/deep-research (19.9k stars, 2026-11-04)
- Loop: user query -> follow-up questions -> generate N search queries (breadth, default 4) -> run in parallel -> extract "learnings" and new directions -> recurse while depth > 0 (default 2) -> markdown report.
- Search and read are one service (Firecrawl). LLM is o3-mini by default.
- Stopping: depth counter only. No quality check on branches (page does not describe one).
- Citations: report lists sources; no verification described.
- Goal: under 500 lines. Limits: paid keys, rate limits at low tiers.

## jina-ai/node-DeepResearch
Repo: https://github.com/jina-ai/node-DeepResearch (5.2k stars, 2026-11-04)
- Loop: Search, Visit, Reflect, Answer actions, repeated until the token budget runs out. Each action gets disabled for the next step if it yielded nothing new. Reflect adds unique sub-questions to a gap queue.
- Stopping: token budget check before each step. On overrun, "Beast Mode" forces a final answer.
- Answer gate: answer to the original question must be definitive AND have references, otherwise the bad attempt is stored, context resets and the loop continues.
- Citations: footnote style [^1].
- Limits: aimed at correct answers, not long reports; some demo answers "partially correct"; step counts 2 to 42.

## Hugging Face open deep research (smolagents)
Blog: https://huggingface.co/blog/open-deep-research
- Source says: a code agent that writes actions as code, not JSON; about 30% fewer steps. JSON actions dropped GAIA validation from ~55% to ~33%. Tools are a minimal text browser and a text inspector for files, adapted from Magentic-One.
- GAIA validation: open version 55.15% vs OpenAI Deep Research 67.36%.
- Admitted gaps: text-only browser, limited file formats, no GUI/vision browsing yet (planned). The page did not describe a manager + search agent split, so I cannot confirm it.

## OpenAI deep research
- I could not read the system card (PDF came back unreadable). Nothing here is verified. Only the HF blog's remarks on it: little disclosed about internals, likely uses a browser agent.

# Patterns across projects
- Most projects share one loop: clarify, plan, search, read, extract notes, check for gaps, write. They differ in who decides to stop.
- Anthropic and LangChain use a lead plus parallel workers with isolated context; the simple repos (dzhng, Jina) use one agent with a queue or recursion.
- Delegation briefs matter more than extra agents: Anthropic and LangChain both fix quality by narrowing and detailing what workers receive.
- Search results are pre-digested by a cheaper model or filter before the main model sees them (LangChain, GPT Researcher). Workers return compressed, cited findings, not raw pages.
- Writing is done once, by one call (LangChain, Anthropic's lead plus a citation pass).
- Stopping is a mix of: model judgment (Anthropic, LangChain), a fixed depth (dzhng), a token budget with forced final answer (Jina). Anthropic needed written effort-scaling rules to stop over-spawning.
- Evidence gate is rare: only Jina refuses an answer with no references; Anthropic adds a separate citation pass. (Inference: this is a cheap, useful pattern.)
- Evals are LLM judges against rubrics or reference reports; small query sets (20) were enough early. Humans still catch source-quality problems.
- Shared failures: over-spawning, endless searching, token bloat, context degradation, preferring SEO sources, cost (15x chat).
- None of these read-focused designs act on sites. Only HF mentions browser interaction, and as missing. (Inference: action-taking is a separate layer for us.)

# Copy / skip for our demo agent
Copy:
- One orchestrator that reads a short brief, with explicit effort rules (e.g. 1 worker for simple asks, max 3 otherwise) and a hard budget with a forced "best answer so far" step (Jina Beast Mode).
- Worker brief template: objective, output format, tools, boundaries.
- Search and read as separate tools; summarise or trim page text before the orchestrator sees it.
- Worker returns compressed findings, each with source URL and quote.
- Evidence gate: no claim in the final report without a URL; run a cheap citation check pass.
- Single-pass final write.
- Tiny eval set (about 20 requests) with an LLM-judge rubric: accuracy, citation accuracy, completeness, source quality, efficiency. Add a check that the agent prefers the business's own pages over aggregators.
- Keep browser/action agent as a separate delegated worker whose end state is checked (Anthropic: judge end state, not path).

Skip:
- Recursive depth/breadth trees, report-length targets, 20+ source reports, image generation, export formats (GPT Researcher, dzhng).
- Many parallel subagents and memory offload; unnecessary at demo scale and costly.
- Code-as-actions (smolagents) unless we already use smolagents.
- Benchmarks like Deep Research Bench or GAIA.
- Relying on archived open_deep_research as a dependency; copy its structure only.
