"""Structured JSONL logs shared by the site, the resource and the control page.

The back office agent's owner inbox reads these later, so every event is one
JSON object per line with a stable shape: ts, stream, event, then the fields.
Events in use: page_hit, quote, dead_end, request, question, lead_form.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def log_event(stream: str, event: str, **fields) -> dict:
    """Append one event to logs/<stream>.jsonl and return it."""
    LOG_DIR.mkdir(exist_ok=True)
    record = {"ts": datetime.now(timezone.utc).isoformat(), "stream": stream, "event": event, **fields}
    line = json.dumps(record, default=str) + "\n"
    fd = os.open(LOG_DIR / f"{stream}.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode())
    finally:
        os.close(fd)
    return record


def read_events(stream: str) -> list[dict]:
    path = LOG_DIR / f"{stream}.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
