"""The rest of the mock web: a stale directory and a few thin competitor sites.

The local search backend indexes these next to the business's site, so the agent
has to build queries, filter results and tell the merchant's own pages from a
listing. The directory's wrong claims come from the facts file, where they're
recorded as false.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from mf_core.business import load_facts

WORLD_HOSTS = ["bayautopages.localhost", "sunsetshine.localhost", "ferrybuildingautocare.localhost", "peninsulasuds.localhost"]

COMPETITORS = {
    "sunsetshine.localhost": (
        "Sunset Shine Auto Spa",
        "Hand car wash and detailing in the Outer Sunset, San Francisco. Drop your car off at our shop. "
        "Interior and exterior packages available. Prices depend on the vehicle, so please call for a quote. Closed Mondays.",
    ),
    "ferrybuildingautocare.localhost": (
        "Ferry Point Auto Care",
        "Downtown San Francisco garage detailing for commuters. We work in partner parking garages only. "
        "Express wash and interior vacuum while you work. Monthly memberships for garage customers. Contact us for rates.",
    ),
    "peninsulasuds.localhost": (
        "Peninsula Suds Mobile Wash",
        "Mobile car wash on the Peninsula, from Burlingame to Palo Alto. Exterior wash and quick vacuum at your home or office. "
        "Sedans from $45. We don't do deep interior work or stain removal. Not serving San Francisco at this time.",
    ),
}


def _shell(title: str, body: str) -> str:
    return (
        f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{title}</title>"
        "<style>body{font:16px/1.5 Georgia,serif;max-width:680px;margin:40px auto;padding:0 16px;color:#222}</style>"
        f"</head><body>{body}</body></html>"
    )


def _directory_home(listing: str, port: str) -> str:
    return _shell(
        "Bay Auto Pages: car care listings in the San Francisco Bay Area",
        "<h1>Bay Auto Pages</h1><p>Local listings for car care around the San Francisco Bay Area. "
        "Listings are submitted by users and may be out of date.</p>"
        f"<h2>Detailing and car wash</h2><ul>{listing}"
        f"<li><a href='http://sunsetshine.localhost:{port}/'>Sunset Shine Auto Spa</a>, Outer Sunset</li>"
        f"<li><a href='http://ferrybuildingautocare.localhost:{port}/'>Ferry Point Auto Care</a>, Downtown</li>"
        f"<li><a href='http://peninsulasuds.localhost:{port}/'>Peninsula Suds Mobile Wash</a>, Peninsula</li>"
        "</ul>",
    )


def create_world_app(site_url: str) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    facts = load_facts()
    claims = {f["id"]: f["value"] for f in facts["facts"] if f["status"] == "false_third_party_claim"}
    price = next(v for v in claims.values() if "claimed_price" in v)
    services = next(v for v in claims.values() if "claimed" in v)
    name = facts["business"]["name"]

    @app.get("/robots.txt", response_class=PlainTextResponse)
    def robots():
        return "User-agent: *\nAllow: /\n"

    @app.get("/{path:path}", response_class=HTMLResponse)
    def page(path: str, request: Request):
        host, _, port = (request.headers.get("host") or "").partition(":")
        if host in COMPETITORS:
            title, text = COMPETITORS[host]
            return _shell(title, f"<h1>{title}</h1><p>{text}</p>")
        if path.strip("/") == "cormorant-mobile-detailing":
            return _shell(
                f"{name} | Bay Auto Pages",
                f"<h1>{name}</h1><p>Mobile detailing, San Francisco, CA. Unclaimed listing, last updated {price['last_updated']}.</p>"
                f"<p><strong>Full detail: flat ${price['claimed_price']}.</strong></p>"
                f"<p>Services: {', '.join(services['claimed'])}, interior and exterior detailing.</p>"
                f"<p>Website: <a href='{site_url}/'>{site_url}</a></p>",
            )
        listing = f"<li><a href='/cormorant-mobile-detailing'>{name}</a>, mobile, San Francisco. Full detail ${price['claimed_price']}</li>"
        return _directory_home(listing, port)

    return app
