# Build plan

*Last updated 5 November 2026. The first demo covers steps 1 to 4 and the local half of step 5, running locally on one business: see [the report](../reports/first-demo.md). Everything from the real Muse check onward is still to do.*

## The order

The sequence is the founder's, with a control test, a separate query bank and the Muse check added.

| Step | Build | Why it's here |
|---|---|---|
| 1 | First mock business site | Gives the agent something real to hit |
| 2 | Consumer agent | Our stand-in for Muse, Instinct, Grok and search-API agents |
| 3 | Query bank and "before" runs | Proves the roadblocks are real |
| 4 | Hand-written resource | The target output for the back office agent |
| 5 | "After" runs and the real Muse check | The go or no-go test |
| 6 | The other three sites | Proves it's horizontal |
| 7 | Back office agent, end to end | The product |
| 8 | Demo assembly | Turns real runs into a story |
| 9 | MCP and Poppy (optional) | Only if there's a reason by then |

Two pieces get reused:

- **The hand-written resource** becomes the answer key for the back office agent.
- **The consumer agent** becomes the simulator inside the back office agent.

## How the first demo changed this

| Topic | Decision |
|---|---|
| First business | Mobile detailing, as the fictional Cormorant Mobile Detailing in San Francisco |
| Order | Facts file first, then the site, resource and agent. The agent is frozen before any benchmark run |
| Where it runs | Everything is local for now. Exa stays available behind the same search tool for public use |
| The "before" site | Three pages (Home, FAQ, Book), tidy but not highly polished, with facts left out where a real small site would leave them out |
| The "after" site | The "before" site plus a visible link to the resource. Nothing else changes |
| Benchmark queries | About 10, written by a fresh subagent from the facts alone, with the site placement data removed. It saw no site, no resource and no sample queries |
| Sample queries | Used only to check the agent on the control page before the freeze. They're the start of a discovery set, not part of the benchmark |
| Resource | Written from the facts file only, with no discovery findings in this round |
| Profile | Hybrid only so far |

**The real Muse test still needs:**

- **Hosting:** a host that can run a small server, because forms and logs need one. A static-only deploy won't work.
- **Two live versions:** they differ only by the link and the resource. An optional third run gives Muse the resource URL directly, which separates "can't find it" from "can't use it".
- **Clean runs:** fresh chats, a clean account or cleared memory if possible, and several repeats of each query.
- **Who runs it:** the founder, by hand at first, since Muse is logged in on Brave and computer use can't click or type in a browser.

## Step 1: First mock business site

**Build:**

- A [facts file](06-demo-businesses.md#the-facts-file) holding the business's real prices, rules and availability.
- A realistic public website with roadblocks drawn from the [catalogue](05-roadblocks-and-queries.md).
- Request logging from the first day.

**Done when:**

- Every roadblock on the site is listed against its catalogue ID.
- Each fact in the facts file is either present somewhere on the site or deliberately missing, and we've recorded which.
- A person can get through the site's real booking flow.

## Step 2: Consumer agent

**Build** what's described in the [design](08-consumer-agent-design.md): one tool loop, three profiles, browser-use for browser work, a run log and a grader.

**Control test:** run the agent against a plain, clean page holding the same facts. If it fails there, the agent is at fault, so fix the agent.

**Done when:** the agent passes the control page reliably, and its instructions are frozen.

## Step 3: Query bank and "before" runs

**Build:** a query bank written separately from the resource, and tagged by query type and by roadblock. Details are in [the catalogue](05-roadblocks-and-queries.md#the-long-tail-of-queries).

**Run:** every query and profile on the "before" site.

**Done when:** results are recorded and each failure is traced to a named roadblock, not to an agent bug. We read transcripts to check this. A result near 0% usually means a broken task, so we check those first.

## Step 4: Hand-written resource

**Build:** a resource written by Claude from the facts file, following the [resource spec](04-resource-spec.md), plus a small form handler and the link from the site. The back office agent isn't involved yet.

**Done when:** every fact in the resource matches the facts file, and the resource's author hasn't seen the query bank.

## Step 5: "After" runs and the real Muse check

**Run:** the same agent, queries and profiles, on the site with the resource added. Then give the real Muse the "before" and "after" URLs.

**This is the go or no-go test.** It answers two questions:

- Does an unmodified agent follow the link at all?
- Does the resource change the outcome?

**If agents don't follow the link:** try the other signals in the [resource spec](04-resource-spec.md#how-an-agent-gets-to-it) first, such as placing key facts on the site itself. A proxy in front of the site is the fallback for mock sites, and the demo would need to say so on screen.

**Done when:** results show the proposed target of failing before and succeeding after in at least 8 of 10 runs on the demo queries, or we know why not.

## Step 6: The other three sites

**Build** the remaining [demo businesses](06-demo-businesses.md), each with its own facts file, query bank and hand-written resource. Each business exposes different roadblocks.

**The agent doesn't change between businesses.** If a change is truly needed, it's a general fix, and all earlier runs get repeated.

**Done when:** all four have before-and-after results.

## Step 7: Back office agent

The full spec is in [09-back-office-agent.md](09-back-office-agent.md). Suggested order within this step:

| Part | Build | Test |
|---|---|---|
| a | Business record and resource generator | Generated resource carries the same facts as the hand-written one |
| b | Ingestion through Context.dev, plus files | Proposes the right facts from each mock site |
| c | Owner chat and inbox | The owner can confirm, correct and answer |
| d | Plain-language revision | Instruction test set: the right change, a question if unclear, nothing unconfirmed |
| e | Simulator, reusing the consumer agent | Finds gaps we removed on purpose |
| f | Learning from activity | A real dead end becomes an owner question, and its answer reaches the next agent |
| g | Composio connectors | Reads a demo calendar and price sheet. Check coverage first |
| h | Request handling and approvals | A request reaches the inbox, and the owner's reply reaches the status page |

**Done when:** a mock business goes from a raw site to a working resource through the back office agent alone, and the consumer agent passes the same queries as it did on the hand-written version.

## Step 8: Demo assembly

- Record real successful runs, and keep the failure rate from the test runs alongside them.
- Rehearse the [demo story](01-project-overview.md#the-demo-story).
- Say on screen that the businesses are mock and that our agent is a stand-in.

## Step 9: MCP and Poppy (optional)

Add `/mcp` and `/.well-known/poppy.json`, generated from the record. Check Poppy's field names against its validator. Do this only if the back office agent is finished and there's a reason to.

## Test rules

**Proposed, not yet confirmed.** A perfect demo still has to survive the question "would a real agent do this?"

| Rule | What it means |
|---|---|
| Roadblocks live on the website | The agent is never tuned or weakened to make it fail |
| Realistic roadblocks | Each one matches something real sites do, and the catalogue records where evidence exists |
| Same facts | The site and the resource come from the same facts file |
| One change | The only difference between "before" and "after" is the resource and the link to it |
| Frozen agent | Instructions and queries are fixed before the resource exists |
| Full capability | Agent features stay on. For example, browser-use's cross-origin iframe option has to be on and its domain list has to include widget hosts, or booking widgets fail for the wrong reason |
| Control page | The agent must pass a plain page holding the same facts |
| Separate authors | Whoever writes the queries hasn't seen the resource, and the other way round |
| Honest answers count | "This isn't offered" or "I can't tell" is a pass when that's true. A confident guess is a failure |
| Repeat runs | Agents vary, so we report pass rates and don't rely on single runs |
| Real agent check | Real Muse's behaviour outranks our stand-in's |

## What each run counts as a pass

- The answer matches the facts file, or it correctly says the fact isn't available.
- The agent gives a source for each claim.
- It gives no personal details until the simulated person approves.
- If an action was asked for, the request actually appears in the site's log.

## Not being built

- Front desk agent
- Application to Meta's connector program
- Business discovery
- Real businesses or real money
- Full checkout protocols

## What the founder needs to provide

| When | What |
|---|---|
| Done | API keys for OpenRouter and Exa, in a git-ignored `.env` |
| Now | More OpenRouter credit. The first demo used almost all of the $10, and a "before" run costs about $0.26 |
| Before the real Muse check | A host that can run a small server, and a domain or two for the mock businesses |
| Step 5 | Time to run the real Muse on the mock site |
| Step 7 | API keys for Context.dev and Composio, and a demo Google account |

## Open questions

- **Should public mock sites say they're mock?** Public sites with invented prices could mislead a real person who finds them. Proposed: fictional names, no real contact details, `noindex`, and forms that contact no one. A visible "demo" note is safer for people but could change how agents behave, so the founder should choose.
- **Which domains?** A realistic domain helps an agent treat the site as the merchant's own. A shared hosting address might not.
