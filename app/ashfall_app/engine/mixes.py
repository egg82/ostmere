"""Mixes: which cards run continuously, at what shares. Saved mixes nest (Composite).

Shares are basis points of the player's time (the HANDS lane), or in a town mix of one person's time (MixLayer). A
mix's components sum to at most BP (10_000), a town mix's per lane; the remainder is idle, shown as idle, never silently given to another card. A paused, waiting or
greyed card's unused share idles too, but for a paused card, whose share the rest of its mix on its lane runs, named
as a source (DESIGN.txt, "SPENT"). A mix holding a completed card is greyed whole (DESIGN.txt,
"Greyed mix").
"""
from dataclasses import dataclass
from enum import Enum

from .errors import InvalidVerbError
from .ids import CardId, MixId
from .units import BP

MAX_MIXES = 64   # saved mixes in a save: SaveMix past it is InvalidVerbError (checks.check_mixes)


class MixLayer(Enum):
    """Whose time a mix's shares are shares of: the player's (HANDS) or each person's own, the person being the lane a
    card is on (TOWN). Read from a mix's cards, and for a mix with none from Mix.layer or the joins that make it
    (plan.mix_layer; DESIGN.txt, "THE TOWN'S MIX")."""

    HANDS = "hands"
    TOWN = "town"


@dataclass(frozen=True)
class CardShare:
    """A card at share_bp of this mix (0 <= share_bp <= BP). The card runs continuously at that share: its work fills
    at the share's speed and its lines run at that share (DESIGN.txt, "Rate form")."""

    card: CardId
    share_bp: int


@dataclass(frozen=True)
class SpentShare:
    """The part, share_bp, of paused or spent card `card`'s saved share that a receiving card of its mix runs now
    (DESIGN.txt, "SPENT", "Giver"). Never saved: a function of the save at an instant."""

    card: CardId
    share_bp: int


@dataclass(frozen=True)
class SubMix:
    """A saved mix dropped in at share_bp: its flattened shares, scaled once by share_bp / BP (flatten_shares)."""

    mix: MixId
    share_bp: int


type Component = CardShare | SubMix


@dataclass(frozen=True)
class Mix:
    """A named, saved mix.

    layer: TOWN on a mix that was a town mix when it was emptied, so it stays one while it holds no card (a mix with
    cards is read from them). SaveMix and a leave set it; the value a verb carries is replaced (DESIGN.txt, "THE
    TOWN'S MIX")."""

    id: MixId
    components: tuple[Component, ...]
    layer: MixLayer = MixLayer.HANDS


@dataclass(frozen=True)
class SwitchMix:
    """Verb: make the saved mix `mix` the active one, the player's own. Switching to the already-active mix changes
    nothing. To a greyed mix: the player's switch is accepted (the mix stays greyed, nothing runs); the queue's cannot
    act. An order's SwitchMix is not applied: its mix runs over the player's while the order's condition holds
    (DESIGN.txt, "Greyed mix", "Order mix")."""

    mix: MixId


def flatten_shares(mixes: tuple[Mix, ...], mix: MixId) -> tuple[CardShare, ...]:
    """The cards a mix runs, at their effective shares, in depth-first declaration order.

    Compositional (DESIGN.txt, "Nested mix share"). Raises InvalidVerbError on an unknown mix id or a nesting cycle.
    """
    return tuple(CardShare(a, s) for a, s in _flat({m.id: m for m in mixes}, mix, (), {}).items())


def _flat(by_id: dict[MixId, Mix], mix: MixId, path: tuple[MixId, ...],
          done: dict[MixId, dict[CardId, int]]) -> dict[CardId, int]:
    """`done` holds each mix already flattened, so a mix nested by many others is walked once, not once per path."""
    if mix in path:
        raise InvalidVerbError(f"mix {mix} nests itself")
    if mix in done:
        return done[mix]
    found = by_id.get(mix)
    if found is None:
        raise InvalidVerbError(f"unknown mix {mix}")
    acc: dict[CardId, int] = {}
    for c in found.components:
        if isinstance(c, CardShare):
            acc[c.card] = acc.get(c.card, 0) + c.share_bp
        else:
            for card, share in _flat(by_id, c.mix, path + (mix,), done).items():
                acc[card] = acc.get(card, 0) + share * c.share_bp // BP
    done[mix] = acc
    return acc
