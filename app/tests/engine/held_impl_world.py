"""Rules for the held-entries tests (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS"), from the engine's public
types only. Hands cards: guard (raises HAND by 5000), wet (guard that also costs an empty store), need (requires x),
cap (one-off that greys a mix), warm (makes f, held at its level), hunt (a fight card). Town: watch on lane la raises HAND
by 4000 then DEF by 1000; b1 is the other person's card."""
from dataclasses import replace

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, Amount, AtLeast, CardDef, CardId, CardShare, FightDef, Flow, Join,
    LaneDef, LaneId, Mix, MixId, Outcome, PacingCurve, Rules, Save, SaveMix, SideDef, SideId, SkillDef, SkillId,
    StoreDef, StoreId, StoreValue, SwitchMix, ThreatDef, ThreatId, TriggerDef, TriggerId, WhileRunning, decide, new_save,
    per_hour,
)

HAND, DEF, WOLF = SideId("hand"), SideId("def"), ThreatId("wolf")
GUARD, WET, NEED, CAP, WARM, HUNT, WATCH, B1 = (CardId(n) for n in ("guard", "wet", "need", "cap", "warm", "hunt", "watch", "b1"))
X, DRY, F, LOST, STASH = (StoreId(n) for n in ("x", "dry", "f", "lost", "stash"))
LA, LB = LaneId("la"), LaneId("lb")
TM, M = MixId("town:main"), MixId("m")
BIG = 10**6 * Q
HOLD_AT = 10 * Q


def cards() -> tuple[CardDef, ...]:
    raise_hand = (WhileRunning(HAND, 5000),)
    return (
        CardDef(GUARD, 10, while_running=raise_hand),
        CardDef(WET, 10, costs=(Flow(DRY, per_hour(1)),), while_running=raise_hand),
        CardDef(NEED, 10, requires=(AtLeast(StoreValue(X), Q, Q),), while_running=raise_hand),
        CardDef(CAP, 20, cap=1),
        CardDef(WARM, 10, makes=(Flow(F, per_hour(1)),), while_running=raise_hand),
        CardDef(HUNT, 100, fight=FightDef(HAND, WOLF, LOST, loses=(Amount(STASH, Q),))),
        CardDef(WATCH, 10, lane=LA, while_running=(WhileRunning(HAND, 4000), WhileRunning(DEF, 1000))),
        CardDef(B1, 10, lane=LB),
    )


def world(*triggers: TriggerDef, held: bool = True) -> Rules:
    stores = tuple(StoreDef(s, BIG, {STASH: BIG, F: HOLD_AT}.get(s, 0)) for s in (X, DRY, F, LOST, STASH))
    deck = cards() if held else tuple(replace(c, while_running=()) for c in cards())
    return Rules(stores, (SkillDef(SkillId("k")),), (), PacingCurve((10**15,)), lanes=(LaneDef(LA, True), LaneDef(LB, True)),
                 cards=deck, triggers=triggers, sides=(SideDef(HAND, 1000), SideDef(DEF, 500)),
                 threats=(ThreatDef(WOLF, 3000),))


def joined(lane: LaneId, card: CardId, at: int = 0) -> TriggerDef:
    return TriggerDef(TriggerId(f"j-{lane}"), AfterTime(at), Outcome(joins=(Join(lane, TM, card),)))


def mixed(r: Rules, *shares: tuple[CardId, int], mix: MixId = M, run: bool = True) -> Save:
    """A new save with `shares` saved as `mix` and, when `run`, the hands' mix switched to it."""
    s = decide(new_save(r), r, 0, SaveMix(Mix(mix, tuple(CardShare(c, bp) for c, bp in shares))))
    return decide(s, r, 0, SwitchMix(mix)) if run and mix == M else s
