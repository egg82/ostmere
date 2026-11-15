"""The makers readout (tests/makers/readout.py) reported against its committed text (tests/readout_snapshot.py), one per
route through day twelve, read here because this job has week two's plays. A change is reported, never failed; commit it
with `python -m tests.readout_snapshot --write makers`."""
import pytest

from tests import readout_snapshot as rs
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.makers import readout
from tests.weektwo.routes import TWELVE_PUSH_ROUTES, twelve

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S), pytest.mark.weektwo_shard("makers")]


def test_the_committed_readouts_are_the_ones_the_makers_write():
    assert rs.stray("makers", readout.NAMES) == ([], [])


@pytest.mark.parametrize("name", TWELVE_PUSH_ROUTES)
def test_a_route_makers_readout_is_reported(name: str):
    text = readout.route_text(name, twelve(name))
    assert "smoked" in text, "the readout reads no smoked store"
    rs.check(f"makers-{name}", text)
