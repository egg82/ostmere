"""Day thirty-one's layers (app/ashfall_app/rules/days/day_thirty_one.toml), in the groups build.py splices into its draw
order: Y8's morning at the hall (the bar that shut the larder's door leaning on the wall), the iron latch on the door from
the latch's last stage, the cat on the hall's ridge (`ridge:cat`, Y11's visit), and SL40's n3 at the racks. Every
condition names an id from that chapter, so nothing here shows before day thirty-one.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

from day_four.dayfour_poses import N3
from day_thirty_one import daythirtyone_made as made
from day_two.daytwo_poses import person
from frame.output import Layer

RAIDED = "feature:larder_raided&store:call_clock@6..10"
"""Y8 (`call_clock` 6) and the morning's next hours: the door found open, its bar lifted out and leant on the wall."""
LATCHED = "pushes:iron_latch@4"
"""The latch's last stage (its cap): from then it is on the door."""
CAT = f"{LATCHED}&feature:larder_raided&day"
"""Y11 lands at the latch's last stage once the larder was raided, and the cat is on the ridge by day from then: no clock
in the content ends the visit, so the cat stays the camp's."""
SCRAPES_AT = (150, 289)
"""n3's feet below the smoke rack, facing it, bent to the meat (her frame cut short): between the crew at the pot above
and the fisher below, clear of whoever sits apart at the fire."""
SCRAPING = "store:call_clock@14..18"
"""SL40 (`t_scrape` at `call_clock` 14) and its next hours: n3 scraping the meat on the racks."""


def made_layers() -> list[Layer]:
    return [
        Layer(id="larder_bar", img=made.bar(), when=RAIDED),
        Layer(id="larder_latch", img=made.latch(), when=LATCHED),
    ]


def figure_layers() -> list[Layer]:
    return [
        Layer(id="cat_ridge", img=made.cat(), when=CAT),
        Layer(id="figure_n3_scrapes_the_racks", img=person(N3, "up", SCRAPES_AT, drop=4), when=SCRAPING),
    ]


STEP_ASIDE: dict[str, tuple[str, ...]] = {
    "figure_n3_by_fire": (SCRAPING,),
    "figure_n3_at_work": (SCRAPING,),
    "figure_n3_at_racks": (SCRAPING,),
}
"""n3's other poses give way while she is at the racks."""
