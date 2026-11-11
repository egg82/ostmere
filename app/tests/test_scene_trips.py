"""tools/scene/trips.py: a trip card hides the seated figure by its id, tapped (`running:`) and mixed (`mix:`), in
conditions the manifest check accepts."""
import importlib
import sys
from pathlib import Path

import pytest

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import output   # tools/scene, on the path from the line above
import trips


def entry(until: str) -> output.Entry:
    return {"id": "figure", "src": "x.png", "x": 0, "y": 0, "when": "always", "until": until}


def test_a_trip_is_away_when_tapped_and_when_mixed():
    got = trips.away(("far_hunt",))
    assert got == ["running:far_hunt", "mix:far_hunt"]
    output.check_conditions([entry("|".join(got))])


def test_no_trips_adds_no_condition():
    assert trips.away(()) == []


def test_a_misspelt_kind_would_fail_the_manifest_check():
    """The control: the check these conditions pass is able to fail."""
    with pytest.raises(ValueError):
        output.check_conditions([entry("runing:far_hunt")])


def test_the_scene_hides_its_seated_figure_for_every_trip(monkeypatch: pytest.MonkeyPatch):
    import build
    importlib.reload(build)
    assert "||" not in build.ELSEWHERE and not build.ELSEWHERE.endswith("|")
    monkeypatch.setattr(trips, "TRIPS", ("far_hunt",))
    importlib.reload(build)
    assert "running:far_hunt" in build.ELSEWHERE and "mix:far_hunt" in build.ELSEWHERE
    monkeypatch.undo()
    importlib.reload(build)
