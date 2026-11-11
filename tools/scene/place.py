"""Where things go in the scene: its size, a blank canvas, placing a sprite, and the named spots every module shares
(the fire, the gap, the seat, where the figure lies, works and rests)."""
from __future__ import annotations

from PIL import Image

from kit import T

W, H = 15 * T, 9 * T
FIRE = (8.5 * T, 6.95 * T)
"""The fire's centre: the ring, laid fire, flames, fireback and light all hang off it."""


def canvas() -> Image.Image:
    return Image.new("RGBA", (W, H))


def put(img: Image.Image, sprite: Image.Image, x: float, y: float) -> None:
    img.alpha_composite(sprite, (int(x), int(y)))


LIE = (1.75 * T, 4.75 * T)
"""Where the figure lies and gets up: its feet, under the roof, against the wall."""
GAP = (8.15 * T, 5.35 * T)
"""Where the figure comes back in with wood: through the wall's gap, to the heap."""
RUBBLE = (12.0 * T, 5.0 * T)
"""Where the figure picks through the ruin: crouched by the stones under the far wall stub."""
BY_FIRE = (FIRE[0] - 2.05 * T, FIRE[1] + 0.4 * T)
"""Where the figure kneels at the fire's left, facing it."""
SEAT = (FIRE[0] + 2.7 * T, FIRE[1] + 1.15 * T)
"""Where the figure's feet go when sat on the stool, at the fire's right."""
WALL_REST = (LIE[0] + 1.1 * T, LIE[1] + 0.3 * T)
"""Where the figure sits to rest: the roof's corner, back to the wall."""
SLAB = (1.9 * T, 5.1 * T)
"""The slab the player woke on: the centre of the glowing rings. The wall's foot, which the rings run under, is y 146."""
RIDGE = (9.1 * T, 3.15 * T)
"""The light on the ridge, seen through the gap in the wall."""
LIP = 4.5 * T
"""Where the camp's floor ends at the wall's foot: past it the ground is lower."""
CREST = 3.35 * T
"""The far crest across the low ground: the line the ridge light sits on."""
LOWEST_HEAD = 0.33 * H
"""The story strip lies along the art's top, so no figure's head may sit above this line (the strip's clearance)."""
