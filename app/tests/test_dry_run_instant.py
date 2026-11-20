"""A dry run answers at the instant of the save as last written, the instant the page's view shows (CONTRACT.txt,
dry-run), so every figure the page reads as before → after compares two views of one moment. Answered at the
server's now instead, a card's tap_s (the rest of its current completion) had counted down by the seconds between the
two, and a preview listed every running card as moved, or nothing, by when its request landed (#380)."""
from typing import Any

from tests.game_client import GameClient

SET_NO_ORDERS: dict[str, Any] = {"kind": "set_orders", "orders": []}


def test_a_dry_run_that_changes_nothing_answers_the_view_the_page_holds(game: GameClient):
    begun = game.begin()
    save_id = begun["save"]["save_id"]
    game.clock.tick(5)
    r = game.advance(save_id)
    assert r.status_code == 200, r.text
    held = r.json()["view"]
    assert held["at"] == 5
    game.clock.tick(7)
    r = game.client.post(f"/api/saves/{save_id}/dry-run", json={"decisions": [SET_NO_ORDERS]})
    assert r.status_code == 200, r.text
    after = r.json()
    assert after["at"] == held["at"]
    assert [(c["card"], c["tap_s"]) for c in after["cards"]] == [(c["card"], c["tap_s"]) for c in held["cards"]]
