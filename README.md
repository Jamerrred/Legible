# Legible

**Make any small business readable to AI agents.**

AI agents already shop for people, but they often can't finish the job on a small business's website. Prices are in images, rules are buried, and the agent gives up or guesses.

Give Legible a website. It reads the site, works out what's missing, asks the owner, and publishes a small page that any AI agent can read and act on. The owner runs it all from one simple app, and only facts they've confirmed ever go public.

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

This takes about 5 minutes. Everything runs on your own computer, and you don't need a Cloudflare account.

### 1. Install what you need

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**, which runs the Python code and installs Python 3.12 and its dependencies.
- **[Node.js](https://nodejs.org)**, version 20 or newer, which runs the public page locally.

### 2. Download the code

```bash
git clone https://github.com/Jamerrred/Musefront.git legible
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

Then open `.env` and fill in the keys you need:

| Key | What it's for | Needed for | Where to get it |
|---|---|---|---|
| `OPENROUTER_API_KEY` | The AI model behind every agent | The app and running the experiment | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `EXA_API_KEY` | Reads websites and runs Errand's web searches | The app. Not the experiment, which searches a saved local copy | [dashboard.exa.ai](https://dashboard.exa.ai) |
| `COMPOSIO_API_KEY` | Lets owners connect accounts such as Google Calendar | Optional, and not yet tested with a real key | [composio.dev](https://composio.dev) |
| `LEGIBLE_ADMIN_TOKEN`, `LEGIBLE_EDGE_URL` | The private link between the app and the public page | Leave these alone: `scripts/start.py` fills them in | |

Re-checking the saved results and running the tests need no keys at all.

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

### Run it again (spends OpenRouter credit)

All 12 questions on all three versions should cost about $5, at the rates we saw. You only need `OPENROUTER_API_KEY`.

**1. Start the local sites** in one terminal, and leave it running:

```bash
uv run python scripts/serve.py
```

| Address | What it is |
|---|---|
| `http://cormorant.localhost:8101` | "Before": the website alone |
| `http://cormorant.localhost:8102` | "After": the same website plus one link line |
| `http://agents.cormorant.localhost:8103` | The hand-written page for agents |
| `http://cormorant.localhost:8104` | Control: a plain page holding the same facts, to show what Errand can do with nothing in its way |

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
uv run python -m errand.run --task "What does a full detail cost at Cormorant Mobile Detailing?" --search local --corpus corpus/after --out runs/adhoc
```

### How it was kept fair

- **One change:** "before" and "after" differ only by the link line.
- **Frozen agent:** Errand knows nothing about Legible or the business, and its behaviour hasn't changed since the tag `first-demo-agent-freeze`, set before any benchmark run. It was later renamed from `consumer_agent/`, which changed only module names in comments and in a test helper. To see that yourself:

  ```bash
  git diff first-demo-agent-freeze:consumer_agent HEAD:errand
  ```

- **Blind writing:** the questions were written from the facts alone, without knowing what the site hides, and the page's author never saw the questions.
- **Graded in code:** each answer is checked against [`bench/queries.json`](bench/queries.json).

## Run Legible

```bash
uv run python scripts/start.py
```

The first start takes a minute. It opens the app at **http://127.0.0.1:8200**. Keep that terminal open while you use it, and press `Ctrl+C` to stop.

The sidebar follows the order an owner works in, so go through it from top to bottom:

**1. Websites: connect a website.** Paste an address and press the arrow. You can use your own, or this fictional demo business, which has prices hidden in images and missing rules on purpose:

```text
https://cormorant-detailing.jamerrred-audiobooks.workers.dev
```

Leave "Also test it with 5 customer agents" ticked to see the full flow. That takes about 5 minutes and costs about $1.50. Untick it for a quick try, which takes about a minute and costs a few cents.

**2. Resource: confirm the facts.** Check what Legible read from the site and press **Confirm all**. Nothing is public until you do. **What agents see** then shows your page exactly as agents read it.

**3. Simulations: fill in what's missing.** Answer the questions, and each answer goes straight onto your page. Then press **Run check** to see how test customers do now.

**4. Resource: change something.** Type this into the box at the bottom:

```text
We're closed for the next 2 days
```

Legible works out the exact dates and asks you to confirm, and the closure ends by itself when the dates pass. You can also click any line or price to edit it, and undo with the version button at the top.

**5. Websites: copy your link.** This is the link a real business would put on its website.

**6. Inbox and Bookings: act like an agent.** Open your link and use its **Ask** and **Request** pages. The question shows up in **Inbox** and the request in **Bookings**. Answer or accept them, then open the status link to see your reply.

To watch the whole product run by itself, with a script playing the owner, start Legible and run this in another terminal. It costs a few cents and only makes sense with the demo business above:

```bash
uv run python scripts/mvp_demo.py --url https://cormorant-detailing.jamerrred-audiobooks.workers.dev
```

### Connect accounts (optional)

To let owners connect accounts such as Google Calendar and Google Sheets through Composio, add `COMPOSIO_API_KEY` to `.env` and restart. Then go to **Websites**, press **Connect a resource**, and follow the popup. Legible reads what you connect and proposes changes for you to confirm.

## Record a demo

A private demo copy plays the whole flow back in about a minute, with no AI credit. Crawling, questions and test customers are scripted from a real crawl and the demo business's facts. Publishing is real, so the public page and its quote, request and ask forms work. It runs separately from your real data:

```bash
LEGIBLE_DEMO=1 LEGIBLE_DB_PATH=legible/demo.db uv run uvicorn legible.api:app --port 8300
```

Open `http://127.0.0.1:8300`. To start a new take, open `http://127.0.0.1:8300/demo/reset`. If you show this to others, say it's sped up with sample data.

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
| `Is another program using that port?` | Close the other program, or use another port: `LEGIBLE_PORT=8300 uv run python scripts/start.py` |
| The website shows "couldn't be read" | Check your Exa key, or try another address. Sites that block automated visitors can fail |
| A test customer says "Agent crashed" | The AI provider returned an error. It doesn't count against the business, so run the check again |
| You want to start over | Stop Legible and delete `legible/legible.db` |

## Limits

- **Real agents are untested.** Whether agents such as Muse follow the link is still an open question, because the test ran on localhost with a stand-in.
- **It's a prototype.** The app has no login, so keep it on your own computer.
- **Pages are local by default,** so outside agents can't reach them. To put them online, deploy `edge/` to Cloudflare with `npx wrangler deploy`, then set `LEGIBLE_EDGE_URL` and the Worker's `ADMIN_TOKEN` secret.
- **The businesses in the demo are fictional.**

## Learn more

- [Experiment results](reports/first-demo-benchmark.md) and [how they were built](reports/first-demo.md)
- [How the Legible app was built and tested](reports/legible-mvp.md)
- [Decisions, research and plan](docs/README.md)
- [How to work in this repository](CLAUDE.md)
