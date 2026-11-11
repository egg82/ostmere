"""Invariant 35 and "Rate form": every line of a card runs at the running share. Its flows and XP are per hour of running
(under the modifiers aimed at them and the lane's speed); its lumps are per completion, so they run at the card's whole
work speed too, and a completion's inputs are paid in proportion to its work as the work is done, by whoever does it,
and never twice. The 1.5A sequence from DESIGN.txt ("REJECTED, AND WHY (cards)") is the first test."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, Amount, CardDef, CardId, Flow, FlowKind, LaneSpeed, Outcome, RateRef, Rules, RunKind, Save, StoreDef,
    StoreId, WorkRef, advance, explain, modified_rate, new_save, view, xp,
)
from cards_world import K, Q, cost, done, lane, make, mul, rules, tap, val, with_mix, work

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
C, F = CardId("c"), CardId("f")
A = Q
"""C's input per completion."""
B = 2 * Q
"""C's outcome store per completion."""
XP_H = 36_000
"""C's XP per hour at a full share: Q of XP over one full-speed completion of 100 s."""


def world():
    return rules([StoreDef(X, 100 * Q, 10 * Q), StoreDef(Y, 100 * Q, 0)],
                 cards=[CardDef(C, 100, skill=K, xp_per_hour=XP_H, inputs=(Amount(X, A),),
                                outcome=Outcome(stores=(Amount(Y, B),)))])


def test_the_one_and_a_half_A_sequence_charges_one_completion_once():
    """The rejected lump design's sequence, run against the rate form. C (input A per completion) runs in the mix at
    50% for half a completion's time: its bar is half full and A/2 has been drawn as a rate. The player taps C: nothing
    is taken at the start, and the tap runs the bar's remaining half, drawing the other A/2. It lands with that one
    completion having cost exactly A (not 1.5A) and paid out exactly B (not B/2 + B), and the mix carries on."""
    r = world()
    s = advance(with_mix(new_save(r), r, 0, {C: 5000}), r, 100)
    assert work(s, C).start_value == 50 * BP
    assert val(s, r, X) == 10 * Q - A // 2 and val(s, r, Y) == B // 2
    s = tap(s, r, 100, C)
    assert val(s, r, X) == 10 * Q - A // 2 and val(s, r, Y) == B // 2  # nothing taken or landed at the start
    a = advance(s, r, 150)
    assert done(a, r, C) == 1 and lane(a, HANDS).card is None
    assert val(a, r, X) == 10 * Q - A
    assert val(a, r, Y) == B
    nxt = advance(a, r, 350)  # the mix's next completion: 200 s at 50%, the same A and B again
    assert done(nxt, r, C) == 2 and val(nxt, r, X) == 10 * Q - 2 * A and val(nxt, r, Y) == 2 * B


def test_a_tap_takes_its_input_as_its_work_is_done():
    """"Rate form": no lump is taken at a start or landed at an end; a tap from an empty bar draws A / work_s per
    second and pays B / work_s per second, linearly, so at every second the store has moved in proportion to the work."""
    r = world()
    s = tap(new_save(r), r, 0, C)
    cur = s
    for t in (1, 2, 50, 99, 100):
        cur = advance(cur, r, t)
        assert val(cur, r, X) == 10 * Q - A * t // 100, t
        assert val(cur, r, Y) == B * t // 100, t
    assert val(advance(cur, r, 1000), r, X) == 10 * Q - A  # the tap ended at 100; nothing more is drawn


@pytest.mark.parametrize("share", [BP, 5000, 4000, 2500, 2000])
def test_one_completion_costs_and_pays_the_same_by_mix_or_by_tap(share: int):
    """Invariant 35: running C for one completion's work at any mix share (here shares where every number divides
    exactly, so no rounding enters) moves x by -A, y by +B and XP by XP_H * work_s / 3600 hours, exactly what a tap
    of one completion moves; the completion takes work_s * BP / share seconds."""
    r = world()
    secs = 100 * BP // share
    s = with_mix(new_save(r), r, 0, {C: share})
    mixed = advance(s, r, secs)
    tapped = advance(tap(new_save(r), r, 0, C), r, 100)
    for a in (mixed, tapped):
        assert done(a, r, C) == 1
        assert val(a, r, X) == 10 * Q - A and val(a, r, Y) == B
    assert xp(mixed, r, K, mixed.time) == xp(tapped, r, K, tapped.time) == XP_H * 100
    assert done(advance(s, r, secs - 1), r, C) == 0


@pytest.mark.parametrize("share", [BP, 5000, 3333, 7, 1])
def test_lump_lines_explain_as_a_quantity_over_work_s(share: int):
    """"Rate form", Explain: a lump line explains with base_per_hour the lump, base_den work_s and the running share;
    per_hour is the formula rounded once, up for an input and down for an outcome store, and modified_rate recomputes
    it from the Explanation's own fields. A non-zero input never rounds to free."""
    r = world()
    s = with_mix(new_save(r), r, 0, {C: share})
    i, o = cost(s, r, C, X), make(s, r, C, Y)
    assert (i.base_per_hour, i.base_den, i.share_bp, i.run.kind) == (A, 100, share, RunKind.FULL)
    assert (o.base_per_hour, o.base_den, o.share_bp) == (B, 100, share)
    assert i.per_hour == -((-A * share) // (100 * BP)) and i.per_hour > 0
    assert o.per_hour == B * share // (100 * BP)
    for e in (i, o):
        assert isinstance(e.ref, RateRef)
        assert modified_rate(e.ref, e.base_per_hour, e.share_bp, e.adds + e.muls, e.run, e.base_den) == e
    assert val(s, r, X) == 10 * Q and segment_rate(s, r, X) == -i.per_hour


def segment_rate(s: Save, r: Rules, store: StoreId):
    return next(ln.segment.rate for ln in view(s, r).ledger if ln.store == store)


def flow_world():
    """f: a flow on z, XP into k0, an input from x and an outcome store into y, each store once (validation)."""
    return rules([StoreDef(X, 100 * Q, 10 * Q), StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
                 cards=[CardDef(F, 100, skill=K, xp_per_hour=XP_H, makes=(Flow(Z, 1000),), inputs=(Amount(X, A),),
                                outcome=Outcome(stores=(Amount(Y, B),)))])


def test_a_work_modifier_scales_the_lumps_but_not_the_flows_or_the_xp():
    """"Rate form", REJECTED (WorkRef scaling a card's flows and XP): a flow is per hour of running and faster work is
    more completions, not more per hour. With WorkRef x0.5 a tap takes 200 s, the flow and the XP run at their own
    rates (and so make twice as much per completion), the lumps at half, and a completion still costs A and pays B. The
    flow's Explanation carries no WorkRef entry."""
    r = flow_world()
    s = tap(new_save(r, (mul(WorkRef(F), 5000, "slow"),)), r, 0, F)
    assert make(s, r, F, Z).per_hour == 1000 and not make(s, r, F, Z).muls
    assert explain(s, r, RateRef(F, FlowKind.XP)).per_hour == XP_H
    assert cost(s, r, F, X).per_hour == A // 200 and make(s, r, F, Y).per_hour == B // 200
    a = advance(s, r, 200)
    assert done(a, r, F) == 1 and lane(a, HANDS).card is None
    assert val(a, r, X) == 10 * Q - A and val(a, r, Y) == B
    assert val(a, r, Z) == 1000 * 200 and xp(a, r, K, 200) == XP_H * 200


def test_the_lane_speed_scales_the_flows_the_xp_and_the_lumps():
    """"Rate form": the lane's LaneSpeed joins every line on the lane. At x0.5 the flow and the XP halve, the lumps run
    over twice the time, so a completion still costs A and pays B while making and training what its 200 s of running
    at half rate give."""
    r = flow_world()
    s = tap(new_save(r, (mul(LaneSpeed(HANDS), 5000, "tired"),)), r, 0, F)
    assert make(s, r, F, Z).per_hour == 500 and explain(s, r, RateRef(F, FlowKind.XP)).per_hour == XP_H // 2
    assert cost(s, r, F, X).per_hour == A // 200 and make(s, r, F, Y).per_hour == B // 200
    a = advance(s, r, 200)
    assert val(a, r, X) == 10 * Q - A and val(a, r, Y) == B and val(a, r, Z) == 500 * 200
    assert xp(a, r, K, 200) == XP_H * 100


def test_inputs_round_up_and_outcomes_down_when_nothing_divides():
    """Invariant 11 for lump lines: with work_s 7 and lumps of Q + 1, a tap draws ceil((Q + 1) / 7) per second and pays
    floor((Q + 1) / 7): one completion's input is never below its lump, its outcome never above."""
    r = rules([StoreDef(X, 100 * Q, 10 * Q), StoreDef(Y, 100 * Q, 0)],
              cards=[CardDef(C, 7, inputs=(Amount(X, Q + 1),), outcome=Outcome(stores=(Amount(Y, Q + 1),)))])
    s = tap(new_save(r), r, 0, C)
    assert cost(s, r, C, X).per_hour == -((-(Q + 1)) // 7) and make(s, r, C, Y).per_hour == (Q + 1) // 7
    a = advance(s, r, 7)
    assert done(a, r, C) == 1
    drawn, paid = 10 * Q - val(a, r, X), val(a, r, Y)
    assert Q + 1 <= drawn < Q + 1 + 7
    assert Q + 1 - 7 < paid <= Q + 1


def test_a_work_modifier_slows_the_bar_and_its_lumps_together():
    """"Rate form": a card's lumps run under its work modifiers too (WorkRef, LaneSpeed), so a WorkRef x0.5 makes the
    tap take twice as long and draw half as fast: one completion still costs exactly A and pays exactly B. The entry
    is listed on the lump line's Explanation retargeted at its RateRef, source kept."""
    r = world()
    half = mul(WorkRef(C), 5000, "slow")
    s = tap(new_save(r, (half,)), r, 0, C)
    i = cost(s, r, C, X)
    assert i.per_hour == A // 200
    assert [(m.target, m.amount_bp, m.source) for m in i.muls] == [(RateRef(C, FlowKind.COST, X), 5000, "slow")]
    assert lane(advance(s, r, 199), HANDS).card == C
    a = advance(s, r, 200)
    assert lane(a, HANDS).card is None and done(a, r, C) == 1
    assert val(a, r, X) == 10 * Q - A and val(a, r, Y) == B


def test_tired_hands_halve_every_line_of_a_tap_and_the_xp_per_completion_holds():
    """"Speed": a LaneSpeed(HANDS) x0.5 joins every line on HANDS, the work, the lumps and the XP alike, so a tap of one
    completion takes 200 s and still moves x by -A, y by +B and XP by what an untired completion trains."""
    r = world()
    s = tap(new_save(r, (mul(LaneSpeed(HANDS), 5000, "tired"),)), r, 0, C)
    e = explain(s, r, RateRef(C, FlowKind.XP))
    assert e.per_hour == XP_H // 2 and e.muls[0].target == RateRef(C, FlowKind.XP)
    a = advance(s, r, 200)
    assert done(a, r, C) == 1 and val(a, r, X) == 10 * Q - A and val(a, r, Y) == B
    assert xp(a, r, K, 200) == XP_H * 100
