"""The ladder readout (tests/ladder/readout.py) against its approved text (tests/readout_snapshot.py), one per route
through day twelve, read here because this job has week two's plays. A change fails until it is approved with
`python -m tests.readout_snapshot --write ladder`."""
import pytest

from tests import readout_snapshot as rs
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.ladder import readout
from tests.weektwo.routes import TWELVE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_the_ladder_writes():
    assert rs.stray("ladder", readout.NAMES) == ([], [])


@pytest.mark.parametrize("twelve_ladder", TWELVE_PUSH_ROUTES, indirect=True)
def test_a_route_ladder_readout_is_approved(twelve_ladder: tuple[str, str]):
    name, text = twelve_ladder
    rs.check(f"ladder-{name}", text)
