"""The first helper's join to the town's mix (engine DESIGN.txt, "THE TOWN'S MIX"), blind to the chapter's trigger: when
the bay is done, and the trigger that brings the second helper to `town:camp` lands, the first helper joins it at the
same instant on the card her always rule tapped, at the whole share, changing nothing she does and not moving the
arrivals tally. Read off the typical route's saves either side of the second the bay reaches 1."""
from dataclasses import dataclass

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, CardId, CardShare, LaneId, Order, Rules, Save, StoreId, TapCard, Unlock,
    UnlockKind, advance, view,
)
from ashfall_app.engine.rates import store_value
from ashfall_app.engine.segments import value_at
from tests.daytwo.player import DayTwoPlayer

N1 = LaneId("n1")
BAY, ARRIVALS = StoreId("bay"), StoreId("arrivals")
TOWN = "town:camp"
WINDOW_S = 60

pytestmark = [pytest.mark.playthrough, pytest.mark.parametrize("day3_route", ["typical"], indirect=True)]


@dataclass(frozen=True)
class Instant:
    rules: Rules
    base: Save
    """The route's last save with the bay short."""
    before: Save
    """`base` at the last second the bay is short."""
    after: Save
    """`base` at the second the bay is done."""
    card: CardId
    """The card her always rule taps in `before`."""


def n1_cards(rules: Rules) -> frozenset[CardId]:
    return frozenset(c.id for c in rules.cards if c.lane == N1)


def always_cards(save: Save, rules: Rules) -> list[CardId]:
    """The cards of her lane that an always rule (AfterTime 0) taps in `save`."""
    return [o.then.card for o in save.orders
            if isinstance(o.then, TapCard) and o.when == AfterTime(0) and o.then.card in n1_cards(rules)]


def bay_done(save: Save, rules: Rules, t: int) -> bool:
    return store_value(advance(save, rules, t), BAY) >= Q


@pytest.fixture(scope="module")
def instant(day3_route: tuple[str, DayTwoPlayer]) -> Instant:
    """The last played save with the bay short, run on to the second its landing falls on, by bisection."""
    p = day3_route[1]
    saves = [s for s, _ in p.history]
    first = next(i for i, s in enumerate(saves) if store_value(s, BAY) >= Q)
    base, lo, hi = saves[first - 1], saves[first - 1].time, saves[first].time
    assert not bay_done(base, p.rules, lo) and bay_done(base, p.rules, hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if bay_done(base, p.rules, mid) else (mid, hi)
    before = advance(base, p.rules, lo)
    (card,) = always_cards(before, p.rules)
    return Instant(p.rules, base, before, advance(base, p.rules, hi), card)


def n1_shares(save: Save, rules: Rules) -> list[CardShare]:
    (mix,) = [m for m in save.mixes if str(m.id) == TOWN]
    return [c for c in mix.components if isinstance(c, CardShare) and c.card in n1_cards(rules)]


def joined(save: Save) -> bool:
    return Unlock(UnlockKind.JOINED, "n1") in save.unlocked


def test_the_bay_done_joins_her_to_the_town_on_her_always_card_at_the_whole_share(instant: Instant):
    r, before, after = instant.rules, instant.before, instant.after
    assert not joined(before) and not any(str(m.id) == TOWN and n1_shares(before, r) for m in before.mixes)
    assert joined(after)
    assert n1_shares(after, r) == [CardShare(instant.card, BP)]
    assert always_cards(after, r) == []
    v = view(after, r)
    assert v.running_town_mix is not None and str(v.running_town_mix) == TOWN
    (card_view,) = [c for c in v.cards if c.card == instant.card]
    assert card_view.share_bp == BP


def test_her_other_rules_stay_when_her_always_rule_goes(instant: Instant):
    r = instant.rules

    def mine(s: Save) -> list[Order]:
        return [o for o in s.orders if isinstance(o.then, TapCard) and o.then.card in n1_cards(r)]

    gone = Order(AfterTime(0), TapCard(instant.card))
    assert gone in mine(instant.before) and len(mine(instant.before)) > 1
    assert mine(instant.after) == [o for o in mine(instant.before) if o != gone]


def lane_card(save: Save, rules: Rules) -> CardId | None:
    (bar,) = [b for b in view(save, rules).lanes if b.lane == N1]
    return bar.card


def work(save: Save, rules: Rules, card: CardId) -> int:
    (cv,) = [c for c in view(save, rules).cards if c.card == card]
    return value_at(cv.bar, save.time)


def test_she_runs_the_same_card_at_the_same_rate_across_the_join(instant: Instant):
    """Her card's cumulative work in the window before the join and in the window after it advance alike."""
    r, card = instant.rules, instant.card
    earlier = advance(instant.base, r, instant.before.time - WINDOW_S)
    later = advance(instant.before, r, instant.after.time + WINDOW_S)
    assert [lane_card(s, r) for s in (earlier, instant.before, instant.after, later)] == [card] * 4
    gained_before = work(instant.before, r, card) - work(earlier, r, card)
    gained_after = work(later, r, card) - work(instant.after, r, card)
    assert gained_before > 0
    assert gained_after == gained_before


def test_her_join_does_not_move_the_arrivals_tally(instant: Instant):
    assert store_value(instant.after, ARRIVALS) - store_value(instant.before, ARRIVALS) == Q
