# First demo benchmark: before and after

This is the source file for infographics and the demo. Every number comes from real runs, and every quote is copied from a run's final answer.

| | |
|---|---|
| **Business** | Cormorant Mobile Detailing, San Francisco. It's fictional |
| **Agent** | Our stand-in consumer agent, on Muse Spark 1.3 through OpenRouter, using the hybrid profile |
| **Run** | 4 November 2026, Pacific time, entirely on localhost |
| **Agent frozen** | At commit `2c319fc`, before any benchmark run, and unchanged since |
| **"Before" site** | Three pages: Home, FAQ and Book. Of its 75 facts, 37 are missing, 34 are hidden and 4 are plain |
| **"After" site** | The same site plus one visible link line to the resource. Nothing else differs |
| **Repeats** | One run per query per version |

## The finding

**On the 7 queries run on both versions, correct answers went from 3 to 7, and no query got worse.** The agent reached the resource in 6 of the 7 "after" runs without being told it exists, and it never needed the browser. On "before", it needed the browser in 5 of 7 runs.

The direction is clear, but this is a small test on a stand-in agent, not a measured rate. Read [What you can and can't claim](#what-you-can-and-cant-claim) before using these numbers.

## Numbers for charts

**Across the 7 queries:**

| Metric | Before | After | Change | Control page |
|---|---|---|---|---|
| Correct answers | 3 of 7 | 7 of 7 | +4 | 7 of 7 |
| Wrong or no answer | 4 of 7 | 0 of 7 | -4 | 0 of 7 |
| Runs that needed the browser | 5 of 7 | 0 of 7 | -5 | 0 of 7 |
| Browser worker calls | 8 | 0 | -8 | 0 |
| Runs that reached the resource | n/a | 6 of 7 | | n/a |
| Average time per run | 165 s | 32 s | About 5x faster | 29 s |
| Average cost per run | $0.263 | $0.071 | About 3.7x lower | $0.041 |
| Total cost of the 7 runs | $1.84 | $0.50 | | $0.29 |

The control page is a plain page holding the same facts. It shows what the agent can do when nothing is in its way.

**Query by query:**

| Query | What the customer asked | Before | After | Before time | After time | Before cost | After cost | Browser calls, before | Live quotes, after | Reached resource |
|---|---|---|---|---|---|---|---|---|---|---|
| q01 | Inside and out on an Outback with dog hair, under $400, Saturday or weekday? | No answer | Correct | 362 s | 42 s | $0.558 | $0.076 | 2 | 2 | Yes |
| q02 | All-in price for a muddy F-250, outlet 150 feet away | Wrong | Correct | 253 s | 34 s | $0.352 | $0.111 | 3 | 1 | Yes |
| q03 | Who can wash three Transit vans on a Saturday, and for how much? | Wrong | Correct | 229 s | 49 s | $0.331 | $0.119 | 1 | 4 | Yes |
| q04 | Ceramic coating on a new Model Y | Correct | Correct | 124 s | 27 s | $0.265 | $0.077 | 1 | 2 | Yes |
| q05 | Clean up dried vomit in a CR-V | Wrong | Correct | 147 s | 27 s | $0.275 | $0.045 | 1 | 0 | Yes |
| q08 | Interior clean in an underground garage with no outlet | Correct | Correct | 17 s | 21 s | $0.025 | $0.025 | 0 | 0 | No |
| q09 | Cancel or move a booking 36 hours out | Correct | Correct | 26 s | 24 s | $0.033 | $0.046 | 0 | 0 | Yes |

## The four answers that changed

### q05: a confident yes becomes a correct no

This is the strongest demo moment, because the wrong answer would send someone a bill for a job the business refuses.

**Customer:** "My kid got carsick in the back of our CR-V over the weekend and threw up all over the back seat and floor. I cleaned what I could but some of it's still dried on and it reeks. Can Cormorant come clean that up and get the smell out? How much? We're in 94122."

**Correct answer:** no. Cormorant doesn't clean biohazards, which include vomit.

**Before: wrong, 147 s, $0.275**

> Yes — Cormorant can come to you in 94122 for this.

> Cutter $179 + shampoo $75 + odour $90 = $344, or $394 with 2-hour odour

**After: correct, 27 s, $0.045**

> No — Cormorant Mobile Detailing says it will not clean this job up, even though you are in its service area.

**Why it changed:** the site never says what it doesn't do (hole F6). The agent's own overconfidence played a part too, since it treated silence as a yes. The resource states the exclusion.

### q03: the Saturday that can't happen

**Customer:** "We're a small plumbing shop in SoMa, 94103, with three Ford Transit vans in our lot. Looking for somebody in San Francisco who'll come to us and wash the outsides, nothing inside. A Saturday would be best since that's when they're all parked. Who can do that and what's the all-in price?"

**Correct answer:** Cormorant can, at $407.67 with the 10% fleet discount and tax, but fleet jobs run Tuesday to Friday only, and three vehicles need a working spigot within 100 feet.

**Before: wrong, 229 s, $0.331**

> 3 x $139 = $417 all-in for the wash itself, before any multi-car discount.

> Saturday: they work Tuesday to Saturday, closed Sunday/Monday.

**After: correct, 49 s, $0.119**

> Catch on Saturday: 3 vans together counts as a fleet job, and fleet jobs run Tuesday to Friday only. So they cannot do all 3 in one visit on a Saturday.

> 1) All 3 together on a weekday - Tuesday-Friday - $407.67 all-in

**Why it changed:** the site leaves out the fleet discount, the fleet's day rule and tax (holes E10, E5, C3). The resource states them, and `/quote` works out the total. This query also names no business, so the agent found Cormorant through search on both versions.

### q01: no answer becomes an exact budget decision

**Customer:** "Can you work out if Cormorant Mobile Detailing fits my budget? I've got a 2021 Subaru Outback in my driveway in Berkeley, 94704, with an outlet right by it. I want it done inside and out, and my dog sheds on the one spot he sits in on the back seat, so that hair needs dealing with too. I'd much rather do a Saturday but I can't go over $400 all in, tax and everything. Does Saturday work or does it have to be a weekday?"

**Correct answer:** Saturday is over budget at $422.38, and a weekday fits at $395.22.

**Before: no answer, 362 s, $0.558.** Two browser workers used about 5 minutes without finishing, then the run hit its 6-minute limit and produced no report. Don't show this as a site error or an outage: the agent ran out of time, and it should have reported what it had.

**After: correct, 42 s, $0.076**

> Saturday total: $422.38 all-in (Schooner midsize $249 + pet hair $55 + Saturday $25 = $329 taxable + $28.38 tax at 8.625% + $65 East Bay travel, no generator fee because you have outlet). That's $22.38 over your $400 cap.

> Tue-Fri total: $395.22 all-in (same $249 + $55 = $304 taxable + $26.22 tax + $65 travel). Within your $400 cap, by $4.78.

**Why it changed:** on the site, prices are in an image (B2), the Saturday fee is behind the lead form (G2, H3), and the travel fee and tax aren't stated (E5, C3). The resource states them all in text.

### q02: an honest "I can't tell" becomes a number

This is the fairest example, because the agent did its job on both versions and the site was the only limit.

**Customer:** "Need a number from Cormorant Mobile Detailing. Our F-250 has been on job sites all year and the inside is wrecked: mud wall to wall on the floor, and the seats and carpet are grubby enough that they need a real shampoo, not just a vacuum. Don't care about the outside, it's a work truck. It sits in our driveway in Sausalito, 94965, and the nearest outlet is a good 150 feet away. Any weekday works. What's the whole thing going to cost me, tax and all?"

**Correct answer:** $628.76, made up of $289 interior detail, $125 shampoo, $75 heavily soiled surcharge, $30 generator fee, $44.76 tax and $65 travel.

**Before: graded wrong, 253 s, $0.352**

> So verified subtotal is $444 + travel fee (unknown) + possible heavily-soiled extra (unknown) + tax if any (unknown).

**After: correct, 34 s, $0.111**

> Total for your job is **$628.76, tax and travel included**.

**Why it changed:** the site says heavily soiled vehicles "may cost extra" without defining it (D4), and gives no travel fee or tax (E5, C3).

**A note on the grade:** the code graded this "wrong" because the agent reported an answer with no total. Reading it, the answer is honest about each unknown. Call it "couldn't give a total", not a false answer.

## The three that passed on both

- **q08 and q09:** the answers are in the FAQ. Its collapsed answers are still in the HTML, so a plain fetch reads them. On q08, the agent didn't need the resource at all.
- **q04:** both versions correctly said no, but on different evidence.
  - **Before, inferred from silence:**

    > No — Cormorant Mobile Detailing does not list a multi-year ceramic coating for your Model Y.

  - **After, stated by the business:**

    > No — Cormorant Mobile Detailing does NOT do ceramic coating, so they can't do a multi-year ceramic coating on your Model Y.

## What the resource fixed

| Hole on the site | Catalogue ID | Queries | What the resource gave instead |
|---|---|---|---|
| Silence on what isn't offered | F6 | q05, q04 | An explicit not-offered list |
| "May cost extra", never defined | D4 | q02 | Defined conditions and surcharge amounts |
| Tax never mentioned | E5, C3 | q01, q02, q03 | The rate and what it applies to |
| Travel fee shown as a map and "for a fee" | B6, F1, C3, E5 | q01, q02 | ZIP codes and the fee for each zone |
| Fleet discount and day rules left out | E10, E3 | q03 | The discount and the days |
| Saturday fee shown only after the lead form | E8, G2, H3 | q01 | The fee stated up front |
| Prices in an image | B2 | q01 to q05 | Prices in text, and `/quote` for totals. The browser could read the image, so this cost time and money rather than correctness |

## Not part of the comparison

Five queries never ran on "before", because OpenRouter credit ran out. **Don't show these as before-and-after.**

| Query | Tests | Control page | After | After time | After cost | Reached resource |
|---|---|---|---|---|---|---|
| q06 | Will polish remove a deep scratch? (unknown) | Correct | Correct | 28 s | $0.079 | Yes |
| q07 | Cybertruck price (unknown) | Correct | Correct | 40 s | $0.130 | Yes |
| q10 | A directory's wrong price | Correct | Correct | 35 s | $0.113 | Yes |
| q11 | Send a request, after checking with the person | Wrong | Correct | 208 s | $0.509 | Yes |
| q12 | Earliest opening | Correct | Correct | 38 s | $0.069 | Yes |

This means **two holes have no "before" evidence yet:** the calendar behind the lead form and the wrong directory price as a direct question.

**The control failure on q11** came from a gap in the facts, not the agent. The facts don't list the Prius, and they say hatchbacks are small and sedans are midsize, so the control run priced it one class lower than `/quote` does. The request itself went through.

## What you can and can't claim

**Safe to say:**

- "In a local test on a fictional business, a stand-in agent got 3 of 7 customer questions right on the site, and 7 of 7 after we added one link to a resource page."
- "It found and used the resource in 6 of 7 runs without being told it exists."
- "With the resource, it never needed the browser on these 7 questions."

**Say only with the small sample stated:** the time and cost differences. They come from 7 runs per version. Load doesn't explain them, since most "after" runs ran under heavier parallel load than most "before" runs.

**Don't say:**

- That real Muse, or any real agent, behaves this way. Real Muse can't reach localhost and hasn't been tested.
- Any percentage as a general rate, such as "100% accurate" or "130% better". Seven single runs can't support that.
- That real sites fail this often. "Before" leaves out 37 of 75 facts on purpose, the way a small site might.
- That the resource beat the calendar behind the lead form. That wasn't tested.

**What's being tested:** the resource holds facts the site leaves out, so better answers on those queries are partly expected by design. The real evidence is that an unmodified agent found the link, trusted the page and used it to reach exact totals.

**Suggested footnote for any graphic:** *Fictional business, stand-in agent built on Muse Spark 1.3, one run per question, run locally. Not a test of Muse itself.*

## How it was kept fair

- **One change:** "before" and "after" differ only by the link line, which was checked by diffing every page and booking step.
- **Frozen agent:** it knows nothing about this project or business, and its code hasn't changed since the freeze.
- **Blind queries:** a fresh subagent wrote them from the facts alone, without the site placement data. It saw no site, no resource and no sample queries.
- **Blind resource:** written from the facts alone. Its author was told not to look at the queries, which weren't in the repo at the time.
- **The link was the only way in:** the resource isn't in the local search index.
- **Grading:** done in code against each query's checks, and I read every answer quoted here.

**Known weak spots:**

- One run per query, and the 7 weren't chosen at random: they're the ones that ran before the credit ran out.
- The same subagent wrote the queries and their checks.
- I read the queries before briefing the site rebuild, and my brief named categories a small site might leave out, which overlap with what the queries test. A separate subagent made the fact-by-fact decisions.
- The agent's instructions tell it to follow useful links on a business's own site, which may make it more willing than real agents.

## Where the numbers come from

| What | Where |
|---|---|
| Graded results | `runs/first-demo/results_before.json`, `results_after.json`, `results_control.json` |
| Each run's full log | `runs/first-demo/<version>/<query>_r1/` |
| Queries and correct answers | `bench/queries.json` |
| Facts and their placement on the site | `businesses/cormorant/facts.json` |
| Holes on the site | `demo_site/holes.json` |
| Build notes, skipped work and commands | [first-demo.md](first-demo.md) |

Regenerate the tables, at no cost:

```bash
uv run python -m bench.summarize --name first-demo
```
