"""Care: a routine's or crowd's `base * fade ** w`, `w` reset by a change, and a worry's growth over consecutive days,
capped at 1 (statement 10). Diligence is held at 1 (floor 1), so a non-must passes exactly when its write roll is
under its care; the stated expectations use `ref_roll`."""
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from ashfall_app.saves.journal import DAY_S, Fade, Line, Press
from journal_world import (
    PLAIN, compose_next, crowd, note, ref_roll, routine, row, shows, slots_of, worry,
)

saves = st.integers(0, 2**40)
R = routine("r", repeat=3)


@pytest.mark.parametrize("w", [1, 2, 3])
@given(save_id=saves)
def test_a_routines_care_fades_with_each_telling(w: int, save_id: int):
    """Statement 10: a told routine passes when its roll is under `base * fade ** w`, `w` its tellings in `composed`."""
    habits = replace(PLAIN, routine=Fade(0.9, 0.5))
    rows = tuple(row(d, note(R, "first" if d == 0 else "repeat", d - 1 if d else 0)) for d in range(w))
    day = compose_next(save_id, rows, [shows(R, d) for d in range(w + 1)], [R], habits)
    written = ref_roll(save_id, w, "r", "write") < 0.9 * 0.5**w
    assert slots_of(day, R) == (["repeat"] if written else [])


@given(save_id=saves)
def test_w_counts_tellings_not_showings(save_id: int):
    """Statement 10 ("Terms"): `w` is the subject's tellings in `composed`; days it showed untold, and its late and
    correction notes, are not tellings, so here w = 1 though it showed on four days before."""
    m = routine("m", repeat=3, late=1, misremember=1)
    habits = replace(PLAIN, routine=Fade(0.9, 0.5), correct_after_days=2)
    rows = (row(0, note(m, "misremember")), row(1, note(m, "late")), row(2, note(m, "correction")), row(3))
    day = compose_next(save_id, rows, [shows(m, d) for d in range(5)], [m], habits)
    written = ref_roll(save_id, 4, "m", "write") < 0.9 * 0.5
    assert slots_of(day, m) == (["repeat"] if written else [])


def test_a_new_key_is_a_change_and_care_starts_over():
    """Statement 10: on a day one of its lines has a key no line before the day held, `w` counts as 0, so a routine
    faded to no care is written again (by `repeat`: it is still told); the next day the key is old and it is not."""
    habits = replace(PLAIN, routine=Fade(1.0, 0.0))
    rows = (row(0, note(R, "first")), row(1, note(R, "repeat")))
    lines = [shows(R, 0), shows(R, 1), shows(R, 2), shows(R, 2, "r.broke", second=9)]
    changed = compose_next(5, rows, lines, [R], habits)
    assert slots_of(changed, R) == ["repeat"]
    after = compose_next(5, (*rows, changed), [*lines, shows(R, 3, "r.broke")], [R], habits)
    assert after.notes == ()


def test_no_change_when_the_key_was_held_before_today():
    """Statement 10: a key held by any earlier line of the subject is no change, however long ago."""
    habits = replace(PLAIN, routine=Fade(1.0, 0.0))
    rows = (row(0, note(R, "first")), row(1), row(2))
    lines = [shows(R, 0, "r.old"), shows(R, 3, "r.old")]
    assert compose_next(5, rows, lines, [R], habits).notes == ()


def test_a_crowds_care_fades_and_a_new_face_is_a_change():
    """Statement 10: a crowd's care is its kind's `base * fade ** w`; with fade 0 a told crowd is not written again
    until a line brings a key no line held before."""
    c = crowd("c", bands=((1, 2),))
    habits = replace(PLAIN, crowd=Fade(1.0, 0.0))
    rows = (row(0, note(c, "first")),)
    same = compose_next(5, rows, [shows(c, 0, "who.a"), shows(c, 1, "who.a")], [c], habits)
    assert same.notes == ()
    new = compose_next(5, rows, [shows(c, 0, "who.a"), shows(c, 1, "who.b")], [c], habits)
    assert slots_of(new, c) == ["mention"]


@given(save_id=saves, days_in_a_row=st.integers(1, 4))
def test_a_worry_grows_with_each_day_in_a_row(save_id: int, days_in_a_row: int):
    """Statement 10: a worry's care is `min(1, base * (1 + press * (r - 1)))`, `r` the consecutive days ending today on
    which it showed; a day without it breaks the run."""
    w = worry("w", repeat=2)
    habits = replace(PLAIN, worry=Press(0.2, 0.75))
    today = 6
    rows = (row(0, note(w, "first")), *(row(d) for d in range(1, today)))
    lines = [shows(w, 0)] + [shows(w, d) for d in range(today - days_in_a_row + 1, today + 1)]
    lines += [shows(w, 1)] if days_in_a_row < today - 1 else []
    day = compose_next(save_id, rows, lines, [w], habits)
    care = min(1.0, 0.2 * (1 + 0.75 * (days_in_a_row - 1)))
    assert slots_of(day, w) == (["repeat"] if ref_roll(save_id, today, "w", "write") < care else [])


@given(save_id=saves)
def test_a_worry_long_enough_in_a_row_always_passes(save_id: int):
    """Statement 10: past the cap a worry's care is 1, so it passes every roll."""
    w = worry("w", repeat=2)
    habits = replace(PLAIN, worry=Press(0.5, 1.0))
    rows = (row(0, note(w, "first")), row(1), row(2))
    day = compose_next(save_id, rows, [shows(w, d) for d in range(4)], [w], habits)
    assert slots_of(day, w) == ["repeat"]


@given(save_id=saves)
def test_a_worrys_first_telling_is_by_its_care_too(save_id: int):
    """Statements 7 and 10: an untold worry is no must; on its first day (r = 1) it passes when its roll is under
    `base`, and is written by `first`."""
    w = worry("w")
    day = compose_next(save_id, (), [shows(w, 0)], [w], replace(PLAIN, worry=Press(0.4, 3.0)))
    assert slots_of(day, w) == (["first"] if ref_roll(save_id, 0, "w", "write") < 0.4 else [])


def test_a_key_held_only_by_other_lines_is_still_a_change():
    """Statement 10: a change is a key no line *of that subject* held before the day; the same key held earlier by
    another subject's line, or by a line feeding no subject, does not stop it being news."""
    other = routine("other")
    habits = replace(PLAIN, routine=Fade(1.0, 0.0))
    rows = (row(0, note(R, "first"), note(other, "first")), row(1, note(R, "repeat")))
    lines = [shows(R, 0), shows(other, 0, "shared"), Line("shared", DAY_S + 5, None), shows(R, 1)]
    lines.append(shows(R, 2, "shared"))
    day = compose_next(5, rows, lines, [R, other], habits)
    assert slots_of(day, R) == ["repeat"]
