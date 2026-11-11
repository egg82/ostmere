"""Rules (orders) and the queue are bounded per save (api/CONTRACT.txt, "Request limits"), and the page is served the
two bounds its editors stop at. A request past a bound does not fit the models: 422 invalid_decision."""
from typing import Any

from pydantic import ValidationError

from ashfall_app.api.saves_models import DecisionRequest
from tests.game_client import GameClient

Json = dict[str, Any]
TAP: Json = {"kind": "tap_card", "card": "stand_up"}
ORDER: Json = {"when": {"kind": "after_time", "at": 0}, "then": TAP}
QUEUE_ENTRY: Json = {"verb": TAP, "until": {"kind": "after_time", "at": 0}}


def refused(body: Json) -> bool:
    try:
        DecisionRequest.model_validate({"decision": body, "after": 0})
    except ValidationError:
        return True
    return False


def test_the_bounds_leave_room_for_what_a_game_holds():
    assert not refused({"kind": "set_orders", "orders": [ORDER] * 64})
    assert not refused({"kind": "set_queue", "entries": [QUEUE_ENTRY] * 64})


def test_orders_are_at_most_64():
    assert refused({"kind": "set_orders", "orders": [ORDER] * 65})


def test_queue_entries_are_at_most_64():
    assert refused({"kind": "set_queue", "entries": [QUEUE_ENTRY] * 65})


def test_an_oversized_list_is_answered_422_naming_the_bound(game: GameClient):
    save = game.begin()["save"]["save_id"]
    r = game.decide(save, {"kind": "set_orders", "orders": [ORDER] * 65}, after=0)
    assert r.status_code == 422 and "at most 64" in r.json()["message"]


def test_the_page_is_served_the_bounds_its_editors_stop_at(game: GameClient):
    assert game.client.get("/api/content").json()["limits"] == {"max_orders": 64, "max_queue": 64, "max_mixes": 64}
