"""Smoke from the pack: the thin curls of Time Fantasy's smoke effect sheet, stacked going up from a foot. Nothing is
drawn: a banked fire's smoke and the hall's chimney's are cut from the same sheet."""
from __future__ import annotations

from PIL import Image

import kit
from place import canvas, put

SHEET = "curated/living/effects/fx_smoke.png"
CELL = 64
"""The sheet's frames are 64 px cells; its second row (1) holds the thin curls, from the second cell on."""
CURLS = ((1, 1), (2, 1), (3, 1), (4, 1))
DRIFT = (0, 3, -2, 4)
"""Each curl's sideways step from the one below, so the stack leans and wavers rather than standing in a column."""


def _curl(n: int) -> Image.Image:
    col, row = CURLS[n % len(CURLS)]
    cell = kit.load(SHEET).crop((col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL))
    box = cell.getchannel("A").getbbox()
    assert box is not None
    return kit.up(cell.crop(box))


def plume(foot: tuple[float, float], curls: int) -> Image.Image:
    """`curls` of them rising from `foot` (the centre of the lowest one's bottom), each just above the last."""
    out = canvas()
    x, y = foot
    for n in range(curls):
        curl = _curl(n)
        x += DRIFT[n % len(DRIFT)]
        y -= curl.height
        put(out, curl, x - curl.width / 2, y)
        y -= 2
    return out
