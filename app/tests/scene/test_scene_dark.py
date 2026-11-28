"""The `dark` condition (tools/scene/frame/conditions.py `holds`, the page's conditions.ts): it holds while the grade the scene shows
is a dusk or a night one, and `in_dark` puts it on each alternative of a condition."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parent.parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
from frame.conditions import holds, in_dark   # tools/scene, on the path from the line above
from frame.stages import STAGES


def test_dark_holds_at_dusk_and_night_and_not_by_day():
    assert not holds("dark", STAGES["53_clear"])
    assert holds("dark", STAGES["54_dusk_15"])
    assert holds("dark", STAGES["54_frost_night"])
    assert holds("day", STAGES["54_day_16"]) and not holds("dark", STAGES["54_day_16"])
    assert holds("dark", STAGES["10_night"]) and not holds("dark", STAGES["11_morning"])


def test_a_dark_condition_is_per_alternative():
    assert in_dark("a:x|b:y&c:z") == "a:x&dark|b:y&c:z&dark"
    assert not holds(in_dark("chip:a|chip:b"), STAGES["53_clear"].then({"chip:a"}))
    assert holds(in_dark("chip:a|chip:b"), STAGES["54_dusk_15"].then({"chip:a"}))
