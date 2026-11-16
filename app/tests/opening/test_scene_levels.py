"""View.levels carries the stores the scene manifest reads that the ledger does not list (CONTRACT.txt, "FIGHTS",
"read a level"), so a layer on a hidden clock holds in play. Judged on the opening's own rules through the Game's view,
with the manifest's layers named after every `store:` condition tools/scene writes."""
import json
from pathlib import Path

from ashfall_app.api.scenestores import scene_stores
from ashfall_app.engine import QUANTITY_SCALE as Q
from ashfall_app.engine import new_save
from ashfall_app.api.service import Game
from tests.shipped_ruleset import ShippedRuleset
from tests.test_scene_stores import named_in_the_scene


def manifest(tmp_path: Path, whens: list[str]) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"layers": [{"id": f"l{i}", "when": w} for i, w in enumerate(whens)],
                                "grades": {"night": {"when": "store:night_12@20|chip:cold"}}}))
    return path


def game(r: ShippedRuleset, path: Path | None) -> Game:
    return Game(r.opening, r.rs, path)


def test_the_stores_are_read_off_every_condition_of_the_manifest(tmp_path: Path):
    path = manifest(tmp_path, ["always", "store:a@3&running:x", "pushes:p@1|store:b", "store:c"])
    assert scene_stores(path) == {"a", "b", "c", "night_12"}
    assert scene_stores(tmp_path / "none.json") == frozenset() == scene_stores(None)


def test_a_hidden_clock_is_on_the_view_with_what_the_opening_starts_it_at(shipped_ruleset: ShippedRuleset, tmp_path: Path):
    path = manifest(tmp_path, [f"store:{s}" for s in sorted(named_in_the_scene())])
    wire = game(shipped_ruleset, path).view(new_save(shipped_ruleset.rs.rules))
    levels = {lv.store: lv.segment for lv in wire.levels}
    assert levels["b7_clock"].start_value == 10 * Q
    assert {"drift_left", "morning_13", "night_12"} <= levels.keys()
    assert not levels.keys() & {ln.store for ln in wire.ledger}


def test_a_store_the_opening_does_not_define_is_not_served(shipped_ruleset: ShippedRuleset, tmp_path: Path):
    wire = game(shipped_ruleset, manifest(tmp_path, ["store:not_a_store"])).view(new_save(shipped_ruleset.rs.rules))
    assert "not_a_store" not in {lv.store for lv in wire.levels}


def test_no_manifest_serves_only_the_wounded_levels(shipped_ruleset: ShippedRuleset):
    wire = game(shipped_ruleset, None).view(new_save(shipped_ruleset.rs.rules))
    assert [lv.store for lv in wire.levels] == ["hurt"]
