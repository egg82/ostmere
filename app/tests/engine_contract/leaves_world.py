"""Fixture rules for the leaves contract tests (engine DESIGN.txt, "LEAVES", invariants 148-155), built from the engine's
public names and the stated interface only. The names a leave adds (Leave, UnlockKind.LEFT, Ended) are reached through
the functions below, at call time, so a module that tests them collects before they exist.

Three ruled lanes. la is the leaver: a1, a2 uncapped (x, w), ac (capped, 50 s, pays 5 items of y by its rate form) and
ad (capped, 30 s). lb stays: b1, b2 uncapped (v, u), bc (capped, 50 s). ld is a person who never joins. Two standing
actions: `stop` (z, named by the leave) and `keep` (z2). Every card takes 10 s a completion at full speed unless said.
Both people join at 0 into the town mix (or, solo, each into a mix of their own), which holds shares of every uncapped card;
the hands tap hc (a capped card) at 0, which greys the hands mix `hm` at 30. la leaves at LEAVE_AT, while ac (started by
an order at 20) is running; ac would complete at 70."""
from typing import Any

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AtLeast, CardDef, CardId, CardShare, Flow,
    Join, LaneDef, LaneId, LineKey, Mix, MixId, Order, Outcome, PacingCurve, RuleChange, Rules, Save, SaveMix, SetOrders, SkillDef,
    SkillId, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, advance,
    decide, new_save, per_hour, validate_rules,
)
from town_mix_world import TM, TM2

LA, LB, LD = LaneId("la"), LaneId("lb"), LaneId("ld")
X, W, Y, V, U, Z, Z2, S, HS = (StoreId(n) for n in ("x", "w", "y", "v", "u", "z", "z2", "s", "hs"))
A1, A2, AC, AD, B1, B2, BC, D1, DC, H1, HC = (CardId(n) for n in (
    "a1", "a2", "ac", "ad", "b1", "b2", "bc", "d1", "dc", "h1", "hc"))
STOP, KEEP = ActionId("stop"), ActionId("keep")
HM = MixId("hm")
AC_DONE, AD_DONE, BC_DONE = LineKey("ac.done"), LineKey("ad.done"), LineKey("bc.done")
LEAVE_AT = 40
BIG = 10**6 * Q
PER_SECOND = per_hour(3600)
LA_CARDS = (A1, A2, AC, AD)

ORDER_AC = Order(AfterTime(20), TapCard(AC))
ORDER_AD = Order(AtLeast(StoreValue(Y), 3 * Q, 3 * Q), TapCard(AD))
ORDER_BC = Order(AfterTime(20), TapCard(BC))
TOWN_RULE = Order(AfterTime(0), SwitchMix(TM))
ORDERS = (TOWN_RULE, ORDER_AC, ORDER_AD, ORDER_BC)
"""The town's mix runs; la's two (one never on before the leave, one on from 50, so both stand removed at 40), and lb's, which stays."""

MIX_TOWN = Mix(TM, (CardShare(A1, 6000), CardShare(A2, 4000), CardShare(B1, 5000), CardShare(B2, 5000)))
MIX_SOLO_A = Mix(TM, (CardShare(A1, 6000), CardShare(A2, 4000)))
MIX_SOLO_B = Mix(TM2, (CardShare(B1, 5000), CardShare(B2, 5000)))
"""The solo world: la alone in the town mix, lb alone in a second one (a mix is made by a join; a player cannot make one)."""
MIX_HANDS = Mix(HM, (CardShare(H1, 5000), CardShare(HC, 5000)))
AFTER_MIXES = {
    TM: Mix(TM, (CardShare(B1, 5000), CardShare(B2, 5000))),
    HM: MIX_HANDS,
}
"""Every saved mix as it stands once la's shares have left (DESIGN.txt, LEAVES, CHOICES step 4)."""


def _card(c: CardId, lane: LaneId, work_s: int = 10, **kw: Any) -> CardDef:
    return CardDef(c, work_s, lane=lane, **kw)


def cards() -> tuple[CardDef, ...]:
    one = {"cap": 1}
    return (
        _card(A1, LA, makes=(Flow(X, PER_SECOND),)), _card(A2, LA, makes=(Flow(W, PER_SECOND),)),
        _card(AC, LA, 50, outcome=Outcome(stores=(Amount(Y, 5 * Q),)), lines=(AC_DONE,), **one),
        _card(AD, LA, 30, lines=(AD_DONE,), **one),
        _card(B1, LB, makes=(Flow(V, PER_SECOND),)), _card(B2, LB, makes=(Flow(U, PER_SECOND),)),
        _card(BC, LB, 50, lines=(BC_DONE,), **one), _card(D1, LD, makes=(Flow(S, PER_SECOND),)), _card(DC, LD, 50, **one),
        CardDef(H1, 10, makes=(Flow(HS, PER_SECOND),)), CardDef(HC, 30, cap=1),
    )


def joiners(solo: bool = False) -> tuple[TriggerDef, ...]:
    return tuple(TriggerDef(TriggerId(f"j{lane}"), AfterTime(0), Outcome(joins=(join(lane, c, m),)))
                 for lane, c, m in ((LA, A1, TM), (LB, B1, TM2 if solo else TM)))


def join(lane: LaneId, card: CardId, mix: MixId = TM) -> Join:
    return Join(lane, mix, card)


def leave(lane: LaneId = LA, stops: tuple[ActionId, ...] = (STOP,)) -> Any:
    from ashfall_app.engine import Leave
    return Leave(lane, stops)


def kills(*rows: int) -> pytest.MarkDecorator:
    """Marks the test as one that must go red for these rows of MUTANTS_leaves.txt."""
    return pytest.mark.kills(*rows)


def left(lane: LaneId = LA) -> Unlock:
    return Unlock(getattr(UnlockKind, "LEFT"), lane)


def ended(name: str) -> Any:
    """Ended.SEASON or Ended.LEFT (the enum's import path is a logged gap: it is taken from the engine package)."""
    from ashfall_app.engine import Ended
    return getattr(Ended, name)


def outcome(**fields: Any) -> Outcome:
    """An Outcome with fields named at call time (leaves, retire_orders), so a module collects before they exist."""
    return Outcome(**fields)


def logged_end(time: int, order: Order, level: int | None, name: str) -> RuleChange:
    """RuleChange(time, order, False, level, Ended.<name>): the order was removed by the game, not turned off."""
    args: tuple[Any, ...] = (time, order, False, level, ended(name))
    return RuleChange(*args)


def ended_changes(changes: tuple[RuleChange, ...]) -> list[RuleChange]:
    """The changes that carry an `ended`, in a fixed order (by the order's text)."""
    return sorted((rc for rc in changes if getattr(rc, "ended") is not None), key=lambda rc: str(rc.order))


def expected_ends(*changes: RuleChange) -> list[RuleChange]:
    return sorted(changes, key=lambda rc: str(rc.order))


def leave_trigger(at: int = LEAVE_AT, lane: LaneId = LA, stops: tuple[ActionId, ...] = (STOP,)) -> TriggerDef:
    return TriggerDef(TriggerId(f"leave-{lane}"), AfterTime(at), outcome(leaves=(leave(lane, stops),)))


def rules(leave_at: int | None = LEAVE_AT, extra: tuple[TriggerDef, ...] = (), solo: bool = False) -> Rules:
    """The world; with leave_at None no one leaves (the control every comparison runs beside)."""
    trig = joiners(solo) + (() if leave_at is None else (leave_trigger(leave_at),)) + extra
    r = Rules(stores=tuple(StoreDef(s, BIG) for s in (X, W, Y, V, U, Z, Z2, S, HS)), skills=(SkillDef(SkillId("k")),),
              standing=(StandingDef(STOP, makes=(Flow(Z, PER_SECOND),)), StandingDef(KEEP, makes=(Flow(Z2, PER_SECOND),))),
              curve=PacingCurve((10**15,)), lanes=tuple(LaneDef(lane, True) for lane in (LA, LB, LD)),
              cards=cards(), triggers=trig)
    validate_rules(r)
    return r


def scene(r: Rules, solo: bool = False) -> Save:
    """At 0: both joined, the mixes saved, the three orders set, the hands tapping hc (done at 30, greying hm)."""
    s = new_save(r)
    for m in ((MIX_SOLO_A, MIX_SOLO_B) if solo else (MIX_TOWN,)) + (MIX_HANDS,):
        s = decide(s, r, 0, SaveMix(m))
    s = decide(s, r, 0, SetOrders(ORDERS))
    return decide(s, r, 0, TapCard(HC))


def before_and_after(t: int = LEAVE_AT, solo: bool = False) -> tuple[Rules, Save, Save]:
    """The rules and the save at t - 1 and at t, so the leave lands exactly between them."""
    r = rules(t, solo=solo)
    s = advance(scene(r, solo), r, t - 1)
    return r, s, advance(s, r, t)
