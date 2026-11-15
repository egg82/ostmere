"""The journal's rows (db/journal.py, db/step.py): a step's statement stores its days beside its lines, a day the save
already holds is left as stored, the save's locking statement reads the day after its newest and, only once a day has
ended that no stored day covers, the days and the lines asked; it says when its snapshot is older than the row it
locked; and deleting a save for good takes its days with it."""
import threading
import time
from collections.abc import Iterator
from datetime import datetime

import pytest
from sqlalchemy import Connection, Engine

from ashfall_app.db import accounts as a
from ashfall_app.db import journal
from ashfall_app.db import saves as s
from ashfall_app.db import step
from ashfall_app.db.engine import open_database
from tests.db.test_records import DAY, T0, written
from tests.saves.journal_fixture import lock_waiters

NOTES_A = [{"subject": "s_a", "slot": "first", "key": "k.a"}]
NOTES_B = [{"subject": "s_b", "slot": "first", "key": "k.b"}]


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


@pytest.fixture
def conn(engine: Engine) -> Iterator[Connection]:
    with engine.begin() as c:
        yield c


def new_save(conn: Connection) -> tuple[int, int]:
    account = a.create_account(conn, T0)
    return account, s.insert_save(conn, account, T0, written())


def seen(conn: Connection, account: int, sid: int, now: datetime) -> journal.Seen:
    found = journal.locked(conn, sid, account, None, ["k"], now)
    assert found is not None and found[0].id == sid
    return found[1]


def test_a_step_stores_its_days_and_the_locking_read_reads_them_once_a_day_is_due(conn: Connection):
    account, sid = new_save(conn)
    assert seen(conn, account, sid, T0 + DAY / 2) == journal.Seen(0, True, None, None)
    step.write_step(conn, sid, T0, written(), [(5, "k"), (6, "other"), (3 * 86400, "k")], None, None,
                    [step.JournalDay(0, NOTES_A, None), step.JournalDay(1, [], "busy")])
    stored = [journal.DayRecord(0, [{"subject": "s_a", "slot": "first", "key": "k.a"}], None),
              journal.DayRecord(1, [], "busy")]
    assert journal.days(conn, sid) == stored
    assert seen(conn, account, sid, T0 + 2 * DAY) == journal.Seen(2, True, None, None)
    assert seen(conn, account, sid, T0 + 3 * DAY) == journal.Seen(2, True, stored, [(5, "k")])


def test_a_locking_read_that_waited_on_another_write_says_its_snapshot_is_stale(pg_url: str, engine: Engine):
    with engine.begin() as c:
        account, sid = new_save(c)
    found: list[journal.Seen] = []
    with engine.connect() as writer:
        writer.begin()
        step.write_step(writer, sid, T0, written(decisions=1), [], None, None, [step.JournalDay(0, NOTES_A, None)])

        def read() -> None:
            with engine.begin() as c:
                found.append(seen(c, account, sid, T0 + 2 * DAY))
        reader = threading.Thread(target=read)
        reader.start()
        deadline = time.monotonic() + 3
        while lock_waiters(pg_url) < 1 and time.monotonic() < deadline:
            pass
        assert lock_waiters(pg_url) == 1, "the read never waited on the write"
        writer.commit()
    reader.join(3)
    assert [(f.fresh, f.next_day, f.days) for f in found] == [(False, 0, [])]
    with engine.begin() as c:
        assert seen(c, account, sid, T0 + 2 * DAY).fresh


def test_a_day_the_save_already_holds_is_left_as_stored(conn: Connection):
    _, sid = new_save(conn)
    step.write_step(conn, sid, T0, written(), [], None, None, [step.JournalDay(0, NOTES_A, None)])
    step.write_step(conn, sid, T0 + DAY, written(decisions=1), [(9, "k")], None, None,
                    [step.JournalDay(0, NOTES_B, None), step.JournalDay(1, NOTES_B, None)])
    assert [(d.day, d.notes[0]["key"]) for d in journal.days(conn, sid)] == [(0, "k.a"), (1, "k.b")]
    assert [ln.key for ln in s.last_lines(conn, sid, 10)] == ["k"], "the step's other writes did not land"


def test_lines_of_reads_only_the_keys_asked_before_the_time_asked(conn: Connection):
    _, sid = new_save(conn)
    s.append_lines(conn, sid, [(1, "a"), (2, "b"), (3, "a"), (4, "a")])
    assert journal.lines_of(conn, sid, ["a"], 4) == [(1, "a"), (3, "a")]


def test_a_save_deleted_for_good_takes_its_days(conn: Connection):
    _, sid = new_save(conn)
    step.write_step(conn, sid, T0, written(), [], None, None, [step.JournalDay(0, NOTES_A, None)])
    s.set_deleted(conn, sid, T0)
    assert s.purge_deleted(conn, T0 + DAY, 10) == 1
    assert journal.days(conn, sid) == []
