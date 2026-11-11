"""A new save starts with no cap rule (docs/decisions.md, "Hitting a cap is a rule for the player to write"): the
shipped content's new save holds no order and no queued one-off, on the engine and on the wire, and two days left
alone install none. The only rules content can install are a ruled lane's always rule (engine DESIGN.txt, "Installed
rule"), an arrival's first task among them."""
from ashfall_app import engine as e
from tests.game_client import GameClient
from tests.shipped_ruleset import ShippedRuleset

DAY_S = 24 * 3600


def test_a_new_save_has_no_orders_and_nothing_queued(shipped_ruleset: ShippedRuleset):
    save = e.new_save(shipped_ruleset.rs.rules)
    assert save.orders == ()
    assert save.queue == ()


def test_two_days_left_alone_install_nothing(shipped_ruleset: ShippedRuleset):
    rules = shipped_ruleset.rs.rules
    save = e.advance(e.new_save(rules), rules, 2 * DAY_S)
    assert save.time == 2 * DAY_S
    assert save.orders == ()
    assert save.queue == ()


def test_a_new_game_on_the_wire_has_no_rules(game: GameClient):
    view = game.begin()["step"]["view"]
    assert "orders" in view and "queue" in view
    assert view["orders"] == []
    assert view["queue"] == []
