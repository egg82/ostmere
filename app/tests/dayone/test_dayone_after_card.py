"""The kept-promise gate covers the time past day one's end card (goals.after_card): its samples run a day on past B3
being seen, the page draws times there, and a time drawn there one second early is caught."""
import pytest

from tests.dayone import goals
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.routes import day

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Probed = tuple[int, list[int], list[tuple[str, str, int]], bool, bool]


@pytest.fixture(scope="module")
def probed() -> Probed:
    """(B3 seen, each sample's time, the times drawn at the last, the first level time kept, the same a second early
    kept), computed in setup: each sample advances the play and forecasts (docs/engineering.md, "Fast from the start")."""
    p = day("typical")
    later = list(goals.after_card(p))
    save, v = later[-1]
    times = goals.drawn(save, v, p.rules)
    level = next((t for t in times if t[0] == "level"), None)
    on_time = level is not None and goals.kept(save, p.rules, v, "level", level[1], level[2])
    early = level is not None and goals.kept(save, p.rules, v, "level", level[1], level[2] - 1)
    return p.seen_at["B3"], [s.time for s, _ in later], times, on_time, early


def test_the_promise_samples_run_a_day_past_the_card(probed: Probed):
    seen, at, times, _, _ = probed
    assert at and all(t > seen for t in at)
    assert at[-1] >= seen + goals.AFTER_CARD_S - goals.AFTER_EVERY_S
    assert any(kind == "level" for kind, _, _ in times), f"no level time drawn a day past the card: {times}"


def test_a_level_time_drawn_a_second_early_past_the_card_is_caught(probed: Probed):
    _, _, _, on_time, early = probed
    assert on_time and not early
