"""The one-off moments of people who are not the later arrivals (people_layers.py has those): each is a window on a
count-up clock the moment's own outcome starts (`store:<clock>@1..<n>`, twentieths of a game hour), the person stood where
the line puts them for its few minutes. The by-the-fire pose gives way to each window (`STEP_ASIDE`), whatever order the
windows come in. A figure here is cut from the poses the camp already has.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageOps

import dayeleven_poses
import dayfour_poses as poses4
from dayfour_made import SHED, SPEAR_FOOT
from daythree_poses import N2, laying, staff
from daytwo_poses import person
from dayfour_poses import N3, spear
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
}
"""Each moment's window. The seed's is the pair's own three-hour count, which the trigger reads at 20; the rest are
clocks of the moment's own, started by the outcome that tells it."""

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


def moment_layers() -> list[Layer]:
    w = WINDOWS
    return [
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
    "figure_n2_by_fire": (WINDOWS["shed"], WINDOWS["his_watch"], WINDOWS["spear"], WINDOWS["thorn"]),
    "figure_n3_by_fire": (WINDOWS["seed"], WINDOWS["caps"]),
    "figure_n4_by_fire": (WINDOWS["old_watch"],),
    "figure_n6_by_fire": (WINDOWS["posts"],),
}
"""Each by-the-fire pose and the moment windows that take the person from it: it is back when the window is over."""
