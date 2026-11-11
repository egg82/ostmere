"""A save across rules and builds: rebased forward at load and written under the new rules; one a later build wrote, or
one that cannot be rebased, is unavailable and nothing is written; the start check counts each kind."""
from dataclasses import replace

import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app import logs
from ashfall_app.db import saves as rows
from ashfall_app.saves.check import check
from ashfall_app.saves.interface import Ruleset, Unavailable
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))


def stored(engine: Engine, save_id: int) -> rows.SaveRecord:
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None
    return row


def test_a_save_an_older_build_wrote_is_rebased_forward_and_written_under_the_new_rules(
        engine: Engine, account: int, clock: FakeClock, rs: Ruleset, rs_changed: Ruleset,
        capsys: pytest.CaptureFixture[str]):
    logs.setup()
    info, _ = PgSaves(engine, rs, clock).create(account)
    clock.tick(10)
    played = PgSaves(engine, rs_changed, clock).decide(account, info.save_id, STAND, after=0)
    row = stored(engine, info.save_id)
    assert (row.rules_digest, row.build, row.release, row.decisions) == (rs_changed.digest, "b3", 3, 1)
    assert e.decode(row.state, rs_changed.rules) == played.save
    first = played.lines[0]   # the new trigger's line lands at the save's own time, before the step's
    assert (first.time, first.seq) == (0, 0) and len({(ln.time, ln.seq) for ln in played.lines}) == len(played.lines)
    out = capsys.readouterr().out
    assert f"event=save.rebased save={info.save_id} from={rs.digest[:12]} to={rs_changed.digest[:12]}" in out
    assert "rebased=true" in out


def test_a_save_a_later_build_wrote_is_unavailable_to_an_older_pod(engine: Engine, account: int, clock: FakeClock,
                                                                   rs: Ruleset, rs_changed: Ruleset,
                                                                   capsys: pytest.CaptureFixture[str]):
    logs.setup()
    newer = PgSaves(engine, rs_changed, clock)
    info, _ = newer.create(account)
    before = stored(engine, info.save_id)
    older = PgSaves(engine, rs, clock)
    clock.tick(5)
    for call in (lambda: older.advance(account, info.save_id), lambda: older.decide(account, info.save_id, STAND, 0),
                 lambda: older.open(account, info.save_id), lambda: older.dry_run(account, info.save_id, ())):
        with pytest.raises(Unavailable):
            call()
    assert stored(engine, info.save_id) == before
    assert f"event=save.newer save={info.save_id} build=b3 release=3" in capsys.readouterr().out
    assert newer.advance(account, info.save_id).save.time == 5   # the newer pod carries on


def test_a_save_under_the_pods_own_rules_is_read_whoever_wrote_it(engine: Engine, account: int, clock: FakeClock,
                                                                  rs: Ruleset):
    """Exactly this pod's rules: decoded, never rebased, so a later build's write of the same rules is no bar."""
    later = replace(rs, build="b9", release=9)
    info, _ = PgSaves(engine, later, clock).create(account)
    clock.tick(1)
    assert PgSaves(engine, rs, clock).advance(account, info.save_id).save.time == 1
    assert stored(engine, info.save_id).build == "b2"


def test_a_save_that_cannot_be_rebased_is_unavailable_and_logged(engine: Engine, account: int, clock: FakeClock,
                                                                 rs: Ruleset, rs_changed: Ruleset,
                                                                 capsys: pytest.CaptureFixture[str]):
    """Written under rules with a card these rules lack (no rename maps it), by an earlier build."""
    logs.setup()
    info, _ = PgSaves(engine, replace(rs_changed, release=1), clock).create(account)
    before = stored(engine, info.save_id)
    with pytest.raises(Unavailable):
        PgSaves(engine, rs, clock).advance(account, info.save_id)
    assert stored(engine, info.save_id) == before
    out = capsys.readouterr().out
    assert f"event=save.rebase_failed save={info.save_id} kind=" in out and "level=error" in out


def test_the_start_check_counts_every_kind_of_save(engine: Engine, account: int, clock: FakeClock, rs: Ruleset,
                                                   rs_changed: Ruleset, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    PgSaves(engine, rs, clock).create(account)                                  # exact
    PgSaves(engine, replace(rs, release=1, digest="0" * 64), clock).create(account)   # a stale digest: rebases
    PgSaves(engine, rs_changed, clock).create(account)                          # a later build's
    PgSaves(engine, replace(rs_changed, release=1), clock).create(account)   # cannot rebase
    done = check(engine, rs)
    assert (done.total, done.ok, done.failed, done.newer) == (4, 2, 1, 1)
    assert "event=saves.check total=4 ok=2 failed=1 newer=1" in capsys.readouterr().out
    clean = check(engine, rs_changed)
    assert (clean.total, clean.ok, clean.failed, clean.newer) == (4, 4, 0, 0)


def test_a_save_another_build_of_the_same_time_wrote_under_other_rules_is_rebased(
        engine: Engine, account: int, clock: FakeClock, rs: Ruleset):
    """Two builds of one commit time: neither is later, so the save is rebased, not refused."""
    info, _ = PgSaves(engine, replace(rs, build="b2x", digest="0" * 64), clock).create(account)
    assert PgSaves(engine, rs, clock).advance(account, info.save_id).decisions == 0
    assert stored(engine, info.save_id).rules_digest == rs.digest
