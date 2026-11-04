"""Small helpers that format dates, money, word lists, links and offering names."""

from __future__ import annotations

import html
from datetime import date, datetime
from urllib.parse import urlencode

from demo_resource.config import SERVICES, SIZES, TZ


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def long_date(iso: str) -> str:
    day = date.fromisoformat(iso[:10])
    return f"{day.day} {day:%B %Y}"


def clock(hhmm: str) -> str:
    hour, minute = hhmm.split(":")
    hour = int(hour)
    suffix = "am" if hour < 12 else "pm"
    return f"{hour % 12 or 12}:{minute} {suffix}"


def whole(amount) -> str:
    return f"${amount:,.0f}"


def usd(amount) -> str:
    return f"${amount:,.2f}"


def money(value) -> str:
    if value is None:
        return "not worked out yet"
    if isinstance(value, dict):
        return f"{usd(value['low'])} to {usd(value['high'])}"
    return usd(value)


def words(items) -> str:
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def local_now() -> datetime:
    return datetime.now(TZ)


def stamp(moment: datetime) -> str:
    return f"{moment.day} {moment:%B %Y} at {clock(moment.strftime('%H:%M'))} Pacific time"


def link(path: str, **params) -> str:
    """A site path with a query string, keeping commas readable."""
    clean = {key: value for key, value in params.items() if value not in (None, "", [], ())}
    return f"{path}?{urlencode(clean, safe=',-')}" if clean else path


def service_name(service_id: str) -> str:
    service = SERVICES[service_id]
    return f"{service['plain_name']} ({service['marketing_name']})"


def addon_price_cells(addon: dict) -> list[str]:
    if "prices" in addon:
        return [whole(addon["prices"][size]) for size in SIZES]
    if "flat" in addon:
        return [f"{whole(addon['flat'])} per pair"] * len(SIZES)
    return [f"{whole(addon['range']['low'])} to {whole(addon['range']['high'])}"] * len(SIZES)
