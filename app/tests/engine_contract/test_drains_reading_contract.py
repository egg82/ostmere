"""Drains, part three: what other parts read of a drain (engine DESIGN.txt, "DRAINS", invariants 129-131, and the fight
odds). Written blind from that part and the public interface; the `kills` marker names the rows of MUTANTS_drains.txt
each test must turn red for."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AtLeast, AtMost, CardDef, CardId, ChipDef, ChipId, EventKind,
    FightDef, Flow, FlowKind, InvalidVerbError, LaneDef, LaneId, Order, RateRef, Rules, Save, SetOrders, SideDef, SideId,
    StandingDef, StoreDef, StoreId, StoreValue, ThreatDef, ThreatId, TapCard, advance, decide, explain, new_save,
    next_event, per_hour, view,
)
from drains_world import BIG, CURE, D, I, X, at, card_view, cure, kills, mixed, tapped, world

BUILD = CardId("build")
L = LaneId("L")


# ---- 129: a drain is a cure ----------------------------------------------------------------------------------

def _hands_busy(chip_when: AtLeast | AtMost) -> tuple[Rules, Save]:
    """x at 10 items, a chip on it shown at once, and the hands in the middle of a 1000 s stage of BUILD."""
    r = world(cure(), CardDef(BUILD, 1000, cap=3), x0=10 * Q, chips=(ChipDef(ChipId("chip"), chip_when),))
    s = decide(new_save(r), r, 0, TapCard(BUILD))
    s = advance(s, r, 100)
    assert s.chips == (True,), "the world's premise: the chip is shown"
    return r, s


@kills(14)
def test_a_card_draining_the_store_of_an_at_least_chip_is_its_cure_and_cuts_in():
    """Invariants 129, 109, 120: the player's tap of the cure on busy hands leaves the interrupted task's work as it stood."""
    r, s = _hands_busy(AtLeast(StoreValue(X), 5 * Q, 5 * Q))
    assert card_view(s, r).cuts_in
    s = decide(s, r, 100, TapCard(CURE))
    assert s.lanes[0].card == CURE
    assert next(cs.work.start_value for cs in s.cards if cs.card == BUILD) == 100 * BP
    assert advance(s, r, 199).lanes[0].card == CURE and at(s, r, X, 200) == 0
    assert advance(s, r, 200).lanes[0].card == BUILD, "the cure landed at its usual time and the queue took the stage up"


@kills(14)
def test_a_drain_is_not_a_cure_for_an_at_most_chip():
    """Invariants 129, 120: the chip shown while x is low is cured by putting x up, which a drain never does."""
    r, s = _hands_busy(AtMost(StoreValue(X), 15 * Q, 15 * Q))
    assert not card_view(s, r).cuts_in
    with pytest.raises(InvalidVerbError):
        decide(s, r, 100, TapCard(CURE))


# ---- 130: not repeat-eligible ----------------------------------------------------------------------------------

def _ruled(card: CardDef, x0: int) -> tuple[Rules, Save]:
    r = world(card, x0=x0, lanes=(LaneDef(L, True),))
    return r, decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(CURE)),)))


def _lane_bar(s: Save, r: Rules):
    return next(b for b in view(s, r).lanes if b.lane == L)


@kills(15)
def test_a_ruled_lane_card_without_drains_repeats_and_with_drains_lands_at_each_completion():
    """Invariants 130, 78: the control repeats (no completion time, no TAP_DONE); with a drain the tap keeps its limit
    and lands at 10 s."""
    r, s = _ruled(CardDef(CURE, 10, lane=L), 0)
    assert _lane_bar(s, r).completes_at is None
    r, s = _ruled(cure(Q, work_s=10, lane=L), 5 * Q // 2)
    assert _lane_bar(s, r).completes_at == 10
    ev = next_event(s, r)
    assert ev is not None and (ev.time, ev.kind) == (10, EventKind.TAP_DONE)


@kills(15)
def test_the_rule_taps_again_while_the_store_holds_and_stops_when_it_is_empty():
    """Invariants 130, 123: 2.5 items fund taps from 0 s and 10 s, and the one at 20 s lands at 30 s with x at 0 from 25 s;
    the rule's next tap is not ready, so the lane is free and the card has landed three times, not a hundred."""
    r, s = _ruled(cure(Q, work_s=10, lane=L), 5 * Q // 2)
    assert [card_view(advance(s, r, t), r).completions for t in (9, 10, 20, 29, 30)] == [0, 1, 2, 2, 3]
    a = advance(s, r, 100)
    assert next(ls.card for ls in a.lanes if ls.lane == L) is None
    assert card_view(a, r).completions == 3 and at(s, r, X, 25) == 0
    assert card_view(advance(s, r, 100_000), r).completions == 3


# ---- 131: split ------------------------------------------------------------------------------------------------

def _split_holds(s: Save, r: Rules, times: tuple[int, ...]) -> None:
    for i, t1 in enumerate(times):
        mid = advance(s, r, t1)
        for t2 in times[i:]:
            assert advance(mid, r, t2) == advance(s, r, t2), (t1, t2)


@kills(16)
def test_split_holds_across_a_drain_reaching_zero_by_a_tap():
    r = world(cure(), x0=4 * Q)
    _split_holds(tapped(r), r, (0, 1, 39, 40, 41, 70, 99, 100, 101, 150))


@kills(16)
def test_split_holds_across_a_mixed_drain_reaching_zero_at_an_odd_instant():
    r = world(cure(7, work_s=3), x0=20)
    _split_holds(mixed(r), r, tuple(range(0, 16)))


@kills(16)
def test_split_holds_across_the_instant_the_drain_starts_being_forgiven_with_an_inflow():
    r = world(cure(), x0=4 * Q, standing=(StandingDef(ActionId("src"), makes=(Flow(X, per_hour(100)),)),))
    _split_holds(tapped(r), r, (0, 54, 55, 56, 57, 99, 100, 101, 110))


@kills(16)
def test_split_holds_across_a_pause_of_another_consumer_at_the_drain_store():
    heal = StandingDef(ActionId("heal"), costs=(Flow(X, per_hour(3)),))
    r = world(cure(), x0=2 * Q, standing=(heal, StandingDef(ActionId("in"), makes=(Flow(X, per_hour(2)),))))
    _split_holds(tapped(r), r, (0, 19, 20, 21, 99, 100, 101, 5499, 5500, 5501))


# ---- the fight odds leave a drain alone ----------------------------------------------------------------------------

G, W = SideId("g"), ThreatId("w")
LOST, STASH, HURT = StoreId("lost"), StoreId("stash"), StoreId("hurt")


def _fighting(p: int, t: int) -> Rules:
    fight = FightDef(G, W, LOST, loses=(Amount(STASH, 3 * Q),), wounds=(Amount(HURT, 2 * Q),))
    return world(cure(fight=fight), x0=BIG, sides=(SideDef(G, p),), threats=(ThreatDef(W, t),),
                 stores=(StoreDef(LOST, BIG), StoreDef(STASH, BIG, BIG), StoreDef(HURT, BIG)))


@kills(24)
@pytest.mark.parametrize("how", ["tapped", "mixed"])
def test_a_fight_cards_odds_scale_its_losses_and_wounds_but_never_its_drain(how: str):
    """DRAINS, "Paid as an input": the drain's line is a cost line the odds leave untouched. At power 0 every fight is
    lost (the loss share is all of BP, the win share none), at power 100 against threat 1 nearly all are won; the stash
    a lost fight takes differs between them (the control), and the drain is its whole amount in both."""
    took = {}
    for p in (0, 1, 100):
        r = _fighting(p, 1)
        s = tapped(r) if how == "tapped" else mixed(r)
        took[p] = (BIG - at(s, r, STASH, 100), BIG - at(s, r, X, 100))
        assert took[p][1] == 10 * Q, p
    assert took[0][0] == 3 * Q and took[0][0] > took[1][0] > took[100][0]


# ---- the read model ------------------------------------------------------------------------------------------------

def test_a_drain_is_listed_in_needs_at_one_unit_after_the_inputs():
    """DRAINS, "Read model": CardView.needs lists a drain's store at quantity 1 (what a tap's start asks), after the
    inputs' whole-completion amounts."""
    r = world(cure(inputs=(Amount(I, 10 * Q),)), x0=Q, i0=10 * Q)
    assert [(n.store, n.quantity) for n in card_view(new_save(r), r).needs] == [(I, 10 * Q), (X, 1)]


def test_a_forgiven_drain_reads_as_an_input_line_never_clamped_and_the_store_is_not_falling():
    """DRAINS, "Read model": at 0 with the drain forgiven its Explanation is still its display rate, net_per_hour sums it
    in unclamped as at a cap, and the segment (rate 0) is not falling."""
    r = world(cure(), x0=0)
    s = advance(mixed(r), r, 10)
    assert explain(s, r, RateRef(CURE, FlowKind.COST, X)).per_hour == D
    line = next(ln for ln in view(s, r).ledger if ln.store == X)
    assert (line.net_per_hour, line.falling, line.segment.rate) == (-D, False, 0)
