"""The shared plays (routes.py) as session fixtures, so each is played once, in a fixture's setup rather than a test's
time. `a_route` takes its (route, seed) by indirect parametrization: `@pytest.mark.parametrize("a_route", plays(),
indirect=True)`; `an_after_end` likewise with after_end_plays()."""
import pytest

from tests.opening.afterend import AfterEnd, AfterEndPlayer
from tests.opening.routes import EagerForager, after_end, eager, route
from tests.plays import mark_plays

PLAYS = frozenset({"typical", "by_hand", "fireback_first", "eager_forager", "a_route", "an_after_end"})
"""The fixtures that hand a test a whole play: a test using one must carry the playthrough marker (its CI job)."""


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    mark_plays(items, PLAYS, None)


@pytest.fixture(scope="session")
def typical() -> AfterEndPlayer:
    return route("typical")


@pytest.fixture(scope="session")
def by_hand() -> AfterEndPlayer:
    return route("by_hand")


@pytest.fixture(scope="session")
def fireback_first() -> AfterEndPlayer:
    return route("fireback_first")


@pytest.fixture(scope="session")
def eager_forager() -> EagerForager:
    return eager()


@pytest.fixture(scope="session")
def a_route(request: pytest.FixtureRequest) -> AfterEndPlayer:
    name, seed = request.param
    return route(name, seed)


@pytest.fixture(scope="session")
def an_after_end(request: pytest.FixtureRequest) -> tuple[AfterEnd, AfterEndPlayer]:
    name, seed = request.param
    return after_end(name, seed)
