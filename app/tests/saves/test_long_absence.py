"""A long absence costs work in proportion to its instants (engine DESIGN.txt, "INVARIANTS" 1): the newest golden save at
the opening's end, advanced as a returning player's is, counted rather than timed, so a busy runner cannot hide it.
Live saves whose rules flip a mix and a chip every few minutes took minutes of CPU over 30 days, because each instant
built every event of every save a handler made; an instant now builds the full schedule once (schedule.pending finds
the rest at now alone). The events-per-day bound catches the other half of the class: content that lands an event
every few seconds all day (a short card on a ruled lane) makes a 30-day return hundreds of thousands of instants.
The same bound on a save from week one's fifth chapter is tests/weekone/test_weekone_long_absence.py."""
from pathlib import Path

import pytest

from ashfall_app.engine import Rules, Save, rebase
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import load_opening, to_rules
from tests.saves.absence import advanced_counted

GOLDEN = Path(__file__).resolve().parent / "golden"
DAYS = 1
INSTANTS_PER_DAY_MAX = 400
"""The end save runs about 120 instants a game day (its rules and the camp's lane); a short cycle all day is thousands."""
SCHEDULES_PER_INSTANT_MAX = 1.1
"""Full schedules built per instant: one each, and the one advance starts from. Before schedule.pending it was 2.4
here and about five on the slow live saves."""


def _end_save() -> Path:
    newest = max(GOLDEN.glob("f*"), key=lambda d: int(d.name[1:]))
    return next(p for p in sorted(newest.glob("*.json")) if "-end" in p.name)


@pytest.fixture(scope="module")
def opening_rules() -> Rules:
    return to_rules(load_opening())


@pytest.fixture(scope="module")
def end_save(opening_rules: Rules) -> Save:
    return rebase(_end_save().read_text().strip(), opening_rules, engine_renames(load_renames()))


@pytest.fixture(scope="module")
def counts(opening_rules: Rules, end_save: Save) -> dict[str, int]:
    """The day's advance runs once, in setup, under the counters; the tests read what it counted."""
    return advanced_counted(end_save, opening_rules, DAYS)


def test_a_long_absence_resolves_a_real_number_of_instants(counts: dict[str, int]):
    assert counts["instants"] > 50


def test_a_long_absence_builds_one_schedule_an_instant(counts: dict[str, int]):
    assert counts["schedules"] <= SCHEDULES_PER_INSTANT_MAX * counts["instants"], counts


def test_a_long_absence_has_no_event_storm(counts: dict[str, int]):
    assert counts["instants"] <= INSTANTS_PER_DAY_MAX * DAYS, counts
