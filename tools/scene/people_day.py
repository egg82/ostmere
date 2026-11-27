"""People at their work by day: a person the content sends to a card's site (`by_day` on a lane,
app/ashfall_app/opening/lane_entries.py) is drawn there, not at the camp fire, while nothing of theirs runs; at dusk and
night they are where they were (the fire, or the hall once it is roofed). The people `by_day` seats at the fire keep their
fire pose. app/tests/test_scene_day.py holds this table to the content.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

from dayeight_poses import BROTHER, HUSBAND
from daytwo_poses import Who, person
from dayfour_poses import N3
from output import Layer
from kit import T
from place import WATCH

Spot = tuple[float, float]


class Work(NamedTuple):
    layer: str
    """The scene layer the person's card is sited at (`site` on the card): the gate checks it is the card's."""
    by_fire: str
    """The person's idle pose at the camp fire, which gives way to this one by day."""
    built: str
    """The condition under which the site is there to stand at."""
    who: Who
    facing: str
    feet: Spot


AT_WORK: dict[str, Work] = {
    "n3": Work("beds_3", "figure_n3_by_fire", "project:n3_sow", N3, "right", (620, 380)),
    "n6": Work("watch_lit", "figure_n6_by_fire", "project:watch_fire|project:n1_build_watch", HUSBAND, "left", (WATCH[0] + 1.9 * T, WATCH[1] + 1.2 * T)),
    "n7": Work("birch_log", "figure_n7_by_fire", "project:woodcutting|running:n1_cut", BROTHER, "left", (452, 226)),
}
"""Each person `by_day` sends to a card's site, by lane."""

HELD_UNDECIDED: frozenset[str] = frozenset({
    "n1", "n2", "n8", "n9", "n10", "n11", "n12", "n13", "n14", "n15", "n16", "n17", "n18", "n19", "n20", "n21", "n22", "n23",
})
"""Person lanes with no `by_day` yet: only shrinks (the check fails on a lane that gained one, and on one that has none and is
not here)."""


def layer_id(person_id: str) -> str:
    return f"figure_{person_id}_at_work"


def _terms(*conds: str | None) -> list[str]:
    """The conjunction of `conds`, each an `|` of `&` terms, as one `|` of `&` terms."""
    out = [""]
    for cond in conds:
        out = [f"{a}&{b}" if a else b for a in out for b in (cond or "always").split("|")]
    return out


def at_work(layers: Iterable[Layer]) -> list[Layer]:
    """`layers` with each person's work pose added: shown as their fire pose is and once the site is there, by day, giving way
    to the same runs; the fire pose gives way to it by day. Run after the fire poses have their runs (`step_aside`)."""
    out = list(layers)
    by_id = {layer["id"]: layer for layer in out}
    for person_id, work in AT_WORK.items():
        fire = by_id[work.by_fire]
        until = "|".join(t for t in (fire.get("until"), "dark") if t)
        out.append(Layer(id=layer_id(person_id), img=person(work.who, work.facing, work.feet),
                         when="|".join(_terms(fire["when"], work.built)), until=until))
        fire["until"] = "|".join(t for t in (fire.get("until"), *(f"{t}&day" for t in _terms(work.built))) if t)
    return out
