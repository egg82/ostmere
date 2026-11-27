"""The later arrivals at their crews' work (people_layers.py has the rest): each stands where the crew's card is worked
while that card runs, once their join has happened. The reapers stand along the beds' lower edge; the stew and fish crew
stand in a loose arc round the fire's south side, facing it. Road clearing and stakes have no place in the camp (people.py, `whereabouts`).

Story spoilers: never shown to the owner."""
from __future__ import annotations

from daythree_poses import AT_GAP
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
"""Who stands at the fire for the pot and fish: the road crew's pair, the four and the three, and those of them the
hearth crew holds."""
HEARTH_COOKS = {"n19", "n21"}
"""The two of them the smallest-crew rule put in the hearth crew; the rest cook with the road crew."""
HEARTH_REAPERS = {"n8", "n10"}
"""The two of the reapers who work in the hearth crew; the others reap with the field crew."""
FISH = "n14"
"""The one of them whose first job there is the fish (the answer's card); the rest are on the stew."""
REAP_AT = {n: (626.0 + 40 * i, 418.0) for i, n in enumerate(REAPERS)}
COOK_AT: dict[str, tuple[float, float, str]] = {
    "n16": (106, 298, "right"), "n17": (112, 366, "right"),
    "n15": (226, 376, "up"), "n18": (270, 424, "up"), "n19": (316, 372, "up"),
    "n20": (398, 426, "left"), "n21": (442, 376, "left"), "n22": (522, 380, "left"),
}
"""The stew crew at the three places its work is: the wood on the camp's west side (the stacks), the pot below the fire, the
fungus on its east (the birch log). Staggered so no two figures share a box, and clear of the idle row at the fire."""
FISH_AT: tuple[float, float, str] = (AT_GAP[0] + 38, AT_GAP[1] + 3, "up")
"""The fish crew's one: in the gap's mouth, the way down to the stream (`dig_clay` is posed there too), back to the camp."""


def _while(person_id: str, card: str) -> str:
    return f"joined:{person_id}&running:{card}|joined:{person_id}&mix:{card}"


def crew_layers() -> list[Layer]:
    reaping = [Layer(id=f"figure_{n}_reaping", img=person(who, "down", REAP_AT[n]),
                     when=_while(n, "g_hearth_reap" if n in HEARTH_REAPERS else "g_field_reap"))
               for n, who in REAPERS.items()]
    cooking = [Layer(id=f"figure_{n}_at_the_pot", img=person(who, COOK_AT[n][2], COOK_AT[n][:2]),
                     when=_while(n, "g_hearth_fungus_stew" if n in HEARTH_COOKS else "g_road_fungus_stew"))
               for n, who in COOKS.items() if n != FISH]
    fishing = Layer(id=f"figure_{FISH}_fishing", img=person(COOKS[FISH], FISH_AT[2], FISH_AT[:2]),
                    when=_while(FISH, "g_road_fog_fish"))
    return [*reaping, *cooking, fishing]
