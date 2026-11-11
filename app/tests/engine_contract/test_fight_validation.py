"""Validation of fights (DESIGN.txt, "FIGHTS", "CHOICES"), each refusal paired with the valid control."""
from collections.abc import Callable
from dataclasses import replace
from typing import Any

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AtLeast, FightDef, FlowKind, InvalidRulesError,
    InvalidVerbError, Modifier, ModifierKind, Outcome, RateRef, Rules, SideId, SourceId, StandingDef, StoreDef, StoreId, StoreValue,
    ThreatId, TriggerDef, TriggerId, new_save, validate_rules,
)
from fight_world import BAIT, FOUGHT, GRAIN, HAND, HUNT, LOOT, LOST, PELT, RLOST, STASH, WOLF, world

SPARE = StoreId("spare")
type Edit = Callable[[Rules], Rules]


def _changed(f: FightDef | None, kw: dict[str, Any]) -> FightDef:
    assert f is not None
    return replace(f, **kw)


def card_fight(**kw: Any) -> Edit:
    return lambda r: replace(r, cards=(replace(r.cards[0], fight=_changed(r.cards[0].fight, kw)),))


def standing_fight(**kw: Any) -> Edit:
    return lambda r: replace(r, standing=(replace(r.standing[0], fight=_changed(r.standing[0].fight, kw)),))


def card_with(**kw: Any) -> Edit:
    return lambda r: replace(r, cards=(replace(r.cards[0], **kw),))



def trig(m: Modifier | None = None, stores: tuple[Amount, ...] = ()) -> Edit:
    t = TriggerDef(TriggerId("t"), AfterTime(5), Outcome(stores=stores, modifiers=(m,) if m else ()))
    return lambda r: replace(r, triggers=(t,))


BAD: dict[str, Edit] = {
    "unknown side": card_fight(side=SideId("x")),
    "unknown threat": standing_fight(threat=ThreatId("x")),
    "a card fight with per_hour": card_fight(per_hour=1_000),
    "a card fight with fought": card_fight(fought=FOUGHT),
    "a standing fight without per_hour": standing_fight(per_hour=0),
    "a fight card with a cap": card_with(cap=3),
    "a loses store the runner already lists": card_fight(loses=(Amount(BAIT, Q),)),
    "a wounds store the runner makes": standing_fight(wounds=(Amount(GRAIN, Q),)),
    "a loses amount of 0": card_fight(loses=(Amount(STASH, 0),)),
    "lost is a store of the runner's outcome": card_fight(lost=LOOT),
    "a tally another runner makes": standing_fight(lost=PELT),
    "a tally an outcome makes": trig(stores=(Amount(LOST, Q),)),
    "an odds source in a trigger": trig(Modifier(RateRef(HUNT, FlowKind.MAKE, LOOT), ModifierKind.MUL_BP, 5_000, SourceId("odds:hunt"))),
}


def test_the_valid_world_passes_the_control_for_every_refusal():
    validate_rules(world(2, 5))
    validate_rules(trig(Modifier(RateRef(HUNT, FlowKind.MAKE, LOOT), ModifierKind.MUL_BP, 5_000, SourceId("t")))(world(2, 5)))


@pytest.mark.parametrize("name", list(BAD))
def test_each_invalid_fight_shape_is_refused(name: str):
    with pytest.raises(InvalidRulesError):
        validate_rules(BAD[name](world(2, 5)))


def test_a_tally_may_be_read_by_a_condition_and_a_second_fight_may_not_share_it():
    r = world(2, 5)
    r = replace(r, stores=r.stores + (StoreDef(SPARE, Q),))
    gate = TriggerDef(TriggerId("third"), AtLeast(StoreValue(LOST), 3 * Q, 3 * Q), Outcome())
    validate_rules(replace(r, triggers=(gate,)))
    second = StandingDef(ActionId("raid2"), fight=FightDef(HAND, WOLF, RLOST, per_hour=1_000))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(r, standing=r.standing + (second,)))
    validate_rules(replace(r, standing=r.standing + (replace(second, fight=_changed(second.fight, {"lost": SPARE})),)))


def test_the_odds_source_is_refused_in_a_starting_stack_too_and_any_other_source_is_not():
    r = world(2, 5)
    ref = RateRef(HUNT, FlowKind.MAKE, LOOT)
    new_save(r, (Modifier(ref, ModifierKind.MUL_BP, BP, SourceId("gear")),))
    with pytest.raises(InvalidVerbError):
        new_save(r, (Modifier(ref, ModifierKind.MUL_BP, BP, SourceId("odds:hunt")),))
