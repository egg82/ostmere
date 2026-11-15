"""Fixture rules for the "or else" contract tests (docs/design/rule-guards.md, "Contract (blind)", statements 14-21),
built from the engine's public names and the note's interface only. `Order(when, then, unless=..., or_else=...)` is
reached through `rule()` at call time, so a module that tests it collects before the field exists.

Stores: W rises by the standing action `wick` (w_rate items a second), and gates the taps' `requires`: a tap that needs
"W is n or more" is unready until W reaches n, a whole second when w_rate divides it. T is what a guard watches, moved
by the standing action `tick`. X, Y, P are made by the mixes.

Lane L holds A1-A3 (1 s unless `dur` says), Z (1 s, for a later rule) and D (10 s); lane L2 holds J. A card with a cap
is dead once it completes that many times. Hands mixes: M1, M2, M3 make X, Y, Z-store; PL is the player's own and makes P.
A hands card with a cap of c and one second of work completes at whole seconds 1..c under a full share, so its mix
greys at c.
"""
from collections.abc import Mapping, Sequence
from typing import Any

import ashfall_app.engine as engine
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, AtLeast, CapRaise, CardDef, CardId, CardShare, Condition, Flow,
    LaneDef, LaneId, Mix, MixId, Order, OrderVerb, Outcome, PacingCurve, Rules, Save, SaveMix, SetOrders, SkillDef, SkillId,
    StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TriggerDef, TriggerId, View, advance, decide, new_save, per_hour,
    view,
)

W, T, X, Y, P, R3 = (StoreId(n) for n in ("w", "t", "x", "y", "p", "r3"))
L, L2 = LaneId("l"), LaneId("l2")
A1, A2, A3, Z, D, J = (CardId(n) for n in ("a1", "a2", "a3", "z", "d", "j"))
G1, G2, G3, GP = (CardId(n) for n in ("g1", "g2", "g3", "gp"))
M1, M2, M3, PL = (MixId(n) for n in ("m1", "m2", "m3", "pl"))
SK = SkillId("k0")
PER_SECOND = per_hour(3600)
ALWAYS = AfterTime(0)
BIG = 10**6 * Q


def need_w(n: int) -> Condition:
    """A plain threshold (release == value), as a card's `requires` must be: W is n items or more."""
    return AtLeast(StoreValue(W), n * Q, n * Q)


def rules(*, w_rate: int = 0, w0: int = 0, t_rate: int = 0, t0: int = 0, dur: Mapping[CardId, int] | None = None,
          req: Mapping[CardId, int] | None = None, cap: Mapping[CardId, int] | None = None,
          triggers: tuple[TriggerDef, ...] = ()) -> Rules:
    """dur: seconds of work per card (default 1; D is 10); req: W items a card needs; cap: completions before it is dead
    (any card; the G cards' caps grey their mixes)."""
    dur, req, cap = dur or {}, req or {}, cap or {}

    def card(c: CardId, lane: LaneId, work: int = 1, **kw: Any) -> CardDef:
        return CardDef(c, dur.get(c, work), lane=lane, cap=cap.get(c), requires=(need_w(req[c]),) if c in req else (), **kw)

    standing = (StandingDef(ActionId("wick"), makes=(Flow(W, w_rate * PER_SECOND),)),) if w_rate else ()
    standing += (StandingDef(ActionId("tick"), makes=(Flow(T, t_rate * PER_SECOND),)),) if t_rate else ()
    cards = (card(A1, L), card(A2, L), card(A3, L), card(Z, L), card(D, L, 10), card(J, L2),
             CardDef(G1, dur.get(G1, 1), skill=SK, cap=cap.get(G1), makes=(Flow(X, PER_SECOND),)),
             CardDef(G2, dur.get(G2, 1), skill=SK, cap=cap.get(G2), makes=(Flow(Y, PER_SECOND),)),
             CardDef(G3, dur.get(G3, 1), skill=SK, cap=cap.get(G3), makes=(Flow(R3, PER_SECOND),)),
             CardDef(GP, 60, skill=SK, makes=(Flow(P, PER_SECOND),)))
    stores = (StoreDef(W, 1000 * Q, w0 * Q), StoreDef(T, 100 * Q, t0 * Q), StoreDef(X, BIG), StoreDef(Y, BIG),
              StoreDef(P, BIG), StoreDef(R3, BIG))
    return Rules(stores=stores, skills=(SkillDef(SK),), standing=standing, curve=PacingCurve((10**15,)),
                 lanes=(LaneDef(L), LaneDef(L2)), cards=cards, triggers=triggers)


def start(r: Rules, orders: Sequence[Order]) -> Save:
    """At 0: the four mixes saved, the player's own running, then the orders."""
    s = new_save(r)
    for m, c in ((M1, G1), (M2, G2), (M3, G3), (PL, GP)):
        s = decide(s, r, 0, SaveMix(Mix(m, (CardShare(c, BP),))))
    s = decide(s, r, 0, SwitchMix(PL))
    return decide(s, r, 0, SetOrders(tuple(orders)))


def rule(when: Condition, then: OrderVerb, or_else: tuple[OrderVerb, ...] = (), *unless: Condition) -> Order:
    """Order(when, then, unless=..., or_else=...), the keyword fields passed by name."""
    kw: dict[str, Any] = {"when": when, "then": then}
    if unless:
        kw["unless"] = tuple(unless)
    if or_else:
        kw["or_else"] = or_else
    return Order(**kw)


def expanded(o: Order) -> tuple[Order, ...]:
    """The n adjacent plain orders a rule with actions a1..an stands for (statement 14): Order(when, ak, unless)."""
    actions = (o.then, *getattr(o, "or_else", ()))
    return tuple(Order(o.when, a, unless=getattr(o, "unless", ())) for a in actions)


def raise_at(at: int, card: CardId, by: int) -> TriggerDef:
    """A trigger at `at` that raises `card`'s cap by `by` completions (it un-greys a mix holding it)."""
    return TriggerDef(TriggerId(f"raise{at}"), AfterTime(at), Outcome(raises=(CapRaise(card, by),)))


def lane_card(s: Save, lane: LaneId = L) -> CardId | None:
    for ls in s.lanes:
        if ls.lane == lane:
            return ls.card
    return None


def timeline(r: Rules, s: Save, until: int) -> list[tuple[CardId | None, object, int]]:
    """Per whole second 0..until: the card L runs, the running mix and W's whole items."""
    out: list[tuple[CardId | None, object, int]] = []
    for t in range(until + 1):
        s = advance(s, r, t)
        out.append((lane_card(s), view(s, r).running_mix, engine.value(s, r, W, t) // Q))
    return out


def lanes(r: Rules, s: Save, until: int) -> list[CardId | None]:
    return [c for c, _, _ in timeline(r, s, until)]


def mixes(r: Rules, s: Save, until: int) -> list[object]:
    return [m for _, m, _ in timeline(r, s, until)]


def view_at(r: Rules, s: Save, t: int) -> View:
    return view(advance(s, r, t), r)


def observe(r: Rules, s: Save, t: int) -> tuple[object, ...]:
    """What statement 14 compares at second t: both lanes, the running mix, every store, every card's completions."""
    v = view(s, r)
    done = tuple(sorted((str(c.card), c.completions) for c in (*v.cards, *v.completed)))
    stores = tuple(engine.value(s, r, st, t) for st in (W, T, X, Y, P, R3))
    return lane_card(s, L), lane_card(s, L2), v.running_mix, stores, done
