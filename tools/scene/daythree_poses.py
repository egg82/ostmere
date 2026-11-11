"""Day three's figures: the player walking the rim, away down the track and at the gap with a shovel; the newcomer, from
a Time Fantasy NPC sheet, with a staff cut from the Farm and Fort spear (its head cut off); Lucy at the watch fire.
The player's away pose is his back view (`figures.from_behind`) shrunk; the one thing placed by hand is the newcomer's
staff in his front hand; everything else is a frame or a tool the kit has.
Story spoilers (content/team/day-three.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageOps

import kit
import valley
from daytwo import cut
from daytwo_poses import Who, person
from dayone_poses import N1
from figures import figure, from_behind
from kit import T
from place import FIRE, H, W
from tints import WOOD

N2: Who = ("timefantasy_characters/timefantasy_characters/sheets/npc1.png", 3)
"""A walking-character sheet and the character on it: a grey-haired man in a dark vest over a pale shirt."""
RIM_WALK = (13.3 * T, 5.05 * T)
"""Where the player walks the edge: along the rim past the wall stub, the drop at his back."""
ON_TRACK = (289, 126)
"""Where the player is when away on the track: on the climb to the crest, small with the distance."""
AT_GAP = (9.55 * T, 4.92 * T)
"""Where he stands to dig at the stream (off the scene): the gap's mouth, back to the camp."""
EDGE_OF_LIGHT = (7.2 * T, 8.75 * T)
"""Where the newcomer stands the first time: below the fire at the light's edge, clear of the wall and the heaps."""
AT_THE_FIRE = (FIRE[0] - 1.75 * T, FIRE[1] + 0.55 * T)
"""Where he stands once he has stayed: the fire's left, the side the player has left to him."""
WATCHING = (10.4 * T, 5.65 * T)
"""Where Lucy keeps the watch: beside the watch fire, facing the track."""
LAYING = {"bay": (2.7 * T, 8.75 * T), "watch": (8.7 * T, 5.9 * T)}
"""Where a townsperson stands to lay the bay's poles, or the watch fire's stones."""


def staff() -> Image.Image:
    """The Farm and Fort long spear with its head cut off: a plain shaft, longer than the man's arm."""
    return cut("tf_farmandfort/rpgmaker_VXa/tileB_farmA.png", (193, 394, 217, 428))


def shovel() -> Image.Image:
    """The Farm and Fort shovel from its tool row."""
    return cut("tf_farmandfort/rpgmaker_VXa/tileB_farmA.png", (66, 386, 88, 414))


def _far(sprite: Image.Image) -> Image.Image:
    """At half size: the track climbs away from the camp."""
    return kit.resize(sprite, (round(sprite.width * 0.5), round(sprite.height * 0.5)))


def walking_the_rim() -> Image.Image:
    """The player walking along the rim, facing the camp."""
    return figure("walk (2)", RIM_WALK, flip=True)


def away_on_the_track() -> Image.Image:
    """The player's back, shrunk to the distance, walking up the track, a shadow under his feet as the cairns have,
    graded as the figures are and then hazed as the low ground at his feet is (the layer's bake leaves it alone)."""
    img = Image.new("RGBA", (W, H))
    x, y = ON_TRACK
    ImageDraw.Draw(img).ellipse((x - 7, y - 3, x + 6, y + 2), fill=(14, 16, 22, 120))
    img.alpha_composite(kit.grade(from_behind(ON_TRACK, tweak=_far), **WOOD))
    return valley.veiled(img, y)


def digging_at_the_gap() -> Image.Image:
    """The player at the gap's mouth with his back to the camp and a shovel in his hand."""
    tool = shovel()
    return from_behind(AT_GAP, held=[(tool, 6, -tool.height + 2)])


def _with_staff(facing: str, feet: tuple[float, float]) -> Image.Image:
    stick = staff() if facing == "left" else ImageOps.mirror(staff())
    return person(N2, facing, feet, held=[(stick, -14 if facing == "left" else 4, -stick.height + 6)])


def stranger() -> Image.Image:
    """The newcomer at the edge of the firelight, his staff in his front hand, facing the fire."""
    return _with_staff("left", EDGE_OF_LIGHT)


def n2_by_fire() -> Image.Image:
    """The newcomer stood at the fire, leaning on the staff."""
    return _with_staff("right", AT_THE_FIRE)


def n1_watching() -> Image.Image:
    """Lucy by the watch fire with her back to the camp, looking up the track."""
    return person(N1, "up", WATCHING, col=0)


def laying(who: Who, at: tuple[float, float], facing: str) -> Image.Image:
    """Crouched at the work with a stone in both hands, as day two's scavenging pose carries one."""
    stone = cut(kit.ASH_B, (0, 64, 32, 96))
    return person(who, facing, at, col=1, drop=6, held=[(stone, -stone.width // 2, -22)])
