"""The scene's layer and grade conditions (tools/scene/build.py, the table `layers()` builds the manifest from, the
day-two, day-three, day-four-to-seven, day-eight-and-nine, day-eleven and day-twelve groups it splices in from
tools/scene/daytwo_layers.py, daythree_layers.py, dayfour_layers.py, dayeight_layers.py, dayeleven_layers.py and
daytwelve_layers.py, and tools/scene/grades.py's GRADES) name only ids the opening has. The page treats an unknown id as never true, so a renamed card would silently hide its layer.

The generator needs Pillow and the art packs, so the table is read as source: every `kind:id` atom in a string of
build.py. The manifest itself lives outside the repo (the assets volume) and is not read."""
import ast
import re
from pathlib import Path

import pytest

from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, load_opening

SCENE = Path(__file__).resolve().parents[3] / "tools" / "scene"
BUILD = SCENE / "build.py"
LAYERS = [BUILD, SCENE / "daytwo_layers.py", SCENE / "daythree_layers.py", SCENE / "dayfour_layers.py",
          SCENE / "dayeight_layers.py", SCENE / "dayeleven_layers.py", SCENE / "daytwelve_layers.py"]
GRADES = SCENE / "grades.py"
ATOM = re.compile(r"\b(project|pushes|running|mix|store|feature|chip|action):([A-Za-z0-9_]+)")


def condition_atoms(source: str) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.update((m[1], m[2]) for m in ATOM.finditer(node.value))
    return found


@pytest.fixture(scope="module")
def ids() -> dict[str, set[str]]:
    """Ids from every chapter, the ones still in writing included: a chapter's art is built before its lines are, and its
    layers never show until the chapter ships. Loaded once for the module: each chapter adds to the load."""
    o = load_opening(chapters=(*CHAPTERS, *IN_WRITING))
    cards = {c.id for c in o.cards}
    return {
        "project": cards, "pushes": cards, "mix": cards, "running": cards | {a.id for a in o.standing},
        "store": {s.id for s in o.stores}, "feature": {f.id for f in o.features}, "chip": {c.id for c in o.chips},
        "action": {a.id for a in o.standing},
    }


def unknown(source: str, ids: dict[str, set[str]]) -> list[str]:
    return sorted(f"{kind}:{name}" for kind, name in condition_atoms(source) if name not in ids[kind])


def test_every_scene_condition_names_an_id_the_opening_has(ids: dict[str, set[str]]):
    source = "\n".join(p.read_text() for p in LAYERS)
    assert {k for k, _ in condition_atoms(source)} >= {"project", "pushes", "running", "store", "feature"}   # the probe sees the table
    assert unknown(source, ids) == []


def test_every_grade_condition_names_an_id_the_opening_has(ids: dict[str, set[str]]):
    source = GRADES.read_text()
    assert {k for k, _ in condition_atoms(source)} >= {"project", "feature", "action"}   # the probe sees GRADES
    assert unknown(source, ids) == []


def test_the_check_fails_on_a_renamed_id(ids: dict[str, set[str]]):
    """Control: a planted id that does not exist is reported, so the test above can fail."""
    assert unknown('BAD = "project:no_such_card|store:no_such_store"', ids) == [
        "project:no_such_card", "store:no_such_store"]
