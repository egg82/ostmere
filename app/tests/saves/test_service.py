"""The saves service on Postgres: a save made, decided, advanced and opened by the server's clock; stale, invalid and
foreign requests; what each write stores."""
import threading

import pytest
from sqlalchemy import Engine, select, update

from ashfall_app import engine as e
from ashfall_app import logs
from ashfall_app.db import accounts
from ashfall_app.db import saves as rows
from ashfall_app.db.tables import save_decisions, save_snapshots
from ashfall_app.db.tables import saves as saves_table
from ashfall_app.saves.interface import Invalid, NotFound, Ruleset, Stale
from ashfall_app.saves.service import PgSaves
from ashfall_app.saves.write import day_of
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))
LOCKED = e.TapCard(e.CardId("build_fireback"))


def stored(engine: Engine, save_id: int) -> rows.SaveRecord:
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None
    return row


def lines(engine: Engine, save_id: int) -> list[tuple[int, str]]:
    with engine.connect() as conn:
        return [(ln.at, ln.key) for ln in rows.last_lines(conn, save_id, 10_000)]


def test_a_new_save_starts_at_zero_under_this_builds_rules(saves: PgSaves, engine: Engine, account: int, rs: Ruleset):
    info, played = saves.create(account)
    row = stored(engine, info.save_id)
    assert (info.decisions, info.game_time, info.ended_at) == (0, 0, None)
    assert played.save == e.decode(row.state, rs.rules) and played.save.time == 0
    assert (row.rules_digest, row.format, row.build, row.release) == (rs.digest, e.FORMAT, "b2", 2)
    assert [ln.key for ln in played.lines] == list(rs.start_lines) and lines(engine, info.save_id) == [
        (0, str(k)) for k in rs.start_lines]
    assert saves.list(account) == [info]


def test_game_time_is_the_servers_clock_since_the_save_began(saves: PgSaves, engine: Engine, account: int,
                                                             clock: FakeClock):
    info, _ = saves.create(account)
    clock.tick(5)
    assert saves.advance(account, info.save_id).save.time == 5
    clock.tick(-60)   # another pod's clock behind: never before the time last written
    assert saves.advance(account, info.save_id).save.time == 5
    clock.tick(70)
    played = saves.decide(account, info.save_id, STAND, after=0)
    assert played.save.time == 15 and played.decisions == 1 and stored(engine, info.save_id).game_time == 15


def test_a_decision_is_written_with_its_log_entry_and_the_days_snapshot(saves: PgSaves, engine: Engine,
                                                                       account: int, clock: FakeClock, rs: Ruleset):
    info, _ = saves.create(account)
    clock.tick(2)
    played = saves.decide(account, info.save_id, STAND, after=0)
    row = stored(engine, info.save_id)
    assert row.decisions == 1 and e.decode(row.state, rs.rules) == played.save
    with engine.connect() as conn:
        logged = rows.decisions_after(conn, info.save_id, 0)
        snap = rows.snapshot(conn, info.save_id, day_of(clock()))
    assert [(d.n, d.at, d.kind) for d in logged] == [(1, 2, "tap_card")]
    assert e.verb_from_json(logged[0].verb) == STAND
    assert snap is not None and (snap.state, snap.decisions) == (row.state, 1)
    clock.tick(10)
    saves.advance(account, info.save_id)
    with engine.connect() as conn:
        assert len(conn.execute(select(save_snapshots)).all()) == 1   # an advance writes no snapshot


def test_the_lines_a_step_brings_are_stored_after_the_last(saves: PgSaves, engine: Engine, account: int,
                                                          clock: FakeClock):
    info, first = saves.create(account)
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(100)
    played = saves.advance(account, info.save_id)
    assert [ln.key for ln in played.lines] == ["l_up_1"] and played.lines[0].time == 3
    assert lines(engine, info.save_id) == [(0, str(k)) for k in (ln.key for ln in first.lines)] + [(3, "l_up_1")]


def test_a_decision_after_another_pages_is_stale_and_the_save_advances_instead(saves: PgSaves, engine: Engine,
                                                                              account: int, clock: FakeClock,
                                                                              rs: Ruleset):
    info, _ = saves.create(account)
    first = saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(100)
    with pytest.raises(Stale) as stale:
        saves.decide(account, info.save_id, STAND, after=0)
    played = stale.value.played
    assert played.decisions == 1 and played.save.time == 100 and [ln.key for ln in played.lines] == ["l_up_1"]
    row = stored(engine, info.save_id)
    assert row.decisions == 1 and row.game_time == 100   # written as an advance
    assert played.save == e.advance(first.save, rs.rules, 100)   # not tapped again
    with engine.connect() as conn:
        assert len(rows.decisions_after(conn, info.save_id, 0)) == 1


def test_advances_never_make_a_decision_stale(saves: PgSaves, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    clock.tick(1)
    saves.advance(account, info.save_id)   # the other tab
    clock.tick(1)
    assert saves.decide(account, info.save_id, STAND, after=0).decisions == 1


def test_an_invalid_decision_writes_nothing(saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    before = stored(engine, info.save_id)
    clock.tick(50)
    with pytest.raises(Invalid):
        saves.decide(account, info.save_id, LOCKED, after=0)
    assert stored(engine, info.save_id) == before


def test_another_accounts_save_or_a_deleted_one_is_not_found(saves: PgSaves, engine: Engine, account: int,
                                                            clock: FakeClock):
    info, _ = saves.create(account)
    other = saves.create(account)[0].save_id
    with engine.begin() as conn:
        stranger = accounts.create_account(conn, clock())
        conn.execute(update(saves_table).where(saves_table.c.id == other).values(deleted_at=clock()))
    for call in (lambda: saves.advance(stranger, info.save_id), lambda: saves.open(stranger, info.save_id),
                 lambda: saves.decide(stranger, info.save_id, STAND, 0), lambda: saves.dry_run(stranger, info.save_id, ()),
                 lambda: saves.stored(stranger, info.save_id),
                 lambda: saves.advance(account, other),
                 lambda: saves.advance(account, info.save_id + 999)):
        with pytest.raises(NotFound):
            call()
    assert [i.save_id for i in saves.list(account)] == [info.save_id] and saves.list(stranger) == []


def test_open_returns_what_was_seen_the_last_lines_and_the_time_away(saves: PgSaves, engine: Engine, account: int,
                                                                    clock: FakeClock, rs: Ruleset):
    info, _ = saves.create(account)
    with engine.begin() as conn:
        rows.append_lines(conn, info.save_id, [(0, f"k{i}") for i in range(250)])
    saves.decide(account, info.save_id, STAND, after=0)
    was = stored(engine, info.save_id)
    clock.tick(3600)
    opened = saves.open(account, info.save_id)
    assert opened.was == e.decode(was.state, rs.rules) and opened.was.time == 0
    assert len(opened.history) == 200 and opened.history[-1].key == "k249" and opened.history[0].n == 50 + len(rs.start_lines)
    assert opened.played.save.time == 3600 and [ln.key for ln in opened.played.lines][0] == "l_up_1"
    assert (opened.info.decisions, opened.info.game_time) == (1, 3600)
    assert stored(engine, info.save_id).game_time == 3600   # open writes like an advance


def test_open_serves_renamed_text_keys_under_their_new_names(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                            account: int):
    from dataclasses import replace
    saves = PgSaves(engine, replace(rs, line_renames={"k_old": "k_new"}), clock)
    info, _ = saves.create(account)
    with engine.begin() as conn:
        rows.append_lines(conn, info.save_id, [(0, "k_old"), (0, "k_other")])
    assert [p.key for p in saves.open(account, info.save_id).history][-2:] == ["k_new", "k_other"]


def test_a_dry_run_shows_the_decisions_and_writes_nothing(saves: PgSaves, engine: Engine, account: int,
                                                          clock: FakeClock):
    info, _ = saves.create(account)
    clock.tick(5)
    before = stored(engine, info.save_id)
    after = saves.dry_run(account, info.save_id, (STAND,))
    assert after.time == 5 and next(ln for ln in after.lanes if ln.lane == e.HANDS).card == "stand_up"
    assert saves.dry_run(account, info.save_id, ()).time == 5
    with pytest.raises(Invalid):
        saves.dry_run(account, info.save_id, (STAND, STAND))   # the lane is busy after the first
    assert stored(engine, info.save_id) == before


def test_stored_is_the_save_as_written_and_counts_and_writes_nothing(saves: PgSaves, engine: Engine, account: int,
                                                                    clock: FakeClock, rs: Ruleset):
    info, _ = saves.create(account)
    saves.decide(account, info.save_id, STAND, after=0)
    clock.tick(3600)
    before, log = stored(engine, info.save_id), lines(engine, info.save_id)
    seen = saves.stored(account, info.save_id)
    assert seen == e.decode(before.state, rs.rules) and seen.time == 0   # not advanced to the hour away
    assert stored(engine, info.save_id) == before and lines(engine, info.save_id) == log


def test_two_decisions_at_once_on_one_save_run_one_after_the_other(saves: PgSaves, engine: Engine, account: int,
                                                                   clock: FakeClock):
    """Two pages deciding with the same `after`, at the same moment: one is applied and the other is stale."""
    info, _ = saves.create(account)
    clock.tick(1)
    got: list[str] = []

    def decide() -> None:
        try:
            saves.decide(account, info.save_id, STAND, after=0)
            got.append("ok")
        except Stale:
            got.append("stale")

    threads = [threading.Thread(target=decide) for _ in range(4)]
    for th in threads:
        th.start()
    for th in threads:
        th.join(10)
    assert sorted(got) == ["ok", "stale", "stale", "stale"]
    with engine.connect() as conn:
        assert len(conn.execute(select(save_decisions)).all()) == 1


def test_each_write_logs_ids_and_counts(saves: PgSaves, account: int, clock: FakeClock,
                                        capsys: pytest.CaptureFixture[str]):
    logs.setup()
    info, _ = saves.create(account)
    saves.decide(account, info.save_id, STAND, after=0)
    with pytest.raises(Stale):
        saves.decide(account, info.save_id, STAND, after=0)
    with pytest.raises(Invalid):
        saves.decide(account, info.save_id, LOCKED, after=1)
    clock.tick(100)
    saves.advance(account, info.save_id)
    saves.open(account, info.save_id)
    out = capsys.readouterr().out
    s = info.save_id
    assert f"event=save.created account={account} save={s}" in out
    assert f"event=save.decision account={account} save={s} kind=tap_card target=stand_up n=1 game_at=0 result=ok" in out
    assert "result=stale" in out and "kind=tap_card target=build_fireback n=1 game_at=0 result=invalid" in out
    assert f"event=save.advanced account={account} save={s} game_at=100 lines=1" in out
    assert f"event=save.opened account={account} save={s} game_at=100" in out and "away_s=" in out
