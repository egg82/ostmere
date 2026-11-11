"""Fixture rules for the day-one checks past the fights (fightchecks.py, cures.py), until a check wants more than the
shipped chapters give: a gatherer into a wood store, a fight card (the hunt) that makes finds and wounds, a standing
fight (the raid) that takes wood, a chip on the wound and the card that tends it. The hands' side and the threat are
level, so half of all fights are lost. `gathers` and `tends` turn off what puts wood up and what takes the wound, the
planted failures. Never a shipped chapter (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, Amount, AtLeast, BP, CardDef, CardId, CardShare, ChipDef, ChipId, FightDef, Flow, Mix, MixId,
    PacingCurve, Rules, Save, SaveMix, SideDef, SideId, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue,
    SwitchMix, ThreatDef, ThreatId, Unlock, UnlockKind, new_save, per_hour, decide,
)

WOOD, HURT, FOUND, LOST, RAIDS, RAID_LOST = (StoreId(n) for n in ("wood", "hurt", "found", "lost", "raids", "raid_lost"))
GATHER, HUNT, TEND, RAID, CHIP = CardId("gather"), CardId("hunt"), CardId("tend"), ActionId("raid"), ChipId("hurt")
HAND, WOLF = SideId("hand"), ThreatId("wolf")
HUNT_S = 3600


def rules(gathers: bool = True, tends: bool = True) -> Rules:
    sk = SkillId("k")
    cards = (CardDef(GATHER, 60, skill=sk, makes=(Flow(WOOD, per_hour(2)),) if gathers else ()),
             CardDef(HUNT, HUNT_S, makes=(Flow(FOUND, per_hour(1)),),
                     fight=FightDef(HAND, WOLF, LOST, wounds=(Amount(HURT, Q),))),
             *((CardDef(TEND, 60, inputs=(Amount(HURT, Q),)),) if tends else ()))
    raid = StandingDef(RAID, fight=FightDef(HAND, WOLF, RAID_LOST, fought=RAIDS, per_hour=per_hour(1),
                                            loses=(Amount(WOOD, Q),)))
    stores = (StoreDef(WOOD, 50 * Q, 3 * Q), StoreDef(HURT, 3 * Q), *(StoreDef(s, 10**6 * Q) for s in (FOUND, LOST, RAIDS, RAID_LOST)))
    return Rules(stores, (SkillDef(sk),), (raid,), PacingCurve((10**15,)), cards=cards, sides=(SideDef(HAND, 3),),
                 threats=(ThreatDef(WOLF, 3),), chips=(ChipDef(CHIP, AtLeast(StoreValue(HURT), Q, Q)),),
                 opening=(*(Unlock(UnlockKind.CARD, str(c.id)) for c in cards), Unlock(UnlockKind.ACTION, str(RAID)),
                          Unlock(UnlockKind.SKILL, str(sk)), Unlock(UnlockKind.CHIP, str(CHIP)),
                          Unlock(UnlockKind.STORE, str(WOOD)), Unlock(UnlockKind.STORE, str(FOUND))))


def mixed(r: Rules, card: CardId, share_bp: int = BP) -> Save:
    """A new save with `card` alone in the active mix."""
    mix = Mix(MixId("only"), (CardShare(card, share_bp),))
    return decide(decide(new_save(r), r, 0, SaveMix(mix)), r, 0, SwitchMix(mix.id))
