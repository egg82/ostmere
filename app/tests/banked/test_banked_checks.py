"""The day-one checks past the sinks (dayone/sinkchecks.py) on the fixture chapter: a trip tapped lands when drawn, a
trip paused dry has its supply's maker in reach, and a trip and a comfort showing every need met start when tapped.
Each is judged on a non-empty set and goes red on a planted fixture that breaks it."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, AfterTime, CardId, CardShare, Flow, InvalidVerbError, LaneDef, LaneId, Mix, MixId, RunKind, Rules, Save, SaveMix,
    StoreDef, SwitchMix, TapCard, Verb, advance, decide, new_save, view,
)
from tests.banked.chapter import CAP, COMFORT, GATHER, TRIP, WOOD, rules
from tests.dayone import sinkchecks
from tests.dayone.sinkchecks import dry_unreached, landing_kept, needs_met_blocked, tap_fails, tapped_landings

H = 3600


def mixed(r: Rules, card: CardId, at: int) -> Save:
    """A new save at `at` with `card` alone in the active mix."""
    mix = Mix(MixId("only"), (CardShare(card, BP),))
    s = advance(new_save(r), r, at)
    return decide(decide(s, r, at, SaveMix(mix)), r, at, SwitchMix(mix.id))


def gathered(r: Rules, until: int = 2 * H) -> Save:
    return advance(mixed(r, GATHER, 0), r, until)


def test_a_trip_and_a_comfort_showing_every_need_met_start_when_tapped():
    r = rules(trip_cost=1)
    s = gathered(r)
    checked, broken = needs_met_blocked([view(s, r)])
    assert checked >= 2 and broken == []
    assert {c.card for c in view(s, r).cards if c.blocker is None} >= {TRIP, COMFORT}
    assert tap_fails(s, r) == []


def test_a_trip_showing_ready_with_an_unlisted_requirement_is_caught():
    """The trip's inputs are in, yet a requires on the clock, which the panel does not list as a need, holds it: shown ready, blocked."""
    r = rules(trip_cost=1)
    held = tuple(replace(c, requires=(AfterTime(10 * H),)) if c.id == TRIP else c for c in r.cards)
    planted = replace(r, cards=held)
    checked, broken = needs_met_blocked([view(gathered(planted), planted)])
    assert checked >= 2 and broken and broken[0].startswith(str(TRIP))


def test_a_tap_that_starts_nothing_is_caught(monkeypatch: pytest.MonkeyPatch):
    r = rules(trip_cost=1)
    s = gathered(r)
    assert tap_fails(s, r) == []
    
    def refuse(save: Save, rules: Rules, t: int, verb: Verb) -> Save:
        return save

    monkeypatch.setattr(sinkchecks, "decide", refuse)
    assert any(f.startswith(str(TRIP)) for f in tap_fails(s, r)) and any(f.startswith(str(COMFORT)) for f in tap_fails(s, r))


def test_a_tap_landing_a_second_late_is_caught(monkeypatch: pytest.MonkeyPatch):
    r = rules(trip_cost=1)
    s = decide(gathered(r, H), r, H, TapCard(TRIP))
    assert tapped_landings(s, r) == []
    
    def late(save: Save, rules: Rules, t: int) -> Save:
        return advance(save, rules, t - 1)

    monkeypatch.setattr(sinkchecks, "advance", late)
    assert tapped_landings(s, r) == [f"{TRIP} drawn landing at t={2 * H}, not kept"]


def test_a_trip_tapped_lands_when_the_page_draws_it():
    r = rules(trip_cost=1)
    s = decide(gathered(r, H), r, H, TapCard(TRIP))
    card = next(c for c in view(s, r).cards if c.card == TRIP)
    assert card.completes_at is not None and card.completes_at > s.time, "the tap runs and draws its landing"
    assert tapped_landings(s, r) == []
    at = card.completes_at
    assert landing_kept(s, r, TRIP, at) and not landing_kept(s, r, TRIP, at - 1) and not landing_kept(s, r, TRIP, at + 1)


def dry(r: Rules) -> tuple[Save, Rules]:
    """The wood store half full and the trip alone in the mix, run on until the wood is gone and the trip paused."""
    stocked = replace(r, stores=(StoreDef(WOOD, CAP, CAP // 2), r.stores[1]))
    return advance(mixed(stocked, TRIP, H // 2), stocked, 8 * H), stocked


def paused(s: Save, r: Rules) -> list[RunKind | None]:
    return [c.run for c in view(s, r).cards if c.card == TRIP]


def test_a_trip_paused_dry_has_its_supply_maker_in_reach():
    s, r = dry(rules(trip_cost=1))
    assert paused(s, r) == [RunKind.PAUSED], "the trip is paused dry"
    assert dry_unreached(s, r) == []


def test_a_trip_paused_dry_whose_unlocked_maker_raises_nothing_is_caught():
    """The gatherer is unlocked, so the wood is not spent and the trip stays PAUSED, but its flow is nil: tapping it
    leaves the wood no higher."""
    r = rules(trip_cost=1)
    s, planted = dry(replace(r, cards=tuple(replace(c, makes=(Flow(WOOD, 0),)) if c.id == GATHER else c for c in r.cards)))
    assert paused(s, planted) == [RunKind.PAUSED]
    assert any(f.startswith(str(TRIP)) for f in dry_unreached(s, planted))


def test_a_trip_on_a_spent_store_is_not_judged_by_dry_unreached():
    """With no maker of the wood in play the store is spent and the trip is SPENT (DESIGN.txt, SPENT): its share goes to
    its mix by design, so a spent pool is not an unreached cure."""
    r = rules(trip_cost=1)
    s, planted = dry(replace(r, cards=tuple(replace(c, makes=()) if c.id == GATHER else c for c in r.cards)))
    assert paused(s, planted) == [RunKind.SPENT]
    assert dry_unreached(s, planted) == []


def test_a_card_on_a_ruled_lane_is_not_judged_by_a_tap_the_player_cannot_make():
    """A ruled lane's cards are set by rules, and the engine refuses the player's tap of one ("set by rules"), so
    showing one ready is not a tap that fails; the same card on a lane the player taps is still judged."""
    r = rules(trip_cost=1)
    lane = LaneId("p1")
    def on(ruled: bool) -> Rules:
        cards = tuple(replace(c, lane=lane) if c.id == COMFORT else c for c in r.cards)
        return replace(r, cards=cards, lanes=(*r.lanes, LaneDef(lane, ruled=ruled)))
    ruled = on(True)
    s = gathered(ruled)
    assert next(c for c in view(s, ruled).cards if c.card == COMFORT).blocker is None, "shown ready"
    with pytest.raises(InvalidVerbError):
        decide(s, ruled, s.time, TapCard(COMFORT))
    assert tap_fails(s, ruled) == []
    free = on(False)
    assert tap_fails(gathered(free), free) == []
