"""Invariant 156 (engine DESIGN.txt, "HELD SPEED, AND ENTRIES HELD BY STANDING ACTIONS": "The entries"): a standing action
holds, per entry, exactly one Modifier(target, ADD_BP, amount_bp, "held:" + id) while it is unlocked, not stopped by a
leave and not paused, and none otherwise; the target is LaneSpeed(lane) for a HeldSpeed and SideStrength(side) for a
WhileRunning, in declaration order, runners in rules order. The paused case is test_heldspeed_dry.py."""
from dataclasses import replace

from hypothesis import given, strategies as st

import ashfall_app.engine as eng
from ashfall_app.engine import (
    BP, HANDS, AfterTime, Leave, LaneSpeed, Modifier, ModifierKind, Outcome, SideStrength, SourceId, TriggerDef, TriggerId,
    advance, explain_strength, new_save, strength,
)
from town_mix_world import LA, LB, LC
from held_world import flat, kills
from heldspeed_world import (
    EAT1, EAT2, EATW, G, HELD, LP, LQ, eater, held_mods, held_of, held_speed, ja, lane_adds, maker, opening_without, side_entry, speed_mod, unlock_at, while_running, world,
)

EVERY_LANE = (HANDS, LA, LB, LC, LP, LQ)


@kills(2, 3, 4, 5)
def test_a_running_eater_holds_one_speed_entry_on_its_lane_and_nothing_on_any_other():
    """eat1 holds 5000 on lp and eat2 3000 on lq, each one add at the whole amount sourced held:<id>; no other lane, HANDS
    included, carries any, and the entry is the same at every instant while they run."""
    r = world()
    for t in (0, 500, 3000):
        s = advance(new_save(r), r, t)
        assert held_mods(s, r) == (speed_mod(EAT1, LP, 5000), speed_mod(EAT2, LQ, 3000))
        for lane in EVERY_LANE:
            assert lane_adds(s, r, lane) == {LP: [speed_mod(EAT1, LP, 5000)], LQ: [speed_mod(EAT2, LQ, 3000)]}.get(lane, [])


@kills(2, 3)
def test_entries_follow_declaration_order_within_a_runner_and_rules_order_across_runners():
    """eat1 declares lp 3000 then lq 2000, eat2 declares lq 1000: the stack holds them in that order, and the two on lq
    add."""
    r = replace(world(), standing=(
        eater(EAT1, held_speed(LP, 3000), held_speed(LQ, 2000)), eater(EAT2, held_speed(LQ, 1000)), maker(3)))
    s = new_save(r)
    assert held_mods(s, r) == (speed_mod(EAT1, LP, 3000), speed_mod(EAT1, LQ, 2000), speed_mod(EAT2, LQ, 1000))
    assert [m.amount_bp for m in lane_adds(s, r, LQ)] == [2000, 1000]


@kills(2, 5)
@given(amount=st.integers(1, 40_000))
def test_the_entry_is_the_declared_amount_whatever_it_is_and_always_an_add(amount: int):
    r = replace(world(), standing=(eater(EAT1, held_speed(LP, amount)), maker(3)))
    s = new_save(r)
    assert held_of(s, r, EAT1) == [Modifier(LaneSpeed(LP), ModifierKind.ADD_BP, flat(amount, BP), SourceId(HELD + EAT1))]


@kills(2, 9)
def test_a_standing_actions_side_entry_is_held_beside_its_speed_entry_in_declaration_order():
    """eatw declares a WhileRunning on g, then a HeldSpeed on lp: both held, the first on SideStrength(g)."""
    r = replace(world(), standing=(eng.StandingDef(EATW, **while_running(side_entry(G, 1500), held_speed(LP, 1000))),))
    s = new_save(r)
    side = Modifier(SideStrength(G), ModifierKind.ADD_BP, 1500, SourceId(HELD + EATW))
    assert held_mods(s, r) == (side, speed_mod(EATW, LP, 1000))
    assert strength(s, r, SideStrength(G)) == BP + 1500
    assert explain_strength(s, r, SideStrength(G)).adds == (side,)


@kills(2, 9)
def test_a_locked_standing_holder_holds_nothing_until_it_is_unlocked():
    r = replace(world(), standing=(eater(EAT1, held_speed(LP, 1000), side_entry(G, 700)), eater(EAT2, held_speed(LQ, 500))))
    r = replace(r, opening=opening_without(r, EAT1), triggers=(unlock_at(EAT1, 50),))
    for t in (0, 49):
        s = advance(new_save(r), r, t)
        assert [m.source for m in held_mods(s, r)] == [HELD + EAT2] and strength(s, r, SideStrength(G)) == BP
    s = advance(new_save(r), r, 50)
    assert [m.source for m in held_mods(s, r)] == [HELD + EAT1, HELD + EAT1, HELD + EAT2]
    assert strength(s, r, SideStrength(G)) == BP + 700


@kills(2)
def test_a_standing_holder_stopped_by_a_leave_holds_nothing_from_that_instant():
    """la's person leaves at 50 and the leave stops eat1: its entry goes at 50, eat2's stays."""
    leave = TriggerDef(TriggerId("leave"), AfterTime(50), Outcome(leaves=(Leave(LA, (EAT1,)),)))
    r = world((ja(), leave))
    before, at = advance(new_save(r), r, 49), advance(new_save(r), r, 50)
    assert [m.source for m in held_mods(before, r)] == [HELD + EAT1, HELD + EAT2]
    assert [m.source for m in held_mods(at, r)] == [HELD + EAT2]
