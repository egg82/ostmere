"""Week two's plays (routes.py) and what the verdicts read off them, built once per session in a fixture's setup (playthrough
tests, which their CI job's timeout budgets): `eight_route` takes its route by indirect parametrization, `eight_counts` the typical
route's per-visit counts (its heavy steps read first, a part to a setup, `week_part`), `eight_marks` its visits marked for the readout, `two_am_eight_run` the 2 AM replay pair;
the `nine_`, `eleven_`, `twelve_`, `fifteen_`, `sixteen_`, `eighteen_`, `nineteen_`, `twentytwo_`, `twentythree_` and
`twentyfive_`, `twentyseven_` and `twentynine_` fixtures the same for days nine, eleven, twelve, fifteen, sixteen, eighteen, nineteen, twenty-two, twenty-three, twenty-five, twenty-seven and twenty-nine, `twelve_cures`, `fifteen_cures`, `sixteen_cures`, `eighteen_cures`, `nineteen_cures`, `twentytwo_cures`, `twentythree_cures`, `twentyfive_cures`, `twentyseven_cures` and `twentynine_cures` the cures gate over typical's days twelve to twenty-nine, `twelve_ladder` a route's ladder readout, `fifteen_worth` and `fifteen_stints` typical's worth readouts, and `rebased_eight`, `rebased_nine`, `rebased_eleven`, `rebased_twelve`, `rebased_fifteen`, `rebased_sixteen`, `rebased_eighteen`, `rebased_nineteen`, `rebased_twentytwo`, `rebased_twentythree`, `rebased_twentyfive` and `rebased_twentyseven` typical's
saved day-eight end loaded under day nine, its day-nine end under day eleven, its day-eleven end under day twelve, its
day-twelve end under day fifteen, its day-fifteen end under day sixteen, its day-sixteen end under day eighteen, its
day-eighteen end under day nineteen, its day-nineteen end under day twenty-two, its day-twenty-two end under day
twenty-three, its day-twenty-three end under day twenty-five, its day-twenty-five end under day twenty-seven and its
day-twenty-seven end under day twenty-nine;
`chapter_end` a chapter's play
beside its saved end and `rebased_inputs` a saved rebased save's stamped inputs beside today's (ends.py). A test reading
one is marked playthrough."""
from collections import Counter
from collections.abc import Generator

import pytest

from tests.daythree import counters
from tests.daytwo import checks as checks2
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured
from tests.weektwo import ends, rebased, verdicts
from tests.plays import mark_plays
from tools import weektwo_shards as shards
from tests.dayone.fights import cures
from tests.ladder import readout
from tests.worth import readout as worth
from tests.worth import stints
from tests.weektwo import routes
from tests.weektwo.rebased import Rebased
from tests.weektwo.routes import (
    CHAPTERS, eighteen, eleven, fifteen, nine, nineteen, saved_end, sixteen, twelve, twentyfive, twentynine, twentyseven, twentythree, twentytwo, week2,
)

EIGHT_PLAYS = frozenset({"eight_route", "eight_counts", "week_part", "two_am_eight_run", "nine_route", "nine_counts",
                         "nine_marks", "eight_marks", "two_am_nine_run", "week_days", "rebased_eight", "eleven_route",
                         "eleven_counts", "two_am_eleven_run", "rebased_nine", "twelve_route",
                         "twelve_counts", "two_am_twelve_run", "rebased_eleven", "rebased_twelve",
                         "twelve_cures", "twelve_ladder", "eleven_marks", "twelve_marks", "chapter_end", "rebased_inputs",
                         "fifteen_route", "fifteen_counts", "two_am_fifteen_run", "fifteen_cures",
                         "fifteen_marks", "fifteen_worth", "fifteen_stints", "sixteen_route", "sixteen_counts", "two_am_sixteen_run",
                         "sixteen_cures", "sixteen_marks", "rebased_fifteen", "eighteen_route", "eighteen_counts",
                         "two_am_eighteen_run", "eighteen_cures", "eighteen_marks", "rebased_sixteen", "nineteen_route",
                         "nineteen_counts", "two_am_nineteen_run", "nineteen_cures", "nineteen_marks", "rebased_eighteen",
                         "twentytwo_route", "twentytwo_counts", "two_am_twentytwo_run", "twentytwo_cures",
                         "twentytwo_marks", "rebased_nineteen", "twentythree_route", "twentythree_counts",
                         "two_am_twentythree_run", "twentythree_cures", "twentythree_marks", "rebased_twentytwo",
                         "twentyfive_route", "twentyfive_counts", "two_am_twentyfive_run", "twentyfive_cures",
                         "twentyfive_marks", "rebased_twentythree", "twentyseven_route", "twentyseven_counts",
                         "two_am_twentyseven_run", "twentyseven_cures", "twentyseven_marks", "rebased_twentyfive",
                         "twentynine_route", "twentynine_counts", "two_am_twentynine_run", "twentynine_cures",
                         "twentynine_marks", "rebased_twentyseven"})


ROUTE_PLAYS = ("eight_route", "nine_route", "eleven_route", "twelve_route", "fifteen_route", "sixteen_route",
               "eighteen_route", "nineteen_route", "twentytwo_route",
               "twentythree_route", "twentyfive_route", "twentyseven_route", "twentynine_route")
"""The route fixtures in the order their plays build on each other (each chapter's play is the one before it played on)."""


def played_first(item: pytest.Item) -> tuple[int, int]:
    """Tests reading a route's play run first, chapter by chapter, then the counting's parts, so each play's and each
    part's setup is paid by a test of its own and not by whichever readout or cap-loss test happens to come first."""
    names = getattr(item, "fixturenames", ())
    uses = [i for i, fixture in enumerate(ROUTE_PLAYS) if fixture in names]
    return (0, min(uses)) if uses else (1, 0) if "week_part" in names else (2, 0)


AFTER = {"rebased_eight": "nine", "rebased_nine": "eleven", "rebased_eleven": "twelve", "rebased_twelve": "twelve",
         "rebased_fifteen": "sixteen", "rebased_sixteen": "eighteen",
         "rebased_eighteen": "nineteen", "rebased_nineteen": "twentytwo",
         "rebased_twentytwo": "twentythree", "rebased_twentythree": "twentyfive",
         "rebased_twentyfive": "twentyseven", "rebased_twentyseven": "twentynine"}
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


def named_shard(item: pytest.Item) -> str | None:
    """The shard a test's `weektwo_shard` marker names, or None."""
    marker = item.get_closest_marker("weektwo_shard")
    return marker.args[0] if marker else None


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
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    mark_plays(items, EIGHT_PLAYS, PLAY_TIMEOUT_S)
    group_by_play(items)
    keep_shard(config, items)
    keep_slice(config, items)
    items.sort(key=played_first)


def keep_shard(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Under WEEKTWO_SHARD, deselect the week-two tests another shard runs (tools/weektwo_shards.py); tests elsewhere
    are kept."""
    name = shards.chosen()
    if name is None:
        return
    dropped = [i for i in items if shards.in_week_two(i) and shards.shard_of(play_of(i), named_shard(i)) != name]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        gone = set(map(id, dropped))
        items[:] = [i for i in items if id(i) not in gone]


FULL_RUN_ONLY = frozenset({f"{c}_counts" for c in CHAPTERS} | {"week_part", "chapter_end", "rebased_inputs"} | set(AFTER))
"""The fixtures that read what only the full run writes: a chapter's own saved end, its heavy-step readings and its
rebased save, all under keys a changed chapter does not have yet."""


def keep_slice(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Under WEEKTWO_SLICE, keep of the week-two tests the slice's (tools/weektwo_shards.py); tests elsewhere are kept."""
    chosen = shards.sliced()
    if chosen is None:
        return
    named = shards.files()

    def kept(item: pytest.Item) -> bool:
        if shards.SMOKE in chosen:
            return item.get_closest_marker(shards.SMOKE) is not None
        play = play_of(item)
        mine = (play is not None and play[0] in chosen) or item.path.resolve() in named
        return mine and not FULL_RUN_ONLY & set(getattr(item, "fixturenames", ()))

    dropped = [i for i in items if shards.in_week_two(i) and not kept(i)]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        gone = set(map(id, dropped))
        items[:] = [i for i in items if id(i) not in gone]


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, None, None]:
    """A play first built while a test's body runs is one `play_of` never placed: it was paid in whichever shard the test
    fell into. Fixture setup, which runs before this, is where plays are built; a test marked `weektwo_shard` names its shard."""
    routes.hidden_play_in = None if named_shard(item) else item.nodeid
    try:
        return (yield)
    finally:
        routes.hidden_play_in = None


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
def week_part(request: pytest.FixtureRequest) -> tuple[int, verdicts.Decided]:
    """(the part, what its heavy steps decide)."""
    chapter, part = request.param
    return part, verdicts.decided_in(chapter, part)


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
    """A chapter's saved rebased save's stamped inputs, and today's: typical's play to the chapter's end, from its
    checkpoint (rebased.todays_inputs)."""
    chapter: str = request.param
    p = verdicts.PLAYS[chapter]("typical")
    now = rebased.todays_inputs(chapter, p)
    return (ends.rebased_text(chapter).inputs if ends.available(chapter) else now), now


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


@pytest.fixture(scope="session")
def fifteen_stints() -> str:
    """The worth readout's route with its own rules (tests/worth/stints.py), read in setup."""
    return stints.text(fifteen(worth.ROUTE), worth.ROUTE)


@pytest.fixture(scope="session")
def sixteen_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, sixteen(name)


@pytest.fixture(scope="session")
def sixteen_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = sixteen("typical")
    return p, verdicts.counts(p, verdicts.SIXTEEN, verdicts.typical_decided("sixteen"))


@pytest.fixture(scope="session")
def sixteen_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(sixteen("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_sixteen_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "sixteen")


@pytest.fixture(scope="session")
def sixteen_cures() -> list[str]:
    """The cures gate over typical's play from B14's landing: every chip shown has a cure on offer."""
    p = sixteen("typical")
    return cures.uncured(p, p.landed_at["B14"])


@pytest.fixture(scope="session")
def rebased_fifteen() -> Rebased:
    return rebased.from_saved("fifteen")


@pytest.fixture(scope="session")
def eighteen_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, eighteen(name)


@pytest.fixture(scope="session")
def eighteen_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = eighteen("typical")
    return p, verdicts.counts(p, verdicts.EIGHTEEN, verdicts.typical_decided("eighteen"))


@pytest.fixture(scope="session")
def eighteen_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(eighteen("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_eighteen_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "eighteen")


@pytest.fixture(scope="session")
def eighteen_cures() -> list[str]:
    """The cures gate over typical's play from B15's landing: every chip shown has a cure on offer."""
    p = eighteen("typical")
    return cures.uncured(p, p.landed_at["B15"])


@pytest.fixture(scope="session")
def rebased_sixteen() -> Rebased:
    return rebased.from_saved("sixteen")


@pytest.fixture(scope="session")
def nineteen_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, nineteen(name)


@pytest.fixture(scope="session")
def nineteen_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = nineteen("typical")
    return p, verdicts.counts(p, verdicts.NINETEEN, verdicts.typical_decided("nineteen"))


@pytest.fixture(scope="session")
def nineteen_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(nineteen("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_nineteen_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "nineteen")


@pytest.fixture(scope="session")
def nineteen_cures() -> list[str]:
    """The cures gate over typical's play from B16's landing: every chip shown has a cure on offer."""
    p = nineteen("typical")
    return cures.uncured(p, p.landed_at["B16"])


@pytest.fixture(scope="session")
def rebased_eighteen() -> Rebased:
    return rebased.from_saved("eighteen")


@pytest.fixture(scope="session")
def twentytwo_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, twentytwo(name)


@pytest.fixture(scope="session")
def twentytwo_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = twentytwo("typical")
    return p, verdicts.counts(p, verdicts.TWENTYTWO, verdicts.typical_decided("twentytwo"))


@pytest.fixture(scope="session")
def twentytwo_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(twentytwo("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_twentytwo_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "twentytwo")


@pytest.fixture(scope="session")
def twentytwo_cures() -> list[str]:
    """The cures gate over typical's play from T13's landing: every chip shown has a cure on offer."""
    p = twentytwo("typical")
    return cures.uncured(p, p.landed_at["T13"])


@pytest.fixture(scope="session")
def rebased_nineteen() -> Rebased:
    return rebased.from_saved("nineteen")


@pytest.fixture(scope="session")
def twentythree_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, twentythree(name)


@pytest.fixture(scope="session")
def twentythree_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = twentythree("typical")
    return p, verdicts.counts(p, verdicts.TWENTYTHREE, verdicts.typical_decided("twentythree"))


@pytest.fixture(scope="session")
def twentythree_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(twentythree("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_twentythree_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "twentythree")


@pytest.fixture(scope="session")
def twentythree_cures() -> list[str]:
    """The cures gate over typical's play from B19's landing: every chip shown has a cure on offer."""
    p = twentythree("typical")
    return cures.uncured(p, p.landed_at["B19"])


@pytest.fixture(scope="session")
def rebased_twentytwo() -> Rebased:
    return rebased.from_saved("twentytwo")


@pytest.fixture(scope="session")
def twentyfive_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, twentyfive(name)


@pytest.fixture(scope="session")
def twentyfive_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = twentyfive("typical")
    return p, verdicts.counts(p, verdicts.TWENTYFIVE, verdicts.typical_decided("twentyfive"))


@pytest.fixture(scope="session")
def twentyfive_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(twentyfive("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_twentyfive_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "twentyfive")


@pytest.fixture(scope="session")
def twentyfive_cures() -> list[str]:
    """The cures gate over typical's play from B20's landing: every chip shown has a cure on offer."""
    p = twentyfive("typical")
    return cures.uncured(p, p.landed_at["B20"])


@pytest.fixture(scope="session")
def rebased_twentythree() -> Rebased:
    return rebased.from_saved("twentythree")


@pytest.fixture(scope="session")
def twentyseven_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, twentyseven(name)


@pytest.fixture(scope="session")
def twentyseven_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = twentyseven("typical")
    return p, verdicts.counts(p, verdicts.TWENTYSEVEN, verdicts.typical_decided("twentyseven"))


@pytest.fixture(scope="session")
def twentyseven_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(twentyseven("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_twentyseven_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "twentyseven")


@pytest.fixture(scope="session")
def twentyseven_cures() -> list[str]:
    """The cures gate over typical's play from B21's landing: every chip shown has a cure on offer."""
    p = twentyseven("typical")
    return cures.uncured(p, p.landed_at["B21"])


@pytest.fixture(scope="session")
def rebased_twentyfive() -> Rebased:
    return rebased.from_saved("twentyfive")



@pytest.fixture(scope="session")
def twentynine_route(request: pytest.FixtureRequest) -> tuple[str, DayTwoPlayer]:
    name: str = request.param
    return name, twentynine(name)


@pytest.fixture(scope="session")
def twentynine_counts() -> tuple[DayTwoPlayer, list[counters.Counts]]:
    p = twentynine("typical")
    return p, verdicts.counts(p, verdicts.TWENTYNINE, verdicts.typical_decided("twentynine"))


@pytest.fixture(scope="session")
def twentynine_marks() -> dict[str, str]:
    """The typical route's visits marked for the readout (daytwo/checks.marks), read in setup."""
    return checks2.marks(twentynine("typical"), first=1)


@pytest.fixture(scope="session")
def two_am_twentynine_run() -> tuple[Measured, Measured]:
    return verdicts.two_am(0, "twentynine")


@pytest.fixture(scope="session")
def twentynine_cures() -> list[str]:
    """The cures gate over typical's play from I13's landing: every chip shown has a cure on offer."""
    p = twentynine("typical")
    return cures.uncured(p, p.landed_at["I13"])


@pytest.fixture(scope="session")
def rebased_twentyseven() -> Rebased:
    return rebased.from_saved("twentyseven")
