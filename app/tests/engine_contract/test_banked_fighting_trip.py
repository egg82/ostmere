"""Banked time with a fight on the trip (engine DESIGN.txt, "BANKED TIME", "A fighting trip", and "FIGHTS"): a trip is an
uncapped card with inputs; give it FightDef(the hands' side, ...) and its supplies are taken whole whatever the odds,
its makes (a flow and a lump) scale by the share won, and its finds, which read CardCount, count trips made, won or
lost. Written from the contract and the public interface only, on fixture rules.

Fixture: supply store S (10 per trip), trip T (work_s 3600; makes W by flow and Y by lump; FightDef on the hands' side
with tally L), finds F at the nth trip. A side of strength P against a threat of T fights at loss share
ceil(BP * T / (T + P)); the pairs below give whole shares, so every expected number is an exact integer.
Each assertion has a control: the same helper on a premise that must move it (engine mutants: MUTANTS.txt,
"Fighting trips")."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, AtLeast, CardCount, CardDef, CardId, CardShare, EventKind, FightDef, Flow,
    FlowKind, Mix, MixId, Outcome, PacingCurve, RateRef, Rules, Save, SaveMix, SideDef, SideId, SkillDef, SkillId,
    StoreDef, StoreId, SwitchMix, TapCard, ThreatDef, ThreatId, TriggerDef, TriggerId, advance, decide, explain,
    new_save, next_event, per_hour, value, view,
)

S, W, Y, L, F = (StoreId(n) for n in "swylf")
TRIP = CardId("trip")
HAND, WOLF = SideId("hand"), ThreatId("wolf")
MIX = MixId("m")
WORK_S = 3600
SUPPLY = 10 * Q
S0 = 1000 * Q
FLOW = per_hour(4)
LUMP = 6 * Q

# (side strength, threat strength) -> (loss_bp, win_bp), each worked from the documented formula by hand.
ODDS = {
    "lose-all": (0, 3, BP, 0),
    "three-to-one-against": (1, 3, 7_500, 2_500),
    "even": (3, 3, 5_000, 5_000),
    "three-to-one-for": (9, 3, 2_500, 7_500),
}
CASES = [pytest.param(p, t, loss, win, id=name) for name, (p, t, loss, win) in ODDS.items()]


def world(p: int, t: int, *, fight: bool = True, finds: int = 0) -> Rules:
    stores = (StoreDef(S, S0, S0),) + tuple(StoreDef(x, 10**6 * Q) for x in (W, Y, L, F))
    trip = CardDef(TRIP, WORK_S, makes=(Flow(W, FLOW),), inputs=(Amount(S, SUPPLY),),
                   outcome=Outcome(stores=(Amount(Y, LUMP),)), fight=FightDef(HAND, WOLF, L) if fight else None)
    triggers = tuple(TriggerDef(TriggerId(f"find{n}"), AtLeast(CardCount(TRIP), n, n), Outcome(stores=(Amount(F, Q),)))
                     for n in range(1, finds + 1))
    return Rules(stores=stores, skills=(SkillDef(SkillId("k")),), standing=(), curve=PacingCurve((10**15,)),
                 cards=(trip,), triggers=triggers, sides=(SideDef(HAND, p),), threats=(ThreatDef(WOLF, t),))


def mixed(r: Rules, share_bp: int = BP) -> Save:
    s = decide(new_save(r), r, 0, SaveMix(Mix(MIX, (CardShare(TRIP, share_bp),))))
    return decide(s, r, 0, SwitchMix(MIX))


def trips(s: Save, r: Rules) -> int:
    return next(c for c in view(s, r).cards if c.card == TRIP).completions


def at(s: Save, r: Rules, store: StoreId, t: int) -> int:
    return value(s, r, store, t)


PROBES = [360, 1800, 3600, 7200, 10_800, 36_000]


# ---- supplies are taken whole ----------------------------------------------------------------------------------

@pytest.mark.parametrize("p,t,loss,win", CASES)
def test_the_supplies_are_taken_whole_whatever_the_odds(p: int, t: int, loss: int, win: int):
    """An input is a cost line of its amount per work_s at the mix share; no odds scale it, so the store falls by 10 an
    hour of full-speed work at every probe, as the fight-free trip's does."""
    r, plain = world(p, t), world(p, t, fight=False)
    s, bare = mixed(r), mixed(plain)
    for sec in PROBES:
        assert at(s, r, S, sec) == S0 - SUPPLY * sec // WORK_S == at(bare, plain, S, sec)


@pytest.mark.parametrize("p,t,loss,win", CASES)
def test_no_odds_entry_sits_on_the_supply_line(p: int, t: int, loss: int, win: int):
    """The explanation of the input's cost line names no 'odds:' source, so a lost trip spent what a won one did."""
    r = world(p, t)
    muls = explain(new_save(r), r, RateRef(TRIP, FlowKind.COST, S)).muls
    assert [m for m in muls if str(m.source).startswith("odds:")] == []


def test_control_the_makes_do_move_with_the_odds_where_the_supplies_do_not():
    """Control: across the four odds the supply store at one probe is one value and the make store is four, so the
    equality above is not a store that never moves with anything."""
    supplies: set[int] = set()
    makes: set[int] = set()
    for p, t, _, _ in ODDS.values():
        r = world(p, t)
        s = mixed(r)
        supplies.add(at(s, r, S, 7200))
        makes.add(at(s, r, W, 7200))
    assert len(supplies) == 1 and supplies != {S0} and len(makes) == len(ODDS)


# ---- makes scale by the share won -------------------------------------------------------------------------------

@pytest.mark.parametrize("share", [BP, 5_000, 2_500])
@pytest.mark.parametrize("p,t,loss,win", CASES)
def test_the_make_line_and_the_lump_pay_the_share_won_of_what_the_fight_free_trip_pays(
        p: int, t: int, loss: int, win: int, share: int):
    """A flow pays FLOW * share * win per second; the lump (6 per work_s of full-speed work) likewise; the lost tally
    pays one per trip at the share lost."""
    r = world(p, t)
    s = mixed(r, share)
    for sec in PROBES:
        assert at(s, r, W, sec) == FLOW * share * win * sec // (BP * BP)
        assert at(s, r, Y, sec) == LUMP * share * win * sec // (BP * BP * WORK_S)
        assert at(s, r, L, sec) == Q * share * loss * sec // (BP * BP * WORK_S)


@pytest.mark.parametrize("p,t,loss,win", CASES)
def test_every_trip_is_won_or_lost_in_whole(p: int, t: int, loss: int, win: int):
    """Over n trips the lump and the tally add back to the n trips made: n = Y / lump + L / unit, wins and losses
    partitioning the fights."""
    r = world(p, t)
    s = mixed(r)
    sec = 10 * WORK_S
    assert trips(advance(s, r, sec), r) == 10
    assert at(s, r, Y, sec) * Q + at(s, r, L, sec) * LUMP == 10 * LUMP * Q


def test_a_trip_that_loses_every_fight_still_spends_its_supplies_and_pays_no_make():
    """The weakest side: the make line and lump are zero, the supplies are not, and the trips are counted."""
    r = world(0, 3)
    s = advance(mixed(r), r, 5 * WORK_S)
    assert (at(s, r, W, s.time), at(s, r, Y, s.time)) == (0, 0)
    assert at(s, r, S, s.time) == S0 - 5 * SUPPLY and trips(s, r) == 5 and at(s, r, L, s.time) == 5 * Q


# ---- finds count trips made -------------------------------------------------------------------------------------

def find_times(r: Rules, s: Save, taps: bool, upto: int) -> list[int]:
    """The seconds at which the find store rose, walking event to event (a tap is re-issued as each one ends)."""
    out: list[int] = []
    while True:
        e = next_event(s, r)
        if e is None or e.time > upto:
            return out
        before = value(s, r, F, s.time)
        s = advance(s, r, e.time)
        if value(s, r, F, s.time) > before:
            out.append(e.time)
        if taps and e.kind == EventKind.TAP_DONE:
            s = decide(s, r, s.time, TapCard(TRIP))


@pytest.mark.parametrize("p,t,loss,win", CASES)
def test_finds_land_at_the_nth_trip_made_whether_it_was_won_or_lost(p: int, t: int, loss: int, win: int):
    """Finds 1..3 fire at 3600, 7200, 10800 s at every odds, the weakest side included, and the trips counted agree."""
    r = world(p, t, finds=3)
    assert find_times(r, mixed(r), False, 12_000) == [3_600, 7_200, 10_800]
    done = advance(mixed(r), r, 10_800)
    assert (trips(done, r), at(done, r, F, 10_800)) == (3, 3 * Q)


@pytest.mark.parametrize("p,t,loss,win", CASES)
def test_finds_land_at_the_same_instants_when_the_trip_is_tapped(p: int, t: int, loss: int, win: int):
    """A tapped trip runs the odds it started at and counts its trip on landing: the same three seconds."""
    r = world(p, t, finds=3)
    tapped = decide(new_save(r), r, 0, TapCard(TRIP))
    assert find_times(r, tapped, True, 12_000) == [3_600, 7_200, 10_800]


def test_control_the_lost_tally_would_time_the_finds_differently():
    """Control: the tally of lost fights reaches its first whole unit at a time that depends on the odds, and not at 3600
    except for the side that loses every fight; so a find read off it would move where this suite says it stays."""
    reached: list[int] = []
    for p, t, _, _ in ODDS.values():
        r = world(p, t)
        s = mixed(r)
        reached.append(next(sec for sec in range(WORK_S, 40 * WORK_S, WORK_S) if at(s, r, L, sec) >= Q))
    assert reached[0] == WORK_S and len(set(reached)) > 1 and reached == sorted(reached)


def test_the_twin_without_a_fight_counts_the_same_trips_and_finds():
    """A fight does not change the trip count: fight-free and fighting trips find at the same seconds."""
    for p, t, _, _ in ODDS.values():
        r, plain = world(p, t, finds=3), world(p, t, fight=False, finds=3)
        assert find_times(r, mixed(r), False, 12_000) == find_times(plain, mixed(plain), False, 12_000)
