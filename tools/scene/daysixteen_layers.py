"""Days sixteen to nineteen's layers (content/team/week-three.md, Art; ids from
app/ashfall_app/opening/{day_sixteen,day_nineteen}.toml), in the group build.py splices into its draw order: past the
walls, the road's four states by its stages, its two over the top, and the cloths on its markers. Every condition names
an id from those chapters, so nothing here shows before day sixteen.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import daysixteen_made as made
from output import Layer

ROAD = (3, 6, 8, 10)
"""The road's stages each state shows from (week-three.md, Art: four states)."""
OVER = (3, 6)
"""The stretches of the way over the top each of its states shows from."""


def _states(card: str, ids: list[str], stages: tuple[int, ...], walls: Image.Image) -> list[Layer]:
    """One layer per state, each shown from its stage until the next state's."""
    return [
        *[Layer(id=i, img=made.road(i, walls), when=f"pushes:{card}@{at}", until=f"pushes:{card}@{until}")
          for i, at, until in zip(ids, stages, stages[1:])],
        Layer(id=ids[-1], img=made.road(ids[-1], walls), when=f"pushes:{card}@{stages[-1]}"),
    ]


def world_layers(walls: Image.Image) -> list[Layer]:
    return [
        *_states("cut_road", [f"road_{n}" for n in (1, 2, 3, 4)], ROAD, walls),
        *_states("cut_over", ["road_over_1", "road_over_2"], OVER, walls),
        Layer(id="road_cloths", img=made.cloths(walls), when="project:road_cloths"),
    ]
