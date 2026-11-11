"""A long absence on a save past the opening: the first heavy step of week one's fifth chapter on the typical route,
advanced one game day with its instants counted (tests/saves/test_long_absence.py is the opening's end). Rules installed
by then (a store's rule that turns on and off as the store drains) cost an instant a turn, which the opening's end save
does not carry."""
import pytest

pytestmark = pytest.mark.playthrough

INSTANTS_PER_DAY_MAX = 6_500
"""A day away on this save resolves about 5,300 instants; the roots rule at a band of one item made it about 8,400."""


def test_a_day_away_on_a_chapter_five_save_resolves_a_real_number_of_instants(week_absence: dict[str, int]):
    assert week_absence["instants"] > 50


def test_a_day_away_on_a_chapter_five_save_has_no_event_storm(week_absence: dict[str, int]):
    assert week_absence["instants"] <= INSTANTS_PER_DAY_MAX, week_absence
