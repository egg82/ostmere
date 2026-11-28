"""Day twenty-seven's layer (app/ashfall_app/opening/day_twenty_seven.toml), in the group build.py splices into its draw
order: I13's night, the town sat round the fire while the bedesman stands and says the names (`fire:names`; the
bedesman's own pose is people_layers.py's). Its condition names that chapter's card.

Story spoilers (content/team/week-four.md, Art): never shown to the owner."""
from __future__ import annotations

from day_twenty_five import daytwentyfive_layers as d25
from day_twenty_five import daytwentyfive_poses as poses
from frame.output import Layer

NAMES = "project:sit_names&dark"
"""A40's sitting, while night 28 lasts."""
AT_THE_FIRE = ("n1", "n2", "n3")
"""The camp's people the circle draws (daytwentyfive_poses.SAT): taken from every other pose of theirs while it sits."""


def figure_layers() -> list[Layer]:
    return [Layer(id=f"figure_fire_names_{i + 1}", img=img, when=NAMES, front=front)
            for i, (img, front) in enumerate(poses.sat_at_fire())]


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    layer_id: (NAMES,) for layer_id in (*d25.poses_of(AT_THE_FIRE), *d25.PLAYER_POSES)
}
"""Everyone sat in the circle leaves their other poses."""
