"""The time gate (tests/time_gate.py: every test and shared fixture under a wall-clock ceiling), registered as a plugin,
and the session's shared fixtures.

`create_app()` loads and checks every shipped chapter (~0.2 s, ~4x on the slow CI node), so a session builds that once
(`shipped_opening`) and every test's `create_app()` reuses it; a test that wants other content still patches
`main.checked_opening` itself.
Likewise the Ruleset and Game for that content (`shipped_ruleset`, tests/shipped_ruleset.py): a test under another
lock, renames or opening gets its own.

Also the Postgres fixtures: `pg_url` (a database of the test's own, migrated) and `pg_empty` (tests/pg.py), and
`game`: the app on such a database (tests/game_client.py).

A test that leaves a connection pool open fails at teardown (`closes_its_pools`): its worker threads would outlive it."""
import os
import re
import threading
from collections.abc import Generator, Iterator

import pytest

from ashfall_app import main
from ashfall_app.opening.schema import Opening
from tests import pg
from tests.game_client import GameClient, game_client
from tests.shipped_ruleset import ShippedRuleset
from tests import time_gate


def pytest_configure(config: pytest.Config) -> None:
    """The time gate is a plugin, not this conftest's hooks: a hook here never sees a session fixture's setup (its node
    is the session, above this directory)."""
    config.pluginmanager.register(time_gate, "time_gate")


@pytest.fixture(scope="session")
def shipped_opening() -> Opening:
    """The shipped content, loaded and release-lock checked once per session."""
    return main.checked_opening()


@pytest.fixture(scope="session")
def townsfolk_opening(shipped_opening: Opening) -> Opening:
    """The townsfolk test chapter's content on the session's shipped opening, built once per session:
    tests/opening/test_townsfolk_loader.py's `loaded` is cached and its `shipped` reads `checked_opening`, so a module
    using them requests this."""
    from tests.opening.test_townsfolk_loader import loaded
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(main, "checked_opening", lambda: shipped_opening)
        return loaded()


@pytest.fixture(scope="session")
def shipped_ruleset(shipped_opening: Opening) -> ShippedRuleset:
    """The shipped opening's Ruleset and Game, built once per session."""
    return ShippedRuleset(shipped_opening)


POOL_THREAD = re.compile(r"-(worker-\d+|scheduler)$")   # psycopg_pool names its threads <pool>-worker-N, <pool>-scheduler


def pool_threads() -> set[int]:
    return {t.ident or 0 for t in threading.enumerate() if POOL_THREAD.search(t.name)}


@pytest.fixture(autouse=True)
def closes_its_pools() -> Iterator[None]:
    """Fails a test whose fixtures or body left a psycopg pool open: Database.close(), not engine.dispose()."""
    before = pool_threads()
    yield
    left = pool_threads() - before
    assert not left, f"{len(left)} connection pool threads outlived the test: close its Database"


@pytest.fixture(autouse=True)
def app_reuses_the_shipped_opening(shipped_opening: Opening, shipped_ruleset: ShippedRuleset,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "checked_opening", lambda: shipped_opening)
    monkeypatch.setattr(main, "ruleset", shipped_ruleset.ruleset)
    monkeypatch.setattr(main, "Game", shipped_ruleset.make_game)


@pytest.fixture(scope="session")
def pg_admin() -> str:
    """The test server's maintenance database (tests/pg.py). CI always sets it; locally a run without it skips."""
    url = os.environ.get("ASHFALL_TEST_PG", "")
    if not url:
        if os.environ.get("CI"):
            pytest.fail("ASHFALL_TEST_PG is not set: the job's postgres service is missing")
        pytest.skip("ASHFALL_TEST_PG is not set (a Postgres to test against)")
    return url


@pytest.fixture(scope="session")
def pg_template(pg_admin: str) -> str:
    return pg.template(pg_admin)


@pytest.fixture
def pg_url(pg_admin: str, pg_template: str) -> Generator[str, None, None]:
    """A database of this test's own, migrated to head."""
    url = pg.create(pg_admin, pg_template)
    yield url
    pg.drop(url)


@pytest.fixture
def pg_empty(pg_admin: str) -> Generator[str, None, None]:
    """A database of this test's own with nothing in it."""
    url = pg.create(pg_admin)
    yield url
    pg.drop(url)


@pytest.fixture
def game(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[GameClient]:
    """The app on a database of this test's own, signed in by beginning a game (tests/game_client.py)."""
    with game_client(pg_url, monkeypatch) as found:
        yield found
