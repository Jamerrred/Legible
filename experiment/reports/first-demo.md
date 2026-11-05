# First demo: build report

*The fictional business was called Cormorant Mobile Detailing when this ran, and it is now Sunrise Auto Detailers. Quotes and names here use the new name. The raw logs in `runs/` keep the old one, unedited.*

*Run on 5 November 2026 (India time), on the fictional Sunrise Auto Detailers, with everything local. The agent was frozen at commit `2c319fc`, tagged `first-demo-agent-freeze`. This report covers what was built, what passed, what failed and how to run it. For the numbers, see [first-demo-benchmark.md](first-demo-benchmark.md).*

## The result

**The resource helped our stand-in agent, but this run is incomplete and too small to trust as a measurement.** OpenRouter credit ran out with 5 of the 12 "before" queries still to run, so the fair comparison covers only 7 queries, each run once.

| On the 7 queries run on every version | Control page | "Before" site | "After" site |
|---|---|---|---|
| Correct, with a source from the merchant | 7 of 7 | **3 of 7** | **7 of 7** |
| Runs that used the browser | 0 | 5 | 0 |
| Average time per run | 29 s | 165 s | 32 s |
| Average cost per run | $0.04 | $0.26 | $0.07 |

Across all 12 queries, "after" got 12 of 12 and the control page got 11 of 12. The agent followed the visible link to the resource in 11 of 12 "after" runs. The twelfth, q08, was answered correctly from the FAQ.

This says nothing yet about real Muse, which can't reach localhost.

The query-by-query results, quotes and chart-ready numbers are in [first-demo-benchmark.md](first-demo-benchmark.md).

## Real holes or agent problems

**Real holes, seen on "before":**

- **Missing facts stopped it (q02, q03, q05):** undefined surcharges (D4), tax and travel fee amounts (E5, C3), fleet terms, and silence on what isn't offered (F6).
- **Image prices slowed it down but didn't stop it:** the browser worker read the price board in q02 to q05. The cost shows in the time and money above, not in the answers.
- **Rules buried in the FAQ didn't stop it (q08, q09):** collapsed answers are still in the HTML, so a plain fetch reads them. That's a limit on this hole, and it may differ for other agents.

**Not tested on "before":** the calendar behind the lead form (G2, H3) and the wrong directory price as a direct question (I1). q10, q11 and q12 are the queries that test them, and they didn't run.

**Agent problems, not fixed because the agent is frozen:**

- **Time limit (q01):** when the run hit its limit, it produced no partial report.
- **Overconfidence (q05):** it treated silence as a yes, though the site's silence is the main cause.

**A facts gap, not an agent bug (control q11):** the facts say hatchbacks are small and sedans are midsize, and don't list the Prius, but `/quote` treats it as midsize. "After" passed q11 because of that mapping. The facts should name it.

**Fixed before the freeze, using sample queries on the control page:** a browser worker that kept hunting for prices after submitting a form, and a provider error that ended a run with no report.

## What passed

- **Site:** rebuilt from scratch as Home, FAQ and Book. The booking check passes on both versions, the link line is the only difference between them, and old URLs return 404.
- **Facts:** 75 facts, each with a confirmation date. On the site, 4 are plain, 34 are hidden and 37 are missing. The holes list has 29 entries tagged with catalogue IDs, kept out of the served pages. Neither placeholder from the side chat appears. I changed a generated $25 generator fee to $30 so it couldn't be mistaken for the placeholder fee.
- **Resource:** written from the facts alone, with all 75 facts present. `/quote` and `/request` were used in real runs: 21 quotes, 6 logged dead ends and 1 request, with a working status link.
- **Personal details:** the two requests sent both had scripted approval, and no run shared contact details without it. Nothing was blocked, so the gate wasn't exercised in the benchmark. A declined approval is still untested.
- **Exa:** a live search through the agent's backend returned 3 results in the same format as local search.

## What failed

- **The 30-minute target:** this took about 95 minutes, including two changes of direction on the site and the credit failure.
- **The first benchmark attempt:** 18 parallel runs exceeded the balance OpenRouter would hold for requests in flight, and most then failed with a 402 error. Those failed runs are excluded. The 18 runs that finished cleanly were kept, and the rest were rerun with lower parallelism. The first attempt's results are in `runs/first-demo/attempt-1-credit-failure/`, and the logs of refused "before" runs are in `runs/first-demo/invalid-runs/`.
- **Finishing "before":** 5 queries didn't run, because the balance fell to $0.21, under the $0.30 floor.
- **Grader bug, now fixed:** a run with no report counted as an honest unknown, which flattered "before". q01 is now graded as gave up.

## What was skipped

- A second repeat of any query.
- Discovery runs on the "before" site, so the resource wasn't informed by any. The sample queries ran only on the control page, before the freeze.
- Every agent profile except the hybrid, and Muse Wonder. Spark did well enough on the control page.
- A full agent run on the live web, including replaying the original van query. Only the Exa search call was tested.
- `/ask` in real runs. No agent used it, so it has only had its author's check.
- Mobbin and pen.dev. The final site is deliberately plain and uses neither.

## Too small to trust

- **Everything here is one run per query.** The "before" comparison rests on 7 queries that weren't chosen at random: they're simply the ones that ran before the money ran out.
- **The site was cut down on purpose.** "Before" leaves out 37 of 75 facts, so its failures partly reflect that choice. They say nothing about how often real sites have these gaps.
- **The time and cost differences** come from a few runs at different parallelism.
- **The link-following rate** may flatter the resource. The agent's instructions tell it to follow links on a business's own site when they look useful, and real agents may not.
- **The checks come from one author.** The same subagent wrote the queries and their regex checks, and I read only some of the passing answers by hand.

**How clean the separation was:**

- The query writer saw only the facts, with placements removed. It saw no site, no resource and no sample queries.
- The resource author and the site's authors were told not to look at the queries, which stayed out of the repo while they worked.
- The facts author never saw the sample queries or the placeholders.
- **One weak spot:** I'd read the queries before the site rebuild. My brief to that author listed categories a small site might leave out, such as tax, fleet terms and the not-offered list, which overlap with what the queries test. The author made the fact-by-fact calls, but the brief could have leaned on them.

## How to run it

Start every server first and leave it running:

```bash
uv run python scripts/serve.py
```

| Address | What it is |
|---|---|
| `http://sunrise.localhost:8101` | "Before" site |
| `http://sunrise.localhost:8102` | "After" site |
| `http://agents.sunrise.localhost:8103` | Resource |
| `http://sunrise.localhost:8104` | Control page |

In another terminal, check the booking flow:

```bash
uv run python scripts/check_booking.py http://sunrise.localhost:8101
```

Re-grade the saved runs and print their tables. Neither of these calls a model, so they're free:

```bash
uv run python -m bench.run_benchmark --variant before --name first-demo --regrade
```

```bash
uv run python -m bench.summarize --name first-demo
```

**The rest spend OpenRouter credit.** Save fresh page copies only if the site has changed, since a benchmark's runs should all use the same copies:

```bash
uv run python -m bench.snapshot before after control
```

Finish the "before" runs. `--resume` keeps every clean run, so this spends only on the missing queries:

```bash
uv run python -m bench.run_benchmark --variant before --name first-demo --resume
```

Run one query by hand on the local web:

```bash
uv run python -m errand.run --task "What does a full detail cost at Sunrise Auto Detailers?" --search local --corpus corpus/after --out runs/adhoc
```

Use `--search exa` for the public web. Results are in `runs/first-demo/results_*.json`, with each run's log beside them. Keep parallelism low on a small balance.

## What real Muse needs next

Real Muse can't reach localhost, so this test needs:

1. **A public deploy or tunnel on a host that can run a small server.** Forms and logs need one, so a static-only host won't do.
2. **Two live versions** that differ only by the link and the resource, on addresses that don't give that away.
3. **An optional third run** that gives Muse the resource URL directly, to separate "can't find it" from "can't use it".
4. **Fresh chats,** with a clean account or cleared memory if possible, and several repeats of each query.
5. **You, running it by hand at first,** since Muse is logged in on Brave. The site's logs then show what Muse fetched.

Public mock sites also need a decision on whether to say they're mock, which is still an [open question](../../docs/planning/03-build-plan.md#open-questions).

## What it would cost to finish

At these rates, about $0.26 per "before" run and $0.12 per "after" run:

- **The 5 missing "before" runs:** about $2.
- **A full second repeat of "before" and "after":** about $4.50.
