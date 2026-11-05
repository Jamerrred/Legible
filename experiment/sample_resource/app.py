"""The agent-readable resource for one business, served at agents.sunrise.localhost:8103.

Every fact comes from businesses/sunrise/facts.json and every total from
business_core.business.quote. The main page and offering pages are built as a small list of
blocks, then rendered to HTML or markdown, so the two versions can't drift apart.

Run from the repo root: uv run python -m sample_resource.app
"""

from __future__ import annotations

import ipaddress
import secrets
from datetime import timedelta

from business_core.logbook import log_event
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from sample_resource.config import (
    ADDONS,
    BASE_URL,
    BIZ,
    DEAD_STATUSES,
    FACT,
    NAME,
    QUOTE_VALID_DAYS,
    SERVICES,
    STREAM,
)
from sample_resource.content import (
    addon_sections,
    facts_used_html,
    main_html,
    main_markdown,
    markdown_response,
    offering_title,
    offerings_sections,
    page,
    render_html,
    render_markdown,
    service_sections,
    wants_markdown,
)
from sample_resource.formatting import esc, link, local_now, stamp
from sample_resource.forms import (
    ask_form,
    find_record,
    normalise_who,
    question_status_html,
    quote_form,
    request_form,
    request_status_html,
)
from sample_resource.quoting import (
    evaluate,
    first,
    headline,
    job_query,
    outcome_html,
    parse_job,
    read_params,
)

app = FastAPI(title=NAME, docs_url=None, redoc_url=None, openapi_url=None)


def ip_range(request: Request) -> str:
    host = request.client.host if request.client else ""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return "unknown"
    prefix = 24 if address.version == 4 else 48
    return str(ipaddress.ip_network(f"{address}/{prefix}", strict=False))


@app.middleware("http")
async def log_page_hit(request: Request, call_next):
    response = await call_next(request)
    headers = request.headers
    log_event(
        STREAM,
        "page_hit",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        user_agent=headers.get("user-agent", ""),
        ip_range=ip_range(request),
        referer=headers.get("referer", ""),
        accept=headers.get("accept", ""),
        signature=headers.get("signature-agent") or headers.get("signature-input") or "",
    )
    return response


@app.api_route("/", methods=["GET", "HEAD"])
def home(request: Request):
    return main_markdown() if wants_markdown(request) else main_html()


@app.api_route("/index.md", methods=["GET", "HEAD"])
def home_markdown():
    return main_markdown()


@app.api_route("/services", methods=["GET", "HEAD"])
def services_index(request: Request):
    title = f"Offerings at {NAME}"
    sections = offerings_sections()
    if wants_markdown(request):
        return markdown_response(render_markdown(title, [], sections))
    return page(title, f"<h1>{esc(title)}</h1>" + render_html(sections))


@app.api_route("/services/{offering_id}", methods=["GET", "HEAD"])
def offering_page(offering_id: str, request: Request):
    as_markdown = offering_id.endswith(".md") or wants_markdown(request)
    offering_id = offering_id.removesuffix(".md")
    if offering_id in SERVICES:
        sections = service_sections(offering_id)
    elif offering_id in ADDONS:
        sections = addon_sections(offering_id)
    else:
        body = "<h1>Not an offering on this site</h1>" + render_html(offerings_sections())
        return page("Not found", body, status_code=404)
    title = offering_title(offering_id)
    if as_markdown:
        return markdown_response(render_markdown(title, [], sections))
    body = (
        f'<h1>{esc(title)}</h1><p>Markdown version: <a href="/services/{esc(offering_id)}.md">/services/{esc(offering_id)}.md</a></p>'
        + render_html(sections)
    )
    return page(title, body, f"/services/{offering_id}.md")


@app.api_route("/quote", methods=["GET", "POST"])
async def quote_route(request: Request):
    params = await read_params(request)
    job = parse_job(params)
    as_json = first(params, "format").lower() == "json"
    if not any(job.values()):
        if as_json:
            return JSONResponse({"status": "needs_info", "still_needed": ["service", "zip_code"], "parameters": f"{BASE_URL}/#addresses"})
        body = (
            f"<h1>Work out a total for {esc(NAME)}</h1>"
            "<p>This takes a job's details and returns a total or range. It takes no personal details. "
            'The values it accepts are listed under <a href="/#addresses">Addresses on this site</a>, and it also works as a plain link.</p>'
            + quote_form(job)
        )
        return page(f"Quote: {NAME}", body)

    outcome = evaluate(job)
    quote_id = "quote-" + secrets.token_hex(6)
    issued = local_now()
    expires = issued + timedelta(days=QUOTE_VALID_DAYS)
    log_event(
        STREAM,
        "quote",
        quote_id=quote_id,
        inputs=job,
        status=outcome["status"],
        total=outcome["total"],
        estimate_range=outcome["estimate_range"],
        deposit_due=outcome["deposit_due"],
        budget=job["budget"] or None,
    )
    if outcome["dead_end"]:
        log_event(STREAM, "dead_end", source="quote", reason=outcome["dead_end"], quote_id=quote_id, inputs=job, notes=outcome["notes"])
    request_url = None
    if outcome["status"] not in DEAD_STATUSES:
        request_url = link("/request", **job_query(job), quote_id=quote_id)
    if as_json:
        return JSONResponse(
            {
                "quote_id": quote_id,
                "business": NAME,
                "issued_at": issued.isoformat(),
                "expires_at": expires.isoformat(),
                "expiry_note": "This expiry is this site's own limit. The owner hasn't stated how long a quoted price stays valid, and a quote doesn't hold a slot.",
                "inputs": job,
                "summary": headline(outcome),
                **{key: value for key, value in outcome.items() if key != "dead_end"},
                "facts_used": [
                    {"id": fid, "statement": FACT[fid]["statement"], "confirmed_on": FACT[fid]["confirmed_on"]}
                    for fid in outcome["fact_ids"]
                    if fid in FACT
                ],
                "request_url": f"{BASE_URL}{request_url}" if request_url else None,
            }
        )
    next_html = (
        f'<p><a href="{esc(request_url)}">Open the request form with these details</a>. Contact details are asked for only there.</p>'
        if request_url
        else '<p>This can\'t go ahead as a request as entered. A question for the owner can go through <a href="/ask">/ask</a>.</p>'
    )
    body = (
        f"<h1>Quote {esc(quote_id)} from {esc(NAME)}</h1>"
        + outcome_html(outcome)
        + f"<h2>Quote ID and expiry</h2><p>Quote ID {esc(quote_id)} was issued on {esc(stamp(issued))} and expires on {esc(stamp(expires))}. "
        "This expiry is this site's own limit, because the owner hasn't stated how long a quoted price stays valid. A quote doesn't hold a slot.</p>"
        + next_html
        + "<h2>Rules behind this answer</h2>"
        + facts_used_html(outcome["fact_ids"])
        + "<h2>Change the details</h2>"
        + quote_form(job)
    )
    return page(f"Quote {quote_id}: {NAME}", body)


@app.get("/request")
async def request_get(request: Request):
    params = await read_params(request)
    job = parse_job(params)
    body = f"<h1>Send a request to {esc(NAME)}</h1>" + request_form(job, params)
    return page(f"Request: {NAME}", body)


@app.post("/request")
async def request_post(request: Request):
    params = await read_params(request)
    job = parse_job(params)
    as_json = first(params, "format").lower() == "json"
    details = {
        "name": first(params, "name"),
        "email": first(params, "email"),
        "phone": first(params, "phone"),
        "address": first(params, "address"),
        "submitted_by": normalise_who(first(params, "submitted_by")),
        "agent_name": first(params, "agent_name"),
        "notes": first(params, "notes"),
        "quote_id": first(params, "quote_id"),
        "request_type": first(params, "request_type").lower() or ("booking" if job["when"] else "quote"),
    }
    errors = []
    if not details["name"]:
        errors.append("A name is needed.")
    if not details["email"] and not details["phone"]:
        errors.append("An email address or phone number is needed, because the owner replies by text or email.")
    if not details["submitted_by"]:
        errors.append("Who's submitting is needed: the customer, or an agent acting for them.")
    if errors:
        log_event(STREAM, "request", id=None, inputs=job, **details, outcome="rejected_missing_details", errors=errors)
        if as_json:
            return JSONResponse({"outcome": "rejected_missing_details", "errors": errors}, status_code=422)
        body = f"<h1>Send a request to {esc(NAME)}</h1>" + request_form(job, params, errors)
        return page(f"Request: {NAME}", body, status_code=422)

    outcome = evaluate(job)
    shared = dict(
        inputs=job,
        **details,
        quote_status=outcome["status"],
        total=outcome["total"],
        estimate_range=outcome["estimate_range"],
        deposit_due=outcome["deposit_due"],
        still_needed=outcome["still_needed"],
        notes_from_quote=outcome["notes"],
        slot_held=False,
    )
    if outcome["status"] in DEAD_STATUSES:
        log_event(STREAM, "request", id=None, outcome=f"refused_{outcome['status']}", **shared)
        log_event(STREAM, "dead_end", source="request", reason=outcome["status"], inputs=job, notes=outcome["notes"])
        if as_json:
            return JSONResponse(
                {"outcome": f"refused_{outcome['status']}", "summary": headline(outcome), "notes": outcome["notes"]}, status_code=422
            )
        body = (
            f"<h1>This request wasn't sent</h1>{outcome_html(outcome)}"
            "<h2>The rules behind this</h2>"
            + facts_used_html(outcome["fact_ids"])
            + '<p>The details can be changed below. A question for the owner can go through <a href="/ask">/ask</a>.</p>'
            + request_form(job, params, ["The job as entered can't be booked."])
        )
        return page(f"Request not sent: {NAME}", body, status_code=422)

    if outcome["dead_end"]:
        log_event(STREAM, "dead_end", source="request", reason=outcome["dead_end"], inputs=job, notes=outcome["notes"])
    request_id = "req-" + secrets.token_hex(8)
    log_event(STREAM, "request", id=request_id, outcome="received", **shared)
    status_path = f"/r/{request_id}"
    if as_json:
        return JSONResponse(
            {
                "id": request_id,
                "outcome": "received",
                "status_url": f"{BASE_URL}{status_path}",
                "slot_held": False,
                "summary": headline(outcome),
                "total": outcome["total"],
                "still_needed": outcome["still_needed"],
                "what_happens_next": [FACT["next_step.reply"]["statement"], FACT["next_step.slot-not-held"]["statement"]],
            }
        )
    body = (
        f"<h1>Request received by {esc(NAME)}</h1>"
        f'<p class="answer">Request {esc(request_id)} was received, and no slot is held yet.</p>'
        f'<p>Status page: <a href="{esc(status_path)}">{esc(BASE_URL + status_path)}</a></p>'
        + outcome_html(outcome)
        + "<h2>What happens next</h2>"
        + facts_used_html(["next_step.reply", "next_step.slot-not-held", "policies.deposit"])
    )
    return page(f"Request received: {NAME}", body)


@app.get("/ask")
async def ask_get(request: Request):
    params = await read_params(request)
    body = (
        f"<h1>Ask {esc(NAME)} a question</h1>"
        "<p>This passes a question to the owner and returns a status page. It doesn't generate an answer, and it needs no contact details. "
        'The rules this site already holds are on <a href="/">the main page</a>.</p>' + ask_form(first(params, "question", "q"))
    )
    return page(f"Ask: {NAME}", body)


@app.post("/ask")
async def ask_post(request: Request):
    params = await read_params(request)
    text = first(params, "question", "q")
    as_json = first(params, "format").lower() == "json"
    if not text:
        if as_json:
            return JSONResponse({"outcome": "rejected_empty", "errors": ["A question is needed."]}, status_code=422)
        return page(f"Ask: {NAME}", f"<h1>Ask {esc(NAME)} a question</h1>" + ask_form(error="A question is needed."), status_code=422)
    question_id = "ask-" + secrets.token_hex(8)
    log_event(STREAM, "question", id=question_id, text=text)
    status_path = f"/r/{question_id}"
    if as_json:
        return JSONResponse({"id": question_id, "outcome": "passed_to_owner", "status_url": f"{BASE_URL}{status_path}"})
    body = (
        f"<h1>Question passed to {esc(BIZ['owner'])}</h1>"
        f'<p class="answer">Question {esc(question_id)} was passed to the owner.</p>'
        f'<p>Status page: <a href="{esc(status_path)}">{esc(BASE_URL + status_path)}</a></p>'
    )
    return page(f"Question received: {NAME}", body)


@app.get("/r/{record_id}")
def status_page(record_id: str):
    record = find_record(record_id)
    if not record:
        return page("Not found", "<h1>No request or question has this ID</h1>", status_code=404)
    body = request_status_html(record) if record["event"] == "request" else question_status_html(record)
    return page(f"Status {record_id}: {NAME}", body)


@app.get("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", media_type="text/plain")


@app.get("/sitemap.xml")
def sitemap():
    paths = ["/", "/index.md", "/services", *(f"/services/{key}" for key in [*SERVICES, *ADDONS]), "/quote", "/request", "/ask"]
    entries = "".join(f"<url><loc>{esc(BASE_URL + path)}</loc></url>" for path in paths)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>'
    return Response(xml, media_type="application/xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8103)
