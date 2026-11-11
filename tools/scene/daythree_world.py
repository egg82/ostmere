"""Day three's found world, cool and drawn in its final colours: the track out through the gap, half sunk in the ash, the
dead field where it ends, the frost on the third night, the glow of the warm ground under the hearth; and the cairns the
camp sets along the track (warm, because the camp made them).
Soft or distant things are drawn at the art's 1x grain and scaled with NEAREST.
Story spoilers (content/team/day-three.md, Art): never shown to the owner."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import kit
import night
from dayone_world import behind
from kit import ASH_B, T
from place import FIRE, H, W
from tints import ACCENT
from valley import HAZE, veil_at, veiled

TRACK = [(284, 147), (278, 137), (286, 126), (296, 116), (293, 107), (292, 99)]
"""The track's waypoints in scene pixels: from the rubble in the gap, up over the low ground to the crest, and on."""
FIELD = (292, 94)
"""The dead field's centre on the far slope, where the track ends."""
CAIRNS = [(270, 125, 0.72), (309, 120, 0.64), (265, 112, 0.56), (306, 106, 0.5), (268, 100, 0.44)]
"""The cairns along the track, near to far: scene x, y and the scale their distance gives. All stand out on the low
ground past the gap's fallen stones, not on them."""
RUT, BANK = (50, 52, 62), (150, 154, 164)
FROST, WASH = (226, 232, 240), (176, 190, 208)
SEED = 17


def _along(points: list[tuple[int, int]]) -> list[tuple[float, float, float]]:
    """A point every half pixel along the waypoints, with how far along (0 near, 1 far)."""
    segs = list(zip(points, points[1:]))
    total = sum(math.dist(a, b) for a, b in segs)
    out: list[tuple[float, float, float]] = []
    done = 0.0
    for (x0, y0), (x1, y1) in segs:
        length = math.dist((x0, y0), (x1, y1))
        steps = max(1, int(length))
        for i in range(steps):
            out.append((x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, (done + length * i / steps) / total))
        done += length
    return out


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


def track(walls: Image.Image) -> Image.Image:
    """Two ruts in the ash that narrow and pale into the haze as they climb (as hazy as the low ground under each row):
    the near side sunk and dark, the far side drifted half full, a lighter bank along each edge."""
    img = Image.new("RGBA", (W // 2, H // 2))
    px = img.load()
    assert px is not None
    for x, y, t in _along(TRACK):
        half = 4.4 - 3.4 * t
        fade = veil_at(y)
        for dx in range(-math.ceil(half), math.ceil(half) + 1):
            if abs(dx) > half - 0.5:
                tone = BANK
            elif dx < half * 0.35:
                tone = RUT
            else:
                tone = _mix(RUT, BANK, 0.6 if (int(x) + dx + int(y)) % 2 else 0.35)
            xx, yy = int(x / 2) + dx, int(y / 2)
            if 0 <= xx < img.width and 0 <= yy < img.height:
                px[xx, yy] = (*_mix(tone, HAZE, fade), 255)
    return behind(kit.up(img), walls)


def field(walls: Image.Image) -> Image.Image:
    """Ploughed ground on the far slope gone to nothing: a darker patch whose furrows run away toward the track's end in
    the haze, a few bare stakes, and a rust-red lump lying in one."""
    img = Image.new("RGBA", (W // 2, H // 2))
    d = ImageDraw.Draw(img)
    fx, fy = FIELD[0] // 2, FIELD[1] // 2
    soil, ridge = (*_mix((66, 62, 66), HAZE, 0.5), 255), (*_mix((92, 88, 88), HAZE, 0.5), 255)
    d.polygon([(fx - 12, fy - 3), (fx + 12, fy - 3), (fx + 21, fy + 3), (fx - 21, fy + 3)], fill=soil)
    for k in range(-3, 4):
        d.line((fx + k * 3, fy - 3, fx + k * 5, fy + 3), fill=ridge)
    for x, y in ((-12, 0), (-5, -3), (10, -1), (16, 2)):
        d.line((fx + x, fy + y - 3, fx + x, fy + y), fill=(*_mix((56, 54, 58), HAZE, 0.3), 255))
    d.rectangle((fx + 5, fy - 1, fx + 8, fy), fill=(118, 66, 48, 255))
    d.line((fx + 5, fy - 2, fx + 7, fy - 2), fill=(158, 94, 64, 255))
    return behind(kit.up(img), walls)


def cairns(first: int, last: int) -> Image.Image:
    """The cairns `first` to `last` of the list, each three stones stacked, the camp's brighter grey, a shadow under,
    each as hazy as the low ground it stands on."""
    sheet = kit.load(ASH_B)
    out = Image.new("RGBA", (W, H))
    for x, y, s in sorted(CAIRNS[first:last], key=lambda c: c[1]):    # far first, so a nearer one stands in front
        out.alpha_composite(veiled(_cairn(sheet, x, y, s), y))
    return out


def _cairn(sheet: Image.Image, x: int, y: int, s: float) -> Image.Image:
    """One cairn on a full canvas, graded."""
    out = Image.new("RGBA", (W, H))
    shadow = Image.new("RGBA", (round(24 * s), 6))
    ImageDraw.Draw(shadow).ellipse((0, 0, shadow.width - 1, 5), fill=(14, 16, 22, 120))
    out.alpha_composite(shadow, (round(x - shadow.width / 2), round(y - 3)))
    top = y
    for col, width in ((0, 0.62), (3, 0.46), (0, 0.3)):
        stone = kit.tile(sheet, col, 2)
        stone = stone.crop(stone.getchannel("A").getbbox())
        w = max(2, round(24 * s * width))
        stone = kit.resize(stone, (w, max(2, round(w * stone.height / stone.width))))
        top -= stone.height - 2
        out.alpha_composite(stone, (round(x - w / 2), round(top)))
    return kit.grade(out, **ACCENT)


def frost(walls: Image.Image) -> Image.Image:
    """Frost on the ground past the firelight: a pale wash in a few steps and sparse white flecks, thicker the further
    from the fire and broken into patches, and none on the stone (nothing where the ruin's walls and fallen stones
    stand, nothing inside the light)."""
    rng = random.Random(SEED)
    img = Image.new("RGBA", (W // 2, H // 2))
    px = img.load()
    assert px is not None
    patch = {(x, y): rng.uniform(0.55, 1.15) for x in range(W // 16 + 1) for y in range(H // 16 + 1)}
    for y in range(146 // 2, H // 2):
        for x in range(W // 2):
            reach = math.hypot(x * 2 - FIRE[0], (y * 2 - FIRE[1]) / 0.8) / (4.2 * T)
            cover = min(1.0, max(0.0, (reach - 0.7) / 0.7)) * patch[(x // 8, y // 8)]
            if cover <= 0.05:
                continue
            if rng.random() < cover * 0.07:
                px[x, y] = (*FROST, 210)
            else:
                px[x, y] = (*WASH, min(5, int(cover * 7)) * 16)
    return behind(kit.up(img), walls)


def warm_glow(walls_foot: int) -> Image.Image:
    """The cracks' red glow in rings round the hearth, kept faint (the slab's glow of day one at about half strength)."""
    glow = night.crack_glow((W, H), FIRE, walls_foot, SEED)
    faint = kit.point(glow.getchannel("A"), lambda v: v * 0.85)
    glow.putalpha(faint)
    return glow
