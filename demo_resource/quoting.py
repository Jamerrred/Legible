"""Reading a job from a request, then pricing it and checking its availability and budget."""

from __future__ import annotations

import re
from datetime import date, timedelta

from fastapi import Request

from demo_resource.config import (
    CONDITIONS,
    DEAD_STATUSES,
    MODEL,
    NEEDS_SIZE,
    RULES,
    SERVICES,
    SIZES,
    SLOT_DAYS,
    SLUG,
    ZONES,
)
from demo_resource.formatting import esc, local_now, long_date, money, usd, words
from legible_core.business import quote, slots

# ---------------------------------------------------------------- reading input


async def read_params(request: Request) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for key, value in request.query_params.multi_items():
        merged.setdefault(key, []).append(value)
    if request.method == "POST":
        if "json" in request.headers.get("content-type", ""):
            try:
                body = await request.json()
            except ValueError:
                body = {}
            if isinstance(body, dict):
                for key, value in body.items():
                    values = value if isinstance(value, list) else [value]
                    merged.setdefault(key, []).extend(str(item) for item in values if item is not None)
        else:
            form = await request.form()
            for key, value in form.multi_items():
                if isinstance(value, str):
                    merged.setdefault(key, []).append(value)
    return merged


def first(params: dict, *names: str) -> str:
    for name in names:
        for value in params.get(name, []):
            if value.strip():
                return value.strip()
    return ""


def many(params: dict, *names: str) -> list[str]:
    found: list[str] = []
    for name in names:
        for value in params.get(name, []):
            for part in value.split(","):
                part = part.strip()
                if part and part not in found:
                    found.append(part)
    return found


def parse_job(params: dict) -> dict:
    when = first(params, "when") or " ".join(part for part in (first(params, "date"), first(params, "window")) if part)
    return {
        "service": first(params, "service"),
        "size": first(params, "size"),
        "vehicle": first(params, "vehicle"),
        "addons": many(params, "addons", "addon"),
        "conditions": many(params, "conditions", "condition"),
        "zip": first(params, "zip", "zip_code"),
        "when": when,
        "recurring": first(params, "recurring"),
        "vehicle_count": first(params, "vehicle_count", "vehicles"),
        "budget": first(params, "budget"),
    }


def job_query(job: dict) -> dict:
    """The job as link parameters."""
    out = {key: value for key, value in job.items() if value}
    for key in ("addons", "conditions"):
        if key in out:
            out[key] = ",".join(out[key])
    return out


# ---------------------------------------------------------------- availability


def slot_fits(slot: dict, service_id: str | None) -> bool:
    if slot["window"] == "evening" and service_id and service_id not in RULES["evening"]["services"]:
        return False
    if service_id == "flagship":
        flagship = RULES["flagship"]
        return slot["weekday"] in flagship["weekdays"] and slot["window"] == flagship["window"]
    return True


def open_slots(service_id: str | None = None) -> list[dict]:
    return [slot for slot in slots(SLUG, days=SLOT_DAYS) if slot["open"] and slot_fits(slot, service_id)]


# ---------------------------------------------------------------- quoting


def run_quote(job: dict, **override) -> dict:
    data = {**job, **override}
    try:
        count = int(data["vehicle_count"] or 1)
    except ValueError:
        count = 1
    return quote(
        SLUG,
        service=data["service"] or None,
        size=data["size"] or None,
        addons=tuple(data["addons"]),
        zip_code=data["zip"] or None,
        conditions=tuple(data["conditions"]),
        when=data["when"] or None,
        vehicle=data["vehicle"] or None,
        recurring=data["recurring"] or None,
        vehicle_count=count,
    )


def candidate_sizes(vehicle: str) -> list[str]:
    text = vehicle.lower()
    for term, entry in MODEL["vehicles"]["ambiguous"].items():
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text):
            return [fact_id.split(".")[1] for fact_id in entry["fact_ids"]]
    return SIZES


def estimate_range(job: dict, result: dict) -> dict | None:
    """When only the size or ZIP code is missing, the range the total could fall in."""
    missing = set(result["still_needed"])
    if result["status"] != "needs_info" or not missing or not missing <= {"zip_code", NEEDS_SIZE}:
        return None
    sizes = candidate_sizes(job["vehicle"]) if NEEDS_SIZE in missing else [job["size"]]
    zips = [zone["zips"][0] for zone in ZONES.values()] if "zip_code" in missing else [job["zip"]]
    lows, highs = [], []
    for size in sizes:
        for zip_code in zips:
            attempt = run_quote(job, size=size, zip=zip_code)
            total = attempt["total"]
            if attempt["status"] != "ok" or total is None:
                continue
            lows.append(total["low"] if isinstance(total, dict) else total)
            highs.append(total["high"] if isinstance(total, dict) else total)
    if not lows:
        return None
    varies = []
    if NEEDS_SIZE in missing:
        varies.append("the vehicle's size class")
    if "zip_code" in missing:
        varies.append("the ZIP code's travel fee")
    return {"low": min(lows), "high": max(highs), "varies_by": varies}


def cited_service(result: dict) -> str | None:
    for fact_id in result["fact_ids"]:
        if fact_id.startswith("services.") and fact_id.split(".")[1] in SERVICES:
            return fact_id.split(".")[1]
    return None


def availability_for(job: dict, result: dict) -> dict | None:
    text = job["when"].strip().lower()
    if not text or result["status"] in DEAD_STATUSES:
        return None
    head = text.split()[0]
    today = local_now().date()
    if head == "tomorrow":
        day = today + timedelta(days=1)
    else:
        try:
            day = date.fromisoformat(head[:10])
        except ValueError:
            return None
    days_out = (day - today).days
    if days_out <= 0 or days_out > 400:
        return None
    window = next((name for name in RULES["windows"] if name in text), None)
    service_id = cited_service(result)
    long_job = any(
        float(match.group(1)) * 60 >= RULES["morning_only_min_minutes"]
        for match in (re.search(r"about ([\d.]+) hour", note) for note in result["notes"])
        if match
    )
    listed = [slot for slot in slots(SLUG, days=days_out + 1) if slot["date"] == day.isoformat()]
    if window:
        listed = [slot for slot in listed if slot["window"] == window]
    fits = [slot for slot in listed if slot["open"] and slot_fits(slot, service_id) and (not long_job or slot["window"] == "morning")]
    return {"date": day.isoformat(), "window": window, "open_windows": [slot["window"] for slot in fits], "has_open": bool(fits)}


def dead_end_reason(job: dict, result: dict, availability: dict | None) -> str | None:
    if result["status"] in DEAD_STATUSES:
        return result["status"]
    if any("currently shows as booked" in note for note in result["notes"]):
        return "no_slot"
    if availability and not availability["has_open"]:
        return "no_slot"
    if NEEDS_SIZE in result["still_needed"] and (job["size"] or job["vehicle"]):
        return "no_match"
    if any(item.startswith("the owner") for item in result["still_needed"]):
        return "owner_undecided"
    return None


def budget_check(job: dict, result: dict, estimate: dict | None) -> str | None:
    cleaned = re.sub(r"[^\d.]", "", job["budget"])
    try:
        budget = float(cleaned)
    except ValueError:
        return None
    total = result["total"] if result["total"] is not None else estimate
    if total is None:
        return None
    low, high = (total["low"], total["high"]) if isinstance(total, dict) else (total, total)
    if high <= budget:
        return f"This is within the stated budget of {usd(budget)}."
    if low > budget:
        return (
            f"This is {usd(low - budget)} or more over the stated budget of {usd(budget)}."
            if low != high
            else f"This is {usd(low - budget)} over the stated budget of {usd(budget)}."
        )
    return f"The stated budget of {usd(budget)} falls inside this range."


def evaluate(job: dict) -> dict:
    result = run_quote(job)
    notes = list(result["notes"])
    if job["vehicle_count"] and not job["vehicle_count"].lstrip("-").isdigit():
        notes.append(f"'{job['vehicle_count']}' isn't a whole number, so this was worked out for 1 vehicle.")
    estimate = estimate_range(job, result)
    availability = availability_for(job, result)
    next_open = []
    if availability and not availability["has_open"]:
        where = f"{long_date(availability['date'])}" + (f" in the {availability['window']} window" if availability["window"] else "")
        notes.append(f"No arrival window that fits this job is open on {where}.")
    reason = dead_end_reason(job, result, availability)
    if reason == "no_slot":
        next_open = [
            {"date": slot["date"], "weekday": slot["weekday"], "window": slot["window"]} for slot in open_slots(cited_service(result))[:3]
        ]
    return {
        **result,
        "notes": notes,
        "estimate_range": estimate,
        "availability": availability,
        "next_open": next_open,
        "budget": job["budget"] or None,
        "budget_check": budget_check(job, result, estimate),
        "dead_end": reason,
    }


def headline(outcome: dict) -> str:
    status, total = outcome["status"], outcome["total"]
    if status == "ok" and isinstance(total, dict):
        return f"The total for this job is a range of {money(total)}, including tax and travel."
    if status == "ok":
        return f"The total for this job is {money(total)}, including tax and travel."
    if status == "needs_info":
        estimate = outcome["estimate_range"]
        if estimate:
            return (
                f"There's no single total yet. It would be between {usd(estimate['low'])} and {usd(estimate['high'])}, "
                f"depending on {words(estimate['varies_by'])}."
            )
        return "There's no total yet, because something is still needed."
    if status == "not_offered":
        return "This job isn't offered."
    if status == "out_of_area":
        return "This ZIP code is outside the service area."
    return "This combination can't be booked as entered."


NEEDED_WORDS = {
    "zip_code": "the ZIP code (zip)",
    "service": "the service (service)",
    NEEDS_SIZE: "the vehicle's size class (size), or its make and model (vehicle)",
    "when, as a date and optionally a window": "the date, as YYYY-MM-DD with an optional window (when)",
}


def needed_word(item: str) -> str:
    return NEEDED_WORDS.get(item, item)


def outcome_html(outcome: dict) -> str:
    """Lines, notes and needs for a quote. All of it is escaped, since notes can repeat input."""
    parts = [f'<p class="answer">{esc(headline(outcome))}</p>']
    if outcome["budget_check"]:
        parts.append(f"<p>{esc(outcome['budget_check'])}</p>")
    if outcome["lines"]:
        rows = "".join(f"<tr><td>{esc(line['label'])}</td><td>{esc(money(line['amount']))}</td></tr>" for line in outcome["lines"])
        if outcome["status"] == "ok":
            rows += f"<tr><td>Subtotal</td><td>{esc(money(outcome['subtotal']))}</td></tr>"
            rows += f"<tr><td>Sales tax</td><td>{esc(money(outcome['tax']))}</td></tr>"
            rows += f"<tr><td><strong>Total</strong></td><td><strong>{esc(money(outcome['total']))}</strong></td></tr>"
        parts.append(
            f'<h2>Line items</h2><div class="wrap"><table><thead><tr><th>Item</th><th>Amount</th></tr></thead><tbody>{rows}</tbody></table></div>'
        )
    if outcome["deposit_due"] is not None:
        parts.append(f"<p>Deposit to book: {esc(money(outcome['deposit_due']))}, which counts toward the total.</p>")
    if outcome["conditions_applied"]:
        labels = [CONDITIONS[item]["label"] for item in outcome["conditions_applied"] if item in CONDITIONS]
        parts.append(f"<h2>Conditions applied</h2><p>{esc(words(labels))}.</p>")
    if outcome["still_needed"]:
        parts.append(
            "<h2>Still needed</h2><ul>" + "".join(f"<li>{esc(needed_word(item))}</li>" for item in outcome["still_needed"]) + "</ul>"
        )
    if outcome["notes"]:
        parts.append("<h2>Notes</h2><ul>" + "".join(f"<li>{esc(note)}</li>" for note in outcome["notes"]) + "</ul>")
    if outcome["next_open"]:
        parts.append(
            "<h2>Next open windows that fit</h2><ul>"
            + "".join(
                f"<li>{esc(slot['weekday'])} {esc(long_date(slot['date']))}, {esc(slot['window'])} window</li>"
                for slot in outcome["next_open"]
            )
            + "</ul>"
        )
    return "".join(parts)
