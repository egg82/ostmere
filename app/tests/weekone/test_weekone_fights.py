"""Combat's checks over week one (docs/design/combat-plan.md, items 9 and 10). Item 9 (engine invariant 81): a route's
decisions end the week with the same saves, stores and fight tallies whenever its player looks, and the route that builds
the week's gear loses fewer hunts than the same route that never does. Item 10 (dayone/fightchecks.py) over the week's
plays from B7: every store a standing fight takes to nothing has a card in reach that puts it up, on each route; and the
2 AM replay across days four to six has the fights fighting in both plays. Each check is judged on a non-empty set."""
import pytest

from ashfall_app.engine import Save, view
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.dayone import fightchecks
from tests.dayone.parity import Measured
from tests.weekone import fights
from tests.weekone.routes import PUSH_ROUTES, week1

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Run = tuple[fights.Week, Save, Save]
Judged = tuple[int, list[str]]


@pytest.mark.parametrize("week_timing", ["sharp", "lazy", "whenever"], indirect=True)
def test_the_same_decisions_end_the_week_the_same_whatever_the_visit_schedule(week_timing: Run):
    w, alone, sliced = week_timing
    assert fights.hunts(alone, w.rules)[0] > 0, "the hunt was fought"
    assert fights.differing(alone, sliced) == [], "stores, tallies and the rest are those of the unsliced run"


def test_a_route_that_builds_the_weeks_gear_loses_fewer_hunts(week_prepared: Run):
    w, prepared, bare = week_prepared
    (fought, lost), (fought_bare, lost_bare) = fights.hunts(prepared, w.rules), fights.hunts(bare, w.rules)
    assert min(fought, fought_bare) >= 10, f"enough hunts fought to compare: {fought} and {fought_bare}"
    num, den = fights.LOSS_RATIO
    assert lost * fought_bare * den <= num * lost_bare * fought, (
        f"hunt lost {lost} of {fought} with the gear, {lost_bare} of {fought_bare} without it")


def test_the_bare_route_never_builds_the_gear(week_prepared: Run):
    w, _, _ = week_prepared
    assert fights.built_gear(w.log) and not fights.built_gear(fights.without_gear(w.log))


def after_b7(name: str) -> list[Save]:
    p = week1(name)
    return [s for s, _ in p.history if s.time >= p.landed_at["B7"]]


@pytest.fixture(scope="module")
def threats() -> dict[str, Judged]:
    out: dict[str, Judged] = {}
    for name in PUSH_ROUTES:
        found = [fightchecks.threat_stores_unreached(s, week1(name).rules) for s in after_b7(name)]
        out[name] = (sum(j for j, _ in found), sorted({x for _, xs in found for x in xs}))
    return out


@pytest.mark.parametrize("route", PUSH_ROUTES)
def test_a_store_a_threat_took_to_nothing_has_a_card_in_reach_that_puts_it_up(threats: dict[str, Judged], route: str):
    judged, problems = threats[route]
    assert judged > 0, f"{route} had a store taken to nothing to judge"
    assert problems == []


def test_the_week_replay_runs_the_fights_in_both_plays(two_am_week_run: tuple[Measured, Measured]):
    """The 2 AM replay across days four to six (weekone/verdicts.two_am_week) has the hunt and both standing fights
    fighting in the whenever player's play and the babysitter's, so its comparison (held below) reads their tallies."""
    rules = week1("whenever").rules
    for m in two_am_week_run:
        fought = {str(f.runner): f.fought for f in view(m.save, rules).fights}
        assert set(fought) >= {"hunt_wolf", "rats", "crows"} and all(fought[k] > 0 for k in ("hunt_wolf", "rats", "crows"))
