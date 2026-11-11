"""The line state lists for any chapter (daythree/lines.py), checked against day two's own (daytwo/lines.py) on the
typical route, the one place both can run: the same screen keys at every view, and the same keys fired and shown."""
import pytest

from tests.daythree import lines
from tests.daytwo import content as c
from tests.daytwo import lines as day_two
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import day2

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def typical() -> DayTwoPlayer:
    return day2("typical")


@pytest.fixture(scope="module")
def found(typical: DayTwoPlayer) -> dict[str, set[str]]:
    return lines.states({"typical": typical}, day_two.day_two_keys(), c.opening2(), {"typical": typical.b3_visit() or 1},
                        {"typical": typical.landed_at["B3"]})


def test_the_chapters_screen_keys_match_day_twos_at_every_view_of_the_play(typical: DayTwoPlayer):
    """The generic reading also names the earlier chapters' lanes (a label of day one's), which the chapter's keys leave out."""
    ours = set(day_two.day_two_keys())
    views = [(s, v) for s, v in typical.history if s.time >= typical.landed_at["B3"]]
    assert views and all(lines.shown(c.opening2(), v, s) & ours == day_two.shown(v, s) & ours for s, v in views)


def test_the_keys_that_fired_or_showed_have_states(found: dict[str, set[str]]):
    assert sum(1 for s in found.values() if s) > 10 and len(found) == len(day_two.day_two_keys())


def test_a_key_the_chapter_never_shows_has_no_state(typical: DayTwoPlayer, found: dict[str, set[str]]):
    """The planted key: one the chapter file does not carry is listed with nothing, beside a real one with states."""
    real = next(k for k, s in found.items() if s)
    out = lines.states({"typical": typical}, (real, "no_such_key"), c.opening2(), {"typical": typical.b3_visit() or 1},
                       {"typical": typical.landed_at["B3"]})
    assert out["no_such_key"] == set() and out[real] == found[real]
