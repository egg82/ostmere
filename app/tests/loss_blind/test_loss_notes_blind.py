"""LOSS LINES composer (api/contract/, L1-L6), written from the contract alone. The expected key is an oracle that
restates L5 (the hash and the round rule); the counts and order are L2-L4. Mutants: MUTANTS.txt beside this file."""
import hashlib
from collections.abc import Sequence
from dataclasses import replace

from ashfall_app.saves.journal import ComposedDay, Habits, Line, Loss, Note, Source, Subject, compose_day
from tests.saves.journal_fixture import BEAT, HABITS, JOURNAL

SAVE = 7
POOL = ("loss.a", "loss.b", "loss.c")
SUBJECTS = JOURNAL.subjects
FOLD = "ui.journal.fold"


def run(lost_by_day: Sequence[int], pool: tuple[str, ...] = POOL, runner: str = "c_hunt",
        lines_by_day: dict[int, tuple[Line, ...]] | None = None, subjects: tuple[Subject, ...] = SUBJECTS,
        habits: Habits = HABITS) -> list[ComposedDay]:
    """Compose days 0..n-1 in a chain; lost_by_day[d] is the runner's floored tally at day d's end."""
    days: list[ComposedDay] = []
    for d, lost in enumerate(lost_by_day):
        lines = (lines_by_day or {}).get(d, ())
        days.append(compose_day(SAVE, d, lines, tuple(days), subjects, habits, ended=True,
                                losses=(Loss(runner, pool, lost),)))
    return days


def pick(runner: str, pool: tuple[str, ...], before: Sequence[Note]) -> str:
    """The L5 key for a loss note, given every note before it (stored days and page so far, oldest first)."""
    drawn = [n.key for n in before if n.slot != "fold" and n.key in pool]
    size = len(pool)
    r = len(drawn) // size
    used = drawn[r * size:]
    cand = [k for k in pool if k not in used]
    if not used and drawn and size >= 2:
        cand = [k for k in cand if k != drawn[-1]]
    return min(cand, key=lambda k: hashlib.sha256(f"{SAVE}|journal|loss|{runner}|{r}|{k}".encode()).digest())


def loss_notes(day: ComposedDay) -> list[Note]:
    return [n for n in day.notes if n.slot in ("loss", "fold")]


def all_notes(days: Sequence[ComposedDay]) -> list[Note]:
    return [n for d in days for n in d.notes]


def test_one_whole_fight_one_loss_note():
    [d] = run([1])
    assert [(n.subject, n.slot, n.count) for n in d.notes] == [("c_hunt", "loss", None)]
    assert d.notes[0].key == pick("c_hunt", POOL, [])
    assert d.gap is None


def test_several_fights_are_one_loss_and_one_fold_with_the_rest():
    [d] = run([5])
    assert [(n.subject, n.slot, n.count) for n in d.notes] == [("c_hunt", "loss", None), ("c_hunt", "fold", 4)]
    assert d.notes[1].key == FOLD
    assert d.notes[0].key in POOL


def test_two_fights_fold_count_one():
    [d] = run([2])
    assert [(n.slot, n.count) for n in d.notes] == [("loss", None), ("fold", 1)]


def test_nothing_owed_writes_nothing_and_a_loss_only_day_is_written():
    [d] = run([0])
    assert d.notes == () and d.gap is None
    [d1] = run([1])
    assert len(d1.notes) == 1


def test_told_is_loss_notes_plus_fold_counts_over_earlier_days():
    days = run([3, 3, 4, 4, 9])
    assert [[(n.slot, n.count) for n in d.notes] for d in days] == [
        [("loss", None), ("fold", 2)], [], [("loss", None)], [], [("loss", None), ("fold", 4)]]


def test_a_long_absence_is_still_one_note_and_one_fold():
    days = run([0, 0, 40, 40])
    assert [len(d.notes) for d in days] == [0, 0, 2, 0]
    assert days[2].notes[1].count == 39


def test_a_lower_tally_than_told_writes_nothing():
    days = run([4, 2])
    assert days[1].notes == ()


def test_same_arguments_same_day_and_stepwise_composition_keeps_notes():
    a = run([3, 3, 5])
    b = run([3, 3, 5])
    assert a == b
    open_day = compose_day(SAVE, 0, (), (), SUBJECTS, HABITS, ended=False, losses=(Loss("c_hunt", POOL, 3),))
    assert loss_notes(open_day) == []
    closed = compose_day(SAVE, 0, (), (), SUBJECTS, HABITS, ended=True, losses=(Loss("c_hunt", POOL, 3),))
    again = compose_day(SAVE, 0, (), (), SUBJECTS, HABITS, ended=True, losses=(Loss("c_hunt", POOL, 3),))
    assert closed == again == a[0]


def test_a_day_that_broke_off_writes_none_and_the_next_ended_day_carries_them():
    beat_line = (Line("l_beat", 100, BEAT.source),)
    busy = replace(HABITS, busy_ratio=0)
    day0 = compose_day(SAVE, 0, beat_line, (), SUBJECTS, busy, ended=True, losses=(Loss("c_hunt", POOL, 3),))
    assert day0.gap == "busy"
    assert loss_notes(day0) == []
    day1 = compose_day(SAVE, 1, (), (day0,), SUBJECTS, HABITS, ended=True, losses=(Loss("c_hunt", POOL, 3),))
    assert [(n.slot, n.count) for n in loss_notes(day1)] == [("loss", None), ("fold", 2)]
    day2 = compose_day(SAVE, 2, (), (day0, day1), SUBJECTS, HABITS, ended=True, losses=(Loss("c_hunt", POOL, 3),))
    assert day2.notes == ()


def test_loss_notes_follow_the_days_other_notes_which_are_unchanged():
    lines = {0: (Line("l_beat", 100, BEAT.source),)}
    plain = run([0], lines_by_day=lines)[0]
    withl = run([4], lines_by_day=lines)[0]
    assert plain.notes and withl.notes[:len(plain.notes)] == plain.notes
    assert [n.slot for n in withl.notes[len(plain.notes):]] == ["loss", "fold"]
    assert withl.marks == plain.marks
    assert withl.gap == plain.gap


def test_loss_notes_leave_what_comes_after_alone():
    """w(S) and the budget are unchanged: later days' other notes are the same with or without loss notes."""
    lines = {d: (Line("l_beat", d * 86400 + 100, BEAT.source), Line("l_work", d * 86400 + 200, JOURNAL.subjects[1].source))
             for d in range(4)}
    a = run([0, 0, 0, 0], lines_by_day=lines)
    b = run([2, 3, 3, 6], lines_by_day=lines)
    for da, db in zip(a, b):
        assert [n for n in db.notes if n.slot not in ("loss", "fold")] == list(da.notes)


def test_runners_in_id_order_each_with_its_own_pool():
    pool_b = ("m.x", "m.y")
    runners = [Loss("c_zeta", pool_b, 2), Loss("c_alpha", POOL, 3)]
    d = compose_day(SAVE, 0, (), (), SUBJECTS, HABITS, ended=True, losses=tuple(runners))
    assert [(n.subject, n.slot, n.count) for n in d.notes] == [
        ("c_alpha", "loss", None), ("c_alpha", "fold", 2), ("c_zeta", "loss", None), ("c_zeta", "fold", 1)]
    assert d.notes[0].key in POOL and d.notes[2].key in pool_b


def test_keys_are_the_hash_choice_no_key_twice_in_a_row_and_each_round_uses_every_key():
    days = run(list(range(1, 31)))
    notes = [n for n in all_notes(days) if n.slot == "loss"]
    assert len(notes) == 30  # one new whole fight a day: one loss note, no fold
    seen: list[Note] = []
    for n in notes:
        assert n.key == pick("c_hunt", POOL, seen)
        seen.append(n)
    keys = [n.key for n in notes]
    assert all(a != b for a, b in zip(keys, keys[1:]))
    for i in range(0, 30, 3):
        assert sorted(keys[i:i + 3]) == sorted(POOL)


def test_fold_notes_draw_nothing_and_do_not_move_the_bag():
    days = run([3, 5, 9, 10])
    notes = [n for n in all_notes(days) if n.slot == "loss"]
    seen: list[Note] = []
    for n in notes:
        assert n.key == pick("c_hunt", POOL, seen)
        seen.append(n)
    keys = [n.key for n in notes]
    assert sorted(keys[:3]) == sorted(POOL)
    folds = [n for n in all_notes(days) if n.slot == "fold"]
    assert [f.count for f in folds] == [2, 1, 3]
    assert all(f.key == FOLD for f in folds)


def test_a_pool_holding_the_fold_key_ignores_fold_notes_as_draws():
    pool = ("loss.a", FOLD)
    days = run([2, 4, 6, 8], pool=pool)
    seen: list[Note] = []
    for n in all_notes(days):
        if n.slot == "loss":
            assert n.key == pick("c_hunt", pool, seen)
        seen.append(n)


def test_a_trigger_subjects_note_from_the_pool_is_the_first_draw():
    subject = Subject("s_pool", "beat", Source("trigger", "t_pool"), first=("loss.a", "loss.b", "loss.c"))
    lines = {0: (Line("l_pool", 50, subject.source),)}
    days = run([1], lines_by_day=lines, subjects=SUBJECTS + (subject,))
    d = days[0]
    trig = [n for n in d.notes if n.subject == "s_pool"]
    assert len(trig) == 1 and trig[0].key in POOL
    loss = [n for n in d.notes if n.slot == "loss"][0]
    assert d.notes.index(trig[0]) < d.notes.index(loss)
    assert loss.key == pick("c_hunt", POOL, [n for n in d.notes if n is not loss])
    assert loss.key != trig[0].key  # size >= 2 and the pool's one draw so far: no key twice in a row


def test_a_pool_of_one_key_repeats_it():
    days = run([1, 2, 3], pool=("only",))
    assert [n.key for n in all_notes(days)] == ["only", "only", "only"]


def test_the_runner_and_save_move_the_choice():
    keys: set[str] = set()
    for runner in ("c_a", "c_b", "c_c", "c_d", "c_e", "c_f"):
        [d] = run([1], runner=runner)
        assert d.notes[0].key == pick(runner, POOL, [])
        keys.add(d.notes[0].key)
    assert len(keys) > 1
