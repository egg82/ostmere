"""Misremembering: a first telling on its own day written by `misremember` under its rate, never in a catch-up or a
later telling, and exactly one correction on the first written day at least `correct_after_days` later (statement
17)."""
from dataclasses import replace

from hypothesis import given, strategies as st

from journal_world import (
    PLAIN, QUIET, beat, compose_next, compose_span, note, of, ref_roll, routine, row, shows, slots_of, worry,
)

WRONG = routine("wrong", repeat=1, misremember=2)
ALWAYS = replace(QUIET, misremember_rate=1.0, correct_after_days=3)
FILLER = beat("filler", repeat=3)


def test_a_first_telling_is_misremembered_under_its_rate():
    """Statement 17: rate 1 writes the first telling by `misremember`, from that slot, and not by `first`."""
    (day,) = compose_span(1, 1, [shows(WRONG, 0)], [WRONG], ALWAYS)
    assert slots_of(day, WRONG) == ["misremember"] and of(day, WRONG)[0].key in WRONG.misremember


def test_a_rate_of_zero_never_misremembers():
    """Statement 17: `roll < 0` never holds."""
    for save_id in range(100):
        (day,) = compose_span(save_id, 1, [shows(WRONG, 0)], [WRONG], replace(ALWAYS, misremember_rate=0.0))
        assert slots_of(day, WRONG) == ["first"]


@given(save_id=st.integers(0, 2**40), first_day=st.integers(0, 4))
def test_the_misremember_roll_is_drawn_for_the_day(save_id: int, first_day: int):
    """Statement 17: misremembered exactly when `roll(save_id, d, subject, "misremember") < misremember_rate`."""
    habits = replace(ALWAYS, misremember_rate=0.5)
    days = compose_span(save_id, first_day + 1, [shows(WRONG, first_day)], [WRONG], habits)
    expected = ref_roll(save_id, first_day, "wrong", "misremember") < 0.5
    assert slots_of(days[first_day], WRONG) == (["misremember"] if expected else ["first"])


def test_the_correction_follows_once_after_the_wait():
    """Statement 17: one correction, on day 3 for a misremembering on day 0 with a wait of three, among written days."""
    days = compose_span(1, 7, [shows(WRONG, 0)] + [shows(FILLER, d) for d in range(7)], [WRONG, FILLER], ALWAYS)
    assert [d.day for d in days for n in of(d, WRONG) if n.slot == "correction"] == [3]
    assert of(days[3], WRONG)[0].key in WRONG.correction


def test_a_correction_writes_a_day_that_would_be_blank():
    """Statements 17 and 15: the correction is owed, so its day is written though nothing else is."""
    days = compose_span(1, 6, [shows(WRONG, 0)], [WRONG], ALWAYS)
    assert [[n.slot for n in d.notes] for d in days] == [["misremember"], [], [], ["correction"], [], []]


def test_a_correction_due_in_a_gap_waits_for_the_next_written_day():
    """Statement 17: the first written day at least the wait later; days 3 and 4 are away, so day 5."""
    trip = worry("trip", away=2)
    days = compose_span(1, 7, [shows(WRONG, 0), shows(trip, 3)], [WRONG, trip], ALWAYS)
    assert [d.day for d in days for n in d.notes if n.slot == "correction"] == [5]


def test_a_first_telling_in_a_catchup_is_never_misremembered():
    """Statement 17: told for the first time in a catch-up is not on its own day: no misremembering, no correction,
    and later showings are tellings after the first."""
    trip = worry("trip", away=1)
    days = compose_span(1, 7, [shows(trip, 1), shows(WRONG, 1)] + [shows(WRONG, d) for d in (3, 4)], [WRONG, trip],
                        replace(ALWAYS, routine=PLAIN.routine))
    slots = [n.slot for d in days for n in of(d, WRONG)]
    assert slots == ["catchup", "repeat", "repeat"]


def test_only_the_first_telling_is_misremembered():
    """Statement 17: a subject already told is written by `repeat`, whatever the rate."""
    rows = (row(0, note(WRONG, "first")),)
    day = compose_next(1, rows, [shows(WRONG, 0), shows(WRONG, 1)], [WRONG], replace(PLAIN, misremember_rate=1.0))
    assert slots_of(day, WRONG) == ["repeat"]


def test_misremembering_is_a_telling():
    """Statements 17 and 7: after a misremembering the routine is told, so it is no must and no first the next day."""
    days = compose_span(1, 2, [shows(WRONG, 0), shows(WRONG, 1)], [WRONG], replace(ALWAYS, correct_after_days=5))
    assert slots_of(days[0], WRONG) == ["misremember"] and days[1].notes == ()


def test_both_slots_are_needed():
    """Statement 17: a subject missing its correction or misremember slot is told by `first` at any rate."""
    no_correction, no_misremember = replace(WRONG, id="a", correction=()), replace(WRONG, id="b", misremember=())
    no_correction = replace(no_correction, source=routine("a").source)
    no_misremember = replace(no_misremember, source=routine("b").source)
    subs = [no_correction, no_misremember]
    (day,) = compose_span(1, 1, [shows(s, 0) for s in subs], subs, ALWAYS)
    assert slots_of(day, "a") == ["first"] and slots_of(day, "b") == ["first"]


def test_each_misremembering_gets_its_own_correction():
    """Statement 17: two subjects misremembered on different days are each corrected once, on their own due day."""
    other = routine("other", misremember=1)
    days = compose_span(1, 8, [shows(WRONG, 0), shows(other, 2)], [WRONG, other], ALWAYS)
    corrections = [(d.day, n.subject) for d in days for n in d.notes if n.slot == "correction"]
    assert corrections == [(3, "wrong"), (5, "other")]


def test_the_shortest_wait_puts_the_correction_on_the_next_day():
    """Statement 17: `correct_after_days` is at least 1, so with the shortest wait the correction is the next written
    day's note and never beside its misremembering."""
    days = compose_span(1, 3, [shows(WRONG, 0)], [WRONG], replace(ALWAYS, correct_after_days=1))
    assert [[n.slot for n in d.notes] for d in days] == [["misremember"], ["correction"], []]
