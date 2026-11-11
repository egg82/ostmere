"""The records modules (db/accounts.py, db/saves.py, db/tries.py) against a migrated database of the test's own."""
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Connection, Engine, FromClause, func, select
from sqlalchemy.exc import OperationalError

from ashfall_app.db import accounts as a
from ashfall_app.db import saves as s
from ashfall_app.db import step
from ashfall_app.db import tries as t
from ashfall_app.db.engine import open_database
from ashfall_app.db.tables import accounts, save_lines, saves, sessions

T0 = datetime(2026, 10, 1, 12, tzinfo=UTC)
DAY = timedelta(days=1)


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


@pytest.fixture
def conn(engine: Engine) -> Iterator[Connection]:
    with engine.begin() as c:
        yield c


def written(decisions: int = 0, state: str = "{}", release: int = 1) -> s.Written:
    return s.Written(state=state, format=4, rules_digest="d", decisions=decisions, game_time=0, ended_at=None,
                     build="b", release=release, camp_level=0)


def rows(conn: Connection, table: FromClause) -> int:
    return int(conn.execute(select(func.count()).select_from(table)).scalar_one())


def test_a_session_is_found_by_its_hash_only_while_alive(conn: Connection):
    acc = a.create_account(conn, T0)
    a.insert_session(conn, acc, b"h1", T0)
    found = a.session_by_hash(conn, b"h1", T0 - DAY)
    assert found is not None and found.account_id == acc and found.last_seen_at == T0
    assert a.session_by_hash(conn, b"h1", T0 + timedelta(seconds=1)) is None   # last used before the cutoff
    assert a.session_by_hash(conn, b"h2", T0 - DAY) is None


def test_touch_moves_the_session_and_its_account(conn: Connection):
    acc = a.create_account(conn, T0)
    a.insert_session(conn, acc, b"h", T0)
    found = a.session_by_hash(conn, b"h", T0 - DAY)
    assert found is not None
    a.touch(conn, found, T0 + DAY)
    again = a.session_by_hash(conn, b"h", T0 - DAY)
    record = a.account(conn, acc)
    assert again is not None and again.last_seen_at == T0 + DAY
    assert record is not None and record.last_seen_at == T0 + DAY and record.created_at == T0


def test_keep_newest_sessions_drops_the_longest_unused(conn: Connection):
    acc, other = a.create_account(conn, T0), a.create_account(conn, T0)
    for i in range(5):
        a.insert_session(conn, acc, b"s%d" % i, T0 + i * DAY)
    a.insert_session(conn, other, b"x", T0)
    assert a.keep_newest_sessions(conn, acc, 3) == 2
    assert [a.session_by_hash(conn, b"s%d" % i, T0 - DAY) is not None for i in range(5)] == [False, False, True, True, True]
    assert a.session_by_hash(conn, b"x", T0 - DAY) is not None   # another account's untouched


def test_sessions_unused_since_a_time_are_deleted(conn: Connection):
    acc = a.create_account(conn, T0)
    a.insert_session(conn, acc, b"old", T0)
    a.insert_session(conn, acc, b"new", T0 + 2 * DAY)
    assert a.delete_sessions_unused_since(conn, T0 + DAY) == 1
    assert rows(conn, sessions) == 1


def test_presentation_is_written_as_the_merge_makes_it(conn: Connection):
    acc = a.create_account(conn, T0)
    record = a.account(conn, acc)
    assert record is not None and record.presentation == {}
    assert a.keep_presentation(conn, acc, lambda stored: {**stored, "rule_seen": True}) == ({}, {"rule_seen": True})
    record = a.account(conn, acc)
    assert record is not None and record.presentation == {"rule_seen": True}
    assert a.keep_presentation(conn, acc + 999, lambda stored: stored) is None
    assert a.account(conn, acc + 999) is None


def test_only_empty_accounts_unused_long_enough_are_deleted_with_their_saves(conn: Connection):
    empty_old = a.create_account(conn, T0)
    s.insert_save(conn, empty_old, T0, written(decisions=0))
    a.insert_session(conn, empty_old, b"e", T0)
    played_old = a.create_account(conn, T0)
    s.insert_save(conn, played_old, T0, written(decisions=0))
    s.insert_save(conn, played_old, T0, written(decisions=1))   # one decision is progress
    empty_new = a.create_account(conn, T0 + 40 * DAY)
    assert a.delete_empty_accounts(conn, T0 + 30 * DAY, limit=10) == 1
    assert a.account(conn, empty_old) is None and rows(conn, sessions) == 0
    assert a.account(conn, played_old) is not None and a.account(conn, empty_new) is not None
    assert rows(conn, saves) == 2


def test_empty_accounts_go_in_batches_oldest_first(conn: Connection):
    made = [a.create_account(conn, T0 + i * timedelta(minutes=1)) for i in range(5)]
    assert a.delete_empty_accounts(conn, T0 + 30 * DAY, limit=2) == 2
    assert [a.account(conn, i) is None for i in made] == [True, True, False, False, False]
    assert rows(conn, accounts) == 3


def test_a_save_is_read_back_as_written_and_only_by_its_account(conn: Connection):
    acc, other = a.create_account(conn, T0), a.create_account(conn, T0)
    sid = s.insert_save(conn, acc, T0, written(state="S", release=7))
    got = s.save(conn, sid, acc)
    assert got is not None and (got.state, got.build, got.release, got.started_at) == ("S", "b", 7, T0)
    assert s.save(conn, sid, other) is None and s.save(conn, sid, None) == got
    s.write(conn, sid, T0 + DAY, s.Written(state="S2", format=4, rules_digest="e", decisions=2, game_time=50,
                                            ended_at=40, build="c", release=9, camp_level=2))
    got = s.save(conn, sid, acc, lock=True)
    assert got is not None and (got.state, got.rules_digest, got.decisions, got.game_time, got.ended_at, got.build,
                                got.release, got.updated_at) == ("S2", "e", 2, 50, 40, "c", 9, T0 + DAY)


def test_saves_of_lists_live_saves_most_recently_written_first(conn: Connection):
    acc = a.create_account(conn, T0)
    first = s.insert_save(conn, acc, T0, written())
    second = s.insert_save(conn, acc, T0 + DAY, written())
    assert [x.id for x in s.saves_of(conn, acc)] == [second, first]
    s.write(conn, first, T0 + 2 * DAY, written())
    assert [x.id for x in s.saves_of(conn, acc)] == [first, second]
    conn.execute(saves.update().where(saves.c.id == first).values(deleted_at=T0))
    assert [x.id for x in s.saves_of(conn, acc)] == [second] and s.save(conn, first, acc) is None


def test_kept_saves_reads_every_save_across_batches_deleted_ones_included(conn: Connection):
    acc = a.create_account(conn, T0)
    made = [s.insert_save(conn, acc, T0, written()) for _ in range(5)]
    s.set_deleted(conn, made[1], T0)
    assert [x.id for x in s.kept_saves(conn, batch=2)] == made


def test_lines_number_on_and_the_last_ones_come_oldest_first(conn: Connection):
    acc = a.create_account(conn, T0)
    sid, other = s.insert_save(conn, acc, T0, written()), s.insert_save(conn, acc, T0, written())
    s.append_lines(conn, sid, [(0, "a"), (0, "b")])
    s.append_lines(conn, sid, [])
    s.append_lines(conn, sid, [(5, "c")])
    s.append_lines(conn, other, [(1, "z")])
    assert s.last_lines(conn, sid, 2) == [s.LineRecord(1, 0, "b"), s.LineRecord(2, 5, "c")]
    assert [x.n for x in s.last_lines(conn, sid, 10)] == [0, 1, 2]
    assert s.last_lines(conn, other, 10) == [s.LineRecord(0, 1, "z")]
    assert rows(conn, save_lines) == 4


def decision(n: int) -> s.DecisionRecord:
    return s.DecisionRecord(n=n, at=n * 10, kind="tap_card", verb={"n": n}, rules_digest="d")


def test_decisions_are_logged_in_order_and_pruned_by_wall_time(conn: Connection):
    acc = a.create_account(conn, T0)
    sid = s.insert_save(conn, acc, T0, written())
    for n in range(1, 4):
        step.write_step(conn, sid, T0 + n * DAY, written(decisions=n), [], step.Log(decision(n), T0 - DAY, 1, 0), None)
    assert [d.n for d in s.decisions_after(conn, sid, 1)] == [2, 3]
    assert s.decisions_after(conn, sid, 0)[0] == s.DecisionRecord(1, 10, "tap_card", {"n": 1}, "d")
    step.write_step(conn, sid, T0 + 4 * DAY, written(decisions=4), [], step.Log(decision(4), T0 + 2 * DAY, 1, 0), None)
    assert [d.n for d in s.decisions_after(conn, sid, 0)] == [2, 3, 4]   # wall T0+1d goes; T0+2d (at the limit) stays


def test_one_snapshot_a_day_and_old_days_pruned(conn: Connection):
    acc = a.create_account(conn, T0)
    sid = s.insert_save(conn, acc, T0, written(state="A"))

    def decide(n: int, state: str, day: int, day_from: int) -> None:
        step.write_step(conn, sid, T0, written(decisions=n, state=state), [], step.Log(decision(n), T0, day, day_from), None)

    decide(1, "A", 10, 0)
    decide(2, "B", 10, 0)
    assert s.snapshot(conn, sid, 10) == s.SnapshotRecord(10, "A", "d", 1), "the day's first decision's save, written"
    decide(3, "C", 11, 11)   # a new day's snapshot prunes the days before the one it is given
    assert s.snapshot(conn, sid, 10) is None and s.snapshot(conn, sid, 11) == s.SnapshotRecord(11, "C", "d", 3)
    decide(4, "D", 11, 99)   # a day already snapshotted prunes nothing
    assert s.snapshot(conn, sid, 11) == s.SnapshotRecord(11, "C", "d", 3)


def test_a_step_writes_its_lines_numbered_on_and_reads_the_matching_decisions(conn: Connection):
    acc = a.create_account(conn, T0)
    sid = s.insert_save(conn, acc, T0, written())
    for n in range(1, 4):
        step.write_step(conn, sid, T0, written(decisions=n), [(n, f"k{n}")], step.Log(decision(n), T0 - DAY, 1, 0), None)
    listed, recent = step.write_step(conn, sid, T0, written(decisions=4), [(4, "k4"), (4, "k5")],
                                     step.Log(decision(4), T0 - DAY, 1, 0), {"tap_card": 20})
    assert [x.n for x in s.last_lines(conn, sid, 10)] == [0, 1, 2, 3, 4]
    assert listed.decisions == 4 and [d.n for d in recent] == [2, 3, 4], "the step's own entry among them"
    assert recent[-1] == decision(4)
    assert step.write_step(conn, sid, T0, written(decisions=4), [], None, {"tap_card": 40})[1] == [decision(4)]
    assert step.write_step(conn, sid, T0, written(decisions=4), [], None, None)[1] == []


def test_tries_count_by_kind_and_who_since_a_time_and_trim(conn: Connection):
    t.hold(conn, "account")
    t.add(conn, "account", b"x", T0)
    t.add(conn, "account", b"y", T0 + timedelta(minutes=30))
    t.add(conn, "other", b"x", T0 + timedelta(minutes=30))
    assert t.count(conn, "account", T0) == 2 and t.count(conn, "account", T0, b"x") == 1
    assert t.count(conn, "account", T0 + timedelta(minutes=1)) == 1
    assert t.trim(conn, "account", T0) == 0   # a try at the cutoff is still in its window
    assert t.trim(conn, "account", T0 + timedelta(minutes=1)) == 1
    assert t.count(conn, "account", T0) == 1 and t.count(conn, "other", T0) == 1


def test_hold_makes_a_second_transaction_wait(engine: Engine):
    """Two transactions counting the same kind take turns: the second's lock waits for the first to end."""
    with engine.begin() as first:
        t.hold(first, "account")
        with pytest.raises(OperationalError, match="lock timeout"):
            with engine.begin() as second:
                second.exec_driver_sql("SET LOCAL lock_timeout = '100ms'")
                t.hold(second, "account")
        with engine.begin() as second:
            second.exec_driver_sql("SET LOCAL lock_timeout = '100ms'")
            t.hold(second, "other kind")   # control: another kind does not wait


def test_numbers_count_on_per_account_deleted_saves_included(conn: Connection):
    acc, other = a.create_account(conn, T0), a.create_account(conn, T0)
    first, second = s.insert_save(conn, acc, T0, written()), s.insert_save(conn, acc, T0, written())
    s.set_deleted(conn, second, T0)
    third, theirs = s.insert_save(conn, acc, T0, written()), s.insert_save(conn, other, T0, written())
    got = {i: s.save(conn, i, None) for i in (first, third, theirs)}
    assert [r.number if r else None for r in got.values()] == [1, 3, 1]


def test_a_save_begun_without_a_number_takes_the_next_when_written(conn: Connection):
    acc = a.create_account(conn, T0)
    first, second = s.insert_save(conn, acc, T0, written()), s.insert_save(conn, acc, T0, written())
    conn.execute(saves.update().where(saves.c.id == first).values(number=None))   # as the build before numbers made it
    s.write(conn, first, T0 + DAY, written())
    s.write(conn, second, T0 + DAY, written())
    assert [r.number for r in s.saves_of(conn, acc)] == [2, 3]


def test_deleted_saves_are_held_and_purged_only_past_the_cutoff(conn: Connection):
    acc = a.create_account(conn, T0)
    live, young, old = (s.insert_save(conn, acc, T0, written()) for _ in range(3))
    s.append_lines(conn, old, [(0, "a")])
    s.set_deleted(conn, old, T0)
    s.set_deleted(conn, young, T0 + 10 * DAY)
    assert s.live_count(conn, acc) == 1
    assert [r.id for r in s.deleted_of(conn, acc, T0)] == [young, old]
    assert [r.id for r in s.deleted_of(conn, acc, T0 + DAY)] == [young]
    assert s.deleted_save(conn, old, acc, T0 + DAY) is None and s.deleted_save(conn, live, acc, T0) is None
    assert s.purge_deleted(conn, T0 + 5 * DAY, 20) == 1
    assert {r.id for r in s.kept_saves(conn)} == {live, young}
    assert conn.execute(select(func.count()).select_from(save_lines).where(save_lines.c.save_id == old)).scalar_one() == 0
    s.set_deleted(conn, young, None)
    assert s.live_count(conn, acc) == 2 and s.deleted_of(conn, acc, T0) == []


def test_a_purge_takes_at_most_its_batch(conn: Connection):
    acc = a.create_account(conn, T0)
    made = [s.insert_save(conn, acc, T0, written()) for _ in range(3)]
    for i in made:
        s.set_deleted(conn, i, T0)
    assert s.purge_deleted(conn, T0 + DAY, 2) == 2 and s.purge_deleted(conn, T0 + DAY, 2) == 1
