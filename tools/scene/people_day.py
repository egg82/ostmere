"""People at their work by day: a person the content sends to a card's site (`by_day` on a lane,
app/ashfall_app/opening/lane_entries.py) is drawn there, not at the camp fire, while nothing of theirs runs; at dusk and
night they are where they were (the fire, or the hall once it is roofed). The people `by_day` seats at the fire keep their
fire pose. A person with no idle pose at the fire (a crew's member) stands, by day, where their crew's pose has them at work. app/tests/test_scene_day.py holds this table to the content.

Story spoilers: never shown to the owner."""
from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

from dayeight_poses import BROTHER, HUSBAND
from daytwo_poses import Who, person
from dayfour_poses import N2_WATCH, N3
from daythree_poses import N2
from output import Layer
from kit import T
from people_crews import COOK_AT, COOKS, REAP_AT, REAPERS
from people_moments import ARRIVALS
from place import WATCH

Spot = tuple[float, float]


class Work(NamedTuple):
    layer: str
    """The scene layer the person's card is sited at (`site` on the card): the gate checks it is the card's."""
    by_fire: str | None
    """The person's idle pose at the camp fire, which gives way to this one by day; none for a crew's member, who is
    drawn nowhere idle today."""
    built: str | None
    """The condition under which the site is there to stand at; none takes the site layer's own."""
    who: Who
    facing: str
    feet: Spot
    crew: str | None = None
    """For a crew's member, their pose while the crew's card runs (`people_crews`): this one gives way to it."""


AT_WORK: dict[str, Work] = {
    "n3": Work("beds_3", "figure_n3_by_fire", "project:n3_sow", N3, "right", (618, 352)),
    "n6": Work("watch_lit", "figure_n6_by_fire", "project:watch_fire|project:n1_build_watch", HUSBAND, "left", (WATCH[0] + 1.9 * T, WATCH[1] + 1.2 * T)),
    "n7": Work("birch_log", "figure_n7_by_fire", "project:woodcutting|running:n1_cut", BROTHER, "left", (452, 226)),
    "n2": Work("watch_lit", "figure_n2_by_fire", "project:watch_fire|project:n1_build_watch", N2, "up", N2_WATCH),
    **{n: Work("beds_3", None, None, REAPERS[n], "down", REAP_AT[n], f"figure_{n}_reaping") for n in ("n8", "n9", "n10")},
    "n12": Work("stakes_1", None, None, ARRIVALS["n12"], "left", (700, 350), "figure_n12_reaping"),
    "n14": Work("fire_lit", None, None, ARRIVALS["n14"], "right", (150, 352), "figure_n14_fishing"),
    "n15": Work("smoke_rack", None, None, ARRIVALS["n15"], "down", (150, 232), "figure_n15_at_the_pot"),
    **{n: Work("fire_lit", None, None, COOKS[n], COOK_AT[n][2], COOK_AT[n][:2], f"figure_{n}_at_the_pot")
       for n in ("n16", "n17", "n18", "n19", "n20", "n21", "n22")},
}
"""Each person `by_day` sends to a card's site, by lane."""

HELD_UNDECIDED: frozenset[str] = frozenset({"n11", "n13", "n23"})
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
    """`layers` with each person's work pose added. A person with an idle pose at the fire: shown as that pose is and once the
    site is there, by day, giving way to the same runs, and the fire pose gives way to it by day. A crew's member: shown from
    their join once the site is there, by day, giving way to their crew pose. Run after the fire poses have their runs
    (`step_aside`)."""
    out = list(layers)
    by_id = {layer["id"]: layer for layer in out}
    for person_id, work in AT_WORK.items():
        built = work.built or by_id[work.layer]["when"]
        img = person(work.who, work.facing, work.feet)
        if work.by_fire is None:
            assert work.crew is not None, person_id
            out.append(Layer(id=layer_id(person_id), img=img, when="|".join(_terms(f"joined:{person_id}", built)),
                             until=f"dark|{by_id[work.crew]['when']}"))
            continue
        fire = by_id[work.by_fire]
        until = "|".join(t for t in (fire.get("until"), "dark") if t)
        out.append(Layer(id=layer_id(person_id), img=img, when="|".join(_terms(fire["when"], built)), until=until))
        fire["until"] = "|".join(t for t in (fire.get("until"), *(f"{t}&day" for t in _terms(built))) if t)
    return out
