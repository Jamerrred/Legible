# MuseFront

MuseFront gives a service business a small website that any AI agent can read and act on, plus a back office agent that keeps that website accurate.

**Status:** the first demo is built on one fictional business, Cormorant Mobile Detailing, and is [live on Cloudflare](deploy/workers/README.md). In local runs, on the 7 queries run on both versions, a stand-in agent went from 3 correct to 7 correct after one link to a resource was added. That's a small test, and real Muse is untested: see [the benchmark](reports/first-demo-benchmark.md).

## Quick start

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

`businesses/cormorant/facts.json` is the single source of truth. The site, resource and grader all come from it.

| Folder | What's in it |
|---|---|
| [docs/](docs/README.md) | Decisions, plan and specs. Start with the README there |
| [reports/](reports/first-demo-benchmark.md) | Benchmark results and the build report |
| `businesses/` | One facts file per business |
| `mf_core/` | Reads the facts, works out quotes and open slots, and writes the structured logs |
| `demo_site/` | The three-page website, in "before" and "after" versions. `holes.json` lists its roadblocks |
| `demo_resource/` | The agent-readable resource, with quote, request and question forms |
| `consumer_agent/` | The general stand-in agent. It knows nothing about this project or business |
| `bench/` | Control page, mock web, queries, grader and benchmark runner |
| [deploy/workers/](deploy/workers/README.md) | The Cloudflare deployment and its live addresses |
| `scripts/` | The server launcher and the booking check |
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
