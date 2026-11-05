"""The app has no login yet, so other websites must not be able to drive it through the owner's browser."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from legible import api, store

WRITE = "/websites/none/check-link"  # 404 means the request got through to the app, and spends nothing.


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.db")
    return TestClient(api.app, base_url="http://127.0.0.1:8200")


@pytest.mark.parametrize("site", ["cross-site", "same-site"])
def test_other_websites_cant_send_changes(client, site):
    assert client.post(WRITE, headers={"sec-fetch-site": site}).status_code == 403


def test_a_foreign_origin_is_refused_without_browser_metadata(client):
    assert client.post(WRITE, headers={"origin": "https://evil.example"}).status_code == 403


def test_a_sandboxed_page_is_refused(client):
    assert client.post(WRITE, headers={"origin": "null"}).status_code == 403


def test_other_websites_cant_read_responses(client):
    response = client.get("/health", headers={"origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers


def test_an_unknown_hostname_is_refused(client):
    assert client.get("/health", headers={"host": "evil.example"}).status_code == 400


@pytest.mark.parametrize(
    "headers",
    [
        {"sec-fetch-site": "same-origin", "origin": "http://127.0.0.1:8200"},
        {"origin": "http://127.0.0.1:8200"},
        {},
    ],
    ids=["owner console", "older browser", "script"],
)
def test_the_owner_and_scripts_still_get_through(client, headers):
    assert client.post(WRITE, headers=headers).status_code == 404


def test_following_a_link_from_another_site_still_opens_the_app(client):
    assert client.get("/", headers={"sec-fetch-site": "cross-site"}).status_code == 200


def test_extra_hostnames_can_be_allowed(monkeypatch):
    monkeypatch.setenv("LEGIBLE_ALLOWED_HOSTS", "legible.internal, 10.0.0.5")
    assert api.allowed_hosts() == ["127.0.0.1", "localhost", "legible.internal", "10.0.0.5"]
