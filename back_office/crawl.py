"""Read a business's website. Exa reads public sites, and Exa can't reach localhost,
so local sites use the consumer agent's own page parser.
"""

from __future__ import annotations

import base64
import re
from urllib.parse import urldefrag, urlparse

import httpx

from consumer_agent.tools import USER_AGENT, ExaBackend, parse_html

SKIP_IMAGE = re.compile(r"(logo|icon|favicon|sprite|avatar|pixel|\.svg)", re.IGNORECASE)
SKIP_LINK = re.compile(r"\.(pdf|zip|jpe?g|png|gif|svg|css|js|ico|xml)(\?|$)", re.IGNORECASE)
MAX_TEXT = 20_000


def is_local(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host in ("localhost", "127.0.0.1", "::1") or host.endswith(".localhost") or host.endswith(".test")


async def crawl_direct(url: str, max_pages: int = 12) -> list[dict]:
    """Breadth-first over one host, using plain requests."""
    host = urlparse(url).netloc
    queue, seen, pages = [url], set(), []
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"user-agent": USER_AGENT}) as client:
        while queue and len(pages) < max_pages:
            current = urldefrag(queue.pop(0))[0]
            key = current.rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            try:
                response = await client.get(current)
            except httpx.HTTPError:
                continue
            if response.status_code >= 400 or "html" not in response.headers.get("content-type", "html"):
                continue
            page = parse_html(response.text, str(response.url))
            pages.append({"url": str(response.url), "title": page["title"], "text": page["text"][:MAX_TEXT], "images": page["images"], "via": "direct"})
            for link in page["links"]:
                target = urldefrag(link["url"])[0]
                if urlparse(target).netloc == host and target.rstrip("/") not in seen and not SKIP_LINK.search(target):
                    queue.append(target)
    return pages


async def crawl_exa(url: str, max_pages: int = 12) -> list[dict]:
    exa = ExaBackend()
    data = await exa._post(
        "/contents",
        {
            "urls": [url],
            "text": {"maxCharacters": MAX_TEXT},
            "subpages": max(max_pages - 1, 0),
            "subpageTarget": ["pricing", "prices", "services", "book", "faq", "about", "contact", "policies", "areas"],
            "extras": {"imageLinks": 15},
            "maxAgeHours": 0,
            "livecrawlTimeout": 30000,
        },
    )
    pages = []
    for result in data.get("results", []):
        for item in [result, *(result.get("subpages") or [])]:
            if item.get("text"):
                images = [{"alt": "", "src": src} for src in (item.get("extras") or {}).get("imageLinks") or []]
                pages.append({"url": item.get("url") or url, "title": item.get("title") or "", "text": item["text"][:MAX_TEXT], "images": images, "via": "exa"})
    return pages[:max_pages]


def _clean(pages: list[dict]) -> list[dict]:
    """Drop non-web entries such as mailto links, and the same page listed twice."""
    seen, out = set(), []
    for page in pages:
        key = page["url"].rstrip("/")
        if page["url"].startswith("http") and key not in seen:
            seen.add(key)
            out.append(page)
    return out


async def crawl(url: str, max_pages: int = 12) -> list[dict]:
    """Exa reads the text of public sites, and a plain crawl fills in pages and images Exa misses."""
    if is_local(url):
        return await crawl_direct(url, max_pages)
    try:
        exa_pages = _clean(await crawl_exa(url, max_pages))
    except Exception:
        exa_pages = []
    try:
        direct = {p["url"].rstrip("/"): p for p in _clean(await crawl_direct(url, max_pages))}
    except Exception:
        direct = {}
    merged = []
    for page in exa_pages:
        twin = direct.pop(page["url"].rstrip("/"), None)
        if twin and not page["images"]:
            page["images"] = twin["images"]
        merged.append(page)
    return (merged + list(direct.values()))[:max_pages]


async def fetch_images(pages: list[dict], limit: int = 4) -> list[dict]:
    """Download images likely to hold facts as data URLs, so a model can read them from any host."""
    found, seen = [], set()
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"user-agent": USER_AGENT}) as client:
        for page in pages:
            for image in page.get("images", []):
                src = image.get("src") or ""
                if not src.startswith("http") or src in seen or SKIP_IMAGE.search(src):
                    continue
                seen.add(src)
                try:
                    response = await client.get(src)
                except httpx.HTTPError:
                    continue
                kind = response.headers.get("content-type", "").split(";")[0]
                if response.status_code >= 400 or not kind.startswith("image/") or not 2_000 < len(response.content) < 5_000_000:
                    continue
                encoded = base64.b64encode(response.content).decode()
                found.append({"src": src, "alt": image.get("alt", ""), "page": page["url"], "data_url": f"data:{kind};base64,{encoded}"})
                if len(found) >= limit:
                    return found
    return found
