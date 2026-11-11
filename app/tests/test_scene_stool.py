"""tools/scene/build.py: a job's seated pose shows only while the stool stands, for every card the job names."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import build   # tools/scene, on the path from the line above
from stages import State, holds


def test_a_seated_pose_needs_the_stool_for_each_of_its_cards():
    for job in build.ROAST.split("|"):
        assert not holds(build.on_stool(build.ROAST), State(frozenset({job})))
        assert holds(build.on_stool(build.ROAST), State(frozenset({job, "feature:stool"})))


def test_a_bare_conjunction_would_show_it_without_the_stool():
    """The control: `&` binds tighter than `|`, so the plain form holds for the first card with no stool."""
    assert holds(f"{build.ROAST}&feature:stool", State(frozenset({"running:roast_roots"})))
