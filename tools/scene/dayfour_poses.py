"""Days four to seven's figures: the player's hand on the stone and off down the track with a spear, Lucy at the fire's far
side, the newcomer on his watch, and the two who join on day five, picked from Time Fantasy's walking-character sheets
(a woman in a blue dress with a sack from the Caves and Mines props, and an old man with white hair and a beard on a stick
cut from the Farm and Fort spear). The player's and the people's frames are day one's to three's; what is new is where they
stand and what they hold.
Story spoilers (content/team/days-four-to-seven.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageOps

import kit
from daythree_poses import AT_GAP, N2, laying, shovel, staff
from daytwo import cut
from daytwo_poses import Who, person
from dayone_poses import N1
from figures import figure, from_behind
from kit import T
from place import BY_FIRE

SHEETS = "timefantasy_characters/timefantasy_characters/sheets/"
N3: Who = (SHEETS + "npc4.png", 0)
"""A woman with dark hair in a plain blue dress."""
N4: Who = (SHEETS + "npc3.png", 1)
"""A man with white hair and a beard, in a vest."""
CAVES = "cavesandmines_TFcolor_update_8.24/_tfrecolor_8.24/1X/tilesets/tileB_cave2.png"
FARM = "tf_farmandfort/rpgmaker_VXa/tileB_farmA.png"

PAIR_AT = (8.2 * T, 8.95 * T)
"""Where she stands the first time: at the light's edge below the hearth."""
PAIR_SITS = (9.35 * T, 8.75 * T)
"""Where he sits: beside her, his stick across his knees."""
N3_BY_FIRE = (7.1 * T, 8.9 * T)
N4_BY_FIRE = (10.0 * T, 8.9 * T)
"""Where each of them keeps once joined, below the hearth's two ends: her standing, him seated."""
N1_FAR = (7.8 * T, 6.0 * T)
"""Lucy's far mark: seated behind the hearth, facing the player across the fire."""
N2_WATCH = (10.0 * T, 6.4 * T)
N4_WATCH = (11.5 * T, 6.65 * T)
"""Where each sits a watch at the watch fire, facing the track (Lucy's is `daythree_poses.WATCHING`)."""
BAY2_WORK = (4.3 * T, 8.95 * T)
"""Where a townsperson stands to lay the second bay's poles."""
TURNED_WORK = (11.3 * T, 7.75 * T)
"""Where she digs: at the turned ground's near edge."""


def spear() -> Image.Image:
    """The Farm and Fort long spear with its head."""
    return cut(FARM, (193, 384, 217, 428))


def sack() -> Image.Image:
    """The Caves and Mines props' tan sack, at one and a half times its size (a bag on a shoulder, not a barrel)."""
    piece = cut(CAVES, (158, 144, 177, 160))
    return kit.resize(piece, (piece.width * 3 // 2, piece.height * 3 // 2))


def hand_on_stone() -> Image.Image:
    """Crouched at the stone's edge on the fire's left, one hand down to it."""
    return figure("crouch (3)", BY_FIRE, flip=True)


def hunting() -> Image.Image:
    """The player's back at the gap's mouth, a spear in his hand (off the scene: the hunt)."""
    tool = spear()
    return from_behind(AT_GAP, held=[(tool, 6, -tool.height + 4)])


def n1_far_side() -> Image.Image:
    """Lucy seated behind the hearth, as day two's rocking pose is seated, looking down at the fire."""
    return person(N1, "down", N1_FAR, drop=7)


def n2_watching() -> Image.Image:
    """The newcomer on his turn at the watch fire, the shaft across his knees, facing the track."""
    return person(N2, "up", N2_WATCH, drop=7, held=[(ImageOps.mirror(staff()), -10, -staff().height // 2 - 4)])


def n3_at_edge() -> Image.Image:
    """The woman at the edge of the light, her sack over her shoulder."""
    bag = sack()
    return person(N3, "left", PAIR_AT, held=[(bag, -bag.width + 6, -36)])


def n4_seated_at_edge() -> Image.Image:
    """The old man sat at the edge of the light, his leg straight out and the stick across his knees."""
    stick = ImageOps.mirror(staff())
    return person(N4, "left", PAIR_SITS, drop=7, held=[(stick, -6, -stick.height // 2 - 4)])


def n3_by_fire() -> Image.Image:
    """Joined: standing below the hearth, the sack set down at her feet."""
    bag = sack()
    return person(N3, "right", N3_BY_FIRE, held=[(bag, -bag.width - 8, -bag.height + 2)])


def n4_by_fire() -> Image.Image:
    """Joined: seated below the hearth, facing the fire."""
    return person(N4, "left", N4_BY_FIRE, drop=7)


def n4_watching() -> Image.Image:
    """Seated at the watch fire with his back to the camp, the stick across his knees."""
    stick = staff()
    return person(N4, "up", N4_WATCH, drop=7, held=[(stick, -10, -stick.height // 2 - 4)])


def n3_laying_bay() -> Image.Image:
    return laying(N3, BAY2_WORK, "left")


def n3_digging() -> Image.Image:
    """Crouched at the turned ground's edge with the shovel."""
    tool: Image.Image = shovel()
    return person(N3, "right", TURNED_WORK, drop=9, held=[(tool, 8, -tool.height - 2)])
