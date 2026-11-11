"""The camp's rim: the broken edge where the floor ends and the low ground begins, and the crumbled coping and loose
stones that sit along it. `edge` gives one row per column; the low ground, the haze and the coping all end on it."""
from __future__ import annotations

import random

from PIL import Image

import kit
from place import LIP, W, canvas, put

WALL_FOOT = 146
"""The row the walls stand on: under a wall the edge never drops below it, or the low ground shows under the wall."""
SEED = 11
STONES = [(0, 2), (1, 2), (2, 2), (0, 4), (0, 5), (3, 2)]
"""Loose rocks on the pack's ash sheet, (column, row) in tiles."""
TUFTS = [(0, 1), (1, 1), (2, 1), (3, 1)]
"""Dead red scrub on the same sheet."""


def _profile(rng: random.Random) -> list[int]:
    """The edge's offset from LIP at every column: runs of 2 to 9 columns at one height, now and then a bite up into
    the low ground or a jut down over the floor."""
    out: list[int] = []
    level = 0
    while len(out) < W:
        run = rng.randint(2, 9)
        step = rng.choice([-3, -2, -1, 1, 2, 3])
        level = max(-5, min(4, level + step))
        roll = rng.random()
        shown = level - 4 if roll < 0.12 else level + 3 if roll > 0.9 else level
        out += [max(-7, min(6, shown))] * run
    return out[:W]


def solid_columns(walls: Image.Image) -> list[bool]:
    """Which columns have wall standing just above its foot."""
    px = walls.load()
    assert px is not None
    return [kit.rgba(px, x, WALL_FOOT - 1)[3] > 0 for x in range(W)]


def edge(walls: Image.Image) -> list[int]:
    """The rim's row at every column: uneven everywhere, and no lower than the walls' foot where a wall stands."""
    solid = solid_columns(walls)
    return [min(int(LIP) + off, WALL_FOOT) if solid[x] else int(LIP) + off
            for x, off in enumerate(_profile(random.Random(SEED)))]


def _coping_strip() -> Image.Image:
    a5 = kit.load("tf_ashlands/2x_RMVX/tf_A5_ashlands_2.png")
    return a5.crop((16, 272, 80, 284)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def _lay_segment(img: Image.Image, strip: Image.Image, rim: list[int], x: int, width: int, rng: random.Random) -> None:
    """One broken piece of coping: columns of the strip from a random start, each sitting on the rim at its own
    column, the whole piece a little proud of it or sunk, so no two neighbours line up."""
    start, sit = rng.randrange(strip.width), rng.choice([-2, -1, 0, 0, 1])
    for i in range(min(width, W - x)):
        col = strip.crop(((start + i) % strip.width, 0, (start + i) % strip.width + 1, strip.height))
        put(img, col, x + i, rim[x + i] + 2 + sit - strip.height)


def coping(rng: random.Random, rim: list[int]) -> Image.Image:
    """Coping laid along the rim in pieces of 5 to 18 columns, a fifth of them missing."""
    strip = _coping_strip()
    img = canvas()
    x = -rng.randrange(40)
    while x < W:
        width = rng.randint(5, 18)
        if x >= 0 and rng.random() > 0.2:
            _lay_segment(img, strip, rim, x, width, rng)
        x += width
    return img


def _open_columns(walls: Image.Image) -> list[int]:
    solid = solid_columns(walls)
    return [x for x in range(W) if not solid[x]]


def _sit(img: Image.Image, sprite: Image.Image, x: int, rim: list[int], sink: int) -> None:
    """The sprite's visible foot on the rim at x, `sink` rows over it onto the floor."""
    box = sprite.getbbox()
    if box is None:
        return
    put(img, sprite.crop(box), x - (box[2] - box[0]) // 2, rim[x] + sink - (box[3] - box[1]))


def _spread(rng: random.Random, spots: list[int], gap: int) -> list[int]:
    """Spots picked at random, none within `gap` columns of another."""
    picked: list[int] = []
    for x in rng.sample(spots, len(spots)):
        if all(abs(x - p) >= gap for p in picked):
            picked.append(x)
    return picked


def strewn(rng: random.Random, rim: list[int], walls: Image.Image) -> Image.Image:
    """A few rocks and tufts on or hanging over the rim, only where no wall hides them, none touching another."""
    sheet = kit.load(kit.ASH_B)
    img = canvas()
    for x in _spread(rng, _open_columns(walls), 26):
        c, r = rng.choice(STONES if rng.random() < 0.6 else TUFTS)
        small = kit.tile(sheet, c, r)
        if rng.random() < 0.5:
            small = small.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        _sit(img, small, x, rim, rng.choice([1, 2, 4, 6]))
    return img
