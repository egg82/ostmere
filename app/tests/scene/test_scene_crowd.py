"""tools/scene/audits/crowd.py and the build's crowding check (output.check_crowd): no two figures a stage shows have boxes that
meet, bar the held pairs, and a check that compared nothing fails."""
import sys
from pathlib import Path

import pytest
from PIL import Image

SCENE = Path(__file__).resolve().parent.parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
from audits import crowd  # tools/scene, on the path from the line above
from frame import output
from frame.output import Entry
from frame.stages import STAGES


def entry(layer_id: str, x: int) -> Entry:
    return Entry(id=layer_id, src=f"{layer_id}.png", x=x, y=0, when="always")


def scene(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, second_at: int) -> list[Entry]:
    """Two 10x10 figures, the second at `second_at`, and a 10x10 prop at x 5 that the check must ignore."""
    monkeypatch.setattr(output, "OUT", tmp_path)
    monkeypatch.setattr(output, "STAGES", dict(list(STAGES.items())[:1]))
    for name in ("figure_a", "figure_b", "stand"):
        Image.new("RGBA", (10, 10), (9, 9, 9, 255)).save(tmp_path / f"{name}.png")
    return [entry("figure_a", 0), entry("figure_b", second_at), entry("stand", 5)]


def test_figures_whose_boxes_meet_fail_the_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """The planted failure: the second figure one pixel into the first's box."""
    monkeypatch.setattr(crowd, "HELD", frozenset[tuple[str, str]]())
    with pytest.raises(ValueError, match="figure_a and figure_b"):
        output.check_crowd(scene(tmp_path, monkeypatch, second_at=9))


def test_figures_side_by_side_pass_and_a_prop_is_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(crowd, "HELD", frozenset[tuple[str, str]]())
    output.check_crowd(scene(tmp_path, monkeypatch, second_at=10))


def test_a_held_pair_passes_and_one_that_no_longer_meets_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(crowd, "HELD", frozenset({("figure_a", "figure_b")}))
    output.check_crowd(scene(tmp_path, monkeypatch, second_at=9))
    with pytest.raises(ValueError, match="no longer meet"):
        output.check_crowd(scene(tmp_path, monkeypatch, second_at=10))


def test_the_check_fails_when_no_stage_shows_two_figures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    entries = scene(tmp_path, monkeypatch, second_at=10)
    for e in entries:
        e["when"] = "feature:never_held"
    with pytest.raises(ValueError, match="looked at nothing"):
        output.check_crowd(entries)
