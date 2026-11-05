"""Walk one business through the whole product, with a scripted owner.

The back office never sees the facts file. Only this scripted owner does, and it answers
only what it's asked, the way a real owner would.

Start the API first: uv run uvicorn back_office.api:app --port 8200
Then: uv run python scripts/mvp_demo.py --url http://cormorant.localhost:8101 [--check] [--proof]

--check runs the first simulation at onboarding, about $1.30. --proof runs 4 benchmark queries
against the generated resource, about $0.50. Neither runs by default.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from back_office.model import ask_json  # noqa: E402
from bench.grade import content_checks, report_text  # noqa: E402

API = "http://127.0.0.1:8200"
client = httpx.Client(timeout=300)


def api(method: str, path: str, **kwargs):
    response = client.request(method, API + path, **kwargs)
    if response.status_code >= 400:
        raise SystemExit(f"{method} {path} failed with {response.status_code}: {response.text[:400]}")
    return response.json()


def owner_facts(slug: str) -> str:
    path = ROOT / "businesses" / slug / "facts.json"
    data = json.loads(path.read_text())
    return "\n".join(f"- {fact['statement']}" for fact in data["facts"] if fact.get("status") == "known")


async def owner_answer(question: str, facts: str) -> str:
    result = await ask_json(
        "You play a small business owner answering a question from your assistant. Answer fully in plain sentences, including every relevant detail and amount, using only the facts below. "
        'If they don\'t cover it, say you haven\'t decided that. Reply as {"answer": ""}.',
        f"QUESTION\n{question}\n\nFACTS YOU KNOW\n{facts}",
        max_tokens=3000,
    )
    return result.get("answer") or "I haven't decided that."


def wait_ready(website_id: str, limit: int = 900) -> dict:
    started = time.time()
    last = None
    while time.time() - started < limit:
        site = api("GET", f"/websites/{website_id}")
        if site["stage_note"] != last:
            last = site["stage_note"]
            print(f"  [{round(time.time() - started):>4}s] {site['stage']}: {last}", flush=True)
        if site["stage"] in ("ready", "failed"):
            return site
        time.sleep(3)
    raise SystemExit("onboarding timed out")


def answer_inbox(website_id: str, facts: str) -> None:
    for item in api("GET", f"/websites/{website_id}/inbox"):
        if item["kind"] == "review":
            result = api("POST", f"/inbox/{item['id']}/confirm", json={})
            print(f"  confirmed crawled facts, version {result['version']}", flush=True)
        elif item["kind"] == "question":
            text = asyncio.run(owner_answer(item["title"], facts))
            result = api("POST", f"/inbox/{item['id']}/answer", json={"text": text})
            print(f"  Q: {item['title'][:90]}\n  A: {text[:110]}\n     -> {str(result['summary'])[:110]} ({len(result['ops'])} changes)", flush=True)


def proof(link: str) -> None:
    """Four held-out benchmark queries through the frozen agent, given the resource URL directly."""
    queries = {q["id"]: q for q in json.loads((ROOT / "bench" / "queries.json").read_text())}
    passed = 0
    procs = []
    for qid in ("q01", "q02", "q03", "q05"):
        out = ROOT / "runs" / "back-office" / "proof" / qid
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob("*"):
            old.unlink()
        person = out / "person.json"
        person.write_text(json.dumps(queries[qid].get("person") or {}))
        task = f"{queries[qid]['query']} (The business's information page is {link})"
        cmd = [sys.executable, "-m", "consumer_agent.run", "--task", task, "--person", str(person), "--search", "exa", "--out", str(out)]
        procs.append((qid, out, subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
    total_cost = 0.0
    for qid, out, process in procs:
        process.wait(timeout=480)
        saved = sorted(out.glob("result-*.json"))
        report = json.loads(saved[-1].read_text()) if saved else {}
        ok, reasons = content_checks(queries[qid], report_text(report))
        passed += int(ok)
        total_cost += report.get("cost") or 0
        print(f"  {qid}: {'PASS' if ok else 'FAIL'} | {report.get('outcome')} | {report.get('wall_s')}s | ${report.get('cost')} | {reasons[:2]}", flush=True)
        print(f"     {(report.get('answer') or '')[:400]!r}", flush=True)
    print(f"  proof: {passed} of 4 correct on the generated resource, ${total_cost:.2f}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://cormorant.localhost:8101")
    parser.add_argument("--facts", default="cormorant", help="Which business's facts the scripted owner knows")
    parser.add_argument("--website-id", help="Reuse a website that's already onboarded")
    parser.add_argument("--check", action="store_true", help="Run the first simulation at onboarding")
    parser.add_argument("--proof", action="store_true", help="Run 4 benchmark queries on the generated resource")
    args = parser.parse_args()
    facts = owner_facts(args.facts)

    print("1. Add the website", flush=True)
    website_id = args.website_id
    if not website_id:
        website_id = api("POST", "/websites", json={"url": args.url, "run_check": args.check})["id"]
    site = wait_ready(website_id)
    if site["stage"] == "failed":
        raise SystemExit(site["stage_note"])
    print(f"  {site['name']}: {site['facts']}", flush=True)
    for page in site["pages"]:
        print(f"  read via {page.get('via')}: {page['url']} ({page.get('chars')} characters, {page.get('images')} images)", flush=True)

    print("2. Owner answers the inbox", flush=True)
    answer_inbox(website_id, facts)
    if not api("GET", f"/websites/{website_id}")["live"]:
        raise SystemExit("nothing was published")
    site = api("GET", f"/websites/{website_id}")
    link = site["link"]
    print(f"  live: {site['live']} | link: {link}\n  link line: {site['link_line']}", flush=True)
    page = httpx.get(link, timeout=30)
    print(f"  page {page.status_code}, {len(page.text)} characters; markdown {httpx.get(link + '/index.md', timeout=30).status_code}", flush=True)

    print("3. Plain-language instruction, confirm, then undo", flush=True)
    proposal = api("POST", f"/websites/{website_id}/instructions", json={"text": "The store will be closed for the next 2 days."})
    print(f"  proposed: {proposal.get('title') or proposal}", flush=True)
    if proposal.get("id"):
        api("POST", f"/inbox/{proposal['id']}/confirm", json={})
        statement = next(op["item"]["statement"] for op in proposal["payload"]["ops"] if op.get("item", {}).get("statement"))
        print(f"  statement: {statement}\n  page shows it: {statement in httpx.get(link + '/index.md', timeout=30).text}", flush=True)
        api("POST", f"/websites/{website_id}/resource/undo")
        print(f"  after undo, page shows it: {statement in httpx.get(link + '/index.md', timeout=30).text}", flush=True)

    print("4. An outside agent quotes, hits a dead end, asks and books", flush=True)
    resource = api("GET", f"/websites/{website_id}/resource")["record"]
    first = resource["offerings"][0]
    variant = (first.get("variants") or [{}])[0].get("id", "")
    quote = httpx.get(f"{link}/quote", params={"service": first["id"], "variant": variant, "zip": "94110", "format": "json"}, timeout=30).json()
    print(f"  quote: {quote['status']} total {quote.get('total')} | {quote['summary'][:100]}", flush=True)
    dead = httpx.get(f"{link}/quote", params={"service": "ceramic coating", "format": "json"}, timeout=30).json()
    print(f"  dead end: {dead['status']} | {dead['summary'][:100]}", flush=True)
    asked = httpx.post(f"{link}/ask", data={"question": "Do you clean boats?", "format": "json"}, timeout=30).json()
    print(f"  asked: {asked['outcome']}", flush=True)
    booked = httpx.post(
        f"{link}/request",
        data={"service": first["id"], "variant": variant, "zip": "94110", "name": "Dana Test", "email": "dana@example.com", "submitted_by": "agent", "format": "json"},
        timeout=30,
    ).json()
    print(f"  request: {booked['outcome']} | {booked.get('status_url')}", flush=True)

    print("5. Owner handles what came in", flush=True)
    for item in api("GET", f"/websites/{website_id}/inbox"):
        if item["kind"] == "request":
            api("POST", f"/inbox/{item['id']}/reply", json={"status": "accepted", "message": "Yes, see you then."})
            status_page = httpx.get(booked["status_url"], timeout=30).text
            print(f"  replied to request; status page shows it: {'see you then' in status_page}", flush=True)
        elif item["kind"] == "agent_question":
            result = api("POST", f"/inbox/{item['id']}/answer", json={"text": "We don't clean boats."})
            print(f"  answered agent question -> {result['summary']}", flush=True)

    print("6. The periodic review", flush=True)
    print(f"  {api('POST', f'/websites/{website_id}/revise')}", flush=True)

    print("7. Activity", flush=True)
    activity = api("GET", f"/websites/{website_id}/activity")
    print(f"  {activity['counts']} | {activity['agents']} | {[i['title'] for i in activity['unmet_demand']]}", flush=True)

    if args.proof:
        print("8. Benchmark proof, on the private preview so it stays out of activity", flush=True)
        asyncio.run(_publish_preview(website_id))
        proof(f"{link}--preview")
    print(f"Done. Website {website_id}. {api('GET', '/health')}", flush=True)


async def _publish_preview(website_id: str) -> None:
    from back_office import work

    await work.publish(website_id, preview=True)


if __name__ == "__main__":
    main()
