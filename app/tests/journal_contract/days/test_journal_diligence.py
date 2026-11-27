"""Diligence: `floor + (1 - floor) * 0.5 ** (s / halflife)` from the settledness of `composed`, never the day number,
and the strict write roll against `care * diligence` (statement 11). Care is held at 1 (base 1, fade 1)."""
from dataclasses import replace

from hypothesis import given, strategies as st

from journal_world import (
    PLAIN, QUIET, beat, blanks, compose_next, note, ref_roll, routine, row, shows, slots_of,
)

saves = st.integers(0, 2**40)
R, Q = routine("r", repeat=2), routine("q")
B1, B2 = beat("b1"), beat("b2")


def test_a_product_of_zero_never_passes():
    """Statement 11: with care 0 the product is 0, and `roll < 0` never holds, over many save ids."""
    rows = (row(0, note(R, "first")),)
    for save_id in range(200):
        assert compose_next(save_id, rows, [shows(R, 0), shows(R, 1)], [R], QUIET).notes == ()


def test_a_product_of_one_always_passes():
    """Statement 11: with care 1 and diligence 1 the product is 1, and every roll in [0, 1) passes."""
    rows = (row(0, note(R, "first")),)
    for save_id in range(200):
        assert slots_of(compose_next(save_id, rows, [shows(R, 0), shows(R, 1)], [R], PLAIN), R) == ["repeat"]


@given(save_id=saves)
def test_diligence_halves_each_halflife_of_written_days(save_id: int):
    """Statement 11: two written days and a halflife of one give diligence 0.25 over a floor of 0."""
    rows = (row(0, note(R, "first")), row(1, note(Q, "first")))
    day = compose_next(save_id, rows, [shows(R, 0), shows(Q, 1), shows(R, 2)], [R, Q], replace(PLAIN, floor=0.0))
    assert slots_of(day, R) == (["repeat"] if ref_roll(save_id, 2, "r", "write") < 0.25 else [])


@given(save_id=saves)
def test_diligence_never_falls_below_its_floor(save_id: int):
    """Statement 11: however settled, diligence is at least `floor` (here 0.4 after thirty written days)."""
    rows = (row(0, note(R, "first")), *(row(d, note(Q, "first" if d == 1 else "repeat")) for d in range(1, 30)))
    habits = replace(PLAIN, floor=0.4, halflife=1.0)
    day = compose_next(save_id, rows, [shows(R, 0), shows(R, 30)], [R, Q], habits)
    expected = 0.4 + 0.6 * 0.5**30
    assert slots_of(day, R) == (["repeat"] if ref_roll(save_id, 30, "r", "write") < expected else [])


@given(save_id=saves)
def test_a_written_beat_takes_settledness_back(save_id: int):
    """Statement 11 ("Terms"): `s` is the written days less `beat_refresh` for each beat note (not each day with one):
    two written days and two beat notes at 0.5 each make s = 1, diligence 0.5 at halflife 1 and floor 0."""
    rows = (row(0, note(B1, "first"), note(B2, "first"), note(R, "first")), row(1, note(Q, "first")))
    habits = replace(PLAIN, floor=0.0, beat_refresh=0.5)
    lines = [shows(B1, 0), shows(B2, 0), shows(R, 0), shows(Q, 1), shows(R, 2)]
    day = compose_next(save_id, rows, lines, [R, Q, B1, B2], habits)
    assert slots_of(day, R) == (["repeat"] if ref_roll(save_id, 2, "r", "write") < 0.5 else [])


@given(save_id=saves, blank_days=st.integers(0, 6))
def test_diligence_ignores_the_day_number(save_id: int, blank_days: int):
    """Statements 11 and 12: diligence depends on `composed`, never on `day`: blank days add no settledness, so after
    one written day it is 0.5 however many blank days follow."""
    rows = (row(0, note(R, "first")), *blanks(1, blank_days))
    today = 1 + blank_days
    day = compose_next(save_id, rows, [shows(R, 0), shows(R, today)], [R], replace(PLAIN, floor=0.0))
    assert slots_of(day, R) == (["repeat"] if ref_roll(save_id, today, "r", "write") < 0.5 else [])


@given(save_id=saves)
def test_a_gap_day_adds_no_settledness(save_id: int):
    """Statement 11 ("Terms"): a written day is one with notes; a stored gap has none, so it adds nothing to `s`."""
    rows = (row(0, note(R, "first")), row(1, gap="busy"), row(2, gap="away"))
    day = compose_next(save_id, rows, [shows(R, 0), shows(R, 3)], [R], replace(PLAIN, floor=0.0))
    assert slots_of(day, R) == (["repeat"] if ref_roll(save_id, 3, "r", "write") < 0.5 else [])
