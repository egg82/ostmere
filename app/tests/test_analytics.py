"""Umami: off unless both values are set, and nothing shipped names a tracker."""
import pytest
from fastapi.testclient import TestClient

from ashfall_app.main import create_app

SCRIPT, SITE = "https://stats.yggdrasil.pub/site.js", "00000000-0000-0000-0000-000000000000"
KEYS = ("ASHFALL_UMAMI_SCRIPT_URL", "ASHFALL_UMAMI_WEBSITE_ID")


def config(monkeypatch: pytest.MonkeyPatch, **env: str) -> dict[str, object]:
    for k in (*KEYS, "VAPID_PUBLIC_KEY"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("BUILD_VERSION", "abc123")
    return TestClient(create_app()).get("/page-config.json").json()


def test_off_without_config_but_the_version_is_served(monkeypatch: pytest.MonkeyPatch):
    assert config(monkeypatch) == {"version": "abc123", "umami": None, "reminders": None}


@pytest.mark.parametrize("env", [{KEYS[0]: SCRIPT}, {KEYS[1]: SITE}])
def test_half_a_config_is_off(monkeypatch: pytest.MonkeyPatch, env: dict[str, str]):
    assert config(monkeypatch, **env)["umami"] is None


def test_both_values_turn_it_on(monkeypatch: pytest.MonkeyPatch):
    assert config(monkeypatch, **dict(zip(KEYS, (SCRIPT, SITE))))["umami"] == {"script_url": SCRIPT, "website_id": SITE}


def test_the_config_route_is_not_in_the_api_contract():
    paths = create_app().openapi()["paths"]
    assert "/api/saves/{save_id}/decisions" in paths   # control: the spec lists routes
    assert "/page-config.json" not in paths and "/api/client-errors" not in paths


def test_the_page_names_no_tracker():
    page = TestClient(create_app()).get("/").text
    assert "<title>The Breaking of Ostmere</title>" in page   # control: the page was served
    assert "stats.yggdrasil.pub" not in page and SITE not in page
