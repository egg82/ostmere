"""Every story line fits a phone's strip whole: at the narrowest phone, in the story's face and size, no line the strip
shows wraps past --strip-rows rows (docs/design/redesign.md, "Phone frame"). The strip's room is that many rows, so the
pinned stage never grows for the longest line ever written; this is the content side of that rule.

What the strip shows is read from the page (client/src/game/chronicle.ts, ROUTES: the kinds routed to the Story
filter), and the rows and the size from client/src/game.css. Lines wrap at spaces only, which can only add rows, never
hide one. A person's name slot is measured as the name it shows (tests/opening/test_line_length.py, shown)."""
import re
import tomllib
from functools import cache
from pathlib import Path
from typing import get_args

from PIL import ImageFont

from ashfall_app.opening.line_kinds import LineKind
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, UNWRITTEN
from tests.opening.test_line_length import shown

APP = Path(__file__).resolve().parents[2]
CLIENT = APP / "client" / "src"
FONT = APP / "ashfall_app" / "static" / "fonts" / "alegreya-sans-latin-italic.woff2"
ROOT_PX = 16
"""The root size on a phone: game.css clamps html's font-size to 16px below 1200px wide."""
PHONE_PX = 360
GUTTER_PX = 16
"""The narrowest phone the frame is checked at, and the strip's padding on each side (game.css, .stage > .strip)."""


@cache
def css_var(name: str) -> str:
    found = re.search(rf"--{name}:\s*([^;]+);", (CLIENT / "game.css").read_text())
    assert found, f"game.css defines no --{name}"
    return found.group(1).strip()


def rows_allowed() -> int:
    return int(css_var("strip-rows"))


@cache
def font() -> ImageFont.FreeTypeFont:
    size = css_var("t-story")
    assert size.endswith("rem"), size
    return ImageFont.truetype(str(FONT), round(float(size.removesuffix("rem")) * ROOT_PX))


def strip_kinds() -> set[str]:
    routes = re.search(r"ROUTES[^=]*=\s*\{([^}]*)\}", (CLIENT / "game" / "chronicle.ts").read_text())
    assert routes, "chronicle.ts has no ROUTES"
    kinds = set(re.findall(r'(\w+):\s*"story"', routes.group(1)))
    assert kinds, "no kind routes to the Story filter"
    return kinds


def rows(text: str, width: float) -> int:
    """How many rows `text` takes at `width` px, broken greedily at spaces."""
    n, line = 1, ""
    for word in text.split():
        trial = f"{line} {word}" if line else word
        if line and font().getlength(trial) > width:
            n, line = n + 1, word
        else:
            line = trial
    return n


def strip_lines(path: Path) -> dict[str, str]:
    data = tomllib.loads(path.read_text())
    kinds, text = data.get("line_kinds", {}), data.get("text", {})
    strip = strip_kinds()
    return {k: shown(text[k]) for k, kind in kinds.items() if kind in strip and k in text and UNWRITTEN not in text[k]}


def too_tall(lines: dict[str, str]) -> list[str]:
    width, allowed = PHONE_PX - 2 * GUTTER_PX, rows_allowed()
    return [f"{k} takes {rows(v, width)} rows at {width}px, past {allowed}" for k, v in lines.items() if rows(v, width) > allowed]


def test_every_story_line_fits_the_phone_strip():
    seen = 0
    for path in (OPENING, *CHAPTERS, *IN_WRITING):
        lines = strip_lines(path)
        seen += len(lines)
        assert too_tall(lines) == [], path.name
    assert seen > 100, "the gate saw the shipped story lines"


def test_a_line_one_row_too_tall_goes_red():
    """Control: the check can fail. Words added until a line takes one row past the strip is named; one row less passes."""
    width, allowed = PHONE_PX - 2 * GUTTER_PX, rows_allowed()
    words: list[str] = []
    while rows(" ".join(words), width) <= allowed:
        words.append("ember")
    over, fits = " ".join(words), " ".join(words[:-1])
    assert too_tall({"l_over": over, "l_fits": fits}) == [f"l_over takes {allowed + 1} rows at {width}px, past {allowed}"]


def test_the_strip_kinds_read_are_line_kinds():
    assert strip_kinds() <= set(get_args(LineKind))
