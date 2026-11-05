# Legible

- All work on this project happens in this folder and its GitHub repo, `Jamerrred/Legible`. The folder is still called `Musefront`, the product's old name.
- The repo is public. Never commit secrets, or real businesses' names and details.
- Start with `README.md`. `docs/planning/README.md` has the original decisions and research.

## Where things live

- `main` is the real product and must always run from a fresh clone. It holds no scripted or sample data in the app itself.
- `experiment/` holds the before-and-after test and everything only it needs.
- The `demo` branch is the scripted film copy. Never merge it into `main`.
- Film and design working files belong in the private repo `Jamerrred/Legible-film`, never in this one.
- The branch `video/legible-film` backs a link in the hackathon submission. Don't delete or rewrite it unless the founder says so.
- The tags `hackathon-submission`, `demo-film-recording` and `first-demo-agent-freeze` mark exact moments. Don't move them, apart from the rule below.

## How to work

- Never work directly on `main`. Make a short-lived branch for each coherent piece of work.
- Commit small and often, with one logical change per commit.
- Open a pull request and merge it as soon as a piece is done and checked, so branches don't pile up. Prefer several small pull requests to one large one, and don't stack them.
- Merge with a merge commit, never a squash, because reports cite commits by hash.
- Delete a branch once it's merged.
- Before opening a pull request, run `uv run ruff check .` and `uv run pytest`.
- Never commit `.env` or anything from it.

## Protect the results

- `errand/`, our consumer agent, is frozen at the tag `first-demo-agent-freeze`, where it was named `consumer_agent/`. Don't change it unless the work is meant to change the agent. If it is, rerun the benchmark and move the tag.
- "Before" and "after" may differ only by the link line.
- Whoever writes benchmark queries sees only the facts, without placements. Whoever writes the resource never sees the queries.
- Benchmark runs spend real OpenRouter credit, so ask first. `--regrade` and `bench.summarize` are free.
