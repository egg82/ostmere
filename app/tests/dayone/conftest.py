"""Day one's shared plays (routes.py) as session fixtures, played once in a fixture's setup: `day_route` takes its
(route, seed) by indirect parametrization, as do `day_verdicts` and `day_uncured` (its checks, computed in setup), `day_leaves` (its leave points, levelpays.py)
and `day_readout` (its readout, report.py);
`two_am_run` is the 2 AM replay pair; `human_run` the human-paced player's day with its sessions; `unlock_runs` the
earned/fixed-time classification against two poorer routes. A test reading one is marked
playthrough (its CI job); a play is seconds long, so every test reading one runs under PLAY_TIMEOUT_S (tests/plays.py),
which a fixture's setup counts against."""
import pytest

from ashfall_app.engine import Unlock
from tests.dayone import absence, cures
from tests.dayone import human_flags as hf
from tests.dayone.human import HumanPlayer, human_day, thresholds
from tests.dayone.levelpays import LeavePoint, leave_points
from tests.dayone.parity import Measured
from tests.dayone.player import DayOnePlayer
from tests.dayone.report import route_text
from tests.dayone.routes import day, two_am
from tests.dayone.verdicts import verdicts
from tests.plays import mark_plays

DAY_PLAYS = frozenset({"day_route", "day_verdicts", "day_uncured", "day_leaves", "day_readout", "two_am_run", "human_run",
                       "unlock_runs", "absence_run"})
PLAY_TIMEOUT_S = 120


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    mark_plays(items, DAY_PLAYS, PLAY_TIMEOUT_S)


@pytest.fixture(scope="session")
def day_route(request: pytest.FixtureRequest) -> DayOnePlayer:
    name, seed = request.param
    return day(name, seed)


@pytest.fixture(scope="session")
def day_verdicts(request: pytest.FixtureRequest) -> tuple[str, int, dict[str, list[str]]]:
    """(route, seed, every check's problems), computed once in setup."""
    name, seed = request.param
    return name, seed, verdicts(name, seed)


@pytest.fixture(scope="session")
def day_readout(request: pytest.FixtureRequest) -> tuple[str, str]:
    """(route, its readout text: report.route_text), rendered once in setup."""
    name, seed = request.param
    return name, route_text(name, day(name, seed))


@pytest.fixture(scope="session")
def day_uncured(request: pytest.FixtureRequest) -> list[str]:
    """(route, seed)'s chips shown with no cure on offer (cures.py), computed once in setup."""
    name, seed = request.param
    return cures.uncured(day(name, seed))


@pytest.fixture(scope="session")
def day_leaves(request: pytest.FixtureRequest) -> tuple[DayOnePlayer, list[LeavePoint]]:
    """(route, seed)'s play and its day-one leave points (levelpays.py), computed once in setup."""
    name, seed = request.param
    p = day(name, seed)
    return p, leave_points(p)


@pytest.fixture(scope="session")
def two_am_run() -> tuple[Measured, Measured]:
    return two_am()


@pytest.fixture(scope="session")
def human_run() -> tuple[HumanPlayer, list[hf.Session]]:
    """The human-paced player's day and its sessions (human_flags.py), computed once in setup."""
    p = human_day()
    return p, hf.sessions(p, thresholds())


@pytest.fixture(scope="session")
def unlock_runs() -> tuple[dict[Unlock, str], dict[Unlock, str]]:
    """The typical route's unlocks as earned or fixed-time against by_hand (the same visits, a poorer setup) and
    against lazy (a poorer presence, which must read as earned: the probe can fire)."""
    margin = thresholds().v("unlock_margin_s")
    return (hf.classify(day("typical"), day("by_hand"), margin), hf.classify(day("typical"), day("lazy"), margin))


@pytest.fixture(scope="session")
def absence_run() -> list[absence.Point]:
    """The human-paced player's first three leave points left for 1, 8 and 24 h (the report runs all four and to 7 days)."""
    return absence.ladder(human_day(), visits=(1, 2, 3), hours=(1, 8, 24))
