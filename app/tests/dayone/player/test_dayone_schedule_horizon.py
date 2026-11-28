"""A schedule built to a later horizon keeps every visit it had to the earlier one, so a chapter that already lands
inside the earlier horizon plays the same visits; schedules.extended runs one on that way and never shortens it."""
import pytest

from tests.dayone.player.schedules import GAPS_H, HOUR, Schedule, Visit, extended, schedule

ROUTES = (*GAPS_H, "evenings", "lunch", "whenever")
EARLIER, LATER = 30 * 24 * HOUR, 37 * 24 * HOUR


@pytest.mark.parametrize("seed", [0, 1, 7])
@pytest.mark.parametrize("name", ROUTES)
def test_a_route_run_on_keeps_its_visits_and_only_adds_later_ones(name: str, seed: int):
    end_at = 5 * HOUR + 17
    before = schedule(name, end_at, seed, EARLIER)
    after = extended(before, LATER)
    assert after == schedule(name, end_at, seed, LATER)
    assert after.visits[:len(before.visits)] == before.visits
    assert after.visits[-1].start >= LATER > before.visits[-1].start


def test_the_babysitters_one_visit_grows_to_the_later_horizon():
    assert extended(schedule("babysitter", 0, 0, EARLIER), LATER).visits == (Visit(0, LATER),)


def test_a_schedule_is_never_shortened_and_a_hand_made_one_never_changed():
    built = schedule("typical", 0, 0, LATER)
    assert extended(built, EARLIER) is built
    hand = Schedule("hand", (Visit(0, 100),))
    assert extended(hand, LATER) is hand
