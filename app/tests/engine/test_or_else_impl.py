"""Fallbacks (engine DESIGN.txt, "OR ELSE"): unit tests written beside the implementation, for what the blind contract
of docs/design/rule-guards.md leaves out: the rule log across a season that retires one of a rule's actions."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, CardDef, CardId, Ended, LaneDef, LaneId, Order, Outcome, PacingCurve,
    RuleChange, Rules, SetOrders, SkillDef, SkillId, StoreDef, StoreId, TapCard, TriggerDef, TriggerId,
    advance_logged, decide, new_save, validate_rules,
)

X = StoreId("x")
P1 = LaneId("p1")
A1, B1 = CardId("a1"), CardId("b1")
ALWAYS = AfterTime(0)


def world() -> Rules:
    """A ruled lane p1 with cards a1 and b1; a turn at 1000 retires a1."""
    cards = (CardDef(A1, 100, lane=P1), CardDef(B1, 100, lane=P1))
    r = Rules(stores=(StoreDef(X, 10**6 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(P1, True),), cards=cards,
              triggers=(TriggerDef(TriggerId("turn"), AfterTime(1000), Outcome(retire_orders=(A1,))),))
    validate_rules(r)
    return r


def test_a_rule_keeping_one_action_through_a_retirement_logs_nothing_and_keeps_its_latch():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1), or_else=(TapCard(B1),)),)))
    step = advance_logged(s, r, 1500)
    assert step.save.orders == (Order(ALWAYS, TapCard(B1)),)
    assert step.save.latches == s.latches == (True,)
    assert step.rule_changes == ()


def test_a_rule_whose_every_action_retires_ends_once_for_the_season():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1), or_else=(TapCard(B1),)), Order(ALWAYS, TapCard(A1)))))
    step = advance_logged(s, r, 1500)
    assert step.save.orders == (Order(ALWAYS, TapCard(B1)),)
    assert list(step.rule_changes) == [RuleChange(1000, Order(ALWAYS, TapCard(A1)), False, None, Ended.SEASON)]
