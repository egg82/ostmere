"""CHOICES "Orders", "Running dry": a player's switch of the running mix that clears the Pause of a card a true tap order
names makes that card ready at the switch's instant, so evaluation runs there, as it would when READY falls at the
Pause's own resume. Otherwise the order waits for the next unrelated instant, which a player acting on every timer
reaches sooner than one who comes back when they like (the 2 AM test, #473)."""
from ashfall_app.engine import (
    BP, HANDS, AfterTime, CardShare, Flow, Mix, Order, Save, SaveMix, SetOrders, StoreDef, SwitchMix, TapCard, advance,
    decide, new_save, segment,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, store_id

S0, M0, M1 = store_id(0), mix_id(0), mix_id(1)
C2, C3 = card_id(2), card_id(3)
SWITCH_AT = 1800

RULES = make_rules([StoreDef(S0, 100 * Q, Q)], [card(2, 0, (Flow(S0, 5000),), ()), card(3, 0, (), (Flow(S0, 10_000),))])
"""c2 makes s0, c3 draws it twice as fast; s0 starts at one item."""


def _paused() -> Save:
    """The player's m0 runs c2 at a fifth and c3 at the rest: s0 runs dry and c3 pauses, then c2 refills s0, still under
    an hour of c3's cost at SWITCH_AT. The always rule on c3 cannot act while it is paused."""
    s = new_save(RULES)
    for v in (SaveMix(Mix(M0, (CardShare(C2, 2000), CardShare(C3, 8000)))), SaveMix(Mix(M1, (CardShare(C2, BP),))),
              SwitchMix(M0), SetOrders((Order(AfterTime(0), TapCard(C3)),))):
        s = decide(s, RULES, 0, v)
    s = advance(s, RULES, SWITCH_AT)
    assert [p.runner for p in s.pauses] == [C3], "the world did not pause c3: the test is blind"
    assert 0 < segment(s, RULES, S0).start_value < Q * 10, "s0 is not between empty and the resume level"
    return s


def _hands(s: Save):
    return next(ls.card for ls in s.lanes if ls.lane == HANDS)


def test_a_switch_that_clears_the_pause_lets_the_tap_order_act_at_once():
    s = _paused()
    assert _hands(s) is None
    after = decide(s, RULES, SWITCH_AT, SwitchMix(M1))
    assert after.pauses == ()
    assert _hands(after) == C3


def test_the_same_switch_with_no_order_on_the_card_starts_nothing():
    s = _paused()
    bare = decide(s, RULES, SWITCH_AT, SetOrders(()))
    after = decide(bare, RULES, SWITCH_AT, SwitchMix(M1))
    assert after.pauses == () and _hands(after) is None
