"""Rule guards (engine design/rule-guards.txt, "RULE GUARDS"): unit tests written beside the implementation, to develop it. The
contract tests of docs/design/rule-guards.md's statements are written blind elsewhere."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, AtLeast, AtMost, CardDef, CardId, CardShare, Flow, GuardedLatch,
    InvalidVerbError, LaneRules, Mix, MixId, Order, OrderState, PacingCurve, Rules, Save, SaveMix, SetOrders, SkillDef,
    SkillId, StoreDef, StoreId, StoreValue, SwitchMix, advance, advance_logged, decide, decode, encode, new_save, per_hour, view,
)
from ashfall_app.engine.savefile.codec import to_json, verb_from_json, verb_to_json
from ashfall_app.engine.core.ids import HANDS

S0 = StoreId("s0")
FILL, SLOW, DRAIN = MixId("fill"), MixId("slow"), MixId("drain")
H = 3600


def _rules(initial: int) -> Rules:
    """S0 (100 items) starting at `initial`; FILL makes 2 items an hour, SLOW 1, DRAIN costs 1."""
    cards = (CardDef(CardId("f"), 60, makes=(Flow(S0, per_hour(2)),)),
             CardDef(CardId("s"), 60, makes=(Flow(S0, per_hour(1)),)),
             CardDef(CardId("d"), 60, costs=(Flow(S0, per_hour(1)),)))
    return Rules((StoreDef(S0, 100 * Q, initial),), (SkillDef(SkillId("k")),), (), PacingCurve((10**15,)), 1000,
                 cards=cards)


def _world(rules: Rules, own: MixId, *orders: Order) -> Save:
    s = new_save(rules)
    for mix, card in ((FILL, "f"), (SLOW, "s"), (DRAIN, "d")):
        s = decide(s, rules, 0, SaveMix(Mix(mix, (CardShare(CardId(card), BP),))))
    s = decide(s, rules, 0, SwitchMix(own))
    return decide(s, rules, 0, SetOrders(orders))


def _at_least(v: int, release: int) -> AtLeast:
    return AtLeast(StoreValue(S0), v * Q, release * Q)


def test_a_guard_pauses_from_its_value_and_resumes_past_its_release_with_no_other_event():
    """Statement 5: always FILL, unless S0 is 4 or more (lets go under 3); the player's DRAIN runs while paused."""
    rules = _rules(0)
    s = _world(rules, DRAIN, Order(AfterTime(0), SwitchMix(FILL), (_at_least(4, 3),)))
    assert s.latches == (GuardedLatch(True, (False,)),)
    at = advance(s, rules, 2 * H - 1)
    assert view(at, rules).running_mix == FILL and view(at, rules).order_states == (OrderState.ON,)
    paused = advance(s, rules, 2 * H)
    v = view(paused, rules)
    assert v.running_mix == DRAIN and v.order_states == (OrderState.PAUSED,) and v.orders_on == (True,)
    assert v.order_guards[0][0].on and v.order_guards[0][0].lets_go == 3 * Q
    # 4 items, falling an item an hour: under 3 one second past the hour.
    assert view(advance(s, rules, 3 * H), rules).running_mix == DRAIN
    assert view(advance(s, rules, 3 * H + 1), rules).running_mix == FILL


def test_a_pause_is_not_a_rule_change():
    """The rule log's came-on and let-go stay the `when` latch's."""
    rules = _rules(0)
    s = _world(rules, DRAIN, Order(AfterTime(0), SwitchMix(FILL), (_at_least(4, 3),)))
    assert advance_logged(s, rules, 10 * H).rule_changes == ()


def test_paused_inside_the_band_it_resumes_without_reaching_when_again():
    """Statement 7: down to 2, until over 8, FILL, unless 5 or more (lets go under 4). From 3 under DRAIN it comes on
    at 2 (1 h), fills to 5 (2.5 h), is paused, falls under 4 and is on again without S0 reaching 2."""
    rules = _rules(3 * Q)
    s = _world(rules, DRAIN, Order(AtMost(StoreValue(S0), 2 * Q, 8 * Q), SwitchMix(FILL), (_at_least(5, 4),)))
    assert view(advance(s, rules, H), rules).running_mix == FILL
    assert view(advance(s, rules, H + 3 * H // 2), rules).order_states == (OrderState.PAUSED,)
    resumed = advance(s, rules, H + 3 * H // 2 + H + 1)
    assert view(resumed, rules).running_mix == FILL and resumed.stores[0].segment.start_value > 2 * Q


def test_until_reached_while_paused_leaves_it_waiting_after_the_guard_lets_go():
    """Statement 7: down to 2, until over 6, FILL, unless 4 or more (plain). The player's SLOW keeps filling while
    paused, so the `when` latch lets go past 6; the guard letting go under DRAIN later changes nothing until 2."""
    rules = _rules(Q)
    s = _world(rules, SLOW, Order(AtMost(StoreValue(S0), 2 * Q, 6 * Q), SwitchMix(FILL), (_at_least(4, 4),)))
    paused = advance(s, rules, 3 * H // 2)
    assert view(paused, rules).order_states == (OrderState.PAUSED,)
    # 4 items at 1.5 h, then SLOW: past 6 one second after 3.5 h.
    waiting = advance(s, rules, 7 * H // 2 + 1)
    assert waiting.latches == (GuardedLatch(False, (True,)),)
    assert view(waiting, rules).order_states == (OrderState.WAITING,)
    s2 = decide(waiting, rules, 4 * H, SwitchMix(DRAIN))
    let_go = advance(s2, rules, 7 * H)
    assert let_go.latches == (GuardedLatch(False, (False,)),) and view(let_go, rules).running_mix == DRAIN
    assert view(advance(s2, rules, 9 * H), rules).running_mix == FILL


def test_two_guards_pause_while_either_holds():
    """Statement 8: unless 4 or more, and unless 6 or more (plain); FILL from 3 under DRAIN."""
    rules = _rules(3 * Q)
    s = _world(rules, DRAIN, Order(AfterTime(0), SwitchMix(FILL), (_at_least(4, 4), _at_least(2, 2))))
    assert s.latches == (GuardedLatch(True, (False, True)),)
    assert view(s, rules).order_states == (OrderState.PAUSED,)
    assert view(advance(s, rules, H + 1), rules).order_states == (OrderState.ON,)


def test_set_orders_keeps_an_equal_rules_latches_and_latches_an_edited_one_afresh():
    """Statement 11."""
    rules = _rules(0)
    o = Order(AfterTime(0), SwitchMix(FILL), (_at_least(4, 1),))
    s = advance(_world(rules, DRAIN, o), rules, 2 * H + 1)
    assert s.latches == (GuardedLatch(True, (True,)),)
    assert decide(s, rules, s.time, SetOrders((o,))).latches == s.latches
    edited = Order(AfterTime(0), SwitchMix(FILL), (_at_least(5, 1),))
    assert decide(s, rules, s.time, SetOrders((edited,))).latches == (GuardedLatch(True, (False,)),)


@pytest.mark.parametrize("guards", [
    tuple(_at_least(i + 1, 0) for i in range(4)),
    (_at_least(4, 3), _at_least(4, 3)),
    (AtLeast(LaneRules(HANDS), 1, 1),),
    (AtLeast(StoreValue(S0), 2 * Q, 3 * Q),),
    (AtLeast(StoreValue(StoreId("nope")), Q, Q),),
])
def test_set_orders_refuses_a_bad_guard_list(guards: tuple[AtLeast, ...]):
    """Statement 3, the guards' parts."""
    rules = _rules(0)
    with pytest.raises(InvalidVerbError):
        _world(rules, DRAIN, Order(AfterTime(0), SwitchMix(FILL), guards))


def test_three_guards_are_accepted():
    rules = _rules(0)
    s = _world(rules, DRAIN, Order(AfterTime(0), SwitchMix(FILL), tuple(_at_least(i + 1, 0) for i in range(3))))
    assert len(s.orders[0].unless) == 3


def test_the_codec_leaves_an_empty_unless_out_and_round_trips_guards():
    """Statements 1 and 2."""
    rules = _rules(0)
    plain = Order(AfterTime(0), SwitchMix(FILL))
    assert "unless" not in str(to_json(plain))
    s = _world(rules, DRAIN, plain)
    assert s.latches == (True,) and "GuardedLatch" not in encode(s, rules)
    guarded = Order(AfterTime(0), SwitchMix(FILL), (_at_least(4, 3),))
    g = advance(_world(rules, DRAIN, guarded), rules, 2 * H + 5)
    assert decode(encode(g, rules), rules) == g
    verb = SetOrders((guarded, plain))
    assert verb_from_json(verb_to_json(verb)) == verb


def test_splitting_an_advance_changes_nothing():
    """Statement 22 (invariant 1) on a guarded world."""
    rules = _rules(3 * Q)
    s = _world(rules, DRAIN, Order(AtMost(StoreValue(S0), 2 * Q, 8 * Q), SwitchMix(FILL), (_at_least(5, 4),)))
    whole = advance(s, rules, 12 * H)
    for t in (H, H + 1, 5 * H // 2, 3 * H + 7, 7 * H):
        assert advance(advance(s, rules, t), rules, 12 * H) == whole
