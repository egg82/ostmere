"""Lookups over Rules by id and position, built once per rules object. Callers must not mutate the dicts.

Rules is an immutable value, so derived data is kept on the object and found by identity: a cache keyed by value would
hash the whole tree on every call. Callers never subclass or wrap Rules.
"""
from collections.abc import Callable
from dataclasses import dataclass

from .cards import CardDef, Outcome
from .ids import HANDS, ActionId, AnswerId, CardId, ChipId, LaneId, MixId, OfferId, Runner, SkillId, StoreId
from .offers import AnswerDef, OfferDef
from .rules import Rules, StandingDef, StoreDef
from .status import ChipDef


@dataclass(frozen=True)
class RulesIndex:
    stores: dict[StoreId, StoreDef]
    store_pos: dict[StoreId, int]
    skill_pos: dict[SkillId, int]
    standing: dict[ActionId, StandingDef]
    cards: dict[CardId, CardDef]
    card_pos: dict[CardId, int]
    runner_pos: dict[Runner, int]
    """rules.standing then rules.cards: the order of pauses and RESUME's sequence."""
    chips: dict[ChipId, ChipDef]
    lanes: tuple[LaneId, ...]
    """HANDS first, then rules.lanes order."""
    lane_pos: dict[LaneId, int]
    runner_lane: dict[Runner, LaneId | None]
    """Where a runner's lines run: a card's lane, None for a standing action."""
    ruled: frozenset[LaneId]
    """The lanes the player's rules run (LaneDef.ruled)."""
    offers: dict[OfferId, OfferDef]
    answers: dict[AnswerId, tuple[OfferId, AnswerDef]]
    """Each answer with the offer it answers."""
    town_mixes: frozenset[MixId]
    """The mixes a join of the rules makes: the game's town mixes, each one TOWN even while it holds no card."""


def derived[T](rules: Rules, name: str, build: Callable[[Rules], T]) -> T:
    """build(rules), computed once per rules object and kept on it under `name`."""
    kept = vars(rules)
    if name not in kept:
        kept[name] = build(rules)
    found: T = kept[name]
    return found


def index(rules: Rules) -> RulesIndex:
    return derived(rules, "_index", _build)


def _joining(rules: Rules) -> list[Outcome]:
    """The outcomes that may join a person: a trigger's and an answer's."""
    return [*(t.outcome for t in rules.triggers), *(a.outcome for o in rules.offers for a in o.answers)]


def _build(rules: Rules) -> RulesIndex:
    lanes = (HANDS, *(d.id for d in rules.lanes))
    runners: list[Runner] = [*(a.id for a in rules.standing), *(c.id for c in rules.cards)]
    runner_lane: dict[Runner, LaneId | None] = {a.id: None for a in rules.standing}
    runner_lane.update({c.id: c.lane for c in rules.cards})
    return RulesIndex(
        stores={s.id: s for s in rules.stores},
        store_pos={s.id: i for i, s in enumerate(rules.stores)},
        skill_pos={s.id: i for i, s in enumerate(rules.skills)},
        standing={a.id: a for a in rules.standing},
        cards={c.id: c for c in rules.cards},
        card_pos={c.id: i for i, c in enumerate(rules.cards)},
        runner_pos={r: i for i, r in enumerate(runners)},
        chips={c.id: c for c in rules.chips},
        lanes=lanes,
        lane_pos={lane: i for i, lane in enumerate(lanes)},
        runner_lane=runner_lane,
        ruled=frozenset(d.id for d in rules.lanes if d.ruled),
        offers={o.id: o for o in rules.offers},
        answers={a.id: (o.id, a) for o in rules.offers for a in o.answers},
        town_mixes=frozenset(j.mix for o in _joining(rules) for j in o.joins),
    )
