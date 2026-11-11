"""Invariant 34 and "One bar": a card has one cumulative work segment, advanced by a tap at a full share or by the mix
at the card's share, never both; on HANDS a tap yields the whole mix and runs the card from wherever its bar stands to
the next completion; the view says who runs it (DESIGN.txt, part "CARDS"; cards.CardDef, cards.LaneState, view.RunBy).
"""
import pytest

from ashfall_app.engine import (
    BP, HANDS, Amount, CardDef, CardId, Event, EventKind, Flow, InvalidVerbError, LaneBar, Outcome, RunBy, RunKind,
    StoreDef, StoreId, advance, explain_work, new_save, next_event, view,
)
from cards_world import Q, RACK, card_view, ceil_div, cost, done, lane, make, rules, tap, val, with_mix, work

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
C, M, R = CardId("c"), CardId("m"), CardId("r")
W = 100 * BP
"""One completion of a work_s 100 card, in work units."""


def world():
    return rules([StoreDef(X, 100 * Q, 50 * Q), StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
                 cards=[CardDef(C, 100, inputs=(Amount(X, Q),), outcome=Outcome(stores=(Amount(Y, 2 * Q),))),
                        CardDef(M, 100, makes=(Flow(Z, 1000),)),
                        CardDef(R, 100, lane=RACK, makes=(Flow(Z, 2000),))],
                 lanes=[RACK])


def test_a_mix_share_fills_the_bar_at_that_share():
    """"One bar", "Completions": a share s fills the card's work s / BP as fast as a tap, so a 50% card's bar fills at
    5000 work units per second and its next completion is 200 s away; the view says the mix runs it and claims no
    landing for it (a rule that takes the hands would yield the mix)."""
    r = world()
    s = with_mix(new_save(r), r, 0, {C: 5000, M: 5000})
    assert work(s, C).rate == 5000 and work(s, M).rate == 5000
    assert explain_work(s, r, C).per_hour == 5000 and explain_work(s, r, C).share_bp == 5000
    a = advance(s, r, 100)
    assert work(a, C).start_value == W // 2
    cv = card_view(a, r, C)
    assert cv is not None
    assert (cv.by, cv.share_bp, cv.run, cv.bar_total, cv.completes_at) == (RunBy.MIX, 5000, RunKind.FULL, W, None)
    assert cv.bar == work(a, C)


def test_a_tap_finishes_the_completion_the_mix_half_did():
    """Invariant 34: a tap started at work w lands when the work reaches the next multiple of work_s * BP above w. The
    mix ran c to half a bar in 100 s; the tap runs the other half at BP and ends (TAP_DONE) at 150, with the work
    exactly on the boundary, the lane free and the mix running c at its share again."""
    r = world()
    s = with_mix(new_save(r), r, 0, {C: 5000, M: 5000})
    s = tap(s, r, 100, C)
    assert next_event(s, r) == Event(150, EventKind.TAP_DONE, 0, HANDS)
    assert work(s, C).start_value == W // 2 and work(s, C).rate == BP
    a = advance(s, r, 150)
    assert work(a, C).start_value == W and done(a, r, C) == 1
    assert lane(a, HANDS).card is None
    assert work(a, C).rate == 5000 and work(a, M).rate == 5000


@pytest.mark.parametrize("t", [0, 1, 99, 100, 199, 200, 201, 350])
def test_a_tap_lands_at_the_next_boundary_above_the_bar(t: int):
    """Invariant 34 at every bar position, the boundary itself included: after t seconds of a 50% mix the work is
    5000 * t; a tap then ends at t + ceil((next multiple above it - w) / BP), with the work on that multiple. A bar
    standing exactly on a boundary has a whole completion ahead of it."""
    r = world()
    s = tap(with_mix(new_save(r), r, 0, {C: 5000}), r, t, C)
    w = 5000 * t
    target = (w // W + 1) * W
    end = t + ceil_div(target - w, BP)
    assert work(s, C).start_value == w
    assert next_event(s, r) == Event(end, EventKind.TAP_DONE, 0, HANDS)
    a = advance(s, r, end)
    assert work(a, C).start_value == target and lane(a, HANDS).card is None
    assert lane(advance(s, r, end - 1), HANDS).card == C


def test_a_tap_on_hands_yields_every_mix_card_and_runs_the_card_once():
    """"One bar": during a HANDS tap every mix card reads YIELDED with its share kept and makes nothing; the tapped
    card, though it is also in the mix, runs once, at BP (its explain share is BP, FULL), so its lines are its tap's
    alone: x falls at Q / 100 per second and y rises at 2Q / 100, the mix adding nothing."""
    r = world()
    s = tap(with_mix(new_save(r), r, 0, {C: 5000, M: 5000}), r, 10, C)
    m = make(s, r, M, Z)
    assert (m.run.kind, m.share_bp, m.per_hour) == (RunKind.YIELDED, 5000, 0)
    assert work(s, M).rate == 0
    c_cost, c_make = cost(s, r, C, X), make(s, r, C, Y)
    assert (c_cost.share_bp, c_cost.run.kind, c_cost.per_hour) == (BP, RunKind.FULL, Q // 100)
    assert (c_make.share_bp, c_make.run.kind, c_make.per_hour) == (BP, RunKind.FULL, 2 * Q // 100)
    assert val(advance(s, r, 20), r, X) - val(s, r, X) == -10 * (Q // 100)
    assert val(advance(s, r, 20), r, Y) - val(s, r, Y) == 10 * (2 * Q // 100)
    assert val(advance(s, r, 20), r, Z) == val(s, r, Z)


def test_the_view_says_who_runs_each_card():
    """CardView.by: TAP for the tapped card (its mix share shown, yielded with the rest of the mix), None for a mix
    card while the hands tap, MIX once the tap lands; LaneBar names the tapped card and when the tap ends."""
    r = world()
    s = tap(with_mix(new_save(r), r, 0, {C: 5000, M: 5000}), r, 100, C)
    c, m = card_view(s, r, C), card_view(s, r, M)
    assert c is not None and m is not None
    assert (c.by, c.share_bp, c.run, c.completes_at) == (RunBy.TAP, 5000, RunKind.YIELDED, 150)
    assert (m.by, m.share_bp, m.run) == (None, 5000, RunKind.YIELDED)
    assert next(b for b in view(s, r).lanes if b.lane == HANDS) == LaneBar(HANDS, C, 150, None)
    a = advance(s, r, 150)
    c2, m2 = card_view(a, r, C), card_view(a, r, M)
    assert c2 is not None and m2 is not None
    assert (c2.by, m2.by, c2.run, m2.run) == (RunBy.MIX, RunBy.MIX, RunKind.FULL, RunKind.FULL)
    assert next(b for b in view(a, r).lanes if b.lane == HANDS) == LaneBar(HANDS, None, None, None)


def test_a_card_nobody_runs_holds_its_bar():
    """"One bar": with no mix, a tap from 0 lands at work_s and the bar then holds still (rate 0): no-one runs the
    card, and the view says so (by None, completes_at None)."""
    r = world()
    a = advance(tap(new_save(r), r, 0, C), r, 5000)
    assert work(a, C).start_value == W and work(a, C).rate == 0
    cv = card_view(a, r, C)
    assert cv is not None and (cv.by, cv.completes_at, cv.share_bp, cv.run) == (None, None, 0, None)


def test_a_rack_tap_never_touches_the_players_time():
    """"Mixable", "Lanes": a card on another lane is tapped on its lane; the mix keeps running on HANDS beside it."""
    r = world()
    s = tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, R)
    assert lane(s, RACK).card == R and lane(s, HANDS).card is None
    assert make(s, r, M, Z).run.kind is RunKind.FULL and make(s, r, M, Z).per_hour == 1000
    assert make(s, r, R, Z).per_hour == 2000
    assert next_event(s, r) == Event(100, EventKind.TAP_DONE, 1, RACK)
    rv = card_view(s, r, R)
    assert rv is not None and rv.by is RunBy.TAP


def test_a_player_tap_on_a_busy_lane_is_refused():
    """Invariant 20 with cards: a lane holds one tap; the player's second tap on it raises InvalidVerbError."""
    r = world()
    s = tap(new_save(r), r, 0, C)
    with pytest.raises(InvalidVerbError):
        tap(s, r, 10, M)
