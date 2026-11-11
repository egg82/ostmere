"""The side layer in the tools: flatcheck.py refuses each planted entry (in a fixture copy of beats.yaml, never the
shipped file), and the simulator counts side beats by kind next to spine and chapter ones."""
import subprocess
import sys
from collections import Counter

import pytest

from tests import sidelayer
from tests.dayone.beats import BEATS_YAML
from tests.dayone.story import FLATCHECK
from tests.opening.playthrough import News

SHIPPED = BEATS_YAML.read_text()
SL1 = "{id: SL1, kind: arc,     chapter: day_three, thread: th-survive, offers: both,     gate: {hours_after: {beat: K1, hours: 1.25}}}"
K2_GATE = "gate: {completions: {card: field_track, n: 1}},"
PLANTS = {
    "side_kind": (SL1, SL1.replace("kind: arc", "kind: quest")),
    "side_chapter": (SL1, SL1.replace("day_three", "day_nowhere")),
    "side_thread": (SL1, SL1.replace("th-survive", "th-nowhere")),
    "side_offers": (SL1, SL1.replace("offers: both", "offers: gift")),
    "side_turn": (SL1, SL1.replace("offers: both,", "offers: both, turn: up,")),
    "side_field": (SL1, SL1.replace("offers: both,", "offers: both, cost: time,")),
    "side_dup": (SL1, SL1 + "\n  - " + SL1),
    "side_gated": (K2_GATE, "gate: {beat: SL1},"),
}


def flags(text: str, tmp_path_factory: pytest.TempPathFactory) -> list[str]:
    f = tmp_path_factory.mktemp("beats") / "beats.yaml"
    f.write_text(text)
    out = subprocess.run([sys.executable, str(FLATCHECK), str(f), "--decisions", str(f) + ".none"],
                         capture_output=True, text=True, check=False)
    return [ln.split()[1] for ln in out.stdout.splitlines() if ln.split()[1:2] and ln.split()[1].startswith("side_")]


def test_the_shipped_side_layer_has_no_side_flags(tmp_path_factory: pytest.TempPathFactory):
    assert SHIPPED.count(SL1) == 1 and flags(SHIPPED, tmp_path_factory) == []


@pytest.mark.parametrize("flag", sorted(PLANTS))
def test_each_refusal_fires_on_its_planted_entry(flag: str, tmp_path_factory: pytest.TempPathFactory):
    old, new = PLANTS[flag]
    assert SHIPPED.count(old) == 1
    assert flag in flags(SHIPPED.replace(old, new), tmp_path_factory)


def test_a_side_gate_naming_a_side_id_is_not_refused_in_the_side_layer_itself(tmp_path_factory: pytest.TempPathFactory):
    old = "gate: {store_at_least: {store: watch_done, n: 2}}}"
    assert SHIPPED.count(old) == 1
    assert flags(SHIPPED.replace(old, "gate: {beat: SL1}}"), tmp_path_factory) == []


def test_the_layers_read_from_the_shipped_file():
    lay = sidelayer.layers()
    assert lay.side["SL1"] == "arc" and len(lay.side) >= 6
    assert {"B4", "B5"} <= lay.spine and {"K1", "K5"} <= lay.chapter and not lay.chapter & lay.spine


def test_the_count_splits_spine_chapter_and_side_by_kind():
    lay = sidelayer.layers()
    things = ["beat:B5", "beat:K1", "beat:K2", "beat:SL1", "beat:SL2", "beat:SL3", "beat:SL1", "feature:x", "card:y"]
    assert sidelayer.count(things, lay) == Counter({"spine": 1, "chapter": 2, "side:arc": 2, "side:comfort": 1})


def test_the_week_report_buckets_by_day_of_play():
    lay = sidelayer.layers()
    news = [News(0, "beat:K1", 0, 0), News(9, "beat:SL1", 0, 0), News(10, "beat:B5", 0, 0)]
    weeks = sidelayer.per_week(news, lay, lambda t: 1 if t < 10 else 8)
    assert weeks == {1: Counter({"chapter": 1, "side:arc": 1}), 2: Counter({"spine": 1})}
    assert sidelayer.line(weeks[1]) == "spine 0 chapter 1 side 1 {'arc': 1}"
