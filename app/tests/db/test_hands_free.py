"""The hands-free columns on saves (db/handsfree.py): one claim wins, a write at or past the instant leaves nothing to
claim, a decision drops the kept answer, and the latest save is the one read."""
import threading
import time
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Connection, Engine

from ashfall_app.db import accounts as a
from ashfall_app.db import handsfree as hf
from ashfall_app.db import reminders as r
from ashfall_app.db import saves as s
from ashfall_app.db.engine import open_database
from tests.db.test_reminders import waiting_on_a_lock
from tests.kills import kills

T0 = datetime(2026, 11, 1, 12, tzinfo=UTC)
AT = 4000
WRITTEN = s.Written(state="{}", format=1, rules_digest="d", decisions=1, game_time=1000, ended_at=None, build="b",
                    release=1, camp_level=0)


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


def taker(conn: Connection, at: datetime = T0, endpoint: str = "https://push.example/1") -> int:
    """An account with a device that takes the notice (its absence reminder off)."""
    account = a.create_account(conn, at)
    r.insert_device(conn, at, r.NewDevice(account, endpoint, "p", "a", None, "UTC", 0, 0, hands_free=True))
    return account


def kept_save(engine: Engine, at: int | None = AT) -> tuple[int, int]:
    """(save, account): a save written at game time 1000 whose kept answer is free at `at`."""
    with engine.begin() as conn:
        account = taker(conn)
        save = s.insert_save(conn, account, T0, WRITTEN)
        assert hf.keep(conn, save, account, WRITTEN.decisions, at, 1000 + 6 * 3600)
    return save, account


def only(engine: Engine) -> hf.Latest:
    with engine.connect() as conn:
        [found] = hf.latest(conn)
    return found


def test_keep_maps_the_instant_to_the_wall_from_the_saves_start(engine: Engine):
    kept_save(engine)
    found = only(engine)
    assert (found.at, found.wall, found.until, found.sent) == (AT, T0 + timedelta(seconds=AT), 1000 + 6 * 3600, None)


def test_keep_after_a_decision_was_written_keeps_nothing(engine: Engine):
    save, account = kept_save(engine, None)
    with engine.begin() as conn:
        assert not hf.keep(conn, save, account, WRITTEN.decisions - 1, AT, 99_999)
    assert only(engine).at is None


def test_a_write_with_a_decision_drops_the_kept_answer_and_an_advance_keeps_it(engine: Engine):
    save, _ = kept_save(engine)
    with engine.begin() as conn:
        s.write(conn, save, T0, replace(WRITTEN, game_time=1500))
    assert only(engine).at == AT
    with engine.begin() as conn:
        s.write(conn, save, T0, replace(WRITTEN, game_time=1600, decisions=2))
    found = only(engine)
    assert (found.at, found.wall, found.until) == (None, None, None) and found.stale(T0)


def test_the_latest_live_save_of_each_taker_is_read_and_no_one_elses(engine: Engine):
    with engine.begin() as conn:
        account = taker(conn)
        older = s.insert_save(conn, account, T0, WRITTEN)
        newer = s.insert_save(conn, account, T0 + timedelta(minutes=1), WRITTEN)
        gone = s.insert_save(conn, account, T0 + timedelta(minutes=2), WRITTEN)
        s.set_deleted(conn, gone, T0)
        bystander = a.create_account(conn, T0)
        r.insert_device(conn, T0, r.NewDevice(bystander, "https://push.example/2", "p", "a", 24, "UTC", 9, 21))
        s.insert_save(conn, bystander, T0, WRITTEN)
    with engine.connect() as conn:
        assert [x.save_id for x in hf.latest(conn)] == [newer] and older != newer


def test_a_claim_marks_the_instant_once(engine: Engine):
    save, _ = kept_save(engine)
    with engine.begin() as conn:
        assert hf.claim(conn, save, AT)
        assert not hf.claim(conn, save, AT)
    assert only(engine).sent == AT


def test_nothing_to_claim_once_the_save_was_written_at_or_past_the_instant(engine: Engine):
    save, _ = kept_save(engine)
    with engine.begin() as conn:
        s.write(conn, save, T0, replace(WRITTEN, game_time=AT))
        assert not hf.claim(conn, save, AT)


def test_nothing_to_claim_for_an_instant_a_new_answer_replaced(engine: Engine):
    save, _ = kept_save(engine)
    with engine.begin() as conn:
        assert not hf.claim(conn, save, AT - 1)


def test_a_claim_that_waits_on_another_loses_when_it_commits(engine: Engine, pg_url: str):
    save, _ = kept_save(engine)
    second: list[bool] = []

    def claim_second() -> None:
        with engine.begin() as conn:
            second.append(hf.claim(conn, save, AT))

    with engine.connect() as first:
        assert hf.claim(first, save, AT)
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


@kills(12)
def test_of_several_claims_at_once_exactly_one_wins(engine: Engine):
    save, _ = kept_save(engine)
    wins: list[bool] = []
    start = threading.Barrier(6)

    def claim() -> None:
        start.wait(10)
        with engine.begin() as conn:
            wins.append(hf.claim(conn, save, AT))

    workers = [threading.Thread(target=claim) for _ in range(6)]
    for w in workers:
        w.start()
    for w in workers:
        w.join(20)
    assert sorted(wins) == [False] * 5 + [True]
