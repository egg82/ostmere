"""Invariant 31 for a card with several unmet preconditions: blocker.ready_at is the time the card is ready, the
latest of the times each unmet input and requires first holds under the current segments (None when any never
holds), and advancing to it leaves the card with no blocker."""
from ashfall_app.engine import (
    ActionId, Amount, AtLeast, CardDef, CardId, Flow, StandingDef, StoreDef, StoreId, StoreValue, Unlock, UnlockKind,
    advance, new_save,
)
from ashfall_app.engine import work as engine_work
from cards_world import Q, rules

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
FAST, SLOW = ActionId("fast"), ActionId("slow")
NEED_X, NEED_Y = AtLeast(StoreValue(X), Q, Q), AtLeast(StoreValue(Y), Q, Q)
NEED_Z = AtLeast(StoreValue(Z), Q, Q)
INPUT_THEN_REQUIRES, REQUIRES_THEN_INPUT, TWO_INPUTS, TWO_REQUIRES, NEVER = (
    CardId(n) for n in ("input_then_requires", "requires_then_input", "two_inputs", "two_requires", "never"))
CARDS = [
    CardDef(INPUT_THEN_REQUIRES, 100, inputs=(Amount(X, Q),), requires=(NEED_Y,)),
    CardDef(REQUIRES_THEN_INPUT, 100, inputs=(Amount(Y, Q),), requires=(NEED_X,)),
    CardDef(TWO_INPUTS, 100, inputs=(Amount(X, Q), Amount(Y, Q))),
    CardDef(TWO_REQUIRES, 100, requires=(NEED_X, NEED_Y)),
    CardDef(NEVER, 100, inputs=(Amount(X, Q),), requires=(NEED_Z,)),
]


def world():
    """x fills an item per 100 s, y an item per 300 s, z never."""
    return rules([StoreDef(s, 100 * Q, 0) for s in (X, Y, Z)],
                 standing=[StandingDef(FAST, makes=(Flow(X, 36_000),)), StandingDef(SLOW, makes=(Flow(Y, 12_000),))],
                 cards=CARDS,
                 opening=[Unlock(UnlockKind.STORE, s) for s in (X, Y, Z)]
                 + [Unlock(UnlockKind.ACTION, a) for a in (FAST, SLOW)] + [Unlock(UnlockKind.CARD, c.id) for c in CARDS])


def test_ready_at_is_the_latest_time_any_unmet_precondition_first_holds():
    """Whichever of inputs and requires is met first, ready_at is when the last one is, and the card is ready then."""
    r = world()
    s = new_save(r)
    for card in (INPUT_THEN_REQUIRES, REQUIRES_THEN_INPUT, TWO_INPUTS, TWO_REQUIRES):
        b = engine_work.blocker(s, r, card)
        assert b is not None and b.ready_at == 300, card
        before = advance(s, r, 299)
        assert engine_work.blocker(before, r, card) is not None, card
        at = advance(s, r, b.ready_at)
        assert engine_work.blocker(at, r, card) is None and engine_work.ready(at, r, card), card


def test_ready_at_is_none_when_a_later_precondition_never_holds():
    """control: the input holds at 100 but z, which nothing makes, never reaches an item: no ready_at."""
    r = world()
    b = engine_work.blocker(new_save(r), r, NEVER)
    assert b is not None and b.ready_at is None
