"""The rebase route (story.py): the opening's golden ended saves loaded into today's rules after an hour, eight hours
and three days away. Day one's new triggers fire at the load, the story lands in order, and every line it emits is a key
the content has; what the load and the time away open is a readout. The loads run in the fixture's setup."""
from pathlib import Path

import pytest

from ashfall_app.engine import TriggerId
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests import readout_snapshot as rs
from tests.dayone.report import rebase_text
from tests.dayone.story import AWAY, Rebased, ended_saves, rebase_problems, rebased_case
from tests.opening.playthrough import opening, opening_rules

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
CASES = [(p, away) for p in ended_saves() for away in AWAY]


@pytest.fixture(scope="module", params=CASES, ids=lambda c: f"{c[0].stem}-{c[1]}")
def loaded(request: pytest.FixtureRequest) -> Rebased:
    path, away = request.param
    assert isinstance(path, Path) and isinstance(away, str)
    return rebased_case(path, away)


def test_there_are_ended_golden_saves():
    assert len(ended_saves()) >= 3


def test_the_rebased_story_lands_in_order(loaded: Rebased):
    assert rebase_problems(loaded) == []


def test_the_night_falls_at_the_load_and_the_lines_are_the_contents(loaded: Rebased):
    """An ended save already has keeps_going, so the night's trigger fires at the rebase instant; every line from
    the load on is a text key."""
    rules = opening_rules()
    night = [t.id for t in rules.triggers].index(TriggerId("t_night"))
    assert loaded.at_load.fired[night]
    keys = set(opening().text)
    assert {ln.key for ln in (*loaded.load_lines, *loaded.lines)} <= keys


def test_a_planted_out_of_order_story_is_caught(loaded: Rebased):
    """The probe can fail: the same record with B3 landing before H1 is reported."""
    swapped = Rebased(loaded.name, loaded.at_load, loaded.load_lines, loaded.opened_at_load,
                      {**loaded.landed_at, "B3": loaded.at_load.time - 1, "H1": loaded.at_load.time})
    assert rebase_problems(swapped)


def test_the_rebase_readout_is_reported():
    """Last in the file, so every load is the cached one its case already made."""
    rs.check("dayone-rebase", rebase_text())
