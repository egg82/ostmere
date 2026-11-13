"""Week one's plays (routes.py) and what the verdicts read off them, built once per session in a fixture's setup (playthrough
tests, which their CI job's timeout budgets): `week_route` takes its route by indirect parametrization, `week_part` one heavy step's reading of a
chapter (verdicts.PARTS), `week_spends` and `week_counts` one chapter's typical-route spend and per-visit counts (also by indirect
parametrization), `week_days` one route's arrivals per calendar day, `week_marks` the typical route's visits marked for the
readout (daytwo/checks.marks), `two_am_week_run` the 2 AM replay pair. A test
reading one is marked playthrough."""
from collections import Counter

import pytest

from ashfall_app.engine import Save
from tests.daythree import counters, plumbing
from tests.daytwo import checks as checks2
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured
from tests.saves.absence import advanced_counted
from tests.weekone import fights, verdicts
from tests.weekone.routes import week1
from tests.weektwo import ends
from tests.weektwo.routes import laters
from tests.plays import mark_plays

WEEK_PLAYS = frozenset({"week_route", "week_spends", "week_part", "week_counts", "week_checks", "week_days", "week_marks",
                        "two_am_week_run", "week_timing", "week_prepared", "week_absence", "week_export"})


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    mark_plays(items, WEEK_PLAYS, PLAY_TIMEOUT_S)


@pytest.fixture(scope="session")
def week_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, week1(name)


@pytest.fixture(scope="session")
def week_export(week_route: tuple[str, DayTwoPlayer]) -> list[str]:
    """The route's play written where the saved week one's job reads it (ends.exported_path), then loaded back: the
    attributes, by name, on which the loaded play differs from the played one. Pickling and compressing a week's play
    is the cost, so it is done once, in the fixture."""
    name, p = week_route
    path = ends.exported_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ends.dump(p))
    return ends.differs(ends.load_from(path, laters("week1", name)), p)


@pytest.fixture(scope="session")
def week_part(request: pytest.FixtureRequest) -> verdicts.Decided:
    chapter, part = request.param
    return verdicts.decided_in(chapter, part)


@pytest.fixture(scope="session")
def week_counts(request: pytest.FixtureRequest) -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = week1("typical")
    return p, verdicts.counts_of(p, request.param, verdicts.typical_decided(request.param))


@pytest.fixture(scope="session")
def week_spends(request: pytest.FixtureRequest) -> tuple[DayTwoPlayer, list[int]]:
    """One chapter's spend per visit on the typical route: the counters' cheap half, with the visits read in setup."""
    p = week1("typical")
    return p, verdicts.spends_of(p, request.param)


@pytest.fixture(scope="session")
def week_days(request: pytest.FixtureRequest) -> tuple[DayTwoPlayer, list[Counter[str]]]:
    """One route's arrivals by kind per whole calendar day (verdicts.calendar_days), counted in setup."""
    p = week1(request.param)
    return p, verdicts.calendar_days(p)


@pytest.fixture(scope="session")
def week_marks() -> dict[str, str]:
    return checks2.marks(week1("typical"), first=1)


@pytest.fixture(scope="session")
def week_checks() -> tuple[plumbing.Plumbing, dict[str, dict[str, tuple[int, ...]]]]:
    """The typical route's checks past the sinks and its cap-loss check at each chapter's end, computed in setup."""
    p = week1("typical")
    return verdicts.plumbed(p), verdicts.cap_loss(p)


@pytest.fixture(scope="session")
def two_am_week_run() -> tuple[Measured, Measured]:
    return verdicts.two_am_week()


@pytest.fixture(scope="session")
def week_timing(request: pytest.FixtureRequest) -> tuple[fights.Week, Save, Save]:
    """The typical route's decisions from day four to an hour past G2, played on their own and with the named schedule's
    visits as stops, each read in setup."""
    w = fights.week()
    return w, fights.unsliced(), fights.run(w, w.log, fights.visit_edges(request.param, 0, w))


@pytest.fixture(scope="session")
def week_prepared() -> tuple[fights.Week, Save, Save]:
    """The same span played as the route did and with the week's gear never built, read in setup."""
    w = fights.week()
    return w, fights.unsliced(), fights.run(w, fights.without_gear(w.log), strict=False)


@pytest.fixture(scope="session")
def week_absence() -> dict[str, int]:
    """A day away from the first heavy step of the fifth chapter on the typical route: instants and schedules counted."""
    p = week1("typical")
    label, i = verdicts.heavy_steps(p, "five")[0]
    save = next(v for v in verdicts.chapter_visits(p, "five") if v.label == label).steps[i].before
    return advanced_counted(save, p.rules, 1)
