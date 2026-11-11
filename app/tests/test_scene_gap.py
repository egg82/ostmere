"""tools/scene: the props in and past the wall's gap each have their own spot. The figure out on the track, the stones
fallen off the walls and the columns of steam cover nothing and nothing covers them; a cairn may stand behind another
cairn only when it is clearly further (the cairns are drawn far first). Their places are fixed, so one check covers every
stage that shows them together. Boxes come from the placing constants and the sizes their sprites fill: no packs."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import dayone_world as world   # tools/scene, on the path from the line above
from daythree_poses import ON_TRACK
from daythree_world import CAIRNS
from parts import FALLEN

Box = tuple[float, float, float, float]

FIGURE_HALF_W, FIGURE_H = 10, 30
"""The away figure's drawn size about its feet (the walking sheet's standing frame at half size)."""
STONE_INSET = 2, 4, 28, 28
"""Where a fallen stone's pixels lie in its tile: the ash sheet's stones fill about this much of it."""


def figure() -> Box:
    x, y = ON_TRACK
    return (x - FIGURE_HALF_W, y - FIGURE_H, x + FIGURE_HALF_W, y)


def cairn(x: float, y: float, s: float) -> Box:
    half = 24 * s / 2
    return (x - half, y - 26 * s, x + half, y + 2)


def stone(x: float, y: float) -> Box:
    l, t, r, b = STONE_INSET
    return (x + l, y + t, x + r, y + b)


def steam(spot: tuple[int, int]) -> Box:
    x, ground = spot[0] * 2, world.steam_ground(spot)
    return (x - 6, ground - 50, x + 6, ground)


def meets(a: Box, b: Box) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def props() -> dict[str, Box]:
    found = {"figure": figure()}
    found |= {f"cairn {i + 1}": cairn(*c) for i, c in enumerate(CAIRNS)}
    found |= {f"fallen stone {i + 1}": stone(x, y) for i, (_, x, y) in enumerate(FALLEN)}
    found |= {f"steam {i + 1}": steam(s) for i, s in enumerate(world.STEAM)}
    return found


APART = 6
"""Rows of depth between two cairns' feet for one to read as clearly behind the other."""


def allowed(a: str, b: str, boxes: dict[str, Box]) -> bool:
    return a.startswith("cairn") and b.startswith("cairn") and abs(boxes[a][3] - boxes[b][3]) >= APART


def test_no_two_props_in_or_past_the_gap_cover_each_other():
    boxes = props()
    names = sorted(boxes)
    hits = [f"{a} and {b}" for i, a in enumerate(names) for b in names[i + 1:]
            if meets(boxes[a], boxes[b]) and not allowed(a, b, boxes)]
    assert not hits, hits


def test_the_check_sees_an_overlap_when_there_is_one():
    """The control: a stone dropped at the figure's feet meets it, and the boxes are all there to judge."""
    assert meets(stone(ON_TRACK[0] - 16, ON_TRACK[1] - 20), figure())
    assert not meets(stone(ON_TRACK[0] + 40, ON_TRACK[1] - 20), figure())
    assert len(props()) >= 10
