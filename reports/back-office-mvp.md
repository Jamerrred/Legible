# Back office prototype: build report

*Run on 5 November 2026 on the fictional Cormorant Mobile Detailing, using the deployed site without the link. The consumer agent is unchanged since its freeze.*

## The result

**The whole flow works end to end on a deployed site, and the generated resource got 3 of 4 test queries right.** That's one run per query with a scripted owner, so it shows the product works, not how accurate it is.

Live resource: https://musefront.jamerrred-audiobooks.workers.dev/b/cormorant-detailing

## What happened in the run

| Step | Result |
|---|---|
| Read the website | 49 draft facts, in about a minute |
| Interview in the inbox | 12 questions, all answered by the scripted owner, which raised it to 73 confirmed facts |
| First check on the website | 3 of 5 settled, $1.41, about 6.5 minutes. 1 run was missing a fact, and 1 crashed on a provider error |
| Publish and copy-paste link | Live, with a page, markdown and a link line |
| "Closed for the next 2 days" | Proposed with absolute dates, confirmed, shown on the page, then undone and gone |
| Outside agent activity | A quote, a dead end, a question and a booking request all reached the inbox |
| Owner's reply to a booking | Shown on the request's public status page |
| Periodic review | Turned a dead end into "1 agent asked for ceramic coating" |

## The 4-query test

Four queries from the benchmark ran through the frozen agent on the generated resource, on a private preview so they stayed out of activity. The agent was given the resource's address directly, so this doesn't test whether agents follow the link. They cost $0.32.

| Query | Result |
|---|---|
| q01: full detail on an Outback, under $400, Saturday or weekday | Correct |
| q02: all-in price for a muddy F-250 | Correct |
| q03: three vans on a Saturday | Correct |
| q05: clean up vomit in a CR-V | **Wrong.** It said yes, because the record never says the business refuses this |

The hand-written resource got 12 of 12 across all queries, but that isn't a like-for-like comparison.

**Why not to quote 3 of 4 as a rate:**

- It's one run per query.
- The scripted owner knows every fact. A real owner would know them too, but would answer less completely.
- A first run scored 1 of 4. I then widened the interview and fixed a ZIP bug after seeing those failures, so this test no longer has the blind separation the first benchmark had.

## Exa

Exa supplied all the text in this run, but it read the home page twice, added a stray `mailto:` entry, missed `/book` and returned no images. So prices that exist only in an image came from the owner's answers rather than the website.

**Fixed afterwards:** a plain crawl now always fills in what Exa misses. On its own, that crawl step found all 3 pages and both images. The fix hasn't been through a full run yet.

## What was reused from the consumer agent

The OpenRouter client, the Exa client, the page parser and the whole agent as the check, all imported without changes. Nothing in it could build a resource, so the record, generator and inbox are new.

## What this version cuts

- **Quotes:** `/quote` handles base prices, variants, add-ons, fees, tax and zones. Rules like fleet discounts appear as text and aren't calculated.
- **Availability:** stated hours and closures only, until a calendar is connected.
- **Hosting:** the back office runs on the founder's Mac, so its 6-hourly review only runs while the Mac is on. The public resource doesn't depend on it.
- **Login:** the API has none, so it has to stay on localhost.
- **Owner channels:** the API only, with no text or email.

## Known problems

- **Agent crash:** runs that reach the agent's tool limit can end on a provider error with no report. That happened in 1 of 5 checks here. The fix means changing the frozen agent, so it hasn't been made. Those runs are counted separately and don't create owner questions.
- **Composio:** the code has never run, because there's no key yet. Its tool names are unverified.
- **Odd entries:** the model sometimes files rules under "not offered", such as "Odour treatment alone". They read fine, but the record could be tidier.
- **Real agents:** real Muse is untested, and so is whether any real agent follows the link.

## Cost

This session used $5.77 of OpenRouter credit, across three full walkthroughs and a stopped one. $9.44 is left.

## How to run it

See [the README](../README.md#run-the-back-office). [The owner app doc](../docs/10-owner-app.md) maps each screen to its API calls.
