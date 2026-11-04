# MuseFront

- All work on this project happens in this folder and its GitHub repo, `Jamerrred/Musefront`.
- Start with `docs/README.md`, which has the current position and the reading order.
- Keep the repo private: `docs/reference/muse-transcript.md` names real businesses.

## How to work

- Never work directly on `main`. Make a short-lived branch for each coherent piece of work.
- Commit small and often, with one logical change per commit.
- Open a pull request and merge it as soon as a piece is done and checked, so branches don't pile up. Prefer several small pull requests to one large one.
- Merge with a merge commit, never a squash, because reports cite commits by hash.
- Delete a branch once it's merged.
- Before opening a pull request, run `uv run ruff check .` and `uv run pytest`.
- Never commit `.env` or anything from it.

## Protect the results

- `consumer_agent/` is frozen at the tag `first-demo-agent-freeze`. Don't change it unless the work is meant to change the agent. If it is, rerun the benchmark and move the tag.
- "Before" and "after" may differ only by the link line.
- Whoever writes benchmark queries sees only the facts, without placements. Whoever writes the resource never sees the queries.
- Benchmark runs spend real OpenRouter credit, so ask first. `--regrade` and `bench.summarize` are free.
