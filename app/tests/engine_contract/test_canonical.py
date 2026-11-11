"""Invariant 9: every save the engine returns is in canonical form."""
from hypothesis import given

from ashfall_app.engine import Save, Rules, advance, decide, new_save
from contract_gen import play, probe_times, scenario_st, few, Scenario


def _canonical(s: Save, rules: Rules) -> None:
    assert [x.store for x in s.stores] == [d.id for d in rules.stores]
    assert [x.skill for x in s.skills] == [d.id for d in rules.skills]
    for x in s.stores:
        assert x.segment.start == s.time
    for k in s.skills:
        assert k.xp.start == s.time
    assert len(s.latches) == len(s.orders)
    order = {r: i for i, r in enumerate([a.id for a in rules.standing] + [c.id for c in rules.cards])}
    assert [order[p.runner] for p in s.pauses] == sorted(order[p.runner] for p in s.pauses)
    assert len({p.runner for p in s.pauses}) == len(s.pauses)
    by_card = {c.id: i for i, c in enumerate(rules.cards)}
    assert [by_card[c.card] for c in s.cards] == sorted(by_card[c.card] for c in s.cards)
    assert len({c.card for c in s.cards}) == len(s.cards)
    for c in s.cards:
        assert c.work.start == s.time
        assert c.work.start_value or c.work.rate or c.raised, c.card  # a state exists iff something in it is non-zero
    ids = [m.id for m in s.mixes]
    assert len(ids) == len(set(ids))
    assert (s.last_cascade is None) == (s.cascade_count == 0)


@few(10)
@given(sc=scenario_st())
def test_saves_are_canonical(sc: Scenario):
    """Invariant 9 (canonical): segments (a card's work too) start at s.time, latches match orders, stores/skills in
    rules order, pauses in runner order (standing, then cards), cards in rules.cards order and present only while their
    work value, rate or raise is non-zero, for new_save, every decide() result and every advance() result."""
    s = new_save(sc.rules, sc.modifiers)
    _canonical(s, sc.rules)
    for dt, verb in sc.steps:
        s = decide(s, sc.rules, s.time + dt, verb)
        _canonical(s, sc.rules)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        assert a.time == t
        _canonical(a, sc.rules)


@few(10)
@given(sc=scenario_st())
def test_mixes_keep_first_saved_order(sc: Scenario):
    """Invariant 9 (canonical): save.mixes keep the order mixes were first saved in; re-saving replaces in place."""
    s = play(sc)
    assert [m.id for m in s.mixes] == sorted((m.id for m in s.mixes), key=lambda i: int(i[1:]))
