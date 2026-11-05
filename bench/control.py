"""The control page: one plain HTML page holding the same facts as the site.

If the agent fails here the fault is the agent's, not a hole in the site. It is
generated from the facts file's statements with no design and no resource logic.
"""

from __future__ import annotations

import html
from collections import defaultdict

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from legible_core.business import load_facts, slots
from legible_core.logbook import log_event

STREAM = "control"


def _page(facts: dict) -> str:
    biz = facts["business"]
    groups: dict[str, list[dict]] = defaultdict(list)
    for fact in facts["facts"]:
        if fact["status"] != "false_third_party_claim":
            groups[fact["category"]].append(fact)
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(biz['name'])}</title></head><body>"]
    parts.append(f"<h1>{html.escape(biz['name'])}</h1>")
    parts.append(f"<p>Phone {html.escape(str(biz.get('phone')))}. Email {html.escape(str(biz.get('email')))}.</p>")
    for category, items in groups.items():
        parts.append(f"<h2>{html.escape(category.replace('_', ' ').title())}</h2><ul>")
        for fact in items:
            label = {"unknown": "Not known: ", "not_offered": "Not offered: "}.get(fact["status"], "")
            parts.append(f"<li>{label}{html.escape(fact['statement'])} (Confirmed {fact['confirmed_on']}.)</li>")
        parts.append("</ul>")
    parts.append("<h2>Open appointment slots</h2><ul>")
    for slot in slots():
        if slot.get("open"):
            parts.append(f"<li>{slot['weekday']} {slot['date']}, {html.escape(str(slot['window']))}: {slot['start']} to {slot['end']}</li>")
    parts.append("</ul>")
    parts.append(
        "<h2>Send a request</h2><form method='post' action='/request'>"
        "<p><label>Your name <input name='name'></label></p>"
        "<p><label>Email <input name='email'></label></p>"
        "<p><label>Phone <input name='phone'></label></p>"
        "<p><label>Address <input name='address'></label></p>"
        "<p><label>Vehicle <input name='vehicle'></label></p>"
        "<p><label>Service and preferred slot <textarea name='details'></textarea></label></p>"
        "<p><label>Who is submitting (the customer, or an agent for them) <input name='submitted_by'></label></p>"
        "<p><button type='submit'>Send request</button></p></form>"
    )
    parts.append("</body></html>")
    return "".join(parts)


def create_control_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    facts = load_facts()

    @app.middleware("http")
    async def _log(request: Request, call_next):
        log_event(STREAM, "page_hit", path=request.url.path, method=request.method, user_agent=request.headers.get("user-agent"))
        return await call_next(request)

    @app.get("/", response_class=HTMLResponse)
    def home():
        return _page(facts)

    @app.post("/request", response_class=HTMLResponse)
    def request_form(
        name: str = Form(""),
        email: str = Form(""),
        phone: str = Form(""),
        address: str = Form(""),
        vehicle: str = Form(""),
        details: str = Form(""),
        submitted_by: str = Form(""),
    ):
        log_event(
            STREAM,
            "request",
            name=name,
            email=email,
            phone=phone,
            address=address,
            vehicle=vehicle,
            details=details,
            submitted_by=submitted_by,
            outcome="received",
        )
        return (
            "<!doctype html><title>Request received</title><h1>Request received</h1>"
            "<p>Your request was received. The owner replies by email.</p>"
        )

    @app.get("/robots.txt", response_class=PlainTextResponse)
    def robots():
        return "User-agent: *\nAllow: /\n"

    return app
