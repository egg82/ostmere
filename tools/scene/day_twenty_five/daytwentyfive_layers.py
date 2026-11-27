"""Day twenty-five's layer (app/ashfall_app/opening/day_twenty_five.toml), in the group build.py splices into its
draw order. Every condition names an id from that chapter, so nothing here shows before it."""
from __future__ import annotations

from day_twenty_five import daytwentyfive_made as made
from frame.output import Layer


def world_layers() -> list[Layer]:
    return [Layer(id="midden_pit", img=made.midden_pit(), when="running:dig_midden|project:dig_midden")]
