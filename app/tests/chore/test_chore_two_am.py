"""The 2 AM test on a season's chore with no order card (week-four-plan item 4, dayone/parity.py), on the fixture chapter:
the chip first shows mid-visit, between the whenever player's two glances, and again each night after. The babysitter,
given the whenever player's reveals and rule, washes by hand the second the chip shows unless that player answered it
later in the same visit; the whenever player's rule, written at its next glance, then covers every night's showing, so
the two end level. A planted policy that writes the rule only when the player is there at the instant the chip shows
never writes it, and the babysitter ends ahead."""
import pytest

from ashfall_app.engine import Order, Rules, Save, SetOrders, TapCard, View, new_save
from tests.chore.chapter import HELPER_WASH, HOUR, SHOWS_AT, WASH, WHEN, rules
from tests.chore.play import Played, play
from tests.daythree import moves
from tests.daythree.chapter import Later
from tests.dayone.player.policy import Move
from tests.dayone.pacing.parity import Measured, Present, babysat, compare, replay
from tests.daytwo.routes import ROUTES

VISITS = ((10 * HOUR, 14 * HOUR), (34 * HOUR, 38 * HOUR))
"""The chip shows at 12 h, inside the first visit and at neither glance."""
UNTIL = 60 * HOUR
BOOSTS = (str(WASH),)


def pair(p: Played) -> tuple[Measured, Measured]:
    r = rules()
    w = replay(r, new_save(r), p.log, UNTIL, False, boosts=BOOSTS)
    b = replay(r, new_save(r), babysat(p.log), UNTIL, True, Present.of(VISITS, p.log), boosts=BOOSTS)
    return w, b


def rules_set(p: Played) -> list[tuple[int, tuple[Order, ...]]]:
    return [(t, v.orders) for t, v in p.log if isinstance(v, SetOrders)]


def test_the_rule_is_written_at_the_first_glance_after_the_chip_shows():
    p = play(VISITS, UNTIL, WASH, True)
    assert rules_set(p) == [(14 * HOUR, (Order(WHEN, TapCard(WASH)),))]


def test_the_babysitter_ends_level_with_the_whenever_players_chip_rule():
    w, b = pair(play(VISITS, UNTIL, WASH, True))
    assert w.landed.get("wash#3") is not None, "the rule washed each night the chip showed"
    assert compare(w, b) == []


def test_a_policy_writing_the_rule_only_when_present_at_the_instant_the_chip_shows_turns_it_red(
        monkeypatch: pytest.MonkeyPatch):
    real = moves.chip_rule
    def at_the_instant(v: View, save: Save, r: Rules, later: Later) -> Move | None:
        return real(v, save, r, later) if v.time == SHOWS_AT * HOUR else None
    monkeypatch.setattr(moves, "chip_rule", at_the_instant)
    p = play(VISITS, UNTIL, WASH, True)
    assert rules_set(p) == []
    w, b = pair(p)
    assert "wash#1" in b.landed and "wash#1" not in w.landed
    assert compare(w, b)


def test_the_cure_is_the_one_on_the_routes_lane():
    p = play(VISITS, UNTIL, HELPER_WASH, True)
    assert rules_set(p) == [(14 * HOUR, (Order(WHEN, TapCard(HELPER_WASH)),))]


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_every_route_that_takes_rules_writes_it_and_lazy_writes_none(name: str):
    p = play(VISITS, UNTIL, WASH, ROUTES[name].her_rule)
    assert bool(rules_set(p)) == ROUTES[name].her_rule
