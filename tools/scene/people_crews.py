"""The later arrivals at their crews' work (people_layers.py has the rest): each stands where the crew's card is worked
while that card runs, once their join has happened. The reapers stand along the beds' lower edge; the stew and fish crew
stand in a loose arc round the fire's south side, facing it. Road clearing and stakes have no place in the camp (people.py, `whereabouts`).

Story spoilers: never shown to the owner."""
from __future__ import annotations

from daytwo_poses import Who, person
from output import Layer
from people_moments import ARRIVALS, SHEETS, SINGERS

REAPERS: dict[str, Who] = {"n8": SINGERS[0], "n9": SINGERS[1], "n10": SINGERS[2], "n12": ARRIVALS["n12"]}
"""Women in a red dress, a blue one and a purple hood, and a woman in a red dress: the crew that reaps the beds."""
COOKS: dict[str, Who] = {
    "n14": ARRIVALS["n14"], "n15": ARRIVALS["n15"],
    "n16": (SHEETS + "npc1.png", 0), "n17": (SHEETS + "npc1.png", 5), "n18": (SHEETS + "npc2.png", 1), "n19": (SHEETS + "npc1.png", 3),
    "n20": (SHEETS + "npc4.png", 0), "n21": (SHEETS + "npc4.png", 1), "n22": (SHEETS + "npc4.png", 6),
}
"""Who stands at the fire for the road crew's pot and fish: the pair, the four and the three."""
FISH = "n14"
"""The one of them whose first job there is the fish (the answer's card); the rest are on the stew."""
REAP_AT = {n: (628.0 + 30 * i, 418.0) for i, n in enumerate(REAPERS)}
COOK_AT: dict[str, tuple[float, float, str]] = {
    "n14": (146, 346, "right"), "n15": (172, 380, "right"), "n16": (208, 358, "up"), "n17": (236, 398, "up"),
    "n18": (270, 380, "up"), "n19": (312, 352, "up"), "n20": (346, 358, "left"), "n21": (392, 372, "left"),
    "n22": (424, 346, "left"),
}
"""A loose arc round the fire's south side, uneven, each turned toward it."""


def _while(person_id: str, card: str) -> str:
    return f"joined:{person_id}&running:{card}|joined:{person_id}&mix:{card}"


def crew_layers() -> list[Layer]:
    reaping = [Layer(id=f"figure_{n}_reaping", img=person(who, "down", REAP_AT[n]), when=_while(n, "g_field_reap"))
               for n, who in REAPERS.items()]
    cooking = [Layer(id=f"figure_{n}_at_the_pot", img=person(who, COOK_AT[n][2], COOK_AT[n][:2]),
                     when=_while(n, "g_road_fog_fish" if n == FISH else "g_road_fungus_stew"))
               for n, who in COOKS.items()]
    return [*reaping, *cooking]
