"""Start the local servers. Usage: uv run python scripts/serve.py [site,resource,control,world]

  8101    "before" site    http://cormorant.localhost:8101
  8102    "after" site     http://cormorant.localhost:8102
  8103    resource         http://agents.cormorant.localhost:8103
  8104    control page     http://cormorant.localhost:8104
  8105-7  mock directory and competitors, linking to the before, after and control site

Each server binds both 127.0.0.1 and ::1, because *.localhost resolves to ::1 from Python
on macOS and asyncio's IPv6 sockets are v6-only.
"""

from __future__ import annotations

import asyncio
import socket
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bench.control import create_control_app  # noqa: E402
from bench.world import create_world_app  # noqa: E402
from demo_resource.app import app as resource_app  # noqa: E402
from demo_site.app import create_app  # noqa: E402

SITE = "http://cormorant.localhost"
GROUPS = {
    "site": lambda: [(8101, create_app("before")), (8102, create_app("after"))],
    "resource": lambda: [(8103, resource_app)],
    "control": lambda: [(8104, create_control_app())],
    "world": lambda: [(port, create_world_app(f"{SITE}:{site_port}")) for port, site_port in ((8105, 8101), (8106, 8102), (8107, 8104))],
}


def sockets_for(port: int) -> list[socket.socket]:
    sockets = []
    for family, address in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if family == socket.AF_INET6:
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        sock.bind((address, port))
        sock.set_inheritable(True)
        sockets.append(sock)
    return sockets


async def main() -> None:
    wanted = sys.argv[1].split(",") if len(sys.argv) > 1 else list(GROUPS)
    apps = [entry for group in wanted for entry in GROUPS[group]()]
    servers = [
        uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False)).serve(sockets=sockets_for(port)) for port, app in apps
    ]
    print("serving:", ", ".join(str(port) for port, _ in apps), flush=True)
    await asyncio.gather(*servers)


if __name__ == "__main__":
    asyncio.run(main())
