"""The booking flow, kept from the first build. Everything else in demo_site is new.

Step 1: GET /book shows a lead form. POST /book takes name, email, phone and address,
all required, and only then shows step 2.
Step 2: the rolling calendar from legible_core.slots. POST /book/request takes the same four
lead fields again (as hidden inputs) plus package, vehicle, addons (repeatable), notes
and slot, where slot is "<date>|<window>" taken from a window's "value".
Step 3: the thanks page. There's no status page.

Templates the site must provide, with the context each receives:
  book_step1.html: lead (dict), error (str or None)
  book_step2.html: lead, days, has_open, error, packages, addons, values
      days is a list of {label, saturday, windows: [{value, label, time, open, evening}]}
  book_done.html: nothing beyond the site's globals

Call register_booking(app, stream, render, packages, addons), where
render(request, template_name, status_code=200, **context) returns a response.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from legible_core.business import slots
from legible_core.logbook import log_event

WINDOW_LABELS = {"morning": "Morning", "afternoon": "Afternoon", "evening": "Evening"}


def clock(hhmm: str) -> str:
    hour, minute = (int(part) for part in hhmm.split(":"))
    suffix = "am" if hour < 12 else "pm"
    return f"{hour % 12 or 12}:{minute:02d} {suffix}"


def calendar_days() -> list[dict]:
    """Group the rolling arrival windows by date for the step 2 calendar."""
    days: dict[str, dict] = {}
    for slot in slots("cormorant"):
        day = date.fromisoformat(slot["date"])
        entry = days.setdefault(
            slot["date"],
            {
                "label": f"{day.strftime('%a')} {day.strftime('%b')} {day.day}",
                "saturday": slot["weekday"] == "Saturday",
                "windows": [],
            },
        )
        entry["windows"].append(
            {
                "value": f"{slot['date']}|{slot['window']}",
                "label": WINDOW_LABELS.get(slot["window"], slot["window"].title()),
                "time": f"{clock(slot['start'])} to {clock(slot['end'])}",
                "open": slot["open"],
                "evening": slot["window"] == "evening",
            }
        )
    return list(days.values())


def open_slot_values() -> set[str]:
    return {f"{s['date']}|{s['window']}" for s in slots("cormorant") if s["open"]}


def clean(form, name: str) -> str:
    return str(form.get(name, "")).strip()


def lead_fields(form) -> dict:
    return {key: clean(form, key) for key in ("name", "email", "phone", "address")}


def register_booking(app: FastAPI, stream: str, render: Callable, packages: list[str], addons: list[str]) -> None:
    def step_two(request: Request, lead: dict, error: str | None = None, values: dict | None = None):
        days = calendar_days()
        has_open = any(w["open"] for day in days for w in day["windows"])
        if not has_open:
            log_event(stream, "dead_end", reason="no open slot", path=str(request.url.path), email=lead.get("email"))
        return render(
            request,
            "book_step2.html",
            lead=lead,
            days=days,
            has_open=has_open,
            error=error,
            packages=packages,
            addons=addons,
            values=values or {},
        )

    @app.get("/book", response_class=HTMLResponse)
    async def book(request: Request):
        return render(request, "book_step1.html", lead={}, error=None)

    @app.post("/book", response_class=HTMLResponse)
    async def book_lead(request: Request):
        form = await request.form()
        lead = lead_fields(form)
        complete = all(lead.values()) and "@" in lead["email"]
        log_event(stream, "lead_form", form="book", complete=complete, **lead)
        if not complete:
            return render(
                request, "book_step1.html", status_code=422, lead=lead, error="Please fill in all four fields so we can continue."
            )
        return step_two(request, lead)

    @app.get("/book/request")
    async def book_request_get():
        return RedirectResponse("/book", status_code=303)

    @app.post("/book/request", response_class=HTMLResponse)
    async def book_request(request: Request):
        form = await request.form()
        lead = lead_fields(form)
        values = {
            "package": clean(form, "package"),
            "vehicle": clean(form, "vehicle"),
            "addons": [str(item) for item in form.getlist("addons")],
            "notes": clean(form, "notes"),
            "slot": clean(form, "slot"),
        }
        slot_date, _, slot_window = values["slot"].partition("|")
        missing = [key for key in ("package", "vehicle", "slot") if not values[key]]
        is_open = values["slot"] in open_slot_values()
        outcome = "received" if not missing and is_open else ("incomplete" if missing else "slot_unavailable")
        log_event(
            stream,
            "request",
            **lead,
            package=values["package"],
            vehicle=values["vehicle"],
            addons=values["addons"],
            notes=values["notes"],
            slot_date=slot_date or None,
            slot_window=slot_window or None,
            outcome=outcome,
        )
        if outcome == "incomplete":
            return step_two(request, lead, error="Please choose a package, tell us your vehicle and pick an arrival window.", values=values)
        if outcome == "slot_unavailable":
            log_event(
                stream, "dead_end", reason="chosen slot not available", path="/book/request", email=lead.get("email"), slot=values["slot"]
            )
            return step_two(request, lead, error="That arrival window isn't available. Please pick another.", values=values)
        return render(request, "book_done.html")
