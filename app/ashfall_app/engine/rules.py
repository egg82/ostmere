"""The rules a save runs under: immutable data passed in, never loaded by the engine.

All quantities are in quantity units, all rates in rate units per hour (units.py). Tuples keep declaration order;
that order is the `sequence` tiebreak for same-instant events (events.py) and the order of a save's tuples.
"""
from dataclasses import dataclass

from .cards import CardDef, FightDef, Held
from .errors import InvalidRulesError
from .flows import Flow
from .ids import ActionId, FeatureId, SkillId, StoreId
from .lanes import LaneDef
from .nodechecks import check_nodes
from .nodes import NodeDef, PrestigeDef
from .offers import OfferDef
from .rules_check import check_parts
from .strengthdefs import SideDef, ThreatDef
from .status import ChipDef, TriggerDef
from .unlocks import Unlock


@dataclass(frozen=True)
class StoreDef:
    """A store: everything has a cap (cap > 0). A store's floor is always 0. 0 <= initial <= cap."""

    id: StoreId
    cap: int
    initial: int = 0


@dataclass(frozen=True)
class SkillDef:
    id: SkillId


@dataclass(frozen=True)
class StandingDef:
    """A standing action: runs at a full share whenever unlocked, outside the mix and every lane (a fire burning, a
    body getting hungry). Never a card, never tapped or mixed: it is not work the player does. Rules with opening None
    start every standing action at time 0 (DESIGN.txt, "Standing", "Instant 0").

    makes and costs per hour, and the skill it trains (skill None: xp_per_hour 0). It may not both make and cost the
    same store, nor list one store twice in makes or in costs; a card holds the same rule over its makes, costs,
    inputs and outcome stores (DESIGN.txt, "Validation of cards").
    """

    id: ActionId
    makes: tuple[Flow, ...] = ()
    costs: tuple[Flow, ...] = ()
    skill: SkillId | None = None
    xp_per_hour: int = 0
    fight: FightDef | None = None
    while_running: tuple[Held, ...] = ()
    """Sides and lane speeds it raises while it runs and is not paused (DESIGN.txt, "HELD SPEED"; the codec leaves
    the field out while empty)."""


@dataclass(frozen=True)
class PacingCurve:
    """XP to level, shared by every skill. thresholds[i] is the total XP (quantity units) to reach level i + 2.

    Level 1 is XP 0; the last threshold is the cap on XP (finite, like everything), so the max level is
    len(thresholds) + 1. Thresholds are strictly increasing and > 0. The curve is data here; choosing which curve
    (an A/B target) is the Pacing curve system's job outside the engine.
    """

    thresholds: tuple[int, ...]


@dataclass(frozen=True)
class Rules:
    """Everything the engine needs to know that is not the player's own state."""

    stores: tuple[StoreDef, ...]
    skills: tuple[SkillDef, ...]
    standing: tuple[StandingDef, ...]
    curve: PacingCurve
    max_firings_per_instant: int = 1000
    """Cap on firings (events processed plus verbs applied by orders and the queue) at one instant; >= 1.
    Reaching it suspends order and queue evaluation for that instant (api.py); it never raises."""
    lanes: tuple[LaneDef, ...] = ()
    """Lanes besides HANDS, which always exists and is never declared (declaring it is invalid)."""
    cards: tuple[CardDef, ...] = ()
    """Every card, in the order a mix's dry pauses and same-instant events read them (DESIGN.txt, "Same instant")."""
    chips: tuple[ChipDef, ...] = ()
    triggers: tuple[TriggerDef, ...] = ()
    opening: tuple[Unlock, ...] | None = None
    """The unlock set a new save starts with; every id not in it is locked until an Outcome unlocks it. None means
    nothing is gated: every id counts as unlocked (rules with no opening, such as engine tests and the simulator's
    bare economies). DESIGN.txt, "Unlocks"."""
    end: FeatureId | None = None
    """The content's end feature: the end is the first instant it is unlocked, recorded as Save.ended_at. None: these
    rules have no end. DESIGN.txt, "The end"."""
    offers: tuple[OfferDef, ...] = ()
    """Every offer, in the order the view lists them (DESIGN.txt, "Offers")."""
    sides: tuple[SideDef, ...] = ()
    """Every side a fight can name, in rules order (DESIGN.txt, "FIGHTS")."""
    threats: tuple[ThreatDef, ...] = ()
    """Every threat of a roster, in rules order."""
    prestige: PrestigeDef | None = None
    """The numbers every skill's phases read (DESIGN.txt, "PRESTIGE PHASES"); None: these rules have no prestige."""
    nodes: tuple[NodeDef, ...] = ()
    """Every skill's prestige track, in rules order; a skill's track is its nodes in this order."""


def validate_rules(rules: Rules) -> None:
    """Raise InvalidRulesError if the rules break any constraint documented on the types above, or reference an
    unknown store or skill, including the card rules (DESIGN.txt, "Validation of cards"). Every other engine function
    assumes rules that pass this; on rules that do not, their behaviour is unspecified. Standing action ids and card ids
    share one namespace (Runner): one id names one rate owner."""
    runners = [a.id for a in rules.standing] + [c.id for c in rules.cards]
    for kind, ids in (("store", [s.id for s in rules.stores]), ("skill", [s.id for s in rules.skills]),
                      ("runner", runners)):
        _require(len(set(ids)) == len(ids), f"duplicate {kind} id")
    for s in rules.stores:
        _require(s.cap > 0 and 0 <= s.initial <= s.cap, f"store {s.id}: need cap > 0 and 0 <= initial <= cap")
    stores = {s.id for s in rules.stores}
    skills = {s.id for s in rules.skills}
    for a in rules.standing:
        _check_standing(a, stores, skills)
    th = rules.curve.thresholds
    _require(len(th) > 0 and th[0] > 0, "pacing curve needs thresholds, the first > 0")
    _require(all(x < y for x, y in zip(th, th[1:])), "pacing curve thresholds must strictly increase")
    _require(rules.max_firings_per_instant >= 1, "max_firings_per_instant must be >= 1")
    check_parts(rules)
    check_nodes(rules)


def _check_standing(a: StandingDef, stores: set[StoreId], skills: set[SkillId]) -> None:
    _require(a.skill in skills if a.skill is not None else a.xp_per_hour == 0, f"action {a.id}: unknown skill")
    _require(a.xp_per_hour >= 0, f"action {a.id}: negative xp")
    makes = [f.store for f in a.makes]
    costs = [f.store for f in a.costs]
    _require(all(f.per_hour >= 0 for f in a.makes + a.costs), f"action {a.id}: negative flow")
    _require(all(s in stores for s in makes + costs), f"action {a.id}: unknown store")
    _require(len(set(makes)) == len(makes) and len(set(costs)) == len(costs), f"action {a.id}: store listed twice")
    _require(not set(makes) & set(costs), f"action {a.id}: makes and costs the same store")


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidRulesError(message)
