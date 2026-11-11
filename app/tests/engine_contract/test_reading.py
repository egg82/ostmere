"""Invariants 4-6: reading writes nothing, value equals the advanced read, values are linear between events."""
from collections.abc import Iterable

import copy

from hypothesis import given

from ashfall_app.engine import (
    BP, CardShare, Flow, Mix, Rules, Save, SaveMix, StoreDef, SwitchMix, advance, decide, explain, explain_work,
    level, level_for, new_save, next_event, segment, value, value_at, xp,
)
from contract_gen import (
    Q, SK, Scenario, card, card_id, few, flow_refs, make_rules, mix_id, play, probe_times, scenario_st, store_id,
)


def _read_everything(s: Save, rules: Rules, ts: Iterable[int]):
    for t in ts:
        for st_ in rules.stores:
            value(s, rules, st_.id, t)
        for sk in rules.skills:
            xp(s, rules, sk.id, t)
            level(s, rules, sk.id, t)
    for st_ in rules.stores:
        segment(s, rules, st_.id)
    next_event(s, rules)
    for ref, _ in flow_refs(rules):
        explain(s, rules, ref)
    for c in rules.cards:
        explain_work(s, rules, c.id)


@given(sc=scenario_st())
def test_reading_leaves_the_save_equal(sc: Scenario):
    """Invariant 4 (reading writes nothing): value/xp/level/segment/next_event/explain/explain_work leave s equal to a
    copy."""
    s = play(sc)
    before = copy.deepcopy(s)
    _read_everything(s, sc.rules, probe_times(s, sc.rules, sc.offsets))
    assert s == before


@few(10)
@given(sc=scenario_st())
def test_reading_does_not_change_later_results(sc: Scenario):
    """Invariant 4 (reading writes nothing): advancing after many reads gives what advancing without reads gave
    (catches a checkpoint or cache left behind by a read)."""
    s = play(sc)
    ts = probe_times(s, sc.rules, sc.offsets)
    expected = [advance(s, sc.rules, t) for t in ts]
    _read_everything(s, sc.rules, ts + [ts[-1] + 100_000])
    assert [advance(s, sc.rules, t) for t in ts] == expected


@given(sc=scenario_st())
def test_value_equals_advanced_read(sc: Scenario):
    """Invariant 5 (value equals advance): value/xp/level at t equal the same read off advance(s, r, t)."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        adv = advance(s, sc.rules, t)
        assert adv.time == t
        for i, sd in enumerate(sc.rules.stores):
            assert value(s, sc.rules, sd.id, t) == adv.stores[i].segment.start_value, (t, sd.id)
        for i, sk in enumerate(sc.rules.skills):
            x = adv.skills[i].xp.start_value
            assert xp(s, sc.rules, sk.id, t) == x
            assert level(s, sc.rules, sk.id, t) == level_for(sc.rules.curve, x)


@few(10)
@given(sc=scenario_st())
def test_linear_between_events(sc: Scenario):
    """Invariant 6 (linear between events): value(t) == value_at(segment, t) for s.time <= t <= next_event.time,
    inclusive at both ends, and the next event is strictly after s.time."""
    s = play(sc)
    e = next_event(s, sc.rules)
    if e is None:
        ts = [s.time, s.time + 1, s.time + 7_777, s.time + 1_000_000]
    else:
        assert e.time > s.time
        mid = (s.time + e.time) // 2
        ts = sorted({s.time, s.time + 1, mid, e.time - 1, e.time})
        ts = [t for t in ts if s.time <= t <= e.time]
    for sd in sc.rules.stores:
        seg = segment(s, sc.rules, sd.id)
        assert seg.start == s.time
        for t in ts:
            assert value(s, sc.rules, sd.id, t) == value_at(seg, t), (sd.id, t, e)


def test_reads_past_an_event_that_stops_the_card_are_not_extrapolated():
    """Invariant 5 (value equals advance), for a store and for XP: one item an hour empties X at t = 3600, the dry rule
    pauses the card that makes Y and trains, and both stop there. A read at any later t is the value at 3600, not the
    first segment's rate carried on."""
    X, Y = store_id(0), store_id(1)
    rules = make_rules([StoreDef(X, 50 * Q, Q), StoreDef(Y, 50 * Q, 0)], [card(0, 3000, (Flow(Y, 2000),), (Flow(X, 1000),))])
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(mix_id(0), (CardShare(card_id(0), BP),))))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    for t in (3599, 3600, 3601, 10_000):
        assert xp(s, rules, SK, t) == advance(s, rules, t).skills[0].xp.start_value == 3000 * min(t, 3600), t
        assert value(s, rules, Y, t) == 2000 * min(t, 3600), t
