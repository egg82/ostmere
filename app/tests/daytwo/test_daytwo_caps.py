"""The cap_loss verdict (verdicts.py) can fail: the typical route's end on day two's rules alone, where nothing after B4
takes the stores, fails on exactly the untrimmed gathered stores. What each store loses as played and away is the
readout's (report.py, caps.lines_of)."""
import pytest

from tests.daytwo.caps import cap_loss_failing
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
RULES_ALONE = ("damp_wood", "roots", "stones")
"""The typical route's gathered stores losing over half their making away from day two's end on day two's rules alone,
with no chapter after it: what the cap_loss verdict, read on the shipped chapters, would see without day three's sinks."""


@pytest.mark.parametrize("day2_route", [("typical", 0)], indirect=True)
def test_without_the_chapters_after_it_day_twos_end_fails_on_the_untrimmed_gathered_stores(day2_route: DayTwoPlayer):
    """The control that the cap_loss verdict can fail: the same route's end on day two's rules alone, where nothing
    after B4 takes the stores, fails on exactly these stores."""
    assert tuple(cap_loss_failing(day2_route)) == RULES_ALONE
