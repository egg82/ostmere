"""Day twenty-nine's figures: n2 crouched on the hall's shingles with day three's shovel, and n14 sat at the fire with
the fiddle and a cloth across his knee. The fiddle is Farm and Fort's lute icon at the kit's 1x grain; the cloth is day
four's hide in the camp's wood grade. Everything else is a frame the camp's people already use.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageOps

from cast.people_moments import ARRIVALS
from day_four.dayfour_made import hide
from day_three.daythree_poses import N2, shovel
from day_two.daytwo import cut
from day_two.daytwo_poses import Who, person
from draw import kit
from draw.kit import T
from draw.place import FIRE

ON_THE_ROOF = (650, 166)
"""n2's feet on the hall's lower shingles, left of the chimney (the hall stands at x 632-760, its eave at y 170)."""
ROOF_CROUCH = 8
"""Rows cut off his frame: crouched on the slope, so his head stays under the story strip's clearance."""
FIDDLER_AT = (FIRE[0] - 1.5 * T, FIRE[1] + 1.4 * T)
"""n14's seat at the fire's near left, between whoever sits apart and the hearth crew's place, facing in."""
LUTE = ("tf_farmandfort/IconSet/tf_icon_16.png", (48, 224, 64, 240))
"""Farm and Fort's lute icon (row 14, fourth): the one stringed instrument the kit draws."""


def n2_on_the_roof() -> Image.Image:
    tool = shovel()
    return person(N2, "down", ON_THE_ROOF, drop=ROOF_CROUCH, held=[(tool, 8, -tool.height + 4)])


def _fiddle() -> Image.Image:
    return kit.grade(cut(*LUTE), sat=0.6, mul=(1.0, 0.95, 0.88), bright=0.95, contrast=1.05)


def fiddling(who: Who, facing: str, feet: tuple[float, float], seated: bool = True) -> Image.Image:
    """A person playing: the fiddle up at the shoulder and, sat, the cloth it was wrapped in across the knee."""
    fiddle = _fiddle() if facing == "left" else ImageOps.mirror(_fiddle())
    held = [(fiddle, 4 if facing != "left" else -fiddle.width - 4, -fiddle.height - (22 if seated else 34))]
    if seated:
        cloth = kit.resize(hide(), (hide().width * 2 // 5, hide().height // 4))
        held.insert(0, (cloth, 0, -cloth.height - 8))
    return person(who, facing, feet, drop=7 if seated else 0, held=held)


def n14_fiddling() -> Image.Image:
    return fiddling(ARRIVALS["n14"], "right", FIDDLER_AT)
