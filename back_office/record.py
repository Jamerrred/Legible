"""The business record, or fact sheet, and the only ways it can change.

The agent changes the record through ops and never touches a page. Prices live in structured
fields, so one edit reaches the page, the markdown and /quote together.
"""

from __future__ import annotations

import copy
import re
from datetime import datetime
from zoneinfo import ZoneInfo

COLLECTIONS = ("offerings", "addons", "fees", "zones", "facts", "not_offered")
CATEGORIES = (
    "vocabulary",
    "dependencies",
    "conditions",
    "eligibility",
    "prerequisites",
    "service_area",
    "availability",
    "staff",
    "policies",
    "timing",
    "credentials",
    "next_step",
    "closure",
    "other",
)

RECORD_SHAPE = """{
  "business": {"name": "", "summary": "one or two plain sentences", "website": "", "phone": "", "email": "", "address": "",
               "timezone": "IANA name, or empty", "closed_weekdays": ["Sunday"]},
  "currency": "USD",
  "tax": {"rate": 0.08625, "applies_to": "what it applies to"},   // null if not stated
  "offerings": [{"id": "kebab-id", "name": "", "description": "", "aliases": ["customer words"], "price_type": "fixed|from|range|quote_only",
                 "price": 180, "price_high": null, "variants": [{"id": "small", "label": "small cars", "price": 120}],
                 "duration": "about 3 hours", "notes": "", "source_url": ""}],
  "addons": [{"id": "", "name": "", "aliases": [], "price_type": "fixed", "price": 55, "variants": [], "requires": "", "notes": "", "source_url": ""}],
  "fees": [{"id": "", "label": "", "amount": 25, "percent": null, "applies_when": "plain condition", "weekdays": ["Saturday"],
            "aliases": [], "taxable": true, "source_url": ""}],
  "zones": [{"id": "", "label": "", "zips": ["94110"], "fee": 0, "source_url": ""}],
  "facts": [{"id": "", "category": "one of the categories", "statement": "one self-contained sentence that names the business",
             "valid_from": null, "valid_to": null, "source_url": ""}],
  "not_offered": [{"id": "", "name": "", "terms": ["words a customer might use"], "statement": "one self-contained sentence", "source_url": ""}]
}"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:60] or "item"


def today_for(record: dict) -> str:
    tz = (record.get("business") or {}).get("timezone") or "UTC"
    try:
        return datetime.now(ZoneInfo(tz)).date().isoformat()
    except Exception:
        return datetime.now(ZoneInfo("UTC")).date().isoformat()


def empty_record(name: str = "", website: str = "") -> dict:
    return {
        "business": {"name": name, "website": website},
        "currency": "USD",
        "tax": None,
        **{c: [] for c in COLLECTIONS},
    }


def normalise(record: dict) -> dict:
    """Fill gaps in model output so later code can rely on the shape."""
    out = empty_record()
    out.update({k: v for k, v in record.items() if v is not None or k == "tax"})
    out["business"] = record.get("business") or {}
    for collection in COLLECTIONS:
        items, seen = [], set()
        for item in record.get(collection) or []:
            if not isinstance(item, dict):
                continue
            base = item.get("id") or item.get("name") or item.get("label") or item.get("statement") or collection
            item_id = slugify(base)
            while item_id in seen:
                item_id += "-2"
            seen.add(item_id)
            items.append({**item, "id": item_id})
        out[collection] = items
    return out


def stamp_all(record: dict, *, status: str, source: str, today: str) -> dict:
    out = copy.deepcopy(record)
    for collection in COLLECTIONS:
        for item in out[collection]:
            item["status"] = status
            item["source"] = source
            if status == "confirmed":
                item["confirmed_on"] = today
    return out


def apply_ops(record: dict, ops: list[dict], *, source: str = "owner", status: str = "confirmed") -> dict:
    """Return a new record with ops applied. Ops: upsert, delete and set."""
    out = copy.deepcopy(record)
    today = today_for(out)
    for op in ops:
        kind = op.get("op")
        if kind == "set":
            root, _, leaf = str(op.get("path", "")).partition(".")
            if root == "business" and leaf:
                out.setdefault("business", {})[leaf] = op.get("value")
            elif root == "tax":
                if leaf:
                    out["tax"] = {**(out.get("tax") or {}), leaf: op.get("value")}
                else:
                    out["tax"] = op.get("value")
            elif root == "currency":
                out["currency"] = op.get("value")
            continue
        collection = op.get("collection")
        if collection not in COLLECTIONS:
            continue
        if kind == "delete":
            out[collection] = [i for i in out[collection] if i.get("id") != op.get("id")]
        elif kind == "upsert" and isinstance(op.get("item"), dict):
            item = op["item"]
            item_id = item.get("id") or slugify(item.get("name") or item.get("label") or item.get("statement") or collection)
            stamp = {"status": status, "source": source}
            if status == "confirmed":
                stamp["confirmed_on"] = today
            for index, existing in enumerate(out[collection]):
                if existing.get("id") == item_id:
                    out[collection][index] = {**existing, **item, "id": item_id, **stamp}
                    break
            else:
                out[collection].append({**item, "id": item_id, **stamp})
    return out


def confirm_drafts(record: dict, exclude_ids: list[str] | None = None) -> dict:
    out = copy.deepcopy(record)
    today = today_for(out)
    exclude = set(exclude_ids or [])
    for collection in COLLECTIONS:
        kept = []
        for item in out[collection]:
            if item.get("status") == "draft":
                if item.get("id") in exclude:
                    continue
                item["status"] = "confirmed"
                item["confirmed_on"] = today
            kept.append(item)
        out[collection] = kept
    return out


def public_view(record: dict, unknowns: list[str] | None = None) -> dict:
    """What the Worker serves: confirmed items only, so a draft can never leave this process."""
    out = copy.deepcopy(record)
    for collection in COLLECTIONS:
        out[collection] = [i for i in out.get(collection, []) if i.get("status", "confirmed") == "confirmed"]
    out["unknowns"] = [{"statement": u} for u in (unknowns or [])]
    out["updated_at"] = today_for(out)
    return out


def counts(record: dict) -> dict:
    total = {"confirmed": 0, "draft": 0}
    for collection in COLLECTIONS:
        for item in record.get(collection, []):
            total["draft" if item.get("status") == "draft" else "confirmed"] += 1
    return total
