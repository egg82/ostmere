"""Invariants 80 (flow), 82 (odds move one way) and 85 (a tap keeps its odds), from DESIGN.txt, "FIGHTS", alone. The
odds are read only through explain(): the MUL_BP entry sourced "odds:<runner>" on a runner's lost line."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, FlowKind, Modifier, ModifierKind, Outcome, RateRef, Rules, Runner, Save,
    SideStrength, SourceId, StoreId, TapCard, ThreatStrength, TriggerDef, TriggerId, advance, decide, explain, new_save, strength, value,
)
from contract_gen import few
from fight_world import (
    BAIT, COST, FOUGHT, GRAIN, HAND, HUNT, LOOT, LOST, RAID, RLOST, WOLF, hand_odds, in_mix, loss_bp, started, twin, world,
)

MAKE = FlowKind.MAKE
ME, THEM = SideStrength(HAND), ThreatStrength(WOLF)


def odds_on(s: Save, r: Rules, runner: Runner, store: StoreId) -> int:
    """The loss share a runner's lost line carries: the one entry sourced 'odds:<runner>'."""
    found = [m.amount_bp for m in explain(s, r, RateRef(runner, MAKE, store)).muls if m.source == SourceId(f"odds:{runner}")]
    assert len(found) == 1
    return found[0]


@given(st.integers(0, 12), st.integers(1, 12), st.sampled_from([3_000, 6_000, 10_000]), st.integers(1, 4_000))
@few(25)
def test_a_fight_pays_what_its_twin_with_the_odds_written_by_hand_pays(p: int, t: int, share: int, secs: int):
    """Invariant 80: every store, a flow or a lump, a card or a standing fight, equals the twin's at every probe."""
    r = world(p, t)
    plain = twin(r)
    a, b = started(r, share_bp=share), started(plain, *hand_odds(p, t), share_bp=share)
    for at in sorted({secs // 3, secs // 2, secs}):
        for st_ in r.stores:
            assert value(a, r, st_.id, at) == value(b, plain, st_.id, at), (st_.id, at)


def test_the_twin_is_not_vacuous_odds_matter_and_the_tallies_run():
    """Control for 80: with no odds written the twin pays differently, and the fight's lines are non-zero."""
    r = world(2, 5)
    a, bare = started(r), started(twin(r))
    assert value(a, r, LOOT, 1000) != value(bare, twin(r), LOOT, 1000)
    assert value(a, r, LOST, 1000) > 0 and value(a, r, RLOST, 1000) > 0 and value(a, r, FOUGHT, 1000) > 0


def test_the_odds_entry_is_the_documented_share_rounded_up_and_a_win_is_the_rest():
    r = world(2, 5)                                # 5/7 of BP is 7142.86: rounded up to 7143
    s = new_save(r)
    assert odds_on(s, r, RAID, RLOST) == 7_143 == loss_bp(2, 5)
    win = [m for m in explain(s, r, RateRef(RAID, MAKE, GRAIN)).muls if m.source == SourceId("odds:raid")]
    assert [m.amount_bp for m in win] == [BP - 7_143]
    assert odds_on(new_save(world(0, 3)), world(0, 3), RAID, RLOST) == BP                  # no strength loses every fight
    assert odds_on(new_save(world(4, 4)), world(4, 4), RAID, RLOST) == 5_000               # equal strengths lose half
    assert odds_on(new_save(world(16, 4)), world(16, 4), RAID, RLOST) == 2_000            # four to one: one in five


def test_costs_that_are_not_losses_and_the_fought_tally_carry_no_odds():
    r = world(2, 5)
    s = new_save(r)
    for ref in (RateRef(RAID, FlowKind.COST, COST), RateRef(RAID, MAKE, FOUGHT), RateRef(HUNT, FlowKind.COST, BAIT)):
        assert not [m for m in explain(s, r, ref).muls if str(m.source).startswith("odds:")]


@given(st.integers(0, 30), st.integers(1, 30), st.sampled_from(["side", "threat"]), st.integers(0, 20_000))
@few(40)
def test_a_raising_entry_never_moves_the_odds_the_wrong_way_and_they_stay_in_bounds(p: int, t: int, who: str, bp: int):
    """Invariant 82. Side entries are ADD_BP >= 0 or MUL_BP >= BP; a threat's likewise."""
    r = world(p, t)
    before = odds_on(new_save(r), r, RAID, RLOST)
    target = ME if who == "side" else THEM
    for kind, amount in ((ModifierKind.ADD_BP, bp), (ModifierKind.MUL_BP, BP + bp)):
        s = new_save(r, (Modifier(target, kind, amount, SourceId("e")),))
        after = odds_on(s, r, RAID, RLOST)
        assert 0 < after <= BP and 0 < before <= BP
        assert after <= before if who == "side" else after >= before
        assert after == loss_bp(strength(s, r, ME), strength(s, r, THEM))


def ramp_to(p_after: int) -> TriggerDef:
    """At t=30 the side gains p_after - 1 times its base (base 1 -> p_after)."""
    return TriggerDef(TriggerId("up"), AfterTime(30), Outcome(modifiers=(
        Modifier(ME, ModifierKind.ADD_BP, (p_after - 1) * BP, SourceId("spear")),)))


def test_a_tap_pays_the_odds_it_started_at_even_when_a_spear_lands_mid_tap():
    """Invariant 85, with its control: the same appended entry changes a mix's odds at once and the next tap's."""
    r = world(1, 4, triggers=(ramp_to(16),))       # at 30s the side goes 1 -> 16: loss 8000 -> 2000
    start, later = loss_bp(1, 4), loss_bp(16, 4)
    assert start != later
    tapped = decide(new_save(r), r, 0, TapCard(HUNT))
    mid = advance(tapped, r, 40)
    assert odds_on(mid, r, HUNT, LOST) == start != later
    assert odds_on(mid, r, RAID, RLOST) == later                                # a standing fight is live
    done = advance(tapped, r, 100)                                              # the tap lands at 100s of work
    kept_pay = value(done, r, LOST, 100)
    assert abs(kept_pay - Q * start // BP) <= 100                               # one fight lost at 80%, to rounding
    after = advance(in_mix(done, r), r, 200)                                    # once the tap has landed the odds are live
    assert abs(value(after, r, LOST, 200) - kept_pay - Q * later // BP) <= 100
    again = decide(done, r, 100, TapCard(HUNT))
    assert odds_on(again, r, HUNT, LOST) == later                               # the next tap reads the new odds
    mixed = advance(started(r), r, 40)
    assert odds_on(mixed, r, HUNT, LOST) == later                               # control: in the mix they are live
