"""Two builds live at once, as two processes on one database (HA plan, multi-pod rule): an older build under today's
rules (release 1) and a newer one under a retune (release 2, tests/saves/changes.py, retuned_opening), a numbers-only
change the older build could rebase back from, so only the release order stops it. The newer rebases the older's saves forward
and writes them; after that the older must not write them, and answers unavailable.

The processes share nothing but the database. They start once for the module (two Python starts, in setup); each step
is one request to one of them."""
import json
import os
import subprocess
import sys
from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

import pytest
from sqlalchemy import Engine

from ashfall_app.db import accounts
from ashfall_app.db import saves as rows
from ashfall_app.db.engine import open_database
from tests import pg
from tests.fake_clock import T0

APP = Path(__file__).resolve().parents[2]
WORKER = "tests.saves.two_builds_worker"


class Pod:
    def __init__(self, url: str, rules: str, build: str, release: int) -> None:
        env = {**os.environ, "ASHFALL_TEST_DB": url, "RULES": rules, "BUILD_VERSION": build, "RELEASE": str(release),
               "PYTHONPATH": str(APP)}
        self.proc = subprocess.Popen([sys.executable, "-m", WORKER], cwd=APP, env=env, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, text=True)

    def ready(self) -> str:
        return str(self._read()["ready"])

    def ask(self, op: str, account: int, save: int = 0, after: int = 0, at: int = 0) -> dict[str, object]:
        assert self.proc.stdin is not None
        now = (T0 + timedelta(seconds=at)).isoformat()
        self.proc.stdin.write(json.dumps({"op": op, "account": account, "save": save, "after": after, "now": now}) + "\n")
        self.proc.stdin.flush()
        return self._read()

    def _read(self) -> dict[str, object]:
        assert self.proc.stdout is not None
        found: dict[str, object] = json.loads(self.proc.stdout.readline())
        return found

    def stop(self) -> None:
        if self.proc.stdin is not None:
            self.proc.stdin.close()
        self.proc.wait(10)


@pytest.fixture(scope="module")
def two_builds(pg_admin: str, pg_template: str) -> Iterator[tuple[str, Pod, Pod]]:
    url = pg.create(pg_admin, pg_template)
    older, newer = Pod(url, "today", "old", 1), Pod(url, "retuned", "new", 2)
    try:
        assert (older.ready(), newer.ready()) == ("old", "new")
        yield url, older, newer
    finally:
        older.stop()
        newer.stop()
        pg.drop(url)


@pytest.fixture
def db(two_builds: tuple[str, Pod, Pod]) -> Iterator[Engine]:
    database = open_database(two_builds[0], max_size=1)
    yield database.engine
    database.close()


def row(engine: Engine, save_id: int) -> rows.SaveRecord:
    with engine.connect() as conn:
        found = rows.save(conn, save_id, None)
    assert found is not None
    return found


def test_the_newer_build_writes_and_the_older_then_cannot(two_builds: tuple[str, Pod, Pod], db: Engine):
    _, older, newer = two_builds
    with db.begin() as conn:
        account = accounts.create_account(conn, T0)
    made = older.ask("create", account)
    save = int(str(made["save"]))
    assert older.ask("decide", account, save, after=0, at=1) == {"ok": True, "save": save, "decisions": 1, "time": 1}
    assert row(db, save).build == "old"

    assert newer.ask("advance", account, save, at=20)["ok"] is True   # rebased forward and written
    written = row(db, save)
    assert (written.build, written.release, written.game_time) == ("new", 2, 20)

    for op in ("advance", "decide"):
        assert older.ask(op, account, save, after=1, at=30) == {"ok": False, "error": "Unavailable"}
    assert row(db, save) == written   # the older build wrote nothing

    assert newer.ask("decide", account, save, after=1, at=40)["decisions"] == 2


def test_from_the_newer_builds_first_write_the_older_stops(two_builds: tuple[str, Pod, Pod], db: Engine):
    _, older, newer = two_builds
    with db.begin() as conn:
        account = accounts.create_account(conn, T0)
    save = int(str(older.ask("create", account)["save"]))
    assert older.ask("advance", account, save, at=5)["ok"] is True
    assert newer.ask("decide", account, save, after=0, at=6)["ok"] is True   # the first newer write
    assert older.ask("advance", account, save, at=7) == {"ok": False, "error": "Unavailable"}
