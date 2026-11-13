"""The strip backfill (saves/strip.py): whole save and snapshot rows are written without their manifest and read whole
again; a row already stripped is left alone; a row whose digest holds another manifest, or whose envelope names
another digest, stays whole; a row a player's write changed after it was read keeps that write; a dry run writes
nothing; and the manifests no row names are pruned, this build's kept."""
import time
from concurrent.futures import Future, ThreadPoolExecutor

import pytest
from sqlalchemy import Engine, insert, select, text, update

from ashfall_app import engine as e
from ashfall_app import logs
from ashfall_app.db import saves as rows
from ashfall_app.db.manifests import stripped
from ashfall_app.db.tables import save_manifests, save_snapshots, saves
from ashfall_app.saves import __main__ as cli
from ashfall_app.saves.__main__ import main
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.service import PgSaves
from ashfall_app.saves.strip import Stripped, strip
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))


def made(engine: Engine, rs: Ruleset, clock: FakeClock, account: int, n: int) -> list[int]:
    """`n` saves written whole, each decided once (so each has a day's snapshot)."""
    pod = PgSaves(engine, rs, clock)
    ids = [pod.create(account)[0].save_id for _ in range(n)]
    clock.tick(5)
    for i in ids:
        pod.decide(account, i, STAND, after=0)
    return ids


def columns(engine: Engine) -> list[str]:
    with engine.connect() as conn:
        return [*conn.execute(select(saves.c.state).order_by(saves.c.id)).scalars(),
                *conn.execute(select(save_snapshots.c.state).order_by(save_snapshots.c.save_id)).scalars()]


def read(engine: Engine, ids: list[int]) -> list[str]:
    """The states the read path gives, saves then snapshots."""
    with engine.connect() as conn:
        found = [r.state for r in (rows.save(conn, i, None) for i in ids) if r is not None]
        days = conn.execute(select(save_snapshots.c.save_id, save_snapshots.c.day).order_by(save_snapshots.c.save_id))
        found += [s.state for s in (rows.snapshot(conn, i, d) for i, d in days.tuples()) if s is not None]
    return found


def held(engine: Engine) -> dict[str, str]:
    with engine.connect() as conn:
        return dict(conn.execute(select(save_manifests.c.rules_digest, save_manifests.c.manifest)).tuples().all())


def whole_count(states: list[str]) -> int:
    return sum('"manifest":' in s for s in states)


def test_whole_rows_are_stripped_in_batches_and_read_whole_again(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                                 account: int, capsys: pytest.CaptureFixture[str]):
    ids = made(engine, rs, clock, account, 3)
    before = columns(engine)
    assert len(before) == 6 and whole_count(before) == 6   # control: three saves and three snapshots, all whole
    logs.setup()
    assert strip(engine, rs, batch=2) == Stripped(stripped=6, whole=0, changed=0, pruned=0)
    after = columns(engine)
    assert whole_count(after) == 0
    assert held(engine) == {rs.digest: stripped(before[0])[1]}
    assert read(engine, ids) == before
    out = capsys.readouterr().out
    assert "event=saves.strip.start dry_run=false" in out
    assert "event=saves.strip.finish dry_run=false stripped=6 whole=0 changed=0 pruned=0 ms=" in out
    assert strip(engine, rs) == Stripped()   # a second run finds nothing left whole
    assert columns(engine) == after


def test_a_dry_run_counts_and_writes_nothing(engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    made(engine, rs, clock, account, 2)
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest="gone", manifest="{}"))
    before, kept = columns(engine), held(engine)
    assert strip(engine, rs, dry_run=True) == Stripped(stripped=4, whole=0, changed=0, pruned=1)
    assert columns(engine) == before and held(engine) == kept


def test_a_row_whose_digest_holds_another_manifest_stays_whole(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                               account: int):
    made(engine, rs, clock, account, 1)
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest=rs.digest, manifest='{"other":1}'))
    before = columns(engine)
    assert strip(engine, rs, dry_run=True) == Stripped(stripped=0, whole=2, changed=0, pruned=0)
    assert strip(engine, rs) == Stripped(stripped=0, whole=2, changed=0, pruned=0)
    assert columns(engine) == before and held(engine) == {rs.digest: '{"other":1}'}


def test_a_row_whose_envelope_names_another_digest_stays_whole(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                               account: int):
    made(engine, rs, clock, account, 1)
    with engine.begin() as conn:
        conn.execute(update(saves).values(rules_digest="elsewhere"))
    assert strip(engine, rs) == Stripped(stripped=1, whole=1, changed=0, pruned=0)
    assert whole_count(columns(engine)[:1]) == 1   # the save; its snapshot names the envelope's digest and is stripped


def test_rows_already_stripped_are_left_and_unnamed_manifests_pruned_but_this_builds(
        engine: Engine, rs: Ruleset, rs_changed: Ruleset, clock: FakeClock, account: int):
    made(engine, rs, clock, account, 1)
    strip(engine, rs)
    stripped_rows = columns(engine)
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest=rs_changed.digest, manifest="{}"))
        conn.execute(insert(save_manifests).values(rules_digest="gone", manifest="{}"))
    assert strip(engine, rs_changed) == Stripped(stripped=0, whole=0, changed=0, pruned=1)
    assert set(held(engine)) == {rs.digest, rs_changed.digest}   # named by the rows, and the running build's
    assert columns(engine) == stripped_rows


def test_a_row_changed_after_it_was_read_keeps_the_change(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                          account: int):
    [save_id] = made(engine, rs, clock, account, 1)
    changed = e.encode(e.advance(e.new_save(rs.rules), rs.rules, 9), rs.rules)
    with ThreadPoolExecutor(1) as pool, engine.connect() as player:
        player.execute(select(saves.c.id).where(saves.c.id == save_id).with_for_update())
        run = pool.submit(strip, engine, rs)
        waiting(engine, run)
        player.execute(update(saves).where(saves.c.id == save_id).values(state=changed))
        player.commit()
        assert run.result(timeout=2) == Stripped(stripped=1, whole=0, changed=1, pruned=0)
    assert columns(engine)[0] == changed


def waiting(engine: Engine, run: Future[Stripped]) -> None:
    """Returns once a session waits on a lock (the backfill's compare-and-set behind the player's row lock); raises
    the backfill's own error if it ended first. Each probe is its own transaction: pg_stat_activity is read once per
    transaction, so a probe repeated inside one never sees a wait that began after its first read."""
    probe = text("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock' AND pid <> pg_backend_pid() "
                 "AND datname = current_database()")
    deadline = time.monotonic() + 2
    with engine.connect() as other:
        while other.execute(probe).scalar_one() == 0:
            other.rollback()
            if run.done():
                pytest.fail(f"the backfill ended without waiting on the player's row: {run.result()}")
            assert time.monotonic() < deadline, "the backfill never waited on the player's row"
            time.sleep(0.01)


def test_the_command_runs_dry_and_for_real(engine: Engine, rs: Ruleset, clock: FakeClock, account: int,
                                           pg_url: str, monkeypatch: pytest.MonkeyPatch,
                                           capsys: pytest.CaptureFixture[str]):
    made(engine, rs, clock, account, 1)
    monkeypatch.setenv("DATABASE_URL", pg_url)
    monkeypatch.setattr(cli, "load_opening", lambda: None)   # the shipped rules are `rs`, already loaded

    def shipped(*_: object) -> Ruleset:
        return rs
    monkeypatch.setattr(cli, "ruleset", shipped)
    assert main(["strip", "--dry-run"]) == 0
    assert whole_count(columns(engine)) == 2
    assert main(["strip"]) == 0
    assert whole_count(columns(engine)) == 0
    out = capsys.readouterr().out
    assert "dry_run=True stripped=2 whole=0 changed=0 pruned=0" in out
    assert "dry_run=False stripped=2 whole=0 changed=0 pruned=0" in out
