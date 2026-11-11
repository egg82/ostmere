"""The hunt's drawn landing (dayone/fightchecks.fight_landings; combat-plan.md, item 10) over the typical route's saves
(daythree/plumbing.sampled): the mixed hunt claims no landing, and the same saves with the hunt tapped draw one that
comes true with nobody deciding. Each judged on a non-empty set."""
import pytest

from ashfall_app.engine import CardId, Rules, RunBy, Save, view
from tests.daythree import plumbing
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.dayone import cures, fightchecks
from tests.weekone.routes import week1

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
HUNT = CardId("hunt_wolf")
Judged = tuple[int, list[str]]


@pytest.fixture(scope="module")
def route() -> tuple[list[Save], Rules]:
    p = week1("typical")
    return plumbing.sampled(p), p.rules


@pytest.fixture(scope="module")
def mixed(route: tuple[list[Save], Rules]) -> list[Save]:
    """The route's saves that mix the hunt, found once in setup (a view of each save is the cost)."""
    saves, rules = route
    return [s for s in saves if run_by(s, rules) is RunBy.MIX]


@pytest.fixture(scope="module")
def tapped(mixed: list[Save], route: tuple[list[Save], Rules]) -> list[Save]:
    """The same saves with the hunt tapped, where the tap takes."""
    rules = route[1]
    return [t for s in mixed if run_by(t := cures.act(s, rules, HUNT), rules) is RunBy.TAP]


def judge(saves: list[Save], rules: Rules) -> Judged:
    found = [fightchecks.fight_landings(s, rules) for s in saves]
    return sum(j for j, _ in found), sorted({x for _, xs in found for x in xs})


def run_by(s: Save, rules: Rules) -> RunBy | None:
    return next((c.by for c in view(s, rules).cards if c.card == HUNT), None)


def test_the_mixed_hunt_claims_no_landing(mixed: list[Save], route: tuple[list[Save], Rules]):
    assert mixed, "the typical route mixes the hunt after B7"
    assert judge(mixed, route[1]) == (len(mixed), [])


PARTS = 3
"""Each tapped save's landing is checked by advancing to it, so the saves are judged in thirds, each under the ceiling."""


@pytest.mark.parametrize("part", range(PARTS))
def test_the_hunt_tapped_on_the_same_saves_lands_when_drawn(part: int, tapped: list[Save], route: tuple[list[Save], Rules]):
    assert tapped, "the hunt taps on the saves that mix it"
    share = tapped[part::PARTS]
    assert judge(share, route[1]) == (len(share), [])
