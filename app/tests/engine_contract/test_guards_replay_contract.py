"""Rule guards keep replay exact (docs/design/rule-guards.md, "Contract (blind)", statements 22 to 24; "Evaluation,
determinism and replay"). The scenes move with nobody deciding: a boundary-chasing rule fills T with its own mix until
its guard pauses it and the player's mix empties T again, so guard latches change again and again on their own; a
second rule taps K under a `when` and guards on T, and a third may be paused by a guard on W, which only rises."""
from hypothesis import assume, given, strategies as st

from ashfall_app.engine import (
    BP, AtLeast, Order, Rules, Save, SetOrders, StoreValue, SwitchMix, TapCard, advance, advance_logged, decide,
    decide_logged, forecast, next_event, value,
)
from contract_gen import few
from guards_world import (
    kills,
    ALWAYS, COND, DOWN, K, T, UP, W, Q, at_least, cond, guarded, guards_of, lane_card, rules, start, when_of,
)


@st.composite
def _scene(draw: st.DrawFn) -> tuple[Rules, Save, list[int]]:
    v = draw(st.integers(3, 20))
    gap = draw(st.integers(0, 3))
    near = st.builds(cond, st.booleans(), st.integers(max(1, v - 5), v + 2), st.integers(0, 3))
    tap_guards = draw(st.lists(near, min_size=1, max_size=3, unique=True))
    when = draw(st.one_of(st.just(ALWAYS), near, COND))
    orders: list[Order] = [guarded(ALWAYS, SwitchMix(UP), at_least(v, max(1, v - gap))),
                           guarded(when, TapCard(K), *tap_guards)]
    if draw(st.booleans()):
        orders.insert(0, guarded(ALWAYS, SwitchMix(UP), at_least(draw(st.integers(5, 40)), 1, W), at_least(v, v - 1)))
    r = rules(t0=0, w_rate=1)
    cuts = sorted(draw(st.lists(st.integers(0, 40), min_size=2, max_size=4)))
    return r, start(r, tuple(orders), active=DOWN), cuts


def _probe_times(r: Rules, s: Save, cuts: list[int], n: int = 3) -> list[int]:
    """The drawn cuts, and the first n event times from s with one second either side."""
    out, cur = set(cuts), s
    for _ in range(n):
        e = next_event(cur, r)
        if e is None:
            break
        out |= {e.time - 1, e.time, e.time + 1}
        cur = advance(cur, r, e.time)
    return sorted(t for t in out if t >= s.time)


# ---- statement 22 -----------------------------------------------------------------------------------------------------

@kills(25)
@few(10)
@given(scene=_scene())
def test_splitting_an_advance_changes_nothing(scene: tuple[Rules, Save, list[int]]):
    """Statement 22, invariant 1: advance(advance(s, t1), t2) == advance(s, t2) for saves holding guards, t1 drawn and
    at event times +/- 1, t2 the next probe time; and every probe time chained."""
    r, s, cuts = scene
    ts = _probe_times(r, s, cuts)
    direct = {t: advance(s, r, t) for t in ts}
    for t1, t2 in zip(ts, ts[1:]):
        assert advance(direct[t1], r, t2) == direct[t2], (t1, t2)
    chained = s
    for t in ts:
        chained = advance(chained, r, t)
        assert chained == direct[t], t


@kills(25)
@few(6)
@given(scene=_scene(), edit=st.booleans())
def test_decide_advances_first(scene: tuple[Rules, Save, list[int]], edit: bool):
    """Statement 22, invariant 3: decide(s, t, v) == decide(advance(s, t), t, v), for a player's switch and for a
    SetOrders that keeps one guarded rule and edits another's guard."""
    r, s, cuts = scene
    verb = SetOrders((s.orders[-1], guarded(ALWAYS, SwitchMix(UP), at_least(7, 4)))) if edit else SwitchMix(UP)
    for t in _probe_times(r, s, cuts):
        assert decide(s, r, t, verb) == decide(advance(s, r, t), r, t, verb), t


@kills(25)
@few(10)
@given(scene=_scene())
def test_a_logged_split_gives_the_same_save_and_lines(scene: tuple[Rules, Save, list[int]]):
    """Statement 22, invariant 25: advance_logged(s, t).save == advance(s, t); the lines of s->t1 then t1->t2 are those
    of s->t2; decide_logged(...).save == decide(...)."""
    r, s, cuts = scene
    t1, t2 = cuts[0], cuts[-1]
    whole = advance_logged(s, r, t2)
    first = advance_logged(s, r, t1)
    assert whole.save == advance(s, r, t2) and first.save == advance(s, r, t1)
    assert first.lines + advance_logged(first.save, r, t2).lines == whole.lines
    assert decide_logged(s, r, t2, SwitchMix(UP)).save == decide(s, r, t2, SwitchMix(UP))


def test_the_logged_split_compares_real_lines():
    """The control for the test above: a guarded tap rule on in the scene's world writes K's lines, one a landing."""
    r = rules(t0=0, w_rate=1)
    s = start(r, (guarded(ALWAYS, TapCard(K), at_least(50, 49)),), active=DOWN)
    assert len(advance_logged(s, r, 10).lines) == 10


# ---- statement 23 -----------------------------------------------------------------------------------------------------

@kills(24)
@few(10)
@given(scene=_scene())
def test_every_lane_is_driven_by_a_rule_that_is_on(scene: tuple[Rules, Save, list[int]]):
    """Statement 23: after an advance that did not hit the firing cap, no rule that is on lists a tap that can act: K
    can always act, so whenever the tap rule's `when` latch is on and none of its guards is, lane L is busy."""
    r, s, cuts = scene
    cur = s
    for t in sorted(set(_probe_times(r, s, cuts)) | set(range(0, 41, 2))):
        a = advance(cur, r, t)
        if a.cascade_count == cur.cascade_count:
            latch = a.latches[-1]
            if when_of(latch) and not any(guards_of(latch)):
                assert lane_card(a) is not None, t
        cur = a


# ---- statement 24 -----------------------------------------------------------------------------------------------------

def _walk(r: Rules, s: Save, until: int, cap_q: int) -> tuple[list[int], list[int]]:
    """When T reaches its cap from below and 0 from above, advancing second by second (T moves one item a second, so
    both land on whole seconds)."""
    fills: list[int] = []
    empties: list[int] = []
    prev = value(s, r, T, s.time)
    cur = s
    for t in range(s.time + 1, until + 1):
        cur = advance(cur, r, t)
        now = value(cur, r, T, t)
        if now == cap_q and prev < cap_q:
            fills.append(t)
        if now == 0 and prev > 0:
            empties.append(t)
        prev = now
    return fills, empties


@kills(26)
@few(10)
@given(cap=st.integers(4, 12), w_level=st.integers(5, 40), share=st.booleans(), extra=st.booleans())
def test_a_forecast_lists_the_fills_and_emptyings_an_advance_reaches(cap: int, w_level: int, share: bool, extra: bool):
    """Statement 24: a rule fills T unless T is full (as a share, or as an amount) and, once W reaches w_level, for
    good; the player's mix empties T. The forecast from the start lists the fills and emptyings of T that advancing
    reaches, guard pauses included."""
    assume(w_level > cap)   # W's guard pauses the rule for good at w_level seconds, so T must fill first
    full = (AtLeast(StoreValue(T), BP, BP, value_of_cap=True, release_of_cap=True) if share
            else at_least(cap, cap - 1))
    guards = (full, at_least(w_level, 1, W)) + ((at_least(cap - 1, cap - 3),) if extra else ())
    r = rules(t0=0, cap=cap, w_rate=1)
    s = start(r, (guarded(ALWAYS, SwitchMix(UP), *guards),), active=DOWN)
    f = forecast(s, r, 60, stores=(T,))
    fills, empties = _walk(r, s, f.until, cap * Q)
    assert fills or extra, "the walk saw no fill"   # T is full by `cap` seconds; the extra guard pauses it an item short
    assert (list(f.fills.get(T, ())), list(f.empties.get(T, ()))) == (fills, empties)
