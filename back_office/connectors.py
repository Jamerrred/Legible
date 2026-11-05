"""Owner accounts through Composio. The product runs without it: with no key, these return a clear error."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta

TOOLKITS = {
    "googlecalendar": "Google Calendar",
    "googlesheets": "Google Sheets",
}


def configured() -> bool:
    return bool(os.environ.get("COMPOSIO_API_KEY"))


class NotConfigured(RuntimeError):
    pass


def _session(website_id: str, callback_url: str | None = None):
    key = os.environ.get("COMPOSIO_API_KEY")
    if not key:
        raise NotConfigured("COMPOSIO_API_KEY isn't set, so accounts can't be connected yet.")
    from composio import Composio

    client = Composio(api_key=key)
    options = {"manage_connections": {"callback_url": callback_url}} if callback_url else {}
    return client.create(user_id=website_id, **options)


def connect_link(website_id: str, toolkit: str, callback_url: str | None = None) -> str:
    return _session(website_id, callback_url).authorize(toolkit).redirect_url


def read_account(website_id: str, toolkit: str, spreadsheet_id: str | None = None) -> str:
    """Read what's useful from a connected account, as text for the model."""
    session = _session(website_id)
    if toolkit == "googlecalendar":
        start = datetime.now(UTC)
        result = session.execute(
            "GOOGLECALENDAR_EVENTS_LIST",
            arguments={
                "calendarId": "primary",
                "timeMin": start.isoformat(),
                "timeMax": (start + timedelta(days=30)).isoformat(),
                "singleEvents": True,
                "maxResults": 100,
            },
        )
    elif toolkit == "googlesheets":
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id is needed to read a sheet")
        result = session.execute("GOOGLESHEETS_BATCH_GET", arguments={"spreadsheet_id": spreadsheet_id, "ranges": ["A1:Z200"]})
    else:
        raise ValueError(f"unknown toolkit {toolkit}")
    return json.dumps(result, default=str, ensure_ascii=False)
