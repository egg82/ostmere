"""Every days note in the shipped content names a spine beat content/beats.yaml has (api/CONTRACT.txt, "JOURNAL": the
loader holds a beat's presence and shape; the canon is not shipped, so this holds that it exists). Ids only."""
import re

from ashfall_app.opening.schema import load_opening
from tests.dayone.beats import BEATS_YAML


def spine_beats() -> frozenset[str]:
    """The ids of beats.yaml's `beats:` list (the spine), not the day lists' steps."""
    text = BEATS_YAML.read_text()
    spine = text.split("\nbeats:\n", 1)[1].split("\n\n", 1)[0]
    return frozenset(re.findall(r"^\s+- \{id:\s*([\w-]+)", spine, re.M))


def unknown_beats(named: dict[str, str]) -> list[str]:
    known = spine_beats()
    return [f"note {n}: beat {b}" for n, b in named.items() if b not in known]


def test_the_spine_is_read():
    beats = spine_beats()
    assert {"B2", "B7", "B9"} <= beats and "A3" not in beats   # control: the spine's ids, and no day list's step


def test_every_days_note_names_a_spine_beat():
    o = load_opening()
    days = {e.id for e in o.entries if e.section == "days"}
    named = {n.id: n.beat or "" for n in o.notes if n.entry in days}
    assert named, "the shipped content has days notes"
    assert unknown_beats(named) == []


def test_a_beat_the_spine_lacks_is_named():
    assert unknown_beats({"n_planted": "B999", "n_real": "B5"}) == ["note n_planted: beat B999"]
