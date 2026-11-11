"""Installed rules (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS", "Installed rule", "Installs land
once", invariants 59 and 60): a trigger's outcome sets a ruled lane's always rule as an ordinary rule, at the top or the
end, once, and a rule the player removed never comes back."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AtLeast, CardCount, CardDef, CardId, InvalidRulesError, LaneDef, LaneId, Order,
    Outcome, PacingCurve, RuleInstall, Rules, SetOrders, SkillDef, SkillId, StoreDef, StoreId, TapCard, TriggerDef,
    TriggerId, advance, advance_logged, decide, encode, new_save, rebase_logged, validate_rules,
)

X = StoreId("x")
HELPER = LaneId("helper")
H, A, B = CardId("h"), CardId("a"), CardId("b")
ALWAYS = AfterTime(0)


def world(*installs: RuleInstall, at: int = 50, triggers: tuple[TriggerDef, ...] | None = None) -> Rules:
    t = TriggerDef(TriggerId("arrive"), AfterTime(at), Outcome(orders=installs))
    r = Rules(stores=(StoreDef(X, 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(HELPER, True),),
              cards=(CardDef(H, 10), CardDef(A, 10, lane=HELPER), CardDef(B, 25, lane=HELPER)),
              triggers=(t,) if triggers is None else triggers)
    validate_rules(r)
    return r


BEFORE = (Order(AtLeast(CardCount(H), 1, 1), TapCard(B)), Order(ALWAYS, TapCard(H)))


def test_installs_go_first_as_a_block_and_the_rest_at_the_end():
    """Invariant 59: F + before + L, each in tuple order, every new latch true, and the same as SetOrders of that
    list at that instant."""
    r = world(RuleInstall(A), RuleInstall(B, first=True), RuleInstall(A, first=True))
    s = decide(new_save(r), r, 0, SetOrders(BEFORE))
    got = advance(s, r, 50)
    want = (Order(ALWAYS, TapCard(B)), *BEFORE, Order(ALWAYS, TapCard(A)))
    assert got.orders == want and (got.latches[0], got.latches[-1]) == (True, True)
    by_hand = decide(advance(s, replace(r, triggers=()), 50), replace(r, triggers=()), 50, SetOrders(want))
    assert (got.orders, got.latches, got.lanes, got.stores) == (by_hand.orders, by_hand.latches, by_hand.lanes,
                                                                 by_hand.stores)


def test_an_equal_order_already_set_is_left_alone():
    r = world(RuleInstall(A, first=True))
    held = (*BEFORE, Order(ALWAYS, TapCard(A)))
    s = decide(new_save(r), r, 0, SetOrders(held))
    assert advance(s, r, 50).orders == held


def test_the_installed_rule_acts_at_once_and_is_reported_as_coming_on():
    r = world(RuleInstall(A))
    step = advance_logged(new_save(r), r, 50)
    assert step.save.lanes[1].card == A
    assert [(c.time, c.order, c.on) for c in step.rule_changes] == [(50, Order(ALWAYS, TapCard(A)), True)]


def test_a_removed_installed_rule_never_comes_back():
    """Invariant 60."""
    r = world(RuleInstall(A))
    s = decide(advance(new_save(r), r, 50), r, 50, SetOrders(()))
    assert advance(s, r, 10_000).orders == ()


def test_a_rebase_onto_rules_whose_new_trigger_already_holds_installs_and_logs_it():
    old = world(triggers=())
    s = advance(new_save(old), old, 80)
    new = world(RuleInstall(A))
    step = rebase_logged(encode(s, old), new)
    assert step.save.orders == (Order(ALWAYS, TapCard(A)),)
    assert [(c.time, c.on) for c in step.rule_changes] == [(80, True)]


BAD: list[Callable[[Rules], Rules]] = [
    lambda r: replace(r, triggers=(TriggerDef(TriggerId("t"), ALWAYS, Outcome(orders=(RuleInstall(H),))),)),
    lambda r: replace(r, cards=(CardDef(H, 10, cap=1, outcome=Outcome(orders=(RuleInstall(A),))), *r.cards[1:])),
    lambda r: replace(r, cards=(CardDef(H, 10, cap=1, finished=Outcome(orders=(RuleInstall(A),))), *r.cards[1:])),
    lambda r: replace(r, triggers=(TriggerDef(TriggerId("t"), ALWAYS, Outcome(queues=(H,))),)),
]


@pytest.mark.parametrize("bad", BAD)
def test_an_install_off_a_ruled_lane_or_outside_a_trigger_is_refused(bad: Callable[[Rules], Rules]):
    r = world(RuleInstall(A))
    with pytest.raises(InvalidRulesError):
        validate_rules(bad(r))
