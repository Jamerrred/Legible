"""The site's page sections, and the page shell and renderers that turn them into HTML or markdown."""

from __future__ import annotations

import re

from business_core.business import quote
from fastapi import Request
from fastapi.responses import HTMLResponse, Response

from sample_resource.config import (
    ADDONS,
    BASE_URL,
    BIZ,
    CONDITIONS,
    DATA,
    FACT,
    FACTS,
    FEES,
    MODEL,
    NAME,
    QUOTE_VALID_DAYS,
    RULES,
    SERVICES,
    SIZES,
    SLOT_DAYS,
    SLUG,
    TAX_RATE,
    ZONES,
)
from sample_resource.formatting import (
    addon_price_cells,
    clock,
    esc,
    link,
    local_now,
    long_date,
    money,
    service_name,
    stamp,
    whole,
    words,
)
from sample_resource.quoting import open_slots

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
    return [fact["id"] for fact in FACTS if fact["category"] == category and fact["status"] == status and fact["id"] not in skip]


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
                rows = "".join("<tr>" + "".join(f"<td>{inline_html(str(cell))}</td>" for cell in row) + "</tr>" for row in block[2])
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
        (
            "p",
            f"As of {moment}, these arrival windows are open in the next {SLOT_DAYS} days. "
            "A window not listed here is booked, closed or inside the 24-hour notice period.",
        ),
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

    addon_values = ", ".join(f"`{key}` ({value['label'].lower()})" for key, value in ADDONS.items())
    condition_values = ", ".join(f"`{key}` ({value['label'].lower()})" for key, value in CONDITIONS.items())
    sections.append(
        (
            "addresses",
            "Addresses on this site",
            [
                (
                    "ul",
                    [
                        "[/services](/services) has one page per offering, with its price rules, dependencies and a prefilled quote link.",
                        "[/quote](/quote) takes a job's details and returns a total or range, line items, what's still needed, a quote ID and an expiry. It takes no personal details. It works as a plain link or a form, and `format=json` returns JSON.",
                        "[/request](/request) sends a booking or quote request. It's the only address that asks for contact details, and a link with job details opens it prefilled and ready to confirm.",
                        "[/ask](/ask) passes a question to the owner.",
                        "`/r/{id}` is the status page for one request or question.",
                        "[/index.md](/index.md) is this page in markdown, and `/` returns the same markdown when the Accept header asks for `text/markdown`.",
                    ],
                ),
                ("h3", "Values /quote and /request accept"),
                (
                    "table",
                    ["Parameter", "What it means", "Valid values"],
                    [
                        [
                            "service",
                            "The service",
                            "`exterior`, `interior`, `full` or `flagship`, or any everyday word listed under Customer's words",
                        ],
                        ["size", "The size class", "`small`, `midsize`, `large` or `oversized`, or Class A, B, C or D"],
                        [
                            "vehicle",
                            "The vehicle's make and model or type, which sets the size class when it's listed",
                            "Any text, such as a make and model",
                        ],
                        ["addons", "Add-ons, separated by commas", addon_values],
                        ["conditions", "Conditions that apply, separated by commas", condition_values],
                        ["zip", "The 5-digit ZIP code where the vehicle is parked", "Any of the listed ZIP codes under Service area"],
                        [
                            "when",
                            "The date, with an optional window, which brings in Saturday, after-hours and same-day rules",
                            "`YYYY-MM-DD`, optionally followed by `morning`, `afternoon` or `evening`, or `today` or `tomorrow`",
                        ],
                        ["recurring", "The recurring plan", "`every-2-weeks` or `every-4-weeks`"],
                        ["vehicle_count", "The number of vehicles at one address on one day", "A whole number"],
                        ["budget", "A budget in US dollars, which is compared with the total and never changes the price", "A number"],
                        ["format", "The response format on /quote", "`json`, or leave it out for HTML"],
                    ],
                ),
                (
                    "p",
                    "For example, [/quote?service=full&size=midsize&zip=94110](/quote?service=full&size=midsize&zip=94110) returns the total for a full detail on a midsize vehicle in ZIP code 94110, and a link to [/request](/request) with the same values opens the request form with them filled in.",
                ),
                (
                    "p",
                    f"A quote ID expires {QUOTE_VALID_DAYS} days after it's issued. That limit is set by this site, because the owner hasn't stated how long a quoted price stays valid. A quote doesn't hold a slot.",
                ),
            ],
        )
    )

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
    sections.append(
        (
            "words",
            "Customer's words",
            [
                facts_block(ids_in("vocabulary")),
                ("p", "This table maps everyday words onto the business's categories and the values /quote takes."),
                ("table", ["Category", "Value", "Words that map to it"], word_rows),
            ],
        )
    )

    sections.append(
        (
            "offerings",
            "Offerings and what each includes",
            [
                facts_block(
                    ids_in("services"),
                    {f"services.{key}": f"[Page for this service](/services/{key})" for key in SERVICES},
                ),
                (
                    "p",
                    "Add-ons have their own pages: "
                    + ", ".join(f"[{value['label']}](/services/{key})" for key, value in ADDONS.items())
                    + ". Their prices and dependencies are under Add-on dependencies.",
                ),
            ],
        )
    )

    ambiguous = MODEL["vehicles"]["ambiguous"]
    camper = MODEL["vehicles"]["camper"]
    notes = list(dict.fromkeys(entry["note"] for entry in ambiguous.values()))
    sections.append(
        (
            "sizes",
            "Size classes and vehicles",
            [
                facts_block(ids_in("size_classes"), size_details()),
                (
                    "ul",
                    notes
                    + [
                        camper["note"] + " Words for this: " + ", ".join(camper["terms"]) + ".",
                        "A vehicle that isn't listed has no assumed size class, and a technician checks the class on arrival ([fact](#fact-conditions.assessed-on-arrival)).",
                        "The Tesla Cybertruck has no size class yet ([fact](#fact-eligibility.cybertruck)).",
                    ],
                ),
            ],
        )
    )

    price_rows = [[service_name(key)] + [whole(value["prices"][size]) for size in SIZES] + ["Fixed"] for key, value in SERVICES.items()]
    addon_rows = [
        [value["label"]] + addon_price_cells(value) + ["Range" if "range" in value else ("Flat" if "flat" in value else "Fixed")]
        for value_key, value in ADDONS.items()
    ]
    sections.append(
        (
            "prices",
            "Price structure",
            [
                facts_block(ids_in("pricing", skip=("pricing.structure",))),
                ("table", ["Service"] + SIZES + ["Type"], price_rows),
                ("table", ["Add-on"] + SIZES + ["Type"], addon_rows),
                (
                    "ul",
                    [
                        "Fixed: every service price is a fixed amount for its size class, and every add-on is a fixed amount for its size class except the two below.",
                        'From: a "starting at" price is the small-class price, and any larger vehicle costs more.',
                        "Range: odour treatment is the only range, and a technician settles it on arrival with a smell test.",
                        "Flat: headlight restoration is the same price at any vehicle size.",
                        "Quote-only: more than 10 vehicles at once has no set price ([fact](#fact-fleet.over-10)).",
                        "What moves a total: size class, add-ons, defined conditions, the generator fee, Saturday, after-hours or same-day timing, the ZIP code's travel fee, and any recurring or fleet discount.",
                    ],
                ),
            ],
        )
    )

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
    sections.append(
        (
            "total",
            "How the full total is worked out",
            [
                facts_block(["pricing.structure", "tax.sales-tax"]),
                ("p", f"**{formula_text()}**"),
                (
                    "p",
                    f"Sales tax is {TAX_RATE * 100:g}%, rounded {MODEL['tax']['rounding']}. The travel fee isn't taxed. A recurring or fleet discount comes off the service price only. On a fleet job the service, add-ons and surcharges are multiplied by the number of vehicles, and there's one travel fee per visit. The deposit counts toward the total, and no tip is added.",
                ),
                ("table", ["Item", "Amount", "Taxed"], rate_rows),
                (
                    "ul",
                    [
                        worked_example(
                            "A full detail with shampoo on a midsize vehicle in ZIP code 94015",
                            service="full",
                            size="midsize",
                            addons=("shampoo",),
                            zip_code="94015",
                        ),
                        worked_example(
                            "An interior detail with odour treatment on a large vehicle in ZIP code 94110",
                            service="interior",
                            size="large",
                            addons=("odor",),
                            zip_code="94110",
                        ),
                    ],
                ),
            ],
        )
    )

    dependency_rows = [
        [f"[{value['label']}](/services/{key})"]
        + [addon_on_service(key, service_id) for service_id in SERVICES]
        + ["yes" if value["standalone"] else "no"]
        for key, value in ADDONS.items()
    ]
    sections.append(
        (
            "dependencies",
            "Add-on dependencies",
            [
                facts_block(ids_in("addons")),
                ("table", ["Add-on"] + [SERVICES[key]["marketing_name"] for key in SERVICES] + ["On its own"], dependency_rows),
            ],
        )
    )

    sections.append(
        (
            "conditions",
            "Defined conditions",
            [
                facts_block(ids_in("conditions")),
                (
                    "p",
                    "These conditions go in the `conditions` parameter of /quote: "
                    + "; ".join(f"`{key}` means {value['label'].lower()}" for key, value in CONDITIONS.items())
                    + ".",
                ),
            ],
        )
    )

    sections.append(
        (
            "eligibility",
            "Eligibility",
            [
                facts_block(ids_in("eligibility")),
                ("p", "Two eligibility questions aren't decided yet, and they're under [Unknown](#unknown)."),
            ],
        )
    )
    sections.append(("prerequisites", "Prerequisites", [facts_block(ids_in("prerequisites"))]))

    sections.append(
        (
            "area",
            "Service area",
            [
                facts_block(ids_in("service_area")),
                (
                    "table",
                    ["Area", "Travel fee per visit", "ZIP codes"],
                    [[zone["label"], whole(zone["fee"]), ", ".join(zone["zips"])] for zone in ZONES.values()],
                ),
            ],
        )
    )

    hours = FACT["availability.durations"]["value"]["hours"]
    sections.append(
        (
            "availability",
            "Availability",
            [
                facts_block(ids_in("availability")),
                (
                    "table",
                    ["Hours on site"] + SIZES,
                    [[service_name(key)] + [f"{hours[key][size]:g}" for size in SIZES] for key in SERVICES],
                ),
                ("h3", "Next open arrival windows"),
                *slots_block(),
            ],
        )
    )

    sections.append(("staff", "Staff differences", [facts_block(ids_in("staff"))]))
    sections.append(("policies", "Policies", [facts_block(ids_in("policies"))]))
    sections.append(("payment", "Payment", [facts_block(ids_in("payment"))]))
    sections.append(
        (
            "timing",
            "Timing rules and blackout dates",
            [
                facts_block(ids_in("timing")),
                (
                    "ul",
                    [
                        f"{long_date(item['start'])} to {long_date(item['end'])}: {item['reason']}"
                        if item["start"] != item["end"]
                        else f"{long_date(item['start'])}: {item['reason']}"
                        for item in RULES["blackout_ranges"]
                    ],
                ),
            ],
        )
    )
    sections.append(
        (
            "recurring",
            "Recurring plan and fleet jobs",
            [
                facts_block(ids_in("recurring") + ids_in("fleet")),
            ],
        )
    )
    sections.append(("gift-cards", "Gift cards", [facts_block(ids_in("gift_cards"))]))
    sections.append(
        (
            "not-offered",
            "Not offered",
            [
                facts_block(ids_with_status("not_offered"), not_offered_details()),
            ],
        )
    )
    sections.append(
        (
            "unknown",
            "Unknown: not decided or not known yet",
            [
                ("p", "Each item says what isn't decided or known and what would settle it."),
                facts_block(ids_with_status("unknown")),
            ],
        )
    )
    sections.append(("credentials", "Credentials", [facts_block(ids_in("credentials"))]))
    sections.append(
        (
            "next-step",
            "Next step and what happens after a request",
            [
                facts_block(ids_in("next_step")),
                (
                    "p",
                    "A request goes through [/request](/request), which asks for contact details and who's submitting, the customer or an agent acting for them. It returns a status page at `/r/{id}`.",
                ),
                (
                    "p",
                    "A question this page doesn't cover goes through [/ask](/ask), which passes it to the owner and returns a status page.",
                ),
            ],
        )
    )
    sections.append(
        (
            "listings",
            "Listings elsewhere that are wrong",
            [facts_block(ids_with_status("false_third_party_claim"), listing_details())],
        )
    )

    by_category: dict[str, list[str]] = {}
    for fact in FACTS:
        by_category.setdefault(fact["category"], []).append(fact["confirmed_on"])
    sections.append(
        (
            "freshness",
            "Freshness",
            [
                (
                    "p",
                    f"Every fact on this page shows the date it was last confirmed. This set of facts is current as of {long_date(DATA['as_of'])}. Open arrival windows are worked out when the page is requested.",
                ),
                (
                    "table",
                    ["Category", "Facts", "Oldest confirmation", "Newest confirmation"],
                    [
                        [category.replace("_", " "), len(dates), long_date(min(dates)), long_date(max(dates))]
                        for category, dates in by_category.items()
                    ],
                ),
            ],
        )
    )
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
        f'<p>Markdown version: <a href="/index.md">/index.md</a></p><nav><ul>{nav}</ul></nav>' + render_html(sections)
    )
    response = page(f"{NAME}: prices, rules and availability", body, "/index.md")
    response.headers["Vary"] = "Accept"
    return response


def main_markdown() -> Response:
    return markdown_response(render_markdown(f"{NAME}: prices, rules, availability and requests", main_intro(), main_sections()))


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
        (
            "what",
            "What it is and what it costs",
            [
                facts_block([f"services.{service_id}", f"pricing.{service_id}"]),
                ("table", ["Size class", "Price", "Time on site", "Link"], size_rows),
                (
                    "p",
                    f"A prefilled quote link such as [{link('/quote', service=service_id, size='midsize', zip='94110')}]({link('/quote', service=service_id, size='midsize', zip='94110')}) returns the total for one ZIP code, and [the request form]({link('/request', service=service_id)}) opens with this service filled in.",
                ),
            ],
        ),
        (
            "total",
            "How the total is worked out",
            [
                facts_block(["pricing.structure", "tax.sales-tax"]),
                ("p", f"**{formula_text()}**"),
                (
                    "p",
                    "Travel fee per visit: "
                    + "; ".join(f"{whole(zone['fee'])} for {zone['label']}" for zone in ZONES.values())
                    + ". The ZIP lists are under [Service area](/#area).",
                ),
            ],
        ),
        (
            "addons",
            "Add-ons and dependencies on this service",
            [
                ("table", ["Add-on", "On this service"] + SIZES, addon_rows),
            ],
        ),
        ("conditions", "Conditions that can change the price", [facts_block(condition_ids)]),
        (
            "requirements",
            "What the customer provides",
            [
                facts_block(
                    [
                        "prerequisites.power",
                        "prerequisites.water",
                        "prerequisites.parking",
                        "prerequisites.permission",
                        "prerequisites.belongings-keys",
                    ]
                ),
            ],
        ),
        ("limits", "What can rule it out", [facts_block(limit_ids)]),
        (
            "timing",
            "When it can happen",
            [
                facts_block(timing_ids),
                ("h3", "Next open arrival windows for this service"),
                *slots_block(service_id),
            ],
        ),
    ]
    if service_id in MODEL["recurring"]["services"]:
        sections.append(
            (
                "discounts",
                "Recurring plan and fleet jobs",
                [
                    facts_block(["recurring.plan", "fleet.discount", "fleet.terms"]),
                ],
            )
        )
    else:
        sections.append(
            (
                "discounts",
                "Discounts",
                [
                    (
                        "p",
                        f"{service['marketing_name']} isn't part of the recurring plan or the fleet discount, which cover the exterior wash, interior detail and full detail only.",
                    ),
                ],
            )
        )
    sections.append(
        (
            "policies",
            "Deposit and policies",
            [
                facts_block(["policies.deposit", "policies.cancellation", "policies.reschedule", "policies.no-show", "policies.weather"]),
            ],
        )
    )
    sections.append(("next-step", "Next step", [facts_block(["next_step.reply", "next_step.slot-not-held"])]))
    return sections


def addon_sections(addon_id: str):
    addon = ADDONS[addon_id]
    rows = []
    for service_id in SERVICES:
        state = addon_on_service(addon_id, service_id)
        chosen = [*addon["requires_addons"], addon_id]
        if state.startswith("available"):
            links = " · ".join(f"[{size}]({link('/quote', service=service_id, addons=','.join(chosen), size=size)})" for size in SIZES)
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
        (
            "dependencies",
            "Dependencies and prefilled quote links",
            [
                ("p", addon["dependency_note"] or "This add-on can be booked on its own with no other service."),
                ("table", ["Service", "This add-on on that service", "Quote by size class"], rows),
            ],
        ),
    ]
    if addon["standalone"]:
        own = link("/quote", addons=addon_id)
        sections[1][2].append(
            ("p", f"On its own: [{own}]({own}), and [the request form]({link('/request', addons=addon_id)}) opens with it filled in.")
        )
    sections += [
        (
            "total",
            "How the total is worked out",
            [
                facts_block(["pricing.structure", "tax.sales-tax"]),
                ("p", f"**{formula_text()}**"),
            ],
        ),
        ("next-step", "Next step", [facts_block(["next_step.reply", "next_step.slot-not-held"])]),
    ]
    return sections


def offering_title(offering_id: str) -> str:
    if offering_id in SERVICES:
        return f"{service_name(offering_id)} at {NAME}"
    return f"{ADDONS[offering_id]['label']} at {NAME}"


def offerings_sections():
    rows = [
        [
            f"[{service_name(key)}](/services/{key})",
            "Service",
            f"{whole(min(value['prices'].values()))} to {whole(max(value['prices'].values()))}",
        ]
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


def facts_used_html(fact_ids) -> str:
    items = "".join(
        f'<li id="fact-{esc(fid)}">{esc(FACT[fid]["statement"])}<div class="when">Confirmed on {long_date(FACT[fid]["confirmed_on"])}</div></li>'
        for fid in fact_ids
        if fid in FACT
    )
    return f'<ul class="facts">{items}</ul>' if items else ""
