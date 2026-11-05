"""Start Legible on this computer with one command: uv run python scripts/start.py

It prepares .env, then runs two things until you press Ctrl+C:
  - the public resource, a Cloudflare Worker running locally, at http://127.0.0.1:8787
  - the owner app, at http://127.0.0.1:8200

No Cloudflare account is needed. Set LEGIBLE_PORT to use a different port for the app.

Add --demo to run the scripted demo copy instead, on port 8300. It plays back sample data, spends
no AI credit and needs no API keys. Open /demo/reset to start a new take.
"""

from __future__ import annotations

import os
import re
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
EDGE = ROOT / "edge"
LOCAL_EDGE = "http://127.0.0.1:8787"


def read_env() -> dict[str, str]:
    values = {}
    for line in ENV.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def set_env(key: str, value: str) -> None:
    text = ENV.read_text()
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    text = pattern.sub(f"{key}={value}", text) if pattern.search(text) else text.rstrip() + f"\n{key}={value}\n"
    ENV.write_text(text)


def prepare_env(demo: bool = False) -> dict[str, str]:
    if not ENV.exists():
        shutil.copy(ROOT / ".env.example", ENV)
        print("Created .env from .env.example")
    values = read_env()
    if not values.get("LEGIBLE_ADMIN_TOKEN"):
        set_env("LEGIBLE_ADMIN_TOKEN", secrets.token_urlsafe(32))
    if not values.get("LEGIBLE_EDGE_URL"):
        set_env("LEGIBLE_EDGE_URL", LOCAL_EDGE)
    values = read_env()
    missing = [key for key in ("OPENROUTER_API_KEY", "EXA_API_KEY") if not values.get(key)]
    if missing and not demo:
        sys.exit(f"\nAdd {' and '.join(missing)} to .env, then run this again.\nThe README says where to get them.\n")
    return values


def wait_for(url: str, seconds: int = 60) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except urllib.error.HTTPError:
            return True
        except OSError:
            time.sleep(0.5)
    return False


def port_in_use(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.5)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def main() -> None:
    demo = "--demo" in sys.argv[1:]
    values = prepare_env(demo)
    edge_url = values["LEGIBLE_EDGE_URL"].rstrip("/")
    edge_host = urlparse(edge_url)
    processes: list[subprocess.Popen] = []
    port = os.environ.get("LEGIBLE_PORT", "8300" if demo else "8200")
    if port_in_use(int(port)):
        sys.exit(f"\nAnother program is using port {port}. Close it, or choose another port: LEGIBLE_PORT=8400 uv run python scripts/start.py\n")

    if edge_host.hostname in ("127.0.0.1", "localhost"):
        if port_in_use(edge_host.port or 8787):
            sys.exit(f"\nAnother program is using port {edge_host.port or 8787}, which the local public page needs. Close it, or stop your other copy of Legible.\n")
        if not shutil.which("npx"):
            sys.exit("\nNode.js is needed for the local resource. Install it from https://nodejs.org, then run this again.\n")
        (EDGE / ".dev.vars").write_text(f"ADMIN_TOKEN={values['LEGIBLE_ADMIN_TOKEN']}\n")
        env = {**os.environ, "WRANGLER_SEND_METRICS": "false"}
        print("Preparing the local resource. The first run downloads a few things...")
        subprocess.run(
            ["npx", "--yes", "wrangler@4", "d1", "execute", "legible", "--local", "--file=schema.sql"],
            cwd=EDGE, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True,
        )  # fmt: skip
        processes.append(
            subprocess.Popen(
                ["npx", "--yes", "wrangler@4", "dev", "--port", str(edge_host.port or 8787), "--ip", "127.0.0.1"],
                cwd=EDGE, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )  # fmt: skip
        )
        if not wait_for(f"{edge_url}/"):
            for process in processes:
                process.terminate()
            sys.exit(f"\nThe local resource didn't start at {edge_url}. Is another program using that port?\n")

    app_env = {**os.environ, "LEGIBLE_DEMO": "1", "LEGIBLE_DB_PATH": "legible/demo.db", "LEGIBLE_CRON_HOURS": "999"} if demo else None
    processes.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "legible.api:app", "--port", port, "--log-level", "warning"], cwd=ROOT, env=app_env))
    app_url = f"http://127.0.0.1:{port}"
    if not wait_for(f"{app_url}/health"):
        for process in processes:
            process.terminate()
        sys.exit(f"\nThe app didn't start. Is another program using port {port}?\n")

    print(f"\nLegible is running.\n\n  Open the app:   {app_url}\n  Public pages:   {edge_url}/b/<your-website>\n\nKeep this window open. Press Ctrl+C to stop.\n")
    if not os.environ.get("LEGIBLE_NO_BROWSER"):
        webbrowser.open(app_url)

    stop = {"now": False}
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.update(now=True))
    while not stop["now"] and all(process.poll() is None for process in processes):
        time.sleep(0.5)
    for process in processes:
        process.terminate()
    print("\nStopped.")


if __name__ == "__main__":
    main()
