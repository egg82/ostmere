"""Retired chores (engine DESIGN.txt, "Retired chores"): unit tests written beside the implementation. The contract
tests of invariants 142 to 147 are written blind elsewhere."""
import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AnswerDef, AnswerId, AtMost, CardDef, CardId, Ended, Flow, InvalidRulesError, LaneDef,
    LaneId, OfferDef, OfferId, Order, Outcome, PacingCurve, RuleChange, Rules, SetOrders, SkillDef, SkillId, StoreDef,
    StoreId, StoreValue, TapCard, TriggerDef, TriggerId, advance, advance_logged, decide, decide_logged, decode, encode,
    new_save, rebase_logged, rules_digest, validate_rules,
)
from ashfall_app.engine.codec import to_json

X = StoreId("x")
P1 = LaneId("p1")
H, A1, B1 = CardId("h"), CardId("a1"), CardId("b1")
TURN = TriggerId("turn")
ALWAYS = AfterTime(0)
LOW = Order(AtMost(StoreValue(X), 5 * Q, 8 * Q), TapCard(A1))


def world(retire: tuple[CardId, ...] = (A1,), at: int = 1000, turn: bool = True) -> Rules:
    """A ruled lane p1 with a chore a1 and another card b1, and (with `turn`) a turn at `at` retiring `retire`."""
    cards = (CardDef(H, 100, makes=(Flow(X, Q),)), CardDef(A1, 100, lane=P1, makes=(Flow(X, Q),)),
             CardDef(B1, 100, lane=P1))
    r = Rules(stores=(StoreDef(X, 10**6 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(P1, True),), cards=cards,
              triggers=(TriggerDef(TURN, AfterTime(at), Outcome(retire_orders=retire)),) if turn else ())
    validate_rules(r)
    return r


def planned(r: Rules) -> tuple[Order, ...]:
    return (Order(ALWAYS, TapCard(A1)), Order(ALWAYS, TapCard(B1)), LOW, Order(ALWAYS, TapCard(A1)))


def test_the_turn_removes_every_order_tapping_the_chore_and_logs_each_distinct_one_once():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders(planned(r)))
    step = advance_logged(s, r, 1500)
    assert step.save.orders == (Order(ALWAYS, TapCard(B1)),)
    ended = [c for c in step.rule_changes if c.ended is not None]
    level = next(st.segment.start_value for st in advance(s, r, 1000).stores if st.store == X)
    assert ended == [RuleChange(1000, Order(ALWAYS, TapCard(A1)), False, None, Ended.SEASON),
                     RuleChange(1000, LOW, False, level, Ended.SEASON)]


def test_a_span_without_the_turn_reports_no_ended_change():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders(planned(r)))
    assert all(c.ended is None for c in advance_logged(s, r, 999).rule_changes)
    removed = decide_logged(advance(s, r, 1500), r, 1500, SetOrders(()))
    assert all(c.ended is None for c in removed.rule_changes)


def test_the_rule_set_again_after_the_turn_stays():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders(planned(r)))
    s = decide(advance(s, r, 1500), r, 1500, SetOrders((Order(ALWAYS, TapCard(A1)),)))
    assert advance(s, r, 9000).orders == (Order(ALWAYS, TapCard(A1)),)


def test_a_tap_under_way_lands_and_is_not_started_again():
    r = world(at=50)
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1)),)))
    at = advance(s, r, 50)
    assert at.orders == () and at.lanes[1].card == A1
    later = advance(s, r, 400)
    assert later.lanes[1].card is None
    assert next(cs.work.start_value for cs in later.cards if cs.card == A1) == 100 * 10_000


@pytest.mark.parametrize("retire", [(A1, A1), (CardId("nope"),)])
def test_validation_refuses_a_card_named_twice_or_unknown(retire: tuple[CardId, ...]):
    with pytest.raises(InvalidRulesError, match=str(retire[0])):
        world(retire=retire)


def test_validation_refuses_retire_orders_outside_a_trigger():
    cards = (CardDef(H, 100, cap=1, outcome=Outcome(retire_orders=(H,))),)
    r = Rules(stores=(StoreDef(X, Q, 0),), skills=(), standing=(), curve=PacingCurve((Q,)), cards=cards)
    with pytest.raises(InvalidRulesError, match="h"):
        validate_rules(r)
    offer = OfferDef(OfferId("o"), (AnswerDef(AnswerId("y"), Outcome(retire_orders=(H,))), AnswerDef(AnswerId("n"))))
    r = Rules(stores=(StoreDef(X, Q, 0),), skills=(), standing=(), curve=PacingCurve((Q,)),
              cards=(CardDef(H, 100),), offers=(offer,))
    with pytest.raises(InvalidRulesError, match="h"):
        validate_rules(r)


def test_rules_without_retire_orders_keep_their_encoding_and_a_save_round_trips():
    r = world(retire=())
    assert "retire_orders" not in str(to_json(r.triggers[0].outcome))
    assert rules_digest(r) != rules_digest(world())
    s = advance(decide(new_save(world()), world(), 0, SetOrders(planned(world()))), world(), 1500)
    assert decode(encode(s, world()), world()) == s


def test_a_save_past_the_turn_rebased_into_rules_that_add_it_loses_the_orders_logged():
    old, r = world(turn=False), world()
    s = advance(decide(new_save(old), old, 0, SetOrders(planned(old))), old, 1500)
    step = rebase_logged(encode(s, old), r)
    assert step.save.orders == (Order(ALWAYS, TapCard(B1)),)
    assert {(c.order, c.time, c.ended) for c in step.rule_changes if c.ended is not None} == {
        (Order(ALWAYS, TapCard(A1)), 1500, Ended.SEASON), (LOW, 1500, Ended.SEASON)}
