"""Days four to seven's layers (content/team/days-four-to-seven.md, Art, with combat-open.md C9 and banked-time-open.md
BT3; ids from app/ashfall_app/opening/{day_four,day_five,b7,day_six}.toml), in the groups build.py splices into its draw
order: the fog and the signs of the wolves, the camp's new builds, the figures, the beasts, and the nights' lights. Every
condition names an id from those chapters, so nothing here shows before day four.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import dayeight_layers as d8
import dayfour_creatures as beasts
import dayone
import dayfour_made as made
import dayfour_poses as poses
import dayfour_world as world
import daythree_world as day3_world
import daytwo_layers as d2
import daythree_layers as d3
import trips
from dayone_poses import build_at
from kit import T
from output import Layer
from parts import firelight
from place import FIRE

HAND = "running:hand_on_stone|mix:hand_on_stone"
TRIPS = ("hunt_wolf", "hunt_bear")
HUNT = "|".join(trips.away(TRIPS))
AWAY_JOBS = HUNT
"""A hunt (week 1's wolf, day twelve's bear) takes the player down the track: the poses at the fire give way, and the
away pose shows."""
COMFORTS = {"woodshed": "running:woodshed", "make_bay2": "running:make_bay2", "make_spear": "running:make_spear",
            "pelt_bedding": "running:pelt_bedding", "hearth_stones": "running:hearth_stones"}
WORK = {"woodshed": (12.4 * T, 6.9 * T), "make_bay2": poses.BAY2_WORK, "make_spear": (2.4 * T, 8.2 * T),
        "pelt_bedding": (2.7 * T, 8.75 * T), "hearth_stones": (FIRE[0] + 1.4 * T, FIRE[1] + 1.6 * T)}
"""Where the player stands to work each, facing it."""
HANDS_AWAY = [HAND, *COMFORTS.values()]
"""The hand on the stone and the builds take the player off the stool."""
N1_FAR = "feature:arcana"
"""From B6 Lucy sits on the fire's far side: day two's by-the-fire pose gives way to hers."""
N1_BUSY = "|".join([d2.N1_OFF, *d2.TASKS.values(), d3.N1_JOBS])
N3_TASKS = {"foraging": "running:n3_forage", "gathering": "running:n3_gather"}
N3_OFF = f"running:n3_build_bay|running:n3_dig_bed|{d8.N3_JOBS}"
NIGHT_6, MORNING_7 = "feature:night_6", "feature:morning_7"
COMBAT = "feature:combat"
ROOFED = "pushes:rack_roof@2"
BARE_RACK = "feature:wolves"
"""From B7 the strip takes the hang off the rack: it stays bare until the stores fill again."""
STRIPPED = f"store:b7_clock|{d8.STRIPPED}"
"""Holds while a strip runs (B7's half hour, E2's hour); the hang is back once it is spent and the rack has meat."""


def world_layers(walls: Image.Image) -> list[Layer]:
    return [
        Layer(id="kill", img=world.kill(walls), when="feature:wolf_sign"),
        Layer(id="wolf_prints", img=world.wolf_prints(walls), when="feature:wolf_sign"),
        Layer(id="ring_prints", img=world.ring_prints(), when="feature:wolf_sign", until="feature:wolves"),
        Layer(id="ridge_shapes", img=world.ridge_shapes(walls), when="feature:ridge", until="action:night_6"),
    ]


def fog_layers(walls: Image.Image) -> list[Layer]:
    """Fog over the whole scene on day five, thinning to haze at morning 6 and gone by that dusk."""
    return [
        Layer(id="fog_dense", img=world.fog(3, walls), when="feature:fog_5", until="feature:morning_6"),
        Layer(id="fog_haze", img=world.fog(1, walls), when="feature:morning_6", until="action:night_6"),
    ]


def hearth_layers() -> list[Layer]:
    return [Layer(id=f"hearth_stones_{n}", img=made.hearth_stones(n), when=f"pushes:hearth_stones@{n}") for n in (1, 2, 3)]


def made_layers() -> list[Layer]:
    bay2 = made.bay2()
    return [
        *[Layer(id=f"woodshed_{n}", img=made.woodshed(n), when=f"pushes:woodshed@{n}") for n in (1, 2, 3)],
        Layer(id="bay2", img=bay2, when="store:bay2"),
        Layer(id="bay2_ghost", img=dayone.ghost(bay2), when="running:make_bay2|running:n3_build_bay", until="store:bay2"),
        *[Layer(id=f"turned_{n}", img=made.turned(n), when=f"pushes:n3_dig_bed@{n}") for n in (1, 2, 3)],
        Layer(id="turned_pelt", img=made.turned_pelt(), when="project:give_pelt&feature:night_7"),
        Layer(id="pelt_pegged_1", img=made.pegged(1), when="store:pelt"),
        Layer(id="pelt_pegged_2", img=made.pegged(2), when="store:pelt@3"),
        *[Layer(id=f"pelt_in_bay_{n}", img=made.pelt_in_bay(n), when=f"pushes:pelt_bedding@{n}") for n in (1, 2, 3)],
        Layer(id="spear_leaning", img=made.spear_leaning(), when="project:make_spear"),
    ]


def hang_layers(meat: Image.Image) -> list[Layer]:
    """The rack's hang: gone from B7, back when the strip is over and the rack holds meat again."""
    return [
        Layer(id="meat_on_rack", img=meat, when="running:smoke_catch", until=BARE_RACK),
        Layer(id="meat_on_rack_again", img=meat, when=f"{BARE_RACK}&store:smoked|{BARE_RACK}&store:catch",
              until=STRIPPED),
    ]


def figure_layers(away: str) -> list[Layer]:
    """`away` is day one's hands-out-working condition, which now includes the hunt."""
    return [
        Layer(id="figure_hand_on_stone", img=poses.hand_on_stone(), when=HAND),
        Layer(id="figure_hunting", img=poses.hunting(), when=HUNT),
        *[Layer(id=f"figure_building_{c}", img=build_at(WORK[c]), when=r, until=away) for c, r in COMFORTS.items()],
        Layer(id="figure_n1_far_side", img=poses.n1_far_side(), when=N1_FAR, until=N1_BUSY, front=True),
        Layer(id="figure_n2_watching", img=poses.n2_watching(), when=d3.N2_WATCH, front=True),
        Layer(id="figure_n3_at_edge", img=poses.n3_at_edge(), when="feature:pair_offer", until="feature:pair_joined", front=True),
        Layer(id="figure_n4_at_edge", img=poses.n4_seated_at_edge(), when="feature:pair_offer", until="feature:pair_joined",
              front=True),
        Layer(id="figure_n3_laying_bay", img=poses.n3_laying_bay(), when="running:n3_build_bay"),
        Layer(id="figure_n3_digging", img=poses.n3_digging(), when="running:n3_dig_bed"),
        *d2.task_layers("n3", poses.N3, N3_TASKS, N3_OFF, NIGHT_6, MORNING_7),
        Layer(id="figure_n3_by_fire", img=poses.n3_by_fire(), when="feature:pair_joined",
              until="|".join([N3_OFF, *N3_TASKS.values()])),
        Layer(id="figure_n4_watching", img=poses.n4_watching(), when="running:n4_watch"),
        Layer(id="figure_n4_by_fire", img=poses.n4_by_fire(), when="feature:pair_joined",
              until=f"running:n4_watch|{d8.N4_JOBS}"),
    ]


def creature_layers() -> list[Layer]:
    """The beasts: a pair of wolves at the light's edge between B7's two beats, then the rat at the larder and the
    crows (on the roof's ridge once it is built, in the hang if not) while combat runs."""
    return [
        Layer(id="wolf_edge_1", img=beasts.wolf("left", (404, 285)), when="feature:wolves", until=COMBAT),
        Layer(id="wolf_edge_2", img=beasts.wolf("right", (150, 285)), when="feature:wolves", until=COMBAT),
        Layer(id="rat_larder", img=beasts.rat("left", (190, 206)), when=COMBAT),
        Layer(id="crows_roof", img=_crows((160, 216), (178, 216)), when=f"{COMBAT}&{ROOFED}"),
        Layer(id="crows_hang", img=_crows((154, 238), (176, 238)), when=COMBAT, until=ROOFED),
    ]


def _crows(a: tuple[float, float], b: tuple[float, float]) -> Image.Image:
    img = beasts.crow("left", a)
    img.alpha_composite(beasts.crow("right", b))
    return img


def light_layers() -> list[Layer]:
    """The nights' lights; the cracks' glow of day three's warm ground comes back each night."""
    glow = day3_world.warm_glow(146)
    return [
        Layer(id="eyes", img=world.eyes(), when="feature:wolves", until=COMBAT, blend="screen", ungraded=True),
        Layer(id="wood_steam", img=world.wood_steam(), when=HAND),
        Layer(id="warm_glow_5", img=glow, when="action:night_5", until="feature:morning_6", blend="screen"),
        Layer(id="warm_glow_6", img=glow, when="action:night_6", until="feature:morning_7", blend="screen"),
        Layer(id="warm_glow_7", img=glow, when="action:night_7", until="feature:drift", blend="screen"),
        Layer(id="firelight_dusk_5", img=firelight(0.7), when="action:night_5", until="feature:morning_6", blend="screen",
              ungraded=True),
        Layer(id="firelight_dusk_6", img=firelight(0.7), when="action:night_6", until="feature:morning_7", blend="screen",
              ungraded=True),
        Layer(id="firelight_dusk_7", img=firelight(0.7), when="action:night_7", until="feature:drift", blend="screen",
              ungraded=True),
    ]
