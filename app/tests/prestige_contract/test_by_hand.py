"""Prestige, UndoPick and MovePick are by hand only: refused as a standing order's verb or a queue entry's, even when the click
itself would be allowed, and the guard lets every other verb through."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AtLeast, Order, Prestige, PrestigeRefusal, PrestigeRefused, QueueEntry, SetOrders, SetQueue, StoreValue, TapCard,
    MovePick, UndoPick, decide,
)
from ashfall_app.engine.prestigeverbs import refuse_by_hand
from prestige_world import K, N1, N2, OTHER, SPAN, WOOD, at_second, rules

R = rules()
VERBS = [Prestige(K, N1), UndoPick(K), MovePick(K, N1, N2)]
IDS = ["Prestige", "UndoPick", "MovePick"]
WHEN = AtLeast(StoreValue(WOOD), 0, 0)
TAP = TapCard(OTHER)


@pytest.mark.parametrize("verb", VERBS, ids=IDS)
def test_refuse_by_hand_refuses_each_prestige_verb(verb: Prestige | UndoPick | MovePick):
    with pytest.raises(PrestigeRefused) as found:
        refuse_by_hand(verb)
    assert found.value.reason is PrestigeRefusal.BY_HAND_ONLY


def test_refuse_by_hand_lets_other_verbs_through():
    refuse_by_hand(TAP)
    refuse_by_hand(SetOrders(()))
    refuse_by_hand("anything else")


@pytest.mark.parametrize("verb", VERBS, ids=IDS)
def test_an_order_or_a_queue_entry_naming_one_is_refused_even_when_the_click_is_allowed(verb: Prestige | UndoPick | MovePick):
    """At the top the click itself would act (the control), yet the standing order and the queue entry are refused."""
    save = at_second(R, SPAN)
    decide(save, R, save.time, Prestige(K, N1))
    for plan in (SetOrders((replace(Order(WHEN, TAP), then=verb),)), SetQueue((replace(QueueEntry(TAP, WHEN), verb=verb),))):
        with pytest.raises(PrestigeRefused) as found:
            decide(save, R, save.time, plan)
        assert found.value.reason is PrestigeRefusal.BY_HAND_ONLY


def test_the_same_plans_with_an_ordinary_verb_are_accepted():
    save = at_second(R, SPAN)
    decide(save, R, save.time, SetOrders((Order(WHEN, TAP),)))
    decide(save, R, save.time, SetQueue((QueueEntry(TAP, WHEN),)))
