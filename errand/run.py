"""CLI and function entry point.

uv run python -m errand.run --task "..." --person person.json \
    --search local --corpus DIR --tier spark --out runs/x/
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .llm import LLM, load_env
from .loop import Config, run_loop
from .person import Person
from .runlog import RunLog
from .tools import ExaBackend, LocalCorpusBackend, ToolBox

# A profile is configuration only: which tools are on, and how read_page behaves.
PROFILES: dict[str, dict[str, Any]] = {
    "hybrid": {"tools": ["search_web", "read_page", "browse_task", "do_math", "ask_person", "finish"]},
    "index_reader": {"tools": ["search_web", "read_page", "finish"], "stored_only": True},
    "plain_fetcher": {"tools": ["read_page", "finish"]},
    "browser_only": {"tools": ["browse_task", "ask_person", "finish"]},
}


def _parse_now(now: datetime | str | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    value = datetime.fromisoformat(now) if isinstance(now, str) else now
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


async def arun_task(
    task: str,
    person: dict[str, Any] | str | Path | None = None,
    search: str = "exa",
    corpus_dir: str | Path | None = None,
    tier: str = "spark",
    out_dir: str | Path = "runs/adhoc",
    profile: str = "hybrid",
    now: datetime | str | None = None,
    query_id: str | None = None,
    site_version: str | None = None,
    **config: Any,
) -> dict[str, Any]:
    load_env()
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; choose from {', '.join(PROFILES)}")
    cfg = Config(**config)
    spec = PROFILES[profile]
    moment = _parse_now(now)
    if isinstance(person, (str, Path)):
        person = json.loads(Path(person).read_text(encoding="utf-8"))

    out = Path(out_dir)
    run_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{os.getpid()}-{secrets.token_hex(2)}"
    log = RunLog(out / f"run-{run_id}.jsonl")
    who = Person(person, log)

    backend = None
    if "search_web" in spec["tools"] or spec.get("stored_only"):
        if search == "local":
            if not corpus_dir:
                raise ValueError("search='local' needs corpus_dir")
            backend = LocalCorpusBackend(corpus_dir)
        elif search == "exa":
            backend = ExaBackend()
        else:
            raise ValueError("search must be 'local' or 'exa'")

    llm = LLM(tier=tier, reasoning_effort=cfg.reasoning_effort, max_tokens=cfg.max_tokens)
    box = ToolBox(spec["tools"], who, log, llm, cfg, moment, out, backend=backend, stored_only=bool(spec.get("stored_only")))
    t0 = time.monotonic()
    report: dict[str, Any] = {}
    error = None
    try:
        await llm.resolve()
        log.event(
            "run_start", run_id=run_id, query_id=query_id, site_version=site_version, profile=profile, model=llm.model,
            tier=tier, agent_version=__version__, search=search, task=task, now=moment.isoformat(),
            limits={"tool_calls": cfg.max_tool_calls, "page_chars": cfg.max_page_chars, "wall_clock_s": cfg.wall_clock_s},
        )
        report = await run_loop(task, llm, box, who, log, cfg, moment)
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)[:400]}"
        report = {"answer": f"The run failed: {error}", "outcome": "blocked", "claims": [], "mapped_terms": [], "next_steps": [], "gate_note": None}
    finally:
        await box.aclose()
        await llm.aclose()

    result = {
        **report,
        "run_id": run_id,
        "profile": profile,
        "model": llm.model,
        "tool_calls": box.calls_used,
        "browse_tasks": box.browse_used,
        "approved": who.approved,
        "usage": llm.usage.snapshot(),
        "cost": round(llm.usage.cost, 6),
        "wall_s": round(time.monotonic() - t0, 2),
        "log_path": str(log.path),
        "error": error,
    }
    log.event("run_end", report=report, tokens=result["usage"], cost=result["cost"], wall_s=result["wall_s"], tool_calls=box.calls_used, error=error)
    log.close()
    (out / f"result-{run_id}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return result


def run_task(
    task: str,
    person: dict[str, Any] | str | Path | None = None,
    search: str = "exa",
    corpus_dir: str | Path | None = None,
    tier: str = "spark",
    out_dir: str | Path = "runs/adhoc",
    profile: str = "hybrid",
    now: datetime | str | None = None,
    **config: Any,
) -> dict[str, Any]:
    return asyncio.run(arun_task(task, person, search, corpus_dir, tier, out_dir, profile, now, **config))


def main() -> None:
    p = argparse.ArgumentParser(description="Act for a person who wants something from a business.")
    p.add_argument("--task", required=True)
    p.add_argument("--person", help="Path to a person JSON file")
    p.add_argument("--search", choices=["local", "exa"], default="exa")
    p.add_argument("--corpus", help="Directory of saved page copies, for --search local")
    p.add_argument("--tier", default="spark", help="spark, wonder, or an explicit model id")
    p.add_argument("--out", default="runs/adhoc")
    p.add_argument("--profile", choices=list(PROFILES), default="hybrid")
    p.add_argument("--now", help="ISO time to treat as now")
    p.add_argument("--max-tool-calls", type=int, default=Config.max_tool_calls)
    p.add_argument("--reasoning-effort", default="low")
    a = p.parse_args()
    result = run_task(
        a.task, a.person, a.search, a.corpus, a.tier, a.out, a.profile, a.now,
        max_tool_calls=a.max_tool_calls, reasoning_effort=a.reasoning_effort,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
