"""Week two's readouts (report.py) reported against their committed text (tests/readout_snapshot.py): per chapter, each route's
beats, absences and calendar days, and the typical route's visits. The conftest orders tests reading a route's play
first and the counting's parts before the visit readouts that reuse them. A change is reported, never failed; commit it with
`python -m tests.readout_snapshot --write weektwo`."""
from collections import Counter

import pytest

from tests import readout_snapshot as rs
from tests.daythree import counters
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone.report import chapter_text
from tests.weektwo import report

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
Counts = tuple[DayTwoPlayer, list[counters.Counts]]
Days = tuple[DayTwoPlayer, list[Counter[str]]]


def test_the_committed_readouts_are_the_ones_the_report_writes():
    assert rs.stray("weektwo", report.NAMES) == ([], [])


@pytest.mark.parametrize("eight_route", report.ROUTES, indirect=True)
def test_a_day_eight_route_readout_is_reported(eight_route: Route):
    name, p = eight_route
    rs.check(f"weektwo-eight-{name}", report.route_text("eight", name, p, None))


@pytest.mark.parametrize("week_days, name", [(("nine", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_nine_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-nine-{name}", report.route_text("nine", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("eleven", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_eleven_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-eleven-{name}", report.route_text("eleven", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("twelve", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_twelve_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-twelve-{name}", report.route_text("twelve", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("fifteen", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_fifteen_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-fifteen-{name}", report.route_text("fifteen", name, *week_days))


def test_day_eights_visit_readout_is_reported(eight_counts: Counts, eight_marks: dict[str, str]):
    assert len(eight_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-eight", chapter_text("eight", eight_counts[1], eight_marks))


def test_day_nines_visit_readout_is_reported(nine_counts: Counts, nine_marks: dict[str, str]):
    assert len(nine_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-nine", chapter_text("nine", nine_counts[1], nine_marks))


def test_day_elevens_visit_readout_is_reported(eleven_counts: Counts, eleven_marks: dict[str, str]):
    assert len(eleven_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-eleven", chapter_text("eleven", eleven_counts[1], eleven_marks))


def test_day_twelves_visit_readout_is_reported(twelve_counts: Counts, twelve_marks: dict[str, str]):
    assert len(twelve_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-twelve", chapter_text("twelve", twelve_counts[1], twelve_marks))


def test_day_fifteens_visit_readout_is_reported(fifteen_counts: Counts, fifteen_marks: dict[str, str]):
    assert len(fifteen_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-fifteen", chapter_text("fifteen", fifteen_counts[1], fifteen_marks))
