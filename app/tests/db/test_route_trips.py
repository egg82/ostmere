"""Round trips for the two routes a returning player's page opens with. From the second site each trip is ~11 ms, so a
route's trips are its latency. Counted through the real app at the engine: each statement sent, and the trips around
them: the pool's read-only check on a checkout, the BEGIN, the COMMIT or ROLLBACK."""
from typing import Any

from sqlalchemy import Engine, event

from tests.db.test_one_checkout import engine_of
from tests.game_client import GameClient

ME = 6
OPEN = 8


def trips(engine: Engine) -> list[str]:
    """One entry per round trip the engine causes, in order, appended as it happens."""
    seen: list[str] = []

    @event.listens_for(engine, "checkout")
    def checkout(*_: Any) -> None:
        seen.append("SHOW transaction_read_only")

    @event.listens_for(engine, "begin")
    def begin(*_: Any) -> None:
        seen.append("BEGIN")

    @event.listens_for(engine, "before_cursor_execute")
    def execute(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        seen.append(" ".join(statement.split())[:70])

    @event.listens_for(engine, "commit")
    def commit(*_: Any) -> None:
        seen.append("COMMIT")

    @event.listens_for(engine, "rollback")
    def rollback(*_: Any) -> None:
        seen.append("ROLLBACK")
    return seen


def test_the_count_sees_every_kind_of_trip(game: GameClient):
    """The control: a checkout, a statement and a commit outside a request are each counted."""
    engine = engine_of(game)
    seen = trips(engine)
    with engine.begin() as conn:
        conn.exec_driver_sql("SELECT 1")
    assert seen == ["SHOW transaction_read_only", "BEGIN", "SELECT 1", "COMMIT"]


def test_each_route_stays_within_its_trips(game: GameClient):
    save = game.begin()["save"]["save_id"]
    seen = trips(engine_of(game))
    seen.clear()
    assert game.client.get("/api/me").status_code == 200
    me, seen[:] = list(seen), []
    assert game.client.post(f"/api/saves/{save}/open").status_code == 200
    opened = list(seen)
    assert len(me) <= ME, me
    assert len(opened) <= OPEN, opened
