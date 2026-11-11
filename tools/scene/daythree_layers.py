"""Day three's layers (content/team/day-three.md, Art; ids from app/ashfall_app/opening/day_three.toml), in the groups
build.py splices into its draw order: the track and its field, the comforts and the bay, the hearth, the figures, and
the evenings' lights. Every condition names a day-three id, so nothing here shows before day three.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import daythree_fire as fire
import daythree_made as made
import daythree_poses as poses
import daythree_world as world
import dayeleven_layers as d11
import daytwo_layers as d2
import dayone
from dayone_poses import build_at
from kit import T
from output import Layer
from parts import firelight
from place import FIRE

EDGE = "running:walk_edge"
TRIP = "running:field_track|mix:field_track"
DIG = "running:dig_clay|mix:dig_clay"
AWAY_JOBS = f"{EDGE}|{TRIP}|{DIG}"
"""The hands' jobs out of the camp: the rim, the track, the stream. The figure is elsewhere while one runs, so the poses
at the fire give way (a trip shows its away pose; the stream's is at the gap)."""
NIGHT_3, MORNING_4, NIGHT_4 = "feature:night_3", "feature:morning_4", "feature:night_4"
COMFORTS = {"larder_floor": "running:larder_floor", "rack_roof": "running:rack_roof",
            "raised_bed": "running:raised_bed", "clay_hearth": "running:clay_hearth",
            "watch_fire": "running:watch_fire", "make_bay": "running:make_bay"}
WORK = {"larder_floor": (5.0 * T, 6.55 * T), "rack_roof": (6.0 * T, 8.85 * T), "raised_bed": (2.0 * T, 6.0 * T),
        "clay_hearth": (FIRE[0] + 1.0 * T, FIRE[1] + 1.5 * T), "watch_fire": (10.3 * T, 6.05 * T),
        "make_bay": (2.7 * T, 8.75 * T)}
"""Where the player stands to work each comfort, facing it."""
HANDS_AWAY = list(COMFORTS.values())
"""The comforts take the player off the stool, as day one's and day two's builds do."""
N1_JOBS = "running:n1_watch|running:n1_build_watch"
"""Lucy's day-three jobs: her by-the-fire pose gives way to them."""
N2_TASKS = {"foraging": "running:n2_forage", "gathering": "running:n2_gather", "cutting": "running:n2_cut",
            "scavenging": "running:n2_scavenge"}
N2_OFF = "running:n2_build_bay"
N2_WATCH = "running:n2_watch"
"""His turn at the watch fire (day four's SL8): his by-the-fire pose gives way to it."""


def _staged(card: str, drawn: list[Image.Image], pushes: list[int]) -> list[Layer]:
    """One layer per stage, each added by the card's n-th push and drawn on top of the stages before it."""
    return [Layer(id=f"{card}_{i + 1}", img=img, when=f"pushes:{card}@{n}") for i, (img, n) in enumerate(zip(drawn, pushes))]


def world_layers(walls: Image.Image) -> list[Layer]:
    """Past the walls (the track, its field) and on the ground (the frost, the cairns the camp sets by the track)."""
    return [
        Layer(id="track", img=world.track(walls), when="feature:track_open"),
        Layer(id="dead_field", img=world.field(walls), when="feature:dead_field"),
        Layer(id="frost", img=world.frost(walls), when=NIGHT_3, until="pushes:clay_hearth@2"),
        Layer(id="cairns_1", img=world.cairns(0, 1), when="pushes:field_track@1"),
        Layer(id="cairns_2", img=world.cairns(1, 3), when="pushes:field_track@3"),
        Layer(id="cairns_3", img=world.cairns(3, 5), when="pushes:field_track@6"),
    ]


def under_layers() -> list[Layer]:
    """What lies on the ground under day one's and two's made things: the larder's floor and the raised bed."""
    return [
        *_staged("larder_floor", [made.larder_floor(n) for n in (1, 2, 3)], [1, 2, 3]),
        *_staged("raised_bed", [made.raised_bed(n) for n in (1, 2, 3)], [1, 2, 3]),
    ]


def hearth_layers() -> list[Layer]:
    """The hearth's courses round the fire (drawn before the flames, so the fire stands in it) and the pot on its rim."""
    return [
        *_staged("clay_hearth", [fire.hearth(n) for n in (1, 2, 3)], [1, 3, 4]),
        Layer(id="stew_pot", img=fire.pot(), when="pushes:clay_hearth@1"),
    ]


def made_layers() -> list[Layer]:
    """The bay and the rack's roof, and the watch fire at the gap: the ring when its first stage is done, lit at the
    second. The bay and the ring show their ghosts while they are being built."""
    bay, ring = made.bay(), fire.watch_ring()
    return [
        Layer(id="bay", img=bay, when="store:bay"),
        Layer(id="bay_ghost", img=dayone.ghost(bay), when="running:make_bay|running:n2_build_bay", until="store:bay"),
        *_staged("rack_roof", [made.rack_roof(n) for n in (1, 2)], [1, 2]),
        Layer(id="watch_ring", img=ring, when="store:watch_done"),
        Layer(id="watch_ring_ghost", img=dayone.ghost(ring), when="running:watch_fire|running:n1_build_watch",
              until="store:watch_done"),
        Layer(id="watch_laid", img=fire.watch_laid(), when="store:watch_done", until="store:watch_done@2"),
        Layer(id="watch_lit", img=fire.watch_lit(), when="store:watch_done@2", ungraded=True),
    ]


def figure_layers(away: str) -> list[Layer]:
    """`away` is day one's hands-out-working condition, which now includes day three's jobs out of the camp."""
    return [
        Layer(id="figure_walking_edge", img=poses.walking_the_rim(), when=EDGE),
        Layer(id="figure_away_track", img=poses.away_on_the_track(), when=TRIP),
        Layer(id="figure_digging", img=poses.digging_at_the_gap(), when=DIG, until=TRIP),
        *[Layer(id=f"figure_building_{c}", img=build_at(WORK[c]), when=r, until=away) for c, r in COMFORTS.items()],
        Layer(id="figure_n1_watching", img=poses.n1_watching(), when="running:n1_watch"),
        Layer(id="figure_n1_building_watch", img=poses.laying(poses.N1, poses.LAYING["watch"], "left"),
              when="running:n1_build_watch"),
        Layer(id="figure_n2_at_edge", img=poses.stranger(), when="feature:stay_offer", until="feature:n2_joined"),
        Layer(id="figure_n2_building_bay", img=poses.laying(poses.N2, poses.LAYING["bay"], "left"), when=N2_OFF),
        *d2.task_layers("n2", poses.N2, N2_TASKS, N2_OFF, NIGHT_4, "feature:morning_5"),
        Layer(id="figure_n2_by_fire", img=poses.n2_by_fire(), when="feature:n2_joined",
              until="|".join([N2_OFF, N2_WATCH, *N2_TASKS.values(), d11.N2_GUARD])),
    ]


def light_layers() -> list[Layer]:
    return [
        Layer(id="firelight_dusk_3", img=firelight(0.7), when="action:evening_3", until=MORNING_4, blend="screen",
              ungraded=True),
        Layer(id="firelight_dusk_4", img=firelight(0.7), when="action:evening_4", until="feature:morning_5",
              blend="screen", ungraded=True),
        Layer(id="watch_light", img=fire.watch_light(), when="store:watch_done@2", blend="screen", ungraded=True),
        Layer(id="warm_glow", img=world.warm_glow(146), when="feature:warm_ground", until="feature:morning_5", blend="screen"),
    ]
