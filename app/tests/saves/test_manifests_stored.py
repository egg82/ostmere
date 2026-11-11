"""Manifests stored once per rules digest (db/manifests.py, saves/manifest.py). This build writes every save whole, so
the build before it reads them; it reads a row stripped of its manifest with its digest's, under its own rules and
across a rebase, golden texts of the oldest format a rebase reads included; a stripped row whose digest has none held
is unavailable and fails the start check, never decoded wrong."""
import json
from dataclasses import replace
from pathlib import Path

import pytest
from sqlalchemy import Engine, insert, select, update

from ashfall_app import engine as e
from ashfall_app import logs
from ashfall_app.db import saves as rows
from ashfall_app.db.manifests import stripped
from ashfall_app.db.tables import save_manifests, save_snapshots, saves
from ashfall_app.saves.check import check
from ashfall_app.saves.interface import Ruleset, Unavailable
from ashfall_app.saves.load import load
from ashfall_app.saves.manifest import register
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock

STAND = e.TapCard(e.CardId("stand_up"))
GOLDEN = Path(__file__).resolve().parent / "golden"


def column(engine: Engine, save_id: int) -> str:
    with engine.connect() as conn:
        return str(conn.execute(select(saves.c.state).where(saves.c.id == save_id)).scalar_one())


def strip(engine: Engine, save_id: int) -> str:
    """Strips the save's stored text of its manifest; the whole text it held."""
    text = column(engine, save_id)
    with engine.begin() as conn:
        conn.execute(update(saves).where(saves.c.id == save_id).values(state=stripped(text)[0]))
    return text


def record(engine: Engine, save_id: int) -> rows.SaveRecord:
    with engine.connect() as conn:
        found = rows.save(conn, save_id, None)
    assert found is not None
    return found


def test_a_save_is_written_whole_as_the_engine_encodes_it(saves: PgSaves, engine: Engine, account: int,
                                                         clock: FakeClock, rs: Ruleset):
    info, _ = saves.create(account)
    clock.tick(10)
    played = saves.decide(account, info.save_id, STAND, after=0)
    assert column(engine, info.save_id) == e.encode(played.save, rs.rules)


def test_register_stores_the_builds_manifest_once_and_reports_one_that_differs(
        engine: Engine, rs: Ruleset, rs_changed: Ruleset, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    assert register(engine, rs) and register(engine, rs)
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest=rs_changed.digest, manifest="{}"))
    assert not register(engine, rs_changed)
    with engine.connect() as conn:
        held = dict(conn.execute(select(save_manifests.c.rules_digest, save_manifests.c.manifest)).tuples().all())
    assert held == {rs.digest: stripped(e.encode(e.new_save(rs.rules), rs.rules))[1], rs_changed.digest: "{}"}
    out = capsys.readouterr().out
    assert f"level=info logger=ashfall.saves event=saves.manifest rules={rs.digest[:12]} agrees=true" in out
    assert f"level=error logger=ashfall.saves event=saves.manifest rules={rs_changed.digest[:12]} agrees=false" in out


def test_a_stripped_save_under_the_pods_rules_is_read_whole(saves: PgSaves, engine: Engine, account: int,
                                                           clock: FakeClock, rs: Ruleset):
    register(engine, rs)
    info, _ = saves.create(account)
    text = strip(engine, info.save_id)
    assert record(engine, info.save_id).state == text
    clock.tick(4)
    assert saves.advance(account, info.save_id).save.time == 4
    assert column(engine, info.save_id).startswith('{"format":%d,"manifest":' % e.FORMAT)


def test_a_stripped_save_under_older_rules_rebases_as_the_whole_one_does(
        engine: Engine, account: int, clock: FakeClock, rs: Ruleset, rs_changed: Ruleset):
    register(engine, rs)
    older = PgSaves(engine, rs, clock)
    kept, bare = older.create(account)[0].save_id, older.create(account)[0].save_id
    strip(engine, bare)
    clock.tick(10)
    newer = PgSaves(engine, rs_changed, clock)
    assert newer.decide(account, bare, STAND, after=0).save == newer.decide(account, kept, STAND, after=0).save


def test_an_oldest_format_golden_text_stored_stripped_rebases_as_the_whole_text(engine: Engine, account: int,
                                                                               clock: FakeClock, rs: Ruleset):
    text = sorted((GOLDEN / f"f{e.OLDEST_FORMAT}").glob("*.json"))[-1].read_text().strip()
    envelope = json.loads(text)
    assert envelope["format"] == e.OLDEST_FORMAT
    bare, manifest = stripped(text)
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest=envelope["rules"], manifest=manifest))
        written = rows.Written(state=bare, format=e.OLDEST_FORMAT, rules_digest=envelope["rules"], decisions=0,
                               game_time=envelope["save"]["time"], ended_at=None, build="old", release=1, camp_level=0)
        save_id = rows.insert_save(conn, account, clock(), written)
    row = record(engine, save_id)
    assert row.state == text
    assert load(row, rs).save == e.rebase(text, rs.rules, rs.renames)


def test_a_stripped_save_with_no_manifest_held_is_unavailable_and_fails_the_check(
        engine: Engine, account: int, clock: FakeClock, rs: Ruleset, rs_changed: Ruleset):
    info, _ = PgSaves(engine, replace(rs, release=1), clock).create(account)
    strip(engine, info.save_id)
    before = column(engine, info.save_id)
    with pytest.raises(Unavailable):
        PgSaves(engine, rs_changed, clock).advance(account, info.save_id)
    assert column(engine, info.save_id) == before
    assert check(engine, rs_changed).failed == 1
    register(engine, rs)
    assert check(engine, rs_changed).failed == 0   # control: with its manifest held it rebases


def test_a_stripped_snapshot_is_read_whole(saves: PgSaves, engine: Engine, account: int, clock: FakeClock,
                                           rs: Ruleset):
    register(engine, rs)
    info, _ = saves.create(account)
    clock.tick(5)
    saves.decide(account, info.save_id, STAND, after=0)
    with engine.begin() as conn:
        day, text = conn.execute(select(save_snapshots.c.day, save_snapshots.c.state)).one()
        conn.execute(update(save_snapshots).values(state=stripped(text)[0]))
        snap = rows.snapshot(conn, info.save_id, day)
    assert snap is not None and snap.state == text


def test_only_a_stripped_text_reads_the_held_manifest(engine: Engine, account: int, clock: FakeClock):
    """The SQL test of a stripped text agrees with the text's own at a two-digit format."""
    with engine.begin() as conn:
        conn.execute(insert(save_manifests).values(rules_digest="d", manifest='{"held":1}'))
        ids = [rows.insert_save(conn, account, clock(), rows.Written(
            state=state, format=10, rules_digest="d", decisions=0, game_time=0, ended_at=None, build="b", release=1,
            camp_level=0)) for state in ('{"format":10,"rules":"d","save":{}}',
                                         '{"format":10,"manifest":{"own":1},"rules":"d","save":{}}')]
    assert [record(engine, i).state for i in ids] == ['{"format":10,"manifest":{"held":1},"rules":"d","save":{}}',
                                                      '{"format":10,"manifest":{"own":1},"rules":"d","save":{}}']
