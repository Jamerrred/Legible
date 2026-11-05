# Legible

**Make any small business readable to AI agents.**

AI agents already shop for people, but they often can't finish the job on a small business's website. Prices are in images, rules are buried, and the agent gives up or guesses.

Give Legible a website. It reads the site, works out what's missing, asks the owner, and publishes a small page that any AI agent can read and act on. The owner runs it all from one simple app, and only facts they've confirmed ever go public.

## Try it

| You want to | Do this | Keys | Cost | Time |
|---|---|---|---|---|
| See the whole story quickly | [Run the demo copy](#try-the-demo-copy) | None | Free | About 3 minutes |
| Use the real app on any website | [Run Legible](#run-legible) | OpenRouter and Exa | About $2 | About 15 minutes |
| Check our results | [Grade the saved runs](#check-the-saved-results-free-no-keys) | None | Free | Under a minute |

All three start with [Set up](#set-up).

## The result

We built a consumer agent, **Errand**, to act as a customer's assistant, then froze it and pointed it at a fictional business's website, with and without one link to a Legible page.

| On the 7 questions run on both versions | Website alone | With the Legible link |
|---|---|---|
| Correct answers | 3 of 7 | **7 of 7** |
| Runs that needed a browser | 5 of 7 | 0 of 7 |
| Average time per run | 165 s | 32 s |
| Average cost per run | $0.263 | $0.071 |

Errand found and used the page in 6 of the 7 "after" runs without being told it exists.

*Fictional business, stand-in agent built on Muse Spark 1.3, one run per question, run locally. This is not a test of Muse or any other real agent, and it's too small to be a measured rate. The website leaves out 37 of its 75 facts on purpose, so better answers are partly expected. Credit ran out before the other 5 of the 12 questions ran on "before". The [full report](reports/first-demo-benchmark.md) has every answer, weak spot and limit on what you can claim.*

## What's in this repository

| Part | What it is | Where |
|---|---|---|
| **Legible** | The product: the owner app and the agent behind it, which reads the site, builds the fact sheet, asks the owner, runs checks and reviews what agents did | [`legible/`](legible/) |
| **Public page** | The page, quote and booking forms that agents use. It's built from the fact sheet and needs no AI to serve | [`edge/`](edge/) |
| **Errand** | Our consumer agent, a general-purpose assistant built on a tool loop with browser-use. It knows nothing about Legible | [`errand/`](errand/) |
| **The experiment** | The questions, runner and grader, and the fictional business's website, hand-written page and facts | [`bench/`](bench/), [`demo_site/`](demo_site/), [`demo_resource/`](demo_resource/), [`businesses/`](businesses/) |
| **The evidence** | Saved page copies, every run's full log, and the reports | [`corpus/`](corpus/), [`runs/`](runs/), [`reports/`](reports/) |
| **Supporting** | Code the demo shares, launch scripts, tests, deployment, and the decisions and research behind it all | [`legible_core/`](legible_core/), [`scripts/`](scripts/), [`tests/`](tests/), [`deploy/`](deploy/), [`docs/`](docs/README.md), [`research_notes/`](research_notes/) |

The agent changes the fact sheet and never the page, so every part of the page stays consistent. Nothing an outside agent says can change the facts.

## Set up

This takes about 5 minutes. Everything runs on your own computer, and you don't need a Cloudflare account. These steps were tested on macOS.

### 1. Install what you need

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**, which runs the Python code and installs Python 3.12 and its dependencies.
- **[Node.js](https://nodejs.org)**, version 20 or newer, which runs the public page locally.

### 2. Download the code

```bash
git clone https://github.com/Jamerrred/Legible.git legible
```

```bash
cd legible
```

```bash
uv sync
```

Errand sometimes needs a real browser, so install one:

```bash
uv run --with playwright playwright install chromium
```

### 3. Add your API keys

Make your settings file, which git ignores:

```bash
cp .env.example .env
```

Then open `.env` and fill in the keys. You bring your own, and the costs below come out of your accounts:

| Key | What it's for | Needed for | Where to get it |
|---|---|---|---|
| `OPENROUTER_API_KEY` | The AI model behind every agent | The real app, and running the experiment again | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `EXA_API_KEY` | Reads websites and runs Errand's web searches | The real app. Not the experiment, which searches a saved local copy | [dashboard.exa.ai](https://dashboard.exa.ai) |
| `COMPOSIO_API_KEY` | Lets owners connect accounts such as Google Calendar | Optional, and not yet tested with a real key | [composio.dev](https://composio.dev) |
| `LEGIBLE_ADMIN_TOKEN`, `LEGIBLE_EDGE_URL` | The private link between the app and the public page | Leave these alone: `scripts/start.py` fills them in | |

The demo copy, the tests and re-checking the saved results need no keys at all.

## Run Legible

```bash
uv run python scripts/start.py
```

The first start takes a minute. It opens the app at **http://127.0.0.1:8200**, empty and ready for a website. Keep that terminal open while you use it, and press `Ctrl+C` to stop.

This is the real app: it crawls the site, and real AI agents do the work. The **Next** card at the bottom of the sidebar always shows what to do now, so you can simply follow it.

**1. Websites: connect a website.** Paste an address and press the arrow. You can use your own, or this fictional demo business, which has prices hidden in images and missing rules on purpose:

```text
https://sunrise-auto-detailers.jamerrred-audiobooks.workers.dev
```

Leave "Also test it with customer agents" on to see the full flow. That runs 5 agents, takes about 5 minutes and costs about $1.50. Turn it off for a quick try, which takes about a minute and costs a few cents.

**2. Simulations: see what stopped the agents.** Each test customer shows the question it was given, its answer, and where it got stuck. Under **What's missing**, answer each question in your own words, or press **This doesn't apply**.

**3. Resource: confirm the facts.** Check what Legible read from the site. Click any line or price to fix it, then press **Confirm and publish**. Nothing is public until you do.

**4. Simulations: test it again.** Press **Run the check again**. The same kind of customers now use your Legible page, so you can compare the two scores. This costs about $0.40.

**5. Websites: put the link on your site.** Copy your link. It's the one line a real business would add to its website, and **Check it's on your site** looks for it. It won't find it on the demo business, because you can't edit that site, so the Next card keeps reminding you. That's expected.

**6. Inbox and Bookings: act like an agent.** Press **Open the page**, then use its **Ask** and **Request** pages. The question shows up in **Inbox** and the request in **Bookings**. Answer or accept them, then open the status link to see your reply. **Inbox** also lists what agents read, where they hit dead ends and what they wanted.

**7. Resource: change something.** Type either of these into the box at the bottom. Each costs about a cent or two:

```text
We're closed for the next 2 days
```

```text
Change the Class A price of the Skiff to $70
```

Legible works out the exact change and asks you to confirm. A closure ends by itself when its dates pass, and **Undo last change** takes back the last edit. **What agents see** shows your page exactly as agents read it.

A full run through all seven steps should cost about $2, at the rates we saw, and a larger website costs more. The app has no spending limit of its own, so set a credit limit on your OpenRouter key if you want a hard stop.

To add another website at any time, press the Legible logo or **Add a website** in the sidebar.

To watch the whole product run by itself, with a script playing the owner, start Legible and run this in another terminal. It costs a few cents and only makes sense with the demo business above:

```bash
uv run python scripts/mvp_demo.py --url https://sunrise-auto-detailers.jamerrred-audiobooks.workers.dev
```

### Connect accounts (optional)

To let owners connect accounts such as Google Calendar and Google Sheets through Composio, add `COMPOSIO_API_KEY` to `.env` and restart. Then go to **Websites**, press **Connect** beside an account, and follow the popup. Legible reads what you connect and proposes changes for you to confirm. This code hasn't been run with a real key yet, so expect rough edges.

## Try the demo copy

The demo copy plays the same story back in about 3 minutes, with no AI credit and no API keys. It's a separate mode that only runs when you ask for it, and its data stays apart from the real app's. You only need the install steps above.

```bash
uv run python scripts/start.py --demo
```

Open `http://127.0.0.1:8300` and follow the **Next** card. Crawling, questions and test customers are scripted from a real crawl and the demo business's facts. Publishing is real, so the public page and its quote, request and ask forms all work. The sidebar says it's sample data, and **Start over** resets it.

[The walkthrough](docs/11-demo-walkthrough.md) gives every step and what to say, for anyone recording or presenting it.

## Reproduce the experiment

### Check the saved results (free, no keys)

Every run's log is in this repository. These commands grade the saved runs again and print the tables, without calling a model:

```bash
uv run python -m bench.run_benchmark --variant before --name first-demo --regrade
```

```bash
uv run python -m bench.run_benchmark --variant after --name first-demo --regrade
```

```bash
uv run python -m bench.run_benchmark --variant control --name first-demo --regrade
```

```bash
uv run python -m bench.summarize --name first-demo
```

The numbers match the table above. Git will show `runs/first-demo/results_before.json` as changed, because the note on the 5 questions that never ran is reworded. Nothing else in it differs.

The logs use the business's earlier name, Cormorant Mobile Detailing. They're kept exactly as they were recorded, and the grader accepts both names.

### Run it again (spends OpenRouter credit)

All 12 questions on all three versions should cost about $6, at the rates we saw. You only need `OPENROUTER_API_KEY`.

**1. Start the local sites** in one terminal, and leave it running:

```bash
uv run python scripts/serve.py
```

| Address | What it is |
|---|---|
| `http://sunrise.localhost:8101` | "Before": the website alone |
| `http://sunrise.localhost:8102` | "After": the same website plus one link line |
| `http://agents.sunrise.localhost:8103` | The hand-written page for agents |
| `http://sunrise.localhost:8104` | Control: a plain page holding the same facts, to show what Errand can do with nothing in its way |

**2. Run each version** in another terminal. Using a new `--name` keeps the published results as they are. The runner stops starting new runs when your balance falls below $0.30.

```bash
rm -rf logs
```

```bash
uv run python -m bench.run_benchmark --variant before --name my-run --concurrency 2
```

```bash
uv run python -m bench.run_benchmark --variant after --name my-run --concurrency 2
```

```bash
uv run python -m bench.run_benchmark --variant control --name my-run --concurrency 2
```

**3. See the results:**

```bash
uv run python -m bench.summarize --name my-run
```

Results are in `runs/my-run/results_*.json`, with each run's log beside them.

**Expect some differences.** Each question runs once, and the model isn't deterministic. Errand also picks the newest Muse Spark version on OpenRouter, so yours may differ from the 1.3 we used.

To ask Errand one question yourself:

```bash
uv run python -m errand.run --task "What does a full detail cost at Sunrise Auto Detailers?" --search local --corpus corpus/after --out runs/adhoc
```

### How it was kept fair

- **One change:** "before" and "after" differ only by the link line.
- **Frozen agent:** Errand knows nothing about Legible or the business, and its behaviour hasn't changed since the tag `first-demo-agent-freeze`, set before any benchmark run. It was later renamed from `consumer_agent/`, which changed only module names in comments and in a test helper. To see that yourself:

  ```bash
  git diff first-demo-agent-freeze:consumer_agent HEAD:errand
  ```

- **Blind writing:** the questions were written from the facts alone, without knowing what the site hides, and the page's author never saw the questions.
- **Graded in code:** each answer is checked against [`bench/queries.json`](bench/queries.json).

## Test it

These need no keys and cost nothing:

```bash
uv run pytest
```

```bash
uv run ruff check .
```

## If something goes wrong

| What you see | What to do |
|---|---|
| `Add OPENROUTER_API_KEY...` when starting | Fill in your keys in `.env`, then start again |
| `Another program is using port...` | Close the other program, or use another port for the app: `LEGIBLE_PORT=8400 uv run python scripts/start.py` |
| The website shows "couldn't be read" | Check your Exa key, or try another address. Sites that block automated visitors can fail |
| A stage fails with an error from the model | Check your OpenRouter key and balance, then add the website again |
| A test customer says "Agent crashed" | The AI provider returned an error. It doesn't count against the business, so run the check again |
| The demo business's address doesn't load | Run `uv run python scripts/serve.py` and use `http://sunrise.localhost:8101` instead |
| You want to start over | Stop Legible and delete `legible/legible.db`. The demo copy has **Start over** in its sidebar |

## Limits

- **Real agents are untested.** Whether agents such as Muse follow the link is still an open question, because the test ran on localhost with a stand-in.
- **It's a prototype.** The app has no login, so keep it on your own computer.
- **Pages are local by default,** so outside agents can't reach them. To put them online, deploy `edge/` to Cloudflare with `npx wrangler deploy`, then set `LEGIBLE_EDGE_URL` and the Worker's `ADMIN_TOKEN` secret.
- **The businesses in the demo are fictional,** and any match with a real business's name is a coincidence.

## Learn more

- [Experiment results](reports/first-demo-benchmark.md) and [how they were built](reports/first-demo.md)
- [How the Legible app was built and tested](reports/legible-mvp.md)
- [The demo walkthrough](docs/11-demo-walkthrough.md)
- [Decisions, research and plan](docs/README.md)
- [How to work in this repository](CLAUDE.md)
