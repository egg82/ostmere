"""Every aim fits one line at the narrowest phone, in its face and size: the aim's room is one line that does not
wrap (game.css, .aim: nowrap, ellipsis), so a longer aim is cut off on screen. Measured as test_strip_rows measures the
strip, with --t-meta and the phone's aim padding (game.css, .stage > .aim)."""
import tomllib

from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, UNWRITTEN
from tests.opening.test_strip_rows import GUTTER_PX, PHONE_PX, font, shown

WIDTH = PHONE_PX - 2 * GUTTER_PX


def aim_lines() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in (OPENING, *CHAPTERS, *IN_WRITING):
        data = tomllib.loads(path.read_text())
        text = data.get("text", {})
        out |= {f"aim {a['id']}": shown(text[a["text_key"]]) for a in data.get("aims", []) if UNWRITTEN not in text.get(a["text_key"], UNWRITTEN)}
    return out


def too_wide(lines: dict[str, str]) -> list[str]:
    f = font("t-meta")
    return [f"{k} is {f.getlength(v):.0f}px wide, past {WIDTH}px: it must fit one line on a phone" for k, v in lines.items() if f.getlength(v) > WIDTH]


def test_every_aim_fits_one_line_on_a_phone():
    lines = aim_lines()
    assert len(lines) >= 10, "the gate saw the shipped aims"
    assert too_wide(lines) == []


def test_an_aim_one_word_too_wide_goes_red():
    """Control: the check can fail. Words added until the line is past the width is named; one word less passes."""
    words: list[str] = []
    while font("t-meta").getlength(" ".join(words)) <= WIDTH:
        words.append("ember")
    over, fits = " ".join(words), " ".join(words[:-1])
    assert [m.split(" is ")[0] for m in too_wide({"aim over": over, "aim fits": fits})] == ["aim over"]

