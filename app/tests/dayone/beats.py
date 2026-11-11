"""Which content step is which of day one's story ids, read off a save; and which of them touch the day's near promise,
read off content/beats.yaml. The simulator names story moments by these ids only (CLAUDE.md, "Never spoil the owner")."""
import re
from collections.abc import Iterable
from pathlib import Path

from ashfall_app.engine import BP, CardId, Rules, Save

BEATS_YAML = Path(__file__).resolve().parents[3] / "content" / "beats.yaml"
TRIGGERED = {"H1": "t_night", "H2": "t_morning", "H6": "t_first_smoke", "H7": "t_prints"}
"""Story ids that land when a trigger fires. H1's step is the night's start at the end (content/team/day-one.md, H1's
row), where the end lines pose its promise; its own lines follow on t_h1."""
STEPS = {"A11": "sit_up", "A12": "look_out", "H3": "look_out", "A13": "set_snare", "H4": "set_snare",
         "A14": "look_over_camp", "H5": "look_over_camp",
         "P0.1": "build_lean_to", "P0.2": "build_larder", "P0.3": "build_smoke_rack", "P0.4": "take_stock",
         "B3": "take_stock"}
"""Story ids that land at a card's first completion."""
STORY = ("H1", "H2", "H3", "H4", "H5", "H6", "H7", "B3")
"""Day one's beats in their authored order (content/team/day-one.md)."""


def landed(save: Save, rules: Rules) -> set[str]:
    """The story ids whose step has landed in this save."""
    fired = {t.id for t, f in zip(rules.triggers, save.fired) if f}
    done = {c.card for c in save.cards if c.work.start_value >= _unit(rules, c.card)}
    return {b for b, t in TRIGGERED.items() if t in fired} | {b for b, c in STEPS.items() if CardId(c) in done}


def _unit(rules: Rules, card: CardId) -> int:
    return next(c.work_s for c in rules.cards if c.id == card) * BP


def near_promise_beats() -> frozenset[str]:
    """Day one's ids whose beats.yaml entry opens, advances or pays the day's near promise (day_one_near_promise),
    the closing ref's spine entry included."""
    text = BEATS_YAML.read_text()
    found = re.search(r"^day_one_near_promise:\s*(\S+)", text, re.M)
    assert found is not None, "beats.yaml names no day_one_near_promise"
    near = found.group(1)
    day = text.split("\nday_one:\n", 1)[1].split("\n\n", 1)[0]
    day_ids = set(re.findall(r"^\s+- \{id:\s*([\w.]+)", day, re.M))
    entries = re.split(r"\n(?=\s+- \{id:)", text)
    return frozenset(m.group(1) for e in entries
                     if (m := re.match(r"\s+- \{id:\s*([\w.]+)", e)) and m.group(1) in day_ids and near in e)


def day_one_promises() -> dict[str, tuple[frozenset[str], frozenset[str]]]:
    """Day one's ids with the promises each opens and pays (beats.yaml), the story questions the simulator tracks by id."""
    text = BEATS_YAML.read_text()
    day = text.split("\nday_one:\n", 1)[1].split("\n\n", 1)[0]

    def refs(entry: str, key: str) -> frozenset[str]:
        found = re.search(rf"\b{key}:\s*\[([^\]]*)\]", entry)
        return frozenset() if found is None else frozenset(x.strip() for x in found.group(1).split(","))

    entries = re.split(r"\n(?=\s+- \{id:)", day)
    return {m.group(1): (refs(e, "opens"), refs(e, "pays")) for e in entries
            if (m := re.match(r"\s+- \{id:\s*([\w.]+)", e))}


def questions_open(seen: Iterable[str]) -> frozenset[str]:
    """The promises opened by the day-one ids in `seen` and not yet paid by one of them."""
    known = day_one_promises()
    opened: set[str] = set()
    paid: set[str] = set()
    for b in seen:
        opens, pays = known.get(b, (frozenset[str](), frozenset[str]()))
        opened |= opens
        paid |= pays
    return frozenset(opened - paid)
