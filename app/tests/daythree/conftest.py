"""Day three's plays (routes.py) and what the verdicts read off them, built once per session in a fixture's setup
(playthrough tests, which their CI job's timeout budgets): `day3_route` takes its route by indirect parametrization, `day3_counts` the
typical route's per-visit counts, `day3_readout` its readout (report.py), `day3_cap_loss` its stores losing to caps, `day3_plumbed` the checks past the sinks over typical's saves, `two_am3_run` the 2 AM replay pair. A test reading one is marked playthrough."""
import pytest

from tests.daythree import counters, plumbing, report, verdicts
from tests.daythree.routes import day3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured
from tests.plays import mark_plays

DAY_PLAYS = frozenset({"day3_route", "day3_counts", "day3_readout", "day3_cap_loss", "day3_plumbed", "two_am3_run"})


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    mark_plays(items, DAY_PLAYS, PLAY_TIMEOUT_S)


@pytest.fixture(scope="session")
def day3_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, day3(name)


@pytest.fixture(scope="session")
def day3_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = day3("typical")
    return p, verdicts.chapter_counts(p)


@pytest.fixture(scope="session")
def day3_readout(day3_counts: tuple[DayTwoPlayer, list[counters.Counts]]) -> str:
    return report.typical_text(*day3_counts)


@pytest.fixture(scope="session")
def day3_cap_loss() -> dict[str, tuple[int, ...]]:
    return verdicts.cap_loss(day3("typical"))


@pytest.fixture(scope="session")
def day3_plumbed() -> plumbing.Plumbing:
    return verdicts.plumbed(day3("typical"))


@pytest.fixture(scope="session")
def two_am3_run() -> tuple[Measured, Measured]:
    return verdicts.two_am3()
