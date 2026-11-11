"""Events and their total order. Field order is the sort order: (time, kind, sequence), so `sorted()` is the order
same-instant events resolve in. Rates are constant between events."""
from dataclasses import dataclass
from enum import IntEnum


class EventKind(IntEnum):
    """Priority within an instant: lower resolves first. `sequence` breaks ties within a kind."""

    STORE_LIMIT = 0
    """A store reaches its segment's limit (empty or cap). sequence: index in rules.stores."""
    RESUME = 1
    """A paused runner's store refills to its resume level. sequence: the runner's index, rules.standing then
    rules.cards."""
    COMPLETION = 2
    """A capped card's work reaches its next completion, tapped or mixed (an uncapped card's completions are rates,
    never events: DESIGN.txt, "Completions"). sequence: the card's index in rules.cards."""
    TAP_DONE = 3
    """A lane's tapped card reaches its next completion (after its COMPLETION, if capped). sequence: the lane's index, HANDS first, then rules.lanes."""
    LEVEL_UP = 4
    """A skill's XP reaches the next threshold (under prestige, the next of its phase's: phases.next_level_xp).
    sequence: index in rules.skills."""
    TOP_OUT = 5
    """Under prestige, a skill whose PhaseState.topped_at is None has XP at its phase's top (phases.phase_top), reached
    now or already held: topped_at becomes this instant. sequence: index in rules.skills."""
    CARRY_END = 6
    """Under prestige, a skill's carry window ends (phases.carry_ends_at) while its XP still rises: its XP rate drops
    to 0. sequence: index in rules.skills."""
    REQUIRES = 7
    """A running card's requires turn all true or one false (a mix card's WAITING starts or ends; a tap is
    interrupted). sequence: the card's index in rules.cards."""
    CHIP = 8
    """A chip's latched condition turns true or false. sequence: index in rules.chips."""
    TRIGGER = 9
    """A trigger that has not fired finds its condition true. sequence: index in rules.triggers."""
    LATCH = 10
    """An order's condition turns true or false. sequence: index in save.orders."""
    QUEUE_POP = 11
    """The controlling queue entry's `until` turns true (the first live entry), or a dead entry's `until` that cannot
    fall turns true (it settles: DESIGN.txt, "Greyed mix"). sequence: 0."""
    READY = 12
    """A TapCard named by a true order or by the controlling queue entry, unlocked, not completed and on a free lane,
    turns ready: orders and the queue evaluate (DESIGN.txt, "Orders"). Also at T + 1 for every such card already ready
    when the firing cap suspended evaluation at T (DESIGN.txt, "Evaluation after a cascade"), and one at T + 1, with
    sequence len(rules.cards) and subject '', for the verbs with no card that could act then. sequence: the card's
    index in rules.cards."""


@dataclass(frozen=True)
class CascadeLimit:
    """An instant whose firings reached rules.max_firings_per_instant: order and queue evaluation was suspended for
    the rest of it and time moved on. `firings` counts every firing at that instant, including events processed after
    the suspension. The latest is kept on the save (Save.last_cascade, counted by Save.cascade_count)."""

    time: int
    firings: int


@dataclass(frozen=True, order=True)
class Event:
    """`subject` is the id of the store, runner (RESUME), lane, card (COMPLETION, REQUIRES, READY), skill, chip or
    trigger, or the order index as a string ('' for QUEUE_POP and for READY of the verbs with no card)."""

    time: int
    kind: EventKind
    sequence: int
    subject: str
