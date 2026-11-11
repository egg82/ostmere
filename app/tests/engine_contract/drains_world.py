"""Fixture rules and readers for the drains contract tests (engine DESIGN.txt, "DRAINS (a take forgiven at 0) AND
FRACTIONS AT THE LOADER", invariants 121-132). Built from the engine's public names only.

One store x is drained, by card CURE (work_s 100, a drain of 10 items by default: x moves at 0.1 item a second while the
card runs at full speed, exactly 360_000 units a second, so every hand-written expectation below is exact). Beside x:
y (a plain make store), i (an input store), x2 (a second drained store), f (a requires store), and the rest are the
test's own."""
from collections.abc import Callable
from dataclasses import replace
from fractions import Fraction
from typing import Any

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, Amount, CardDef, CardId, CardShare, ChipDef, Flow, LaneDef, Mix, MixId, Modifier,
    PacingCurve, Rules, Save, SaveMix, SideDef, SkillDef, SkillId, StandingDef, StoreDef, StoreId, SwitchMix, TapCard,
    ThreatDef, TriggerDef, advance, decide, new_save, per_hour, validate_rules, value, view,
)
from ashfall_app.engine.viewparts import CardView

X, X2, Y, I, F = (StoreId(n) for n in ("xstore", "x2store", "ystore", "istore", "fstore"))
K = SkillId("k")
CURE = CardId("cure")
BIG = 10**6 * Q
MIX = MixId("m")
PER_SECOND = per_hour(3600)
"""One whole item a second as a rate."""
D = 10 * Q // 100
"""The default cure's drain, units a second at a full share: 10 items per completion of 100 s."""


def kills(*mutants: int) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Marks the test as one that must go red for these rows of MUTANTS_drains.txt."""
    return pytest.mark.kills(*mutants)


def cure(a: int = 10 * Q, work_s: int = 100, **kw: Any) -> CardDef:
    """CURE: drains x by `a` per completion; uncapped, on the hands. Any other CardDef field goes in kw."""
    return replace(CardDef(CURE, work_s, drains=(Amount(X, a),)), **kw)


def world(*cards: CardDef, x0: int = 0, i0: int = 0, x2: int = 0, standing: tuple[StandingDef, ...] = (),
          chips: tuple[ChipDef, ...] = (), lanes: tuple[LaneDef, ...] = (), triggers: tuple[TriggerDef, ...] = (),
          sides: tuple[SideDef, ...] = (), threats: tuple[ThreatDef, ...] = (),
          stores: tuple[StoreDef, ...] = ()) -> Rules:
    """Rules over x (starting at x0), x2, y, i (i0) and f, plus `stores`; checked by the engine's own validation."""
    base = (StoreDef(X, BIG, x0), StoreDef(X2, BIG, x2), StoreDef(Y, BIG), StoreDef(I, BIG, i0), StoreDef(F, BIG))
    r = Rules(base + stores, (SkillDef(K),), standing, PacingCurve((10**15,)), lanes=lanes, cards=cards, chips=chips,
              triggers=triggers, sides=sides, threats=threats)
    validate_rules(r)
    return r


def tapped(r: Rules, mods: tuple[Modifier, ...] = (), card: CardId = CURE) -> Save:
    """A new save (at 0) with `card` tapped by the player at 0."""
    return decide(new_save(r, mods), r, 0, TapCard(card))


def mixed(r: Rules, share_bp: int = BP, mods: tuple[Modifier, ...] = (), card: CardId = CURE) -> Save:
    """A new save running a mix of `card` alone at this share."""
    s = decide(new_save(r, mods), r, 0, SaveMix(Mix(MIX, (CardShare(card, share_bp),))))
    return decide(s, r, 0, SwitchMix(MIX))


def at(s: Save, r: Rules, store: StoreId, t: int) -> int:
    return value(s, r, store, t)


def card_view(s: Save, r: Rules, card: CardId = CURE) -> CardView:
    return next(cv for cv in view(s, r).cards if cv.card == card)


def near(v: int, exact: Fraction) -> None:
    """Invariant 11's bound for a lump store: never above the exact rational, and under one unit below it."""
    assert exact - 1 < v <= exact, (v, float(exact))


def drained(x0: int, a: int, work_s: int, work: int) -> Fraction:
    """Invariant 122's exact rational: max(0, x0 - a * work / (work_s * BP)), work in work units (BP a second)."""
    return max(Fraction(0), x0 - Fraction(a * work, work_s * BP))


def pinned() -> tuple[Rules, Save]:
    """Rules with an input, a cost, a make and a standing cost (no drain), and a mixed save at 500 s."""
    card = CardDef(CURE, 100, inputs=(Amount(I, 10 * Q),), makes=(Flow(Y, PER_SECOND),), costs=(Flow(X2, per_hour(1)),))
    r = world(card, x0=5 * Q, i0=100 * Q, x2=50 * Q, standing=(StandingDef(ActionId("heal"), costs=(Flow(X, per_hour(3)),)),))
    return r, advance(mixed(r), r, 500)
