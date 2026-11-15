"""A rule of taps does the first of its actions that can start (docs/design/rule-guards.md, "Contract (blind)",
statements 15, 16 and 17; "Or else": can act, the rule's action, a better action coming back, none can act). In the
world W rises one item a second, so a tap that needs "W is n or more" is ready from second n; every tap here takes one
second unless said, so a lane read at second t shows the tap started at t (or at t - 1 and landing now)."""
from hypothesis import given, strategies as st

from ashfall_app.engine import CardId, Rules, Save, TapCard
from contract_gen import few
from guards_world import kills
from or_else_world import (
    A1, A2, A3, ALWAYS, D, Z, lanes, rule, rules, start, view_at,
)


def _first_ready(t: int, *needs: tuple[CardId, int]) -> CardId | None:
    """The first card, in list order, whose need is met at second t (None if none)."""
    return next((c for c, n in needs if t >= n), None)


# ---- statement 15 -----------------------------------------------------------------------------------------------------

@kills(1, 2, 18)
def test_an_unready_first_action_is_passed_over_for_the_second():
    """Statement 15: A1 needs W of 5, A2 is ready. A2 runs for seconds 0 to 4; A1, now ready and listed first, starts at
    5 as A2 lands."""
    r = rules(w_rate=1, req={A1: 5})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 8) == [A2] * 5 + [A1] * 4


@kills(1, 2)
def test_with_both_ready_the_first_action_starts():
    """Statement 15: both ready from the start: A1 each second, A2 never."""
    r = rules(w_rate=1)
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 5) == [A1] * 6


@kills(18)
def test_a_dead_first_action_is_passed_over_for_the_second():
    """Statement 15 with "can act" as a card's own: A1 is capped at one completion, so it runs 0 to 1, completes and is
    dead; A2 runs from 1 though A1 is listed first."""
    r = rules(cap={A1: 1})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 4) == [A1, A2, A2, A2, A2]


@kills(1, 2, 6, 8, 18)
@few(40)
@given(n1=st.integers(0, 6), n2=st.integers(0, 6), n3=st.integers(0, 6))
def test_the_rule_runs_the_first_listed_tap_that_is_ready_at_each_second(n1: int, n2: int, n3: int):
    """Statement 15 and 17, for every readiness: at second t the lane runs the first of A1, A2, A3 whose W need (0: none)
    is met, and when none is, runs nothing until the first becomes ready, at that second."""
    needs = {A1: n1, A2: n2, A3: n3}
    r = rules(w_rate=1, req={c: n for c, n in needs.items() if n})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2), TapCard(A3))),))
    want = [_first_ready(t, *needs.items()) for t in range(9)]
    assert lanes(r, s, 8) == want


# ---- statement 16 -----------------------------------------------------------------------------------------------------

@kills(3, 4)
def test_a_fallback_running_lands_when_the_first_action_turns_ready_and_the_first_starts_then():
    """Statement 16: A2 takes 5 s and starts at 0; A1 turns ready at 2. A2 lands at 5 as it would have (one completion
    at 5, none after) and A1 starts at 5."""
    r = rules(w_rate=1, req={A1: 2}, dur={A2: 5})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 8) == [A2] * 5 + [A1] * 4
    for t, done in ((4, 0), (5, 1), (8, 1)):
        assert _completions(r, s, t, A2) == done


@kills(3, 4)
def test_a_fallback_run_as_a_rate_lands_at_its_next_completion():
    """Statement 16, "a fallback that runs as a rate": A2 (3 s, uncapped, no inputs: a repeating tap) is on its second
    completion when A1 turns ready at 4; it lands at its next completion, 6, and A1 starts then."""
    r = rules(w_rate=1, req={A1: 4}, dur={A2: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 8) == [A2] * 6 + [A1] * 3
    assert _completions(r, s, 6, A2) == 2


@kills(3, 4)
@few(30)
@given(d=st.integers(2, 5), early=st.integers(1, 5))
def test_the_first_action_starts_at_the_landing_after_it_turns_ready(d: int, early: int):
    """Statement 16, for every length of the running fallback and every second A1 turns ready inside it: A2 runs to its
    landing at d and A1 starts there."""
    n = min(early, d)
    r = rules(w_rate=1, req={A1: n}, dur={A2: d})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, d + 2) == [A2] * d + [A1] * 3


def _completions(r: Rules, s: Save, t: int, card: CardId) -> int:
    v = view_at(r, s, t)
    return next(c.completions for c in (*v.cards, *v.completed) if c.card == card)


# ---- statement 17 -----------------------------------------------------------------------------------------------------

@kills(6, 8)
def test_with_no_action_able_to_start_the_first_to_turn_ready_starts_at_that_second():
    """Statement 17: A1 needs W of 5, A2 of 3, the lane free and no later rule. Nothing runs for 0 to 2; A2 starts at 3
    with no other event falling there; A1 takes over at 5, when A2 lands."""
    r = rules(w_rate=1, req={A1: 5, A2: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 8) == [None] * 3 + [A2] * 2 + [A1] * 4


@kills(7)
def test_with_no_action_able_to_start_a_later_rules_tap_on_the_lane_does():
    """Statement 17: the same rule with a later rule tapping Z on the lane: Z runs each second until A2 turns ready at 3
    and the rule, listed first, takes the lane up as Z lands."""
    r = rules(w_rate=1, req={A1: 5, A2: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)), rule(ALWAYS, TapCard(Z))))
    assert lanes(r, s, 8) == [Z] * 3 + [A2] * 2 + [A1] * 4


@kills(6, 7)
def test_a_tap_the_lane_went_to_meanwhile_lands_first():
    """Statement 17: the later rule's D (10 s) holds the lane from 0; A2 turns ready at 3 and waits; at 10, as D lands,
    the earlier rule takes the lane, A1 (ready since 5) first."""
    r = rules(w_rate=1, req={A1: 5, A2: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)), rule(ALWAYS, TapCard(D))))
    assert lanes(r, s, 12) == [D] * 10 + [A1] * 3
