"""Day two's readouts (report.py) reported against their committed text (tests/readout_snapshot.py), one per push route, rendered
from the session's shared plays. A change is reported, never failed; commit it with
`python -m tests.readout_snapshot --write daytwo`."""
import pytest

from tests import readout_snapshot as rs
from tests.daytwo import report
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.routes import PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_the_report_writes():
    assert rs.stray("daytwo", report.NAMES) == ([], [])


@pytest.mark.parametrize("day2_readout", [(name, 0) for name in PUSH_ROUTES], indirect=True, ids=lambda r: r[0])
def test_a_route_readout_is_reported(day2_readout: tuple[str, str]):
    name, text = day2_readout
    rs.check(f"daytwo-{name}", text)
