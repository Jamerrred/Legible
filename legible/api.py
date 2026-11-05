"""The owner app's API, shaped around its five screens: websites, simulations, resource, inbox and bookings.

Run from the repo root: uv run uvicorn legible.api:app --port 8200
The app is at /, and interactive API docs are at /docs. There's no login yet, so keep it on localhost.
"""

from __future__ import annotations

import asyncio
import os
from collections import Counter
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from legible import brain, connectors, demo, edge, model, store, work
from legible.record import confirm_drafts, counts, slugify, today_for

_tasks: set[asyncio.Task] = set()


def _background(coro) -> None:
    task = asyncio.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


@asynccontextmanager
async def lifespan(_: FastAPI):
    hours = float(os.environ.get("LEGIBLE_CRON_HOURS", "6"))
    cron = asyncio.create_task(work.cron_loop(hours))
    yield
    cron.cancel()


app = FastAPI(title="Legible app", lifespan=lifespan)
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


def _needs(website_id: str) -> dict:
    """What's waiting on the owner, by the screen it belongs to."""
    rows = store.query("SELECT kind, COUNT(*) AS n FROM inbox_item WHERE website_id = ? AND status = 'open' GROUP BY kind", website_id)
    by_kind = {r["kind"]: r["n"] for r in rows}
    return {
        "missing": by_kind.get("question", 0),
        "review": by_kind.get("review", 0),
        "proposals": by_kind.get("proposal", 0),
        "agent_questions": by_kind.get("agent_question", 0),
        "insights": by_kind.get("insight", 0),
        "bookings": by_kind.get("request", 0),
    }


def _checks(website_id: str) -> dict:
    """The score the owner cares about: the first check, the latest check, and whether one is running."""
    rows = store.query("SELECT id, label, target, status, summary, created_at FROM simulation WHERE website_id = ? ORDER BY created_at", website_id)
    done = [r for r in rows if r["status"] == "done"]

    def score(row: dict) -> dict:
        summary = row["summary"] or {}
        return {"id": row["id"], "label": row["label"], "target": row["target"], "answered": summary.get("answered", 0), "queries": summary.get("queries", 0)}

    return {"first": score(done[0]) if done else None, "latest": score(done[-1]) if done else None, "count": len(done), "running": any(r["status"] == "running" for r in rows)}


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def _next_step(site: dict, needs: dict, checks: dict, facts: dict) -> dict | None:
    """The one thing the owner should do now. The sidebar and the Websites screen both show it."""
    if site["stage"] == "failed":
        return {"screen": "websites/new", "label": "Try another address", "note": "This website couldn't be read."}
    if site["stage"] != "ready":
        return {"screen": "websites", "label": "Legible is reading your website", "note": "You can leave this page while it works.", "busy": True}
    if needs["missing"]:
        return {"screen": "simulations", "label": f"Answer {_plural(needs['missing'], 'question')}", "note": "Test customers got stuck on these."}
    if needs["review"]:
        return {"screen": "resource", "label": f"Confirm {_plural(facts['draft'], 'fact')}", "note": "Nothing is public until you do."}
    if needs["proposals"]:
        return {"screen": "resource", "label": f"Review {_plural(needs['proposals'], 'proposed change')}", "note": "These wait for your yes."}
    if site["published_version"] and checks["latest"] and checks["latest"]["target"] != "resource" and not checks["running"]:
        return {"screen": "simulations", "label": "Run the check again", "note": "See how far your score has moved."}
    if needs["bookings"]:
        return {"screen": "bookings", "label": f"Reply to {_plural(needs['bookings'], 'booking request')}", "note": "An agent is waiting on your answer."}
    if needs["agent_questions"]:
        return {"screen": "inbox", "label": f"Answer {_plural(needs['agent_questions'], 'agent question')}", "note": "Your answer shows on its status page."}
    return None


async def _publish_edit(website_id: str) -> dict | None:
    """Publish an owner's edit, unless they haven't yet confirmed what was read from their website."""
    if store.one("SELECT id FROM inbox_item WHERE website_id = ? AND kind = 'review' AND status = 'open'", website_id):
        return None
    return await work.publish(website_id)


def _site_view(site: dict) -> dict:
    link = edge.link_for(site["slug"])
    record = work.current_record(site["id"])
    name = site["name"] or site["slug"]
    needs = _needs(site["id"])
    checks = _checks(site["id"])
    facts = counts(record) if record else {"confirmed": 0, "draft": 0}
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
        "facts": facts,
        "checks": checks,
        "next": _next_step(site, needs, checks, facts),
        "page_reads": store.one("SELECT COUNT(*) AS n FROM event WHERE website_id = ? AND event = 'page_hit'", site["id"])["n"],
        "open_inbox": store.one("SELECT COUNT(*) AS n FROM inbox_item WHERE website_id = ? AND status = 'open'", site["id"])["n"],
        "needs": needs,
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
    if demo.ENABLED:
        # A demo take has one business. Its script and sample visits all use the one public address.
        await demo.reset()
    host = urlparse(body.url).hostname or body.url
    base = demo.SLUG if demo.ENABLED else slugify(body.name or host.removeprefix("www.").split(".")[0])
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
    _background(demo.onboard(website_id, body.run_check) if demo.ENABLED else work.onboard(website_id, body.run_check, body.sim_queries))
    return _site_view(store.website(website_id))


@app.get("/websites")
def list_websites():
    return [_site_view(s) for s in store.query("SELECT * FROM website ORDER BY created_at DESC")]


@app.get("/websites/{website_id}")
def get_website(website_id: str):
    return {**_site_view(_site(website_id)), "pages": _site(website_id)["pages"]}


def _fact_preview(record: dict | None) -> dict:
    """A short taste of the fact sheet for the live onboarding view."""
    if not record:
        return {"count": 0, "lines": []}
    symbol = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}.get(record.get("currency") or "USD", "")
    lines = []
    for item in (record.get("offerings") or [])[:4]:
        low, high = item.get("price"), item.get("price_high")
        value = f"{symbol}{low} to {symbol}{high}" if low and high else f"{symbol}{low}" if low else "Price not stated"
        lines.append({"text": item.get("name", ""), "value": value})
    lines += [{"text": item.get("statement", "")[:120], "value": ""} for item in (record.get("facts") or [])[:6]]
    tally = counts(record)
    return {"count": tally["draft"] + tally["confirmed"], "lines": lines}


@app.get("/websites/{website_id}/trace")
def trace(website_id: str):
    """Live progress for the app: the onboarding stage, pages read, facts found, and each test customer's steps."""
    site = _site(website_id)
    sim = store.one("SELECT id, label FROM simulation WHERE website_id = ? AND status = 'running' ORDER BY created_at DESC LIMIT 1", website_id)
    return {
        "stage": site["stage"],
        "stage_note": site["stage_note"],
        "name": site["name"] or site["slug"],
        "pages": site["pages"],
        "facts": _fact_preview(work.current_record(website_id)),
        "questions": [q["title"] for q in work.open_questions(website_id)],
        "simulation": {"id": sim["id"], "label": sim["label"], "agents": work.sim_trace(sim["id"])} if sim else None,
    }


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
async def inbox(website_id: str, status: str = "open", kinds: str | None = None):
    """Every open item by default. `kinds` narrows it, such as agent_question,insight."""
    _site(website_id)
    await work.sync_activity(website_id)
    order = "CASE kind WHEN 'review' THEN 0 WHEN 'request' THEN 1 WHEN 'proposal' THEN 2 WHEN 'agent_question' THEN 3 WHEN 'question' THEN 4 ELSE 5 END"
    rows = store.query(f"SELECT * FROM inbox_item WHERE website_id = ? AND status = ? ORDER BY {order}, created_at", website_id, status)
    if kinds:
        wanted = set(kinds.split(","))
        rows = [r for r in rows if r["kind"] in wanted]
    return rows


@app.get("/websites/{website_id}/missing")
async def missing(website_id: str):
    """What the Simulations screen asks the owner: gaps found by tests and real agents first."""
    _site(website_id)
    await work.sync_activity(website_id)
    order = "CASE source WHEN 'simulation' THEN 0 WHEN 'agent_activity' THEN 1 ELSE 2 END, created_at"
    return {
        "open": store.query(f"SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'question' AND status = 'open' ORDER BY {order}", website_id),
        "answered": store.query(
            "SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'question' AND status != 'open' ORDER BY resolved_at DESC LIMIT 20", website_id
        ),
    }


@app.get("/websites/{website_id}/bookings")
async def bookings(website_id: str):
    """Booking requests agents have sent, with open ones first."""
    site = _site(website_id)
    await work.sync_activity(website_id)
    link = edge.link_for(site["slug"])
    rows = store.query(
        "SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'request' AND status != 'dismissed' ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, created_at DESC",
        website_id,
    )
    return [{**r, "status_url": f"{link}/r/{r['payload'].get('remote_id')}"} for r in rows]


class Instruction(BaseModel):
    text: str


@app.post("/websites/{website_id}/instructions")
async def instruct(website_id: str, body: Instruction):
    """Plain language in, a proposal out. Nothing changes until the owner confirms it."""
    _site(website_id)
    record = work.current_record(website_id)
    if demo.ENABLED:
        await asyncio.sleep(1.1)
        plan = demo.plan_instruction(record, body.text, today_for(record))
    else:
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
        plan = demo.plan_answer(item, body.text) if demo.ENABLED else await brain.answer_to_ops(record, item["title"], body.text, today_for(record))
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
    await _publish_edit(website_id)
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
    if demo.ENABLED and item["kind"] == "review":
        _background(demo.seed_activity(website_id))
    return {"confirmed": True, "version": store.latest_record(website_id)["version"], "published": published}


@app.post("/inbox/{item_id}/dismiss")
async def dismiss(item_id: str):
    item = _item(item_id)
    store.resolve_inbox(item_id, "dismissed", "dismissed")
    if item["kind"] == "question":
        await _publish_edit(item["website_id"])
    return {"dismissed": True}


class Reply(BaseModel):
    status: str = "accepted"
    message: str = ""


@app.post("/bookings/{item_id}/reply")
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
    events = [e for e in events if not (e.get("user_agent") or "").startswith("legible")]  # The app's own preview reads.
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
    if demo.ENABLED:
        await work.sync_activity(website_id)
        return {"signals": 0, "questions": 0, "insights": 0}
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
    published = await _publish_edit(website_id)
    return {"version": store.latest_record(website_id)["version"], "published": published}


@app.post("/websites/{website_id}/resource/undo")
async def undo(website_id: str):
    _site(website_id)
    versions = store.query("SELECT * FROM record_version WHERE website_id = ? ORDER BY version DESC LIMIT 2", website_id)
    if len(versions) < 2:
        raise HTTPException(409, "There's no earlier version")
    store.save_record(website_id, versions[1]["record"], f"Undid: {versions[0]['reason']}")
    await _publish_edit(website_id)
    return {"version": store.latest_record(website_id)["version"], "restored": versions[1]["version"]}


@app.get("/websites/{website_id}/resource/changes")
def changes(website_id: str):
    """What the owner asked for in the Resource text box, with anything awaiting confirmation first."""
    _site(website_id)
    return store.query(
        "SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'proposal' ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, created_at DESC LIMIT 20",
        website_id,
    )


@app.get("/websites/{website_id}/resource/agent-view")
async def agent_view(website_id: str):
    """The page exactly as agents read it, as markdown from the live Worker."""
    site = _site(website_id)
    async with httpx.AsyncClient(timeout=20, headers={"user-agent": "legible-app"}) as client:
        response = await client.get(f"{edge.link_for(site['slug'])}/index.md")
    return {"live": response.status_code == 200, "text": response.text if response.status_code == 200 else ""}


@app.get("/websites/{website_id}/resource/quote")
async def try_quote(website_id: str, request: Request):
    """Ask the live page for a quote exactly as an agent would. The Worker keeps this out of activity."""
    site = _site(website_id)
    if not site["published_version"]:
        raise HTTPException(409, "Your page isn't live yet")
    params = [(key, value) for key, value in request.query_params.multi_items() if value]
    address = httpx.URL(f"{edge.link_for(site['slug'])}/quote", params=params)
    async with httpx.AsyncClient(timeout=20, headers={"user-agent": "legible-app"}) as client:
        response = await client.get(address, params=[*params, ("format", "json")])
    if response.status_code >= 500:
        raise HTTPException(502, "Your page didn't answer. Try again.")
    return {"address": str(address), "quote": response.json()}


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
    _background(demo.run_simulation(website_id, body.target) if demo.ENABLED else work.run_simulation(website_id, target=body.target, n=body.n, profile=body.profile))
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
    runs = store.query("SELECT * FROM simulation_run WHERE simulation_id = ?", simulation_id)
    traces = work.sim_trace(simulation_id)
    for run in runs:
        match = next((t for t in traces if t["query"].startswith(run["query"])), None)
        run["path"] = match["path"] if match else []
    return {**found, "runs": runs}


# ---------------------------------------------------------------- connected accounts


@app.get("/connections/available")
def connections_available():
    """Whether accounts can be connected on this install. Composio is optional."""
    return {"configured": connectors.configured(), "toolkits": connectors.TOOLKITS}


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
    except Exception as error:
        raise HTTPException(502, f"Composio couldn't start this connection. Check your COMPOSIO_API_KEY. ({type(error).__name__})") from error
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
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    except Exception as error:
        raise HTTPException(502, f"That account couldn't be read yet. Finish connecting it, then try again. ({type(error).__name__})") from error
    store.run("UPDATE connection SET status = 'connected' WHERE website_id = ? AND toolkit = ?", website_id, toolkit)
    record = work.current_record(website_id)
    plan = await brain.source_to_ops(record, toolkit, data, today_for(record))
    if not plan.get("ops"):
        return {"proposal": None, "summary": "Nothing new in this account"}
    item_id = store.add_inbox(website_id, "proposal", plan.get("summary", f"Changes from {toolkit}"), f"Read from {toolkit}.", {"ops": plan["ops"]}, "connector")
    return {"proposal": item_id, "summary": plan.get("summary")}


@app.get("/config")
def config():
    return {"demo": demo.ENABLED, "demo_url": demo.SITE_URL if demo.ENABLED else None, "suggestions": demo.AGENT_SUGGESTIONS if demo.ENABLED else {}}


@app.get("/demo/reset")
async def demo_reset():
    """Start a demo take over. It only works in the demo copy."""
    if not demo.ENABLED:
        raise HTTPException(404, "Not found")
    await demo.reset()
    return RedirectResponse("/")


@app.get("/health")
def health():
    return {"ok": True, "edge": edge.EDGE_URL, "model_calls": model.spend["calls"], "model_cost": round(model.spend["cost"], 4), "composio": bool(os.environ.get("COMPOSIO_API_KEY"))}


# The owner app itself. This stays last, so the API's routes win.
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent / "web", html=True), name="web")
