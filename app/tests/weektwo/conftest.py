"""Week two's plays (routes.py) and what the verdicts read off them, built once per session in a fixture's setup (setup is
not timed by the CPU ceiling): `eight_route` takes its route by indirect parametrization, `eight_counts` the typical
route's per-visit counts (its heavy steps read first, a part to a setup, `week_part`), `eight_loss` its cap-loss check
at the chapter's end, `eight_marks` its visits marked for the readout, `two_am_eight_run` the 2 AM replay pair;
the `nine_`, `eleven_`, `twelve_` and `fifteen_` fixtures the same for days nine, eleven, twelve and fifteen,
`twelve_cures` and `fifteen_cures` the cures gate over typical's day twelve and day fifteen, `twelve_ladder` a route's ladder readout, `fifteen_worth` typical's worth readout, and `rebased_eight`, `rebased_nine`, `rebased_eleven` and `rebased_twelve` typical's saved
day-eight end loaded under day nine, its day-nine end under day eleven, its day-eleven end under day twelve and its
day-twelve end under day fifteen; `chapter_end` a chapter's play
beside its saved end and `rebased_inputs` a saved rebased save's stamped inputs beside today's (ends.py). A test reading
one is marked playthrough."""
from collections import Counter

import pytest

from tests.daythree import counters
from tests.daytwo import checks as checks2
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured
from tests.weektwo import ends, rebased, verdicts
from tests.plays import mark_plays
from tests.dayone import cures
from tests.ladder import readout
from tests.worth import readout as worth
from tests.weektwo.rebased import Rebased
from tests.weektwo.routes import CHAPTERS, eleven, fifteen, nine, saved_end, twelve, week2

EIGHT_PLAYS = frozenset({"eight_route", "eight_counts", "week_part", "eight_loss", "two_am_eight_run", "nine_route", "nine_counts",
                         "nine_loss", "nine_marks", "eight_marks", "two_am_nine_run", "week_days", "rebased_eight", "eleven_route",
                         "eleven_counts", "eleven_loss", "two_am_eleven_run", "rebased_nine", "twelve_route",
                         "twelve_counts", "twelve_loss", "two_am_twelve_run", "rebased_eleven", "rebased_twelve",
                         "twelve_cures", "twelve_ladder", "eleven_marks", "twelve_marks", "chapter_end", "rebased_inputs",
                         "fifteen_route", "fifteen_counts", "fifteen_loss", "two_am_fifteen_run", "fifteen_cures",
                         "fifteen_marks", "fifteen_worth"})


ROUTE_PLAYS = ("eight_route", "nine_route", "eleven_route", "twelve_route", "fifteen_route")
"""The route fixtures in the order their plays build on each other (each chapter's play is the one before it played on)."""


def played_first(item: pytest.Item) -> tuple[int, int]:
    """Tests reading a route's play run first, chapter by chapter, then the counting's parts, so each play's and each
    part's setup is paid by a test of its own and not by whichever readout or cap-loss test happens to come first."""
    names = getattr(item, "fixturenames", ())
    uses = [i for i, fixture in enumerate(ROUTE_PLAYS) if fixture in names]
    return (0, min(uses)) if uses else (1, 0) if "week_part" in names else (2, 0)


AFTER = {"rebased_eight": "nine", "rebased_nine": "eleven", "rebased_eleven": "twelve", "rebased_twelve": "twelve"}
"""The chapter whose play each saved-end fixture's test plays on."""


def play_of(item: pytest.Item) -> tuple[str, str] | None:
    """The (chapter, route) play a test reads, or None when it reads none of week two's plays. Each is played from the
    saved end of the chapter before, so one is independent of every other."""
    params = getattr(getattr(item, "callspec", None), "params", {})
    for name in getattr(item, "fixturenames", ()):
        chapter = next((c for c in CHAPTERS if c in name.split("_")), None)
        if name in ROUTE_PLAYS or name == "twelve_ladder":
            return name.split("_")[0], params[name]
        if name in ("week_days", "chapter_end"):
            return params[name]
        if name == "week_part":
            return params[name][0], "typical"
        if name == "rebased_inputs":
            return params[name], "typical"
        if name in AFTER:
            return AFTER[name], "typical"
        if name.startswith("two_am_") and chapter:
            return chapter, "whenever"
        if chapter and name in EIGHT_PLAYS:
            return chapter, "typical"
    return None


def group_by_play(items: list[pytest.Item]) -> None:
    """Under `pytest -n N --dist loadgroup`, a play's readers share one worker, which builds it once; without xdist the
    marker does nothing."""
    for item in items:
        play = play_of(item)
        if play is not None:
            item.add_marker(pytest.mark.xdist_group("-".join(play)))
        elif EIGHT_PLAYS & set(getattr(item, "fixturenames", ())):
            raise pytest.UsageError(f"{item.nodeid} reads a week-two play that play_of does not place in a (chapter, route)")


@pytest.hookimpl(tryfirst=True)   # xdist reads the group markers in its own hook, which runs after a conftest's unless this does
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    mark_plays(items, EIGHT_PLAYS, PLAY_TIMEOUT_S)
    group_by_play(items)
    items.sort(key=played_first)


@pytest.fixture(scope="session")
def eight_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, week2(name)


@pytest.fixture(scope="session")
def eight_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = week2("typical")
    return p, verdicts.counts(p, verdicts.EIGHT, verdicts.typical_decided("eight"))


@pytest.fixture(scope="session")
def eight_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(week2("typical"), first=1)


@pytest.fixture(scope="session")
def week_part(request: pytest.FixtureRequest) -> verdicts.Decided:
    chapter, part = request.param
    return verdicts.decided_in(chapter, part)


@pytest.fixture(scope="session")
def eight_loss() -> dict[str, tuple[int, ...]]:
    return verdicts.cap_loss(week2("typical"))


@pytest.fixture(scope="session")
def two_am_eight_run() -> tuple[Measured, Measured]:
    return verdicts.two_am()


@pytest.fixture(scope="session")
def nine_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, nine(name)


@pytest.fixture(scope="session")
def nine_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = nine("typical")
    return p, verdicts.counts(p, verdicts.NINE, verdicts.typical_decided("nine"))


@pytest.fixture(scope="session")
def nine_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(nine("typical"), first=1)


@pytest.fixture(scope="session")
def nine_loss() -> dict[str, tuple[int, ...]]:
    return verdicts.cap_loss(nine("typical"), verdicts.NINE)


@pytest.fixture(scope="session")
def two_am_nine_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "nine")


@pytest.fixture(scope="session")
def week_days(request: pytest.FixtureRequest) -> tuple[DayTwoPlayer, list[Counter[str]]]:
    """One chapter's route's arrivals by kind per whole calendar day after week one's, through the chapter
    (verdicts.calendar_days), counted in setup."""
    chapter, route = request.param
    p = verdicts.PLAYS[chapter](route)
    return p, verdicts.calendar_days(p)


@pytest.fixture(scope="session")
def rebased_eight() -> Rebased:
    return rebased.from_saved("eight")


@pytest.fixture(scope="session")
def eleven_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, eleven(name)


@pytest.fixture(scope="session")
def eleven_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = eleven("typical")
    return p, verdicts.counts(p, verdicts.ELEVEN, verdicts.typical_decided("eleven"))


@pytest.fixture(scope="session")
def eleven_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(eleven("typical"), first=1)


@pytest.fixture(scope="session")
def eleven_loss() -> dict[str, tuple[int, ...]]:
    return verdicts.cap_loss(eleven("typical"), verdicts.ELEVEN)


@pytest.fixture(scope="session")
def two_am_eleven_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "eleven")


@pytest.fixture(scope="session")
def rebased_nine() -> Rebased:
    return rebased.from_saved("nine")


@pytest.fixture(scope="session")
def twelve_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, twelve(name)


@pytest.fixture(scope="session")
def twelve_ladder(request: pytest.FixtureRequest) -> tuple[str, str]:
    """(route, its ladder readout: tests/ladder/readout.py), read in setup."""
    name: str = request.param
    return name, readout.route_text(name, twelve(name))


@pytest.fixture(scope="session")
def twelve_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = twelve("typical")
    return p, verdicts.counts(p, verdicts.TWELVE, verdicts.typical_decided("twelve"))


@pytest.fixture(scope="session")
def twelve_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(twelve("typical"), first=1)


@pytest.fixture(scope="session")
def twelve_loss() -> dict[str, tuple[int, ...]]:
    return verdicts.cap_loss(twelve("typical"), verdicts.TWELVE)


@pytest.fixture(scope="session")
def two_am_twelve_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "twelve")


@pytest.fixture(scope="session")
def rebased_eleven() -> Rebased:
    return rebased.from_saved("eleven")


@pytest.fixture(scope="session")
def rebased_twelve() -> Rebased:
    return rebased.from_saved("twelve")


@pytest.fixture(scope="session")
def twelve_cures() -> list[str]:
    """The cures gate over typical's play from B11's landing: every chip shown has a cure on offer."""
    p = twelve("typical")
    return cures.uncured(p, p.landed_at["B11"])


@pytest.fixture(scope="session")
def chapter_end(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer, DayTwoPlayer]:
    """(chapter, route): the session's play of the chapter on the route and its saved end, loaded in setup."""
    chapter, name = request.param
    return f"{chapter} on {name}", verdicts.PLAYS[chapter](name), saved_end(chapter, name)


@pytest.fixture(scope="session")
def rebased_inputs(request: pytest.FixtureRequest) -> tuple[str, str]:
    """A chapter's saved rebased save's stamped inputs, and today's: typical's play to the chapter's end (rebased.inputs)."""
    chapter: str = request.param
    p = verdicts.PLAYS[chapter]("typical")
    now = rebased.inputs(p, rebased.ENDS[chapter](p))
    return (ends.rebased_text(chapter).inputs if ends.available() else now), now


@pytest.fixture(scope="session")
def fifteen_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, fifteen(name)


@pytest.fixture(scope="session")
def fifteen_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = fifteen("typical")
    return p, verdicts.counts(p, verdicts.FIFTEEN, verdicts.typical_decided("fifteen"))


@pytest.fixture(scope="session")
def fifteen_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(fifteen("typical"), first=1)


@pytest.fixture(scope="session")
def fifteen_loss() -> dict[str, tuple[int, ...]]:
    return verdicts.cap_loss(fifteen("typical"), verdicts.FIFTEEN)


@pytest.fixture(scope="session")
def two_am_fifteen_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "fifteen")


@pytest.fixture(scope="session")
def fifteen_cures() -> list[str]:
    """The cures gate over typical's play from S4's landing: every chip shown has a cure on offer."""
    p = fifteen("typical")
    return cures.uncured(p, p.landed_at["S4"])


@pytest.fixture(scope="session")
def fifteen_worth() -> str:
    """Typical's worth readout through day fifteen (tests/worth/readout.py), read in setup."""
    return worth.text(fifteen(worth.ROUTE))
