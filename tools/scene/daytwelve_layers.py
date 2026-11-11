"""Day twelve's layers (content/team/week-two.md, Art and the timeline's Scene column; ids from
app/ashfall_app/opening/day_twelve.toml), in the groups build.py splices into its draw order: the cellar and the lamps,
the bear's sign on the birch, the figures with the pyre and the wolf at the light's edge, then night 14's lights.
Every condition names an id from that chapter, so nothing here shows before day twelve.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import daythree_world as day3_world
import daytwelve_made as made
import daytwelve_poses as poses
import daytwelve_world as world
from output import Layer
from parts import firelight

MORNING = "action:morning_13"
"""Morning 13, an hour after the vigil: night 12's grade, lights and the covered body end on it."""
BURNING = "store:morning_13@20"
"""Its hidden clock's hour: the burning at first light lasts until it has run."""
DIG = "running:dig_cellar|mix:dig_cellar"
HANDS_AWAY = [DIG]
"""Digging takes the player off the stool."""
SIGN = "store:bear_sign|project:hunt_bear"
"""SL20's sign at the bloom: its pool of hunts while any is left, and for good once one has been made."""
SITTER, DAWN = "feature:sitter", "feature:week_two_end"
"""S3's wolf at the light's edge, gone by S4's dawn."""
NIGHT_14 = "action:night_14"
STAGES = 4
LAMPS = "pushes:tallow_lamps@3"
"""The lamps' last stage: both lit."""


def made_layers() -> list[Layer]:
    return [
        *[Layer(id=f"cellar_{n}", img=made.cellar(n), when=f"pushes:dig_cellar@{n}", until=f"pushes:dig_cellar@{n + 1}")
          for n in range(1, STAGES)],
        Layer(id=f"cellar_{STAGES}", img=made.cellar(STAGES), when=f"pushes:dig_cellar@{STAGES}"),
        *[Layer(id=f"lamp_{n + 1}", img=made.lamp(n), when=f"pushes:tallow_lamps@{n + 1}", until=LAMPS) for n in (0, 1)],
        Layer(id="lamps_lit", img=made.lamps_lit(), when=LAMPS, ungraded=True),
    ]


def birch_layers(log: Image.Image, stump: Image.Image, birch: str) -> list[Layer]:
    """`birch` is what shows the felled birch: its shelves torn down and the claw marks, from the sign on."""
    signed = "|".join(f"{c}&{s}" for c in birch.split("|") for s in SIGN.split("|"))
    return [
        Layer(id="fungus_torn", img=world.torn(log, stump),
              when="|".join(f"store:bloom&{c}&{s}" for c in birch.split("|") for s in SIGN.split("|"))),
        Layer(id="claw_marks", img=world.claw_marks(stump), when=signed),
    ]


def figure_layers(away: str) -> list[Layer]:
    """`away` is day one's hands-out-working condition: the digging pose steps aside for it, as the builds do."""
    return [
        Layer(id="pyre", img=made.pyre(), when=MORNING, until=BURNING),
        Layer(id="pyre_flames", img=made.pyre_flames(), when=MORNING, until=BURNING, ungraded=True),
        Layer(id="figure_digging_cellar", img=poses.digging(), when=DIG, until=away),
        Layer(id="wolf_sitting", img=world.sitter(), when=SITTER, until=DAWN),
    ]


def light_layers() -> list[Layer]:
    """The lamps' light, and night 14's fire as night 12's: the evening's firelight and the warm ground's glow."""
    return [
        Layer(id="lamp_light", img=made.lamp_light(), when=LAMPS, blend="screen", ungraded=True),
        Layer(id="warm_glow_14", img=day3_world.warm_glow(146), when=NIGHT_14, blend="screen"),
        Layer(id="firelight_dusk_14", img=firelight(0.7), when=NIGHT_14, blend="screen", ungraded=True),
    ]
