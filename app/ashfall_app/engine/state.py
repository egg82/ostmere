"""A save's engine state at one instant. Immutable; the engine returns new saves, never mutates one.

Canonical form, so two saves that mean the same thing compare equal: every segment starts at `time`; stores and
skills follow rules order; mixes keep the order they were first saved in; pauses follow runner order (rules.standing
then rules.cards); cards follow rules.cards order.
"""
from dataclasses import dataclass

from .cards import CardState, LaneState
from .events import CascadeLimit
from .ids import MixId, NodeId, Runner, SkillId, StoreId
from .mixes import Mix
from .modifiers import Modifier
from .orders import Order, QueueEntry
from .segments import Segment
from .unlocks import Unlock


@dataclass(frozen=True)
class StoreState:
    store: StoreId
    segment: Segment


@dataclass(frozen=True)
class ParkedRank:
    """A rank the player moved (prestige.MovePick), waiting for its new node: it takes effect at the click that lifts
    the skill into phase `due`, and till then is held by neither node."""

    node: NodeId
    due: int


@dataclass(frozen=True)
class PhaseState:
    """One skill's prestige phase (phases.py), held on its SkillState, never on Save.

    phase >= 1: 1 until the skill's first click; each click that lifts the top adds 1.
    picks: the node each click put a rank into, in click order. len(picks) == phase - 1, or phase - 2 while a pick
    is owed: UndoPick took the last pick back and kept the phase, and the next Prestige of the skill fills it.
    topped_at: the instant the skill's XP reached phases.phase_top(phase), None while below it. It bounds the carry
    (phases.carry_ends_at). Set once per phase; a click into a phase whose top the carried XP already reaches sets it
    to the click's instant.
    click_level: the shown level the last click landed at (the carried XP read in its new phase), None in phase 1.
    The undo window is open while the shown level is still click_level (prestige.undo_open); levels only rise within
    a phase, so once it closes it stays closed until the next click.
    parked: ranks moved by MovePick and not yet settled, each on the node it will join. len(picks) + len(parked) ==
    phase - 1, or phase - 2 while a pick is owed. A click into phase `due` settles a rank: it joins picks just before
    the click's own pick, so UndoPick still takes back the click's.

    The default (FIRST_PHASE) is every skill's state until it first tops out; the codec leaves it out of the text, so
    a save that never topped out encodes as it did before phases existed."""

    phase: int = 1
    picks: tuple[NodeId, ...] = ()
    topped_at: int | None = None
    click_level: int | None = None
    parked: tuple[ParkedRank, ...] = ()


FIRST_PHASE = PhaseState()


@dataclass(frozen=True)
class SkillState:
    """XP as a segment; its limit is at most its phase's ceiling (phases.xp_ceiling: the curve's last threshold with no
    prestige). The level is derived (skills.level_for; phases.level_shown under prestige).

    phase: where the skill stands in prestige (PhaseState); FIRST_PHASE under rules with no prestige. Every engine
    write of a SkillState keeps it (dataclasses.replace), so only Prestige, UndoPick and topping out change it."""

    skill: SkillId
    xp: Segment
    phase: PhaseState = FIRST_PHASE


@dataclass(frozen=True)
class Pause:
    """`runner` is paused because `store` ran dry; it resumes when the store reaches `resume_at`. A paused card's work
    stops with it (its bar and its lump lines both stop: DESIGN.txt, "Rate form")."""

    runner: Runner
    store: StoreId
    resume_at: int


@dataclass(frozen=True)
class Save:
    """Every event at or before `time` has been resolved; the next event is strictly after `time`.

    latches[i] belongs to orders[i]. active is the player's own mix, written only by the player's and the queue's
    SwitchMix and by DeleteMix: None until the first switch, and after DeleteMix of it. An order's mix runs over it
    while the order is latched (the running mix, derived: DESIGN.txt, "Order mix"). An active mix may be greyed
    (derived, never stored: DESIGN.txt, "Greyed mix").
    """

    time: int
    stores: tuple[StoreState, ...]
    skills: tuple[SkillState, ...]
    mixes: tuple[Mix, ...]
    active: MixId | None
    pauses: tuple[Pause, ...]
    orders: tuple[Order, ...]
    latches: tuple[bool, ...]
    queue: tuple[QueueEntry, ...]
    modifiers: tuple[Modifier, ...]
    cascade_count: int = 0
    """How many instants have hit the firing cap; a caller logs a new one by comparing counts."""
    last_cascade: CascadeLimit | None = None
    """The most recent instant that hit the firing cap (events.CascadeLimit), or None."""
    lanes: tuple[LaneState, ...] = ()
    """One per lane, HANDS first, then rules.lanes order (DESIGN.txt, "Lanes")."""
    cards: tuple[CardState, ...] = ()
    """Each card with a tap count, mix work or a raised cap, in rules.cards order; absent means all zero. The
    Completed set is derived from these and the caps, never stored (DESIGN.txt, "Caps")."""
    unlocked: tuple[Unlock, ...] = ()
    """The unlock set, sorted by unlocks.unlock_key; only grows. Ignored when rules.opening is None."""
    chips: tuple[bool, ...] = ()
    """chips[i] is the latch of rules.chips[i]."""
    chips_seen: tuple[bool, ...] = ()
    """chips_seen[i] is True once rules.chips[i] has shown (time 0 included); it never resets, so the chip's on_line
    plays once per save (DESIGN.txt, "Chips")."""
    fired: tuple[bool, ...] = ()
    """fired[i] is True once rules.triggers[i] has fired; it never resets."""
    ended_at: int | None = None
    """The first instant rules.end held (DESIGN.txt, "The end"), or None; once set it never changes."""
