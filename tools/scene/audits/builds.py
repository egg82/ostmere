"""What counts as a build on the ground, and which pairs of builds crowd each other.

A build is a standing thing the camp makes: its states, parts and what it carries are one build, so a roof and the ash
on it, or a heap's three sizes, never count against each other. Every layer of the scene is a build's member, is
named in `NOT_BUILDS` (the backdrop, the ground's own marks, the wall, the dead and the beasts), is a figure, or is an
overlay; `unsorted` fails on any other, so a new layer cannot slip past the overlap check unclassified.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING

from audits import depth

if TYPE_CHECKING:
    from frame.output import Entry, Layer

MIN_SHARED = 30
"""Pixels two builds may share before they read as one drawing laid over the other."""

NOT_BUILDS = frozenset({
    "ruin", "ridge_shape", "ridge_bare", "track", "dead_field", "frost", "cairns_1", "cairns_2", "cairns_3", "kill",
    "wolf_prints", "ring_prints", "ridge_shapes", "road_smoke", "cleared", "prints", "watch_ring_ghost",
    "gap_ring_ghost", "rim_haze", "valley_fog_1", "valley_fog_2", "valley_fog_3", "valley_fog_4", "valley_fog_5", "stream_steam_1",
    "stream_steam_2", "stream_steam_3", "wolf_gap", "palisade_3", "palisade_6", "palisade_9", "palisade_12",
    "scored_line", "roof_posts", "lean_to_ghost", "larder_ghost", "smoke_rack_ghost", "n1_shelter_ghost",
    "woodstack_ghost", "bay_ghost", "bay2_ghost", "hut_ghost", "hall_ghost", "lamp_1", "lamp_2", "lamps_lit", "vigil_body",
    "pyre_flames", "wolf_sitting", "wolf_edge_1", "wolf_edge_2", "rat_larder", "crows_roof", "crows_hang", "yard_tracks",
    "wolves_yard_pack", "cat_ridge",
})
"""Layers that are not a build: the backdrop and the world beyond it, marks on the ground, the palisade, the lamps,
a body, the beasts and birds, and the ghosts a build shows while it is being made."""

BUILDS: Mapping[str, tuple[str, ...]] = {
    "campfire": (
        "ring", "fire_laid", "clay_hearth_1", "clay_hearth_2", "clay_hearth_3", "hearth_stones_1", "hearth_stones_2",
        "hearth_stones_3", "stones_1", "stones_2", "stones_3", "fireback", "clay_hearth_1_front",
        "clay_hearth_2_front", "clay_hearth_3_front", "stew_pot", "fire_lit", "stool", "pot_shelf_1", "pot_shelf_2",
        "pot_shelf_3",
    ),
    "larder_floor": ("larder_floor_1", "larder_floor_2", "larder_floor_3", "wood_stack_1", "wood_stack_2", "wood_stack_3"),
    "raised_bed": ("raised_bed_1", "raised_bed_2", "raised_bed_3"),
    "watch_ring": ("watch_ring", "watch_laid", "watch_banked", "watch_lit"),
    "plot": ("turned_1", "turned_2", "turned_3", "turned_pelt", "turned_sacking", "ashed_1", "ashed_2", "ashed_3", "beds_1", "beds_2", "beds_3"),
    "pelt_pegged_1": ("pelt_pegged_1",),
    "pelt_pegged_2": ("pelt_pegged_2",),
    "gap_ring": ("gap_ring", "gap_laid", "gap_banked", "gap_lit"),
    "cellar": ("cellar_1", "cellar_2", "cellar_3", "cellar_4"),
    "damp_wood_1": ("damp_wood_1", "damp_wood_2", "damp_wood_3"),
    "dry_wood_1": ("dry_wood_1", "dry_wood_2"),
    "wood_drying": ("wood_drying", "rack"),
    "lean_to": ("lean_to", "bay", "pelt_in_bay_1", "pelt_in_bay_3", "roof_ash_bay", "roof_ash_lean_to", "hide_flaps_1"),
    "larder": ("larder",),
    "smoke_rack": (
        "smoke_rack", "rack_roof_1", "rack_roof_2", "roof_ash_rack_roof", "meat_on_rack", "meat_on_rack_again", "racks_film",
    ),
    "n1_shelter": ("n1_shelter", "spear_leaning", "roof_ash_n1_shelter"),
    "woodstack": ("woodstack",),
    "woodshed_1": ("woodshed_1", "woodshed_2", "woodshed_3", "roof_ash_woodshed"),
    "bay2": ("bay2", "pelt_in_bay_2", "roof_ash_bay2", "hide_flaps_2"),
    "stakes": ("stakes_1", "stakes_2"),
    "ash_heap": ("ash_heap",),
    "snare_4": ("snare_4",),
    "hut": ("hut",),
    "tally_board": ("tally_board",),
    "birch_log": ("birch_log", "birch_stump", "fungus_birch", "fungus_torn", "claw_marks"),
    "snare_1": ("snare_1",),
    "snare_2": ("snare_2",),
    "snare_3": ("snare_3",),
    "pyre": ("pyre",),
    "hall": ("hall_1", "hall_2", "hall_3", "hall_4", "hall_hearth", "hall_smoke", "roof_ash_hall", "larder_bar",
             "larder_latch"),
    "n6_posts": ("n6_posts",),
    "midden": ("midden_pit",),
    "road": ("road_1", "road_2", "road_3", "road_4", "road_over_1", "road_over_2", "road_cloths"),
}
"""Each build and the layers that are it: its states, its parts, what it carries."""

NO_SCENE: frozenset[str] = frozenset({"post_door", "post", "bind_book", "waystation"})
"""Builds (craft cards with a cap, app/tests/scene/test_scene_shown.py) the player makes that stand nowhere in the scene:
`post` and `post_door` are out in the wood and `waystation` on the far hill, map stamps and not scene stamps
(content/team/week-four.md and week-five.md, Art); `bind_book` is a book handed to a person, which the journal shows, not
the camp."""

HELD_UNSHOWN: frozenset[str] = frozenset({"screen_fire"})
"""Builds with no scene state today, held so the check stays on for the rest: may only shrink."""

HELD_CROWDED: frozenset[tuple[str, str]] = frozenset()
"""Pairs of builds (sorted) that share `MIN_SHARED` pixels today, held so the check stays on for the rest: may only shrink."""

ROOFED = "pushes:hall@8"
"""The hall's last stage: the roof on and the door hung, with everyone under it (week-three.md, "will they all fit under one
roof")."""

FATES = ("taken_down", "indoors")
"""What becomes of an outgrown build: its poles and hides go to the hall, or what it was for (a bed, a shelter) moves
inside and the scene shows the hall's lit window and nothing of it."""

RETIRED: Mapping[str, tuple[str, str]] = {
    "lean_to": (ROOFED, "taken_down"), "bay2": (ROOFED, "taken_down"), "hut": (ROOFED, "taken_down"),
    "n1_shelter": (ROOFED, "indoors"), "raised_bed": (ROOFED, "indoors"),
}
"""Builds the camp outgrows: the condition that supersedes each, and the fate. Every layer of the build gets it as an
`until` (`retire`). Authored, never read off an id."""

PELTS = "the layer is the pelt store's stock (`store:pelt`), shown while the store holds pelts and the hall's roof takes pelts"
TALLY = "the town's tally board: the content reads it again in a later chapter (`B12`), so it is not outgrown"
PIT = "a dug pit stays dug: nothing in the content fills it"
SNARES = "the snare line is worked all game: day sixteen's `reset_snares` sets it again"
KEPT: Mapping[str, str] = {
    "tally_board": TALLY,
    "midden": PIT,
    "pelt_pegged_1": PELTS,
    "pelt_pegged_2": PELTS,
    "snare_1": SNARES,
    "snare_2": SNARES,
    "snare_3": SNARES,
    "snare_4": SNARES,
}
"""Builds that stay up, and why."""

HELD_UNDECIDED: frozenset[str] = frozenset({
    "campfire", "larder_floor", "watch_ring", "plot", "gap_ring", "cellar", "damp_wood_1", "dry_wood_1", "wood_drying",
    "larder", "smoke_rack", "woodstack", "woodshed_1", "stakes", "ash_heap", "birch_log", "pyre", "hall",
    "n6_posts", "road",
})
"""Builds not yet judged against the content as outgrown or kept: may only shrink. A build leaves it by gaining a row in
`RETIRED` or `KEPT`; a new build is in neither and fails the check."""

MEMBER_OF = {layer: build for build, layers in BUILDS.items() for layer in layers}


def undecided() -> list[str]:
    """Faults in the tables above: a build in none of `RETIRED`, `KEPT` and `HELD_UNDECIDED` or in more than one, a row
    naming no build, an unknown fate, and a held build that now has a row."""
    named = [*RETIRED, *KEPT, *HELD_UNDECIDED]
    faults = [f"{b}: in more than one of RETIRED, KEPT and HELD_UNDECIDED" for b in sorted({b for b in named if named.count(b) > 1})]
    faults += [f"{b}: not a build" for b in sorted(set(named) - BUILDS.keys())]
    faults += [f"{b}: no row in RETIRED or KEPT, and not held" for b in sorted(BUILDS.keys() - set(named))]
    faults += [f"{b}: fate {fate!r} is not one of {FATES}" for b, (_, fate) in RETIRED.items() if fate not in FATES]
    return faults


def retire(layers: Sequence[Layer]) -> list[Layer]:
    """`layers` with every layer of a retired build hidden by what supersedes it."""
    out = list(layers)
    for layer in out:
        row = RETIRED.get(MEMBER_OF.get(layer["id"], ""))
        if row is not None:
            layer["until"] = "|".join(t for t in (layer.get("until"), row[0]) if t)
    return out


def is_thing(entry: Entry) -> bool:
    """Whether the layer is one the classification must account for: not a figure, not an overlay."""
    return not entry["id"].startswith("figure_") and not depth.is_overlay(entry)


def unsorted(entries: Sequence[Entry]) -> list[str]:
    """Layers of `entries` (the whole scene) that are neither in a build nor named in `NOT_BUILDS`, and names in either
    table that no layer has: an unclassified layer would never be checked, and a stale name checks nothing."""
    ids = {e["id"] for e in entries}
    loose = sorted(e["id"] for e in entries if is_thing(e) and e["id"] not in MEMBER_OF and e["id"] not in NOT_BUILDS)
    gone = sorted((MEMBER_OF.keys() | NOT_BUILDS) - ids)
    return [*loose, *gone]


def crowded(shown: Sequence[Entry], shared: Callable[[Sequence[str], Sequence[str]], int]) -> list[tuple[str, str, int]]:
    """Pairs of builds (sorted names, pixels) of `shown` (all shown at once) whose drawings share `MIN_SHARED` pixels or
    more; `shared` is how many pixels two sets of layers (a build's shown members) have in common."""
    members: dict[str, list[str]] = {}
    for e in shown:
        if e["id"] in MEMBER_OF:
            members.setdefault(MEMBER_OF[e["id"]], []).append(e["id"])
    names = sorted(members)
    pairs = [(a, b, shared(members[a], members[b])) for i, a in enumerate(names) for b in names[i + 1:]]
    return [p for p in pairs if p[2] >= MIN_SHARED]
