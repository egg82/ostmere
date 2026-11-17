"""The queue's day counts kept in Postgres (db/writer_counts.py): a fresh Queue on the same database sees today's visits
and spent calls, a new day starts empty, and a visit drops the rows of past days."""
from collections.abc import Iterator
from datetime import date, timedelta

import pytest
from sqlalchemy import Engine, func, select

from ashfall_app.db.engine import open_database
from ashfall_app.db.tables import writer_day
from ashfall_app.db.writer_counts import PgCounts
from ashfall_app.writer import budget as budgets
from ashfall_app.writer.interface import JobKind
from ashfall_app.writer.queue import Job, Queue
from ashfall_app.writer.service import Registry, Writer

KIND = JobKind("arrival")
BUDGET = budgets.Budget(global_daily=100, per_save_daily=2, weight_cap=8)
DAY = date(2026, 11, 16)


class Counting:
    def __init__(self) -> None:
        self.calls = 0

    def write(self, kind: JobKind, stand_in: str) -> str:
        self.calls += 1
        return "written"


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


def boot(engine: Engine, day: date = DAY) -> tuple[Queue, Counting]:
    """A queue as a freshly started process builds it."""
    client = Counting()
    return Queue(Writer(Registry((KIND,)), client), lambda: day, BUDGET, PgCounts(engine)), client


def run(q: Queue, n: int, save: str = "a") -> list[str]:
    for _ in range(n):
        assert q.enqueue(Job(save, "arrival", "stand-in"))
    return [text for _, text in q.drain()]


def rows(engine: Engine) -> set[tuple[date, str]]:
    with engine.connect() as conn:
        return {(r.day, r.save_id) for r in conn.execute(select(writer_day.c.day, writer_day.c.save_id))}


def test_a_restart_keeps_the_days_visits_and_spent_calls(engine: Engine) -> None:
    first, _ = boot(engine)
    first.visit("a", 0)
    assert run(first, 2) == ["written", "written"]
    second, client = boot(engine)
    assert second.enqueue(Job("a", "arrival", "stand-in")), "the visit survived the restart"
    assert second.drain() == [(Job("a", "arrival", "stand-in"), "stand-in")], "the spent calls did too"
    assert client.calls == 0


def test_a_save_over_its_cap_after_a_restart_still_gets_the_stand_in(engine: Engine) -> None:
    first, _ = boot(engine)
    first.visit("a", 0)
    first.visit("b", 0)
    run(first, 1, "a")
    second, _ = boot(engine)
    assert run(second, 2, "a") == ["written", "stand-in"], "one call left of the two"
    assert run(second, 1, "b") == ["written"], "another world's allowance is untouched"


def test_a_new_day_starts_empty(engine: Engine) -> None:
    first, _ = boot(engine)
    first.visit("a", 0)
    run(first, 2)
    tomorrow, _ = boot(engine, DAY + timedelta(days=1))
    assert not tomorrow.enqueue(Job("a", "arrival", "stand-in")), "yesterday's visit does not carry over"
    tomorrow.visit("a", 0)
    assert run(tomorrow, 1) == ["written"]


def test_a_visit_deletes_the_rows_of_past_days_and_keeps_today(engine: Engine) -> None:
    old, _ = boot(engine, DAY - timedelta(days=3))
    old.visit("a", 0)
    older, _ = boot(engine, DAY - timedelta(days=1))
    older.visit("b", 0)
    today, _ = boot(engine)
    today.visit("c", 0)
    assert rows(engine) == {(DAY, "c")}
    again, _ = boot(engine)
    again.visit("d", 0)
    again.visit("c", 4)
    assert rows(engine) == {(DAY, "c"), (DAY, "d")}


def test_a_second_visit_keeps_what_the_world_spent(engine: Engine) -> None:
    q, _ = boot(engine)
    q.visit("a", 0)
    run(q, 1)
    q.visit("a", 3)
    with engine.connect() as conn:
        row = conn.execute(select(writer_day.c.weight, writer_day.c.spent)).one()
        assert conn.execute(select(func.count()).select_from(writer_day)).scalar_one() == 1
    assert (row.weight, row.spent) == (4, 1)
