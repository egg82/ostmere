"""A rule waits on hurt (issue #171): `hurt` has no ledger line and is never unlocked as a store, yet the engine reads a
store_value condition on it as on any store, so "when hurt, make a poultice" is a rule the engine runs."""
from ashfall_app.engine import AtLeast, Order, SetOrders, StoreValue, TapCard
from ashfall_app.engine.api import decide_logged
from ashfall_app.engine.rates import tapped_cards
from tests.opening.test_poultice_tap import HURT, POULTICE, in_hand, rules
from ashfall_app.engine import QUANTITY_SCALE as Q

RULE = SetOrders((Order(AtLeast(StoreValue(HURT), Q, Q), TapCard(POULTICE)),))


def taps(hurt_units: int) -> bool:
    s = in_hand(hurt_units)
    after = decide_logged(s, rules(), s.time, RULE).save
    return POULTICE in tapped_cards(after, rules())


def test_the_rule_taps_the_poultice_once_hurt_reaches_its_level():
    assert taps(Q + Q // 2)


def test_it_waits_while_nothing_is_hurt():
    assert not taps(0)


def test_reaches_two_is_on_when_the_chip_reads_two():
    """The page builds "reaches 2, until under 1" on hurt, whose chip shows whole items rounded up (contract/the-client-may.txt, "a store
    rule"), as at_least above one item (Q + 1) releasing under one (1): on at 1.5 hurt, off at 1 and under."""
    rule = SetOrders((Order(AtLeast(StoreValue(HURT), Q + 1, 1), TapCard(POULTICE)),))

    def on(units: int) -> bool:
        s = in_hand(units)
        return POULTICE in tapped_cards(decide_logged(s, rules(), s.time, rule).save, rules())

    assert on(Q + Q // 2) and on(Q + 1)
    assert not on(Q) and not on(Q // 2)
