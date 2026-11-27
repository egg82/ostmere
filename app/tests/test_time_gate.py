"""The per-test time gate (time_gate.py): its verdicts can fail, a slow function fixture fails the test it serves, a slow
shared fixture fails by name and is not charged to the tests that use it (a slow test after its first user still
fails), a playthrough is not timed, the held lists stay empty, and a test over the ceiling once is timed again: slow
both times fails, slow only the first passes and is named in the summary."""
from pathlib import Path

import pytest

from tests import time_gate as gate

pytest_plugins = ["pytester"]

CONTROL = """
import time
import pytest

@pytest.fixture
def slow():
    time.sleep(0.15)
    yield

@pytest.fixture(scope="session")
def tree():
    time.sleep(0.4)
    return 1

@pytest.fixture(scope="session")
def bush():
    time.sleep(0.1)
    return 1

def test_slow_setup(slow):
    pass

def test_uses_tree(tree):
    pass

def test_uses_tree_again(tree):
    pass

def test_slow_after_the_shared_fixture(tree, slow):
    pass

def test_slow_in_its_body_after_a_shared_fixture_it_set_up(bush):
    time.sleep(0.15)

@pytest.mark.playthrough
def test_a_slow_playthrough(slow):
    pass

def test_fast():
    pass
"""


def test_over_the_ceiling_is_slow():
    assert gate.too_slow("tests/x.py::t", gate.CEILING_S + 0.01)


def test_under_the_ceiling_is_fine():
    assert not gate.too_slow("tests/x.py::t", gate.CEILING_S)


def test_a_slow_shared_fixture_is_slow():
    assert gate.fixture_too_slow("tree", gate.FIXTURE_CEILING_S + 0.01)
    assert not gate.fixture_too_slow("tree", gate.FIXTURE_CEILING_S)


def test_the_held_lists_stay_empty():
    assert gate.too_slow("tests/x.py::t", 99) and gate.fixture_too_slow("tree", 99)
    assert not gate.HELD and not gate.HELD_FIXTURES, "the held lists may only shrink; they start empty, so stay empty"


def test_the_gate_fails_slow_fixtures_and_spares_a_playthrough(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    """The gate, registered as conftest.py registers it, run in-process over a file whose only costs are fixtures'
    sleeps, under a 0.08 s test ceiling and a 0.3 s shared-fixture ceiling."""
    monkeypatch.setattr(gate, "CEILING_S", 0.08)
    monkeypatch.setattr(gate, "FIXTURE_CEILING_S", 0.3)
    pytester.makeini("[pytest]\nmarkers =\n    playthrough: a whole-game simulation\n")
    pytester.makeconftest("from tests import time_gate\n\n"
                          "def pytest_configure(config):\n    config.pluginmanager.register(time_gate, 'time_gate')\n")
    pytester.makepyfile(test_control=CONTROL)
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly", "-rA")
    result.assert_outcomes(passed=6, errors=4)   # a teardown error leaves its test counted as passed too
    result.stdout.fnmatch_lines(["*test_slow_setup took *s of wall clock*",
                                 "*fixture tree (session scope) took *s to set up*",
                                 "*test_slow_after_the_shared_fixture took *s of wall clock*",
                                 "*test_slow_in_its_body_after_a_shared_fixture_it_set_up took *s of wall clock*",
                                 "PASSED test_control.py::test_uses_tree_again"], consecutive=False)


RETIME = """
import time

timings = []

def test_slow_every_time():
    time.sleep(0.15)

def test_slow_only_the_first_time():
    timings.append(1)
    if len(timings) == 1:
        time.sleep(0.15)

def test_fast():
    pass
"""


def retime_control(pytester: pytest.Pytester) -> None:
    pytester.makeini("[pytest]\nmarkers =\n    playthrough: a whole-game simulation\n")
    pytester.makeconftest("from tests import time_gate\n\n"
                          "def pytest_configure(config):\n    config.pluginmanager.register(time_gate, 'time_gate')\n")
    pytester.makepyfile(test_retime=RETIME)


def test_a_test_slow_only_on_its_first_timing_passes_and_is_named(pytester: pytest.Pytester,
                                                                 monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate, "CEILING_S", 0.08)
    retime_control(pytester)
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly", "-rA")
    result.assert_outcomes(passed=3, errors=1)   # the always-slow one still fails, its teardown error counted as passed too
    result.stdout.fnmatch_lines(["*test_slow_every_time took *s of wall clock*",
                                 "*time gate: slow once, passed on a second timing*",
                                 "test_retime.py::test_slow_only_the_first_time: 0.1*s the first time*",
                                 "PASSED test_retime.py::test_slow_only_the_first_time"])
    assert "test_slow_only_the_first_time took" not in result.stdout.str()
    assert "test_slow_every_time: " not in result.stdout.str().split("slow once")[-1]


def test_the_retime_reaches_the_controller_under_xdist(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    """Each worker retimes its own test and reports the second timing, so the controller sees the same verdicts."""
    monkeypatch.setenv("TEST_CEILING_S", "0.08")
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parent.parent))
    retime_control(pytester)
    result = pytester.runpytest_subprocess("-p", "no:cacheprovider", "-p", "no:randomly", "-n", "2", "-rA")
    result.assert_outcomes(passed=3, errors=1)
    result.stdout.fnmatch_lines(["*test_slow_every_time took *s of wall clock*",
                                 "*time gate: slow once, passed on a second timing*",
                                 "test_retime.py::test_slow_only_the_first_time: 0.1*s the first time*"])


GUARDED = """
import time
import pytest

@pytest.fixture(scope="session")
def tree():
    time.sleep(0.7)

@pytest.fixture(scope="session")
def bush(tree):
    time.sleep(0.7)

def test_first_user_of_shared_fixtures(bush):
    pass

def test_slow_in_its_body():
    time.sleep(1.5)
"""


def test_shared_fixtures_are_not_charged_to_the_hang_guard(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    """Under a 1 s hang guard, a test whose shared fixtures take 1.4 s between them passes (they run under their own
    guard of FIXTURE_CEILING_S), and a test slow in its own body is still stopped."""
    monkeypatch.setattr(gate, "FIXTURE_CEILING_S", 5.0)
    pytester.makeini("[pytest]\ntimeout = 1\ntimeout_method = signal\n")
    pytester.makeconftest("from tests import time_gate\n\n"
                          "def pytest_configure(config):\n    config.pluginmanager.register(time_gate, 'time_gate')\n")
    pytester.makepyfile(test_guarded=GUARDED)
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly", "-rA")
    result.stdout.fnmatch_lines(["PASSED test_guarded.py::test_first_user_of_shared_fixtures",
                                 "FAILED test_guarded.py::test_slow_in_its_body*Timeout*"])


PLAYED = """
import time
import pytest

@pytest.fixture(scope="session")
def play():
    time.sleep(0.7)

@pytest.mark.playthrough
def test_reads_the_play(play):
    pass

def test_reads_a_slow_fixture(slow):
    pass

@pytest.fixture(scope="module")
def slow():
    time.sleep(0.7)
"""


def test_a_playthroughs_shared_fixture_keeps_the_tests_own_guard(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    """A playthrough's shared fixture is the play itself: it runs under the test's guard, never the shared-fixture one;
    the same fixture time on an ordinary test still trips the shared-fixture guard (the control)."""
    monkeypatch.setattr(gate, "FIXTURE_CEILING_S", 0.3)
    pytester.makeini("[pytest]\ntimeout = 5\ntimeout_method = signal\nmarkers =\n    playthrough: a whole play\n")
    pytester.makeconftest("from tests import time_gate\n\n"
                          "def pytest_configure(config):\n    config.pluginmanager.register(time_gate, 'time_gate')\n")
    pytester.makepyfile(test_played=PLAYED)
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly", "-rA")
    result.stdout.fnmatch_lines(["PASSED test_played.py::test_reads_the_play", "ERROR test_played.py::test_reads_a_slow_fixture*"])


HANGS = """
import time

def test_hangs():
    time.sleep(5)
"""


@pytest.mark.xfail(strict=True, reason="the hang guard's dump names no test")
def test_a_test_killed_by_the_hang_guard_is_named(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    """pytest-timeout's thread method kills the process with only a stack dump, and a `-q` log has no test ids: the
    kill must name the test it interrupted."""
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parent.parent))
    pytester.makeini("[pytest]\ntimeout = 1\ntimeout_method = thread\n")
    pytester.makeconftest("from tests import time_gate\n\n"
                          "def pytest_configure(config):\n    config.pluginmanager.register(time_gate, 'time_gate')\n")
    pytester.makepyfile(test_hang=HANGS)
    result = pytester.runpytest_subprocess("-q", "-p", "no:cacheprovider", "-p", "no:randomly")
    assert result.ret != 0
    out = result.stdout.str()
    assert "Timeout" in out   # control: the guard fired
    assert "test_hang.py::test_hangs" in out
