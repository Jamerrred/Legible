# Simulation Harness, Human-in-the-Loop Inbox, Self-Improving Resource: Techniques and Risks (as of 3 November 2026)

Provenance key. Every bullet is from a page opened on 2026-11-03 unless tagged. **[snippet-only]** = seen only in a search-tool summary, page not opened (the session's shared WebSearch budget ran out, and a few pages returned 403 or were blocked). **[vendor claim]** = the vendor's own unverified statement. Status tags: **[shipped]**, **[announced]**, **[draft]**, **[research]**. Legal items are issues for counsel, not advice. Inferences are mine and carry no source.

## Simulation: state-of-the-art methods and tools for simulated users and agent testing

### Takeaway
The working pattern everywhere is a three-role loop: an LLM simulated user, the system under test, and an independent judge, re-run many times and gated in CI. No vendor tool targets Legible's exact case, which is simulating a consumer *agent* against a small business's resource, so open-source components plus a thin custom layer fit best.

### Cited Findings
- **tau-bench** [shipped, open source]: latest is tau-bench 2.0 (tau-i18n), six languages in text and full-duplex voice. The prior release, tau3-bench v1.0, added voice and `banking_knowledge`. Latest changelog entry shown is v1.0.1, 2026-07-15. Domains: mock, airline, retail, telecom, banking_knowledge, intake. — [tau2-bench repo](https://github.com/sierra-research/tau2-bench)
- **Sierra simulations** [shipped; vendor claim] (19 Aug 2025): personas vary by language, tech comfort and tone; tests are auto-generated from SOPs, knowledge bases, coaching transcripts and flows, and persist for re-runs; a separate judge grades goal reached, SOP and brand adherence, and accuracy; releases can be gated through GitHub Actions or CLI; 35,000+ tests a day across customers. The post does not describe adversarial tests or statistical methods. — [Sierra](https://sierra.ai/blog/simulations-the-secret-behind-every-great-agent). A search summary dated this post April 2026 from a blog index; the opened page says August 2025.
- Sierra's product head describes re-running a conversation 5, 10 or 15 times and comparing outcomes, with user agent, AI agent and LLM evaluator, plus adversarial tests for hijacking and abuse. **[snippet-only]** — [MLOps Community talk](https://home.mlops.community/home/videos/simulate-to-scale-how-realistic-simulations-power-reliable-agents-in-production-sachi-shah-2025-11-27). Voice Sims launched around Sept 2025, free to customers. **[snippet-only]** — [AI Economy](https://theaieconomy.substack.com/p/ai-customer-service-sierra-voice-sims-launch)
- **Salesforce Agentforce** [shipped]: tests are generated from the subagents and actions assigned to the agent, default 20 cases, with the positive/negative split set in the Test Objective, run in parallel. The Trailhead unit does not mention metrics, multi-turn or personas. — [Trailhead](https://trailhead.salesforce.com/content/learn/modules/agentforce-agent-testing/use-ai-to-generate-tests). Multi-turn personas such as "frustrated customer" appear in one developer post only. **[snippet-only]** — [dev.to](https://dev.to/dipojjal/how-to-test-agentforce-agents-before-they-hit-production-44fj)
- **Scenario (LangWatch)** [shipped, Apache-2.0, about 1.0k stars]: `UserSimulatorAgent` plus `JudgeAgent(criteria=[...])`, scripted flows, judge callable at chosen points, one `call()` adapter, works across frameworks, and a red-team section including GOAT. — [site](https://langwatch.ai/scenario/); [repo](https://github.com/langwatch/scenario)
- **Promptfoo** [shipped, open source]: agent plugins include `bola`, `bfla`, `rbac`, `ssrf`, `pii`, `cross-session-leak`, `rag-poisoning`, `agentic:memory-poisoning`, `tool-discovery`, `mcp`, `excessive-agency`, `hijacking`. Strategies include `crescendo`, `mischievous-user`, `jailbreak:hydra`, and OpenTelemetry trace-based grading. That page names no dedicated indirect-injection plugin. — [docs](https://www.promptfoo.dev/docs/red-team/agents/). Acquisition by OpenAI announced 9 Mar 2026, closing subject to conditions at that date; the company says it will stay open source and multi-provider. — [Promptfoo](https://promptfoo.dev/blog/promptfoo-joining-openai)
- **Inspect AI** [shipped]: agents, multi-agent, checkpointing, intervention, Agent Bridge for external frameworks, and limits on tokens, messages and time. The agents page does not mention simulated users or cost limits. — [Inspect](https://inspect.aisi.org.uk/agents.html)
- **Petri** [shipped]: donated by Anthropic to Meridian Labs on 7 May 2026. Petri 3.0 separates auditor and target, and its "Dish" add-on runs tests with the model's real system prompt and scaffolding because models often detect artificial tests. An auditor simulates scenarios and a judge scores transcripts. It tests model alignment (deception, sycophancy), not a business's resource. — [Anthropic](https://www.anthropic.com/research/donating-open-source-petri). Built on Inspect. **[snippet-only]** — [Inspect Petri](https://meridianlabs-ai.github.io/inspect_petri/)
- **Coval, Cekura, Bluejay, Maxim** [shipped; vendor claims]: Bluejay claims "Digital Humans" across voice, chat and text plus A/B testing, no plan details on the page. — [Bluejay](https://www.getbluejay.ai/). Maxim claims multi-turn persona simulation with AI, human and programmatic evaluators and CI integration. — [Maxim](https://www.getmaxim.ai/products/agent-simulation-evaluation). Coval's plans meter simulation minutes and include persona libraries of 10 to 50. — [Coval](https://www.coval.ai/pricing). Cekura's plans list production call simulation and bill per voice minute and per reply. — [Cekura](https://www.cekura.ai/pricing)
- **Published persona methods**: Persona Policies (PPol, 13 May 2026, U. Washington and Georgetown) evolves a persona generator by program search, with fitness combining human-likeness (a discriminator over 19 behavioral features) and coverage (Chamfer distance to human traces). Evolved rules are operational, such as withholding the order number in the opening message or answering one field at a time. — [arXiv 2605.12894](https://arxiv.org/html/2605.12894v1). RealUserSim (Salesforce, May 2026) builds 7,275 behavioral profiles from real WildChat conversations (the page also shows 7,273), pairing commands with real quotes. — [alphaXiv 2605.20204](https://www.alphaxiv.org/abs/2605.20204)

### Inferences
- Design recommendation: use a two-layer harness. A persona layer plays the human consumer and instructs a stock LLM acting as the consumer agent, which calls the real Legible endpoint. Assert on endpoint state and tool calls rather than prose alone.
- Build: Scenario or a thin custom loop for functional runs; Promptfoo for adversarial runs on a schedule (`bola`, `cross-session-leak`, `mcp`, `excessive-agency`, memory poisoning). Skip paid voice-first vendors unless voice becomes a channel.
- Petri's Dish lesson transfers: test with real client scaffolding. Periodically replay scenarios through actual clients (Claude, ChatGPT and others) to check the stock consumer-agent prompt.
- Promptfoo's ownership change is a dependency risk worth tracking, though its stated open-source commitment is the mitigation.

### Gaps
- I found no published method specifically for simulating consumer agents against SMB resources.
- Bluejay's plan pricing conflicts across third-party pages and Maxim's simulation price is not public (see the cost question).

## Simulator realism and the simulator-reality gap

### Takeaway
LLM simulators are measurably an "easy mode": too polite, too complete, too cooperative, and they do not walk away. LLM judges also diverge from human ratings. Treat simulator scores as a regression signal and a gap finder, never as a prediction of real-world performance.

### Cited Findings
- **Mind the Sim2Real Gap** (March 2026; 451 people, 165 tau-bench tasks, 31 simulators; same GPT-5.2 agent) [research]: User-Sim Index is 92.9 for the human baseline, best 76.0 (DeepSeek-V3.1), best proprietary 73.3 (Gemini-2.0-Flash), GPT-5.1 70.9, lowest 46.5. — [arXiv 2603.11245](https://arxiv.org/html/2603.11245v1)
- Same study, behavior: GPT-4o polite turns 49.0% vs 15.3% for humans; short turns 1.0% vs 29.0%; pivots after errors 19.1% vs 8.4%. Human baseline task success was 63.6%, with general simulators mostly higher, up to 77.8%. — [arXiv 2603.11245](https://arxiv.org/html/2603.11245v1)
- Same study, judging: a GPT-5.1 evaluator scored human-likeness +1.11 and reuse intent +0.83 above human raters, and task success −0.15. Binary reward aligned poorly: 70.6% of reward=0 interactions were judged successful by humans, and about 33% of reward=1 were judged unsuccessful or partial. — [arXiv 2603.11245](https://arxiv.org/html/2603.11245v1)
- More capable models did not reliably give more faithful simulators. — [arXiv 2603.11245](https://arxiv.org/html/2603.11245v1)
- **Simulated Customers Never Walk Away** (June 2026; 2,790 production sales conversations, 793 with verified payment) [research]: simulators match eventual buyers (depth bias +0.09) but overstate engagement among non-buyers (+0.40, d=0.38). Non-buyer resistance falls from 25.1% to 13.5%; deliberation rises from 21.9% to 40.1%. Telling the simulator it may disengage cut marginal bias about five-fold but barely changed the buyer/non-buyer contrast. — [arXiv 2606.20708](https://arxiv.org/abs/2606.20708)
- **RealUserSim**: unconstrained simulators match real style only 6–8%; hand-written directives like "act frustrated" get exaggerated. Grounded profiles raise the fidelity match from 24.2% to 45.3%, and lower tau-bench success about 3.2–3.5%. Removing the hand-crafted difficult directives improved retail by up to 16.7%, suggesting they are artificially adversarial. — [alphaXiv 2605.20204](https://www.alphaxiv.org/abs/2605.20204)
- **PPol**: annotators rated PPol users human 80.4% of the time vs 46.5% for baseline (16 annotators, 87 conversations). Agents fine-tuned with PPol improved 17% on simulated challenge suites (0.213 to 0.250). The paper lists live-user performance as future work. A search summary reported a +23% live-user figure, which the opened paper does not contain. — [arXiv 2605.12894](https://arxiv.org/html/2605.12894v1)

### Inferences
- Almost all of this evidence concerns simulated *humans*. Legible's caller is an LLM agent, so the style gap may be smaller but the behavior gap is different: first-proposal bias, tool selection, browser versus protocol paths. Do not import the human numbers as an estimate of Legible's gap.
- Design recommendation: grade with deterministic checks (slot held, correct price returned, policy path taken) first and use the LLM judge only for prose. Hand-audit a sample of judge verdicts each cycle, since judge error is documented.
- Add an explicit "walk-away" persona share, but do not trust it to fix the bias, given the five-fold result that left the buyer/non-buyer contrast intact.
- Report results to owners as "gaps found", never as "X% of agents will succeed".

### Gaps
- I found no study measuring how well simulated consumer agents match real consumer-agent traffic.

## Generating a query set, coverage scoring, gap detection, and turning failures into owner questions

### Takeaway
Vendors generate tests from an agent's own documents and actions, which misses what the business never wrote down. Legible should generate from a vertical intent taxonomy instead. Coverage scoring has no published standard, so this is design work.

### Cited Findings
- Sierra generates from SOPs, knowledge bases, coaching transcripts and flows [vendor claim]. — [Sierra](https://sierra.ai/blog/simulations-the-secret-behind-every-great-agent)
- Agentforce generates from assigned subagents and actions, with a set positive/negative split. — [Trailhead](https://trailhead.salesforce.com/content/learn/modules/agentforce-agent-testing/use-ai-to-generate-tests)
- PPol's coverage objective (distance to the human behavioral distribution) is the only published coverage metric I found, and it covers behavior, not intents. — [arXiv 2605.12894](https://arxiv.org/html/2605.12894v1)
- Decagon tests fixes against the originating conversation plus a golden set of hundreds, updated automatically [announced; vendor claim, 9 Jun 2026]. — [Decagon](https://decagon.ai/blog/autopilot)

### Inferences
- Design recommendation, query generation: build a `vertical × intent × constraint × persona` matrix. Example for a plumber: book, quote, emergency, hours, service area, payment terms, cancel, warranty. Use pairwise sampling rather than the full cross-product. Start with about 40 scenarios per business, 5 repeats each. Generating only from the business's existing content would hide exactly the gaps this feature exists to find.
- Design recommendation, scoring: report five sub-scores per intent, not a composite. (1) Capability: is a tool or fact present? (2) Answerable: was it answered at all? (3) Correct: does it match owner-confirmed ground truth? (4) Actionable: could the action complete or reach the inbox? (5) Policy: did it take the right allow/ask/deny path?
- Design recommendation, triage: classify each failure as missing fact, missing capability, contradictory facts, ambiguous policy, or agent/harness error. Only the first four become owner questions; the last goes to the Legible team.
- Design recommendation, owner questions: rank by likely intent frequency × severity. Ask one at a time in plain language, show the concrete scenario, and offer tap answers plus "doesn't apply". Example: "An agent asked to book Tuesday 2pm. Nothing is connected to your calendar. Connect it, or take requests by text?" Cap at about three a week so this does not add to approval fatigue. All numbers here are starting values to tune in the pilot.
- A "doesn't apply" answer must suppress that intent permanently, or the harness will nag.

### Gaps
- I found no public SMB-vertical intent library or benchmark; it would have to be authored.
- I found no published method for converting evaluation failures into owner-facing questions.

## Cost of a simulation run

### Takeaway
Token cost is small if the volume work runs on a cheap model and the judge on a stronger one: roughly $4 per 200-conversation run on my assumptions. Per-minute vendor pricing is about ten times or more higher and is built for voice.

### Cited Findings
- Anthropic list prices per MTok, input/output, seen 2026-11-03: Sonnet 5 $2/$10; Haiku 4.5 $1/$5; Haiku 5.5 $0.10/$0.50 for prompts up to 100k tokens. Batch API is 50% off. Claude 4.7 and later use a tokenizer producing about 30% more tokens. — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Coval [vendor pricing]: Starter $100/mo with 100 simulation minutes, $0.40/min overage; Growth $500/mo with 1,000 minutes, $0.25/min; Enterprise from $4,500/mo. Chat and voice metering are not distinguished. — [Coval](https://www.coval.ai/pricing)
- Cekura [vendor pricing]: pay-as-you-go $0.25/voice minute and $0.025/reply (the reply rate has no chat label); Startup $500/mo with about 2,000 minutes. — [Cekura](https://www.cekura.ai/pricing)
- Maxim's pricing URL now shows only the gateway product, OSS free and Enterprise custom, with no per-log or per-seat prices. — [Maxim pricing](https://www.getmaxim.ai/pricing). Bluejay's page lists "Start for Free" with no plan details. — [Bluejay](https://www.getbluejay.ai/). A $500 Growth tier with 1,500 minutes is reported by a competitor-adjacent page. **[snippet-only]** — [Vattara](https://vattara.ai/blog/bluejay-alternatives)
- tau-bench's text-v1 is 900 calls for one trial, and a cheap check is 12 calls. No cost figures are published. — [tau2-bench repo](https://github.com/sierra-research/tau2-bench)

### Inferences
My worked estimate. Assumptions (mine, unmeasured): 8 turns; simulator 2,000 input and 60 output tokens per turn; consumer-agent LLM 4,000 and 150 per turn; judge 5,000 and 400 once. Total 53,000 input and 2,080 output tokens per conversation. A run is 40 scenarios × 5 repeats = 200 conversations. A month is 24 businesses × weekly ≈ 104 runs.

| Model mix | Per conversation | Per run | Per month |
|---|---|---|---|
| All Sonnet 5 | $0.127 | $25.36 | ≈$2,640 |
| All Haiku 4.5 | $0.063 | $12.68 | ≈$1,320 |
| Haiku 5.5 sim and agent, Sonnet 5 judge | $0.020 | $3.93 | ≈$410 |
| All Haiku 5.5 | $0.006 | $1.27 | ≈$130 |

- Batch API would roughly halve these for non-urgent runs. Adjust upward if the tokenizer note applies to the model you pick.
- For scale, Cekura at $0.025 per reply would be about $40 a run and $4,160 a month if a reply means one agent turn (unit unclear). Coval Growth would be about $10,650 a month if a conversation is metered at two minutes (metering unclear).
- Design recommendation: weekly full runs, plus a small smoke set (about 10 scenarios) on any resource change. Do not assume the cheapest simulator is adequate; re-validate it against the stronger model on a sample, since the capability/fidelity relationship is not monotonic.

### Gaps
- Real per-conversation token counts need measuring on the prototype.
- Vendors publish no chat-specific simulation pricing I could find.

## Agent readiness scoring: public tools and rubrics

### Takeaway
Public scorers test protocol plumbing such as robots.txt, MCP cards and OAuth discovery, not whether an agent can actually complete a task with this business. That is the gap Legible's outcome-based harness fills.

### Cited Findings
- **Cloudflare Agent Readiness / isitagentready.com** [shipped, 17 Apr 2026; page modified 15 Jul 2026]. Discoverability: robots.txt, sitemap, Link headers. Content: Markdown negotiation (llms.txt only in custom scans). Bot Access Control: Content Signals, AI bot rules, Web Bot Auth. Capabilities: Agent Skills, API Catalog (RFC 9727), OAuth discovery, MCP Server Card, WebMCP. x402, UCP and ACP are checked but do not count. Failing checks give prompts for coding agents. It also exposes an MCP `scan_site` tool and a URL Scanner tab. — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- Cloudflare Radar, top 200,000 domains: 78% have robots.txt (mostly for search crawlers), 4% declare Content Signals, 3.9% pass Markdown negotiation, and fewer than 15 sites have MCP Server Cards or API Catalogs. — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- Weighting and scale are not defined in the post. Third parties conflict: 16 checks across five categories with levels such as Bot-Aware and Agent-Native, versus 19 checks on a 0–5 scale. **[snippet-only]** — [Georadar](https://georadar.tenten.co/en/glossary/agent-readiness-score); [SEJ](https://www.searchenginejournal.com/all-you-need-to-know-about-cloudflares-agent-readiness-score/). Critics warn against treating the composite as more than a checklist. **[snippet-only]** — [McKaye](https://jamiemckaye.com/agent-readiness-score-useful-number-trap/)
- **StartupHub.ai** [shipped 20 Apr 2026]: 50+ signals in six dimensions (Discoverability, Content, Access, Capabilities, Commerce, Quality), A+ to F, free, callable over MCP. Its sidebar shows a stated median of 41. — [StartupHub](https://www.startuphub.ai/news/why-we-built-agent-readiness-scanner-2026)
- **Codal** audit runs a live agent through user journeys across five weighted layers; **Apify** actor runs nine checks; **Agentic Readiness Index** uses Google Lighthouse's agentic-browsing audit with four pillars (Read, Understand, Act, Trust). All **[snippet-only]**. — [Codal](https://codal.com/insights/ai-agent-readiness-audit-framework/); [Apify](https://apify.com/exalted_mud_vjz/agent-readiness-audit); [ARI](https://4amkarmyogi-agentic-readiness-index.static.hf.space/index.html)

### Inferences
- Design recommendation: run isitagentready against the Legible-hosted resource as a hygiene check (it has an MCP tool, so it automates cheaply), but make the owner-facing score outcome-based: "of the 40 things agents ask, how many can you answer or act on?" This is a differentiator, since the static scorers cannot see it.
- Fewer than 15 sites among 200,000 having MCP cards in April 2026 suggests real MCP traffic to a long-tail business will be very sparse for now, which affects the trace plan below.

### Gaps
- I could not verify the Lighthouse agentic-browsing audit from a primary Chrome source, because search was exhausted.
- I found no rubric aimed at long-tail service businesses.

## Human-in-the-loop: asynchronous approval protocols

### Takeaway
Standards for durable pending states now exist (MCP Tasks, A2A), but consumer-client support is thin: ChatGPT is not listed as supporting MCP Tasks. Legible must work without them, using a plain tool result that says "pending" with a handle, backed by its own durable workflow.

### Cited Findings
- **MCP Tasks** [shipped as an official extension in spec 2026-07-28; previously experimental in core 2025-11-25]: server returns a durable handle with `taskId`, status, `ttlMs`, `pollIntervalMs`; states `working`, `input_required`, `completed`, `failed`, `cancelled`; polling via `tasks/get`; input via `tasks/update`; cooperative `tasks/cancel`. Human approval is a named use case. Clients should persist task IDs, and servers must never return a task to a client that did not declare support. — [MCP Tasks](https://modelcontextprotocol.io/specification/2026-07-28/basic/utilities/tasks); [AAIF, 28 Aug 2026](https://aaif.io/blog/handle-long-running-mcp-tool-calls-with-the-mcp-tasks-extension)
- `tasks/list` was removed; a JSON-RPC error marks `failed`, while `isError: true` still counts as `completed`. — [AAIF](https://aaif.io/blog/handle-long-running-mcp-tool-calls-with-the-mcp-tasks-extension)
- **Client support** (community-maintained matrix, read 2026-11-03): Tasks is checked for Claude (web), Claude Code, MCPJam and Glean. Not checked: ChatGPT, Claude Desktop, Cursor, VS Code Copilot, M365 Copilot. — [matrix source](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/extensions/client-matrix.mdx)
- **MCP 2026-07-28 core**: sessions removed and stateless; MRTR's `InputRequiredResult` replaces server-initiated requests; SSE resumability removed, so a broken stream loses the in-flight request and clients must re-issue it. — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- **MCP elicitation**: asks the *client's user*. Form mode must not collect secrets; URL mode is required for payment and credentials. URL mode `accept` means consent, not completion. URLs must not be pre-authenticated or carry PII, and the server must verify the person opening the link. — [elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)
- **A2A** [v1.0, joined the Agentic AI Foundation per site banner; release date not shown]: interrupted states `INPUT_REQUIRED` and `AUTH_REQUIRED`; terminal `COMPLETED`, `CANCELED`, `REJECTED`, `FAILED`; terminal tasks cannot restart, so follow-ups need a new task. — [life of a task](https://a2a-protocol.org/latest/topics/life-of-a-task/); [v1 notes](https://a2a-protocol.org/latest/whats-new-v1/)
- A2A push notifications suit tasks of minutes to days. Webhook auth is required, receivers should guard against replay, and servers should not POST to unchecked client URLs because of SSRF. — [A2A async](https://a2a-protocol.org/latest/topics/streaming-and-async/)
- **LangGraph**: `interrupt()` plus `Command(resume=...)`, needs a durable checkpointer and the same `thread_id`. The node restarts from the top on resume, so side effects before the interrupt re-run; make them idempotent. — [LangChain](https://docs.langchain.com/oss/python/langgraph/interrupts)
- **Inngest**: `step.waitForEvent` returns null on timeout, needs a stable `match` ID, and only sees events sent after it starts listening. Register the wait first or check external state. — [Inngest](https://www.inngest.com/docs/features/inngest-functions/steps-workflows/wait-for-event)
- **Temporal**: timers range from a second to years, persist through outages, and use no worker resources while pending; signals are asynchronous writes, updates are tracked and acknowledged. Those pages do not spell out an approval recipe. — [timers](https://docs.temporal.io/workflow-execution/timers-delays); [message passing](https://docs.temporal.io/encyclopedia/workflow-message-passing)

### Inferences
- Key semantic point: `input_required` and elicitation mean "the *caller* must supply input". Waiting on the *business owner* is not that. Model owner review as `working` with a status message. Use `input_required` only for questions to the consumer, such as "2pm is gone, would 3pm work?". Misusing it would prompt the consumer agent to answer its own approval.
- Design recommendation, dual path. If the client declares Tasks, return a task. Otherwise return an ordinary completed tool result such as `{status:"pending_owner_approval", request_id, expires_at, check_with:"get_request_status", what_to_tell_user:"Not confirmed yet..."}` and expose `get_request_status`. Bind `request_id` to the caller, because the spec says possession of a handle is not authentication.
- Design recommendation, engine: for a two-person team use a durable-function service (Inngest fits; Temporal is more than a pilot needs). LangGraph is only needed if the approval sits inside an LLM graph, and Legible's approval path should not be LLM-driven. Keep a plain `approval_request` table as the source of truth, so that switching engines is cheap.
- Handle the Inngest-style race by writing the row and starting the wait before notifying the owner.
- Make denial a completed result with `decision:"denied"`, not a protocol failure. Agents then treat it as an answer rather than retrying.

### Gaps
- The matrix is community-maintained and undated; verify with live client tests.
- I did not confirm Gemini, Perplexity or other consumer agents' behavior; none are on the matrix.

## Human-in-the-loop: session end, timeouts, and notifying an owner who works with their hands

### Takeaway
Assume the requesting agent is gone by the time the owner answers. Deliver outcomes out-of-band, hold inventory on a short lease, and fail closed on expiry. SMS is the cheap default: about 3 cents per round trip on Twilio, plus 10DLC registration.

### Cited Findings
- A task ID lets a client resume polling after restart, but only if the client persists it and supports Tasks. — [MCP Tasks](https://modelcontextprotocol.io/specification/2026-07-28/basic/utilities/tasks)
- Client-side tool timeouts are commonly about 60 seconds (one SDK default). **[snippet-only]** — [mcp-use](https://docs.mcp-use.com/typescript/client/tools). A user reported OpenAI's client failing with error 424 at about a minute and ignoring progress. **[snippet-only; user report, may be dated]** — [OpenAI forum](https://community.openai.com/t/call-remote-mcp-server-tool-timed-out-resulting-in-error-424/1364167)
- **Twilio US SMS** (Oct 2026): $0.0083 per segment each way; carrier fees outbound AT&T $0.0035, T-Mobile $0.0045, Verizon $0.005; inbound AT&T $0.0035, T-Mobile $0.0025, Verizon $0.007. Long code $1.15/mo, toll-free $2.15/mo. Failed message $0.001. 10DLC onboarding fees are mentioned but not listed. — [Twilio](https://www.twilio.com/en-us/sms/pricing/us)
- **10DLC fees** **[snippet-only; Twilio's article returned 403 to the fetcher]**: sole-prop or low-volume brand $4.50 one-time, secondary vetting $41.50, Standard about $46 up front; campaign verification $15 per campaign; sole-prop campaign $2/mo, one campaign per brand, about 1,000 msgs/day; registration up to 5 business days for standard use. — [Twilio fees](https://support.twilio.com/hc/en-us/articles/1260803965530); [vetting FAQ](https://support.twilio.com/hc/en-us/articles/11587910480155-A2P-10DLC-Campaign-Vetting-FAQ); [overview](https://pages.twilio.com/10DLC-HelpArticles-WW)
- **Twilio messaging policy**: prior express consent is required, for one sender and subject, with proof kept; informational messages need express consent, promotional need written consent; first message must carry an opt-out; every message must identify the sender; all traffic is treated as A2P. — [Twilio policy](https://www.twilio.com/en-us/legal/messaging-policy)
- **WhatsApp via Twilio** (Sep 2026): Twilio $0.005 each way plus Meta $0.0034 for utility templates outside the 24-hour window. The page is internally inconsistent on in-window charges and on marketing fees. — [Twilio WhatsApp](https://www.twilio.com/en-us/whatsapp/pricing)

### Inferences
- A pending request should survive with no agent attached. Design recommendation: capture a consumer reachback at request time (phone or email, with consent, or a status URL the agent is told to give its user) and send the outcome there. The tool result should instruct the agent to tell its user that the booking is *not confirmed* and how they will hear back.
- Design recommendation, leases: a booking request places a tentative hold with a short TTL so the slot is not double-sold and cannot be held forever. Starting values, unsourced and to tune: first alert immediately; reminder at 15 min; second channel at 30 min; expire at 2 h or at a cutoff before the slot, whichever comes first. Discounts: 24 h. Payment links: 1 h.
- Design recommendation, fail closed: expiry equals "not approved", and the requester is told so. If the owner approves late, re-validate slot and price and treat any change as a new request.
- Owner channels, in order: SMS by default (nothing to install); WhatsApp where the owner already lives in it; push if they install a PWA. Batch low-risk items into a digest. Respect quiet hours and let the owner set "on the job" snooze so requests expire honestly rather than silently.
- SMS binding: a bare "YES" is ambiguous with two pending items. Use reply codes such as "Y7/N7", or a one-tap link. For anything involving money, require the link with a session or PIN, in line with the MCP rule that URLs must not be pre-authenticated and the opener must be verified.
- Keep message text free of consumer data for clinics: "New request #A7, tap to review." Do not put PHI in SMS.
- Cost estimate: one round trip (one outbound and one inbound segment) costs about $0.024–$0.029, depending on carrier. At 100 round trips per business per month across 24 businesses, about $70/mo. That budget is immaterial compared with trust; do not ration alerts to save on SMS.
- Design question for Twilio or counsel: Legible alerting opted-in owners from one Legible-registered brand is simpler than registering 24 small businesses. It would only work for owner alerts; consumer-facing texts sent in a business's name may need per-business registration.

### Gaps
- No standard exists for a consumer agent waking up later to act on a resolved request, and I found no documentation on how ChatGPT handles a pending state. Test this empirically.
- Quiet-hour requirements were not covered by the pages opened.
- WhatsApp's US share among tradespeople is not known from my sources.

## Comparable SMB products, approval fatigue, and auto-approve design

### Takeaway
SMB tools mostly use text alerts plus a review queue with no approve-by-reply that I could confirm. Evidence on fatigue is strong: people approve almost everything, so the inbox must be rare, specific, and backed by deterministic rules.

### Cited Findings
- **Jobber AI Receptionist** [shipped; vendor claim]: books using existing online-booking settings; if it cannot book, creates a work request to review; keyword-based transfer or text alert; owner can watch text threads live and take over; everything logged with transcript. The page shows no approval workflow for bookings or pricing. — [Jobber](https://www.getjobber.com/hclp/ai-receptionist/)
- Housecall Pro CSR AI books into the live schedule from a price book. **[snippet-only]** — [Stork](https://www.stork.ai/compare/housecall-pro-ai-team-vs-jobber-ai-receptionist). Direct booking for standard services and manual approval for longer jobs is described as an option. **[snippet-only]** — [SkipCalls](https://skipcalls.com/blog/answering-service-appointment-setting)
- **Anthropic Claude Code data** (25 Mar 2026): users accept 93% of manual prompts, and approval fatigue is named as the reason manual review degrades. Its three tiers: safe allowlist, in-project actions, then a classifier for anything with real downside. The classifier's false-negative rate on real overeager actions is 17% (n=52), and false-positive rate 0.4% on real traffic (n=10,000). — [Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)
- Aug 7, 2026 follow-up: classifier flagged more dangerous actions than developers did by hand, but publishes no catch rate; teams still add deny rules, and some users go manual for sensitive work. — [Claude blog](https://claude.com/blog/auto-mode-in-production). Secondary reports cite 97% approvals and 89% vs 14% catch rates. **[snippet-only; not in the opened post, so unverified]** — [Gigazine](https://gigazine.net/gsc_news/en/20260810-claude-code-auto-mode/)
- Meta's Rule of Two notes that compliant designs can still fail when a user approves a warning without reading it (31 Oct 2025). — [Meta](https://ai.meta.com/blog/practical-ai-agent-security/)
- Decagon quotes a customer accepting almost 100% of Autopilot suggestions [vendor claim, 9 Sep 2026]. — [Decagon](https://decagon.ai/blog/autopilot-in-production)
- OWASP ASI09 is Human-Agent Trust Exploitation: adversaries use people's trust in an agent to influence decisions. — [Modulos summary of OWASP](https://docs.modulos.ai/frameworks/owasp-top-10-agentic)

### Inferences
- Read near-100% approval as a warning as much as a success. Decagon's quote is marketing, but paired with the 93% figure it suggests approval rates should not be used as a quality metric.
- Design recommendation: treat every ask as spent attention. Target few asks per day per business. Track approve rate, time to decision, and approvals made without opening details. Any rule at more than 90% approvals over a meaningful count gets a proposal to convert to allow-with-limits, and the owner confirms it. Never auto-promote money rules.
- Design recommendation: the approval card is rendered from structured fields only: requester identity tier, action, exact price, slot, expiry. Free text from the requesting agent is hidden by default and shown as quoted data, because that string is attacker-controlled and targeted at the owner.
- Add a random "control" check sparingly, such as a monthly rule review, rather than synthetic fake approvals, which would erode trust among busy owners.

### Gaps
- I could not confirm any SMB product with SMS approve/deny of a pending booking, and Podium did not surface in search.
- No published approval-fatigue data for small-business owners; the available numbers are from developers.

## Policy model: expressing allow, ask, and deny rules over intents

### Takeaway
Use a small deterministic rule table over intents with hard constraints, evaluated outside the LLM. AP2's open/closed mandate pattern and fail-closed handling of unknown constraints are the best templates; Sierra's distinction between plain-English rules and deterministic guards shows why the rules must not live only in a prompt.

### Cited Findings
- **AP2** [v0.2 referenced on site; samples shipped; standardization continuing in FIDO working groups]: two verifiable credentials with open and closed stages. Checkout Mandate records items and purchase details, and Payment Mandate authorizes against an instrument. Open states constraints such as budget and allowed instruments; closed binds to one transaction. Cards are the initial pull method; samples cover human-present and human-not-present; push payments and digital currencies are on the roadmap. — [AP2](https://ap2-protocol.org/). Repo: no releases listed, Python SDK not on PyPI. — [GitHub](https://github.com/google-agentic-commerce/AP2)
- AP2 framework: users approve on a Trusted Surface; a Verifier verifies the chain, confirms the closed mandate matches, evaluates each constraint, and returns a signed receipt; **unknown constraints must fail**. Examples shown are `checkout.line_items` and `checkout.allowed_merchants`; after a successful receipt, the agent narrows the open mandate's scope. Fallback may be a directly approved closed mandate or a non-agentic flow. — [AP2 authorization](https://ap2-protocol.org/ap2/agent_authorization/)
- Third-party pages disagree on v0.2's date (April vs 20 May 2026). Earlier field names such as `intent_expiry` appear in a third-party crate's fixture, but are not confirmed in the current Checkout/Payment model. **[snippet-only]** — [a2a-ap2 crate](https://docs.rs/crate/a2a-ap2/0.3.1/source/src/types/mandate.rs)
- **Sierra, Defense in Depth** (13 Aug 2026): layers are content, plain-English rules, supervisors (separate models that block, rewrite or nudge), deterministic guards (e.g., account tools withheld until authenticated; output scanning for payment details), plus monitoring and red teaming. It states that rules share a prompt with customer input, retrieval can pull planted instructions, supervisors share agent weaknesses, and guards only enforce what is explicitly defined. — [Sierra](https://sierra.ai/blog/defense-in-depth-in-the-age-of-agents)
- **Payment-UX requirements in MCP**: payment credentials must not use form mode; use URL mode; show the full domain; do not pre-fetch; the client must not be able to inspect entries. — [elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)

### Inferences
- Design recommendation, the schema. An example rule, conceptual:
  `{intent:"booking.create", when:{service:"drain_clean", within_hours:true, lead_time_h:{gte:4}, price_total:{lte:250}}, action:"allow", limits:{per_requester_per_day:2}, on_expire:"deny"}`
  Resolution: deny beats ask beats allow; no matching rule means **ask**; a rule with an unrecognized constraint means **deny and alert** (AP2 pattern).
- Fixed constraint vocabulary for the pilot: service, price or discount cap, date/time window, lead time, party size, requester identity tier, velocity limits. Do not let owners write free-form rules that an LLM interprets at runtime; an LLM may *draft* structured rules from what an owner says, which the owner then confirms.
- Onboarding defaults by vertical, conservative: read-only facts allow; bookings ask; discounts ask with a cap; payment links ask; refunds and anything outside listed services deny. Med-spa and clinic defaults stricter.
- Never let the LLM decide policy. Legible's endpoint should compute the decision in code, and the LLM may only phrase it.
- AP2 mandates are not something long-tail businesses will meet soon, and the repo has no tagged release. Copy the concepts (open vs closed, constraints, signed receipts, fail closed) rather than integrating now. Log a signed internal receipt for each approval: who approved what, exact terms, at what time.
- Never collect card data through the agent channel; a payment link should go to a hosted page from an established processor, so PCI scope stays with them.

### Gaps
- I did not find a published owner-facing allow/ask/deny rule UX for SMBs.
- AP2's budget/expiry constraint field names could not be confirmed in the pages opened.

## Trace capture: what is observable at the endpoint, and which standards apply

### Takeaway
Legible sees only the calls that reach it: what was asked, which tool, what was returned. It does not see the consumer's prompt, reasoning, alternatives, or the eventual outcome. Log your own structured events and use OTel conventions, noting they are still in Development.

### Cited Findings
- MCP 2026-07-28 requests carry protocol version and client capabilities in `_meta`; clients **SHOULD** identify themselves in `clientInfo`; `Mcp-Method` and `Mcp-Name` headers are required on Streamable HTTP. With sessions removed, cross-call state uses server-minted handles. SEP-414 documents `traceparent`, `tracestate`, `baggage` in `_meta`. Logging is deprecated in favor of stderr or OpenTelemetry. — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- **OTel GenAI**: conventions moved to a dedicated repo; the MCP client and server span status is **Development**; span name `{mcp.method.name} {target}`; required `mcp.method.name`, plus `gen_ai.tool.name`, `gen_ai.operation.name=execute_tool`; `gen_ai.tool.call.arguments` and `.result` are opt-in and sensitive; the MCP client span is the parent of the server span. The repo's schema URL is listed as TODO and no release is shown. — [MCP conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md); [repo](https://github.com/open-telemetry/semantic-conventions-genai)
- Browser agents can be invisible: Comet uses no distinct user-agent string, so Amazon could not tell when the assistant was involved, per a law-firm summary of the Ninth Circuit opinion. — [Troutman](https://www.troutmanprivacy.com/2026/08/ninth-circuit-holds-human-user-not-developer-of-ai-agent-responsible-for-websites-accessed/)
- Web Bot Auth identifies the bot operator by signature (Ed25519 key directory, `Signature-Agent`, RFC 9421 subset); nothing on the page says it proves user authorization. — [Cloudflare docs](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/)
- **Langfuse** [vendor pricing]: Hobby free, 50k units, 30 days; Core $29/mo, 100k units, 90 days; overage $8 per 100k; open source and free to self-host. — [Langfuse](https://langfuse.com/pricing)
- **Braintrust** [vendor pricing]: Starter $0, 1 GB, 10K scores, 14 days; Pro $249/mo, 5 GB, 50K scores, 30 days. — [Braintrust](https://www.braintrust.dev/pricing)

### Inferences
- Visible at the endpoint: client-declared name (forgeable), protocol metadata, tool names and arguments, returned payload, timing, refusals, retry patterns, abandonment after a pending result, and signed operator identity when present. Hidden: the consumer's original wording, the agent's reasoning, competing businesses, what it told its user, whether the user bought. A browser agent may look like an ordinary visitor and never touch the MCP endpoint at all.
- Because of this, "agent satisfaction" cannot be measured directly. Use proxies: a tool call chain ending in a successful action, a repeat call for the same fact (confusion signal), a request for a fact the resource lacks, no-show or cancellation after booking, owner-reported outcome.
- Design recommendation: a first-party event table is the source of truth (`request_id, business_id, client_declared, identity_tier, tool, intent, policy_decision, result_code, resource_version, redacted_args`). Export to OTel and Langfuse (self-hosted, or the $29 tier) if useful. Log `resource_version` on every event, or rollback analysis is impossible. Do not depend on `traceparent` arriving; treat it as a bonus.
- Keep redaction on by default, reflecting the OTel sensitive flag. Store args hashed or tokenized for PII, with a short raw retention, and none for clinics until counsel approves.
- Pair each real-traffic gap with a one-click harness scenario so sparse traces feed the test suite.

### Gaps
- I did not find measured data on how many consumer agents send `clientInfo`, `traceparent` or Web Bot Auth signatures to small-business endpoints. The prototype should measure this.

## How self-improvement actually works in practice, and its safety rails

### Takeaway
Production "self-improvement" at Sierra and Decagon is propose, test against a golden set, and have a human approve. Recursive self-modification remains research. For Legible, separate what can be auto-tuned (presentation) from what only the owner can assert (facts and policy).

### Cited Findings
- **Decagon Duet Autopilot** [announced 9 Jun 2026; vendor claims]: analyzes all interactions, proposes targeted fixes, tests against the originating conversation and a golden set of hundreds, iterates; every change requires human approval, with versioned diffs; any procedure can be marked untouchable. — [Decagon](https://decagon.ai/blog/autopilot)
- Follow-up (9 Sep 2026): reviewers see projected deflection impact, later replaced with measured actuals on the same conversation set; 85% of accepted changes remained in effect after 30 days (Duetbench-2); oversight is said to shift from reviewing edits to setting objectives and thresholds. It does not discuss regression detection or rollback. Its customer quote implies live use by September, so treat Autopilot as shipped to at least some customers by then. — [Decagon](https://decagon.ai/blog/autopilot-in-production). Coverage notes no customers were named at launch. **[snippet-only]** — [RuntimeWire](https://runtimewire.com/article/decagon-duet-autopilot-self-improving-cx-agents)
- **Sierra Insights** [announced at Summit, post dated 5 Nov 2025]: Explorer queries conversations in natural language; Expert Answers drafts knowledge articles from how human agents resolved similar cases; teams edit, approve and publish. No quantitative results. — [Sierra](https://sierra.ai/blog/insights)
- **GEPA** [research, ICLR 2026 oral; in DSPy]: reflective evolution using text feedback from traces, keeping a Pareto frontier. Up to 35x fewer rollouts than a comparison RL method (GRPO), over 10% better than MIPROv2. Validation set drives selection. Docs state no minimum dataset size and give no overfitting warning. — [arXiv 2507.19457](https://arxiv.org/abs/2507.19457); [DSPy](https://dspy.ai/current/api/optimizers/GEPA/overview/)
- **Karpathy autoresearch** (March 2026; about 99k stars): the agent edits one file, trains for a fixed 5-minute budget against a fixed metric (`val_bpb`), keeps or discards; about 12 experiments an hour; humans edit `program.md`. Evaluation code stays fixed. The README gives no benchmark numbers. — [GitHub](https://github.com/karpathy/autoresearch). Community forks retarget it at prompt files. **[snippet-only]** — [skills.sh](https://www.skills.sh/maroffo/claude-forge/autoresearch-prompt)
- **Meta Hyperagents** [research; March 2026, v2 listed 1 Nov 2026]: self-referential agents with an editable meta agent, extending the Darwin Gödel Machine; reports improvement across domains and transfer of meta-level features such as memory and performance tracking. The abstract does not discuss safety; I could not open the full HTML. — [arXiv 2603.19461](https://arxiv.org/abs/2603.19461)
- MCP results for listing and reads now require `ttlMs` and `cacheScope`, a standard freshness hint. — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Moffatt reasoning: customers should not have to cross-check information across a site. — [McCarthy on Moffatt](https://www.mccarthy.ca/en/insights/blogs/techlex/moffatt-v-air-canada-misrepresentation-ai-chatbot)

### Inferences
- "Recursive" is a misnomer for what a trustworthy pilot should ship. Adopt the autoresearch shape: one editable artifact, one fixed evaluator the optimizer cannot touch, keep or discard. Do not adopt Hyperagents-style editing of the improver itself; no evidence supports that in production for this kind of product.
- Design recommendation, two-track change model.
  - **Track A, presentation** (tool descriptions, field ordering, phrasing, examples): optimizer may propose and auto-test; ship after passing gates, reversible, with owner notified only if meaningfully different.
  - **Track B, assertions** (prices, hours, policies, availability, service area): never learned from traces and never auto-applied. A trace can only raise a question to the owner. No agent-supplied string may enter the resource without owner confirmation. This is the direct defense against ASI06 (memory and context poisoning).
- Safety rails, minimum: immutable versioned resource with `resource_version` on every event; one-click rollback; regression set of owner-confirmed facts plus security tests that must not get worse; the evaluator kept outside the optimizer's write access; shadow comparison before release; a rate limit on changes per week; a human gate for any Track B change; automatic rollback on a spike in failures or owner complaints.
- Stale-fact expiry: every fact carries `source`, `verified_at`, `expires_at`. Suggested defaults: prices 90 days, hours 30 days, promos at stated end, availability live only. On expiry, the resource marks a fact "unverified, confirm with business" rather than serving it as fact. A scheduled one-tap "still right?" prompt is the cheapest high-value feature in this list. Expose `ttlMs` from these values. These durations are judgment calls, unsourced.
- Do not optimize the resource purely against simulator scores: given the documented reward/human misalignment, a resource tuned to a simulator will overfit it (Goodhart). Keep a holdout scenario set and validate with real clients.
- GEPA is appropriate later, since it depends on a stable text-feedback metric; manual reflective edits on the first few failures will teach more at this stage.

### Gaps
- No independent evaluation of Decagon's or Sierra's loops, and neither discloses rollback mechanics in the pages opened.
- I found no published standard for stale-fact handling in agent-facing resources.

## Self-improvement with sparse traffic: cross-tenant learning, vertical templates, and privacy limits

### Takeaway
A plumber might get a handful of agent calls a month, far too few to optimize on. Simulation supplies the volume, vertical templates carry learning across businesses, and only non-content aggregates should cross tenants. With two dozen businesses, even aggregates can re-identify, and health verticals should be excluded.

### Cited Findings
- Decagon's golden set is hundreds of conversations and Sierra's loop mines human agent resolutions, which assume volume long-tail businesses do not have. — [Decagon](https://decagon.ai/blog/autopilot); [Sierra](https://sierra.ai/blog/insights)
- **Clio / Anthropic Insights** (Dec 2024; the page notes an Aug 2026 rename): privacy-preserving analysis through facet extraction with instructions to omit private details, clustering, summarization, and a minimum threshold on unique users or conversations, then a check that summaries contain no identifying details. Threshold value is not stated on the page. — [Anthropic](https://www.anthropic.com/research/clio)
- CNIL (2022): a processor may reuse data for its own purposes only with the controller's written permission, and then becomes a controller for that use. The guidance notes improvements may not benefit the customer whose data was used. **[snippet-only]** — [IAPP](https://iapp.org/news/a/cnil-sets-parameters-for-processors-reuse-of-data-for-product-improvement); [Goodwin](https://www.goodwinlaw.com/en/insights/blogs/2022/01/cnil-sets-parameters-for-processors-reuse-of-data-for-product-improvement)
- One firm's March 2026 opinion concludes an Art. 28 processor cannot rely on legitimate interest to fine-tune an LLM on client data. Single-firm view, low authority. **[snippet-only]** — [opinion PDF](https://docs.google.com/document/d/1D3jVVQLLaSgXXqvUGWEpoqeMYjOFwBe-/export?format=pdf)
- Washington's My Health My Data Act covers non-HIPAA health data, reaches small businesses (from 30 Jun 2024) and processors including out-of-state, with AG and private enforcement through the Consumer Protection Act; inferences about health from non-health data count. — [WA AG](https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy)

### Inferences
- Design recommendation, a three-tier data boundary:
  - **Global (shared):** vertical templates, intent lists, tool-description patterns, scenarios. Authored by Legible or derived from synthetic simulation only.
  - **Aggregate (shared, opt-in, contract-covered):** counts only, such as "% of plumbers failing `service_area` intent". No free text. Suppress below a minimum number of businesses in a cell; in a 24-business pilot, most cells will be below any sensible threshold, so treat this tier as largely inactive.
  - **Tenant only:** all trace content, facts, consumer data. Health verticals remain here without exception.
- Learning loop: improve template-level presentation (Track A) using simulation runs across a vertical's businesses, then promote through the regression suite. Each business then gets the benefit with no data shared, because synthetic data carries the learning.
- With only 3–5 businesses per vertical, an aggregate could tell a competitor something identifiable. Local competitors in one pilot cohort is a concrete re-identification risk, and a reason not to share by vertical-and-city.
- Say so in the pilot agreement. An owner's first question will be whether their data helps a competitor, and a plain no is a selling point.

### Gaps
- I found no 2026 regulator guidance directly on cross-tenant model improvement, and no empirical work on minimum viable traffic for per-business optimization.

## Security threats, real incidents, guidance, and minimum controls

### Takeaway
Injection runs in both directions and no filter fully stops it. The durable defense is architectural: keep the request path deterministic, keep prices and policy in code, and treat all text from agents, scraped pages and reviews as untrusted data. A small team's first controls are identity tiers, per-requester velocity limits, tentative holds, and tenant isolation.

### Cited Findings
- **Lethal trifecta** (Willison, 16 Jun 2025): private data + untrusted content + external communication is dangerous, and no method reliably prevents exploitation; 95% is a failing grade. — [Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- **Agents Rule of Two** (Meta, 31 Oct 2025): no more than two of [A] untrusted inputs, [B] sensitive access, [C] external action in a session; if all three, require supervision or split sessions. — [Meta](https://ai.meta.com/blog/practical-ai-agent-security/)
- **OWASP Agentic Top 10** (9 Dec 2025): ASI01 Goal Hijack, ASI02 Tool Misuse, ASI03 Identity and Privilege Abuse, ASI04 Supply Chain, ASI05 Unexpected Code Execution, ASI06 Memory and Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation, ASI10 Rogue Agents. — [OWASP date](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/); [item names via Modulos](https://docs.modulos.ai/frameworks/owasp-top-10-agentic)
- **OWASP MCP Top 10** [Beta]: MCP01 Token Mismanagement, MCP02 Scope Creep, MCP03 Tool Poisoning, MCP04 Supply Chain, MCP05 Command Injection, MCP06 Prompt Injection via Contextual Payloads, MCP07 Insufficient AuthN/AuthZ, MCP08 Lack of Audit and Telemetry, MCP09 Shadow MCP Servers, MCP10 Context Injection and Over-Sharing. — [OWASP](https://owasp.org/www-project-mcp-top-10/)
- **MCP security best practices** (2026-07-28 version): token passthrough forbidden; state handle hijacking (possession of a handle is not authentication; bind to the verified user, use random, expiring handles); scope minimization; confused deputy; SSRF; Client ID Metadata Document trust policies. — [MCP](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
- **In the wild, Unit 42** (3 Mar 2026): 22 techniques observed; top intents include irrelevant output 28.6%, data destruction 14.2%, moderation bypass 9.5%; delivery by visible plaintext 37.8%, HTML attribute cloaking 19.8%, CSS suppression 16.9%. Examples: forced purchases and payment links, and **myshantispa.com hiding text to force positive spa reviews**. Recommends human confirmation for payments and hidden-text checks in review pipelines. — [Unit 42](https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/)
- **In the wild, Google** (23 Apr 2026): Common Crawl scan of 2–3 billion pages a snapshot, excluding most social media; malicious prompts up 32% between Nov 2025 and Feb 2026; sophistication low; expected to grow. — [Google](https://blog.google/security/prompt-injections-web/)
- **Consumer-agent vulnerability, Magentic Marketplace** (Microsoft, Oct 2025): severe first-proposal bias with a 10–30x speed advantage over quality; 80–100% accepted the first proposal; with fake reviews, awards and injection, some models resisted all and others had all payments redirected; more search results reduced welfare. — [Microsoft](https://www.microsoft.com/en-us/research/publication/mage/)
- **Incidents, MCP**: GitHub MCP issue-to-private-repo leak (May 2025); Asana cross-organization isolation flaw (Jun 2025); malicious Postmark MCP copying outbound email (Sep 2025); Smithery path traversal exposing a token for 3,000+ apps (Oct 2025); fake Oura MCP spreading malware via registries (Feb 2026); nginx-ui CVE-2026-33032 with auth skipped for command execution (Mar 2026). — [AuthZed timeline](https://authzed.com/blog/timeline-mcp-breaches)
- **Supabase** (16 Sep 2025): read-only mode, scoped projects and tool groups help, but injection can still expose data in read-only mode; classifiers reduce and do not remove risk; guardrails alone are insufficient, so pair with environment separation; cites CaMeL. — [Supabase](https://supabase.com/blog/mcp)
- **Price manipulation**: Chevrolet of Watsonville's ChatGPT bot agreed to a $1 Tahoe in Dec 2023 ("legally binding" text prompted by the user). The deal was not honored and the bot was shut down. — [AIID](https://incidentdatabase.ai/reports/3534)
- **Impersonation**: A2A offers Signed Agent Cards (RFC 8785 plus JWS), with clients to fail if verification fails. — [A2A v1](https://a2a-protocol.org/latest/whats-new-v1/). Web Bot Auth proves operator, not user consent; Cloudflare does not validate nonces, so short expiry is the replay defense. — [Cloudflare docs](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/). MCP says user identification must not be client-asserted. — [elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)
- **Slot exhaustion**: OWASP lists Denial of Inventory (OAT-021) for tying up goods or services without completing the transaction. Page could not be opened; definition from prior knowledge. — [OWASP Automated Threats](https://owasp.org/www-project-automated-threats-to-web-applications/)

### Inferences
Threat map for Legible:
- **Inbound (malicious agent attacks Legible).** If an LLM sits on the request path with calendar and customer data, Legible has the full trifecta and fails the Rule of Two. Design recommendation: make the public endpoint a deterministic API, with no LLM in the privileged path, so a hostile string has nothing to hijack. Injection risk then moves to the places an LLM does read that text: trace mining, owner-inbox summaries, gap classification. Run those in a quarantined context with no tools, and a schema-constrained output.
- **Outbound (business content poisons consumer agents).** Legible would republish scraped reviews and captions, making it a vector, and any injection would carry the owner's brand. On ingest, strip hidden text, zero-width characters and CDATA; store as structured fields; quote reviews as attributed data; do not pass through free-form HTML. Scan continually with Promptfoo-style `rag-poisoning` checks. Note the Unit 42 spa example was a business doing this to itself, so owner-supplied text gets the same treatment.
- **Price and discount manipulation.** Prices come only from the resource; the LLM cannot compute or quote a figure not in a table. Discounts always go through policy. Every quote carries version, expiry and "subject to confirmation".
- **Slot exhaustion.** Tentative holds with short TTLs; limit active holds per identity, per contact and per business; verify the consumer contact before a hold on high-value slots; a deposit option for repeat offenders; burst alert to owner; a kill switch per business.
- **PII exfiltration.** Never return customer records to an agent. Availability returns slots, not who holds them. Tenant ID derived from the token or route, enforced at the database layer (row-level security), and Asana-style isolation tests in CI with `bola` and `cross-session-leak`.
- **Agent impersonation.** Identity tiers: anonymous (read public facts), signed operator (higher limits), verified user (OAuth or signed mandate, may request actions). Do not grant anything on the basis of `clientInfo` or user-agent.
- **Scraping.** Public facts are meant to be read, so serve them cached and cheap; rate-limit behind a CDN; separate read and action budgets.
- **Business-side first-proposal bias**: response speed may matter more than quality to consumer agents, which argues for fast static facts and fast "pending" replies. This is both a growth lever and a manipulation risk if rivals game speed.

**Minimum viable controls for the pilot** (judgment, ordered):
1. Deterministic policy and pricing outside the LLM.
2. Tenant isolation at the data layer, tested in CI.
3. Per-IP, per-identity, per-tool and per-business limits; a separate low cap for write actions.
4. Holds with TTL and per-identity caps.
5. OAuth for action tools with narrow scopes, audience validation, no token passthrough.
6. Random, expiring, caller-bound handles.
7. Ingestion sanitizer for scraped content.
8. Structured approval cards with no raw agent text.
9. Append-only audit log and a per-business kill switch.
10. Weekly automated red-team run and a dependency pin plus review for MCP packages, given the Postmark and Oura supply-chain cases.

### Gaps
- OAT-021 text and HHS guidance could not be opened in this session.
- I found no public incident specific to fake-agent booking exhaustion at a small business; the risk is inferred from general patterns.
- Published rate-limit thresholds for agent endpoints were not found; numbers must be set from pilot traffic.

## Legal and trust issues (flag for counsel; not legal advice)

### Takeaway
Businesses are likely to answer for what their agent-facing resource says, and Moffatt is the reference point although it is a small-claims tribunal decision. *Amazon v. Perplexity* helps user-directed agents on computer-access law, but its reasoning relies on facts that may not cover Legible's own server-side scraping. Consent, health data and multi-party liability allocation need counsel before the pilot starts.

### Cited Findings
**Liability for misstatements**
- *Moffatt v. Air Canada*, 2024 BCCRT 149 (commentary dated 19 Feb 2024): liable for negligent misrepresentation; the chatbot was part of the website, not a separate entity; customers should not have to cross-check pages; Air Canada did not appear to rely on disclaimer terms and gave no evidence about how the bot was built or tested. — [McCarthy](https://www.mccarthy.ca/en/insights/blogs/techlex/moffatt-v-air-canada-misrepresentation-ai-chatbot). Award C$650.88 plus interest and fees; tribunal decision, not binding. **[snippet-only]** — [CanLII, unopened](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html)
- The Chevrolet case shows the opposite outcome in practice, with no enforcement of a $1 deal, but it was not adjudicated. — [AIID](https://incidentdatabase.ai/reports/3534)

**Agent-to-agent contract formation**
- UETA §14 lets contracts form by interaction of electronic agents even if no individual reviewed them; §9 attributes an agent's acts to the person it is attributable to; error provisions may protect individuals when no correction mechanism is offered. Commentary only, no case applying these to AI agents found; liability for erroneous orders is called unresolved. **[snippet-only]** — [Tish Law](https://tish.law/blog/can-an-ai-agent-bind-your-company-to-a-contract-apparent-authority-in-the-age-of-autonomous-ai/); [Promise Legal](https://blog.promise.legal/ai-agent-legal-liability-contracting-authority/)

**Amazon v. Perplexity (Comet), No. 26-1444**
- 4 Aug 2026: Ninth Circuit vacated the preliminary injunction. The user, not Perplexity, accesses Amazon's systems under CFAA and CDAFA; the assistant is a tool. The court relied on Comet using the user's own browser, with Perplexity's servers never contacting Amazon's directly, and applied lenity. — [Jones Day](https://www.jonesday.com/en/insights/2026/09/ninth-circuit-vacates-cfaa-injunction-against-perplexitys-comet-ai-agent); [Troutman](https://www.troutmanprivacy.com/2026/08/ninth-circuit-holds-human-user-not-developer-of-ai-agent-responsible-for-websites-accessed/); [PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/ninth-circuit-narrows-cfaa-reach-in-perplexity-agentic-commerce-ruling/)
- Left open: different facts or more developer control, and breach of contract, unfair competition, tortious interference and state consumer claims. — [Troutman](https://www.troutmanprivacy.com/2026/08/ninth-circuit-holds-human-user-not-developer-of-ai-agent-responsible-for-websites-accessed/)
- Status: the March 2026 preliminary injunction was vacated and the case remanded. — [Pearl Cohen, 31 Aug 2026](https://www.pearlcohen.com/ninth-circuit-vacates-injunction-against-perplexitys-ai-shopping-agent/). Amazon sought en banc review around 19 Aug 2026. — [Law360](https://www.law360.com/cases/69b1ed14972d406710e45f2d/articles). Rehearing was denied 10 Sep 2026 with no judge requesting a vote, per one blog updated 22 Sep 2026. — [NoHacks](https://nohacks.co/blog/amazon-perplexity-cfaa-agent-visitor-rights). An amended complaint on 21 Sep 2026 aimed at the iOS app, with the case active in district court, appeared only in a search-tool summary; no page I opened confirms it, so counsel should check the docket. **[snippet-only]**

**Scraping and platform terms**
- *Meta v. Bright Data* (N.D. Cal., Jan 2024): no breach from logged-off scraping of public data; logged-in scraping not addressed, and the ruling is specific to Meta's terms. **[snippet-only]** — [FBM](https://www.fbm.com/post/102kqw7/)
- *Google v. SerpApi* (22 Jul 2026 report): DMCA §1201 claims dismissed; search-result claims without leave to amend, knowledge-panel claims with leave. The court agreed spoofing fingerprints, rotating IPs and solving CAPTCHAs is circumvention, though only actionable where the barrier protects copyrighted works with holders' permission. — [SE Roundtable](https://www.seroundtable.com/google-lawsuit-serpapi-dismissed-41731.html). Amended complaint 10 Aug 2026 and parallel *Reddit v. SerpApi/Perplexity* ongoing. **[snippet-only]** — [Parallel](https://parallel.ai/articles/is-scraping-google-legal)

**FTC**
- Reviews Rule (effective 21 Oct 2024; staff Q&A Nov 2024): a business putting testimonials on its own site is disseminating, not hosting, and could be liable if false; non-representative reviews in marketing could be deceptive; ranking by helpfulness is not suppression; civil penalties for knowing violations. — [FTC](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers)
- FTC chatbot guidance (Fenwick, 11 Jul 2024): do not misrepresent capabilities; mitigate harmful output including hallucinations; outputs must be true in practice; disclose AI. — [Fenwick](https://www.fenwick.com/insights/publications/ftc-outlines-five-donts-for-ai-chatbots). The FTC reportedly walked back Rytr, and a March 2026 policy statement appears in low-quality sources I could not verify. **[snippet-only]** — [Mondaq](https://www.mondaq.com/unitedstates/new-technology/1750930/the-ftc-walks-back-its-rytr-enforcement-action-signaling-a-shift-in-federal-ai-regulation)

**Privacy**
- CCPA ADMT rules: compliance date 1 Jan 2027; human involvement means a reviewer can understand and evaluate the output and change the final decision. Coverage thresholds are not on the page opened. — [NatLawReview](https://natlawreview.com/article/cppa-finalizes-ccpa-regulations-automated-decision-making-technology-risk)
- EU AI Act: provisional Omnibus deal (7 May 2026) keeps Article 50 transparency for deployers from 2 Aug 2026; Art. 50(2) provider marking moves to 2 Dec 2026; not finally adopted at that date, and I did not confirm later adoption. — [JD Supra](https://www.jdsupra.com/legalnews/eu-legislators-agree-to-delay-for-high-5617765/)
- GDPR processor reuse: see the CNIL finding in the sparse-traffic section. **[snippet-only]** — [IAPP](https://iapp.org/news/a/cnil-sets-parameters-for-processors-reuse-of-data-for-product-improvement)
- HIPAA: a cash-only med spa with no standard electronic transactions may fall outside HIPAA, but it depends on the facts; vendors handling PHI need a BAA first. Mostly vendor sources. **[snippet-only]** — [Accountable](https://www.accountablehq.com/post/hipaa-requirements-for-med-spas-a-practical-compliance-checklist). HHS cloud guidance could not be opened (403). — [HHS, unopened](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html)
- Washington MHMDA applies to non-HIPAA health data including small businesses and processors. — [WA AG](https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy)

**TCPA and messaging**
- FCC "revoke-all" rule (47 CFR 64.1200(a)(10)) delayed by a 6 Jan 2026 order to 31 Jan 2027; FCC is considering changes. — [Burr & Forman](https://www.burr.com/telephone-consumer-protection-act/the-fcc-delays-effective-date-of-tcpa-revoke-all-rule-until-january-31-2027). Revocation by any reasonable method still applies. **[snippet-only]** — [JD Supra](https://www.jdsupra.com/legalnews/the-fcc-delays-effective-date-of-tcpa-3491538/)
- Twilio's contract terms independently require express consent, opt-out and sender ID. — [Twilio](https://www.twilio.com/en-us/legal/messaging-policy)

### Inferences
Issues to put to counsel, with the design posture I would adopt meanwhile:
1. **Who is liable for a misstated price or policy: the business, Legible, or the consumer agent's maker?** Moffatt suggests the business faces the customer first, so expect owners to ask Legible to stand behind it. Posture: owner reviews and confirms each fact; every fact carries provenance; pilot terms allocate responsibility; keep the audit log. Moffatt's disclaimer point was not tested, so do not rely on a disclaimer alone. The absence of evidence about testing there is a reason to keep test records.
2. **Is a business bound by what the resource tells an agent?** Under §14-style commentary, possibly yes. Posture: label non-allow actions as *requests*, not confirmations; separate quote, hold and confirmed states in the API; include "binding only on confirmation" terms in the tool response; have allow-rule bookings be understood as real commitments the owner opted into.
3. **Does the owner's approval create the contract, and on what terms?** The approval card should show exact terms, with a signed receipt.
4. **Scraping on behalf of an owner.** The Comet reasoning rests on the user's own browser and no vendor-server contact. Legible's servers fetching Instagram would be the opposite pattern, so the ruling may offer little cover. Posture: use owner-authorized official APIs or owner exports; do not use the owner's login for automated access; do not use IP rotation or CAPTCHA solving, given the SerpApi court's view of those as circumvention. Have counsel read Instagram's current terms directly.
5. **Consumer agents visiting owner sites.** After Perplexity, CFAA is a harder route for anyone wanting to block them, and contract theories remain. This is a minor issue for owners, since they want the traffic.
6. **Reviews.** If Legible selects or summarizes reviews for agents, that may be dissemination, and a positive-only selection may be deceptive. Posture: show representative samples, include rating counts, attribute the source; never generate reviews.
7. **Health verticals.** Consider excluding clinics and med spas from the first cohort, or restrict them to public facts with no consumer data, until a BAA chain (Legible to LLM vendor to SMS vendor) and MHMDA review are done. Note SMS alerts could carry PHI if careless.
8. **SMS consent.** Owner alerts: record opt-in at onboarding. Consumer status texts: consent captured from an agent on a consumer's behalf is a novel problem, because Twilio bars consent obtained on someone else's behalf, and whether an agent's relay counts needs a legal answer. Until then, prefer status URLs for consumers over outbound texts.
9. **AI disclosure and ADMT.** Disclose that requests are handled by automation. Keep the human-approval path meaningful so it satisfies a "can change the final decision" standard; bookings seem unlikely to be "significant decisions", but ask, especially for healthcare-adjacent services.
10. **Data roles and cross-tenant use.** Decide controller or processor explicitly and write it into the terms. The conservative pilot posture is no cross-tenant use of trace content.

### Gaps
- I did not obtain the Ninth Circuit opinion, CanLII decision, or statutory UETA text; only law-firm summaries. Primary reads belong to counsel.
- WSGR's alert returned 403.
- Instagram's current terms could not be retrieved, so nothing here characterizes them.
- *McLaughlin Chiropractic v. McKesson*, the FCC's AI-voice ruling, the current TCPA treatment of business-mobile numbers, and CCPA thresholds for small businesses were not verified; search was exhausted before I could reach them.
- I found no authority on whether an agent can validly relay a consumer's SMS consent, and no regulator guidance for agent-to-agent consent.
