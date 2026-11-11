"""A small world with one fight card and one standing fight, built from the engine's public types only (DESIGN.txt,
"FIGHTS"). Amounts are whole multiples of Q so every hand-written twin line below is exact."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, CardDef, CardId, CardShare, FightDef, Flow, FlowKind, Mix, MixId, Modifier,
    ModifierKind, Outcome, PacingCurve, RateRef, Rules, Save, SideDef, SideId, SkillDef, SkillId, SourceId,
    StandingDef, ActionId, StoreDef, StoreId, SwitchMix, SaveMix, ThreatDef, ThreatId, TriggerDef, ceil_div, decide,
    new_save, per_hour,
)

HAND, WOLF = SideId("hand"), ThreatId("wolf")
HUNT, RAID = CardId("hunt"), ActionId("raid")
LOOT, PELT, STASH, HURT, BAIT, LOST, FOUGHT, GRAIN, RLOST, RHURT, RSTASH, COST = (
    StoreId(n) for n in ("loot", "pelt", "stash", "hurt", "bait", "lost", "fought", "grain", "rlost", "rhurt", "rstash", "cost"))
BIG = 10**6 * Q
MIX = MixId("m")
RAID_PER_HOUR = per_hour(2)
K = SkillId("k")


def stores() -> tuple[StoreDef, ...]:
    return tuple(StoreDef(s, BIG, BIG if s in (STASH, RSTASH, BAIT, COST) else 0)
                 for s in (LOOT, PELT, STASH, HURT, BAIT, LOST, FOUGHT, GRAIN, RLOST, RHURT, RSTASH, COST))


def hunt(work_s: int = 100, fight: bool = True) -> CardDef:
    """Wins pay loot (a lump) and pelt (a flow); a lost fight takes stash, wounds hurt and counts in lost. Bait is an
    input and is not touched by the odds."""
    return CardDef(HUNT, work_s, skill=K, makes=(Flow(PELT, per_hour(4)),), inputs=(Amount(BAIT, Q),),
                   outcome=Outcome(stores=(Amount(LOOT, 6 * Q),)),
                   fight=FightDef(HAND, WOLF, LOST, loses=(Amount(STASH, 3 * Q),), wounds=(Amount(HURT, 2 * Q),))
                   if fight else None)


def raid(fight: bool = True) -> StandingDef:
    return StandingDef(RAID, makes=(Flow(GRAIN, per_hour(3)),), costs=(Flow(COST, per_hour(1)),),
                       fight=FightDef(HAND, WOLF, RLOST, FOUGHT, RAID_PER_HOUR, (Amount(RSTASH, 3 * Q),),
                                      (Amount(RHURT, 2 * Q),)) if fight else None)


def world(p: int, t: int, *, fight: bool = True, work_s: int = 100, triggers: tuple[TriggerDef, ...] = ()) -> Rules:
    return Rules(stores(), (SkillDef(K),), (raid(fight),), PacingCurve((10**15,)), cards=(hunt(work_s, fight),),
                 triggers=triggers, sides=(SideDef(HAND, p),), threats=(ThreatDef(WOLF, t),))


def loss_bp(p: int, t: int) -> int:
    """The documented odds: ceil(BP * T / (T + P))."""
    return ceil_div(BP * t, t + p)


def hand(runner: CardId | ActionId, kind: FlowKind, store: StoreId, bp: int) -> Modifier:
    return Modifier(RateRef(runner, kind, store), ModifierKind.MUL_BP, bp, SourceId("by-hand"))


def hand_odds(p: int, t: int) -> tuple[Modifier, ...]:
    """The odds entries written by hand onto the fight-free twin, per DESIGN.txt: win on makes, loss on the rest."""
    lose, win = loss_bp(p, t), BP - loss_bp(p, t)
    M, C = FlowKind.MAKE, FlowKind.COST
    return (hand(HUNT, M, PELT, win), hand(HUNT, M, LOOT, win), hand(HUNT, C, STASH, lose),
            hand(HUNT, M, HURT, lose), hand(HUNT, M, LOST, lose),
            hand(RAID, M, GRAIN, win), hand(RAID, C, RSTASH, lose), hand(RAID, M, RHURT, lose), hand(RAID, M, RLOST, lose))


def twin(rules: Rules) -> Rules:
    """The same rules with the fight written out as the lines it stands for (no FightDef): wounds and the tally as
    outcome stores, loses as an input, on the standing action as flows."""
    h = rules.cards[0]
    assert h.fight is not None
    card = replace(h, fight=None, inputs=h.inputs + h.fight.loses,
                   outcome=Outcome(stores=h.outcome.stores + h.fight.wounds + (Amount(h.fight.lost, Q),)))
    a = rules.standing[0]
    assert a.fight is not None
    f = a.fight
    def flow(am: Amount) -> Flow:
        return Flow(am.store, am.quantity * f.per_hour // Q)

    action = replace(a, fight=None, costs=a.costs + tuple(map(flow, f.loses)),
                     makes=a.makes + tuple(map(flow, f.wounds)) + (Flow(f.lost, f.per_hour), Flow(f.fought or FOUGHT, f.per_hour)))
    return replace(rules, cards=(card,), standing=(action,))


def in_mix(s: Save, r: Rules, share_bp: int = BP) -> Save:
    s = decide(s, r, s.time, SaveMix(Mix(MIX, (CardShare(HUNT, share_bp),))))
    return decide(s, r, s.time, SwitchMix(MIX))


def started(r: Rules, *mods: Modifier, share_bp: int = BP) -> Save:
    return in_mix(new_save(r, tuple(mods)), r, share_bp)
