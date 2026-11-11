"""Week one's route readouts (report.py) against their approved text (tests/readout_snapshot.py): when each route's
beats land beside their target days, and each calendar day's arrivals. Each chapter's visit readout is compared in
test_weekone_routes.py, after the parts its counts reuse. A change fails until it is approved with
`python -m tests.readout_snapshot --write weekone`."""
from collections import Counter

import pytest

from tests import readout_snapshot as rs
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone import report

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_the_report_writes():
    assert rs.stray("weekone", report.NAMES) == ([], [])


@pytest.mark.parametrize("week_days, name", [(r, r) for r in report.DAY_ROUTES], indirect=["week_days"])
def test_a_route_readout_is_approved(week_days: tuple[DayTwoPlayer, list[Counter[str]]], name: str):
    rs.check(f"weekone-{name}", report.route_text(name, *week_days))
