"""Forward only: `composed` is read as given, never recomposed from the lines, so rows stored under other habits,
subjects or slots count as they stand (statement 20), and composing is the same day by day or in one sitting
(statement 1)."""
from dataclasses import replace

import pytest

from ashfall_app.saves.journal import Fade, Habits, Press
from journal_mixed import HABITS, SAVE_ID, composed, lines, subjects
from journal_world import (
    OWN_SLOTS, PLAIN, QUIET, beat, compose_next, compose_span, lines_before, note, routine, row, shows, slots_of, worry,
)

R, B = routine("r"), beat("b")
FIVE = tuple(routine(f"f{i}") for i in range(5))
HALVING = replace(PLAIN, lines_start=4, lines_floor=1, lines_halflife=1.0)


def test_a_stored_telling_counts_without_its_line():
    """Statement 20: a routine stored as told is told, though no line shows it that day: with no care it is no must."""
    day = compose_next(1, (row(0, note(R, "first")),), [shows(R, 1)], [R], QUIET)
    assert day.notes == ()


def test_a_stored_day_missing_a_must_is_not_recomposed():
    """Statement 20: a stored day without the beat that showed on it leaves the beat untold: it is a first the next day,
    and no catch-up is owed (the stored day is no gap)."""
    day = compose_next(1, (row(0),), [shows(B, 0), shows(B, 1)], [B], QUIET)
    assert slots_of(day, B) == ["first"]


def test_a_stored_gap_owes_its_catchups():
    """Statements 20 and 9: a day stored as busy is a gap, though today's habits would not make it one."""
    day = compose_next(1, (row(0, gap="busy"),), [shows(B, 0)], [B], QUIET)
    assert slots_of(day, B) == ["catchup"]


def test_a_removed_subjects_notes_still_settle_the_journal():
    """Statement 20: a written day whose notes name a subject no longer in `subjects` is still a written day, so the
    budget after it is 3 (s = 1), not 4."""
    rows = (row(0, note("gone", "first"), *(note(f, "first") for f in FIVE)),)
    day = compose_next(1, rows, [shows(f, d) for f in FIVE for d in (0, 1)], FIVE, HALVING)
    assert len(day.notes) == 3


def test_a_stored_key_outside_todays_slot_is_still_a_telling():
    """Statement 20: a telling stored with a key the slot no longer holds counts; with fade 0 the routine has no
    care."""
    rows = (row(0, note(R, "first", key="r.retired")),)
    day = compose_next(1, rows, [shows(R, 0), shows(R, 1)], [R], replace(PLAIN, routine=Fade(1.0, 0.0)))
    assert day.notes == ()


def test_new_habits_apply_from_the_next_day_only():
    """Statement 20: rows composed under the old habits feed the new ones as stored; the new habits decide the days
    after: with no care for worries and crowds none of theirs is told after the change, and with full care one is."""
    before = composed()[:6]
    kinds = {s.id: s.kind for s in subjects()}

    def crowd_or_worry_told(habits: Habits) -> bool:
        after = compose_span(SAVE_ID, 12, lines(), subjects(), habits, composed=before)
        assert after[:6] == before
        return any(kinds[n.subject] in ("worry", "crowd") and n.slot in OWN_SLOTS for d in after[6:] for n in d.notes)

    no_care = replace(HABITS, worry=Press(0.0, 0.0), crowd=Fade(0.0, 0.0))
    full_care = replace(HABITS, worry=Press(1.0, 0.0), crowd=Fade(1.0, 1.0), floor=1.0, lines_start=50,
                        lines_floor=50, busy_ratio=100.0)
    assert not crowd_or_worry_told(no_care) and crowd_or_worry_told(full_care)


def test_day_by_day_equals_one_sitting():
    """Statement 1: composing each day in its own call, as steps do, stores the same rows as one span, and a day
    composed again from the stored rows comes out equal."""
    span = composed()
    for d in range(len(span)):
        again = compose_next(SAVE_ID, span[:d], lines_before(lines(), d), subjects(), HABITS)
        assert again == span[d], d


@pytest.mark.parametrize("beat_refresh", [0.0, 1.0])
def test_a_day_of_only_removed_subjects_notes_is_written_and_takes_nothing_back(beat_refresh: float):
    """Statement 20 and "Terms": a stored day whose notes all name subjects no longer in `subjects` still counts as
    written, and such a note has no kind, so it takes no settledness back even at a beat_refresh of 1: s = 1 and the
    budget is 3 (not 4) of five untold worries passing at care 1."""
    worries = tuple(worry(f"w{i}") for i in range(5))
    rows = (row(0, note("gone", "first"), note("also_gone", "first")),)
    day = compose_next(1, rows, [shows(w, 1) for w in worries], worries, replace(HALVING, beat_refresh=beat_refresh))
    assert len(day.notes) == 3 and {n.slot for n in day.notes} == {"first"}
