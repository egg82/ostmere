"""A guard pauses the whole rule, fallbacks included (docs/design/rule-guards.md, "Contract (blind)", statement 19;
"Or else": "a fallback is for an action that cannot start, never for a guard that blocks"). T rises one item a second;
the guard "T is g or less" (released one item past) holds from the start and lets go at second g + 2."""
from hypothesis import given, strategies as st

from ashfall_app.engine import AtLeast, AtMost, QUANTITY_SCALE as Q, StoreValue, SwitchMix, TapCard
from contract_gen import few
from guards_world import kills
from or_else_world import A1, A2, ALWAYS, G1, M1, M2, PL, T, Z, lanes, mixes, rule, rules, start


def _low(g: int) -> AtMost:
    return AtMost(StoreValue(T), g * Q, (g + 1) * Q)


@kills(11, 12)
def test_no_listed_tap_starts_while_a_guard_holds_whichever_could():
    """Statement 19: A1 (ready from 3) and A2 (ready) both could start; the guard holds to 5, so neither does. At 6 A1,
    the first, starts."""
    r = rules(t_rate=1, w_rate=1, req={A1: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),), _low(4)),))
    assert lanes(r, s, 9) == [None] * 6 + [A1] * 4


@kills(11, 12)
def test_a_guard_does_not_send_the_rule_to_its_fallback():
    """Statement 19: A1 is not ready until 8, A2 is; with the guard on, the fallback does not run for it either. At 6 the
    guard lets go and A2, the first that can start, runs; A1 takes over at 8."""
    r = rules(t_rate=1, w_rate=1, req={A1: 8})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),), _low(4)),))
    assert lanes(r, s, 10) == [None] * 6 + [A2] * 2 + [A1] * 3


@kills(11, 12)
def test_a_later_rule_runs_while_the_guarded_rule_is_paused():
    """Statement 19: a paused rule takes nothing from the lane; the later rule's Z runs until the guard lets go at 6."""
    r = rules(t_rate=1, w_rate=1, req={A1: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),), _low(4)), rule(ALWAYS, TapCard(Z))))
    assert lanes(r, s, 8) == [Z] * 6 + [A1] * 3


@kills(11, 12)
def test_a_guard_coming_on_hands_the_layer_over_though_a_fallback_could_run():
    """Statement 19 for mixes: "T is 3 or more" comes on at 3. M1 (cap 2) runs 0 to 1, greys at 2 and M2, the fallback,
    runs at 2; at 3 the guard comes on and the player's mix runs, M2 not being able to run for the paused rule."""
    r = rules(t_rate=1, cap={G1: 2})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),), AtLeast(StoreValue(T), 3 * Q, 2 * Q)),))
    assert mixes(r, s, 6) == [M1, M1, M2, PL, PL, PL, PL]


@kills(11, 12)
@few(40)
@given(g=st.integers(1, 5), n1=st.integers(0, 8), n2=st.integers(0, 8))
def test_a_paused_rule_starts_nothing_and_resumes_with_the_first_action_that_can(g: int, n1: int, n2: int):
    """Statement 19, for every guard level and every readiness: nothing starts before the guard lets go at g + 2; from
    then the lane runs the first of A1, A2 whose need is met."""
    needs = {A1: n1, A2: n2}
    r = rules(t_rate=1, w_rate=1, req={c: n for c, n in needs.items() if n})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),), _low(g)),))
    want = [None if t < g + 2 else next((c for c, n in needs.items() if t >= n), None) for t in range(11)]
    assert lanes(r, s, 10) == want
