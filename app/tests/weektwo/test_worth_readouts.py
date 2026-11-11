"""The worth readout (tests/worth/readout.py) against its approved text (tests/readout_snapshot.py), read here because
this job has day fifteen's plays. A change fails until it is approved with `python -m tests.readout_snapshot --write
worth`."""
import pytest

from tests import readout_snapshot as rs
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.worth import readout

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_worth_writes():
    assert rs.stray("worth", readout.NAMES) == ([], [])


def test_the_worth_readout_is_approved(fifteen_worth: str):
    rs.check(f"worth-{readout.ROUTE}", fifteen_worth)
