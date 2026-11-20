"""The forecast route's Game keeps the last forecast's path of the few saves forecast last and hands it to the next
forecast of that save (engine forecast.py, `kept`), so the page's forecast a minute on resolves only what is new."""
from collections.abc import Callable

import pytest

from ashfall_app import engine as e
from ashfall_app.api import service
from ashfall_app.api.service import KEPT_PATHS, Game
from ashfall_app.saves.interface import Played
from tests.shipped_ruleset import ShippedRuleset


def test_each_save_s_next_forecast_is_handed_its_last_path(shipped_ruleset: ShippedRuleset,
                                                            monkeypatch: pytest.MonkeyPatch):
    game, rules = Game(shipped_ruleset.opening, shipped_ruleset.rs), shipped_ruleset.rs.rules
    handed: list[tuple[int, e.ForecastPath | None]] = []
    made: list[e.ForecastPath | None] = []
    real = e.forecast

    def spied(save: e.Save, rules: e.Rules, until: int, stores: tuple[e.StoreId, ...] = (),
              stop: Callable[[], bool] | None = None, kept: e.ForecastPath | None = None) -> e.Forecast:
        handed.append((save.time, kept))
        f = real(save, rules, until, stores, stop, kept)
        made.append(f.path)
        return f

    monkeypatch.setattr(service.e, "forecast", spied)
    s = e.new_save(rules)
    ids = list(range(1, KEPT_PATHS + 2))
    for i in ids:
        game.forecast(Played(save_id=i, decisions=0, save=s, lines=()), lambda: False)
    later = e.advance(s, rules, 60)
    game.forecast(Played(save_id=ids[-1], decisions=0, save=later, lines=()), lambda: False)
    game.forecast(Played(save_id=ids[0], decisions=0, save=later, lines=()), lambda: False)
    assert [k for _, k in handed[:len(ids)]] == [None] * len(ids)
    assert handed[len(ids)][1] is made[len(ids) - 1] is not None
    assert handed[len(ids) + 1][1] is None   # the oldest save's path was let go
