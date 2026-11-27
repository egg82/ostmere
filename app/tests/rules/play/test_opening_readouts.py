"""The opening's readout (report.py) reported against its committed text (tests/readout_snapshot.py): a change in how the opening
moves is reported by the test and fails its job after the upload; commit it with `python -m tests.readout_snapshot --write opening`."""
import pytest

from tests import readout_snapshot as rs
from tests.rules.play import report
from tests.rules.play.afterend import AfterEnd, AfterEndPlayer

pytestmark = pytest.mark.playthrough


def test_the_committed_readouts_are_the_ones_the_report_writes():
    assert rs.stray("opening", report.NAMES) == ([], [])


@pytest.mark.parametrize("an_after_end", [("by_hand", 0)], indirect=True)
def test_the_opening_readout_is_reported(typical: AfterEndPlayer, by_hand: AfterEndPlayer, fireback_first: AfterEndPlayer,
                                         an_after_end: tuple[AfterEnd, AfterEndPlayer]):
    routes = {"typical": typical, "by_hand": by_hand, "fireback_first": fireback_first}
    rs.check("opening", report.render(routes, an_after_end[0]))
