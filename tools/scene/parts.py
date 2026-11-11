"""The scene's drawn parts: the ground, ruin, heaps, rack, stool, birch, the fire's pieces and the figures' carried
loads, each a full-canvas image built from the packs' tiles."""
from __future__ import annotations

import random
from collections.abc import Sequence

from PIL import Image, ImageChops, ImageOps

import kit
import props
import rim
import valley
from dayone_world import behind
from figures import Held, figure
from kit import ASH_B, FORT, T
from place import FIRE, H, LIP, SEAT, W, canvas, put
from tints import CLEARED, GROUND, STONE


def ground(rng: random.Random) -> Image.Image:
    """Grey ash over everything; here and there the stone shows through it."""
    a5 = kit.load("tf_ashlands/2x_RMVX/tf_A5_ashlands_2.png")
    img = canvas()
    for r in range(9):
        for c in range(15):
            stone = False
            put(img, kit.tile(a5, rng.choice([1, 2, 3, 4, 5]), 0 if stone else 1), c * T, r * T)
    return kit.grade(kit.calm(img, 0.6), **GROUND)


def shade() -> Image.Image:
    """The roof's shadow on the ground in front of the sheltered corner, and darkest just under the eave on the wall."""
    s = Image.new("RGBA", (W, H), (10, 8, 6, 255))
    a = kit.radial((W, H), (2.2 * T, 4.4 * T), 3.2 * T, 150, 0, squash=0.45)
    for i in range(6):
        a.paste(ImageChops.lighter(a.crop((ROOF_X[0], EAVE_Y + i, ROOF_X[1], EAVE_Y + i + 1)),
                                   Image.new("L", (ROOF_X[1] - ROOF_X[0], 1), 170 - i * 22)), (ROOF_X[0], EAVE_Y + i))
    s.putalpha(a)
    return s


WALL_Y = LIP + 2 - 58
"""The walls' top: their opaque foot (row 57 of the tile) lands on the coping's last row, so no strip shows below."""
DROP = (WALL_Y - 2.4 * T) / T
"""How far the walls and what hangs off them moved down, in tiles, from where the foot stood above the coping."""
EAVE = 10
"""How far the roof's eave stands out over the camp floor, in px. The roof comes that far down the wall's face, the wall
under it is in shadow and posts hold it up that far in front of the wall's foot (dayone.roof_posts), so it reads as
covering the corner where the figure lay, not as sloping away behind the wall (the packs' roofs are drawn from above)."""
EAVE_Y = round((2.5 + DROP) * T) + EAVE
"""The eave's line on the art: the roof's lowest row."""
ROOF_X = (round(-0.6 * T), round(4.4 * T))
"""The roof's left and right edges."""
FALLEN = [(5, 7.75 * T, (3.55 + DROP) * T), (4, 9.65 * T, (3.75 + DROP) * T), (1, 6.9 * T, (4.15 + DROP) * T),
          (5, 12.6 * T, (4.2 + DROP) * T)]
"""Stones come down off the walls: (column on the ash sheet's stone row, x, y), each a tile. The two in the gap lie
against its ends, so the track runs out through its middle clear of them."""


def ruin() -> Image.Image:
    """Walls, mostly, and a roof over one corner: the ruined-house wall fronts with a holed roof over the left end."""
    walls = kit.load("TimeFantasy_TILES_6.24.17/RPGMAKER/RMVX/tileC_HOUSE_ruined.png")
    roof = kit.load("TimeFantasy_TILES_6.24.17/RPGMAKER/RMVX/tileD_HOUSE_TOP_black.png")
    img = canvas()
    put(img, kit.tile(walls, 8, 1, 4, 2), 0, WALL_Y)             # wall under the roof, a hole knocked through
    put(img, kit.tile(walls, 8, 3, 4, 2), 4 * T, WALL_Y)         # the wall runs on, broken lower
    put(img, kit.tile(walls, 14, 1, 2, 2), 10.2 * T, WALL_Y)     # a stub past the gap, a plank still nailed on
    put(img, kit.tile(roof, 3, 1 - DROP, 5, 2.5 + DROP + EAVE / T), ROOF_X[0], 0)   # what is left of the roof, holed, its eave out over the floor
    rubble = kit.load("tf_ashlands/2x_RMVX/tf_B_ashlands_2.png")
    for c, x, y in FALLEN:
        put(img, kit.tile(rubble, c, 2), x, y)                    # stones come down off the walls
    for c, x, y in [(0, 3.2, 7.3), (5, 13.1, 7.6)]:
        put(img, kit.tile(rubble, c, 2), x * T, y * T)        # and some lie further out
    return kit.grade(img, **STONE)


def campfire_split(name: str) -> tuple[Image.Image, Image.Image]:
    """The pack's campfire split in two by colour: its grey stones (the ring) and the rest (the fire laid or lit)."""
    src = kit.curated(name)
    stones, rest = src.copy(), src.copy()
    sp, rp = stones.load(), rest.load()
    assert sp is not None and rp is not None
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = kit.rgba(sp, x, y)
            grey = a and max(r, g, b) - min(r, g, b) < 28
            if grey:
                rp[x, y] = (0, 0, 0, 0)
            else:
                sp[x, y] = (0, 0, 0, 0)
    return stones, rest


def at_fire(sprite: Image.Image, dx: float = 0, dy: float = 0) -> Image.Image:
    """The sprite centred on the fire, offset by (dx, dy) pixels, on a full canvas."""
    img = canvas()
    put(img, sprite, FIRE[0] - sprite.width / 2 + dx, FIRE[1] - sprite.height / 2 + dy)
    return img


def cleared(rng: random.Random) -> Image.Image:
    """Grey scraped back to stone: the stone tiles under the ring, cut to an oval with a dithered, ragged edge."""
    a5 = kit.load("tf_ashlands/2x_RMVX/tf_A5_ashlands_2.png")
    patch = canvas()
    for c in range(-3, 3):
        for r in range(-3, 2):
            put(patch, kit.tile(a5, rng.choice([1, 2, 3, 4, 5]), 0), FIRE[0] + c * T, FIRE[1] + r * T)
    mask = kit.radial(patch.size, (FIRE[0], FIRE[1] - 4), 3.3 * T, 255, 0, squash=0.66)
    noise = Image.frombytes("L", patch.size, bytes(rng.randrange(256) for _ in range(W * H)))
    edge = ImageChops.add(mask, Image.eval(noise, lambda v: v // 6))       # ragged: noise nudges the cut
    patch.putalpha(Image.eval(edge, lambda v: 255 if v > 120 else 0))
    return kit.grade(kit.calm(patch, 0.6), **CLEARED)


def fireback() -> Image.Image:
    """Stones stacked at the fire's back: the pack's loose rocks, piled in a low arc behind the ring."""
    b = kit.load("tf_ashlands/2x_RMVX/tf_B_ashlands_2.png")
    img = canvas()
    courses = [(-34, -40, [0, 3, 0, 3, 0]), (-25, -48, [3, 0, 3, 0]), (-16, -56, [0, 3, 0])]
    for x0, dy, row in courses:
        for i, c in enumerate(row):
            put(img, kit.tile(b, c, 2), FIRE[0] - T / 2 + x0 + i * 17, FIRE[1] - T / 2 + dy)
    return img


def wood_drying() -> Image.Image:
    """Damp wood laid to dry: sticks propped against the wall at the roof's edge, a heap beside them."""
    fort = kit.load("tf_farmandfort/rpgmaker_VXa/tileB_fortA.png")
    img = canvas()
    put(img, kit.tile(fort, 10, 1), 3.55 * T, 3.75 * T)
    put(img, kit.tile(fort, 10, 2), 4.3 * T, 3.85 * T)
    put(img, kit.tile(fort, 15, 3), 4.15 * T, 4.3 * T)
    return img


def pieces(sheet: str, placed: Sequence[tuple[float, float, float, float]], flip: bool = False) -> Image.Image:
    """Tiles (c, r) from one sheet set down at (x, y) in tiles: a heap built up piece by piece."""
    src = kit.load(sheet)
    img = canvas()
    for c, r, x, y in placed:
        t = kit.tile(src, c, r)
        put(img, t.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if flip else t, x * T, y * T)
    return img


def damp_heap(size: int) -> Image.Image:
    """Dead wood dumped in the open by the wall's end, still grey-wet: each size adds sticks to the one before."""
    heaps = [[(7, 15, 6.2, 4.5)],
             [(7, 15, 6.75, 4.3), (6, 15, 6.95, 4.1)],
             [(7, 15, 6.45, 4.1), (7, 15, 6.2, 4.55), (6, 15, 5.85, 4.2)]]
    return pieces(ASH_B, heaps[size])


def stones_heap(size: int) -> Image.Image:
    """Stones carried in from the ruin, set down at the back of the spot."""
    heaps = [[(1, 2, 10.6, 5.45)], [(3, 2, 10.95, 5.3), (0, 2, 10.35, 5.6)], [(4, 2, 11.3, 5.55), (5, 2, 10.75, 5.75)]]
    return pieces(ASH_B, heaps[size])


def dry_stack(size: int) -> Image.Image:
    """Dried wood kept under the roof in the corner, out of the wet."""
    stacks = [[(15, 3, 0.2, 4.1)], [(15, 3, 0.45, 3.8), (14, 3, -0.15, 3.85)]]
    return pieces(FORT, stacks[size])


def rack() -> Image.Image:
    """A rail on legs in front of the wall at the roof's edge, the wood stood against it: there from the first drying."""
    fort = kit.load(FORT)
    img = canvas()
    put(img, kit.tile(fort, 0, 10, 2.75, 1), 3.2 * T, 3.95 * T)
    return img


def stool() -> Image.Image:
    img = canvas()
    put(img, kit.curated("camp_stump_a"), FIRE[0] + 1.85 * T, FIRE[1] + 0.25 * T)
    return img


def birch(part: int) -> Image.Image:
    """The birch felled at the scene's right edge: part 0 the trunk lying, part 1 the stump it came from."""
    trunk, stump = props.felled_birch()
    img = canvas()
    if part == 0:
        put(img, props.figure_shadow(trunk.width + 6), 11.5 * T, 6.0 * T + trunk.height - 6)
        put(img, trunk, 11.5 * T + 3, 6.0 * T)
    else:
        put(img, stump, 11.5 * T + trunk.width + 2, 6.0 * T + trunk.height - stump.height + 2)
    return img


def seated_at_work(frame: str, held: Held) -> Image.Image:
    """A kneeling job's pose once the stool is built: the same frame and prop, sat on the stool and facing the fire
    from its right, so the prop (drawn for a figure facing right) is mirrored about the feet."""
    prop, dx, dy = held
    return figure(frame, SEAT, tweak=props.seated, held=[(ImageOps.mirror(prop), -dx - prop.width, dy)])


def carrying(feet: tuple[float, float]) -> Image.Image:
    """Walking back in with an armful of the dead wood held in front."""
    img = figure("walk (2)", feet)
    sticks = kit.tile(kit.load(ASH_B), 7, 15)
    sticks = sticks.crop(sticks.getchannel("A").getbbox())
    put(img, sticks, feet[0] - 24, feet[1] - 34)
    return img


def firelight(strength: float) -> Image.Image:
    """Warm light thrown by the fire, for a screen blend; the fireback's is a second, smaller one on top."""
    mask = kit.radial((W, H), FIRE, 4.2 * T, int(255 * strength), 0, squash=0.8)
    light = Image.new("RGBA", (W, H), (150, 78, 26, 255))
    light.putalpha(mask)
    return light


def base(rng: random.Random) -> tuple[Image.Image, Image.Image]:
    """The backdrop (ground, low ground, ruin) and the haze rising at the rim with its coping, cut away where the walls
    stand: two layers, so what stands out on the low ground is drawn between them. Already graded per part."""
    img = ground(rng)
    walls = ruin()
    rim_y = rim.edge(walls)
    img.alpha_composite(valley.lowland(rng, rim_y))
    img.alpha_composite(valley.trees(rng))
    edge = behind(valley.drop(rng, rim_y, walls), walls.getchannel("A"))
    img.alpha_composite(walls)
    img.alpha_composite(shade())
    return img, edge
