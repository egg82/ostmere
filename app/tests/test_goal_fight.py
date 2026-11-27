"""View.goals for a story beat waiting on a card fight's lost tally (api/goals.py; contract/goals.txt, "Goals"): the goal names
the fight's card and states the tally, in play once the card is, at the lowest target of the beats waiting on it."""
from dataclasses import replace

from ashfall_app import engine as e
from ashfall_app.api import goal_models as g
from ashfall_app.api.goals import goals
from ashfall_app.opening.goals import GoalDef
from tests.engine.held_impl_world import HUNT, LOST, Q, world


def served(waits: dict[str, int], lost: int = 1, card_in_play: bool = True) -> list[g.Goal]:
    """The goals with one beat per `waits` entry (trigger id to the fights it waits on), `lost` fights already lost."""
    beats = tuple(e.TriggerDef(e.TriggerId(t), e.AtLeast(e.StoreValue(LOST), n * Q, n * Q),
                               e.Outcome(unlocks=(e.Unlock(e.UnlockKind.CHIP, "c"),))) for t, n in waits.items())
    r = world(*beats)
    r = replace(r, stores=tuple(replace(s, initial=lost * Q) if s.id == LOST else s for s in r.stores))
    if not card_in_play:
        r = replace(r, cards=tuple(c for c in r.cards if c.id != HUNT))
    s = e.new_save(r)
    defs = {t: GoalDef("fight", str(HUNT), n * Q, tally=str(LOST)) for t, n in waits.items()}
    return goals(s, r, e.view(s, r), defs)


def test_the_fights_card_and_its_tally_are_served_at_the_lowest_target() -> None:
    out = served({"far": 5, "near": 3}, lost=2)
    assert [(x.kind, x.card, x.store, x.target) for x in out] == [(g.GoalKind.FIGHT, "hunt", "lost", 3 * Q)]
    assert out[0].value is not None and out[0].value.start_value == 2 * Q


def test_a_card_not_in_play_serves_nothing() -> None:
    assert served({"near": 3}, card_in_play=False) == []
