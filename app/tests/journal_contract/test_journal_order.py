"""Order on the page: catch-ups (by the day each showed, then id), the day's own musts (by order roll), its non-musts
(care descending, ties by order roll), late additions, corrections (each by id) (statement 18). A catch-up and a late
addition never share a day (one needs the day before a gap, the other written), so two days cover the five groups."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import Fade, Note
from journal_world import (
    PLAIN, beat, compose_next, compose_span, find_save, note, ref_roll, routine, row, shows,
)

MUSTS = (beat("m3"), beat("m1"), beat("m2"))
K1, K2 = routine("k1", misremember=1), routine("k2", misremember=1)


def _sorted_by_order(notes: list[Note], save_id: int, day: int) -> bool:
    """Ordered by the order roll, lower first (statement 18)."""
    rolls = [ref_roll(save_id, day, n.subject, "order") for n in notes]
    return rolls == sorted(rolls)


def test_catchups_then_musts_then_non_musts_then_corrections():
    """Statement 18 on a day after a gap: catch-ups [cb, cc shown day 2, by id; ca shown day 3], then the three own
    musts, then non-musts n1 and n3 (care 0.5, by order roll) before n2 (care 0.25), then corrections k1, k2."""
    ca, cb, cc = beat("ca"), beat("cb"), beat("cc")
    n1, n2, n3 = routine("n1", repeat=2), routine("n2", repeat=2), routine("n3", repeat=2)
    today = 4
    rows = (
        row(0, note(K2, "misremember"), note(K1, "misremember"), *(note(n, "first") for n in (n1, n2, n3))),
        row(1, note(n2, "repeat")), row(2, gap="away"), row(3, gap="away"),
    )
    lines = [shows(s, 0) for s in (K1, K2, n1, n2, n3)] + [shows(n2, 1), shows(cc, 2), shows(cb, 2), shows(ca, 3)]
    lines += [shows(s, today) for s in (*MUSTS, n1, n2, n3)]
    habits = replace(PLAIN, routine=Fade(1.0, 0.5), correct_after_days=today)
    save_id = find_save(lambda sid: max(ref_roll(sid, today, s, "write") for s in ("n1", "n3")) < 0.5
                        and ref_roll(sid, today, "n2", "write") < 0.25)
    subs = (ca, cb, cc, *MUSTS, n1, n2, n3, K1, K2)
    day = compose_next(save_id, rows, lines, subs, habits)
    got = [(n.subject, n.slot) for n in day.notes]
    assert got[:3] == [("cb", "catchup"), ("cc", "catchup"), ("ca", "catchup")]
    assert sorted(got[3:6]) == [("m1", "first"), ("m2", "first"), ("m3", "first")]
    assert _sorted_by_order(list(day.notes[3:6]), save_id, today)
    n13 = sorted(("n1", "n3"), key=lambda s: ref_roll(save_id, today, s, "order"))
    assert got[6:9] == [(n13[0], "repeat"), (n13[1], "repeat"), ("n2", "repeat")]
    assert got[9:] == [("k1", "correction"), ("k2", "correction")]


def test_musts_then_non_musts_then_late_then_corrections():
    """Statement 18 on a day after a written one: own musts, non-musts, late additions by id, corrections by id."""
    lt1, lt2 = routine("lt1", late=1), routine("lt2", late=1)
    n1, n2 = routine("n1"), routine("n2")
    subs = (lt2, lt1, K2, K1, n2, n1, *MUSTS)
    lines = [shows(s, 0) for s in (lt2, lt1, K2, K1, n2, n1)] + [shows(s, 1) for s in (*MUSTS, n2, n1)]
    habits = replace(PLAIN, late_rate=1.0, misremember_rate=1.0, correct_after_days=1)
    days = compose_span(11, 2, lines, subs, habits)
    got = [(n.subject, n.slot) for n in days[1].notes]
    assert sorted(got[:3]) == [("m1", "first"), ("m2", "first"), ("m3", "first")]
    assert _sorted_by_order(list(days[1].notes[:3]), 11, 1)
    assert sorted(got[3:5]) == [("n1", "repeat"), ("n2", "repeat")]
    assert got[5:] == [("lt1", "late"), ("lt2", "late"), ("k1", "correction"), ("k2", "correction")]


@given(save_id=st.integers(0, 2**40))
def test_non_musts_by_care_then_order_roll(save_id: int):
    """Statement 18: non-musts of equal care (four told routines at care 1) run by lower order roll first."""
    subs = tuple(routine(f"r{i}") for i in range(4))
    rows = (row(0, *(note(s, "first") for s in subs)),)
    habits = replace(PLAIN, routine=Fade(1.0, 1.0))
    day = compose_next(save_id, rows, [shows(s, d) for s in subs for d in (0, 1)], subs, habits)
    order = sorted(subs, key=lambda s: ref_roll(save_id, 1, s.id, "order"))
    assert [n.subject for n in day.notes] == [s.id for s in order]


@given(save_id=st.integers(0, 2**40))
def test_own_musts_follow_the_order_roll(save_id: int):
    """Statement 18: the day's own musts are ordered by `roll(..., "order")`, lower first, not by id or by `subjects`'
    order."""
    subs = tuple(beat(f"b{i}") for i in range(5))
    (day,) = compose_span(save_id, 1, [shows(s, 0) for s in subs], subs, PLAIN)
    assert len(day.notes) == 5 and _sorted_by_order(list(day.notes), save_id, 0)


def test_care_beats_order_roll():
    """Statement 18: a higher care comes first whatever the order rolls: care 1 (a fresh change) before care 0.5."""
    hi, lo = routine("hi"), routine("lo")
    habits = replace(PLAIN, routine=Fade(1.0, 0.5))
    rows = (row(0, note(hi, "first"), note(lo, "first")),)
    save_id = find_save(lambda sid: ref_roll(sid, 1, "lo", "write") < 0.5
                        and ref_roll(sid, 1, "lo", "order") < ref_roll(sid, 1, "hi", "order"))
    lines = [shows(hi, 0), shows(lo, 0), shows(hi, 1, "hi.new"), shows(lo, 1)]
    day = compose_next(save_id, rows, lines, (lo, hi), habits)
    assert [n.subject for n in day.notes] == ["hi", "lo"]


def test_catchups_by_the_first_gap_day_each_showed_on():
    """Statement 18: catch-ups run by the first day of the gap run each showed on, then id: z showed on days 1 and 3,
    a and m on day 3 only, so z leads (by its last day it would tie with a and m and fall behind them by id)."""
    z, a, m = beat("z"), beat("a"), beat("m")
    trip = beat("trip", away=3)
    lines = [shows(trip, 1), shows(z, 1, second=5), shows(z, 3), shows(m, 3), shows(a, 3, second=9)]
    days = compose_span(1, 5, lines, [trip, z, a, m], PLAIN)
    assert [d.gap for d in days[1:4]] == ["away"] * 3
    assert [(n.subject, n.slot) for n in days[4].notes] == [
        ("trip", "catchup"), ("z", "catchup"), ("a", "catchup"), ("m", "catchup")]
