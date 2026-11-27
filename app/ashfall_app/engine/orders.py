"""Standing orders (an ordered list of (condition, verb), first match wins) and the queue of verbs.

Conditions are thresholds on stores, levels and time, each with a latch (Save.latches). When orders act: design/core.txt,
"Orders" and "Firing cap".
"""
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace

from .answers import AnswerKind, AnswerOffer
from .ids import CardId, LaneId, Runner, SkillId, StoreId
from .lanes import TapCard
from .mixes import SwitchMix
from .unlocks import Unlock
from .units import BP


@dataclass(frozen=True)
class StoreValue:
    store: StoreId


@dataclass(frozen=True)
class SkillLevel:
    skill: SkillId


@dataclass(frozen=True)
class CardCount:
    """How many times `card` has completed, by taps and the mix together. Solved from the card's work segment like a
    store, not discrete: completions are a count read off one segment (design/cards.txt, "Completions")."""

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
    (engine/design/, "Lane rules")."""

    lane: LaneId


type Subject = StoreValue | SkillLevel | CardCount | Unlocked | Running | LaneRules
type DiscreteSubject = Unlocked | Running | LaneRules


@dataclass(frozen=True)
class AtLeast:
    """True once subject >= value; then stays true until subject < release (release <= value).

    release == value is a plain threshold; release < value is a hysteresis band, so two orders can't flip each other.
    For a SkillLevel subject, value and release are levels; for a store, quantity units; for a CardCount, a count;
    for Unlocked and Running, 0 or 1; for LaneRules, a count.

    value_of_cap, release_of_cap: that level is basis points (0..BP) of the watched store's cap now, read as a quantity
    wherever the condition is read; a StoreValue subject in the save's orders and queue only (engine/design/, "SHARE
    LEVELS"). The release-side rule above then holds between the read quantities.
    """

    subject: Subject
    value: int
    release: int
    value_of_cap: bool = False
    release_of_cap: bool = False


@dataclass(frozen=True)
class AtMost:
    """True once subject <= value; then stays true until subject > release (release >= value). value_of_cap and
    release_of_cap as AtLeast's."""

    subject: Subject
    value: int
    release: int
    value_of_cap: bool = False
    release_of_cap: bool = False


@dataclass(frozen=True)
class AfterTime:
    """True from engine time `time` onward."""

    time: int


type Condition = AtLeast | AtMost | AfterTime


def share_problem(cond: AtLeast | AtMost) -> str | None:
    """Why a condition holding a share level is not a valid one, or None (design/share-levels.txt, "SHARE LEVELS"): a share level
    reads a StoreValue's cap and is in 0..BP, and a release is on the right side of a value in the same form. A share
    and a quantity are on different scales, so a band of one of each is never compared."""
    if not isinstance(cond.subject, StoreValue):
        return "a share level reads a store's cap"
    levels = ((cond.value, cond.value_of_cap), (cond.release, cond.release_of_cap))
    if any(of_cap and not 0 <= b <= BP for b, of_cap in levels):
        return "a share level is in 0..BP"
    if cond.value_of_cap != cond.release_of_cap:
        return None
    ok = cond.release <= cond.value if isinstance(cond, AtLeast) else cond.release >= cond.value
    return None if ok else "condition release is on the wrong side of its value"

type OrderVerb = SwitchMix | TapCard | AnswerOffer | AnswerKind
"""Verbs an order or the queue can apply: every player verb that acts in the world (SaveMix, DeleteMix, SetOrders and
SetQueue edit the plan itself). Every later world verb joins this union (docs/systems.md, "Every verb has an order").
An AnswerOffer that cannot act changes nothing; one of an answered offer is dead (design/townsfolk.txt, "Dead"). An AnswerKind is
never dead (design/offer-kinds.txt, "OFFER KINDS")."""


@dataclass(frozen=True)
class Order:
    """While the rule is on (rule_on: `when` true and no guard's latch true): a TapCard taps when it can act and no
    earlier tap order is on and can act; a SwitchMix runs its mix over the player's when no earlier mix order's mix
    runs, and the player's own comes back once it is off. An order whose verb cannot act is passed over; tap and mix
    orders never shadow each other (engine/design/, "Orders", "Order mix"). A TapCard may name a card locked today."""

    when: Condition
    then: OrderVerb
    unless: tuple[Condition, ...] = ()
    """Guards: while any one's latch is true the rule is paused, never let go (design/rule-guards.txt, "RULE GUARDS"). Each is
    stored as the condition that blocks, latched as `when` is, with its own band. At most MAX_GUARDS, none twice."""
    or_else: tuple[OrderVerb, ...] = ()
    """Fallbacks: the rule acts through the first of `actions` that can act (design/or-else.txt, "OR ELSE"). Every action is
    the same kind of verb, taps of one lane or mixes of one layer; a rule answering an offer has none."""
    below_next: bool = False
    """The rule sits under Next, the queue's row in the hands' list: a ready queue entry outranks it (engine/design/, "Next's
    row"). Set by the player alone, never read off what the rule does. It is where the rule sits, as its index is, so
    readers that ask whether two rules are the same rule compare them unplaced. Orders keep it as a run to the end
    (placed)."""

    @property
    def actions(self) -> tuple[OrderVerb, ...]:
        """`then` followed by `or_else`: what the rule tries, in that order."""
        return (self.then, *self.or_else)


MAX_GUARDS = 3
MAX_ACTIONS = 3


@dataclass(frozen=True)
class GuardedLatch:
    """The latches of a rule with guards: `when`'s, and one per guard in the order of Order.unless. A rule with no
    guard has a bare bool instead, so each rule has one form and equal saves encode alike."""

    when: bool
    unless: tuple[bool, ...]


type Latch = bool | GuardedLatch
"""Save.latches[i]: a bool for a rule with no guard, else a GuardedLatch."""


@dataclass(frozen=True)
class QueueEntry:
    """Apply `verb` when this entry is the controlling one: the first live entry. An entry whose verb is dead is passed
    over: a tap of a completed card pops at once, and a switch to a greyed mix is kept, frozen: never popped while dead
    unless it settles (its `until` holds and cannot fall), when it pops. The controlling entry pops once its `until` is true
    (checked at every instant, whoever controls), at once if it already is when it comes to control, a revived dead
    entry included (design/cards.txt, "Greyed mix")."""

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


def rule_on(latch: Latch) -> bool:
    """Whether the rule holding `latch` is on: its `when` latch true and no guard's. What everything that acts on a
    rule asks (which mix runs, which tap starts, which lane a rule holds, READY)."""
    if isinstance(latch, GuardedLatch):
        return latch.when and not any(latch.unless)
    return latch


def when_latch(latch: Latch) -> bool:
    """The state of the rule's `when` latch alone: what the rule log and View.orders_on read."""
    return latch.when if isinstance(latch, GuardedLatch) else latch


def guard_latches(latch: Latch) -> tuple[bool, ...]:
    """Each guard's latch, in the order of Order.unless; () for a rule with no guard."""
    return latch.unless if isinstance(latch, GuardedLatch) else ()


def listed(orders: tuple[Order, ...], latches: tuple[Latch, ...]) -> Iterator[tuple[int, OrderVerb, Latch]]:
    """(rule index, action, the rule's latch) for every action of every rule, in rule order and then list order: the
    rules read as the adjacent one-action rules they stand for, which is how every source of evaluation walks them
    (design/or-else.txt, "OR ELSE")."""
    for i, (o, latch) in enumerate(zip(orders, latches)):
        for a in o.actions:
            yield i, a, latch


def pruned(order: Order, drop: Callable[[OrderVerb], bool]) -> Order | None:
    """The order with the actions `drop` names taken out of its list, else unchanged; None when none is left."""
    actions = tuple(a for a in order.actions if not drop(a))
    if not actions:
        return None
    return order if actions == order.actions else replace(order, then=actions[0], or_else=actions[1:])


def placed(orders: tuple[Order, ...]) -> tuple[Order, ...]:
    """The orders with every rule after one below Next below it too: Next is one row, so a rule appended (the lowest
    priority) lands under it once any rule does (design/nexts-row.txt, "Next's row")."""
    first = next((i for i, o in enumerate(orders) if o.below_next), len(orders))
    return tuple(o if i < first or o.below_next else replace(o, below_next=True) for i, o in enumerate(orders))


def unplaced(order: Order) -> Order:
    """The rule without where it sits relative to Next: what it is, for matching a rule across a move."""
    return replace(order, below_next=False) if order.below_next else order


def latch_of(when: bool, guards: tuple[bool, ...]) -> Latch:
    """The one form of a rule's latch: the bare `when` latch with no guard, else a GuardedLatch."""
    return GuardedLatch(when, guards) if guards else when
