"""The agent-readable resource, and the rule that the agent stays general."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from demo_resource.app import app
from legible_core.business import load_facts, quote

ROOT = Path(__file__).resolve().parent.parent
FACTS = load_facts()["facts"]


@pytest.fixture
def client():
    return TestClient(app)


def test_every_fact_is_on_the_main_page(client):
    page = client.get("/").text
    missing = [fact["id"] for fact in FACTS if f'id="fact-{fact["id"]}"' not in page]
    assert not missing


def test_main_page_needs_no_javascript_and_gives_no_orders(client):
    page = client.get("/").text
    assert "<script" not in page
    assert not re.search(r"\b(ai agents?|agents) (should|must)\b", page, re.IGNORECASE)


def test_markdown_version_is_available(client):
    assert "text/markdown" in client.get("/", headers={"Accept": "text/markdown"}).headers["content-type"]
    assert "text/markdown" in client.get("/index.md").headers["content-type"]


def test_quote_link_matches_the_calculator_and_asks_for_no_contact_details(client):
    job = "/quote?service=full&vehicle=Subaru+Outback&zip=94704&format=json"
    body = client.get(job).text
    expected = quote(service="full", vehicle="Subaru Outback", zip_code="94704")["total"]
    assert str(expected) in body
    assert "email" not in body.lower()


def test_ask_only_logs_the_question_and_returns_a_status_link(client, isolated_logs):
    response = client.post("/ask", data={"question": "Do you clean roof racks?"})
    assert response.status_code == 200
    assert re.search(r"/r/[\w-]+", response.text)
    log = (isolated_logs / "resource.jsonl").read_text()
    assert '"event": "question"' in log
    assert "Do you clean roof racks?" in log


def test_errand_knows_nothing_about_this_project():
    code = "\n".join(path.read_text() for path in (ROOT / "errand").glob("*.py"))
    for word in ("sunrise", "legible", "agents.", "detailing"):
        assert word not in code.lower(), word
