"""Invariant 17 for cards: each invalid shape "Validation of cards" lists raises InvalidRulesError, and the valid
neighbours of each do not. A store appears at most once across a card's makes, costs, inputs and outcome stores; requires
are plain thresholds. Shapes the stage-1 validate_rules already rejected (a runner id shared by a standing action
and a card) are not repeated here: this suite tests the cards part."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    HANDS, ActionId, Amount, AtLeast, AtMost, CapRaise, CardCount, CardDef, CardId, ChipDef, ChipId, Flow,
    InvalidRulesError, LaneDef, LaneId, LaneSpeed, LineKey, Order, Outcome, QueueEntry, Rules, Running, SetOrders,
    SetQueue, SkillId, StandingDef, StoreDef, StoreId, StoreValue, TapCard, TriggerDef, TriggerId, Unlock,
    UnlockKind, Unlocked, WorkRef, decide, new_save, validate_rules,
)
from cards_world import K, Q, RACK, mul, rules

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
FIRE = ActionId("fire")
CA, CB, RB, CC = CardId("ca"), CardId("cb"), CardId("rb"), CardId("cc")
LEDGER = Unlock(UnlockKind.FEATURE, "ledger")
ON_LEDGER = AtLeast(Unlocked(LEDGER), 1, 1)
CH, TR = ChipId("ch"), TriggerId("tr")

CARD_A = CardDef(
    CA, 100, inputs=(Amount(X, Q),), requires=(AtLeast(StoreValue(Z), Q, Q),), cap=2,
    outcome=Outcome(stores=(Amount(Y, Q),), unlocks=(Unlock(UnlockKind.CARD, CB),), modifiers=(mul(WorkRef(CB), 5000, "a"),),
                    raises=(CapRaise(CA, 1),), starts=(RB,), lines=(LineKey("ca.out"),)),
    finished=Outcome(lines=(LineKey("ca.fin"),), raises=(CapRaise(RB, 2),)),
    lines=(LineKey("ca.1"), LineKey("ca.2")))
CARD_B = CardDef(CB, 50, skill=K, xp_per_hour=100, makes=(Flow(Y, 1000),), costs=(Flow(Z, 500),),
                 lines=(LineKey("cb.tap"),))
CARD_R = CardDef(RB, 30, lane=RACK, cap=3, outcome=Outcome(starts=(CA,)))  # a rack completion may start a hands card
CHIP = ChipDef(CH, AtMost(StoreValue(X), Q, 2 * Q), (mul(LaneSpeed(HANDS), 5000, "ch"),), LineKey("ch.on"),
               LineKey("ch.off"))
TRIGGER = TriggerDef(TR, AtLeast(CardCount(CA), 1, 1), Outcome(unlocks=(Unlock(UnlockKind.CHIP, CH),), starts=(CA,),
                                                               raises=(CapRaise(CA, 1),)))
OPENING = (Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.SKILL, K), Unlock(UnlockKind.ACTION, FIRE),
           Unlock(UnlockKind.CARD, CA), Unlock(UnlockKind.CARD, RB))


def valid() -> Rules:
    return rules([StoreDef(X, 20 * Q, 10 * Q), StoreDef(Y, 20 * Q), StoreDef(Z, 20 * Q)],
                 standing=[StandingDef(FIRE, costs=(Flow(X, 100),))],
                 cards=[CARD_A, CARD_B, CARD_R], lanes=[RACK], chips=[CHIP], triggers=[TRIGGER], opening=list(OPENING))


def with_card(i: int, **changes: object) -> Rules:
    r = valid()
    cards = list(r.cards)
    cards[i] = replace(cards[i], **changes)
    return replace(r, cards=tuple(cards))


def with_a_outcome(**changes: object) -> Rules:
    return with_card(0, outcome=replace(CARD_A.outcome, **changes))


def with_b_outcome(**changes: object) -> Rules:
    return with_card(1, outcome=replace(Outcome(), **changes))


@pytest.mark.parametrize("r", [
    valid(),
    replace(valid(), opening=None),
    with_card(0, lines=()),
    with_card(1, lines=()),
    with_card(1, skill=None, xp_per_hour=0),
    with_card(0, costs=(Flow(Z, 10),), requires=(AtLeast(StoreValue(Z), Q, Q),)),
    with_card(2, outcome=Outcome(starts=(RB,))),
    with_card(0, requires=(AtLeast(CardCount(CB), 2, 2), AtMost(StoreValue(Y), 3 * Q, 3 * Q))),
    replace(valid(), opening=OPENING + (LEDGER,), cards=(replace(CARD_A, requires=(ON_LEDGER,)), CARD_B, CARD_R)),
    replace(valid(), cards=(CARD_A, CARD_B, CARD_R, CardDef(CardId("x"), 10))),
    replace(valid(), lanes=(LaneDef(LaneId(str(RB))),), cards=(CARD_A, CARD_B, replace(CARD_R, lane=LaneId(str(RB))))),
    replace(valid(), stores=valid().stores + (StoreDef(StoreId(str(K)), 20 * Q),)),
], ids=["valid", "no-opening", "capped-without-lines", "uncapped-without-lines", "no-skill-no-xp",
        "requires-store-beside-a-cost-on-it", "rack-card-starts-itself", "plain-count-and-store-requires",
        "condition-on-an-opened-feature", "a-card-and-a-store-share-an-id", "a-lane-and-a-card-share-an-id",
        "a-skill-and-a-store-share-an-id"])
def test_valid_rules_pass(r: Rules):
    """The control: rules using every part of a card validly pass: a capped card with every outcome part and a
    finished that raises another card's cap, a requires on a store the card also costs (a condition is no side), plain
    threshold requires over a count and a store, a rack card starting a hands card or itself, a trigger raising a cap,
    feature ids from the opening, and ids unique per kind rather than across kinds."""
    validate_rules(r)


INVALID = {
    "duplicate lane id": lambda: replace(valid(), lanes=(LaneDef(RACK), LaneDef(RACK))),
    "duplicate chip id": lambda: replace(valid(), chips=(CHIP, CHIP)),
    "duplicate trigger id": lambda: replace(valid(), triggers=(TRIGGER, TRIGGER)),
    "a lane declared as hands": lambda: replace(valid(), lanes=(LaneDef(RACK), LaneDef(HANDS))),
    "undeclared lane": lambda: with_card(1, lane=LaneId("kiln")),
    "work_s 0": lambda: with_card(1, work_s=0),
    "cap 0": lambda: with_card(0, cap=0, lines=()),
    "cap negative": lambda: with_card(0, cap=-1, lines=()),
    "unknown skill": lambda: with_card(1, skill=SkillId("nope")),
    "xp without a skill": lambda: with_card(1, skill=None),
    "flow on unknown store": lambda: with_card(1, makes=(Flow(StoreId("nope"), 10),)),
    "negative flow": lambda: with_card(1, makes=(Flow(Y, -10),)),
    "input amount 0": lambda: with_card(0, inputs=(Amount(X, 0),)),
    "input amount negative": lambda: with_card(0, inputs=(Amount(X, -Q),)),
    "input on unknown store": lambda: with_card(0, inputs=(Amount(StoreId("nope"), Q),)),
    "outcome amount 0": lambda: with_a_outcome(stores=(Amount(Y, 0),)),
    "outcome on unknown store": lambda: with_a_outcome(stores=(Amount(StoreId("nope"), Q),)),
    "trigger outcome amount 0": lambda: replace(valid(), triggers=(replace(TRIGGER, outcome=Outcome(
        stores=(Amount(Y, 0),))),)),
    "uncapped flow and outcome store on one store": lambda: with_card(1, outcome=Outcome(stores=(Amount(Y, Q),))),
    "capped cost flow and input on one store": lambda: with_card(0, costs=(Flow(X, 10),)),
    "store twice in makes": lambda: with_card(1, makes=(Flow(Y, 10), Flow(Y, 20))),
    "store twice in costs": lambda: with_card(1, costs=(Flow(Z, 10), Flow(Z, 20))),
    "store twice in inputs": lambda: with_card(0, inputs=(Amount(X, Q), Amount(X, 2 * Q))),
    "store twice in outcome stores": lambda: with_a_outcome(stores=(Amount(Y, Q), Amount(Y, Q))),
    "input and outcome store on one store": lambda: with_a_outcome(stores=(Amount(X, Q),)),
    "requires with a band on a store": lambda: with_card(0, requires=(AtLeast(StoreValue(Z), Q, Q // 2),)),
    "requires with a band below on a store": lambda: with_card(0, requires=(AtMost(StoreValue(Z), Q, 2 * Q),)),
    "requires with a band on a count": lambda: with_card(0, requires=(AtLeast(CardCount(CB), 2, 1),)),
    "requires on a running card": lambda: with_card(0, requires=(AtLeast(Running(CB), 1, 1),)),
    "requires on a running action": lambda: with_card(0, requires=(AtMost(Running(FIRE), 0, 0),)),
    "make flow and cost flow on one store": lambda: with_card(1, costs=(Flow(Y, 10),)),
    "make flow and input on one store": lambda: with_card(1, inputs=(Amount(Y, Q),)),
    "outcome store and cost flow on one store": lambda: with_card(0, costs=(Flow(Y, 10),)),
    "outcome store and input on one store": lambda: with_card(0, inputs=(Amount(X, Q), Amount(Y, Q))),
    "uncapped outcome with an unlock": lambda: with_b_outcome(unlocks=(Unlock(UnlockKind.CARD, CA),)),
    "uncapped outcome with a modifier": lambda: with_b_outcome(modifiers=(mul(WorkRef(CB), 5000, "b"),)),
    "uncapped outcome with a raise": lambda: with_b_outcome(raises=(CapRaise(CA, 1),)),
    "uncapped outcome with a start": lambda: with_b_outcome(starts=(RB,)),
    "uncapped outcome with a line": lambda: with_b_outcome(lines=(LineKey("cb.out"),)),
    "uncapped with a finished": lambda: with_card(1, finished=Outcome(lines=(LineKey("cb.fin"),))),
    "uncapped with two lines": lambda: with_card(1, lines=(LineKey("cb.1"), LineKey("cb.2"))),
    "capped with too few lines": lambda: with_card(0, lines=(LineKey("ca.1"),)),
    "capped with too many lines": lambda: with_card(0, lines=(LineKey("ca.1"), LineKey("ca.2"), LineKey("ca.3"))),
    "a raise of an uncapped card": lambda: with_a_outcome(raises=(CapRaise(CB, 1),)),
    "a raise by 0": lambda: with_a_outcome(raises=(CapRaise(CA, 0),)),
    "a raise of an unknown card": lambda: with_a_outcome(raises=(CapRaise(CardId("nope"), 1),)),
    "a trigger raising an uncapped card": lambda: replace(valid(), triggers=(replace(TRIGGER, outcome=Outcome(
        raises=(CapRaise(CB, 1),))),)),
    "hands completion starts itself": lambda: with_a_outcome(starts=(CA,)),
    "hands completion starts another hands card": lambda: with_a_outcome(starts=(CB,)),
    "hands finished starts a hands card": lambda: with_card(0, finished=Outcome(starts=(CB,))),
    "outcome starts an unknown card": lambda: with_a_outcome(starts=(CardId("nope"),)),
    "outcome unlocks an unknown id": lambda: with_a_outcome(unlocks=(Unlock(UnlockKind.CHIP, "nope"),)),
    "opening names an unknown card": lambda: replace(valid(), opening=OPENING + (Unlock(UnlockKind.CARD, "nope"),)),
    "opening names a card as an action": lambda: replace(valid(), opening=OPENING + (Unlock(UnlockKind.ACTION, CB),)),
    "opening names an action as a card": lambda: replace(valid(), opening=OPENING + (Unlock(UnlockKind.CARD, FIRE),)),
    "requires on an unknown store": lambda: with_card(0, requires=(AtLeast(StoreValue(StoreId("nope")), Q, Q),)),
    "chip condition on an unknown card's count": lambda: replace(valid(), chips=(replace(CHIP, when=AtLeast(
        CardCount(CardId("nope")), 1, 1)),)),
    "trigger condition on an unknown runner": lambda: replace(valid(), triggers=(replace(TRIGGER, when=AtLeast(
        Running(CardId("nope")), 1, 1)),)),
    "condition on a feature nothing unlocks": lambda: with_card(0, requires=(AtLeast(Unlocked(
        Unlock(UnlockKind.FEATURE, "nope")), 1, 1),)),
    "chip effect sourced elsewhere": lambda: replace(valid(), chips=(replace(CHIP, effects=(
        mul(LaneSpeed(HANDS), 5000, "other"),)),)),
}


@pytest.mark.parametrize("name", sorted(INVALID))
def test_invalid_card_shapes_raise(name: str):
    """Invariant 17: each invalid shape of the cards part raises InvalidRulesError."""
    r = INVALID[name]()
    with pytest.raises(InvalidRulesError):
        validate_rules(r)


def test_orders_and_the_queue_keep_bands_and_running_subjects():
    """Requires are plain thresholds, but an order or a queue entry may use a band and a Running subject: both are
    accepted by SetOrders and SetQueue."""
    r = valid()
    s = new_save(r)
    s = decide(s, r, 0, SetOrders((Order(AtLeast(StoreValue(Z), 2 * Q, Q), TapCard(CB)),
                                   Order(AtMost(Running(CB), 0, 1), TapCard(CB)))))
    decide(s, r, 0, SetQueue((QueueEntry(TapCard(CB), AtLeast(Running(CB), 1, 0)),)))
