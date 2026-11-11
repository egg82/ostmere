"""Lumps paid by work (engine DESIGN.txt, "Rate form"; CHOICES (cards), "One bar"). Written from the contract and the
public interface only. A card's lump (an input or an outcome store, A per completion) moves its store by
floor(A * W(t) / K), W the card's cumulative work (the card view's bar, in work_s * BP units per completion) and
K = work_s * BP, so the lump is whole at every completion boundary at any speed and any work_s.

Each behaviour test has a control beside it: the same world with a work_s that divides (or speed 1.0x), where even the
old per-second lump rate is exact. The behaviour tests were strict xfails against that old rate, so each is shown able
to fail. Cut-and-once agreement (invariant 1) passed under it too; it has a world that can fail it."""
from typing import NamedTuple

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import DrawFn

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, AtLeast, CardDef, CardId, CardShare, Mix, MixId, Modifier,
    ModifierKind, Outcome, PacingCurve, Rules, Save, SaveMix, SkillDef, SkillId, SourceId, StoreDef, StoreId,
    StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, advance, decide, new_save, next_event, segment, value_at,
    view,
)
from ashfall_app.engine.modifiers import WorkRef

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
A, B = CardId("a"), CardId("b")
BIG = 10**6 * Q
MIX = MixId("m")


def world(*cards: CardDef, x_initial: int = 0, triggers: tuple[TriggerDef, ...] = (),
          y_initial: int = 0) -> Rules:
    stores = (StoreDef(X, BIG, x_initial), StoreDef(Y, BIG, y_initial), StoreDef(Z, BIG))
    return Rules(stores=stores, skills=(SkillDef(SkillId("k")),), standing=(), curve=PacingCurve((10**15,)),
                 cards=cards, triggers=triggers)


def lump(work_s: int, items: int = 1, inputs: tuple[Amount, ...] = ()) -> CardDef:
    """Card a on the hands: `items` of y per completion, optional inputs; uncapped, no continuous lines."""
    return CardDef(A, work_s, inputs=inputs, outcome=Outcome(stores=(Amount(Y, items * Q),)))


def speed(*mul_bp: int) -> tuple[Modifier, ...]:
    return tuple(Modifier(WorkRef(A), ModifierKind.MUL_BP, m, SourceId(f"s{i}")) for i, m in enumerate(mul_bp))


def stored(s: Save, r: Rules, store: StoreId) -> int:
    return value_at(segment(s, r, store), s.time)


def card_view(s: Save, r: Rules, c: CardId = A):
    return next(cv for cv in view(s, r).cards if cv.card == c)


def work(s: Save, r: Rules) -> int:
    """The card's cumulative work at the save's time, from its bar."""
    return value_at(card_view(s, r).bar, s.time)


def tap(s: Save, r: Rules) -> Save:
    return decide(s, r, s.time, TapCard(A))


def mixed(r: Rules, share_bp: int, mods: tuple[Modifier, ...] = ()) -> Save:
    s = decide(new_save(r, mods), r, 0, SaveMix(Mix(MIX, (CardShare(A, share_bp),))))
    return decide(s, r, 0, SwitchMix(MIX))


# ---- T1: whole at any speed ----------------------------------------------------------------------------------

def _whole_at_the_end(work_s: int) -> None:
    fired = TriggerDef(TriggerId("t"), AtLeast(StoreValue(Y), Q, Q), Outcome(stores=(Amount(Z, Q),)))
    r = world(lump(work_s), triggers=(fired,))
    s = tap(new_save(r), r)
    before, at = advance(s, r, work_s - 1), advance(s, r, work_s)
    assert stored(at, r, Y) == Q
    assert stored(before, r, Y) < Q
    assert (stored(before, r, Z), stored(at, r, Z)) == (0, Q)


def test_t1_a_tapped_lump_is_whole_at_the_completion_and_its_trigger_fires_then():
    _whole_at_the_end(16560)


def test_t1_control_a_dividing_work_s_is_whole_at_the_completion():
    _whole_at_the_end(10)


# ---- T2: the last partial second -----------------------------------------------------------------------------

def _ten_taps(mul_bp: int) -> tuple[int, int]:
    r = world(lump(4))
    s = new_save(r, speed(mul_bp))
    for _ in range(10):
        s = tap(s, r)
        s = advance(s, r, card_view(s, r).completes_at or s.time)
    return card_view(s, r).completions, stored(s, r, Y)


def test_t2_ten_taps_under_a_work_speed_pay_ten_lumps():
    assert _ten_taps(11_000) == (10, 10 * Q)


@pytest.mark.parametrize("mul_bp", [BP, 2 * BP])
def test_t2_control_a_speed_that_divides_work_s_pays_ten_lumps(mul_bp: int):
    assert _ten_taps(mul_bp) == (10, 10 * Q)


# ---- T3: inputs ----------------------------------------------------------------------------------------------

def _one_input_completion(work_s: int) -> None:
    r = world(lump(work_s, inputs=(Amount(X, Q),)), x_initial=Q)
    s = tap(new_save(r), r)
    at = advance(s, r, work_s)
    assert card_view(at, r).completions == 1
    assert stored(at, r, X) == 0
    assert stored(at, r, Y) == Q
    assert all(ev.time > work_s for ev in [next_event(at, r)] if ev is not None)   # no pause at the boundary


def test_t3_a_single_input_is_paid_whole_and_the_tap_completes_unpaused():
    _one_input_completion(16560)


def test_t3_control_a_dividing_work_s_completes_on_one_input():
    _one_input_completion(10)


# ---- T4: the store moves by floor(A * W / K) -----------------------------------------------------------------

class Scene(NamedTuple):
    work_s: int
    items: int
    mods: list[int]
    how: str
    share: int
    cuts: list[int]


@st.composite
def scenes(draw: DrawFn, dividing: bool) -> Scene:
    """A lone maker, tapped or mixed. Dividing: whole-second completions at every cut (no modifiers, a share of 1,
    1/2 or 1/4 and a work_s those divide)."""
    work_s = draw(st.sampled_from([5, 10, 20, 100]) if dividing else st.integers(1, 20_000))
    mods = [] if dividing else draw(st.lists(st.integers(5000, 15_000), max_size=3))
    share = draw(st.sampled_from([BP, 5000, 2500]) if dividing else st.integers(1, BP))
    return Scene(work_s, draw(st.integers(1, 50)), mods, draw(st.sampled_from(["tap", "mix"])), share,
                 draw(st.lists(st.integers(1, 60_000), min_size=1, max_size=5)))


def _start(sc: Scene, how: str) -> tuple[Save, Rules]:
    r = world(lump(sc.work_s, sc.items))
    s = new_save(r, speed(*sc.mods))
    return (tap(s, r) if how == "tap" else mixed(r, sc.share, speed(*sc.mods))), r


def _gain_matches_work(sc: Scene) -> None:
    s0, r = _start(sc, sc.how)
    k = sc.work_s * BP
    for t in sorted(set(sc.cuts)):
        s = advance(s0, r, t)
        done = card_view(s, r).completions
        if sc.how == "tap":
            assert stored(s, r, Y) == (sc.items * Q if done else sc.items * Q * work(s, r) // k)
        else:
            assert stored(s, r, Y) == sc.items * Q * work(s, r) // k


@given(scenes(False))
def test_t4_a_lone_makers_store_moves_by_floor_of_its_lump_times_work(sc: Scene):
    _gain_matches_work(sc)


@given(scenes(True))
def test_t4_control_dividing_worlds_match_the_same_formula(sc: Scene):
    _gain_matches_work(sc)


def _gain_at_each_boundary(sc: Scene) -> None:
    """The store crosses n whole lumps in completion n's own second, never before, and stands at floor(A * W / K)
    there (the work may run past the boundary within that second)."""
    s, r = _start(sc, "mix")
    a, k = sc.items * Q, sc.work_s * BP
    for n in range(1, 4):
        due = card_view(s, r).completes_at
        if due is None:
            return
        s = advance(s, r, due - 1)
        assert stored(s, r, Y) < n * a
        s = advance(s, r, due)
        assert card_view(s, r).completions == n
        assert n * a <= stored(s, r, Y) == a * work(s, r) // k


@given(scenes(False))
def test_t4_the_gain_at_every_completion_boundary_is_exactly_k_lumps(sc: Scene):
    _gain_at_each_boundary(sc)


@given(scenes(True))
def test_t4_control_dividing_worlds_gain_k_lumps_at_boundary_k(sc: Scene):
    _gain_at_each_boundary(sc)


@given(scenes(False))
def test_t4_advancing_in_cuts_equals_advancing_once(sc: Scene):
    """Invariant 1; passes today and guards a remainder carried between cuts."""
    s0, r = _start(sc, sc.how)
    s = s0
    for t in sorted(set(sc.cuts)):
        s = advance(s, r, t)
    once = advance(s0, r, s.time)
    assert (stored(s, r, Y), card_view(s, r).completions, work(s, r)) == \
           (stored(once, r, Y), card_view(once, r).completions, work(once, r))
