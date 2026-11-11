"""View.order_states (plan.order_states; DESIGN.txt, "Orders", "Order mix", "Greyed mix"): each order is exactly one of
on, waiting (its latch is false), outranked (a latched mix order while an earlier mix order's mix runs) or passed over
(its verb is dead: a greyed mix, a completed card, whatever its latch). It reads the save and changes nothing, so a
replay is the same with or without it; and the wire View carries it in order."""
from hypothesis import given, strategies as st

from ashfall_app.api import convert
from ashfall_app.engine import (
    BP, AfterTime, AtMost, CardDef, CardShare, Flow, Mix, Order, OrderState, Save, SaveMix, SetOrders, StoreDef,
    StoreValue, SwitchMix, TapCard, advance, decide, new_save, view,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, store_id

S0 = store_id(0)
M0, M1, M2, M3 = mix_id(0), mix_id(1), mix_id(2), mix_id(3)
NEVER = AfterTime(10**9)
NOW = AfterTime(0)
G = CardDef(card_id(4), 100, cap=1)


def _world():
    """s0 at 5 of 10 items; m0 = {c0}, m1 = {c1} (the player's), m2 = {c2}, m3 = {c0 50%, g 50%}; g (cap 1) is tapped
    at 0 and completes at 100, greying m3. Returned at 100, with no orders."""
    rules = make_rules([StoreDef(S0, 10 * Q, 5 * Q)], [
        card(0, 0, (Flow(S0, 2000),), ()), card(1, 0, (), (Flow(S0, 1000),)), card(2, 0, (), (Flow(S0, 500),)), G])
    s = new_save(rules)
    for v in (SaveMix(Mix(M0, (CardShare(card_id(0), BP),))), SaveMix(Mix(M1, (CardShare(card_id(1), BP),))),
              SaveMix(Mix(M2, (CardShare(card_id(2), BP),))),
              SaveMix(Mix(M3, (CardShare(card_id(0), 5000), CardShare(G.id, 5000)))), SwitchMix(M1), TapCard(G.id)):
        s = decide(s, rules, 0, v)
    a = advance(s, rules, 100)
    assert view(a, rules).greyed_mixes == (M3,)   # the world's premise
    return rules, a


def _states(orders: tuple[Order, ...]) -> tuple[tuple[OrderState, ...], Save]:
    rules, a = _world()
    b = decide(a, rules, 100, SetOrders(orders))
    return view(b, rules).order_states, b


def test_an_order_whose_condition_does_not_hold_is_waiting():
    states, b = _states((Order(NEVER, SwitchMix(M0)), Order(AtMost(StoreValue(S0), 2 * Q, 4 * Q), TapCard(card_id(2)))))
    assert b.latches == (False, False)
    assert states == (OrderState.WAITING, OrderState.WAITING)


def test_the_first_latched_mix_order_is_on_and_a_later_one_is_outranked():
    states, b = _states((Order(NOW, SwitchMix(M0)), Order(NOW, SwitchMix(M2))))
    assert b.latches == (True, True)
    assert states == (OrderState.ON, OrderState.OUTRANKED)


def test_a_waiting_order_ahead_does_not_outrank():
    states, _ = _states((Order(NEVER, SwitchMix(M0)), Order(NOW, SwitchMix(M2))))
    assert states == (OrderState.WAITING, OrderState.ON)


def test_a_greyed_mix_is_passed_over_whatever_its_latch_and_outranks_nothing():
    states, b = _states((Order(NOW, SwitchMix(M3)), Order(NEVER, SwitchMix(M3)), Order(NOW, SwitchMix(M2))))
    assert b.latches == (True, False, True)
    assert states == (OrderState.PASSED_OVER, OrderState.PASSED_OVER, OrderState.ON)


def test_a_tap_order_is_on_while_its_condition_holds_and_never_outranked_by_a_mix_order():
    states, _ = _states((Order(NOW, SwitchMix(M0)), Order(NOW, TapCard(card_id(2))), Order(NOW, TapCard(G.id))))
    assert states == (OrderState.ON, OrderState.ON, OrderState.PASSED_OVER)   # g is completed: a dead tap


def test_the_wire_view_carries_the_states_in_order():
    states, b = _states((Order(NEVER, SwitchMix(M0)), Order(NOW, SwitchMix(M2)), Order(NOW, SwitchMix(M0)),
                         Order(NOW, SwitchMix(M3))))
    rules, _ = _world()
    wire = convert.view(b, view(b, rules)).order_states
    assert [s.value for s in wire] == ["waiting", "on", "outranked", "passed_over"]
    assert [s.value for s in wire] == [s.value for s in states]


@given(st.lists(st.sampled_from([0, 1, 2, 3]), min_size=1, max_size=4), st.lists(st.booleans(), min_size=4, max_size=4))
def test_reading_the_states_changes_nothing_and_every_order_has_one(mixes: list[int], held: list[bool]):
    rules, a = _world()
    orders = tuple(Order(NOW if held[i] else NEVER, SwitchMix(mix_id(m))) for i, m in enumerate(mixes))
    b = decide(a, rules, 100, SetOrders(orders))
    before = advance(b, rules, 5000)
    states = view(b, rules).order_states
    assert len(states) == len(orders)
    assert sum(s is OrderState.ON for s in states) <= 1   # one mix rule has the hands, or none
    assert advance(b, rules, 5000) == before
