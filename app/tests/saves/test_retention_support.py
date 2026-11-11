"""What the saves writer keeps: decisions 30 days, one snapshot a UTC day for 30 days, lines for good; and the support
tools that replay and restore from them."""
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, FromClause, event, func, select

from ashfall_app import engine as e
from ashfall_app.db import saves as rows
from ashfall_app.db.tables import save_decisions, save_lines, save_snapshots
from ashfall_app.saves import __main__ as cli
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.service import PgSaves
from ashfall_app.saves.support import SupportError, replay, restore
from ashfall_app.saves.write import day_of
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))   # three taps complete it
LOOK = e.TapCard(e.CardId("look_around"))   # open once stand_up is complete


def n_rows(engine: Engine, table: FromClause) -> int:
    with engine.connect() as conn:
        return int(conn.execute(select(func.count()).select_from(table)).scalar_one())


def logged(engine: Engine, save_id: int) -> list[int]:
    with engine.connect() as conn:
        return [d.n for d in rows.decisions_after(conn, save_id, 0)]


def days_kept(engine: Engine) -> list[int]:
    with engine.connect() as conn:
        return sorted(int(d) for d in conn.execute(select(save_snapshots.c.day)).scalars())


def test_decisions_are_kept_thirty_days_by_the_decision_that_writes_the_next(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    saves.decide(account, info.save_id, STAND, after=0)        # wall T0
    clock.tick(days=30)
    saves.advance(account, info.save_id)
    assert logged(engine, info.save_id) == [1]                # an advance prunes nothing
    saves.decide(account, info.save_id, STAND, after=1)       # T0 + 30 d: the first is exactly at the limit, kept
    assert logged(engine, info.save_id) == [1, 2]
    clock.tick(60)
    saves.decide(account, info.save_id, STAND, after=2)       # T0 + 30 d + 1 min: the first is past it
    assert logged(engine, info.save_id) == [2, 3]


def test_one_snapshot_a_utc_day_kept_thirty_days_and_lines_kept_for_good(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    first = day_of(clock())
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(60)
    saves.decide(account, info.save_id, STAND, after=1)       # the same day: no second snapshot
    assert days_kept(engine) == [first]
    clock.tick(days=30)
    saves.decide(account, info.save_id, STAND, after=2)       # day first + 30: day `first` is still in
    assert days_kept(engine) == [first, first + 30]
    lines = n_rows(engine, save_lines)
    clock.tick(days=1)
    saves.decide(account, info.save_id, LOOK, after=3)        # day first + 31: day `first` goes
    assert days_kept(engine) == [first + 30, first + 31]
    assert n_rows(engine, save_lines) >= lines + 1             # lines only ever grow


def test_replay_from_a_days_snapshot_matches_the_save(saves: PgSaves, engine: Engine, account: int, clock: FakeClock,
                                                     rs: Ruleset):
    info, _ = saves.create(account)
    day = day_of(clock())
    saves.decide(account, info.save_id, STAND, after=0)       # the day's snapshot is taken after this one
    clock.tick(10)
    saves.decide(account, info.save_id, STAND, after=1)
    clock.tick(30)
    saves.advance(account, info.save_id)
    got = replay(engine, rs, info.save_id, day)
    assert got.matches and got.decisions == 2
    with pytest.raises(SupportError):
        replay(engine, rs, info.save_id, day + 1)


def test_replay_sees_a_save_that_differs_from_its_log(saves: PgSaves, engine: Engine, account: int,
                                                      clock: FakeClock, rs: Ruleset):
    info, _ = saves.create(account)
    day = day_of(clock())
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(10)
    saves.decide(account, info.save_id, STAND, after=1)
    with engine.begin() as conn:   # the second decision's log entry lost: the replay comes up one tap short
        conn.execute(save_decisions.delete().where(save_decisions.c.n == 2))
    assert not replay(engine, rs, info.save_id, day).matches


def test_restore_keeps_the_row_then_sets_the_save_back(saves: PgSaves, engine: Engine, account: int,
                                                       clock: FakeClock, rs: Ruleset, tmp_path: Path):
    info, _ = saves.create(account)
    day = day_of(clock())
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(10)
    saves.decide(account, info.save_id, STAND, after=1)
    keep = tmp_path / "row.json"
    assert restore(engine, rs, clock, info.save_id, day, 1, keep) == 1   # the snapshot, taken after decision 1
    assert '"decisions": 2' in keep.read_text()
    with engine.connect() as conn:
        row = rows.save(conn, info.save_id, None)
    assert row is not None and row.decisions == 1 and row.game_time == 0
    with pytest.raises(FileExistsError):
        restore(engine, rs, clock, info.save_id, day, None, keep)   # never over a kept file


def test_a_restored_save_takes_its_next_decision(saves: PgSaves, engine: Engine, account: int, clock: FakeClock,
                                                 rs: Ruleset, tmp_path: Path):
    info, _ = saves.create(account)
    day = day_of(clock())
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(days=1)
    saves.decide(account, info.save_id, STAND, after=1)        # logged as 2, and snapshotted on the next day
    assert days_kept(engine) == [day, day + 1]
    assert restore(engine, rs, clock, info.save_id, day, 1, tmp_path / "row.json") == 1
    assert logged(engine, info.save_id) == [1] and days_kept(engine) == [day]
    saves.decide(account, info.save_id, STAND, after=1)        # the number 2 is free again
    assert logged(engine, info.save_id) == [1, 2]


def test_a_restore_to_a_count_the_snapshot_cannot_reach_is_refused_and_writes_nothing(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock, rs: Ruleset, tmp_path: Path):
    info, _ = saves.create(account)
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(days=1)
    day = day_of(clock())
    saves.decide(account, info.save_id, STAND, after=1)        # the day's snapshot holds 2 decisions
    with pytest.raises(SupportError):
        restore(engine, rs, clock, info.save_id, day, 1, tmp_path / "row.json")
    with engine.connect() as conn:
        row = rows.save(conn, info.save_id, None)
    assert row is not None and row.decisions == 2 and logged(engine, info.save_id) == [1, 2]
    assert not (tmp_path / "row.json").exists()


@pytest.fixture
def one_save(saves: PgSaves, account: int) -> None:
    saves.create(account)


@pytest.mark.usefixtures("one_save")
def test_the_command(pg_url: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli.main(["check"]) == 2
    monkeypatch.setenv("DATABASE_URL", pg_url)
    assert cli.main(["check"]) == 0
    assert "total=1 ok=1 failed=0 newer=0" in capsys.readouterr().out


def test_a_decision_does_not_send_the_save_to_the_database_for_a_snapshot_it_already_has(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    saves.decide(account, info.save_id, STAND, after=0)
    sent: list[int] = []

    @event.listens_for(engine, "before_cursor_execute")
    def watch(conn: object, cursor: object, statement: str, parameters: Any, context: object, many: bool) -> None:
        if "save_snapshots" in statement:
            sent.append(len(str(parameters)))

    clock.tick(60)
    saves.decide(account, info.save_id, STAND, after=1)
    clock.tick(60)
    saves.decide(account, info.save_id, STAND, after=2)
    event.remove(engine, "before_cursor_execute", watch)
    assert sent != [], "no snapshot statement seen: this test is blind"
    with engine.connect() as conn:
        row = rows.save(conn, info.save_id, account)
        assert row is not None
        assert max(sent) > len(row.state), "control: the save's own write carries the state"
        assert max(sent) < 2 * len(row.state), "a statement carried the save twice: the snapshot copies it in the database"
        snap = rows.snapshot(conn, info.save_id, day_of(clock()))
    assert snap is not None and snap.decisions == 1, "the day's first decision's save"
