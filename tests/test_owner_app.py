"""The owner app's promises: nothing goes public before the first confirmation, and one clear next step."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from legible import api, edge, store, work

DRAFT = {
    "business": {"name": "Test Bakery", "timezone": "America/Los_Angeles"},
    "currency": "USD",
    "tax": None,
    "offerings": [{"id": "loaf", "name": "Loaf", "price": 8, "status": "draft", "source": "crawl"}],
    "addons": [],
    "fees": [],
    "zones": [],
    "facts": [],
    "not_offered": [],
}


@pytest.fixture
def app_state(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.db")
    published = []

    async def put_business(slug, record, noindex=True):
        published.append(slug)
        return {"ok": True}

    async def no_events(slug, after=0):
        return []

    monkeypatch.setattr(edge, "put_business", put_business)
    monkeypatch.setattr(edge, "get_events", no_events)
    monkeypatch.setattr(edge, "get_items", no_events)

    async def answer_to_ops(record, title, text, today):
        return {
            "summary": "Added",
            "ops": [{"op": "upsert", "collection": "facts", "item": {"id": "hours", "category": "other", "statement": text}}],
        }

    monkeypatch.setattr(api.brain, "answer_to_ops", answer_to_ops)
    website_id = store.new_id("web")
    store.insert(
        "website",
        id=website_id,
        slug="bakery",
        name="Test Bakery",
        url="https://bakery.example",
        stage="ready",
        stage_note="",
        pages=[],
        created_at=store.now(),
    )
    store.save_record(website_id, DRAFT, "Read from the website")
    review = store.add_inbox(website_id, "review", "Confirm 1 fact", "", {"count": 1})
    question = store.add_inbox(
        website_id, "question", "What are your hours?", "", {"unknown_statement": "Hours aren't stated."}, "simulation"
    )
    return {"client": TestClient(api.app), "id": website_id, "review": review, "question": question, "published": published}


def test_answering_a_question_stays_private_until_the_first_confirmation(app_state):
    client, website_id = app_state["client"], app_state["id"]
    assert client.post(f"/inbox/{app_state['question']}/answer", json={"text": "9 to 5"}).status_code == 200
    assert app_state["published"] == []
    assert client.get(f"/websites/{website_id}").json()["live"] is False

    assert client.post(f"/inbox/{app_state['review']}/confirm").status_code == 200
    assert app_state["published"] == ["bakery"]
    assert client.get(f"/websites/{website_id}").json()["live"] is True


def test_the_next_step_follows_the_owners_path(app_state):
    client, website_id = app_state["client"], app_state["id"]
    step = lambda: client.get(f"/websites/{website_id}").json()["next"]  # noqa: E731
    assert step()["screen"] == "simulations"
    client.post(f"/inbox/{app_state['question']}/answer", json={"text": "9 to 5"})
    assert step()["screen"] == "resource"
    client.post(f"/inbox/{app_state['review']}/confirm")
    assert step() is None

    store.insert(
        "simulation",
        id="sim_1",
        website_id=website_id,
        label="First",
        target="storefront",
        status="done",
        summary={"answered": 1, "queries": 4},
        created_at=store.now(),
    )
    assert step()["label"] == "Run the check again"
    store.insert(
        "simulation",
        id="sim_2",
        website_id=website_id,
        label="Again",
        target="resource",
        status="done",
        summary={"answered": 4, "queries": 4},
        created_at=store.now(),
    )
    assert step() is None

    checks = client.get(f"/websites/{website_id}").json()["checks"]
    assert (checks["first"]["answered"], checks["latest"]["answered"], checks["count"]) == (1, 4, 2)


def test_a_finished_check_keeps_each_customers_path(app_state, tmp_path, monkeypatch):
    monkeypatch.setattr(work, "RUNS", tmp_path)
    folder = tmp_path / "sim_1" / "customer-0"
    folder.mkdir(parents=True)
    (folder / "run-1.jsonl").write_text(
        '{"event": "run_start", "task": "Can I book a loaf? (The business\'s information page is https://x.example)"}\n'
        '{"event": "tool_call", "tool": "read_page", "args": {"url": "https://x.example/b/bakery/quote?service=loaf"}}\n'
        '{"event": "tool_call", "tool": "browse_task", "args": {"objective": "Find the price"}}\n'
        '{"event": "run_end", "report": {"outcome": "answered"}}\n'
    )
    client = app_state["client"]
    store.insert(
        "simulation",
        id="sim_1",
        website_id=app_state["id"],
        label="First",
        target="resource",
        status="done",
        summary={"answered": 1, "queries": 1},
        created_at=store.now(),
    )
    store.insert(
        "simulation_run",
        id="run_1",
        simulation_id="sim_1",
        query="Can I book a loaf?",
        type="",
        result={"answer": "Yes"},
        settled=1,
        created_at=store.now(),
    )
    path = client.get("/simulations/sim_1").json()["runs"][0]["path"]
    assert [step["kind"] for step in path] == ["quote", "browse"]


def test_the_quote_console_needs_a_live_page(app_state):
    assert app_state["client"].get(f"/websites/{app_state['id']}/resource/quote?service=loaf").status_code == 409
