"""tools/scene: a figure out on the low ground stands in the haze at its own depth. Wherever its feet are along the
track, the page draws it behind every haze layer that lies nearer than its feet (the rim's, a fog band, a column of
steam) and in front of every one that lies beyond them, so near the rim its feet are veiled. A haze layer's depth is
read from its pixels: the lowest row of its densest part, where it lies on the ground."""
import sys
from pathlib import Path

import pytest
from PIL import Image

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import dayone_world as world   # tools/scene, on the path from the line above
import depth
import kit
import valley
from daythree_world import TRACK
from output import Entry
from place import H, LIP, W

PROBE = "figure_away_track"
AMBIGUOUS = 6
"""Rows either side of a haze's ground line where in front and behind are both fair, skipped: the fog is blurred by 3
px at the art's 1x grain, so where a band lies is fuzzy by 6 scene rows."""


def _along_track(step: float = 3.0) -> list[tuple[int, int]]:
    """Feet every `step` px along the track, past the rim only (where the low ground is)."""
    out: list[tuple[int, int]] = []
    for (x0, y0), (x1, y1) in zip(TRACK, TRACK[1:]):
        n = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) / step))
        out += [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n)]
    return [p for p in out if p[1] < LIP - 2]


@pytest.fixture(scope="module")
def hazes() -> dict[str, Image.Image]:
    """The scene's haze layers past the rim, built as build.py builds them, with no walls cut out and a level rim."""
    walls = Image.new("L", (W, H))
    found = {"rim_haze": valley.rim_haze([int(LIP)] * W)}
    found |= {f"valley_fog_{i + 1}": img for i, img in enumerate(world.valley_fog(walls))}
    found |= {f"stream_steam_{i + 1}": img for i, img in enumerate(world.stream_steam(walls))}
    return found


def ground_row(img: Image.Image) -> int:
    """The lowest row where the layer is at its densest: the row it lies on."""
    a = img.getchannel("A")
    densest = max(level for level, count in enumerate(a.histogram()) if count)
    box = kit.point(a, lambda p: 255 if p >= densest else 0).getbbox()
    assert box is not None
    return box[3] - 1


def drawn(hazes: dict[str, Image.Image], feet: tuple[int, int]) -> list[str]:
    """The page's draw order of the haze layers and a figure with its feet at `feet`."""
    bottoms = {name: (img.getchannel("A").getbbox() or (0, 0, 0, 0))[3] for name, img in hazes.items()}
    bottoms[PROBE] = feet[1]
    entries = [Entry(id=name, src=f"{name}.png", x=0, y=0, when="always") for name in bottoms]
    for name in (depth.FLAT | depth.OVERLAY | depth.BASE_OVERRIDE.keys() | depth.PART_OF.keys()
                 | set(depth.PART_OF.values())) - set(bottoms):
        entries.append(Entry(id=name, src=f"{name}.png", x=0, y=0, when="always"))
        bottoms[name] = 300
    return [e["id"] for e in depth.draw_order(depth.arrange(entries, bottoms))]


def test_the_track_has_points_past_the_rim_and_every_haze_layer_has_a_ground_line(hazes: dict[str, Image.Image]):
    """The control: the samples and the layers this suite judges are there to judge."""
    assert len(_along_track()) >= 10
    assert len(hazes) >= 3 and all(0 < ground_row(img) < H for img in hazes.values())


def test_a_figure_on_the_track_is_behind_the_haze_nearer_than_its_feet_and_in_front_of_the_haze_beyond(
        hazes: dict[str, Image.Image]):
    wrong: list[str] = []
    judged = 0
    for feet in _along_track():
        order = drawn(hazes, feet)
        for name, img in hazes.items():
            ground = ground_row(img)
            if abs(ground - feet[1]) <= AMBIGUOUS:
                continue
            judged += 1
            over = order.index(name) > order.index(PROBE)
            if over != (ground > feet[1]):
                wrong.append(f"feet {feet}: {name} (lies on row {ground}) drawn {'over' if over else 'under'} the figure")
    assert judged > 20
    assert not wrong, "\n".join(wrong[:12])


def test_near_the_rim_the_figures_feet_are_veiled_by_haze_drawn_over_them(hazes: dict[str, Image.Image]):
    """Within the rim's haze the ground at the figure's feet is hazed, so its feet are too: some haze drawn after the
    figure covers the pixel just above them."""
    near = [p for p in _along_track() if p[1] > LIP - valley.HAZE_BAND + 4]
    assert near
    for x, y in near:
        order = drawn(hazes, (x, y))
        after = [hazes[n] for n in order[order.index(PROBE) + 1:] if n in hazes]
        assert any(img.getchannel("A").crop((x, y - 1, x + 1, y)).getbbox() for img in after), (x, y)


def test_a_figure_in_camp_is_in_front_of_every_haze(hazes: dict[str, Image.Image]):
    order = drawn(hazes, (300, int(LIP) + 12))
    assert all(order.index(n) < order.index(PROBE) for n in hazes)
