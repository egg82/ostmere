"""The hall lived in: once it is roofed, the people the content lodges there (`lodging` on a lane,
app/ashfall_app/opening/lane_entries.py) leave the camp fire at dusk and night, and a few of them are seen at its door
going in and out, the windows lit (`hall_lit`) and the chimney smoking (`hall_smoke`). By day they are as they were:
at the fire or at their work. app/tests/scene/test_scene_lodging.py holds this table to the content.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from collections.abc import Iterable

from day_eight.dayeight_poses import HUSBAND, WOMAN
from day_two.daytwo_poses import Who, person
from audits.builds import ROOFED
from frame.output import Layer
from frame.conditions import in_dark

INDOORS = in_dark(ROOFED)

IDLE: dict[str, tuple[str, ...]] = {
    "n1": ("figure_n1_by_fire", "figure_n1_by_fire_day_3", "figure_n1_far_side"),
    "n2": ("figure_n2_by_fire",),
    "n3": ("figure_n3_by_fire",),
    "n4": ("figure_n4_by_fire",),
    "n5": ("figure_n5_by_fire", "figure_child_by_fire"),
    "n6": ("figure_n6_by_fire",),
    "n7": ("figure_n7_by_fire",),
}
"""Each lodger's idle poses at the camp fire (a person who works is at the work): they give way at dusk and night. The
child is the household's, shown with the mother."""

AT_THE_DOOR: tuple[tuple[str, Who, str, tuple[float, float]], ...] = (
    ("n5", WOMAN, "up", (664, 262)),
    ("n6", HUSBAND, "down", (738, 260)),
)
"""Two seen at the hall's door at dusk and night, beside the bedesman who stands there: who, their sheet, the way they face
(going in, coming out) and their feet."""


def door_layers() -> list[Layer]:
    return [Layer(id=f"figure_{n}_at_hall_door_dark", img=person(who, facing, feet), when=INDOORS)
            for n, who, facing, feet in AT_THE_DOOR]


def at_home(layers: Iterable[Layer]) -> list[Layer]:
    """`layers` with each lodger's idle poses hidden at dusk and night once the hall is roofed."""
    gone = {i for ids in IDLE.values() for i in ids}
    out = list(layers)
    for layer in out:
        if layer["id"] in gone:
            layer["until"] = "|".join(t for t in (layer.get("until"), INDOORS) if t)
    return out
