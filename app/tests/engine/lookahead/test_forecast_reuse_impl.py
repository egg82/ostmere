"""A forecast handed an earlier forecast's path (engine forecast.py, `kept`) takes the instants it already resolved
when the save is on that path, and gives the answer a forecast without it gives (engine/design/, "Forecast"). The page
asks for a forecast every minute, each from the save a minute on: without the path each one resolved its every instant
again (issue 400)."""
import importlib

import pytest

from ashfall_app.engine import (
    BP, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, Rules, Save, SaveMix, SkillDef, SkillId, StoreDef,
    StoreId, SwitchMix, advance, decide, decode, encode, new_save, per_hour, units, validate_rules,
)
from ashfall_app.engine.lookahead.forecast import MAX_INSTANTS, forecast

forecasting = importlib.import_module("ashfall_app.engine.lookahead.forecast")
"""The module: the engine package's `forecast` is the function."""

WOOD, TOOLS = StoreId("wood"), StoreId("tools")
CHOP, MEND = CardId("chop"), CardId("mend")
H = 3600


def world() -> tuple[Rules, Save]:
    """chop fills wood and trains its skill; mend has a cap, so each of its completions, one a minute at its half
    share, is an instant."""
    r = Rules(stores=(StoreDef(WOOD, units(20)), StoreDef(TOOLS, units(10**6))), skills=(SkillDef(SkillId("k")),),
              standing=(), curve=PacingCurve((units(5), units(20), units(60))),
              cards=(CardDef(CHOP, 60, skill=SkillId("k"), xp_per_hour=per_hour(10), makes=(Flow(WOOD, per_hour(20)),)),
                     CardDef(MEND, 30, cap=10**6, makes=(Flow(TOOLS, per_hour(1)),))))
    validate_rules(r)
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m"), (CardShare(CHOP, 5000), CardShare(MEND, 5000)))))
    return r, decide(s, r, 0, SwitchMix(MixId("m")))


def counted(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    times: list[int] = []
    real = forecasting.resolve_instant

    def resolve(save: Save, *rest: object, **kw: object) -> Save:
        times.append(save.time)
        return real(save, *rest, **kw)

    monkeypatch.setattr(forecasting, "resolve_instant", resolve)
    return times


def test_a_forecast_a_minute_on_resolves_only_the_instants_past_the_last_one(monkeypatch: pytest.MonkeyPatch):
    r, s = world()
    first = forecast(s, r, s.time + 3 * H, (WOOD,))
    later = decode(encode(advance(s, r, s.time + 90), r), r)   # the save as a later request reads it
    fresh = forecast(later, r, later.time + 3 * H, (WOOD,))
    times = counted(monkeypatch)
    again = forecast(later, r, later.time + 3 * H, (WOOD,), kept=first.path)
    assert again == fresh and fresh.level_ups and fresh.fills
    assert times and all(t > first.until for t in times)


def test_a_path_the_save_left_is_not_reused(monkeypatch: pytest.MonkeyPatch):
    r, s = world()
    first = forecast(s, r, s.time + 3 * H, (WOOD,))
    other = decide(advance(s, r, s.time + 90), r, s.time + 90, SaveMix(Mix(MixId("m"), (CardShare(CHOP, BP),))))
    fresh = forecast(other, r, other.time + 3 * H, (WOOD,))
    times = counted(monkeypatch)
    assert forecast(other, r, other.time + 3 * H, (WOOD,), kept=first.path) == fresh
    assert fresh.path is not None and len(times) == len(fresh.path.legs) - 1


def test_reused_instants_count_toward_max_instants():
    """mend lands 60 times an hour: a ten-hour forecast stops at MAX_INSTANTS, and so does one handed that path."""
    r, s = world()
    first = forecast(s, r, s.time + 10 * H)
    later = advance(s, r, s.time + 90)
    again = forecast(later, r, later.time + 10 * H, kept=first.path)
    assert first.until < s.time + 10 * H
    assert again == forecast(later, r, later.time + 10 * H)
    assert again.path is not None and len(again.path.legs) == MAX_INSTANTS + 1


def test_a_shorter_forecast_stops_at_its_own_until_on_a_longer_path():
    r, s = world()
    first = forecast(s, r, s.time + 3 * H, (WOOD,))
    later = advance(s, r, s.time + 90)
    assert forecast(later, r, later.time + 600, (WOOD,), kept=first.path) == forecast(later, r, later.time + 600, (WOOD,))
