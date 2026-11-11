"""The checks past the sinks over played routes (daythree/plumbing.py): the push day-two routes judge a non-empty set
and break nothing, and the same wiring goes red on a fixture trip held back by a requirement the panel does not list."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, AfterTime, CardShare, Mix, MixId, SaveMix, SwitchMix, advance, decide, new_save,
)
from tests.banked.chapter import GATHER, TRIP, rules
from tests.daythree import plumbing
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import PUSH_ROUTES, day2

H = 3600


@pytest.fixture(scope="module", params=PUSH_ROUTES)
def found(request: pytest.FixtureRequest) -> plumbing.Plumbing:
    """A route played and checked in setup (a lazily played route would charge its play to the first test)."""
    p: DayTwoPlayer = day2(request.param)
    return plumbing.check(plumbing.sampled(p), p.rules)


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_a_day_two_route_judges_something_and_breaks_nothing(found: plumbing.Plumbing):
    assert found.judged > 0, "nothing was shown ready, tapped or paused: the checks are blind"
    assert found.problems == ()


def test_a_trip_shown_ready_but_held_by_an_unlisted_requirement_is_caught():
    """The planted route: the trip's inputs are in and a requirement on the clock, which the panel does not list as a
    need, holds it."""
    r = rules(trip_cost=1)
    planted = replace(r, cards=tuple(replace(c, requires=(AfterTime(10 * H),)) if c.id == TRIP else c for c in r.cards))
    mix = Mix(MixId("only"), (CardShare(GATHER, BP),))
    s = new_save(planted)
    for verb in (SaveMix(mix), SwitchMix(mix.id)):
        s = decide(s, planted, 0, verb)
    s = advance(s, planted, 2 * H)
    assert plumbing.check([s], r).problems == ()
    found = plumbing.check([s], planted)
    assert found.judged > 0 and any(x.startswith(str(TRIP)) for x in found.problems)
