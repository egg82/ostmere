"""Invariants 1-3: splitting a span, idempotent now, decide advances first."""
from hypothesis import given, strategies as st

from ashfall_app.engine import advance, decide, new_save
from contract_gen import play, probe_times, scenario_st, few, Scenario


@few(10)
@given(sc=scenario_st())
def test_split_at_event_boundaries(sc: Scenario):
    """Invariant 1 (split): advance(advance(s,t1),t2) == advance(s,t2), t1 drawn from event times and +/- 1."""
    s = play(sc)
    ts = probe_times(s, sc.rules, sc.offsets)
    for i, t1 in enumerate(ts):
        mid = advance(s, sc.rules, t1)
        for t2 in ts[i:]:
            assert advance(mid, sc.rules, t2) == advance(s, sc.rules, t2), (t1, t2)


@few(10)
@given(sc=scenario_st(), cuts=st.lists(st.integers(0, 30_000), min_size=2, max_size=12))
def test_many_chained_split_points(sc: Scenario, cuts: list[int]):
    """Invariant 1 (split): many split points chained, uniformly drawn, equal one direct advance at every prefix."""
    s = play(sc)
    chained = s
    t = s.time
    for c in sorted(cuts):
        t = s.time + c
        chained = advance(chained, sc.rules, t)
        assert chained == advance(s, sc.rules, t), t


@few(10)
@given(sc=scenario_st())
def test_split_through_every_event(sc: Scenario):
    """Invariant 1 (split): stepping event by event (t = each event time, then +1) equals the direct jump."""
    from ashfall_app.engine import next_event
    s = play(sc)
    stepped = s
    for _ in range(6):
        e = next_event(stepped, sc.rules)
        if e is None:
            break
        stepped = advance(stepped, sc.rules, e.time)
        assert stepped == advance(s, sc.rules, e.time)
        stepped = advance(stepped, sc.rules, e.time + 1)
        assert stepped == advance(s, sc.rules, e.time + 1)


@given(sc=scenario_st())
def test_idempotent_now(sc: Scenario):
    """Invariant 2 (idempotent now): advance(s, r, s.time) == s, for every save a scenario passes through."""
    s = new_save(sc.rules, sc.modifiers)
    assert advance(s, sc.rules, s.time) == s
    for dt, verb in sc.steps:
        s = decide(s, sc.rules, s.time + dt, verb)
        assert advance(s, sc.rules, s.time) == s
    later = advance(s, sc.rules, s.time + sc.offsets[0])
    assert advance(later, sc.rules, later.time) == later


@few(10)
@given(sc=scenario_st())
def test_decide_advances_first(sc: Scenario):
    """Invariant 3 (decide advances first): decide(s,t,v) == decide(advance(s,t),t,v) at event times and +/- 1."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        assert decide(s, sc.rules, t, sc.probe) == decide(advance(s, sc.rules, t), sc.rules, t, sc.probe), t
