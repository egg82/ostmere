"""The ledger with cards (invariant 41, "Starved line", "Read model"): a line is starved iff its store is at 0 and a
runner is paused on it or a tap a true order or the queue's controlling entry names is blocked by an AtLeast on its
value; all_covered is false while one is, covered or not. covered follows an order's TapCard through what the card makes
and what its outcome starts."""
import pytest

from ashfall_app.engine import (
    BP, ActionId, AfterTime, Amount, AtLeast, CardDef, CardId, Flow, MixId, Order, Outcome, QueueEntry, Rules, Save,
    SetOrders, SetQueue, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, Verb, advance, decide,
    new_save, view,
)
from ashfall_app.engine import work as engine_work
from cards_world import Q, RACK, ledger, rules, save_mix, with_mix

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
C, G, H, RX, CZ = (CardId(n) for n in ("c", "g", "h", "rx", "cz"))
FIRE = ActionId("fire")
NEVER = AfterTime(10**9)


def world(x0: int, fire: bool = False):
    """c needs an item of x per completion; g's outcome is x; h (capped) starts rx on the rack, whose outcome is x; cz
    requires z >= 1 item. fire, when present, burns x slowly."""
    return rules([StoreDef(X, 100 * Q, x0), StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
                 standing=[StandingDef(FIRE, costs=(Flow(X, 1000),))] if fire else [],
                 cards=[CardDef(C, 100, inputs=(Amount(X, Q),), outcome=Outcome(stores=(Amount(Y, Q),))),
                        CardDef(G, 100, outcome=Outcome(stores=(Amount(X, Q),))),
                        CardDef(H, 100, cap=5, outcome=Outcome(starts=(RX,))),
                        CardDef(RX, 100, lane=RACK, outcome=Outcome(stores=(Amount(X, Q),))),
                        CardDef(CZ, 100, requires=(AtLeast(StoreValue(Z), Q, Q),))],
                 lanes=[RACK])


def starved(s: Save, r: Rules, store: StoreId):
    line = ledger(s, r, store)
    assert line.starved == engine_work.starved(s, r, store)
    return line.starved


def test_a_runner_paused_on_a_dry_store_starves_its_line_covered_or_not():
    """Invariant 41: c, mixed, drains x to 0 at 50 and pauses on it: x is starved and all_covered is false, though an
    order's TapCard of g (whose outcome makes x) covers the line."""
    r = world(Q // 2)
    s = with_mix(new_save(r), r, 0, {C: BP})
    s = decide(s, r, 0, SetOrders((Order(AtLeast(StoreValue(Y), 90 * Q, 90 * Q), TapCard(G)),)))
    assert not starved(s, r, X)
    a = advance(s, r, 50)
    line = ledger(a, r, X)
    assert line.segment.start_value == 0 and line.covered
    assert starved(a, r, X) and not view(a, r).all_covered


@pytest.mark.parametrize("plan", ["order", "queue"])
def test_a_waiting_tap_blocked_on_an_empty_store_starves_it(plan: str):
    """"Starved line": x is at 0 and the tap a true order (or the queue's controlling entry) names is blocked by an
    AtLeast on x's value: starved, with nothing running."""
    r = world(0)
    verb = (SetOrders((Order(AfterTime(0), TapCard(C)),)) if plan == "order"
            else SetQueue((QueueEntry(TapCard(C), NEVER),)))
    s = decide(new_save(r), r, 0, verb)
    assert starved(s, r, X) and not view(s, r).all_covered
    assert not starved(s, r, Y) and not starved(s, r, Z)  # empty too, but the tap is not blocked on them


def test_a_requires_on_an_empty_store_starves_it():
    """"Starved line": the blocking AtLeast may be a requires: cz needs z >= 1 item and z is at 0."""
    r = world(0)
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(CZ)),)))
    assert starved(s, r, Z)


@pytest.mark.parametrize("case", ["no-order", "order-not-true", "store-not-empty"])
def test_nothing_waiting_or_a_store_above_zero_is_not_starved(case: str):
    """Invariant 41's other direction: an empty store nothing waits on, an order that is not true, or a store above 0
    (blocked but not dry) is not starved."""
    r = world(Q // 2 if case == "store-not-empty" else 0)
    s = new_save(r)
    if case != "no-order":
        when = NEVER if case == "order-not-true" else AfterTime(0)
        s = decide(s, r, 0, SetOrders((Order(when, TapCard(C)),)))
    assert not starved(s, r, X)


def covered(r: Rules, verb: Verb | None):
    s = save_mix(save_mix(new_save(r), r, 0, {G: BP}, "mg"), r, 0, {C: BP}, "mc")
    if verb is not None:
        s = decide(s, r, 0, verb)
    return ledger(s, r, X)


@pytest.mark.parametrize("verb, expected", [
    (None, False),
    (SetOrders((Order(NEVER, TapCard(G)),)), True),
    (SetOrders((Order(NEVER, TapCard(H)),)), True),
    (SetOrders((Order(NEVER, TapCard(C)),)), False),
    (SetOrders((Order(NEVER, SwitchMix(MixId("mg"))),)), True),
    (SetOrders((Order(NEVER, SwitchMix(MixId("mc"))),)), False),
    (SetQueue((QueueEntry(TapCard(H), NEVER),)), True),
], ids=["nothing", "tap-of-a-maker", "tap-whose-outcome-starts-a-maker", "tap-of-a-consumer", "switch-to-a-maker",
        "switch-to-a-consumer", "queue-head-tapping-h"])
def test_covered_follows_what_a_verb_makes(verb: Verb | None, expected: bool):
    """"Read model", covered: an order's verb, latched or not, or the queue head's covers a falling line when it makes
    its store: a TapCard through the card's outcome stores and through what its outcome starts (h starts rx, which
    makes x), a SwitchMix through its flattened mix; a tap of a card (or a switch to a mix) that only costs x does not."""
    r = world(10 * Q, fire=True)
    line = covered(r, verb)
    assert line.falling and line.covered is expected and not line.starved
    assert view(advance(new_save(r), r, 0), r).all_covered is False


def test_contributions_name_each_card_once():
    """LedgerLine: net_per_hour is the sum of the contributions, one per running runner, a mixed card's lump line
    among them."""
    r = world(10 * Q, fire=True)
    s = with_mix(new_save(r), r, 0, {C: 5000})
    line = ledger(s, r, X)
    assert sorted((str(c.runner), c.per_hour) for c in line.contributions) == [("c", -(Q // 200)), ("fire", -1000)]
    assert line.net_per_hour == -(Q // 200) - 1000 == line.segment.rate
    assert view(s, r).runs_out_at == line.empties_at is not None


@pytest.mark.parametrize("dead", ["tap-of-completed", "switch-to-greyed"])
def test_a_dead_verb_covers_nothing(dead: str):
    """"Read model", covered: a verb that cannot act (a tap of a completed card, a switch to a greyed mix) makes
    nothing. h (cap 5) starts rx, whose outcome is x, and mix mh holds g (a maker of x) beside h, so either verb
    covers x until h's fifth completion at 500 (the running mix runs h alone)."""
    r = world(0)
    s = save_mix(new_save(r), r, 0, {G: BP // 2, H: BP // 2}, "mh")
    s = with_mix(s, r, 0, {H: BP}, "mrun")
    verb = TapCard(H) if dead == "tap-of-completed" else SwitchMix(MixId("mh"))
    s = decide(s, r, 0, SetOrders((Order(NEVER, verb),)))
    assert ledger(s, r, X).covered
    assert not ledger(advance(s, r, 500), r, X).covered
