"""Read a business's facts file and work out availability and quotes from its rules.

The module has no business data of its own. It reads businesses/<slug>/facts.json and
applies `availability_rules` and `pricing_model`.

Money in `quote()` results is a plain number, or {"low": x, "high": y} where the facts
say the price is a range. Subtotal, tax and total are None unless status is "ok".
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

BUSINESSES_DIR = Path(__file__).resolve().parent.parent / "businesses"
CENT = Decimal("0.01")
STATUS_ORDER = ("not_offered", "out_of_area", "invalid_combination", "needs_info", "ok")


def load_facts(slug="sunrise"):
    """Return the parsed facts file for one business."""
    with (BUSINESSES_DIR / slug / "facts.json").open(encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------- dates and slots


def _local_now(tz, now):
    if now is None:
        return datetime.now(tz)
    if isinstance(now, str):
        now = datetime.fromisoformat(now)
    if not isinstance(now, datetime):
        now = datetime.combine(now, time(0, 0))
    return now.replace(tzinfo=tz) if now.tzinfo is None else now.astimezone(tz)


def _at(day, hhmm, tz):
    return datetime.combine(day, time.fromisoformat(hhmm), tz)


def _blackout(rules, day):
    iso = day.isoformat()
    for item in rules["blackout_ranges"]:
        if item["start"] <= iso <= item["end"]:
            return item
    return None


def _is_booked(rules, day, window, days_out):
    """Stable across processes: the score depends only on the date and the window.

    The booked share grows as a date gets closer, so a slot can fill up as time passes
    but a booked slot never reopens.
    """
    model = rules["booked_model"]
    digest = hashlib.sha256(f"{model['salt']}|{day.isoformat()}|{window}".encode()).digest()
    score = int.from_bytes(digest[:8], "big") / 2**64
    share = model["base_share"][window]
    for tier in model["near_term_bumps"]:
        if days_out <= tier["within_days"]:
            share += tier["add"]
            break
    return score < share


def slots(slug="sunrise", now=None, days=21):
    """List arrival windows for the next `days` calendar days, starting today.

    Closed weekdays and blackout dates are left out. Windows inside the lead time and
    windows already booked are listed with "open": False.
    """
    rules = load_facts(slug)["availability_rules"]
    tz = ZoneInfo(rules["timezone"])
    current = _local_now(tz, now)
    earliest = current + timedelta(hours=rules["lead_time_hours"])
    listed = []
    for days_out in range(days):
        day = current.date() + timedelta(days=days_out)
        weekday = day.strftime("%A")
        if weekday in rules["closed_weekdays"] or _blackout(rules, day):
            continue
        for name in rules["weekday_windows"].get(weekday, []):
            window = rules["windows"][name]
            is_open = _at(day, window["start"], tz) >= earliest and not _is_booked(rules, day, name, days_out)
            listed.append(
                {
                    "date": day.isoformat(),
                    "weekday": weekday,
                    "window": name,
                    "start": window["start"],
                    "end": window["end"],
                    "open": is_open,
                }
            )
    return listed


# ---------------------------------------------------------------- matching words


def _norm(text):
    return re.sub(r"\s+", " ", str(text).strip().lower().replace("_", " "))


def _find(text, terms):
    """Return the longest term found in text as whole words, or None."""
    for term in sorted(terms, key=len, reverse=True):
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text):
            return term
    return None


def _alias_table(entries):
    table = {}
    for entry_id, entry in entries.items():
        table[_norm(entry_id)] = entry_id
        for alias in entry.get("aliases", []):
            table[_norm(alias)] = entry_id
    return table


def _resolve(text, entries):
    table = _alias_table(entries)
    norm = _norm(text)
    if norm in table:
        return table[norm]
    term = _find(norm, table)
    return table[term] if term else None


def _match_vehicle(model, text):
    """Classify a vehicle description against the facts' vehicle tables."""
    norm = _norm(text)
    vehicles = model["vehicles"]
    term = _find(norm, vehicles["not_offered"])
    if term:
        return {"kind": "not_offered", "term": term, "fact_id": vehicles["not_offered"][term]}
    term = _find(norm, vehicles["undecided"])
    if term:
        return {"kind": "undecided", "term": term, **vehicles["undecided"][term]}
    term = _find(norm, vehicles["camper"]["terms"])
    if term:
        return {"kind": "camper", "term": term, **vehicles["camper"]}
    by_term = {t: size for size, terms in vehicles["by_size"].items() for t in terms}
    term = _find(norm, by_term)
    if term:
        return {"kind": "size", "term": term, "size": by_term[term]}
    term = _find(norm, vehicles["ambiguous"])
    if term:
        return {"kind": "ambiguous", "term": term, **vehicles["ambiguous"][term]}
    return {"kind": "unlisted"}


def _parse_when(when, current, rules):
    """Return (date, window or None), or None if `when` can't be read."""
    windows = rules["windows"]
    if isinstance(when, dict):
        return _parse_when(when.get("date"), current, rules)[0], when.get("window")
    if isinstance(when, datetime):
        when = when.isoformat()
    elif isinstance(when, date):
        return when, None
    text = _norm(when)
    window = _find(text, windows)
    head = text.split()[0] if text else ""
    if head == "today":
        return current.date(), window
    if head == "tomorrow":
        return current.date() + timedelta(days=1), window
    try:
        moment = datetime.fromisoformat(head)
    except ValueError:
        return None
    if "t" in head and window is None:
        clock = moment.strftime("%H:%M")
        window = next((n for n, w in windows.items() if w["start"] <= clock <= w["end"]), "outside")
    return moment.date(), window


# ---------------------------------------------------------------- money


def _money(value):
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def _out(value):
    """Decimal, or a (low, high) pair, to plain JSON numbers."""
    if isinstance(value, tuple):
        return {"low": float(value[0]), "high": float(value[1])}
    return float(value)


def _pair(value):
    return value if isinstance(value, tuple) else (value, value)


def _usd(value):
    return f"${value:,.2f}"


# ---------------------------------------------------------------- quote


def quote(
    slug="sunrise",
    service=None,
    size=None,
    addons=(),
    zip_code=None,
    conditions=(),
    when=None,
    vehicle=None,
    now=None,
    *,
    recurring=None,
    vehicle_count=1,
):
    """Work out the total for a job, or say why it can't be priced yet.

    `recurring` ("every-2-weeks" or "every-4-weeks") and `vehicle_count` are optional
    extras for the recurring plan and fleet rules.
    """
    facts = load_facts(slug)
    model = facts["pricing_model"]
    rules = facts["availability_rules"]
    tz = ZoneInfo(rules["timezone"])
    current = _local_now(tz, now)

    statuses, notes, still_needed, cited, applied = set(), [], [], [], []
    items = []  # dicts of label, amount (Decimal or (low, high)), taxable

    def cite(*ids):
        for fact_id in ids:
            if fact_id not in cited:
                cited.append(fact_id)

    def finish(deposit=None):
        status = next(s for s in STATUS_ORDER if s in statuses or s == "ok")
        result = {
            "status": status,
            "lines": [],
            "subtotal": None,
            "tax": None,
            "total": None,
            "deposit_due": None,
            "conditions_applied": applied,
            "still_needed": still_needed,
            "notes": notes,
            "fact_ids": cited,
        }
        if status in ("ok", "needs_info"):
            result["lines"] = [{"label": item["label"], "amount": _out(item["amount"])} for item in items]
            result["deposit_due"] = float(deposit) if deposit is not None else None
        if status == "ok":
            low, high = Decimal(0), Decimal(0)
            taxable_low, taxable_high = Decimal(0), Decimal(0)
            for item in items:
                item_low, item_high = _pair(item["amount"])
                low += item_low
                high += item_high
                if item["taxable"]:
                    taxable_low += item_low
                    taxable_high += item_high
            rate = Decimal(str(model["tax"]["rate"]))
            tax_low, tax_high = _money(taxable_low * rate), _money(taxable_high * rate)
            if low == high:
                result.update(subtotal=_out(low), tax=_out(tax_low), total=_out(low + tax_low))
            else:
                result.update(
                    subtotal=_out((low, high)),
                    tax=_out((tax_low, tax_high)),
                    total=_out((low + tax_low, high + tax_high)),
                )
        return result

    # Words that name something the business doesn't do decide the answer straight away.
    refused = model["not_offered_terms"]
    for text in (service, *addons, *conditions):
        if text is None:
            continue
        term = _find(_norm(text), refused)
        if term:
            statuses.add("not_offered")
            cite(refused[term]["fact_id"])
            notes.append(refused[term]["note"])
            return finish()

    # Vehicle and size class.
    size_id = _resolve(size, model["sizes"]) if size else None
    if size and not size_id:
        notes.append(f"'{size}' isn't a size class.")
    if size_id:
        cite(f"size_classes.{size_id}")

    camper = None
    undecided_vehicle = False
    condition_texts = list(conditions)
    if vehicle:
        match = _match_vehicle(model, vehicle)
        kind = match["kind"]
        if kind == "not_offered":
            statuses.add("not_offered")
            cite(match["fact_id"])
            notes.append(f"Vehicles described as '{match['term']}' aren't served.")
            return finish()
        if kind == "undecided":
            undecided_vehicle = True
            size_id = None
            cite(match["fact_id"])
            notes.append(match["note"])
            still_needed.append(match["still_needed"])
        elif kind == "camper":
            camper = match
            size_id = match["size"]
            cite(f"size_classes.{size_id}", match["fact_id"])
        elif kind == "size":
            if size_id and size_id != match["size"]:
                notes.append(
                    f"The vehicle '{vehicle}' is {model['sizes'][match['size']]['label']}, so that class is used instead of the size given."
                )
            size_id = match["size"]
            cite(f"size_classes.{size_id}")
        elif kind == "ambiguous":
            if not size_id:
                cite(*match["fact_ids"])
                notes.append(match["note"])
        elif not size_id:
            notes.append(f"'{vehicle}' isn't a listed model, so its size class can't be assumed.")
        if _find(_norm(vehicle), model["matte_terms"]):
            condition_texts.append("matte-or-wrapped")

    # Service and add-ons. A service name that is really an add-on is treated as one.
    service_id = None
    addon_ids = []
    for text in addons:
        addon_id = _resolve(text, model["addons"])
        if addon_id:
            if addon_id not in addon_ids:
                addon_ids.append(addon_id)
        else:
            statuses.add("invalid_combination")
            notes.append(f"'{text}' isn't one of the add-ons.")
    if service is not None:
        service_id = _resolve(service, model["services"])
        if not service_id:
            addon_id = _resolve(service, model["addons"])
            if addon_id:
                if addon_id not in addon_ids:
                    addon_ids.append(addon_id)
            else:
                statuses.add("invalid_combination")
                notes.append(f"'{service}' isn't one of the services.")
    svc = model["services"].get(service_id)
    if service_id:
        cite(f"services.{service_id}", f"pricing.{service_id}")
    has_interior = bool(svc and svc["includes_interior"])
    has_exterior = bool(svc and svc["includes_exterior"])

    # Conditions.
    wanted_conditions = []
    for text in condition_texts:
        condition_id = _resolve(text, model["conditions"])
        if condition_id:
            if condition_id not in wanted_conditions:
                wanted_conditions.append(condition_id)
        else:
            notes.append(f"'{text}' isn't a defined condition, so nothing was charged for it.")
    for condition_id in wanted_conditions:
        condition = model["conditions"][condition_id]
        if condition.get("forces_addon") and has_interior and condition["forces_addon"] not in addon_ids:
            addon_ids.append(condition["forces_addon"])
            notes.append(f"{condition['label']} also needs the {condition['forces_addon']} add-on, so it was added.")

    # Recurring plan and fleet counts.
    count = int(vehicle_count or 1)
    if count < 1:
        statuses.add("invalid_combination")
        notes.append("vehicle_count must be at least 1.")
        count = 1
    fleet = model["fleet"]
    discount_pct = Decimal(0)
    discount_label = None
    if count > fleet["max_priced_vehicles"]:
        cite("fleet.over-10")
        still_needed.append("the owner's price for more than 10 vehicles, which hasn't been set")
    elif count >= fleet["min_vehicles"]:
        cite("fleet.discount", "fleet.terms", "prerequisites.water")
        notes.append("Jobs of 3 or more vehicles need a working spigot within 100 feet.")
        if service_id and service_id not in fleet["services"]:
            statuses.add("invalid_combination")
            notes.append("Fleet jobs cover the exterior wash, interior detail and full detail only.")
        else:
            for tier in fleet["tiers"]:
                if tier["min"] <= count <= tier["max"]:
                    discount_pct = Decimal(tier["pct"])
                    discount_label = f"Fleet discount, {tier['pct']}% off the service price"
    recurring_id = None
    if recurring:
        plan = model["recurring"]
        recurring_id = _resolve(recurring, plan["frequencies"])
        cite("recurring.plan")
        if not recurring_id:
            statuses.add("invalid_combination")
            notes.append("The recurring plan runs every 2 weeks or every 4 weeks only.")
        elif service_id and service_id not in plan["services"]:
            statuses.add("invalid_combination")
            notes.append("The recurring plan covers the exterior wash, interior detail and full detail only.")
        else:
            pct = Decimal(plan["frequencies"][recurring_id]["pct"])
            if pct > discount_pct:
                discount_pct = pct
                discount_label = f"Recurring plan, {pct}% off the service price"
            elif discount_pct:
                notes.append("Discounts don't combine, so the larger one is used.")

    # Add-on dependencies.
    is_standalone_visit = False
    if not service_id and service is None:
        if addon_ids and all(model["addons"][a]["standalone"] for a in addon_ids):
            is_standalone_visit = True
        elif addon_ids:
            statuses.add("invalid_combination")
            still_needed.append("service")
            for addon_id in addon_ids:
                addon = model["addons"][addon_id]
                cite(f"addons.{addon_id}")
                if not addon["standalone"]:
                    notes.append(addon["dependency_note"])
        else:
            still_needed.append("service")
    elif not service_id and addon_ids and all(model["addons"][a]["standalone"] for a in addon_ids):
        is_standalone_visit = "invalid_combination" not in statuses
    elif not service_id:
        statuses.add("invalid_combination")
        for addon_id in addon_ids:
            cite(f"addons.{addon_id}")
            if not model["addons"][addon_id]["standalone"]:
                notes.append(model["addons"][addon_id]["dependency_note"])

    chargeable = []
    if service_id:
        for addon_id in addon_ids:
            addon = model["addons"][addon_id]
            cite(f"addons.{addon_id}")
            if service_id in addon["included_in"]:
                notes.append(f"{addon['label']} is already included in {svc['marketing_name']}, so it isn't charged.")
                continue
            needs = addon.get("requires_service_with")
            if (needs == "interior" and not has_interior) or (needs == "exterior" and not has_exterior):
                statuses.add("invalid_combination")
                notes.append(addon["dependency_note"])
                continue
            missing = [a for a in addon["requires_addons"] if a not in addon_ids]
            if missing:
                statuses.add("invalid_combination")
                notes.append(addon["dependency_note"])
                continue
            chargeable.append(addon_id)
    elif is_standalone_visit:
        for addon_id in addon_ids:
            cite(f"addons.{addon_id}")
        chargeable = list(addon_ids)

    # Conditions that rule something out, or apply a surcharge.
    surcharge_ids = []
    generator = False
    for condition_id in wanted_conditions:
        condition = model["conditions"][condition_id]
        cite(condition["fact_id"])
        kind = condition["kind"]
        if kind == "surcharge":
            needs = condition["applies_to"]
            if (needs == "interior" and has_interior) or (needs == "exterior" and has_exterior):
                surcharge_ids.append(condition_id)
                applied.append(condition_id)
            elif service_id:
                notes.append(f"{condition['label']} doesn't apply, because this service doesn't include the {needs}.")
        elif kind == "generator":
            if has_interior:
                generator = True
                applied.append(condition_id)
            elif service_id:
                notes.append("The exterior wash needs no power, so no generator fee applies.")
        elif kind == "blocks_interior":
            if has_interior:
                statuses.add("invalid_combination")
                notes.append(condition["note"])
        elif kind == "blocks_paint_work":
            blocked = [a for a in chargeable if a in condition["blocked_addons"]]
            if service_id in condition["blocked_services"] or blocked:
                statuses.add("invalid_combination")
                notes.append(condition["note"])

    # Camper van conversions: exterior is known, the living quarters aren't decided.
    if camper:
        if has_interior:
            still_needed.append(camper["still_needed"])
            notes.append(camper["note"])
        elif not service_id:
            notes.append(camper["note"])

    # Price lines.
    priced_by_size = bool(service_id) or any("prices" in model["addons"][a] for a in chargeable)
    if priced_by_size and not size_id and not undecided_vehicle:
        still_needed.append("vehicle size class, or the make and model")
    times = f" x {count}" if count > 1 else ""
    if size_id or is_standalone_visit:
        size_label = model["sizes"][size_id]["label"] if size_id else ""
        if service_id and size_id:
            base = Decimal(svc["prices"][size_id]) * count
            items.append(
                {
                    "label": f"{svc['plain_name']} ({svc['marketing_name']}), {size_label}{times}",
                    "amount": base,
                    "taxable": True,
                }
            )
            if discount_pct:
                items.append(
                    {
                        "label": discount_label,
                        "amount": -_money(base * discount_pct / 100),
                        "taxable": True,
                    }
                )
        for addon_id in chargeable:
            addon = model["addons"][addon_id]
            if "range" in addon:
                amount = (Decimal(addon["range"]["low"]) * count, Decimal(addon["range"]["high"]) * count)
                notes.append(addon["range"]["note"])
            elif "flat" in addon:
                amount = Decimal(addon["flat"]) * count
            elif size_id:
                amount = Decimal(addon["prices"][size_id]) * count
            else:
                continue
            items.append({"label": f"{addon['label']}{times}", "amount": amount, "taxable": True})
        for condition_id in surcharge_ids:
            condition = model["conditions"][condition_id]
            items.append(
                {
                    "label": f"{condition['label']} surcharge{times}",
                    "amount": Decimal(condition["surcharge"]) * count,
                    "taxable": True,
                }
            )
    if generator:
        items.append(
            {
                "label": "Generator fee",
                "amount": Decimal(model["conditions"]["no-power"]["surcharge"]),
                "taxable": True,
            }
        )
    if service_id or addon_ids:
        cite("pricing.structure", "tax.sales-tax")

    # Service area.
    zone = None
    if zip_code is None:
        still_needed.append("zip_code")
    else:
        code = re.sub(r"\D", "", str(zip_code))[:5]
        for zone_id, entry in model["travel"]["zones"].items():
            if code in entry["zips"]:
                zone = zone_id
                cite(entry["fact_id"])
                items.append(
                    {
                        "label": f"Travel fee ({entry['label']})",
                        "amount": Decimal(entry["fee"]),
                        "taxable": False,
                    }
                )
                break
        if zone is None:
            statuses.add("out_of_area")
            cite("service_area.outside")
            notes.append(f"ZIP {code} is outside the service area, and there are no exceptions for one-off jobs.")

    # Duration, which also limits the windows a job can use.
    minutes = None
    if size_id and service_id:
        minutes = svc["duration_hours"][size_id] * 60 * count
        minutes += sum(model["addons"][a]["minutes"] for a in chargeable) * count
        hours = minutes / 60
        notes.append(f"Estimated time on site: about {hours:g} hour{'' if hours == 1 else 's'}.")
        cite("availability.durations")
    elif is_standalone_visit:
        minutes = sum(model["addons"][a]["minutes"] for a in chargeable) * count

    # Timing.
    if when is None:
        if service_id or is_standalone_visit:
            fees = model["timing_fees"]
            notes.append(f"No date given: a Saturday adds ${fees['saturday']} and the evening window adds ${fees['evening']}.")
            cite("timing.saturday-fee", "timing.evening")
    else:
        parsed = None
        with contextlib.suppress(TypeError, ValueError, AttributeError, KeyError):
            parsed = _parse_when(when, current, rules)
        if not parsed or parsed[0] is None:
            still_needed.append("when, as a date and optionally a window")
        else:
            day, window = parsed
            if isinstance(day, datetime):
                day = day.date()
            _apply_timing(
                model,
                rules,
                tz,
                current,
                day,
                window,
                service_id,
                chargeable,
                zone,
                count,
                minutes,
                statuses,
                notes,
                cited,
                items,
            )

    # Deposit.
    deposit = None
    if service_id:
        deposit = model["deposit"]["by_service"].get(service_id, model["deposit"]["standard"])
    elif is_standalone_visit:
        deposit = model["deposit"]["standalone_addons"]
    if deposit is not None:
        cite("policies.deposit")

    if still_needed:
        statuses.add("needs_info")

    result = finish(deposit)
    if result["status"] == "ok" and discount_label and discount_label.startswith("Recurring"):
        saved = next(-item["amount"] for item in items if item["label"] == discount_label)
        with_tax = saved * (1 + Decimal(str(model["tax"]["rate"])))
        total = result["total"]["low"] if isinstance(result["total"], dict) else result["total"]
        notes.append(
            "This is the price of each visit after the first. The first visit is full price, "
            f"about {_usd(_money(Decimal(str(total)) + with_tax))} in total, and at least 3 visits are required."
        )
    return result


def _apply_timing(
    model,
    rules,
    tz,
    current,
    day,
    window,
    service_id,
    chargeable,
    zone,
    count,
    minutes,
    statuses,
    notes,
    cited,
    items,
):
    def cite(*ids):
        for fact_id in ids:
            if fact_id not in cited:
                cited.append(fact_id)

    def refuse(text, *ids):
        statuses.add("invalid_combination")
        notes.append(text)
        cite(*ids)

    weekday = day.strftime("%A")
    today = current.date()
    fees = model["timing_fees"]
    windows = rules["weekday_windows"].get(weekday, [])

    if window == "outside":
        refuse("That time isn't inside an arrival window.", "availability.days-windows")
        return
    if day < today:
        refuse("That date has passed.", "availability.lead-time")
        return
    if weekday in rules["closed_weekdays"]:
        refuse(f"The business is closed on {weekday}s.", "availability.days-windows")
        return
    closure = _blackout(rules, day)
    if closure:
        refuse(f"The business is closed on {day.isoformat()} ({closure['reason']}).", "timing.blackouts")
        return
    if window and window not in windows:
        refuse(f"There's no {window} window on {weekday}s.", "availability.days-windows")
        return

    earliest = current + timedelta(hours=rules["lead_time_hours"])

    if day == today:
        same_day = rules["same_day"]
        cite("availability.same-day")
        if service_id not in same_day["services"]:
            refuse("Same-day work covers only the exterior wash or interior detail.")
            return
        if current.strftime("%H:%M") >= same_day["cutoff"]:
            refuse("Same-day work has to be arranged by phone before 10:00 am, and that time has passed today.")
            return
        if window and window != same_day["window"]:
            refuse("Same-day work uses only that day's afternoon window.")
            return
        if same_day["window"] not in windows:
            refuse("There's no afternoon window today, so same-day work isn't possible.")
            return
        window = same_day["window"]
        items.append({"label": "Same-day fee", "amount": Decimal(same_day["fee"]), "taxable": True})
        notes.append("Same-day work is by phone only and depends on a technician being free, so it isn't guaranteed.")
    elif window:
        if _at(day, rules["windows"][window]["start"], tz) < earliest:
            refuse("That arrival window is inside the 24-hour notice period.", "availability.lead-time")
            return
    elif not any(_at(day, rules["windows"][n]["start"], tz) >= earliest for n in windows):
        refuse("Every arrival window that day is inside the 24-hour notice period.", "availability.lead-time")
        return

    flagship = rules["flagship"]
    if service_id == "flagship":
        cite("staff.who")
        if weekday not in flagship["weekdays"]:
            refuse("The Flagship runs only on Wednesday, Thursday and Friday mornings.")
            return
        if window and window != flagship["window"]:
            refuse("The Flagship runs only in the morning window.")
            return
        window = flagship["window"]

    if minutes and minutes >= rules["morning_only_min_minutes"]:
        cite("availability.durations")
        if window and window != "morning":
            refuse("Jobs of 5 hours or more must start in the morning window.")
            return

    if window == "evening":
        evening = rules["evening"]
        cite("timing.evening")
        if service_id not in evening["services"] or chargeable:
            refuse("The evening window is for the exterior wash only, with no add-ons.")
            return
        if zone is not None and zone not in evening["zones"]:
            refuse("The evening window is only for ZIP codes with no travel fee.")
            return
        items.append({"label": "After-hours evening fee", "amount": Decimal(fees["evening"]), "taxable": True})

    if weekday == "Saturday":
        if count >= model["fleet"]["min_vehicles"]:
            refuse("Fleet jobs run Tuesday to Friday only.", "fleet.terms")
            return
        cite("timing.saturday-fee")
        items.append({"label": "Saturday fee", "amount": Decimal(fees["saturday"]), "taxable": True})

    undecided_from = model.get("prices_undecided_from")
    if undecided_from and day.isoformat() >= undecided_from["date"]:
        cite(undecided_from["fact_id"])
        notes.append(undecided_from["note"])

    if window and day != today:
        days_out = (day - today).days
        if _is_booked(rules, day, window, days_out):
            notes.append("That arrival window currently shows as booked, so another window would be needed.")
