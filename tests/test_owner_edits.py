"""Owner edits: a price change must reach one size only, and the demo must read plain words."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legible import demo
from legible.record import apply_ops

DRAFT = Path(__file__).resolve().parent.parent / "legible" / "demo_draft.json"
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


@pytest.mark.parametrize(
    "text",
    [
        "Change the class A price of the Skiff from 69 to 70",
        "change the class a price of the skip from 69 to 70",
        "The Skiff class A is going to $70",
        "Skiff from $69 to $70",
        "Class A of the Skiff is now $70",
    ],
)
def test_demo_reads_a_plain_price_change(record, text):
    plan = demo.plan_instruction(record, text, TODAY)
    assert plan["summary"] == "The Skiff, Class A, goes from $69 to $70"
    assert [v["price"] for v in _skiff(apply_ops(record, plan["ops"]))["variants"]] == [70, 79, 99, 139]


def test_demo_asks_which_size_when_it_cant_tell(record):
    plan = demo.plan_instruction(record, "Change the Skiff to 70", TODAY)
    assert "Class A" in plan["clarifying_question"]
    assert not plan.get("ops")


def test_demo_asks_when_a_price_change_names_nothing_it_knows(record):
    plan = demo.plan_instruction(record, "Change the price of the wax to 70", TODAY)
    assert plan["clarifying_question"]


def test_demo_changes_a_fee(record):
    plan = demo.plan_instruction(record, "Raise the generator fee to $35", TODAY)
    fee = next(f for f in apply_ops(record, plan["ops"])["fees"] if f["id"] == "generator-fee")
    assert fee["amount"] == 35


def test_demo_still_adds_a_plain_statement(record):
    plan = demo.plan_instruction(record, "We now take Apple Pay", TODAY)
    assert "Apple Pay" in plan["ops"][0]["item"]["statement"]


def test_new_database_tracks_whether_the_link_is_on_the_site(tmp_path, monkeypatch):
    from legible import store

    monkeypatch.setattr(store, "DB_PATH", tmp_path / "fresh.db")
    store.insert("website", id="web_1", slug="s", url="https://example.com", pages=[], created_at=store.now())
    assert store.website("web_1")["link_placed"] == 0
    store.update("website", "id", "web_1", link_placed=1)
    assert store.website("web_1")["link_placed"] == 1
