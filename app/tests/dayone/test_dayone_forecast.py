"""The forecast (engine forecast.py) is exactly what advance does with nobody deciding, on saves a real day-one play saw
(orders and the queue on): at each listed time a level lands, a store reaches its cap, a store runs to 0, and a second
before it had not; every level-up by the horizon is listed. Made earlier on the same path, it lists the same future,
so a plain advance may reuse it. Proven able to fail by a forecast planted one second late."""
from collections.abc import Mapping

import pytest

from ashfall_app.engine import Forecast, Rules, Save, SkillId, StoreId, UnlockKind, advance, forecast, view
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.player import DayOnePlayer
from tests.dayone.routes import day

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
HORIZON_S = 2 * 3600
LATER_S = 1800
Checked = tuple[list[str], list[str], list[str]]


def _levels(save: Save, rules: Rules) -> dict[str, int]:
    return {b.skill: b.level for b in view(save, rules).skills}


def _value(save: Save, rules: Rules, store: str) -> tuple[int, int]:
    line = next(x for x in view(save, rules).ledger if x.store == store)
    return line.segment.start_value, line.cap


def _lands(save: Save, rules: Rules, kind: str, store: str, at: int) -> bool:
    v0, cap0 = _value(advance(save, rules, at - 1), rules, store)
    v1, cap1 = _value(advance(save, rules, at), rules, store)
    return (v1 >= cap1 and v0 < cap0) if kind == "full" else (v1 == 0 and v0 > 0)


def problems(save: Save, rules: Rules, f: Forecast) -> list[str]:
    out: list[str] = []
    for skill, times in f.level_ups.items():
        for at in times:
            if not _levels(advance(save, rules, at), rules)[skill] > _levels(advance(save, rules, at - 1), rules)[skill]:
                out.append(f"level {skill} at +{at - save.time}s")
    start, end = _levels(save, rules), _levels(advance(save, rules, f.until), rules)
    listed = {str(k): len(v) for k, v in f.level_ups.items()}
    out += [f"{skill}: {end[skill] - start[skill]} level-ups by the horizon, {listed.get(skill, 0)} listed"
            for skill in start if end[skill] - start[skill] != listed.get(skill, 0)]
    for kind, found in (("full", f.fills), ("empty", f.empties)):
        out += [f"{kind} {store} at +{at - save.time}s" for store, times in found.items() for at in times
                if not _lands(save, rules, kind, store, at)]
    return out


def _cut(found: Mapping[SkillId, tuple[int, ...]] | Mapping[StoreId, tuple[int, ...]], since: int,
         until: int) -> dict[str, tuple[int, ...]]:
    return {str(k): kept for k, v in found.items() if (kept := tuple(t for t in v if since < t <= until))}


def overlap(early: Forecast, late: Forecast, since: int) -> list[str]:
    """What both forecasts cover past `since` (the later one's start) must be the same."""
    pairs = (("level_ups", early.level_ups, late.level_ups), ("fills", early.fills, late.fills),
             ("empties", early.empties, late.empties))
    return [f"{name} differ" for name, a, b in pairs
            if _cut(a, since, early.until) != _cut(b, since, early.until)]


def saves(p: DayOnePlayer, every_s: int = 600) -> list[Save]:
    """Saves the play saw after the end, at most one per `every_s`."""
    out: list[Save] = []
    for save, _ in p.history:
        if p.end_at is not None and save.time >= p.end_at and (not out or save.time - out[-1].time >= every_s):
            out.append(save)
    return out


def shown(save: Save) -> tuple[StoreId, ...]:
    return tuple(StoreId(u.id) for u in save.unlocked if u.kind is UnlockKind.STORE)


@pytest.fixture(scope="module", params=["typical", "babysitter"])
def checked(request: pytest.FixtureRequest) -> Checked:
    """(the real forecasts' problems, the same planted one second late, reuse mismatches), computed in setup: each
    check advances the play's saves several times over (docs/engineering.md, "Fast from the start")."""
    p = day(request.param)
    real: list[str] = []
    late: list[str] = []
    reuse: list[str] = []
    for save in saves(p)[:6]:
        f = forecast(save, p.rules, save.time + HORIZON_S, shown(save))
        real += problems(save, p.rules, f)
        if f.level_ups:
            shifted = {k: tuple(t + 1 for t in v) for k, v in f.level_ups.items()}
            late += problems(save, p.rules, Forecast(f.until, shifted, f.fills, f.empties))
        on = advance(save, p.rules, save.time + LATER_S)
        reuse += overlap(f, forecast(on, p.rules, on.time + HORIZON_S, shown(save)), on.time)
    return real, late, reuse


def test_the_forecast_is_what_happens_with_nobody_deciding(checked: Checked):
    assert checked[0] == []


def test_a_forecast_one_second_late_is_caught(checked: Checked):
    assert checked[1]


def test_a_forecast_made_earlier_on_the_same_path_lists_the_same_future(checked: Checked):
    assert checked[2] == []


INSTANTS_MAX = 240
"""The most instants one forecast at the served horizon may resolve over day one's saves: twice the 118 measured (the
typical route; babysitter's reach 56). A count, not a time, so the runner's speed and load do not move it: the CPU
ratio this replaced failed at 2.65 against its 2.4 on unchanged code on a loaded host. What one instant costs is the
engine bench's question (tools/bench_ab.py). The forecast is computed only when the page asks (CONTRACT.txt,
"Forecast"), never on a plain advance or a decision."""


@pytest.fixture(scope="module")
def forecast_work() -> list[tuple[int, bool]]:
    """(instants resolved, horizon reached) of the served forecast on 12 saves each from two plays, counted through the
    `stop` hook the API passes, which the forecast asks once before each instant."""
    from ashfall_app.api.service import FORECAST_S
    work: list[tuple[int, bool]] = []
    for name in ("typical", "babysitter"):
        p = day(name)
        found = saves(p, every_s=1)
        for save in found[:: max(1, len(found) // 12)][:12]:
            asked = [0]

            def stop() -> bool:
                asked[0] += 1
                return False
            f = forecast(save, p.rules, save.time + FORECAST_S, shown(save), stop)
            work.append((asked[0], f.until == save.time + FORECAST_S))
    return work


def test_a_forecast_stays_inside_its_budget(forecast_work: list[tuple[int, bool]]):
    most = max(n for n, _ in forecast_work)
    assert most <= INSTANTS_MAX, f"a forecast resolved {most} instants, over {INSTANTS_MAX}"


def test_a_served_forecast_reaches_its_horizon(forecast_work: list[tuple[int, bool]]):
    """None stops at MAX_INSTANTS short of the horizon, where nothing past it would be known."""
    assert len(forecast_work) == 24 and all(reached for _, reached in forecast_work)
