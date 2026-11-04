# What we learned from the Muse transcript

*Last updated 4 November 2026.*

On 4 November 2026 the founder asked Muse to find van cleaning with pet hair removal in San Francisco, under $150, within two days. They then asked Muse to explain its process and how businesses could prepare. The [full transcript](reference/muse-transcript.md) is saved separately.

**How to use this document:** treat it as one strong data point. It shows the kinds of failure an agent runs into and how one agent works. The wider set of roadblocks is in [05-roadblocks-and-queries.md](05-roadblocks-and-queries.md).

## The result

Muse used about 10 searches, 3 page fetches, a places lookup and a delegated browser session. It still couldn't verify a price and an open slot for any business.

The most useful moment was a correction. A third-party listing showed one business charging $50–150 for dog hair removal. That business's own site showed a minivan interior from $375 plus $39 for pet hair, or $414. Muse had already passed the wrong price to the founder and had to retract it.

## How Muse says it works

This is Muse's own account, so it may not be accurate.

| Stage | What it does |
|---|---|
| Constraint extraction | Turns the sentence into slots: location, vehicle, service, budget as a total cap, and dates resolved in the service's timezone |
| Planning | Searches memory, loads a skill and connector doc, and writes a short to-do list |
| Query generation | Writes whole-intent queries with synonyms, runs them in parallel, then runs follow-ups per business |
| Filtering | Does the arithmetic (base price plus add-on against the budget) and rejects most candidates here |
| Verification | Uses structured place records, then the merchant's own pages. "Merchant's own site beats aggregator, always" |
| Live availability | Delegates to a separate browser agent with its own Chromium. It gets a self-contained assignment and can't see the chat. The assignment says "check only, do not book/pay, report where you get stuck" |
| Synthesis | Classifies results by evidence quality, not rank: verified and in budget, listed but unverified, verified but over, or a maybe with an unknown variable |

Its tools fall into five groups: search and fetch for reading, a live browser agent for interaction, command-line connectors for structured services, a filesystem and shell, and persistent memory.

## Which routes MuseFront can reach

| Route | Reachable today? | What it needs |
|---|---|---|
| `browser.open` on merchant pages | **Yes, the best way to read** | Facts in plain page text, linked from the merchant's site |
| Live browser agent | **Yes, the best way to act** | A real quote form that needs no personal details |
| `browser.search` index | Maybe | The page has to be in the index, and results can be days old |
| Places lookup | No | It's a third party's database |
| Connectors | No | Would require Meta's approval, which we've dropped from the plan |
| MCP and `poppy.json` | Not today, by Muse's account | Muse would need open-web tooling for them |

## General failure patterns

These are the transcript's specific failures, generalised. Doc 05 extends them across other service types.

| What happened to Muse | The general pattern |
|---|---|
| "Van" means different size tiers on each site | The customer's words don't match the business's categories |
| Pet hair exists only as an add-on | Options depend on other options |
| "Starting at" prices | The real total can't be worked out |
| Vague "excessive hair" surcharges | Conditions that change the price aren't defined |
| Water and power needed at the curb, buried in an FAQ | Deal-breaking requirements are hidden |
| Calendar behind a name, address and phone form | Facts are locked behind lead capture |
| Free-text "desired date/time" box | There's no way to get a structured answer |
| A wrong price on a third-party listing | Outside sources contradict the business, or nothing says which is current |
| Prices crawled days ago | Stale data with no date on it |
| Booking stops at personal details by design | The agent can't go further without the person's approval |

## What this changed in the requirements

- **Quote separate from booking:** a total and open slots need no personal details. Contact details come only at booking, after the person approves.
- **Full totals:** fees and add-ons included. If a total can't be calculated, give a range and say what's still needed.
- **Plain synonyms, defined conditions and listed prerequisites** on every offering where they apply.
- **Looks like the merchant's own:** a subdomain of the business's domain where possible, with the link on pricing and booking pages rather than only in the footer.
- **"Who's submitting" field:** Muse says it won't pose as a human if asked. A form field can capture what server logs can't, with no protocol needed.
- **Demand insights become core:** "lost at the $150–200 price band" is information an owner can't get today.

The [resource spec](04-resource-spec.md) applies these across business types.

## What a business sees today

Muse's account of the traces it left:

| Channel | What the business sees |
|---|---|
| Search queries | Nothing. They go to the search provider |
| Page fetches | A bot-like GET, indistinguishable from a crawler refreshing an index |
| Places lookups | Nothing. They go to the data provider |
| Live browser session | A session that browsed, configured a job and left at the personal-details form. It looks like a human who bounced |

No site was told an agent was acting, or for whom. Muse describes its stance as: being an agent is disclosable by default, and the person's identity is need-to-know only. It says it won't impersonate a human, and it won't send a name, phone or address until a booking needs them and the person approves.

It also separated traffic into tiers. A public catalog would be fetched by Muse and crawlers alike and would look the same in logs. A dynamic quote or availability request is something crawlers generally won't make, so those requests are the meaningful signal of intent.

## Don't over-read it

- **It's self-reported.** An agent can be wrong about its own internals. What it hit on those sites is more reliable than its suggestions, and even that needs testing.
- **One claim conflicts with outside reporting.** Muse says it can't present a signed identity, but [DataDome reported](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/) that Meta began signing a small share of Muse's requests around 12 October 2026. Log signatures if they appear, but don't depend on them.
- **`/.well-known/agent.json` looks like Muse's own suggestion.** It isn't one of the standards we found, and Muse didn't mention Poppy.
- **Some of it is speculation.** The questions invited agreement, and claims like first movers getting "all" the agent demand have no evidence behind them. Its "yes, I'd leave a trace" is hypothetical, because it says it lacks the tooling.
- **MuseFront wouldn't have created a $150 van clean.** Where the real price is $414, it would give a faster, verified answer and show the owner the demand lost on price.

## Testing on Muse directly

Once a mock site is public, give Muse the URL so search indexing isn't a factor, and use the same style of query. Then check:

1. Does it follow the link from the pricing page to the resource?
2. Does it treat the resource as the merchant's own, or as a third party?
3. Does its browser agent use the quote form and report a verified total?
4. Does it answer the "who's submitting" field honestly?

**How to run it fairly:**

- **Two live versions** that differ only by the link and the resource. An optional third run gives Muse the resource URL directly, which separates "can't find it" from "can't use it".
- **Clean runs:** fresh chats, and a clean account or cleared memory if possible, because Muse searches its memory at the start of a task.
- **Repeats:** run each query several times.

Real Muse behaviour outranks anything our stand-in does, because the stand-in is only an approximation.
