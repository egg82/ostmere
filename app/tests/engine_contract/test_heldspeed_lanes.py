"""Invariants 157 and 159 and the amended 114 (engine DESIGN.txt, "HELD SPEED ..."): a HeldSpeed(l, A) held at share h
changes every make, cost and XP line of a runner on lane l and every card's work there exactly as
Modifier(LaneSpeed(l), ADD_BP, A * h // BP) written into save.modifiers by hand would, and no line on another lane, HANDS
included; no LaneState.speed and no save.modifiers ever holds a held entry; only the lines on a HeldSpeed's lane list that
entry, and no WhileRunning's entry is listed by a rate, work or threat explanation."""
from dataclasses import replace

from hypothesis import given, strategies as st

import ashfall_app.engine as eng
from ashfall_app.engine import (
    BP, HANDS, CardId, CardShare, FlowKind, Mix, SaveMix, LaneSpeed, Modifier, ModifierKind, RateRef, SideStrength, SourceId, StoreId, ThreatStrength,
    TapCard, advance, explain_strength, explain_work, new_save, value, view,
)
from town_mix_world import A1, TM, X
from held_world import flat, kills
from heldspeed_world import (
    EAT1, EAT2, EATW, G, GS, HELD, INP, LP, LQ, OUT, OUT2, WOLF, WP, WQ, after, at, by_hand, eater, held_mods, held_of, held_speed, hands_mix, ja, maker, plain, rate, readings, side_entry, speed_mod, tapped, world,
)

TIMES = (1, 30, 59, 600)
H2 = CardId("h2")


def twin_of(r: eng.Rules, *cards: CardId, mods: tuple[Modifier, ...]) -> tuple[eng.Rules, eng.Save]:
    p = plain(r)
    return p, tapped(p, *cards, mods=mods)


@kills(3, 4)
def test_every_line_on_a_lane_reads_the_entry_as_the_same_rules_with_it_written_by_hand():
    """wp (make, cost, xp, work) on lp and wq on lq, with eat1 and eat2 held: every reading equals the entry-free rules
    carrying +5000 on lp and +3000 on lq in save.modifiers, at each sampled instant. The control: with no entries at all the
    readings are different, so the equality is not vacuous."""
    r = world()
    s = tapped(r, WP, WQ)
    twin_r, twin = twin_of(r, WP, WQ, mods=(by_hand(LP, 5000), by_hand(LQ, 3000)))
    bare_r, bare = twin_of(r, WP, WQ, mods=())
    for t in TIMES:
        assert readings(s, r, t) == readings(twin, twin_r, t), t
        assert readings(s, r, t) != readings(bare, bare_r, t), t


@kills(3, 4)
def test_every_line_on_the_lane_lists_the_entry_among_its_adds_and_no_line_of_another_lane_does():
    r = world()
    s = advance(tapped(r, WP, WQ), r, 30)
    lp_lines = (rate(s, r, WP, FlowKind.MAKE, OUT), rate(s, r, WP, FlowKind.COST, INP), rate(s, r, WP, FlowKind.XP),
                explain_work(s, r, WP))
    for e in lp_lines:
        assert at(e, speed_mod(EAT1, LP, 5000)) in e.adds and at(e, speed_mod(EAT2, LQ, 3000)) not in e.adds
    e = rate(s, r, WQ, FlowKind.MAKE, OUT2)
    assert at(e, speed_mod(EAT2, LQ, 3000)) in e.adds and at(e, speed_mod(EAT1, LP, 5000)) not in e.adds
    w = explain_work(s, r, WQ)
    assert w.adds.count(at(w, speed_mod(EAT2, LQ, 3000))) == 1


@kills(5)
def test_the_entry_is_an_add_beside_another_add_and_a_factor_on_the_lane():
    """lp already carries a hand add of 2000 and a factor of two: the held 5000 adds to the 2000 before the factor, as it
    would by hand (a multiplier of BP + 5000 would give a different speed)."""
    factor = Modifier(LaneSpeed(LP), ModifierKind.MUL_BP, 2 * BP, SourceId("gear"))
    mods = (by_hand(LP, 2000), factor)
    r = world()
    s = tapped(r, WP, mods=mods)
    twin_r, twin = twin_of(r, WP, mods=(*mods, by_hand(LP, 5000)))
    for t in TIMES:
        assert readings(s, r, t) == readings(twin, twin_r, t), t
    assert held_of(s, r, EAT1) == [speed_mod(EAT1, LP, 5000)]


@kills(3)
def test_no_line_on_another_lane_changes_and_hands_and_a_ruled_lane_keep_their_speed():
    """With only eat1 (lp) held: wq (lq), the hands' tap of h2, a hands mix of gs and la's town share all read as in the
    rules where nothing is held."""
    r = replace(world((ja(),)), standing=(eater(EAT1, held_speed(LP, 5000)), maker(3)))
    plain_r = plain(r)

    def play(rules: eng.Rules) -> eng.Save:
        return after(new_save(rules), rules, TapCard(WQ), TapCard(H2), SaveMix(Mix(TM, (CardShare(A1, 4000),))))

    s, p = play(r), play(plain_r)
    for t in TIMES:
        a, b = advance(s, r, t), advance(p, plain_r, t)
        assert value(a, r, OUT2, t) == value(b, plain_r, OUT2, t) > 0
        assert value(a, r, X, t) == value(b, plain_r, X, t) > 0
        cva = next(c for c in view(a, r).cards if c.card == H2)
        cvb = next(c for c in view(b, plain_r).cards if c.card == H2)
        assert (cva.bar, cva.completes_at) == (cvb.bar, cvb.completes_at)
    assert [m for m in held_mods(s, r) if m.target == LaneSpeed(HANDS)] == []


@kills(3, 13)
def test_a_hands_tap_takes_the_same_time_whatever_a_heldspeed_does_around_it():
    """gs (100 s on HANDS, itself a holder of a HeldSpeed on lp) is tapped at 0 while eat1 and eat2 run, and again while
    eat1 is unlocked only at 40: its landing and bar equal the rules with no entry anywhere."""
    base = world()
    r2 = replace(base, standing=(eater(EAT1, held_speed(LP, 5000)), maker(3)))
    r2 = replace(r2, opening=tuple(eng.Unlock(eng.UnlockKind.CARD, c.id) for c in r2.cards), triggers=(
        eng.TriggerDef(eng.TriggerId("late"), eng.AfterTime(40), eng.Outcome(unlocks=(eng.Unlock(eng.UnlockKind.ACTION, EAT1),))),))
    for r in (base, r2):
        s, p_r = tapped(r, GS), plain(r)
        p = tapped(p_r, GS)
        for t in (0, 39, 40, 41, 99):
            a, b = advance(s, r, t), advance(p, p_r, t)
            cva = next(c for c in view(a, r).cards if c.card == GS)
            cvb = next(c for c in view(b, p_r).cards if c.card == GS)
            assert (cva.bar, cva.completes_at) == (cvb.bar, cvb.completes_at) and cva.completes_at == 100, t
        assert advance(s, r, 100).cards == advance(p, p_r, 100).cards


@kills(13)
def test_no_lane_state_and_no_modifier_of_a_save_ever_holds_a_held_entry():
    """Taps on lp (a project lane) and HANDS (gs) started while the eaters run, and read over the following instants."""
    r = world()
    s = tapped(r, WP, WQ, GS)
    for t in (0, 1, 50, 2000):
        a = advance(s, r, t)
        assert a.modifiers == ()
        for lane in a.lanes:
            assert all(not m.source.startswith(HELD) for m in lane.speed or ()), (lane.lane, t)
    assert any(lane.card == GS for lane in s.lanes)


@kills(3, 9)
def test_only_the_lines_on_a_heldspeeds_lane_list_its_entry_and_no_rate_work_or_threat_lists_a_whilerunnings():
    """eatw holds a side entry on g and a speed entry on lq; eat1 a speed entry on lp. Every rate and work line of wp lists
    eat1's and none of eatw's; wq's lists eatw's speed entry only; the standing runners' own lines list neither; the threat
    and g's strength carry no speed entry; the side entry is on g alone."""
    r = replace(world(), standing=(
        eater(EAT1, held_speed(LP, 5000)), eater(EATW, held_speed(LQ, 2000), side_entry(G, 1500)), maker(3)))
    s = advance(tapped(r, WP, WQ), r, 30)
    side = Modifier(SideStrength(G), ModifierKind.ADD_BP, 1500, SourceId(HELD + EATW))

    def listed(e: eng.Explanation) -> list[Modifier]:
        return [m for m in (*e.adds, *e.muls) if m.source.startswith(HELD)]

    wp = [rate(s, r, WP, FlowKind.MAKE, OUT), rate(s, r, WP, FlowKind.COST, INP), rate(s, r, WP, FlowKind.XP),
          explain_work(s, r, WP)]
    assert [listed(e) for e in wp] == [[at(e, speed_mod(EAT1, LP, 5000))] for e in wp]
    wq = (rate(s, r, WQ, FlowKind.MAKE, OUT2), explain_work(s, r, WQ))
    assert [listed(e) for e in wq] == [[at(e, speed_mod(EATW, LQ, 2000))] for e in wq]
    for ref in (RateRef(EAT1, FlowKind.COST, StoreId("stew")), RateRef(eng.ActionId("mk"), FlowKind.MAKE, StoreId("stew"))):
        assert listed(eng.explain(s, r, ref)) == []
    assert explain_strength(s, r, SideStrength(G)).adds == (side,)
    threat = explain_strength(s, r, ThreatStrength(WOLF))
    assert threat.adds == () and threat.muls == () and threat.value == BP


@kills(3, 4, 14)
@given(share=st.integers(1, BP))
def test_a_cards_heldspeed_at_a_fractional_share_floors_once_and_reads_as_the_entry_by_hand(share: int):
    """gs (a HeldSpeed of 4000 on lp) in the running hands' mix at `share`: one entry of 4000 * share // BP, rounded down,
    on lp, and wp's lines read as with that add in save.modifiers."""
    r = replace(world(), standing=(maker(3),))
    s = after(tapped(r, WP), r, *hands_mix((GS, share)))
    assert held_of(s, r, GS) == [speed_mod(GS, LP, flat(4000, share))]
    twin_r = plain(r)
    twin = after(tapped(twin_r, WP, mods=(by_hand(LP, flat(4000, share)),)), twin_r, *hands_mix((GS, share)))
    assert readings(s, r, 40) == readings(twin, twin_r, 40)


@kills(14)
def test_a_share_that_rounds_up_or_to_nearest_still_floors():
    """4000 * 3337 / BP = 1334.8: floor 1334, ceil and nearest 1335."""
    r = replace(world(), standing=(maker(3),))
    s = after(new_save(r), r, *hands_mix((GS, 3337)))
    assert [m.amount_bp for m in held_of(s, r, GS)] == [1334]
