"""Day three's readouts (report.py) reported against their committed text (tests/readout_snapshot.py): the typical route's visits
and the beats it and the sharp route reach, rendered from the session's shared plays. A change is reported, never failed;
commit it with `python -m tests.readout_snapshot --write daythree`."""
import pytest

from tests import readout_snapshot as rs
from tests.daythree import report
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_the_report_writes():
    assert rs.stray("daythree", report.NAMES) == ([], [])


def test_the_typical_readout_is_reported(day3_readout: str):
    rs.check("daythree-typical", day3_readout)


@pytest.mark.parametrize("day3_route", ["sharp"], indirect=True)
def test_the_sharp_readout_is_reported(day3_route: tuple[str, DayTwoPlayer]):
    rs.check("daythree-sharp", report.sharp_text(day3_route[1]))
