"""Fixture rules for the rule-guards contract tests (docs/design/rule-guards.md, "Contract (blind)", statements 1-13 and
22-24), built from the engine's public names and the note's interface only. The names guards add (Order.unless,
Order.or_else, GuardedLatch, OrderState.PAUSED, View.order_guards) are reached through the functions below, at call
time, so a module that tests them collects before they exist.

One store T is what guards (and some `when`s) watch; it moves by exactly one item a second or not at all, so every
level that is a whole number of items is crossed at a whole second:

- by the player's hands mix: UP makes T, DOWN costs T, IDLE makes only X; or
- by the standing action `tick` (t_rate items a second), when the rule's own mix must not move it.

W is a second store, moved only by the standing action `wick`, for a `when` that must move on its own. The rule taps
K, a one-second card on lane L, or switches to a mix. With K, the lane holds K at a whole second exactly while the
rule is on: a tap started at t lands at t + 1, where the rule taps again if it is still on.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import pytest
from hypothesis import strategies as st

import ashfall_app.engine as engine
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AtLeast, AtMost, CardDef, CardId, CardShare, Condition, Flow, LaneDef,
    LaneId, LineKey, Mix, MixId, Modifier, ModifierKind, Order, OrderState, OrderVerb, Outcome, PacingCurve, Rules, Save,
    SaveMix, SetOrders, SkillDef, SkillId, SourceId, StandingDef, StoreCap, StoreDef, StoreId, StoreValue, SwitchMix,
    OfferDef, TriggerDef, TriggerId, View, decide, new_save, per_hour,
)

T, W, X, Y = StoreId("t"), StoreId("w"), StoreId("x"), StoreId("y")
L, L2 = LaneId("l"), LaneId("l2")
K, K2, K3, K4, KL, J = (CardId(n) for n in ("k", "k2", "k3", "k4", "kl", "j"))
K_DONE = LineKey("k.done")
CU, CD, CI, CR, CR2 = CardId("cu"), CardId("cd"), CardId("ci"), CardId("cr"), CardId("cr2")
UP, DOWN, IDLE, RM, RM2 = MixId("up"), MixId("down"), MixId("idle"), MixId("rm"), MixId("rm2")
SK = SkillId("k0")
PER_SECOND = per_hour(3600)
ALWAYS = AfterTime(0)
BIG = 10**6 * Q
SLOPE_MIX = {1: UP, -1: DOWN, 0: IDLE}


def rules(*, t0: int = 0, cap: int = 100, t_rate: int = 0, w0: int = 0, w_rate: int = 0,
          triggers: tuple[TriggerDef, ...] = (), max_firings: int = 1000, k_cap: int = 10**6,
          offers: tuple[OfferDef, ...] = ()) -> Rules:
    """The world. t0, cap, w0 in whole items; t_rate and w_rate in items a second (0: no such standing action).
    k_cap: K's cap (the default is never reached, so K can always act). On lane L: K (1 s, a line per completion), K2-K4 (1 s) and
    KL (10 s, making X at one item a second and one item of Y as it lands); on lane L2: J (1 s)."""
    standing: list[StandingDef] = []
    if t_rate:
        standing.append(StandingDef(ActionId("tick"), makes=(Flow(T, t_rate * PER_SECOND),)))
    if w_rate:
        standing.append(StandingDef(ActionId("wick"), makes=(Flow(W, w_rate * PER_SECOND),)))
    cards = (
        CardDef(CU, 60, skill=SK, makes=(Flow(T, PER_SECOND),)),
        CardDef(CD, 60, skill=SK, costs=(Flow(T, PER_SECOND),)),
        CardDef(CI, 60, skill=SK, makes=(Flow(X, PER_SECOND),)),
        CardDef(CR, 60, skill=SK, makes=(Flow(X, PER_SECOND),)),
        CardDef(CR2, 60, skill=SK, makes=(Flow(X, PER_SECOND),)),
        CardDef(K, 1, lane=L, cap=k_cap, outcome=Outcome(lines=(K_DONE,))),
        CardDef(K2, 1, lane=L),
        CardDef(K3, 1, lane=L),
        CardDef(K4, 1, lane=L),
        CardDef(KL, 10, lane=L, makes=(Flow(X, PER_SECOND),), outcome=Outcome(stores=(Amount(Y, Q),))),
        CardDef(J, 1, lane=L2),
    )
    return Rules(stores=(StoreDef(T, cap * Q, t0 * Q), StoreDef(W, 1000 * Q, w0 * Q), StoreDef(X, BIG), StoreDef(Y, BIG)),
                 skills=(SkillDef(SK),), standing=tuple(standing), curve=PacingCurve((10**15,)),
                 max_firings_per_instant=max_firings, lanes=(LaneDef(L), LaneDef(L2)), cards=cards, triggers=triggers,
                 offers=offers)


def cap_raise(at: int, factor_bp: int) -> TriggerDef:
    """A trigger at `at` multiplying T's cap by factor_bp / BP."""
    return TriggerDef(TriggerId(f"raise{at}"), AfterTime(at),
                      Outcome(modifiers=(Modifier(StoreCap(T), ModifierKind.MUL_BP, factor_bp, SourceId("raise")),)))


def tick_at(at: int, n: int = 1) -> tuple[TriggerDef, ...]:
    """n triggers at `at` that change nothing: each is one firing at that instant."""
    return tuple(TriggerDef(TriggerId(f"tick{at}_{i}"), AfterTime(at), Outcome()) for i in range(n))


def start(r: Rules, orders: Sequence[Order], active: MixId = IDLE) -> Save:
    """At 0: every mix saved, `active` the player's own, then the orders."""
    s = new_save(r)
    for m, c in ((UP, CU), (DOWN, CD), (IDLE, CI), (RM, CR), (RM2, CR2)):
        s = decide(s, r, 0, SaveMix(Mix(m, (CardShare(c, BP),))))
    s = decide(s, r, 0, SwitchMix(active))
    return decide(s, r, 0, SetOrders(tuple(orders)))


def lane_card(s: Save, lane: LaneId = L) -> CardId | None:
    for ls in s.lanes:
        if ls.lane == lane:
            return ls.card
    return None


def kills(*rows: int) -> pytest.MarkDecorator:
    """Marks the test as one that must go red for these rows of MUTANTS_guards.txt."""
    return pytest.mark.kills(*rows)


# ---- the names guards add, reached at call time ---------------------------------------------------------------------

def order(when: Condition, then: OrderVerb, **lists: tuple[Any, ...]) -> Order:
    """Order(when, then, unless=..., or_else=...), passed by name so a module calling it collects before the fields
    exist."""
    kw: dict[str, Any] = {"when": when, "then": then, **lists}
    return Order(**kw)


def guarded(when: Condition, then: OrderVerb, *unless: Condition) -> Order:
    """Order(when, then, unless=...): the note's shape, "What a rule is"."""
    return order(when, then, unless=tuple(unless))


def with_else(when: Condition, then: OrderVerb, or_else: tuple[OrderVerb, ...], *unless: Condition) -> Order:
    return order(when, then, unless=tuple(unless), or_else=or_else)


def guarded_latch(when: bool, unless: Sequence[bool]) -> Any:
    """GuardedLatch(when, unless), the saved form of a guarded rule's latches ("The saved shape"). Taken from the engine
    package: where it is defined is not in the note (gaps.txt)."""
    return getattr(engine, "GuardedLatch")(when, tuple(unless))


def paused() -> OrderState:
    return getattr(OrderState, "PAUSED")


def guard_on(v: View, i: int, j: int) -> bool:
    return bool(getattr(v, "order_guards")[i][j].on)


def when_of(latch: object) -> bool:
    """The `when` latch of a saved latch entry, in either form."""
    return latch if isinstance(latch, bool) else bool(getattr(latch, "when"))


def guards_of(latch: object) -> tuple[bool, ...]:
    return () if isinstance(latch, bool) else tuple(getattr(latch, "unless"))


# ---- conditions on T, in whole items --------------------------------------------------------------------------------

def at_least(v: int, r: int, subject: StoreId = T) -> AtLeast:
    return AtLeast(StoreValue(subject), v * Q, r * Q)


def at_most(v: int, r: int, subject: StoreId = T) -> AtMost:
    return AtMost(StoreValue(subject), v * Q, r * Q)


def block_from(v: int) -> AtLeast:
    """The page's guard "unless T is v or more": blocks from v, lets go under v - 1 (one item of band)."""
    return at_least(v, v - 1)


# ---- the reference: T over time, and a latch read off it ------------------------------------------------------------

@dataclass(frozen=True)
class Path:
    """T in whole items at each whole second 0..end, and the player's switches that make it (time, mix)."""

    values: tuple[int, ...]
    switches: tuple[tuple[int, MixId], ...]


def path(t0: int, segments: Sequence[tuple[int, int]]) -> Path:
    """segments: (seconds, slope) with slope in -1, 0, 1, played from 0. The caller keeps T inside 1..cap-1."""
    values: list[int] = [t0]
    switches: list[tuple[int, MixId]] = []
    t, x = 0, t0
    for dur, slope in segments:
        switches.append((t, SLOPE_MIX[slope]))
        for _ in range(dur):
            x += slope
            values.append(x)
        t += dur
    return Path(tuple(values), tuple(switches))


def latch_series(cond: AtLeast | AtMost, values: Sequence[int], first: bool | None = None) -> tuple[bool, ...]:
    """The latch of a quantity-level condition on T at each whole second: set from its value alone at 0 (or `first`),
    then on at its value and off past its release (orders.AtLeast / AtMost)."""
    v, r = cond.value // Q, cond.release // Q
    out: list[bool] = []
    latch = False
    for i, x in enumerate(values):
        if i == 0:
            latch = (x >= v if isinstance(cond, AtLeast) else x <= v) if first is None else first
        elif isinstance(cond, AtLeast):
            latch = (x >= v) if not latch else not (x < r)
        else:
            latch = (x <= v) if not latch else not (x > r)
        out.append(latch)
    return tuple(out)


# ---- drawn scenes ---------------------------------------------------------------------------------------------------

type Scene = tuple[int, list[tuple[int, int]], Condition, list[AtLeast | AtMost]]


def cond(kind: bool, v: int, gap: int) -> AtLeast | AtMost:
    return at_least(v, max(0, v - gap)) if kind else at_most(v, v + gap)


COND = st.builds(cond, st.booleans(), st.integers(1, 40), st.integers(0, 3))


@st.composite
def scene_st(draw: st.DrawFn) -> Scene:
    """T's start, the player's spans (seconds, slope) keeping T in 1..99, a `when` and one to three guards on T."""
    t0 = draw(st.integers(5, 30))
    segments: list[tuple[int, int]] = []
    x = t0
    for _ in range(draw(st.integers(1, 6))):
        slope = draw(st.sampled_from([-1, 0, 1]))
        dur = draw(st.integers(1, 8))
        dur = min(dur, x - 1) if slope < 0 else min(dur, 99 - x) if slope > 0 else dur
        if dur > 0:
            segments.append((dur, slope))
            x += slope * dur
    if not segments:
        segments = [(4, 0)]
    when = draw(st.one_of(st.just(ALWAYS), COND))
    guards = draw(st.lists(COND, min_size=1, max_size=3, unique=True))
    return t0, segments, when, guards
