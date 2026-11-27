"""Rule guards across edits, in the view, and past the firing cap (docs/design/rule-guards.md, "Contract (blind)",
statements 11 to 13; "Guards": editing a rule, at the firing cap; "A rule's states")."""
from ashfall_app.engine import (
    AfterTime, AtLeast, AtMost, Order, OrderState, Rules, Save, SetOrders, SwitchMix, TapCard, advance, decide, view,
)
from guards_world import (
    kills,
    ALWAYS, DOWN, IDLE, K, RM, RM2, UP, at_least, at_most, block_from, guard_on, guarded, guarded_latch, paused, rules,
    start, tick_at,
)

NEVER = AfterTime(10**9)

# ---- statement 11 -----------------------------------------------------------------------------------------------------

WHEN = at_most(3, 11)          # "T under 3, until over 11": on at T = 0, never let go below 12
GUARD = at_least(10, 5)        # "unless T is 10 or more, until under 5"
EDIT_AT = 13


def _rule() -> Order:
    return guarded(WHEN, SwitchMix(UP), GUARD)


def _mid_band() -> tuple[Rules, Save]:
    """The rule fills T from 0 (the player's DOWN empties it): the guard comes on at 10 (t = 10), and at 13 T is 7,
    inside both bands, with both latches on. Neither would be on if set afresh at 7."""
    r = rules(t0=0)
    s = advance(start(r, (_rule(),), active=DOWN), r, EDIT_AT)
    assert s.latches == (guarded_latch(True, (True,)),)
    assert view(s, r).running_mix == DOWN
    return r, s


def _set(r: Rules, s: Save, *orders: Order) -> Save:
    return decide(s, r, EDIT_AT, SetOrders(tuple(orders)))


@kills(9)
def test_an_equal_rule_keeps_its_when_latch_and_its_guard_latch():
    """Statement 11: SetOrders holding an order equal to the old one keeps both latches, kept in place, moved behind a
    new rule, or listed beside another; the rule stays paused."""
    r, s = _mid_band()
    other = Order(NEVER, SwitchMix(RM2))
    kept = guarded_latch(True, (True,))
    assert _set(r, s, _rule()).latches == (kept,)
    assert _set(r, s, other, _rule()).latches == (False, kept)
    after = _set(r, s, _rule(), other)
    assert after.latches == (kept, False)
    assert view(advance(after, r, EDIT_AT + 1), r).running_mix == DOWN


@kills(10)
def test_a_rule_edited_in_a_guard_or_an_action_is_latched_afresh():
    """Statement 11: an order that differs in a guard (its band, a second guard) or in its action is a new rule: every
    latch is set from its threshold alone at 13, where T is 7 (7 <= 3 is false, 7 >= 10 is false)."""
    r, s = _mid_band()
    for edited, fresh in (
        (guarded(WHEN, SwitchMix(UP), at_least(10, 4)), guarded_latch(False, (False,))),
        (guarded(WHEN, SwitchMix(UP), GUARD, at_least(20, 19)), guarded_latch(False, (False, False))),
        (guarded(WHEN, SwitchMix(UP), at_least(20, 19), GUARD), guarded_latch(False, (False, False))),
        (guarded(WHEN, SwitchMix(RM), GUARD), guarded_latch(False, (False,))),
        (guarded(at_most(3, 12), SwitchMix(UP), GUARD), guarded_latch(False, (False,))),
    ):
        assert _set(r, s, edited).latches == (fresh,), edited


@kills(8)
def test_an_edited_rules_latches_hold_where_their_thresholds_hold_now():
    """Statement 11: afresh means from the threshold, not off: a guard edited to "7 or more" holds at 7, and a `when`
    edited to "under 8" holds at 7."""
    r, s = _mid_band()
    assert _set(r, s, guarded(WHEN, SwitchMix(UP), at_least(7, 6))).latches == (guarded_latch(False, (True,)),)
    assert _set(r, s, guarded(at_most(8, 11), SwitchMix(UP), GUARD)).latches == (guarded_latch(True, (False,)),)


@kills(10, 19)
def test_dropping_a_rules_guards_makes_a_new_rule_with_a_bare_latch():
    """Statement 11 and "The saved shape": the same `when` and action with no guard is a different order, latched
    afresh, and its latch is a bare bool."""
    r, s = _mid_band()
    assert _set(r, s, Order(WHEN, SwitchMix(UP))).latches == (False,)


# ---- statement 12 -----------------------------------------------------------------------------------------------------

HOLDS = at_most(50, 51)   # T starts at 5 and stays under 50: latched throughout
NEVER_HOLDS = at_least(60, 59)


def _states(*orders: Order, k_cap: int = 10**6, at: int = 3) -> tuple[Rules, Save]:
    r = rules(t0=5, k_cap=k_cap)
    s = start(r, ())
    if k_cap == 1:
        s = decide(s, r, 0, TapCard(K))   # K completes at 1 and is dead from then on
    return r, decide(advance(s, r, at), r, at, SetOrders(orders))


@kills(15, 16)
def test_a_rule_with_when_on_and_a_guard_on_is_paused_not_outranked():
    """Statement 12: paused comes before outranked; an earlier rule holding the mix does not change it."""
    r, s = _states(Order(ALWAYS, SwitchMix(RM)), guarded(ALWAYS, SwitchMix(RM2), HOLDS))
    v = view(s, r)
    assert v.order_states == (OrderState.ON, paused())
    assert v.orders_on == (True, True) and guard_on(v, 1, 0) is True


@kills(14)
def test_waiting_and_passed_over_come_before_paused():
    """Statement 12: with `when` off the rule is waiting whatever its guard; with every action dead it is passed over."""
    r, s = _states(guarded(NEVER, SwitchMix(RM), HOLDS))
    v = view(s, r)
    assert v.order_states == (OrderState.WAITING,) and v.orders_on == (False,) and guard_on(v, 0, 0) is True
    r, s = _states(guarded(ALWAYS, TapCard(K), HOLDS), k_cap=1)
    assert view(s, r).order_states == (OrderState.PASSED_OVER,)


@kills(1, 15)
def test_a_rule_whose_guards_are_off_is_on_and_each_guard_reads_its_own_latch():
    """Statement 12: order_guards[i][j].on is guard j's latch, in list order; with none on, the rule is on."""
    r, s = _states(guarded(ALWAYS, SwitchMix(RM), NEVER_HOLDS, HOLDS), guarded(ALWAYS, TapCard(K), NEVER_HOLDS))
    v = view(s, r)
    assert v.order_states == (paused(), OrderState.ON)
    assert [guard_on(v, 0, 0), guard_on(v, 0, 1), guard_on(v, 1, 0)] == [False, True, False]
    assert v.running_mix == IDLE


# ---- statement 13 -----------------------------------------------------------------------------------------------------

def _capped(guard: AtLeast | AtMost, max_firings: int) -> tuple[Rules, Save]:
    """T rises one item a second from 0, crossing the guard's level at 10. Three triggers fire at 10 and one at 15."""
    r = rules(t0=0, t_rate=1, max_firings=max_firings, triggers=tick_at(10, 3) + tick_at(15))
    return r, start(r, (guarded(ALWAYS, SwitchMix(RM), guard),))


def _run(r: Rules, s: Save, until: int) -> tuple[list[object], int]:
    out: list[object] = []
    cur = s
    for t in range(until + 1):
        cur = advance(cur, r, t)
        out.append(view(cur, r).running_mix)
    return out, cur.cascade_count


@kills(17)
def test_a_guard_coming_on_past_the_firing_cap_waits_for_the_next_firing():
    """Statement 13: past the cap at 10 (two firings allowed, three triggers there), the guard coming on at 10 leaves
    the rule's mix running; it is seen at 15, where a trigger fires. Below the cap it hands over at 10."""
    r, s = _capped(block_from(10), 2)
    got, cascades = _run(r, s, 16)
    assert cascades >= 1   # the premise: 10 hit the cap
    assert got == [RM] * 15 + [IDLE] * 2
    r, s = _capped(block_from(10), 1000)
    assert _run(r, s, 16)[0] == [RM] * 10 + [IDLE] * 7


@kills(17)
def test_a_guard_letting_go_past_the_firing_cap_waits_for_the_next_firing():
    """Statement 13: "T is 8 or less" (release 9) lets go at 10, past the cap: the rule's mix comes at 15, not 10."""
    r, s = _capped(at_most(8, 9), 2)
    got, cascades = _run(r, s, 16)
    assert cascades >= 1
    assert got == [IDLE] * 15 + [RM] * 2
    r, s = _capped(at_most(8, 9), 1000)
    assert _run(r, s, 16)[0] == [IDLE] * 10 + [RM] * 7
