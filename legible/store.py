"""SQLite storage. Each call opens its own connection, so this is safe from any task."""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(os.environ.get("LEGIBLE_DB_PATH", Path(__file__).resolve().parent / "legible.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS website (
  id TEXT PRIMARY KEY, slug TEXT UNIQUE, name TEXT, url TEXT, stage TEXT, stage_note TEXT,
  published_version INTEGER DEFAULT 0, event_cursor INTEGER DEFAULT 0, revised_through INTEGER DEFAULT 0,
  pages TEXT DEFAULT '[]', created_at TEXT);
CREATE TABLE IF NOT EXISTS record_version (
  website_id TEXT, version INTEGER, record TEXT, reason TEXT, created_at TEXT, PRIMARY KEY (website_id, version));
CREATE TABLE IF NOT EXISTS inbox_item (
  id TEXT PRIMARY KEY, website_id TEXT, kind TEXT, status TEXT DEFAULT 'open', title TEXT, body TEXT,
  payload TEXT DEFAULT '{}', source TEXT, created_at TEXT, resolved_at TEXT, resolution TEXT);
CREATE TABLE IF NOT EXISTS simulation (
  id TEXT PRIMARY KEY, website_id TEXT, label TEXT, target TEXT, status TEXT, summary TEXT DEFAULT '{}',
  created_at TEXT, finished_at TEXT);
CREATE TABLE IF NOT EXISTS simulation_run (
  id TEXT PRIMARY KEY, simulation_id TEXT, query TEXT, type TEXT, result TEXT DEFAULT '{}', settled INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS event (
  website_id TEXT, remote_id INTEGER, ts TEXT, event TEXT, payload TEXT, PRIMARY KEY (website_id, remote_id));
CREATE TABLE IF NOT EXISTS connection (
  website_id TEXT, toolkit TEXT, status TEXT, detail TEXT DEFAULT '{}', created_at TEXT, PRIMARY KEY (website_id, toolkit));
"""
JSON_COLUMNS = {"pages", "payload", "summary", "result", "detail", "record"}


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(6)}"


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    out = dict(row)
    for key in JSON_COLUMNS & out.keys():
        if isinstance(out[key], str):
            out[key] = json.loads(out[key])
    return out


def query(sql: str, *args) -> list[dict]:
    with connect() as conn:
        return [_row(r) for r in conn.execute(sql, args).fetchall()]


def one(sql: str, *args) -> dict | None:
    with connect() as conn:
        return _row(conn.execute(sql, args).fetchone())


def run(sql: str, *args) -> None:
    with connect() as conn:
        conn.execute(sql, args)


def insert(table: str, **fields) -> dict:
    fields = {k: json.dumps(v, default=str) if k in JSON_COLUMNS and not isinstance(v, str) else v for k, v in fields.items()}
    columns = ", ".join(fields)
    marks = ", ".join("?" for _ in fields)
    run(f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({marks})", *fields.values())
    return fields


def update(table: str, key: str, value, **fields) -> None:
    fields = {k: json.dumps(v, default=str) if k in JSON_COLUMNS and not isinstance(v, str) else v for k, v in fields.items()}
    sets = ", ".join(f"{k} = ?" for k in fields)
    run(f"UPDATE {table} SET {sets} WHERE {key} = ?", *fields.values(), value)


# ---------------------------------------------------------------- shared helpers


def website(website_id: str) -> dict | None:
    return one("SELECT * FROM website WHERE id = ?", website_id)


def latest_record(website_id: str) -> dict | None:
    return one("SELECT * FROM record_version WHERE website_id = ? ORDER BY version DESC LIMIT 1", website_id)


def save_record(website_id: str, record: dict, reason: str) -> int:
    current = latest_record(website_id)
    version = (current["version"] + 1) if current else 1
    insert("record_version", website_id=website_id, version=version, record=record, reason=reason, created_at=now())
    return version


def add_inbox(website_id: str, kind: str, title: str, body: str = "", payload: dict | None = None, source: str = "agent") -> str:
    item_id = new_id("inb")
    insert(
        "inbox_item",
        id=item_id,
        website_id=website_id,
        kind=kind,
        status="open",
        title=title,
        body=body,
        payload=payload or {},
        source=source,
        created_at=now(),
    )
    return item_id


def resolve_inbox(item_id: str, resolution: str, status: str = "done") -> None:
    update("inbox_item", "id", item_id, status=status, resolution=resolution, resolved_at=now())
