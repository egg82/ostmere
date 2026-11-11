"""Completions (invariants 36-38, "Completions"): a card completes each time its work crosses a multiple of work_s *
BP, tapped or mixed. A capped card's completion is an event (COMPLETION) at that exact second, with its line and its
outcome's non-store parts, and it resolves before the tap's TAP_DONE at the same instant; an uncapped card's completions
are counted off the work segment, never evented, so CardCount is solved and an order or trigger on it fires at the
exact second. A capped and an uncapped card at one share complete at the same seconds: work is limited only at the cap
and at a tap's boundary."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, AfterTime, AtLeast, AtMost, CardCount, CardDef, CardId, Event, EventKind, Flow, LaneSpeed, LineKey, MixId,
    Order, Outcome, SetOrders, StoreDef, StoreId, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Amount,
    advance, advance_logged, decide, new_save, next_event,
)
from ashfall_app.engine.schedule import events
from cards_world import K, Q, ceil_div, done, keys, lane, mul, rules, running_mix, save_mix, tap, val, with_mix, work

Y, Z = StoreId("y"), StoreId("z")
CC, CU, CM, CC2, DL = (CardId(n) for n in ("cc", "cu", "cm", "cc2", "dl"))
TRIG = TriggerId("t")


def world(trigger_on: CardId | None = None, opening: list[Unlock] | None = None):
    return rules(
        [StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
        cards=[CardDef(CC, 100, cap=3, lines=(LineKey("c.1"), LineKey("c.2"), LineKey("c.3")),
                       outcome=Outcome(stores=(Amount(Y, Q),), lines=(LineKey("c.out"),)),
                       finished=Outcome(lines=(LineKey("c.fin"),))),
               CardDef(CU, 100, makes=(Flow(Y, 1000),), lines=(LineKey("cu.tap"),)),
               CardDef(CM, 100, makes=(Flow(Z, 1000),)),
               CardDef(CC2, 100, cap=5, outcome=Outcome(unlocks=(Unlock(UnlockKind.CARD, DL),))),
               CardDef(DL, 100)],
        triggers=[] if trigger_on is None else [
            TriggerDef(TRIG, AtLeast(CardCount(trigger_on), 2, 2), Outcome(lines=(LineKey("t.fired"),)))],
        opening=opening)


def test_a_capped_card_completes_at_each_boundary_in_the_mix():
    """Invariant 38: a capped card in the mix completes at each boundary, a COMPLETION at the exact second; completion n
    emits lines[n - 1], then its outcome's lines, and at the cap `finished`'s. Its outcome stores ran as rates."""
    r = world()
    s = with_mix(new_save(r), r, 0, {CC: 5000})
    assert next_event(s, r) == Event(200, EventKind.COMPLETION, 0, CC)
    step = advance_logged(s, r, 2000)
    assert keys(step.lines) == [(200, "c.1"), (200, "c.out"), (400, "c.2"), (400, "c.out"),
                                (600, "c.3"), (600, "c.out"), (600, "c.fin")]
    assert done(step.save, r, CC) == 3 and work(step.save, CC).rate == 0
    assert val(advance(s, r, 300), r, Y) == Q + Q // 2


def test_a_capped_card_completes_at_the_seconds_an_uncapped_one_crosses_its_boundaries():
    """"Completions": work is limited only at the cap, so no completion loses a partial second: at 30% a 100 s card
    completes at 334, 667 and 1000, the seconds the work first reaches 1, 2 and 3 boundaries (an uncapped card's count
    crosses at the same ones), with the work running through each boundary and clamped at the third, the cap."""
    r = world()
    s = with_mix(new_save(r), r, 0, {CC: 3000})
    step = advance_logged(s, r, 2000)
    assert [ln for ln in keys(step.lines) if ln[1].startswith("c.") and ln[1][2:].isdigit()] == [
        (334, "c.1"), (667, "c.2"), (1000, "c.3")]
    assert work(advance(s, r, 334), CC).start_value == 334 * 3000 > 100 * BP
    assert done(advance(s, r, 666), r, CC) == 1 and done(advance(s, r, 667), r, CC) == 2


@pytest.mark.parametrize("share", [5000, 3000, 3333, 2500, 1700, 7])
def test_capped_and_uncapped_cards_at_one_share_complete_at_the_same_seconds(share: int):
    """"Completions", REJECTED (a capped card's work limited at every completion): in one mix, a capped card's n-th
    COMPLETION and an uncapped card's n-th crossing both fall at ceil(n * work_s * BP / share), the first second the
    work has reached the n-th boundary; at the cap the work stops on the boundary exactly."""
    n_cap = 5
    r = rules([StoreDef(Y, 100 * Q, 0)],
              cards=[CardDef(CC, 100, cap=n_cap, outcome=Outcome(lines=(LineKey("c.out"),))), CardDef(CU, 100)])
    s = with_mix(new_save(r), r, 0, {CC: share, CU: share})
    due = [ceil_div(n * 100 * BP, share) for n in range(1, n_cap + 1)]
    step = advance_logged(s, r, due[-1] + 10)
    assert keys(step.lines) == [(t, "c.out") for t in due]
    for n, t in enumerate(due, 1):
        assert done(advance(s, r, t), r, CU) == n and done(advance(s, r, t - 1), r, CU) == n - 1
        assert done(advance(s, r, t), r, CC) == n
    assert work(step.save, CC).start_value == n_cap * 100 * BP and work(step.save, CC).rate == 0


@pytest.mark.parametrize("card", [CC, CU])
def test_a_tap_at_a_speed_that_does_not_divide_ends_exactly_on_its_boundary(card: CardId):
    """"Completions": a tap does exactly one completion, so the last partial second's overshoot is clamped at its
    boundary: at a hands speed of 30% a 100 s card takes 334 s and leaves its work on exactly one boundary, capped or
    not."""
    r = world()
    s = tap(new_save(r, (mul(LaneSpeed(HANDS), 3000, "slow"),)), r, 0, card)
    a = advance(s, r, 334)
    assert lane(a, HANDS).card is None and work(a, card).start_value == 100 * BP and done(a, r, card) == 1
    assert lane(advance(s, r, 333), HANDS).card == card


def test_an_uncapped_card_counts_its_completions_without_events():
    """Invariant 36: no event falls at an uncapped card's completion; its count is read off the work segment
    (CardCount = work // (work_s * BP)), and the mix emits none of its lines."""
    r = world()
    s = with_mix(new_save(r), r, 0, {CU: 5000})
    assert all(e.kind is not EventKind.COMPLETION for e in events(s, r))
    ev = next_event(s, r)
    assert ev is None or ev.time > 10_000
    step = advance_logged(s, r, 1000)
    assert keys(step.lines) == [] and done(step.save, r, CU) == 5
    assert done(advance(s, r, 399), r, CU) == 1 and done(advance(s, r, 400), r, CU) == 2


@pytest.mark.parametrize("share, second", [(5000, 400), (3000, 667), (BP, 200), (7000, 286)])
def test_an_order_on_a_mixed_count_fires_at_the_exact_second(share: int, second: int):
    """Invariant 37: CardCount is a solved subject; an order "cu completed twice: switch to m2" latches at the second
    the work crosses 2 * work_s * BP (ceil(2_000_000 / speed), no rounding carried per completion), not later."""
    r = world()
    s = save_mix(new_save(r), r, 0, {CM: BP}, "m2")
    s = with_mix(s, r, 0, {CU: share}, "m1")
    s = decide(s, r, 0, SetOrders((Order(AtLeast(CardCount(CU), 2, 2), SwitchMix(MixId("m2"))),)))
    assert next_event(s, r) == Event(second, EventKind.LATCH, 0, "0")
    before = advance(s, r, second - 1)
    assert running_mix(before, r) == MixId("m1") and done(before, r, CU) == 1
    at = advance(before, r, second)
    assert running_mix(at, r) == MixId("m2") and done(at, r, CU) == 2


@pytest.mark.parametrize("share, second", [(5000, 400), (3000, 667), (7000, 286)])
def test_an_at_most_on_a_count_releases_when_the_count_passes_its_release(share: int, second: int):
    """Invariant 37, "Completions": an AtMost on CardCount is true at count 0, stays latched while the count is at most
    its release (1) and releases at the second the work crosses the second boundary, the count passing the release: a
    LATCH event at that exact second."""
    r = world()
    s = with_mix(new_save(r), r, 0, {CU: share}, "m1")
    s = decide(s, r, 0, SetOrders((Order(AtMost(CardCount(CU), 0, 1), SwitchMix(MixId("m1"))),)))
    assert s.latches == (True,)
    assert next_event(s, r) == Event(second, EventKind.LATCH, 0, "0")
    before = advance(s, r, second - 1)
    assert before.latches == (True,) and done(before, r, CU) == 1
    assert advance(before, r, second).latches == (False,)


def test_a_trigger_on_a_count_fires_at_the_exact_second():
    """Invariant 37 for triggers: the count trigger fires at the second the mixed work crosses the boundary."""
    r = world(trigger_on=CU)
    s = with_mix(new_save(r), r, 0, {CU: 3000})
    step = advance_logged(s, r, 5000)
    assert keys(step.lines) == [(667, "t.fired")]


def test_a_capped_tap_completes_before_its_tap_is_done():
    """"Completions", events.EventKind: a tapped capped card's COMPLETION and its TAP_DONE fall at the same second,
    COMPLETION first (kind 2 before 3); the completion's lines land, the TAP_DONE adds none, and the lane is free."""
    r = world()
    s = tap(new_save(r), r, 0, CC)
    due = sorted(e for e in events(s, r) if e.time == 100)
    assert due == [Event(100, EventKind.COMPLETION, 0, CC), Event(100, EventKind.TAP_DONE, 0, HANDS)]
    step = advance_logged(s, r, 100)
    assert keys(step.lines) == [(100, "c.1"), (100, "c.out")]
    assert lane(step.save, HANDS).card is None and done(step.save, r, CC) == 1


def test_a_tap_of_a_capped_card_the_mix_half_did_completes_at_the_boundary():
    """Invariants 34, 38: the mix runs cc to half a bar; a tap finishes it, and the COMPLETION falls when the work
    reaches the boundary (150), whoever ran each half."""
    r = world()
    s = tap(with_mix(new_save(r), r, 0, {CC: 5000}), r, 100, CC)
    assert next_event(s, r) == Event(150, EventKind.COMPLETION, 0, CC)
    assert keys(advance_logged(s, r, 150).lines) == [(150, "c.1"), (150, "c.out")]


def test_an_uncapped_card_emits_its_line_when_a_tap_ends_at_a_completion():
    """CardDef.lines without a cap: the one key is emitted when a tap ends at a completion (TAP_DONE), however much of
    the bar the mix had done; a mix completion emits nothing."""
    r = world()
    s = with_mix(new_save(r), r, 0, {CU: 5000})
    step = advance_logged(tap(s, r, 100, CU), r, 1000)
    assert keys(step.lines) == [(150, "cu.tap")]


def test_a_mixed_capped_completion_makes_orders_evaluate():
    """"Caps", Outcome: orders and the queue evaluate after a completion's outcome, mixed as well as tapped. A true
    order to tap the locked dl cannot act; cc2's first completion in the mix unlocks dl and the order taps it at that
    second."""
    opening = [Unlock(UnlockKind.STORE, Y), Unlock(UnlockKind.STORE, Z), Unlock(UnlockKind.SKILL, K)] + [
        Unlock(UnlockKind.CARD, c) for c in (CC, CU, CM, CC2)]
    r = world(opening=opening)
    s = with_mix(new_save(r), r, 0, {CC2: BP})
    s = decide(s, r, 0, SetOrders((Order(AfterTime(0), TapCard(DL)),)))
    assert lane(advance(s, r, 99), HANDS).card is None
    assert lane(advance(s, r, 100), HANDS).card == DL
