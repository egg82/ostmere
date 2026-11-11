"""Per-test time gate: any test whose call phase uses more than CEILING_S of CPU fails, so a slow test fails CI the
day it appears (docs/engineering.md, "Fast from the start"). It applies to every collected test, present and future.

CPU seconds (this process and its children, os.times()), not wall seconds: wall time measures the runner as much as the
test, so a slower CPU type or a busy runner failed fast tests. A test that waits (a sleep, the database) uses little CPU
and passes; wait-bound slowness belongs to a timeout. A lazily built @cache charges its whole cost to the first test that
fills it, so build shared data in a fixture (setup is not timed). The ceiling is 2 s; raise it never, speed the test up
or split it. HELD (like test_function_size's) starts empty and may only shrink.
Caches built by session- and module-scoped fixtures are frozen out of the collector (`freeze_caches`), so no full
collection that walks them is charged to a test's call.

`create_app()` loads and checks every shipped chapter (~0.2 s of CPU, ~4x on the slow CI node), so a session builds
that once (`shipped_opening`, in setup) and every test's `create_app()` reuses it; a test that wants other content still
patches `main.checked_opening` itself.
Likewise the Ruleset and Game for that content (`shipped_ruleset`, tests/shipped_ruleset.py): a test under another
lock, renames or opening gets its own.

Also the Postgres fixtures: `pg_url` (a database of the test's own, migrated) and `pg_empty` (tests/pg.py), and
`game`: the app on such a database (tests/game_client.py).

A test that leaves a connection pool open fails at teardown (`closes_its_pools`): its worker threads would outlive it."""
import gc
import os
import re
import threading
from collections.abc import Generator, Iterator

import pytest
from pluggy import Result

from ashfall_app import main
from ashfall_app.opening.schema import Opening
from tests import pg
from tests.game_client import GameClient, game_client
from tests.shipped_ruleset import ShippedRuleset

# Pushes keep the 2 s ceiling; the nightly deep run (`tests-deep` in .github/workflows/nightly.yml) is meant to be slow and sets its own.
CEILING_S = float(os.environ.get("TEST_CEILING_S", "2.0"))
HELD: frozenset[str] = frozenset()
CPU_KEY = pytest.StashKey[float]()


def pytest_collection_finish(session: pytest.Session) -> None:
    """Park what collection built out of the cyclic collector's reach, so a test's collections cost what its own
    objects cost, not the whole suite's heap (the per-test ceiling measures the test, not its position)."""
    freeze_caches()


def freeze_caches() -> None:
    """Park everything alive out of the collector's reach, after collecting the garbage. A cache a session- or
    module-scoped fixture just built would otherwise sit in the young-to-old heap, and the next full pass would walk it
    (about 1.2 s, charged to whichever test is running)."""
    gc.collect()
    gc.freeze()


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef: pytest.FixtureDef[object]) -> Generator[None, None, None]:
    yield
    if fixturedef.scope in ("session", "package", "module"):
        freeze_caches()


def cpu_now() -> float:
    t = os.times()
    return t.user + t.system + t.children_user + t.children_system


def too_slow(nodeid: str, cpu_s: float) -> bool:
    return cpu_s > CEILING_S and nodeid not in HELD


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, None, None]:
    start = cpu_now()
    yield
    item.stash[CPU_KEY] = cpu_now() - start


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, Result[pytest.TestReport], None]:
    outcome = yield
    report = outcome.get_result()
    cpu_s = item.stash.get(CPU_KEY, None)
    if report.when == "call" and report.passed and cpu_s is not None and too_slow(item.nodeid, cpu_s):
        report.outcome = "failed"
        report.longrepr = f"{item.nodeid} used {cpu_s:.2f}s of CPU, over the {CEILING_S}s per-test ceiling (tests/conftest.py)"


@pytest.fixture(scope="session")
def shipped_opening() -> Opening:
    """The shipped content, loaded and release-lock checked once per session (setup is not timed)."""
    return main.checked_opening()


@pytest.fixture(scope="session")
def townsfolk_opening(shipped_opening: Opening) -> Opening:
    """The townsfolk test chapter's content on the session's shipped opening, built once in setup (not timed):
    tests/opening/test_townsfolk_loader.py's `loaded` is cached and its `shipped` reads `checked_opening`, so a module
    using them requests this."""
    from tests.opening.test_townsfolk_loader import loaded
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(main, "checked_opening", lambda: shipped_opening)
        return loaded()


@pytest.fixture(scope="session")
def shipped_ruleset(shipped_opening: Opening) -> ShippedRuleset:
    """The shipped opening's Ruleset and Game, built once per session (setup is not timed)."""
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
