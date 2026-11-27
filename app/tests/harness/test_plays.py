"""tests/plays.py's mark_plays, on a planted suite: a play's setup is charged to whichever test first requests it, so
every reader runs under the play's timeout (a larger one of its own kept), a test reading no play keeps pytest.ini's,
and a reader without the playthrough marker fails collection."""
import pytest

pytest_plugins = ("pytester",)

CONFTEST = """
import time
import pytest
from tests.plays import mark_plays

def pytest_collection_modifyitems(items):
    mark_plays(items, frozenset({"play"}), 5)

@pytest.fixture(scope="session")
def play():
    time.sleep(0.4)
    return "played"
"""
INI = "[pytest]\ntimeout = 0.2\ntimeout_method = signal\nmarkers =\n    playthrough: reads a play\n"


@pytest.fixture
def planted(pytester: pytest.Pytester) -> pytest.Pytester:
    pytester.makeconftest(CONFTEST)
    pytester.makeini(INI)
    return pytester


def test_the_first_reader_plays_under_the_play_timeout_not_the_ini(planted: pytest.Pytester):
    planted.makepyfile(test_first="import pytest\n\n@pytest.mark.playthrough\ndef test_first(play):\n    assert play == \"played\"\n")
    planted.runpytest_inprocess("-p", "no:cacheprovider").assert_outcomes(passed=1)


def test_a_reader_whose_file_sets_a_larger_timeout_keeps_it(planted: pytest.Pytester):
    planted.makepyfile(test_larger="""
import pytest

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(900)]

def test_larger(play, request):
    assert request.node.get_closest_marker("timeout").args == (900,)
""")
    planted.runpytest_inprocess("-p", "no:cacheprovider").assert_outcomes(passed=1)


def test_a_reader_is_stamped_and_a_non_reader_keeps_the_ini(planted: pytest.Pytester):
    planted.makepyfile(test_marks="""
import pytest

@pytest.mark.playthrough
def test_stamped(play, request):
    assert request.node.get_closest_marker("timeout").args == (5,)

def test_no_play(request):
    assert request.node.get_closest_marker("timeout") is None
""")
    planted.runpytest_inprocess("-p", "no:cacheprovider").assert_outcomes(passed=2)


def test_a_reader_not_marked_playthrough_fails_collection(planted: pytest.Pytester):
    planted.makepyfile(test_unmarked="def test_unmarked(play):\n    pass\n")
    result = planted.runpytest_inprocess("-p", "no:cacheprovider")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["ERROR: test_unmarked.py::test_unmarked reads *'play'* but is not marked playthrough"])
