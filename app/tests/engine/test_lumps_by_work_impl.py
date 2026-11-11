"""Lumps paid by work (engine DESIGN.txt, "Rate form", invariant 80): a store moves by floor(G), G the sum of each
lump's amount times its card's work over the work per completion, so a whole completion pays exactly its amount at
any speed and a lump stops where its work stops.

Each directed test runs a control beside it: the same world at a whole-second speed, which the rounded per-second
rate this replaced already paid exactly, so a test shows it can tell the two apart."""
from fractions import Fraction
from math import floor

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, AtLeast, CardDef, CardId, CardShare, LineKey, Mix, MixId,
    Modifier, ModifierKind, Outcome, PacingCurve, Rules, Save, SaveMix, SkillDef, SkillId, SourceId,
    StoreDef, StoreId, StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, WorkRef, advance,
    advance_logged, decide, new_save, segment, validate_rules, value_at,
)
from ashfall_app.engine.segments import Lump, LumpSegment, Segment, reach_time

X, Y = StoreId("x"), StoreId("y")
C = CardId("c")
FIRST = LineKey("first.line")


def world(work_s: int, *, outcome: int = 0, inputs: int = 0, x0: int = 0, speed_bp: tuple[int, ...] = (),
          trigger: bool = False) -> tuple[Rules, Save]:
    """One uncapped HANDS card c of work_s seconds making `outcome` units of y and taking `inputs` units of x a
    completion; its work runs at the product of `speed_bp`; with `trigger`, y reaching one completion's outcome fires a
    line."""
    card = CardDef(C, work_s, outcome=Outcome(stores=(Amount(Y, outcome),) if outcome else ()),
                   inputs=(Amount(X, inputs),) if inputs else ())
    triggers = (TriggerDef(TriggerId("first"), AtLeast(StoreValue(Y), outcome, outcome), Outcome(lines=(FIRST,))),
                ) if trigger else ()
    r = Rules(stores=(StoreDef(X, 10**6 * Q, x0), StoreDef(Y, 10**6 * Q)), skills=(SkillDef(SkillId("k")),),
              standing=(), curve=PacingCurve((10**15,)), cards=(card,), triggers=triggers)
    validate_rules(r)
    mods = tuple(Modifier(WorkRef(C), ModifierKind.MUL_BP, m, SourceId(f"m{i}")) for i, m in enumerate(speed_bp))
    return r, new_save(r, mods)


def val(s: Save, r: Rules, store: StoreId) -> int:
    return segment(s, r, store).start_value


def test_a_long_one_item_card_pays_its_item_at_the_second_its_work_completes():
    """The fit pass's T1: work_s 16560, one item, full speed. The rounded rate paid Q - 6480 and the trigger never
    fired; paid by work, y is Q at 16560, one second earlier it is short, and the trigger fires at 16560."""
    for work_s in (16560, 16000):   # 16000 divides Q * BP: the control
        r, s = world(work_s, outcome=Q, trigger=True)
        s = decide(s, r, 0, TapCard(C))
        before = advance(s, r, work_s - 1)
        assert val(before, r, Y) < Q and not before.fired[0]
        step = advance_logged(before, r, work_s)
        assert val(step.save, r, Y) == Q and step.save.fired[0]
        assert [ln.time for ln in step.lines if ln.key == FIRST] == [work_s]


def test_ten_taps_at_a_speed_with_no_whole_duration_pay_ten_outcomes():
    """The fit pass's T2: work_s 4 at 1.1x lands each tap 3.64 s in; the last partial second used to pay on, 2.2 items
    a tap. Paid by work, ten taps are ten completions and exactly ten outcomes; 2x (2 s, whole) is the control."""
    for speed in ((11_000,), (11_000, 11_000, 11_000), (5_000, 11_000), (20_000,)):
        r, s = world(4, outcome=2 * Q, speed_bp=speed)
        for _ in range(10):
            s = advance(decide(s, r, s.time, TapCard(C)), r, s.time + 30)
        assert val(s, r, Y) == 20 * Q, speed


def test_a_tap_with_one_whole_input_in_store_completes_and_empties_it():
    """The fit pass's T3 and the stall (iii): x holds exactly one completion's input; the input's rounded-up rate used
    to empty x before the work reached its boundary, pausing the card 0 completions in. Paid by work, x reaches 0 at
    the completion, the tap lands, nothing is paused."""
    for work_s in (16560, 16000):
        r, s = world(work_s, inputs=Q, x0=Q, outcome=Q)
        s = decide(s, r, 0, TapCard(C))
        mid = advance(s, r, work_s - 1)
        assert val(mid, r, X) > 0 and mid.pauses == ()
        end = advance(mid, r, work_s)
        assert val(end, r, X) == 0 and val(end, r, Y) == Q and end.pauses == ()
        assert next(cs for cs in end.cards if cs.card == C).work.start_value == work_s * BP
        assert all(ls.card is None for ls in end.lanes)


def test_a_mixed_card_with_one_whole_input_pays_it_and_pauses_at_the_boundary():
    """DESIGN.txt, "Inputs against a dry store", in the mix at a speed with no whole duration: x empties at the first
    completion, which counts, and the card pauses there instead of running its next completion unpaid. A mix card's
    work has no limit, so its last second runs past the boundary (1000 of 11000 work units here): y is paid for that
    second's part, under one second's pay, and x, at 0, is not charged for it."""
    r, s = world(100, inputs=Q, x0=Q, outcome=Q, speed_bp=(11_000,))
    s = decide(decide(s, r, 0, SaveMix(Mix(MixId("m"), (CardShare(C, BP),)))), r, 0, SwitchMix(MixId("m")))
    end = advance(s, r, 1_000)
    assert val(end, r, X) == 0 and Q <= val(end, r, Y) < Q + Q * 11_000 // (100 * BP)
    assert next(cs for cs in end.cards if cs.card == C).work.start_value // (100 * BP) == 1
    assert [p.runner for p in end.pauses] == [C]


def test_a_store_no_lump_touches_keeps_the_plain_segment():
    """A store no lump line touches keeps the plain Segment: segment() gives the type the save holds."""
    r, s = world(4, outcome=2 * Q)
    s = decide(s, r, 0, TapCard(C))
    assert type(segment(s, r, X)) is Segment and isinstance(segment(s, r, Y), LumpSegment)
    assert all(type(st.segment) is Segment for st in s.stores)


@st.composite
def lump_segments(draw: st.DrawFn) -> LumpSegment:
    """A store moved by a flow and up to three lumps, each card's work rising at its own speed toward a limit (a tap's
    next completion) or with none."""
    den = draw(st.integers(1, 50_000))
    lumps: list[Lump] = []
    for _ in range(draw(st.integers(1, 3))):
        w0 = draw(st.integers(0, 10_000))
        rate = draw(st.integers(1, 3_000))
        limit = draw(st.one_of(st.none(), st.integers(w0 + 1, w0 + 200_000)))
        lumps.append(Lump(Segment(0, w0, rate, limit), draw(st.integers(-4_000, 4_000))))
    flow = draw(st.integers(-200, 200))
    v0 = draw(st.integers(0, 10**6))
    slope = flow * den + sum(k.num * k.work.rate for k in lumps)
    beyond = st.integers(v0 + 1, v0 + 10**6) if slope > 0 else st.integers(0, v0 - 1) if v0 > 0 else st.nothing()
    limit = None if slope == 0 else draw(st.one_of(st.none(), beyond))
    return LumpSegment(0, v0, slope // den, limit, flow, den, tuple(lumps))


@given(seg=lump_segments(), target_off=st.integers(-3_000, 3_000))
def test_reach_time_is_the_first_second_value_at_reaches_the_target(seg: LumpSegment, target_off: int):
    """value_at is the exact rational with one floor (checked against Fractions), clamped at the limit; reach_time
    is the first integer second it reaches the target, found by scanning, or None when the scan never does."""
    def exact(t: int) -> int:
        g = sum(Fraction(k.num * value_at(k.work, t), seg.den) for k in seg.lumps)
        g0 = sum(Fraction(k.num * k.work.start_value, seg.den) for k in seg.lumps)
        return seg.start_value + seg.flow * t + floor(g) - floor(g0)
    horizon = 250
    for t in range(horizon):
        raw = exact(t)
        if seg.limit is not None:
            raw = min(raw, seg.limit) if seg.limit > seg.start_value else max(raw, seg.limit)
        assert value_at(seg, t) == raw, t
    target = max(0, seg.start_value + target_off)
    up = target >= seg.start_value
    first = next((t for t in range(horizon) if (value_at(seg, t) >= target if up else value_at(seg, t) <= target)), None)
    got = reach_time(seg, target)
    if first is not None:
        assert got == first
    else:
        assert got is None or got >= horizon
