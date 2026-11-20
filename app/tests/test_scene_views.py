"""tools/scene: the views the page shows are authored data that only ever widens the frame."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import views   # tools/scene, on the path from the line above
from stages import State


def test_the_authored_views_are_well_formed():
    assert views.problems(views.VIEWS) == []
    assert views.EXTENT == (max(v.size[0] for v in views.VIEWS), max(v.size[1] for v in views.VIEWS))


def test_a_malformed_list_is_reported():
    """The planted failures: a shrinking view, a second default, a conditional first."""
    camp, wide = views.View("camp", (480, 288), None), views.View("wide", (576, 336), "feature:x")
    assert views.problems((camp, wide)) == []
    assert views.problems((wide, camp)) != [] and views.problems((camp, views.View("b", (500, 300), None))) != []
    assert views.problems((camp, wide, views.View("small", (500, 300), "feature:y"))) == ["small: smaller than wide"]


def test_the_view_is_the_last_one_whose_unlock_holds():
    """Each view's own unlock (and those before it) shows it; with none held it is the first."""
    assert views.pick(State()) == views.VIEWS[0]
    held: set[str] = set()
    for view in views.VIEWS[1:]:
        assert view.when is not None
        held.add(view.when)
        assert views.pick(State(frozenset(held))) == view
