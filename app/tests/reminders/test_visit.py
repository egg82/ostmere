"""The visit stamp (db/reminders.py `visit`): open and advance stamp a device's visit at most once per VISIT_EVERY,
only for an account with a device on, inside the statement that locks the save, so the request runs no more
statements than it did."""
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from sqlalchemy import Engine, event

from tests.game_client import GameClient
from tests.reminders.wire import engine_of, on, rows, visited


def statements(engine: Engine) -> list[str]:
    seen: list[str] = []

    @event.listens_for(engine, "before_cursor_execute")
    def executed(_conn: Any, _cursor: Any, statement: str, *_: Any) -> None:
        seen.append(statement)
    return seen


def counted(seen: list[str], call: Callable[[], Any]) -> int:
    before = len(seen)
    r = call()
    assert r.status_code == 200, r.text
    return len(seen) - before


def test_open_and_advance_stamp_the_visit_at_most_once_per_ten_minutes(game: GameClient):
    save = game.begin()["save"]["save_id"]
    game.client.put("/api/reminders", json=on())
    t0 = visited(game)
    game.clock.tick(minutes=9)
    game.advance(save)
    assert visited(game) == t0
    game.clock.tick(minutes=2)
    game.advance(save)
    assert visited(game) == t0 + timedelta(minutes=11)
    game.clock.tick(minutes=11)
    assert game.client.post(f"/api/saves/{save}/open").status_code == 200
    assert visited(game) == t0 + timedelta(minutes=22)


def test_another_accounts_advance_does_not_stamp_this_ones(game: GameClient):
    game.begin()
    game.client.put("/api/reminders", json=on())
    t0 = visited(game)
    other = game.stranger()
    theirs = other.post("/api/saves").json()["save"]["save_id"]
    game.clock.tick(minutes=11)
    assert other.post(f"/api/saves/{theirs}/advance").status_code == 200
    assert visited(game) == t0


def test_the_stamp_adds_no_statement_to_open_or_advance(game: GameClient):
    seen = statements(engine_of(game))
    save = game.begin()["save"]["save_id"]
    assert seen, "the counter sees the app's statements"
    game.clock.tick(minutes=11)
    bare = (counted(seen, lambda: game.advance(save)), counted(seen, lambda: game.client.post(f"/api/saves/{save}/open")))
    game.client.put("/api/reminders", json=on())
    t0 = visited(game)
    game.clock.tick(minutes=11)
    with_row = (counted(seen, lambda: game.advance(save)),)
    game.clock.tick(minutes=11)
    with_row += (counted(seen, lambda: game.client.post(f"/api/saves/{save}/open")),)
    assert visited(game) == t0 + timedelta(minutes=22), "both requests stamped"
    assert with_row == bare, (bare, with_row)
    assert len(rows(game)) == 1
