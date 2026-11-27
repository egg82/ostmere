"""Rule guards, as a property over the latches (docs/design/rule-guards.md, "Contract (blind)", statements 5, 7, 8 and
12; "A rule's states", "Guards"). The player moves T up, down or not at all over drawn spans; one rule taps K, with a
`when` and one to three guards on T, each with its own band. The reference reads each latch off T second by second as
orders.AtLeast / AtMost define it, from its value alone at the start: the rule is on exactly while its `when` latch is
on and no guard's is. K takes one second, so the lane holds K at a second exactly while the rule is on there."""
from hypothesis import given

from ashfall_app.engine import AfterTime, OrderState, SwitchMix, TapCard, advance, decide, view
from contract_gen import few
from guards_world import (
    kills,
    K, Scene, guard_on, guarded, guards_of, lane_card, latch_series, path, paused, rules, scene_st, start, when_of,
)


@kills(1, 2, 3, 4, 7, 8, 15, 16, 23)
@few(15)
@given(scene=scene_st())
def test_a_rule_is_on_exactly_while_its_when_is_latched_and_no_guard_is(scene: Scene):
    """Statements 5, 7, 8, 12: at every second, the saved `when` latch and each guard latch equal the reference (a
    guard never moves the `when` latch, and each guard keeps its own band); the lane holds K exactly while the rule is
    on; view.orders_on is the `when` latch, view.order_guards[0][j].on guard j's latch, and view.order_states is
    waiting with `when` off, paused with `when` on and a guard on, else on."""
    t0, segments, when, guards = scene
    p = path(t0, segments)
    when_ref = (tuple(True for _ in p.values) if isinstance(when, AfterTime) else latch_series(when, p.values))
    guard_ref = [latch_series(g, p.values) for g in guards]
    r = rules(t0=t0)
    switches = dict(p.switches)
    cur = start(r, (guarded(when, TapCard(K), *guards),), active=switches[0])
    for t in range(len(p.values)):
        if t:
            cur = advance(cur, r, t)
            if t in switches:
                cur = decide(cur, r, t, SwitchMix(switches[t]))
        g_now = tuple(g[t] for g in guard_ref)
        on = when_ref[t] and not any(g_now)
        latch = cur.latches[0]
        assert (when_of(latch), guards_of(latch)) == (when_ref[t], g_now), (t, p.values[t])
        assert (lane_card(cur) == K) == on, (t, p.values[t])
        v = view(cur, r)
        assert v.orders_on[0] == when_ref[t]
        assert tuple(guard_on(v, 0, j) for j in range(len(guards))) == g_now
        expected = OrderState.WAITING if not when_ref[t] else paused() if any(g_now) else OrderState.ON
        assert v.order_states[0] == expected, t
