"""View.goals for a story beat waiting on a store a standing action moves (api/goals/goals.py; contract/goals.txt, "Goals"): the
clock carries the store and its amount when the content states it (GoalDef.count), and nothing else when it does not."""
from dataclasses import replace

from ashfall_app import engine as e
from ashfall_app.api.goals import goal_models as g
from ashfall_app.api.goals.goals import goals
from ashfall_app.rules.goals import GoalDef
from tests.engine.held_impl_world import Q, X, world

HOUR = 3600


def served(count: str | None) -> list[g.Goal]:
    beat = e.TriggerDef(e.TriggerId("beat"), e.AtLeast(e.StoreValue(X), 3 * Q, 3 * Q),
                        e.Outcome(unlocks=(e.Unlock(e.UnlockKind.CHIP, "c"),)))
    r = replace(world(beat), standing=(e.StandingDef(e.ActionId("run"), makes=(e.Flow(X, e.per_hour(1)),)),))
    s = e.new_save(r)
    return goals(s, r, e.view(s, r), {"beat": GoalDef("clock", None, 3 * Q if count else 0, count=count)})


def test_a_stated_clock_serves_the_store_its_amount_and_its_target() -> None:
    (clock,) = served("x")
    assert (clock.kind, clock.store, clock.target, clock.at) == (g.GoalKind.CLOCK, "x", 3 * Q, 3 * HOUR)
    assert clock.value is not None and clock.value.start_value == 0 and clock.value.rate > 0


def test_an_unstated_clock_serves_the_time_alone() -> None:
    (clock,) = served(None)
    assert (clock.store, clock.target, clock.value, clock.at) == (None, 0, None, 3 * HOUR)
