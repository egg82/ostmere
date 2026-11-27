"""A step writes the loss runners' notes at each day's end it passes (api/contract/loss-lines.txt, "LOSS LINES"): the tallies are
read at the day's end whatever the steps were, so many small steps store what one long advance stores, and a fold's
count is stored and read back. The tally is fixtures/loss_tick.toml's store, which grows by one an hour from the first
minute."""
from dataclasses import replace
from pathlib import Path

import pytest
from sqlalchemy import select

from ashfall_app.db import accounts
from ashfall_app.db.engine import open_database
from ashfall_app.db.migrate import migrate
from ashfall_app.db.tables import save_journal
from ashfall_app.opening.schema import OPENING, load_opening
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.journal_rules import LossRunner
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "loss_tick.toml"
POOL = ("t_s_tick", "t_a_ticker")
HOUR = 3600


@pytest.fixture(scope="module")
def ticking() -> Ruleset:
    rs = ruleset(load_opening(OPENING, (FIXTURE,)), "t", 1)
    assert rs.journal is not None
    return replace(rs, journal=replace(rs.journal, losses=(LossRunner("t_runner", "t_tick", POOL),)))


def _stepped(url: str, rs: Ruleset, steps: list[int]) -> tuple[int, list[tuple[int, list[dict[str, object]]]]]:
    database = open_database(url, max_size=2)
    try:
        clock = FakeClock()
        with database.engine.begin() as conn:
            account = accounts.create_account(conn, clock())
        saves = PgSaves(database.engine, rs, clock, stop_for=lambda: lambda: False)
        save_id = saves.create(account)[0].save_id
        for s in steps:
            clock.tick(s)
            saves.advance(account, save_id)
        j = save_journal.c
        with database.engine.begin() as conn:
            found = conn.execute(select(j.day, j.notes).where(j.save_id == save_id).order_by(j.day)).all()
        return save_id, [(r.day, [n for n in r.notes if n["subject"] == "t_runner"]) for r in found]
    finally:
        database.close()


STEPS = [7 * HOUR + 13 * 60] * 10
"""Ten steps of 7h13m: three days, each day's end mid-step."""


def test_each_day_end_tells_that_day_s_whole_losses_once(pg_url: str, ticking: Ruleset):
    _, rows = _stepped(pg_url, ticking, STEPS)
    told = {day: [(n["slot"], n.get("count")) for n in notes] for day, notes in rows}
    assert told[0] == [("loss", None), ("fold", 22)]
    assert told[1] == [("loss", None), ("fold", 23)]
    assert told[2] == [("loss", None), ("fold", 23)]
    assert told[3] == []
    assert all(n["key"] in POOL for _, notes in rows for n in notes if n["slot"] == "loss")


def test_small_steps_and_one_long_advance_store_the_same_loss_notes(pg_url: str, pg_empty: str, ticking: Ruleset):
    """Two databases, so the two saves share an id: every draw is keyed by it."""
    migrate(pg_empty)
    assert _stepped(pg_url, ticking, STEPS) == _stepped(pg_empty, ticking, [sum(STEPS)])
