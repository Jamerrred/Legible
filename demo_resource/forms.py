"""The quote, request and ask forms, and the status pages for what they send."""

from __future__ import annotations

from datetime import datetime

from demo_resource.config import ADDONS, BIZ, CONDITIONS, MODEL, SERVICES, STREAM, TZ
from demo_resource.content import facts_used_html
from demo_resource.formatting import esc, money, service_name, stamp
from demo_resource.quoting import evaluate, first, headline, needed_word
from legible_core.logbook import read_events


def option(value: str, label: str, current: str) -> str:
    selected = " selected" if value == current else ""
    return f'<option value="{esc(value)}"{selected}>{esc(label)}</option>'


def select_field(name: str, label: str, choices: list[tuple[str, str]], current: str) -> str:
    known = [value for value, _ in choices]
    options = option("", "Not chosen", current) + "".join(option(value, text, current) for value, text in choices)
    if current and current not in known:
        options += option(current, current, current)
    return f'<label for="{name}">{esc(label)}</label><select id="{name}" name="{name}">{options}</select>'


def text_field(name: str, label: str, value: str = "", kind: str = "text", hint: str = "") -> str:
    hint_html = f' placeholder="{esc(hint)}"' if hint else ""
    return f'<label for="{name}">{esc(label)}</label><input type="{kind}" id="{name}" name="{name}" value="{esc(value)}"{hint_html}>'


def checks(name: str, legend: str, entries: dict, current: list[str]) -> str:
    boxes = "".join(
        f'<div><input type="checkbox" id="{name}-{esc(key)}" name="{name}" value="{esc(key)}"{" checked" if key in current else ""}> '
        f'<label class="inline" for="{name}-{esc(key)}">{esc(value["label"])}</label></div>'
        for key, value in entries.items()
    )
    extras = "".join(
        f'<div><input type="hidden" name="{name}" value="{esc(item)}">Also entered: {esc(item)}</div>'
        for item in current
        if item not in entries
    )
    return f"<fieldset><legend>{esc(legend)}</legend>{boxes}{extras}</fieldset>"


def job_fields(job: dict) -> str:
    return "".join(
        [
            select_field("service", "Service", [(key, service_name(key)) for key in SERVICES], job["service"]),
            select_field("size", "Size class", [(key, value["label"]) for key, value in MODEL["sizes"].items()], job["size"]),
            text_field("vehicle", "Vehicle make and model, or type", job["vehicle"]),
            checks("addons", "Add-ons", ADDONS, job["addons"]),
            checks("conditions", "Conditions that apply", CONDITIONS, job["conditions"]),
            text_field("zip", "ZIP code", job["zip"]),
            text_field("when", "Date, with an optional window", job["when"], hint="YYYY-MM-DD morning"),
            select_field(
                "recurring", "Recurring plan", [(key, key.replace("-", " ")) for key in MODEL["recurring"]["frequencies"]], job["recurring"]
            ),
            text_field("vehicle_count", "Number of vehicles", job["vehicle_count"], kind="number"),
            text_field("budget", "Budget in US dollars", job["budget"]),
        ]
    )


def quote_form(job: dict) -> str:
    return f'<form method="get" action="/quote">{job_fields(job)}<br><button type="submit">Work out the total</button></form>'


def request_form(job: dict, params: dict, errors: list[str] | None = None) -> str:
    """Contact fields refill only from a POST, so personal details never come from a link."""
    posted = params if errors else {}
    who = first(posted, "submitted_by")
    request_type = first(params, "request_type") or ("booking" if job["when"] else "quote")
    error_html = ""
    if errors:
        error_html = (
            '<div class="error"><p>This request wasn\'t sent yet:</p><ul>'
            + "".join(f"<li>{esc(item)}</li>" for item in errors)
            + "</ul></div>"
        )
    summary = ""
    if any(job.values()):
        summary = f"<p>For the details below: {esc(headline(evaluate(job)))}</p>"
    return (
        f"{error_html}{summary}"
        + facts_used_html(["next_step.slot-not-held", "next_step.reply"])
        + '<form method="post" action="/request">'
        + f'<input type="hidden" name="quote_id" value="{esc(first(params, "quote_id"))}">'
        + "<fieldset><legend>Kind of request</legend>"
        + f'<div><input type="radio" id="type-booking" name="request_type" value="booking"{" checked" if request_type == "booking" else ""}> <label class="inline" for="type-booking">Booking request</label></div>'
        + f'<div><input type="radio" id="type-quote" name="request_type" value="quote"{" checked" if request_type == "quote" else ""}> <label class="inline" for="type-quote">Quote request</label></div>'
        + "</fieldset><h2>The job</h2>"
        + job_fields(job)
        + "<h2>Contact details</h2><p>A name is needed, plus an email address or phone number, because the owner replies by text or email.</p>"
        + text_field("name", "Name", first(posted, "name"))
        + text_field("email", "Email", first(posted, "email"), kind="email")
        + text_field("phone", "Phone", first(posted, "phone"), kind="tel")
        + text_field("address", "Address where the vehicle is parked", first(posted, "address"))
        + "<fieldset><legend>Who's submitting</legend>"
        + f'<div><input type="radio" id="who-customer" name="submitted_by" value="customer"{" checked" if who == "customer" else ""}> <label class="inline" for="who-customer">The customer</label></div>'
        + f'<div><input type="radio" id="who-agent" name="submitted_by" value="agent"{" checked" if who == "agent" else ""}> <label class="inline" for="who-agent">An agent acting for the customer</label></div>'
        + text_field("agent_name", "Name of the agent, if one is submitting", first(posted, "agent_name"))
        + "</fieldset>"
        + '<label for="notes">Anything else about the job</label>'
        + f'<textarea id="notes" name="notes" rows="3">{esc(first(posted, "notes"))}</textarea>'
        + '<br><button type="submit">Send request</button></form>'
    )


def normalise_who(text: str) -> str:
    lowered = text.lower()
    if "agent" in lowered:
        return "agent"
    if "customer" in lowered:
        return "customer"
    return ""


def ask_form(question: str = "", error: str = "") -> str:
    error_html = f'<div class="error"><p>{esc(error)}</p></div>' if error else ""
    return (
        f"{error_html}"
        '<form method="post" action="/ask"><label for="question">Question</label>'
        f'<textarea id="question" name="question" rows="5">{esc(question)}</textarea>'
        '<br><button type="submit">Pass this to the owner</button></form>'
    )


def find_record(record_id: str) -> dict | None:
    for event in reversed(read_events(STREAM)):
        if event.get("event") in ("request", "question") and event.get("id") == record_id:
            return event
    return None


def request_status_html(record: dict) -> str:
    job = record.get("inputs", {})
    rows = [
        ("Kind", f"{record.get('request_type', 'request')} request"),
        ("Service", job.get("service")),
        ("Size class", job.get("size")),
        ("Vehicle", job.get("vehicle")),
        ("Add-ons", ", ".join(job.get("addons", []))),
        ("Conditions", ", ".join(job.get("conditions", []))),
        ("ZIP code", job.get("zip")),
        ("Date and window asked for", job.get("when")),
        ("Number of vehicles", job.get("vehicle_count")),
        ("Recurring plan", job.get("recurring")),
        ("Quote ID", record.get("quote_id")),
        ("Total at the time of the request", money(record["total"]) if record.get("total") is not None else None),
        ("Deposit to book", money(record["deposit_due"]) if record.get("deposit_due") is not None else None),
        ("Submitted by", "An agent acting for the customer" if record.get("submitted_by") == "agent" else "The customer"),
    ]
    table = "".join(f"<tr><td>{esc(label)}</td><td>{esc(value)}</td></tr>" for label, value in rows if value)
    still = record.get("still_needed") or []
    still_html = ""
    if still:
        still_html = "<h2>Still needed</h2><ul>" + "".join(f"<li>{esc(needed_word(item))}</li>" for item in still) + "</ul>"
    return (
        f"<h1>Status of request {esc(record['id'])}</h1>"
        f'<p class="answer">Received on {esc(stamp(datetime.fromisoformat(record["ts"]).astimezone(TZ)))}, and waiting for the owner\'s reply. No slot is held.</p>'
        f'<div class="wrap"><table><tbody>{table}</tbody></table></div>{still_html}'
        "<p>Contact details aren't shown on this page.</p>"
        "<h2>What happens next</h2>" + facts_used_html(["next_step.reply", "next_step.slot-not-held", "policies.deposit"])
    )


def question_status_html(record: dict) -> str:
    return (
        f"<h1>Status of question {esc(record['id'])}</h1>"
        f'<p class="answer">This question was passed to the owner, {esc(BIZ["owner"])}, on {esc(stamp(datetime.fromisoformat(record["ts"]).astimezone(TZ)))}. No answer has been posted here yet.</p>'
        f"<h2>The question</h2><blockquote>{esc(record.get('text', ''))}</blockquote>"
        "<p>The owner's stated reply time of 4 business hours is for requests. She hasn't stated a reply time for questions.</p>"
    )
