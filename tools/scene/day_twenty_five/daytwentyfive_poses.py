"""Week four's figures at the camp fire and the stone: the player lying at the camp stone at first light (the battler's
down frame), and the town in a circle round the fire, standing (B21's ring) or sat (I13's night). The circle is the
kit's walking sheets of the people who are always there, each facing the fire; the poses key on their moments, never
on a lane. Nothing is drawn.

Story spoilers (content/team/week-four.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

from day_eight.dayeight_poses import WOMAN
from day_four.dayfour_poses import N3
from day_one.dayone_poses import N1
from day_three.daythree_poses import N2
from day_two.daytwo_poses import Who, person
from draw.figures import PLAYER_SHEET, figure
from draw.place import FIRE
from cast.people_layers import N23, STONE

WAKE_AT = (STONE[0], STONE[1] + 26)
"""The player's body on the ground just below the camp stone."""
AROUND: tuple[tuple[tuple[float, float], str], ...] = (
    ((FIRE[0] - 66, FIRE[1] + 18), "right"), ((FIRE[0] + 98, FIRE[1] + 14), "left"),
    ((FIRE[0] + 50, FIRE[1] + 78), "up"), ((FIRE[0] + 88, FIRE[1] + 76), "up"),
    ((FIRE[0] - 28, FIRE[1] + 78), "up"), ((FIRE[0] + 10, FIRE[1] + 80), "up"),
)
"""Feet round the fire, each facing it: its two sides (the right past the stew pot and the stool), then the front row
right of middle (the second on the stump), then its left and middle. Behind it is the hearth's wall, and the front's far
left is Sorrel's, who stands apart there."""
RING: tuple[Who, ...] = (N2, N3, WOMAN, N1, PLAYER_SHEET, N23)
"""B21's ring: the bedesman leading at the front, the player, and the camp's first people."""
SAT: tuple[Who, ...] = (N1, N3, N2, PLAYER_SHEET)
"""I13's night: the town sat round the fire, the front's left and middle left to the bedesman standing."""


def _circle(whos: tuple[Who, ...], drop: int) -> list[tuple[Image.Image, bool]]:
    """One figure each, so each stands at its own depth among the things round the fire, and whether it stands in front
    of the fire's light and the hearth's front (the front row, as the bedesman saying the names does)."""
    return [(person(who, facing, feet, drop=drop), feet[1] > FIRE[1] + 60) for who, (feet, facing) in zip(whos, AROUND)]


def ring_at_fire() -> list[tuple[Image.Image, bool]]:
    return _circle(RING, 0)


def sat_at_fire() -> list[tuple[Image.Image, bool]]:
    return _circle(SAT, 9)


def wake_at_stone() -> Image.Image:
    return figure("dead", WAKE_AT)
