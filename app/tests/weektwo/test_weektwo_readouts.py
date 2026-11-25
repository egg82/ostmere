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
from tests.weekone.verdicts import cap_lines
from tests.weektwo import verdicts
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


@pytest.mark.parametrize("week_days, name", [(("sixteen", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_sixteen_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-sixteen-{name}", report.route_text("sixteen", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("eighteen", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_eighteen_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-eighteen-{name}", report.route_text("eighteen", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("nineteen", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_nineteen_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-nineteen-{name}", report.route_text("nineteen", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("twentytwo", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_twenty_two_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-twentytwo-{name}", report.route_text("twentytwo", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("twentythree", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_twenty_three_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-twentythree-{name}", report.route_text("twentythree", name, *week_days))


@pytest.mark.parametrize("week_days, name", [(("twentyfive", r), r) for r in report.ROUTES], indirect=["week_days"],
                         ids=report.ROUTES)
def test_a_day_twenty_five_route_readout_is_reported(week_days: Days, name: str):
    rs.check(f"weektwo-twentyfive-{name}", report.route_text("twentyfive", name, *week_days))


def test_day_eights_visit_readout_is_reported(eight_counts: Counts, eight_marks: dict[str, str]):
    assert len(eight_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-eight", chapter_text("eight", eight_counts[1], eight_marks, cap_lines(eight_counts[0], verdicts.CHAPTERS["eight"])))


def test_day_nines_visit_readout_is_reported(nine_counts: Counts, nine_marks: dict[str, str]):
    assert len(nine_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-nine", chapter_text("nine", nine_counts[1], nine_marks, cap_lines(nine_counts[0], verdicts.CHAPTERS["nine"])))


def test_day_elevens_visit_readout_is_reported(eleven_counts: Counts, eleven_marks: dict[str, str]):
    assert len(eleven_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-eleven", chapter_text("eleven", eleven_counts[1], eleven_marks, cap_lines(eleven_counts[0], verdicts.CHAPTERS["eleven"])))


def test_day_twelves_visit_readout_is_reported(twelve_counts: Counts, twelve_marks: dict[str, str]):
    assert len(twelve_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-twelve", chapter_text("twelve", twelve_counts[1], twelve_marks, cap_lines(twelve_counts[0], verdicts.CHAPTERS["twelve"])))


def test_day_fifteens_visit_readout_is_reported(fifteen_counts: Counts, fifteen_marks: dict[str, str]):
    assert len(fifteen_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-fifteen", chapter_text("fifteen", fifteen_counts[1], fifteen_marks, cap_lines(fifteen_counts[0], verdicts.CHAPTERS["fifteen"])))


def test_day_sixteens_visit_readout_is_reported(sixteen_counts: Counts, sixteen_marks: dict[str, str]):
    assert len(sixteen_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-sixteen", chapter_text("sixteen", sixteen_counts[1], sixteen_marks, cap_lines(sixteen_counts[0], verdicts.CHAPTERS["sixteen"])))


def test_day_eighteens_visit_readout_is_reported(eighteen_counts: Counts, eighteen_marks: dict[str, str]):
    assert len(eighteen_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-eighteen", chapter_text("eighteen", eighteen_counts[1], eighteen_marks, cap_lines(eighteen_counts[0], verdicts.CHAPTERS["eighteen"])))


def test_day_nineteens_visit_readout_is_reported(nineteen_counts: Counts, nineteen_marks: dict[str, str]):
    assert len(nineteen_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-nineteen", chapter_text("nineteen", nineteen_counts[1], nineteen_marks, cap_lines(nineteen_counts[0], verdicts.CHAPTERS["nineteen"])))


def test_day_twenty_twos_visit_readout_is_reported(twentytwo_counts: Counts, twentytwo_marks: dict[str, str]):
    assert len(twentytwo_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-twentytwo", chapter_text("twentytwo", twentytwo_counts[1], twentytwo_marks,
                                               cap_lines(twentytwo_counts[0], verdicts.CHAPTERS["twentytwo"])))


def test_day_twenty_threes_visit_readout_is_reported(twentythree_counts: Counts, twentythree_marks: dict[str, str]):
    assert len(twentythree_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-twentythree", chapter_text("twentythree", twentythree_counts[1], twentythree_marks,
                                                 cap_lines(twentythree_counts[0], verdicts.CHAPTERS["twentythree"])))


def test_day_twenty_fives_visit_readout_is_reported(twentyfive_counts: Counts, twentyfive_marks: dict[str, str]):
    assert len(twentyfive_counts[1]) >= 3, "the chapter's visits were counted"
    rs.check("weektwo-twentyfive", chapter_text("twentyfive", twentyfive_counts[1], twentyfive_marks,
                                                cap_lines(twentyfive_counts[0], verdicts.CHAPTERS["twentyfive"])))
