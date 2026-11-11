"""Orders and the queue with cards (invariants 23, 24; "Orders" with TapCard as the one verb): a tap's landing makes
orders and the queue evaluate and a player's tap does not; "keep doing this until" is a queue entry on a CardCount;
an order re-taps at each landing while it is latched, its store moving as a rate; READY starts a queued tap the second
it turns ready; landings count toward the firing cap, and after a cascade READY falls at the next second so the hands
never idle on the cap. An order may name an unknown card: it acts on nothing."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, Amount, AtLeast, AtMost, CardCount, CardDef, CardId, Event, EventKind, Flow,
    LineKey, MixId, Order, Outcome, QueueEntry, Rules, SetOrders, SetQueue, StandingDef, StoreDef, StoreId,
    OrderVerb, StoreValue, SwitchMix, TriggerDef, TriggerId, Unlock, UnlockKind, advance, advance_logged, decide, new_save,
    next_event, segment, view,
)
from ashfall_app.engine.schedule import events
from ashfall_app.engine import TapCard
from cards_world import K, Q, RACK, done, keys, lane, ledger, rules, running_mix, save_mix, tap, val

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
CU, M0C, M1C, R, C, CP = (CardId(n) for n in ("cu", "m0c", "m1c", "r", "c", "cp"))
GEN = ActionId("gen")
M0, M1 = MixId("m0"), MixId("m1")
NEVER_ON = AfterTime(10**9)


def world(max_firings: int = 1000, gen: int = 0):
    return rules([StoreDef(X, 100 * Q, 0), StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
                 standing=[StandingDef(GEN, makes=(Flow(X, gen),))],
                 cards=[CardDef(CU, 100, outcome=Outcome(stores=(Amount(Y, Q),)), lines=(LineKey("cu.tap"),)),
                        CardDef(M0C, 100, makes=(Flow(Z, 10),)), CardDef(M1C, 100, makes=(Flow(Z, 20),)),
                        CardDef(R, 100, lane=RACK), CardDef(C, 100, inputs=(Amount(X, Q),)), CardDef(CP, 100, cap=3)],
                 lanes=[RACK], max_firings=max_firings)


def test_a_trigger_that_fires_makes_orders_evaluate():
    """"Orders": orders and the queue evaluate after a trigger's outcome, as after a landing. An order names a card that
    is locked until a trigger unlocks it at 100: it taps then, with nothing else to start it (it is ready the moment it
    unlocks, so no READY event falls)."""
    locked = CardId("locked")
    r = rules([StoreDef(X, 100 * Q, 0)], cards=[CardDef(locked, 100)],
              triggers=[TriggerDef(TriggerId("t"), AfterTime(100), Outcome(unlocks=(Unlock(UnlockKind.CARD, locked),)))],
              opening=[Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.SKILL, K)])
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(locked)),)))
    assert lane(advance(s, r, 99), HANDS).card is None
    assert lane(advance(s, r, 100), HANDS).card == locked


def test_the_queue_repeats_a_tap_until_its_count():
    """"keep doing this until" is a queue entry: its TapCard is re-applied at each landing until its until (a
    CardCount) pops it, at the landing that reaches the count."""
    r = world()
    s = decide(new_save(r), r, 0, SetQueue((QueueEntry(TapCard(CU), AtLeast(CardCount(CU), 3, 3)),)))
    assert lane(s, HANDS).card == CU
    a = advance(s, r, 1000)
    assert done(a, r, CU) == 3 and a.queue == () and lane(a, HANDS).card is None


def test_an_order_retaps_at_each_landing_until_its_latch_releases():
    """Invariant 24 with the rate form: "y <= 0 (release above 2 items): tap cu" taps at once and again at each
    landing. y rises as each tap runs, so it reaches 2 items exactly at the second landing (still latched: release is
    "above") and passes it a second into the third tap; that tap runs to its end (no cancel) and nothing restarts."""
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(AtMost(StoreValue(Y), 0, 2 * Q), TapCard(CU)),)))
    step = advance_logged(s, r, 1000)
    assert keys(step.lines) == [(100, "cu.tap"), (200, "cu.tap"), (300, "cu.tap")]
    a = step.save
    assert done(a, r, CU) == 3 and lane(a, HANDS).card is None and val(a, r, Y) == 3 * Q
    assert a.latches == (False,)
    assert advance(s, r, 201).latches == (False,) and lane(advance(s, r, 201), HANDS).card == CU


def test_a_queue_mix_runs_over_a_players_switch_through_a_landing():
    """"Queue mix": the queue's m0 runs while its entry controls; the player's switch to m1 sets only save.active, and
    neither the player's tap nor its landing on the rack changes either."""
    r = world()
    s = save_mix(save_mix(new_save(r), r, 0, {M0C: BP}, "m0"), r, 0, {M1C: BP}, "m1")
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(M0), AfterTime(10**9)),)))
    assert running_mix(s, r) == M0 and s.active is None
    s = tap(decide(s, r, 10, SwitchMix(M1)), r, 10, R)
    for t in (10, 109, 110):
        a = advance(s, r, t)
        assert a.active == M1 and running_mix(a, r) == M0


def test_a_queued_tap_starts_the_second_it_turns_ready():
    """Invariant 23 / READY: the queue head taps c, which needs an item of x; gen fills x at an item per 100 s, so a
    READY falls at 100 and c starts then, ready."""
    r = world(gen=36_000)
    s = decide(new_save(r), r, 0, SetQueue((QueueEntry(TapCard(C), AfterTime(10**9)),)))
    assert lane(s, HANDS).card is None
    assert next_event(s, r) == Event(100, EventKind.READY, 4, C)
    a = advance(s, r, 100)
    assert lane(a, HANDS).card == C
    assert lane(advance(s, r, 99), HANDS).card is None


def test_landings_count_toward_the_firing_cap():
    """Invariants 13, 24: with max_firings_per_instant 1 the order's tap at the SetOrders instant is applied (a decide
    starts a fresh count), but at the landing the TAP_DONE itself reaches the cap: evaluation is suspended, the
    instant recorded, and nothing re-taps cu."""
    r = world(max_firings=1)
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(CU)),)))
    assert lane(s, HANDS).card == CU
    a = advance(s, r, 100)
    assert a.cascade_count == s.cascade_count + 1 and a.last_cascade is not None and a.last_cascade.time == 100
    assert lane(a, HANDS).card is None


@pytest.mark.parametrize("max_firings, suspended", [(1000, False), (2, True)])
def test_after_a_cascade_ready_falls_at_the_next_second_for_a_card_ready_all_along(max_firings: int, suspended: bool):
    """"Evaluation after a cascade": the player taps cp (capped) while a true order names cu, which is ready but cannot
    start on the busy hands. cp's COMPLETION and TAP_DONE at 100 are two firings: with a cap of 2 evaluation is
    suspended at that instant (a cascade) and cu, ready all along, has no READY to turn; one falls at 101 and the order
    starts it then. The control, with room for the firings, starts cu at 100."""
    r = world(max_firings=max_firings)
    s = decide(tap(new_save(r), r, 0, CP), r, 0, SetOrders((Order(AfterTime(0), TapCard(CU)),)))
    assert lane(s, HANDS).card == CP
    a = advance(s, r, 100)
    if not suspended:
        assert a.cascade_count == 0 and lane(a, HANDS).card == CU
        return
    assert a.cascade_count == 1 and a.last_cascade is not None and a.last_cascade.time == 100
    assert lane(a, HANDS).card is None
    e = next_event(a, r)
    assert e is not None and (e.time, e.kind, e.subject) == (101, EventKind.READY, CU)
    assert lane(advance(a, r, 101), HANDS).card == CU


def test_an_order_naming_an_unknown_card_is_accepted_and_acts_on_nothing():
    """Validation of cards: an order or queue entry may name a card the rules lack. It is never tappable, covers nothing
    and is never a candidate: no tap, no READY event, and the ledger is no better covered."""
    r = world(gen=0)
    ghost = CardId("ghost")
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(ghost)),)))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(ghost), AfterTime(10**9)),)))
    assert lane(s, HANDS).card is None and not [e for e in events(s, r) if e.kind is EventKind.READY]
    a = advance(s, r, 1000)
    assert lane(a, HANDS).card is None and a.queue == s.queue
    assert not ledger(a, r, X).covered


# ---- Order mix: tap orders and mix orders never compete (invariant 44, "Order mix", "Read model" covered) ----------

def _mixes(r: Rules):
    """m0 = {m0c} (z at 10/s) is the player's; m1 = {m1c} (z at 20/s) is the one orders name."""
    s = save_mix(save_mix(new_save(r), r, 0, {M0C: BP}, "m0"), r, 0, {M1C: BP}, "m1")
    return decide(s, r, 0, SwitchMix(M0))


def test_a_hands_tap_rule_after_a_latched_mix_rule_still_taps():
    """Invariant 44: "run m1" is latched first and "tap cu" second; the mix order cannot shadow the tap order, so cu
    taps on the hands (yielding the running m1) and re-taps at its landing; save.active stays the player's m0."""
    r = world()
    s = decide(_mixes(r), r, 0, SetOrders((Order(AfterTime(0), SwitchMix(M1)), Order(AfterTime(0), TapCard(CU)))))
    assert lane(s, HANDS).card == CU and s.active == M0
    a = advance(s, r, 150)
    assert done(a, r, CU) == 1 and lane(a, HANDS).card == CU
    assert view(s, r).running_mix == M1 and view(s, r).mix_order == 0


@pytest.mark.parametrize("tap_first", [False, True], ids=["mix-rule-first", "tap-rule-first"])
def test_a_rack_tap_rule_and_a_mix_rule_both_act(tap_first: bool):
    """Invariant 44: a rack tap order and a mix order, in either sequence: r taps on the rack and m1 runs beside it
    (z rises at m1c's 20/s), with save.active still the player's m0."""
    r = world()
    orders = [Order(AfterTime(0), SwitchMix(M1)), Order(AfterTime(0), TapCard(R))]
    if tap_first:
        orders.reverse()
    s = decide(_mixes(r), r, 0, SetOrders(tuple(orders)))
    assert lane(s, RACK).card == R and lane(s, HANDS).card is None
    assert segment(s, r, Z).rate == 20 and s.active == M0
    assert view(s, r).running_mix == M1


BURN = ActionId("burn")
MK, ONE = CardId("mk"), CardId("one")
MG = MixId("mg")


def _covered_world():
    """x falls (burn draws it); mk makes x; one (cap 1) adds an item of x per completion; mg = {mk, one}."""
    r = rules([StoreDef(X, 100 * Q, 10 * Q)], standing=[StandingDef(BURN, costs=(Flow(X, 1000),))],
              cards=[CardDef(MK, 100, makes=(Flow(X, 1000),)),
                     CardDef(ONE, 100, cap=1, outcome=Outcome(stores=(Amount(X, Q),)))])
    return r, save_mix(new_save(r), r, 0, {MK: 5000, ONE: 5000}, "mg")


@pytest.mark.parametrize("verb", [SwitchMix(MG), TapCard(ONE)], ids=["switch-to-mg", "tap-of-one"])
def test_covered_is_false_for_a_dead_rule_verb(verb: OrderVerb):
    """"Read model", covered: an order switching to mg or tapping one covers falling x while it can act; once one
    completes (mg greyed, one spent) the same order is dead and covers nothing."""
    r, s = _covered_world()
    live = decide(s, r, 0, SetOrders((Order(NEVER_ON, verb),)))
    assert ledger(live, r, X).falling and ledger(live, r, X).covered
    a = advance(tap(s, r, 0, ONE), r, 100)
    v = view(a, r)
    assert v.greyed_mixes == (MG,) and ONE in [c.card for c in v.completed]
    dead = decide(a, r, 100, SetOrders((Order(NEVER_ON, verb),)))
    assert ledger(dead, r, X).falling and not ledger(dead, r, X).covered
