"""The forecast has its own call, kept off every View (CONTRACT.txt, "Forecast"): it reads the save at now, writing nothing,
and answers the decision count it holds for and what lands by its horizon; no Step carries one."""
from ashfall_app.db import saves as rows
from tests.game_client import GameClient


def test_the_forecast_is_its_own_call_and_no_step_carries_one(game: GameClient):
    begun = game.begin()
    save = begun["save"]["save_id"]
    assert "forecast" not in begun["step"]["view"]
    game.clock.tick(seconds=30)
    asked = game.client.post(f"/api/saves/{save}/forecast")
    assert asked.status_code == 200, asked.text
    body = asked.json()
    assert body["decisions"] == 0 and body["forecast"]["horizon_at"] > 0
    decided = game.decide(save, {"kind": "tap_card", "card": "stand_up"}, after=0)
    assert decided.status_code == 200 and "forecast" not in decided.json()["view"]
    again = game.client.post(f"/api/saves/{save}/forecast").json()
    assert again["decisions"] == 1
    assert game.client.post(f"/api/saves/{save + 99}/forecast").status_code == 404


def test_a_forecast_writes_nothing_so_no_line_it_passes_is_lost(game: GameClient):
    save = game.begin()["save"]["save_id"]
    game.clock.tick(seconds=30)
    with game.app.state.db.engine.connect() as conn:
        before = rows.save(conn, save, None)
    assert game.client.post(f"/api/saves/{save}/forecast").status_code == 200
    with game.app.state.db.engine.connect() as conn:
        assert rows.save(conn, save, None) == before
