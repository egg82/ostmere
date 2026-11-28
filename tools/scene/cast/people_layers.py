"""The later people the camp shows, where an outcome's `whereabouts` names them (people.py): the weeks' one-off moments
(a pose for a clock's few hours, a card's run) and the arrivals after the hall, each on a spot of the camp. Every
condition names an id from the chapters, so nothing here shows early; a by-the-fire pose that would double one of these
gives way to it (`STEP_ASIDE`).

Story spoilers: never shown to the owner."""
from __future__ import annotations

from collections.abc import Iterable

from PIL import Image, ImageDraw, ImageFilter

from day_four import dayfour_poses
from day_four import dayfour_world as world4
from draw import kit
from cast import people_crews
from cast import people_hall
from cast import people_moments
from cast.people_moments import SINGERS
from day_eight.dayeight_poses import BROTHER, HUSBAND, WOMAN, n4_twisting
from day_three.daythree_made import POTS
from day_three.daythree_poses import N2
from day_four.dayfour_poses import N3, N4, sack
from day_two.daytwo import cut
from day_two.daytwo_poses import Who, person
from draw.kit import FORT, T
from audits.builds import ROOFED
from frame.output import Layer
from cast.people_hall import INDOORS
from draw.place import BY_FIRE, SEAT, WATCH, canvas
from draw.tints import WOOD

SHEETS = "timefantasy_characters/timefantasy_characters/sheets/"
N13: Who = (SHEETS + "npc1.png", 6)
"""A dark-haired man in a grey coat."""
N23: Who = (SHEETS + "chara3.png", 6)
"""A bald old man in a tan robe."""

Spot = tuple[float, float]
BEDS_EDGE: Spot = (626, 372)
BEDS_PATH: Spot = (630, 348)
SUN_EDGE: Spot = (742, 405)
WARM_EDGE: Spot = (170, 330)
POT_LEFT: Spot = (368, 214)
POT_RIGHT: Spot = (372, 232)
HAULED_AT: Spot = (392, 222)
RACKS: Spot = (218, 268)
STONE: Spot = (BY_FIRE[0] - 10, BY_FIRE[1] + 8)
WOOD_EDGE: Spot = (704, 266)
HEARTH_WATCH: Spot = (WATCH[0] - 0.65 * T, WATCH[1] + 3.0 * T)
"""Where the hearth crew's watcher keeps the watch fire: its west side, below the others' seats (`dayfour_poses.N2_WATCH`)."""
STRANGER_IN: Spot = (372, 160)
NAMING_AT: Spot = (STRANGER_IN[0] - 26, STRANGER_IN[1] + 6)
BOWL_AT: Spot = (SEAT[0] + 22, SEAT[1] + 2)
STRANGER_APART: Spot = (190, 300)
HALL_DOOR: Spot = (700, 240)
AT_BOARD: Spot = (352, 320)
"""Before the tally stump (dayeleven_made.BOARD_AT), facing it."""
NAMES_AT: Spot = (262, 292)
AT_STONE: Spot = (STONE[0] + 22, STONE[1] - 4)
"""Kneeling at the camp stone from its far side, clear of whoever sits apart below it."""
"""Standing on the fire's near side, facing the town round it: night 28, after A40."""
SINGING_AT: tuple[Spot, ...] = ((668, 240), (692, 246), (716, 240))
HALL_GLOW: tuple[tuple[Spot, int], ...] = (((708, 205), 34), ((676, 176), 18), ((742, 176), 18))
"""Where the hall's door and windows are, and how far each one's light reaches."""



def _glow() -> Image.Image:
    """The hall's door and windows lit from inside: warm discs, softened."""
    img = canvas()
    d = ImageDraw.Draw(img)
    for (x, y), r in HALL_GLOW:
        d.ellipse((x - r, y - r // 2, x + r, y + r // 2), fill=(255, 168, 70, 150))
        d.ellipse((x - r // 3, y - r // 5, x + r // 3, y + r // 5), fill=(255, 214, 140, 230))
    return img.filter(ImageFilter.GaussianBlur(5))


def _hauled(walls: Image.Image) -> Image.Image:
    """The newcomer in the gap hauling a kill in beside him: the downed deer, cut out of the scene's own art."""
    kill = world4.kill(walls)
    box = kill.getchannel("A").getbbox()
    assert box is not None
    prey = kill.crop(box)
    return person(N2, "down", HAULED_AT, held=[(prey, 6, -prey.height + 4)])


def _setting_bowl() -> Image.Image:
    """The woman at the player's place by the fire, setting a wooden bowl down."""
    bowl = kit.grade(cut(FORT, POTS[1]), **WOOD)
    return person(N3, "left", BOWL_AT, held=[(bowl, -bowl.width - 6, -bowl.height - 2)])


def _carrying(feet: Spot) -> Image.Image:
    bag = sack()
    return person(N3, "left", feet, held=[(bag, -bag.width - 4, -bag.height - 8)])


def people_layers(walls: Image.Image) -> list[Layer]:
    w = people_moments.WINDOWS
    field, picking = "running:g_field_forage|mix:g_field_forage", "running:g_field_pick|mix:g_field_pick"
    watching = "running:g_hearth_watch|mix:g_hearth_watch"
    return [
        Layer(id="figure_n3_sowing", img=person(N3, "right", BEDS_EDGE, drop=9), when="running:n3_sow|mix:n3_sow"),
        Layer(id="figure_n3_pulled_rows", img=_carrying(BEDS_PATH), when="store:rows_black_left"),
        Layer(id="figure_n4_in_the_sun", img=person(N4, "up", SUN_EDGE), when=w["sun"]),
        Layer(id="figure_n2_at_warm_edge", img=person(N2, "right", WARM_EDGE), when=w["deer"]),
        Layer(id="hall_lit", img=_glow(), when=f"action:table&{ROOFED}|{INDOORS}", blend="screen", ungraded=True),
        Layer(id="figure_n3_at_pot", img=person(N3, "left", POT_LEFT), when=w["pot"]),
        Layer(id="figure_n2_hauling_in", img=_hauled(walls), when="store:ashwood_trips", until="store:ashwood_trips@2"),
        Layer(id="figure_n3_at_racks", img=person(N3, "left", RACKS), when="running:n3_wash_meat|mix:n3_wash_meat"),
        Layer(id="figure_n5_at_stone", img=person(WOMAN, "right", STONE, drop=9), when=w["stone"]),
        Layer(id="figure_n13_arrived", img=person(N13, "down", STRANGER_IN), when="feature:stranger_home",
              until="feature:bedesman_home"),
        Layer(id="figure_n13_outside_ring", img=person(N13, "right", STRANGER_APART), when="feature:bedesman_home"),
        Layer(id="figure_n23_at_hall_door", img=person(N23, "down", HALL_DOOR), when="feature:bedesman_home"),
        Layer(id="figure_n23_at_board", img=person(N23, "up", AT_BOARD), when=w["board"]),
        Layer(id="figure_n23_at_stone", img=person(N23, "left", AT_STONE, drop=9), when=w["hands"]),
        Layer(id="figure_n23_says_the_names", img=person(N23, "up", NAMES_AT), when="project:sit_names&dark", front=True),
        Layer(id="figure_n5_at_wood_edge", img=person(WOMAN, "left", WOOD_EDGE), when=field),
        Layer(id="figure_n6_at_the_watch_fire", img=person(HUSBAND, "up", HEARTH_WATCH), when=watching),
        Layer(id="figure_n7_at_pot", img=person(BROTHER, "left", POT_RIGHT), when=picking),
        Layer(id="figure_n3_works_ash_in", img=dayfour_poses.n3_digging(), when=w["drift"]),
        Layer(id="figure_n4_rolls_cord", img=n4_twisting(), when=w["drift"]),
        Layer(id="figure_n3_names_the_stranger", img=person(N3, "right", NAMING_AT), when=w["naming"]),
        Layer(id="figure_n3_sets_the_bowl", img=_setting_bowl(), when=w["bowl"]),
        *[Layer(id=f"figure_n{n}_singing", img=person(who, "down", at), when=f"{w['singing']}&answered:o_choir")
          for n, who, at in zip((8, 9, 10), SINGERS, SINGING_AT)],
        *people_hall.door_layers(),
        *people_moments.moment_layers(),
        *people_crews.crew_layers(),
    ]


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    "figure_n3_by_fire": ("running:n3_sow|mix:n3_sow", "store:rows_black_left", "running:n3_wash_meat|mix:n3_wash_meat"),
    "figure_n5_by_fire": ("running:g_field_forage|mix:g_field_forage",),
    "figure_n6_by_fire": ("running:g_hearth_watch|mix:g_hearth_watch",),
    "figure_n7_by_fire": ("running:g_field_pick|mix:g_field_pick",),
    "figure_n5_at_hall_door_dark": ("running:g_field_forage|mix:g_field_forage",),
    "figure_n6_at_hall_door_dark": ("running:g_hearth_watch|mix:g_hearth_watch",),
    "figure_n13_arrived": (people_moments.WINDOWS["fiddle_2"],),
    "figure_n23_at_hall_door": (people_moments.WINDOWS["board"], people_moments.WINDOWS["hands"], "project:sit_names&dark"),
}
"""Each by-the-fire pose, each lodger seen at the hall's door, and the stranger at the gate, with the runs and moments
that take the person from it: it gives way to them (a person is drawn in one place; the stranger steps back while the
next newcomers come in at the gate)."""


def _join(*terms: str | None) -> str:
    return "|".join(t for t in terms if t)


def step_aside(layers: Iterable[Layer]) -> list[Layer]:
    """`layers` with each by-the-fire pose giving way to the runs above and the moment windows (people_moments.py)."""
    out = list(layers)
    by_id = {layer["id"]: layer for layer in out}
    for layer_id in STEP_ASIDE.keys() | people_moments.STEP_ASIDE.keys():
        runs = (*STEP_ASIDE.get(layer_id, ()), *people_moments.STEP_ASIDE.get(layer_id, ()))
        by_id[layer_id]["until"] = _join(by_id[layer_id].get("until"), *runs)
    return out
