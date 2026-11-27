"""The store rules with share levels the page's rule editor writes (client/fixtures/share_cases.json, which
client/test/game/condition/sharelevels.test.ts proves the editor builds and reads back) are orders the engine accepts: each, in a
set_orders and a set_queue through the wire models and the engine's decide on the shipped rules, becomes the save's,
and the view serves it back unchanged, flags included. A share level on a skill, one over 10000 and a share band on
the wrong side are refused, so the check can fail."""
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter

from ashfall_app import engine as e
from ashfall_app.api import models as w
from tests.shipped_ruleset import ShippedRuleset

Json = dict[str, Any]
CASES: list[Json] = json.loads((Path(__file__).resolve().parents[1] / "client/fixtures/share_cases.json").read_text())["cases"]
DECISION = TypeAdapter[w.Decision](w.Decision)


def _shipped(when: Json, game: ShippedRuleset) -> Json:
    when = json.loads(json.dumps(when))
    when["watched"]["store"] = str(game.rs.rules.stores[0].id)
    return when


def _decide(decision: Json, game: ShippedRuleset) -> tuple[e.Save, w.View]:
    rules = game.rs.rules
    g = game.make_game(game.opening, game.rs)
    save = e.new_save(rules)
    after = e.decide(save, rules, save.time, g.verb(DECISION.validate_python(decision)))
    return after, g.view(after)


def _tap(game: ShippedRuleset) -> Json:
    return {"kind": "tap_card", "card": str(game.rs.rules.cards[0].id)}


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_each_share_rule_the_editor_writes_is_an_order_the_engine_accepts(case: Json, shipped_ruleset: ShippedRuleset):
    when = _shipped(case["when"], shipped_ruleset)
    save, view = _decide({"kind": "set_orders", "orders": [{"when": when, "then": _tap(shipped_ruleset)}]}, shipped_ruleset)
    assert len(save.orders) == 1
    assert view.orders[0].when.model_dump(mode="json") == when
    save, view = _decide({"kind": "set_queue", "entries": [{"verb": _tap(shipped_ruleset), "until": when}]}, shipped_ruleset)
    assert view.queue == [] or view.queue[0].until.model_dump(mode="json") == when


def test_the_share_flags_are_optional_on_the_wire_and_default_to_amounts(shipped_ruleset: ShippedRuleset):
    """A page of the build before the flags sends conditions without them: they read as amounts."""
    when = _shipped({k: v for k, v in CASES[-1]["when"].items() if not k.endswith("_of_cap")}, shipped_ruleset)
    _, view = _decide({"kind": "set_orders", "orders": [{"when": when, "then": _tap(shipped_ruleset)}]}, shipped_ruleset)
    served = view.orders[0].when.model_dump(mode="json")
    assert served["value_of_cap"] is False and served["release_of_cap"] is False


@pytest.mark.parametrize("when", [
    {"kind": "at_least", "watched": {"kind": "skill_level", "skill": "?"}, "value": 5000, "release": 5000, "value_of_cap": True},
    {"kind": "at_most", "watched": {"kind": "store_value", "store": "?"}, "value": 2500, "release": 10001,
     "value_of_cap": True, "release_of_cap": True},
    {"kind": "at_most", "watched": {"kind": "store_value", "store": "?"}, "value": 5000, "release": 2500,
     "value_of_cap": True, "release_of_cap": True},
])
def test_a_share_level_the_engine_refuses_is_refused(when: Json, shipped_ruleset: ShippedRuleset):
    rules = shipped_ruleset.rs.rules
    w_ = json.loads(json.dumps(when))
    if w_["watched"]["kind"] == "skill_level":
        w_["watched"]["skill"] = str(rules.skills[0].id)
    else:
        w_["watched"]["store"] = str(rules.stores[0].id)
    with pytest.raises(e.InvalidVerbError):
        _decide({"kind": "set_orders", "orders": [{"when": w_, "then": _tap(shipped_ruleset)}]}, shipped_ruleset)
