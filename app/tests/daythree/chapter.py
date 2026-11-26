"""A chapter past B4 as a route plays it, by ids (CLAUDE.md, "Never spoil the owner"): its sinks (dayone/sinks.py), the
one-off steps tapped the moment they are ready, the order cards a route that takes rules sets once offered, the cards
tapped by hand to keep a store up, and how to read its story ids off a save. Day two's player (daytwo/player.py)
plays one on top of day two's moves from the beat it starts at to the visit its last beat is seen in; a route that
neither holds a trip nor queues comforts does both by hand (moves.py)."""
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ashfall_app.engine import AnswerId, CardId, ChipId, OfferId, Order, Rules, Save, StoreId, Unlock, UnlockKind, View
from ashfall_app.engine.work import completions
from tests.dayone.policy import Move
from tests.dayone.sinks import Chapter


@dataclass(frozen=True)
class Landings:
    """How a chapter's story ids are read off a save (ids only, CLAUDE.md, "Never spoil the owner")."""

    triggered: Mapping[str, tuple[str, ...]]
    """Story ids that land when one of these triggers fires."""
    steps: Mapping[str, tuple[str, ...]]
    """Story ids that land at the first completion of one of these cards."""
    stages: Mapping[str, tuple[str, int]]
    """Story ids that land at a card's nth completion."""
    offers: Mapping[str, OfferId]
    """Story ids that land when the offer shows."""

    def of(self, save: Save, rules: Rules) -> set[str]:
        fired = fired_ids(save, rules)
        found = {b for b, ts in self.triggered.items() if fired & set(ts)}
        found |= {b for b, cs in self.steps.items() if any(completions(save, rules, CardId(c)) > 0 for c in cs)}
        found |= {b for b, (c, n) in self.stages.items() if completions(save, rules, CardId(c)) >= n}
        found |= {b for b, o in self.offers.items() if Unlock(UnlockKind.OFFER, o) in save.unlocked}
        return found


_FIRED: list[tuple[object, Rules, frozenset[str]]] = []


def fired_ids(save: Save, rules: Rules) -> frozenset[str]:
    """The ids of the triggers fired in `save`, kept while its fired flags and the rules are the same objects: every
    chapter's Landings reads them off each save of an absence."""
    if _FIRED and _FIRED[0][0] is save.fired and _FIRED[0][1] is rules:
        return _FIRED[0][2]
    found = frozenset(t.id for t, f in zip(rules.triggers, save.fired) if f)
    _FIRED[:] = [(save.fired, rules, found)]
    return found


@dataclass(frozen=True)
class Keep:
    """A card tapped by hand while its store is under `below` items: what a player does to have some of it on hand."""

    card: CardId
    store: StoreId
    below: int


@dataclass(frozen=True)
class Share:
    """A card added to the active mix at `share_bp`, the mix's other cards scaled to leave it, no hold (the hunt)."""

    card: CardId
    share_bp: int
    until: Callable[[Save], bool] | None = None
    """Once this holds, the card is taken out of the active mix (the kept shares scaled up) and not added again: what
    it makes or draws has run out of use."""


@dataclass(frozen=True)
class Cure:
    """A card tapped by hand while `store` holds any (a bad state's cure, tapped the moment it is ready)."""

    card: CardId
    store: StoreId


@dataclass(frozen=True)
class ChipRule:
    """A rule the player writes on a chip no order card answers (a season's chore): the chip's own condition, tapping
    its cure on the lane the route chose (moves.chip_rule)."""

    chip: ChipId
    cure: CardId


@dataclass(frozen=True)
class Later:
    start: str
    """The beat the chapter's moves start at."""
    stop: str
    """The beat whose visit ends the play."""
    sinks: Chapter
    steps: tuple[CardId, ...]
    """One-off steps, tapped the moment they are ready."""
    order_cards: tuple[tuple[Unlock, Order], ...]
    """Each order card's rule (the content's order_cards) and the unlock it is offered after: a route that takes rules
    sets it, first in its orders, once offered."""
    keeps: tuple[Keep, ...]
    landed: Callable[[Save, Rules], set[str]]
    """The chapter's story ids landed in a save."""
    news: tuple[str, ...]
    """The chapter's beats and side beats, in authored order, as News once seen."""
    answers: tuple[tuple[OfferId, AnswerId], ...] = ()
    """Offers of no kind, answered by hand when they show."""
    shares: tuple[Share, ...] = ()
    cures: tuple[Cure, ...] = ()
    own: Callable[[View, Save, Rules], Move | None] | None = None
    """The chapter's own moves, made before the shared ones (moves.move): what a later week adds to the policies."""
    queued: tuple[CardId, ...] = ()
    """One-off steps queued When ready once shown unready with a countdown (a presence step in a story night), rather
    than tapped when ready, so one that turns ready while the player is away still lands then."""
    chip_rules: tuple[ChipRule, ...] = ()
    """Rules a route that takes rules writes on chips with no order card, from the visit each chip is first seen."""
