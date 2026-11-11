"""A forecast is cut by the same per-request stop an advance is (saves/service.py `stop_for`) and ends at the horizon it
reached, which the answer names (api/CONTRACT.txt, "Forecast"); a stop that never fires changes nothing."""
from collections.abc import Callable

import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.service import PgSaves
from ashfall_app.services import Services
from tests.game_client import GameClient
from tests.saves.chunks import every, golden, never, todays_rules

HOURS_6 = 6 * 3600


def forecast(stop: Callable[[], bool] | None = None) -> e.Forecast:
    save = golden("f7/05-seed0-end526")
    return e.forecast(save, todays_rules(), save.time + HOURS_6, (), stop)


@pytest.fixture(scope="module")
def full() -> e.Forecast:
    return forecast()


def test_the_golden_save_has_instants_to_cut(full: e.Forecast):
    assert full.until > 0


def test_a_stop_ends_the_forecast_at_a_shorter_horizon(full: e.Forecast):
    assert forecast(every(1)()).until < full.until


def test_a_stop_that_never_fires_changes_nothing(full: e.Forecast):
    assert forecast(lambda: False) == full


def test_a_forecast_asked_over_the_api_is_cut_by_the_saves_stop(game: GameClient, shipped_opening: Opening):
    save = game.begin()["save"]["save_id"]
    game.clock.tick(seconds=30)
    whole = game.client.post(f"/api/saves/{save}/forecast").json()["forecast"]["horizon_at"]
    engine: Engine = game.app.state.db.engine
    rs = ruleset(shipped_opening, load_renames(), "dev", load_lock().release)
    old = game.app.state.services
    game.app.state.services = Services(accounts=old.accounts, saves=PgSaves(engine, rs, game.clock, stop_for=every(1)))
    cut = game.client.post(f"/api/saves/{save}/forecast").json()["forecast"]["horizon_at"]
    assert cut < whole


def test_a_forecast_request_spends_one_time_budget_on_the_read_and_the_replay(game: GameClient, shipped_opening: Opening):
    save = game.begin()["save"]["save_id"]
    game.clock.tick(seconds=30)
    engine: Engine = game.app.state.db.engine
    rs = ruleset(shipped_opening, load_renames(), "dev", load_lock().release)
    made: list[int] = []

    def stop_for() -> Callable[[], bool]:
        made.append(1)
        return never()

    old = game.app.state.services
    game.app.state.services = Services(accounts=old.accounts, saves=PgSaves(engine, rs, game.clock, stop_for=stop_for))
    assert game.client.post(f"/api/saves/{save}/forecast").status_code == 200
    assert made == [1]
