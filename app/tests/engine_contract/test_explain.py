"""Invariants 10-11: explain agrees with the segment rate and the formula; rounding never favours the player."""
from dataclasses import replace
from random import Random

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, CardId, FlowKind, Modifier, ModifierKind, RateRef,
    Run, RunKind, Runner, SourceId, StoreId, advance, explain,
    flatten_shares, modified_rate, segment, view,
)
from contract_gen import ceil_frac, exact_rate, flow_refs, floor_frac, play, probe_times, scenario_st, Scenario

_ref = RateRef(CardId("c0"), FlowKind.MAKE, StoreId("s0"))
_other = RateRef(CardId("c1"), FlowKind.MAKE, StoreId("s0"))


def _mod(kind: ModifierKind, amount: int, ref: RateRef = _ref, n: int = 0):
    return Modifier(ref, kind, amount, SourceId(f"src{n}"))


_stack = st.lists(
    st.tuples(st.sampled_from(list(ModifierKind)), st.integers(-12_000, 40_000), st.booleans()), max_size=6
).map(lambda xs: tuple(
    _mod(k, abs(a) if k is ModifierKind.MUL_BP else a, _ref if hit else _other, i) for i, (k, a, hit) in enumerate(xs)))

_run = st.one_of(
    st.just(Run(RunKind.FULL)),
    st.just(Run(RunKind.PAUSED, 0, 1, StoreId("s0"))),
)


def _expect(ref: RateRef, base: int, share: int, stack: tuple[Modifier, ...], run: Run):
    mine = [m for m in stack if m.target == ref]
    adds = [m.amount_bp for m in mine if m.kind is ModifierKind.ADD_BP]
    muls = [m.amount_bp for m in mine if m.kind is ModifierKind.MUL_BP]
    ex = exact_rate(base, share, adds, muls, run.num, run.den)
    return ex, (ceil_frac(ex) if ref.kind is FlowKind.COST else floor_frac(ex))


@given(kind=st.sampled_from(list(FlowKind)), base=st.integers(0, 50_000), share=st.integers(0, BP),
       stack=_stack, run=_run)
def test_modified_rate_matches_the_formula_with_one_rounding(kind: FlowKind, base: int, share: int, stack: tuple[Modifier, ...], run: Run):
    """Invariants 10, 11 (explain, rounding): per_hour is the documented formula rounded once, down for makes and
    XP, up for costs; the explanation echoes its inputs; stack entries aimed elsewhere are ignored."""
    ref = RateRef(_ref.runner, kind, None if kind is FlowKind.XP else _ref.store)
    stack = tuple(Modifier(ref if m.target == _ref else m.target, m.kind, m.amount_bp, m.source) for m in stack)
    exp = modified_rate(ref, base, share, stack, run)
    ex, want = _expect(ref, base, share, stack, run)
    assert exp.per_hour == want
    if kind is FlowKind.COST:
        assert exp.per_hour >= ex
        if ex > 0:
            assert exp.per_hour >= 1  # a non-zero cost never rounds to free
    else:
        assert exp.per_hour <= ex  # makes and XP are never rounded up
    assert (exp.ref, exp.base_per_hour, exp.share_bp, exp.run) == (ref, base, share, run)
    assert exp.adds == tuple(m for m in stack if m.target == ref and m.kind is ModifierKind.ADD_BP)
    assert exp.muls == tuple(m for m in stack if m.target == ref and m.kind is ModifierKind.MUL_BP)


@given(st.integers(0, 50_000), st.integers(0, BP), st.integers(-12_000, 0))
def test_additive_sum_floors_at_zero(base: int, share: int, neg: int):
    """Invariant 11 (rounding): a negative additive total (below -100%) gives 0, never a negative rate."""
    stack = (_mod(ModifierKind.ADD_BP, neg - BP),)
    assert modified_rate(_ref, base, share, stack, Run(RunKind.FULL)).per_hour == 0


@given(base=st.integers(0, 50_000), share=st.integers(0, BP), stack=_stack, seed=st.randoms())
def test_modifier_order_does_not_change_the_rate(base: int, share: int, stack: tuple[Modifier, ...], seed: Random):
    """Invariant 10 (explain): additive entries sum and multipliers compound commutatively, so the stack order
    never changes per_hour (two +10% are +20% whichever comes first)."""
    shuffled = list(stack)
    seed.shuffle(shuffled)
    a = modified_rate(_ref, base, share, stack, Run(RunKind.FULL)).per_hour
    assert modified_rate(_ref, base, share, tuple(shuffled), Run(RunKind.FULL)).per_hour == a


@given(base=st.integers(1, 50_000), share=st.integers(1, BP), n=st.integers(1, 5), amt=st.integers(1, 3000))
def test_additive_entries_do_not_compound(base: int, share: int, n: int, amt: int):
    """Invariant 10 (explain): n additive entries of +a% equal one entry of +n*a%."""
    many = tuple(_mod(ModifierKind.ADD_BP, amt, n=i) for i in range(n))
    one = (_mod(ModifierKind.ADD_BP, n * amt),)
    f = Run(RunKind.FULL)
    assert modified_rate(_ref, base, share, many, f).per_hour == modified_rate(_ref, base, share, one, f).per_hour


@given(sc=scenario_st())
def test_explain_agrees_with_inputs_and_formula(sc: Scenario):
    """Invariant 10 (explain): every Explanation's inputs come from the rules, the running mix and the save's
    modifiers, per_hour == modified_rate(...) on them and equals the exact formula; paused cards contribute 0. A share
    is the saved one plus what paused cards give it, each named in gained (invariant 137); a card paused on a spent
    store reads SPENT."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        running = view(a, sc.rules).running_mix
        shares: dict[Runner, int] = {x.card: x.share_bp for x in flatten_shares(a.mixes, running)} if running else {}
        paused = {p.runner for p in a.pauses}
        for ref, base in flow_refs(sc.rules):
            e = explain(a, sc.rules, ref)
            assert e.ref == ref and e.base_per_hour == base
            assert e.share_bp == shares.get(ref.runner, 0) + sum(g.share_bp for g in e.gained)
            assert e.base_den == 1  # a flow, not a card's lump line
            assert e.adds == tuple(m for m in a.modifiers if m.target == ref and m.kind is ModifierKind.ADD_BP)
            assert e.muls == tuple(m for m in a.modifiers if m.target == ref and m.kind is ModifierKind.MUL_BP)
            assert replace(e, gained=()) == modified_rate(ref, e.base_per_hour, e.share_bp, a.modifiers, e.run)
            assert e.per_hour == _expect(ref, e.base_per_hour, e.share_bp, a.modifiers, e.run)[1]
            if ref.runner in paused:
                assert e.run.kind in (RunKind.PAUSED, RunKind.SPENT) and e.per_hour == 0


@given(sc=scenario_st())
def test_segment_rate_is_makes_minus_costs(sc: Scenario):
    """Invariant 10 (explain): for a store strictly inside (0, cap), the segment rate equals the
    sum of its MAKE per_hour minus its COST per_hour."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        for sd in sc.rules.stores:
            seg = segment(a, sc.rules, sd.id)
            if not 0 < seg.start_value < sd.cap:
                continue
            net = 0
            for cd in sc.rules.cards:
                for f in cd.makes:
                    if f.store == sd.id:
                        net += explain(a, sc.rules, RateRef(cd.id, FlowKind.MAKE, sd.id)).per_hour
                for f in cd.costs:
                    if f.store == sd.id:
                        net -= explain(a, sc.rules, RateRef(cd.id, FlowKind.COST, sd.id)).per_hour
            assert seg.rate == net, (sd.id, t)


@given(sc=scenario_st())
def test_xp_segment_rate_is_the_sum_of_its_explanations(sc: Scenario):
    """Invariant 10 (explain): a skill's XP segment rate equals the sum of the XP explanations of the cards that
    train it (0 once XP sits at the last threshold)."""
    s = play(sc)
    top = sc.rules.curve.thresholds[-1]
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        for sk in a.skills:
            want = sum(explain(a, sc.rules, RateRef(x.id, FlowKind.XP)).per_hour
                       for x in sc.rules.cards if x.skill == sk.skill)
            assert sk.xp.rate == (0 if sk.xp.start_value >= top else want), (sk.skill, t)


@given(kind=st.sampled_from([FlowKind.MAKE, FlowKind.COST]), lump=st.integers(1, 50_000_000), work_s=st.integers(1, 100_000),
       share=st.integers(0, BP), stack=_stack)
def test_a_lump_line_divides_by_its_work_time_once(kind: FlowKind, lump: int, work_s: int, share: int, stack: tuple[Modifier, ...]):
    """Invariants 10, 11 (explain, rounding; DESIGN.txt "Rate form"): a card's lump line (quantity per completion
    `lump`, base_den = work_s) runs at lump / work_s per hour at a full share, through the same formula and a single
    rounding (down for outcome stores, up for inputs); the Explanation echoes base_den."""
    ref = RateRef(_ref.runner, kind, _ref.store)
    stack = tuple(Modifier(ref if m.target == _ref else m.target, m.kind, m.amount_bp, m.source) for m in stack)
    run = Run(RunKind.FULL)
    exp = modified_rate(ref, lump, share, stack, run, work_s)
    mine = [m for m in stack if m.target == ref]
    ex = exact_rate(lump, share, [m.amount_bp for m in mine if m.kind is ModifierKind.ADD_BP],
                    [m.amount_bp for m in mine if m.kind is ModifierKind.MUL_BP], 1, work_s)
    assert exp.per_hour == (ceil_frac(ex) if kind is FlowKind.COST else floor_frac(ex))
    assert exp.base_den == work_s and exp.base_per_hour == lump
