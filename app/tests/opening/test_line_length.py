"""Every shipped story line fits the task card: no line of a shipped or in-writing chapter is past MAX_LINE characters.

A line is a text key with the `l_` prefix (the content files' convention: `l_look`, `l_knap_2`; labels and UI text
carry other prefixes). The limit is the lines briefs' 90th-percentile figure applied to each line, since the briefs set
no per-line maximum; their median (45) and 90th percentile (75) are printed per chapter, not gated. A person's name slot
is measured as the name it shows (api/CONTRACT.txt, "Text and numbers", {<lane>}). A line over it that
shipped before this gate is held in HELD, which may only shrink (a held line now within the limit fails as stale).
prestige.toml holds node labels and no lines, so it alone of the shipped files may have none."""
import re
import statistics
import tomllib
from functools import cache
from pathlib import Path

from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, PRESTIGE, UNWRITTEN

MAX_LINE = 75
HELD: dict[str, int] = {"l_lintel": 79}
"""Shipped lines past MAX_LINE, by key to length; fix the line and delete its entry, never raise MAX_LINE."""


@cache
def names() -> dict[str, str]:
    """Each named lane's name, from every chapter: a slot names a person a chapter before it may have named."""
    out: dict[str, str] = {}
    for path in (*CHAPTERS, *IN_WRITING):
        data = tomllib.loads(path.read_text())
        out |= {x["id"]: data["text"][x["name_key"]] for x in data.get("lanes", []) if "name_key" in x}
    return out


def shown(text: str) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: names().get(m.group(1), m.group(0)), text)


def written_lines(text: dict[str, str]) -> dict[str, str]:
    return {k: shown(v) for k, v in text.items() if k.startswith("l_") and UNWRITTEN not in v}


def chapter_lines(path: Path) -> dict[str, str]:
    return written_lines(tomllib.loads(path.read_text())["text"])


def too_long(lines: dict[str, str]) -> dict[str, int]:
    return {k: len(v) for k, v in lines.items() if len(v) > MAX_LINE}


def problems(lines: dict[str, str]) -> list[str]:
    over = too_long(lines)
    new = [f"{k} is {n} characters, past {MAX_LINE}" for k, n in over.items() if k not in HELD]
    stale = [f"{k} is held but now within {MAX_LINE}: delete it from HELD" for k in HELD if k in lines and k not in over]
    return new + stale


def test_every_written_line_of_every_chapter_is_within_the_limit():
    seen = 0
    for path in (*CHAPTERS, *IN_WRITING):
        lines = chapter_lines(path)
        assert lines or path in (*IN_WRITING, PRESTIGE), f"{path.name}: the gate found no written lines"
        if not lines:
            continue
        seen += len(lines)
        lens = sorted(len(v) for v in lines.values())
        p90 = lens[max(0, -(-9 * len(lens) // 10) - 1)]
        print(f"{path.name}: {len(lines)} lines, median {statistics.median(lens)}, p90 {p90}, longest {lens[-1]}")
        assert problems(lines) == [], path.name
    assert seen > 50, "the gate saw the shipped lines"


def test_the_held_lines_are_shipped_lines():
    shipped = {k for p in CHAPTERS for k in chapter_lines(p)}
    assert set(HELD) <= shipped


def test_a_line_over_the_limit_goes_red_and_a_unwritten_one_is_skipped():
    """Control: the check can fail. A planted long line is named; one at the limit, a label, and an unwritten line pass."""
    lines = {"l_ok": "x" * MAX_LINE, "l_plant": "x" * (MAX_LINE + 1)}
    assert problems(lines) == [f"l_plant is {MAX_LINE + 1} characters, past {MAX_LINE}"]
    text = {**lines, "c_label": "x" * 200, "l_todo": UNWRITTEN + "x" * 200}
    assert set(written_lines(text)) == {"l_ok", "l_plant"}
    stale = {k: "short" for k in HELD}
    assert len(problems(stale)) == len(HELD)


def test_a_name_slot_is_measured_as_the_name():
    """A line whose slots fit but whose name pushes it past the limit is over it; an unnamed slot stays as written."""
    name = names()["n2"]
    line = "x" * (MAX_LINE - len(name) + 1)
    assert written_lines({"l_plant": line + "{n2}"}) == {"l_plant": line + name}
    assert problems(written_lines({"l_plant": line + "{n2}"})) != []
    assert written_lines({"l_x": "{n1}"}) == {"l_x": "{n1}"}
