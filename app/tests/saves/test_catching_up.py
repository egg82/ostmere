"""A long absence through the saves service in bounded slices (saves/service.py; CONTRACT.txt, "Catching up"), with a
stop that ends every request after its first instant: each slice is written with catching_up_to, a decision whose
advance stops short is written as that slice and refused (Behind), a dry run that would stop short writes nothing,
and the slices end where one unbounded advance does."""
import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.db import saves as rows
from ashfall_app.saves.interface import Behind, Ruleset
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))
AWAY_S = 6 * 3600


def stored(engine: Engine, save_id: int) -> rows.SaveRecord:
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None
    return row


def test_slices_are_written_until_caught_up_and_a_decision_waits_for_them(engine: Engine, rs: Ruleset,
                                                                        clock: FakeClock, account: int):
    saves = PgSaves(engine, rs, clock, stop_for=lambda: lambda: True)
    info, _ = saves.create(account)
    first = saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(AWAY_S)
    whole = e.advance_logged(first.save, rs.rules, first.save.time + AWAY_S)

    with pytest.raises(Behind) as behind:
        saves.decide(account, info.save_id, STAND, after=1)
    played = behind.value.played
    assert played.catching_up_to == AWAY_S + first.save.time and played.save.time < AWAY_S
    row = stored(engine, info.save_id)
    assert row.decisions == 1 and row.game_time == played.save.time   # written as an advance, the verb not applied

    with pytest.raises(Behind):
        saves.dry_run(account, info.save_id, (STAND,))
    assert stored(engine, info.save_id) == row   # a dry run writes nothing

    lines, slices = list(played.lines), 1
    while played.catching_up_to is not None:
        played, slices = saves.advance(account, info.save_id), slices + 1
        lines += played.lines
    assert slices > 2   # control: the absence really came back in slices
    assert played.save == whole.save and tuple(ln.key for ln in lines) == tuple(ln.key for ln in whole.lines)
    assert saves.decide(account, info.save_id, STAND, after=1).decisions == 2
