"""Store caps (DESIGN.txt, "Store caps"): a Modifier aimed at StoreCap(store) raises what the store holds, combined as
rates are and rounded down; LedgerLine.cap is the cap now; a full store's makers restart the instant it lands; a
lump landing after it is clamped at the raised cap; only raises validate; the save carrying one round-trips."""
import pytest

from ashfall_app.engine import (
    ActionId, AfterTime, Amount, Flow, InvalidRulesError, Modifier, Outcome, StandingDef, StoreCap, StoreDef, StoreId,
    TriggerDef, TriggerId, advance, decode, encode, new_save, validate_rules,
)
from cards_world import Q, add, ledger, mul, rules, val

X = StoreId("x")
GEN = ActionId("gen")


def world(raise_by: list[Modifier], lump_at: int | None = None):
    """gen fills x (cap 4 items) at an item per 100 s; at t = 500 a trigger lands raise_by aimed at x's cap; with
    lump_at, a second trigger then adds ten items of x."""
    camp = Outcome(modifiers=tuple(raise_by))
    triggers = [TriggerDef(TriggerId("camp"), AfterTime(500), camp)]
    if lump_at is not None:
        triggers.append(TriggerDef(TriggerId("lump"), AfterTime(lump_at), Outcome(stores=(Amount(X, 10 * Q),))))
    return rules([StoreDef(X, 4 * Q, 0)], standing=[StandingDef(GEN, makes=(Flow(X, 36_000),))], triggers=triggers)


def test_a_raised_cap_lets_a_full_store_fill_on_to_it():
    """Full at 400 and held at 4 items; x1.5 lands at 500, so the cap is 6 items from then, the maker restarts at
    once and the store is full again at 700, held there."""
    r = world([mul(StoreCap(X), 15_000, "camp")])
    s = new_save(r)
    assert ledger(s, r, X).cap == 4 * Q and ledger(s, r, X).fills_at == 400
    at450 = advance(s, r, 450)
    assert val(at450, r, X) == 4 * Q and ledger(at450, r, X).cap == 4 * Q
    at600 = advance(at450, r, 600)
    assert val(at600, r, X) == 5 * Q and ledger(at600, r, X).cap == 6 * Q and ledger(at600, r, X).fills_at == 700
    assert val(advance(at600, r, 1_000), r, X) == 6 * Q


def test_cap_modifiers_combine_as_rates_do_and_round_down():
    """+50% and +25% sum to +75%, then x2 compounds: 4 items x 1.75 x 2 = 14 items; x1.0001 of 4 items rounds down."""
    r = world([add(StoreCap(X), 5_000, "a"), add(StoreCap(X), 2_500, "b"), mul(StoreCap(X), 20_000, "c")])
    assert ledger(advance(new_save(r), r, 500), r, X).cap == 14 * Q
    odd = world([mul(StoreCap(X), 10_001, "d")])
    assert ledger(advance(new_save(odd), odd, 500), odd, X).cap == 4 * Q * 10_001 // 10_000


def test_a_lump_after_the_raise_is_clamped_at_the_raised_cap():
    """Ten items land at 600 on a store at 5 items whose cap is now 6: it holds 6, not 4 and not 15."""
    r = world([mul(StoreCap(X), 15_000, "camp")], lump_at=600)
    assert val(advance(new_save(r), r, 600), r, X) == 6 * Q


@pytest.mark.parametrize("bad", [
    mul(StoreCap(X), 9_999, "lower"), add(StoreCap(X), -1, "lower"), mul(StoreCap(StoreId("nope")), 15_000, "unknown"),
])
def test_only_a_raise_of_a_known_store_validates(bad: Modifier):
    with pytest.raises(InvalidRulesError):
        validate_rules(world([bad]))


def test_a_save_holding_a_cap_modifier_round_trips():
    r = world([mul(StoreCap(X), 15_000, "camp")])
    s = advance(new_save(r), r, 600)
    assert any(isinstance(m.target, StoreCap) for m in s.modifiers)
    assert decode(encode(s, r), r) == s
