"""A skill's prestige phase on the wire (CONTRACT.txt, "PRESTIGE PHASES"; re-exported from models.py)."""
from pydantic import BaseModel


class MenuNode(BaseModel):
    """One node the skill's next pick may go into: `ranks_taken` of its `ranks` (drawn "2/5"), and its target's value
    now and with one more rank, each at a full share: a make in rate units per hour, a card's work in work units per
    second, a store's cap in quantity units (Scales)."""

    node: str
    ranks_taken: int
    ranks: int
    before_value: int
    after_value: int


class ParkedPick(BaseModel):
    """A rank a move parked on `node`: it takes effect at the click that lifts the skill into phase `due`."""

    node: str
    due: int


class SkillPrestige(BaseModel):
    """Where the skill stands in its prestige phases, at view.at."""

    phase: int
    """1 until the first click."""
    level_counted: int
    """Levels counted across phases: what a skill-level condition reads. It never falls at a click."""
    at_top: bool
    """The skill waits at its phase's top for the player's click (SkillBar.level is the phase's top level)."""
    waiting_levels: int
    """The levels a click now would land the new phase at, above its level 1 ("+6 levels waiting"); 0 below the top.
    As of view.at: the carry raises it until the carry window closes."""
    menu_nodes: list[MenuNode]
    """The nodes the next pick may go into, in track order; the same all phase. Empty once mastered."""
    undo_open: bool
    """Taking back the last pick would act now."""
    mastered: bool
    """Every node of the track is finished: no click waits at the top, ever."""
    pick_owed: bool
    """An undo took the last pick back: the next Prestige fills it from menu_nodes, at or below the top, and the phase
    stays."""
    topped_at: int | None
    """When the skill reached its current phase's top; null below it."""
    picked: list[str]
    """The nodes the skill's picks hold, in click order: what a move may take a rank from."""
    parked: list[ParkedPick]
    """Ranks a move parked, each out of play until phase `due` begins."""
