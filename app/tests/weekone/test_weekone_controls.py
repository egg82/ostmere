"""The week's counters read what they claim (docs/design/days-four-to-seven-plan.md, item 1): a visit with nothing
affordable at a full store reads zero spend, a planted dead day is found among the real ones, and blocking every card
leaves nothing to spend on."""
from collections import Counter
from dataclasses import replace

import pytest

from ashfall_app.engine import AtLeast, Rules, Save, StoreId, StoreValue, view
from tests.daythree import counters
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone import absence, daily

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def test_a_visit_with_nothing_affordable_at_a_full_store_reads_zero_spend():
    assert counters.line(counters.Counts("V1", 0, 0, 1)) == "spend  0  decide  1"
    assert counters.line(counters.Counts("V1", 0, 1, 1)) == "spend  1  decide  1"


@pytest.mark.parametrize("week_days", ["typical"], indirect=True)
def test_a_dead_day_is_found_among_real_ones(week_days: tuple[DayTwoPlayer, list[Counter[str]]]):
    """A window whose two ends are one state counts nothing, and one with only lines counts as dead too; swapped into
    the real days each is the one found."""
    p, days = week_days
    assert len(days) >= 6
    real = set(daily.empty_days(days))
    v = view(p.history[-1][0], p.rules)
    dead, _ = absence.counts(p.rules, v, v, ())
    assert sum(dead.values()) == 0
    lines_only = Counter(line=days[0]["line"])
    assert lines_only["line"] > 0
    assert not {3, 5} & real, "the plants land on days the route keeps alive"
    assert set(daily.empty_days([*days[:2], dead, *days[3:]])) == real | {3}
    assert set(daily.empty_days([*days[:4], lines_only, *days[5:]])) == real | {5}


@pytest.fixture(scope="module")
def returns(week_spends: tuple[DayTwoPlayer, list[int]]) -> tuple[Rules, list[Save]]:
    """The visits' exits that find something to spend, and the rules with every card blocked, read in setup (a view of
    each exit is the cost)."""
    p, _ = week_spends
    returned = [v.exit for v in p.visits if v.exit is not None and counters.spendable(v.exit, p.rules)]
    never = AtLeast(StoreValue(StoreId("damp_wood")), 10**12, 10**12)
    return replace(p.rules, cards=tuple(replace(c, requires=(*c.requires, never)) for c in p.rules.cards)), returned


@pytest.mark.parametrize("week_spends", ["four"], indirect=True)
def test_a_real_return_has_something_to_spend(week_spends: tuple[DayTwoPlayer, list[int]], returns: tuple[Rules, list[Save]]):
    assert any(week_spends[1])
    assert returns[1], "some return finds a full store with a card to spend it on"


STUCK_PARTS = 3
"""Each exit is read under the blocked rules (a view each), so they are judged in thirds, each under the ceiling."""


@pytest.mark.parametrize("part", range(STUCK_PARTS))
@pytest.mark.parametrize("week_spends", ["four"], indirect=True)
def test_blocking_every_card_leaves_nothing_to_spend(part: int, returns: tuple[Rules, list[Save]]):
    stuck, returned = returns
    assert all(counters.spendable(s, stuck) == () for s in returned[part::STUCK_PARTS])
