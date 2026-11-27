"""Lanes: where taps run, one at a time each, and the verb that taps a card.

HANDS (ids.py) is always a lane, the player's own time, where the active mix runs; Rules.lanes declares the others (a
drying rack). Semantics: engine/design/, "Lanes", part "CARDS".
"""
from dataclasses import dataclass

from .ids import CardId, LaneId


@dataclass(frozen=True)
class LaneDef:
    """A lane other than HANDS (declaring HANDS is invalid). It runs one tap at a time and never touches the player's
    time; only a ruled lane has a mix, the town's, once its person has joined (design/towns-mix.txt, "THE TOWN'S MIX"). ruled: a
    townsperson's lane, whose task the player's rules set and which the player never taps by hand (engine/design/, "Ruled
    lane").

    pooled: a ruled lane that is never a person: the group its members' cards sit on (engine/design/, "GROUPS (pooled
    lanes)"). It never joins and never taps. group: on a person's ruled lane, the pooled lane that is their group. The
    codec and the rules digest leave both out while at their defaults."""

    id: LaneId
    ruled: bool = False
    pooled: bool = False
    group: LaneId | None = None


@dataclass(frozen=True)
class TapCard:
    """Verb: do one completion of `card` on its lane (CardDef.lane), by hand. The player's tap, an order and the queue
    issue this same verb (Command).

    From the player: a card on a ruled lane (set by rules), a locked or unknown card, a busy lane, or a completed card
    raises InvalidVerbError; an unready
    card is a failed tap: it takes no time, changes nothing and emits no line. From an order,
    the queue or an Outcome: any of those, or an unready card, changes nothing. A player's tap does not make orders
    and the queue evaluate; its landing does.
    """

    card: CardId
