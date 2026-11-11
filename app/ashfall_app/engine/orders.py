"""Standing orders (an ordered list of (condition, verb), first match wins) and the queue of verbs.

Conditions are thresholds on stores, levels and time, each with a latch (Save.latches). When orders act: DESIGN.txt,
"Orders" and "Firing cap".
"""
from dataclasses import dataclass

from .answers import AnswerKind, AnswerOffer
from .ids import CardId, LaneId, Runner, SkillId, StoreId
from .lanes import TapCard
from .mixes import SwitchMix
from .unlocks import Unlock


@dataclass(frozen=True)
class StoreValue:
    store: StoreId


@dataclass(frozen=True)
class SkillLevel:
    skill: SkillId


@dataclass(frozen=True)
class CardCount:
    """How many times `card` has completed, by taps and the mix together. Solved from the card's work segment like a
    store, not discrete: completions are a count read off one segment (DESIGN.txt, "Completions")."""

    card: CardId


@dataclass(frozen=True)
class Unlocked:
    """1 while `unlock` is in the save's unlock set, else 0. A discrete subject."""

    unlock: Unlock


@dataclass(frozen=True)
class Running:
    """1 while `runner` contributes to some rate (a standing action unlocked, a card with a non-zero mix share or
    tapped, and not paused, yielded, waiting, greyed or held at 0), else 0: its Run's num and its share are both > 0.
    A discrete subject: it changes only at instants where something else fires."""

    runner: Runner


@dataclass(frozen=True)
class LaneRules:
    """How many orders in the save tap a card on the ruled lane `lane` and are not AfterTime(0), the shape an install
    makes: the rules the player set, not the always rule. A discrete subject, allowed only as a trigger's `when`
    (DESIGN.txt, "Lane rules")."""

    lane: LaneId


type Subject = StoreValue | SkillLevel | CardCount | Unlocked | Running | LaneRules
type DiscreteSubject = Unlocked | Running | LaneRules


@dataclass(frozen=True)
class AtLeast:
    """True once subject >= value; then stays true until subject < release (release <= value).

    release == value is a plain threshold; release < value is a hysteresis band, so two orders can't flip each other.
    For a SkillLevel subject, value and release are levels; for a store, quantity units; for a CardCount, a count;
    for Unlocked and Running, 0 or 1; for LaneRules, a count.
    """

    subject: Subject
    value: int
    release: int


@dataclass(frozen=True)
class AtMost:
    """True once subject <= value; then stays true until subject > release (release >= value)."""

    subject: Subject
    value: int
    release: int


@dataclass(frozen=True)
class AfterTime:
    """True from engine time `time` onward."""

    time: int


type Condition = AtLeast | AtMost | AfterTime

type OrderVerb = SwitchMix | TapCard | AnswerOffer | AnswerKind
"""Verbs an order or the queue can apply: every player verb that acts in the world (SaveMix, DeleteMix, SetOrders and
SetQueue edit the plan itself). Every later world verb joins this union (docs/systems.md, "Every verb has an order").
An AnswerOffer that cannot act changes nothing; one of an answered offer is dead (DESIGN.txt, "Dead"). An AnswerKind is
never dead (DESIGN.txt, "OFFER KINDS")."""


@dataclass(frozen=True)
class Order:
    """While `when` is true: a TapCard taps when it can act and no earlier tap order is true and can act; a SwitchMix
    runs its mix over the player's when no earlier mix order's mix runs, and the player's own comes back once it
    releases. An order whose verb cannot act is passed over; tap and mix orders never shadow each other (DESIGN.txt,
    "Orders", "Order mix"). A TapCard may name a card locked today."""

    when: Condition
    then: OrderVerb


@dataclass(frozen=True)
class QueueEntry:
    """Apply `verb` when this entry is the controlling one: the first live entry. An entry whose verb is dead (a switch
    to a greyed mix, a tap of a completed card) is passed over and kept, frozen: never popped while dead unless it
    settles (its `until` holds and cannot fall), when it pops. The controlling entry pops once its `until` is true
    (checked at every instant, whoever controls), at once if it already is when it comes to control, a revived dead
    entry included (DESIGN.txt, "Greyed mix")."""

    verb: OrderVerb
    until: Condition


def initial_latch(condition: Condition, subject_value: int | None, now: int) -> bool:
    """A latch's state when orders are set: AtLeast is v >= value, AtMost is v <= value, AfterTime is now >= time.
    subject_value is None exactly for AfterTime."""
    if isinstance(condition, AfterTime):
        return now >= condition.time
    if subject_value is None:
        raise ValueError("a threshold condition needs its subject's value")
    if isinstance(condition, AtLeast):
        return subject_value >= condition.value
    return subject_value <= condition.value
