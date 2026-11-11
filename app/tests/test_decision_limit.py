"""A save takes a bounded number of decisions a minute and an hour (api/CONTRACT.txt, "Request limits"): past either,
429 rate_limited with Retry-After, and nothing written. The limits are shrunk here; their real size is
accounts/limits.py's. A refused decision writes no row and counts nothing, and a decision that is stale or invalid
counts nothing either."""
from typing import Any

import pytest

from ashfall_app.accounts import limits
from ashfall_app.db import saves as rows
from tests.game_client import GameClient

SET_NO_ORDERS: dict[str, Any] = {"kind": "set_orders", "orders": []}
MINUTE_S, HOUR_S = 60, 3600


@pytest.fixture
def small(monkeypatch: pytest.MonkeyPatch) -> tuple[int, int]:
    """(per minute, per hour) for the test."""
    monkeypatch.setattr(limits, "DECISIONS_PER_MINUTE", 3)
    monkeypatch.setattr(limits, "DECISIONS_PER_HOUR", 5)
    return 3, 5


def count(game: GameClient, save_id: int) -> int:
    with game.app.state.db.engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None
    return row.decisions


def test_a_save_takes_so_many_decisions_a_minute_and_an_hour(game: GameClient, small: tuple[int, int]):
    per_minute, per_hour = small
    save_id = game.begin()["save"]["save_id"]
    for n in range(per_minute):
        assert game.decide(save_id, SET_NO_ORDERS, after=n).status_code == 200
    r = game.decide(save_id, SET_NO_ORDERS, after=per_minute)
    assert r.status_code == 429 and r.json()["code"] == "rate_limited", r.text
    assert 1 <= int(r.headers["Retry-After"]) <= MINUTE_S
    assert count(game, save_id) == per_minute, "the refused decision wrote nothing"
    game.clock.tick(MINUTE_S + 1)
    for n in range(per_minute, per_hour):
        assert game.decide(save_id, SET_NO_ORDERS, after=n).status_code == 200
    game.clock.tick(MINUTE_S + 1)
    r = game.decide(save_id, SET_NO_ORDERS, after=per_hour)
    assert r.status_code == 429 and r.json()["code"] == "rate_limited", r.text
    assert MINUTE_S < int(r.headers["Retry-After"]) <= HOUR_S
    game.clock.tick(HOUR_S)
    assert game.decide(save_id, SET_NO_ORDERS, after=per_hour).status_code == 200


def test_a_stale_decision_counts_nothing(game: GameClient, small: tuple[int, int]):
    per_minute, _ = small
    save_id = game.begin()["save"]["save_id"]
    for _ in range(per_minute + 2):
        assert game.decide(save_id, SET_NO_ORDERS, after=99).status_code == 409
    for n in range(per_minute):
        assert game.decide(save_id, SET_NO_ORDERS, after=n).status_code == 200
    assert game.decide(save_id, SET_NO_ORDERS, after=per_minute).status_code == 429
