"""Day one's invariant checks on every route a run plays (routes.py; verdicts.py): the story's order, a tool user's B3
lag behind the babysitter's (bands.py), every rate-raising step queueable before it is ready, and every drawn time
coming true. The checks run in the fixture's setup. The route's rhythm is its readout (report.py)."""
import pytest

from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.player import DayOnePlayer
from tests.dayone.routes import plays
from tests.dayone.verdicts import CHECKS, verdicts

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Verdicts = tuple[str, int, dict[str, list[str]]]


@pytest.mark.parametrize("check", sorted(CHECKS))
@pytest.mark.parametrize("day_verdicts", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_a_route_meets_the_bar(day_verdicts: Verdicts, check: str):
    _, _, found = day_verdicts
    assert found[check] == []


@pytest.mark.xfail(strict=True, reason="a route that never sees B3 raises KeyError in the B3-relative checks")
def test_a_route_that_never_sees_b3_still_yields_verdicts():
    assert set(verdicts("lazy", 0)) == set(CHECKS)


@pytest.mark.parametrize("day_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_what_lands_away_is_seen_on_return(day_route: DayOnePlayer):
    """Every story id is seen no sooner than it lands, and inside a visit: one that landed while the player was away
    is seen at the return (a planned moment plays in full then), never at its own time."""
    p = day_route
    for beat, t in p.seen_at.items():
        assert t >= p.landed_at[beat]
        assert any(v.start <= t <= v.end for v in p.visits) or t <= (p.end_at or 0), (beat, t)
    away = [b for b, t in p.landed_at.items() if not any(v.start <= t <= v.end for v in p.visits)]
    assert all(p.seen_at[b] in {v.start for v in p.visits} for b in away if b in p.seen_at)
