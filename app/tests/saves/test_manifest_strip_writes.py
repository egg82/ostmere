"""Saves written without their manifest (saves/write.py `written`, saves/manifest.py `registered`): a pod whose start
stored its manifest writes save and snapshot rows stripped of it, one whose start found another manifest held writes
them whole, and a restore stores the manifest before it writes. Every row written stripped reads whole again through
the read path the build before this one shipped with (db/saves.py), and rebases under later rules."""
from pathlib import Path

from sqlalchemy import Engine, insert, select

from ashfall_app import engine as e
from ashfall_app.db import saves as rows
from ashfall_app.db.manifests import stripped
from ashfall_app.db.tables import save_manifests, save_snapshots, saves
from ashfall_app.saves.check import check
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.manifest import registered
from ashfall_app.saves.service import PgSaves
from ashfall_app.saves.support import restore
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))


def stored(engine: Engine) -> list[str]:
    """Every save's and snapshot's state column, as stored."""
    with engine.connect() as conn:
        return [*conn.execute(select(saves.c.state).order_by(saves.c.id)).scalars(),
                *conn.execute(select(save_snapshots.c.state)).scalars()]


def carries_manifest(state: str) -> bool:
    return '"manifest":' in state


def played(engine: Engine, rs: Ruleset, clock: FakeClock, account: int) -> tuple[int, e.Save]:
    """A save begun and decided once (which takes the day's snapshot) by a pod under `rs`: its id and save."""
    pod = PgSaves(engine, rs, clock)
    info, _ = pod.create(account)
    clock.tick(5)
    return info.save_id, pod.decide(account, info.save_id, STAND, after=0).save


def test_a_registered_pod_writes_its_saves_and_snapshots_without_the_manifest(engine: Engine, rs: Ruleset,
                                                                             clock: FakeClock, account: int):
    mine = registered(engine, rs)
    assert mine.held_manifest is not None
    save_id, save = played(engine, mine, clock, account)
    states = stored(engine)
    assert len(states) == 2 and not any(carries_manifest(s) for s in states)
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None and row.state == e.encode(save, rs.rules)
    assert stripped(row.state) == (states[0], mine.held_manifest)


def test_a_pod_whose_digest_holds_another_manifest_writes_whole(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                               account: int):
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest=rs.digest, manifest="{}"))
    mine = registered(engine, rs)
    assert mine.held_manifest is None
    played(engine, mine, clock, account)
    states = stored(engine)
    assert len(states) == 2 and all(carries_manifest(s) for s in states)


def test_rows_written_stripped_read_whole_by_a_pod_writing_whole_and_rebase_under_later_rules(
        engine: Engine, rs: Ruleset, rs_changed: Ruleset, clock: FakeClock, account: int):
    save_id, save = played(engine, registered(engine, rs), clock, account)
    assert not any(carries_manifest(s) for s in stored(engine))   # control: the rows are stripped
    assert check(engine, rs_changed).failed == 0
    old = PgSaves(engine, rs, clock)   # a pod that writes whole and reads through db/saves.py, as the build before
    clock.tick(3)
    assert old.advance(account, save_id).save == e.advance(save, rs.rules, save.time + 3)
    assert carries_manifest(stored(engine)[0])   # it wrote the row back whole


def test_a_restore_stores_the_manifest_before_it_writes_the_row_without_it(engine: Engine, rs: Ruleset,
                                                                           clock: FakeClock, account: int,
                                                                           tmp_path: Path):
    save_id, _ = played(engine, rs, clock, account)
    with engine.connect() as conn:
        day = int(conn.execute(select(save_snapshots.c.day)).scalar_one())
        assert conn.execute(select(save_manifests.c.rules_digest)).all() == []
    assert restore(engine, rs, clock, save_id, day, None, tmp_path / "row.json") == 1
    with engine.connect() as conn:
        assert conn.execute(select(save_manifests.c.rules_digest)).scalars().all() == [rs.digest]
        row = rows.save(conn, save_id, None)
    assert not carries_manifest(stored(engine)[0])
    assert row is not None and carries_manifest(row.state)
