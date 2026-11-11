"""Things the figure holds or leaves behind, composed from Time Fantasy pieces or drawn at 1x in the pack's tones and
scaled with NEAREST so they sit in the art's pixel grain: the book, the flint, the root on a stick, the felled birch.
Colour follows the palette: what the player made or carries is warm, the found world is cool.
"""
from __future__ import annotations

import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

import kit

Rgba = tuple[int, int, int, int]
CHIP = (196, 188, 172, 255)
"""The Ashlands rocks' lightest grey: what a struck chip shows."""


def _pixels(rows: list[str], key: dict[str, Rgba]) -> Image.Image:
    """A 1x sprite from rows of key characters ('.' is clear), scaled to the scene's 2x."""
    return kit.up(kit.pixels(rows, key))


BOOK = ("hometown_TFcolor_update_8.24/_tfrecolor_8.24/1X/characters/!objects1.png", (66, 82, 79, 95))
"""Hometown's book object, the frame where it opens in a V: brown cover, pages up, its ribbon hanging below."""


def book() -> Image.Image:
    """The coat's book held open: the kit's open brown book."""
    sheet, box = BOOK
    return kit.up(kit.load(sheet).crop(box))


def flint() -> Image.Image:
    """Two stones on the ground, a core and the one that strikes it (the Ashlands' loose rocks, as the stones heap's),
    and a few chips that have flown off, in the rock's own lightest grey."""
    sheet = kit.load(kit.ASH_B)
    core, striker = (kit.tile(sheet, c, 2).crop(kit.tile(sheet, c, 2).getbbox()) for c in (0, 1))
    img = Image.new("RGBA", (core.width + striker.width + 2, core.height + 6))
    img.alpha_composite(core, (0, 6))
    img.alpha_composite(striker, (core.width + 2, img.height - striker.height))
    chip = Image.new("RGBA", (2, 2), CHIP)
    for x, y in ((8, 0), (18, 2), (24, 0)):
        img.alpha_composite(chip, (x, y))
    return img


def root_on_stick(rising: bool = False) -> Image.Image:
    """A stick held out over the coals with a root on its end, charring: in the Farm and Fort wood's ramp with its
    outline under each piece, as the kit draws a pole, the root's tip gone dark. It runs down to the right from the
    hands, or up to the right when `rising` (from the stool, which sits lower than the fire)."""
    if rising:
        root = ["." * 19 + ".rrm", "." * 18 + "lmmmmc", "." * 16 + "hlommmcc", "." * 16 + "oo.oooo"]
        stick = ["." * (2 * r) + "hloo" for r in range(7, -1, -1)] + ["oo"]
    else:
        stick = ["hl"] + ["." * (2 * r - 2) + "oohl" for r in range(1, 6)]
        root = ["." * 12 + "oohl.rrm..", "." * 14 + "oolmmmmc", "." * 16 + "ommmcc", "." * 17 + "oooo."]
    return _pixels(root + stick if rising else stick + root,
                   {"h": (199, 153, 92, 255), "l": (184, 126, 80, 255), "r": (157, 95, 62, 255),
                    "m": (92, 66, 45, 255), "o": (108, 60, 74, 255), "c": (53, 64, 72, 255)})


def seated(sprite: Image.Image) -> Image.Image:
    """The shadow under the feet taken off (a figure sitting on a seat casts none onto it): its dark navy rows, the
    sprite's bottom few pixels."""
    sprite = sprite.copy()
    px = sprite.load()
    assert px is not None
    for y in range(sprite.height - 10, sprite.height):
        for x in range(sprite.width):
            r, g, b, a = kit.rgba(px, x, y)
            if a and r < 70 and g < 78 and b < 92 and b >= r:
                px[x, y] = (0, 0, 0, 0)
    return sprite


TREES = Path(os.environ.get("TIME_FANTASY", os.path.expanduser("~/src/time-fantasy"))) / "curated/terrain"


def _birchen(piece: Image.Image, seed: int) -> Image.Image:
    """A dead trunk piece recoloured as birch: pale, cool, a dark mark every few pixels (the found world's wood)."""
    rng = random.Random(seed)
    grey = ImageOps.grayscale(piece.convert("RGB"))
    ramp = ImageOps.colorize(grey, black=(46, 50, 58), white=(222, 224, 218), mid=(160, 164, 166), blackpoint=40, whitepoint=190)
    out = ramp.convert("RGBA")
    out.putalpha(piece.getchannel("A"))
    px = out.load()
    assert px is not None
    for _ in range(piece.width * piece.height // 12):
        x, y = rng.randrange(piece.width), rng.randrange(piece.height)
        if kit.rgba(px, x, y)[3] and kit.rgba(px, x, y)[0] > 110:
            for dx in range(3):
                if x + dx < piece.width and kit.rgba(px, x + dx, y)[3]:
                    px[x + dx, y] = (50, 52, 58, 255)
    return ImageEnhance.Contrast(out).enhance(1.0)


def _warm_cut(piece: Image.Image, edge: str, depth: int = 2) -> Image.Image:
    """The sawn end of a trunk or stump: the made thing's warm pale wood, as a few columns/rows at one edge."""
    out = piece.copy()
    px = out.load()
    assert px is not None
    w, h = out.size
    for y in range(h):
        for x in range(w):
            if not kit.rgba(px, x, y)[3]:
                continue
            near = {"left": x, "top": y, "right": w - 1 - x}[edge]
            if near < depth:
                px[x, y] = (214, 178, 128, 255) if (x + y) % 3 else (190, 150, 104, 255)
    return out


def felled_birch() -> tuple[Image.Image, Image.Image]:
    """(the trunk lying on the ground, the stump left standing): the dead-tree sheet's upright trunk turned onto its
    side and its low stump, recoloured as birch, their cut ends warm."""
    sheet = Image.open(TREES / "terrain_muspelheim_dead_tree_small.png").convert("RGBA")
    bole = sheet.crop((16, 9, 23, 30)).transpose(Image.Transpose.ROTATE_90)
    log = Image.new("RGBA", (bole.width + 14, bole.height))
    log.alpha_composite(bole, (14, 0))
    log.alpha_composite(bole, (0, 0))
    log = log.transpose(Image.Transpose.FLIP_LEFT_RIGHT)       # the sawn end toward the stump on the right
    stump = sheet.crop((2, 38, 11, 50))
    trunk = kit.up(_warm_cut(_birchen(log, 3), "right"))
    stump = kit.up(_warm_cut(_birchen(stump, 5), "top"))
    return trunk, stump


def figure_shadow(width: int) -> Image.Image:
    """A soft dark oval under a lying thing (the trunk has none of its own)."""
    img = Image.new("RGBA", (width, 10))
    ImageDraw.Draw(img).ellipse((0, 0, width - 1, 9), fill=(14, 16, 22, 90))
    return img
