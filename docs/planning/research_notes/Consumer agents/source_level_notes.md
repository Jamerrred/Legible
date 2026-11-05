# Source-level notes (read 2026-11-04, raw GitHub, main/master branches)

Files actually read (fully or in the parts cited):
- browser-use: browser_use/agent/system_prompts/system_prompt.md (full), browser_use/browser/profile.py (lines ~672-692), browser_use/dom/serializer/serializer.py (grep of function names only, NOT read in depth)
- open_deep_research: src/open_deep_research/configuration.py (grep of defaults), prompts.py (lead_researcher_prompt, research_system_prompt start, final_report_generation_prompt)
- gpt-researcher: gpt_researcher/prompts.py (report prompt ~l.296-340, curate_sources; rest grepped only)
- node-DeepResearch: src/agent.ts (action prompt l.184-235, loop l.420-720)
- deepagents: libs/deepagents/deepagents/middleware/subagents.py (TASK_TOOL_DESCRIPTION), graph.py (legacy base prompt, first ~30 lines)
NOT read: browser-use DOM serializer internals, deepagents todo tool text, gpt-researcher planning/sub-query prompts, jina evaluator.ts.

URLs (prefix https://github.com/):
- browser-use/browser-use/blob/main/browser_use/agent/system_prompts/system_prompt.md
- browser-use/browser-use/blob/main/browser_use/browser/profile.py
- langchain-ai/open_deep_research/blob/main/src/open_deep_research/prompts.py and configuration.py
- assafelovic/gpt-researcher/blob/master/gpt_researcher/prompts.py
- jina-ai/node-DeepResearch/blob/main/src/agent.ts
- langchain-ai/deepagents/blob/main/libs/deepagents/deepagents/middleware/subagents.py and graph.py

## 1. browser-use
What the model sees (per the prompt's own description): per step, XML-ish sections: user_request, agent_history (per step: evaluation of previous step, memory, next goal, action results), agent_state (file system, todo), browser_state, optional screenshot with boxes (browser_vision), read_state (one-shot, after extract/read_file).
browser_state = current URL, open tabs, and a tab-indented tree of ONLY interactive elements as `[index]<tag attr=value />` with text as unindexed child lines. `*[` marks elements new since last step (e.g. autocomplete options after typing). `|SCROLL|` and `|SHADOW(open)|` prefixes. By default only elements in the visible viewport are listed. Screenshot is declared "ground truth".
Rules (paraphrased):
- Only use indexes that are explicitly listed. Open a new tab for side research.
- Apply filters/sort first when the request has criteria (price, rating, location) before scrolling results.
- Autocomplete/combobox: type, WAIT a step, click the suggestion; only press Enter if none appear.
- If a multi-action sequence is interrupted by a page change, finish the remaining actions next step.
- Handle popups/cookie banners/modals immediately. Do not log in unless needed and credentials exist.
- On 403, bot detection, rate limit: do not retry same URL; try another route or report limitation.
- Stuck detection: same URL 3+ steps without progress, or same action failing 2-3 times -> change approach, record failed approaches in memory.
- Tools: `extract` is expensive (don't repeat same query); `search_page` and `find_elements` (CSS) are free; prefer search_page over scrolling.
- CAPTCHAs: prompt says they are auto-solved by the browser; agent told not to attempt them. (Relies on a backend feature - check before depending on it.)
- Page-changing actions (navigate, search, go_back, switch, evaluate) must be last in an action list; remaining actions skipped on page change. Max actions per step is a parameter.
- Planning: simple tasks act directly; complex ones emit plan_update (3-10 items). Finishing all plan items does not mean done; re-verify against the request.
- Filesystem/todo.md only for tasks over ~10 steps.
Finishing/honesty (strongest part, worth copying): `done` must be called alone; `success=true` only if the full request is met. Pre-done checklist: list every requirement, check counts/filters/format, verify submitted forms actually took effect via page state, "every URL, price, name, value must appear verbatim in tool outputs", don't fill gaps from training knowledge, unresolved blockers (payment declined, login wall, paywall, access denied) => success=false. "Partial results with success=false are more valuable than overclaiming." At 75% of step budget, re-evaluate and consolidate partial results. Also: never assume an action worked just because it is in history; verify on screenshot.
Not in the prompt: no explicit iframe rules, no explicit rules on payments/irreversible actions or asking the user for confirmation.
cross_origin_iframes: in profile.py the default is True (not off). Description: when False only same-origin frames processed. Also max_iframes default 100, max_iframe_depth default 5. So booking widgets in cross-origin iframes (OOPIF) are in scope by default, subject to caps; behaviour on specific widgets not tested.

## 2. open_deep_research
Config defaults (configuration.py): max_researcher_iterations=6 (supervisor), max_react_tool_calls=10 (per researcher), max_concurrent_research_units=5, max_structured_output_retries=3, search API default Tavily, max_content_length=50000 chars for pages before summarising, summarisation model gpt-4.1-mini, research/compression/report models gpt-4.1.
Supervisor prompt: acts as "research manager with limited time and resources"; tools ConductResearch, ResearchComplete, think_tool; must think before delegating and after each result ("what's missing? enough to answer?"). Bias towards a SINGLE sub-agent unless clear parallelism; comparisons -> one agent per compared element; "stop when you can answer confidently"; hard stop after N tool calls; sub-agents see nothing of each other, so each brief must be standalone, no acronyms.
Researcher prompt: broad searches first then narrow; think_tool after each search (never in parallel with search); budgets: simple 2-3 searches, complex up to 5; stop immediately when answerable, 3+ relevant sources, or last 2 searches returned similar info.
Final report: citation rules: one number per unique URL, sequential no gaps, "### Sources" list; "Citations are extremely important". Separate summarize-webpage prompt compresses raw pages before the researcher sees them.

## 3. gpt-researcher
Only the report and source-curation prompts read. Report prompt: must form its own concrete opinion rather than generic conclusions; prefer reliable sources and newer articles if trustworthy; in-text markdown citations at end of sentence plus reference list; no TOC. curate_sources: ranks by relevance, credibility, currency, objectivity (biased sources kept if they add a different perspective), and quantitative value; bias is toward inclusion, exclude only clearly irrelevant/outdated/unusable. Notably it has no explicit conflict-resolution rule in what I read (conflicts are not reconciled; just diversity retained). Did not read its planning / sub-query prompts.

## 4. node-DeepResearch (Jina)
Loop (agent.ts): maintains a `gaps` list of sub-questions (starts with original question); each step picks gaps[step % len] (round-robin). Each step the LLM chooses one action among search / read / answer / reflect (/coding), with actions disabled by state: no read if no URLs known, no search once >50 URLs queued, reflect disabled when too many gaps, answer disabled at step 1 if a "freshness" evaluation says question is time-sensitive. Token budget default 1,000,000; regular phase ends at 85%, then "beast mode" forces a best-effort answer (the prompt is shouty all-caps; partial answers allowed). Reflect = generate clarifying sub-questions to fill knowledge gaps.
Answer check: evaluation types chosen per question (e.g. freshness, plurality, definitive, completeness, 'strict'); evaluator LLM judges the answer against gathered knowledge. Each evaluation type has numEvalsRequired = maxBadAttempts (default 2). On fail: decrement that counter, store an improvement plan (strict), log why the answer was bad, run an error analysis, push the lesson into knowledge, and retry. When all counters hit 0, give up and go to beast mode. If the LLM answers immediately with no references, evaluations are skipped. Answer prompt: casual/general questions answered directly; if uncertain, reflect.

## 5. deepagents
subagents.py TASK_TOOL_DESCRIPTION: launch parallel subagents in one message when independent; each subagent is stateless and sees ONLY the prompt, so put full detail and state exactly what it should return; its report is not shown to the user so relay a summary; tell it whether to create, analyze, or only research. Base prompt (legacy in graph.py): concise, no preamble; ask only minimal follow-up when underspecified; understand -> act -> verify ("check against what was asked, not your own output"); keep going until complete; if something fails repeatedly, stop and analyze why instead of retrying; if blocked, tell the user. Todo tool text not read.

## Prompt rules worth copying
1. Pre-done verification checklist with success flag; blockers => success=false; partial honest results beat overclaiming (browser-use).
2. Every value reported must appear verbatim in tool output; never fill from training knowledge (browser-use).
3. Verify an action happened from page state, not from the action log (browser-use).
4. Loop breaker: 3+ steps same URL or 2-3 identical failures => change approach; do not retry 403/bot walls.
5. Filters first, then browse; autocomplete: type, wait, click suggestion.
6. Orchestrator: bias to one sub-agent, parallelise only independent items; standalone briefs; think step before and after each delegation; fixed iteration cap and "stop when you can answer confidently" (ODR: 6 supervisor iterations, 10 researcher calls, 5 parallel; researcher 2-5 searches).
7. Brief delegates with exact required return format; tell them the intent (deepagents).
8. Answer gate: separate evaluator pass with limited retries, then a forced best-effort answer when budget runs out (Jina) - add "say what is unverified" to the forced answer, since Jina's version does not.
9. Numbered, gap-free citations tied to URLs (ODR); prefer sources with concrete data and recent dates (gpt-researcher).

## Technical facts that affect our design
- browser-use shows the model only viewport-visible interactive elements by default; prices or slots below the fold need scroll, search_page, or extract (extra LLM call). Plan for a text-first path (search_page/extract) before relying on clicks.
- cross_origin_iframes defaults True, max 100 iframes, depth 5: booking widgets in iframes are reachable in principle; still verify on real widgets.
- The prompt has no payment, irreversible-action, or ask-the-user rule: we must add our own approval gate before submit/pay, and handle logins/OTP ourselves (its stance is just "don't log in without credentials").
- CAPTCHA handling is assumed by the prompt (auto-solved); depends on browser backend config.
- Output contract is strict JSON per step (thinking, evaluation, memory, next_goal, action list); `done` carries success + text + files, a clean interface for the orchestrator to consume.
- ODR numbers give sensible starting budgets for our orchestrator caps; page text should be summarised/truncated (50k chars) before entering orchestrator context.
- Sub-agents are stateless: all context must be in the task prompt, and the orchestrator must relay results to the user.
- Jina token-budget plus beast-mode pattern is a simple way to guarantee a final answer.
