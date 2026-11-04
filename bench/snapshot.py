"""Save dated copies of a site and the mock web for the local search backend.

Usage: uv run python -m bench.snapshot before|after|control
Crawls the site and the mock directory and competitors for that variant into
corpus/<variant>/. The resource is left out on purpose, so in the "after" runs
the only way to reach it is the visible link on the site.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from bench.world import WORLD_HOSTS

ROOT = Path(__file__).resolve().parent.parent
SITE = {"before": 8101, "after": 8102, "control": 8104}
WORLD = {"before": 8105, "after": 8106, "control": 8107}


def extract(html: str) -> tuple[str, str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    title = soup.title.get_text(strip=True) if soup.title else ""
    return title, " ".join(soup.get_text(" ").split()), links


def crawl(start: str, out: Path, fetched_at: str) -> int:
    start_netloc = urlparse(start).netloc
    seen, queue, count = set(), [start], 0
    with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "corpus-snapshot"}) as client:
        while queue and count < 60:
            url = urldefrag(queue.pop(0))[0]
            if url in seen:
                continue
            seen.add(url)
            try:
                resp = client.get(url)
            except httpx.HTTPError:
                continue
            if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
                continue
            title, text, links = extract(resp.text)
            name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".json"
            (out / name).write_text(json.dumps({"url": url, "title": title, "text": text, "fetched_at": fetched_at}, indent=1))
            count += 1
            for link in links:
                absolute = urljoin(url, link)
                if urlparse(absolute).netloc == start_netloc:
                    queue.append(absolute)
    return count


def snapshot(variant: str) -> int:
    out = ROOT / "corpus" / variant
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    fetched_at = datetime.now(UTC).date().isoformat()
    total = crawl(f"http://cormorant.localhost:{SITE[variant]}/", out, fetched_at)
    for host in WORLD_HOSTS:
        total += crawl(f"http://{host}:{WORLD[variant]}/", out, fetched_at)
    return total


if __name__ == "__main__":
    for name in sys.argv[1:] or ["before", "after", "control"]:
        print(name, snapshot(name), "pages")
