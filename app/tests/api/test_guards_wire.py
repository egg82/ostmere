"""Rule guards and fallbacks over the wire (contract/endpoints.txt, "Rule guards"; docs/design/rule-guards.md, "The saved shape"):
an Order carries `unless` and `or_else`, the View serves `order_guards`, `order_doing` and the state `paused`, and a rule
with neither encodes and reads as it did before. Run through the wire models and the engine on the shipped rules."""
import json
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.engine import codec
from ashfall_app.main import create_app
from tests.shipped_ruleset import ShippedRuleset

Json = dict[str, Any]
DECISION = TypeAdapter[w.Decision](w.Decision)
ALWAYS: Json = {"kind": "after_time", "at": 0}
LOW_WOOD: Json = {"kind": "at_most", "watched": {"kind": "store_value", "store": "damp_wood"}, "value": 100, "release": 200}


def _mix(mix_id: str, card: str) -> Json:
    return {"kind": "save_mix", "mix": {"id": mix_id, "components": [{"kind": "card_share", "card": card, "share_bp": 10000}]}}


def _switch(mix_id: str) -> Json:
    return {"kind": "switch_mix", "mix_id": mix_id}


def _orders(*orders: Json) -> Json:
    return {"kind": "set_orders", "orders": list(orders)}


class Play:
    """A save on the shipped rules that decisions, as the wire states them, are played into."""

    def __init__(self, shipped: ShippedRuleset) -> None:
        self.rules = shipped.rs.rules
        self.game: Game = shipped.make_game(shipped.opening, shipped.rs)
        self.save = e.new_save(self.rules)

    def decide(self, decision: Json) -> w.View:
        self.save = e.decide(self.save, self.rules, self.save.time, self.game.verb(DECISION.validate_python(decision)))
        return self.game.view(self.save)

    def advance(self, t: int) -> w.View:
        self.save = e.advance(self.save, self.rules, t)
        return self.game.view(self.save)


@pytest.fixture
def play(shipped_ruleset: ShippedRuleset) -> Play:
    return Play(shipped_ruleset)


def test_a_rule_with_no_guard_and_no_fallback_is_as_it_was(play: Play):
    """An old page sends neither field; the engine's rule is the one it always had, its saved text names neither, and
    the view serves empty lists and one empty guard list and no doing per rule."""
    play.decide(_mix("m1", "stand_up"))
    sent: Json = {"when": ALWAYS, "then": _switch("m1")}
    assert "unless" not in sent and "or_else" not in sent
    view = play.decide(_orders(sent))
    assert play.save.orders == (e.Order(e.AfterTime(0), e.SwitchMix(e.MixId("m1"))),)
    assert all(isinstance(latch, bool) for latch in play.save.latches)
    text = codec.encode(play.save, play.rules)
    assert "unless" not in text and "or_else" not in text
    served = view.orders[0].model_dump(mode="json")
    assert served["unless"] == [] and served["or_else"] == []
    assert view.order_guards == [[]] and view.order_doing == [0]
    assert view.order_states == [w.OrderState.ON]


def test_a_rule_sent_back_as_served_is_the_same_rule(play: Play):
    """The page sends the whole list back: what the view served is accepted and changes nothing, guards and fallbacks
    included, and the save's text is the same."""
    play.decide(_mix("m1", "stand_up"))
    play.decide(_mix("m2", "stand_up"))
    rule: Json = {"when": ALWAYS, "then": _switch("m1"), "unless": [LOW_WOOD], "or_else": [_switch("m2")]}
    view = play.decide(_orders(rule, {"when": ALWAYS, "then": _switch("m2")}))
    before = codec.encode(play.save, play.rules)
    again = play.decide(_orders(*[o.model_dump(mode="json") for o in view.orders]))
    assert again.orders == view.orders
    assert codec.encode(play.save, play.rules) == before


def test_unless_and_or_else_reach_the_engine_and_come_back(play: Play):
    play.decide(_mix("m1", "stand_up"))
    play.decide(_mix("m2", "stand_up"))
    rule: Json = {"when": ALWAYS, "then": _switch("m1"), "unless": [LOW_WOOD], "or_else": [_switch("m2")]}
    view = play.decide(_orders(rule))
    (order,) = play.save.orders
    assert [type(g) for g in order.unless] == [e.AtMost] and order.or_else == (e.SwitchMix(e.MixId("m2")),)
    served = view.orders[0].model_dump(mode="json")
    assert served["unless"] == [{**LOW_WOOD, "value_of_cap": False, "release_of_cap": False}]
    assert served["or_else"] == [_switch("m2")]


def test_a_paused_rule_is_paused_and_its_guard_serves_its_latch_and_release(play: Play):
    play.decide(_mix("m1", "stand_up"))
    skill = str(play.rules.skills[0].id)
    levelled: Json = {"kind": "at_least", "watched": {"kind": "skill_level", "skill": skill}, "value": 5, "release": 5}
    view = play.decide(_orders({"when": ALWAYS, "then": _switch("m1"), "unless": [LOW_WOOD, levelled]}))
    assert view.order_states == [w.OrderState.PAUSED]
    assert view.orders_on == [True]            # the `when` latch, whatever the guards say
    assert view.order_guards == [[w.OrderGuard(on=True, lets_go=200), w.OrderGuard(on=False, lets_go=None)]]
    assert view.order_doing == [None] and view.running_mix_id is None


def test_order_doing_names_the_action_the_rule_runs(play: Play):
    """m1 holds the card stand_up, which greys it once done; m2 is then the mix that runs, action 1 of the rule."""
    play.decide(_mix("m1", "stand_up"))
    rule: Json = {"when": ALWAYS, "then": _switch("m1")}
    assert play.decide(_orders(rule)).order_doing == [0]
    view = play.advance(120)
    assert view.greyed_mix_ids == ["m1"] and view.running_mix_id is None and view.order_doing == [None]
    play.decide(_mix("m2", "look_around"))
    view = play.decide(_orders({**rule, "or_else": [_switch("m2")]}))
    assert view.running_mix_id == "m2" and view.order_doing == [1] and view.order_states == [w.OrderState.ON]


def test_rule_runs_and_the_view_word_a_rule_alike(shipped_ruleset: ShippedRuleset):
    """A rule_run's `order` equals its rule in View.orders (contract/): both are convert.order."""
    rules = shipped_ruleset.rs.rules
    order = e.Order(e.AfterTime(0), e.SwitchMix(e.MixId("m1")),
                    (e.AtMost(e.StoreValue(rules.stores[0].id), 100, 200),), (e.SwitchMix(e.MixId("m2")),))
    wire = convert.order(order)
    assert wire.unless and wire.or_else
    assert convert.from_order(wire, rules) == order


@pytest.mark.parametrize("rule", [
    {"unless": [LOW_WOOD] * 4},
    {"or_else": [_switch("a"), _switch("b"), _switch("c")]},
], ids=["four guards", "four actions"])
def test_a_rule_past_the_limits_is_refused_before_the_engine_sees_it(rule: Json):
    with pytest.raises(ValidationError):
        DECISION.validate_python(_orders({"when": ALWAYS, "then": _switch("m1"), **rule}))


@pytest.mark.parametrize("rule", [
    {"unless": [{"kind": "at_least", "watched": {"kind": "running", "runner": "stand_up"}, "value": 1, "release": 1}]},
    {"unless": [LOW_WOOD, LOW_WOOD]},
    {"or_else": [_switch("m1")]},
    {"or_else": [{"kind": "tap_card", "card": "stand_up"}]},
], ids=["a running guard", "a guard twice", "an action twice", "a tap and a mix"])
def test_a_rule_the_engine_refuses_is_refused(play: Play, rule: Json):
    play.decide(_mix("m1", "stand_up"))
    with pytest.raises(e.InvalidVerbError):
        play.decide(_orders({"when": ALWAYS, "then": _switch("m1"), **rule}))


def test_the_spec_says_the_same():
    schemas = create_app().openapi()["components"]["schemas"]
    order = schemas["Order"]
    assert {"unless", "or_else"} <= set(order["properties"]) and not {"unless", "or_else"} & set(order["required"])
    assert order["properties"]["unless"]["maxItems"] == e.MAX_GUARDS
    assert order["properties"]["or_else"]["maxItems"] == e.MAX_ACTIONS - 1
    assert "paused" in schemas["OrderState"]["enum"]
    assert {"order_guards", "order_doing"} <= set(schemas["View"]["required"])
    assert set(schemas["OrderGuard"]["required"]) == {"on", "lets_go"}
    assert json.loads(json.dumps(schemas["OrderGuard"]))["properties"]["lets_go"]["anyOf"]   # int | null
