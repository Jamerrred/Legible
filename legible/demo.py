"""A scripted private copy of the app, for recording demos. It only runs with LEGIBLE_DEMO=1.

Crawling, questions and test customers are played back quickly from fixed data, with no model
calls. The fact sheet is a real crawl of the demo site, and the answers come from its facts file.
Publishing is real, so the public page, /quote, /request and /ask all work.

Run: LEGIBLE_DEMO=1 LEGIBLE_DB_PATH=legible/demo.db uv run uvicorn legible.api:app --port 8300
Start over by opening /demo/reset.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import re
from datetime import UTC, date, datetime, timedelta
from difflib import get_close_matches
from pathlib import Path

import httpx

from legible import edge, store, work
from legible.record import slugify, stamp_all, today_for

ENABLED = os.environ.get("LEGIBLE_DEMO") == "1"
SLUG = "sunrise"
SITE_URL = "https://sunrise-auto-detailers.jamerrred-audiobooks.workers.dev"
HERE = Path(__file__).resolve().parent
NAME = "Sunrise Auto Detailers"
AGENT_SUGGESTIONS = {"golf": "We don't detail golf carts.", "military": "No, we don't offer a senior or military discount."}
AGENT_UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/140.0 Safari/537.36 PersonalAssistant/1.0"
UNNAMED_UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"


def _facts() -> dict:
    return json.loads((HERE.parent / "businesses" / "sunrise" / "facts.json").read_text())


def _questions() -> dict[str, dict]:
    zones = _facts()["pricing_model"]["travel"]["zones"]
    zone_ops = [{"op": "delete", "collection": "zones", "id": i} for i in ("san-francisco", "marin", "treasure-island", "east-bay", "peninsula")]
    for key, zone_id, label in (("zone-1", "san-francisco", "San Francisco"), ("zone-2", "peninsula", "The Peninsula and Treasure Island"), ("zone-3", "marin-east-bay", "Marin and the East Bay")):
        zone_ops.append({"op": "upsert", "collection": "zones", "item": {"id": zone_id, "label": label, "zips": zones[key]["zips"], "fee": zones[key]["fee"]}})
    fee = lambda i, label, amount, when, **more: {"op": "upsert", "collection": "fees", "item": {"id": i, "label": label, "amount": amount, "applies_when": when, "taxable": True, **more}}  # noqa: E731
    refuse = lambda i, name, terms, statement: {"op": "upsert", "collection": "not_offered", "item": {"id": i, "name": name, "terms": terms, "statement": statement}}  # noqa: E731
    fact = lambda i, statement: {"op": "upsert", "collection": "facts", "item": {"id": i, "category": "policies", "statement": statement}}  # noqa: E731
    return {
        "fees": {
            "chip": "Saturday and condition fees",
            "title": "Do you charge extra for Saturdays, evenings or very dirty cars? How much?",
            "why": "A test customer with a $400 budget couldn't tell whether a Saturday fits.",
            "suggested": "Saturdays add $25, the 5 to 6 pm evening window adds $30, a heavily soiled interior adds $75, and excessive pet hair adds $60.",
            "summary": "Added the Saturday, evening, heavily soiled and pet hair fees",
            "unknown": f"{NAME} hasn't stated its surcharges.",
            "ops": [
                fee("saturday-fee", "Saturday fee", 25, "any job done on a Saturday", weekdays=["Saturday"]),
                fee("evening-fee", "After-hours fee", 30, "the 5 to 6 pm window on Tuesdays and Thursdays, for an exterior wash"),
                fee("heavily-soiled", "Heavily soiled surcharge", 75, "mud on over half the floor, or dried spills on 2 or more seats", aliases=["heavily soiled", "muddy", "mud"]),
                fee("excess-pet-hair", "Excessive pet hair surcharge", 60, "hair embedded across 3 or more seats"),
            ],
        },
        "tax": {
            "chip": "Tax and travel fees",
            "title": "Do you add sales tax, and what's your travel fee outside San Francisco?",
            "why": "Test customers couldn't work out an all-in price for Berkeley or Sausalito.",
            "suggested": "We add 8.625% sales tax, but not on travel. San Francisco has no travel fee, the Peninsula is $35, and Marin and the East Bay are $65.",
            "summary": "Set 8.625% sales tax and travel fees for 47 ZIP codes",
            "unknown": f"{NAME} hasn't stated its tax or travel fees.",
            "ops": [{"op": "set", "path": "tax", "value": {"rate": 0.08625, "applies_to": "services, add-ons and surcharges, but not the travel fee"}}, *zone_ops],
        },
        "refuse": {
            "chip": "What you refuse",
            "title": "What jobs do you refuse? A customer asked about cleaning up vomit.",
            "why": "A test customer's agent couldn't say no, because your site never lists what you don't do.",
            "suggested": "We don't clean vomit, blood, mould or other biohazards. We don't do ceramic coating, and we don't detail boats or RVs.",
            "summary": "Added biohazards, ceramic coating, boats and RVs to what you don't do",
            "unknown": f"{NAME} hasn't stated what it refuses.",
            "ops": [
                refuse("biohazard", "Biohazard cleanup", ["vomit", "blood", "mould", "biohazard", "carsick"], f"{NAME} doesn't clean biohazards, meaning visible mould, blood, vomit, or human or animal waste."),
                refuse("ceramic-coating", "Ceramic coating", ["ceramic"], f"{NAME} doesn't do ceramic coating. Its longest-lasting paint protection is the 6-month paint sealant."),
                refuse("boats", "Boats", ["boat", "jet ski", "motorcycle"], f"{NAME} doesn't detail boats, jet skis or motorcycles."),
                refuse("rvs", "RVs", ["rv", "motorhome", "trailer"], f"{NAME} doesn't detail RVs, motorhomes or trailers."),
            ],
        },
        "discounts": {
            "chip": "Discounts",
            "title": "Do you give discounts for several cars or regular visits?",
            "why": "Your website doesn't mention any, so agents can't quote fleets or repeat customers.",
            "suggested": "Yes. Three or more vehicles in one visit get 10% off, and regular visits get 15% off every 2 weeks or 10% off every 4 weeks.",
            "summary": "Added fleet and recurring discounts",
            "unknown": f"{NAME} hasn't stated whether it gives discounts.",
            "ops": [
                fact("fleet-discount", f"{NAME} takes 10% off for 3 to 4 vehicles at one address on one day, on Tuesday to Friday only."),
                fact("recurring-plan", f"{NAME}'s recurring plan takes 15% off visits every 2 weeks, or 10% off visits every 4 weeks."),
            ],
        },
    }


def _add_question(website_id: str, key: str, source: str) -> None:
    q = _questions()[key]
    blocks = [c["query"] for c in CUSTOMERS if key in c["needs"]]
    payload = {"demo_key": key, "unknown_statement": q["unknown"], "suggested": q["suggested"], "demo_ops": q["ops"], "demo_summary": q["summary"], "chip": q["chip"], "blocks": blocks}
    store.add_inbox(website_id, "question", q["title"], q["why"], payload, source)


# The test customers. Each step is what the live trace shows: a "say" line or a tool call.
CUSTOMERS = [
    {
        "query": "Inside and out on my 2021 Subaru Outback in Berkeley, 94704, with dog hair on the back seat. I can't go over $400 all in. Does a Saturday work?",
        "needs": ["fees", "tax"],
        "first": [("say", "I'll check Sunrise's prices for your Outback."), ("read", "/"), ("browse", "Read the prices on the package image"), ("read", "/book"), ("say", "No Saturday fee, tax or East Bay travel fee is stated anywhere."), ("finish", "")],
        "first_answer": "The Schooner for a midsize car is $249, plus $55 for pet hair, so $304 before anything else. I can't confirm an all-in total, because the site doesn't state tax, the East Bay travel fee or any Saturday fee.",
        "again": [("say", "I'll work out both days for your budget."), ("read", "/b/sunrise"), ("quote", "/b/sunrise/quote?service=the-schooner&variant=class-b&addon=pet-hair-removal&zip=94704&when=saturday"), ("quote", "/b/sunrise/quote?service=the-schooner&variant=class-b&addon=pet-hair-removal&zip=94704&when=tuesday"), ("finish", "")],
        "again_answer": "Saturday comes to $422.38, which is $22.38 over your $400. Tuesday to Friday comes to $395.22, which fits.",
    },
    {
        "query": "My kid got carsick in the back of our CR-V and it reeks. Can Sunrise come clean that up in 94122? How much?",
        "needs": ["refuse"],
        "first": [("say", "I'll see if Sunrise can take this job."), ("read", "/"), ("read", "/faq"), ("search", "Sunrise Auto Detailers vomit cleanup"), ("say", "The site never says what it refuses, so I can't rule this in or out."), ("finish", "")],
        "first_answer": "I can't tell. They offer interior cleaning and odour treatment, but the site doesn't say whether they take biohazard jobs like this one. You'd need to call and ask.",
        "again": [("read", "/b/sunrise"), ("say", "Found it under what they don't offer."), ("finish", "")],
        "again_answer": "No. Sunrise doesn't clean biohazards, which includes vomit, even though you're in its service area.",
    },
    {
        "query": "Need a number for our muddy F-250 in Sausalito, 94965. Inside only, with a real shampoo. The outlet is 150 feet away. What's the whole cost, tax and all?",
        "needs": ["fees", "tax"],
        "first": [("say", "I'll add up the whole job for your truck."), ("read", "/"), ("browse", "Find the price for a heavy-duty pickup"), ("read", "/faq"), ("say", "“May cost extra” is never defined, and neither is the travel fee."), ("finish", "")],
        "first_answer": "$444 so far, for the interior detail, the shampoo and the generator. I can't give a total: the heavily soiled charge, the travel fee and tax aren't stated.",
        "again": [("read", "/b/sunrise"), ("quote", "/b/sunrise/quote?service=the-cutter&variant=class-d&addon=shampoo&condition=heavily-soiled&condition=generator-fee&zip=94965"), ("finish", "")],
        "again_answer": "$628.76, tax and travel included: $289 interior detail, $125 shampoo, $75 heavily soiled, $30 generator, $44.76 tax and $65 travel.",
    },
    {
        "query": "I've booked but need to cancel 36 hours before. Do I lose my deposit?",
        "needs": [],
        "first": [("read", "/"), ("read", "/faq"), ("say", "The FAQ covers this."), ("finish", "")],
        "first_answer": "You get half your deposit back when you cancel between 24 and 48 hours before the arrival window.",
        "again": [("read", "/b/sunrise"), ("finish", "")],
        "again_answer": "You get half your deposit back when you cancel between 24 and 48 hours before the arrival window.",
    },
]


async def _play_customer(sim_id: str, index: int, customer: dict, steps: list, answer: str, settled: bool, base_url: str, pace: float) -> None:
    folder = work.RUNS / sim_id / f"customer-{index}"
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / "run-demo.jsonl"

    def write(event: dict) -> None:
        with log.open("a") as handle:
            handle.write(json.dumps(event) + "\n")

    await asyncio.sleep(index * 0.35)
    write({"event": "run_start", "task": customer["query"]})
    for kind, text in steps:
        await asyncio.sleep(random.uniform(0.75, 1.35) * pace)
        if kind == "say":
            write({"event": "turn_end", "text": text})
        elif kind == "search":
            write({"event": "tool_call", "tool": "search_web", "args": {"queries": [text]}})
        elif kind == "browse":
            write({"event": "tool_call", "tool": "browse_task", "args": {"objective": text}})
        elif kind == "finish":
            write({"event": "tool_call", "tool": "finish", "args": {}})
        else:
            write({"event": "tool_call", "tool": "read_page", "args": {"url": base_url + text}})
    await asyncio.sleep(0.6 * pace)
    write({"event": "run_end", "report": {"outcome": "answered" if settled else "unknown"}})
    store.insert(
        "simulation_run",
        id=store.new_id("run"),
        simulation_id=sim_id,
        query=customer["query"],
        type="",
        result={"answer": answer, "outcome": "answered" if settled else "unknown", "claims": [], "cost": 0, "wall_s": 0},
        settled=int(settled),
        created_at=store.now(),
    )


async def run_simulation(website_id: str, target: str = "storefront") -> str:
    first = target == "storefront"
    sim_id = store.new_id("sim")
    label = "First check, your website" if first else "Check on your resource"
    store.insert("simulation", id=sim_id, website_id=website_id, label=label, target=target, status="running", created_at=store.now())
    answered = {q["payload"].get("demo_key") for q in store.query("SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'question' AND status = 'done'", website_id)}
    jobs = []
    for index, customer in enumerate(CUSTOMERS):
        if first:
            steps, answer, settled = customer["first"], customer["first_answer"], not customer["needs"]
        else:
            ready = set(customer["needs"]) <= answered
            steps, answer, settled = (customer["again"], customer["again_answer"], True) if ready else (customer["first"], customer["first_answer"], False)
        jobs.append(_play_customer(sim_id, index, customer, steps, answer, settled, SITE_URL if first else edge.EDGE_URL, 1.5 if first else 1.25))
    await asyncio.sleep(0.8)
    await asyncio.gather(*jobs)
    runs = store.query("SELECT settled FROM simulation_run WHERE simulation_id = ?", sim_id)
    summary = {"queries": len(runs), "answered": sum(r["settled"] for r in runs), "agent_errors": 0, "cost": 0, "average_seconds": 0}
    store.update("simulation", "id", sim_id, status="done", summary=summary, finished_at=store.now())
    if first:
        for key in ("fees", "tax", "refuse"):
            _add_question(website_id, key, "simulation")
    return sim_id


async def onboard(website_id: str, run_check: bool = True) -> None:
    store.update("website", "id", website_id, name=NAME)
    site = store.website(website_id)
    stage = lambda name, note: store.update("website", "id", website_id, stage=name, stage_note=note)  # noqa: E731
    # Earlier takes leave events on the Worker, so start after them, and take the old page down.
    old = await edge.get_events(SLUG, 0)
    store.update("website", "id", website_id, event_cursor=old[-1]["id"] if old else 0)
    await edge.delete_business(SLUG)

    stage("crawling", "Reading your website")
    pages = []
    for path, title, chars, images in (("/", "Home", 1879, 2), ("/faq", "FAQ", 6146, 0), ("/book", "Book", 397, 0)):
        await asyncio.sleep(1.1)
        pages.append({"url": site["url"].rstrip("/") + path, "title": title, "via": "exa", "chars": chars, "images": images})
        store.update("website", "id", website_id, pages=pages)
    await asyncio.sleep(0.5)

    stage("extracting", "Reading the prices in your images")
    await asyncio.sleep(1.8)
    stage("extracting", "Building your fact sheet")
    await asyncio.sleep(1.6)
    draft = json.loads((HERE / "demo_draft.json").read_text())
    draft["business"]["website"] = site["url"]
    draft["business"]["timezone"] = "America/Los_Angeles"
    record = stamp_all(draft, status="draft", source="crawl", today=today_for(draft))
    store.save_record(website_id, record, "Read from the website")
    store.update("website", "id", website_id, name=NAME)
    total = sum(len(record[c]) for c in ("offerings", "addons", "fees", "zones", "facts", "not_offered"))
    store.add_inbox(website_id, "review", f"Confirm {total} facts read from your website", "Nothing is public until you confirm it.", {"count": total})
    await asyncio.sleep(3.0)  # Long enough to see the facts arrive.

    stage("interviewing", "Working out what's missing")
    await asyncio.sleep(2.0)
    _add_question(website_id, "discounts", "interview")

    if run_check:
        stage("checking", "Running 4 customer agents on your website")
        await run_simulation(website_id, "storefront")
    stage("ready", "Ready for you to confirm and answer")


def _next(weekday: int, today: date) -> date:
    """The next date on this weekday, at least 2 days out so no same-day fee applies. Monday is 0."""
    days = (weekday - today.weekday()) % 7
    return today + timedelta(days=days if days >= 2 else days + 7)


def _booking(name: str, contact: str, phone: str, notes: str, **job) -> dict:
    return {"name": name, "email": f"{contact}@example.com", "phone": phone, "submitted_by": "agent", "agent_name": "a personal agent", "notes": notes, "format": "json", **job}


def sample_visits(today: date) -> list[tuple]:
    """A sample week of agents using the public page: (method, path, data, user agent).

    Every customer here is invented. The story behind each one comes from the business's own rules,
    and the page itself works out every total, so the numbers on screen are real.
    """
    saturday, sunday, tuesday, wednesday, friday = (_next(day, today).isoformat() for day in (5, 6, 1, 2, 4))
    quote = lambda agent=AGENT_UA, **job: ("GET", "/quote", {**job, "format": "json"}, agent)  # noqa: E731
    read = lambda path="", agent=AGENT_UA: ("GET", path, None, agent)  # noqa: E731
    outback = {"service": "the-schooner", "variant": "class-b", "zip": "94110", "when": saturday}
    golden = {"service": "the-cutter", "variant": "class-b", "addon": "pet-hair-removal", "zip": "94117", "when": tuesday}
    # The muddy F-250 from the test customers, now with a total the owner's answers made possible.
    truck = {"service": "the-cutter", "variant": "class-d", "addon": "shampoo", "condition": ["heavily-soiled", "generator-fee"], "zip": "94965", "when": wednesday}
    minivan = {"service": "the-schooner", "variant": "class-c", "addon": "shampoo", "zip": "94114", "when": friday}
    return [
        read(),
        read("/services/the-schooner", UNNAMED_UA),
        quote(service="the-schooner", variant="class-b", zip="94110"),
        quote(service="ceramic coating"),
        read("", UNNAMED_UA),
        quote(UNNAMED_UA, service="ceramic coating for a new Model Y"),
        read(),
        quote(**golden),
        ("POST", "/request", _booking("Priya Raman", "priya.raman", "415-555-0142", "Golden retriever hair on the back seat. It's in the driveway, and someone will be home to hand over the keys.", **golden), AGENT_UA),
        read("", UNNAMED_UA),
        quote(service="the-cutter", variant="class-c", zip="94103", when=sunday),
        ("POST", "/ask", {"question": "Do you detail golf carts?", "format": "json"}, AGENT_UA),
        read(),
        quote(**truck),
        ("POST", "/request", _booking("Marcus Ellery", "marcus.ellery", "415-555-0118", "Work truck with mud across the floor, inside only. It's in our driveway, and the nearest outlet is about 150 feet away.", **truck), AGENT_UA),
        quote(service="ceramic coat"),
        read("/services/the-flagship", UNNAMED_UA),
        quote(service="RV detailing"),
        read("", UNNAMED_UA),
        quote(UNNAMED_UA, service="motorhome wash"),
        ("POST", "/ask", {"question": "Do you offer a senior or military discount?", "format": "json"}, AGENT_UA),
        read(),
        quote(**minivan),
        ("POST", "/request", _booking("Renee Okafor", "renee.okafor", "415-555-0163", "Spilled milk on the carpet in the back of our minivan. It's in the driveway, with an outlet in the garage.", **minivan), AGENT_UA),
        read("", UNNAMED_UA),
        quote(service="the-skiff", variant="class-a", zip="94107"),
        read(),
        read("/services/the-schooner"),
        quote(**outback),
        ("POST", "/request", _booking("Dana Whitlock", "dana.whitlock", "415-555-0177", "Parked in the driveway, with an outlet nearby.", **outback), AGENT_UA),
    ]


# Two of the sample bookings already have a reply, so the owner can see both states.
SAMPLE_REPLIES = {
    "Marcus Ellery": ("accepted", "Yes, we can do this. We'll bring the generator, and we'll text you your arrival window the day before."),
    "Renee Okafor": ("suggested", "We're full that Friday. Would the following Tuesday morning work?"),
}
SAMPLE_DAYS = 4


def sample_times(count: int, now: datetime) -> list[str]:
    """When each visit shows as happening: uneven gaps across the last few days, ending now."""
    rng = random.Random(count)
    gaps = [rng.uniform(0.3, 1.7) for _ in range(count)]
    span, total, passed, times = timedelta(days=SAMPLE_DAYS), sum(gaps), 0.0, []
    for gap in gaps:
        passed += gap
        times.append((now - span + span * (passed / total)).isoformat(timespec="seconds"))
    return times


async def _date_arrivals(website_id: str, after: int, stamp: str) -> int:
    """Pull what just arrived and date it on the sample week. Returns the last event dated."""
    await work.sync_activity(website_id)
    rows = store.query("SELECT remote_id, payload FROM event WHERE website_id = ? AND remote_id > ?", website_id, after)
    for row in rows:
        store.run("UPDATE event SET ts = ? WHERE website_id = ? AND remote_id = ?", stamp, website_id, row["remote_id"])
        if row["payload"].get("id"):
            store.run("UPDATE inbox_item SET created_at = ? WHERE website_id = ? AND json_extract(payload, '$.remote_id') = ?", stamp, website_id, row["payload"]["id"])
    return max((r["remote_id"] for r in rows), default=after)


async def seed_activity(website_id: str) -> None:
    """Sample visits to the real public page, once the owner has put the link on their website.

    They arrive in seconds so the counts climb on camera, and they're dated across the last few
    days so the Inbox reads like a real week. The demo's sidebar says the data is a sample.
    """
    link = edge.link_for(SLUG)
    await asyncio.sleep(1.0)
    visits = sample_visits(date.today())
    seen = store.website(website_id)["event_cursor"] or 0
    times = sample_times(len(visits), datetime.now(UTC))
    async with httpx.AsyncClient(timeout=20) as client:
        for (method, path, data, agent), stamp in zip(visits, times, strict=True):
            headers = {"user-agent": agent}
            if method == "POST":
                await client.post(link + path, data=data, headers=headers)
            else:
                await client.get(link + path, params=data, headers=headers)
            await asyncio.sleep(0.4)  # Slow enough to watch the counts climb.
            seen = await _date_arrivals(website_id, seen, stamp)
    await asyncio.sleep(0.5)  # The page logs just after it responds, so catch the last ones.
    await _date_arrivals(website_id, seen, times[-1])
    for item in store.query("SELECT * FROM inbox_item WHERE website_id = ? AND kind = 'request' AND status = 'open'", website_id):
        reply = SAMPLE_REPLIES.get(item["payload"].get("details", {}).get("name"))
        if reply:
            await edge.reply(item["payload"]["remote_id"], *reply)
            store.resolve_inbox(item["id"], f"{reply[0]}: {reply[1]}")
    store.add_inbox(website_id, "insight", "3 agents asked for ceramic coating", "It isn't something you offer.", {}, "agent_activity")
    store.add_inbox(website_id, "insight", "2 agents asked about RVs and motorhomes", "It isn't something you offer.", {}, "agent_activity")
    store.add_inbox(website_id, "insight", "1 agent asked about Sunday visits", "You're closed on Sundays.", {}, "agent_activity")


def plan_answer(item: dict, text: str) -> dict:
    payload = item.get("payload") or {}
    if payload.get("demo_ops"):
        return {"summary": payload.get("demo_summary", "Added to your page"), "ops": payload["demo_ops"]}
    if "golf" in item["title"].lower():
        return {"summary": "Added golf carts to what you don't do", "ops": [{"op": "upsert", "collection": "not_offered", "item": {"id": "golf-carts", "name": "Golf carts", "terms": ["golf cart"], "statement": f"{NAME} doesn't detail golf carts."}}]}
    return {"summary": "Added to your page", "ops": [{"op": "upsert", "collection": "facts", "item": {"category": "other", "statement": f"{NAME}: {text}"}}]}


def _names_item(item: dict, lower: str, words: list[str]) -> bool:
    name = (item.get("name") or item.get("label") or "").lower().removeprefix("the ").strip()
    if not name:
        return False
    if name in lower:
        return True
    return " " not in name and bool(get_close_matches(name, words, n=1, cutoff=0.6))


def _price_change(record: dict, text: str) -> dict | None:
    """A plain price edit, such as "Class A of the Skiff from 69 to 70". The real app asks the model instead."""
    lower = text.lower()
    target = re.search(r"\b(?:to|now)\s+\$?(\d+(?:\.\d+)?)", lower)
    if not target:
        return None
    new = float(target.group(1))
    before = re.search(r"\bfrom\s+\$?(\d+(?:\.\d+)?)", lower)
    words = re.findall(r"[a-z]+", lower)
    for collection in ("offerings", "addons", "fees"):
        for item in record.get(collection, []):
            if not _names_item(item, lower, words):
                continue
            name = item.get("name") or item.get("label")
            if collection == "fees":
                return {"summary": f"{name} goes from ${item.get('amount'):g} to ${new:g}", "ops": [{"op": "upsert", "collection": "fees", "item": {"id": item["id"], "amount": new}}]}
            variants = item.get("variants") or []
            if not variants:
                return {"summary": f"{name} goes from ${item.get('price'):g} to ${new:g}", "ops": [{"op": "upsert", "collection": collection, "item": {"id": item["id"], "price": new}}]}
            chosen = [v for v in variants if v.get("label", "").lower() in lower]
            if not chosen and before:
                chosen = [v for v in variants if v.get("price") == float(before.group(1))]
            if len(chosen) != 1:
                labels = ", ".join(v.get("label", "") for v in variants)
                return {"clarifying_question": f"Which size of {name} should change: {labels}?"}
            variant = chosen[0]
            return {
                "summary": f"{name}, {variant['label']}, goes from ${variant['price']:g} to ${new:g}",
                "ops": [{"op": "upsert", "collection": collection, "item": {"id": item["id"], "variants": [{"id": variant["id"], "price": new}]}}],
            }
    return None


def plan_instruction(record: dict, text: str, today: str) -> dict:
    lower = text.lower()
    change = _price_change(record, text)
    if change:
        return change
    if re.search(r"\b(price|cost|charge|raise|lower|change)\b", lower):
        return {"clarifying_question": "Which price should change? Name the service, the size and the new price, such as “Class A of the Skiff to $70”."}
    if "clos" in lower or "shut" in lower or "holiday" in lower:
        start = date.fromisoformat(today) + timedelta(days=1)
        end, back = start + timedelta(days=1), start + timedelta(days=2)
        return {
            "summary": f"Closed {start:%b} {start.day} and {end.day}, back on {back:%b} {back.day}. Quotes for those dates will say you're closed, and this ends by itself",
            "ops": [{"op": "upsert", "collection": "facts", "item": {"id": f"closure-{start.isoformat()}", "category": "closure", "statement": f"{NAME} is closed on {start:%B} {start.day} and {end.day}, {start.year}, and back on {back:%B} {back.day}.", "valid_from": start.isoformat(), "valid_to": end.isoformat()}}],
        }
    sentence = text.strip().rstrip(".") + "."
    return {"summary": f"Add this to your page: “{sentence}”", "ops": [{"op": "upsert", "collection": "facts", "item": {"id": slugify(text)[:40], "category": "other", "statement": f"{NAME}: {sentence}"}}]}


async def reset() -> None:
    for table in ("website", "record_version", "inbox_item", "simulation", "simulation_run", "event", "connection"):
        store.run(f"DELETE FROM {table}")
    await edge.delete_business(SLUG)
