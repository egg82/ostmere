"""Days eight and nine's layers (content/team/week-two.md, Art and the timelines' Scene column; ids from
app/ashfall_app/opening/{day_eight,day_nine}.toml), in the groups build.py splices into its draw order: the Drift's world
and the people beyond the back line, the camp's new builds, the ash on its roofs, the fungus on the birch, the figures
and the gap fire's light. Every condition names an id from those chapters, so nothing here shows before day eight.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image

import daythree_made as day3
import dayeight_made as made
import dayeight_poses as poses
import dayeight_world as world
import dayeleven_layers as d11
import daytwelve_layers as d12
import dayfour_made as day4
import dayfour_poses as day4_poses
import dayone
import daytwo
from output import Layer

PALISADE = "running:palisade|mix:palisade"
HANDS_AWAY = [PALISADE]
"""Raising the posts takes the player off the stool."""
N3_JOBS = "running:n3_pick|running:n3_ash_ground"
"""Her day-eight jobs: her by-the-fire pose gives way to them."""
N4_JOBS = "running:n4_cord"
"""His cord: his by-the-fire pose gives way to it."""
STRIPPED = "store:e2_clock"
"""Holds while E2's strip runs: the rack's hang is gone for its hour."""
CLOSED, SAFETY = "feature:ring_closed", "feature:safety"
ROOFS = {"bay": "store:bay", "bay2": "store:bay2", "lean_to": "feature:lean_to", "n1_shelter": "feature:n1_shelter",
         "woodshed": "pushes:woodshed@3", "rack_roof": "pushes:rack_roof@2"}
"""Each roof the ash lies on, and what shows it."""


def _roofs() -> dict[str, Image.Image]:
    return {"bay": day3.bay(), "bay2": day4.bay2(), "lean_to": dayone.lean_to(), "n1_shelter": daytwo.n1_shelter(),
            "woodshed": day4.woodshed(3), "rack_roof": day3.rack_roof(2)}


def world_layers(walls: Image.Image) -> list[Layer]:
    """At the back line, under everything the camp has built in front of it: the smoke, the pack and the four at the gate,
    then the palisade, which stands in front of them."""
    return [
        Layer(id="road_smoke", img=world.road_smoke(walls), when="pushes:palisade@9", until=SAFETY),
        Layer(id="wolf_gap", img=world.wolves_at_gap(walls), when="action:pack", until=CLOSED),
        Layer(id="figure_family_gate", img=poses.at_the_gate(), when=SAFETY, until=d11.ARRIVED),
        *[Layer(id=f"palisade_{n}", img=made.palisade(n), when=f"pushes:palisade@{n}") for n in (3, 6, 9, 12)],
        Layer(id="scored_line", img=world.scored_line(), when="store:b9_clock@2", until="pushes:palisade@12"),
    ]


def made_layers() -> list[Layer]:
    ring = made.gap_ring()
    return [
        Layer(id="stakes_1", img=made.stakes(1), when="store:stakes"),
        Layer(id="stakes_2", img=made.stakes(2), when="store:stakes@12"),
        Layer(id="gap_ring", img=ring, when="pushes:gap_fire@1"),
        Layer(id="gap_ring_ghost", img=dayone.ghost(ring), when="running:gap_fire", until="pushes:gap_fire@1"),
        Layer(id="gap_laid", img=made.gap_laid(), when="pushes:gap_fire@1", until="pushes:gap_fire@2"),
        Layer(id="gap_lit", img=made.gap_lit(), when="pushes:gap_fire@2", ungraded=True),
        Layer(id="ash_heap", img=made.ash_heap(), when="store:ash"),
        *[Layer(id=f"ashed_{n}", img=made.ashed(n), when=f"store:ashed_ground&pushes:n3_dig_bed@{n}") for n in (1, 2, 3)],
        Layer(id="snare_4", img=made.snare_4(), when="action:snare_4"),
        *[Layer(id=f"roof_ash_{r}", img=world.roof_ash(img), when=f"chip:ash_laden&{ROOFS[r]}")
          for r, img in _roofs().items()],
    ]


def birch_layers(log: Image.Image, stump: Image.Image, birch: str) -> list[Layer]:
    """`birch` is what shows the felled birch: the shelves grow on it while the bloom lasts."""
    return [Layer(id="fungus_birch", img=world.fungus(log, stump),
                  when="|".join(f"store:bloom&{c}" for c in birch.split("|")), until=d12.SIGN)]


def figure_layers(away: str) -> list[Layer]:
    """`away` is day one's hands-out-working condition: the raising pose steps aside for it, as the other builds do."""
    return [
        Layer(id="figure_building_palisade", img=poses.raising_posts(), when=PALISADE, until=away),
        Layer(id="figure_n3_sorting", img=poses.n3_sorting(), when="running:n3_pick"),
        Layer(id="figure_n3_ashing", img=day4_poses.n3_digging(), when="running:n3_ash_ground"),
        Layer(id="figure_n4_cord", img=poses.n4_twisting(), when=N4_JOBS),
    ]


def light_layers() -> list[Layer]:
    return [
        Layer(id="gap_light", img=made.gap_light(), when="pushes:gap_fire@2", blend="screen", ungraded=True),
        Layer(id="ash_drift", img=world.drift_ash(), when="store:drift_left"),
    ]
