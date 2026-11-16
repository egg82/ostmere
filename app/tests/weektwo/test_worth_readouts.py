"""The worth readout (tests/worth/readout.py) and its route with its own rules (tests/worth/stints.py) reported against
their committed text (tests/readout_snapshot.py), read here because this job has day fifteen's plays. A change is reported,
never failed; commit it with `python -m tests.readout_snapshot --write worth`."""
import pytest

from tests import readout_snapshot as rs
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.weektwo.routes import fifteen
from tests.worth import readout, stints

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_the_committed_readouts_are_the_ones_worth_writes():
    assert rs.stray("worth", readout.NAMES) == ([], [])


def test_the_worth_readout_is_reported(fifteen_worth: str):
    rs.check(f"worth-{readout.ROUTE}", fifteen_worth)


def test_the_route_with_its_own_rules_is_reported():
    rs.check(f"worth-stints-{readout.ROUTE}", stints.text(fifteen(readout.ROUTE), readout.ROUTE))
