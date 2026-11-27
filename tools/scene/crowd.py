"""No two figures drawn on top of each other: the boxes of the figures a stage shows (the alpha-trimmed art each layer is
cut to) never meet, bar the pairs held below. Checked at every stage by `output.check_crowd`, so a crew or watch spread
over one fire has to be spaced out, not stacked."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from output import Entry

HELD: frozenset[tuple[str, str]] = frozenset({
    ("figure_n1_foraging_day_3", "figure_walking_edge"),
    ("figure_hand_on_stone", "figure_n2_by_fire"),
    ("figure_child_at_gate", "figure_n5_at_gate"),
    ("figure_n1_far_side", "figure_sitting_apart"),
    ("figure_n5_at_gate", "figure_n6_at_gate"),
    ("figure_n6_at_gate", "figure_n7_at_gate"),
    ("figure_child_by_fire", "figure_n5_by_fire"),
    ("figure_n6_by_fire", "figure_n7_by_fire"),
    ("figure_n3_at_pot", "figure_on_stool"),
    ("figure_n7_at_pot", "figure_on_stool"),
    ("figure_n10_singing", "figure_n6_at_hall_door_dark"),
    ("figure_n10_singing", "figure_n9_singing"),
    ("figure_n5_at_hall_door_dark", "figure_n8_singing"),
    ("figure_n5_at_hall_door_dark", "figure_n9_singing"),
    ("figure_n8_singing", "figure_n9_singing"),
    ("figure_n13_arrived", "figure_n3_names_the_stranger"),
    ("figure_n3_sets_the_bowl", "figure_on_stool"),
    ("figure_n3_holds_out_a_hand", "figure_n6_by_fire"),
    ("figure_n3_holds_out_a_hand", "figure_n7_by_fire"),
    ("figure_n3_holds_out_a_hand", "figure_on_stool"),
    ("figure_n10_at_the_gate", "figure_n9_at_the_gate"),
    ("figure_n8_at_the_gate", "figure_n9_at_the_gate"),
    ("figure_n11_at_the_gate", "figure_n12_at_the_gate"),
    ("figure_n14_at_the_gate", "figure_n15_at_the_gate"),
})
"""Pairs of figure layers (sorted) whose boxes meet at some stage today, held so the check stays on for the rest: may only
shrink."""


def is_figure(entry: Entry) -> bool:
    return entry["id"].startswith("figure_")


def overlapping(shown: Sequence[Entry], size: Callable[[Entry], tuple[int, int]]) -> list[tuple[str, str]]:
    """Pairs of figure layers (sorted ids) of `shown` (all shown at once) whose boxes share any area; `size` is a layer's
    drawn width and height."""
    boxes = [(e["id"], e["x"], e["y"], e["x"] + size(e)[0], e["y"] + size(e)[1]) for e in shown if is_figure(e)]
    return sorted({(min(a[0], b[0]), max(a[0], b[0])) for i, a in enumerate(boxes) for b in boxes[i + 1:]
                   if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]})
