"""Wire model of what the next story beats wait on (View.goals; CONTRACT.txt, "Goals"); the conventions in models.py
hold here."""
from enum import StrEnum

from pydantic import BaseModel

from .decision_models import AtLeast, Segment


class GoalKind(StrEnum):
    STORE = "store"
    CARD = "card"
    LEVEL = "level"
    CLOCK = "clock"


class Goal(BaseModel):
    """One thing an open story beat waits on: a store's amount reaching `target` (store, value), a card's completions
    reaching `target` or the card running at target 0 (card), a skill's level reaching `target` (skill), or a wait on
    the clock alone landing at `at`. The page marks the store's line, the card or the skill's row; a store with no line
    yet, and the clock, it states as a line of their own, the clock's naming what keeps it moving."""

    kind: GoalKind
    store: str | None
    card: str | None
    skill: str | None
    target: int
    """Quantity units (store), completions (card), a level (level); 0 for a clock or a card running."""
    value: Segment | None
    """The store's amount, sampled like a ledger line; null unless kind is store."""
    at: int | None
    """When the clock lands if nothing changes the segments; null unless kind is clock, or the clock waits on a dry
    store of `feeds`. It holds until next_event_at."""
    feeds: list[str]
    """A clock's: the stores whose running dry pauses it, whose lines the page marks; empty otherwise."""


class GoalLimit(BaseModel):
    """A store a card moving the goal waits on, dry: the line that holds the goal back while it stays dry."""

    store: str
    in_per_hour: int
    """What comes into the store per hour as set, in rate units: its makers' lines alone."""


class RuleDry(BaseModel):
    """A store rule's mix that cannot reach the rule's release for want of a store (CONTRACT.txt, "Dry rules"): the rule
    holds the hands and the store is dry (`holding`), or no card of the mix makes the store, so the mix may stop short."""

    store: str
    """The shown input store: the first in running order that a runner making the watched store is paused or spent on
    (holding), else the first the mix's cards cost and none makes."""
    holding: bool


class GoalRow(BaseModel):
    """How the setup as set moves one goal (CONTRACT.txt, "Goal rows"): a store reaching `target` (store) or a skill
    reaching level `target` (skill), when it lands at today's rates, and the line that binds it."""

    kind: GoalKind
    """store or level; a card's count and the clock are never rows (a mix does not move them)."""
    store: str | None
    skill: str | None
    target: int
    """Quantity units (store), a level (level): the shown level for a skill's next one, the counted level for a level
    a story beat waits on."""
    lands_at: int | None
    """Game time the goal lands if the rates as set hold: now when already met; null when they never land it (nothing
    moves it, the store falls, or `target` is over its cap)."""
    per_hour: int
    """The goal's own line as set, rate units per hour: the store's net, or the XP the skill gains."""
    limit: GoalLimit | None
    """The dry store a runner moving the goal waits on, the first in running order; null when none does (the goal's
    own line binds it) and for a goal already met."""
    until: AtLeast
    """The condition that holds once the goal lands: at_least store_value `target` (store), or at_least skill_level at
    the counted level `target` is in the skill's phase (level), value and release equal. A goal stint's queue entry
    takes it as its `until` (CONTRACT.txt, "Goal stints")."""
