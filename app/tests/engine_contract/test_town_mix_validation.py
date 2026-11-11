"""Invariant 96 (engine DESIGN.txt, "THE TOWN'S MIX": "Join", "Town share", "Verbs", "Reserved ids"): what rules and
verbs the engine refuses. Each refusal has an accepted control beside it."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, AfterTime, CardDef, CardId, CardShare, InvalidRulesError, InvalidVerbError, Join, LaneId, Mix, MixId, Order, Outcome,
    QueueEntry, Rules, SaveMix, SetQueue, SubMix, SwitchMix, TriggerDef, TriggerId, Unlock, UnlockKind, advance, decide,
    validate_rules,
)
from town_mix_world import (
    A1, A2, AC, B1, B2, C1, H1, LA, LB, TM, TM2, WORK, ALWAYS, HM1, hands_mixes, joiner, orders, start, world,
)

GO = TriggerId("go")


def _with_outcome(o: Outcome) -> Rules:
    return world((TriggerDef(GO, AfterTime(10), o),))


def _join(lane: LaneId, mix: MixId, card: CardId | None = None) -> Outcome:
    return Outcome(joins=(Join(lane, mix, card),))


@pytest.mark.parametrize("bad", [
    _join(LaneId("nowhere"), TM), _join(LaneId("hands"), TM, H1), _join(LA, TM, AC), _join(LA, TM, B1),
    _join(LA, TM, H1), _join(LA, TM, CardId("nope")), _join(LA, MixId("main")), _join(LA, MixId("")),
    Outcome(unlocks=(Unlock(UnlockKind.JOINED, LA),)),
], ids=["undeclared lane", "hands lane", "capped card", "card on another lane", "hands card", "unknown card",
        "mix without town: prefix", "empty mix id", "JOINED in unlocks"])
def test_a_bad_join_or_a_joined_unlock_is_refused(bad: Outcome):
    """Invariant 96: InvalidRulesError for a Join of a lane not declared (or the hands), of a card capped, on another
    lane, on the hands or unknown, of a mix not beginning "town:"; and for a JOINED unlock in Outcome.unlocks."""
    with pytest.raises(InvalidRulesError):
        validate_rules(_with_outcome(bad))
    validate_rules(_with_outcome(_join(LA, TM, A1)))


def test_a_join_of_a_lane_that_is_declared_but_not_ruled_is_refused():
    """Invariant 96: "a declared ruled lane": the same lane declared unruled refuses; ruled, it is valid."""
    r = _with_outcome(_join(LA, TM, A1))
    validate_rules(r)
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(r, lanes=tuple(replace(d, ruled=False) if d.id == LA else d for d in r.lanes)))


@pytest.mark.parametrize("place", ["card outcome", "card finished", "opening"])
def test_a_join_outside_a_trigger_or_answer_and_a_joined_opening_are_refused(place: str):
    """Invariant 96: Outcome.joins in a card's outcome or finished outcome, and a JOINED unlock in Rules.opening, are
    InvalidRulesError."""
    j = _join(LA, TM, A1)
    r = world()
    cards: dict[str, Callable[[], Rules]] = {
        "card outcome": lambda: replace(r, cards=r.cards + (CardDef(CardId("g"), WORK, cap=1, outcome=j),)),
        "card finished": lambda: replace(r, cards=r.cards + (CardDef(CardId("g"), WORK, cap=1, finished=j),)),
        "opening": lambda: replace(r, opening=(Unlock(UnlockKind.JOINED, LA),)),
    }
    with pytest.raises(InvalidRulesError):
        validate_rules(cards[place]())


# ---- the verbs ----------------------------------------------------------------------------------------------------

def _joined_both():
    r = world((joiner("ja", LA, TM, A1), joiner("jb", LB, TM2, B1)))
    return r, start(r)


@pytest.mark.parametrize("mix", [
    Mix(TM, (CardShare(A1, 1000), CardShare(H1, 1000))),
    Mix(TM, (CardShare(A1, 1000), CardShare(C1, 1000))),
    Mix(TM, (CardShare(A1, 1000), CardShare(AC, 1000))),
    Mix(TM, (CardShare(A1, 6000), CardShare(A2, 4001))),
    Mix(TM, (CardShare(B1, 6000), SubMix(TM2, 5000))),
    Mix(TM, (CardShare(B2, 6000), SubMix(TM2, 5000))),
    Mix(HM1, (CardShare(H1, 1000), CardShare(A1, 1000))),
], ids=["layers mixed", "unjoined cure lane", "capped card", "lane sum above BP",
        "lane sum above BP through a nested mix", "same, other card", "hands mix with a town card"])
def test_a_save_mix_that_breaks_the_town_rules_is_refused(mix: Mix):
    """Invariant 96 ("Town share", "Layer"): InvalidVerbError for a mix mixing layers, naming a card on an unjoined
    lane or a capped ruled-lane card, or summing a lane above BP (counted on the flattened shares). lb is joined to
    town:two here, so the nested rows differ only in the sum: B1 and B2 share lb's time."""
    r, s = _joined_both()
    if mix.id == TM and any(isinstance(c, SubMix) for c in mix.components) and mix.components[0] == CardShare(B2, 6000):
        s = decide(s, r, 0, SaveMix(Mix(TM2, (CardShare(B2, BP),))))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SaveMix(mix))


def test_a_save_mix_naming_a_card_of_an_unjoined_person_is_refused():
    """Invariant 96 ("Town share"): lb has not joined, so a town mix naming b1 is refused; once lb joins (control, in
    town:two) the same shares are accepted."""
    r = world((joiner("ja", LA, TM, A1),))
    s = start(r)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SaveMix(Mix(TM, (CardShare(A1, 1000), CardShare(B1, 1000)))))
    both = world((joiner("ja", LA, TM, A1), joiner("jb", LB, TM2, B1)))
    decide(start(both), both, 0, SaveMix(Mix(TM, (CardShare(A1, 1000), CardShare(B1, 1000)))))


def test_a_set_orders_naming_a_town_mix_that_does_not_exist_yet_is_refused():
    """"Verbs" and "Reserved ids": SetOrders accepts a switch to a town mix; a mix absent from save.mixes is refused as
    any SwitchMix to an unknown mix is, since only a join creates a town mix. Control: after the join it is accepted."""
    r = world((joiner("ja", LA, TM, A1, 100),))
    s = start(r)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, orders(Order(ALWAYS, SwitchMix(TM2))))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 50, orders(Order(ALWAYS, SwitchMix(TM))))
    decide(advance(s, r, 100), r, 100, orders(Order(ALWAYS, SwitchMix(TM))))


def test_the_accepted_controls_for_a_town_save_mix():
    """Invariant 96, controls: lane sums of exactly BP, two people each at BP, and the player's edit of an existing
    town mix are accepted."""
    r, s = _joined_both()
    decide(s, r, 0, SaveMix(Mix(TM, (CardShare(A1, 6000), CardShare(A2, 4000)))))
    decide(s, r, 0, SaveMix(Mix(TM2, (CardShare(B1, BP),))))


def test_a_player_cannot_make_a_new_town_id_switch_to_a_town_mix_or_queue_one():
    """Invariant 96 ("Reserved ids", "Verbs"): SaveMix of a "town:" id not in save.mixes, a player's SwitchMix of a
    town mix and SetQueue with a switch to one are InvalidVerbError; SetOrders with one is accepted."""
    r, s = _joined_both()
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SaveMix(Mix(MixId("town:mine"), (CardShare(A1, 1000),))))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SwitchMix(TM))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(TM), AfterTime(5)),)))
    decide(s, r, 0, orders(Order(ALWAYS, SwitchMix(TM2)), Order(AfterTime(5), SwitchMix(TM))))
    decide(start(r, *hands_mixes()), r, 0, SwitchMix(HM1))
