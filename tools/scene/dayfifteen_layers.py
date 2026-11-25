"""Day fifteen's layers (content/team/week-three.md, Art; ids from app/ashfall_app/opening/day_fifteen.toml), in the
group build.py splices into its draw order: the hall's ghost while it is built and its four states. Every condition
names an id from that chapter, so nothing here shows before day fifteen.

Story spoilers: never shown to the owner."""
from __future__ import annotations

import dayfifteen_made as made
from output import Layer

STATES = (2, 4, 6, 8)
"""The hall's stages each state shows from (week-three.md, Art: four states)."""
BUILDING = "running:hall|mix:hall"


def made_layers() -> list[Layer]:
    last = len(STATES)
    return [
        Layer(id="hall_ghost", img=made.hall(0), when=BUILDING, until=f"pushes:hall@{STATES[-1]}"),
        *[Layer(id=f"hall_{n}", img=made.hall(n), when=f"pushes:hall@{at}", until=f"pushes:hall@{until}")
          for n, (at, until) in enumerate(zip(STATES, STATES[1:]), start=1)],
        Layer(id=f"hall_{last}", img=made.hall(last), when=f"pushes:hall@{STATES[-1]}"),
    ]
