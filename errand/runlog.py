"""One JSONL event file per run."""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RunLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("a", encoding="utf-8")
        self._lock = threading.Lock()
        self._t0 = time.monotonic()

    def event(self, event: str, **fields: Any) -> None:
        record = {
            "event": event,
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "t": round(time.monotonic() - self._t0, 3),
            **fields,
        }
        line = json.dumps(record, ensure_ascii=False, default=str)
        with self._lock:
            self._file.write(line + "\n")
            self._file.flush()

    def count(self, event: str) -> int:
        with self.path.open(encoding="utf-8") as f:
            return sum(1 for line in f if json.loads(line)["event"] == event)

    def close(self) -> None:
        with self._lock:
            self._file.close()
