"""What a rule with fallbacks reports and what retiring a chore leaves of it (docs/design/rule-guards.md, "Contract
(blind)", statements 20 and 21; "The saved shape", the wire: `order_states`, `order_doing`). `order_doing[i]` is "the
index in the rule's actions", which the note gives no base for (gaps.txt): the tests read it relative to the first
action, so a rule running its first action reads the base b and one running its second reads b + 1."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    AtLeast, AtMost, CardId, OrderState, Outcome, QUANTITY_SCALE as Q, Rules, Save, StoreValue, SwitchMix, TapCard,
    TriggerDef, TriggerId, AfterTime, advance,
)
from contract_gen import few
from guards_world import kills, paused
from or_else_world import (
    A1, A2, A3, ALWAYS, G1, G2, J, M1, M2, T, W, Z, lanes, rule, rules, start, view_at,
)

TAPS = (A1, A2, A3)


def _states(r: Rules, s: Save, until: int, i: int = 0) -> list[OrderState]:
    return [view_at(r, s, t).order_states[i] for t in range(until + 1)]


def _doing(r: Rules, s: Save, until: int, i: int = 0) -> list[int | None]:
    return [getattr(view_at(r, s, t), "order_doing")[i] for t in range(until + 1)]


# ---- statement 20: passed over ------------------------------------------------------------------------------------------

@kills(5)
def test_a_rule_is_passed_over_exactly_when_every_listed_tap_is_dead():
    """Statement 20: A1 is capped at one completion and A2 at two. A1 is dead from 1 and the rule lives through A2 (on);
    A2 is dead from 3, and the rule is passed over."""
    r = rules(cap={A1: 1, A2: 2})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert lanes(r, s, 4) == [A1, A2, A2, None, None]
    assert _states(r, s, 4) == [OrderState.ON] * 3 + [OrderState.PASSED_OVER] * 2


@kills(5)
def test_a_rule_is_passed_over_exactly_when_every_listed_mix_is_greyed():
    """Statement 20: M1 greys at 1 and M2 at 2; the rule is on until then and passed over after."""
    r = rules(cap={G1: 1, G2: 1})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    assert _states(r, s, 3) == [OrderState.ON, OrderState.ON, OrderState.PASSED_OVER, OrderState.PASSED_OVER]


@kills(5)
def test_a_rule_with_a_live_action_it_cannot_yet_start_is_on_not_passed_over():
    """Statement 20 and the table: both taps unready, neither dead; the rule's `when` holds and no earlier rule has the
    lane, so it is on ("on now, nothing it lists can start yet")."""
    r = rules(w_rate=1, req={A1: 5, A2: 4})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    assert _states(r, s, 3) == [OrderState.ON] * 4


# ---- statement 20: order_doing ---------------------------------------------------------------------------------------------

@kills(13)
def test_order_doing_names_the_action_the_lane_runs_for_this_rule():
    """Statement 20: A1 is ready from 3. Until then the lane runs A2 for the rule (its second action), from 3 A1 (its
    first): the two readings differ by one, and the first is a position in a two-action list."""
    r = rules(w_rate=1, req={A1: 3})
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),))
    got = _doing(r, s, 6)
    assert None not in got
    first, second = got[3], got[0]
    assert got == [second] * 3 + [first] * 4
    assert (first, second) in ((0, 1), (1, 2))
    assert _states(r, s, 6) == [OrderState.ON] * 7


@kills(13)
def test_order_doing_names_the_mix_that_runs_for_this_rule():
    """Statement 20: M1 (cap 3) runs 0 to 2, M2 from 3: the position moves from the first to the second action."""
    r = rules(cap={G1: 3})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    got = _doing(r, s, 5)
    first = got[0]
    assert first is not None
    assert got == [first] * 3 + [first + 1] * 3


@kills(13)
def test_order_doing_is_the_same_position_for_a_rule_of_one_action():
    """Statement 20: the position of a rule's first action does not depend on how many actions the rule lists, so a lone
    A1 reads as a rule [A1, A2] running A1 does."""
    r = rules(w_rate=1, req={A1: 3})
    both = _doing(r, start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)),)), 5)[3]
    lone = _doing(r, start(r, (rule(ALWAYS, TapCard(A1)),)), 5)[3]
    assert both == lone and lone is not None


@kills(13)
def test_order_doing_is_none_when_the_rule_runs_nothing():
    """Statement 20: waiting, outranked by an earlier rule holding the lane, and paused by a guard each read None."""
    waiting = rules(w_rate=1)
    s = start(waiting, (rule(AtLeast(StoreValue(W), 100 * Q, 100 * Q), TapCard(A1), (TapCard(A2),)),))
    assert _doing(waiting, s, 3) == [None] * 4
    assert _states(waiting, s, 3) == [OrderState.WAITING] * 4
    r = rules(w_rate=1)
    s = start(r, (rule(ALWAYS, TapCard(Z)), rule(ALWAYS, TapCard(A1), (TapCard(A2),))))
    assert _doing(r, s, 3, 1) == [None] * 4
    assert _states(r, s, 3, 1) == [OrderState.OUTRANKED] * 4
    g = rules(t_rate=1)
    s = start(g, (rule(ALWAYS, TapCard(A1), (TapCard(A2),), AtMost(StoreValue(T), 3 * Q, 4 * Q)),))
    doing = _doing(g, s, 5)
    assert doing[:5] == [None] * 5 and doing[5] is not None
    assert _states(g, s, 5) == [paused()] * 5 + [OrderState.ON]


# ---- statement 21 --------------------------------------------------------------------------------------------------------

def _retiring(*cards: CardId, w_rate: int = 0, t_rate: int = 0) -> Rules:
    chore = TriggerDef(TriggerId("chore"), AfterTime(4), Outcome(retire_orders=tuple(cards)))
    return rules(triggers=(chore,), w_rate=w_rate, t_rate=t_rate)


@kills(14, 15)
def test_retiring_the_first_action_leaves_the_rest_and_runs_the_next():
    """Statement 21: a season retires A1 at 4 from [A1, A2, A3]: the rule stays with A2, A3 and runs A2 from 4 though A1
    is ready."""
    r = _retiring(A1)
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2), TapCard(A3))),))
    assert advance(s, r, 5).orders == (rule(ALWAYS, TapCard(A2), (TapCard(A3),)),)
    assert lanes(r, s, 6) == [A1] * 4 + [A2] * 3


@kills(14, 15)
def test_retiring_a_fallback_leaves_the_others():
    """Statement 21: retiring A2 from [A1, A2, A3] leaves [A1, A3]."""
    r = _retiring(A2)
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2), TapCard(A3))),))
    assert advance(s, r, 5).orders == (rule(ALWAYS, TapCard(A1), (TapCard(A3),)),)


@kills(16)
def test_a_rule_that_keeps_an_action_keeps_its_latches():
    """Statement 21: the `when` latch and the guard latch survive the retiring unchanged."""
    r = _retiring(A1, w_rate=1, t_rate=1)
    when, guard = AtLeast(StoreValue(W), 2 * Q, Q), AtMost(StoreValue(T), 4 * Q, 5 * Q)
    s = start(r, (rule(when, TapCard(A1), (TapCard(A2),), guard),))
    before = advance(s, r, 3)
    after = advance(s, r, 5)
    assert after.latches == before.latches
    assert after.orders == (rule(when, TapCard(A2), (), guard),)


@kills(14, 15, 17)
def test_retiring_every_action_removes_the_rule():
    """Statement 21: naming A1 and A2 removes the rule and only its own latch; the other rule stays with its latch."""
    r = _retiring(A2, A1)
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2),)), rule(ALWAYS, TapCard(J))))
    after = advance(s, r, 5)
    assert after.orders == (rule(ALWAYS, TapCard(J)),)
    assert after.latches == advance(s, r, 3).latches[1:]


@kills(14, 15, 16, 17)
@few(40)
@given(picks=st.permutations([0, 1, 2]), n=st.integers(1, 3), gone=st.sets(st.integers(0, 2), min_size=1))
def test_retiring_any_set_of_actions_leaves_the_rest_in_order(picks: list[int], n: int, gone: set[int]):
    """Statement 21, for every rule and every set of named cards: the rule keeps the listed actions not named, in their
    order, and its latch; with none left it is removed."""
    acts = tuple(TAPS[i] for i in picks[:n])
    named = tuple(TAPS[i] for i in sorted(gone))
    keep = tuple(a for a in acts if a not in named)
    r = _retiring(*named)
    s = start(r, (rule(ALWAYS, TapCard(acts[0]), tuple(TapCard(a) for a in acts[1:])),))
    after = advance(s, r, 5)
    if keep:
        assert after.orders == (rule(ALWAYS, TapCard(keep[0]), tuple(TapCard(a) for a in keep[1:])),)
        assert after.latches == advance(s, r, 3).latches
    else:
        assert after.orders == () and after.latches == ()
