"""Page marks: the kinds of mark a day's page carries, drawn from what the day's notes held, seeded by kind, at most
`marks_most`, in `MARK_KINDS` order (statement 21)."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import MARK_KINDS, ComposedDay, Habits, Line, MarkKind, MarkRates, Subject, compose_day
from journal_gen import History, examples, histories
from journal_world import (
    PLAIN, QUIET, beat, compose_span, find_save, lines_before, ref_roll, routine, shows, slots_of, worry,
)

EVENT_KINDS: tuple[MarkKind, ...] = ("blood", "soot", "water", "mud")
ALL = MarkRates(1.0, 1.0, 1.0, 1.0, 1.0)
SURE = replace(PLAIN, marks=ALL, marks_most=5)
"""Every held kind is drawn and the cap is out of the way."""


def marked(subject: Subject, kind: MarkKind) -> Subject:
    return replace(subject, mark=kind)


def rates(**by_kind: float) -> MarkRates:
    return MarkRates(**by_kind)


def day_marks(subjects: list[Subject], lines: list[Line], habits: Habits, days: int = 1,
              save_id: int = 1) -> tuple[MarkKind, ...]:
    return compose_span(save_id, days, lines, subjects, habits)[-1].marks


# --- held: what the day's notes cause -------------------------------------------------------------------------------


def test_a_marked_subject_written_marks_the_day():
    """Statement 21: a day with a note of a subject whose `mark` is blood holds blood; at rate 1 it is drawn."""
    fight = marked(beat("fight"), "blood")
    assert day_marks([fight], [shows(fight, 0)], SURE) == ("blood",)


def test_a_mark_comes_only_from_a_subject_that_causes_it():
    """Statement 21: a subject with no `mark` holds nothing, and a subject marked soot holds soot and no other kind."""
    plain, fire = beat("plain"), marked(beat("fire"), "soot")
    assert day_marks([plain], [shows(plain, 0)], SURE) == ()
    assert day_marks([plain, fire], [shows(plain, 0), shows(fire, 0)], SURE) == ("soot",)


def test_a_subject_not_written_that_day_holds_nothing():
    """Statement 21: a marked subject that shows but is not written (care 0, not a must) leaves no mark."""
    dig = marked(worry("dig"), "mud")
    other = beat("other")
    days = compose_span(1, 1, [shows(dig, 0), shows(other, 0)], [dig, other], replace(QUIET, marks=ALL, marks_most=5))
    assert slots_of(days[0], dig) == [] and days[0].marks == ()


def test_a_subject_no_longer_in_subjects_holds_nothing():
    """Statement 21: the note must be of a subject in `subjects`; one the content has dropped does not mark the day."""
    gone = marked(beat("gone"), "water")
    stays = beat("stays")
    first = compose_span(1, 1, [shows(gone, 0)], [gone], SURE)
    assert first[0].marks == ("water",)
    day = compose_day(1, 1, lines_before([shows(stays, 1)], 1), first, (stays,), SURE)
    assert day.marks == ()


def test_a_late_addition_does_not_hold_its_subjects_mark():
    """Statement 21: a note by `late` is not one of the notes a kind is held by."""
    lately = marked(routine("lately", late=1), "mud")
    filler = beat("filler", repeat=3)
    habits = replace(SURE, late_rate=1.0)
    days = compose_span(1, 2, [shows(lately, 0), shows(filler, 0), shows(filler, 1)], [lately, filler], habits)
    assert slots_of(days[1], lately) == ["late"]
    assert days[0].marks == ("mud",) and days[1].marks == ()


def test_a_correction_does_not_hold_its_subjects_mark():
    """Statement 21: a note by `correction` is not one of the notes a kind is held by."""
    wrong = marked(routine("wrong", misremember=1), "water")
    habits = replace(SURE, misremember_rate=1.0)
    days = compose_span(1, 2, [shows(wrong, 0)], [wrong], habits)
    assert slots_of(days[0], wrong) == ["misremember"] and slots_of(days[1], wrong) == ["correction"]
    assert days[0].marks == ("water",) and days[1].marks == ()


def test_a_catchup_note_holds_its_subjects_mark():
    """Statement 21: a note by `catchup` is by a slot other than late or correction, so its subject's mark is held."""
    trip, seen = worry("trip", away=1), marked(beat("seen"), "soot")
    days = compose_span(1, 3, [shows(trip, 1), shows(seen, 1)], [trip, seen], replace(SURE, marks=rates(soot=1.0)))
    assert days[1].gap == "away" and slots_of(days[2], seen) == ["catchup"]
    assert days[2].marks == ("soot",)


# --- smudge: the day's own mark --------------------------------------------------------------------------------------


def test_a_catchup_day_holds_smudge():
    """Statement 21: a day with a note by `catchup` holds smudge, whatever the subject's own mark."""
    trip, seen = worry("trip", away=1), beat("seen")
    days = compose_span(1, 3, [shows(trip, 1), shows(seen, 1)], [trip, seen], replace(SURE, marks=rates(smudge=1.0)))
    assert slots_of(days[2], seen) == ["catchup"] and days[2].marks == ("smudge",)


def test_a_day_without_a_catchup_does_not_hold_smudge():
    """Statement 21: smudge needs a catch-up; an ordinary written day, a late day and a correction day have none."""
    quick = routine("quick", late=1, misremember=1)
    filler = beat("filler", repeat=3)
    habits = replace(SURE, late_rate=1.0, misremember_rate=1.0, marks=rates(smudge=1.0))
    days = compose_span(1, 3, [shows(quick, 0)] + [shows(filler, d) for d in range(3)], [quick, filler], habits)
    assert [d.notes != () for d in days] == [True] * 3
    assert all(d.marks == () for d in days)


def test_smudge_is_held_by_the_catchup_not_by_the_subject_marks():
    """Statement 21: the smudge rate alone governs smudge; a catch-up day with other rates at 0 holds only smudge."""
    trip, seen = worry("trip", away=1), marked(beat("seen"), "mud")
    habits = replace(SURE, marks=rates(smudge=1.0))
    days = compose_span(1, 3, [shows(trip, 1), shows(seen, 1)], [trip, seen], habits)
    assert days[2].marks == ("smudge",)


# --- drawn: the roll and the rate ------------------------------------------------------------------------------------


@given(save_id=st.integers(0, 2**40), rate=st.sampled_from([0.25, 0.5, 0.75]))
def test_a_held_kind_is_drawn_by_its_own_roll(save_id: int, rate: float):
    """Statement 21: kind K held on day d is drawn exactly when `roll(save_id, d, K, "mark") < rate`; the roll is
    keyed by the kind, not by the subject's id, and by the day."""
    fight = marked(beat("fight", repeat=3), "blood")
    habits = replace(PLAIN, marks=rates(blood=rate), marks_most=5)
    days = compose_span(save_id, 5, [shows(fight, d) for d in range(5)], [fight], habits)
    for d, day in enumerate(days):
        assert day.marks == (("blood",) if ref_roll(save_id, d, "blood", "mark") < rate else ()), d


@given(save_id=st.integers(0, 2**40), rate=st.sampled_from([0.25, 0.5, 0.75]))
def test_smudge_is_drawn_by_its_own_roll(save_id: int, rate: float):
    """Statement 21: smudge is drawn exactly when `roll(save_id, d, "smudge", "mark") < smudge`, d the catch-up day."""
    trip, seen = worry("trip", away=1), beat("seen")
    habits = replace(PLAIN, marks=rates(smudge=rate), marks_most=5)
    days = compose_span(save_id, 3, [shows(trip, 1), shows(seen, 1)], [trip, seen], habits)
    assert days[2].marks == (("smudge",) if ref_roll(save_id, 2, "smudge", "mark") < rate else ())


def test_a_rate_of_zero_never_draws_and_a_rate_of_one_always_does():
    """Statement 21: the draw is strict, so a rate of 0 never passes and a rate of 1 always does."""
    fight = marked(beat("fight"), "blood")
    for save_id in range(60):
        zero = replace(PLAIN, marks=rates(blood=0.0), marks_most=5)
        one = replace(PLAIN, marks=rates(blood=1.0), marks_most=5)
        assert day_marks([fight], [shows(fight, 0)], zero, save_id=save_id) == ()
        assert day_marks([fight], [shows(fight, 0)], one, save_id=save_id) == ("blood",)


def test_a_kinds_rate_is_its_own():
    """Statement 21: each kind is compared with its own rate (`getattr(habits.marks, kind)`), not another kind's."""
    subs = [marked(beat(k), k) for k in EVENT_KINDS]
    lines = [shows(s, 0) for s in subs]
    for kind in EVENT_KINDS:
        habits = replace(PLAIN, marks=rates(**{kind: 1.0}), marks_most=5)
        assert day_marks(subs, lines, habits) == (kind,)


def test_two_subjects_of_one_mark_hold_it_once():
    """Statement 21: each kind at most once, and one roll, however many subjects hold it."""
    a, b = marked(beat("a"), "mud"), marked(beat("b"), "mud")
    assert day_marks([a, b], [shows(a, 0), shows(b, 0)], SURE) == ("mud",)


# --- kept: order and the cap -----------------------------------------------------------------------------------------


def test_marks_run_in_the_order_drawn():
    """Statement 21: marks are in the order the notes holding them were written, and a catch-up holds its subject's mark
    before its smudge."""
    subs = [marked(beat(f"s{i}"), k) for i, k in enumerate(reversed(EVENT_KINDS))]
    lines = [shows(s, 0, second=i) for i, s in enumerate(subs)]
    assert day_marks(subs, lines, SURE) == tuple(reversed(EVENT_KINDS))
    trip, seen = worry("trip", away=1), marked(beat("seen"), "blood")
    days = compose_span(1, 3, [shows(trip, 1), shows(seen, 1)], [trip, seen], SURE)
    assert days[2].marks == ("blood", "smudge")


def test_a_day_keeps_the_first_marks_most_of_its_drawn_kinds():
    """Statement 21: the first `marks_most` kinds drawn, in the order their notes are written, are kept; 0 keeps none."""
    subs = [marked(beat(k), k) for k in EVENT_KINDS]
    lines = [shows(s, 0) for s in subs]
    for most in range(6):
        habits = replace(SURE, marks_most=most)
        assert day_marks(subs, lines, habits) == MARK_KINDS[:min(most, 4)], most


def test_the_cap_cuts_after_the_draw_not_before():
    """Statement 21: the cap takes the first of the kinds *drawn*, so a held kind that fails its roll does not use up a
    place."""
    subs = [marked(beat(k), k) for k in ("blood", "soot", "water")]
    lines = [shows(s, 0) for s in subs]
    save_id = find_save(lambda i: ref_roll(i, 0, "blood", "mark") >= 0.5 > max(
        ref_roll(i, 0, "soot", "mark"), ref_roll(i, 0, "water", "mark")))
    habits = replace(PLAIN, marks=rates(blood=0.5, soot=0.5, water=0.5), marks_most=2)
    assert day_marks(subs, lines, habits, save_id=save_id) == ("soot", "water")


def test_smudge_competes_for_the_cap_in_its_place():
    """Statement 21: smudge is last in `MARK_KINDS`, so it is the first cut when the cap is reached."""
    trip, seen = worry("trip", away=1), marked(beat("seen"), "mud")
    habits = replace(SURE, marks_most=1)
    assert compose_span(1, 3, [shows(trip, 1), shows(seen, 1)], [trip, seen], habits)[2].marks == ("mud",)


# --- days with no page notes -----------------------------------------------------------------------------------------


def test_a_gap_day_has_no_marks():
    """Statement 21: a gap has none, though a marked subject shows on it."""
    trip, seen = worry("trip", away=1), marked(beat("seen"), "blood")
    days = compose_span(1, 2, [shows(trip, 1), shows(seen, 1)], [trip, seen], SURE)
    assert days[1].gap == "away" and days[1].notes == () and days[1].marks == ()


def test_a_blank_day_has_no_marks():
    """Statement 21: a blank day has none, even with every rate at 1."""
    fight = marked(beat("fight"), "blood")
    days = compose_span(1, 2, [shows(fight, 0)], [fight], SURE)
    assert days[1].notes == () and days[1].gap is None and days[1].marks == ()


# --- marks change nothing else ---------------------------------------------------------------------------------------


def test_the_default_habits_carry_no_marks():
    """Statement 21: with no marks rates and `marks_most` 0, a day carries none, whatever its subjects are marked."""
    subs = [marked(beat(k), k) for k in EVENT_KINDS]
    assert day_marks(subs, [shows(s, 0) for s in subs], PLAIN) == ()


@st.composite
def marked_histories(draw: st.DrawFn) -> History:
    """A generated history whose subjects are given marks, with rates and a cap."""
    history = draw(histories(max_days=8))
    pick = st.sampled_from([None, *EVENT_KINDS])
    subjects = tuple(replace(s, mark=draw(pick)) for s in history.subjects)
    unit = st.sampled_from([0.0, 0.3, 0.7, 1.0])
    mark_rates = MarkRates(*(draw(unit) for _ in MARK_KINDS))
    habits = replace(history.habits, marks=mark_rates, marks_most=draw(st.integers(0, 5)))
    return replace(history, subjects=subjects, habits=habits)


def expected_marks(save_id: int, day: int, row: ComposedDay, subjects: tuple[Subject, ...],
                   habits: Habits) -> tuple[MarkKind, ...]:
    """Statement 21 as stated, from the day's notes alone, in the order they were written."""
    by_id = {s.id: s for s in subjects}
    drawn: list[MarkKind] = []
    for n in row.notes:
        if n.slot in ("late", "correction"):
            continue
        mark = by_id[n.subject].mark if n.subject in by_id else None
        kinds: list[MarkKind] = [*([mark] if mark is not None else []), *(["smudge"] if n.slot == "catchup" else [])]
        for k in kinds:
            if (k not in drawn and len(drawn) < habits.marks_most
                    and ref_roll(save_id, day, k, "mark") < getattr(habits.marks, k)):
                drawn.append(k)
    return tuple(drawn)


@examples(30)
@given(h=marked_histories())
def test_every_day_carries_exactly_the_marks_its_notes_draw(h: History):
    """Statement 21, for every history: a day's marks equal those drawn from its own notes as they were written, so each
    is unique, at most `marks_most`, held, drawn, and a day with no notes has none."""
    days = compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)
    for d, row in enumerate(days):
        assert row.marks == expected_marks(h.save_id, d, row, h.subjects, h.habits), d
        assert len(row.marks) <= h.habits.marks_most and len(set(row.marks)) == len(row.marks)


@examples(30)
@given(h=marked_histories())
def test_marks_never_change_the_notes_or_gaps(h: History):
    """Statement 21: with and without marks the days have the same notes in the same order and the same gaps."""
    bare = replace(h.habits, marks=MarkRates(), marks_most=0)
    with_marks = compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)
    without = compose_span(h.save_id, h.days, h.lines, h.subjects, bare)
    assert [(d.day, d.notes, d.gap) for d in with_marks] == [(d.day, d.notes, d.gap) for d in without]
    assert all(d.marks == () for d in without)


@examples(30)
@given(h=marked_histories())
def test_a_day_re_viewed_has_the_same_marks(h: History):
    """Statements 21 and 1: composing the same day again from the same arguments gives the same marks."""
    days = compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)
    again = compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)
    assert [d.marks for d in days] == [d.marks for d in again]
