"""The forecast on the wire (CONTRACT.txt, "Forecast"; re-exported from models.py)."""
from pydantic import BaseModel


class ForecastLevel(BaseModel):
    skill: str
    at: int
    """When one of the skill's next levels lands: one entry per level-up, in order."""


class ForecastTop(BaseModel):
    skill: str
    at: int
    """When the skill reaches its phase's top ("tops out in"); at most one per skill."""


class ForecastFull(BaseModel):
    store: str
    at: int
    """A time the store reaches its cap from below, the cap as it stands then."""


class ForecastEmpty(BaseModel):
    store: str
    at: int
    """A time the store runs down to 0 from above."""


class Forecast(BaseModel):
    """Everything that lands by `horizon_at` if the player changes nothing: orders, the queue and everything running
    played out (engine DESIGN.txt, "Forecast"). It holds for every later view of the save until its next decision.
    A time past horizon_at is unknown: draw none, never a guess."""

    horizon_at: int
    level_ups: list[ForecastLevel]
    """No entry past a phase's top: the levels the carry passes wait for the click."""
    tops_out: list[ForecastTop]
    """Each skill below its phase's top, not mastered, that reaches it by horizon_at; empty without prestige."""
    fills: list[ForecastFull]
    """Only for stores the view has unlocked, as are empties."""
    empties: list[ForecastEmpty]


class ForecastAnswer(BaseModel):
    """POST /api/saves/{save_id}/forecast: the save advanced to now, and its forecast from there."""

    decisions: int
    """The save's Step.decisions: the forecast holds while the save still has this many."""
    forecast: Forecast
