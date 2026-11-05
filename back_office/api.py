"""The owner app's API, shaped around its four screens: inbox, resource, simulations and websites.

Run from the repo root: uv run uvicorn back_office.api:app --port 8200
Interactive docs are at /docs. There's no login yet, so keep it on localhost.
"""

from __future__ import annotations

import asyncio
import os
from collections import Counter
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from back_office import brain, connectors, edge, model, store, work
from back_office.record import confirm_drafts, counts, slugify, today_for

_tasks: set[asyncio.Task] = set()


def _background(coro) -> None:
    task = asyncio.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


@asynccontextmanager
async def lifespan(_: FastAPI):
    hours = float(os.environ.get("MF_CRON_HOURS", "6"))
    cron = asyncio.create_task(work.cron_loop(hours))
    yield
    cron.cancel()


app = FastAPI(title="MuseFront back office", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _site(website_id: str) -> dict:
    site = store.website(website_id)
    if not site:
        raise HTTPException(404, "No website has this ID")
    return site


def _item(item_id: str) -> dict:
    item = store.one("SELECT * FROM inbox_item WHERE id = ?", item_id)
    if not item:
        raise HTTPException(404, "No inbox item has this ID")
    if item["status"] != "open":
        raise HTTPException(409, f"This item is already {item['status']}")
    return item


def _site_view(site: dict) -> dict:
    link = edge.link_for(site["slug"])
    record = work.current_record(site["id"])
    name = site["name"] or site["slug"]
    line = f"Prices, availability and booking requests for {name}: {link}"
    return {
        "id": site["id"],
        "slug": site["slug"],
        "name": name,
        "url": site["url"],
        "stage": site["stage"],
        "stage_note": site["stage_note"],
        "live": bool(site["published_version"]),
        "link": link,
        "link_line": line,
        "link_line_html": f'<p>Prices, availability and booking requests for {name}: <a href="{link}">{link}</a></p>',
        "facts": counts(record) if record else {"confirmed": 0, "draft": 0},
        "open_inbox": store.one("SELECT COUNT(*) AS n FROM inbox_item WHERE website_id = ? AND status = 'open'", site["id"])["n"],
        "connections": store.query("SELECT toolkit, status FROM connection WHERE website_id = ?", site["id"]),
        "created_at": site["created_at"],
    }


# ---------------------------------------------------------------- websites


class NewWebsite(BaseModel):
    url: str
    name: str | None = None
    run_check: bool = True
    sim_queries: int = 5


@app.post("/websites", status_code=202)
async def add_website(body: NewWebsite):
    host = urlparse(body.url).hostname or body.url
    base = slugify(body.name or host.removeprefix("www.").split(".")[0])
    slug, n = base, 2
    while store.one("SELECT id FROM website WHERE slug = ?", slug):
        slug, n = f"{base}-{n}", n + 1
    website_id = store.new_id("web")
    store.insert(
        "website",
        id=website_id,
        slug=slug,
        name=body.name or "",
        url=body.url,
        stage="queued",
        stage_note="Starting",
        pages=[],
        created_at=store.now(),
    )
    _background(work.onboard(website_id, body.run_check, body.sim_queries))
    return _site_view(store.website(website_id))


@app.get("/websites")
def list_websites():
    return [_site_view(s) for s in store.query("SELECT * FROM website ORDER BY created_at DESC")]


@app.get("/websites/{website_id}")
def get_website(website_id: str):
    return {**_site_view(_site(website_id)), "pages": _site(website_id)["pages"]}


@app.post("/websites/{website_id}/publish")
async def publish_website(website_id: str):
    _site(website_id)
    result = await work.publish(website_id)
    if not result:
        raise HTTPException(409, "Nothing is confirmed yet, so there's nothing to publish")
    return result


@app.post("/websites/{website_id}/check-link")
async def check_link(website_id: str):
    """Does the owner's site carry the resource link yet? A plain fetch of the home page."""
    site = _site(website_id)
    link = edge.link_for(site["slug"])
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(site["url"])
    return {"link": link, "found": link in response.text}


# ---------------------------------------------------------------- inbox


@app.get("/websites/{website_id}/inbox")
async def inbox(website_id: str, status: str = "open"):
    _site(website_id)
    await work.sync_activity(website_id)
    order = "CASE kind WHEN 'review' THEN 0 WHEN 'request' THEN 1 WHEN 'proposal' THEN 2 WHEN 'agent_question' THEN 3 WHEN 'question' THEN 4 ELSE 5 END"
    return store.query(f"SELECT * FROM inbox_item WHERE website_id = ? AND status = ? ORDER BY {order}, created_at", website_id, status)


class Instruction(BaseModel):
    text: str


@app.post("/websites/{website_id}/instructions")
async def instruct(website_id: str, body: Instruction):
    """Plain language in, a proposal out. Nothing changes until the owner confirms it."""
    _site(website_id)
    record = work.current_record(website_id)
    plan = await brain.instruction_to_ops(record, body.text, today_for(record))
    if plan.get("clarifying_question") or not plan.get("ops"):
        question = plan.get("clarifying_question") or "That didn't map to a change. Could you say it another way?"
        return {"needs_clarifying": True, "question": question}
    item_id = store.add_inbox(website_id, "proposal", plan.get("summary", body.text), body.text, {"ops": plan["ops"]}, "owner_instruction")
    return store.one("SELECT * FROM inbox_item WHERE id = ?", item_id)


class Answer(BaseModel):
    text: str
    scope: str = "everyone"  # "everyone" adds it to the record. "once" only replies.


@app.post("/inbox/{item_id}/answer")
async def answer(item_id: str, body: Answer):
    item = _item(item_id)
    if item["kind"] not in ("question", "agent_question"):
        raise HTTPException(409, "Only questions can be answered")
    website_id = item["website_id"]
    plan = {"summary": "Replied without changing the record", "ops": []}
    if body.scope != "once":
        record = work.current_record(website_id)
        plan = await brain.answer_to_ops(record, item["title"], body.text, today_for(record))
        statement = item["payload"].get("unknown_statement")
        if not plan.get("ops") and statement:
            # The owner has no answer yet, so the page keeps saying so plainly.
            plan["ops"] = [{"op": "upsert", "collection": "facts", "item": {"category": "other", "statement": statement}}]
        if plan.get("ops"):
            work.apply_and_save(website_id, plan["ops"], f"Answered: {item['title']}")
    store.resolve_inbox(item_id, body.text)
    remote_id = item["payload"].get("remote_id")
    if remote_id:
        await edge.reply(remote_id, "answered", body.text)
    await work.publish(website_id)
    return {"summary": plan.get("summary"), "ops": plan.get("ops", []), "version": store.latest_record(website_id)["version"]}


class Confirm(BaseModel):
    exclude_ids: list[str] = []


@app.post("/inbox/{item_id}/confirm")
async def confirm(item_id: str, body: Confirm | None = None):
    item = _item(item_id)
    website_id = item["website_id"]
    if item["kind"] == "review":
        record = confirm_drafts(work.current_record(website_id), body.exclude_ids if body else [])
        store.save_record(website_id, record, "Confirmed facts read from the website")
    elif item["kind"] == "proposal":
        source = "connector" if item["source"] == "connector" else "owner"
        work.apply_and_save(website_id, item["payload"].get("ops", []), item["title"], source)
    elif item["kind"] != "insight":
        raise HTTPException(409, "This item can't be confirmed")
    store.resolve_inbox(item_id, "confirmed")
    published = await work.publish(website_id) if item["kind"] != "insight" else None
    return {"confirmed": True, "version": store.latest_record(website_id)["version"], "published": published}


@app.post("/inbox/{item_id}/dismiss")
async def dismiss(item_id: str):
    item = _item(item_id)
    store.resolve_inbox(item_id, "dismissed", "dismissed")
    if item["kind"] == "question":
        await work.publish(item["website_id"])
    return {"dismissed": True}


class Reply(BaseModel):
    status: str = "accepted"
    message: str = ""


@app.post("/inbox/{item_id}/reply")
async def reply(item_id: str, body: Reply):
    """Answer a booking request. The reply shows on the request's public status page."""
    item = _item(item_id)
    if item["kind"] != "request":
        raise HTTPException(409, "Only requests can be replied to")
    await edge.reply(item["payload"]["remote_id"], body.status, body.message)
    store.resolve_inbox(item_id, f"{body.status}: {body.message}")
    return {"status": body.status}


# ---------------------------------------------------------------- activity


def _agent_label(payload: dict) -> str:
    user_agent = (payload.get("user_agent") or "").lower()
    for term, label in (
        ("chatgpt", "ChatGPT"),
        ("gptbot", "OpenAI crawler"),
        ("claude", "Claude"),
        ("perplexity", "Perplexity"),
        ("google-agent", "Google agent"),
        ("meta", "Meta"),
        ("exa", "Exa"),
        ("personalassistant", "Personal agent"),
        ("curl", "Script"),
        ("python", "Script"),
    ):
        if term in user_agent:
            return label
    return "Browser or unnamed agent"


@app.get("/websites/{website_id}/activity")
async def activity(website_id: str, limit: int = 50):
    """Deliberately small: a feed, a few counts and unmet demand."""
    _site(website_id)
    await work.sync_activity(website_id)
    rows = store.query("SELECT * FROM event WHERE website_id = ? ORDER BY remote_id DESC", website_id)
    events = [{"id": r["remote_id"], "ts": r["ts"], "event": r["event"], **r["payload"]} for r in rows]
    kinds = Counter(e["event"] for e in events)
    feed = []
    for event in events[:limit]:
        feed.append({**event, "agent": _agent_label(event)} if event["event"] == "page_hit" else event)
    reasons = Counter(
        ((e.get("inputs") or {}).get("service") or e.get("reason") or "unknown").lower()
        for e in events
        if e["event"] == "dead_end"
    )
    insights = store.query("SELECT title, body, created_at FROM inbox_item WHERE website_id = ? AND kind = 'insight' ORDER BY created_at DESC", website_id)
    return {
        "counts": {
            "page_reads": kinds["page_hit"],
            "quotes": kinds["quote"],
            "dead_ends": kinds["dead_end"],
            "requests": kinds["request"],
            "questions": kinds["question"],
        },
        "agents": Counter(_agent_label(e) for e in events if e["event"] == "page_hit").most_common(),
        "dead_ends_by_topic": reasons.most_common(10),
        "unmet_demand": insights,
        "feed": feed,
    }


@app.post("/websites/{website_id}/revise")
async def revise_now(website_id: str):
    """Run the periodic review now, rather than waiting for the cron."""
    _site(website_id)
    return await work.revise(website_id)


# ---------------------------------------------------------------- resource


@app.get("/websites/{website_id}/resource")
def resource(website_id: str):
    site = _site(website_id)
    row = store.latest_record(website_id)
    if not row:
        raise HTTPException(404, "The fact sheet hasn't been built yet")
    link = edge.link_for(site["slug"])
    return {
        "link": link,
        "agent_view": f"{link}/index.md",
        "version": row["version"],
        "published_version": site["published_version"],
        "updated_at": row["created_at"],
        "counts": counts(row["record"]),
        "not_stated_yet": work.unknowns(website_id),
        "record": row["record"],
    }


class Edit(BaseModel):
    ops: list[dict]
    reason: str = "Edited by the owner"


@app.patch("/websites/{website_id}/resource")
async def edit_resource(website_id: str, body: Edit):
    """Direct and programmatic edits. The owner made them, so they apply and publish at once."""
    _site(website_id)
    work.apply_and_save(website_id, body.ops, body.reason)
    published = await work.publish(website_id)
    return {"version": store.latest_record(website_id)["version"], "published": published}


@app.post("/websites/{website_id}/resource/undo")
async def undo(website_id: str):
    _site(website_id)
    versions = store.query("SELECT * FROM record_version WHERE website_id = ? ORDER BY version DESC LIMIT 2", website_id)
    if len(versions) < 2:
        raise HTTPException(409, "There's no earlier version")
    store.save_record(website_id, versions[1]["record"], f"Undid: {versions[0]['reason']}")
    await work.publish(website_id)
    return {"version": store.latest_record(website_id)["version"], "restored": versions[1]["version"]}


@app.get("/websites/{website_id}/resource/versions")
def versions(website_id: str):
    _site(website_id)
    return store.query("SELECT version, reason, created_at FROM record_version WHERE website_id = ? ORDER BY version DESC", website_id)


# ---------------------------------------------------------------- simulations


class NewCheck(BaseModel):
    target: str = "resource"  # "resource" or "storefront"
    n: int = 5
    profile: str = "hybrid"


@app.post("/websites/{website_id}/simulations", status_code=202)
async def run_check(website_id: str, body: NewCheck):
    _site(website_id)
    _background(work.run_simulation(website_id, target=body.target, n=body.n, profile=body.profile))
    return {"started": True}


@app.get("/websites/{website_id}/simulations")
def simulations(website_id: str):
    _site(website_id)
    return store.query("SELECT * FROM simulation WHERE website_id = ? ORDER BY created_at DESC", website_id)


@app.get("/simulations/{simulation_id}")
def simulation(simulation_id: str):
    found = store.one("SELECT * FROM simulation WHERE id = ?", simulation_id)
    if not found:
        raise HTTPException(404, "No simulation has this ID")
    return {**found, "runs": store.query("SELECT * FROM simulation_run WHERE simulation_id = ?", simulation_id)}


# ---------------------------------------------------------------- connected accounts


class NewConnection(BaseModel):
    toolkit: str
    callback_url: str | None = None


@app.post("/websites/{website_id}/connections")
async def connect(website_id: str, body: NewConnection):
    _site(website_id)
    if body.toolkit not in connectors.TOOLKITS:
        raise HTTPException(422, f"Choose one of: {', '.join(connectors.TOOLKITS)}")
    try:
        link = await asyncio.to_thread(connectors.connect_link, website_id, body.toolkit, body.callback_url)
    except connectors.NotConfigured as error:
        raise HTTPException(409, str(error)) from error
    store.insert("connection", website_id=website_id, toolkit=body.toolkit, status="pending", detail={}, created_at=store.now())
    return {"connect_link": link}


class SyncAccount(BaseModel):
    spreadsheet_id: str | None = None


@app.post("/websites/{website_id}/connections/{toolkit}/sync")
async def sync_account(website_id: str, toolkit: str, body: SyncAccount | None = None):
    """Read a connected account and put any proposed changes in the inbox."""
    _site(website_id)
    try:
        data = await asyncio.to_thread(connectors.read_account, website_id, toolkit, body.spreadsheet_id if body else None)
    except connectors.NotConfigured as error:
        raise HTTPException(409, str(error)) from error
    store.update("connection", "website_id", website_id, status="connected")
    record = work.current_record(website_id)
    plan = await brain.source_to_ops(record, toolkit, data, today_for(record))
    if not plan.get("ops"):
        return {"proposal": None, "summary": "Nothing new in this account"}
    item_id = store.add_inbox(website_id, "proposal", plan.get("summary", f"Changes from {toolkit}"), f"Read from {toolkit}.", {"ops": plan["ops"]}, "connector")
    return {"proposal": item_id, "summary": plan.get("summary")}


@app.get("/health")
def health():
    return {"ok": True, "edge": edge.EDGE_URL, "model_calls": model.spend["calls"], "model_cost": round(model.spend["cost"], 4), "composio": bool(os.environ.get("COMPOSIO_API_KEY"))}
