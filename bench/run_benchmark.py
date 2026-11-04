"""Run the frozen agent over a query set on one version of the site, then grade.

Usage:
  uv run python -m bench.run_benchmark --variant before --name first-demo --resume
  uv run python -m bench.run_benchmark --variant before --name first-demo --regrade

--resume keeps runs that finished with no API failure and spends only on the rest.
--regrade makes no model calls: it re-grades saved runs against saved site logs.

A run the API refuses for credit is retried once, then recorded as invalid and left out
of the rates. No new run starts once the OpenRouter balance is under --credit-floor
dollars. Keep --concurrency low on a small balance, because OpenRouter holds budget for
requests in flight. Clear logs/ before a benchmark, because its events get saved with it.

Each run gets a fresh process, a fresh browser profile and its own fake contact email.
The email is how a form submission in the site's log is joined back to a run, so nothing
run-specific goes into a URL or a header.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from dotenv import dotenv_values

from bench.grade import grade, read_run
from mf_core.logbook import read_events

ROOT = Path(__file__).resolve().parent.parent
STREAMS = {"before": ["site-before"], "after": ["site-after", "resource"], "control": ["control"]}
DEFAULT_PROFILE = {
    "name": "Dana Whitlock",
    "email": "dana.whitlock@example.com",
    "phone": "415-555-0177",
    "address": "742 Example Way, San Francisco, CA",
    "zip": "94117",
    "vehicle": "2021 Toyota RAV4",
}


def person_for(query: dict, run_tag: str) -> dict:
    person = copy.deepcopy(query.get("person") or {})
    profile = {**DEFAULT_PROFILE, **(person.get("profile") or {})}
    local, _, domain = profile["email"].partition("@")
    profile["email"] = f"{local}.{run_tag}@{domain}"
    person["profile"] = profile
    person.setdefault("shareable_without_asking", ["zip", "vehicle"])
    person.setdefault("answers", {"approve_submit": False, "free_text": "I don't have anything to add."})
    return person


def credit_left() -> float | None:
    key = dotenv_values(ROOT / ".env").get("OPENROUTER_API_KEY")
    try:
        data = httpx.get("https://openrouter.ai/api/v1/credits", headers={"Authorization": f"Bearer {key}"}, timeout=20).json()["data"]
        return float(data["total_credits"]) - float(data["total_usage"])
    except (httpx.HTTPError, KeyError, ValueError):
        return None


def not_run(reason: str, repeat: int, out: Path) -> dict:
    return {"api_failure": f"not run: {reason}", "repeat": repeat, "person": {}, "crashed": False, "out": out}


def one_run(query: dict, variant: str, repeat: int, args: argparse.Namespace, retried: bool = False) -> dict:
    out = ROOT / "runs" / args.name / variant / f"{query['id']}_r{repeat}"
    relative = str(out.relative_to(ROOT))
    if (args.resume or args.regrade) and out.exists():
        info = read_run(out)
        if info.get("report") and not info.get("api_failure"):
            person = json.loads((out / "person.json").read_text())
            info.update(person=person, crashed=False, repeat=repeat, reused=True)
            return {"query": query, "run": info, "out": relative}
    if args.regrade:
        return {"query": query, "run": not_run("no saved run", repeat, relative), "out": relative}
    left = credit_left()
    if left is not None and left < args.credit_floor:
        reason = f"balance ${left:.2f} is under the ${args.credit_floor:.2f} floor"
        return {"query": query, "run": not_run(reason, repeat, relative), "out": relative}
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    run_tag = f"{variant[0]}{query['id']}r{repeat}".replace("-", "")
    person = person_for(query, run_tag)
    person_path = out / "person.json"
    person_path.write_text(json.dumps(person, indent=1))
    cmd = [
        sys.executable, "-m", "consumer_agent.run", "--task", query["query"], "--person", str(person_path),
        "--search", "local", "--corpus", str(ROOT / "corpus" / variant), "--tier", args.tier, "--out", str(out),
    ]  # fmt: skip
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=480, check=False)
        (out / "stdout.txt").write_text(proc.stdout[-4000:])
        (out / "stderr.txt").write_text(proc.stderr[-4000:])
        crashed = proc.returncode != 0
    except subprocess.TimeoutExpired:
        crashed = True
        (out / "stderr.txt").write_text("timed out after 480s")
    info = read_run(out)
    if info.get("api_failure") and not retried:
        time.sleep(45)  # let in-flight requests settle
        return one_run(query, variant, repeat, args, retried=True)
    info.update(person=person, crashed=crashed, repeat=repeat, seconds=info.get("seconds") or round(time.time() - started, 1))
    return {"query": query, "run": info, "out": relative}


def saved_events(variant: str, saved: Path) -> list[dict]:
    """The events for a version, from the benchmark's saved copy and any live logs."""
    events: list[dict] = []
    seen: set[str] = set()
    for stream in STREAMS[variant]:
        for event in read_events(stream, saved) + read_events(stream):
            key = json.dumps(event, sort_keys=True)
            if key not in seen:
                seen.add(key)
                events.append(event)
    return events


def save_events(variant: str, saved: Path, events: list[dict]) -> None:
    saved.mkdir(parents=True, exist_ok=True)
    for stream in STREAMS[variant]:
        kept = [json.dumps(e) for e in events if e.get("stream") == stream]
        if kept:
            (saved / f"{stream}.jsonl").write_text("\n".join(kept) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", required=True, choices=["before", "after", "control"])
    parser.add_argument("--queries", default="bench/queries.json")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--name", default="first-demo")
    parser.add_argument("--tier", default="spark")
    parser.add_argument("--only", default="")
    parser.add_argument("--resume", action="store_true", help="keep finished runs and spend only on the rest")
    parser.add_argument("--regrade", action="store_true", help="re-grade saved runs with no model calls")
    parser.add_argument("--credit-floor", type=float, default=0.3)
    args = parser.parse_args()

    queries = json.loads((ROOT / args.queries).read_text())
    if args.only:
        wanted = set(args.only.split(","))
        queries = [q for q in queries if q["id"] in wanted]
    jobs = [(q, r) for r in range(1, args.repeats + 1) for q in queries]
    print(f"{len(jobs)} runs on {args.variant}", flush=True)

    outputs = []
    with ThreadPoolExecutor(args.concurrency) as pool:
        futures = [pool.submit(one_run, q, args.variant, r, args) for q, r in jobs]
        for future in futures:
            item = future.result()
            outputs.append(item)
            print(item["query"]["id"], "done", item["run"].get("seconds"), flush=True)

    out_dir = ROOT / "runs" / args.name
    saved = out_dir / "site-logs"
    # A re-grade uses only what the benchmark saved, so it can't pick up later test traffic.
    if args.regrade:
        events = [event for stream in STREAMS[args.variant] for event in read_events(stream, saved)]
    else:
        events = saved_events(args.variant, saved)
    results = []
    for item in outputs:
        graded = grade(item["query"], item["run"], args.variant, events)
        graded.update(
            repeat=item["run"]["repeat"], out=item["out"], cost=item["run"].get("cost"), seconds=item["run"].get("seconds"),
            used_resource=item["run"].get("used_resource"), tool_calls=item["run"].get("tool_calls"), reused=item["run"].get("reused", False),
            browser_calls=item["run"].get("browser_calls"), crashed=item["run"].get("crashed"),
            report=item["run"].get("report"),
        )
        results.append(graded)

    (out_dir / f"results_{args.variant}.json").write_text(json.dumps(results, indent=1, default=str))
    if not args.regrade:
        save_events(args.variant, saved, events)

    valid = [r for r in results if r.get("valid", True)]
    n = len(valid)
    print(f"\n{args.variant}: valid runs {n}/{len(results)}, correct {sum(r['correct'] for r in valid)}/{n}, "
          f"acceptable {sum(r['acceptable'] for r in valid)}/{n}, partial {sum(r['partial'] for r in valid)}, "
          f"cost ${sum(float(r['cost'] or 0) for r in valid):.2f}")
    for r in results:
        flag = "resource" if r["used_resource"] else ""
        print(f"  {r['query_id']} r{r['repeat']}: {r['result']:20} {flag:9} {r['seconds']}s  {'; '.join(r['problems'])[:140]}")


if __name__ == "__main__":
    main()
