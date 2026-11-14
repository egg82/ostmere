"""Which key of a slot: the n-th note of a subject and slot, n counted over `composed`, completes a round of the
slot's keys before any repeats; a crowd's bands each keep their own round (statement 19)."""
from collections.abc import Sequence
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import ComposedDay
from journal_world import (
    PLAIN, QUIET, beat, compose_next, compose_span, crowd, keys, note, row, shows, worry,
)


def _rounds_complete(drawn: list[str], slot: tuple[str, ...]) -> bool:
    size = len(slot)
    return all(len(set(drawn[i:i + size])) == len(drawn[i:i + size]) for i in range(0, len(drawn), size))


def _drawn(days: Sequence[ComposedDay], subject: str, slot: str) -> list[str]:
    return [n.key for d in days for n in d.notes if n.subject == subject and n.slot == slot]


@given(save_id=st.integers(0, 2**40), size=st.integers(1, 4))
def test_a_slots_keys_take_turns(save_id: int, size: int):
    """Statement 19: a beat shown eleven days running draws its repeat keys in rounds, none repeating within one."""
    b = beat("b", repeat=size)
    days = compose_span(save_id, 11, [shows(b, d) for d in range(11)], [b], QUIET)
    drawn = _drawn(days, "b", "repeat")
    assert len(drawn) == 10 and set(drawn) <= set(b.repeat) and _rounds_complete(drawn, b.repeat)


def test_the_count_is_over_composed_as_stored():
    """Statement 19: two repeat notes already stored (keys 0 and 2 of three) leave key 1 to finish the round."""
    b = beat("b", repeat=3)
    rows = (row(0, note(b, "first")), row(1, note(b, "repeat", 0)), row(2, note(b, "repeat", 2)))
    day = compose_next(4, rows, [shows(b, d) for d in range(4)], [b], QUIET)
    assert [n.key for n in day.notes] == ["b.repeat.1"]


def test_a_single_key_slot_always_draws_it():
    """Statement 19: a round of one key is that key every time."""
    b = beat("b", repeat=1)
    days = compose_span(4, 5, [shows(b, d) for d in range(5)], [b], QUIET)
    assert _drawn(days, "b", "repeat") == ["b.repeat.0"] * 4


def test_each_slot_keeps_its_own_round():
    """Statement 19: rounds are per subject and slot; a catch-up does not advance the repeat slot's round."""
    two = replace(beat("b", repeat=2), catchup=keys("b", "catchup", 2))
    trip = worry("trip", away=1)
    lines = [shows(two, d) for d in (0, 1, 3, 4, 6, 7)] + [shows(trip, d) for d in (2, 5)]
    lines += [shows(two, d, second=1) for d in (2, 5)]
    days = compose_span(4, 8, lines, [two, trip], QUIET)
    assert _rounds_complete(_drawn(days, "b", "repeat"), two.repeat)
    assert sorted(_drawn(days, "b", "catchup")) == ["b.catchup.0", "b.catchup.1"]


def test_two_subjects_rounds_are_apart():
    """Statement 19: one subject's draws do not move another's round."""
    a, b = beat("a", repeat=2), beat("b", repeat=2)
    days = compose_span(4, 7, [shows(s, d) for s in (a, b) for d in range(7)], [a, b], QUIET)
    for s in (a, b):
        drawn = _drawn(days, s.id, "repeat")
        assert len(drawn) == 6 and _rounds_complete(drawn, s.repeat)


@given(save_id=st.integers(0, 2**40))
def test_each_band_keeps_its_own_round(save_id: int):
    """Statement 19: within one band of a crowd's mention slot, keys take turns, counted over that band's notes."""
    c = crowd("c", bands=((1, 2), (3, 3)))
    counts = [1, 1, 3, 1, 4, 2, 3, 1, 5, 1, 3, 3]
    lines = [shows(c, d, f"who.{i}", second=i) for d, n in enumerate(counts) for i in range(n)]
    days = compose_span(save_id, len(counts), lines, [c], PLAIN)
    mentions = _drawn(days, "c", "mention")
    assert len(mentions) == len(counts) - 1
    for band in c.mention:
        drawn = [k for k in mentions if k in band.keys]
        assert drawn and _rounds_complete(drawn, band.keys), band
