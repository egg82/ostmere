"""Day eight's line state list (report.py, `--lines`): its keys are read against the typical route from G2's landing, and
the ones that fired or showed have states. A fight's pool keys are drawn by the page per fight, which the plays never
roll, so they never have a state and are not counted."""
import pytest

from ashfall_app.opening.fight_refs import fights
from ashfall_app.opening.schema import DAY_EIGHT
from tests.daythree import content as c3
from tests.daythree import lines
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone import verdicts as v1
from tests.weektwo import verdicts

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.mark.parametrize("eight_route", ["typical"], indirect=True)
def test_day_eights_keys_have_states_on_the_typical_route(eight_route: tuple[str, DayTwoPlayer]):
    _, p = eight_route
    keys = lines.chapter_keys(DAY_EIGHT)
    o = c3.opening3()
    found = lines.states({"typical": p}, keys, o, {"typical": v1.span(p, verdicts.EIGHT)[0]}, {"typical": p.landed_at["G2"]})
    pools = {k for _, f in fights(o) for k in (*f.won_line_keys, *f.lost_line_keys)}
    counted = [k for k in keys if k not in pools]
    assert len(found) == len(keys) > 0
    assert sum(1 for k in counted if found[k]) > len(counted) // 4, "too few of day eight's keys showed or fired"
