"""tools/scene: the roof over the corner where the figure lay reads as coming out over the camp floor, held up there.
Its posts reach from the eave down to the floor in front of the wall's foot, and the page draws a figure lying under
the roof behind them and one standing out on the floor in front of them."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import dayone   # tools/scene, on the path from the line above
import depth
from output import Entry
from parts import EAVE, EAVE_Y, ROOF_X
from place import LIP

WALL_FOOT = int(LIP) + 2


def posts():
    return dayone.roof_posts(EAVE_Y, WALL_FOOT + EAVE, (ROOF_X[0] + 24, ROOF_X[1] - 14))


def test_the_posts_stand_on_the_floor_in_front_of_the_wall_and_reach_the_eave():
    box = posts().getchannel("A").getbbox()
    assert box is not None
    _, top, _, bottom = box
    assert top <= EAVE_Y   # up to the roof's lowest row (drawn at the packs' 1x grain, so to an even row)
    assert bottom - 1 > WALL_FOOT


def test_a_figure_lying_under_the_roof_is_behind_its_posts_and_one_out_on_the_floor_in_front():
    bottom = posts().getchannel("A").getbbox()
    assert bottom is not None
    ids = ["ruin", "figure_lying", "roof_posts", "figure_resting"]
    bottoms = {"ruin": 288, "figure_lying": 152, "roof_posts": bottom[3], "figure_resting": 161}
    entries = [Entry(id=i, src=f"{i}.png", x=0, y=0, when="always") for i in ids]
    for name in (depth.FLAT | depth.OVERLAY | depth.BASE_OVERRIDE.keys() | depth.PART_OF.keys()
                 | set(depth.PART_OF.values())) - set(bottoms):
        entries.append(Entry(id=name, src=f"{name}.png", x=0, y=0, when="always"))
        bottoms[name] = 100
    order = [e["id"] for e in depth.draw_order(depth.arrange(entries, bottoms))]
    assert order.index("figure_lying") < order.index("roof_posts") < order.index("figure_resting")
