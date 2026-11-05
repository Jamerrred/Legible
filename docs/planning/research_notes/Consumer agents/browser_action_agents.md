# Browser-action agents: how they are built (read 2026-11-04)

Method: GitHub README pages and official docs, read through a summarising fetch tool, not cloned or run. "Not stated" means the page I read did not say it, not that the project lacks it. Items marked INFERENCE are mine. A quick, time-boxed pass of about 2 minutes; READMEs only, no source code read.

## browser-use
- Repo: https://github.com/browser-use/browser-use. MIT. About 120k stars (page, 2026-11-04).
- Perception: the README does not say. Docs show `use_vision` (True / False / "auto"), `highlight_elements` (marks interactive elements for the model's vision) and `paint_order_filtering` (drops hidden elements from the DOM tree) ([browser params](https://docs.browser-use.com/customize/browser/all-parameters), [agent params](https://docs.browser-use.com/customize/agent/all-parameters)). INFERENCE: a filtered DOM list of clickable elements plus an optional screenshot.
- Loop: `Agent(task, llm).run()` returns a history object; `final_result()` gives the answer. Custom actions via `@tools.action`. `max_failures` default 5 retries. `fallback_llm` takes over if the main model keeps failing. `flash_mode` skips the thinking/evaluation fields for speed.
- Structured output: `output_model_schema` (Pydantic).
- Secrets: `sensitive_data` placeholders. README warns snapshots and results are not redacted.
- Domains: `allowed_domains` (wildcards allowed) and `prohibited_domains`. The allow list wins if both are set.
- Iframes: `cross_origin_iframes` is off by default ("may cause complexity").
- CAPTCHA: the README says cloud stealth browsers and proxies "reduce" CAPTCHA challenges and nothing guarantees a solve. Cloud costs $0.02 per browser-hour plus traffic.
- Replay: `load_and_rerun` replays recorded steps without a model call per step. It fails at the first step that doesn't match, and earlier steps have already run (a form may already be submitted).
- Human gates: none stated on the page I read.
- Not found: PDFs, a token-cost discussion, a human approval gate. The architecture blog post URL I guessed returned 404.

## Stagehand (Browserbase)
- Repo: https://github.com/browserbase/stagehand. MIT. About 25.9k stars. TypeScript, Python, Go.
- Primitives: `act`, `observe` (candidate elements and selectors), `extract` (schema-validated; Zod / Pydantic) and `agent`. Caching with Browserbase can skip model calls on repeated identical calls. The README claims self-healing when sites change.
- Perception ([agent docs](https://docs.stagehand.dev/v3/basics/agent)): DOM mode uses the accessibility tree (default, any LLM, TypeScript only); CUA mode uses screenshots with a computer-use model; hybrid mode (recommended, experimental) uses both. Default viewport is 1288x711, and other sizes may cause misclicks.
- Iframes and shadow DOM: deep locators reach nested iframes and closed shadow roots (README).
- Recovery: agent stops at `maxSteps`; docs say check `result.success` and split tasks.
- Human-in-the-loop: no dedicated gate. Streaming, `onStepFinish` callbacks, abort signals.
- Not stated: domain restrictions, CAPTCHA handling, token costs.

## Skyvern
- Repo: https://github.com/Skyvern-AI/skyvern. AGPL-3.0 (copyleft; relevant if we embed or host it). About 23.3k stars.
- Perception: README says it relies on vision LLMs rather than XPath; Playwright underneath. DOM use not explained.
- Loop: "swarm of agents" plan and act; details are only in a diagram I couldn't read.
- Structured output: `data_extraction_schema` (JSON schema) or `page.extract(prompt, schema)`.
- CAPTCHA and anti-bot: only in Skyvern Cloud, not the open-source repo. 2FA (TOTP, email, SMS) supported.
- Self-reported accuracy: 64.4% on WebBench.
- Not stated: PDFs (only a file-parsing workflow block), conditionals ("coming soon"), human gates, domain limits.

## Playwright MCP
- Repo: https://github.com/microsoft/playwright-mcp. Apache-2.0. About 39.2k stars.
- Perception: accessibility-tree snapshots, no vision model needed. Optional `--caps=vision` adds coordinate clicks.
- Loop: it is a tool server; the calling LLM runs the loop. Tools cover click, type, navigate, forms, screenshots, PDF, tabs, network, JS evaluation.
- Restrictions: `--allowed-origins` / blocked origins, but the README says these are not a security boundary and the server "is not a security boundary".
- Gaps: no iframe notes, no structured-output or human-gate features on the page.

## agent-browser (Vercel Labs)
- Repo: https://github.com/vercel-labs/agent-browser. Apache-2.0. About 45.5k stars. Rust CLI.
- Perception: `snapshot -i` returns compact text with refs like `@e1`. The agent acts on a ref, re-snapshots, repeats. Refs go stale after DOM changes. Failed clicks report failure instead of silently succeeding.
- Safety: README mentions an auth vault, domain allowlists, action policies and `confirm` / `deny` commands, but only points to a Security guide I did not read. Frame, dialog, PDF and screenshot commands exist.
- Not verified: how the policies work.

## Magentic-UI (Microsoft)
- Repo: https://github.com/microsoft/magentic-ui. MIT. About 10.1k stars. README now presents "MagenticLite" (MagenticBrain orchestrator plus Fara browser model, in a VM sandbox); I did not verify whether this replaces the original. Experimental.
- Architecture (from the [Microsoft blog](https://www.microsoft.com/en-us/research/blog/magentic-ui-an-experimental-human-centered-web-agent/)): Orchestrator, WebSurfer, Coder, FileSurfer.
- Human gates (blog): user edits and approves a plan before execution; asks permission before irreversible actions; a configurable "ask before every action" mode; allow-list of sites, anything else needs explicit approval.
- Weaknesses: blog and README don't say how pages are shown to the model; evaluation was preliminary (GAIA, simulated users).

## Nanobrowser
- Repo: https://github.com/nanobrowser/nanobrowser. Apache-2.0. About 14.2k stars. Chrome/Edge extension.
- The README now describes a non-AI browser control layer: per-element IDs that go stale rather than point at a different element, visibility/enabled/covered checks before acting, Chrome debugger API plus Puppeteer for frames, optional screenshots. I did not see the older Planner/Navigator description.
- Gates: Ask mode (default) asks before submit, send, delete or upload. In both modes payments, passwords/codes and access grants go back to the user. Per-site Allow / Ask / Block rules. The README admits prompt-injection protection is imperfect.

## OpenManus and Suna
- OpenManus: https://github.com/FoundationAgents/OpenManus. MIT. About 58.9k stars. Default browser tool is browser-use over MCP (`uvx browser-use --cli-mcp`). README calls the multi-agent flow "unstable". Not a new browser layer.
- Suna: kortix-ai/suna now shows as kortix-ai/CompanyOS ("Kortix CompanyOS"), about 20.4k stars. License not stated on the page (separate white-label licence file mentioned). Browser approach not documented. Skip.

## Anthropic computer use
- Docs: https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/computer-use-tool. Screenshot plus mouse/keyboard toolset (17 tools incl. screenshot, click, type, key, scroll, zoom).
- Loop: send prompt, run returned actions in order, return `tool_result` (images for screenshots), repeat until text with no tool calls or an iteration limit. A failed action skips the rest of that batch.
- Security advice: use a dedicated VM/container, keep credentials from the model, allow-list domains, human confirmation for purchases, accepting terms and cookie consent. Prompt injection from pages is a stated risk.
- Screenshot limits: up to 2,576 px long edge / 4,784 visual tokens on newer models (page). I only read the first 100k of 128k characters, so latency, CAPTCHA and cost sections were not seen.

## Comparison
| Project | Licence | Stars | Page shown as | Structured output | Domain limits | Human gate |
|---|---|---|---|---|---|---|
| browser-use | MIT | 120k | filtered DOM + optional screenshot (inferred) | Pydantic | allow/deny lists | none stated |
| Stagehand | MIT | 25.9k | a11y tree, screenshots, or both | Zod/Pydantic | not stated | callbacks only |
| Skyvern | AGPL-3.0 | 23.3k | vision (+Playwright) | JSON schema | not stated | not stated |
| Playwright MCP | Apache-2.0 | 39.2k | a11y tree (+vision opt.) | caller's job | origins, "not a boundary" | none |
| agent-browser | Apache-2.0 | 45.5k | text snapshot + refs | caller's job | allowlist (unverified) | confirm/deny |
| Magentic-UI | MIT | 10.1k | not stated | not stated | allow-list + approval | plan approval, action guards |
| Nanobrowser | Apache-2.0 | 14.2k | element IDs + screenshots | not stated | Allow/Ask/Block | Ask mode |
| Claude computer use | API | n/a | screenshots | caller's job | advised allow-list | advised |

## Patterns across projects
- Two ways to show the page: text structure (DOM or accessibility tree with element IDs) or screenshots. Newer designs mix them (Stagehand hybrid, browser-use vision "auto"). INFERENCE: text first is cheaper and more stable; screenshots rescue widgets with no usable structure.
- IDs go stale on purpose (agent-browser, Nanobrowser): safer than clicking the wrong thing; the loop re-observes.
- Loop is observe, act, observe with a step cap and retry limit; a fallback model is a common safety net.
- Schema-validated output is standard in the SDKs (browser-use, Stagehand, Skyvern).
- Gates cluster around submit, send, delete, upload, payments, passwords. Nanobrowser and Magentic-UI have the clearest designs.
- CAPTCHA and anti-bot handling is a paid cloud feature (browser-use, Skyvern). Nobody claims to solve it reliably.
- Domain allow-lists exist but docs warn they are not security boundaries.
- Not found in any source: embedded third-party booking widget handling, PDF form filling, token cost per task. Treat as untested until we try.

## Copy / skip / recommendation
Copy:
- A hard step cap, retry cap, fallback model and a visible final status (Stagehand `success`, browser-use history).
- A schema for what comes back (price, availability, form fields found, what was submitted), enforced by the SDK.
- Allow-listed domains per assignment, and stale-ID safety.
- A gate before any submit with real personal data. For the demo, use fake persona data and make the gate a logged step, with "stop before final submit" as a mode.
- Save the step trace or GIF (`generate_gif`) as demo evidence.

Skip:
- Skyvern (AGPL, key anti-bot only in the cloud), Suna/Kortix, OpenManus (wraps browser-use), Magentic-UI (research prototype, heavy), Nanobrowser (browser extension, wrong shape for server use), Playwright MCP as the main loop (no loop of its own, "not a security boundary").

Recommendation: browser-use as the browser layer. MIT, by far the largest community, takes a self-contained task string, returns Pydantic output, has domain allow-lists and a fallback model. Use it with fake persona data and a "do not submit" instruction or custom action gate.
Runner-up: Stagehand (MIT, accessibility-tree default, iframe-aware, strong extract primitive; best if we write TypeScript and want deterministic scripts for known demo sites).
Caveats: I did not run either, did not read source, and could not verify browser-use's actual page representation, PDF behaviour, or booking-widget handling. A one-hour trial on 3 mock sites should decide it.
