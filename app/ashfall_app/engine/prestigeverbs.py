"""The player's prestige verbs and why one is refused (DESIGN.txt, "PRESTIGE PHASES"). Applying them: prestige.py.

All three are by hand only: none is an orders.OrderVerb, and an Order or QueueEntry naming one is refused
(refuse_by_hand). A click set ahead and landed while the player is away would be an auto-prestige with an extra step;
the carry window (phases.accrues) is what makes clicking at 03:00 gain nothing on clicking at breakfast.
"""
from dataclasses import dataclass
from enum import Enum

from .errors import InvalidVerbError
from .ids import NodeId, SkillId


@dataclass(frozen=True)
class Prestige:
    """Verb, the player's only: put one rank into `node` on `skill`'s track.

    It acts in one of two ways, checked in this order:
    - a pick is owed (PhaseState: len(picks) == phase - 2, after an UndoPick): the rank fills it. The phase, the XP,
      topped_at and click_level are unchanged; `node` must be on the menu (prestige.menu).
    - else the skill is at its top (phases.at_top): the click. The rank is appended to picks, the phase goes up by
      one, click_level becomes the level the XP already held shows in the new phase, and topped_at becomes the
      click's instant if that XP is already at the new phase's top, else None. XP itself is unchanged: the carry is
      ordinary XP whose level waited for the click. Nothing earned is taken back (unlocks, the stack, landed levels'
      pays); the new rank's entry joins the stack (pickentries.pick_entries), and orders and the queue evaluate at once.
    Refused (PrestigeRefused, the save unchanged) with the first that applies of: NO_PRESTIGE, UNKNOWN_SKILL,
    LOCKED_SKILL, then with no pick owed NOT_AT_TOP and TRACK_DONE, then NOT_ON_MENU. A skill whose whole track is
    finished is mastered: every click is refused TRACK_DONE, and it rests at its top."""

    skill: SkillId
    node: NodeId


@dataclass(frozen=True)
class UndoPick:
    """Verb, the player's only: take back `skill`'s last pick, a misclick window. Removes the last of picks, so a pick
    is owed (the next Prestige of the skill fills it from the same menu); the phase, its XP, its levels, topped_at
    and click_level stay. The window is open from the click until the skill's shown level first rises above
    click_level, which only work after the click can do (levels the carried XP landed at the click don't close it):
    prestige.undo_open. Orders and the queue evaluate at once.
    Refused with the first that applies of: NO_PRESTIGE, UNKNOWN_SKILL, LOCKED_SKILL, NOTHING_TO_UNDO (phase 1, or a
    pick already owed), UNDO_CLOSED."""

    skill: SkillId


@dataclass(frozen=True)
class MovePick:
    """Verb, the player's only: move the rank `node` holds on `skill`'s track to `to`, paying that rank's progress.

    The rank leaves `node` at once, so `node` has its rank open again, and parks on `to` (PhaseState.parked): it takes
    effect at the click that lifts the skill into the phase after next, so it is held by neither node for the rest of
    this phase and the whole of the next. The phase, its XP, levels, topped_at and click_level stay; the stack is
    rebuilt without the rank. `to` must be on the menu now (prestige.menu), and a parked rank holds its node as a
    taken rank does, so the menu moves on.
    Refused with the first that applies of: NO_PRESTIGE, UNKNOWN_SKILL, LOCKED_SKILL, PICK_OWED (an undo left a pick
    owed), NOT_PICKED (`node` holds no rank of the skill's picks), NOT_ON_MENU (`to` is not on the menu, or is `node` itself)."""

    skill: SkillId
    node: NodeId
    to: NodeId


class PrestigeRefusal(Enum):
    """Why a prestige verb cannot act. Each is carried by PrestigeRefused."""

    NO_PRESTIGE = "no_prestige"
    """rules.prestige is None."""
    UNKNOWN_SKILL = "unknown_skill"
    """The verb's skill is not in the rules."""
    LOCKED_SKILL = "locked_skill"
    """The skill is not unlocked (DESIGN.txt, "Unlocks")."""
    NOT_AT_TOP = "not_at_top"
    """Prestige with no pick owed, and the skill's XP is below its phase's top."""
    TRACK_DONE = "track_done"
    """Prestige with no pick owed, and every node on the skill's track is finished: the menu is empty. The skill is
    mastered: it rests at its top for good, its XP stopping at the carry's end as at any top."""
    NOT_ON_MENU = "not_on_menu"
    """The node is unknown, on another skill's track, finished, or not among the menu's nodes."""
    NOTHING_TO_UNDO = "nothing_to_undo"
    """UndoPick with no pick to take back: the skill is in phase 1, or its last pick is already undone."""
    UNDO_CLOSED = "undo_closed"
    """UndoPick after the skill's shown level rose past the level the click landed at."""
    PICK_OWED = "pick_owed"
    """MovePick while an undone pick is owed: fill it first."""
    NOT_PICKED = "not_picked"
    """MovePick of a node that holds no rank of the skill's picks (a parked rank is not held yet)."""
    BY_HAND_ONLY = "by_hand_only"
    """A standing order's or a queue entry's verb is a Prestige, an UndoPick or a MovePick."""


class PrestigeRefused(InvalidVerbError):
    """decide() refused a prestige verb, or an order or queue entry naming one; `reason` says why. An
    InvalidVerbError, so a caller that handles refused verbs handles these the same way."""

    def __init__(self, reason: PrestigeRefusal) -> None:
        super().__init__(f"prestige refused: {reason.value}")
        self.reason = reason


def refuse_by_hand(verb: object) -> None:
    """Raise PrestigeRefused(BY_HAND_ONLY) when `verb`, an order's or a queue entry's, is a Prestige, UndoPick or MovePick.
    Takes object: the order types already exclude them, and this catches one built or decoded around the types."""
    if isinstance(verb, (Prestige, UndoPick, MovePick)):
        raise PrestigeRefused(PrestigeRefusal.BY_HAND_ONLY)
