"""A step stores the journal days it closes (docs/design/journal.md, "What it reads, and when it writes"): one
save_journal row per game day the save passed the end of, written or not, equal to what the composer makes of the
lines before that day's end; composing a day at a time or a span in one step stores the same rows; two steps racing on
one save store each day once; and rows once stored are never rewritten, whatever the habits become."""
import threading
import time
from collections.abc import Callable
from dataclasses import replace

import psycopg
from sqlalchemy import Engine

from ashfall_app.db import accounts
from ashfall_app.db.engine import open_database
from ashfall_app.db.migrate import migrate
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.journal import DAY_S, ComposedDay
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.journal_fixture import (
    HABITS, JOURNAL, WORK, journaled, lock_waiters, reference, store_lines, stored,
)


def never() -> Callable[[], bool]:
    return lambda: False


def begun(engine: Engine, rs: Ruleset, clock: FakeClock, account: int) -> tuple[PgSaves, int]:
    saves = PgSaves(engine, journaled(rs), clock, stop_for=never)
    info, _ = saves.create(account)
    store_lines(engine, info.save_id)
    return saves, info.save_id


def test_a_step_stores_every_day_it_closes_and_no_later_one(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                             account: int):
    saves, save_id = begun(engine, rs, clock, account)
    clock.tick(3 * DAY_S + 3600)
    played = saves.advance(account, save_id)
    assert stored(engine, save_id) == reference(engine, save_id, 3)
    assert [d.day for d in played.days] == [0, 1, 2] and list(played.days) == stored(engine, save_id)
    assert "s_tired" in {n.subject for n in played.days[0].notes}, "the step's own line did not show its subject"
    clock.tick(DAY_S - 7200)
    assert saves.advance(account, save_id).days == ()
    assert len(stored(engine, save_id)) == 3


def test_a_day_ends_at_its_last_second(engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves, save_id = begun(engine, rs, clock, account)
    clock.tick(DAY_S - 1)
    assert saves.advance(account, save_id).days == ()
    clock.tick(1)
    assert [d.day for d in saves.advance(account, save_id).days] == [0]


def test_day_by_day_and_one_jump_store_the_same_rows(pg_url: str, pg_empty: str, rs: Ruleset):
    """Two databases, so the two saves share an id: every roll is keyed by it."""
    migrate(pg_empty)
    found: list[tuple[int, list[ComposedDay]]] = []
    for url, steps in ((pg_url, [DAY_S] * 6 + [3600]), (pg_empty, [6 * DAY_S + 3600])):
        database = open_database(url, max_size=2)
        try:
            clock = FakeClock()
            with database.engine.begin() as conn:
                account = accounts.create_account(conn, clock())
            saves, save_id = begun(database.engine, rs, clock, account)
            for s in steps:
                clock.tick(s)
                saves.advance(account, save_id)
            found.append((save_id, stored(database.engine, save_id)))
        finally:
            database.close()
    assert found[0][0] == found[1][0]
    assert found[0][1] == found[1][1] and len(found[0][1]) == 6


def test_opened_carries_the_written_days_stored_before_it_and_its_step_those_it_composed(
        engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    """Day 1 has no line and is blank: stored, and not carried."""
    saves = PgSaves(engine, journaled(rs), clock, stop_for=never)
    save_id = saves.create(account)[0].save_id
    store_lines(engine, save_id, ((100, "l_beat"), (2 * DAY_S + 10, "l_beat"), (3 * DAY_S + 10, "l_beat")))
    clock.tick(3 * DAY_S + 60)
    first = saves.open(account, save_id)
    assert first.days == () and [d.day for d in first.played.days] == [0, 1, 2]
    clock.tick(DAY_S)
    again = saves.open(account, save_id)
    assert [d.day for d in again.days] == [0, 2] and list(again.days) == [stored(engine, save_id)[i] for i in (0, 2)]
    assert [d.day for d in again.played.days] == [3]


def test_a_habits_or_slots_change_leaves_every_stored_row_as_it_was(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                                    account: int):
    saves, save_id = begun(engine, rs, clock, account)
    clock.tick(3 * DAY_S + 60)
    saves.advance(account, save_id)
    before = stored(engine, save_id)
    work = replace(WORK, first=("j.work_new",), repeat=("j.work_new_a",))
    tuned = replace(JOURNAL, habits=replace(HABITS, lines_start=1, lines_floor=1),
                    subjects=tuple(work if s == WORK else s for s in JOURNAL.subjects))
    later = PgSaves(engine, journaled(rs, tuned), clock, stop_for=never)
    clock.tick(2 * DAY_S)
    played = later.advance(account, save_id)
    after = stored(engine, save_id)
    assert after[:3] == before and [d.day for d in played.days] == [3, 4]
    assert after[3:] == reference(engine, save_id, 5, tuned)[3:] != reference(engine, save_id, 5)[3:]


def test_a_line_stored_under_a_key_renamed_since_feeds_the_subject_of_its_new_key(
        engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves = PgSaves(engine, journaled(replace(rs, line_renames={"l_old_work": "l_work"})), clock, stop_for=never)
    save_id = saves.create(account)[0].save_id
    store_lines(engine, save_id, ((DAY_S + 5, "l_old_work"),))
    clock.tick(2 * DAY_S)
    played = saves.advance(account, save_id)
    assert [n.subject for n in played.days[1].notes] == ["s_work"]


def test_two_steps_racing_on_one_save_store_each_day_once(pg_url: str, engine: Engine, rs: Ruleset,
                                                          clock: FakeClock, account: int):
    """Both steps wait on a third transaction holding the save's row, so the second to run reads the save after the
    first committed it, from a statement begun before that commit."""
    saves, save_id = begun(engine, rs, clock, account)
    clock.tick(4 * DAY_S + 60)
    results: list[Played] = []
    errors: list[Exception] = []

    def step() -> None:
        try:
            results.append(saves.advance(account, save_id))
        except Exception as ex:
            errors.append(ex)

    with psycopg.connect(pg_url) as holder:
        holder.execute("SELECT 1 FROM saves WHERE id = %s FOR UPDATE", (save_id,))
        threads = [threading.Thread(target=step) for _ in range(2)]
        for t in threads:
            t.start()
        deadline = time.monotonic() + 3
        while lock_waiters(pg_url) < 2 and time.monotonic() < deadline:
            pass
        assert lock_waiters(pg_url) == 2, "the two steps never both waited on the save's row"
        holder.commit()
    for t in threads:
        t.join(3)
    assert errors == []
    assert stored(engine, save_id) == reference(engine, save_id, 4)
    assert sorted(d.day for r in results for d in r.days) == [0, 1, 2, 3]
