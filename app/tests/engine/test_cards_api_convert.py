"""The wire conversion of the cards view and verbs (api/convert.py): plain field copies, both ways."""
from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from tests.engine.test_cards_impl import CHOP, CRAFT, STORY, WOOD, mixed, rules


def test_view_converts_with_one_bar_per_card_and_starved_flags():
    r = rules(wood=0)
    s = e.decide(mixed(r, (CHOP, 4000), (CRAFT, 4000)), r, 3, e.TapCard(STORY))
    wire = convert.view(s, e.view(s, r))
    assert w.View.model_validate(wire.model_dump()) == wire
    card = next(c for c in wire.cards if c.card == STORY)
    assert card.by == w.RunBy.TAP and card.cap == 3 and wire.lanes[0].running_card == STORY
    assert next(c for c in wire.cards if c.card == CHOP).run == w.RunKind.YIELDED


def test_verbs_and_runners_convert_back():
    r = rules()
    assert convert.verb(w.TapCard(card="chop"), r) == e.TapCard(CHOP)
    cond = w.AtLeast(watched=w.Running(runner="chop"), value=1, release=1)
    assert convert.from_condition(cond, r) == e.AtLeast(e.Running(CHOP), 1, 1)
    assert convert.from_subject(w.Running(runner="fire"), r) == e.Running(e.ActionId("fire"))
    assert WOOD


def test_view_carries_the_running_mix_and_which_orders_are_on():
    """running_mix_id, mix_order and orders_on copy the engine view: an order's mix runs over the player's own."""
    r = rules()
    s = mixed(r, (CHOP, 4000))
    s = e.decide(s, r, 0, e.SaveMix(e.Mix(e.MixId("other"), (e.CardShare(CRAFT, 5000),))))
    never = e.AfterTime(10**9)
    orders = (e.Order(never, e.TapCard(STORY)), e.Order(e.AfterTime(0), e.SwitchMix(e.MixId("other"))))
    s = e.decide(s, r, 1, e.SetOrders(orders))
    wire = convert.view(s, e.view(s, r))
    assert (wire.active_mix_id, wire.running_mix_id, wire.mix_order, wire.orders_on) == ("m", "other", 1, [False, True])
