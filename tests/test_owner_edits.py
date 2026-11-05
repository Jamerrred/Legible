"""Owner edits: a price change must reach one size only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legible.record import apply_ops

DRAFT = Path(__file__).resolve().parent / "fixtures" / "sunrise_draft.json"
TODAY = "2026-11-05"


@pytest.fixture
def record() -> dict:
    return json.loads(DRAFT.read_text())


def _skiff(record: dict) -> dict:
    return next(o for o in record["offerings"] if o["id"] == "the-skiff")


def test_changing_one_size_keeps_the_others_and_moves_the_from_price(record):
    ops = [{"op": "upsert", "collection": "offerings", "item": {"id": "the-skiff", "variants": [{"id": "class-a", "price": 70}]}}]
    skiff = _skiff(apply_ops(record, ops))
    assert [v["price"] for v in skiff["variants"]] == [70, 79, 99, 139]
    assert skiff["variants"][0]["label"] == "Class A"
    assert skiff["price"] == 70
    assert skiff["price_high"] == 139


def test_new_database_tracks_whether_the_link_is_on_the_site(tmp_path, monkeypatch):
    from legible import store

    monkeypatch.setattr(store, "DB_PATH", tmp_path / "fresh.db")
    store.insert("website", id="web_1", slug="s", url="https://example.com", pages=[], created_at=store.now())
    assert store.website("web_1")["link_placed"] == 0
    store.update("website", "id", "web_1", link_placed=1)
    assert store.website("web_1")["link_placed"] == 1
