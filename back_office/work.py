"""The jobs the back office agent runs: onboarding, the initial check, publishing and the periodic review."""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from pathlib import Path

from back_office import brain, edge, store
from back_office.crawl import crawl, fetch_images, is_local
from back_office.record import apply_ops, counts, public_view, stamp_all, today_for

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs" / "back-office"
PERSON = {
    "profile": {
        "name": "Dana Whitlock",
        "email": "dana.whitlock@example.com",
        "phone": "415-555-0177",
        "address": "742 Example Way",
        "zip": "94117",
    },
    "shareable_without_asking": ["zip"],
    "answers": {"approve_submit": False, "free_text": "I don't have anything to add."},
}


def current_record(website_id: str) -> dict:
    row = store.latest_record(website_id)
    return row["record"] if row else {}


def open_questions(website_id: str) -> list[dict]:
    return store.query("SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'question' AND status = 'open'", website_id)


def asked_titles(website_id: str) -> list[str]:
    rows = store.query("SELECT title FROM inbox_item WHERE website_id = ? AND kind IN ('question', 'insight')", website_id)
    return [r["title"] for r in rows]


def unknowns(website_id: str) -> list[str]:
    return [q["payload"].get("unknown_statement") for q in open_questions(website_id) if q["payload"].get("unknown_statement")]


def add_questions(website_id: str, questions: list[dict], source: str) -> int:
    for q in questions:
        if q.get("question"):
            store.add_inbox(
                website_id,
                "question",
                q["question"],
                q.get("why", ""),
                {"topic": q.get("topic", ""), "unknown_statement": q.get("unknown_statement", "")},
                source,
            )
    return len(questions)


async def publish(website_id: str, preview: bool = False) -> dict | None:
    """Push confirmed facts to the Worker. Drafts are stripped here and never leave this process."""
    site = store.website(website_id)
    record = current_record(website_id)
    if not counts(record)["confirmed"]:
        return None
    view = public_view(record, unknowns(website_id))
    slug = f"{site['slug']}--preview" if preview else site["slug"]
    result = await edge.put_business(slug, view)
    if not preview:
        store.update("website", "id", website_id, published_version=store.latest_record(website_id)["version"])
    return result


def apply_and_save(website_id: str, ops: list[dict], reason: str, source: str = "owner") -> dict:
    record = apply_ops(current_record(website_id), ops, source=source)
    store.save_record(website_id, record, reason)
    return record


# ---------------------------------------------------------------- onboarding


def _stage(website_id: str, stage: str, note: str = "") -> None:
    store.update("website", "id", website_id, stage=stage, stage_note=note)


async def onboard(website_id: str, run_check: bool = True, sim_queries: int = 5, max_pages: int = 12) -> None:
    site = store.website(website_id)
    try:
        _stage(website_id, "crawling", "Reading your website")
        pages = await crawl(site["url"], max_pages)
        if not pages:
            _stage(website_id, "failed", "The website couldn't be read")
            return
        store.update("website", "id", website_id, pages=[{"url": p["url"], "title": p["title"], "via": p.get("via"), "chars": len(p["text"]), "images": len(p["images"])} for p in pages])

        _stage(website_id, "extracting", f"Building your fact sheet from {len(pages)} pages")
        images = await fetch_images(pages)
        image_text = await brain.read_images(images)
        draft = await brain.extract_record(pages, image_text, site["url"])
        draft["business"]["website"] = draft["business"].get("website") or site["url"]
        record = stamp_all(draft, status="draft", source="crawl", today=today_for(draft))
        store.save_record(website_id, record, "Read from the website")
        name = record["business"].get("name") or site["name"]
        store.update("website", "id", website_id, name=name)
        total = counts(record)["draft"]
        store.add_inbox(website_id, "review", f"Confirm {total} facts read from your website", "Nothing is public until you confirm it.", {"count": total})

        _stage(website_id, "interviewing", "Working out what's missing")
        add_questions(website_id, await brain.interview_questions(record), "interview")

        if run_check:
            _stage(website_id, "checking", f"Running {sim_queries} customer agents on your website")
            await run_simulation(website_id, target="storefront", n=sim_queries, label="First check, your website")
        _stage(website_id, "ready", "Ready for you to confirm and answer")
    except Exception as error:
        traceback.print_exc()
        _stage(website_id, "failed", f"{type(error).__name__}: {str(error)[:300]}")


# ---------------------------------------------------------------- simulation


def _agent_broke(result: dict) -> bool:
    """A run that ended on a model or provider error says nothing about the business."""
    return bool(result.get("error")) or (result.get("answer") or "").startswith("The model stopped responding")


def _settled(result: dict) -> bool:
    if _agent_broke(result):
        return False
    if result.get("error") or result.get("outcome") in ("unknown", "blocked", None):
        return False
    return not any(c.get("evidence") == "unknown" for c in result.get("claims") or [])


async def _run_query(simulation_id: str, query: dict, task: str, site_url: str, gate: asyncio.Semaphore, profile: str) -> None:
    run_id = store.new_id("run")
    out = RUNS / simulation_id / run_id
    out.mkdir(parents=True, exist_ok=True)
    person_path = out / "person.json"
    person_path.write_text(json.dumps(PERSON))
    corpus = ROOT / "corpus" / "before"
    local_corpus = is_local(site_url) and "cormorant" in site_url and corpus.exists()
    cmd = [sys.executable, "-m", "consumer_agent.run", "--task", task, "--person", str(person_path), "--profile", profile, "--out", str(out)]
    cmd += ["--search", "local", "--corpus", str(corpus)] if local_corpus else ["--search", "exa"]
    result: dict = {}
    async with gate:
        process = await asyncio.create_subprocess_exec(*cmd, cwd=ROOT, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        try:
            await asyncio.wait_for(process.wait(), timeout=430)
        except TimeoutError:
            process.kill()
            result = {"error": "timed out", "outcome": "blocked", "answer": ""}
    saved = sorted(out.glob("result-*.json"))
    if saved:
        result = json.loads(saved[-1].read_text())
    keep = {k: result.get(k) for k in ("answer", "outcome", "claims", "next_steps", "error", "cost", "wall_s", "tool_calls", "browse_tasks")}
    store.insert(
        "simulation_run",
        id=run_id,
        simulation_id=simulation_id,
        query=query["query"],
        type=query.get("type", ""),
        result=keep,
        settled=int(_settled(keep)),
        created_at=store.now(),
    )


async def run_simulation(website_id: str, target: str = "storefront", n: int = 5, label: str | None = None, profile: str = "hybrid") -> str:
    """One check. A later check reuses the first check's queries, so scores can be compared."""
    site = store.website(website_id)
    record = current_record(website_id)
    simulation_id = store.new_id("sim")
    if target == "resource":
        await publish(website_id, preview=True)
        target_url = edge.link_for(f"{site['slug']}--preview")
    else:
        target_url = site["url"]
    store.insert(
        "simulation",
        id=simulation_id,
        website_id=website_id,
        label=label or ("Check on your resource" if target == "resource" else "Check on your website"),
        target=target,
        status="running",
        created_at=store.now(),
    )
    earlier = store.one("SELECT id FROM simulation WHERE website_id = ? AND status = 'done' ORDER BY created_at LIMIT 1", website_id)
    if earlier:
        queries = [{"query": r["query"], "type": r["type"]} for r in store.query("SELECT query, type FROM simulation_run WHERE simulation_id = ?", earlier["id"])]
    else:
        queries = await brain.write_queries(record, site["url"], n)

    def task_for(query: dict) -> str:
        return f"{query['query']} (The business's information page is {target_url})" if target == "resource" else query["query"]

    gate = asyncio.Semaphore(5)
    await asyncio.gather(*(_run_query(simulation_id, q, task_for(q), target_url, gate, profile) for q in queries))

    runs = store.query("SELECT * FROM simulation_run WHERE simulation_id = ?", simulation_id)
    settled = sum(r["settled"] for r in runs)
    broken = [r for r in runs if _agent_broke(r["result"])]
    summary = {
        "queries": len(runs),
        "answered": settled,
        "agent_errors": len(broken),
        "cost": round(sum(r["result"].get("cost") or 0 for r in runs), 3),
        "average_seconds": round(sum(r["result"].get("wall_s") or 0 for r in runs) / max(len(runs), 1), 1),
    }
    store.update("simulation", "id", simulation_id, status="done", summary=summary, finished_at=store.now())
    failures = [
        {"customer_request": r["query"], "agent_answer": (r["result"].get("answer") or "")[:1500], "outcome": r["result"].get("outcome")}
        for r in runs
        if not r["settled"] and not _agent_broke(r["result"])
    ]
    added = add_questions(website_id, await brain.holes_to_questions(record, failures, asked_titles(website_id)), "simulation")
    if added and target == "resource":
        await publish(website_id)
    return simulation_id


# ---------------------------------------------------------------- activity and the periodic review


_sync_lock = asyncio.Lock()


async def sync_activity(website_id: str) -> int:
    """Pull new events. Requests and questions reach the owner at once, with no model involved.

    The app loads several things at once, so this takes a lock and skips events it already has.
    Otherwise one booking could arrive twice.
    """
    async with _sync_lock:
        return await _sync_activity(website_id)


async def _sync_activity(website_id: str) -> int:
    site = store.website(website_id)
    if not site["published_version"]:
        return 0
    events = await edge.get_events(site["slug"], site["event_cursor"])
    if not events:
        return 0
    items = None
    for event in events:
        if store.one("SELECT remote_id FROM event WHERE website_id = ? AND remote_id = ?", website_id, event["id"]):
            continue
        store.insert(
            "event",
            website_id=website_id,
            remote_id=event["id"],
            ts=event["ts"],
            event=event["event"],
            payload=json.dumps(event["payload"]),
        )
        payload = event["payload"]
        if event["event"] == "question":
            store.add_inbox(website_id, "agent_question", payload.get("text", ""), "An agent asked this for a customer.", {"remote_id": payload.get("id")}, "agent_activity")
        elif event["event"] == "request" and payload.get("id"):
            if items is None:
                items = {i["id"]: i for i in await edge.get_items(site["slug"])}
            data = (items.get(payload["id"]) or {}).get("data", {})
            job = data.get("inputs", {})
            title = f"Booking request: {job.get('service') or 'a job'}{' on ' + job['when'] if job.get('when') else ''}"
            store.add_inbox(website_id, "request", title, data.get("notes", ""), {"remote_id": payload["id"], "details": data}, "agent_activity")
    store.update("website", "id", website_id, event_cursor=events[-1]["id"])
    return len(events)


async def revise(website_id: str) -> dict:
    """The periodic job. It turns what agents did into owner questions and never changes the record itself."""
    await sync_activity(website_id)
    site = store.website(website_id)
    rows = store.query(
        "SELECT * FROM event WHERE website_id = ? AND remote_id > ? AND event IN ('dead_end', 'question', 'quote') ORDER BY remote_id",
        website_id,
        site["revised_through"],
    )
    signals = [{"event": r["event"], **r["payload"]} for r in rows]
    signals = [s for s in signals if s["event"] != "quote" or s.get("status") != "ok"]
    last = store.one("SELECT MAX(remote_id) AS m FROM event WHERE website_id = ?", website_id)["m"] or 0
    store.update("website", "id", website_id, revised_through=last)
    if not signals:
        return {"signals": 0, "questions": 0, "insights": 0}
    review = await brain.review_activity(current_record(website_id), signals, asked_titles(website_id))
    added = add_questions(website_id, review["questions"], "agent_activity")
    for item in review["demand"]:
        store.add_inbox(website_id, "insight", item.get("title", ""), item.get("detail", ""), {}, "agent_activity")
    if added:
        await publish(website_id)
    return {"signals": len(signals), "questions": added, "insights": len(review["demand"])}


async def cron_loop(hours: float) -> None:
    while True:
        await asyncio.sleep(hours * 3600)
        for site in store.query("SELECT id FROM website WHERE published_version > 0"):
            try:
                await revise(site["id"])
            except Exception:
                traceback.print_exc()
