"""Where the people are: every outcome that joins or leaves a person, or puts one somewhere the scene could show, names
the scene layer that shows it or says why none does (`whereabouts`, entries.WhereaboutsEntry). A case is
`<owner>:<person>`, the owner being `trigger:<id>`, `card:<id>/outcome`, `card:<id>/finished` or `offer:<offer>/<answer>`.
app/tests/test_scene_people.py holds every join and leave to the field, and the cases in `HELD_UNPLACED` to the audit."""

HELD_UNPLACED: frozenset[str] = frozenset({
    "offer:o_choir/o_choir_beds:n10",
    "offer:o_choir/o_choir_beds:n8",
    "offer:o_choir/o_choir_beds:n9",
    "offer:o_choir/o_choir_road:n10",
    "offer:o_choir/o_choir_road:n8",
    "offer:o_choir/o_choir_road:n9",
    "offer:o_cutter/o_cutter_beds:n11",
    "offer:o_cutter/o_cutter_beds:n12",
    "offer:o_cutter/o_cutter_road:n11",
    "offer:o_cutter/o_cutter_road:n12",
    "offer:o_fiddle/o_fiddle_build:n14",
    "offer:o_fiddle/o_fiddle_build:n15",
    "offer:o_fiddle/o_fiddle_food:n14",
    "offer:o_fiddle/o_fiddle_food:n15",
    "offer:o_walkers/o_walkers_build:n16",
    "offer:o_walkers/o_walkers_build:n17",
    "offer:o_walkers/o_walkers_build:n18",
    "offer:o_walkers/o_walkers_build:n19",
    "offer:o_walkers/o_walkers_food:n16",
    "offer:o_walkers/o_walkers_food:n17",
    "offer:o_walkers/o_walkers_food:n18",
    "offer:o_walkers/o_walkers_food:n19",
    "offer:o_widowers/o_widowers_build:n20",
    "offer:o_widowers/o_widowers_build:n21",
    "offer:o_widowers/o_widowers_build:n22",
    "offer:o_widowers/o_widowers_food:n20",
    "offer:o_widowers/o_widowers_food:n21",
    "offer:o_widowers/o_widowers_food:n22",
})
"""Cases that put a person somewhere the scene shows nothing of today (the audit, one row each): may only shrink. A
case leaves this list when its outcome gains a `whereabouts` entry for the person."""
