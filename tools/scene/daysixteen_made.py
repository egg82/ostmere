"""Days sixteen to nineteen's built thing: the road, cut from the camp up the far slope to the ridge, then over the top,
with the cloth strips on its marker stakes (the stream and its bridge lie on the low ground behind the wall stub, out of
sight). The cut is the Ashlands' scraped stone (the cleared ground's tiles) in a strip that narrows as it climbs, the
markers Farm and Fort's torn cloth on its pole; all of it as hazy as the slope it lies on, and cut away behind the
ruin's walls. Nothing is drawn.
Story spoilers (content/team/week-three.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageDraw

import kit
from dayone_world import behind
from kit import FORT, T
from place import canvas, put
from valley import on_slope

LINE = [(394, 110), (404, 96), (415, 82), (425, 66), (433, 50), (440, 34), (446, 18), (450, 6), (452, 0)]
"""The road's middle from where it climbs out of the low ground (behind the palisade) to the top of the art, which is
the ridge's top: it leans right and bends upright as it goes away."""
CUT = kit.Grade(sat=0.1, mul=(0.98, 1.0, 1.04), bright=1.45, contrast=0.85)
"""The cut's stone, paler than the cleared ground's: the ash scraped off it shows as a pale line from the camp."""
NEAR_HALF, FAR_HALF = 7.0, 1.0
"""Its half width at the foot of the line and at the top."""
STRETCHES = {"road_1": 88, "road_2": 72, "road_3": 56, "road_4": 40, "road_over_1": 20, "road_over_2": 0}
"""How far up each state reaches (the row its head is on): the road's four (its stages 3, 6, 8, 10), the head on the
ridge at the fourth, then the way over the top (its two)."""
CLOTH = (194, 388, 222, 442)
"""Farm and Fort's torn brown cloth on a pole (fortA): a marker stake with its strip."""
MARKERS = [(98, -1), (88, 1), (78, -1), (68, 1), (58, -1), (49, 1), (41, -1)]
"""Each marker's foot (its row on the road, and the side it stands: -1 left, 1 right), along the road's four states."""


def _at(y: float) -> tuple[float, float]:
    """The road's middle x and half width at row y."""
    for (x0, y0), (x1, y1) in zip(LINE, LINE[1:]):
        if y1 <= y <= y0:
            x = x0 + (x1 - x0) * (y0 - y) / (y0 - y1)
            t = (LINE[0][1] - y) / LINE[0][1]
            return x, NEAR_HALF + (FAR_HALF - NEAR_HALF) * t
    raise ValueError(f"row {y} is off the road")


def _stone() -> Image.Image:
    """The cleared ground's scraped stone over the whole art, in the cut's grade."""
    a5 = kit.load("tf_ashlands/2x_RMVX/tf_A5_ashlands_2.png")
    img = canvas()
    for r in range(img.height // T + 1):
        for c in range(img.width // T + 1):
            put(img, kit.tile(a5, 1 + (r + c) % 5, 0), c * T, r * T)
    return kit.grade(kit.calm(img, 0.6), **CUT)


def _strip(top: int) -> Image.Image:
    """The road's cut from its foot up to row `top`."""
    mask = Image.new("L", canvas().size, 0)
    d = ImageDraw.Draw(mask)
    for y in range(top, LINE[0][1] + 1):
        x, half = _at(y)
        d.line(((round(x - half), y), (round(x + half), y)), fill=255)
    out = canvas()
    out.paste(_stone(), (0, 0), mask)
    return out


def road(state: str, walls: Image.Image) -> Image.Image:
    """The road as far as `state` (a key of `STRETCHES`) reaches."""
    return behind(on_slope(_strip(STRETCHES[state])), walls)


def cloths(walls: Image.Image) -> Image.Image:
    """A strip of cloth tied to each marker stake along the road, smaller as the road goes away."""
    pole = kit.load(FORT).crop(CLOTH)
    out = canvas()
    for y, side in MARKERS:
        x, half = _at(y)
        h = round(4 + 6 * (y - MARKERS[-1][0]) / (MARKERS[0][0] - MARKERS[-1][0]))
        marker = kit.resize(pole, (max(2, round(h * pole.width / pole.height)), h))
        put(out, marker, x + side * (half + 2) - marker.width / 2, y - marker.height)
    return behind(on_slope(out), walls)
