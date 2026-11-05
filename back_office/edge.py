"""Talk to the public Worker: publish a record, pull events and items, send owner replies."""

from __future__ import annotations

import os

import httpx

from consumer_agent.llm import load_env

load_env()
EDGE_URL = os.environ.get("MF_EDGE_URL", "http://127.0.0.1:8787").rstrip("/")


def _headers() -> dict:
    token = os.environ.get("MF_ADMIN_TOKEN")
    if not token:
        raise RuntimeError("MF_ADMIN_TOKEN is not set")
    return {"authorization": f"Bearer {token}", "user-agent": "musefront-back-office"}


def link_for(slug: str) -> str:
    return f"{EDGE_URL}/b/{slug}"


async def _call(method: str, path: str, **kwargs) -> dict:
    async with httpx.AsyncClient(timeout=30, headers=_headers()) as client:
        response = await client.request(method, f"{EDGE_URL}{path}", **kwargs)
        response.raise_for_status()
        return response.json()


async def put_business(slug: str, record: dict, noindex: bool = True) -> dict:
    return await _call("PUT", f"/admin/businesses/{slug}", json={"record": record, "noindex": noindex})


async def delete_business(slug: str) -> dict:
    return await _call("DELETE", f"/admin/businesses/{slug}")


async def get_events(slug: str, after: int = 0) -> list[dict]:
    return (await _call("GET", f"/admin/businesses/{slug}/events", params={"after": after}))["events"]


async def get_items(slug: str) -> list[dict]:
    return (await _call("GET", f"/admin/businesses/{slug}/items"))["items"]


async def reply(item_id: str, status: str, message: str) -> dict:
    return await _call("POST", f"/admin/items/{item_id}/reply", json={"status": status, "message": message})
