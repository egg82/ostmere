"""A failed tap (invariant 22, "Failed tap" in part "CARDS"): the player's tap of an unready card takes no time. Nothing
runs, nothing is taken, the lane stays free and the mix keeps running; the card's failed_line lands at the tap's
instant, and the decision's Step names the card (Step.failed), whatever its blocker: a short input, a false requires
or a Pause. An order, the queue or an Outcome never taps an unready card (invariant 23). A tap at speed 0, ready or
not, is refused."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, AfterTime, Amount, AtLeast, CardDef, CardId, EventKind, Flow, InvalidVerbError, LaneState, LineKey, Order,
    MixId, Outcome, QueueEntry, RunKind, SetOrders, SetQueue, StandingDef, StoreDef, Step, StoreId, StoreValue, SwitchMix,
    TapCard, WorkRef, ActionId, advance, advance_logged, decide, decide_logged, new_save, next_event,
)
from ashfall_app.engine import work as engine_work
from cards_world import Q, RACK, add, lane, make, rules, running_mix, save_mix, tap, view_of, with_mix

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
C, M, R, D, E, N, P, RS = (CardId(n) for n in ("c", "m", "r", "d", "e", "n", "p", "rs"))
GEN = ActionId("gen")


def world():
    """x short of c's and r's input; d waits on z; e is a blank ready card; n is unready with no failed line; p (200 s)
    costs y faster than gen refills it, so in the mix it runs y dry and is paused; rs, on the rack, starts c."""
    return rules(
        [StoreDef(X, 100 * Q, Q - 1), StoreDef(Y, 100 * Q, Q // 2), StoreDef(Z, 100 * Q, 0)],
        standing=[StandingDef(GEN, makes=(Flow(Y, 18_000),))],
        cards=[CardDef(C, 100, inputs=(Amount(X, Q),), failed_line=LineKey("c.failed")),
               CardDef(M, 100, makes=(Flow(Z, 1000),)),
               CardDef(R, 100, lane=RACK, inputs=(Amount(X, Q),), failed_line=LineKey("r.failed")),
               CardDef(D, 40, requires=(AtLeast(StoreValue(Z), 5 * Q, 5 * Q),), failed_line=LineKey("d.failed")),
               CardDef(E, 100),
               CardDef(N, 100, inputs=(Amount(X, Q),)),
               CardDef(P, 200, costs=(Flow(Y, 36_000),), failed_line=LineKey("p.failed")),
               CardDef(RS, 10, lane=RACK, cap=5, outcome=Outcome(starts=(C,)))],
        lanes=[RACK])


def said(step: Step) -> list[tuple[int, str, CardId | None]]:
    return [(ln.time, ln.key, ln.card) for ln in step.lines]


@pytest.mark.parametrize("card, key", [(C, "c.failed"), (D, "d.failed"), (R, "r.failed")],
                         ids=["short-input", "false-requires", "other-lane"])
def test_an_unready_tap_changes_nothing_and_says_its_line_at_once(card: CardId, key: str):
    """The save after the tap equals the save advanced to the tap's instant: every lane free, the mix running at its
    share, no TAP_DONE ahead; the failed line is the step's only line, at the tap's instant, written by the card."""
    r = world()
    s = with_mix(new_save(r), r, 0, {M: BP})
    step = decide_logged(s, r, 10, TapCard(card))
    assert step.save == advance(s, r, 10)
    assert all(ls == LaneState(ls.lane) for ls in step.save.lanes)
    assert make(step.save, r, M, Z).run.kind is RunKind.FULL
    nxt = next_event(step.save, r)
    assert nxt is None or nxt.kind is not EventKind.TAP_DONE
    assert said(step) == [(10, key, card)]
    assert step.failed == card


def test_an_unready_card_with_no_failed_line_says_nothing_and_is_still_named():
    r = world()
    s = new_save(r)
    step = decide_logged(s, r, 5, TapCard(N))
    assert step.save == advance(s, r, 5) and said(step) == [] and step.failed == N


def test_a_paused_card_fails_at_once_and_keeps_its_pause():
    """A tap of a card held by a Pause (its blocker the pause's store reaching resume_at) is a failed tap too."""
    r = world()
    a = advance(with_mix(new_save(r), r, 0, {P: BP}), r, 1000)
    blocker = engine_work.blocker(a, r, P)
    assert blocker is not None and blocker.condition == AtLeast(StoreValue(Y), a.pauses[0].resume_at, a.pauses[0].resume_at)
    step = decide_logged(a, r, 1000, TapCard(P))
    assert step.save == a and said(step) == [(1000, "p.failed", P)] and step.failed == P


def test_the_view_after_a_failed_tap_still_shows_what_stopped_it():
    """The card is not run by the tap, and its blocker is the one that failed the tap, unchanged."""
    r = world()
    s = new_save(r)
    before = view_of(s, r, C)
    after = view_of(decide_logged(s, r, 0, TapCard(C)).save, r, C)
    assert after.by is None and after.blocker == before.blocker is not None


def test_a_ready_tap_names_no_failure():
    r = world()
    step = decide_logged(new_save(r), r, 0, TapCard(E))
    assert step.failed is None and lane(step.save, HANDS).card == E


def test_tapping_unready_again_and_again_moves_nothing():
    """Tapping thirty times in a row leaves the save where advancing alone would, with one line per tap."""
    r = world()
    s = with_mix(new_save(r), r, 0, {M: BP})
    lines = 0
    for t in range(1, 31):
        step = decide_logged(s, r, t, TapCard(C))
        s, lines = step.save, lines + len(step.lines)
    assert s == advance(with_mix(new_save(r), r, 0, {M: BP}), r, 30) and lines == 30
    assert tap(s, r, 30, E) is not None


@pytest.mark.parametrize("verb", ["order", "queue"])
def test_an_order_or_the_queue_never_taps_an_unready_card(verb: str):
    """Invariant 23: an order or queue entry naming an unready card changes nothing and says nothing."""
    r = world()
    plan = (SetOrders((Order(AfterTime(0), TapCard(C)),)) if verb == "order"
            else SetQueue((QueueEntry(TapCard(C), AfterTime(10**9)),)))
    a = decide(new_save(r), r, 0, plan)
    step = advance_logged(a, r, 500)
    assert lane(a, HANDS) == lane(step.save, HANDS) == LaneState(HANDS)
    assert not any(ln.card == C for ln in step.lines)


def test_an_outcome_never_taps_an_unready_card():
    """Invariant 23 / Outcome.starts: a rack card's completion starting an unready hands card changes nothing."""
    r = world()
    step = advance_logged(tap(new_save(r), r, 0, RS), r, 10)
    assert lane(step.save, RACK) == LaneState(RACK) and lane(step.save, HANDS) == LaneState(HANDS)
    assert not any(ln.card == C for ln in step.lines)


STOP = (add(WorkRef(E), -BP, "stop"), add(WorkRef(N), -BP, "stop"))
"""Work speed 0 for e (ready) and n (unready)."""


@pytest.mark.parametrize("card", [E, N], ids=["ready", "unready"])
def test_a_tap_at_speed_zero_is_refused_for_the_player_and_does_nothing_for_an_order(card: CardId):
    """A tap at speed 0 (work.tap_seconds None), ready or not, is refused: InvalidVerbError from the player, nothing
    from an order or the queue (no tap, no line, the lane free). The control, e at a normal speed, taps."""
    r = world()
    s = new_save(r, STOP)
    assert engine_work.tap_seconds(s, r, card) is None
    with pytest.raises(InvalidVerbError):
        tap(s, r, 0, card)
    for plan in (SetOrders((Order(AfterTime(0), TapCard(card)),)), SetQueue((QueueEntry(TapCard(card), AfterTime(10**9)),))):
        a = decide(s, r, 0, plan)
        assert lane(a, HANDS) == LaneState(HANDS) and lane(advance(a, r, 500), HANDS) == LaneState(HANDS)
    assert lane(tap(new_save(r), r, 0, E), HANDS).card == E


def test_a_failed_tap_does_not_make_orders_and_the_queue_evaluate():
    """Invariant 24: a player's TapCard never evaluates, failed or not. The queue's head runs mix a; the player then
    switches to b, which sets only the mix that comes back; a failed tap leaves both as they were."""
    r = world()
    s = save_mix(save_mix(new_save(r), r, 0, {M: BP}, "a"), r, 0, {E: BP}, "b")
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(MixId("a")), AfterTime(10**9)),)))
    assert running_mix(s, r) == MixId("a")
    s = decide(s, r, 5, SwitchMix(MixId("b")))
    assert s.active == MixId("b") and running_mix(s, r) == MixId("a")
    step = decide_logged(s, r, 6, TapCard(C))
    assert step.failed == C and step.save == advance(s, r, 6)
    assert step.save.active == MixId("b") and running_mix(step.save, r) == MixId("a")
