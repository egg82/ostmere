"""The counters read a real played route (daythree/visits.py): the typical day-two play, as visits and steps."""
import pytest

from ashfall_app.engine import AnswerOffer
from tests.daythree import counters, visits
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import day2

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def typical() -> DayTwoPlayer:
    return day2("typical")


@pytest.fixture(scope="module")
def steps(typical: DayTwoPlayer) -> list[counters.Step]:
    return visits.steps_of(typical)


@pytest.fixture(scope="module")
def seen(typical: DayTwoPlayer) -> list[tuple[counters.Visit, counters.Counts]]:
    """Each visit with its counts, counted once: a mix or queue step looks a day ahead."""
    return [(v, counters.count(v, typical.rules)) for v in visits.visits_of(typical)]


def test_a_visit_per_visit_and_each_returns_at_its_start(typical: DayTwoPlayer, seen: list[tuple[counters.Visit, counters.Counts]]):
    assert [v.returned.time for v, _ in seen] == [v.start for v in typical.visits] and len(seen) > 3
    assert [v.gap for v, _ in seen] == [v.gap for v in typical.visits]


def test_every_decision_after_the_opening_is_in_a_visit(steps: list[counters.Step], seen: list[tuple[counters.Visit, counters.Counts]]):
    assert sum(len(v.steps) for v, _ in seen) == len(steps) > 0


def test_the_visit_that_answers_the_offer_decides(seen: list[tuple[counters.Visit, counters.Counts]]):
    answered = [c for v, c in seen if any(isinstance(s.verb, AnswerOffer) for s in v.steps)]
    assert answered and all(c.decide >= 1 for c in answered)


def test_a_visit_with_its_steps_taken_out_decides_nothing(typical: DayTwoPlayer, seen: list[tuple[counters.Visit, counters.Counts]]):
    """The planted control: the same returns with no steps."""
    bare = [counters.count(counters.Visit(v.label, v.gap, v.returned, ()), typical.rules) for v, _ in seen]
    assert all(c.decide == 0 for c in bare) and any(c.spend > 0 for c in bare)
    assert any(c.decide > 0 for _, c in seen)
