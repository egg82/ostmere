"""Day two's routes use the sink policies (dayone/sinks.py): a route that queues comforts puts the comfort in the queue
When ready the visit it opens in (V1), never while A16 or a build waits, and builds it without a hand tap; the same
route with no sink knobs taps it by hand.
The second is the planted control that the check can tell."""
from collections.abc import Sequence

import pytest

from ashfall_app.engine import CardId, SetQueue, TapCard, Verb
from ashfall_app.engine.work import completions
from tests.daytwo import content as c
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import play2
from tests.dayone.sinks import SinkKnobs

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
BED = CardId(c.BED)
Log = Sequence[tuple[int, str, Verb]]


def queued(log: Log) -> bool:
    return any(isinstance(v, SetQueue) and any(e.verb == TapCard(BED) for e in v.entries) for _, _, v in log)


def tapped(log: Log) -> bool:
    return any(v == TapCard(BED) for _, _, v in log)


def built(p: DayTwoPlayer) -> int:
    return completions(p.save, p.rules, BED)


@pytest.fixture(scope="module")
def by_hand() -> DayTwoPlayer:
    return play2("typical", 0, SinkKnobs())


typical = pytest.mark.parametrize("day2_route", [("typical", 0)], indirect=True)


@typical
def test_the_typical_route_queues_the_comfort_and_builds_it_without_a_tap(day2_route: DayTwoPlayer):
    p = day2_route
    assert queued(p.decisions) and not tapped(p.decisions) and built(p) >= 1


@typical
def test_the_comfort_is_queued_in_v1_and_never_while_b4s_way_waits(day2_route: DayTwoPlayer):
    """First queued before J2 puts A16 on the cards (V1), and never again until both builds are built."""
    p = day2_route
    times = [t for t, _, v in p.decisions if isinstance(v, SetQueue) and any(e.verb == TapCard(BED) for e in v.entries)]
    built = max(p.landed_at[b] for b in ("A17", "A18"))
    assert times and times[0] < p.landed_at["J2"]
    assert all(t < p.landed_at["J2"] or t >= built for t in times), times


def test_the_same_route_with_no_sink_knobs_taps_it_instead(by_hand: DayTwoPlayer):
    """The planted control: queued() is false and tapped() true on a route that does not queue."""
    assert not queued(by_hand.decisions) and tapped(by_hand.decisions)
