"""Invariant 16: running dry pauses consumers last-in-mix first."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, ActionId, CardShare, EventKind, Flow, FlowKind, Mix, Pause, RateRef, RunKind, SaveMix, StandingDef, StoreDef, SwitchMix,
    advance, decide, explain, explain_work, new_save, next_event, segment, value, view, xp,
)
from contract_gen import (
    Q, SK, card, card_id, make_rules, mix_id, play, probe_times, scenario_st, store_id, few, Scenario,
)

X = store_id(0)


def test_a_pause_resumes_at_the_cap_when_an_hour_of_its_cost_is_more_than_the_store_holds():
    """Invariant 16 (dry): a paused consumer resumes when the store refills to one hour of its cost "(or the cap)". The
    store holds two items and the consumer draws five an hour, so the hour is out of reach: it resumes when the maker has
    filled the store to its cap. While it is paused its share goes to the maker (SPENT, "Giver"), which then makes two
    items an hour."""
    rules = make_rules([StoreDef(X, 2 * Q, Q)], [card(0, 0, (Flow(X, 2000),), ()), card(1, 0, (), (Flow(X, 10_000),))])
    mix = Mix(mix_id(0), (CardShare(card_id(0), BP // 2), CardShare(card_id(1), BP // 2)))
    s = decide(decide(new_save(rules), rules, 0, SaveMix(mix)), rules, 0, SwitchMix(mix_id(0)))
    a = advance(s, rules, 900)  # one item at 4 items an hour net: empty at 900 s
    assert a.pauses == (Pause(card_id(1), X, 2 * Q),)
    assert advance(a, rules, 4499).pauses == a.pauses  # the maker at the whole share fills two in 3600 s more
    assert advance(a, rules, 4500).pauses == ()


@few(10)
@given(sc=scenario_st())
def test_no_store_is_ever_negative_and_paused_cards_contribute_nothing(sc: Scenario):
    """Invariants 16, 41 (dry, starved): no store is negative at any probe time, and a card in save.pauses has Run
    PAUSED (SPENT on a spent store) and contributes 0 to every rate (makes, costs and XP) and to its work: its bar (explain_work and its
    CardState segment) does not move (DESIGN.txt, "Rate form")."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        for sd in sc.rules.stores:
            assert value(a, sc.rules, sd.id, t) >= 0
        for p in a.pauses:
            act = next(x for x in sc.rules.cards if x.id == p.runner)
            refs = ([RateRef(act.id, FlowKind.MAKE, f.store) for f in act.makes]
                    + [RateRef(act.id, FlowKind.COST, f.store) for f in act.costs] + [RateRef(act.id, FlowKind.XP)])
            for ref in refs:
                e = explain(a, sc.rules, ref)
                assert e.run.kind in (RunKind.PAUSED, RunKind.SPENT) and e.per_hour == 0
            w = explain_work(a, sc.rules, act.id)
            assert w.run.kind in (RunKind.PAUSED, RunKind.SPENT) and w.per_hour == 0
            assert all(c.work.rate == 0 for c in a.cards if c.card == act.id)


@few(10)
@given(sc=scenario_st())
def test_a_line_is_starved_exactly_when_its_empty_store_has_a_card_paused_on_it(sc: Scenario):
    """Invariant 41 (starved): a ledger line is starved iff its store is at 0 and some runner that is not a spent card
    is paused on it (the scenarios issue no taps, so no tap waits); all_covered is false while any line is starved."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        v = view(a, sc.rules)
        assert [ln.store for ln in v.ledger] == [sd.id for sd in sc.rules.stores]
        spent = {p.runner for p in a.pauses
                 if explain(a, sc.rules, RateRef(p.runner, FlowKind.XP)).run.kind is RunKind.SPENT}
        for ln in v.ledger:
            want = value(a, sc.rules, ln.store, t) == 0 and any(
                p.store == ln.store and p.runner not in spent for p in a.pauses)
            assert ln.starved == want, (ln.store, t)
        if any(ln.starved for ln in v.ledger):
            assert not v.all_covered


def _fed(m: int, consumers: list[tuple[int, int]], order: tuple[int, ...]):
    """Store s0, empty, made by a standing action at m a second; cards c<i> consume it at `cost` a second at a 50%
    share (base 2 * cost), the mix listing them in `order`."""
    rules = make_rules([StoreDef(X, 50 * Q, 0)], [card(i, 0, (), (Flow(X, 2 * cost),)) for i, cost in consumers])
    rules = replace(rules, standing=(StandingDef(ActionId("mk"), makes=(Flow(X, m),)),))
    mix = Mix(mix_id(0), tuple(CardShare(card_id(i), BP // 2) for i in order))
    s = decide(new_save(rules), rules, 0, SaveMix(mix))
    return rules, decide(s, rules, 0, SwitchMix(mix_id(0)))


@given(c0=st.integers(1, 200), d=st.integers(1, 200), m=st.integers(0, 10_000))
def test_dry_pauses_last_in_mix_first_until_net_is_not_negative(c0: int, d: int, m: int):
    """Invariant 16 and SPENT ("Giver"): store empty, a standing maker m, consumers c0 then c1 at half shares, with
    2 * c0 <= m < c0 + c1: the last consumer pauses and its share goes to c0, which then draws 2 * c0, still within m,
    so c0 runs on; the pause resumes at min(cap, one hour of its saved cost) via a RESUME event at the exact second."""
    c1 = c0 + d
    m = 2 * c0 + m % (c1 - c0)  # 2 * c0 <= m < c0 + c1
    rules, s = _fed(m, [(0, c0), (1, c1)], (0, 1))
    resume_at = min(50 * Q, 3600 * c1)
    assert s.pauses == (Pause(card_id(1), X, resume_at),)
    assert explain(s, rules, RateRef(card_id(1), FlowKind.COST, X)).per_hour == 0
    e = explain(s, rules, RateRef(card_id(0), FlowKind.COST, X))
    assert (e.per_hour, e.share_bp, tuple((g.card, g.share_bp) for g in e.gained)) == (2 * c0, BP, ((card_id(1), BP // 2),))
    net = m - 2 * c0
    assert segment(s, rules, X).rate == net
    if net > 0:
        ev = next_event(s, rules)
        assert ev is not None and ev.kind == EventKind.RESUME and ev.subject == "c1"
        assert ev.time == -(-resume_at // net)
        assert advance(s, rules, ev.time - 1).pauses != ()
        assert advance(s, rules, ev.time).pauses == ()
    ledger = {ln.store: ln for ln in view(s, rules).ledger}
    assert ledger[X].starved and not view(s, rules).all_covered  # empty, and the last consumer is paused on it
    if net > 0:
        later = advance(s, rules, 1)  # still paused (hysteresis), but the store holds something: not starved
        assert later.pauses != () and value(later, rules, X, 1) > 0
        assert not view(later, rules).ledger[0].starved
    for t in (0, 10, 10_000):
        assert value(s, rules, X, t) >= 0


@given(c0=st.integers(1, 200), c1=st.integers(1, 200), m=st.integers(0, 10_000))
def test_a_consumer_drawing_the_paused_ones_share_past_the_maker_pauses_too(c0: int, c1: int, m: int):
    """Invariant 16 and SPENT ("The instant, and the hour": the rule pauses with the yields of the pauses in force):
    with c0 <= m < 2 * c0 and m < c0 + c1, pausing c1 hands its share to c0, which then draws more than m, so c0
    pauses too; each resumes at an hour of its saved cost and the store fills at m meanwhile."""
    m = c0 + m % min(c0, c1)  # c0 <= m < min(2 * c0, c0 + c1)
    rules, s = _fed(m, [(0, c0), (1, c1)], (0, 1))
    assert s.pauses == (Pause(card_id(0), X, min(50 * Q, 3600 * c0)), Pause(card_id(1), X, min(50 * Q, 3600 * c1)))
    assert segment(s, rules, X).rate == m
    assert [c.run for c in view(s, rules).cards] == [RunKind.PAUSED, RunKind.PAUSED]


@given(c0=st.integers(1, 200), c1=st.integers(1, 200))
def test_dry_with_no_maker_pauses_every_consumer_and_stays_at_zero(c0: int, c1: int):
    """Invariants 9, 16 (canonical, dry): nothing makes the store, so every consumer pauses (last in the mix first),
    save.pauses is in rules.cards order whatever the creation order, the store stays at 0 and never goes negative.
    Both are spent cards, each resuming at an hour of its cost at its saved share, so the line is not starved
    (invariant 41 as SPENT amends it)."""
    rules = make_rules([StoreDef(X, 50 * Q, 0)], [
        card(0, 0, (), (Flow(X, 2 * c0),)),
        card(1, 0, (), (Flow(X, 2 * c1),))])
    mix = Mix(mix_id(0), (CardShare(card_id(0), 5000), CardShare(card_id(1), 5000)))
    s = decide(new_save(rules), rules, 0, SaveMix(mix))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    # created last-in-mix first (c1 then c0) but stored in rules.cards order, each resuming at an hour of its cost
    assert s.pauses == (Pause(card_id(0), X, min(50 * Q, 3600 * c0)), Pause(card_id(1), X, min(50 * Q, 3600 * c1)))
    assert segment(s, rules, X).rate == 0
    assert next_event(s, rules) is None
    assert value(s, rules, X, 10**7) == 0
    v = view(s, rules)
    assert [c.run for c in v.cards] == [RunKind.SPENT, RunKind.SPENT] and not v.ledger[0].starved


@given(c1=st.integers(1, 100), d=st.integers(1, 100), extra=st.integers(0, 10_000))
def test_dry_pausing_follows_mix_order_not_rules_order(c1: int, d: int, extra: int):
    """Invariants 12, 16 (same-instant order, dry): the mix lists c1 before c0 (the opposite of rules order); the
    last in the MIX (c0) pauses first and alone when c1, running c0's share as well, still draws within the maker."""
    c0 = c1 + d
    m = 2 * c1 + extra % (c0 - c1)  # 2 * c1 <= m < c0 + c1: covers c1 at the whole share, not c1 and c0 together
    rules, s = _fed(m, [(0, c0), (1, c1)], (1, 0))
    assert s.pauses == (Pause(card_id(0), X, min(50 * Q, 3600 * c0)),)
    assert segment(s, rules, X).rate == m - 2 * c1


@given(r0=st.integers(1, 500), xp_rate=st.integers(1, 3000))
def test_paused_card_trains_and_works_nothing(r0: int, xp_rate: int):
    """Invariants 10, 16, 41 (explain, dry, starved): once a card is paused for a dry store its XP segment rate is 0,
    equal to the sum of the XP explanations (0 for the paused card), the skill's XP stops growing, and its work (the
    bar) stops with it."""
    rules = make_rules([StoreDef(X, 50 * Q, 0)], [card(0, xp_rate, (), (Flow(X, r0),))])
    mix = Mix(mix_id(0), (CardShare(card_id(0), BP),))
    s = decide(new_save(rules), rules, 0, SaveMix(mix))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    assert s.pauses and s.pauses[0].runner == card_id(0)
    e = explain(s, rules, RateRef(card_id(0), FlowKind.XP))
    assert e.run.kind is RunKind.SPENT and e.per_hour == 0   # nothing makes the store: spent (invariant 133)
    assert s.skills[0].xp.rate == 0
    assert xp(s, rules, SK, 10**6) == xp(s, rules, SK, 0) == 0
    w = explain_work(s, rules, card_id(0))
    assert w.run.kind is RunKind.SPENT and w.per_hour == 0
    assert all(c.work.start_value == 0 for c in advance(s, rules, 10**6).cards)
