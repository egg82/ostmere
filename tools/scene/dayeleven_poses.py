"""Day eleven's figures: the family of four at the gate and the man who came behind them sitting apart; the player and
the woman at the hut; the three at the fire once joined, the child beside the woman; him lying wrapped on the far side,
then covered; the guard at the gap with the spear; the husband walking the ring. The three adults and the man are day
nine's picks (`dayeight_poses`); the child is the core pack's dark-haired boy, never posed working. Lying is the bed
sprites' convention, as Lucy's sleep is.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

import kit
import props
from daythree_poses import AT_GAP, laying
from dayeight_poses import BROTHER, HUSBAND, STRANGER, WOMAN
from dayfour_poses import spear
from dayone_poses import build_at, drab, outlined
from daytwo import bedroll
from daytwo_poses import Who, person
from figures import stand
from place import canvas, put

CHILDREN = "elements_core_pack_2.14.24/premade/100/with_shadow/e_childrenA_shadow.png"
CHILD = 4
"""The sheet's fifth child: dark hair, a plain brown shirt and trousers."""
AT_GATE = {"woman": (WOMAN, 320, 158), "husband": (HUSBAND, 342, 157), "brother": (BROTHER, 364, 158)}
"""Where each waits inside the gate, right of the gap fire, in front of the woodstack."""
CHILD_AT_GATE = (303, 160)
"""The child at the woman's side."""
SITS_APART = (230, 170)
"""Where the man sits, left of the gap fire, away from them."""
HUT_WORK = (416, 170)
"""Where the hut is worked from: its left, facing it."""
BY_FIRE = {"woman": (262, 287), "husband": (384, 286), "brother": (410, 284)}
"""The three at the fire: her on its near side with her back to us, the men past the stool."""
CHILD_BY_FIRE = (281, 287)
LIES = (108, 158)
"""His bedroll's top-left: the far side of the camp from them, under the rack, above the larder."""
GUARD = (AT_GAP[0] - 4, AT_GAP[1] + 10)
"""The guard: in the gap's mouth beside the gap fire, facing out, low enough that the spear clears the story strip."""
RING_WALK = (403, 156)
"""The husband at the palisade's first stretch, a hand on its posts."""
SPEAR = kit.Grade(sat=0.3, mul=(1.0, 1.0, 1.0), bright=1.6, contrast=1.2)
"""The spear lifted pale, so the shaft holds against the palisade's wood behind it at phone width."""


def _child(facing: str, drop: int = 0) -> Image.Image:
    """One frame of the children's sheet (16 x 32 cells, eight children in a 4 x 2 block), upscaled; `drop` rows cut
    off the bottom with the rest moved down, as `kit.walker` sits a frame."""
    x = (CHILD % 4) * 48 + 16
    y = (CHILD // 4) * 128 + kit.SHEET_FACING[facing] * 32
    frame = kit.load(CHILDREN).crop((x, y, x + 16, y + 32 - drop))
    out = Image.new("RGBA", (16, 32))
    out.alpha_composite(frame, (0, drop))
    return kit.up(out)


def _kid(facing: str, feet: tuple[float, float], drop: int = 0) -> Image.Image:
    return outlined(drab(stand(_child(facing, drop), feet)))


def at_gate(who: str) -> Image.Image:
    sheet, x, feet = AT_GATE[who]
    return person(sheet, "down", (x, feet))


def child_at_gate() -> Image.Image:
    return _kid("down", CHILD_AT_GATE)


def sitting_apart() -> Image.Image:
    """Sat on the ground, hood up, facing the camp."""
    return person(STRANGER, "down", SITS_APART, drop=7)


def building_hut() -> Image.Image:
    return build_at(HUT_WORK, flip=True)


def n5_building_hut() -> Image.Image:
    return laying(WOMAN, HUT_WORK, "right")


def by_fire(who: str) -> Image.Image:
    sheet, facing, drop = {"woman": (WOMAN, "up", 7), "husband": (HUSBAND, "left", 7), "brother": (BROTHER, "left", 0)}[who]
    return person(sheet, facing, BY_FIRE[who], drop=drop)


def child_by_fire() -> Image.Image:
    return _kid("up", CHILD_BY_FIRE, drop=5)


def _head(who: Who) -> Image.Image:
    head = drab(kit.walker(*who, "up"))
    box = head.getchannel("A").getbbox()
    assert box is not None
    return head.crop((box[0], box[1], box[2], box[1] + 22)).transpose(Image.Transpose.ROTATE_90)


def lying() -> Image.Image:
    """Wrapped in a bedroll, the back of his hood on the pillow end, as Lucy sleeps."""
    roll, head = bedroll(), _head(STRANGER)
    img = canvas()
    put(img, props.figure_shadow(roll.width + 4), LIES[0] - 2, LIES[1] + roll.height - 7)
    put(img, roll, LIES[0], LIES[1])
    put(img, head, LIES[0] - 6, LIES[1] + (roll.height - head.height) / 2 - 2)
    return img


def covered() -> Image.Image:
    """The same bedroll drawn up over his head: its blanket carried past the pillow end."""
    roll = bedroll()
    cloth = roll.crop((roll.width // 3, 0, roll.width // 3 + 10, roll.height))
    img = canvas()
    put(img, props.figure_shadow(roll.width + 10), LIES[0] - 8, LIES[1] + roll.height - 7)
    put(img, roll, LIES[0], LIES[1])
    put(img, cloth, LIES[0] - 6, LIES[1])
    return img


def guarding(who: Who) -> Image.Image:
    """At the gap with the spear upright at his side, head up, his back to the camp."""
    tool = spear().rotate(150, expand=True, resample=Image.Resampling.NEAREST)
    box = tool.getchannel("A").getbbox()
    assert box is not None
    tool = kit.grade(tool.crop(box), **SPEAR)
    return person(who, "up", GUARD, held=[(tool, 7, -tool.height - 18)])


def walking_ring() -> Image.Image:
    """Along the palisade, side on, a hand out to its posts."""
    return person(HUSBAND, "left", RING_WALK, col=0)

