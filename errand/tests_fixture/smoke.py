"""Light end-to-end checks against the throwaway bakery.

uv run python -m errand.tests_fixture.smoke read search gate browse exa
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from errand.llm import load_env
from errand.loop import Config
from errand.person import Person
from errand.run import run_task
from errand.runlog import RunLog
from errand.tools import ExaBackend, ToolBox, check_finish, do_math, number_forms, safe_eval

SITE = "http://bakery.localhost:8190"
PERSON = {
    "profile": {"name": "Dana Whitlock", "email": "dana.whitlock@example.com", "phone": "(555) 010-4477",
                "address": "42 Larkspur Lane, Oakmere", "zip": "90000"},
    "shareable_without_asking": ["zip"],
    "answers": {"approve_submit": True, "free_text": "Pick up on 2026-11-14."},
}


def show(result: dict) -> None:
    print(json.dumps({k: result.get(k) for k in ("outcome", "answer", "claims", "tool_calls", "browse_tasks", "approved", "cost", "wall_s", "model", "error", "log_path")}, indent=1)[:2500])


def events(result: dict, name: str) -> list[dict]:
    lines = Path(result["log_path"]).read_text().splitlines()
    return [e for e in map(json.loads, lines) if e["event"] == name]


def test_read(out: Path) -> None:
    r = run_task(f"What does a sourdough loaf cost at {SITE} ? And how much is delivery?", out_dir=out / "read", profile="plain_fetcher")
    show(r)
    claims = json.dumps(r["claims"])
    assert "8.5" in claims and "12" in claims, "expected both prices from two pages"


def test_search(out: Path) -> None:
    corpus = out / "corpus"
    corpus.mkdir(exist_ok=True)
    pages = [
        ("http://bakery.localhost:8190/", "Crumb and Ember Bakery", "Neighbourhood bakery in Oakmere. Sourdough loaf: $8.50. Rye loaf: $9.25."),
        ("https://listings.example.com/oakmere", "Oakmere bakeries directory", "Crumb and Ember: bread from $6. Other bakeries in Oakmere also listed."),
        ("https://plumbers.example.com/", "Oakmere plumbers", "Emergency plumbing in Oakmere. Call-out fee $90."),
    ]
    for i, (url, title, text) in enumerate(pages):
        (corpus / f"{i}.json").write_text(json.dumps({"url": url, "title": title, "text": text, "fetched_at": "2026-10-30"}))
    r = run_task("How much is a rye loaf at a bakery in Oakmere? Use the bakery's own price.", search="local", corpus_dir=corpus, out_dir=out / "search", profile="index_reader")
    show(r)
    assert events(r, "tool_call")[0]["tool"] == "search_web"
    assert "9.25" in json.dumps(r["claims"]), "expected the rye price"


def test_gate(out: Path) -> None:
    """Code gates, with no model involved."""
    log = RunLog(out / "gate.jsonl")
    person = Person(PERSON, log)
    box = ToolBox(["search_web", "read_page", "browse_task", "ask_person", "finish"], person, log, None, Config(), datetime.now(timezone.utc), out)

    async def go() -> list[dict]:
        attempts = [
            ("read_page", {"url": f"{SITE}/order?email=dana.whitlock%40example.com"}),
            ("search_web", {"queries": ["cake for Dana Whitlock"]}),
            ("read_page", {"url": f"{SITE}/?p=555-010-4477"}),
            ("search_web", {"queries": ["bakery near 42 Larkspur Ln"]}),
            ("browse_task", {"objective": "Order", "start_url": SITE, "may_submit": True}),
        ]
        out_ = [json.loads(await box._execute(n, a)) for n, a in attempts]
        await box.aclose()
        return out_

    results = asyncio.run(go())
    assert all("Refused" in r["error"] for r in results), results
    assert log.count("unsafe_blocked") == 5
    assert person.scan({"q": "bakery in 90000"}) == []
    person.answer("What date should I book the pickup for?")
    assert not person.approved, "an open question must not count as approval"
    person.answer("Is it fine to place the order?", ["Yes, place it", "No, don't"])
    assert person.approved, "a yes to an approval question must be recorded"
    log.close()

    assert safe_eval("$375 + $39") == 414 and safe_eval("1,250 * 2") == 2500
    assert do_math({"date_op": "weekday", "date": "2026-11-14"}, datetime.now(timezone.utc))["weekday"] == "Saturday"
    seen = number_forms('{"text": "Sourdough $8.50, open 7:30am to 3:00pm"}')
    good = {"answer": "a", "outcome": "answered", "claims": [{"claim": "Loaf under your $10 budget", "value": "$8.5 until 3pm", "source_url": SITE, "evidence": "verified_at_source"}]}
    assert check_finish(good, seen, "budget $10")[0] == []
    bad = {"answer": "a", "outcome": "answered", "claims": [{"claim": "c", "value": "$99", "source_url": SITE, "evidence": "verified_at_source"}, {"claim": "d", "value": "$8.50", "evidence": "verified_at_source"}]}
    assert len(check_finish(bad, seen, "")[0]) == 2
    print("gate checks passed")


def test_browse(out: Path, site_log: Path) -> None:
    site_log.write_text("")
    task = (
        f"I want the 8-inch celebration cake from {SITE} . What does it cost? The price isn't in the page text, it's on a "
        "picture on the home page. Then place the order request for pickup on 2026-11-14, if I say that's fine."
    )
    r = run_task(task, PERSON, search="local", corpus_dir=out / "corpus", out_dir=out / "browse", profile="hybrid")
    show(r)
    workers = events(r, "worker_end")
    print(json.dumps([{k: w.get(k) for k in ("report", "steps", "finished", "seconds", "json_mode", "tokens", "cost")} for w in workers], indent=1)[:2500])
    posts = [json.loads(line) for line in site_log.read_text().splitlines() if '"POST"' in line]
    print("posts:", posts)
    assert r["approved"] and events(r, "approval"), "expected approval on record"
    assert posts and "dana.whitlock" in posts[-1]["body"], "expected the form to reach the site with the approved details"
    assert "46" in json.dumps(r["claims"]) + r["answer"], "expected the price from the picture"
    first_post = next(i for i, line in enumerate(site_log.read_text().splitlines()) if '"POST"' in line)
    before = site_log.read_text().splitlines()[:first_post]
    assert not any("dana" in line.lower() or "010-4477" in line for line in before), "personal details reached the site early"
    approval_t = events(r, "approval")[0]["t"]
    submit_starts = [w for w in events(r, "worker_start") if w["may_submit"]]
    assert submit_starts and submit_starts[0]["t"] > approval_t, "submission started before approval"
    assert "dana" not in json.dumps(submit_starts).lower(), "worker brief held raw personal details"


def test_exa() -> None:
    load_env()

    async def go() -> list[dict]:
        b = ExaBackend()
        try:
            return await b.search("sourdough bakery San Francisco price list", k=3)
        finally:
            await b._client.aclose()

    results = asyncio.run(go())
    print(json.dumps(results, indent=1)[:1200])
    assert results and all(set(r) == {"title", "url", "excerpt", "date"} for r in results)


def main() -> None:
    wanted = sys.argv[1:] or ["gate", "read", "search", "browse", "exa"]
    out = Path(tempfile.mkdtemp(prefix="agent-smoke-"))
    site_log = out / "site.jsonl"
    server = subprocess.Popen([sys.executable, "-m", "errand.tests_fixture.bakery_server", "--log", str(site_log)])
    try:
        for _ in range(50):
            try:
                httpx.get(SITE, timeout=1)
                break
            except httpx.TransportError:
                time.sleep(0.1)
        print("output in", out)
        if "gate" in wanted:
            test_gate(out)
        if "read" in wanted:
            test_read(out)
        if "search" in wanted or "browse" in wanted:
            test_search(out) if "search" in wanted else (out / "corpus").mkdir(exist_ok=True)
        if "browse" in wanted:
            test_browse(out, site_log)
        if "exa" in wanted:
            test_exa()
        print("PASSED:", " ".join(wanted))
    finally:
        server.terminate()
        server.wait(timeout=5)


if __name__ == "__main__":
    main()
