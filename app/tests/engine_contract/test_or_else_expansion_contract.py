"""A rule with actions a1..an behaves as the n adjacent orders it expands to (docs/design/rule-guards.md, "Contract
(blind)", statement 14; "Or else": a rule holds one place in the rule list and tries its actions there, top down).
Both saves are played second by second under the same decisions and compared on everything the statement lists: lanes,
the running mix, stores, completions. The expanded save holds only plain orders and guards, so it runs on any engine
that has guards; the rule's save needs `or_else`."""
from dataclasses import dataclass

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AtLeast, AtMost, CardShare, Condition, Mix, Order, OrderVerb, Rules, Save, SaveMix,
    StoreValue, SwitchMix, TapCard, advance, decide,
)
from contract_gen import few
from guards_world import kills
from or_else_world import (
    A1, A2, A3, ALWAYS, G1, G2, G3, GP, M1, M2, M3, T, W, Z, expanded, observe, rule, rules, start,
)

TAPS, MIXES, GREYABLE = (A1, A2, A3), (M1, M2, M3), (G1, G2, G3)
HORIZON = 12


@dataclass(frozen=True)
class Case:
    rules: Rules
    when: Condition
    acts: tuple[OrderVerb, ...]
    guards: tuple[Condition, ...]
    later: tuple[Order, ...]
    decisions: tuple[tuple[int, SaveMix], ...]


def _wait(v: int, r: int) -> Condition:
    return AtLeast(StoreValue(W), v * Q, r * Q)


def _guard(kind: bool, v: int) -> Condition:
    s = StoreValue(T)
    return AtMost(s, v * Q, (v + 1) * Q) if kind else AtLeast(s, v * Q, (v - 1) * Q)


@st.composite
def case_st(draw: st.DrawFn) -> Case:
    """One to three distinct actions of one kind, each with its own work, readiness (taps: the W it needs), cap (a tap
    dead, a mix greyed after that many completions), a `when`, up to two guards on T, and, for taps, a later rule on the
    same lane; for mixes, an optional SaveMix that un-greys one of the actions' mixes."""
    mix = draw(st.booleans())
    picks = draw(st.permutations([0, 1, 2]))[: draw(st.integers(1, 3))]
    cards = GREYABLE if mix else TAPS
    dur = {c: draw(st.integers(1, 3)) for c in cards}
    cap = {c: k for c in cards if (k := draw(st.integers(0, 3)))}
    req = {} if mix else {c: q for c in cards if (q := draw(st.integers(0, 6)))}
    v = draw(st.integers(1, 6))
    when = draw(st.one_of(st.just(ALWAYS), st.builds(_wait, st.just(v), st.integers(0, v))))
    guards = draw(st.lists(st.builds(_guard, st.booleans(), st.integers(1, 8)), max_size=2, unique=True))
    r = rules(w_rate=1, w0=draw(st.integers(0, 2)), t_rate=1, t0=draw(st.integers(0, 3)), dur=dur, cap=cap, req=req)
    acts: tuple[OrderVerb, ...] = tuple(SwitchMix(MIXES[i]) if mix else TapCard(TAPS[i]) for i in picks)
    later = (Order(ALWAYS, TapCard(Z)),) if not mix and draw(st.booleans()) else ()
    decisions: tuple[tuple[int, SaveMix], ...] = ()
    if mix and draw(st.booleans()):
        back = SaveMix(Mix(MIXES[draw(st.sampled_from(picks))], (CardShare(GP, BP),)))
        decisions = ((draw(st.integers(1, 8)), back),)
    return Case(r, when, acts, tuple(guards), later, decisions)


def _play(r: Rules, s: Save, decisions: tuple[tuple[int, SaveMix], ...]) -> list[tuple[object, ...]]:
    out = [observe(r, s, 0)]
    for t in range(1, HORIZON + 1):
        s = advance(s, r, t)
        for at, verb in decisions:
            if at == t:
                s = decide(s, r, t, verb)
        out.append(observe(r, s, t))
    return out


@kills(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 18)
@few(60)
@given(case_st())
def test_a_rule_is_the_adjacent_orders_it_expands_to(c: Case):
    """Statement 14: from the same save and the same decisions the rule's save and the expanded save agree at every
    second on lanes, the running mix, stores and completions, for taps of unequal readiness, caps and work, mixes that
    grey and un-grey, a `when` of its own, guards, and a later rule on the lane."""
    o = rule(c.when, c.acts[0], c.acts[1:], *c.guards)
    expected = _play(c.rules, start(c.rules, expanded(o) + c.later), c.decisions)
    got = _play(c.rules, start(c.rules, (o, *c.later)), c.decisions)
    assert got == expected


@kills(1, 2, 3)
def test_the_property_is_not_vacuous_a_fallback_changes_what_the_rule_does():
    """Statement 14, control: with the first action unready, a rule of two actions does what its first alone never does,
    so equality with the expansion is an equality of behaviour that needs the fallback."""
    r = rules(w_rate=1, req={A1: 5})
    two = rule(ALWAYS, TapCard(A1), (TapCard(A2),))
    alone = _play(r, start(r, (rule(ALWAYS, TapCard(A1)),)), ())
    assert _play(r, start(r, (two,)), ()) != alone
    assert _play(r, start(r, (two,)), ()) == _play(r, start(r, expanded(two)), ())
