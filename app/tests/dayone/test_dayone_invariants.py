"""If a card's panel entry shows every need met, a tap starts it ready: its blocker is None, or names a skill level or
another card's completions, which the panel lists apart from the stores (content_models SkillNeed, StepNeed). Anything
else unmet would be a failed attempt on a card that shows nothing short. Read off every view of the day's plays
(routes.py), unlocked and not at its cap; the blocker ignores the lane, so a busy lane changes nothing here."""
import pytest

from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.player import DayOnePlayer
from tests.dayone.routes import plays
from tests.dayone.sinkchecks import needs_met_blocked

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.mark.parametrize("day_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_a_card_showing_every_need_met_taps_ready(day_route: DayOnePlayer):
    checked, broken = needs_met_blocked(v for _, v in day_route.history)
    assert checked > 0, "no card showed its needs met in any view: the check is blind"
    assert broken[:5] == []
