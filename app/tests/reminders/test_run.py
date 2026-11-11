"""One run of the job (reminders/run.py) against a database and a push service on localhost."""
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Engine

from ashfall_app import logs
from ashfall_app.db import accounts as a
from ashfall_app.db import reminders as store
from ashfall_app.db.engine import open_database
from ashfall_app.reminders.run import RETENTION, Counts, run
from ashfall_app.reminders.sender import WebPushSender

from tests.reminders.fakepush import push_service, subscription_keys, vapid_config

VISIT = datetime(2026, 11, 1, 12, tzinfo=UTC)
NOW = VISIT + timedelta(days=2)   # noon UTC, a day past a 24 hour wait
SECRET = "token-that-must-not-be-logged"


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


def add(engine: Engine, endpoint: str, visited: datetime = VISIT) -> int:
    p256dh, auth = subscription_keys()
    with engine.begin() as conn:
        account = a.create_account(conn, visited)
        return store.insert_device(conn, visited, store.NewDevice(account, endpoint, p256dh, auth, 24, "UTC", 9, 21))


def go(engine: Engine, now: datetime = NOW) -> Counts:
    return run(engine, WebPushSender(vapid_config(), allowed=lambda e: True), lambda: now)


def remaining(engine: Engine) -> list[int]:
    with engine.connect() as conn:
        return [d.id for d in store.unsent(conn)]


def job_lines(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return [ln for ln in capsys.readouterr().out.splitlines() if "logger=ashfall.reminders" in ln]


def test_a_201_is_sent_and_marked_so_the_next_run_sends_nothing(engine: Engine, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    with push_service() as (base, seen):
        device = add(engine, f"{base}/201/{SECRET}")
        assert go(engine) == Counts(due=1, sent=1)
        assert go(engine, NOW + timedelta(minutes=5)) == Counts()
        assert len(seen.paths) == 1
    assert remaining(engine) == []
    assert device not in remaining(engine)
    runs = [ln for ln in job_lines(capsys) if "event=reminders.run " in ln]
    assert len(runs) == 2 and " due=1 sent=1 gone=0 failed=0 pruned=0 ms=" in runs[0]


def test_a_410_deletes_the_device_with_one_line(engine: Engine, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    with push_service() as (base, _):
        add(engine, f"{base}/410/{SECRET}")
        assert go(engine) == Counts(due=1, gone=1)
    with engine.connect() as conn:
        assert conn.exec_driver_sql("SELECT count(*) FROM reminder_devices").scalar_one() == 0
    gone = [ln for ln in job_lines(capsys) if "event=reminders.gone" in ln]
    assert len(gone) == 1 and "status=410" in gone[0]


def test_a_500_keeps_the_device_with_one_line_and_does_not_send_again(engine: Engine, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    with push_service() as (base, seen):
        add(engine, f"{base}/500/{SECRET}")
        assert go(engine) == Counts(due=1, failed=1)
        assert go(engine, NOW + timedelta(minutes=5)) == Counts()
        assert len(seen.paths) == 1
    with engine.connect() as conn:
        assert conn.exec_driver_sql("SELECT count(*) FROM reminder_devices").scalar_one() == 1
    failed = [ln for ln in job_lines(capsys) if "event=reminders.send_failed" in ln]
    assert len(failed) == 1 and "status=500" in failed[0] and "why=http" in failed[0]


def test_no_endpoint_or_key_reaches_the_log(engine: Engine, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    with push_service() as (base, _):
        for status in (201, 410, 500):
            add(engine, f"{base}/{status}/{SECRET}")
        go(engine)
    out = capsys.readouterr().out
    assert "event=reminders.run " in out and "event=reminders.gone" in out and "event=reminders.send_failed" in out
    assert SECRET not in out and "127.0.0.1" not in out and "p256dh" not in out


def test_a_device_not_yet_due_is_left_alone(engine: Engine):
    with push_service() as (base, seen):
        add(engine, f"{base}/201", visited=NOW - timedelta(hours=1))
        assert go(engine) == Counts()
        assert seen.paths == []


def test_the_run_prunes_devices_unvisited_past_the_retention(engine: Engine):
    with push_service() as (base, _):
        old = add(engine, f"{base}/201/old", visited=NOW - RETENTION - timedelta(days=1))
        kept = add(engine, f"{base}/201/kept", visited=NOW - RETENTION + timedelta(days=1))
        assert go(engine).pruned == 1
    with engine.connect() as conn:
        left = [r[0] for r in conn.exec_driver_sql("SELECT id FROM reminder_devices")]
    assert old not in left and kept in left
