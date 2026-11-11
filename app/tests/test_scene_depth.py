"""tools/scene/depth.py: the generator marks which layers the page depth-sorts and gives each its ground-contact `base`,
and draw_order is the page's rule (scene/manifest.ts depthOrder), so the previews match the page."""
import sys
from pathlib import Path

import pytest

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import depth   # tools/scene, on the path from the line above
from output import Entry


def entry(layer_id: str, blend: str = "") -> Entry:
    made = Entry(id=layer_id, src=f"{layer_id}.png", x=0, y=0, when="always")
    if blend:
        made["blend"] = blend
    return made


def camp() -> tuple[list[Entry], dict[str, int]]:
    ids = ["ruin", "cleared", "fireback", "figure_gathering", "bay", "pelt_in_bay_1", "firelight", "ash"]
    bottoms = {"ruin": 288, "cleared": 265, "fireback": 190, "figure_gathering": 171, "bay": 282, "pelt_in_bay_1": 280,
               "firelight": 288, "ash": 288}
    return [entry(i, "screen" if i == "firelight" else "") for i in ids], bottoms


def arranged() -> list[Entry]:
    entries, bottoms = camp()
    stale = depth.FLAT | depth.OVERLAY | depth.BASE_OVERRIDE.keys() | depth.PART_OF.keys() | set(depth.PART_OF.values())
    for name in stale - set(bottoms):
        entries.append(entry(name))
        bottoms[name] = 100
    return depth.arrange(entries, bottoms)


def test_flat_ground_comes_first_and_overlays_last_with_no_base():
    got = arranged()
    kinds = ["flat" if e["id"] in depth.FLAT else "over" if "base" not in e else "sorted" for e in got]
    assert kinds == sorted(kinds, key=["flat", "sorted", "over"].index)
    assert {"flat", "sorted", "over"} == set(kinds)
    assert all("base" not in e for e in got if e["id"] in depth.FLAT or e["id"] in depth.OVERLAY)


def test_a_standing_layer_takes_its_lowest_pixel_as_base_and_a_part_takes_its_parents_if_larger():
    base = {e["id"]: e.get("base") for e in arranged()}
    assert (base["fireback"], base["figure_gathering"]) == (190, 171)
    assert base["pelt_in_bay_1"] == base["bay"] == 282


def test_the_figure_at_the_gap_is_drawn_behind_the_fireback():
    order = [e["id"] for e in depth.draw_order(arranged())]
    assert order.index("figure_gathering") < order.index("fireback")


def test_a_part_stays_over_its_parent_and_unbased_layers_never_move():
    got = arranged()
    order = [e["id"] for e in depth.draw_order(got)]
    assert order.index("bay") < order.index("pelt_in_bay_1")
    assert [i for i in order if i in depth.FLAT] == [e["id"] for e in got if e["id"] in depth.FLAT]
    assert order.index("ash") > order.index("fireback") and order.index("firelight") > order.index("pelt_in_bay_1")


def test_a_name_the_scene_no_longer_has_fails_the_build():
    """The control: arrange refuses a table that names a missing layer, rather than silently not sorting it."""
    entries, bottoms = camp()
    with pytest.raises(ValueError):
        depth.arrange(entries, bottoms)


def test_a_body_by_the_larder_keeps_its_override_base():
    base = {e["id"]: e.get("base") for e in arranged()}
    assert base["vigil_body"] == base["figure_lying_apart"] == 204

