"""A long absence over the API (api/CONTRACT.txt, Step and ERRORS): every Step says whether it is still catching up
and to what game time, and a decision, a forecast or a dry run on a save that is behind is refused with a 409
`catching_up` rather than applied. The app is the real one on a test database; its saves service is given a stop that
cuts every request after five instants, since which stop production uses is not part of the contract."""
from typing import Any

import pytest
from sqlalchemy import Engine

from ashfall_app.db import saves as rows
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.service import PgSaves
from ashfall_app.services import Services
from tests.game_client import GameClient
from tests.saves.behind import AWAY_S, seed
from tests.saves.chunks import MakeStop, Stop, every

Json = dict[str, Any]
SET_NO_ORDERS: Json = {"kind": "set_orders", "orders": []}


@pytest.fixture
def behind(game: GameClient, shipped_opening: Opening) -> int:
    """The id of a save of the signed-in account that is AWAY_S behind the clock, served by slices of five instants."""
    engine, rs, account = serve(game, shipped_opening, every(5))
    save_id = seed(engine, rs, account, game.clock())
    game.clock.tick(AWAY_S)
    return save_id


def serve(game: GameClient, opening: Opening, stop_for: MakeStop) -> tuple[Engine, Ruleset, int]:
    """Gives the app a saves service whose requests stop by `stop_for`; the engine, the ruleset and the signed-in account."""
    begun = game.begin()["save"]["save_id"]
    engine: Engine = game.app.state.db.engine
    rs = ruleset(opening, load_renames(), "dev", load_lock().release)
    with engine.connect() as conn:
        row = rows.save(conn, begun, None)
    assert row is not None
    old = game.app.state.services
    game.app.state.services = Services(accounts=old.accounts, saves=PgSaves(engine, rs, game.clock, stop_for=stop_for))
    return engine, rs, row.account_id


def stored(game: GameClient, save_id: int) -> tuple[Any, ...]:
    with game.app.state.db.engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None
    return (row.state, row.game_time, row.decisions, row.updated_at)


def test_a_step_says_what_it_is_catching_up_to_until_it_has_caught_up(game: GameClient, behind: int):
    ordinary = game.begin()["step"]
    assert "catching_up_to" in ordinary and ordinary["catching_up_to"] is None
    seen: list[int | None] = []
    for _ in range(200):
        r = game.advance(behind)
        assert r.status_code == 200, r.text
        step = r.json()
        seen.append(step["catching_up_to"])
        assert (step["catching_up_to"] is None) == (step["view"]["at"] == AWAY_S)
        if step["catching_up_to"] is None:
            break
    assert len(seen) > 1 and seen[:-1] == [AWAY_S] * (len(seen) - 1) and seen[-1] is None, seen


def test_a_decision_on_a_save_that_is_behind_is_a_409_with_the_slice_as_its_step(game: GameClient, behind: int):
    r = game.decide(behind, SET_NO_ORDERS, after=0)
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "catching_up" and body["merge"] is None
    step = body["step"]
    assert step["save_id"] == behind and step["decisions"] == 0 and step["catching_up_to"] == AWAY_S
    assert 0 < step["view"]["at"] < AWAY_S and step["lines"], "the slice that was written is the step"
    assert set(step) == set(game.advance(behind).json()), "the same shape as any Step, as stale's is"
    game.client.get("/api/me")   # the account still has its session after the refusal
    assert stored(game, behind)[2] == 0


def test_a_decision_goes_through_once_the_save_has_caught_up(game: GameClient, behind: int):
    for _ in range(200):
        if game.advance(behind).json()["catching_up_to"] is None:
            break
    r = game.decide(behind, SET_NO_ORDERS, after=0)
    assert r.status_code == 200, r.text
    assert r.json()["decisions"] == 1 and r.json()["catching_up_to"] is None


@pytest.mark.parametrize("path, body", [
    ("forecast", None),
    ("dry-run", {"decisions": [SET_NO_ORDERS]}),
], ids=["forecast", "dry-run"])
def test_a_forecast_or_a_dry_run_on_a_save_that_is_behind_is_refused_and_writes_nothing(
        game: GameClient, behind: int, path: str, body: Json | None):
    """Both are reads (CONTRACT.txt, "Forecast"): the 409's step is the save as stored, with no lines."""
    before = stored(game, behind)
    r = game.client.post(f"/api/saves/{behind}/{path}", json=body)
    assert r.status_code == 409 and r.json()["code"] == "catching_up", r.text
    assert stored(game, behind) == before
    step = r.json()["step"]
    assert step["lines"] == [] and step["catching_up_to"] == AWAY_S


@pytest.mark.parametrize("path, body", [
    ("forecast", None),
    ("dry-run", {"decisions": [SET_NO_ORDERS]}),
], ids=["forecast", "dry-run"])
def test_a_forecast_or_a_dry_run_replays_holding_no_database_connection(
        game: GameClient, shipped_opening: Opening, path: str, body: Json | None):
    """A replay is up to the whole budget of CPU; the pod's four connections are for requests that read and write."""
    pool = game.app.state.db.pool
    checked_out: list[int] = []

    def stop_for() -> Stop:
        def stop() -> bool:
            stats = pool.get_stats()
            checked_out.append(stats["pool_size"] - stats["pool_available"])
            return len(checked_out) % 5 == 0
        return stop

    engine, rs, account = serve(game, shipped_opening, stop_for)
    save_id = seed(engine, rs, account, game.clock())
    game.clock.tick(AWAY_S)
    r = game.client.post(f"/api/saves/{save_id}/{path}", json=body)
    assert r.status_code == 409 and r.json()["code"] == "catching_up", r.text
    assert len(checked_out) >= 5, "the replay asked its stop"
    assert max(checked_out) == 0, checked_out
