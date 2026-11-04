"""Start every local server. Each binds both 127.0.0.1 and ::1, because
*.localhost resolves to ::1 from Python here and asyncio's IPv6 sockets are v6-only.

  8101  before site      http://cormorant.localhost:8101
  8102  after site       http://cormorant.localhost:8102
  8103  resource         http://agents.cormorant.localhost:8103
  8104  control page     http://cormorant.localhost:8104
  8105-7 mock directory and competitors, linking to the before, after and control site
"""
from __future__ import annotations

import asyncio
import socket
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SITE = "http://cormorant.localhost"


def build_apps(only: set[str] | None) -> list[tuple[int, object]]:
    """Import lazily, so the control page can run while the site is being built."""
    apps: list[tuple[int, object]] = []
    want = lambda name: only is None or name in only  # noqa: E731
    if want("site"):
        from demo_site.app import create_app

        apps += [(8101, create_app("before")), (8102, create_app("after"))]
    if want("resource"):
        from demo_resource.app import app as resource_app

        apps.append((8103, resource_app))
    if want("control"):
        from bench.control import create_control_app

        apps.append((8104, create_control_app()))
    if want("world"):
        from bench.world import create_world_app

        apps += [(8105, create_world_app(f"{SITE}:8101")), (8106, create_world_app(f"{SITE}:8102")), (8107, create_world_app(f"{SITE}:8104"))]
    return apps


def sockets_for(port: int) -> list[socket.socket]:
    out = []
    for family, addr in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        s = socket.socket(family, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if family == socket.AF_INET6:
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        s.bind((addr, port))
        s.set_inheritable(True)
        out.append(s)
    return out


async def main() -> None:
    only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
    apps = build_apps(only)
    tasks = []
    for port, app in apps:
        server = uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))
        tasks.append(server.serve(sockets=sockets_for(port)))
    print("serving:", ", ".join(str(p) for p, _ in apps), flush=True)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
