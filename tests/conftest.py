"""Shared test setup."""

from __future__ import annotations

import pytest

from mf_core import logbook


@pytest.fixture(autouse=True)
def isolated_logs(tmp_path, monkeypatch):
    """Keep test traffic out of the real logs/ folder."""
    monkeypatch.setattr(logbook, "LOG_DIR", tmp_path)
    return tmp_path
