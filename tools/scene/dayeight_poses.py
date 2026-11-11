"""Days eight and nine's figures: the player raising the palisade's posts, her sorting caps on a cloth and working ash
into her ground, the old man twisting cord, and the four who come to the gate at B10, picked from Time Fantasy's
walking-character sheets (a woman in a green dress, a brown-haired man, a fair young man, and a hooded man who keeps
his face in shadow). The cloth is Farm and Fort's hide, the caps the cave plants', the cord the fort's braided rope.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

import dayeight_world as world
import dayfour_made as d4made
import kit
from dayfour_poses import N3, N3_BY_FIRE, N4, N4_BY_FIRE
from dayone_poses import build_at
from daytwo import cut
from daytwo_poses import Who, person
from kit import FORT, T
from place import canvas, put

SHEETS = "timefantasy_characters/timefantasy_characters/sheets/"
WOMAN: Who = (SHEETS + "npc2.png", 5)
"""A woman with brown hair in a plain green dress: the one who talks for them."""
HUSBAND: Who = (SHEETS + "npc1.png", 5)
"""A brown-haired man in a grey vest."""
BROTHER: Who = (SHEETS + "npc3.png", 2)
"""A fair-haired young man in a pale shirt."""
STRANGER: Who = (SHEETS + "chara2.png", 2)
"""A man in a grey hood, his face in its shadow."""
AT_GATE = [(STRANGER, 322, 146), (HUSBAND, 297, 147), (WOMAN, 284, 148), (BROTHER, 270, 147)]
"""Where each stands outside the gate, the stranger apart from the three."""
GATE_SCALE = 0.8
"""Beyond the camp's back line they are a little smaller than the people at the fire."""
RAISING = (13.6 * T, 4.95 * T)
"""Where the player works the palisade: inside the rim, at the stakes, by the stretch going up."""
ROPE = (234, 400, 244, 420)
"""A length of the fort's braided rope."""


def raising_posts() -> Image.Image:
    return build_at(RAISING)


def _cloth_of_caps() -> Image.Image:
    cloth = d4made.hide()
    cloth = kit.resize(cloth, (cloth.width, cloth.height // 2))
    caps = kit.up(kit.grade(cut(world.CAVE, world.CAPS[0]), **world.FUNGUS))
    out = cloth.copy()
    out.alpha_composite(caps, (4, 0))
    out.alpha_composite(caps, (12, 2))
    return out


def n3_sorting() -> Image.Image:
    """Crouched below the hearth at a cloth laid with the picked caps."""
    cloth = _cloth_of_caps()
    return person(N3, "right", N3_BY_FIRE, drop=9, held=[(cloth, 8, -cloth.height)])


def n4_twisting() -> Image.Image:
    """Seated below the hearth, a length of cord across his knees."""
    cord = cut(FORT, ROPE).rotate(80, expand=True, resample=Image.Resampling.NEAREST)
    return person(N4, "left", N4_BY_FIRE, drop=7, held=[(cord, -cord.width + 4, -18)])


def _far(who: Who, x: float, feet: float) -> Image.Image:
    sprite = person(who, "down", (x, feet))
    box = sprite.getchannel("A").getbbox()
    assert box is not None
    piece = sprite.crop(box)
    piece = kit.resize(piece, (round(piece.width * GATE_SCALE), round(piece.height * GATE_SCALE)))
    out = canvas()
    put(out, piece, x - piece.width / 2, feet - piece.height)
    return out


def at_the_gate() -> Image.Image:
    """The four outside the closed gate, facing in."""
    out = canvas()
    for who, x, feet in AT_GATE:
        out.alpha_composite(_far(who, x, feet))
    return out
