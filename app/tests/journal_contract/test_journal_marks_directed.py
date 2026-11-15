"""Directed tests for plants the blind marks suite left alive (statement 21): a mark takes no place in the budget."""
from dataclasses import replace

from ashfall_app.saves.journal import MarkRates
from journal_world import PLAIN, compose_span, routine, shows

ALL = MarkRates(1.0, 1.0, 1.0, 1.0, 1.0)


def test_a_mark_takes_no_place_in_the_budget():
    """Statement 21: with room for two repeat notes among five routines, one of them marked, the same two are written
    whether or not marks are switched on."""
    plain = [routine(f"r{i}", repeat=2) for i in range(5)]
    lines = [shows(s, d) for s in plain for d in (0, 1)]
    tight = replace(PLAIN, lines_start=2, lines_floor=2)
    bare = compose_span(1, 2, lines, plain, tight)[1]
    assert len(bare.notes) == 2
    kept = bare.notes[0].subject
    subjects = [replace(s, mark="blood") if s.id == kept else s for s in plain]
    marked = compose_span(1, 2, lines, subjects, replace(tight, marks=ALL, marks_most=5))[1]
    assert marked.marks == ("blood",)
    assert marked.notes == bare.notes
