"""Structured JSONL logs shared by the site, the resource and the control page.

The back office agent's owner inbox reads these later, so every event is one
JSON object per line with a stable shape: ts, stream, event, then the fields.
Events in use: page_hit, quote, dead_end, request, question, lead_form.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

# Python Workers can only write to /tmp, and only until the Worker restarts.
LOG_DIR = Path(os.environ.get("MF_LOG_DIR") or Path(__file__).resolve().parent.parent / "logs")


def log_event(stream: str, event: str, **fields) -> dict:
    """Append one event to logs/<stream>.jsonl and return it."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {"ts": datetime.now(UTC).isoformat(), "stream": stream, "event": event, **fields}
    line = json.dumps(record, default=str) + "\n"
    if os.environ.get("MF_LOG_STDOUT"):
        print(line, end="", flush=True)
    fd = os.open(LOG_DIR / f"{stream}.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode())
    finally:
        os.close(fd)
    return record


def read_events(stream: str, log_dir: Path | None = None) -> list[dict]:
    """Read one stream from logs/, or from a benchmark's saved copy if given."""
    path = (log_dir or LOG_DIR) / f"{stream}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
