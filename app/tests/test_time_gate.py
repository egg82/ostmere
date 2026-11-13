"""The per-test time gate (time_gate.py): its verdicts can fail, a slow function fixture fails the test it serves, a slow
shared fixture fails by name and is not charged to the tests that use it, a playthrough is not timed, and the held
lists stay empty."""
import pytest

from tests import time_gate as gate

pytest_plugins = ["pytester"]

CONTROL = """
import time
import pytest

@pytest.fixture
def slow():
    time.sleep(0.3)
    yield

@pytest.fixture(scope="session")
def tree():
    time.sleep(0.3)
    return 1

def test_slow_setup(slow):
    pass

def test_uses_tree(tree):
    pass

def test_uses_tree_again(tree):
    pass

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
    sleeps, under a 0.1 s test ceiling and a 0.2 s shared-fixture ceiling."""
    monkeypatch.setattr(gate, "CEILING_S", 0.1)
    monkeypatch.setattr(gate, "FIXTURE_CEILING_S", 0.2)
    pytester.makeini("[pytest]\nmarkers =\n    playthrough: a whole-game simulation\n")
    pytester.makeconftest("from tests import time_gate\n\n"
                          "def pytest_configure(config):\n    config.pluginmanager.register(time_gate, 'time_gate')\n")
    pytester.makepyfile(test_control=CONTROL)
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly", "-rA")
    result.assert_outcomes(passed=4, errors=2)
    result.stdout.fnmatch_lines(["*test_slow_setup took 0.3*s of wall clock*",
                                 "*fixture tree (session scope) took 0.3*s to set up*",
                                 "PASSED test_control.py::test_uses_tree_again"])
