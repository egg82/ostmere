"""Per-test time gate, a plugin tests/conftest.py registers at configure time: any test whose setup + call + teardown
takes more than CEILING_S of wall clock fails, so a slow test fails CI the day it appears (docs/engineering.md, "Fast
from the start"). It applies to every collected test, present and future, except those marked `playthrough`: a whole-game simulation is
budgeted by its CI job's timeout.

Wall clock, and all three phases, because that is what a person waits on. A wait (a sleep, a production timeout, a
closed port) counts like work: give the code an injected clock or a tiny timeout, or a fake that fails at once
(tests/fake_clock.py).

A shared fixture (class, module, package or session scope) is timed on its own against FIXTURE_CEILING_S, by name, and
its setup is taken out of the test's charge: which test meets it first changes with ordering and sharding, so charging
it there would make the gate's verdict land on a different test from run to run. Its teardown still lands on the last
test that used it, so shared teardowns stay cheap. A fixture set up for a playthrough test is the play itself, and is
not timed. After a shared fixture is built, the heap is frozen out of the cyclic collector (`freeze_caches`), so the
next full collection does not walk that cache and charge it to whichever test is running.

CEILING_S is 4 s, FIXTURE_CEILING_S 10 s. Measured on CI (run 43347069455, both `tests` shards, `--durations-min=1`,
setup and call summed per test): the slowest test's own cost is 3.01 s, db/test_failover's silent-host wait on libpq's
connect timeout, cut to a one-second smoke test; every other phase over 1 s is a shared fixture's setup (the household
names scan at 2.17 s, session fixtures at 1.0-1.4 s). 4 s leaves headroom for a slower runner and sits under pytest.ini's
`timeout = 6`, which stays: that is the hang guard (a thread dump and the worker killed), this is the budget (an
ordinary failure naming the test), so a slow test meets this one first. 10 s is over four times the slowest shared
fixture measured. Raise neither: speed the test or fixture up, or split it. HELD and HELD_FIXTURES start empty and may
only shrink. A deliberately slow run (the nightly deep run, tools/silent_vanish.sh) sets TEST_CEILING_S, and with it
the fixture ceiling unless FIXTURE_CEILING_S is set too."""
import gc
import os
import time
from collections.abc import Generator

import pytest
from pluggy import Result

CEILING_S = float(os.environ.get("TEST_CEILING_S", "4.0"))
FIXTURE_CEILING_S = float(os.environ.get("FIXTURE_CEILING_S", str(max(10.0, CEILING_S))))
HELD: frozenset[str] = frozenset()
HELD_FIXTURES: frozenset[str] = frozenset()
SPENT_KEY = pytest.StashKey[float]()
SHARED_KEY = pytest.StashKey[float]()


class Shared:
    """The test being set up, and the seconds spent setting up shared fixtures, outermost only, so a shared fixture
    that requests another is not subtracted twice."""

    item: pytest.Item | None = None
    depth = 0
    total = 0.0


def too_slow(nodeid: str, wall_s: float) -> bool:
    return wall_s > CEILING_S and nodeid not in HELD


def fixture_too_slow(name: str, wall_s: float) -> bool:
    return wall_s > FIXTURE_CEILING_S and name not in HELD_FIXTURES


def timed(item: pytest.Item | None) -> bool:
    """Every test but a whole-game simulation (the `playthrough` marker), which its CI job's timeout budgets."""
    return item is None or item.get_closest_marker("playthrough") is None


def charge(item: pytest.Item, seconds: float) -> float:
    """Adds one phase's wall seconds to the test's total; the total so far."""
    total = item.stash.get(SPENT_KEY, 0.0) + seconds
    item.stash[SPENT_KEY] = total
    return total


def freeze_caches() -> None:
    """Park everything alive out of the collector's reach, after collecting the garbage. A cache a shared fixture just
    built would otherwise sit in the young-to-old heap, and the next full pass would walk it (about 1.2 s)."""
    gc.collect()
    gc.freeze()


def pytest_collection_finish(session: pytest.Session) -> None:
    """Park what collection built out of the cyclic collector's reach, so a test's collections cost what its own
    objects cost, not the whole suite's heap."""
    freeze_caches()


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef: pytest.FixtureDef[object]) -> Generator[None, None, None]:
    if fixturedef.scope == "function":
        yield
        return
    Shared.depth += 1
    start = time.perf_counter()
    try:
        yield
        freeze_caches()
    finally:
        spent = time.perf_counter() - start
        Shared.depth -= 1
        if Shared.depth == 0:
            Shared.total += spent
    if timed(Shared.item) and fixture_too_slow(fixturedef.argname, spent):
        pytest.fail(f"fixture {fixturedef.argname} ({fixturedef.scope} scope) took {spent:.2f}s to set up, over the "
                    f"{FIXTURE_CEILING_S}s shared-fixture ceiling (tests/time_gate.py): make it cheaper", pytrace=False)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item: pytest.Item) -> Generator[None, None, None]:
    Shared.item, before = item, Shared.total
    try:
        yield
    finally:
        item.stash[SHARED_KEY] = Shared.total - before
        Shared.item = None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, Result[pytest.TestReport], None]:
    outcome = yield
    report = outcome.get_result()
    own = call.duration - (item.stash.get(SHARED_KEY, 0.0) if call.when == "setup" else 0.0)
    spent = charge(item, own)
    if report.when == "teardown" and report.passed and timed(item) and too_slow(item.nodeid, spent):
        report.outcome = "failed"
        report.longrepr = (f"{item.nodeid} took {spent:.2f}s of wall clock with its setup and teardown (shared "
                           f"fixtures timed on their own), over the {CEILING_S}s per-test ceiling (tests/time_gate.py): "
                           f"speed it up or split it")
