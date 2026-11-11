"""The conditions the page's rule editor writes on a count and a level (client/fixtures/
subject_cases.json, which client/test/subjectrules.test.ts proves the editor writes and reads back) are rules the engine
accepts: each, in a set_orders through the wire models and the engine's decide on the shipped rules, becomes the save's
order, and the view serves it back unchanged. Ids are swapped for shipped ones of the same kind, a Camp level's `at` for
the shipped level's. A release on the wrong side and an unknown card are refused, so the check can fail; so is a
condition on Running, which is why the editor offers none."""
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter

from ashfall_app import engine as e
from ashfall_app.api import models as w
from tests.shipped_ruleset import ShippedRuleset

Json = dict[str, Any]
CASES_FILE = Path(__file__).resolve().parents[1] / "client/fixtures/subject_cases.json"
CASES: list[Json] = json.loads(CASES_FILE.read_text())["cases"]
DECISION = TypeAdapter[w.Decision](w.Decision)


def shipped_when(case: Json, game: ShippedRuleset) -> Json:
    """The case's condition with shipped ids: the first card and skill; the Camp store and level."""
    rules = game.rs.rules
    when = json.loads(json.dumps(case["when"]))
    watched = when["watched"]
    if watched["kind"] == "card_count":
        watched["card"] = str(rules.cards[0].id)
    elif watched["kind"] == "skill_level":
        watched["skill"] = str(rules.skills[0].id)
    else:
        camp = game.make_game(game.opening, game.rs).content().camp
        assert camp is not None
        watched["store"] = camp.store
        level: int = case["camp_level"]
        when["value"] = when["release"] = camp.camp_levels[level - 1].at
    return when


def set_orders(when: Json, game: ShippedRuleset) -> tuple[e.Save, w.Order]:
    """A fresh shipped save after a set_orders holding one rule on `when` that taps the first card."""
    rules = game.rs.rules
    order = {"when": when, "then": {"kind": "tap_card", "card": str(rules.cards[0].id)}}
    g = game.make_game(game.opening, game.rs)
    save = e.new_save(rules)
    verb = g.verb(DECISION.validate_python({"kind": "set_orders", "orders": [order]}))
    after = e.decide(save, rules, save.time, verb)
    return after, g.view(after).orders[0]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_each_condition_the_editor_writes_is_an_order_the_engine_accepts(case: Json, shipped_ruleset: ShippedRuleset):
    when = shipped_when(case, shipped_ruleset)
    save, served = set_orders(when, shipped_ruleset)
    assert len(save.orders) == 1
    assert served.when.model_dump(mode="json") == when


@pytest.mark.parametrize("bad", ["release", "card"])
def test_a_wrong_shape_or_an_unknown_card_is_refused(bad: str, shipped_ruleset: ShippedRuleset):
    when = shipped_when(CASES[0], shipped_ruleset)
    assert when["watched"]["kind"] == "card_count"
    if bad == "release":
        when["release"] = when["value"] + 1
    else:
        when["watched"]["card"] = "no_such_card"
    with pytest.raises(e.InvalidVerbError):
        set_orders(when, shipped_ruleset)


def test_every_kind_the_editor_writes_has_a_case():
    kinds = {(c["when"]["kind"], c["when"]["watched"]["kind"]) for c in CASES}
    assert kinds == {("at_least", "card_count"), ("at_least", "skill_level"), ("at_least", "store_value")}


def test_a_running_condition_is_refused(shipped_ruleset: ShippedRuleset):
    runner = str(shipped_ruleset.rs.rules.cards[0].id)
    with pytest.raises(e.InvalidVerbError, match="running"):
        set_orders({"kind": "at_least", "watched": {"kind": "running", "runner": runner}, "value": 1, "release": 1},
                   shipped_ruleset)
