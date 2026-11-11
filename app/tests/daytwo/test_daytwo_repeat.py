"""Her lane's task as a rate on day two's own content (engine DESIGN.txt, "REPEATING TAPS", invariants 75 and 76): from
a typical play's save at B3, hours with nobody deciding equal the per-landing engine's, with her always rule alone and
with a rule over it that switches her task, and her lane lands only where her task changes. The per-landing engine is
this one with retap.settle doing nothing, started from the same save with her tap bounded at its next completion, as
that engine stored it."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AtLeast, CardId, EventKind, LaneId, Order, Rules, Save, SetOrders, StoreId, StoreValue,
    TapCard, advance, decide, next_event,
)
from ashfall_app.engine import retap
from ashfall_app.engine.schedule import events
from tests.daytwo.player import DayTwoPlayer

HER = LaneId("n1")
ROOTS = StoreId("roots")
SAMPLE_S = 600


def bounded(save: Save, rules: Rules) -> Save:
    """The save as the per-landing engine stored it: every running tap limited at its next completion."""
    units = {c.id: c.work_s * BP for c in rules.cards}
    tapped = {ls.card for ls in save.lanes if ls.card is not None}
    cards = tuple(replace(cs, work=replace(cs.work, limit=(cs.work.start_value // units[cs.card] + 1) * units[cs.card]))
                  if cs.card in tapped and cs.work.limit is None and cs.work.rate > 0 else cs for cs in save.cards)
    return replace(save, cards=cards)


def her_card(save: Save) -> object:
    return next(ls.card for ls in save.lanes if ls.lane == HER)


def state(s: Save, r: Rules) -> tuple[object, ...]:
    work = {cs.card: cs.work.start_value for cs in s.cards}
    return (s.time, tuple(st.segment.start_value for st in s.stores), tuple(k.xp.start_value for k in s.skills),
            tuple(ls.card for ls in s.lanes), s.latches, s.orders, s.queue, s.fired, s.unlocked, s.pauses,
            tuple(work.get(c.id, 0) // (c.work_s * BP) for c in r.cards))


def walk(s: Save, r: Rules, span: int) -> tuple[list[tuple[object, ...]], int, int]:
    """One pass over the span, instant by instant: the state every SAMPLE_S, her lane's landings, and how many of them
    changed her task."""
    found: list[tuple[object, ...]] = []
    landed = switched = 0
    end, at = s.time + span, s.time
    while at <= end:
        e = next_event(s, r)
        step = end if e is None else min(e.time, end)
        while at <= step:
            found.append(state(advance(s, r, at), r))   # between instants: a shift, no event resolved
            at += SAMPLE_S
        if e is None or e.time > end:
            break
        lands = any(x.kind is EventKind.TAP_DONE and x.subject == HER for x in events(s, r) if x.time == e.time)
        before, s = her_card(s), advance(s, r, e.time)
        landed += int(lands)
        switched += int(lands and her_card(s) != before)
    return found, landed, switched


ROOTS_RULE_UP, ROOTS_RULE_DOWN = 20, 18
"""A rule over her always rule: gather once roots are 20 items above where they stood at B3, until they fall below 18
above. Her forage raises roots and the hands eat them, so the rule comes on and lets go
(again within the first hour and a half)."""


def no_settle(save: Save, rules: Rules, crossing: frozenset[LaneId]) -> tuple[Save, bool]:
    """retap.settle in the per-landing engine: no tap ever repeats."""
    return save, False


def compare(start: Save, r: Rules, span: int, monkeypatch: pytest.MonkeyPatch) -> tuple[int, int]:
    """Asserts the two engines sample alike and her lane lands only where her task changes; returns her switches in
    this engine and her landings in the per-landing one."""
    found, landed, switched = walk(start, r, span)
    with monkeypatch.context() as m:
        m.setattr(retap, "settle", no_settle)
        old_found, old_landed, old_switched = walk(bounded(start, r), r, span)
    assert found == old_found and len(found) == span // SAMPLE_S + 1
    assert landed == switched == old_switched, "her lane lands only where her task changes"
    return switched, old_landed


def b3_save(p: DayTwoPlayer) -> Save:
    return next(save for save, _ in p.history if her_card(save) is not None)


@pytest.mark.playthrough
@pytest.mark.parametrize("day2_route", [("typical", 0)], indirect=True, ids=["typical"])
def test_six_hours_of_her_always_rule_equal_the_per_landing_engine(day2_route: DayTwoPlayer,
                                                                   monkeypatch: pytest.MonkeyPatch):
    span = 6 * 3_600
    switched, old_landed = compare(b3_save(day2_route), day2_route.rules, span, monkeypatch)
    assert switched == 0 and old_landed >= span // 120, "her forage repeated through the span, landing every 120 s"


@pytest.mark.playthrough
@pytest.mark.parametrize("day2_route", [("typical", 0)], indirect=True, ids=["typical"])
def test_her_switching_rules_equal_the_per_landing_engine(day2_route: DayTwoPlayer, monkeypatch: pytest.MonkeyPatch):
    r, start = day2_route.rules, b3_save(day2_route)
    roots = next(st.segment.start_value for st in start.stores if st.store == ROOTS)
    rule = Order(AtLeast(StoreValue(ROOTS), roots + ROOTS_RULE_UP * Q, roots + ROOTS_RULE_DOWN * Q),
                 TapCard(CardId("n1_gather")))
    switched, _ = compare(decide(start, r, start.time, SetOrders((rule, *start.orders))), r, 5_400, monkeypatch)
    assert switched >= 3, "the rule switched her task, on, off and on again, in the span"
