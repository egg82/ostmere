"""Store-cap raises, written from DESIGN.txt ("Store caps", "Caps", "Retired") and Outcome's docstring alone: a Modifier
aimed at StoreCap(store) changes what the store holds, adds sum and muls compound with one rounding down at the end;
LedgerLine.cap is the cap now; it only raises, so nothing is clamped and no stock is lost; the rebuild at the instant a
raise lands restarts a full store's makers; an Outcome's
modifiers are appended to the save's stack for good (a completed or retired granter does not take them back).

World: store x (cap 10 items, 1 item/s from a source) and a capped card `land` whose outcome carries the raise. The
source is a standing action, or a mixed card with `land` on the rack. Samples carry forward from the last (invariant 1)."""
from itertools import permutations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, Amount, AtLeast, ChipDef, ChipId, CardDef, CardId, EventKind, Flow, FlowKind,
    InvalidRulesError, InvalidVerbError, LedgerLine, Modifier, Outcome, RateRef, Rules, Save, StandingDef, StoreCap, StoreDef,
    StoreId, StoreValue, TriggerDef, TriggerId, Unlock, UnlockKind, advance, decode, encode, new_save,
    next_event, segment, validate_rules, view,
)
from cards_world import Q, RACK, add, ledger, make, mul, rules, tap, val, with_mix

X, Y = StoreId("x"), StoreId("y")
SRC = ActionId("src")
MK, LAND, LA, LB, LC, OLD, RET = (CardId(n) for n in ("mk", "land", "la", "lb", "lc", "old", "ret"))
KINDS = ["standing-tap", "standing-mix", "mixmaker-racktap"]


def cap_add(bp: int, source: str = "u", store: StoreId = X) -> Modifier:
    return add(StoreCap(store), bp, source)


def cap_mul(bp: int, source: str = "u", store: StoreId = X) -> Modifier:
    return mul(StoreCap(store), bp, source)


def floor_cap(base: int, adds: list[int], muls: list[int]) -> int:
    """The contract's formula, exactly: (1 + sum of adds) times each mul, one rounding down at the end."""
    num, den = base * (BP + sum(adds)), BP
    for m in muls:
        num, den = num * m, den * BP
    return num // den


def world(kind: str, *, cap: int = 10 * Q, initial: int = 0, rate: int = Q, outcome: Outcome = Outcome(),
          finished: Outcome = Outcome(), work_s: int = 30, card_cap: int = 1,
          triggers: tuple[TriggerDef, ...] = ()) -> Rules:
    mixmaker = kind == "mixmaker-racktap"
    cards = [CardDef(LAND, work_s, cap=card_cap, lane=RACK if mixmaker else HANDS, outcome=outcome,
                     finished=finished)]
    if mixmaker:
        cards.append(CardDef(MK, 100, makes=(Flow(X, rate),)))
    standing = [] if mixmaker else [StandingDef(SRC, makes=(Flow(X, rate),))]
    return rules([StoreDef(X, cap, initial), StoreDef(Y, 10 * Q, 0)], standing=standing, cards=cards, lanes=[RACK],
                 triggers=list(triggers))


def start(kind: str, r: Rules) -> Save:
    """Time 0: the source running, `land` begun (tapped, or mixed at the full share)."""
    if kind == "standing-tap":
        return tap(new_save(r), r, 0, LAND)
    if kind == "standing-mix":
        return with_mix(new_save(r), r, 0, {LAND: BP})
    return tap(with_mix(new_save(r), r, 0, {MK: BP}), r, 0, LAND)


def again(kind: str, s: Save, r: Rules, t: int) -> Save:
    """The next completion's work: a mixed card carries on by itself, a tap is made again."""
    return advance(s, r, t) if kind == "standing-mix" else tap(s, r, t, LAND)


def raise_by(bp: int, source: str = "u") -> Outcome:
    return Outcome(modifiers=(cap_add(bp, source),))


def cap_of(s: Save, r: Rules, store: StoreId = X) -> int:
    return ledger(s, r, store).cap


def full(line: LedgerLine) -> bool:
    return line.segment.start_value == line.cap


def losing(line: LedgerLine) -> bool:
    return full(line) and line.net_per_hour > 0


# ---- a raise is a number with sources ----------------------------------------------------------------------------

@pytest.mark.parametrize("base, adds, muls, expected", [
    (10 * Q, [], [], 10 * Q),
    (10 * Q, [5000], [], 15 * Q),
    (10 * Q, [1000, 1000], [], 12 * Q),
    (10 * Q, [], [15_000, 15_000], 81_000_000),
    (10 * Q, [5000], [20_000], 30 * Q),
    (10 * Q, [0], [BP], 10 * Q),
    (10 * Q, [1], [], 10 * Q + 3600),
    (5, [], [19_999], 9),
    (5, [], [15_000, 15_000], 11),
    (5, [5000], [15_000], 11),
    (3, [3333], [], 3),
])
def test_the_cap_is_the_base_under_its_stack(base: int, adds: list[int], muls: list[int], expected: int) -> None:
    """Adds sum, muls compound, one rounding down at the end (not per step, not to nearest)."""
    r = world("standing-tap", cap=base)
    stack = tuple([cap_add(a, f"a{i}") for i, a in enumerate(adds)] + [cap_mul(m, f"m{i}") for i, m in enumerate(muls)])
    s = new_save(r, stack)
    assert expected == floor_cap(base, adds, muls)
    assert cap_of(s, r) == expected


@given(base=st.integers(1, 10**9), adds=st.lists(st.integers(0, 30_000), max_size=3),
       muls=st.lists(st.integers(BP, 30_000), max_size=3), data=st.data())
def test_the_cap_follows_the_formula_in_any_order(base: int, adds: list[int], muls: list[int],
                                                  data: st.DataObject) -> None:
    r = world("standing-tap", cap=base)
    stack = [cap_add(a, f"a{i}") for i, a in enumerate(adds)] + [cap_mul(m, f"m{i}") for i, m in enumerate(muls)]
    stack = data.draw(st.permutations(stack))
    s = new_save(r, tuple(stack))
    assert cap_of(s, r) == floor_cap(base, adds, muls) >= base


def test_a_raise_aims_at_its_store_only_and_changes_no_rate() -> None:
    """Y keeps its cap; the source's make is the same rate with the same explanation, the entry in no add or mul."""
    r = world("standing-tap")
    plain, raised = new_save(r), new_save(r, (cap_add(5000), cap_mul(20_000, "v")))
    assert cap_of(raised, r, Y) == 10 * Q and cap_of(raised, r, X) == 30 * Q
    assert make(raised, r, SRC, X) == make(plain, r, SRC, X)
    only_y = new_save(r, (cap_add(5000, "y", Y),))
    assert cap_of(only_y, r, X) == 10 * Q and cap_of(only_y, r, Y) == 15 * Q


# ---- the store holds the raised cap ------------------------------------------------------------------------------

def test_a_store_fills_to_the_raised_cap_at_the_exact_second() -> None:
    """12.5 items at 1/3 item/s: ceil(37.5) = 38. Below it by exact arithmetic, never above, the fill an event."""
    r = world("standing-tap", rate=Q // 3)
    s = new_save(r, (cap_add(2500),))
    cap = 125 * Q // 10
    assert cap_of(s, r) == cap and ledger(s, r, X).fills_at == 38
    ev = next_event(s, r)
    assert ev is not None and (ev.time, ev.kind, ev.subject) == (38, EventKind.STORE_LIMIT, "x")
    for t in range(1, 41):
        s = advance(s, r, t)
        assert val(s, r, X) == min(t * (Q // 3), cap)


def test_a_store_starting_full_under_a_raise_keeps_its_stock_and_fills_on() -> None:
    """Initial at the base cap, the raise in the starting stack: nothing is lost or clamped, the maker runs from 0."""
    r = world("standing-tap", initial=10 * Q)
    s = new_save(r, (cap_add(5000),))
    assert val(s, r, X) == 10 * Q and segment(s, r, X).rate == Q and ledger(s, r, X).fills_at == 5
    assert val(advance(s, r, 7), r, X) == 15 * Q


# ---- a raise landing mid-run -------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_a_raise_takes_effect_at_the_instant_it_lands_and_restarts_a_full_store(kind: str) -> None:
    r = world(kind, outcome=raise_by(5000))
    s = advance(start(kind, r), r, 29)
    assert cap_of(s, r) == 10 * Q and val(s, r, X) == 10 * Q and segment(s, r, X).rate == 0
    s = advance(s, r, 30)
    assert cap_of(s, r) == 15 * Q and val(s, r, X) == 10 * Q
    assert segment(s, r, X).rate == Q and ledger(s, r, X).fills_at == 35
    s = advance(s, r, 33)
    assert val(s, r, X) == 13 * Q
    s = advance(s, r, 35)
    assert val(s, r, X) == 15 * Q and segment(s, r, X).rate == 0
    s = advance(s, r, 400)
    assert val(s, r, X) == 15 * Q and cap_of(s, r) == 15 * Q


@pytest.mark.parametrize("kind", KINDS)
def test_the_old_cap_is_not_an_event_after_the_raise(kind: str) -> None:
    """At 10 the store is full and the next event is the landing; after the landing it is the fill at the new cap."""
    r = world(kind, outcome=raise_by(5000))
    s = advance(start(kind, r), r, 10)
    ev = next_event(s, r)
    assert ev is not None and ev.time == 30 and ev.kind != EventKind.STORE_LIMIT
    ev = next_event(advance(s, r, 30), r)
    assert ev is not None and (ev.time, ev.kind) == (35, EventKind.STORE_LIMIT)


@pytest.mark.parametrize("kind", KINDS)
def test_a_raise_below_the_cap_loses_no_stock(kind: str) -> None:
    """Landing at 5 with 5 items held: the value climbs one item a second through the landing, to the new cap."""
    r = world(kind, outcome=raise_by(5000), work_s=5)
    s = start(kind, r)
    for t in range(0, 20):
        s = advance(s, r, t)
        assert val(s, r, X) == min(t * Q, 15 * Q if t >= 5 else 10 * Q), t
        assert cap_of(s, r) == (15 * Q if t >= 5 else 10 * Q), t


@pytest.mark.parametrize("kind", KINDS)
def test_full_and_losing_follow_the_raised_cap(kind: str) -> None:
    """The page's full (value at cap) and losing (full and still gaining) read the line's cap: both at the old cap
    before the landing, neither at the instant of it, both again at the new cap."""
    r = world(kind, outcome=raise_by(5000))
    s = advance(start(kind, r), r, 29)
    before = ledger(s, r, X)
    assert full(before) and losing(before)
    s = advance(s, r, 30)
    line = ledger(s, r, X)
    assert not full(line) and not losing(line) and line.net_per_hour == before.net_per_hour
    s = advance(s, r, 40)
    line = ledger(s, r, X)
    assert full(line) and losing(line) and line.cap == 15 * Q


@pytest.mark.parametrize("order", list(permutations("abc")))
def test_several_landed_raises_combine_as_the_stack_does(order: tuple[str, ...]) -> None:
    """Two +50% and a x2, landing in any order: adds sum and the mul scales the sum; each step's cap is the formula's."""
    by = {"a": raise_by(5000, "a"), "b": raise_by(5000, "b"), "c": Outcome(modifiers=(cap_mul(20_000, "c"),))}
    card = {"a": LA, "b": LB, "c": LC}
    r = rules([StoreDef(X, 10 * Q, 0), StoreDef(Y, 10 * Q, 0)], standing=[StandingDef(SRC, makes=(Flow(X, Q),))],
              cards=[CardDef(card[k], 10, cap=1, outcome=by[k]) for k in "abc"])
    s = new_save(r)
    adds: list[int] = []
    muls: list[int] = []
    for i, k in enumerate(order):
        s = tap(s, r, 10 * i, card[k])
        s = advance(s, r, 10 * i + 9)
        assert cap_of(s, r) == floor_cap(10 * Q, adds, muls)
        s = advance(s, r, 10 * i + 10)
        (muls if k == "c" else adds).extend([20_000] if k == "c" else [5000])
        assert cap_of(s, r) == floor_cap(10 * Q, adds, muls)
    assert cap_of(s, r) == 40 * Q


def test_a_trigger_outcome_raises_the_cap_when_it_fires() -> None:
    r = world("standing-tap", work_s=999, triggers=(TriggerDef(TriggerId("t0"), AfterTime(20), raise_by(5000)),))
    s = advance(new_save(r), r, 19)
    assert cap_of(s, r) == 10 * Q
    s = advance(s, r, 21)
    assert cap_of(s, r) == 15 * Q and segment(s, r, X).rate == Q


# ---- Completed, finished and retirement --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_a_completed_card_keeps_the_raise_it_landed(kind: str) -> None:
    """The outcome's modifiers are appended for good: the card at its cap is on the Completed tab and the cap stays."""
    r = world(kind, outcome=raise_by(5000))
    s = advance(start(kind, r), r, 10_000)
    v = view(s, r)
    assert LAND in [c.card for c in v.completed] and LAND not in [c.card for c in v.cards]
    assert cap_of(s, r) == 15 * Q and val(s, r, X) == 15 * Q


@pytest.mark.parametrize("kind", ["standing-tap", "standing-mix"])
def test_finished_lands_its_raise_only_at_the_cap_and_after_outcome(kind: str) -> None:
    """A card with cap 2: its `finished` raise lands at the second completion only; with `outcome` raising too, the
    last completion lands both and they sum."""
    r = world(kind, finished=raise_by(5000, "fin"), work_s=10, card_cap=2)
    s = again(kind, advance(start(kind, r), r, 10), r, 10)
    s = advance(s, r, 19)
    assert cap_of(s, r) == 10 * Q
    s = advance(s, r, 20)
    assert cap_of(s, r) == 15 * Q
    both = world(kind, outcome=raise_by(5000, "out"), finished=raise_by(5000, "fin"), work_s=10)
    s = advance(start(kind, both), both, 10)
    assert cap_of(s, both) == 20 * Q


def retiring_world() -> Rules:
    """old (cap 1) raises by 50% when it completes; ret (cap 1) retires old and raises by 50% in one outcome."""
    opening = [Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.STORE, Y), Unlock(UnlockKind.ACTION, SRC),
               Unlock(UnlockKind.CARD, OLD), Unlock(UnlockKind.CARD, RET)]
    return rules([StoreDef(X, 10 * Q, 0), StoreDef(Y, 10 * Q, 0)], standing=[StandingDef(SRC, makes=(Flow(X, Q),))],
                 cards=[CardDef(OLD, 10, cap=1, outcome=raise_by(5000, "old")),
                        CardDef(RET, 10, cap=1, outcome=Outcome(unlocks=(Unlock(UnlockKind.RETIRED, OLD),),
                                                                modifiers=(cap_add(5000, "ret"),)))],
                 opening=opening)


def test_retiring_the_granter_keeps_its_raise_and_lands_the_retirers_at_once() -> None:
    r = retiring_world()
    s = advance(tap(new_save(r), r, 0, OLD), r, 10)
    assert cap_of(s, r) == 15 * Q and OLD in [c.card for c in view(s, r).completed]
    s = advance(tap(s, r, 10, RET), r, 19)
    assert cap_of(s, r) == 15 * Q
    s = advance(s, r, 20)
    assert cap_of(s, r) == 20 * Q
    assert OLD in [c.card for c in view(s, r).completed]
    s = advance(s, r, 5000)
    assert cap_of(s, r) == 20 * Q and val(s, r, X) == 20 * Q


# ---- codec, split ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_codec_and_split_hold_across_a_landed_raise(kind: str) -> None:
    r = world(kind, outcome=raise_by(5000))
    s = start(kind, r)
    chain = s
    for t in (10, 29, 30, 31, 35, 36, 100):
        chain = advance(chain, r, t)
        assert chain == advance(s, r, t)
        back = decode(encode(chain, r), r)
        assert back == chain and cap_of(back, r) == cap_of(chain, r)


# ---- validation: it may only raise -------------------------------------------------------------------------------

def outcome_rules(place: str, m: Modifier) -> Rules:
    o = Outcome(modifiers=(m,))
    if place == "trigger":
        return world("standing-tap", triggers=(TriggerDef(TriggerId("t0"), AfterTime(5), o),))
    return world("standing-tap", outcome=o if place == "outcome" else Outcome(),
                 finished=o if place == "finished" else Outcome())


PLACES = ["outcome", "finished", "trigger"]


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("m", [cap_add(-1), cap_mul(BP - 1), cap_mul(0), cap_add(5000, "u", StoreId("nope"))],
                         ids=["add -1", "mul below BP", "mul 0", "unknown store"])
def test_a_lowering_or_stray_cap_modifier_is_invalid_rules(place: str, m: Modifier) -> None:
    with pytest.raises(InvalidRulesError):
        validate_rules(outcome_rules(place, m))


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("m", [cap_add(0), cap_add(1), cap_mul(BP), cap_mul(BP + 1)],
                         ids=["add 0", "add 1", "mul BP", "mul BP+1"])
def test_the_boundary_of_raising_is_valid(place: str, m: Modifier) -> None:
    validate_rules(outcome_rules(place, m))


# ---- every place the store's cap is read -------------------------------------------------------------------------

def test_a_lump_landed_by_an_outcome_is_clamped_at_the_raised_cap() -> None:
    """Outcome.stores are "clamped at cap": the cap now. x holds 8 items, a trigger adds 4 at t=5, the cap is 15."""
    o = Outcome(stores=(Amount(X, 4 * Q),))
    r = rules([StoreDef(X, 10 * Q, 8 * Q), StoreDef(Y, 10 * Q, 0)],
              triggers=[TriggerDef(TriggerId("t0"), AfterTime(5), o)])
    s = advance(new_save(r, (cap_add(5000),)), r, 6)
    assert val(s, r, X) == 12 * Q
    plain = advance(new_save(r), r, 6)
    assert val(plain, r, X) == 10 * Q
    r2 = rules([StoreDef(X, 10 * Q, 10 * Q), StoreDef(Y, 10 * Q, 0)],
               triggers=[TriggerDef(TriggerId("t0"), AfterTime(5), Outcome(stores=(Amount(X, 9 * Q),)))])
    assert val(advance(new_save(r2, (cap_add(5000),)), r2, 6), r2, X) == 15 * Q


@pytest.mark.parametrize("stack, resume_at, kind", [
    ((), 6600, EventKind.STORE_LIMIT),  # the cap is the resume level: the store's limit falls at the same second, first
    ((cap_add(5000),), 7800, EventKind.RESUME), ((cap_mul(20_000),), 7800, EventKind.RESUME),
], ids=["no raise", "+50%", "x2"])
def test_a_dry_pause_resumes_at_an_hours_cost_or_the_cap_now(stack: tuple[Modifier, ...], resume_at: int,
                                                             kind: EventKind) -> None:
    """The consumer costs 12 items/h, so an hour's cost is 12 items; x (base cap 10) starts at 1 item with 6 items/h
    coming in. It runs dry at 600 s and pauses, and resumes when x is back to min(cap now, 12 items)."""
    con, src = ActionId("con"), ActionId("src")
    r = rules([StoreDef(X, 10 * Q, Q), StoreDef(Y, 10 * Q, 0)],
              standing=[StandingDef(src, makes=(Flow(X, 6000),)), StandingDef(con, costs=(Flow(X, 12_000),))])
    s = advance(new_save(r, stack), r, 600)
    assert val(s, r, X) == 0
    ev = next_event(s, r)
    assert ev is not None and (ev.time, ev.kind) == (resume_at, kind)
    assert val(advance(s, r, resume_at), r, X) == (12 * Q if kind is EventKind.RESUME else 10 * Q)


def test_a_chip_cannot_aim_at_a_cap() -> None:
    """A chip's effect is true only while it is shown, so a cap raised by one could fall under a full store: refused
    for any store and any kind, while the same chip aimed at a rate is valid."""
    cond = AtLeast(StoreValue(Y), Q, Q)
    for m in (cap_add(5000, "warm"), cap_mul(15_000, "warm"), cap_add(0, "warm"), cap_add(5000, "warm", Y)):
        r = rules([StoreDef(X, 10 * Q, 0), StoreDef(Y, 10 * Q, 2 * Q)], chips=[ChipDef(ChipId("warm"), cond, (m,))])
        with pytest.raises(InvalidRulesError):
            validate_rules(r)
    ok = rules([StoreDef(X, 10 * Q, 0), StoreDef(Y, 10 * Q, 2 * Q)], standing=[StandingDef(SRC, makes=(Flow(X, Q),))],
               chips=[ChipDef(ChipId("warm"), cond, (mul(RateRef(SRC, FlowKind.MAKE, X), 15_000, "warm"),))])
    validate_rules(ok)


# ---- an outcome's raise lands at every completion ---------------------------------------------------------------

@pytest.mark.parametrize("kind", ["standing-tap", "standing-mix"])
def test_an_outcome_raise_on_a_repeating_card_stacks_per_completion(kind: str) -> None:
    """An outcome lands at each completion like any other, so a card with cap 3 whose outcome adds 50% is +50%, +100%,
    then +150%; `finished` still lands once."""
    r = world(kind, outcome=raise_by(5000, "out"), work_s=10, card_cap=3)
    s = advance(start(kind, r), r, 9)
    assert cap_of(s, r) == 10 * Q
    s = advance(s, r, 10)
    assert cap_of(s, r) == 15 * Q
    s = again(kind, s, r, 10)
    assert cap_of(advance(s, r, 19), r) == 15 * Q
    s = advance(s, r, 20)
    assert cap_of(s, r) == 20 * Q
    s = again(kind, s, r, 20)
    s = advance(s, r, 30)
    assert cap_of(s, r) == 25 * Q
    assert len(s.modifiers) == 3
    assert cap_of(advance(s, r, 1000), r) == 25 * Q


# ---- the starting stack is validated like the rules' placements --------------------------------------------------

@pytest.mark.parametrize("m", [cap_add(-1), cap_mul(BP - 1), cap_mul(0)], ids=["add -1", "mul below BP", "mul 0"])
def test_a_lowering_cap_entry_in_the_starting_stack_is_refused(m: Modifier) -> None:
    with pytest.raises(InvalidVerbError):
        new_save(world("standing-tap"), (cap_add(5000), m))


@pytest.mark.parametrize("m", [cap_add(0), cap_mul(BP)], ids=["add 0", "mul BP"])
def test_a_non_lowering_cap_entry_in_the_starting_stack_is_accepted(m: Modifier) -> None:
    r = world("standing-tap")
    assert cap_of(new_save(r, (m,)), r) == 10 * Q


# ---- fills_at for a full store ------------------------------------------------------------------------------------

def test_fills_at_of_a_store_at_its_cap_is_when_it_got_there() -> None:
    """The ledger's rule (reach_time at the cap): a store already at the cap reads the start of its segment, which a
    sample carries forward to the sample's time (not when the store filled; its maker's net still shows the overflow),
    and after a raise it reads the new fill time."""
    r = world("standing-tap")
    for t in (10, 50):
        line = ledger(advance(new_save(r), r, t), r, X)
        assert full(line) and line.segment.rate == 0 and line.net_per_hour > 0
        assert line.fills_at == line.segment.start == t
    full_from_start = world("standing-tap", initial=10 * Q)
    line = ledger(new_save(full_from_start), full_from_start, X)
    assert full(line) and line.fills_at == 0
    raised = ledger(new_save(r, (cap_add(5000),)), r, X)
    assert raised.fills_at == 15
