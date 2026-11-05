# Legible docs

*Last updated 5 November 2026. This folder holds the project's decisions, research and plan. the Legible agent's backend is built as a prototype: see [its report](../reports/legible-mvp.md).*

## Current position

Legible gives a service business a small website that any AI agent can read and act on, plus a Legible agent that keeps it accurate. The goal right now is a working prototype, as fast as possible.

**Done so far:** the first mock business (mobile detailing), its hand-written resource, the consumer agent, a local before-and-after test ([benchmark](../reports/first-demo-benchmark.md)), and the Legible app backend with a public resource on Cloudflare ([report](../reports/legible-mvp.md)).

**Next steps:** the [owner app](10-owner-app.md) is built and runs locally, so next come connecting real accounts through Composio, and 1 or 2 searches on real Muse with and without the resource.

**Skipped on the founder's direction, 5 November:** the 5 missing "before" runs and the other three mock businesses, which wait until the founder asks for them. Whether real agents follow the link is still untested.

## Read these in order

| Doc | What's in it |
|---|---|
| [01 Project overview](01-project-overview.md) | The product, decisions made, what replaced what, parts, demo story, validation status, glossary |
| [02 Muse findings](02-muse-findings.md) | What the founder's Muse test showed, and how far to trust it |
| [03 Build plan](03-build-plan.md) | The step-by-step plan, test rules, and what's needed from the founder |
| [04 Resource spec](04-resource-spec.md) | What the "slug" website contains, how it's written, and how agents reach it |
| [05 Roadblocks and queries](05-roadblocks-and-queries.md) | The long-tail catalogue of what stops agents, query types, and grading |
| [06 Demo businesses](06-demo-businesses.md) | The four proposed businesses, their roadblocks, and the facts file |
| [07 Consumer agent research](07-consumer-agent-research.md) | How research agents, browser agents and harnesses are built, with sources |
| [08 Consumer agent design](08-consumer-agent-design.md) | What we'd build as our stand-in agent, including draft instructions |
| [09 Legible agent](09-legible-agent.md) | Spec for the product's one agent: use cases, limits, and how it learns |
| [10 Owner app](10-owner-app.md) | The five screens, how they map to the API, and who can change what |

Also: [the Muse transcript](reference/muse-transcript.md), unedited. It names real businesses, so don't publish it as is.

## If you're coming from another chat

Older material may say something different. These positions are current:

- **The front desk agent and the connector application are dropped.**
- **MCP and Poppy are optional**, and come only after the Legible agent.
- **The first resource is written by hand**, by Claude. It's the answer key for the Legible agent.
- **The consumer agent, Errand, is ours**, built on a tool loop with browser-use, and it doubles as the simulator. It runs on Muse Spark through OpenRouter.
- **The demo set is four service businesses**, not a car wash, HVAC company and online store.
- **Roadblocks and queries are long-tail.** The van cleaning query is one example only.
- **The earlier in-chat PRD is out of date.** These docs replace it.
- **Exa reads websites**, not Context.dev, with a plain crawl as backup.
- **There's one simulation at onboarding**, then a periodic review of real agent activity. Nothing simulates continuously.
- **Analytics stay minimal:** a feed, a few counts and unmet demand.
- **The resource is served by a Cloudflare Worker,** and the Legible app runs separately.

[01 Project overview](01-project-overview.md#what-replaced-what) has the full list and the reasons.

## Decided or proposed

| Status | Where to look |
|---|---|
| Decided by the founder | [Decisions](01-project-overview.md#decisions) |
| Proposed, awaiting confirmation | [Proposed](01-project-overview.md#proposed-not-yet-confirmed), [Test rules](03-build-plan.md#test-rules), [Open questions](03-build-plan.md#open-questions), and all of docs 06 and 08 |

## Earlier research

| Folder | Status |
|---|---|
| `research_notes/Consumer agents/` | Raw notes behind docs 05, 07 and 08 |
| `research_notes/Agentic commerce for long tail/` | Older notes. `competitors.md` and `harness_inbox_trust.md` were finished, while `protocols.md`, `errands.md` and `connectors_and_delivery.md` may be partial, since those tracks were stopped early |
