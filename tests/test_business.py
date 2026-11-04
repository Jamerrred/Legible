"""The facts file and the rules worked out from it."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from mf_core.business import load_facts, quote, slots

FACTS = load_facts()


def test_every_fact_has_a_confirmation_date_and_a_placement():
    for fact in FACTS["facts"]:
        assert fact["confirmed_on"], fact["id"]
        assert fact["before_site"]["placement"] in {"plain", "hidden", "missing"}, fact["id"]


def test_fact_ids_are_unique():
    ids = [fact["id"] for fact in FACTS["facts"]]
    assert len(ids) == len(set(ids))


def test_side_chat_placeholders_did_not_carry_over():
    text = str(FACTS).lower()
    assert "brightside" not in text
    assert "50-foot" not in text
    assert "water and power fee" not in text


@pytest.mark.parametrize(
    ("job", "total"),
    [
        ({"service": "full", "size": "midsize", "zip_code": "94117"}, 270.48),
        ({"service": "full", "size": "midsize", "zip_code": "94704", "addons": ("pet-hair",), "when": "2026-11-10 afternoon"}, 395.22),
        ({"service": "full", "size": "midsize", "zip_code": "94704", "addons": ("pet-hair",), "when": "2026-11-07 morning"}, 422.38),
    ],
)
def test_quote_totals(job, total):
    now = datetime(2026, 11, 4, 12, tzinfo=ZoneInfo(FACTS["business"]["timezone"]))
    result = quote(now=now, **job)
    assert result["status"] == "ok"
    assert result["total"] == pytest.approx(total)


def test_quote_rejects_a_zip_outside_the_service_area():
    assert quote(service="full", size="midsize", zip_code="94901")["status"] == "out_of_area"


def test_slots_roll_forward_and_are_deterministic():
    now = datetime(2026, 11, 4, 12, tzinfo=ZoneInfo(FACTS["business"]["timezone"]))
    first = slots(now=now)
    assert first == slots(now=now)
    assert all(slot["date"] >= "2026-11-04" for slot in first)
    assert any(slot["open"] for slot in first)
