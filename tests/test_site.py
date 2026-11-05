"""The mock website. "After" may differ from "before" only by the link line."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from business_core.business import load_facts
from fastapi.testclient import TestClient
from sample_site.app import create_app
from scripts.check_booking import LEAD, check

ROOT = Path(__file__).resolve().parent.parent
LINK_LINE = re.compile(r'\s*<p class="site-note">Prices, availability and booking requests.*?</p>', re.DOTALL)


@pytest.fixture
def before():
    return TestClient(create_app("before"))


@pytest.fixture
def after():
    return TestClient(create_app("after"))


@pytest.mark.parametrize("variant", ["before", "after"])
def test_booking_flow_works_end_to_end(variant):
    assert check(TestClient(create_app(variant))) is None


@pytest.mark.parametrize("path", ["/", "/faq", "/book"])
def test_after_differs_from_before_only_by_the_link_line(before, after, path):
    with_link = after.get(path).text
    assert "http://agents.sunrise.localhost:8103" in with_link
    assert LINK_LINE.sub("", with_link).split() == before.get(path).text.split()


def test_link_line_uses_the_configured_address(monkeypatch):
    monkeypatch.setenv("LEGIBLE_RESOURCE_BASE_URL", "https://example.test")
    page = TestClient(create_app("after")).get("/").text
    assert '<a href="https://example.test">https://example.test</a>' in page
    assert "localhost" not in page


def test_booking_steps_differ_only_by_the_link_line(before, after):
    first, second = before.post("/book", data=LEAD).text, after.post("/book", data=LEAD).text
    assert LINK_LINE.sub("", second).split() == first.split()


@pytest.mark.parametrize("path", ["/", "/faq", "/book"])
def test_before_has_no_trace_of_the_resource_or_the_test(before, path):
    page = before.get(path).text.lower()
    for word in ("agents.sunrise", "legible", "data-hole", "benchmark"):
        assert word not in page


def test_site_has_only_three_pages(before):
    for path in ("/pricing", "/services", "/about", "/terms", "/fleet", "/gift-cards", "/contact"):
        assert before.get(path).status_code == 404
    assert before.get("/sitemap.xml").text.count("<loc>") == 3


def test_every_hidden_fact_is_in_the_holes_list():
    holes = json.loads((ROOT / "experiment" / "sample_site" / "holes.json").read_text())
    listed = {fact_id for hole in holes for fact_id in hole["fact_ids"]}
    hidden = {fact["id"] for fact in load_facts()["facts"] if fact["before_site"]["placement"] == "hidden"}
    assert hidden <= listed
    assert all(hole["catalogue_ids"] for hole in holes)
    assert {hole["page"] for hole in holes} <= {"/", "/faq", "/book"}
