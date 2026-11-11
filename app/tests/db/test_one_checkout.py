"""Every request takes one pool checkout at most, its session lookup and any session renewal included: each checkout
pays the pool's read-only check and a BEGIN, a round trip apiece, and from the second site each round trip is ~11 ms.
Counted through the real app, at the engine's pool, for each route a returning player's page calls."""
from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy import Engine, event, select

from ashfall_app.db.engine import Database
from ashfall_app.db.tables import saves
from tests.db.test_failover import at_statement, read_only_transaction, terminate, writes
from tests.game_client import GameClient


def checkouts(engine: Engine) -> list[int]:
    """One entry per connection the engine takes from the pool, appended as each is taken."""
    seen: list[int] = []

    @event.listens_for(engine, "checkout")
    def checkout(*_: Any) -> None:
        seen.append(1)
    return seen


def engine_of(game: GameClient) -> Engine:
    database: Database = game.app.state.db
    return database.engine


def test_a_checkout_outside_a_request_is_counted(game: GameClient):
    """The control: the count sees every connection the engine takes."""
    engine = engine_of(game)
    seen = checkouts(engine)
    for _ in range(2):
        with engine.begin():
            pass
    assert len(seen) == 2


def test_each_route_takes_one_checkout(game: GameClient):
    seen = checkouts(engine_of(game))
    client, clock = game.client, game.clock

    def taken(call: Callable[[], Any]) -> int:
        before = len(seen)
        r = call()
        assert r.status_code < 500, r.text
        return len(seen) - before

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
    clock.tick(days=2)
    counts["advance, renewing the session"] = taken(lambda: game.advance(save))
    counts["begin, no account"] = taken(lambda: game.stranger().post("/api/saves"))
    assert all(n >= 1 for n in counts.values()), counts
    assert {k: n for k, n in counts.items() if n > 1} == {}


def into_sessions(statement: str) -> bool:
    return statement.lstrip().upper().startswith("UPDATE SESSIONS")


def test_a_decision_refused_read_only_after_its_session_lookup_replays_once(
        game: GameClient, capsys: pytest.CaptureFixture[str]):
    """The lookup shares the decision's transaction, so the refusal discards both; the replay runs the whole request
    again on a new checkout and the decision is applied once."""
    first = game.begin()
    save, after = first["save"]["save_id"], first["step"]["decisions"]
    engine = engine_of(game)
    seen = checkouts(engine)
    at_statement(engine, read_only_transaction)
    r = game.decide(save, {"kind": "tap_card", "card": "stand_up"}, after)
    assert r.status_code == 200, r.text
    assert r.json()["decisions"] == after + 1
    assert len(seen) == 2
    assert "event=db.failover kind=readonly sqlstate=25006 replayed=true" in capsys.readouterr().out


def test_a_renewal_lost_after_the_write_committed_is_not_replayed(
        game: GameClient, pg_url: str, capsys: pytest.CaptureFixture[str]):
    """The renewal runs after the write's COMMIT, on the same checkout: its loss changes nothing about the answer and
    runs nothing again."""
    save = game.begin()["save"]["save_id"]
    game.clock.tick(days=2)
    engine = engine_of(game)
    seen = writes(engine)
    at_statement(engine, terminate(pg_url), into_sessions)
    capsys.readouterr()
    r = game.advance(save)
    assert r.status_code == 200 and "set-cookie" not in r.headers, r.text
    out = capsys.readouterr().out
    assert "event=session.renew_failed" in out and "event=db.failover" not in out
    assert sum("UPDATE SAVES SET" in s.upper() for s in seen) == 1
    with engine.connect() as conn:
        assert conn.execute(select(saves.c.updated_at).where(saves.c.id == save)).scalar_one() == game.clock()
