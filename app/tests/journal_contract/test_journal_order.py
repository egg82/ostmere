"""Order on the page: catch-ups (by the earliest line each showed by in its gap run), the day's own notes, musts and
non-musts alike (by the earliest line showing each that day), ties in `at` by id; then late additions and corrections,
each by id (statement 18). A catch-up and a late addition never share a day (one needs the day before a gap, the other
written), so two days cover the four groups."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import Fade
from journal_world import (
    PLAIN, beat, compose_next, compose_span, find_save, note, ref_roll, routine, row, shows,
)

K1, K2 = routine("k1", misremember=1), routine("k2", misremember=1)


def test_catchups_then_own_notes_by_their_lines_then_corrections():
    """Statement 18 on a day after a gap: catch-ups cc (day 2, second 10), cb (day 2, second 40), ca (day 3); then the
    own notes by second, musts and non-musts interleaved and care (n2 at 0.25, the others 0.5 or 1) no help to place;
    then corrections k1, k2."""
    ca, cb, cc = beat("ca"), beat("cb"), beat("cc")
    m1, m2, m3 = beat("m1"), beat("m2"), beat("m3")
    n1, n2, n3 = routine("n1", repeat=2), routine("n2", repeat=2), routine("n3", repeat=2)
    today = 4
    rows = (
        row(0, note(K2, "misremember"), note(K1, "misremember"), *(note(n, "first") for n in (n1, n2, n3))),
        row(1, note(n2, "repeat")), row(2, gap="away"), row(3, gap="away"),
    )
    lines = [shows(s, 0) for s in (K1, K2, n1, n2, n3)] + [shows(n2, 1)]
    lines += [shows(ca, 3), shows(cb, 2, second=40), shows(cc, 2, second=10)]
    at = {m1: 300, m2: 100, m3: 200, n1: 150, n2: 50, n3: 250}
    lines += [shows(s, today, second=sec) for s, sec in at.items()]
    habits = replace(PLAIN, routine=Fade(1.0, 0.5), correct_after_days=today)
    save_id = find_save(lambda sid: max(ref_roll(sid, today, s, "write") for s in ("n1", "n3")) < 0.5
                        and ref_roll(sid, today, "n2", "write") < 0.25)
    subs = (ca, cb, cc, m1, m2, m3, n1, n2, n3, K1, K2)
    day = compose_next(save_id, rows, lines, subs, habits)
    assert [(n.subject, n.slot) for n in day.notes] == [
        ("cc", "catchup"), ("cb", "catchup"), ("ca", "catchup"),
        ("n2", "repeat"), ("m2", "first"), ("n1", "repeat"), ("m3", "first"), ("n3", "repeat"), ("m1", "first"),
        ("k1", "correction"), ("k2", "correction")]


def test_own_notes_by_their_lines_then_late_then_corrections():
    """Statement 18 on a day after a written one: the own notes by second, then late additions by id, then corrections
    by id."""
    lt1, lt2 = routine("lt1", late=1), routine("lt2", late=1)
    n1, n2 = routine("n1"), routine("n2")
    m1, m2, m3 = beat("m1"), beat("m2"), beat("m3")
    subs = (lt2, lt1, K2, K1, n2, n1, m3, m1, m2)
    lines = [shows(s, 0) for s in (lt2, lt1, K2, K1, n2, n1)]
    lines += [shows(m1, 1, second=40), shows(n2, 1, second=30), shows(m3, 1, second=20), shows(n1, 1, second=10),
              shows(m2, 1, second=50)]
    habits = replace(PLAIN, late_rate=1.0, misremember_rate=1.0, correct_after_days=1)
    days = compose_span(11, 2, lines, subs, habits)
    assert [(n.subject, n.slot) for n in days[1].notes] == [
        ("n1", "repeat"), ("m3", "first"), ("n2", "repeat"), ("m1", "first"), ("m2", "first"),
        ("lt1", "late"), ("lt2", "late"), ("k1", "correction"), ("k2", "correction")]


@given(save_id=st.integers(0, 2**40), seconds=st.permutations(range(0, 5000, 1000)))
def test_own_notes_follow_their_lines_whatever_the_rolls(save_id: int, seconds: list[int]):
    """Statement 18: the day's own notes run by the second of their lines, not by id, `subjects`' order or the order
    roll."""
    subs = tuple(beat(f"b{i}") for i in range(5))
    (day,) = compose_span(save_id, 1, [shows(s, 0, second=sec) for s, sec in zip(subs, seconds)], subs, PLAIN)
    by_line = [s.id for _, s in sorted(zip(seconds, subs, strict=True), key=lambda p: p[0])]
    assert [n.subject for n in day.notes] == by_line


def test_care_never_decides_the_place():
    """Statement 18: a note of care 1 (a fresh change) whose line came later stands after one of care 0.5."""
    hi, lo = routine("hi"), routine("lo")
    habits = replace(PLAIN, routine=Fade(1.0, 0.5))
    rows = (row(0, note(hi, "first"), note(lo, "first")),)
    save_id = find_save(lambda sid: ref_roll(sid, 1, "lo", "write") < 0.5)
    lines = [shows(hi, 0), shows(lo, 0), shows(hi, 1, "hi.new", second=50), shows(lo, 1, second=10)]
    day = compose_next(save_id, rows, lines, (hi, lo), habits)
    assert [n.subject for n in day.notes] == ["lo", "hi"]


def test_a_subject_stands_by_its_earliest_line_of_the_day():
    """Statement 18: a's lines at seconds 90 and 10 (given latest first) put it before b at 50: lines run by their
    second, whatever the order given."""
    a, b = beat("a"), beat("b")
    lines = [shows(a, 0, "a.late", second=90), shows(b, 0, second=50), shows(a, 0, second=10)]
    (day,) = compose_span(1, 1, lines, (b, a), PLAIN)
    assert [n.subject for n in day.notes] == ["a", "b"]


def test_ties_in_the_second_go_in_the_order_stored():
    """Statement 18: three notes whose lines share one second run in the order the lines were stored, not by id."""
    subs = (beat("z"), beat("a"), beat("m"))
    (day,) = compose_span(1, 1, [shows(s, 0, second=7) for s in subs], subs, PLAIN)
    assert [n.subject for n in day.notes] == ["z", "a", "m"]


def test_catchups_by_their_earliest_line_in_the_gap_run():
    """Statement 18: catch-ups run by the earliest line each showed by in the run, ties by id: trip (day 1, second 0),
    z (day 1, second 5; again on day 3), m (day 3, second 2), then a and b (day 3, second 9)."""
    z, a, b, m = beat("z"), beat("a"), beat("b"), beat("m")
    trip = beat("trip", away=3)
    lines = [shows(trip, 1), shows(z, 1, second=5), shows(z, 3), shows(m, 3, second=2), shows(b, 3, second=9),
             shows(a, 3, second=9)]
    days = compose_span(1, 5, lines, [trip, z, a, b, m], PLAIN)
    assert [d.gap for d in days[1:4]] == ["away"] * 3
    assert [(n.subject, n.slot) for n in days[4].notes] == [
        ("trip", "catchup"), ("z", "catchup"), ("m", "catchup"), ("a", "catchup"), ("b", "catchup")]
