"""The decision limits (accounts/limits.py `decided_in`): a save may take DECISIONS_PER_MINUTE in a minute and
DECISIONS_PER_HOUR in an hour; a decision over either is refused with the wait until the oldest counted try leaves
its window, and a refusal counts nothing."""
import math
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Engine, func, insert, select

from ashfall_app.accounts import limits
from ashfall_app.db import tries
from ashfall_app.db.engine import open_database
from ashfall_app.db.tables import tries as tries_table

NOW = datetime(2026, 10, 1, 12, tzinfo=UTC)
MINUTE, HOUR = limits.DECISIONS_MINUTE, limits.DECISIONS_HOUR
PER_MINUTE, PER_HOUR = limits.DECISIONS_PER_MINUTE, limits.DECISIONS_PER_HOUR


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url, max_size=6)
    yield database.engine
    database.close()


def seed(engine: Engine, who: int, ats: list[datetime], kind: str = limits.DECISION) -> None:
    with engine.begin() as conn:
        conn.execute(insert(tries_table), [{"kind": kind, "who": str(who).encode(), "at": at} for at in ats])


def decide(engine: Engine, save: int) -> limits.Refusal | None:
    with engine.begin() as conn:
        return limits.decided_in(conn, save, NOW)


def stored(engine: Engine, who: int) -> int:
    with engine.connect() as conn:
        return int(conn.execute(select(func.count()).select_from(tries_table)
                                .where(tries_table.c.who == str(who).encode())).scalar_one())


def test_the_last_decision_of_a_minute_is_counted_and_the_next_is_refused(engine: Engine):
    seed(engine, 1, [NOW - timedelta(seconds=40)] * (PER_MINUTE - 1))
    assert decide(engine, 1) is None
    assert stored(engine, 1) == PER_MINUTE
    assert decide(engine, 1) == limits.Refusal(limits.DECISION, 20)
    assert stored(engine, 1) == PER_MINUTE, "a refusal counts nothing"


def test_a_try_exactly_a_window_old_still_counts_and_one_older_does_not(engine: Engine):
    seed(engine, 1, [NOW - MINUTE] + [NOW - timedelta(seconds=5)] * (PER_MINUTE - 1))
    assert decide(engine, 1) == limits.Refusal(limits.DECISION, 1)
    seed(engine, 2, [NOW - MINUTE - timedelta(microseconds=1)] + [NOW - timedelta(seconds=5)] * (PER_MINUTE - 1))
    assert decide(engine, 2) is None


def test_the_hour_limit_refuses_what_the_minute_limit_allows(engine: Engine):
    seed(engine, 1, [NOW - timedelta(minutes=30)] * (PER_HOUR - 1))
    assert decide(engine, 1) is None
    refused = decide(engine, 1)
    assert refused == limits.Refusal(limits.DECISION, math.ceil((timedelta(minutes=30)).total_seconds()))
    assert stored(engine, 1) == PER_HOUR


def test_the_minute_limit_names_its_own_wait_when_both_are_reached(engine: Engine):
    seed(engine, 1, [NOW - timedelta(minutes=30)] * (PER_HOUR - PER_MINUTE) + [NOW - timedelta(seconds=10)] * PER_MINUTE)
    assert decide(engine, 1) == limits.Refusal(limits.DECISION, 50)


def test_another_saves_or_kinds_tries_do_not_count(engine: Engine):
    seed(engine, 2, [NOW - timedelta(seconds=5)] * PER_HOUR)
    seed(engine, 1, [NOW - timedelta(seconds=5)] * PER_HOUR, kind=limits.CODE_MAKE)
    assert decide(engine, 1) is None
    assert stored(engine, 1) == PER_HOUR + 1


def test_a_decision_that_fails_after_its_count_leaves_no_try(engine: Engine):
    with pytest.raises(RuntimeError):
        with engine.begin() as conn:
            assert limits.decided_in(conn, 1, NOW) is None
            raise RuntimeError
    assert stored(engine, 1) == 0


def test_tries_past_the_longest_window_go_and_the_rest_stay(engine: Engine):
    seed(engine, 3, [NOW - HOUR - timedelta(seconds=1), NOW - HOUR, NOW - timedelta(minutes=5)])
    assert decide(engine, 1) is None
    with engine.connect() as conn:
        assert tries.count(conn, limits.DECISION, NOW - timedelta(days=1)) == 3   # one gone, two kept, one added
