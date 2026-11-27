"""The `dark` condition (tools/scene/stages.py `holds`, the page's conditions.ts): it holds while the grade the scene shows
is a dusk or a night one, and `in_dark` puts it on each alternative of a condition."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
from stages import STAGES, holds, in_dark   # tools/scene, on the path from the line above


def test_dark_holds_at_dusk_and_night_and_not_by_day():
    day = STAGES["64_all_built"].then({"action:morning_13"}, {"action:night_14"}, night_12=0, night_14=0)
    assert not holds("dark", day)
    assert holds("dark", day.then({"action:night_14"}))
    assert holds("dark", day.then({"action:night_14"}, night_14=20))
    assert holds("dark", STAGES["10_night"]) and not holds("dark", STAGES["11_morning"])


def test_a_dark_condition_is_per_alternative():
    assert in_dark("a:x|b:y&c:z") == "a:x&dark|b:y&c:z&dark"
    day = STAGES["64_all_built"].then({"action:morning_13", "chip:a"}, {"action:night_14"}, night_12=0, night_14=0)
    assert not holds(in_dark("chip:a|chip:b"), day)
    assert holds(in_dark("chip:a|chip:b"), day.then({"action:night_14"}))
