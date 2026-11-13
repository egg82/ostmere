"""Invariant 160 and invariant 114's codec half (engine DESIGN.txt, "HELD SPEED ...": "Validation", "Codec"):
InvalidRulesError for a HeldSpeed naming HANDS or an undeclared lane, an amount_bp below 1, one lane twice in one runner,
a standing action's WhileRunning naming an undeclared side or one side twice, and a standing action with while_running
whose id is a card's, the message naming the runner id and the side or lane id; rules that declare no while_running on a
standing action keep their digest."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import HANDS, ActionId, CardId, InvalidRulesError, LaneId, Rules, SideId, StandingDef, rules_digest, validate_rules
from held_world import kills
from heldspeed_world import (
    EAT1, EAT2, G, GS, LP, LQ, eater, eaters, held_speed, side_entry, while_running, world,
)

type Edit = Callable[[Rules], Rules]
NOWHERE = LaneId("nowhere")


def card_holds(card: CardId, *entries: object) -> Edit:
    return lambda r: replace(r, cards=tuple(replace(c, **while_running(*entries)) if c.id == card else c for c in r.cards))


def standing_holds(*entries: object, action: ActionId = EAT1, cost: int = 2) -> Edit:
    """Replaces eat1 (or adds `action` when it is not one of the world's) with a standing action holding `entries`."""
    def edit(r: Rules) -> Rules:
        e = eater(action, *entries, cost=cost)
        return replace(r, standing=tuple(e if a.id == action else a for a in r.standing) if action in (EAT1, EAT2)
                       else (*r.standing, e))
    return edit


def added_standing(action: str, *entries: object) -> Edit:
    return lambda r: replace(r, standing=(*r.standing, StandingDef(ActionId(action), **while_running(*entries))))


BAD: dict[str, tuple[Callable[[], Edit], str, str]] = {
    "a card's HeldSpeed on HANDS": (lambda: card_holds(GS, held_speed(HANDS, 1000)), GS, HANDS),
    "a standing HeldSpeed on HANDS": (lambda: standing_holds(held_speed(HANDS, 1000)), EAT1, HANDS),
    "a card's HeldSpeed on an undeclared lane": (lambda: card_holds(GS, held_speed(NOWHERE, 1000)), GS, NOWHERE),
    "a standing HeldSpeed on an undeclared lane": (lambda: standing_holds(held_speed(NOWHERE, 1000)), EAT1, NOWHERE),
    "a standing amount of 0": (lambda: standing_holds(held_speed(LP, 0)), EAT1, LP),
    "a card's amount of 0": (lambda: card_holds(GS, held_speed(LP, 0)), GS, LP),
    "a negative amount": (lambda: standing_holds(held_speed(LP, -5)), EAT1, LP),
    "one lane twice in a card": (lambda: card_holds(GS, held_speed(LP, 100), held_speed(LP, 200)), GS, LP),
    "one lane twice in a standing action": (lambda: standing_holds(held_speed(LQ, 100), held_speed(LQ, 200)), EAT1, LQ),
    "a standing WhileRunning on an undeclared side": (lambda: standing_holds(side_entry(SideId("nope"), 100)), EAT1, "nope"),
    "one side twice in a standing action": (lambda: standing_holds(side_entry(G, 100), side_entry(G, 200)), EAT1, G),
}
"""Each refusal is built when its test runs, so this module imports before the engine has HeldSpeed. Edit, runner id,
the side or lane id the message must name."""


def test_the_valid_world_passes_the_control_for_every_refusal():
    """Controls: the fixture, an amount of 1, two lanes in one runner, one lane in two runners, a side entry beside a speed
    entry, a standing action that holds nothing under a new id."""
    r = world()
    validate_rules(r)
    validate_rules(standing_holds(held_speed(LP, 1))(r))
    validate_rules(standing_holds(held_speed(LP, 100), held_speed(LQ, 100))(r))
    validate_rules(standing_holds(held_speed(LQ, 100))(r))
    validate_rules(standing_holds(side_entry(G, 100), held_speed(LP, 100), action=ActionId("eatw"))(r))
    validate_rules(card_holds(GS, held_speed(LP, 100), held_speed(LQ, 100), side_entry(G, 50))(r))
    assert len(BAD) == 11


@kills(6, 11)
@pytest.mark.parametrize("name", list(BAD))
def test_each_invalid_shape_is_refused_naming_the_runner_and_the_side_or_lane(name: str):
    edit, runner, entry = BAD[name]
    with pytest.raises(InvalidRulesError) as e:
        validate_rules(edit()(world()))
    assert runner in str(e.value) and entry in str(e.value)


def digest_rules(held: bool) -> Rules:
    """A rules with a standing action holding (or, held False, declaring nothing of the feature at all)."""
    return world(standing=eaters(3, held=held), with_gs=False)


RECORDED = "6579b137ea469cb6b7b81053b620bb528a3c8e2d0f06fa41b7e72e379b1d891f"
"""rules_digest of digest_rules(False), with no standing action holding."""


@kills(12)
def test_rules_whose_standing_actions_declare_no_while_running_keep_their_digest():
    assert rules_digest(digest_rules(False)) == RECORDED
    r = digest_rules(False)
    assert rules_digest(replace(r, standing=tuple(replace(a, **while_running()) for a in r.standing))) == RECORDED


@kills(12)
def test_a_standing_holder_changes_the_digest_by_its_entries():
    plain_d, held_d = rules_digest(digest_rules(False)), rules_digest(digest_rules(True))
    other = replace(digest_rules(True), standing=(eater(EAT1, held_speed(LP, 5001)), *digest_rules(True).standing[1:]))
    assert len({plain_d, held_d, rules_digest(other)}) == 3
