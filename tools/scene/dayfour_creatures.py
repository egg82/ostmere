"""The animals combat brings into the camp (content/team/combat-open.md, C9), each a Time Fantasy frame: the wolf is
the Monsters pack's white wolf, darkened to a grey pelt, the fat rat its grey small animal, the crows the Animals 2 vulture's perched frame with
its pink head and yellow beak turned to feather grey. Grimed to the world's cool tones, trimmed and stood on a spot.
Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import kit
from place import canvas, put

WOLF = "tf_monsters_assetpack/tf_monsters_assetpack/TimeFantasy_Monsters/1x/monster_wolf1.png"
SMALL = "animals1_shadowless/shadowless/animals2_shadowless.png"
VULTURE = "TimeFantasyAnimals2/TimeFantasyAnimals2/1x/vulture_sit.png"
WORLD = kit.Grade(sat=0.35, mul=(0.95, 1.0, 1.06), bright=0.8, contrast=1.05)
"""Beasts of the found world: drained, cool and a shade dark."""
PELT = kit.Grade(sat=0.25, mul=(0.9, 0.95, 1.05), bright=0.5, contrast=1.1)
"""The white wolf's coat taken to a dark grey, its red eyes kept."""
FACING = {"down": 0, "left": 1, "right": 2, "up": 3}


def _frame(sheet: str, cell: tuple[int, int], facing: str, col: int = 1) -> Image.Image:
    """One frame of a 3-column, 4-facing animal block at the sheet's top left, at 1x."""
    x, y = col * cell[0], FACING[facing] * cell[1]
    return kit.load(sheet).crop((x, y, x + cell[0], y + cell[1]))


def _stood(sprite: Image.Image, feet: tuple[float, float]) -> Image.Image:
    box = sprite.getchannel("A").getbbox()
    assert box is not None
    sprite = sprite.crop(box)
    img = canvas()
    put(img, sprite, feet[0] - sprite.width / 2, feet[1] - sprite.height)
    return img


def wolf(facing: str, feet: tuple[float, float], coat: kit.Grade = PELT) -> Image.Image:
    """The Monsters pack's wolf at its own grain (lean, long-legged, ears up), in a dark grey pelt unless `coat` says
    otherwise."""
    return _stood(kit.grade(_frame(WOLF, (65, 66), facing), **coat), feet)


def rat(facing: str, feet: tuple[float, float]) -> Image.Image:
    """The grey small animal, a quarter narrower than at 2x and as tall as it was: stout, not long."""
    src = kit.grade(kit.up(_frame(SMALL, (42, 36), facing)), **WORLD)
    box = src.getchannel("A").getbbox()
    assert box is not None
    src = src.crop(box)
    return _stood(kit.resize(src, (src.width * 3 // 4, src.height)), feet)


def _feathered(sprite: Image.Image) -> Image.Image:
    """The pink head and yellow beak recoloured to the body's own grey."""
    out = sprite.copy()
    px = out.load()
    assert px is not None
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = kit.rgba(px, x, y)
            if a and r > b + 40:
                px[x, y] = (46, 48, 56, a) if g < 150 else (96, 96, 90, a)
    return out


def crow(facing: str, feet: tuple[float, float]) -> Image.Image:
    """The perched vulture turned crow, at 1x (a bird a third the height of a person)."""
    src = _frame(VULTURE, (42, 36), facing, col=0)
    return _stood(kit.grade(_feathered(src), **WORLD), feet)
