"""Typed ids, so a store id can't be passed where an action id is meant."""
from enum import Enum
from typing import NewType

StoreId = NewType("StoreId", str)
SkillId = NewType("SkillId", str)
ActionId = NewType("ActionId", str)
MixId = NewType("MixId", str)
SourceId = NewType("SourceId", str)
"""Where a modifier comes from (a building, a tool, a season): shown by explain(), never interpreted."""
CardId = NewType("CardId", str)
"""One card: a kind of work the player taps by hand or runs in the mix (cards.py)."""
LaneId = NewType("LaneId", str)
ChipId = NewType("ChipId", str)
TriggerId = NewType("TriggerId", str)
SideId = NewType("SideId", str)
"""One side of a fight, by strength: the player's hands, a lane's person, a region's guard (strength.SideDef)."""
ThreatId = NewType("ThreatId", str)
"""One entry of a region's roster of threats (strength.ThreatDef)."""
FeatureId = NewType("FeatureId", str)
"""A part of the page the engine only switches on (the ledger, the craft list, the journal): unlocked, never run."""
EntryId = NewType("EntryId", str)
"""One page of the journal, unlocked when its first note is written; the engine only carries it (DESIGN.txt, "Unlocks")."""
NoteId = NewType("NoteId", str)
"""One note written on a journal page, unlocked when its gate holds; as EntryId."""
OfferId = NewType("OfferId", str)
"""Someone asking the player something, with two or more answers (DESIGN.txt, "Offers")."""
AnswerId = NewType("AnswerId", str)
"""One answer of one offer; unique across every offer."""
KindId = NewType("KindId", str)
"""A group of offers that ask the same question; an AnswerKind names it (DESIGN.txt, "OFFER KINDS")."""
RoleId = NewType("RoleId", str)
"""What an answer means within its offer's kind: the same in every offer of the kind."""
NodeId = NewType("NodeId", str)
"""One node of a skill's prestige track: a bonus each click puts one rank into (nodes.NodeDef)."""
LineKey = NewType("LineKey", str)
"""A content key for one log line. The engine emits keys and never text (DESIGN.txt, "Lines")."""

type Runner = ActionId | CardId
"""What a rate line belongs to: a standing action or a card (modifiers.RateRef, state.Pause)."""

HANDS = LaneId("hands")
"""The player's own time: the lane the active mix runs its cards on and taps occupy (DESIGN.txt, "Lanes")."""

TOWN_PREFIX = "town:"
"""A MixId beginning so is the game's: only a join creates one (DESIGN.txt, "THE TOWN'S MIX", "Reserved ids")."""


class IdKind(Enum):
    """The kinds of id a rename names (DESIGN.txt, "Renames"): each id is renamed by renames of its own kind. STANDING
    is a standing action's id (ActionId); SOURCE a modifier's source, a label that is renamed but never checked."""

    STORE = "store"
    SKILL = "skill"
    STANDING = "standing"
    CARD = "card"
    LANE = "lane"
    CHIP = "chip"
    TRIGGER = "trigger"
    FEATURE = "feature"
    SOURCE = "source"
    OFFER = "offer"
    ANSWER = "answer"
    ENTRY = "entry"
    NOTE = "note"
    NODE = "node"
