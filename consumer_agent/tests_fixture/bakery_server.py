"""Throwaway site for an invented bakery, for checking the agent's own tools.

Serves http://bakery.localhost:8190 on both 127.0.0.1 and ::1, and appends every request to a
JSONL file so a check can see exactly what reached the site.
"""

from __future__ import annotations

import argparse
import html
import io
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from PIL import Image, ImageDraw, ImageFont

PORT = 8190
LOG_PATH = "bakery_requests.jsonl"
_lock = threading.Lock()


def price_card() -> bytes:
    img = Image.new("RGB", (560, 160), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "Celebration cake", fill="black", font=ImageFont.load_default(size=36))
    draw.text((20, 80), "8-inch: $46", fill="black", font=ImageFont.load_default(size=44))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


PAGE = "<!doctype html><html><head><title>{title}</title></head><body><h1>{title}</h1>{body}</body></html>"
HOME = PAGE.format(title="Crumb and Ember Bakery", body="""
<p>Neighbourhood bakery in Oakmere. Open Tuesday to Saturday, 7:30am to 3pm.</p>
<h2>Prices</h2>
<ul><li>Sourdough loaf: $8.50</li><li>Rye loaf: $9.25</li></ul>
<h2>Cakes</h2>
<img src="/price-card.png" alt="Celebration cake price card">
<p><a href="/pickup">Pickup and delivery</a> | <a href="/order">Order a cake</a></p>""")
PICKUP = PAGE.format(title="Pickup and delivery", body="""
<p>Cakes need 48 hours' notice. Delivery within Oakmere costs $12. Pickup is free.</p>
<p><a href="/">Home</a> | <a href="/order">Order a cake</a></p>""")
ORDER = PAGE.format(title="Order a cake", body="""
<form method="post" action="/order">
<p><label for="name">Your name</label> <input id="name" name="name" required></p>
<p><label for="email">Email</label> <input id="email" name="email" type="email" required></p>
<p><label for="item">Cake</label>
<select id="item" name="item"><option>Celebration cake, 8-inch</option></select></p>
<p><label for="date">Pickup date</label> <input id="date" name="date" placeholder="YYYY-MM-DD" required></p>
<p><button type="submit">Send order request</button></p></form>""")


class Handler(BaseHTTPRequestHandler):
    def _record(self, body: str = "") -> None:
        with _lock, open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"method": self.command, "path": self.path, "ua": self.headers.get("User-Agent"), "body": body}) + "\n")

    def _send(self, content: bytes, kind: str = "text/html; charset=utf-8", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        self._record()
        pages = {"/": HOME, "/pickup": PICKUP, "/order": ORDER}
        path = self.path.split("?")[0]
        if path == "/price-card.png":
            self._send(price_card(), "image/png")
        elif path in pages:
            self._send(pages[path].encode())
        else:
            self._send(b"Not found", status=404)

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode()
        self._record(body)
        form = parse_qs(body)
        who = html.escape((form.get("name") or ["customer"])[0])
        done = PAGE.format(title="Order received", body=f"<p>Thank you, {who}. Your order request is received. Reference CE-4417.</p>")
        self._send(done.encode())

    def log_message(self, *args: object) -> None:
        pass


class V6Server(ThreadingHTTPServer):
    address_family = socket.AF_INET6


def main() -> None:
    global LOG_PATH
    p = argparse.ArgumentParser()
    p.add_argument("--log", default=LOG_PATH)
    p.add_argument("--port", type=int, default=PORT)
    a = p.parse_args()
    LOG_PATH = a.log
    servers = [ThreadingHTTPServer(("127.0.0.1", a.port), Handler), V6Server(("::1", a.port), Handler)]
    threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in servers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
