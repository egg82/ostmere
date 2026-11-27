"""Wire models of what the player keeps doing by hand (Step.repeats; contract/repeats.txt, "Repeats"); the conventions in
models.py hold here."""
from pydantic import BaseModel


class RepeatedTap(BaseModel):
    """A hands card tapped `count` times in the window while the hands ran a mix without it (contract/repeats.txt,
    "Repeats")."""

    card: str
    count: int


class RepeatedSwitch(BaseModel):
    """The player's own mix switched to `mix_id` `count` times in the window while `chip` showed (contract/repeats.txt,
    "Repeats")."""

    chip: str
    mix_id: str
    count: int


class Repeats(BaseModel):
    """What the player keeps doing by hand, counted from the save's decision log: only what reached its count."""

    taps: list[RepeatedTap]
    switches: list[RepeatedSwitch]
