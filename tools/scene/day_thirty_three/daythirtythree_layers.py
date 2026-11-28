"""Day thirty-three's layers (app/ashfall_app/rules/days/day_thirty_three.toml), in the groups build.py splices into its
draw order: Y15's night, everyone out in the yard before the hall with n14 playing among them (`yard:night`), and night
35's firelight. Every condition names an id from that chapter, so nothing here shows before day thirty-three. The
night's grade is in frame/grades.py.

The crowd is the camp's people from the sheets they are drawn with everywhere else, stood in two loose rows, the back
row facing the fiddler, the front row facing the hall; drawn as one layer, so the crowd check sees one group.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

from cast.people_layers import N13, N23
from cast.people_moments import ARRIVALS, SINGERS
from day_eight.dayeight_poses import BROTHER, HUSBAND, WOMAN
from day_four.dayfour_poses import N3, N4
from day_three.daythree_poses import N2
from day_twenty_nine.daytwentynine_poses import fiddling
from day_two.daytwo_poses import Who, person
from draw.parts import FLICKER, firelight
from draw.place import canvas
from frame.output import Layer

YARD_NIGHT = "feature:week_five_end"
"""Y15, at dusk 35 once Y14 has landed: the chapter's end feature. Night 35 has no morning in week 5, so it stays."""
FIDDLER = (694, 280)
"""n14's feet in the middle of the open ground before the hall, in the ring's open middle."""
CROWD: tuple[tuple[Who, str, tuple[float, float]], ...] = (
    (N2, "right", (618, 252)), (N3, "right", (646, 248)), (N23, "down", (676, 244)), (WOMAN, "left", (724, 248)),
    (HUSBAND, "left", (752, 254)), (SINGERS[0], "right", (640, 296)), (SINGERS[1], "up", (664, 314)), (N4, "up", (694, 318)),
    (BROTHER, "up", (722, 314)), (SINGERS[2], "left", (746, 298)), (N13, "left", (758, 330)),
)
"""Who stands round him and where, back row first: each person's sheet, the way they face, their feet."""


def _yard() -> Image.Image:
    """The crowd and the fiddler, each drawn over whoever stands behind them (by their feet)."""
    figures = [(feet[1], person(who, facing, feet)) for who, facing, feet in CROWD]
    figures.append((FIDDLER[1], fiddling(ARRIVALS["n14"], "down", FIDDLER, seated=False)))
    out = canvas()
    for _, img in sorted(figures, key=lambda f: f[0]):
        out.alpha_composite(img)
    return out


def figure_layers() -> list[Layer]:
    return [Layer(id="figure_yard_night", img=_yard(), when=YARD_NIGHT)]


def light_layers() -> list[Layer]:
    return [Layer(id="firelight_dusk_35", flicker=FLICKER, sound="evening", img=firelight(0.7), when="action:night_35",
                  blend="screen", ungraded=True)]


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    "figure_n2_guarding": (YARD_NIGHT,), "figure_n13_outside_ring": (YARD_NIGHT,), "figure_n23_at_hall_door": (YARD_NIGHT,),
    "figure_n5_at_hall_door_dark": (YARD_NIGHT,), "figure_n6_at_hall_door_dark": (YARD_NIGHT,),
    "figure_n23_says_the_names": (YARD_NIGHT,),
}
"""Everyone drawn out of doors at night joins the crowd in the yard."""
