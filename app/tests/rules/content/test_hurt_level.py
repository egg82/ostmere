"""View.levels (contract/fights.txt, "FIGHTS", "read a level"): each store a lost fight adds to, as its segment, so the page
can draw its level though the store has no ledger line. Judged on the opening's own rules and a save holding hurt."""
from ashfall_app.api.goals.levels import levels
from ashfall_app.api.world.scenestores import scene_stores
from ashfall_app.engine import QUANTITY_SCALE as Q, StoreId
from ashfall_app.engine import view as engine_view
from tests.shipped_ruleset import ShippedRuleset
from tests.rules.content.test_poultice_tap import HURT, in_hand, rules


def test_hurt_is_served_as_the_store_it_is():
    s = in_hand(Q + Q // 2)
    got = levels(s, rules(), engine_view(s, rules()))
    assert [lv.store for lv in got] == ["hurt"]
    assert got[0].segment.start_value == Q + Q // 2


def test_a_store_no_fight_wounds_is_not_a_level():
    s = in_hand(0)
    assert {lv.store for lv in levels(s, rules(), engine_view(s, rules()))} == {"hurt"}
    assert "clay" not in {lv.store for lv in levels(s, rules(), engine_view(s, rules()))}


def test_the_store_has_no_ledger_line_to_read_instead():
    """The control: the page cannot read the level from the ledger, which is why levels is served."""
    s = in_hand(Q)
    assert HURT not in {ln.store for ln in engine_view(s, rules()).ledger}
    assert StoreId("hurt") == HURT


def test_the_game_serves_them_in_its_view(shipped_ruleset: ShippedRuleset):
    s = in_hand(Q + Q // 2)
    wire = shipped_ruleset.make_game(shipped_ruleset.opening, shipped_ruleset.rs).view(s)
    served = [(lv.store, lv.segment.start_value) for lv in wire.levels]
    assert served[0] == ("hurt", Q + Q // 2)
    assert {store for store, _ in served[1:]} <= scene_stores()
