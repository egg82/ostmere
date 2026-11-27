"""Next's row over the wire (contract/endpoints.txt, "Next's row"): an Order may carry below_next; an old page sends none and the
save is as it was; set_orders makes the rules after the first under Next a run to the end; the view serves the flag and
a rule_run's order without it. Run through the wire models and the engine on the shipped rules."""
from typing import Any

import pytest
from pydantic import TypeAdapter

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.engine import codec
from ashfall_app.engine.rulelog import rule_changes
from tests.shipped_ruleset import ShippedRuleset

Json = dict[str, Any]
DECISION = TypeAdapter[w.Decision](w.Decision)
ALWAYS: Json = {"kind": "after_time", "at": 0}
LOW_WOOD: Json = {"kind": "at_most", "watched": {"kind": "store_value", "store": "damp_wood"}, "value": 100, "release": 200}


class Play:
    def __init__(self, shipped: ShippedRuleset) -> None:
        self.rules = shipped.rs.rules
        self.game: Game = shipped.make_game(shipped.opening, shipped.rs)
        self.save = e.new_save(self.rules)

    def decide(self, decision: Json) -> w.View:
        self.save = e.decide(self.save, self.rules, self.save.time, self.game.verb(DECISION.validate_python(decision)))
        return self.game.view(self.save)


@pytest.fixture
def play(shipped_ruleset: ShippedRuleset) -> Play:
    p = Play(shipped_ruleset)
    p.decide({"kind": "save_mix", "mix": {"id": "m1", "components": [{"kind": "card_share", "card": "stand_up", "share_bp": 10000}]}})
    return p


def _rule(when: Json, **more: Any) -> Json:
    return {"when": when, "then": {"kind": "switch_mix", "mix_id": "m1"}, **more}


def test_an_old_page_sends_no_flag_and_the_save_is_as_it_was(play: Play):
    view = play.decide({"kind": "set_orders", "orders": [_rule(ALWAYS)]})
    assert "below_next" not in codec.encode(play.save, play.rules)
    assert view.orders[0].model_dump(mode="json")["below_next"] is False


def test_rules_after_the_first_under_next_are_under_it_and_served_so(play: Play):
    view = play.decide({"kind": "set_orders", "orders": [_rule(LOW_WOOD), _rule(ALWAYS, below_next=True), _rule({**LOW_WOOD, "value": 50})]})
    assert [o.below_next for o in play.save.orders] == [False, True, True]
    assert [o.below_next for o in view.orders] == [False, True, True]


def test_a_rule_run_names_its_rule_without_the_row(play: Play):
    """The rule log, which rule_runs serve, names a rule under Next unplaced; the flag itself round-trips the wire."""
    before = play.save
    play.decide({"kind": "set_orders", "orders": [_rule(ALWAYS, below_next=True)]})
    changes = rule_changes(before, play.save, play.rules)
    assert [c.order.below_next for c in changes] == [False] and changes[0].on
    assert convert.from_order(convert.order(play.save.orders[0]), play.rules) == play.save.orders[0]
