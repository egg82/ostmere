"""Every verb the player can decide. Each one an order or the queue can also apply is in orders.OrderVerb: all that act
in the world but Prestige, UndoPick and MovePick, which are by hand only (prestigeverbs.py)."""
from dataclasses import dataclass

from ..offers.answers import AnswerKind, AnswerOffer
from .ids import MixId
from ..orders.lanes import TapCard
from ..mixes.mixes import Mix, SwitchMix
from ..orders.orders import Order, QueueEntry
from ..prestige.prestigeverbs import MovePick, Prestige, UndoPick


@dataclass(frozen=True)
class SaveMix:
    """Save `mix` under its id, replacing any saved mix of that id in place (new ids append). If it is the running
    mix, the change takes effect at once. Invalid shares, unknown ids, a nesting cycle, a card off HANDS, a
    locked card, or a completed card (a mix is never saved greyed: design/cards.txt, "Greyed mix"), a new id
    past MAX_MIXES saved mixes, or cards of the other layer under a saved mix's id (design/towns-mix.txt, "Reserved ids"):
    InvalidVerbError."""

    mix: Mix


@dataclass(frozen=True)
class DeleteMix:
    """Delete the saved mix `mix`. Unknown, nested in another saved mix, or named by an order or a queue entry:
    InvalidVerbError (edit those first; nothing is deleted under them). Deleting the active mix leaves no mix active
    (an order's mix running over it keeps running), and orders and the queue evaluate at once (the hands would
    otherwise idle by the player's own edit)."""

    mix: MixId


@dataclass(frozen=True)
class SetOrders:
    """Replace the standing orders. An order equal to an old one keeps its latch; a new one's is set by
    orders.initial_latch (engine/design/, "Rule changes"). If that changes the running mix, every
    pause clears (design/cards.txt, "Order mix"); then orders evaluate at once.
    A condition with release on the wrong side, or a verb naming an unsaved mix: InvalidVerbError. A TapCard of a
    locked card is accepted (it cannot act until unlocked)."""

    orders: tuple[Order, ...]


@dataclass(frozen=True)
class SetQueue:
    """Replace the queue (an empty tuple clears it), then evaluate at once. Validated as SetOrders is, and an entry
    tapping a card on a ruled lane, or an AnswerKind, raises InvalidVerbError (the queue is the hands' plan: engine/design/,
    "Ruled lane", "OFFER KINDS")."""

    entries: tuple[QueueEntry, ...]


type Verb = (SwitchMix | SaveMix | DeleteMix | SetOrders | SetQueue | TapCard | AnswerOffer | AnswerKind | Prestige
             | UndoPick | MovePick)
