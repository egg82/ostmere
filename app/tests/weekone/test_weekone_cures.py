"""The cures gate (dayone/cures.py) over the week's plays, from B5 (combat-plan.md, item 10): every chip shown has a cure on
offer, the lost fight's chip among those the gate samples (the babysitter's play shows it)."""
import pytest

from ashfall_app.engine import Save
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone import cures
from tests.weekone.routes import week1

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
CHIP = "hurt"
PUSH = ("typical", "babysitter")


@pytest.fixture(scope="module")
def uncured() -> dict[str, list[str]]:
    return {n: cures.uncured(p, p.landed_at["B5"]) for n, p in ((n, week1(n)) for n in PUSH)}


@pytest.fixture(scope="module")
def hurt_shown() -> tuple[DayTwoPlayer, Save]:
    p = week1("babysitter")
    return p, next(s for s, v in p.history if CHIP in [str(c) for c in v.chips])


@pytest.mark.parametrize("route", PUSH)
def test_every_chip_shown_in_the_week_has_a_cure(uncured: dict[str, list[str]], route: str):
    assert uncured[route] == []


def test_the_lost_fights_chip_is_among_the_samples_checked(hurt_shown: tuple[DayTwoPlayer, Save]):
    p, _ = hurt_shown
    assert CHIP in {chip for _, _, chip in cures.checked(p)}
