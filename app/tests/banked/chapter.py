"""A fixture chapter for the sink policies (tests/dayone/sinks.py) and the 2 AM test, until a real chapter with sinks
exists: a gatherer into a wood store, a trip that takes wood and brings finds, a comfort that takes most of the store
once, and an arrival offer. Each sink shows at a time the caller sets (a trigger on the clock), so a test can show it
while the player is there or only in the night. Never a shipped chapter (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import replace
from typing import TypedDict

from ashfall_app.engine import (
    ActionId, AfterTime, AnswerDef, AnswerId, Amount, CardDef, CardId, FightDef, Flow, LaneDef, LaneId, OfferDef,
    OfferId, Outcome, PacingCurve, Rules, SideDef, SideId, SkillDef, SkillId, StandingDef, StoreDef, StoreId,
    ThreatDef, ThreatId, TriggerDef, TriggerId, Unlock, UnlockKind,
)
from tests.dayone.sinks import Chapter, Trip

RATE, HOUR = 3600, 3600
CAP = 4 * RATE * HOUR
WOOD, FOUND = StoreId("wood"), StoreId("found")
GATHER, TRIP, COMFORT = CardId("gather"), CardId("trip"), CardId("comfort")
CLEAR, RAID, SIDE = CardId("clear"), ActionId("raid"), LaneId("side")
HAND, WOLF = SideId("hand"), ThreatId("wolf")
LOST, RAID_LOST, CLEAR_LOST, RAIDS = (StoreId(n) for n in ("lost", "raid_lost", "clear_lost", "raids"))
NEWCOMER, STAY, MOVE_ON = OfferId("newcomer"), AnswerId("stay"), AnswerId("move_on")
CHAPTER = Chapter((Trip(TRIP, WOOD),), (COMFORT,), ((NEWCOMER, STAY),))
FIGHTING = Chapter((Trip(TRIP, WOOD, reserve_for=(CLEAR,)),), (COMFORT, CLEAR), CHAPTER.arrivals)
"""The chapter when `rules(fights=True)`: the fight card CLEAR is a sink beside the comfort. Its twelve hours draw wood
while the trip drinks it, and the dry store pauses another lane first, so the player keeps a reserve of wood for it."""


class Times(TypedDict, total=False):
    """The seconds and cost `rules` takes by keyword, so a caller passing them on cannot pass `fights` by accident."""
    trip_at: int
    comfort_at: int
    offer_at: int
    trip_cost: int
    clear_at: int


def rules(trip_at: int = HOUR // 2, comfort_at: int = HOUR // 2, offer_at: int = 4 * HOUR, trip_cost: int = 8,
          fights: bool = False, clear_at: int = HOUR // 2) -> Rules:
    """Each sink is shown by a trigger at the given second of game time. The gatherer makes 2 RATE at full speed into a
    wood store of 4 RATE-hours; the trip takes `trip_cost` (8) RATE-hours of wood per completion, more than the store holds, so in the mix it runs the store dry and waits for it to fill;
    a tappable trip costs 1; the comfort takes 3. `fights`: the trip is a fight on a side level with its threat, a standing
    raid takes wood, and a fight card (CLEAR, shown at `clear_at`, a lane of its own, 12 hours, takes 1 wood) joins the
    comfort among the sinks."""
    sk = SkillId("k0")
    cards = (CardDef(GATHER, 60, skill=sk, xp_per_hour=0, makes=(Flow(WOOD, 2 * RATE),)),
             CardDef(TRIP, HOUR, inputs=(Amount(WOOD, trip_cost * RATE * HOUR),), makes=(Flow(FOUND, RATE),)),
             CardDef(COMFORT, HOUR, inputs=(Amount(WOOD, 3 * RATE * HOUR),), cap=1))
    cards, standing, sides = _fights(cards) if fights else (cards, (), ())
    shown = ((cards[1], trip_at), (cards[2], comfort_at), *((c, clear_at) for c in cards[3:]))
    shows = [(TriggerId(f"show_{c.id}"), t, Outcome(unlocks=(Unlock(UnlockKind.CARD, str(c.id)),))) for c, t in shown]
    shows.append((TriggerId("show_newcomer"), offer_at, Outcome(unlocks=(Unlock(UnlockKind.OFFER, str(NEWCOMER)),))))
    return Rules(
        (StoreDef(WOOD, CAP, 0), StoreDef(FOUND, 10**9 * RATE * HOUR),
         *(StoreDef(s, 10**9 * RATE * HOUR) for s in ((LOST, RAID_LOST, CLEAR_LOST, RAIDS) if fights else ()))),
        (SkillDef(sk),), standing, PacingCurve((10**15,)), 1000,
        cards=cards, triggers=tuple(TriggerDef(i, AfterTime(t), o) for i, t, o in shows),
        opening=(Unlock(UnlockKind.STORE, str(WOOD)), Unlock(UnlockKind.STORE, str(FOUND)),
                 Unlock(UnlockKind.CARD, str(GATHER)), Unlock(UnlockKind.SKILL, "k0"),
                 *(Unlock(UnlockKind.ACTION, str(a.id)) for a in standing)),
        offers=(OfferDef(NEWCOMER, (AnswerDef(STAY), AnswerDef(MOVE_ON))),), sides=sides,
        threats=(ThreatDef(WOLF, 3),) if fights else (), lanes=(LaneDef(SIDE),) if fights else ())


def _fights(cards: tuple[CardDef, ...]) -> tuple[tuple[CardDef, ...], tuple[StandingDef, ...], tuple[SideDef, ...]]:
    """The trip made a fight, the fight card CLEAR added after the comfort, the raid and the hands' side."""
    trip = replace(cards[1], fight=FightDef(HAND, WOLF, LOST))
    clear = CardDef(CLEAR, 12 * HOUR, lane=SIDE, inputs=(Amount(WOOD, RATE * HOUR),), fight=FightDef(HAND, WOLF, CLEAR_LOST))
    raid = StandingDef(RAID, fight=FightDef(HAND, WOLF, RAID_LOST, fought=RAIDS, per_hour=1000,
                                            loses=(Amount(WOOD, RATE * HOUR // 10),)))
    return (cards[0], trip, cards[2], clear), (raid,), (SideDef(HAND, 3),)
