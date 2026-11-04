"""The agent-readable resource for one business, served at agents.cormorant.localhost:8103.

Every fact comes from businesses/cormorant/facts.json and every total from
mf_core.business.quote. The main page and offering pages are built as a small list of
blocks, then rendered to HTML or markdown, so the two versions can't drift apart.

Run from the repo root: uv run python -m demo_resource.app
"""

from __future__ import annotations

import html
import ipaddress
import os
import re
import secrets
from datetime import date, datetime, timedelta
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from mf_core.business import load_facts, quote, slots
from mf_core.logbook import log_event, read_events

SLUG = "cormorant"
STREAM = "resource"
BASE_URL = os.environ.get("MF_RESOURCE_BASE_URL", "http://agents.cormorant.localhost:8103")
SLOT_DAYS = 21
QUOTE_VALID_DAYS = 7  # This site's own limit. The facts don't set a quote validity period.

DATA = load_facts(SLUG)
BIZ = DATA["business"]
NAME = BIZ["name"]
FACTS = DATA["facts"]
FACT = {fact["id"]: fact for fact in FACTS}
MODEL = DATA["pricing_model"]
RULES = DATA["availability_rules"]
TZ = ZoneInfo(RULES["timezone"])
SIZES = list(MODEL["sizes"])
SERVICES = MODEL["services"]
ADDONS = MODEL["addons"]
CONDITIONS = MODEL["conditions"]
ZONES = MODEL["travel"]["zones"]
FEES = MODEL["timing_fees"]
TAX_RATE = MODEL["tax"]["rate"]
NEEDS_SIZE = "vehicle size class, or the make and model"
DEAD_STATUSES = ("not_offered", "out_of_area", "invalid_combination")

app = FastAPI(title=NAME, docs_url=None, redoc_url=None, openapi_url=None)


# ---------------------------------------------------------------- small formatting helpers


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def long_date(iso: str) -> str:
    day = date.fromisoformat(iso[:10])
    return f"{day.day} {day:%B %Y}"


def clock(hhmm: str) -> str:
    hour, minute = hhmm.split(":")
    hour = int(hour)
    suffix = "am" if hour < 12 else "pm"
    return f"{hour % 12 or 12}:{minute} {suffix}"


def whole(amount) -> str:
    return f"${amount:,.0f}"


def usd(amount) -> str:
    return f"${amount:,.2f}"


def money(value) -> str:
    if value is None:
        return "not worked out yet"
    if isinstance(value, dict):
        return f"{usd(value['low'])} to {usd(value['high'])}"
    return usd(value)


def words(items) -> str:
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def local_now() -> datetime:
    return datetime.now(TZ)


def stamp(moment: datetime) -> str:
    return f"{moment.day} {moment:%B %Y} at {clock(moment.strftime('%H:%M'))} Pacific time"


def link(path: str, **params) -> str:
    """A site path with a query string, keeping commas readable."""
    clean = {key: value for key, value in params.items() if value not in (None, "", [], ())}
    return f"{path}?{urlencode(clean, safe=',-')}" if clean else path


def service_name(service_id: str) -> str:
    service = SERVICES[service_id]
    return f"{service['plain_name']} ({service['marketing_name']})"


def addon_price_cells(addon: dict) -> list[str]:
    if "prices" in addon:
        return [whole(addon["prices"][size]) for size in SIZES]
    if "flat" in addon:
        return [f"{whole(addon['flat'])} per pair"] * len(SIZES)
    return [f"{whole(addon['range']['low'])} to {whole(addon['range']['high'])}"] * len(SIZES)


# ---------------------------------------------------------------- blocks and rendering

TAGS = {"unknown": "Unknown", "not_offered": "Not offered", "false_third_party_claim": "False listing"}
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def inline_html(text: str) -> str:
    """Authored text only. Visitor input never passes through this."""
    out = esc(text)
    out = INLINE_LINK.sub(r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", out)


def inline_md(text: str) -> str:
    return re.sub(r"\]\(/", f"]({BASE_URL}/", text)


def facts_block(ids, details=None):
    details = details or {}
    return ("facts", [(FACT[fact_id], details.get(fact_id)) for fact_id in ids])


def ids_in(category, status="known", skip=()):
    return [
        fact["id"]
        for fact in FACTS
        if fact["category"] == category and fact["status"] == status and fact["id"] not in skip
    ]


def ids_with_status(status):
    return [fact["id"] for fact in FACTS if fact["status"] == status]


def render_html(sections, seen=None) -> str:
    seen = set() if seen is None else seen
    out = []
    for section_id, title, blocks in sections:
        out.append(f'<section id="{esc(section_id)}"><h2>{esc(title)}</h2>')
        for block in blocks:
            kind = block[0]
            if kind == "p":
                out.append(f"<p>{inline_html(block[1])}</p>")
            elif kind == "h3":
                out.append(f"<h3>{esc(block[1])}</h3>")
            elif kind == "ul":
                out.append("<ul>" + "".join(f"<li>{inline_html(item)}</li>" for item in block[1]) + "</ul>")
            elif kind == "table":
                head = "".join(f"<th>{esc(cell)}</th>" for cell in block[1])
                rows = "".join(
                    "<tr>" + "".join(f"<td>{inline_html(str(cell))}</td>" for cell in row) + "</tr>"
                    for row in block[2]
                )
                out.append(f'<div class="wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
            elif kind == "facts":
                out.append('<ul class="facts">')
                for fact, detail in block[1]:
                    attr = "" if fact["id"] in seen else f' id="fact-{esc(fact["id"])}"'
                    seen.add(fact["id"])
                    tag = TAGS.get(fact["status"])
                    tag_html = f'<span class="tag">{tag}</span> ' if tag else ""
                    extra = f'<div class="detail">{inline_html(detail)}</div>' if detail else ""
                    out.append(
                        f"<li{attr}>{tag_html}{esc(fact['statement'])}{extra}"
                        f'<div class="when">Confirmed on <time datetime="{esc(fact["confirmed_on"])}">'
                        f"{long_date(fact['confirmed_on'])}</time></div></li>"
                    )
                out.append("</ul>")
        out.append("</section>")
    return "\n".join(out)


def render_markdown(title, intro, sections) -> str:
    out = [f"# {title}", ""]
    for paragraph in intro:
        out += [inline_md(paragraph), ""]
    for _section_id, heading, blocks in sections:
        out += [f"## {heading}", ""]
        for block in blocks:
            kind = block[0]
            if kind == "p":
                out += [inline_md(block[1]), ""]
            elif kind == "h3":
                out += [f"### {block[1]}", ""]
            elif kind == "ul":
                out += [f"- {inline_md(item)}" for item in block[1]] + [""]
            elif kind == "table":
                out.append("| " + " | ".join(block[1]) + " |")
                out.append("|" + " --- |" * len(block[1]))
                out += ["| " + " | ".join(inline_md(str(cell)) for cell in row) + " |" for row in block[2]]
                out.append("")
            elif kind == "facts":
                for fact, detail in block[1]:
                    tag = TAGS.get(fact["status"])
                    prefix = f"**{tag}:** " if tag else ""
                    line = f"- {prefix}{fact['statement']}"
                    if detail:
                        line += f" {inline_md(detail)}"
                    line += f" *Confirmed on {long_date(fact['confirmed_on'])}. Fact id: {fact['id']}.*"
                    out.append(line)
                out.append("")
    return "\n".join(out)


STYLE = """
:root { color-scheme: light dark; }
body { font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; margin: 0 auto; max-width: 56rem; padding: 1rem; }
h1 { font-size: 1.6rem; line-height: 1.25; } h2 { font-size: 1.25rem; margin-top: 2.2rem; border-bottom: 1px solid #8884; padding-bottom: .2rem; }
h3 { font-size: 1.05rem; margin-top: 1.4rem; }
ul.facts { padding-left: 1.1rem; } ul.facts li { margin-bottom: .75rem; }
.when { font-size: .82rem; opacity: .7; } .detail { font-size: .92rem; margin-top: .2rem; }
.tag { font-size: .75rem; font-weight: 600; border: 1px solid currentColor; border-radius: 3px; padding: 0 .3rem; }
.wrap { overflow-x: auto; } table { border-collapse: collapse; margin: .6rem 0; font-size: .92rem; }
th, td { border: 1px solid #8885; padding: .3rem .55rem; text-align: left; vertical-align: top; }
code { font-size: .9em; } nav ul { columns: 2; padding-left: 1.1rem; font-size: .92rem; }
label { display: block; margin: .7rem 0 .15rem; font-weight: 600; } label.inline { display: inline; font-weight: 400; margin: 0; }
input[type=text], input[type=email], input[type=tel], input[type=number], select, textarea { font: inherit; width: 100%; max-width: 28rem; padding: .35rem; box-sizing: border-box; }
fieldset { border: 1px solid #8885; margin: 1rem 0; } button { font: inherit; padding: .45rem 1rem; margin-top: 1rem; }
.error { border-left: 4px solid #c33; padding-left: .7rem; } .answer { font-size: 1.1rem; font-weight: 600; }
blockquote { border-left: 3px solid #8886; margin-left: 0; padding-left: .8rem; white-space: pre-wrap; }
""".strip()


def page(title: str, body: str, markdown_href: str | None = None, status_code: int = 200) -> HTMLResponse:
    alt = f'<link rel="alternate" type="text/markdown" href="{esc(markdown_href)}">' if markdown_href else ""
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(title)}</title>{alt}<style>{STYLE}</style></head><body>"
        f'<p><a href="/">{esc(NAME)}</a> · <a href="/quote">Quote</a> · <a href="/request">Request</a> · <a href="/ask">Ask</a></p>'
        f"<main>{body}</main>"
        f"<footer><p>Prices, availability and booking requests for {esc(NAME)}: {esc(BASE_URL)}. "
        "This business is fictional.</p></footer></body></html>"
    )
    return HTMLResponse(document, status_code=status_code)


def wants_markdown(request: Request) -> bool:
    accept = request.headers.get("accept", "").lower()
    if "text/markdown" not in accept:
        return False
    html_at = accept.find("text/html")
    return html_at == -1 or accept.find("text/markdown") < html_at


def markdown_response(text: str) -> Response:
    return Response(text, media_type="text/markdown; charset=utf-8", headers={"Vary": "Accept"})


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


def slot_notes(slot: dict) -> str:
    notes = []
    if slot["weekday"] == "Saturday":
        notes.append(f"Saturday fee {whole(FEES['saturday'])}")
    if slot["window"] == "evening":
        notes.append(f"After-hours window: exterior wash only, no add-ons, no-travel-fee ZIP codes, {whole(FEES['evening'])} fee")
    flagship = RULES["flagship"]
    if slot["window"] == flagship["window"] and slot["weekday"] in flagship["weekdays"]:
        notes.append("The Flagship can start in this window")
    return "; ".join(notes) or "None"


def slots_block(service_id: str | None = None):
    found = open_slots(service_id)
    moment = stamp(local_now())
    if not found:
        return [("p", f"As of {moment}, no arrival window that fits is open in the next {SLOT_DAYS} days.")]
    rows = [
        [
            long_date(slot["date"]),
            slot["weekday"],
            slot["window"],
            f"{clock(slot['start'])} to {clock(slot['end'])}",
            slot_notes(slot),
            f"[Request]({link('/request', service=service_id, when=slot['date'] + ' ' + slot['window'])})",
        ]
        for slot in found
    ]
    return [
        ("p", f"As of {moment}, these arrival windows are open in the next {SLOT_DAYS} days. "
              "A window not listed here is booked, closed or inside the 24-hour notice period."),
        ("table", ["Date", "Day", "Window", "Arrival", "Notes", "Link"], rows),
    ]


# ---------------------------------------------------------------- facts as pages


def addon_on_service(addon_id: str, service_id: str) -> str:
    addon = ADDONS[addon_id]
    service = SERVICES[service_id]
    if service_id in addon["included_in"]:
        return "already included"
    needs = addon.get("requires_service_with")
    if needs == "interior" and not service["includes_interior"]:
        return "not available"
    if needs == "exterior" and not service["includes_exterior"]:
        return "not available"
    required = addon["requires_addons"]
    if required:
        return "available with " + words(ADDONS[item]["label"].lower() for item in required)
    return "available"


def formula_text() -> str:
    return (
        "Total = (service price for the size class + add-ons + condition surcharges + generator fee + "
        "Saturday, after-hours or same-day fee, minus any recurring or fleet discount) "
        f"× {1 + TAX_RATE:.5f} + travel fee."
    )


def worked_example(label: str, **job) -> str:
    result = quote(SLUG, **job)
    lines = "; ".join(f"{line['label']} {money(line['amount'])}" for line in result["lines"])
    return f"{label}: {lines}; sales tax {money(result['tax'])}; total {money(result['total'])}."


def size_details() -> dict:
    details = {}
    for size in SIZES:
        fact_id = f"size_classes.{size}"
        details[fact_id] = "Listed vehicles and words for this class: " + ", ".join(FACT[fact_id]["value"]["examples"]) + "."
    return details


def not_offered_details() -> dict:
    grouped: dict[str, list[str]] = {}
    for term, entry in MODEL["not_offered_terms"].items():
        grouped.setdefault(entry["fact_id"], []).append(term)
    for term, fact_id in MODEL["vehicles"]["not_offered"].items():
        grouped.setdefault(fact_id, [])
        if term not in grouped[fact_id]:
            grouped[fact_id].append(term)
    return {fact_id: "Words that map to this: " + ", ".join(terms) + "." for fact_id, terms in grouped.items()}


def listing_details() -> dict:
    full = FACT["pricing.full"]["value"]["prices"]
    closed = words(FACT["availability.days-windows"]["value"]["closed"])
    prices = ", ".join(f"{whole(full[size])} for {size}" for size in SIZES)
    url = FACT["third_party.listing-price"]["value"]["listing_url"]
    return {
        "third_party.listing-price": f"True value: the full detail costs {prices}. The listing is at {url}.",
        "third_party.listing-services": (
            "True values: boats aren't detailed ([fact](#fact-not_offered.boats-motorcycles)), ceramic coating isn't offered "
            f"([fact](#fact-not_offered.ceramic-coating)), and the business is closed on {closed} "
            "([fact](#fact-availability.days-windows))."
        ),
    }


def main_sections():
    sections = []

    # Addresses and parameter values.
    addon_values = ", ".join(f"`{key}` ({value['label'].lower()})" for key, value in ADDONS.items())
    condition_values = ", ".join(f"`{key}` ({value['label'].lower()})" for key, value in CONDITIONS.items())
    sections.append((
        "addresses", "Addresses on this site",
        [
            ("ul", [
                "[/services](/services) has one page per offering, with its price rules, dependencies and a prefilled quote link.",
                "[/quote](/quote) takes a job's details and returns a total or range, line items, what's still needed, a quote ID and an expiry. It takes no personal details. It works as a plain link or a form, and `format=json` returns JSON.",
                "[/request](/request) sends a booking or quote request. It's the only address that asks for contact details, and a link with job details opens it prefilled and ready to confirm.",
                "[/ask](/ask) passes a question to the owner.",
                "`/r/{id}` is the status page for one request or question.",
                "[/index.md](/index.md) is this page in markdown, and `/` returns the same markdown when the Accept header asks for `text/markdown`.",
            ]),
            ("h3", "Values /quote and /request accept"),
            ("table", ["Parameter", "What it means", "Valid values"], [
                ["service", "The service", "`exterior`, `interior`, `full` or `flagship`, or any everyday word listed under Customer's words"],
                ["size", "The size class", "`small`, `midsize`, `large` or `oversized`, or Class A, B, C or D"],
                ["vehicle", "The vehicle's make and model or type, which sets the size class when it's listed", "Any text, such as a make and model"],
                ["addons", "Add-ons, separated by commas", addon_values],
                ["conditions", "Conditions that apply, separated by commas", condition_values],
                ["zip", "The 5-digit ZIP code where the vehicle is parked", "Any of the listed ZIP codes under Service area"],
                ["when", "The date, with an optional window, which brings in Saturday, after-hours and same-day rules", "`YYYY-MM-DD`, optionally followed by `morning`, `afternoon` or `evening`, or `today` or `tomorrow`"],
                ["recurring", "The recurring plan", "`every-2-weeks` or `every-4-weeks`"],
                ["vehicle_count", "The number of vehicles at one address on one day", "A whole number"],
                ["budget", "A budget in US dollars, which is compared with the total and never changes the price", "A number"],
                ["format", "The response format on /quote", "`json`, or leave it out for HTML"],
            ]),
            ("p", "For example, [/quote?service=full&size=midsize&zip=94110](/quote?service=full&size=midsize&zip=94110) returns the total for a full detail on a midsize vehicle in ZIP code 94110, and a link to [/request](/request) with the same values opens the request form with them filled in."),
            ("p", f"A quote ID expires {QUOTE_VALID_DAYS} days after it's issued. That limit is set by this site, because the owner hasn't stated how long a quoted price stays valid. A quote doesn't hold a slot."),
        ],
    ))

    # Customer's words.
    word_rows = []
    for key, value in SERVICES.items():
        word_rows.append([service_name(key), f"service={key}", ", ".join(value["aliases"])])
    for key, value in MODEL["sizes"].items():
        word_rows.append([f"Size class: {value['label']}", f"size={key}", ", ".join(value["aliases"])])
    for key, value in ADDONS.items():
        word_rows.append([f"Add-on: {value['label']}", f"addons={key}", ", ".join(value["aliases"])])
    for key, value in CONDITIONS.items():
        word_rows.append([f"Condition: {value['label']}", f"conditions={key}", ", ".join(value["aliases"])])
    for key, value in MODEL["recurring"]["frequencies"].items():
        word_rows.append([f"Recurring plan: {value['pct']}% off", f"recurring={key}", ", ".join(value["aliases"])])
    sections.append((
        "words", "Customer's words",
        [
            facts_block(ids_in("vocabulary")),
            ("p", "This table maps everyday words onto the business's categories and the values /quote takes."),
            ("table", ["Category", "Value", "Words that map to it"], word_rows),
        ],
    ))

    # Offerings.
    sections.append((
        "offerings", "Offerings and what each includes",
        [
            facts_block(
                ids_in("services"),
                {f"services.{key}": f"[Page for this service](/services/{key})" for key in SERVICES},
            ),
            ("p", "Add-ons have their own pages: " + ", ".join(f"[{value['label']}](/services/{key})" for key, value in ADDONS.items()) + ". Their prices and dependencies are under Add-on dependencies."),
        ],
    ))

    # Size classes.
    ambiguous = MODEL["vehicles"]["ambiguous"]
    camper = MODEL["vehicles"]["camper"]
    notes = list(dict.fromkeys(entry["note"] for entry in ambiguous.values()))
    sections.append((
        "sizes", "Size classes and vehicles",
        [
            facts_block(ids_in("size_classes"), size_details()),
            ("ul", notes + [
                camper["note"] + " Words for this: " + ", ".join(camper["terms"]) + ".",
                "A vehicle that isn't listed has no assumed size class, and a technician checks the class on arrival ([fact](#fact-conditions.assessed-on-arrival)).",
                "The Tesla Cybertruck has no size class yet ([fact](#fact-eligibility.cybertruck)).",
            ]),
        ],
    ))

    # Price structure.
    price_rows = [
        [service_name(key)] + [whole(value["prices"][size]) for size in SIZES] + ["Fixed"]
        for key, value in SERVICES.items()
    ]
    addon_rows = [
        [value["label"]] + addon_price_cells(value) + ["Range" if "range" in value else ("Flat" if "flat" in value else "Fixed")]
        for value_key, value in ADDONS.items()
    ]
    sections.append((
        "prices", "Price structure",
        [
            facts_block(ids_in("pricing", skip=("pricing.structure",))),
            ("table", ["Service"] + SIZES + ["Type"], price_rows),
            ("table", ["Add-on"] + SIZES + ["Type"], addon_rows),
            ("ul", [
                "Fixed: every service price is a fixed amount for its size class, and every add-on is a fixed amount for its size class except the two below.",
                "From: a \"starting at\" price is the small-class price, and any larger vehicle costs more.",
                "Range: odour treatment is the only range, and a technician settles it on arrival with a smell test.",
                "Flat: headlight restoration is the same price at any vehicle size.",
                "Quote-only: more than 10 vehicles at once has no set price ([fact](#fact-fleet.over-10)).",
                "What moves a total: size class, add-ons, defined conditions, the generator fee, Saturday, after-hours or same-day timing, the ZIP code's travel fee, and any recurring or fleet discount.",
            ]),
        ],
    ))

    # Full total.
    rate_rows = [
        ["Service", "Set by size class", "Yes"],
        ["Add-ons", "Set by size class, except headlight restoration and odour treatment", "Yes"],
    ]
    for key in ("excessive-pet-hair", "heavily-soiled", "heavy-contamination"):
        rate_rows.append([f"{CONDITIONS[key]['label']} surcharge", whole(CONDITIONS[key]["surcharge"]), "Yes"])
    rate_rows += [
        ["Generator fee, when no outlet is within 75 feet", whole(CONDITIONS["no-power"]["surcharge"]), "Yes"],
        ["Saturday fee", whole(FEES["saturday"]), "Yes"],
        ["After-hours evening fee", whole(FEES["evening"]), "Yes"],
        ["Same-day fee", whole(FEES["same_day"]), "Yes"],
    ]
    for zone in ZONES.values():
        rate_rows.append([f"Travel fee per visit: {zone['label']}", whole(zone["fee"]), "No"])
    sections.append((
        "total", "How the full total is worked out",
        [
            facts_block(["pricing.structure", "tax.sales-tax"]),
            ("p", f"**{formula_text()}**"),
            ("p", f"Sales tax is {TAX_RATE * 100:g}%, rounded {MODEL['tax']['rounding']}. The travel fee isn't taxed. A recurring or fleet discount comes off the service price only. On a fleet job the service, add-ons and surcharges are multiplied by the number of vehicles, and there's one travel fee per visit. The deposit counts toward the total, and no tip is added."),
            ("table", ["Item", "Amount", "Taxed"], rate_rows),
            ("ul", [
                worked_example("A full detail with shampoo on a midsize vehicle in ZIP code 94015", service="full", size="midsize", addons=("shampoo",), zip_code="94015"),
                worked_example("An interior detail with odour treatment on a large vehicle in ZIP code 94110", service="interior", size="large", addons=("odor",), zip_code="94110"),
            ]),
        ],
    ))

    # Add-on dependencies.
    dependency_rows = [
        [f"[{value['label']}](/services/{key})"]
        + [addon_on_service(key, service_id) for service_id in SERVICES]
        + ["yes" if value["standalone"] else "no"]
        for key, value in ADDONS.items()
    ]
    sections.append((
        "dependencies", "Add-on dependencies",
        [
            facts_block(ids_in("addons")),
            ("table", ["Add-on"] + [SERVICES[key]["marketing_name"] for key in SERVICES] + ["On its own"], dependency_rows),
        ],
    ))

    # Defined conditions.
    sections.append((
        "conditions", "Defined conditions",
        [
            facts_block(ids_in("conditions")),
            ("p", "These conditions go in the `conditions` parameter of /quote: " + "; ".join(f"`{key}` means {value['label'].lower()}" for key, value in CONDITIONS.items()) + "."),
        ],
    ))

    sections.append(("eligibility", "Eligibility", [
        facts_block(ids_in("eligibility")),
        ("p", "Two eligibility questions aren't decided yet, and they're under [Unknown](#unknown)."),
    ]))
    sections.append(("prerequisites", "Prerequisites", [facts_block(ids_in("prerequisites"))]))

    # Service area.
    sections.append((
        "area", "Service area",
        [
            facts_block(ids_in("service_area")),
            ("table", ["Area", "Travel fee per visit", "ZIP codes"], [
                [zone["label"], whole(zone["fee"]), ", ".join(zone["zips"])] for zone in ZONES.values()
            ]),
        ],
    ))

    # Availability.
    hours = FACT["availability.durations"]["value"]["hours"]
    sections.append((
        "availability", "Availability",
        [
            facts_block(ids_in("availability")),
            ("table", ["Hours on site"] + SIZES, [
                [service_name(key)] + [f"{hours[key][size]:g}" for size in SIZES] for key in SERVICES
            ]),
            ("h3", "Next open arrival windows"),
            *slots_block(),
        ],
    ))

    sections.append(("staff", "Staff differences", [facts_block(ids_in("staff"))]))
    sections.append(("policies", "Policies", [facts_block(ids_in("policies"))]))
    sections.append(("payment", "Payment", [facts_block(ids_in("payment"))]))
    sections.append(("timing", "Timing rules and blackout dates", [
        facts_block(ids_in("timing")),
        ("ul", [
            f"{long_date(item['start'])} to {long_date(item['end'])}: {item['reason']}"
            if item["start"] != item["end"] else f"{long_date(item['start'])}: {item['reason']}"
            for item in RULES["blackout_ranges"]
        ]),
    ]))
    sections.append(("recurring", "Recurring plan and fleet jobs", [
        facts_block(ids_in("recurring") + ids_in("fleet")),
    ]))
    sections.append(("gift-cards", "Gift cards", [facts_block(ids_in("gift_cards"))]))
    sections.append(("not-offered", "Not offered", [
        facts_block(ids_with_status("not_offered"), not_offered_details()),
    ]))
    sections.append(("unknown", "Unknown: not decided or not known yet", [
        ("p", "Each item says what isn't decided or known and what would settle it."),
        facts_block(ids_with_status("unknown")),
    ]))
    sections.append(("credentials", "Credentials", [facts_block(ids_in("credentials"))]))
    sections.append((
        "next-step", "Next step and what happens after a request",
        [
            facts_block(ids_in("next_step")),
            ("p", "A request goes through [/request](/request), which asks for contact details and who's submitting, the customer or an agent acting for them. It returns a status page at `/r/{id}`."),
            ("p", "A question this page doesn't cover goes through [/ask](/ask), which passes it to the owner and returns a status page."),
        ],
    ))
    sections.append((
        "listings", "Listings elsewhere that are wrong",
        [facts_block(ids_with_status("false_third_party_claim"), listing_details())],
    ))

    # Freshness.
    by_category: dict[str, list[str]] = {}
    for fact in FACTS:
        by_category.setdefault(fact["category"], []).append(fact["confirmed_on"])
    sections.append((
        "freshness", "Freshness",
        [
            ("p", f"Every fact on this page shows the date it was last confirmed. This set of facts is current as of {long_date(DATA['as_of'])}. Open arrival windows are worked out when the page is requested."),
            ("table", ["Category", "Facts", "Oldest confirmation", "Newest confirmation"], [
                [category.replace("_", " "), len(dates), long_date(min(dates)), long_date(max(dates))]
                for category, dates in by_category.items()
            ]),
        ],
    ))
    return sections


def main_intro() -> list[str]:
    office = BIZ["hours"]["office"]
    return [
        f"Prices, rules, availability and booking requests for {NAME}, a mobile car detailing business based in {BIZ['base_area']}. {BIZ['service_model']} The owner is {BIZ['owner']}.",
        f"Phone {BIZ['phone']}. Email {BIZ['email']}. The office is open {office['days']} from {clock(office['open'])} to {clock(office['close'])}, and the service days are {words(BIZ['hours']['service_days'])}. This business is fictional.",
    ]


def main_html() -> HTMLResponse:
    sections = main_sections()
    nav = "".join(f'<li><a href="#{esc(sid)}">{esc(title)}</a></li>' for sid, title, _ in sections)
    intro = "".join(f"<p>{inline_html(text)}</p>" for text in main_intro())
    body = (
        f"<h1>{esc(NAME)}: prices, rules, availability and requests</h1>{intro}"
        f'<p>Markdown version: <a href="/index.md">/index.md</a></p><nav><ul>{nav}</ul></nav>'
        + render_html(sections)
    )
    response = page(f"{NAME}: prices, rules and availability", body, "/index.md")
    response.headers["Vary"] = "Accept"
    return response


def main_markdown() -> Response:
    return markdown_response(
        render_markdown(f"{NAME}: prices, rules, availability and requests", main_intro(), main_sections())
    )


def service_sections(service_id: str):
    service = SERVICES[service_id]
    size_rows = [
        [
            MODEL["sizes"][size]["label"],
            whole(service["prices"][size]),
            f"{service['duration_hours'][size]:g} hours",
            f"[Quote]({link('/quote', service=service_id, size=size)})",
        ]
        for size in SIZES
    ]
    addon_rows = [
        [f"[{addon['label']}](/services/{key})", addon_on_service(key, service_id)] + addon_price_cells(addon)
        for key, addon in ADDONS.items()
    ]
    has_interior = service["includes_interior"]
    has_exterior = service["includes_exterior"]
    condition_ids = []
    if has_interior:
        condition_ids += ["conditions.excessive-pet-hair", "conditions.heavily-soiled"]
    if has_exterior:
        condition_ids.append("conditions.heavy-contamination")
    condition_ids.append("conditions.assessed-on-arrival")
    limit_ids = ["eligibility.served", "eligibility.matte-wrap"]
    if has_interior:
        limit_ids.append("eligibility.camper-interior")
    limit_ids.append("eligibility.cybertruck")
    if service_id == "flagship":
        limit_ids += ["services.scratch-outcome", "not_offered.paint-correction", "not_offered.ceramic-coating"]
    timing_ids = ["availability.days-windows", "availability.durations", "availability.lead-time"]
    if service_id in RULES["same_day"]["services"]:
        timing_ids.append("availability.same-day")
    if service_id in RULES["evening"]["services"]:
        timing_ids.append("timing.evening")
    timing_ids += ["timing.saturday-fee", "timing.blackouts", "staff.who"]
    sections = [
        ("what", "What it is and what it costs", [
            facts_block([f"services.{service_id}", f"pricing.{service_id}"]),
            ("table", ["Size class", "Price", "Time on site", "Link"], size_rows),
            ("p", f"A prefilled quote link such as [{link('/quote', service=service_id, size='midsize', zip='94110')}]({link('/quote', service=service_id, size='midsize', zip='94110')}) returns the total for one ZIP code, and [the request form]({link('/request', service=service_id)}) opens with this service filled in."),
        ]),
        ("total", "How the total is worked out", [
            facts_block(["pricing.structure", "tax.sales-tax"]),
            ("p", f"**{formula_text()}**"),
            ("p", "Travel fee per visit: " + "; ".join(f"{whole(zone['fee'])} for {zone['label']}" for zone in ZONES.values()) + ". The ZIP lists are under [Service area](/#area)."),
        ]),
        ("addons", "Add-ons and dependencies on this service", [
            ("table", ["Add-on", "On this service"] + SIZES, addon_rows),
        ]),
        ("conditions", "Conditions that can change the price", [facts_block(condition_ids)]),
        ("requirements", "What the customer provides", [
            facts_block(["prerequisites.power", "prerequisites.water", "prerequisites.parking", "prerequisites.permission", "prerequisites.belongings-keys"]),
        ]),
        ("limits", "What can rule it out", [facts_block(limit_ids)]),
        ("timing", "When it can happen", [
            facts_block(timing_ids),
            ("h3", "Next open arrival windows for this service"),
            *slots_block(service_id),
        ]),
    ]
    if service_id in MODEL["recurring"]["services"]:
        sections.append(("discounts", "Recurring plan and fleet jobs", [
            facts_block(["recurring.plan", "fleet.discount", "fleet.terms"]),
        ]))
    else:
        sections.append(("discounts", "Discounts", [
            ("p", f"{service['marketing_name']} isn't part of the recurring plan or the fleet discount, which cover the exterior wash, interior detail and full detail only."),
        ]))
    sections.append(("policies", "Deposit and policies", [
        facts_block(["policies.deposit", "policies.cancellation", "policies.reschedule", "policies.no-show", "policies.weather"]),
    ]))
    sections.append(("next-step", "Next step", [facts_block(["next_step.reply", "next_step.slot-not-held"])]))
    return sections


def addon_sections(addon_id: str):
    addon = ADDONS[addon_id]
    rows = []
    for service_id in SERVICES:
        state = addon_on_service(addon_id, service_id)
        chosen = [*addon["requires_addons"], addon_id]
        if state.startswith("available"):
            links = " · ".join(
                f"[{size}]({link('/quote', service=service_id, addons=','.join(chosen), size=size)})" for size in SIZES
            )
        else:
            links = "None"
        rows.append([service_name(service_id), state, links])
    price_table = ("table", SIZES, [addon_price_cells(addon)])
    what_ids = [f"addons.{addon_id}"]
    if addon_id == "pet-hair":
        what_ids.append("conditions.excessive-pet-hair")
    if addon_id in ("clay", "sealant"):
        what_ids.append("eligibility.matte-wrap")
    if addon_id == "sealant":
        what_ids.append("not_offered.ceramic-coating")
    sections = [
        ("what", "What it is and what it costs", [facts_block(what_ids), price_table]),
        ("dependencies", "Dependencies and prefilled quote links", [
            ("p", addon["dependency_note"] or "This add-on can be booked on its own with no other service."),
            ("table", ["Service", "This add-on on that service", "Quote by size class"], rows),
        ]),
    ]
    if addon["standalone"]:
        own = link("/quote", addons=addon_id)
        sections[1][2].append(("p", f"On its own: [{own}]({own}), and [the request form]({link('/request', addons=addon_id)}) opens with it filled in."))
    sections += [
        ("total", "How the total is worked out", [
            facts_block(["pricing.structure", "tax.sales-tax"]),
            ("p", f"**{formula_text()}**"),
        ]),
        ("next-step", "Next step", [facts_block(["next_step.reply", "next_step.slot-not-held"])]),
    ]
    return sections


def offering_title(offering_id: str) -> str:
    if offering_id in SERVICES:
        return f"{service_name(offering_id)} at {NAME}"
    return f"{ADDONS[offering_id]['label']} at {NAME}"


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
    when = first(params, "when") or " ".join(
        part for part in (first(params, "date"), first(params, "window")) if part
    )
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


def ip_range(request: Request) -> str:
    host = request.client.host if request.client else ""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return "unknown"
    prefix = 24 if address.version == 4 else 48
    return str(ipaddress.ip_network(f"{address}/{prefix}", strict=False))


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
    fits = [
        slot for slot in listed
        if slot["open"] and slot_fits(slot, service_id) and (not long_job or slot["window"] == "morning")
    ]
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
        return f"This is {usd(low - budget)} or more over the stated budget of {usd(budget)}." if low != high else f"This is {usd(low - budget)} over the stated budget of {usd(budget)}."
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
            {"date": slot["date"], "weekday": slot["weekday"], "window": slot["window"]}
            for slot in open_slots(cited_service(result))[:3]
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


def facts_used_html(fact_ids) -> str:
    items = "".join(
        f'<li id="fact-{esc(fid)}">{esc(FACT[fid]["statement"])}<div class="when">Confirmed on {long_date(FACT[fid]["confirmed_on"])}</div></li>'
        for fid in fact_ids
        if fid in FACT
    )
    return f'<ul class="facts">{items}</ul>' if items else ""


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
        parts.append(f'<h2>Line items</h2><div class="wrap"><table><thead><tr><th>Item</th><th>Amount</th></tr></thead><tbody>{rows}</tbody></table></div>')
    if outcome["deposit_due"] is not None:
        parts.append(f"<p>Deposit to book: {esc(money(outcome['deposit_due']))}, which counts toward the total.</p>")
    if outcome["conditions_applied"]:
        labels = [CONDITIONS[item]["label"] for item in outcome["conditions_applied"] if item in CONDITIONS]
        parts.append(f"<h2>Conditions applied</h2><p>{esc(words(labels))}.</p>")
    if outcome["still_needed"]:
        parts.append("<h2>Still needed</h2><ul>" + "".join(f"<li>{esc(needed_word(item))}</li>" for item in outcome["still_needed"]) + "</ul>")
    if outcome["notes"]:
        parts.append("<h2>Notes</h2><ul>" + "".join(f"<li>{esc(note)}</li>" for note in outcome["notes"]) + "</ul>")
    if outcome["next_open"]:
        parts.append(
            "<h2>Next open windows that fit</h2><ul>"
            + "".join(f"<li>{esc(slot['weekday'])} {esc(long_date(slot['date']))}, {esc(slot['window'])} window</li>" for slot in outcome["next_open"])
            + "</ul>"
        )
    return "".join(parts)


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
    return "".join([
        select_field("service", "Service", [(key, service_name(key)) for key in SERVICES], job["service"]),
        select_field("size", "Size class", [(key, value["label"]) for key, value in MODEL["sizes"].items()], job["size"]),
        text_field("vehicle", "Vehicle make and model, or type", job["vehicle"]),
        checks("addons", "Add-ons", ADDONS, job["addons"]),
        checks("conditions", "Conditions that apply", CONDITIONS, job["conditions"]),
        text_field("zip", "ZIP code", job["zip"]),
        text_field("when", "Date, with an optional window", job["when"], hint="YYYY-MM-DD morning"),
        select_field("recurring", "Recurring plan", [(key, key.replace("-", " ")) for key in MODEL["recurring"]["frequencies"]], job["recurring"]),
        text_field("vehicle_count", "Number of vehicles", job["vehicle_count"], kind="number"),
        text_field("budget", "Budget in US dollars", job["budget"]),
    ])


# ---------------------------------------------------------------- logging


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


# ---------------------------------------------------------------- pages


@app.api_route("/", methods=["GET", "HEAD"])
def home(request: Request):
    return main_markdown() if wants_markdown(request) else main_html()


@app.api_route("/index.md", methods=["GET", "HEAD"])
def home_markdown():
    return main_markdown()


def offerings_sections():
    rows = [
        [f"[{service_name(key)}](/services/{key})", "Service", f"{whole(min(value['prices'].values()))} to {whole(max(value['prices'].values()))}"]
        for key, value in SERVICES.items()
    ]
    for key, addon in ADDONS.items():
        if "prices" in addon:
            price = f"{whole(min(addon['prices'].values()))} to {whole(max(addon['prices'].values()))}"
        elif "flat" in addon:
            price = whole(addon["flat"])
        else:
            price = f"{whole(addon['range']['low'])} to {whole(addon['range']['high'])}"
        rows.append([f"[{addon['label']}](/services/{key})", "Add-on", price])
    return [("offerings", "Offerings", [("table", ["Offering", "Kind", "Price before fees and tax"], rows)])]


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
    body = f'<h1>{esc(title)}</h1><p>Markdown version: <a href="/services/{esc(offering_id)}.md">/services/{esc(offering_id)}.md</a></p>' + render_html(sections)
    return page(title, body, f"/services/{offering_id}.md")


def quote_form(job: dict) -> str:
    return f'<form method="get" action="/quote">{job_fields(job)}<br><button type="submit">Work out the total</button></form>'


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
            '<p>This takes a job\'s details and returns a total or range. It takes no personal details. '
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
        return JSONResponse({
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
                for fid in outcome["fact_ids"] if fid in FACT
            ],
            "request_url": f"{BASE_URL}{request_url}" if request_url else None,
        })
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
        + "<h2>Rules behind this answer</h2>" + facts_used_html(outcome["fact_ids"])
        + "<h2>Change the details</h2>" + quote_form(job)
    )
    return page(f"Quote {quote_id}: {NAME}", body)


def request_form(job: dict, params: dict, errors: list[str] | None = None) -> str:
    """Contact fields refill only from a POST, so personal details never come from a link."""
    posted = params if errors else {}
    who = first(posted, "submitted_by")
    request_type = first(params, "request_type") or ("booking" if job["when"] else "quote")
    error_html = ""
    if errors:
        error_html = '<div class="error"><p>This request wasn\'t sent yet:</p><ul>' + "".join(f"<li>{esc(item)}</li>" for item in errors) + "</ul></div>"
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
        inputs=job, **details, quote_status=outcome["status"], total=outcome["total"],
        estimate_range=outcome["estimate_range"], deposit_due=outcome["deposit_due"],
        still_needed=outcome["still_needed"], notes_from_quote=outcome["notes"], slot_held=False,
    )
    if outcome["status"] in DEAD_STATUSES:
        log_event(STREAM, "request", id=None, outcome=f"refused_{outcome['status']}", **shared)
        log_event(STREAM, "dead_end", source="request", reason=outcome["status"], inputs=job, notes=outcome["notes"])
        if as_json:
            return JSONResponse({"outcome": f"refused_{outcome['status']}", "summary": headline(outcome), "notes": outcome["notes"]}, status_code=422)
        body = (
            f"<h1>This request wasn't sent</h1>{outcome_html(outcome)}"
            "<h2>The rules behind this</h2>" + facts_used_html(outcome["fact_ids"])
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
        return JSONResponse({
            "id": request_id,
            "outcome": "received",
            "status_url": f"{BASE_URL}{status_path}",
            "slot_held": False,
            "summary": headline(outcome),
            "total": outcome["total"],
            "still_needed": outcome["still_needed"],
            "what_happens_next": [FACT["next_step.reply"]["statement"], FACT["next_step.slot-not-held"]["statement"]],
        })
    body = (
        f"<h1>Request received by {esc(NAME)}</h1>"
        f'<p class="answer">Request {esc(request_id)} was received, and no slot is held yet.</p>'
        f'<p>Status page: <a href="{esc(status_path)}">{esc(BASE_URL + status_path)}</a></p>'
        + outcome_html(outcome)
        + "<h2>What happens next</h2>" + facts_used_html(["next_step.reply", "next_step.slot-not-held", "policies.deposit"])
    )
    return page(f"Request received: {NAME}", body)


def ask_form(question: str = "", error: str = "") -> str:
    error_html = f'<div class="error"><p>{esc(error)}</p></div>' if error else ""
    return (
        f"{error_html}"
        '<form method="post" action="/ask"><label for="question">Question</label>'
        f'<textarea id="question" name="question" rows="5">{esc(question)}</textarea>'
        '<br><button type="submit">Pass this to the owner</button></form>'
    )


@app.get("/ask")
async def ask_get(request: Request):
    params = await read_params(request)
    body = (
        f"<h1>Ask {esc(NAME)} a question</h1>"
        "<p>This passes a question to the owner and returns a status page. It doesn't generate an answer, and it needs no contact details. "
        'The rules this site already holds are on <a href="/">the main page</a>.</p>'
        + ask_form(first(params, "question", "q"))
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
