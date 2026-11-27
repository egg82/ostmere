"""A small world for a working's chain (engine design/spells.txt, "SPELLS"): one standing fight on a group threat and
one hands card whose completions resolve chains on it. The fight runs `per_hour` whole fights an hour, so its fought
tally is exact at whole multiples of 3600 / per_hour seconds."""
from dataclasses import replace

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, Amount, CardDef, CardId, ChainDef, FightDef, Flow, LineKey, PacingCurve,
    Rules, SideDef, SideId, StandingDef, StoreDef, StoreId, ThreatDef, ThreatId, TriggerDef, per_hour, validate_rules,
)

HAND, PACK = SideId("hand"), ThreatId("pack")
RAID, JUMP = ActionId("raid"), CardId("jump")
FOUGHT, LOST, CHAINED, HAIR, ASH = (StoreId(n) for n in ("fought", "lost", "chained", "hair", "ash"))
LINKS = (LineKey("link_1"), LineKey("link_2"), LineKey("link_n"))
BIG = 10**6 * Q
WORK_S = 600


def jump(reach: int = 3, *, cap: int | None = None, lines: tuple[LineKey, ...] = LINKS, chain: bool = True) -> CardDef:
    """Takes two hair and makes ash, as any card; its chain reaches `reach` before any entry."""
    return CardDef(JUMP, WORK_S, inputs=(Amount(HAIR, 2 * Q),), makes=(Flow(ASH, per_hour(1)),), cap=cap,
                   lines=tuple(LineKey(f"own_{i}") for i in range(1, cap + 1)) if cap else (),
                   chain=ChainDef(RAID, reach, lines) if chain else None)


def raid(fights_per_hour: int) -> StandingDef:
    return StandingDef(RAID, fight=FightDef(HAND, PACK, LOST, FOUGHT, per_hour(fights_per_hour), chained=CHAINED))


def world(members: int = 4, reach: int = 3, fights_per_hour: int = 1, *, side: int = 1, cap: int | None = None,
          max_firings: int = 1000, lines: tuple[LineKey, ...] = LINKS, chain: bool = True,
          triggers: tuple[TriggerDef, ...] = ()) -> Rules:
    stores = tuple(StoreDef(s, BIG, BIG if s == HAIR else 0) for s in (FOUGHT, LOST, CHAINED, HAIR, ASH))
    r = Rules(stores, (), (raid(fights_per_hour),), PacingCurve((10**15,)), max_firings_per_instant=max_firings,
              cards=(jump(reach, cap=cap, lines=lines, chain=chain),), triggers=triggers,
              sides=(SideDef(HAND, side),), threats=(ThreatDef(PACK, 1, members),))
    validate_rules(r)
    return r


def without_chain(rules: Rules) -> Rules:
    """The same rules with the card's chain removed: what the chain must leave untouched."""
    return replace(rules, cards=tuple(replace(c, chain=None) for c in rules.cards))
