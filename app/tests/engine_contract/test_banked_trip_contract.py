"""Banked time (engine DESIGN.txt, "BANKED TIME", invariants 88-89): a trip is an uncapped card with inputs, run in the
mix or tapped. Written from the contract and the public interface only, on fixture rules; every expected number follows
from the documented arithmetic (a mix share s runs a card at s/BP of full speed; an input is a cost line of its amount
per work_s at that speed).

Fixture: supply store S (cap 20 items), trip T (work_s 3600, 10 S per completion, one Y per completion) and an
observer G of Z. Each invariant has a control: the same helper run on a fixture that breaks the assertion's
premise, so the assertion is shown able to fail (the engine-side mutants are in MUTANTS.txt, "banked trips")."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, AtLeast, CardCount, CardDef, CardId, CardShare, EventKind, Flow, FlowKind,
    Mix, MixId, Modifier, ModifierKind, Outcome, PacingCurve, RateRef, Rules, RunKind, Save, SaveMix, SkillDef, SkillId,
    SourceId, StoreDef, StoreId, SwitchMix, TapCard, TriggerDef, TriggerId, advance, decide, explain, explain_work,
    new_save, next_event, per_hour, value, view,
)

S, Y, Z, W = StoreId("s"), StoreId("y"), StoreId("z"), StoreId("w")
T, G = CardId("trip"), CardId("obs")
MIX = MixId("m")
CAP = 20 * Q
TRIP_S = 3600


def world(cards: tuple[CardDef, ...], s0: int, triggers: tuple[TriggerDef, ...] = (), cap: int = CAP) -> Rules:
    stores = (StoreDef(S, cap, s0), StoreDef(Y, 10**6 * Q), StoreDef(Z, 10**9 * Q), StoreDef(W, 10**6 * Q))
    return Rules(stores=stores, skills=(SkillDef(SkillId("k")),), standing=(), curve=PacingCurve((10**15,)),
                 cards=cards, triggers=triggers)


def trip(inputs: tuple[Amount, ...] = (Amount(S, 10 * Q),), makes: tuple[Flow, ...] = ()) -> CardDef:
    return CardDef(T, TRIP_S, inputs=inputs, makes=makes, outcome=Outcome(stores=(Amount(Y, Q),)))


def observer() -> CardDef:
    return CardDef(G, TRIP_S, makes=(Flow(Z, per_hour(3600)),))


def run_mix(r: Rules, shares: tuple[CardShare, ...]) -> Save:
    s = decide(new_save(r), r, 0, SaveMix(Mix(MIX, shares)))
    return decide(s, r, 0, SwitchMix(MIX))


def completions(s: Save, r: Rules, c: CardId = T) -> int:
    return next(cv for cv in view(s, r).cards if cv.card == c).completions


# ---- 88: finds land when the nth trip's work completes -------------------------------------------------------

def find_world(n: int, share_bp: int) -> tuple[Rules, Save]:
    """The nth find doubles G's Z line from then on, so Z after one long advance shows the instant it fired."""
    double = Modifier(RateRef(G, FlowKind.MAKE, Z), ModifierKind.MUL_BP, 20_000, SourceId("find"))
    find = TriggerDef(TriggerId("find"), AtLeast(CardCount(T), n, n), Outcome(modifiers=(double,)))
    r = world((trip(), observer()), 1000 * Q, (find,), cap=1000 * Q)
    return r, run_mix(r, (CardShare(T, share_bp), CardShare(G, BP - share_bp)))


def z_after(share_bp: int, n: int, cuts: list[int], end: int) -> int:
    r, s = find_world(n, share_bp)
    for c in cuts:
        s = advance(s, r, c)
        view(s, r)
    return value(advance(s, r, end), r, Z, end)


def expected_z(share_bp: int, n: int, end: int) -> int:
    """G runs at (BP - share) / BP of per_hour(3600) = 3.6 M units a second, doubled from the find at n * 3600 * BP /
    share seconds (all the shares used divide so the second is whole)."""
    rate = per_hour(3600) * (BP - share_bp) // BP
    fired = n * TRIP_S * BP // share_bp
    return rate * min(end, fired) + 2 * rate * max(0, end - fired)


@given(n=st.integers(1, 3), share=st.sampled_from([2500, 5000, 10_000 - 2500]),
       cuts=st.lists(st.integers(0, 150_000), max_size=4))
def test_the_nth_find_lands_at_the_second_the_nth_trip_completes_for_any_slicing(n: int, share: int, cuts: list[int]):
    """Invariant 88: the find fires at n * work_s * BP / share, however the advance is cut and viewed on the way; the
    expected Z is the exact doubled integral from that second, so a find stamped at a visit shows a different Z."""
    end = 160_000
    assert z_after(share, n, sorted(cuts), end) == expected_z(share, n, end)


def test_control_a_visit_stamped_find_would_show_a_different_z():
    """Control for 88: the Z a find stamped at the visit (here the end) would leave differs from the right one, so the
    assertion above can tell the two apart."""
    end = 160_000
    stamped = per_hour(3600) // 2 * end
    assert stamped != expected_z(5000, 2, end)


def find_times(r: Rules, s: Save, taps: bool, upto: int) -> list[int]:
    """The seconds at which the find store W rose, walking event to event (a tap is re-issued as each one ends)."""
    out: list[int] = []
    while True:
        e = next_event(s, r)
        if e is None or e.time > upto:
            return out
        before = value(s, r, W, s.time)
        s = advance(s, r, e.time)
        if value(s, r, W, s.time) > before:
            out.append(e.time)
        if taps and e.kind == EventKind.TAP_DONE:
            s = decide(s, r, s.time, TapCard(T))


def test_finds_land_at_the_same_instants_whether_the_trip_ran_mixed_or_as_repeated_taps():
    """Invariant 88 (mixed or tapped): a trip mixed at the whole share and a trip tapped over and over do the same total
    work, so finds 1..3 fire at the same seconds, 3600, 7200, 10800."""
    finds = tuple(TriggerDef(TriggerId(f"f{n}"), AtLeast(CardCount(T), n, n), Outcome(stores=(Amount(W, Q),)))
                  for n in (1, 2, 3))
    r = world((trip(),), 1000 * Q, finds, cap=1000 * Q)
    mixed = find_times(r, run_mix(r, (CardShare(T, BP),)), False, 12_000)
    tapped = find_times(r, decide(new_save(r), r, 0, TapCard(T)), True, 12_000)
    assert mixed == tapped == [3600, 7200, 10_800]


# ---- 89: a dry trip sends nothing ----------------------------------------------------------------------------

def dry_world(s0: int, inputs: tuple[Amount, ...] = (Amount(S, 10 * Q),)) -> tuple[Rules, Save]:
    """The trip alone at the whole share, with a make line of its own (one W an hour at full speed) and a lump."""
    r = world((trip(inputs, (Flow(W, per_hour(1)),)),), s0)
    return r, run_mix(r, (CardShare(T, BP),))


def sent_after(r: Rules, s: Save, t0: int, t1: int) -> tuple[int, int, int]:
    """What the trip paid between t0 and t1: make-line units, lump units, and the completions that rose."""
    a, b = advance(s, r, t0), advance(s, r, t1)
    return (value(b, r, W, t1) - value(a, r, W, t0), value(b, r, Y, t1) - value(a, r, Y, t0),
            completions(b, r) - completions(a, r))


def test_a_trip_against_an_empty_store_is_paused_and_sends_nothing_ever():
    """Invariant 89: the store is below one completion's inputs and the trip is paused, so its make line and its lump pay
    nothing and CardCount stays 0, its bar does not move, at any later time. Nothing makes the store, so the pause
    reads SPENT (invariant 133)."""
    r, s = dry_world(0)
    a = advance(s, r, 1)
    assert [p.runner for p in a.pauses] == [T]
    assert explain(a, r, RateRef(T, FlowKind.MAKE, W)).run.kind is RunKind.SPENT
    assert explain_work(a, r, T).per_hour == 0
    assert sent_after(r, s, 1, 600_000) == (0, 0, 0)


def test_a_trip_that_runs_the_supply_dry_stops_paying_from_that_second():
    """Invariant 89: three items in store, the trip drawing ten an hour at the whole share, runs 1080 s (0.3 of a trip,
    no completion) then pauses at the empty store: the make line paid 1080 s of one an hour, then nothing."""
    r, s = dry_world(3 * Q)
    assert sent_after(r, s, 1080, 600_000) == (0, 0, 0)
    assert value(advance(s, r, 600_000), r, W, 600_000) == per_hour(1) * 1080
    assert completions(advance(s, r, 600_000), r) == 0


def test_control_a_trip_with_no_inputs_is_never_paused_and_does_pay():
    """Control for 89: the same trip without inputs is not paused and pays on the same span, so the zero above is the
    pause and not a trip that never pays."""
    r, s = dry_world(0, inputs=())
    assert advance(s, r, 1).pauses == ()
    make, lump, done = sent_after(r, s, 1, 600_000)
    assert make > 0 and lump > 0 and done > 0
