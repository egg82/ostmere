"""Day eleven's layers (content/team/week-two.md, Art and the timeline's Scene column; ids from
app/ashfall_app/opening/day_eleven.toml), in the groups build.py splices into its draw order: the hut and the board,
then the figures. Every condition names an id from that chapter, so nothing here shows before day eleven.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from day_eleven import dayeleven_made as made
from day_twelve import daytwelve_layers as d12
from day_eleven import dayeleven_poses as poses
from day_three import daythree_world as day3_world
from day_eight.dayeight_poses import BROTHER
from day_four.dayfour_poses import N2_WATCH
from day_three.daythree_poses import N2
from frame.output import Layer
from draw.parts import FLICKER, firelight

ARRIVED = "action:stranger_clock"
"""B10's moment: the family at the gate and the man behind them, who comes in with it."""
JOINED = "feature:family_joined"
"""Z1: the hut done, the three join and the child with them."""
COUNTED = f"store:stranger_clock@400&{JOINED}"
"""Z3: the trigger's own gate (twenty hours from B10, once Z1), which unlocks only a card."""
BUILDING = "running:make_hut|running:n5_build_hut"
BUILT = "project:make_hut|project:n5_build_hut"
HUT_HANDS = "running:make_hut"
HANDS_AWAY = [HUT_HANDS]
"""Building the hut takes the player off the stool."""
NIGHT_12 = "action:night_12"
"""Dusk 12: the story night's standing clock, which the grades read too."""
N2_GUARD, N7_GUARD, N6_POSTS = "running:n2_guard", "running:n7_guard", "running:n6_posts"
"""The guard's turn at the gap takes him from the fire (n2's by-the-fire pose gives way to it); the posts take the
husband to the ring."""


def made_layers() -> list[Layer]:
    return [
        Layer(id="hut_ghost", img=made.hut(building=True), when=BUILDING, until=BUILT),
        Layer(id="hut", img=made.hut(), when=BUILT),
        Layer(id="tally_board", img=made.tally_board(), when="feature:b11"),
        Layer(id="n6_posts", img=made.posts_set(), when="project:n6_posts"),
    ]


def light_layers() -> list[Layer]:
    """Night 12's fire, as week one's nights have theirs: the evening's firelight and the warm ground's glow, from dusk
    to morning 13."""
    return [
        Layer(id="warm_glow_12", img=day3_world.warm_glow(146), when=NIGHT_12, until=d12.MORNING, blend="screen"),
        Layer(id="firelight_dusk_12", flicker=FLICKER, sound="evening", img=firelight(0.7), when=NIGHT_12, until=d12.MORNING, blend="screen",
              ungraded=True),
    ]


def figure_layers(away: str) -> list[Layer]:
    """`away` is day one's hands-out-working condition: the hut's building pose steps aside for it, as the others do."""
    return [
        Layer(id="figure_n5_at_gate", img=poses.at_gate("woman"), when=ARRIVED, until=f"{JOINED}|running:n5_build_hut"),
        Layer(id="figure_child_at_gate", img=poses.child_at_gate(), when=ARRIVED, until=JOINED),
        *[Layer(id=f"figure_{n}_at_gate", img=poses.at_gate(who), when=ARRIVED, until=JOINED)
          for n, who in (("n6", "husband"), ("n7", "brother"))],
        Layer(id="figure_sitting_apart", img=poses.sitting_apart(), when=ARRIVED, until=JOINED),
        Layer(id="figure_building_hut", img=poses.building_hut(), when=HUT_HANDS, until=away),
        Layer(id="figure_n5_building_hut", img=poses.n5_building_hut(), when="running:n5_build_hut"),
        Layer(id="figure_lying_apart", img=poses.lying(), when=JOINED, until=COUNTED),
        Layer(id="vigil_body", img=poses.covered(), when=COUNTED, until=d12.MORNING),
        Layer(id="figure_n5_by_fire", img=poses.by_fire("woman"), when=JOINED, front=True),
        Layer(id="figure_child_by_fire", img=poses.child_by_fire(), when=JOINED, front=True),
        Layer(id="figure_n6_by_fire", img=poses.by_fire("husband"), when=JOINED, until=N6_POSTS),
        Layer(id="figure_n7_by_fire", img=poses.by_fire("brother"), when=JOINED, until=N7_GUARD),
        Layer(id="figure_n6_walking_ring", img=poses.walking_ring(), when=N6_POSTS),
        Layer(id="figure_n2_guarding", img=poses.guarding(N2, N2_WATCH), when=N2_GUARD),
        Layer(id="figure_n7_guarding", img=poses.guarding(BROTHER, poses.N7_GUARD), when=N7_GUARD),
    ]
