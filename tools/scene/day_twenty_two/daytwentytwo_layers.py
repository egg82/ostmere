"""Day twenty-two's layers (app/ashfall_app/opening/day_twenty_two.toml), in the groups build.py splices into its draw
order: the Still's fog lying over the camp from I1 to week five's turn (day five's thin haze, the kit having no fog), and
the grey film on the racks' meat while the chip `ashed` shows (the meat the rack held, washed grey). Every condition
names an id from that chapter, or the next season's turn that ends it.

Story spoilers (content/team/week-four.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

from day_four import dayfour_world as world4
from day_one import dayone
from draw import kit
from frame.output import Layer

STILL = "feature:still"
TURNED = "feature:drift_two"
FILM = (150, 148, 144)
"""The settled ash's grey, laid over the meat."""


def filmed_meat() -> Image.Image:
    meat = dayone.meat_on_rack()
    grey = Image.blend(meat.convert("RGB"), Image.new("RGB", meat.size, FILM), 0.7)
    return kit.keep_alpha(meat, grey)


def world_layers() -> list[Layer]:
    return [Layer(id="racks_film", img=filmed_meat(), when="chip:ashed")]


def fog_layers(walls: Image.Image) -> list[Layer]:
    return [Layer(id="fog_still", img=world4.fog(1, walls), when=STILL, until=TURNED)]
