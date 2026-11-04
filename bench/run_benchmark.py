"""Run the frozen agent over a query set on one version of the site, then grade.

Usage:
  uv run python -m bench.run_benchmark --variant before --queries bench/queries.json \
      --repeats 2 --concurrency 6 --name first-demo [--tier spark] [--only q01,q02]

Each run gets a fresh process, a fresh browser profile and its own fake contact
email. The email is how a form submission in the site's log is joined back to a
run, so nothing run-specific goes into a URL or a header.
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

from bench.grade import grade, read_run
from mf_core.logbook import read_events

ROOT = Path(__file__).resolve().parent.parent
PYTHON = str(ROOT / ".venv" / "bin" / "python")
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


def one_run(query: dict, variant: str, repeat: int, name: str, tier: str) -> dict:
    out = ROOT / "runs" / name / variant / f"{query['id']}_r{repeat}"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    run_tag = f"{variant[0]}{query['id']}r{repeat}".replace("-", "")
    person = person_for(query, run_tag)
    person_path = out / "person.json"
    person_path.write_text(json.dumps(person, indent=1))
    cmd = [PYTHON, "-m", "consumer_agent.run", "--task", query["query"], "--person", str(person_path),
           "--search", "local", "--corpus", str(ROOT / "corpus" / variant), "--tier", tier, "--out", str(out)]
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=480)
        (out / "stdout.txt").write_text(proc.stdout[-4000:])
        (out / "stderr.txt").write_text(proc.stderr[-4000:])
        crashed = proc.returncode != 0
    except subprocess.TimeoutExpired:
        crashed = True
        (out / "stderr.txt").write_text("timed out after 480s")
    info = read_run(out)
    info.update(person=person, crashed=crashed, repeat=repeat, seconds=info.get("seconds") or round(time.time() - started, 1))
    return {"query": query, "run": info, "out": str(out.relative_to(ROOT))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", required=True, choices=["before", "after", "control"])
    parser.add_argument("--queries", default="bench/queries.json")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--name", default="first-demo")
    parser.add_argument("--tier", default="spark")
    parser.add_argument("--only", default="")
    args = parser.parse_args()

    queries = json.loads((ROOT / args.queries).read_text())
    if args.only:
        wanted = set(args.only.split(","))
        queries = [q for q in queries if q["id"] in wanted]
    jobs = [(q, r) for r in range(1, args.repeats + 1) for q in queries]
    print(f"{len(jobs)} runs on {args.variant}", flush=True)

    outputs = []
    with ThreadPoolExecutor(args.concurrency) as pool:
        futures = [pool.submit(one_run, q, args.variant, r, args.name, args.tier) for q, r in jobs]
        for future in futures:
            item = future.result()
            outputs.append(item)
            print(item["query"]["id"], "done", item["run"].get("seconds"), flush=True)

    events = [e for stream in STREAMS[args.variant] for e in read_events(stream)]
    results = []
    for item in outputs:
        graded = grade(item["query"], item["run"], args.variant, events)
        graded.update(
            repeat=item["run"]["repeat"], out=item["out"], cost=item["run"].get("cost"), seconds=item["run"].get("seconds"),
            used_resource=item["run"].get("used_resource"), tool_calls=item["run"].get("tool_calls"),
            browser_calls=item["run"].get("browser_calls"), crashed=item["run"].get("crashed"),
            report=item["run"].get("report"),
        )
        results.append(graded)

    out_dir = ROOT / "runs" / args.name
    (out_dir / f"results_{args.variant}.json").write_text(json.dumps(results, indent=1, default=str))
    logs = out_dir / "site-logs"
    logs.mkdir(exist_ok=True)
    for stream in STREAMS[args.variant]:
        source = ROOT / "logs" / f"{stream}.jsonl"
        if source.exists():
            shutil.copy(source, logs / source.name)

    n = len(results)
    print(f"\n{args.variant}: correct {sum(r['correct'] for r in results)}/{n}, "
          f"acceptable {sum(r['acceptable'] for r in results)}/{n}, partial {sum(r['partial'] for r in results)}, "
          f"cost ${sum(float(r['cost'] or 0) for r in results):.2f}")
    for r in results:
        flag = "resource" if r["used_resource"] else ""
        print(f"  {r['query_id']} r{r['repeat']}: {r['result']:18} {flag:9} {r['seconds']}s  {'; '.join(r['problems'])[:140]}")
    sys.exit(0)


if __name__ == "__main__":
    main()
