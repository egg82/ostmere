"""The side layer as the simulator counts it (content/beats.yaml, `side_layer:`): which story ids are spine, chapter or
side beats, and how many of each (side ones by kind) a visit or a week of play showed as new things. Ids and counts
only (CLAUDE.md, "Never spoil the owner"). The fields themselves are checked by content/team/flatcheck.py."""
import re
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from tests.dayone.beats import BEATS_YAML
from tests.opening.playthrough import News

ENTRY = re.compile(r"^\s+- \{id:\s*([\w.-]+)(.*)$", re.M)


@dataclass(frozen=True)
class Layers:
    """Story ids by layer: the spine (`beats:`), the chapters (every `day_*:` list) and the side layer with its kinds."""

    spine: frozenset[str]
    chapter: frozenset[str]
    side: dict[str, str]


def _blocks(text: str) -> dict[str, str]:
    parts = re.split(r"^([a-z_]+):[^\n]*\n", text, flags=re.M)
    return {k: body.split("\n\n", 1)[0] for k, body in zip(parts[1::2], parts[2::2])}


def layers(text: str | None = None) -> Layers:
    blocks = _blocks(BEATS_YAML.read_text() if text is None else text)
    chapters = {i for k, b in blocks.items() if k.startswith("day_") and not k.endswith("promise")
                for i, _ in ENTRY.findall(b)}
    side = {i: m.group(1) for i, rest in ENTRY.findall(blocks.get("side_layer", ""))
            if (m := re.search(r"\bkind:\s*(\w+)", rest))}
    spine = {i for i, _ in ENTRY.findall(blocks.get("beats", ""))}
    return Layers(frozenset(spine), frozenset(chapters - spine - side.keys()), side)


def count(things: Iterable[str], lay: Layers) -> Counter[str]:
    """New things by layer: `spine`, `chapter`, and `side:<kind>`; each story id once, other things not counted."""
    ids = {t.split(":", 1)[1] for t in things if t.startswith("beat:")}
    out: Counter[str] = Counter()
    for i in ids:
        if i in lay.side:
            out["side:" + lay.side[i]] += 1
        elif i in lay.chapter:
            out["chapter"] += 1
        elif i in lay.spine:
            out["spine"] += 1
    return out


def per_week(news: Iterable[News], lay: Layers, day_of: Callable[[int], int]) -> dict[int, Counter[str]]:
    """The count for each week of play (day_of: a clock time to its day of play, from 1)."""
    by_week: dict[int, list[str]] = {}
    for n in news:
        by_week.setdefault((day_of(n.at) - 1) // 7 + 1, []).append(n.thing)
    return {w: count(things, lay) for w, things in sorted(by_week.items())}


def line(c: Counter[str]) -> str:
    side = {k.split(":", 1)[1]: v for k, v in sorted(c.items()) if k.startswith("side:")}
    return f"spine {c['spine']} chapter {c['chapter']} side {sum(side.values())} {side}"
