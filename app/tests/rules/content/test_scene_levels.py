"""View.levels carries the stores the scene reads that the ledger does not list (contract/fights.txt, "FIGHTS", "read a
level"), so a layer on a hidden clock holds in play. Judged on the opening's own rules through the Game's view, with
no assets volume anywhere: the store set ships with the code (api/world/scene_stores.json)."""
from ashfall_app.api.world.scenestores import scene_stores
from ashfall_app.api.service import Game
from ashfall_app.engine import QUANTITY_SCALE as Q
from ashfall_app.engine import new_save
from tests.shipped_ruleset import ShippedRuleset
from tests.scene.test_scene_stores import named_in_the_scene


def test_a_hidden_clock_is_on_the_view_with_what_the_opening_starts_it_at(shipped_ruleset: ShippedRuleset):
    wire = Game(shipped_ruleset.opening, shipped_ruleset.rs).view(new_save(shipped_ruleset.rs.rules))
    levels = {lv.store: lv.segment for lv in wire.levels}
    assert levels["b7_clock"].start_value == 10 * Q
    assert {"drift_left", "morning_13", "night_12"} <= levels.keys()
    assert not levels.keys() & {ln.store for ln in wire.ledger}


def test_only_the_stores_the_scene_reads_and_the_opening_defines_are_served(shipped_ruleset: ShippedRuleset):
    wire = Game(shipped_ruleset.opening, shipped_ruleset.rs).view(new_save(shipped_ruleset.rs.rules))
    served = {lv.store for lv in wire.levels}
    assert served - {"hurt"} <= scene_stores() == named_in_the_scene()
    assert [lv.store for lv in wire.levels][:1] == ["hurt"]
