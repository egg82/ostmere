"""Counting a decision (accounts/limits.py decided_in) trims the decision tries past their window, and a trim never
waits on another transaction: a decision on one save does not wait for a decision on another to finish, however many
expired tries are lying about."""
import threading
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError

from ashfall_app.accounts import limits
from ashfall_app.db import tries
from ashfall_app.db.engine import open_database

NOW = datetime(2026, 10, 1, 12, tzinfo=UTC)
LOCK_TIMEOUT = "300ms"


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


def second_decision(engine: Engine, out: list[object]) -> None:
    try:
        with engine.begin() as conn:
            conn.execute(text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))
            out.append(limits.decided_in(conn, 2, NOW))
    except OperationalError as ex:
        out.append(ex)


def test_a_decision_does_not_wait_for_another_saves_decision_to_trim(engine: Engine):
    with engine.begin() as conn:
        tries.add(conn, limits.DECISION, b"99", NOW - timedelta(hours=2))
    out: list[object] = []
    with engine.connect() as first, first.begin():
        assert limits.decided_in(first, 1, NOW) is None
        thread = threading.Thread(target=second_decision, args=(engine, out))
        thread.start()
        thread.join()
    assert out == [None], out


def test_the_expired_tries_still_go(engine: Engine):
    with engine.begin() as conn:
        tries.add(conn, limits.DECISION, b"99", NOW - timedelta(hours=2))
        assert limits.decided_in(conn, 1, NOW) is None
        assert tries.count(conn, limits.DECISION, NOW - timedelta(days=1)) == 1
