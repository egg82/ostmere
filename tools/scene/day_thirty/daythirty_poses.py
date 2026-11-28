"""Day thirty's figures and beasts: the pack sat in the yard facing the hall's door (week one's wolf, its back view, which
the sheet draws upright on its haunches), the player in the hall's door with a fist up (the battler's cheer), the player
crouched at the gate with a hand down (the battler's crouch), and the tracker crouched over the yard's tracks with their
back to the camp. The tracker is cast from whichever lane the save's history picks, so the pose is a hooded figure seen
from behind, the same whoever it is: it keys on its own id, never a lane. Nothing is drawn but the prints.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

import math

from PIL import Image

from day_four.dayfour_creatures import wolf
from day_one.dayone_world import prints
from day_twelve.daytwelve_world import GREY
from day_two.daytwo_poses import Who, person
from draw.figures import figure
from draw.place import canvas

SHEETS = "timefantasy_characters/timefantasy_characters/sheets/"
TRACKER: Who = (SHEETS + "chara4.png", 4)
"""A figure in a long dark hooded cloak, seen from behind: no face, no one's own coat."""
PACK_AT: tuple[tuple[float, float], ...] = ((646, 258), (680, 264), (714, 256), (748, 262), (664, 288), (730, 290))
"""The pack's feet on the open ground before the hall, in two loose rows, each wolf sat facing up to the door."""
DOOR_CALL = (712, 224)
"""The player's feet in the hall's doorway (the door's foot is at y 222, between x 695 and 727)."""
AT_THE_GATE = (300, 168)
"""The player's feet just inside the palisade's gate, between its lamps, crouched to the stone at its foot."""
TRACKS_FROM = (700, 268)
"""Where the pack sat: the yard's tracks run out from here."""
TRACKS: tuple[tuple[float, float], ...] = ((-160, -50), (-120, 40), (-40, 75), (50, 60), (75, 0), (-70, -30))
"""Each trail's far end, from `TRACKS_FROM`: out in every direction, to the gate, the wall and the wood's edge."""
READS_AT = (660, 290)
"""The tracker's feet on the open ground before the hall, among the trails, clear of the crews at their work."""


def pack_in_the_yard() -> Image.Image:
    out = canvas()
    for feet in sorted(PACK_AT, key=lambda f: f[1]):
        out.alpha_composite(wolf("up", feet, coat=GREY))
    return out


def door_call() -> Image.Image:
    return figure("cheer (1)", DOOR_CALL)


def warding_the_gate() -> Image.Image:
    return figure("crouch (3)", AT_THE_GATE)


def yard_tracks() -> Image.Image:
    out = canvas()
    x0, y0 = TRACKS_FROM
    for dx, dy in TRACKS:
        bend = (x0 + dx * 0.5 + dy * 0.12, y0 + dy * 0.5 - dx * 0.12)
        out.alpha_composite(prints([(x0, y0), bend, (x0 + dx, y0 + dy)], step=7.0 + math.hypot(dx, dy) / 60))
    return out


def tracker_reading() -> Image.Image:
    return person(TRACKER, "up", READS_AT, drop=9)
