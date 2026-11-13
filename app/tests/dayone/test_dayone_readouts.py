"""Day one's readouts (report.py) reported against their committed text (tests/readout_snapshot.py): each push route, the
human-paced player's day and the absence ladder, rendered from the session's shared plays. A change is reported, never failed;
commit it with `python -m tests.readout_snapshot --write dayone`. The rebase readout is compared last in
test_dayone_rebase.py, where its loads are made."""
import pytest

from tests import readout_snapshot as rs
from tests.dayone import absence, report
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.human import HumanPlayer
from tests.dayone.human_flags import Session
from tests.dayone.routes import PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_the_report_writes():
    assert rs.stray("dayone", report.NAMES) == ([], [])


@pytest.mark.parametrize("day_readout", [(name, 0) for name in PUSH_ROUTES], indirect=True, ids=lambda r: r[0])
def test_a_route_readout_is_reported(day_readout: tuple[str, str]):
    name, text = day_readout
    rs.check(f"dayone-{name}", text)


def test_the_human_paced_readout_is_reported(human_run: tuple[HumanPlayer, list[Session]]):
    rs.check("dayone-human", report.human_text(*human_run))


def test_the_absence_readout_is_reported(absence_run: list[absence.Point]):
    rs.check("dayone-absence", report.absence_text(absence_run))
