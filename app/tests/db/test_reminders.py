"""The reminder store (db/reminders.py): one claim wins, the prune keeps what is in limit."""
import threading
import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import psycopg
import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError

from ashfall_app.db import accounts as a
from ashfall_app.db import reminders as r
from ashfall_app.db.engine import open_database

T0 = datetime(2026, 11, 1, 12, tzinfo=UTC)
LATER = T0 + timedelta(days=2)


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


def device(engine: Engine, at: datetime = T0, endpoint: str = "https://push.example/1") -> int:
    with engine.begin() as conn:
        account = a.create_account(conn, at)
        return r.insert_device(conn, at, r.NewDevice(account, endpoint, "p", "a", 24, "UTC", 9, 21))


def waiting_on_a_lock(url: str) -> bool:
    with psycopg.connect(url) as c:
        row = c.execute("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock'").fetchone()
    return row is not None and row[0] > 0


@pytest.mark.parametrize("from_hour, until_hour", [(-1, 21), (9, 24), (24, 0), (0, -1)])
def test_a_send_hour_outside_zero_to_twenty_three_is_refused(engine: Engine, from_hour: int, until_hour: int):
    with engine.begin() as conn:
        account = a.create_account(conn, T0)
    with pytest.raises(IntegrityError), engine.begin() as conn:
        r.insert_device(conn, T0, r.NewDevice(account, "https://push.example/9", "p", "a", 24, "UTC", from_hour, until_hour))


def test_a_claim_that_waits_on_another_loses_when_it_commits(engine: Engine, pg_url: str):
    """Two jobs pick the same device in the same minute; the second's claim blocks on the first's row and, once the
    first commits, finds the reminder already sent."""
    device_id = device(engine)
    second: list[bool] = []

    def claim_second() -> None:
        with engine.begin() as conn:
            second.append(r.claim(conn, device_id, T0, LATER + timedelta(seconds=1)))

    with engine.connect() as first:
        assert r.claim(first, device_id, T0, LATER)
        worker = threading.Thread(target=claim_second)
        worker.start()
        for _ in range(100):
            if waiting_on_a_lock(pg_url) or not worker.is_alive():
                break
            time.sleep(0.05)
        assert worker.is_alive(), "the second claim was not blocked on the first's row, so the race was not set up"
        first.commit()
    worker.join(20)
    assert second == [False]


def test_of_several_claims_at_once_exactly_one_wins(engine: Engine):
    device_id = device(engine)
    wins: list[bool] = []
    start = threading.Barrier(6)

    def claim() -> None:
        start.wait(10)
        with engine.begin() as conn:
            wins.append(r.claim(conn, device_id, T0, LATER))

    workers = [threading.Thread(target=claim) for _ in range(6)]
    for w in workers:
        w.start()
    for w in workers:
        w.join(20)
    assert sorted(wins) == [False] * 5 + [True]


def test_a_visit_since_the_candidates_were_read_leaves_nothing_to_claim(engine: Engine):
    device_id = device(engine)
    assert not _claim(engine, device_id, T0 - timedelta(hours=1))


def test_a_claim_marks_the_visit_and_the_device_is_no_longer_a_candidate(engine: Engine):
    device_id = device(engine)
    assert [d.id for d in _unsent(engine)] == [device_id]
    assert _claim(engine, device_id, T0)
    assert _unsent(engine) == []


def _claim(engine: Engine, device_id: int, visited_at: datetime) -> bool:
    with engine.begin() as conn:
        return r.claim(conn, device_id, visited_at, LATER)


def _unsent(engine: Engine) -> list[r.DeviceRecord]:
    with engine.connect() as conn:
        return r.unsent(conn)


def test_the_prune_drops_past_limit_devices_and_keeps_in_limit_ones(engine: Engine):
    before = T0
    old = device(engine, before - timedelta(seconds=1), "https://push.example/old")
    edge = device(engine, before, "https://push.example/edge")
    fresh = device(engine, before + timedelta(days=1), "https://push.example/fresh")
    with engine.begin() as conn:
        assert r.delete_unvisited_before(conn, before, limit=10) == 1
    assert sorted(d.id for d in _unsent(engine)) == [edge, fresh] and old not in {d.id for d in _unsent(engine)}


def test_the_prune_takes_at_most_its_limit_oldest_first(engine: Engine):
    ids = [device(engine, T0 - timedelta(days=n), f"https://push.example/{n}") for n in (3, 2, 1)]
    with engine.begin() as conn:
        assert r.delete_unvisited_before(conn, T0, limit=2) == 2
    assert [d.id for d in _unsent(engine)] == [ids[2]]
