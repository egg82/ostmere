from pydantic import BaseModel

from .goal_models import GoalRow


class StoreNet(BaseModel):
    store: str
    per_hour: int
    """The store's net per hour (rate units) under the mix, unclamped."""


class MixRow(BaseModel):
    """One saved mix of the player's own as if it ran from now (contract/mix-rows.txt, "Mix rows")."""

    id: str
    goals: list[GoalRow]
    """The same rows as View.goal_rows, under this mix."""
    nets: list[StoreNet]
    """One per ledger line, in ledger order."""
    runs_out_at: int | None
    """Game time the mix stops for want of a store; null when it runs indefinitely (View.runs_out_at)."""


class MixBest(BaseModel):
    """The earliest landing the player's own saved mixes gave a goal, as projected when each was saved."""

    goal: str
    """The goal's key: kind, store, skill and target, joined with '|' (the same fields as the GoalRow)."""
    mix_id: str
    """The mix that set it, by the name it had then."""
    lands_at: int
    """Game time the goal was projected to land under it, as set when it was saved."""
    saved_at: int
    """Game time the mix was saved."""


class MixRows(BaseModel):
    at: int
    rows: list[MixRow]
    best: list[MixBest]
