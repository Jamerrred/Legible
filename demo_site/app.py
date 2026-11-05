"""The Cormorant Mobile Detailing site: Home, FAQ and Book."""

from __future__ import annotations

import ipaddress
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from demo_site.booking import register_booking
from legible_core.business import load_facts
from legible_core.logbook import log_event

HERE = Path(__file__).resolve().parent
PAGES = ["/", "/faq", "/book"]


def ip_range(host: str | None) -> str | None:
    if not host:
        return None
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return None
    prefix = 24 if address.version == 4 else 64
    return str(ipaddress.ip_network(f"{host}/{prefix}", strict=False))


def create_app(variant: str = "before") -> FastAPI:
    if variant not in ("before", "after"):
        raise ValueError("variant must be 'before' or 'after'")
    stream = f"site-{variant}"
    facts = load_facts("cormorant")
    model = facts["pricing_model"]
    starting = {key: service["prices"]["small"] for key, service in model["services"].items()}
    packages = [service["marketing_name"] for service in model["services"].values()]
    addons = [addon["label"] for addon in model["addons"].values()]

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static", check_dir=False), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    templates.env.trim_blocks = True
    templates.env.lstrip_blocks = True
    templates.env.globals["resource_url"] = os.environ.get("LEGIBLE_RESOURCE_BASE_URL", "http://agents.cormorant.localhost:8103")
    templates.env.globals.update(variant=variant, business=facts["business"])

    def render(request: Request, template_name: str, status_code: int = 200, **context):
        return templates.TemplateResponse(request, template_name, context, status_code=status_code)

    @app.middleware("http")
    async def log_page_hit(request: Request, call_next):
        log_event(
            stream,
            "page_hit",
            path=request.url.path,
            method=request.method,
            user_agent=request.headers.get("user-agent"),
            ip_range=ip_range(request.client.host if request.client else None),
            referer=request.headers.get("referer"),
        )
        return await call_next(request)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        if exc.status_code == 404:
            return render(request, "not_found.html", status_code=404)
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return render(request, "home.html", starting=starting, addons=addons)

    @app.get("/faq", response_class=HTMLResponse)
    async def faq(request: Request):
        return render(request, "faq.html")

    @app.get("/robots.txt", response_class=PlainTextResponse)
    async def robots(request: Request):
        base = str(request.base_url).rstrip("/")
        return f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"

    @app.get("/sitemap.xml")
    async def sitemap(request: Request):
        base = str(request.base_url).rstrip("/")
        urls = "".join(f"  <url><loc>{base}{path}</loc></url>\n" for path in PAGES)
        xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
        return Response(xml, media_type="application/xml")

    register_booking(app, stream, render, packages, addons)
    return app
