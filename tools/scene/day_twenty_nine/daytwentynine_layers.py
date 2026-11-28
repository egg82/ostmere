"""Day twenty-nine's layers (app/ashfall_app/rules/days/day_twenty_nine.toml), in the groups build.py splices into its
draw order: the ash back on the hall's roof, and the two moments the chapter's lines tell, each a window on the Drift's
clock. Every condition names an id from that chapter, so nothing here shows before day twenty-nine. The Drift's grade is
in frame/grades.py; its falling ash is week two's layer, back on the store the turn refills.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

from audits.builds import ROOFED
from day_eight import dayeight_world as world8
from day_fifteen import dayfifteen_made as hall
from day_twenty_nine import daytwentynine_poses as poses
from frame.output import Layer

DRIFT_TWO = "feature:drift_two"
ROOF_SHOVELLED = f"{DRIFT_TWO}&store:drift_clock@504..508"
"""Y1's first hours (the Drift's clock reads 504 at the turn): n2 up on the hall's roof with a shovel."""
FIDDLE = f"{DRIFT_TWO}&store:drift_clock@508..512"
"""SL37, the first evening of wind (`t_fiddle_plays` at 508): n14 at the fire with the fiddle."""
ROOF_ASH_DEPTH = 3
"""Rows of ash on the hall's ridge, at the 1x grain: thicker than week two's caps, as the turn's lines have it."""


def made_layers() -> list[Layer]:
    return [Layer(id="roof_ash_hall", img=world8.roof_ash(hall.hall(4), ROOF_ASH_DEPTH), when=f"chip:ash_laden&{ROOFED}")]


def figure_layers() -> list[Layer]:
    return [
        Layer(id="figure_n2_shovels_the_hall_roof", img=poses.n2_on_the_roof(), when=ROOF_SHOVELLED),
        Layer(id="figure_n14_plays_at_the_fire", img=poses.n14_fiddling(), when=FIDDLE),
    ]


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    "figure_n2_by_fire": (ROOF_SHOVELLED,),
    "figure_n2_guarding": (ROOF_SHOVELLED,),
    "figure_n2_at_work": (ROOF_SHOVELLED,),
    "figure_n14_at_work": (FIDDLE,),
}
"""Each pose of n2 and n14 the chapter's moments take them from (`step_aside_late` in cast/give_way.py)."""
