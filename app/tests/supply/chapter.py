"""A fixture outpost and its supply line (week-five-plan item 2), neutral ids, on existing shapes only: a gatherer into
a town store, a trip-shaped card (and its town twin) that takes the town store and fills the outpost's store, a
standing upkeep that draws the outpost's store and pauses dry, a trip and a staged build that take it as an input, a
standing fight whose losses take it, and two cards that hold the fight's side while they run. Each card shows at a time
a trigger sets. Never a shipped chapter (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import replace
from typing import TypedDict

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AtLeast, CardCount, CardDef, CardId, FightDef, Flow, LaneDef, LaneId, Outcome,
    PacingCurve, Rules, SideDef, SideId, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue, ThreatDef, ThreatId,
    TriggerDef, TriggerId, Unlock, UnlockKind, WhileRunning, per_hour,
)
from tests.dayone.player.sinks import Chapter, Trip

HOUR = 3600
BIG = 10**9 * Q
TOWN, POST, FOUND, KEPT = (StoreId(n) for n in ("town", "post", "found", "kept"))
LOST, FOUGHT = StoreId("post_lost"), StoreId("post_fought")
GATHER, HAUL, TWIN, TRIP, BUILD = (CardId(n) for n in ("gather", "haul", "n1_haul", "trip", "build"))
HOLD_A, HOLD_B = CardId("hold_a"), CardId("hold_b")
KEEP, RAID = ActionId("keep"), ActionId("raid")
HAND, WOLF, TOWN_LANE = SideId("hand"), ThreatId("wolf"), LaneId("town")
STAGES, STOCKED = 3, 6
CHAPTER = Chapter((Trip(HAUL, TOWN), Trip(TRIP, POST, BP // 10)))
"""What the whenever player does about the sinks: the filler and the trip mixed. The staged build's stages are queued in
one move (play.py), since the sinks queue a comfort for its next completion only."""


class Knobs(TypedDict, total=False):
    upkeep: bool
    fight: bool
    shown_at: int
    build_at: int


def rules(*, upkeep: bool = True, fight: bool = True, shown_at: int = HOUR // 2, build_at: int | None = None) -> Rules:
    """The town store holds 4 items and the gatherer makes 2 an hour. The filler takes 2 from it per completion
    (an hour's work) and lands 4 in the post's store; the upkeep draws half an hour of the post's store, the trip 2 per
    completion, a build stage 1 (STAGES of them), a lost raid 1 (the raid fights once an hour, about half lost); each hold card
    adds to the hands' side while it runs. `upkeep`, `fight`: leave those standing actions out. `shown_at`: when the
    cards show, `build_at` the build alone (`shown_at` when None)."""
    sk = SkillId("k0")
    per = Q
    cards = (
        CardDef(GATHER, 60, skill=sk, xp_per_hour=0, makes=(Flow(TOWN, per_hour(2)),)),
        CardDef(HAUL, HOUR, inputs=(Amount(TOWN, 2 * per),), outcome=Outcome(stores=(Amount(POST, 4 * per),))),
        CardDef(TWIN, HOUR, lane=TOWN_LANE, inputs=(Amount(TOWN, 2 * per),), outcome=Outcome(stores=(Amount(POST, 4 * per),))),
        CardDef(TRIP, HOUR, inputs=(Amount(POST, 2 * per),), makes=(Flow(FOUND, per_hour(1)),)),
        CardDef(BUILD, HOUR, inputs=(Amount(POST, per),), cap=STAGES),
        CardDef(HOLD_A, HOUR, inputs=(Amount(TOWN, per),), while_running=(WhileRunning(HAND, 5000),)),
        CardDef(HOLD_B, HOUR, inputs=(Amount(TOWN, per),), while_running=(WhileRunning(HAND, 5000),)),
    )
    standing = (
        *((StandingDef(KEEP, costs=(Flow(POST, per_hour(1) // 2),), makes=(Flow(KEPT, per_hour(1) // 2),)),) if upkeep else ()),
        *((StandingDef(RAID, fight=FightDef(HAND, WOLF, LOST, fought=FOUGHT, per_hour=1000, loses=(Amount(POST, per),))),)
          if fight else ()),
    )
    shown = (HAUL, TRIP, BUILD, HOLD_A, HOLD_B)
    shows = tuple(TriggerDef(TriggerId(f"show_{c}"), AfterTime(build_at if c == BUILD and build_at is not None else shown_at),
                             Outcome(unlocks=(Unlock(UnlockKind.CARD, str(c)),))) for c in shown)
    done = TriggerDef(TriggerId("built"), AtLeast(CardCount(BUILD), STAGES, STAGES), Outcome())
    stocked = TriggerDef(TriggerId("stocked"), AtLeast(StoreValue(POST), STOCKED * per, STOCKED * per), Outcome())
    return Rules(
        (StoreDef(TOWN, 4 * per, 0), StoreDef(POST, 12 * per, 0), StoreDef(FOUND, BIG), StoreDef(KEPT, BIG),
         *((StoreDef(LOST, BIG), StoreDef(FOUGHT, BIG)) if fight else ())),
        (SkillDef(sk),), standing, PacingCurve((10**15,)), 1000,
        cards=cards, triggers=(*shows, done, stocked),
        opening=(Unlock(UnlockKind.STORE, str(TOWN)), Unlock(UnlockKind.STORE, str(POST)), Unlock(UnlockKind.STORE, str(FOUND)),
                 Unlock(UnlockKind.CARD, str(GATHER)), Unlock(UnlockKind.SKILL, "k0"),
                 *(Unlock(UnlockKind.ACTION, str(a.id)) for a in standing)),
        sides=(SideDef(HAND, 100),) if fight else (), threats=(ThreatDef(WOLF, 100),) if fight else (),
        lanes=(LaneDef(TOWN_LANE),))


def without(r: Rules, *cards: CardId) -> Rules:
    return replace(r, cards=tuple(c for c in r.cards if c.id not in cards))
