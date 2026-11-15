"""What refuses a tap of `poultice` with its inputs in hand, read through the engine's decide path (issue #160): its
drain on `hurt` at 0 (engine DESIGN.txt, "DRAINS", "Ready above 0"), and nothing else. The card's face draws the
inputs; the drain is the require it must draw too (tests/opening/test_requires_shown.py)."""
from dataclasses import replace
from functools import cache

from ashfall_app.engine import AtLeast, CardId, Rules, Save, StoreId, StoreState, StoreValue, TapCard, new_save, units
from ashfall_app.engine.api import decide_logged
from ashfall_app.engine.rates import tapped_cards
from ashfall_app.engine.segments import Segment
from ashfall_app.engine.unlocks import Unlock, UnlockKind, unlock_key
from ashfall_app.engine.work import blocker
from ashfall_app.opening.schema import load_opening, to_rules

POULTICE, HURT = CardId("poultice"), StoreId("hurt")


@cache
def rules() -> Rules:
    return to_rules(load_opening())


def in_hand(hurt_units: int) -> Save:
    """The card shown, its lane free, clay and roots well past its inputs, and `hurt` at the given level."""
    r = rules()
    s = new_save(r)
    have = {StoreId("clay"): units(10), StoreId("roots"): units(20), HURT: hurt_units}
    stores = tuple(StoreState(x.store, Segment(s.time, have[x.store], 0)) if x.store in have else x for x in s.stores)
    shown = {Unlock(UnlockKind.CARD, "poultice"), Unlock(UnlockKind.STORE, "clay"), Unlock(UnlockKind.STORE, "roots")}
    return replace(s, stores=stores, unlocked=tuple(sorted({*s.unlocked, *shown}, key=unlock_key)))


def tap(s: Save) -> tuple[Save, CardId | None]:
    step = decide_logged(s, rules(), s.time, TapCard(POULTICE))
    return step.save, step.failed


def test_with_its_inputs_in_hand_and_no_hurt_the_tap_fails_on_the_drain():
    s = in_hand(0)
    after, failed = tap(s)
    assert failed == POULTICE and POULTICE not in tapped_cards(after, rules())
    b = blocker(s, rules(), POULTICE)
    assert b is not None and b.condition == AtLeast(StoreValue(HURT), 1, 1)


def test_any_hurt_at_all_lets_the_same_tap_start():
    after, failed = tap(in_hand(1))
    assert failed is None and POULTICE in tapped_cards(after, rules())
