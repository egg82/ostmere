"""Round trips of each route a returning player's page calls, pinned. From the second site each trip is ~11 ms
(docs/decisions/saves.md), so a route's trips are its latency; the pool's read-only check, a BEGIN and a COMMIT are
trips as much as a statement. Counted where psycopg sends, through the real app: each command (BEGIN, COMMIT) and
each statement, not the one-off prepare a repeated statement earns."""
from collections.abc import Callable, Generator
from typing import Any

import pytest
from psycopg import Connection
from psycopg import _cursor_base as cursors
from sqlalchemy import text

from tests.db.test_one_checkout import engine_of
from tests.game_client import GameClient

SENDS = (
    (Connection, "_exec_command"),
    (cursors.BaseCursor, "_execute_send"),
    (cursors.BaseCursor, "_send_query_prepared"),
)


@pytest.fixture
def trips(monkeypatch: pytest.MonkeyPatch) -> Generator[list[int]]:
    """One entry per round trip psycopg makes on any connection, appended as it is sent."""
    seen: list[int] = []

    def counted(original: Callable[..., Any]) -> Callable[..., Any]:
        def send(*args: Any, **kwargs: Any) -> Any:
            seen.append(1)
            return original(*args, **kwargs)
        return send

    for owner, name in SENDS:
        monkeypatch.setattr(owner, name, counted(getattr(owner, name)))
    yield seen


def test_a_transaction_outside_a_request_is_counted(game: GameClient, trips: list[int]):
    """The control: the pool's check, BEGIN, the statement and COMMIT are four trips."""
    engine = engine_of(game)
    before = len(trips)
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
    assert len(trips) - before == 4


def test_each_route_takes_its_round_trips(game: GameClient, trips: list[int]):
    client = game.client

    def taken(call: Callable[[], Any]) -> int:
        before = len(trips)
        r = call()
        assert r.status_code < 500, r.text
        return len(trips) - before

    first = game.begin()
    save = first["save"]["save_id"]
    after = first["step"]["decisions"]
    counts = {
        "begin, signed in": taken(lambda: client.post("/api/saves")),
        "me": taken(lambda: client.get("/api/me")),
        "open": taken(lambda: client.post(f"/api/saves/{save}/open")),
        "advance": taken(lambda: game.advance(save)),
        "forecast": taken(lambda: client.post(f"/api/saves/{save}/forecast")),
        "decide": taken(lambda: game.decide(save, {"kind": "tap_card", "card": "stand_up"}, after)),
        "games": taken(lambda: client.get("/api/saves")),
        "devices": taken(lambda: client.get("/api/me/devices")),
    }
    game.clock.tick(days=2)
    counts["advance, renewing the session"] = taken(lambda: game.advance(save))
    counts["begin, no account"] = taken(lambda: game.stranger().post("/api/saves"))
    assert counts == {
        "begin, signed in": 13,
        "me": 5,
        "open": 6,
        "advance": 6,
        "forecast": 5,
        "decide": 7,
        "games": 6,
        "devices": 5,
        "advance, renewing the session": 10,
        "begin, no account": 23,
    }
