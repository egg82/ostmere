"""Invariants 158 and 161, the directed halves (engine DESIGN.txt, "HELD SPEED ...": "The dry rule is unchanged"): each pause
at a dry instant is picked from the stack the pauses before it leave, so a paused eater's lane speed has left before the next
consumer is chosen; and a resume rebuilds every line on the eater's lanes at that instant, so what advance() produces from
there on is what the entry written by hand from that instant would give."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, CardDef, CardId, Flow, Rules, Save, advance, next_event, per_hour, value, value_at, view,
)
from held_world import kills
from heldspeed_world import (
    EAT1, EAT2, LP, LQ, OUT2, STEW, WP, WQ, by_hand, dry_instant, eater, eaters_paused, held_speed, maker, plain, resumed, stew_world,
    tapped, while_running, world,
)

WM = CardId("wm")
MAKE_RATE = 18
EAT_COST = 20


def feeder_world() -> tuple[Rules, Save]:
    """wm on lq makes stew at 18 an hour (raised to 23.4 while eat2 runs); eat1 and eat2 eat 20 an hour each. Running
    all three the store loses 16.6 an hour; with eat2 paused its lane's speed leaves, so wm falls to 18 and the net is
    -2, still dry. An eater picked from the stack as it stood before eat2's pause would see +3.4 and stop there."""
    r = world(standing=(eater(EAT1, held_speed(LP, 5000), cost=EAT_COST), eater(EAT2, held_speed(LQ, 3000), cost=EAT_COST)),
              stew=Q)
    r = replace(r, cards=(*r.cards, CardDef(WM, 20000, lane=LQ, makes=(Flow(STEW, per_hour(MAKE_RATE)),))))
    return r, tapped(r, WM)


CE, CW = CardId("ce"), CardId("cw")


def fed_worker_world() -> tuple[Rules, Save]:
    """ce (a tap on lq, the lane the dry rule reaches first) eats 20 stew an hour and holds 5000 on lp; cw on lp eats 20 an
    hour at its lane's speed, so 30 while ce runs; mk makes 15. Pausing ce alone leaves -5, so cw is paused too."""
    r = world(standing=(maker(15),), stew=Q)
    ce = CardDef(CE, 20000, lane=LQ, costs=(Flow(STEW, per_hour(20)),), **while_running(held_speed(LP, 5000)))
    cw = CardDef(CW, 20000, lane=LP, costs=(Flow(STEW, per_hour(20)),))
    r = replace(r, cards=(*r.cards, ce, cw))
    return r, tapped(r, CE, CW)


@kills(7)
def test_the_second_pause_is_read_under_the_stack_the_first_pause_leaves():
    """Both are paused, each Pause's level one hour of its consumer's cost (as the drains part words it): cw's is read
    after ce's pause took ce's speed off lp, so 20 items, not the 30 it ate while ce ran."""
    r, s = fed_worker_world()
    d = dry_instant(r, s)
    assert eaters_paused(d) == {CE, CW}
    assert {p.runner: p.resume_at for p in d.pauses} == {CE: 20 * Q, CW: 20 * Q}
    r, s = feeder_world()
    assert eaters_paused(dry_instant(r, s)) == {EAT1, EAT2}


@kills(8)
def test_a_resumed_eaters_lane_works_at_the_raised_speed_from_the_resume_instant_on():
    """m = 3: eat2 resumes at the instant its Pause ends; with no other event before T + d, wq's store gains 13000 / BP
    of a second's work a second over d, and its work bar as fast as the same lane under the entry by hand."""
    r, s = stew_world(3)
    n = resumed(r, dry_instant(r, s), EAT2)
    ev = next_event(n, r)
    assert ev is not None
    d = min(1000, ev.time - n.time - 1)
    assert d > 100
    later = advance(n, r, n.time + d)
    assert abs(value(later, r, OUT2, n.time + d) - value(n, r, OUT2, n.time) - d * Q * (BP + 3000) // BP) <= d

    ref_r = plain(r)
    ref = tapped(ref_r, WP, WQ, mods=(by_hand(LP, 5000), by_hand(LQ, 3000)))
    assert abs(bar_gain(n, r, n.time, n.time + d) - bar_gain(ref, ref_r, 100, 100 + d)) <= 2


def bar_gain(save: Save, rules: Rules, t0: int, t1: int) -> int:
    """How far wq's work bar moves from t0 to t1, each end read from advance()."""
    def bar(t: int) -> int:
        x = advance(save, rules, t)
        return value_at(next(c.bar for c in view(x, rules).cards if c.card == WQ), t)
    return bar(t1) - bar(t0)
