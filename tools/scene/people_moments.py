"""The one-off moments of people who are not the later arrivals (people_layers.py has those): each is a window on a
count-up clock the moment's own outcome starts (`store:<clock>@1..<n>`, twentieths of a game hour), the person stood where
the line puts them for its few minutes. The by-the-fire pose gives way to each window (`STEP_ASIDE`), whatever order the
windows come in. A figure here is cut from the poses the camp already has.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageOps

import dayeleven_poses
import dayfour_poses as poses4
from dayeight_poses import HUSBAND
from dayfour_made import SHED, SPEAR_FOOT, hide
from daythree_poses import N2, laying, staff
from daytwo_poses import Who, person
from dayfour_poses import BAY2_WORK, N3, N4, spear
from kit import T
from output import Layer
from place import BY_FIRE, WATCH

WINDOWS: dict[str, str] = {
    "shed": "store:shed_stack_clock@1..14",
    "his_watch": "store:his_watch_clock@1..20",
    "old_watch": "store:old_watch_clock@1..20",
    "spear": "store:spear_clock@1..12",
    "thorn": "store:thorn_clock@1..12",
    "caps": "store:caps_clock@1..14",
    "posts": "store:posts_clock@1..14",
    "seed": "store:pair_3h@20..32",
    "bedding": "store:bedding_4_clock@1..12",
    "pelt_ask": "store:pelt_ask_clock@1..12",
    "stage_7": "store:stage_7_clock@1..12",
    "posts_cord": "store:posts_cord_clock@1..12",
    "n6_posts_done": "store:n6_posts_done_clock@1..12",
    "choir_2": "store:choir_2_clock@1..16",
    "road_pair": "store:road_pair_clock@1..16",
    "fiddle_2": "store:fiddle_2_clock@1..16",
    "sun": "store:torn_clock@3..6",
    "deer": "store:clear_clock@18..21",
    "pot": "store:choir_clock@3..6",
    "stone": "store:kept_clock@30..33",
    "singing": "store:still_clock@30..33",
    "drift": "store:drift_clock@12..15",
    "naming": "store:sorrel_clock@6..9",
    "bowl": "store:kept_clock@8..11",
}
"""Each moment's window. The seed's is the pair's own three-hour count, which the trigger reads at 20; the first
group are clocks of the moment's own, started by the outcome that tells it, and the last the chapters' own hours-since
clocks (hours, not twentieths)."""

SHEETS = "timefantasy_characters/timefantasy_characters/sheets/"
SINGERS: tuple[Who, ...] = ((SHEETS + "npc2.png", 3), (SHEETS + "npc2.png", 4), (SHEETS + "npc2.png", 2))
"""Three women in a red dress, a blue one and a purple hood: n8, n9, n10."""
ARRIVALS: dict[str, Who] = {"n11": (SHEETS + "npc3.png", 5), "n12": (SHEETS + "npc4.png", 4),
                            "n14": (SHEETS + "npc3.png", 4), "n15": (SHEETS + "npc4.png", 3)}
"""A red-haired man in a grey coat and a woman in a red dress (n11, n12); a grey-haired man in a green coat and a
fair woman in a pale blue dress (n14, n15)."""
GATE_AT = ((350, 160), (374, 161), (398, 160))
"""Where people who have come to the palisade's gate stand: just inside it, clear of the lamps either side of the gate."""
STRETCH_AT, POSTS_AT, TEST_AT = (360, 158), (516, 162), (392, 158)
"""Where he lashes the palisade's first stretch, braces the three posts and leans on one."""
HAND_AT = (382, 266)
"""Where she comes to the player's place by the fire with a hand out."""

SHED_AT = (SHED[0] - 10, SHED[1] + 44)
THORN_AT = (WATCH[0] - 1.5 * T, WATCH[1] + 1.0 * T)
SEED_AT = (6.9 * T, 9.7 * T)
CAPS_AT = (BY_FIRE[0] + 0.5 * T, BY_FIRE[1] + 1.1 * T)


def _hefting() -> Image.Image:
    """Standing at the lean-to with the spear upright in one hand, turned to hand it back."""
    shaft = spear()
    return person(N2, "down", (SPEAR_FOOT[0] + 34, SPEAR_FOOT[1] + 4), held=[(shaft, 8, -shaft.height + 4)])


def _thorn() -> Image.Image:
    """At the watch fire's near side with the headless shaft in his hand, looking out."""
    shaft = ImageOps.mirror(staff())
    return person(N2, "left", THORN_AT, held=[(shaft, -shaft.width - 4, -shaft.height + 2)])


def _seed() -> Image.Image:
    """Kneeling, the seed in its cloth beside her."""
    bag = poses4.sack()
    return person(N3, "down", SEED_AT, drop=9, held=[(bag, -bag.width - 8, -bag.height + 2)])


def _arrivals(window: str, who: dict[str, Who], spots: tuple[tuple[int, int], ...]) -> list[Layer]:
    return [Layer(id=f"figure_{n}_at_the_gate", img=person(sheet, "down", at), when=window)
            for (n, sheet), at in zip(who.items(), spots)]


def _line_layers() -> list[Layer]:
    """The marked lines' moments (`[line_doings]`): each window starts when the owner of the line tells it."""
    w = WINDOWS
    cloth = hide()
    return [
        Layer(id="figure_n2_takes_the_pelt", img=person(N2, "left", BAY2_WORK, held=[(cloth, -cloth.width - 2, -cloth.height - 8)]),
              when=w["bedding"]),
        Layer(id="figure_n3_holds_out_a_hand", img=person(N3, "left", HAND_AT), when=w["pelt_ask"]),
        Layer(id="figure_n2_tests_a_post", img=person(N2, "up", TEST_AT), when=w["stage_7"]),
        Layer(id="figure_n4_lashes_the_stretch", img=person(N4, "up", STRETCH_AT, drop=7), when=w["posts_cord"]),
        Layer(id="figure_n6_braces_the_posts", img=person(HUSBAND, "up", POSTS_AT), when=w["n6_posts_done"]),
        *_arrivals(w["choir_2"], {f"n{n}": s for n, s in zip((8, 9, 10), SINGERS)}, GATE_AT),
        *_arrivals(w["road_pair"], {k: ARRIVALS[k] for k in ("n11", "n12")}, GATE_AT[:2]),
        *_arrivals(w["fiddle_2"], {k: ARRIVALS[k] for k in ("n14", "n15")}, GATE_AT[:2]),
    ]


def moment_layers() -> list[Layer]:
    w = WINDOWS
    return [
        *_line_layers(),
        Layer(id="figure_n2_stacks_the_logs", img=laying(N2, SHED_AT, "right"), when=w["shed"]),
        Layer(id="figure_n2_his_watch", img=poses4.n2_watching(), when=w["his_watch"], front=True),
        Layer(id="figure_n4_old_watch", img=poses4.n4_watching(), when=w["old_watch"]),
        Layer(id="figure_n2_hefts_the_spear", img=_hefting(), when=w["spear"]),
        Layer(id="figure_n2_looks_to_the_thorn", img=_thorn(), when=w["thorn"]),
        Layer(id="figure_n3_sets_seed", img=_seed(), when=w["seed"]),
        Layer(id="figure_n3_sorts_the_caps", img=person(N3, "right", CAPS_AT, drop=6), when=w["caps"]),
        Layer(id="figure_n6_tries_the_posts", img=dayeleven_poses.walking_ring(), when=w["posts"]),
    ]


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    "figure_n2_by_fire": (WINDOWS["bedding"], WINDOWS["stage_7"], WINDOWS["shed"], WINDOWS["his_watch"], WINDOWS["spear"], WINDOWS["thorn"], WINDOWS["deer"]),
    "figure_n3_by_fire": (WINDOWS["pelt_ask"], WINDOWS["seed"], WINDOWS["caps"], WINDOWS["drift"], WINDOWS["pot"], WINDOWS["naming"],
                          WINDOWS["bowl"]),
    "figure_n4_by_fire": (WINDOWS["posts_cord"], WINDOWS["old_watch"], WINDOWS["drift"], WINDOWS["sun"]),
    "figure_n5_by_fire": (WINDOWS["stone"],),
    "figure_n6_by_fire": (WINDOWS["posts"], WINDOWS["n6_posts_done"]),
}
"""Each by-the-fire pose and the moment windows that take the person from it: it is back when the window is over."""
