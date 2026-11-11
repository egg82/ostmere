"""Progress is stated, never hinted (docs/decisions.md): on each push route's play from the start through day fifteen,
the edge of written content, every gate met was stated on screen at the moment before it was met (tests/goals/walk.py
says what stated means for each kind of gate). Walked in a fixture's setup; the tests read the result. Trigger ids only
(CLAUDE.md, "Never spoil the owner")."""
from dataclasses import replace

import pytest

from ashfall_app.engine import AtLeast
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.goals.walk import Met, misses, served_nothing, taps, unjudged, walk
from tests.weektwo.routes import FIFTEEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture
def walked(fifteen_route: tuple[str, DayTwoPlayer]) -> tuple[list[Met], list[Met]]:
    """The route's gates met, as the page states them, and as a page that states no goal would (the control)."""
    _, p = fifteen_route
    tapped = taps(p.decisions, p.undecided)
    return walk(p.history, p.rules, tapped=tapped), walk(p.history, p.rules, served_nothing, tapped)


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_every_gate_met_was_stated_before_it(walked: tuple[list[Met], list[Met]]):
    met, _ = walked
    assert sum(m.stated is not None for m in met) > 100, "judged too few gates: the walk is blind"
    assert met[0].at < 3600, "the walk starts after the opening"
    assert misses(met) == []


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_every_gate_met_was_judged(walked: tuple[list[Met], list[Met]]):
    """A gate with no open step starting it at the moment before (tests/goals/walk.py) is a gap in what the page can
    state, held here by id."""
    met, _ = walked
    assert unjudged(met) == set()


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_the_walk_fails_a_page_that_states_no_goal(walked: tuple[list[Met], list[Met]]):
    """The control: with View.goals empty, the clocks, stores and counts met go unstated, the opening's included, and so
    do those judged by the step that starts them; only a gate that came of the player's move at that moment holds."""
    _, bare = walked
    missed = misses(bare)
    assert len(missed) > 20 and any(float(m.split(" at ")[1].rstrip("h")) < 1 for m in missed)
    assert [m.trigger for m in bare if m.stated and m.before != m.at and m.tapped is None] == []
    assert unjudged(bare) == set()


@pytest.mark.parametrize("fifteen_route", ["sharp"], indirect=True)
def test_a_beat_lands_with_a_tapped_card_only_when_it_waits_on_nothing_else(fifteen_route: tuple[str, DayTwoPlayer],
                                                                             walked: tuple[list[Met], list[Met]]):
    """Sharp meets a beat whose last unmet condition is an unlock a tapped card's completion gives. Walked over its
    two moments it is stated with that card; without the player's taps, or with its own condition one unit short of
    met at the moment before (its clock not yet full), it is not."""
    _, p = fifteen_route
    met, _ = walked
    landed = [m for m in met if m.tapped is not None]
    assert landed, "no beat landed with a tapped card: the control reads nothing"
    m = landed[0]
    i = next(i for i, (s, _) in enumerate(p.history) if s.time == m.before and p.history[i + 1][0].time == m.at)
    pair, tapped = p.history[i:i + 2], taps(p.decisions, p.undecided)
    k = next(k for k, t in enumerate(p.rules.triggers) if t.id == m.trigger)
    when = p.rules.triggers[k].when
    assert isinstance(when, AtLeast)
    short = replace(p.rules.triggers[k], when=replace(when, value=when.value + 1, release=when.value + 1))
    unmet = replace(p.rules, triggers=(*p.rules.triggers[:k], short, *p.rules.triggers[k + 1:]))
    assert _beat(walk(pair, p.rules, tapped=tapped), m.trigger) == m
    assert _beat(walk(pair, p.rules), m.trigger).stated is not True
    assert _beat(walk(pair, unmet, tapped=tapped), m.trigger).stated is not True


def _beat(found: list[Met], trigger: str) -> Met:
    return next(x for x in found if x.trigger == trigger)
