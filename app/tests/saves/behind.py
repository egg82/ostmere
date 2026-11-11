"""A save that is far behind its clock, for the catching-up suites: a golden save written at game time 526 whose
row began `now`, so one tick of the fake clock puts the game hours ahead of the save."""
from datetime import datetime

from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.db import saves as rows
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.write import written
from tests.saves.chunks import golden

NAME = "f7/05-seed0-end526"
SAVED_AT = 526
AWAY_S = 3600
"""How far the tests move the clock: some twenty-five instants for this save."""


def seed(engine: Engine, rs: Ruleset, account: int, now: datetime) -> int:
    """A new live row for `account` holding the golden save, begun at `now`."""
    with engine.begin() as conn:
        return rows.insert_save(conn, account, now, written(golden(NAME, rs.rules), 0, rs))


BUSY_AWAY_S = 4 * 3600
"""Long enough for the rules of seed_busy to start and let go several times over."""
_M = 1_000_000


def seed_busy(engine: Engine, rs: Ruleset, account: int, now: datetime) -> int:
    """As seed, with more rules in play than a save keeps records of (saves.ruleruns.KEPT): the save's own two, one that
    starts early and lets go late, and nine that start one after another in between."""
    save, rules = golden(NAME, rs.rules), rs.rules
    then = e.SwitchMix(e.MixId("Main"))
    late = e.Order(e.AtLeast(e.StoreValue(e.StoreId("dry_wood")), 30 * _M, 12 * _M), then)
    stepping = tuple(e.Order(e.AtLeast(e.StoreValue(e.StoreId("night")), n * _M, (n - 1) * _M), then)
                     for n in range(15, 70, 6))
    save = e.decide(save, rules, save.time, e.SetOrders((*save.orders, late, *stepping)))
    with engine.begin() as conn:
        return rows.insert_save(conn, account, now, written(save, 0, rs))


def snapshot(engine: Engine, save_id: int) -> tuple[object, ...]:
    """What a save stores that catching up must not depend on how it was sliced: state, counters, rule runs, lines."""
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
        assert row is not None
        lines = [(ln.at, ln.key) for ln in rows.last_lines(conn, save_id, 100_000)]
    return (row.state, row.game_time, row.decisions, row.ended_at, row.camp_level, row.rule_runs, lines)
