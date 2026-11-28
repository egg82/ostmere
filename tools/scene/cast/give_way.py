"""Week five's moments take people from every pose they could otherwise be drawn in, including the work poses
`people_day.at_work` adds (a crew's member has no fire pose for `people_layers.step_aside` to reach), so this pass runs
after it: a person is drawn in one place.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from day_thirty import daythirty_layers as d30
from day_thirty_one import daythirtyone_layers as d31
from day_thirty_three import daythirtythree_layers as d33
from day_twenty_nine import daytwentynine_layers as d29
from frame.output import Layer

TABLES: tuple[Mapping[str, tuple[str, ...]], ...] = (d29.STEP_ASIDE, d30.STEP_ASIDE, d31.STEP_ASIDE, d33.STEP_ASIDE)
"""Each chapter's poses and the moments that take the person from them."""


def step_aside_late(layers: Iterable[Layer]) -> list[Layer]:
    """`layers` with each pose a chapter's table names hidden while any of its moments holds."""
    out = list(layers)
    by_id = {layer["id"]: layer for layer in out}
    for table in TABLES:
        for layer_id, moments in table.items():
            layer = by_id[layer_id]
            layer["until"] = "|".join(t for t in (layer.get("until"), *moments) if t)
    return out
