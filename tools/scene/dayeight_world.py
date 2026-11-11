"""Days eight and nine's found world, cool and drawn in its final colours: the Drift's heavy ash, ash heaped on the
roofs, fungus shelves on the dead birch, the pack at the gap, the line scored in the ash where the wall will go, and
smoke on the road beyond the ridge.
Pieces are Time Fantasy's: the wolf is week 1's (dayfour_creatures), the shelves and caps the Caves and Mines cave
plants. Drawn are the ash and the smoke, which the kit has no sprite for, at the art's 1x grain as day one's fog is.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

import dayfour_creatures as beasts
import kit
from daytwo import cut
from dayone_world import behind, blank_mask, soft
from place import H, W, canvas, put

SEED = 89
CAVE = "cavesandmines_TFcolor_update_8.24/_tfrecolor_8.24/1X/tilesets/tileB_cave1.png"
SHELVES = [(66, 148, 78, 153), (81, 151, 96, 157), (96, 150, 111, 158)]
"""The cave plants' brown bracket fungi."""
CAPS = [(70, 114, 79, 121), (82, 117, 93, 126)]
"""The cave plants' tan mushroom clusters."""
FUNGUS = kit.Grade(sat=0.55, mul=(1.08, 1.0, 0.86), bright=1.25, contrast=1.05)
"""Pale ochre shelves, lighter than the bark they grow on."""
ASH_CAP = ((206, 200, 190, 255), (178, 172, 164, 255))
"""The ash lying on a roof: its top and its shaded lower edge."""
WOLVES = [("right", (256, 142)), ("down", (276, 137)), ("down", (298, 139)), ("left", (322, 143))]
"""The pack at the gap: four of week 1's wolf, beyond the camp's back line, facing in."""
WOLF_SCALE = 0.75
"""Beyond the back line they are a little smaller than the wolves that came to the light's edge."""
LINE = [[(392, 145), (424, 143), (452, 146), (480, 144)], [(252, 147), (276, 149), (300, 148), (328, 146)]]
"""Where the line is scored: along the rim past the wall stub, and across the gap."""
SMOKES = [(296, 100), (318, 103), (342, 99)]
"""Where each fire's smoke rises, beyond the ridge on the road."""


def drift_ash() -> Image.Image:
    """Ash coming down thick: the always-on specks again, more of them and some two high."""
    img = kit.ash((W, H), 1300, (190, 178, 160), SEED)
    d = ImageDraw.Draw(img)
    r = random.Random(SEED)
    for _ in range(260):
        x, y = r.randrange(W), r.randrange(H)
        d.line((x, y, x, y + 1), fill=(200, 188, 170, r.choice((110, 170))))
    return img


def roof_ash(roof: Image.Image, depth: int = 2) -> Image.Image:
    """Ash heaped along a roof's top edge, at the 1x grain: each column's top `depth` pixels and, here and there, one
    above."""
    small = kit.resize(roof, (W // 2, H // 2))
    alpha = small.getchannel("A")
    box = alpha.getbbox()
    out = Image.new("RGBA", small.size)
    if box is None:
        return kit.up(out)
    a, px = alpha.load(), out.load()
    assert a is not None and px is not None
    r = random.Random(SEED + box[0])
    for x in range(box[0], box[2]):
        top = next((y for y in range(box[1], box[3]) if a[x, y]), None)
        if top is None:
            continue
        for k in range(depth):
            if top + k < box[3] and a[x, top + k]:
                px[x, top + k] = ASH_CAP[k == depth - 1]
        if top > 0 and r.random() < 0.45:
            px[x, top - 1] = ASH_CAP[0]
    return kit.up(out)


def shelf(box: tuple[int, int, int, int]) -> Image.Image:
    return kit.up(kit.grade(cut(CAVE, box), **FUNGUS))


def fungus(log: Image.Image, stump: Image.Image) -> Image.Image:
    """Shelves along the felled birch's top and up the stump's side, and caps at their feet."""
    out = canvas()
    shelves, caps = [shelf(b) for b in SHELVES], [shelf(b) for b in CAPS]
    lb, sb = log.getchannel("A").getbbox(), stump.getchannel("A").getbbox()
    assert lb is not None and sb is not None
    span = lb[2] - lb[0]
    for i, f in enumerate((0.08, 0.38, 0.66)):
        s = shelves[i]
        put(out, s, lb[0] + f * span, lb[1] - s.height // 2)
    put(out, shelves[1], sb[0] - 4, sb[1] + 4)
    put(out, caps[0], lb[0] + span * 0.5, lb[3] - caps[0].height + 2)
    put(out, caps[1], sb[2] - 6, sb[3] - caps[1].height + 2)
    return out


def wolves_at_gap(walls: Image.Image) -> Image.Image:
    img = canvas()
    for facing, feet in WOLVES:
        wolf = beasts.wolf(facing, feet)
        box = wolf.getchannel("A").getbbox()
        assert box is not None
        piece = wolf.crop(box)
        piece = kit.resize(piece, (round(piece.width * WOLF_SCALE), round(piece.height * WOLF_SCALE)))
        put(img, piece, feet[0] - piece.width / 2, feet[1] - piece.height)
    return behind(img, walls)


def scored_line() -> Image.Image:
    """A dark furrow in the pale ash, one art pixel wide, broken where the stick lifted."""
    img = Image.new("RGBA", (W // 2, H // 2))
    d = ImageDraw.Draw(img)
    r = random.Random(SEED)
    for run in LINE:
        pts = [(x // 2, y // 2) for x, y in run]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            for x in range(x0, x1):
                if r.random() < 0.9:
                    y = round(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
                    d.point((x, y), fill=(58, 56, 62, 200))
    return kit.up(img)


def road_smoke(walls: Image.Image) -> Image.Image:
    """Low smoke from more than one fire beyond the ridge, leaning the way the wind goes, faint in the brown."""
    m, d = blank_mask()
    r = random.Random(SEED + 1)
    for x0, y0 in SMOKES:
        x = x0 / 2
        for k in range(9):
            y = y0 / 2 - 2 - k * 3
            rr = 1.2 + k * 0.4
            x += r.uniform(0.4, 1.4)
            d.ellipse((x - rr, y - rr * 0.8, x + rr, y + rr * 0.8), fill=240 - k * 22)
    return behind(soft(m, 0.8, (70, 130, 190), (164, 156, 146)), walls)
