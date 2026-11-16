"""The journal's rows (db/journal.py, db/step.py): a step's statement stores its days beside its lines, a day still being
written is appended to and never rewritten, a day closed or stored whole is left as stored, the save's locking
statement reads every stored day and the lines asked; it says when its snapshot is older than the row it locked; and
deleting a save for good takes its days with it."""
import threading
import time
from collections.abc import Iterator

import pytest
from sqlalchemy import Connection, Engine, insert

from ashfall_app.db import accounts as a
from ashfall_app.db import journal
from ashfall_app.db import saves as s
from ashfall_app.db import step
from ashfall_app.db.engine import open_database
from ashfall_app.db.tables import save_journal
from tests.db.test_records import DAY, T0, written
from tests.kills import kills
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


def seen(conn: Connection, account: int, sid: int) -> journal.Seen:
    found = journal.locked(conn, sid, account, None, ["k"])
    assert found is not None and found[0].id == sid
    return found[1]


def test_the_locking_read_reads_the_last_lines_asked_oldest_first(conn: Connection):
    account, sid = new_save(conn)
    step.write_step(conn, sid, T0, written(), [(5, "a"), (6, "b"), (7, "c")], None, None, [])
    asked = journal.locked(conn, sid, account, None, ["k"], history=2)
    assert asked is not None and asked[1].history == [s.LineRecord(1, 6, "b"), s.LineRecord(2, 7, "c")]
    assert seen(conn, account, sid).history is None
    assert s.last_lines(conn, sid, 2) == asked[1].history


def test_a_step_stores_its_days_and_the_locking_read_reads_them(conn: Connection):
    account, sid = new_save(conn)
    assert seen(conn, account, sid) == journal.Seen(True, [], [])
    step.write_step(conn, sid, T0, written(), [(5, "k"), (6, "other"), (3 * 86400, "k")], None, None,
                    [step.JournalDay(0, NOTES_A, None, ["soot", "smudge"], 86400),
                     step.JournalDay(1, [], "busy", [], 86400 + 9)])
    stored = [journal.DayRecord(0, [{"subject": "s_a", "slot": "first", "key": "k.a"}], None, ["soot", "smudge"],
                                86400),
              journal.DayRecord(1, [], "busy", [], 86400 + 9)]
    assert journal.days(conn, sid) == stored
    assert seen(conn, account, sid) == journal.Seen(True, stored, [(5, "k"), (3 * 86400, "k")])


def test_a_locking_read_that_waited_on_another_write_says_its_snapshot_is_stale(pg_url: str, engine: Engine):
    with engine.begin() as c:
        account, sid = new_save(c)
    found: list[journal.Seen] = []
    with engine.connect() as writer:
        writer.begin()
        step.write_step(writer, sid, T0, written(decisions=1), [], None, None,
                        [step.JournalDay(0, NOTES_A, None, [], 9)])

        def read() -> None:
            with engine.begin() as c:
                found.append(seen(c, account, sid))
        reader = threading.Thread(target=read)
        reader.start()
        deadline = time.monotonic() + 3
        while lock_waiters(pg_url) < 1 and time.monotonic() < deadline:
            pass
        assert lock_waiters(pg_url) == 1, "the read never waited on the write"
        writer.commit()
    reader.join(3)
    assert [(f.fresh, f.days) for f in found] == [(False, [])]
    with engine.begin() as c:
        assert seen(c, account, sid).fresh


@kills(10)
def test_a_day_closed_or_stored_whole_is_left_as_stored(conn: Connection):
    _, sid = new_save(conn)
    step.write_step(conn, sid, T0, written(), [], None, None, [step.JournalDay(0, NOTES_A, None, [], 86400)])
    conn.execute(insert(save_journal).values(save_id=sid, day=1, notes=NOTES_A, gap=None))
    step.write_step(conn, sid, T0 + DAY, written(decisions=1), [(9, "k")], None, None,
                    [step.JournalDay(0, NOTES_B, None, [], 86400), step.JournalDay(1, NOTES_B, None, [], 2 * 86400),
                     step.JournalDay(2, NOTES_B, None, [], 2 * 86400 + 5)])
    assert [(d.day, [n["key"] for n in d.notes]) for d in journal.days(conn, sid)] == [
        (0, ["k.a"]), (1, ["k.a"]), (2, ["k.b"])]
    assert [ln.key for ln in s.last_lines(conn, sid, 10)] == ["k"], "the step's other writes did not land"


@kills(3)
def test_a_day_still_being_written_is_appended_to_and_never_rewritten(conn: Connection):
    _, sid = new_save(conn)
    for i, add in enumerate([step.JournalDay(0, NOTES_A, None, ["soot"], 100),
                             step.JournalDay(0, NOTES_B, "busy", ["blood"], 200),
                             step.JournalDay(0, [], "away", [], 86400),
                             step.JournalDay(0, NOTES_A, None, ["mud"], 86400)]):
        step.write_step(conn, sid, T0, written(decisions=i), [], None, None, [add])
    assert journal.days(conn, sid) == [journal.DayRecord(0, NOTES_A + NOTES_B, "busy", ["soot", "blood"], 86400)]


def test_lines_of_reads_only_the_keys_asked_before_the_time_asked(conn: Connection):
    _, sid = new_save(conn)
    s.append_lines(conn, sid, [(1, "a"), (2, "b"), (3, "a"), (4, "a")])
    assert journal.lines_of(conn, sid, ["a"], 4) == [(1, "a"), (3, "a")]


def test_a_save_deleted_for_good_takes_its_days(conn: Connection):
    _, sid = new_save(conn)
    step.write_step(conn, sid, T0, written(), [], None, None, [step.JournalDay(0, NOTES_A, None, [], 9)])
    s.set_deleted(conn, sid, T0)
    assert s.purge_deleted(conn, T0 + DAY, 10) == 1
    assert journal.days(conn, sid) == []
