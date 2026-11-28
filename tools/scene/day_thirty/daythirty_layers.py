"""Day thirty's layers (app/ashfall_app/rules/days/day_thirty.toml), in the groups build.py splices into its draw order:
the pack in the yard on night 30 (`yard:pack`), the player calling the heat out from the hall's door (`door:call`, A42's
run), the ward worked at the gate (`ward_gate`'s run), and B23's morning: the yard's tracks and the tracker reading them
(`track:read`). Every condition names an id from that chapter, so nothing here shows before day thirty. The night's
grade is in frame/grades.py.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

from cast import people_day, people_hall
from day_thirty import daythirty_poses as poses
from draw.parts import FLICKER, firelight
from frame.output import Layer

NIGHT_30 = "store:dawn_31@0..12"
"""From Y6 to dawn 31's twelfth hour (`dawn_31` counts them from Y6, as night 30's clock does)."""
PACK = f"feature:pack_yard&{NIGHT_30}"
"""Y6's night: the pack sat in the yard facing the hall's door, gone at dawn."""
CALL = "running:call_pack"
WARD = "running:ward_gate|mix:ward_gate"
AFTER_CALL = "feature:pack_called&store:call_clock@0..6"
"""B23's first hours (`call_clock` counts them from B23) until Y8: the yard's tracks."""
READING = "feature:pack_called&store:call_clock@0..3"
"""B23's first three hours: the tracker over the tracks."""
TRACKER_LANES = ("n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10", "n11", "n12", "n13", "n14", "n15", "n23")
"""The lanes B22's cast can pick (a lane with `{lane}_walk_ashwood` or `{lane}_forage`, day_twenty_nine.toml `t_b22`):
the cast unlocks `tracker_<lane>`, which is what takes that person from their other poses while the tracker reads."""
OTHER_POSES: dict[str, tuple[str, ...]] = {
    "n2": ("figure_n2_guarding",), "n13": ("figure_n13_outside_ring",), "n23": ("figure_n23_at_hall_door",),
}
"""Poses a candidate stands in by day that neither the fire's idle table nor the work table names."""


def world_layers() -> list[Layer]:
    return [Layer(id="yard_tracks", img=poses.yard_tracks(), when=AFTER_CALL)]


def figure_layers() -> list[Layer]:
    return [
        Layer(id="wolves_yard_pack", img=poses.pack_in_the_yard(), when=PACK),
        Layer(id="figure_door_call", img=poses.door_call(), when=CALL),
        Layer(id="figure_warding_the_gate", img=poses.warding_the_gate(), when=WARD),
        Layer(id="figure_track_read", img=poses.tracker_reading(), when=READING),
    ]


def light_layers() -> list[Layer]:
    return [Layer(id="firelight_dusk_30", flicker=FLICKER, sound="evening", img=firelight(0.7),
                  when=f"action:night_30&{NIGHT_30}", blend="screen", ungraded=True)]


def _tracker_poses() -> dict[str, tuple[str, ...]]:
    out: dict[str, tuple[str, ...]] = {}
    for lane in TRACKER_LANES:
        poses_of = (*people_hall.IDLE.get(lane, ()), *OTHER_POSES.get(lane, ()),
                    *((people_day.layer_id(lane),) if lane in people_day.AT_WORK else ()))
        for layer_id in poses_of:
            out[layer_id] = (*out.get(layer_id, ()), f"feature:tracker_{lane}&{READING}")
    return out


def _merged(*tables: dict[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    out: dict[str, tuple[str, ...]] = {}
    for table in tables:
        for layer_id, moments in table.items():
            out[layer_id] = (*out.get(layer_id, ()), *moments)
    return out


STEP_ASIDE = _merged(
    {"figure_on_stool": (CALL, WARD), "figure_by_fire": (CALL, WARD), "figure_n23_at_hall_door": (CALL, PACK),
     "figure_n5_at_hall_door_dark": (PACK,), "figure_n6_at_hall_door_dark": (PACK,)},
    _tracker_poses(),
)
"""The player's seat gives way to the call and the ward; the door's people go in while the pack sits facing it and the
player stands in it; the cast tracker leaves their other poses while reading the tracks."""
