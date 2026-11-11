"""Repeating taps (engine DESIGN.txt, part "REPEATING TAPS", invariants 75 to 79): a lane whose rule would start the
same card again at each completion runs it as a rate, with no instant per completion, and lands where the
per-landing engine would have switched its task.

The per-landing engine is this engine with retap.settle replaced by one that changes nothing (`per_landing`): the
oracle the equality tests compare against."""
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, AfterTime, Amount, AtLeast, AtMost, CardDef, CardId, Event, EventKind, Flow,
    LaneDef, LaneId, LaneSpeed, LineKey, Modifier, ModifierKind, Order, Outcome, PacingCurve, Rules, Save, SetOrders,
    SkillDef, SkillId, SourceId, StandingDef, StoreDef, StoreId, StoreValue, TapCard, TriggerDef, TriggerId, ActionId,
    advance, advance_logged, decide, new_save, next_event, validate_rules, view,
)
from ashfall_app.engine import retap
from ashfall_app.engine.schedule import events

HELPER = LaneId("helper")
X, Y, W, Z = StoreId("x"), StoreId("y"), StoreId("w"), StoreId("z")
A, B, E = CardId("a"), CardId("b"), CardId("e")
ALWAYS = AfterTime(0)
LOW_Y = Order(AtMost(StoreValue(Y), 5 * Q, 11 * Q), TapCard(B))
"""Her switching rule: cut when the store is low, until it is back above 11 (day two's damp wood card's shape)."""


def world(*, a_s: int = 12, b_s: int = 6, y0: int = 20 * Q, drain: int = 360_000, shelter: bool = True,
          gated_e: bool = True, a: CardDef | None = None, extra: tuple[CardDef, ...] = ()) -> Rules:
    """A lane run by rules beside a store a standing action drains. a makes x and counts w (cap 1, as her first task
    is counted); b refills y; e, when gated_e, takes 3 z a completion, which a standing action makes slowly, so it turns
    ready now and then. shelter: when w first fills, the lane runs at 1.2 (work_s multiples of 6 keep it exact)."""
    cards = (a or CardDef(A, a_s, lane=HELPER, outcome=Outcome(stores=(Amount(X, 2 * Q), Amount(W, Q)))),
             CardDef(B, b_s, lane=HELPER, outcome=Outcome(stores=(Amount(Y, 6 * Q), Amount(W, Q)))),
             CardDef(E, 30, lane=HELPER, inputs=(Amount(Z, 3 * Q),), outcome=Outcome(stores=(Amount(X, Q),))))
    standing = [StandingDef(ActionId("drain"), costs=(Flow(Y, drain),))]
    if gated_e:
        standing.append(StandingDef(ActionId("fill"), makes=(Flow(Z, 36_000),)))
    triggers = (TriggerDef(TriggerId("first"), AtLeast(StoreValue(W), Q, Q), Outcome(
        lines=(LineKey("first.line"),),
        modifiers=(Modifier(LaneSpeed(HELPER), ModifierKind.MUL_BP, 12_000, SourceId("shelter")),) if shelter else ()),
    ),)
    r = Rules(stores=(StoreDef(X, 10**6 * Q), StoreDef(Y, 100 * Q, y0), StoreDef(W, Q), StoreDef(Z, 100 * Q)),
              skills=(SkillDef(SkillId("k")),), standing=tuple(standing), curve=PacingCurve((10**9 * Q,)),
              lanes=(LaneDef(HELPER, ruled=True),), cards=cards + extra, triggers=triggers)
    validate_rules(r)
    return r


def started(r: Rules, *orders: Order) -> Save:
    return decide(new_save(r), r, 0, SetOrders(orders))


def no_settle(save: Save, rules: Rules, crossing: frozenset[LaneId]) -> tuple[Save, bool]:
    """retap.settle in the per-landing engine: no tap ever repeats."""
    return save, False


@contextmanager
def per_landing(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """The per-landing engine: no tap ever repeats."""
    with monkeypatch.context() as m:
        m.setattr(retap, "settle", no_settle)
        yield


def done(s: Save, r: Rules) -> tuple[int, ...]:
    work = {cs.card: cs.work.start_value for cs in s.cards}
    return tuple(work.get(c.id, 0) // (c.work_s * BP) for c in r.cards)


def state(s: Save, r: Rules) -> tuple[object, ...]:
    """What invariant 75 holds equal: values, counts and the discrete state, never a segment's limit."""
    return (s.time, tuple(st.segment.start_value for st in s.stores), tuple(k.xp.start_value for k in s.skills),
            tuple(ls.card for ls in s.lanes), s.latches, s.orders, s.queue, s.fired, s.unlocked, s.pauses, done(s, r))


type Walked = tuple[list[tuple[object, ...]], list[tuple[int, str]], set[CardId | None]]


def run(s: Save, r: Rules, until: int, step: int) -> Walked:
    """Samples every `step` s, each carried forward from the last, the lines on the way, and the cards her lane ran."""
    samples, lines, cards = [state(s, r)], list[tuple[int, str]](), {her_card(s)}
    for t in range(step, until + 1, step):
        logged = advance_logged(s, r, t)
        s = logged.save
        samples.append(state(s, r))
        lines += [(ln.time, ln.key) for ln in logged.lines]
        cards.add(her_card(s))
    return samples, lines, cards


def instants(s: Save, r: Rules, until: int) -> list[Event]:
    """Every event that falls at each instant the save resolves up to `until` (one instant per distinct time)."""
    found: list[Event] = []
    while (e := next_event(s, r)) is not None and e.time <= until:
        found += [x for x in events(s, r) if x.time == e.time]
        s = advance(s, r, e.time)
    return found


def landings(found: list[Event], lane: LaneId = HELPER) -> list[int]:
    return [e.time for e in found if e.kind is EventKind.TAP_DONE and e.subject == lane]


def her_card(s: Save) -> CardId | None:
    return s.lanes[1].card


def test_a_task_that_holds_costs_no_instant_per_completion():
    """Invariant 76: an hour of a's always rule resolves no TAP_DONE; the per-landing engine landed every 10 s."""
    r = world(gated_e=False, drain=0)
    s = started(r, Order(ALWAYS, TapCard(A)))
    found = instants(s, r, 3_600)
    assert landings(found) == []
    assert len({e.time for e in found}) <= 3, found
    end = advance(s, r, 3_600)
    assert her_card(end) == A and done(end, r)[0] == 1 + (3_600 - 12) // 10   # 12 s at 1.0, then 10 s at 1.2


def test_the_per_landing_engine_lands_every_completion(monkeypatch: pytest.MonkeyPatch):
    """The oracle is what it claims: without the settle every completion is a TAP_DONE."""
    r = world(gated_e=False, drain=0)
    with per_landing(monkeypatch):
        found = instants(started(r, Order(ALWAYS, TapCard(A))), r, 600)
    assert len(landings(found)) == 1 + (600 - 12) // 10


@pytest.mark.parametrize("gated_e", [False, True], ids=["switching", "with-a-blocked-earlier-card"])
def test_outcomes_equal_the_per_landing_engine(monkeypatch: pytest.MonkeyPatch, gated_e: bool):
    """Invariant 75: half an hour of her rules (a switching store rule over an always rule, the lane's speed rising part
    way, and, with e, an earlier always rule whose card is ready only now and then; the cycle repeats about every
    minute, so this holds dozens of switches) sampled every 7 s: the same values,
    counts, latches, lanes and lines as the per-landing engine."""
    r = world(gated_e=gated_e)
    orders = (Order(ALWAYS, TapCard(E)),) if gated_e else ()
    orders += (LOW_Y, Order(ALWAYS, TapCard(A)))
    repeating = run(started(r, *orders), r, 1_800, 7)
    with per_landing(monkeypatch):
        landing = run(started(r, *orders), r, 1_800, 7)
    assert repeating == landing
    assert repeating[2] >= ({A, B, E} if gated_e else {A, B})   # every task ran: the comparison saw switches


def test_a_task_change_lands_at_the_first_completion_after_it():
    """Invariant 77: y reaches 5 at 45 s; a (10 s) runs to its completion at 50, then b starts."""
    r = world(a_s=10, y0=int(9.5 * Q), gated_e=False, shelter=False)
    s = started(r, LOW_Y, Order(ALWAYS, TapCard(A)))
    assert [her_card(advance(s, r, t)) for t in (44, 45, 49, 50)] == [A, A, A, B]


def test_a_task_change_at_a_completion_lands_then():
    """Invariant 77: y reaches 5 at 50 s, exactly a's fifth completion: it lands at 50 (the per-landing engine had a
    landing there, and evaluation ran after the latch), not at 60."""
    r = world(a_s=10, y0=10 * Q, gated_e=False, shelter=False)
    s = started(r, LOW_Y, Order(ALWAYS, TapCard(A)))
    at_49 = advance(s, r, 49)
    assert her_card(at_49) == A
    assert her_card(advance(at_49, r, 50)) == B
    assert done(advance(at_49, r, 50), r)[0] == 5


def test_a_decision_at_a_completion_runs_one_more(monkeypatch: pytest.MonkeyPatch):
    """Invariant 77: a rule set at 50 s, when a's work stands on its fifth completion, takes the lane at a's next one
    (60): the per-landing engine landed and re-tapped a inside the advance to 50, before the decision."""
    r = world(a_s=10, gated_e=False, shelter=False, drain=0)
    orders = SetOrders((Order(ALWAYS, TapCard(B)), Order(ALWAYS, TapCard(A))))
    after = decide(started(r, Order(ALWAYS, TapCard(A))), r, 50, orders)
    got = [her_card(advance(after, r, t)) for t in (50, 59, 60)]
    with per_landing(monkeypatch):
        oracle = decide(started(r, Order(ALWAYS, TapCard(A))), r, 50, orders)
        want = [her_card(advance(oracle, r, t)) for t in (50, 59, 60)]
    assert got == want == [A, A, B]


def _line_card() -> CardDef:
    return CardDef(A, 12, lane=HELPER, outcome=Outcome(stores=(Amount(X, 2 * Q), Amount(W, Q))),
                   lines=(LineKey("a.tap"),))


@pytest.mark.parametrize("which", ["capped", "inputs", "a-tap-line", "hands"])
def test_only_eligible_taps_repeat(which: str):
    """Invariant 78: a capped card, one with inputs, one with a tap line, and a tap on the hands each still land at
    their next completion; the eligible card beside them does not."""
    hand = CardDef(CardId("h"), 12)
    a = {"capped": CardDef(A, 12, lane=HELPER, cap=1000),
         "inputs": CardDef(A, 12, lane=HELPER, inputs=(Amount(Y, Q),)),
         "a-tap-line": _line_card(),
         "hands": None}[which]
    r = world(gated_e=False, drain=0, shelter=False, a=a, extra=(hand,))
    card = hand.id if which == "hands" else A
    s = advance(started(r, Order(ALWAYS, TapCard(card))), r, 30)
    lane = HANDS if which == "hands" else HELPER
    assert landings(instants(s, r, 60), lane) == [36, 48, 60]
    control = world(gated_e=False, drain=0, shelter=False)
    assert landings(instants(advance(started(control, Order(ALWAYS, TapCard(A))), control, 30), control, 60)) == []


def test_the_view_of_a_repeating_lane():
    """Invariant 79: while a repeats, its LaneBar has no end and its bar no limit; once y's rule comes on (45 s) it is
    bounded at its completion (50 s)."""
    r = world(a_s=10, y0=int(9.5 * Q), gated_e=False, shelter=False)
    s = advance(started(r, LOW_Y, Order(ALWAYS, TapCard(A))), r, 20)
    bar = next(b for b in view(s, r).lanes if b.lane == HELPER)
    card = next(c for c in view(s, r).cards if c.card == A)
    assert (bar.card, bar.completes_at, card.bar.limit, card.completes_at) == (A, None, None, 30)
    s = advance(s, r, 45)
    bar = next(b for b in view(s, r).lanes if b.lane == HELPER)
    card = next(c for c in view(s, r).cards if c.card == A)
    assert (bar.card, bar.completes_at, card.bar.limit) == (A, 50, 5 * 10 * BP)


def test_split_holds_across_repeats():
    """Invariant 1 with a lane repeating, switching and repeating again: any split point gives the same save."""
    r = world()
    s = started(r, Order(ALWAYS, TapCard(E)), LOW_Y, Order(ALWAYS, TapCard(A)))
    whole = advance(s, r, 1_000)
    assert whole.lanes[1].card is not None and any(done(whole, r))   # the lane ran: the splits cut a live save
    for t1 in (1, 12, 13, 45, 50, 299, 300, 301, 777, 999):
        assert advance(advance(s, r, t1), r, 1_000) == whole, t1


def test_a_live_save_with_a_bounded_tap_repeats_from_its_next_instant():
    """A save written by the per-landing engine (her tap bounded at its completion) decodes as it is and repeats once
    that completion lands; its values are those of a save that repeated all along."""
    r = world(gated_e=False, drain=0, shelter=False)
    s = advance(started(r, Order(ALWAYS, TapCard(A))), r, 30)
    work = s.cards[0].work
    bounded = replace(s, cards=(replace(s.cards[0], work=replace(work, limit=(work.start_value // (12 * BP) + 1)
                                                                  * 12 * BP)),) + s.cards[1:])
    assert next_event(bounded, r) == Event(36, EventKind.TAP_DONE, 1, HELPER)
    later: Callable[[Save], Save] = lambda x: advance(x, r, 600)
    assert state(later(bounded), r) == state(later(s), r)
    assert later(bounded).cards[0].work.limit is None
