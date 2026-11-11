"""A save id past what the database stores is a request that does not fit the contract (api/CONTRACT.txt, "Save ids"):
422 invalid_decision on every route that names a save, and on POST /api/feedback, not a 500. An id in range that is
not this account's stays 404."""
from typing import Any

import pytest

from tests.game_client import GameClient

PAST_BIGINT = 2**63
DECISION: dict[str, Any] = {"decision": {"kind": "set_orders", "orders": []}, "after": 0}
ROUTES: list[tuple[str, str, dict[str, Any] | None]] = [
    ("open", "/api/saves/{}/open", None),
    ("advance", "/api/saves/{}/advance", None),
    ("forecast", "/api/saves/{}/forecast", None),
    ("decisions", "/api/saves/{}/decisions", DECISION),
    ("dry-run", "/api/saves/{}/dry-run", {"decisions": []}),
    ("delete", "/api/saves/{}/delete", None),
    ("restore", "/api/saves/{}/restore", None),
]


@pytest.mark.parametrize("name,path,body", ROUTES, ids=[r[0] for r in ROUTES])
def test_a_save_id_past_bigint_is_422(game: GameClient, name: str, path: str, body: dict[str, Any] | None):
    game.begin()
    r = game.client.post(path.format(PAST_BIGINT), json=body)
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision", f"{name}: {r.status_code} {r.text[:200]}"


def test_feedback_with_a_save_id_past_bigint_is_422(game: GameClient):
    r = game.client.post("/api/feedback", json={"text": "hello", "save_id": PAST_BIGINT})
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision", f"{r.status_code} {r.text[:200]}"


@pytest.mark.parametrize("name,path,body", ROUTES, ids=[r[0] for r in ROUTES])
def test_an_in_range_save_that_is_not_this_accounts_is_404(game: GameClient, name: str, path: str,
                                                           body: dict[str, Any] | None):
    other = game.begin()["save"]["save_id"]
    r = game.stranger().post("/api/saves", json=None)
    assert r.status_code == 200
    mine = r.json()["save"]["save_id"]
    assert mine != other
    r = game.client.post(path.format(mine), json=body)
    assert r.status_code == 404 and r.json()["code"] == "not_found", f"{name}: {r.status_code} {r.text[:200]}"
