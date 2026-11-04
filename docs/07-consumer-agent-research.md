# How consumer agents are built: research learnings

*Researched 4 November 2026. Star counts are as shown on that date.*

This is what we learned about building research and web-action agents, to design our own stand-in for agents such as Muse, Instinct and Grok. The resulting design is in [08-consumer-agent-design.md](08-consumer-agent-design.md).

**How far to trust this:** it was a short pass of about 7 minutes across eight parallel research tracks. Most of it comes from READMEs, docs and engineering posts, read through a tool that summarises pages. We read parts of the source for five repos and ran none of the code. Raw notes, including what each track couldn't verify, are in `research_notes/Consumer agents/`.

## The main findings

1. **Research agents and action agents are separate families.** Deep research projects read and write reports but don't act on sites. Browser agents act on sites but don't plan research. A Muse-style agent combines them, with an orchestrator that reads and a delegated browser worker that clicks. The closest open-source project we saw is OpenManus, a general agent that wraps browser-use, and we didn't assess it in depth.
2. **The core loop is small.** Call the model, run its tool calls, append the results, stop. Most of the difficulty lies in tool design, briefs, stopping rules and checking the result.
3. **Quality comes from briefs and rules, not more agents.** Anthropic's agents spawned 50 subagents on simple queries until written effort rules fixed it. LangChain's prompt prefers a single sub-agent unless the work clearly parallelises.
4. **Forcing honesty takes explicit rules.** The best examples are browser-use's check before finishing and Jina's answer check. BrowserArena shows why: one model never detected a blocking banner, yet marked over half those tasks complete.
5. **Nobody solves bot checks reliably.** CAPTCHA handling is a paid cloud feature where it exists at all, and no project claims it always works.
6. **Small test sets work.** Anthropic suggests starting with 20–50 tasks drawn from real failures. Sites we control are also more stable than live ones.

## Deep research agents

These share one loop:

```
Clarify --> Plan --> Search --> Read --> Extract notes --> Check for gaps --> Write
                       ^                                        |
                       +------------- not enough yet -----------+
```

They differ mainly in who decides to stop.

| Project | Shape | Stops when | Notable idea |
|---|---|---|---|
| [Anthropic research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Lead agent plus parallel subagents, then a citation pass | Lead judges it has enough | Written effort-scaling rules, and detailed worker briefs |
| [open_deep_research](https://github.com/langchain-ai/open_deep_research) (12.7k stars, archived) | Scope, then supervisor and researchers, then one write | Supervisor decides, capped at 6 iterations and 10 tool calls per researcher | A cheap model summarises pages, and the report is written in one pass |
| [deepagents](https://github.com/langchain-ai/deepagents) (~31k) | General harness with planning, files and subagents | Model judgment | Offloads large tool output to disk |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) (30.5k) | Planner, per-question scrapers, publisher | Fixed plan, or depth and breadth settings | Filters passages before the model sees them |
| [dzhng/deep-research](https://github.com/dzhng/deep-research) (19.9k) | Recursive queries, under 500 lines | Depth counter | Very small |
| [node-DeepResearch](https://github.com/jina-ai/node-DeepResearch) (5.2k) | Search, read, reflect and answer actions, with a gap queue | Token budget, then a forced final answer | Disables actions by state, and retries a bad answer a limited number of times |
| [smolagents open deep research](https://huggingface.co/blog/open-deep-research) | A code agent with a text browser | Model judgment | Lists browser interaction as missing |

**What the projects report going wrong:** over-spawning, endless searching for sources that don't exist, token bloat from raw tool output, disjointed reports from parallel writers, and a preference for SEO content that humans had to catch. Anthropic reports agents using about 4 times the tokens of chat, and multi-agent systems about 15 times.

## Browser agents

| Project | Licence | Stars | How the model sees a page | Output | Limits and gates |
|---|---|---|---|---|---|
| [browser-use](https://github.com/browser-use/browser-use) | MIT | ~120k | Tree of visible interactive elements, plus an optional screenshot | Pydantic schema | Domain lists. No approval gate |
| [Stagehand](https://github.com/browserbase/stagehand) | MIT | 25.9k | Accessibility tree, screenshots, or both | Zod or Pydantic | Callbacks only |
| [Skyvern](https://github.com/Skyvern-AI/skyvern) | AGPL-3.0 | 23.3k | Mainly vision | JSON schema | Anti-bot only in its cloud |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Apache-2.0 | 39.2k | Accessibility tree | Left to the caller | Says it isn't a security boundary |
| [agent-browser](https://github.com/vercel-labs/agent-browser) | Apache-2.0 | 45.5k | Text snapshot with references | Left to the caller | Confirm and deny commands, not verified |
| [Magentic-UI](https://github.com/microsoft/magentic-ui) | MIT | 10.1k | Not stated | Not stated | Plan approval and action guards |
| [Nanobrowser](https://github.com/nanobrowser/nanobrowser) | Apache-2.0 | 14.2k | Element IDs plus screenshots | Not stated | Asks before submit, send, delete or upload |
| [Claude computer use](https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/computer-use-tool) | API | n/a | Screenshots | Left to the caller | Advises an allow-list and confirmations |

[OpenManus](https://github.com/FoundationAgents/OpenManus) (58.9k) uses browser-use as its browser tool, so it isn't a separate option here. Suna now appears as Kortix CompanyOS and doesn't document its browser approach.

**What they have in common:**

- **Two ways to see a page:** text structure with element IDs, or screenshots. Newer designs mix them. Our inference is that text is cheaper and steadier, and that screenshots rescue widgets with no usable structure.
- **Stale IDs fail on purpose:** agent-browser and Nanobrowser would rather fail than click the wrong thing, so the agent re-reads the page.
- **Standard safeguards:** step caps, retry caps and a fallback model.
- **Approval gates cluster around** submit, send, delete, upload, payments and passwords.
- **Domain lists aren't security boundaries**, as their own docs say.

### What the browser-use source shows

These come from its system prompt and browser profile code.

| Fact | Why it matters for us |
|---|---|
| The model sees a tree of interactive elements, with text as child lines, and by default only what's in the visible viewport | Facts below the fold need scrolling or a page search |
| `cross_origin_iframes` defaults to `True` in the code, up to 100 iframes and depth 5. A docs page we read described it as off by default | Check the setting after installing. Booking widgets may be reachable, but that's untested |
| The prompt has no rule on payments, irreversible actions or asking the user | We must add our own approval gate |
| The prompt tells the model that CAPTCHAs are solved automatically | This relies on a backend feature, so a local run may behave oddly at a CAPTCHA. Test it |
| `done` carries a success flag and text, and success is true only if the whole request is met | A clean interface for the orchestrator |
| It says partial results marked as failed are better than overclaiming | Worth keeping |
| Replays stop at the first mismatched step, by which time a form may already be submitted | Don't use replay for repeated test runs with real submissions |

## Harnesses

"If you're not the model, you're the harness," as [LangChain](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) puts it.

| Option | Language | Licence | Stars | Best thing to learn from it | Fit for our small web agent |
|---|---|---|---|---|---|
| Hand-written loop | Python | n/a | n/a | Full control and visibility | **High** |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Python | MIT | ~30.5k | Works across providers, with built-in tracing | Medium to high |
| [Pi](https://github.com/badlogic/pi-mono) (now shown as earendil-works/pi) | TypeScript | MIT | ~120k | Prompt and tools under ~1,000 tokens, four tools, clean event stream | Medium, because browser-use is Python |
| [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) | Python, TypeScript | MIT plus terms | ~8.4k | Hooks and permission modes | Medium. Claude-only, runs a CLI as a subprocess, and has a coding toolset to strip out |
| [Deep Agents and LangGraph](https://github.com/langchain-ai/deepagents) | Python, JS | MIT | ~31k | Offloading and approval steps | Medium, and heavier than needed |
| [smolagents](https://github.com/huggingface/smolagents) | Python | Apache-2.0 | ~30.2k | Code as actions | Medium |
| [OpenCode](https://github.com/anomalyco/opencode) | Not verified | MIT | ~224.5k | Per-agent `ask`, `allow` and `deny` permissions | Low, since it's a coding product first |

### Lessons on building a tool loop

From [Anthropic's agent](https://www.anthropic.com/engineering/building-effective-agents), [context](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and [tool](https://www.anthropic.com/engineering/writing-tools-for-agents) posts, and [Mario Zechner's post on Pi](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/):

1. Start with direct API calls. Frameworks can hide prompts and responses.
2. Keep tools few and non-overlapping, with clear names.
3. Return concise, useful results. Offer a concise or detailed mode, cap the size, and say how to narrow.
4. Make errors say what to do next.
5. Keep the system prompt short.
6. Manage context by clearing old tool results first, and keep notes and plans outside the context.
7. Use a subagent only to isolate context, and have it return a summary. Pi rejects subagents because they reduce visibility. For us, the browser task is the natural subagent.
8. Log everything: an event per turn, tool call and result. Anthropic's tool runner docs point to a manual loop when you need custom logging.
9. Enforce permissions through which tools are available, not through prompt text.

## How real agents reach a website

| Agent or tool | How it reaches a page | JavaScript | Forms | What the site sees | Confidence |
|---|---|---|---|---|---|
| [Claude web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) | Server-side fetch, only URLs already seen in the conversation or results | No, stated | No | Obeys `robots.txt` | Stated |
| [Claude web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) | Server-side search | Not stated | No | Not stated | Stated |
| [ChatGPT-User, OAI-SearchBot](https://developers.openai.com/api/docs/bots) | Fetch on request, and an index crawler | Not stated | Not for the fetch | Published user agents and IPs. `robots.txt` "may not apply" to user-initiated fetches | Stated |
| ChatGPT agent | Not verified | Unknown | Unknown | Unknown | Couldn't read OpenAI's pages |
| [Perplexity-User, PerplexityBot](https://docs.perplexity.ai/guides/bots) | Fetch on request, and an index crawler | Not stated | Not stated | Published user agents and IPs. The user fetcher generally ignores `robots.txt` | Stated |
| Perplexity Comet | Browser agent in the user's session | Yes | Yes | Not documented | Secondary, and reports conflict |
| [Grok API search](https://docs.x.ai/docs/guides/tools/search-tools) | Server-side search that browses pages | Not covered | Not covered | No crawler doc found | Partly stated |
| Manus | Per-task cloud VM with Chromium | Yes | Yes | Unknown | Secondary only |
| Muse | Search, fetch, and a delegated browser agent, by its own account | Yes, in the browser | Yes | Looks like an ordinary browser | Self-reported ([details](02-muse-findings.md)) |
| Instinct | Uses a phone and computer the way a person does | Unknown | Unknown | Unknown | No developer docs found |
| [Exa Contents](https://docs.exa.ai/reference/get-contents) | Cached copy, or a live crawl if uncached | Not stated | No | Crawler | Stated |
| [Tavily Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract) | Reads given URLs. Docs don't say whether live or cached | Not stated | No | Not stated | Stated in part |
| [Parallel Extract](https://docs.parallel.ai/extract/advanced-extract-settings) | Indexed copy, or a live fetch by policy. Never-crawled URLs aren't addressed | Claimed, not confirmed | No | Crawler | Stated in part |

These reduce to **three profiles**: an index reader, a plain fetcher and a browser agent. Real agents often run them in that order. Staleness is part of the first profile, invisibility of JavaScript content is part of the second, and getting stuck in forms is part of the third.

## How web agents are evaluated

| Source | Approach | Worth borrowing |
|---|---|---|
| [WebArena](https://arxiv.org/abs/2307.13854) | Self-hosted realistic sites, with outcomes checked for correctness | Sites we control, so answers don't drift |
| [WebVoyager](https://arxiv.org/abs/2401.13919) | 15 live sites, with an automatic judge that agrees with humans 85.3% of the time | A judge needs checking against humans |
| [Online-Mind2Web](https://arxiv.org/abs/2504.01382) | 300 tasks on 136 live sites. The authors say earlier results were over-optimistic | Be sceptical of high scores |
| BrowseComp | Questions with short, checkable answers | One checkable answer per task |
| [DeepResearch Bench](https://arxiv.org/abs/2506.11763) | 100 expert tasks, scored against reference reports | Not needed at our size |
| [BrowserArena](https://arxiv.org/abs/2510.02418) | Live-web comparison on Browser Use, with users labelling failures | Banner and CAPTCHA tests |
| [Anthropic's guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 20–50 tasks, reference solutions, outcome grading, repeated trials | Our method, set out below |

**What our test set takes from these:**

- 20–50 tasks per business to start, built from sites we control.
- A reference solution per task, proving it can be solved.
- Grading on outcomes in code first. A model judge only for free text, with an "unknown" option.
- Repeated trials in a clean environment, reported as pass@k and pass^k.
- Tasks where the right answer is "not offered" or "can't tell".
- Reading transcripts to separate agent faults from task or grader faults. A near-zero result usually means a broken task.

We couldn't find a published list of failure categories. The eval pages we read don't give one, and reading the full papers would be the next step.

## Prompt rules worth copying

| Rule | Source |
|---|---|
| Before finishing, list every requirement and check it | browser-use |
| Every value reported must appear in tool output. Never fill gaps from general knowledge | browser-use |
| Verify an action worked from page state, not from the action log | browser-use |
| Unresolved blockers mean failure is reported, and honest partial results beat overclaiming | browser-use |
| Change approach after 3 steps on one URL with no progress, or 2–3 identical failures. Don't retry a block | browser-use |
| Apply filters first, then browse. For autocomplete: type, wait, click the suggestion | browser-use |
| Think before delegating and after each result: what's missing, and is it enough? | open_deep_research |
| Prefer one worker unless the work clearly parallelises. Workers see nothing else, so each brief stands alone | open_deep_research, deepagents |
| Stop when you can answer, or when the last two searches added nothing | open_deep_research |
| A separate check of the answer, limited retries, then a forced best-effort answer on budget | Jina. We'd add "say what's unverified", which Jina's version doesn't |
| Consider credibility and date when weighing sources, not only relevance | GPT Researcher |

## What we couldn't verify

- **Real agents:** ChatGPT agent's behaviour, what Comet, Manus, Grok or Instinct look like to a site, and whether they fill forms reliably.
- **Booking platforms:** how each embeds and when it asks for personal details. We only confirmed Calendly's embed styles, and that Acuity's and Square's availability APIs need the owner's credentials.
- **browser-use:** real behaviour on booking widgets, PDFs and CAPTCHAs when run locally. The DOM code wasn't read in depth.
- **Harness details:** LangGraph, OpenCode's internals, and OpenAI's harness post (seen only as a search summary).
- **Benchmarks:** we read abstracts and vendor summaries, not the full papers.
- **OpenAI deep research:** its system card couldn't be read.

## Raw notes

In `research_notes/Consumer agents/`:

- `deep_research_agents.md`
- `browser_action_agents.md`
- `harnesses.md`
- `real_agents_and_evals.md`
- `source_level_notes.md`
- `roadblock_evidence.md`
- `booking_platforms_and_failures.md`
- `vertical_gaps_and_questions.md`
