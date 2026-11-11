"""Day two's shared plays (routes.py) as session fixtures, played once in a fixture's setup: `day2_route` takes its
(route, seed) by indirect parametrization, as do `day2_verdicts` (its checks, computed in setup) and `day2_readout`
(its readout, report.py); `two_am2_run` is the
2 AM replay pair. A test reading one is marked playthrough (its CI job). Her lane makes a day-two play far slower than
a day-one one, so every test reading one runs under PLAY_TIMEOUT_S (tests/plays.py), which a fixture's setup counts
against."""
import pytest

from tests.daytwo.parity import two_am2
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.report import route_text
from tests.daytwo.routes import day2
from tests.daytwo.verdicts import verdicts
from tests.dayone.parity import Measured
from tests.plays import mark_plays

DAY_PLAYS = frozenset({"day2_route", "day2_verdicts", "day2_readout", "two_am2_run"})
PLAY_TIMEOUT_S = 600


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    mark_plays(items, DAY_PLAYS, PLAY_TIMEOUT_S)


@pytest.fixture(scope="session")
def day2_route(request: pytest.FixtureRequest) -> DayTwoPlayer:
    name, seed = request.param
    return day2(name, seed)


@pytest.fixture(scope="session")
def day2_verdicts(request: pytest.FixtureRequest) -> tuple[str, int, dict[str, list[str]]]:
    name, seed = request.param
    return name, seed, verdicts(name, seed)


@pytest.fixture(scope="session")
def day2_readout(request: pytest.FixtureRequest) -> tuple[str, str]:
    name, seed = request.param
    return name, route_text(name, day2(name, seed))


@pytest.fixture(scope="session")
def two_am2_run() -> tuple[Measured, Measured]:
    return two_am2()
