"""The end moment's two lights: the cracks in the cut floor glowing in rings round the slab the player woke on, and a
light on the far ridge that is not the player's fire. Both are screen-blended lights, drawn pre-grade, so they are
bright enough to survive the dusk grade's darkening and still read.

Palette: the glow is a dull deep red, a different red from the fire's orange (the fire is the player's, this is the
ground's own); the ridge light is a pale cool yellow-white, apart from the fire, because it is someone else's.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import kit

HALF = 2
"""Cracks are drawn at half size and scaled up with NEAREST, so a crack is as coarse as the art's own pixels."""
RING_RADII = (11, 22, 35, 50, 67)
"""Half-size x-radii of the rings round the slab; each ring is dimmer than the one inside it."""
RING_LEVEL = (255, 225, 190, 150, 110)
SQUASH = 0.46
"""The floor seen at a slant: a ring's height is this much of its width."""


def _arc_runs(rng: random.Random) -> list[tuple[float, float]]:
    """Broken arcs round a circle: runs of crack with gaps between, as (start, end) angles."""
    runs: list[tuple[float, float]] = []
    a = rng.uniform(0, math.tau)
    end = a + math.tau
    while a < end:
        run = rng.uniform(0.7, 1.9)
        runs.append((a, min(a + run, end)))
        a += run + rng.uniform(0.12, 0.45)
    return runs


def _draw_ring(d: ImageDraw.ImageDraw, rng: random.Random, c: tuple[float, float], radius: float, level: int) -> None:
    for a0, a1 in _arc_runs(rng):
        wobble = 0.0
        prev: tuple[float, float] | None = None
        a = a0
        while a <= a1:
            wobble = max(-2.5, min(2.5, wobble + rng.uniform(-1.1, 1.1)))
            r = radius + wobble
            p = (c[0] + r * math.cos(a), c[1] + r * SQUASH * math.sin(a))
            if prev:
                d.line((prev, p), fill=level)
            prev = p
            a += 0.09


def _draw_spokes(d: ImageDraw.ImageDraw, rng: random.Random, c: tuple[float, float]) -> None:
    """A few cracks running across the rings, from one ring to the next, jagged."""
    for k in range(len(RING_RADII) - 1):
        for _ in range(rng.choice((2, 3))):
            a = rng.uniform(0, math.tau)
            r0, r1 = RING_RADII[k], RING_RADII[k + 1]
            x, y = c[0] + r0 * math.cos(a), c[1] + r0 * SQUASH * math.sin(a)
            steps = 5
            for i in range(1, steps + 1):
                r = r0 + (r1 - r0) * i / steps
                a += rng.uniform(-0.12, 0.12)
                nx, ny = c[0] + r * math.cos(a) + rng.uniform(-1, 1), c[1] + r * SQUASH * math.sin(a) + rng.uniform(-1, 1)
                d.line(((x, y), (nx, ny)), fill=RING_LEVEL[k + 1])
                x, y = nx, ny


def crack_mask(size: tuple[int, int], centre: tuple[float, float], floor_y: float, seed: int) -> Image.Image:
    """The cracks as an L mask at full size: crisp lines, nothing above the wall's foot (they run under it)."""
    rng = random.Random(seed)
    small = Image.new("L", (size[0] // HALF, size[1] // HALF), 0)
    d = ImageDraw.Draw(small)
    c = (centre[0] / HALF, centre[1] / HALF)
    for radius, level in zip(RING_RADII, RING_LEVEL):
        _draw_ring(d, rng, c, radius, level)
    _draw_spokes(d, rng, c)
    mask = kit.resize(small, size)
    fade = Image.new("L", size, 255)
    fd = ImageDraw.Draw(fade)
    for y in range(int(floor_y) - 14, int(floor_y)):
        fd.line(((0, y), (size[0], y)), fill=int(255 * (y - (floor_y - 14)) / 14))
    fd.rectangle((0, 0, size[0], int(floor_y) - 14), fill=0)
    return ImageChops.multiply(mask, fade)


def crack_glow(size: tuple[int, int], centre: tuple[float, float], floor_y: float, seed: int) -> Image.Image:
    """A light for a screen blend: the crack lines in a hot dull red, and a soft red haze the same shape round them."""
    lines = crack_mask(size, centre, floor_y, seed)
    haze = kit.point(lines.filter(ImageFilter.GaussianBlur(4)), lambda v: min(255, v * 3))
    wide = kit.point(lines.filter(ImageFilter.GaussianBlur(14)), lambda v: min(255, v * 4))
    rgba = Image.new("RGBA", size, (0, 0, 0, 0))
    for mask, colour, strength in ((wide, (130, 16, 10), 0.9), (haze, (196, 36, 22), 1.0), (lines, (226, 74, 48), 1.0)):
        layer = Image.new("RGBA", size, (*colour, 255))
        layer.putalpha(kit.point(mask, lambda v, s=strength: int(v * s)))
        rgba.alpha_composite(layer)
    return rgba


def ridge_light(size: tuple[int, int], at: tuple[float, float]) -> Image.Image:
    """A small steady light far off: a pale core with a thin halo, no flicker and no reach (it is a long way off)."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    halo = Image.new("L", size, 0)
    ImageDraw.Draw(halo).ellipse((at[0] - 11, at[1] - 11, at[0] + 11, at[1] + 11), fill=150)
    halo = halo.filter(ImageFilter.GaussianBlur(5))
    glow = Image.new("RGBA", size, (206, 200, 150, 255))
    glow.putalpha(halo)
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    x, y = int(at[0]) // 2 * 2, int(at[1]) // 2 * 2
    d.rectangle((x - 2, y - 2, x + 1, y + 1), fill=(244, 238, 196, 255))
    d.rectangle((x - 4, y, x + 3, y + 1), fill=(236, 230, 180, 150))
    return img
