"""Properties over random card worlds (DESIGN.txt, "INVARIANTS" 1-3, 7, 9, 25, 26 and 34-38): splitting time is
harmless, now is idempotent, decide advances first, values and counts stay in bounds, every segment starts at the save's
time and is linear to the next event, counts are read off the work, no uncapped completion is an event, a HANDS tap
never runs beside the mix, and the logged entry points split exactly with keys from the rules."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, HANDS, CardDef, CardId, EventKind, Flow, InvalidVerbError, MixId, RunBy, StoreDef, StoreId, SwitchMix, advance,
    advance_logged, decide, explain_work, new_save, next_event, segment, value, value_at, view,
)
from ashfall_app.engine import work as engine_work
from ashfall_app.engine.schedule import events
from cards_gen import Scenario, few, play, play_logged, rule_keys, scenario_st, span, timeline
from cards_world import Q, lane, rules, save_mix, work


@few(8)
@given(sc=scenario_st())
def test_split_at_event_boundaries(sc: Scenario):
    """Invariant 1: advance(advance(s, t1), t2) == advance(s, t2) with t1 at event times and +/- 1 (completions, taps
    done, interrupts, requires and READY among them)."""
    s = play(sc)
    r = sc.rules
    stops = timeline(s, r, sc.offsets)
    for t1 in stops[:: max(1, len(stops) // 4)]:
        assert t1 == advance(s, r, t1.time), t1.time
        assert advance(t1, r, stops[-1].time) == stops[-1], (t1.time, stops[-1].time)


@few(8)
@given(sc=scenario_st(), cuts=st.lists(st.integers(0, 12_000), min_size=2, max_size=6))
def test_many_chained_split_points(sc: Scenario, cuts: list[int]):
    """Invariant 1: many split points chained equal one direct advance at the end."""
    s = play(sc)
    chained = s
    cuts = [span(sc.rules, c) for c in cuts]
    for c in sorted(cuts):
        chained = advance(chained, sc.rules, s.time + c)
    assert chained == advance(s, sc.rules, s.time + max(cuts))


@few(8)
@given(sc=scenario_st(), dt=st.integers(0, 6000))
def test_now_is_idempotent_and_decide_advances_first(sc: Scenario, dt: int):
    """Invariants 2 and 3: advance(s, s.time) == s; decide(s, t, v) == decide(advance(s, t), t, v), TapCard included,
    and both refuse alike."""
    s = play(sc)
    r = sc.rules
    assert advance(s, r, s.time) == s
    t = s.time + span(sc.rules, dt)
    outcomes: list[object] = []
    for base in (s, advance(s, r, t)):
        try:
            outcomes.append(decide(base, r, t, sc.probe))
        except InvalidVerbError:
            outcomes.append("refused")
    assert outcomes[0] == outcomes[1]


@few(8)
@given(sc=scenario_st())
def test_values_counts_and_segments_stay_in_bounds(sc: Scenario):
    """Invariants 7, 9, 16, 38: stores in [0, cap] and XP in [0, last threshold]; every store, XP and card work segment
    starts at the save's time; lanes HANDS first then rules order, cards in rules order; a card's work never falls and
    its completions never pass its effective cap; a card has a state only while its work value, rate or raise is
    non-zero; a lane holds a card only while its work moves (a failed tap never holds one)."""
    s = play(sc)
    r = sc.rules
    per = {c.id: c.work_s * BP for c in r.cards}
    order = [c.id for c in r.cards]
    last: dict[str, int] = {}
    for a in timeline(s, r, sc.offsets):
        for sd, st_ in zip(r.stores, a.stores):
            assert 0 <= st_.segment.start_value <= sd.cap and st_.segment.start == a.time, (a.time, sd.id)
        for sk in a.skills:
            assert 0 <= sk.xp.start_value <= r.curve.thresholds[-1] and sk.xp.start == a.time
        assert [ls.lane for ls in a.lanes] == [HANDS] + [x.id for x in r.lanes]
        assert [cs.card for cs in a.cards] == [c for c in order if c in {cs.card for cs in a.cards}]
        for cs in a.cards:
            assert cs.work.start == a.time and cs.work.start_value >= last.get(cs.card, 0)
            assert cs.work.start_value or cs.work.rate or cs.raised, (cs.card, a.time)
            last[cs.card] = cs.work.start_value
            cap = engine_work.effective_cap(a, r, cs.card)
            assert cap is None or cs.work.start_value // per[cs.card] <= cap
        for ls in a.lanes:
            if ls.card is not None:
                assert work(a, ls.card).rate > 0, (ls.card, a.time)


@few(8)
@given(sc=scenario_st())
def test_linear_to_the_next_event_and_no_uncapped_completion_is_an_event(sc: Scenario):
    """Invariants 6 and 36: up to the next event every store reads off its segment and every card's work off its own;
    no COMPLETION is scheduled for a card without a cap."""
    s = play(sc)
    r = sc.rules
    uncapped = {c.id for c in r.cards if c.cap is None}
    for a in timeline(s, r, sc.offsets, events=3):
        assert not [e for e in events(a, r) if e.kind is EventKind.COMPLETION and e.subject in uncapped]
        e = next_event(a, r)
        horizon = a.time + 5000 if e is None else e.time
        for t in sorted({a.time, (a.time + horizon) // 2, max(a.time, horizon - 1), horizon}):
            b = advance(a, r, t)
            for st_, now in zip(a.stores, b.stores):
                assert now.segment.start_value == value_at(segment(a, r, st_.store), t), (st_.store, t)
            for cs in a.cards:
                assert work(b, cs.card).start_value == value_at(cs.work, t), (cs.card, t)
        if e is not None:
            x = a.stores[0].store
            assert e.time > a.time and value(a, r, x, e.time) == value_at(segment(a, r, x), e.time)


@few(8)
@given(sc=scenario_st())
def test_counts_are_read_off_the_work_and_a_hands_tap_never_runs_beside_the_mix(sc: Scenario):
    """Invariants 34 and 37: each card's completions in the view equal its work // (work_s * BP) and
    work.completions agrees; while a ready tap holds HANDS no card is run by the mix, the tapped card is run by TAP and
    its work rises at explain_work's speed."""
    s = play(sc)
    r = sc.rules
    per = {c.id: c.work_s * BP for c in r.cards}
    for a in timeline(s, r, sc.offsets, events=3):
        v = view(a, r)
        for cv in v.cards:
            assert cv.completions == work(a, cv.card).start_value // per[cv.card] == engine_work.completions(a, r, cv.card)
        for cc in v.completed:
            assert cc.completions == work(a, cc.card).start_value // per[cc.card]
        if lane(a, HANDS).card is not None:
            assert not [cv.card for cv in v.cards if cv.by is RunBy.MIX], a.time
        for ls in a.lanes:
            if ls.card is not None:
                assert work(a, ls.card).rate == explain_work(a, r, ls.card).per_hour, (ls.card, a.time)
                tapped = next((cv for cv in v.cards if cv.card == ls.card), None)
                assert tapped is None or tapped.by is RunBy.TAP


@few(8)
@given(sc=scenario_st(), cut=st.integers(0, 12_000), extra=st.integers(0, 12_000))
def test_logged_advance_splits_and_emits_only_rule_keys(sc: Scenario, cut: int, extra: int):
    """Invariants 25, 26: advance_logged(s, t).save == advance(s, t); the lines of s->t1 then t1->t2 equal those of
    s->t2, in (time, seq) order with seq from 0 at each instant; every key is one the rules can emit (a card's lines,
    an outcome's or finished's lines, a chip's)."""
    s, _, history = play_logged(sc)
    r = sc.rules
    t1, t2 = s.time + span(r, cut), s.time + span(r, cut) + span(r, extra)
    whole = advance_logged(s, r, t2)
    assert whole.save == advance(s, r, t2)
    first = advance_logged(s, r, t1)
    second = advance_logged(first.save, r, t2)
    assert first.lines + second.lines == whole.lines
    pairs = [(ln.time, ln.seq) for ln in whole.lines]
    assert pairs == sorted(pairs) and len(set(pairs)) == len(pairs)
    assert all(seq == sum(1 for t, _ in pairs[:i] if t == time) for i, (time, seq) in enumerate(pairs))
    keys = rule_keys(r)
    assert all(ln.key in keys for ln in history + whole.lines)


def test_a_card_state_exists_iff_its_work_value_rate_or_raise_is_non_zero():
    """Save.cards, "State, canonical": a running card with an empty bar has a state (its rate is non-zero); one at share
    0 has none; a card that stops with work done keeps its state (the value is non-zero); a mix that runs nothing leaves
    none, and the free lane beside is empty."""
    c, d, y = CardId("c"), CardId("d"), StoreId("y")
    r = rules([StoreDef(y, 100 * Q, 0)], cards=[CardDef(c, 100, makes=(Flow(y, 1000),)),
                                                 CardDef(d, 100, makes=(Flow(y, 1000),))])
    m0, m1 = MixId("m0"), MixId("m1")
    s = save_mix(save_mix(new_save(r), r, 0, {c: BP}, "m0"), r, 0, {d: 0}, "m1")
    assert s.cards == ()
    running = decide(s, r, 0, SwitchMix(m0))
    assert [cs.card for cs in running.cards] == [c] and work(running, c).start_value == 0 and work(running, c).rate == BP
    idle = decide(s, r, 0, SwitchMix(m1))
    assert idle.cards == () and idle.lanes[0].card is None
    stopped = decide(advance(running, r, 50), r, 50, SwitchMix(m1))
    assert [cs.card for cs in stopped.cards] == [c] and work(stopped, c).start_value == 50 * BP
    assert work(stopped, c).rate == 0
