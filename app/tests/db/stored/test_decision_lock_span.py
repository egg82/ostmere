"""A decision holds its save's row (SELECT ... FOR UPDATE) from the lock to the COMMIT, and from the second site each
statement in between is a round trip of ~11 ms that every other request on the save waits behind. Counted through the
real app, as statements the engine sends: the lock's own, each after it, and the COMMIT."""
from typing import Any

from sqlalchemy import Engine, event, select, text

from tests.db.test_one_checkout import engine_of
from tests.game_client import GameClient

MOST = 4
"""The lock, `tries` in one statement, the write in one statement, the COMMIT."""


def lock_span(engine: Engine) -> list[int]:
    """One entry per row lock taken, appended when its transaction commits: the statements from the lock through the
    COMMIT, the COMMIT counted as one."""
    spans: list[int] = []
    open_: list[int] = []

    @event.listens_for(engine, "before_cursor_execute")
    def before(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        if "FOR UPDATE" in statement.upper() and not open_:
            open_.append(0)
        if open_:
            open_[0] += 1

    @event.listens_for(engine, "commit")
    def commit(conn: Any) -> None:
        if open_:
            spans.append(open_.pop() + 1)
    return spans


def test_the_span_counts_a_locked_read_and_its_commit(game: GameClient):
    """The control: a lock, one statement after it and the COMMIT are three."""
    engine = engine_of(game)
    spans = lock_span(engine)
    with engine.begin() as conn:
        conn.execute(select(text("1")).with_for_update())
        conn.execute(select(text("1")))
    assert spans == [3]


def test_a_decision_holds_its_lock_over_few_round_trips(game: GameClient):
    first = game.begin()
    save, after = first["save"]["save_id"], first["step"]["decisions"]
    spans = lock_span(engine_of(game))
    found: dict[str, int] = {}

    def decide(label: str) -> None:
        nonlocal after
        before = len(spans)
        r = game.decide(save, {"kind": "tap_card", "card": "stand_up"}, after)
        assert r.status_code == 200, r.text
        after = r.json()["decisions"]
        assert len(spans) == before + 1, (label, spans)
        found[label] = spans[-1]

    game.clock.tick(minutes=10)
    decide("first of its day")
    game.clock.tick(minutes=10)
    decide("mid-day")
    game.clock.tick(days=2)
    decide("session renewal due")
    assert {k: n for k, n in found.items() if n > MOST} == {}, found
