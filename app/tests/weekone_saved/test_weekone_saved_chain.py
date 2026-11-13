"""Week one's saved ends (tests/weektwo/ends.py), which day eight plays on from in week two's job, are today's play: each
saved route's week one, as week one's job played and exported it (tests/weekone/test_weekone_export.py), ends where its
saved end says. This is the first link of the saved chain; week two's job checks the rest
(tests/weektwo/test_weektwo_saved.py). Where no export is present the play is made here from the start; under
ASHFALL_REQUIRE_SAVED, which CI sets, a missing export is a failure."""
import os

import pytest

from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone.routes import week1
from tests.weektwo import ends
from tests.weektwo.routes import SAVED, laters, saved_end

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]

HISTORY_PARTS = 4
"""A week's history holds thousands of saves, too many to compare in one test inside a sensible timeout."""


def todays_play(name: str) -> DayTwoPlayer:
    path = ends.exported_path(name)
    if path.exists():
        return ends.load_from(path, laters("week1", name))
    assert not os.environ.get(ends.REQUIRE), f"week one's job left no play of {name} at {path}"
    return week1(name)


@pytest.fixture(scope="module", params=SAVED["week1"])
def week_end(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer, DayTwoPlayer]:
    """The route's play of today and its saved end, loaded in setup."""
    name: str = request.param
    return name, todays_play(name), saved_end("week1", name)


def test_week_ones_saved_end_is_todays_play(week_end: tuple[str, DayTwoPlayer, DayTwoPlayer]):
    name, p, saved = week_end
    stale = ends.differs(p, saved, skip=frozenset({"history"}))
    assert stale == [], f"week one's saved end on {name} is stale: {ends.REWRITE}"


@pytest.mark.parametrize("part", range(HISTORY_PARTS))
def test_week_ones_saved_history_is_todays_play(week_end: tuple[str, DayTwoPlayer, DayTwoPlayer], part: int):
    name, p, saved = week_end
    assert len(p.history) == len(saved.history), f"week one's saved history on {name} is stale: {ends.REWRITE}"
    n = -(-len(p.history) // HISTORY_PARTS)
    span = slice(part * n, (part + 1) * n)
    assert p.history[span] == saved.history[span], f"week one's saved history on {name} is stale: {ends.REWRITE}"
