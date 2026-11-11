"""verb_to_json / verb_from_json: every kind of verb round-trips, and nothing else reads as one."""
import pytest

from ashfall_app.engine import (
    AnswerKind, AtMost, CardId, CardShare, DeleteMix, KindId, Mix, MixId, Order, QueueEntry, RoleId, SaveMix, SetOrders, SetQueue,
    StateFormatError, StoreId, StoreValue, SwitchMix, TapCard, Verb, verb_from_json, verb_to_json,
)
from ashfall_app.engine.codec import Json, to_json

WHEN = AtMost(StoreValue(StoreId("wood")), 5, 9)
VERBS: list[Verb] = [
    TapCard(CardId("stand_up")),
    SwitchMix(MixId("m")),
    SaveMix(Mix(MixId("m"), (CardShare(CardId("gather"), 10_000),))),
    DeleteMix(MixId("m")),
    SetOrders((Order(WHEN, TapCard(CardId("gather"))),)),
    SetQueue((QueueEntry(TapCard(CardId("gather")), WHEN),)),
    SetOrders(()),
    SetOrders((Order(WHEN, AnswerKind(KindId("ask"), RoleId("yes"))),)),
]


@pytest.mark.parametrize("verb", VERBS, ids=lambda v: type(v).__name__)
def test_every_verb_round_trips(verb: Verb):
    assert verb_from_json(verb_to_json(verb)) == verb


@pytest.mark.parametrize("value", [
    None, 3, "tap", [], {"@": "Nope"}, {"@": "TapCard"}, {"@": "TapCard", "card": "a", "extra": 1},
    to_json(StoreValue(StoreId("wood"))),   # an engine value, but not a verb
])
def test_anything_else_is_a_state_format_error(value: Json):
    with pytest.raises(StateFormatError):
        verb_from_json(value)
