"""tools/scene/builds.py and the build's overlap check (output.check_builds): no two builds share 30 pixels at any
stage but the held pairs, every layer is classified, and a check that compared nothing fails."""
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest
from PIL import Image

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import builds   # tools/scene, on the path from the line above
import output
from output import Entry
from stages import STAGES


def entry(layer_id: str, x: int = 0, blend: str = "") -> Entry:
    made = Entry(id=layer_id, src=f"{layer_id}.png", x=x, y=0, when="always")
    if blend:
        made["blend"] = blend
    return made


def test_pairs_of_builds_sharing_thirty_pixels_are_reported_and_fewer_are_not():
    shown = [entry("cellar_1"), entry("larder"), entry("pyre"), entry("figure_digging_cellar"), entry("ruin")]
    sharing = {("cellar_1", "larder"): 30, ("cellar_1", "pyre"): 29}

    def shared(a: Sequence[str], b: Sequence[str]) -> int:
        return sharing.get((a[0], b[0]), 0)

    assert builds.crowded(shown, shared) == [("cellar", "larder", 30)]
    assert builds.crowded([entry("cellar_1"), entry("cellar_2")], lambda a, b: 99) == []


def test_a_layer_in_no_build_or_a_name_the_scene_lost_is_reported():
    every = [entry(i) for i in [*builds.MEMBER_OF, *builds.NOT_BUILDS]]
    assert builds.unsorted(every) == []
    assert builds.unsorted([*every, entry("new_heap"), entry("figure_new"), entry("new_light", blend="screen")]) == ["new_heap"]
    assert builds.unsorted([e for e in every if e["id"] != "larder"]) == ["larder"]


def scene(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cellar_at: int) -> list[Entry]:
    """Every classified layer as a 1px sprite far apart, and the cellar and the dry stack 10x10 with the cellar at
    `cellar_at`."""
    monkeypatch.setattr(output, "OUT", tmp_path)
    monkeypatch.setattr(output, "STAGES", dict(list(STAGES.items())[:1]))
    entries: list[Entry] = []
    for n, name in enumerate([*builds.MEMBER_OF, *builds.NOT_BUILDS]):
        big = name in ("cellar_1", "dry_wood_1")
        size, x = (10, cellar_at if name == "cellar_1" else 0) if big else (1, 20 + n)
        Image.new("RGBA", (size, size), (9, 9, 9, 255)).save(tmp_path / f"{name}.png")
        entries.append(entry(name, x))
    return entries


def test_builds_drawn_over_each_other_fail_the_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """The planted failure: the cellar moved onto the dry stack (a 10x10 on a 10x10 shares 50 px here)."""
    monkeypatch.setattr(builds, "HELD_CROWDED", frozenset[tuple[str, str]]())
    with pytest.raises(ValueError, match="cellar and dry_wood_1"):
        output.check_builds(scene(tmp_path, monkeypatch, cellar_at=5))


def test_the_check_passes_when_the_builds_are_clear(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(builds, "HELD_CROWDED", frozenset[tuple[str, str]]())
    output.check_builds(scene(tmp_path, monkeypatch, cellar_at=10))


def test_the_check_passes_while_the_overlap_is_held(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(builds, "HELD_CROWDED", frozenset[tuple[str, str]]({("cellar", "dry_wood_1")}))
    output.check_builds(scene(tmp_path, monkeypatch, cellar_at=5))


def test_a_held_pair_that_no_longer_overlaps_fails_the_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(builds, "HELD_CROWDED", frozenset[tuple[str, str]]({("cellar", "dry_wood_1")}))
    with pytest.raises(ValueError, match="no longer overlap"):
        output.check_builds(scene(tmp_path, monkeypatch, cellar_at=10))


def test_the_check_fails_when_no_stage_shows_two_builds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    entries = scene(tmp_path, monkeypatch, cellar_at=10)
    for e in entries:
        e["when"] = "feature:never_held"
    with pytest.raises(ValueError, match="looked at nothing"):
        output.check_builds(entries)
