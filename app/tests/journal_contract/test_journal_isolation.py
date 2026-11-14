"""Isolation: lines feeding no subject change nothing, and a new subject with its own lines moves no other subject's
draws or write rolls (statements 5 and 6), on the fixed mixed history and on generated ones."""
from collections.abc import Sequence
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import (
    DAY_S, ComposedDay, Habits, Line, Source, SourceKind, Subject, Way, compose_day,
)
from journal_gen import History, histories
from journal_mixed import HABITS, SAVE_ID, composed, lines, subjects
from journal_world import OWN_SLOTS, beat, compose_span, lines_before, routine, shows, worry


def _wide(habits: Habits) -> Habits:
    """Budget and busy out of the way, so a subject's notes show which subjects passed (statement 6's caveat)."""
    return replace(habits, lines_start=50, lines_floor=50, busy_ratio=100.0)


OTHER_KIND: dict[SourceKind, SourceKind] = {
    "card": "trigger", "trigger": "card", "lane": "lane", "mentions": "mentions",
}


def _near_misses(subjects: Sequence[Subject]) -> list[Source]:
    """Sources one field away from a subject's: the other kind with its id, its lane or mentions the other way."""
    out: list[Source] = []
    for s in subjects:
        way: Way | None = None if s.source.way is None else ("left" if s.source.way == "joined" else "joined")
        out.append(Source(OTHER_KIND[s.source.kind], s.source.id, way if s.source.kind != "trigger" else None))
    return [x for x in out if x not in {s.source for s in subjects}]


def _noise(days: int, subjects: Sequence[Subject]) -> list[Line]:
    """Lines whose cause feeds no subject: none resolved, an unknown card, and each subject's near misses."""
    out: list[Line] = []
    for d in range(days):
        out += [Line(f"noise.{d}", d * DAY_S + 11, None), Line(f"card.{d}", d * DAY_S + 12, Source("card", "nobody"))]
        out += [Line(f"near.{d}.{i}", d * DAY_S + 13 + i, x) for i, x in enumerate(_near_misses(subjects))]
    return out


def test_lines_feeding_no_subject_change_nothing():
    """Statement 5: adding lines whose source matches no subject leaves every day of the mixed history equal."""
    noisy = compose_span(SAVE_ID, len(composed()), [*lines(), *_noise(len(composed()), subjects())], subjects(), HABITS)
    assert noisy == composed()


@given(history=histories())
def test_noise_never_changes_a_generated_history(history: History):
    """Statement 5 over generated histories: noise added changes no day."""
    plain = compose_span(history.save_id, history.days, history.lines, history.subjects, history.habits)
    more = [*history.lines, *_noise(history.days, history.subjects)]
    noisy = compose_span(history.save_id, history.days, more, history.subjects, history.habits)
    assert noisy == plain


def _others(day: ComposedDay, new_id: str) -> list[tuple[str, str, str]]:
    kept = OWN_SLOTS | {"catchup"}
    return [(n.subject, n.slot, n.key) for n in day.notes if n.subject != new_id and n.slot in kept]


def _with_new(history: History, new: Subject, days: list[int]) -> tuple[tuple[Line, ...], tuple[Subject, ...]]:
    return (*history.lines, *(shows(new, d, second=5) for d in days)), (*history.subjects, new)


def _same_for_others(history: History, new: Subject, new_days: list[int]) -> None:
    """Each day composed from the same stored rows, with and without the new subject and its lines."""
    habits = _wide(history.habits)
    rows = compose_span(history.save_id, history.days, history.lines, history.subjects, habits)
    more_lines, more_subjects = _with_new(history, new, new_days)
    for d in range(history.days):
        with_new = compose_day(history.save_id, d, lines_before(more_lines, d), rows[:d], more_subjects, habits)
        assert _others(with_new, new.id) == _others(rows[d], new.id), d


@given(history=histories(), new_days=st.lists(st.integers(0, 9), max_size=6), kind=st.sampled_from(["b", "r", "w"]))
def test_a_new_subject_moves_no_other_subjects_writing(history: History, new_days: list[int], kind: str):
    """Statement 6: with the same `composed`, a new subject and lines showing only it change no other subject's own
    notes or catch-ups (budget and busy held wide, as the statement allows them to move)."""
    new = {"b": beat("zz_new", repeat=1), "r": routine("zz_new", repeat=2), "w": worry("zz_new")}[kind]
    _same_for_others(history, new, [d for d in new_days if d < history.days])


def test_a_new_subject_moves_nothing_on_the_mixed_history():
    """Statement 6 on the fixed history, with a new subject showing every day."""
    history = History(SAVE_ID, len(composed()), lines(), subjects(), HABITS)
    _same_for_others(history, routine("aa_new", repeat=3), list(range(history.days)))
