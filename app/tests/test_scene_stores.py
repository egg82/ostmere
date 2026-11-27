"""tools/scene: a layer's `store:` condition reads the page's ledger, which holds only stores the opening unlocks
(engine/view.py `_ledger`), else View.levels, which serves the rest the scene names (api/goals/levels.py, from the committed
api/world/scene_stores.json). Judged here: that list is the stores the scene names, and each is one the opening defines. What a built thing shows on is a card's completions."""
import json
import re
import sys
from pathlib import Path

from ashfall_app.api.world import scenestores
from ashfall_app.rules.refs import outcomes
from ashfall_app.rules.schema import load_opening, to_rules

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))


def named_in_the_scene() -> set[str]:
    return {m for p in SCENE.rglob("*.py") if p.name != "stages.py"
            for m in re.findall(r"\bstore:([a-z][a-z0-9_]*)", p.read_text())}


def unlocked_by_the_opening() -> set[str]:
    o = load_opening()
    return {u.id for u in [*o.start, *(u for _, out in outcomes(o) for u in out.unlocks)] if u.unlock_kind == "store"}


def test_the_scene_names_stores_and_the_opening_unlocks_some():
    assert {"stakes", "stones"} <= named_in_the_scene() & unlocked_by_the_opening()


def test_every_store_a_layer_reads_is_one_the_opening_defines():
    """A store no card unlocks is read off View.levels instead (api/goals/levels.py), which serves every store the scene names
    that the opening defines: one it does not define would never hold."""
    defined = {s.id for s in to_rules(load_opening()).stores}
    assert named_in_the_scene() <= defined, sorted(named_in_the_scene() - defined)


def test_the_committed_list_is_the_stores_the_scene_names():
    """tools/scene/build.py rewrites the list from the layers it seeds (storeset.py); a store atom added to a scene module
    without rebuilding leaves it short and the hidden clock unserved."""
    listed = json.loads(Path(scenestores.__file__).with_name("scene_stores.json").read_text())
    assert listed == sorted(named_in_the_scene()), sorted(named_in_the_scene() ^ set(listed))


def test_storeset_reads_every_condition_of_layers_and_grades():
    from frame.storeset import stores_read
    layers = [{"when": "always"}, {"when": "store:a@3&running:x"}, {"when": "pushes:p@1|store:b", "until": "store:z"}]
    assert stores_read(layers, {"night": {"when": "store:c@20|chip:cold"}}) == ["a", "b", "c", "z"]
