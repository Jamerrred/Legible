"""Put the public page online on your own Cloudflare account: uv run python scripts/deploy.py

It signs you in if needed, creates the database, deploys edge/, sets the private password between
the app and the page, and points .env at the live address. A free Cloudflare account is enough.
Run it again after you change edge/.

The owner app stays on your computer, because it has no login.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from start import EDGE, ROOT, prepare_env, set_env

NAME = "legible"
CONFIG = "wrangler.deploy.toml"
WRANGLER = ["npx", "--yes", "wrangler@4"]
ENV = {**os.environ, "WRANGLER_SEND_METRICS": "false"}
DATABASE = Path(os.environ.get("LEGIBLE_DB_PATH", ROOT / "legible" / "legible.db"))


def wrangler(*args: str, stdin: str | None = None, check: bool = True) -> str:
    result = subprocess.run([*WRANGLER, *args], cwd=EDGE, env=ENV, input=stdin, capture_output=True, text=True)
    if check and result.returncode:
        sys.exit(f"\nwrangler {args[0]} failed:\n{result.stdout}\n{result.stderr}\n")
    return result.stdout


def sign_in() -> None:
    if "not authenticated" in wrangler("whoami", check=False).lower():
        print("Opening your browser so you can sign in to Cloudflare...")
        subprocess.run([*WRANGLER, "login"], cwd=EDGE, env=ENV, check=True)


def database_id() -> str:
    def find() -> str | None:
        return next((db["uuid"] for db in json.loads(wrangler("d1", "list", "--json")) if db["name"] == NAME), None)

    found = find()
    if not found:
        print(f"Creating the database '{NAME}'...")
        wrangler("d1", "create", NAME)
        found = find()
    if not found:
        sys.exit(f"\nThe database '{NAME}' wasn't created. Check your Cloudflare account, then run this again.\n")
    return found


def write_config(uuid: str) -> None:
    """The repository's wrangler.toml has a placeholder ID for local use, so yours stays out of git."""
    text = (EDGE / "wrangler.toml").read_text()
    (EDGE / CONFIG).write_text(re.sub(r'^database_id = .*$', f'database_id = "{uuid}"', text, flags=re.MULTILINE))


def wait_until_ready(url: str, token: str, seconds: int = 45) -> None:
    request = urllib.request.Request(f"{url}/admin/businesses/deploy-check/events", headers={"authorization": f"Bearer {token}", "user-agent": "legible-app"})
    deadline = time.time() + seconds
    last = "no answer"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    return
                last = f"HTTP {response.status}"
        except urllib.error.HTTPError as error:
            last = f"HTTP {error.code}"
        except OSError as error:
            last = str(error)
        time.sleep(2)
    sys.exit(f"\nThe page deployed, but it isn't answering properly at {url} ({last}). Wait a minute, then run this again.\n")


def move_websites(url: str, token: str) -> None:
    """Published websites follow the page to its new home. Activity from the old address doesn't."""
    if not DATABASE.exists():
        return
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DELETE FROM event")
        connection.execute("UPDATE website SET event_cursor = 0, revised_through = 0")
    connection.close()
    os.environ.update(LEGIBLE_EDGE_URL=url, LEGIBLE_ADMIN_TOKEN=token)
    sys.path.insert(0, str(ROOT))
    from legible import edge, store, work

    for site in store.query("SELECT id, slug FROM website WHERE published_version > 0"):
        asyncio.run(work.publish(site["id"]))
        print(f"  Published {edge.link_for(site['slug'])}")


def main() -> None:
    values = prepare_env()
    token, previous = values["LEGIBLE_ADMIN_TOKEN"], values["LEGIBLE_EDGE_URL"].rstrip("/")
    sign_in()
    write_config(database_id())
    print("Setting up the database...")
    wrangler("d1", "execute", NAME, "--remote", "--yes", "--file=schema.sql", "--config", CONFIG)
    print("Deploying the public page...")
    match = re.search(r"https://\S+\.workers\.dev", wrangler("deploy", "--config", CONFIG))
    if not match:
        sys.exit("\nThe page deployed, but its address wasn't in the output. Find it under Workers & Pages in the Cloudflare dashboard, then set LEGIBLE_EDGE_URL in .env.\n")
    url = match.group(0)
    wrangler("secret", "put", "ADMIN_TOKEN", "--config", CONFIG, stdin=token)
    wait_until_ready(url, token)
    set_env("LEGIBLE_EDGE_URL", url)
    if previous != url:
        move_websites(url, token)
    print(f"\nYour public page is online at {url}\nPages live at {url}/b/<your-website>\n\nStart or restart Legible: uv run python scripts/start.py\n")


if __name__ == "__main__":
    main()
