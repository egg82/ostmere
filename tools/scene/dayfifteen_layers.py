"""Days fifteen and sixteen's layers (content/team/week-three.md, Art; ids from
app/ashfall_app/opening/{day_fifteen,day_sixteen}.toml), in the group build.py splices into its draw order: the hall's
ghost while it is built, its four states and its hearth, and her beds' three. Every condition names an id from those
chapters, so nothing here shows before day fifteen.

Story spoilers: never shown to the owner."""
from __future__ import annotations

import dayfifteen_made as made
from output import Layer

STATES = (2, 4, 6, 8)
"""The hall's stages each state shows from (week-three.md, Art: four states)."""
BUILDING = "running:hall|mix:hall"
SOWN = (1, 3, 6)
"""The stages of her sowing each state of the beds shows from: sown, green, ripe (week-three.md, Art: three states)."""


def made_layers() -> list[Layer]:
    last = len(STATES)
    return [
        Layer(id="hall_ghost", img=made.hall(0), when=BUILDING, until=f"pushes:hall@{STATES[-1]}"),
        *[Layer(id=f"hall_{n}", img=made.hall(n), when=f"pushes:hall@{at}", until=f"pushes:hall@{until}")
          for n, (at, until) in enumerate(zip(STATES, STATES[1:]), start=1)],
        Layer(id=f"hall_{last}", img=made.hall(last), when=f"pushes:hall@{STATES[-1]}"),
        Layer(id="hall_hearth", img=made.hall_hearth(), when=f"project:hall_hearth&pushes:hall@{STATES[-1]}"),
        Layer(id="hall_smoke", img=made.hall_smoke(), when=f"project:hall_hearth&pushes:hall@{STATES[-1]}"),
        *[Layer(id=f"beds_{n}", img=made.beds(n), when=f"pushes:n3_sow@{at}", until=f"pushes:n3_sow@{until}")
          for n, (at, until) in enumerate(zip(SOWN, SOWN[1:]), start=1)],
        Layer(id=f"beds_{len(SOWN)}", img=made.beds(len(SOWN)), when=f"pushes:n3_sow@{SOWN[-1]}"),
    ]
