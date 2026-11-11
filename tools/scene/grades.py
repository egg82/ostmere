"""The scene's whole-screen grades, as the page applies them (a CSS filter on the scene, a colour laid over it),
and the same maths in Pillow so the composites show what the page will.

One home: build.py writes GRADES into the manifest, and composites go through apply() with the same values.
"""
from __future__ import annotations

import re
from collections.abc import Callable

from PIL import Image, ImageChops

import kit

GRADES: dict[str, dict[str, str | float | None]] = {
    "dark": {"when": None, "filter": "brightness(0.5) saturate(0.6) contrast(1.1)",
             "overlay": "rgba(12,16,30,0.24)"},
    "cold": {"when": "project:look_around", "filter": "brightness(0.95) saturate(1.0) contrast(1.18)",
             "overlay": "rgba(84,62,40,0.08)"},
    "warm": {"when": "project:strike_fire", "filter": "brightness(1.04) saturate(1.1) contrast(1.2)",
             "overlay": "rgba(255,140,60,0.06)"},
    "dusk": {"when": "action:evening|end:showing", "filter": "brightness(0.66) saturate(0.7) contrast(1.22)",
             "overlay": "rgba(34,38,84,0.34)", "ease_s": 40},
    "night": {"when": "feature:night", "filter": "brightness(0.64) saturate(0.65) contrast(1.12)",
              "overlay": "rgba(14,18,40,0.28)"},
}
"""The first is the default (the dark the player wakes in); a later grade whose `when` holds replaces it, so look_around
lifts it to cold, the fire to warm, the evening to dusk (dusk wins over warm; `ease_s` is how many seconds the page
takes to move into a grade, default 2.5: dusk comes on over the evening's quiet stretch before the end, so the light is
seen going before the end lands), nightfall to night and the morning back to
the warm grade, which is also the day's (decisions.md, "Day and night run on the story's clock"; night is `night_n2`,
look-tested with the owner)."""
GRADES["day"] = {**GRADES["warm"], "when": "feature:morning"}
GRADES["dusk_2"] = {**GRADES["dusk"], "when": "feature:dusk_2"}
GRADES["night_2"] = {**GRADES["night"], "when": "feature:night_2"}
GRADES["day_3"] = {**GRADES["warm"], "when": "feature:morning_3"}
GRADES["dusk_3"] = {**GRADES["dusk"], "when": "action:evening_3"}
GRADES["night_3"] = {**GRADES["night"], "when": "feature:night_3"}
GRADES["day_4"] = {**GRADES["warm"], "when": "feature:morning_4"}
GRADES["dusk_4"] = {**GRADES["dusk"], "when": "action:evening_4"}
GRADES["night_4"] = {**GRADES["night"], "when": "feature:night_4"}
GRADES["day_5"] = {**GRADES["warm"], "when": "feature:morning_5"}
GRADES["dusk_5"] = {**GRADES["dusk"], "when": "action:night_5"}
GRADES["night_5"] = {**GRADES["night"], "when": "feature:night_5"}
GRADES["day_6"] = {**GRADES["warm"], "when": "feature:morning_6"}
GRADES["dusk_6"] = {**GRADES["dusk"], "when": "action:night_6"}
GRADES["night_6"] = {**GRADES["night"], "when": "feature:night_6"}
GRADES["day_7"] = {**GRADES["warm"], "when": "feature:morning_7"}
GRADES["dusk_7"] = {**GRADES["dusk"], "when": "action:night_7"}
GRADES["night_7"] = {**GRADES["night"], "when": "feature:night_7"}
"""Day two's evening, second night and third day, then each later day's the same way (days five to seven by their
standing dusk action): the same grades again, later in the list so each wins over the day it follows."""
GRADES["drift"] = {"when": "feature:drift", "filter": "brightness(0.74) saturate(0.72) contrast(1.14)",
                   "overlay": "rgba(104,66,30,0.30)", "ease_s": 40}
"""The Drift, from B8 (content/team/week-two.md, Art): brown at noon, warm and dark, ash falling heavy (the ash itself is
a layer). It comes on slowly, as dusk does; later in the list than week 1's last night, so it wins over it."""
GRADES["dusk_12"] = {**GRADES["dusk"], "when": "action:night_12"}
GRADES["night_12"] = {**GRADES["night"], "when": "store:night_12@20"}
"""Night 12, a story night inside the Drift: dusk at its standing action, night once its hidden clock has run its hour
(day_eleven.toml, `night_12`). Later in the list than the Drift, so each wins over it."""
GRADES["day_13"] = {**GRADES["drift"], "when": "action:morning_13"}
GRADES["dusk_14"] = {**GRADES["dusk"], "when": "action:night_14"}
GRADES["night_14"] = {**GRADES["night"], "when": "store:night_14@20"}
"""Morning 13 returns the Drift's light; night 14 comes as night 12 did (day_twelve.toml, `morning_13`, `night_14`).
Night 14 has no morning in week 2: week 3's first morning ends it."""


def pick(holds: Callable[[str], bool]) -> str:
    """The grade the page shows: the first, unless a later one's `when` holds (the client's rule, chooseGrade)."""
    chosen = next(iter(GRADES))
    for name, spec in list(GRADES.items())[1:]:
        when = spec["when"]
        if isinstance(when, str) and when and holds(when):
            chosen = name
    return chosen


def _saturate(img: Image.Image, s: float) -> Image.Image:
    """CSS saturate(), by the Filter Effects spec's matrix."""
    m = (0.213 + 0.787 * s, 0.715 - 0.715 * s, 0.072 - 0.072 * s, 0,
         0.213 - 0.213 * s, 0.715 + 0.285 * s, 0.072 - 0.072 * s, 0,
         0.213 - 0.213 * s, 0.715 - 0.715 * s, 0.072 + 0.928 * s, 0)
    return img.convert("RGB", m)


def _filter(img: Image.Image, css: str) -> Image.Image:
    rgb = img.convert("RGB")
    for name, arg in re.findall(r"(\w+)\(([\d.]+)\)", css):
        v = float(arg)
        if name == "brightness":
            rgb = kit.point(rgb, lambda p: min(255, round(p * v)))
        elif name == "saturate":
            rgb = _saturate(rgb, v)
        elif name == "contrast":
            rgb = kit.point(rgb, lambda p: min(255, max(0, round((p - 127.5) * v + 127.5))))
        else:
            raise ValueError(f"no emulation for CSS {name}()")
    return rgb


def _overlay(img: Image.Image, css: str) -> Image.Image:
    r, g, b, a = (float(x) for x in re.findall(r"[\d.]+", css))
    top = Image.new("RGB", img.size, (int(r), int(g), int(b)))
    return Image.blend(img, top, a)


def apply(img: Image.Image, name: str) -> Image.Image:
    g = GRADES[name]
    flt, overlay = g["filter"], g["overlay"]
    assert isinstance(flt, str) and isinstance(overlay, str)
    return _overlay(_filter(img, flt), overlay)


def screen(base: Image.Image, light: Image.Image) -> Image.Image:
    """mix-blend-mode: screen of an RGBA light over an opaque base."""
    lit = ImageChops.screen(base.convert("RGB"), light.convert("RGB"))
    return Image.composite(lit, base.convert("RGB"), light.getchannel("A")).convert("RGBA")
