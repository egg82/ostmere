"""The scene's grades: the tints the drawn parts are graded with, and the per-layer grade baked into each layer."""
from __future__ import annotations

import kit

GROUND = kit.Grade(sat=0.4, mul=(0.93, 1.0, 1.1), bright=0.88, contrast=0.72)
"""The ground and the waste: cool, desaturated blue-grey ash, low contrast so it recedes."""
CLEARED = kit.Grade(sat=0.4, mul=(0.95, 1.0, 1.1), bright=0.95, contrast=0.8)
STONE = kit.Grade(sat=0.12, mul=(1.0, 1.0, 1.03), bright=0.98, contrast=1.1)
"""The ruin's stone: a neutral grey, apart from the bluer ground."""
WOOD = kit.Grade(sat=0.62, mul=(1.04, 1.0, 0.9), bright=0.9, contrast=1.05)
"""Made things (wood, rack, stool): warm and more saturated than the ground."""
SOIL = kit.Grade(sat=0.5, mul=(0.95, 0.95, 1.0), bright=0.78, contrast=1.0)
"""Turned ground: the pack's soil in a dark, drained brown, the ground the camp worked rather than a thing it built."""
FIRE_HOT = kit.Grade(sat=1.0, mul=(1.15, 1.02, 0.8), bright=1.1, contrast=1.05)
ACCENT = kit.Grade(sat=0.1, mul=(0.97, 1.0, 1.03), bright=1.12, contrast=1.05)
"""Stones carried in and the ring: a brighter cool neutral grey against the dull ground."""
BAKES: dict[str, kit.Grade | None] = {
    "cleared": None, "ruin": None, "roof_posts": STONE, "birch_log": None, "birch_stump": None, "ring": ACCENT, "fireback": STONE, "fire_laid": WOOD, "fire_lit": FIRE_HOT,
    **{f"stones_{i}": ACCENT for i in (1, 2, 3)}, "ridge_shape": None, "rim_haze": None, **{f"valley_fog_{i}": None for i in (1, 2, 3, 4)},
    **{f"stream_steam_{i}": None for i in (1, 2, 3)}, "figure_away_track": None, "prints": None, "smoke_plume": None, "larder": None, "larder_ghost": None,
    "ridge_bare": None, "woodstack": None, "woodstack_ghost": None,
    "track": None, "dead_field": None, "frost": None, **{f"cairns_{i}": None for i in (1, 2, 3)},
    **{f"larder_floor_{i}": None for i in (1, 2, 3)}, "watch_ring": ACCENT, "watch_ring_ghost": ACCENT,
    "fog_dense": None, "fog_haze": None, "kill": None, "wolf_prints": None, "ring_prints": None, "ridge_shapes": None,
    "wood_steam": None, **{f"hearth_stones_{i}": None for i in (1, 2, 3)}, "wolf_edge_1": None, "wolf_edge_2": None,
    "rat_larder": None, "crows_roof": None, "crows_hang": None, **{f"turned_{i}": SOIL for i in (1, 2, 3)},
"turned_pelt": WOOD,
    "ash_drift": None, "road_smoke": None, "wolf_gap": None, "scored_line": None, "fungus_birch": None,
    "ash_heap": None, **{f"ashed_{i}": None for i in (1, 2, 3)}, "gap_ring": ACCENT, "gap_ring_ghost": ACCENT,
    **{f"roof_ash_{r}": None for r in ("bay", "bay2", "lean_to", "n1_shelter", "woodshed", "rack_roof")},
    "hut": None, "hut_ghost": None, **{f"cellar_{i}": None for i in (1, 2, 3, 4)}, "lamp_1": None, "lamp_2": None,
    "lamps_lit": None, "pyre": None, "pyre_flames": FIRE_HOT, "fungus_torn": None, "claw_marks": None, "wolf_sitting": None,
}
"""Per-layer grade baked in (the page's grades sit on top); layers not named take WOOD, figures take CLOTHES."""
