"""Day two's layers (content/team/day-two.md, Art; ids from app/ashfall_app/opening/day_two.toml), in the groups
build.py splices into its draw order: the ridge's second state, the two builds, the figures, and the evening's light.
Every condition names a day-two id, so nothing here shows in day one.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import daytwo
import daytwo_poses as poses
import dayone
import dayone_world as world
from dayone_poses import N1, build_at, n1_by_fire
from kit import T
from output import Layer
from parts import firelight

TASKS = {"foraging": "running:n1_forage", "gathering": "running:n1_gather", "cutting": "running:n1_cut",
         "scavenging": "running:n1_scavenge"}
"""Her lane's cards, one pose each."""
STOOL, WALK, N1_WALK = "running:give_stool", "running:walk_ridge", "running:n1_walk_ridge"
NIGHT, MORNING = "feature:night_2", "feature:morning_3"
"""Night 2 falls and morning 3 comes. Features never clear, so a day pose hidden for the night returns as a second
layer from morning 3."""
N1_OFF = f"{STOOL}|{N1_WALK}"
"""She is on the stool or out on the walk: her task pose gives way."""
N1_BUSY = "|".join([N1_OFF, *TASKS.values(), NIGHT])
"""Day one's N1 by the fire gives way to any of her day-two poses."""
BUILDS = {"n1_shelter": "running:build_shelter", "woodstack": "running:build_woodstack"}
WORK = {"n1_shelter": (3.4 * T, 8.65 * T), "woodstack": (12.5 * T, 5.05 * T)}
"""Where the player stands to build each, facing it."""
HANDS_AWAY = [STOOL, WALK, *BUILDS.values()]
"""Day two's hands jobs that take the player off the stool; the walk takes them out of the scene."""


def world_layers(walls: Image.Image) -> list[Layer]:
    return [Layer(id="ridge_bare", img=world.ridge_shape(walls, square=False), when="feature:night_2_sound")]


def made_layers() -> list[Layer]:
    made = {"n1_shelter": daytwo.n1_shelter(), "woodstack": daytwo.woodstack()}
    return [
        *[Layer(id=b, img=img, when=f"feature:{b}") for b, img in made.items()],
        *[Layer(id=f"{b}_ghost", img=dayone.ghost(made[b]), when=BUILDS[b], until=f"feature:{b}") for b in made],
    ]


DRAWN = {"foraging": poses.foraging, "gathering": poses.gathering, "cutting": poses.cutting,
         "scavenging": poses.scavenging}
"""The four task poses, by task name; each takes whoever does it."""


def task_layers(key: str, who: poses.Who, tasks: dict[str, str], off: str, night: str,
                morning: str | None = None) -> list[Layer]:
    """One person's task poses: each shows while its card runs, steps aside for `off` (their other jobs) and for
    `night`, and returns as a second layer from `morning` when there is one."""
    out: list[Layer] = []
    for name, running in tasks.items():
        img = DRAWN[name](who)
        out.append(Layer(id=f"figure_{key}_{name}", img=img, when=running, until=f"{off}|{night}"))
        if morning:
            out.append(Layer(id=f"figure_{key}_{name}_day_3", img=img, when=f"{running}&{morning}", until=off))
    return out


def figure_layers(away: str, n1_jobs: str) -> list[Layer]:
    """`away` is day one's hands-out-working condition: the player's building pose steps aside for it, as day one's.
    `n1_jobs` are her later jobs, which her by-the-fire pose gives way to as it does to day two's."""
    return [
        Layer(id="figure_giving_stool", img=poses.giving_stool(), when=STOOL),
        *[Layer(id=f"figure_building_{b}", img=build_at(WORK[b]), when=c, until=away) for b, c in BUILDS.items()],
        Layer(id="figure_n1_rocking", img=poses.n1_rocking(), when=STOOL),
        *task_layers("n1", N1, TASKS, N1_OFF, NIGHT, MORNING),
        Layer(id="figure_n1_by_fire_day_3", img=n1_by_fire(), when=MORNING, until="|".join([N1_OFF, *TASKS.values(), n1_jobs])),
        Layer(id="figure_n1_asleep", img=poses.n1_asleep(), when=NIGHT, until=MORNING),
        Layer(id="figure_n1_leaving", img=poses.n1_leaving(), when=N1_WALK),
    ]


def light_layers() -> list[Layer]:
    return [Layer(id="firelight_dusk_2", img=firelight(0.7), when="feature:dusk_2", until=MORNING, blend="screen",
                  ungraded=True)]
