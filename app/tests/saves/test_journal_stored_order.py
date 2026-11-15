"""A day stored before the composer ordered notes by their lines reads in page order (statement 18) when opened, its
row untouched and no note added, dropped or redrawn (statement 20)."""
from collections.abc import Callable

from sqlalchemy import Engine, update

from ashfall_app.db.tables import save_journal
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.journal import DAY_S, ComposedDay, Line, Note
from ashfall_app.saves.journal_composer.history import read
from ashfall_app.saves.journal_composer.order import page_order
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.journal_fixture import BEAT, JOURNAL, TIRED, WORK, journaled, store_lines, stored

SUBJECTS = JOURNAL.subjects


def never() -> Callable[[], bool]:
    return lambda: False


def test_a_stored_day_is_read_catch_ups_then_own_by_first_line_then_late_then_corrections():
    lines = [Line("l_tired", 40, TIRED.source), Line("l_beat", DAY_S + 40, BEAT.source),
             Line("l_work", DAY_S + 90, WORK.source), Line("l_work", DAY_S + 95, WORK.source)]
    shown = (Note("s_beat", "correction", "k"), Note("s_work", "first", "k"), Note("s_tired", "late", "k"),
             Note("s_beat", "first", "k"), Note("s_tired", "catchup", "k"), Note("s_beat", "late", "k"))
    got = page_order(ComposedDay(1, shown, None, ("soot",)), (ComposedDay(0, (), "busy"),), read(lines, SUBJECTS),
                     SUBJECTS)
    assert [(n.subject, n.slot) for n in got.notes] == [
        ("s_tired", "catchup"), ("s_beat", "first"), ("s_work", "first"), ("s_beat", "late"), ("s_tired", "late"),
        ("s_beat", "correction")]
    assert sorted(got.notes, key=repr) == sorted(shown, key=repr)
    assert got.day == 1 and got.marks == ("soot",)


def test_a_note_whose_subject_no_longer_shows_keeps_its_place_after_the_placed_ones():
    lines = [Line("l_work", 50, WORK.source)]
    shown = (Note("s_gone", "first", "k"), Note("s_work", "first", "k"))
    got = page_order(ComposedDay(0, shown, None), (), read(lines, SUBJECTS), SUBJECTS)
    assert [n.subject for n in got.notes] == ["s_work", "s_gone"]


def test_opened_reads_a_day_stored_in_the_old_order_in_page_order_and_leaves_its_row(
        engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves = PgSaves(engine, journaled(rs), clock, stop_for=never)
    save_id = saves.create(account)[0].save_id
    store_lines(engine, save_id, ((50, "l_work"), (100, "l_beat")))
    clock.tick(DAY_S + 60)
    saves.open(account, save_id)
    right = stored(engine, save_id)[0]
    assert [n.subject for n in right.notes] == ["s_work", "s_beat"]
    old = [{"subject": n.subject, "slot": n.slot, "key": n.key} for n in reversed(right.notes)]
    with engine.begin() as conn:
        conn.execute(update(save_journal).where(save_journal.c.save_id == save_id, save_journal.c.day == 0)
                     .values(notes=old))
    assert [n.subject for n in stored(engine, save_id)[0].notes] == ["s_beat", "s_work"]
    again = saves.open(account, save_id)
    assert [n.subject for n in again.days[0].notes] == ["s_work", "s_beat"]
    assert [n.subject for n in stored(engine, save_id)[0].notes] == ["s_beat", "s_work"]
