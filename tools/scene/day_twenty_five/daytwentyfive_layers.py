"""Day twenty-five's layers (app/ashfall_app/opening/day_twenty_five.toml), in the groups build.py splices into its
draw order: the midden pit, the player waking at the camp stone (`stone:wake`, B20's visit) and B21's ring at the fire
(`fire:ring`, until I11). Every condition names an id from that chapter or a clock it starts.

Story spoilers (content/team/week-four.md, Art): never shown to the owner."""
from __future__ import annotations

from cast import people_day, people_hall
from day_twenty_five import daytwentyfive_made as made
from day_twenty_five import daytwentyfive_poses as poses
from frame.output import Layer

WAKE = "feature:kept&store:kept_clock@0..2"
"""B20's first light: the player on the ground at the camp stone, for the two hours after `kept` (its clock counts them)."""
RING = "feature:bedesman_home&store:bede_clock@0..4"
"""B21 until I11 (`bede_clock` counts the hours from B21): the ring at the fire, Sorrel outside it."""
IN_THE_RING = ("n1", "n2", "n3", "n4", "n5", "n16", "n17", "n18", "n19", "n20", "n21", "n22")
"""The people at the fire while the ring stands (its cooks among them), drawn in it (daytwentyfive_poses.RING) or behind
its backs: taken from every other pose of theirs."""
PLAYER_POSES = ("figure_by_fire", "figure_on_stool")


def world_layers() -> list[Layer]:
    return [Layer(id="midden_pit", img=made.midden_pit(), when="running:dig_midden|project:dig_midden")]


def figure_layers() -> list[Layer]:
    return [
        Layer(id="figure_stone_wake", img=poses.wake_at_stone(), when=WAKE),
        *[Layer(id=f"figure_fire_ring_{i + 1}", img=img, when=RING, front=front)
          for i, (img, front) in enumerate(poses.ring_at_fire())],
    ]


def poses_of(people: tuple[str, ...]) -> tuple[str, ...]:
    """Every idle and work pose of `people` (people_hall.IDLE, people_day.AT_WORK)."""
    return (*(i for p in people for i in people_hall.IDLE.get(p, ())),
            *(people_day.layer_id(p) for p in people if p in people_day.AT_WORK))


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    **{layer_id: (RING,) for layer_id in poses_of(IN_THE_RING)},
    "figure_n23_at_hall_door": (RING,),
    **{layer_id: (WAKE, RING) for layer_id in PLAYER_POSES},
}
"""The player's seat gives way to their waking and the ring; everyone in the ring leaves their other poses."""
