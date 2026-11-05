# MuseFront

MuseFront gives a service business a small website that any AI agent can read and act on, plus a back office agent that keeps that website accurate.

**Status:** the back office backend is built as a prototype, and it publishes a public resource to a Cloudflare Worker: see [its report](reports/back-office-mvp.md). It has no interface yet. The first local demo, on the fictional Cormorant Mobile Detailing, is [here](reports/first-demo-benchmark.md). Real Muse is untested.

## Run the back office

Start the API and leave it running, then open `http://127.0.0.1:8200/docs`:

```bash
uv run uvicorn back_office.api:app --port 8200
```

Walk one business through the whole product with a scripted owner. It spends a few cents without the optional flags:

```bash
uv run python scripts/mvp_demo.py --url http://cormorant.localhost:8101
```

Redeploy the public resource after changing `edge/`:

```bash
cd edge && npx wrangler deploy
```

[The owner app doc](docs/10-owner-app.md) maps each screen to its API calls.

## Quick start for the first demo

You need [uv](https://docs.astral.sh/uv/). Install the dependencies and add your keys:

```bash
uv sync
```

```bash
cp .env.example .env
```

Start every local server and leave it running:

```bash
uv run python scripts/serve.py
```

| Address | What it is |
|---|---|
| `http://cormorant.localhost:8101` | The site, "before" |
| `http://cormorant.localhost:8102` | The site, "after", which adds one link line |
| `http://agents.cormorant.localhost:8103` | The resource |
| `http://cormorant.localhost:8104` | The control page, a plain page with the same facts |

Check everything works, with no keys or servers needed:

```bash
uv run pytest
```

```bash
uv run ruff check .
```

Print the benchmark's tables, at no cost:

```bash
uv run python -m bench.summarize --name first-demo
```

[The build report](reports/first-demo.md) has the commands for running the agent and the benchmark. Those spend OpenRouter credit.

## How it fits together

For the first demo, `businesses/cormorant/facts.json` is the single source of truth, and the site, hand-written resource and grader all come from it. The back office never reads that file: it builds its own record from the website and the owner's answers.

| Folder | What's in it |
|---|---|
| `back_office/` | The back office agent and its API: fact sheet, crawl, interview, check, inbox, activity and review |
| `edge/` | The Cloudflare Worker that serves every business's public resource from its published record |
| [docs/](docs/README.md) | Decisions, plan and specs. Start with the README there |
| [reports/](reports/first-demo-benchmark.md) | Benchmark results and the build report |
| `businesses/` | One facts file per business |
| `mf_core/` | Reads the facts, works out quotes and open slots, and writes the structured logs |
| `demo_site/` | The three-page website, in "before" and "after" versions. `holes.json` lists its roadblocks |
| `demo_resource/` | The hand-written resource, with quote, request and question forms. It's the answer key |
| `consumer_agent/` | The general stand-in agent. It knows nothing about this project or business |
| `bench/` | Control page, mock web, queries, grader and benchmark runner |
| `scripts/` | The server launcher, the booking check and the scripted owner |
| `tests/` | Tests for the facts, site, resource and grader |
| `corpus/` | Saved page copies for the agent's local search |
| [runs/](runs/README.md) | Raw run logs and graded results |
| `research_notes/` | Raw research behind the docs |

## Rules that protect the results

- **`consumer_agent/` is frozen** at the tag `first-demo-agent-freeze`, so any remaining runs use the same agent. If you change it, rerun the benchmark and move the tag.
- **"Before" and "after" differ only by the link line.** A test enforces this.
- **Keep the query writer and the resource author separate.** Neither sees the other's work, and the query writer doesn't see the site.

## How we work

Work happens in small commits on a short-lived branch, then a pull request merged into `main` with a merge commit. See [CLAUDE.md](CLAUDE.md).

## Keep this repo private

[The Muse transcript](docs/reference/muse-transcript.md) names real businesses and makes claims about their prices and ratings. Replace those names before making it public.
