# MuseFront

MuseFront gives a service business a small website that any AI agent can read and act on, plus a back office agent that keeps that website accurate.

**Status:** the first local demo is built on one fictional business, Cormorant Mobile Detailing. The results and all the commands are in [the report](reports/first-demo.md). The back office agent and the real Muse test aren't done yet.

## Where things are

| Folder | What's in it |
|---|---|
| [docs/](docs/README.md) | Decisions, plan and specs. Start with the README there |
| [reports/](reports/first-demo.md) | Benchmark results and how to run everything |
| `businesses/cormorant/facts.json` | The single source of truth for the site, resource and grader |
| `mf_core/` | Reads the facts, works out quotes and open slots, and writes the structured logs |
| `demo_site/` | The three-page website, in "before" and "after" versions. `holes.json` lists its roadblocks |
| `demo_resource/` | The agent-readable resource, with quote, request and question forms |
| `consumer_agent/` | The general stand-in agent. It knows nothing about this project or business |
| `bench/` | Control page, mock web, queries, grader and benchmark runner |
| `corpus/`, `runs/` | Saved page copies for local search, and run logs and results |
| [research_notes/](research_notes/) | Raw research behind the docs |

The order of work is in the [build plan](docs/03-build-plan.md).

## Keep this repo private

[The Muse transcript](docs/reference/muse-transcript.md) names real businesses and makes claims about their prices and ratings. Replace those names before making it public.
