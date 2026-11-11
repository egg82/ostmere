"""Drains, part five: validation (engine DESIGN.txt, "DRAINS", CHOICES, "Validation"): InvalidRulesError naming the card and
the store for a drain on an unknown store, a quantity below 1, a store also in the card's makes, costs, inputs, outcome
stores or fight lines, or drained twice. Written blind from that part and the public interface."""
import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, Amount, CardDef, FightDef, Flow, InvalidRulesError, Outcome, Rules, SideDef, SideId, StoreDef, StoreId,
    ThreatDef, ThreatId, per_hour,
)
from drains_world import CURE, F, I, X, X2, Y, cure, kills, world

G, W, LOST = SideId("g"), ThreatId("w"), StoreId("lost")


def build(card: CardDef) -> Rules:
    """World with a side, a threat and a tally store for the fight shapes."""
    return world(card, sides=(SideDef(G, 4),), threats=(ThreatDef(W, 3),), stores=(StoreDef(LOST, 100 * Q),))


def fight(loses: tuple[Amount, ...] = (), wounds: tuple[Amount, ...] = ()) -> FightDef:
    return FightDef(G, W, LOST, loses=loses, wounds=wounds)


REFUSED = {
    "unknown store": cure(drains=(Amount(StoreId("nowhere"), Q),)),
    "quantity zero": cure(0),
    "quantity negative": cure(-1),
    "also an input": cure(inputs=(Amount(X, Q),)),
    "also a cost": cure(costs=(Flow(X, per_hour(1)),)),
    "also a make": cure(makes=(Flow(X, per_hour(1)),)),
    "also an outcome store": cure(outcome=Outcome(stores=(Amount(X, Q),))),
    "also a fight loss": cure(fight=fight(loses=(Amount(X, Q),))),
    "also a fight wound": cure(fight=fight(wounds=(Amount(X, Q),))),
    "also the fight's tally": cure(fight=FightDef(G, W, X)),
    "drained twice": cure(drains=(Amount(X, Q), Amount(X, 2 * Q))),
}
ACCEPTED = {
    "one drain": cure(),
    "two drains on two stores": cure(drains=(Amount(X, Q), Amount(X2, Q))),
    "a drain beside other lines on other stores": cure(
        makes=(Flow(Y, per_hour(1)),), inputs=(Amount(I, Q),), outcome=Outcome(stores=(Amount(F, Q),))),
    "a drain beside a fight on other stores": cure(fight=fight(loses=(Amount(I, Q),), wounds=(Amount(Y, Q),))),
    "the smallest quantity": cure(1),
    "a finished landing on the drained store": cure(cap=1, finished=Outcome(stores=(Amount(X, Q),))),
}


@kills(18)
@pytest.mark.parametrize("card", REFUSED.values(), ids=REFUSED.keys())
def test_rules_the_engine_must_refuse_are_refused_naming_the_card_and_the_store(card: CardDef):
    with pytest.raises(InvalidRulesError) as e:
        build(card)
    named = str(e.value)
    assert str(CURE) in named, named
    assert any(str(s) in named for s in (X, "nowhere")), named


@kills(18)
@pytest.mark.parametrize("card", ACCEPTED.values(), ids=ACCEPTED.keys())
def test_the_near_misses_validate(card: CardDef):
    """The controls: each refused shape's neighbour that breaks no rule, so a validator that refuses everything fails here."""
    build(card)
