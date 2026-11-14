"""The scene's depth: which layers the page sorts by their ground contact, and the `base` each carries.

The page draws layers in manifest order, except that layers with a `base` (the y of the art's ground contact) are
re-sorted among themselves by it, so a figure whose feet are above a prop's foot stands behind it. Three bands, in
this order: FLAT ground (no base, always underneath), the sorted layers (figures and everything standing), and
the overlays (lights, fog, smoke, ash; no base, always on top). A layer that is part of another's art (a roof's ash,
a pelt in a bay, a build's ghost) takes the larger of its own bottom and its parent's base, so the sort keeps it
above the parent it was drawn on. The haze over the low ground (the rim's, each fog band, each column of steam) is
sorted too, each at the row it lies on, so a figure out there is behind the haze nearer than its feet.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING

from dayone_world import FOG_BANDS, STEAM, fog_ground, steam_ground
from place import LIP

if TYPE_CHECKING:
    from output import Entry

FLAT = frozenset({
    "ruin", "ridge_shape", "ridge_bare", "track", "dead_field", "frost", "cairns_1",
    "cairns_2", "cairns_3", "kill", "wolf_prints", "ring_prints", "ridge_shapes", "road_smoke",
    "cleared", "prints", "ring", "fire_laid",
    "clay_hearth_1", "clay_hearth_2", "clay_hearth_3", "hearth_stones_1", "hearth_stones_2", "hearth_stones_3",
    "larder_floor_1", "larder_floor_2", "larder_floor_3", "raised_bed_1",
    "raised_bed_2", "raised_bed_3", "turned_1", "turned_2", "turned_3", "turned_pelt", "ashed_1", "ashed_2",
    "ashed_3", "pelt_pegged_1", "pelt_pegged_2", "gap_ring", "gap_ring_ghost", "watch_ring", "watch_ring_ghost",
    "cellar_1", "cellar_2", "cellar_3", "cellar_4",
})
"""Lie on the ground or are the backdrop: drawn first, in manifest order, under everything that stands."""

OVERLAY = frozenset({"fog_dense", "fog_haze", "ash_drift", "smoke_plume", "wood_steam", "ash"})
"""Not things in the scene (a layer with a blend is one too): drawn last, in manifest order."""

BASE_OVERRIDE: Mapping[str, int] = {
    "figure_lying_apart": 204, "vigil_body": 204, "rim_haze": int(LIP), "wolf_gap": int(LIP) + 1,
    **{f"valley_fog_{i + 1}": fog_ground(band) for i, band in enumerate(FOG_BANDS)},
    **{f"stream_steam_{i + 1}": steam_ground(spot) for i, spot in enumerate(STEAM)},
}
"""Layers whose depth is not their lowest pixel: a body lying by the larder stays in front of it (the larder's base);
the haze rising at the rim lies at the camp floor's lip, in front of everything out on the low ground, and the wolves in
the gap stand on the rim in front of it; each band of fog
and column of steam lies where it touches the low ground, not where its blur ends, so a figure on the track is behind
the haze nearer than its feet and in front of the haze beyond them."""

PART_OF: Mapping[str, str] = {
    "damp_wood_2": "damp_wood_1", "damp_wood_3": "damp_wood_1", "dry_wood_2": "dry_wood_1", "stones_2": "stones_1",
    "stones_3": "stones_1", "rack": "wood_drying", "rack_roof_2": "rack_roof_1", "roof_ash_rack_roof": "rack_roof_2",
    "roof_ash_bay": "bay", "roof_ash_bay2": "bay2", "roof_ash_lean_to": "lean_to", "roof_ash_n1_shelter": "n1_shelter",
    "roof_ash_woodshed": "woodshed_1", "woodshed_2": "woodshed_1", "woodshed_3": "woodshed_1",
    "pelt_in_bay_1": "bay", "pelt_in_bay_2": "bay2", "pelt_in_bay_3": "lean_to", "spear_leaning": "n1_shelter",
    "lean_to_ghost": "lean_to", "larder_ghost": "larder", "smoke_rack_ghost": "smoke_rack",
    "n1_shelter_ghost": "n1_shelter", "woodstack_ghost": "woodstack", "bay_ghost": "bay", "bay2_ghost": "bay2",
    "hut_ghost": "hut", "meat_on_rack": "smoke_rack", "meat_on_rack_again": "smoke_rack", "fungus_birch": "birch_log",
    "fungus_torn": "birch_log", "claw_marks": "birch_log", "birch_stump": "birch_log", "pyre_flames": "pyre",
    "lamp_1": "palisade_9", "lamp_2": "palisade_9", "lamps_lit": "palisade_9", "gap_laid": "gap_ring", "gap_lit": "gap_ring",
    "watch_laid": "watch_ring", "watch_lit": "watch_ring", "clay_hearth_2_front": "clay_hearth_1_front",
    "clay_hearth_3_front": "clay_hearth_2_front",
}
"""Layers drawn as part of another layer's art, to the layer they belong to."""


def is_overlay(entry: Entry) -> bool:
    return entry["id"] in OVERLAY or bool(entry.get("blend"))


def arrange(entries: Sequence[Entry], bottoms: Mapping[str, int]) -> list[Entry]:
    """The entries in band order (flat, sorted, overlay), each sorted one with its `base`; `bottoms` is each layer's
    lowest drawn pixel. Order inside a band is the manifest's own."""
    ids = {e["id"] for e in entries}
    stale = (FLAT | OVERLAY | BASE_OVERRIDE.keys() | PART_OF.keys() | set(PART_OF.values())) - ids
    if stale:
        raise ValueError(f"depth names layers the scene no longer has: {sorted(stale)}")
    flat = [e for e in entries if e["id"] in FLAT]
    over = [e for e in entries if is_overlay(e) and e["id"] not in FLAT]
    sorted_band = [e for e in entries if e["id"] not in FLAT and not is_overlay(e)]
    bases: dict[str, int] = {}

    def base_of(layer_id: str) -> int:
        if layer_id not in bases:
            parent = PART_OF.get(layer_id)
            own = BASE_OVERRIDE.get(layer_id, bottoms[layer_id])
            bases[layer_id] = max(own, base_of(parent)) if parent else own
        return bases[layer_id]

    for e in sorted_band:
        e["base"] = base_of(e["id"])
    return [*flat, *sorted_band, *over]


PASSES = ("base", "ungraded", "front")
"""The page's passes, in the order it draws them (scene/manifest.ts passOf): each over everything before it."""


def pass_of(entry: Entry) -> str:
    return "front" if entry.get("front") else "ungraded" if entry.get("ungraded") else "base"


HELD_MISDRAWN = frozenset({("figure_n2_guarding", "lamps_lit")})
"""Pairs misdrawn today that no single pass can fix, held so the check stays on for the rest: may only shrink. The
guard stands before the lit lamps on one night and behind the gap's fires on another; a layer per night would fix it."""


def misdrawn(entries: Sequence[Entry], overlap: Callable[[str, str], bool]) -> list[tuple[str, str]]:
    """Pairs (near, far) of `entries` (arranged, all shown at once) where the depth puts `near` in front of `far` but
    the page draws `far` over it where their pixels meet (`overlap`): an ungraded or front pass laid over something
    standing nearer. Flat ground is behind everything standing; lights and overlays are not things and are skipped."""
    order = draw_order(entries)
    drawn = {e["id"]: (PASSES.index(pass_of(e)), i) for i, e in enumerate(order)}
    things = [e for e in order if not is_overlay(e)]
    deep = {e["id"]: (1, e["base"], drawn[e["id"]][1]) if "base" in e else (0, 0, drawn[e["id"]][1]) for e in things}
    return [(a["id"], b["id"]) for a in things for b in things
            if deep[a["id"]] > deep[b["id"]] and drawn[a["id"]] < drawn[b["id"]] and overlap(a["id"], b["id"])]


def draw_order(entries: Sequence[Entry]) -> list[Entry]:
    """The order the page draws in: layers with a `base` re-sorted by it (ties keep manifest order), each into a
    slot a based layer held, so layers without a base never move. The page's own rule (scene/manifest.ts)."""
    slots = [i for i, e in enumerate(entries) if "base" in e]
    ranked = sorted((entries[i] for i in slots), key=lambda e: e.get("base", 0))
    out = list(entries)
    for slot, entry in zip(slots, ranked):
        out[slot] = entry
    return out
