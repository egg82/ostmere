"""Late additions: drawn under `late_rate` by the day the subject was written, landing only on the next day and only
when that day is written for another reason (statement 16)."""
from dataclasses import replace

from hypothesis import given, strategies as st

from journal_world import (
    QUIET, beat, compose_span, of, ref_roll, routine, shows, slots_of, worry,
)

ALWAYS = replace(QUIET, late_rate=1.0)
LATELY = routine("lately", late=2)
FILLER = beat("filler", repeat=3)
"""A beat with repeats, shown on a day to make it written for another reason."""


def test_a_late_addition_lands_the_next_day_only():
    """Statement 16: written on day 0, a subject with a late slot gets one late note on day 1 and on no other day."""
    lines = [shows(LATELY, 0)] + [shows(FILLER, d) for d in range(4)]
    days = compose_span(1, 4, lines, [LATELY, FILLER], ALWAYS)
    assert [slots_of(d, LATELY) for d in days] == [["first"], ["late"], [], []]
    assert of(days[1], LATELY)[0].key in LATELY.late


def test_a_late_addition_alone_does_not_write_a_day():
    """Statements 16 and 15: with nothing else to write, the next day is blank and the late addition is dropped."""
    days = compose_span(1, 3, [shows(LATELY, 0), shows(FILLER, 2)], [LATELY, FILLER], ALWAYS)
    assert days[1].notes == () and days[1].gap is None
    assert slots_of(days[2], LATELY) == []


def test_a_late_addition_is_dropped_into_a_gap():
    """Statement 16: when the next day is a gap it is not written, so there is no late note then or after."""
    trip = worry("trip", away=1)
    lines = [shows(LATELY, 0), shows(trip, 1)] + [shows(FILLER, d) for d in range(4)]
    days = compose_span(1, 4, lines, [LATELY, FILLER, trip], ALWAYS)
    assert days[1].gap == "away" and all(slots_of(d, LATELY) in ([], ["first"]) for d in days)


def test_a_rate_of_zero_never_adds_late():
    """Statement 16: `roll < 0` never holds."""
    lines = [shows(LATELY, 0)] + [shows(FILLER, d) for d in range(2)]
    for save_id in range(100):
        days = compose_span(save_id, 2, lines, [LATELY, FILLER], replace(QUIET, late_rate=0.0))
        assert slots_of(days[1], LATELY) == []


@given(save_id=st.integers(0, 2**40), first_day=st.integers(0, 4))
def test_the_late_roll_is_drawn_for_the_day_written(save_id: int, first_day: int):
    """Statement 16: the late note follows `roll(save_id, d, subject, "late") < late_rate` with d the day written, not
    the day it lands."""
    lines = [shows(LATELY, first_day)] + [shows(FILLER, d) for d in range(first_day + 2)]
    days = compose_span(save_id, first_day + 2, lines, [LATELY, FILLER], replace(QUIET, late_rate=0.5))
    expected = ref_roll(save_id, first_day, "lately", "late") < 0.5
    assert slots_of(days[first_day + 1], LATELY) == (["late"] if expected else [])


def test_any_writing_but_late_or_correction_draws_a_late():
    """Statement 16: a catch-up, a repeat or a misremembering each count as written; the late note itself does not, so
    a late addition gets no late addition of its own."""
    trip = worry("trip", away=1)
    caught, again = beat("caught", late=1), beat("again", repeat=1, late=1)
    wrong = routine("wrong", late=1, misremember=1)
    habits = replace(ALWAYS, misremember_rate=1.0)
    lines = [shows(again, 0), shows(trip, 1), shows(caught, 1), shows(again, 2), shows(wrong, 2)]
    lines += [shows(FILLER, d) for d in (0, 2, 3, 4)]
    days = compose_span(1, 5, lines, [caught, again, wrong, FILLER, trip], habits)
    assert slots_of(days[2], caught) == ["catchup"] and slots_of(days[3], caught) == ["late"]
    assert slots_of(days[2], again) == ["repeat"] and slots_of(days[2], wrong) == ["misremember"]
    assert slots_of(days[3], again) == ["late"] and slots_of(days[3], wrong) == ["late", "correction"]
    assert all(slots_of(days[4], s) == [] for s in (caught, again, wrong))


def test_a_subject_with_no_late_slot_never_gets_one():
    """Statement 16: only a subject with a non-empty late slot."""
    plain = routine("plain")
    lines = [shows(plain, 0)] + [shows(FILLER, d) for d in range(2)]
    days = compose_span(1, 2, lines, [plain, FILLER], ALWAYS)
    assert all(n.slot != "late" for d in days for n in d.notes)


def test_a_late_addition_sits_beside_that_days_own_note():
    """Statements 16 and 4: a subject written two days running has its own note and the late note of the day before."""
    both = beat("both", repeat=2, late=2)
    days = compose_span(1, 3, [shows(both, d) for d in range(3)], [both], ALWAYS)
    assert slots_of(days[1], both) == ["repeat", "late"] == slots_of(days[2], both)
