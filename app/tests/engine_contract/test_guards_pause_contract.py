"""Rule guards pause a rule and never let it go (docs/design/rule-guards.md, "Contract (blind)", statements 5 to 8;
"Guards"). Expected times are worked from the world's rates: T moves one item a second, so a level of n items is
reached at a whole second, and AtLeast lets go at the first second its store is under the release."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    CardId, Order, OrderState, Rules, Save, SwitchMix, TapCard, advance, advance_logged, value, view,
)
from contract_gen import few
from guards_world import (
    kills,
    ALWAYS, DOWN, IDLE, K, KL, RM, UP, W, X, Y, at_least, at_most, block_from, guarded, lane_card, paused, rules, start,
)


def _mixes(r: Rules, s: Save, until: int) -> list[object]:
    out: list[object] = []
    cur = s
    for t in range(until + 1):
        cur = advance(cur, r, t)
        out.append(view(cur, r).running_mix)
    return out


def _lanes(r: Rules, s: Save, until: int) -> list[CardId | None]:
    out: list[CardId | None] = []
    cur = s
    for t in range(until + 1):
        cur = advance(cur, r, t)
        out.append(lane_card(cur))
    return out


def _chase(v: int, gap: int, until: int) -> list[object]:
    """The running mix at each second when a rule switching to UP from T = 0, guarded by "T is v or more, until under
    v - gap", is the only rule and DOWN is the player's: the guard comes on at v, the player's mix takes T down, and the
    rule resumes at the first second T is under v - gap."""
    out: list[object] = []
    x, latch = 0, False
    for t in range(until + 1):
        latch = (x >= v) if (t == 0 or not latch) else not (x < v - gap)
        out.append(DOWN if latch else UP)
        x += -1 if latch else 1
    return out


# ---- statement 5 ------------------------------------------------------------------------------------------------------

@kills(2, 5)
def test_a_guard_on_a_rules_own_mix_hands_the_layer_over_and_back_at_its_band():
    """Statement 5: the rule's mix fills T; "unless T is 10 or more" (release 9) takes the layer away at 10, the
    player's mix runs T down, and the rule's mix comes back at the first second T is under 9 (T = 8 at 12), with no
    other event. On at 10, back at 12, away at 14, back at 16."""
    r = rules(t0=0)
    s = start(r, (guarded(ALWAYS, SwitchMix(UP), block_from(10)),), active=DOWN)
    got = _mixes(r, s, 17)
    assert got == [UP] * 10 + [DOWN, DOWN, UP, UP, DOWN, DOWN, UP, UP]
    assert got == _chase(10, 1, 17)


@kills(2, 5)
@few(12)
@given(gap=st.integers(1, 3), extra=st.integers(1, 25))
def test_a_boundary_chasing_rule_switches_only_at_its_guards_value_and_release(gap: int, extra: int):
    """Statement 5, as a property over the guard's level and band: the running mix is the rule's exactly while the
    guard's latch is off, the latch read off T as the note defines it."""
    v = gap + extra + 1
    r = rules(t0=0)
    s = start(r, (guarded(ALWAYS, SwitchMix(UP), at_least(v, v - gap)),), active=DOWN)
    until = v + 4 * (gap + 1) + 2
    assert _mixes(r, s, until) == _chase(v, gap, until)


@kills(5, 8, 23, 24)
def test_a_ready_tap_starts_at_the_instant_its_guard_lets_go():
    """Statement 5 for a tap: T falls from 12 under the player's DOWN; "unless T is 10 or more" holds from the start
    and lets go at 4 (T = 8). No tap of K starts before 4, and one starts at 4 with no decision or other event there."""
    r = rules(t0=12)
    s = start(r, (guarded(ALWAYS, TapCard(K), block_from(10)),), active=DOWN)
    assert _lanes(r, s, 6) == [None] * 4 + [K] * 3


@kills(23)
def test_a_guard_coming_on_stops_the_next_tap():
    """Statement 5: T rises from 5 under UP; from 10 (t = 5) no tap of K starts. K lands each second, so the lane is
    free from 5 on."""
    r = rules(t0=5)
    s = start(r, (guarded(ALWAYS, TapCard(K), block_from(10)),), active=UP)
    assert _lanes(r, s, 8) == [K] * 5 + [None] * 4


# ---- statement 6 ------------------------------------------------------------------------------------------------------

def _card_completions(r: Rules, s: Save, card: CardId) -> int:
    return next(cv.completions for cv in view(s, r).cards if cv.card == card)


@kills(6)
def test_a_tap_running_when_its_guard_comes_on_lands_as_it_would_have():
    """Statement 6: KL (10 s) starts at 0; the guard comes on at 5 (T reaches 10 under UP from 5). KL lands at 10, with
    the stores and completions a rule with no guard gives it at 10; no second KL starts."""
    r = rules(t0=5)
    s = start(r, (guarded(ALWAYS, TapCard(KL), block_from(10)),), active=UP)
    control = start(r, (Order(ALWAYS, TapCard(KL)),), active=UP)
    assert _lanes(r, s, 12) == [KL] * 10 + [None] * 3
    a, b = advance(s, r, 10), advance(control, r, 10)
    for store in (X, Y):
        assert value(a, r, store, 10) == value(b, r, store, 10)
    assert _card_completions(r, a, KL) == _card_completions(r, b, KL) == 1
    assert value(a, r, Y, 10) > value(advance(s, r, 9), r, Y, 9)   # the landing's outcome is there at 10


# ---- statement 7 ------------------------------------------------------------------------------------------------------

def _when_world(guard_level: int) -> tuple[Rules, Save, Save]:
    """W rises one item a second from 3; the rule's `when` is "W under 5, until over 15" (on at 0, lets go at 13). T
    rises one a second from 0; the guard "T is guard_level or less" (release one more) lets go at guard_level + 2.
    Returns the rules, the guarded save and the same rule with no guard."""
    r = rules(t0=0, t_rate=1, w0=3, w_rate=1)
    when = at_most(5, 15, W)
    s = start(r, (guarded(when, SwitchMix(RM), at_most(guard_level, guard_level + 1)),))
    return r, s, start(r, (Order(when, SwitchMix(RM)),))


def _when_trace(r: Rules, s: Save, until: int) -> list[bool]:
    out: list[bool] = []
    cur = s
    for t in range(until + 1):
        cur = advance(cur, r, t)
        out.append(view(cur, r).orders_on[0])
    return out


@kills(3, 4)
def test_a_paused_rules_when_latch_moves_as_it_would_with_no_guard():
    """Statement 7: the `when` latch reads `when` alone while the rule is paused; W does not depend on what runs, so
    the guarded and unguarded rule's `when` latches, and their logged rule changes, agree second by second."""
    for level in (8, 14):
        r, s, control = _when_world(level)
        assert _when_trace(r, s, 20) == _when_trace(r, control, 20) == [True] * 13 + [False] * 8
        log = [(c.time, c.on) for c in advance_logged(s, r, 20).rule_changes]
        assert log == [(c.time, c.on) for c in advance_logged(control, r, 20).rule_changes] == [(13, False)]


@kills(3)
def test_a_rule_paused_inside_its_band_resumes_when_the_guard_lets_go():
    """Statement 7: the guard lets go at 10, when W is 13: past `when`'s value (5), short of its release (15). The
    rule's mix runs from 10 though W never came back under 5, until `when` lets go at 13."""
    r, s, _ = _when_world(8)
    assert _mixes(r, s, 15) == [IDLE] * 10 + [RM] * 3 + [IDLE] * 3


@kills(4)
def test_a_rule_whose_until_is_reached_while_paused_is_waiting_after_the_guard_lets_go():
    """Statement 7: `when` lets go at 13 while the guard holds; the guard lets go at 16 and the rule stays off,
    waiting."""
    r, s, _ = _when_world(14)
    assert _mixes(r, s, 20) == [IDLE] * 21
    states = [view(advance(s, r, t), r).order_states[0] for t in (12, 13, 16, 20)]
    assert states == [paused(), OrderState.WAITING, OrderState.WAITING, OrderState.WAITING]


# ---- statement 8 ------------------------------------------------------------------------------------------------------

@kills(1, 7)
def test_with_two_guards_the_rule_resumes_when_the_second_lets_go():
    """Statement 8: T rises from 0; "T is 4 or less" lets go at 6, "T is 8 or less" at 10. The rule runs from 10, in
    either listing order."""
    r = rules(t0=0, t_rate=1)
    for guards in ((at_most(4, 5), at_most(8, 9)), (at_most(8, 9), at_most(4, 5))):
        s = start(r, (guarded(ALWAYS, SwitchMix(RM), *guards),))
        assert _mixes(r, s, 12) == [IDLE] * 10 + [RM] * 3


@kills(7)
def test_with_two_guards_either_one_latched_pauses_the_rule():
    """Statement 8: "T is 4 or less" lets go at 6 and "T is 8 or more" comes on at 8: the rule runs at 6 and 7 only."""
    r = rules(t0=0, t_rate=1)
    s = start(r, (guarded(ALWAYS, SwitchMix(RM), at_most(4, 5), at_least(8, 7)),))
    assert _mixes(r, s, 11) == [IDLE] * 6 + [RM] * 2 + [IDLE] * 4


@kills(7)
def test_a_guard_on_another_store_pauses_only_while_it_holds():
    """Statements 5 and 8: guards on two stores, T rising from 0 and W from 3: "W is 6 or less" (release 7) lets go at
    5, when W is 8, and "T is 2 or less" (release 3) at 4; the rule runs from 5."""
    r = rules(t0=0, t_rate=1, w0=3, w_rate=1)
    s = start(r, (guarded(ALWAYS, SwitchMix(RM), at_most(6, 7, W), at_most(2, 3)),))
    assert _mixes(r, s, 7) == [IDLE] * 5 + [RM] * 3
