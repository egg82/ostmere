"""Fixture rules and readers for the held-speed contract tests (engine DESIGN.txt, "HELD SPEED, AND ENTRIES HELD BY
STANDING ACTIONS", invariants 156-161 and the amended 114). Built from the engine's public names only; the new ones
(HeldSpeed, StandingDef.while_running) are looked up when a fixture is built, never when a test module imports.

On top of town_mix_world's three ruled lanes (la, lb, lc) two project lanes lp and lq and a side g (base BP):
  wp (lp, 20000 s a completion, never completes in a test): costs inp, makes out, earns xp in k, each at one a second;
  wq (lq, the same): makes out2 at one a second;
  gs (hands, 100 s): a card holding a HeldSpeed on lp, so a fractional share reaches a speed entry.
Standing actions: eat1 (HeldSpeed on lp, 5000) and eat2 (HeldSpeed on lq, 3000) each eat 2 stew an hour, and mk makes stew
at `maker` an hour. Eaters sit in rules order eat1, eat2, so a dry store pauses eat2 first (Standing, the dry rule).
With the default stew (BIG) nothing runs dry."""
from dataclasses import replace
from typing import Any

import ashfall_app.engine as eng
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, CardDef, CardId, Flow, FlowKind, LaneDef, LaneId, LaneSpeed, Modifier,
    ModifierKind, RateRef, Rules, Save, SideDef, SideId, SourceId, StandingDef, StoreDef, StoreId, TapCard, new_save,
    per_hour, value, value_at, view,
)
from held_world import first, paused
from town_mix_world import LA, PER_SECOND, TM, joiner, world as town_world

LP, LQ = LaneId("lp"), LaneId("lq")
G, WOLF = SideId("g"), eng.ThreatId("wolf")
OUT, OUT2, INP, STEW = (StoreId(n) for n in ("out", "out2", "inp", "stew"))
WP, WQ, GS = CardId("wp"), CardId("wq"), CardId("gs")
EAT1, EAT2, MK, EATW = (ActionId(n) for n in ("eat1", "eat2", "mk", "eatw"))
BIG = 10**6 * Q
HELD = "held:"
EAT_AMOUNT = {EAT1: 5000, EAT2: 3000}
"""The speed each eater holds, on lp and lq."""
HOUR = 3600


def held_speed(lane: LaneId, amount_bp: int) -> Any:
    return getattr(eng, "HeldSpeed")(lane, amount_bp)  # a name this feature adds: looked up here, not at import


def side_entry(side: SideId, amount_bp: int) -> Any:
    return getattr(eng, "WhileRunning")(side, amount_bp)


def while_running(*entries: Any) -> dict[str, Any]:
    """The keyword for a runner's held entries, built at call time (StandingDef takes it only once the feature exists)."""
    return {"while_running": tuple(entries)}


def eater(action: ActionId, *entries: Any, cost: int = 2) -> StandingDef:
    """A standing action eating `cost` stew an hour, holding `entries` while it runs (none: no field at all)."""
    kw = while_running(*entries) if entries else {}
    return StandingDef(action, costs=(Flow(STEW, per_hour(cost)),), **kw)


def maker(rate: int) -> StandingDef:
    return StandingDef(MK, makes=(Flow(STEW, per_hour(rate)),))


def eaters(maker_rate: int = 3, held: bool = True) -> tuple[StandingDef, ...]:
    """eat1 and eat2 as above; held False declares no entry at all (a rules with none of the feature's names)."""
    e1 = (held_speed(LP, EAT_AMOUNT[EAT1]),) if held else ()
    e2 = (held_speed(LQ, EAT_AMOUNT[EAT2]),) if held else ()
    return eater(EAT1, *e1), eater(EAT2, *e2), maker(maker_rate)


def cards(with_gs: bool = True) -> tuple[CardDef, ...]:
    gs = (CardDef(GS, 100, **while_running(held_speed(LP, 4000))),) if with_gs else ()
    return (
        CardDef(WP, 20000, lane=LP, skill=eng.SkillId("k"), xp_per_hour=PER_SECOND, makes=(Flow(OUT, PER_SECOND),),
                costs=(Flow(INP, PER_SECOND),)),
        CardDef(WQ, 20000, lane=LQ, makes=(Flow(OUT2, PER_SECOND),)),
        *gs,
    )


def world(triggers: tuple[eng.TriggerDef, ...] = (), *, standing: tuple[StandingDef, ...] | None = None,
          opening: tuple[eng.Unlock, ...] | None = None, stew: int = BIG, with_gs: bool = True) -> Rules:
    """`standing` defaults to eaters(); stew is the store's start. with_gs False leaves gs out (the digest world has none
    of the feature's names)."""
    r = town_world(triggers, cards(with_gs), opening)
    stores = tuple(StoreDef(s, BIG, stew if s == STEW else BIG if s == INP else 0) for s in (OUT, OUT2, INP, STEW))
    return replace(r, stores=r.stores + stores, lanes=r.lanes + (LaneDef(LP), LaneDef(LQ)),
                   standing=eaters() if standing is None else standing, sides=(SideDef(G, BP),), threats=(eng.ThreatDef(WOLF, BP),))


def plain(r: Rules) -> Rules:
    """The same rules with no runner holding anything: the twin that takes the entries by hand."""
    return replace(r, cards=tuple(replace(c, **while_running()) for c in r.cards),
                   standing=tuple(replace(a, **while_running()) for a in r.standing))


def by_hand(lane: LaneId, amount_bp: int, source: str = "by-hand") -> Modifier:
    return Modifier(LaneSpeed(lane), ModifierKind.ADD_BP, amount_bp, SourceId(source))


def at(e: "eng.Explanation", m: Modifier) -> Modifier:
    """`m` as an Explanation lists it: aimed at the explained line itself (DESIGN.txt, "HELD SPEED", "The entries")."""
    return replace(m, target=e.ref)


def speed_mod(runner: str, lane: LaneId, amount_bp: int) -> Modifier:
    """What a holder puts on the stack for a HeldSpeed on `lane`, whose share gives `amount_bp`."""
    return Modifier(LaneSpeed(lane), ModifierKind.ADD_BP, amount_bp, SourceId(HELD + runner))


def tapped(r: Rules, *cards_: CardId, mods: tuple[Modifier, ...] = (), at: int = 0) -> Save:
    """A new save (with these starting entries) that taps each card at `at`."""
    s = new_save(r, mods)
    for c in cards_:
        s = eng.decide(eng.advance(s, r, at), r, at, TapCard(c))
    return s


def stack(s: Save, r: Rules) -> tuple[Modifier, ...]:
    from ashfall_app.engine.gates import effective_stack
    return effective_stack(s, r)


def held_mods(s: Save, r: Rules) -> tuple[Modifier, ...]:
    return tuple(m for m in stack(s, r) if m.source.startswith(HELD))


def held_of(s: Save, r: Rules, runner: str) -> list[Modifier]:
    return [m for m in held_mods(s, r) if m.source == HELD + runner]


def lane_adds(s: Save, r: Rules, lane: LaneId) -> list[Modifier]:
    """The ADD_BP entries on a lane's speed in the stack."""
    return [m for m in stack(s, r) if m.target == LaneSpeed(lane) and m.kind is ModifierKind.ADD_BP]


def rate(s: Save, r: Rules, runner: CardId, kind: FlowKind, store: StoreId | None = None) -> eng.Explanation:
    return eng.explain(s, r, RateRef(runner, kind, store))


def readings(s: Save, r: Rules, t: int) -> tuple[object, ...]:
    """Every line the worker wp has at t (its make, cost and xp stores, its work bar and the rate of each line and of its
    work) plus wq's make: what a lane speed must reach on each and nowhere else."""
    a = eng.advance(s, r, t)
    v = view(a, r)
    xp = next(b.xp for b in v.skills if b.skill == "k")
    cv = next(c for c in v.cards if c.card == WP)
    return (tuple(value(a, r, st, t) for st in (OUT, OUT2, INP)), value_at(xp, t), value_at(cv.bar, t), cv.completes_at,
            tuple(rate(a, r, WP, k, st).per_hour for k, st in ((FlowKind.MAKE, OUT), (FlowKind.COST, INP), (FlowKind.XP, None))),
            eng.explain_work(a, r, WP).per_hour, rate(a, r, WQ, FlowKind.MAKE, OUT2).per_hour)


def eaters_paused(s: Save) -> set[str]:
    return {p.runner for p in s.pauses}


def dry_instant(r: Rules, s: Save) -> Save:
    """The save at the first instant a dry pause lands."""
    return first(s, r, lambda x: bool(x.pauses))


def resumed(r: Rules, s: Save, action: ActionId) -> Save:
    """From a save where `action` is paused: the save at the instant its Pause resumes."""
    assert paused(s, action)
    return first(s, r, lambda x: not paused(x, action))


def stew_world(maker_rate: int) -> tuple[Rules, Save]:
    """Stew at one item, eaters as above and mk at `maker_rate`; wp and wq tapped at 0. The store dries at an instant
    where the dry rule pauses eaters last first."""
    r = world(standing=eaters(maker_rate), stew=Q)
    return r, tapped(r, WP, WQ)


def ja(at: int = 0) -> eng.TriggerDef:
    """la's person joins the town mix at `at`."""
    return joiner("ja", LA, TM, CardId("a1"), at)


def opening_without(r: Rules, *locked: str) -> tuple[eng.Unlock, ...]:
    """Every card and standing action unlocked at the start but the ones named."""
    return (tuple(eng.Unlock(eng.UnlockKind.CARD, c.id) for c in r.cards if c.id not in locked)
            + tuple(eng.Unlock(eng.UnlockKind.ACTION, a.id) for a in r.standing if a.id not in locked))


def unlock_at(action: ActionId, at: int) -> eng.TriggerDef:
    return eng.TriggerDef(eng.TriggerId(f"unlock-{action}"), eng.AfterTime(at),
                          eng.Outcome(unlocks=(eng.Unlock(eng.UnlockKind.ACTION, action),)))


def hands_mix(*shares: tuple[CardId, int]) -> tuple[eng.Verb, ...]:
    """Save a hands' mix of these shares and switch to it."""
    mix_id = eng.MixId("hm")
    return eng.SaveMix(eng.Mix(mix_id, tuple(eng.CardShare(c, b) for c, b in shares))), eng.SwitchMix(mix_id)


def after(s: Save, r: Rules, *verbs: eng.Verb) -> Save:
    for v in verbs:
        s = eng.decide(s, r, s.time, v)
    return s

