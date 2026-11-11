"""Repeating taps (engine DESIGN.txt, part "REPEATING TAPS", invariants 75-79; api CONTRACT.txt, "A LANE RUN BY RULES").
Written from the contract and the public interface only. A ruled side lane `L` runs an always rule on an uncapped
card with no inputs; every expected number below is derived from the documented arithmetic (a completion every
work_s seconds at full speed, a make of w whole items per second moves a store by w * Q per second)."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, AfterTime, Amount, AtMost, CardDef, CardId, EventKind, Flow,
    LaneDef, LaneId, LaneSpeed, Modifier, ModifierKind, Order, Outcome, PacingCurve, Rules, Save, SetOrders, SkillDef,
    SkillId, SourceId, StoreDef, StoreId, StoreValue, TapCard, TriggerDef, TriggerId, advance, decide, forecast,
    level, new_save, next_event, per_hour, segment, value_at, view,
)

L = LaneId("L")
X, Y, F, Z = StoreId("x"), StoreId("y"), StoreId("f"), StoreId("z")
A, B, H, C = CardId("a"), CardId("b"), CardId("h"), CardId("c")
K = SkillId("k")
ALWAYS = AfterTime(0)
BIG = 10**6 * Q
PER_SECOND = per_hour(3600)   # one whole item per second


def world(cards: tuple[CardDef, ...], stores: tuple[StoreDef, ...] = (), triggers: tuple[TriggerDef, ...] = (),
          thresholds: tuple[int, ...] = (10**15,)) -> Rules:
    base = (StoreDef(X, BIG), StoreDef(Y, BIG), StoreDef(F, BIG, 1000 * Q), StoreDef(Z, BIG, 1000 * Q))
    return Rules(stores=base + stores, skills=(SkillDef(K),), standing=(), curve=PacingCurve(thresholds),
                 lanes=(LaneDef(L, True),), cards=cards, triggers=triggers)


def lump(work_s: int = 10) -> CardDef:
    """Card a on L: one Y per completion (a lump line), one X per second of running, XP; uncapped, no inputs."""
    return CardDef(A, work_s, lane=L, skill=K, xp_per_hour=PER_SECOND, makes=(Flow(X, PER_SECOND),),
                   outcome=Outcome(stores=(Amount(Y, Q),)))


def started(r: Rules, *orders: Order, at: int = 0) -> Save:
    return decide(new_save(r), r, at, SetOrders(orders))


def always(card: CardId) -> Order:
    return Order(ALWAYS, TapCard(card))


def lane_card(s: Save) -> CardId | None:
    return next(ls.card for ls in s.lanes if ls.lane == L)


def bar(s: Save, r: Rules):
    return next(b for b in view(s, r).lanes if b.lane == L)


def card_view(s: Save, r: Rules, c: CardId):
    return next(cv for cv in view(s, r).cards if cv.card == c)


def stored(s: Save, r: Rules, store: StoreId) -> int:
    return value_at(segment(s, r, store), s.time)


def count(s: Save, r: Rules, c: CardId) -> int:
    return card_view(s, r, c).completions


# ---- totals over long stretches (invariant 75) ---------------------------------------------------------------

@given(t=st.integers(1, 20_000), work_s=st.sampled_from([5, 10, 12, 60]))
def test_totals_over_any_stretch_equal_the_per_completion_totals(t: int, work_s: int):
    """Invariant 75: at full speed (which divides work_s * BP) CardCount is exactly t // work_s; stores and XP run at
    their rates, so the lump store holds t * Q / work_s to within the rate's rounding (under one unit per second) and
    the make line holds exactly t whole items."""
    r = world((lump(work_s),))
    s = advance(started(r, always(A)), r, t)
    assert count(s, r, A) == t // work_s
    assert abs(stored(s, r, Y) - t * Q // work_s) <= t
    assert stored(s, r, X) == t * Q
    assert lane_card(s) == A


def test_a_day_of_repeats_matches_the_sum_of_its_completions():
    r = world((lump(10),))
    s = advance(started(r, always(A)), r, 86_400)
    assert count(s, r, A) == 8_640
    assert stored(s, r, Y) == 8_640 * Q
    assert stored(s, r, X) == 86_400 * Q


def test_xp_runs_at_its_rate_while_the_lane_repeats():
    """XP comes in at the card's xp_per_hour; 1 whole XP/s gives 3600 per hour, so a level threshold of 600 XP is
    reached at exactly 600 s (level 1 is XP 0, so the level goes 1 to 2)."""
    r = world((lump(10),), thresholds=(600 * Q,))
    s = started(r, always(A))
    assert level(advance(s, r, 599), r, K, 599) == 1
    assert level(advance(s, r, 600), r, K, 600) == 2


# ---- repeats cost no instants (invariant 76) -----------------------------------------------------------------

def test_next_event_moves_past_the_completions():
    """Invariant 76 and the view note: the next event is the store filling at 500, not the landing at 3."""
    r = _capped_world(500)
    ev = next_event(started(r, always(A)), r)
    assert ev is not None and (ev.time, ev.kind, ev.subject) == (500, EventKind.STORE_LIMIT, "z")


def _capped_world(cap_whole: int) -> Rules:
    stores = tuple(StoreDef(st, cap_whole * Q if st == Z else BIG, 0) for st in (X, Y, F, Z))
    return Rules(stores=stores, skills=(SkillDef(K),), standing=(), curve=PacingCurve((10**15,)),
                 lanes=(LaneDef(L, True),),
                 cards=(CardDef(A, 3, lane=L, makes=(Flow(Z, PER_SECOND),)),))


@given(cap=st.integers(10, 3000))
def test_a_forecast_over_many_completions_resolves_few_instants(cap: int):
    """Invariant 76: the lane lands every 3 s, so cap seconds hold cap // 3 completions; the forecast asks `stop`
    once per instant it resolves, and that is a handful (the fill, at most a start), never one per completion."""
    r = _capped_world(cap)
    s = started(r, always(A))
    asked: list[int] = []
    fc = forecast(s, r, cap + 50, (Z,), stop=lambda: bool(asked.append(1)))
    assert fc.fills[Z] == (cap,)
    assert len(asked) <= 3


def test_advance_steps_through_a_long_span_with_next_event_never_a_tap_done():
    r = _capped_world(900)
    s = started(r, always(A))
    seen: list[EventKind] = []
    while (ev := next_event(s, r)) is not None and ev.time <= 1000:
        seen.append(ev.kind)
        assert ev.time > s.time
        s = advance(s, r, ev.time)
    assert seen and EventKind.TAP_DONE not in seen
    assert count(s, r, A) == s.time // 3 and s.time == 900


# ---- a switch happens when the contract says (invariant 77) --------------------------------------------------

def _two_card_world(work_s: int) -> Rules:
    return world((CardDef(A, work_s, lane=L, makes=(Flow(X, PER_SECOND),)),
                  CardDef(B, 7, lane=L, makes=(Flow(Y, PER_SECOND),))))


@given(T=st.integers(1, 300), work_s=st.sampled_from([4, 10, 13]))
def test_a_rule_coming_on_by_time_lands_the_tap_at_the_first_completion_at_or_after_it(T: int, work_s: int):
    """Invariant 77: the switch lands c at the first completion at or after T (at T itself when T is a completion,
    reached by time passing), and the next task starts at that landing."""
    r = _two_card_world(work_s)
    s = started(r, Order(AfterTime(T), TapCard(B)), always(A))
    land = -(-T // work_s) * work_s
    assert lane_card(advance(s, r, land - 1)) == A
    at = advance(s, r, land)
    assert lane_card(at) == B
    assert card_view(at, r, B).completes_at == land + 7
    assert count(at, r, A) == land // work_s
    assert stored(at, r, X) == land * Q


def test_a_switch_exactly_on_a_completion_lands_there_when_reached_by_time():
    r = _two_card_world(10)
    s = started(r, Order(AfterTime(40), TapCard(B)), always(A))
    assert (lane_card(advance(s, r, 39)), lane_card(advance(s, r, 40))) == (A, B)


def test_a_decision_on_a_completion_never_lands_it():
    """Invariant 77: a task change that is a decision at T never lands at T: the tap of the instant before runs one
    more completion, and the next task starts there."""
    r = _two_card_world(10)
    s = advance(started(r, always(A)), r, 40)
    s = decide(s, r, 40, SetOrders((Order(ALWAYS, TapCard(B)),)))
    assert lane_card(s) == A
    assert lane_card(advance(s, r, 49)) == A
    assert lane_card(advance(s, r, 50)) == B
    assert count(advance(s, r, 50), r, A) == 5


def test_an_at_most_rule_switches_at_the_time_its_store_crosses_then_lands():
    """F falls 1 whole/s from 1000 under A; at_most 955 is true at t = 45, A lands at 50."""
    r = world((CardDef(A, 10, lane=L, costs=(Flow(F, PER_SECOND),)), CardDef(B, 7, lane=L, makes=(Flow(Y, PER_SECOND),))))
    s = started(r, Order(AtMost(StoreValue(F), 955 * Q, 955 * Q), TapCard(B)), always(A))
    assert lane_card(advance(s, r, 49)) == A
    assert lane_card(advance(s, r, 50)) == B
    assert bar(advance(s, r, 45), r).completes_at == 50   # bounded as soon as the task no longer holds


# ---- a cap keeps landings (invariant 78) ---------------------------------------------------------------------

def test_a_capped_card_lands_at_every_completion_and_stops_at_its_cap():
    r = world((CardDef(A, 10, lane=L, cap=3, makes=(Flow(X, PER_SECOND),)),))
    s = started(r, always(A))
    times: list[int] = []
    while (ev := next_event(s, r)) is not None and ev.time <= 100:
        assert ev.kind in (EventKind.TAP_DONE, EventKind.COMPLETION)
        times.append(ev.time)
        s = advance(s, r, ev.time)
    assert sorted(set(times)) == [10, 20, 30]
    s = advance(s, r, 100)
    assert [(c.card, c.completions) for c in view(s, r).completed] == [(A, 3)]
    assert lane_card(s) is None


# ---- inputs keep landing per completion (invariant 78) --------------------------------------------------------

def test_a_card_with_inputs_lands_at_each_completion_and_pays_each_input():
    r = world((CardDef(A, 10, lane=L, inputs=(Amount(F, 2 * Q),), outcome=Outcome(stores=(Amount(Y, Q),))),))
    s = started(r, always(A))
    for n in range(1, 6):
        ev = next_event(s, r)
        assert ev is not None and (ev.time, ev.kind) == (10 * n, EventKind.TAP_DONE)
        s = advance(s, r, ev.time)
        assert lane_card(s) == A
    assert count(s, r, A) == 5
    assert stored(s, r, F) == 1000 * Q - 5 * 2 * Q
    assert stored(s, r, Y) == 5 * Q
    assert bar(s, r).completes_at == 60


def test_the_same_card_without_inputs_repeats_where_this_one_does_not():
    """Control for the test above: only the inputs differ."""
    plain = world((CardDef(A, 10, lane=L, outcome=Outcome(stores=(Amount(Y, Q),))),))
    withs = world((CardDef(A, 10, lane=L, inputs=(Amount(F, 2 * Q),), outcome=Outcome(stores=(Amount(Y, Q),))),))
    assert bar(started(plain, always(A)), plain).completes_at is None
    assert bar(started(withs, always(A)), withs).completes_at == 10


# ---- the hands are unaffected (invariant 78) ------------------------------------------------------------------

def test_a_tap_on_the_hands_lands_at_each_completion():
    r = world((CardDef(H, 10, makes=(Flow(X, PER_SECOND),)),))
    s = started(r, always(H))
    for n in range(1, 6):
        ev = next_event(s, r)
        assert ev is not None and (ev.time, ev.kind) == (10 * n, EventKind.TAP_DONE)
        s = advance(s, r, ev.time)
    hands = next(b for b in view(s, r).lanes if b.lane == HANDS)
    assert hands.completes_at == 60
    assert count(s, r, H) == 5


# ---- a lane speed changing mid-run -----------------------------------------------------------------------------

def _slowed(at: int) -> Rules:
    halve = Modifier(LaneSpeed(L), ModifierKind.MUL_BP, BP // 2, SourceId("slow"))
    return world((lump(10),), triggers=(TriggerDef(TriggerId("slow"), AfterTime(at), Outcome(modifiers=(halve,))),))


def test_a_lane_speed_change_moves_the_totals_and_the_completions_it_names():
    """Halved at 40: work after 40 runs at half speed, so by 140 the work is 40 + 50 = 90 s of full-speed work:
    9 completions; Y, X and XP are on the same clock."""
    r = _slowed(40)
    s = started(r, always(A))
    assert count(advance(s, r, 40), r, A) == 4
    at = advance(s, r, 140)
    assert count(at, r, A) == 9
    assert abs(stored(at, r, Y) - 9 * Q) <= 140
    assert abs(stored(at, r, X) - 90 * Q) <= 140
    assert lane_card(at) == A


def test_after_a_speed_change_the_next_completion_is_at_the_new_speed_and_the_lane_still_repeats():
    r = _slowed(40)
    at = advance(started(r, always(A)), r, 40)
    assert card_view(at, r, A).completes_at == 60
    assert bar(at, r).completes_at is None
    ev = next_event(at, r)
    assert ev is None or ev.kind is not EventKind.TAP_DONE


# ---- the view (invariant 79) ------------------------------------------------------------------------------------

def test_while_a_lane_repeats_its_bar_is_open_and_the_card_bar_has_no_limit():
    r = world((lump(10),))
    for t in (0, 1, 9, 10, 37, 100):
        s = advance(started(r, always(A)), r, t)
        b, cv = bar(s, r), card_view(s, r, A)
        assert (b.card, b.completes_at, b.order) == (A, None, 0)
        assert cv.bar.limit is None
        assert cv.bar_total == 10 * BP
        assert value_at(cv.bar, t) % cv.bar_total == (t * BP) % cv.bar_total
        assert cv.completes_at == (t // 10 + 1) * 10


def test_once_bounded_the_lane_bar_names_the_next_completion_and_the_card_bar_its_work():
    """AfterTime(35) turns the task off while A runs: at 35 the tap is bounded at its next completion, 40."""
    r = _two_card_world(10)
    s = advance(started(r, Order(AfterTime(35), TapCard(B)), always(A)), r, 35)
    b, cv = bar(s, r), card_view(s, r, A)
    assert (b.card, b.completes_at) == (A, 40)
    assert cv.bar.limit == 40 * BP
    assert cv.completes_at == 40
    before = advance(started(r, Order(AfterTime(35), TapCard(B)), always(A)), r, 20)
    assert bar(before, r).completes_at is None    # control: still repeating before the change


# ---- forecast and advance agree ------------------------------------------------------------------------------

@given(cap=st.integers(5, 2000))
def test_forecast_fill_time_is_the_first_time_advance_shows_the_store_full(cap: int):
    r = _capped_world(cap)
    s = started(r, always(A))
    fc = forecast(s, r, cap + 10, (Z,))
    (fill,) = fc.fills[Z]
    assert stored(advance(s, r, fill - 1), r, Z) < cap * Q
    assert stored(advance(s, r, fill), r, Z) == cap * Q


@given(T=st.integers(1, 200))
def test_forecast_across_a_switch_matches_advance(T: int):
    """A feeds nothing relevant; after the switch B fills Z at 1 whole/s from its landing: the forecast's fill time is
    the landing plus the whole seconds B needs, and advance shows the same."""
    cap = 40
    r = Rules(stores=(StoreDef(X, BIG), StoreDef(Z, cap * Q)), skills=(SkillDef(K),), standing=(),
              curve=PacingCurve((10**15,)), lanes=(LaneDef(L, True),),
              cards=(CardDef(A, 10, lane=L, makes=(Flow(X, PER_SECOND),)),
                     CardDef(B, 1000, lane=L, makes=(Flow(Z, PER_SECOND),))))
    s = started(r, Order(AfterTime(T), TapCard(B)), always(A))
    land = -(-T // 10) * 10
    fc = forecast(s, r, land + cap + 20, (Z,))
    assert fc.fills[Z] == (land + cap,)
    assert stored(advance(s, r, land + cap - 1), r, Z) < cap * Q
    assert stored(advance(s, r, land + cap), r, Z) == cap * Q


def test_forecast_level_ups_match_advance():
    r = world((lump(10),), thresholds=(120 * Q, 500 * Q))
    s = started(r, always(A))
    fc = forecast(s, r, 1000)
    assert fc.level_ups[K] == (120, 500)
    for t, lv in ((119, 1), (120, 2), (499, 2), (500, 3)):
        assert level(advance(s, r, t), r, K, t) == lv


# ---- piecewise advance equals one advance ---------------------------------------------------------------------

@given(cuts=st.lists(st.integers(1, 500), min_size=1, max_size=6))
def test_advancing_in_pieces_equals_advancing_once(cuts: list[int]):
    r = _slowed(40)
    s0 = started(r, always(A))
    total, s = 0, s0
    for c in cuts:
        total += c
        s = advance(s, r, total)
    once = advance(s0, r, total)
    assert (count(s, r, A), stored(s, r, Y), stored(s, r, X), lane_card(s)) == \
           (count(once, r, A), stored(once, r, Y), stored(once, r, X), lane_card(once))
