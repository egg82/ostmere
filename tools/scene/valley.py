"""The land past the wall, drawn as lower ground seen from the camp's rim: a stone lip at the wall's foot, a pale haze
rising from below it that hides the near valley, the low ground starting further up and going cooler and hazier with
distance, a far slope above a crest, and small trees, two of them a step bigger, their bases lost in the haze. Everything
cool and neutral; what the camp's own floor is stays in parts.py."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import kit
from kit import T
import rim
from place import CREST, H, LIP, W, canvas, put

HAZE = (104, 112, 124)
"""The distance colour, cool grey-blue; the further the ground, the more of it."""
FLOOR = kit.Grade(sat=0.35, mul=(0.9, 1.0, 1.12), bright=0.72, contrast=0.7)
"""The low ground: darker and cooler than the camp's floor, so it does not read as the same ground continuing."""
TREES = kit.Grade(sat=0.3, mul=(0.9, 1.0, 1.12), bright=0.8, contrast=0.7)
"""Far trees: a step lighter than the slope they stand against, so they show as shapes in the haze."""
SLOPE = kit.Grade(sat=0.3, mul=(0.88, 0.98, 1.14), bright=0.5, contrast=0.7)
"""The far slope above the crest: darker again."""


NEAR, FAR = 0.15, 0.6
"""How much of the haze colour the low ground takes at the lip and at the crest: the further, the hazier."""


HAZE_BAND = 26
"""How many rows above the lip the rim haze rises; the first HAZE_SOLID of them hide the ground entirely."""
HAZE_SOLID = 6
CREST_BASE = int(CREST + 8)
"""The row the haze steps from the floor's to the slope's."""


def _crest_y(x: float) -> float:
    """The crest's height at x: a long low line, a little uneven."""
    return CREST + 5 * math.sin(x / 41) + 3 * math.sin(x / 17 + 1)


def _floor(rng: random.Random, grade: kit.Grade) -> Image.Image:
    """The ash tiles laid half a tile off the camp's grid, so no seam or tile lines up with the camp floor's."""
    a5 = kit.load("tf_ashlands/2x_RMVX/tf_A5_ashlands_2.png")
    img = canvas()
    for r in range(-1, 6):
        for c in range(-1, 16):
            put(img, kit.tile(a5, rng.choice([1, 2, 3, 4, 5]), 1), c * T + T // 2, r * T + T // 2)
    return kit.grade(kit.calm(img, 0.7), **grade)


def _fade(img: Image.Image, top: float, bottom: float, y0: float, y1: float) -> Image.Image:
    """The image blended toward the haze colour, `top` at row y0 and `bottom` at row y1: further up is hazier."""
    ramp = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(ramp)
    for y in range(img.height):
        t = min(1.0, max(0.0, (y - y1) / (y0 - y1)))
        d.line(((0, y), (img.width, y)), fill=int(255 * (bottom + (top - bottom) * t)))
    fog = Image.new("RGBA", img.size, (*HAZE, 255))
    out = Image.composite(fog, img, ramp)
    out.putalpha(img.getchannel("A"))
    return out


def veil_at(y: float) -> float:
    """The haze on the low ground at row y, from the lip to the crest: what anything standing there with its foot on
    that row takes too, so it is as far as the ground it stands on."""
    return NEAR + (FAR - NEAR) * min(1.0, max(0.0, (y - LIP) / (CREST_BASE - LIP)))


OUTLINE = 70
"""Pixels darker than this (in luma) are a sprite's outline: they take half the haze, so a thing out in it keeps its
edge, as the packs draw far things, rather than going to a flat blob."""


def veiled(img: Image.Image, foot_y: float) -> Image.Image:
    """`img` blended toward the haze as the low ground is at its foot's row, its outline half as much."""
    fog = Image.new("RGBA", img.size, (*HAZE, 255))
    amount = veil_at(foot_y)
    out = Image.blend(img, fog, amount)
    edge = Image.blend(img, fog, amount / 2)
    out = Image.composite(edge, out, kit.point(img.convert("L"), lambda v: 255 if v < OUTLINE else 0))
    out.putalpha(img.getchannel("A"))
    return out


def lowland(rng: random.Random, rim_y: list[int]) -> Image.Image:
    """Low floor from the rim up to the crest, the far slope over it, each hazier toward the top."""
    below = _fade(_floor(rng, FLOOR), FAR, NEAR, CREST_BASE, LIP)
    above = _fade(_floor(rng, SLOPE), 0.55, 0.2, 0, CREST_BASE)
    cut = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(cut)
    for x in range(W):
        d.line(((x, 0), (x, int(_crest_y(x)))), fill=255)
    out = Image.composite(above, below, cut)
    for x, y in enumerate(rim_y):
        out.paste((0, 0, 0, 0), (x, y, x + 1, H))
    return out


def rim_haze(rim_y: list[int]) -> Image.Image:
    """Pale haze rising from the rim, densest behind it, following it column by column."""
    ramp = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ramp)
    fade = [int(255 * (1 - max(0.0, (i - HAZE_SOLID) / (HAZE_BAND - HAZE_SOLID))) ** 1.6) for i in range(HAZE_BAND)]
    for x, y in enumerate(rim_y):
        for i, a in enumerate(fade):
            d.point((x, y - 1 - i), fill=a)
    haze = Image.new("RGBA", (W, H), (*HAZE, 255))
    haze.putalpha(ramp)
    return haze


def drop(rng: random.Random, rim_y: list[int], walls: Image.Image) -> Image.Image:
    """The camp's floor ending: haze rising from below the rim, and broken coping with a few stones along it. It is
    its own layer at the rim (build's rim_haze), so it veils everything out on the low ground and nothing in camp."""
    edge = rim.coping(rng, rim_y)
    edge.alpha_composite(rim.strewn(rng, rim_y, walls))
    haze = rim_haze(rim_y)
    haze.alpha_composite(kit.grade(edge, sat=0.15, mul=(0.95, 1.0, 1.08), bright=0.8, contrast=1.0))
    return haze


def trees(rng: random.Random) -> Image.Image:
    """Small dead trees on the far slope and crest, washed into the haze; two a step bigger, standing on the low ground
below the rim with their bases under the rim haze, so they rise out of it rather than stand at camp level."""
    b = kit.load("tf_ashlands/2x_RMVX/tf_B_ashlands_2.png")
    far = canvas()
    for sprite, x, y in [(kit.tile(b, 0, 7, 1, 2), 5.0, 1.4), (kit.tile(b, 1, 7, 1, 3), 6.9, 0.5),
                         (kit.tile(b, 0, 7, 1, 2), 8.6, 1.2), (kit.tile(b, 1, 7, 1, 3), 9.9, 0.9),
                         (kit.tile(b, 0, 7, 1, 2), 11.0, 1.3), (kit.tile(b, 1, 7, 1, 3), 13.6, 0.7),
                         (kit.tile(b, 0, 7, 1, 2), 1.9, 1.1), (kit.tile(b, 4, 3), 7.7, 2.7), (kit.tile(b, 4, 3), 10.4, 2.9)]:
        put(far, sprite, x * T, y * T)
    for sprite, x, base in [(kit.tile(b, 2, 7, 2, 5), 5.4, LIP - 10), (kit.tile(b, 2, 7, 2, 5), 13.3, LIP - 10)]:
        small = kit.resize(sprite, (sprite.width * 11 // 20, sprite.height * 11 // 20))
        put(far, small, x * T, base - small.height)
    far = kit.grade(far, **TREES)
    return _fade(far, 0.55, 0.4, 0, int(LIP))
