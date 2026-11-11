"""Invariant 111, the mix half (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "The held share h(c)", rules 2 and
3; "Completion and locking"): a card in the running mix of its own layer holds its flattened share when its Run is FULL,
and nothing while it is in a mix that does not run, locked, on an unjoined lane, greyed,
completed or retired. The running mix is read as the engine runs it (an order's over the player's), never off
save.active alone."""
from ashfall_app.engine import (
    AfterTime, CardShare, DeleteMix, LaneSpeed, Mix, MixId, Modifier, ModifierKind, Order, Outcome,
    SaveMix, SetOrders, SourceId, SwitchMix, TriggerDef, TriggerId, Unlock, UnlockKind, advance, decide, new_save,
)
from held_world import (
    GA, GB, GCAP, GH, GH2, GLK, HM, hands, held_mods, held_of, ja, jb, kills, opening_all, raised, town, world,
)
from town_mix_world import LA, TM, orders

M2 = MixId("m2")


def trigger(at: int, outcome: Outcome) -> TriggerDef:
    return TriggerDef(TriggerId(f"t{at}"), AfterTime(at), outcome)


@kills(1, 2, 4, 13, 14, 17, 22)
def test_an_orders_mix_runs_over_the_players_and_the_players_holds_nothing_meanwhile():
    """The player runs hm (gh); an order switches to m2 (gh2) from 1000: before it gh holds, after it gh2 holds and gh
    does not (save.active still names hm)."""
    r = world()
    s = hands(r, (GH, 5000))
    s = decide(s, r, 0, SaveMix(Mix(M2, ((CardShare(GH2, 5000)),))))
    s = decide(s, r, 0, SetOrders((Order(AfterTime(1000), SwitchMix(M2)),)))
    before, after = advance(s, r, 999), advance(s, r, 1000)
    assert (held_of(before, r, GH), held_of(before, r, GH2)) == ([2500], [])
    assert after.active == HM
    assert (held_of(after, r, GH), held_of(after, r, GH2)) == ([], [1000])


@kills(1, 2, 4, 12, 14, 17)
def test_a_mix_the_player_saved_but_nothing_runs_holds_nothing():
    """A saved mix that is not the player's active one and that no order runs: its guard holds nothing."""
    r = world()
    s = decide(new_save(r), r, 0, SaveMix(Mix(HM, (CardShare(GH, 5000),))))
    assert held_mods(advance(s, r, 50), r) == ()
    s = decide(s, r, 50, SwitchMix(HM))
    assert held_of(s, r, GH) == [2500]
    s = decide(s, r, 60, DeleteMix(HM))
    assert held_mods(s, r) == () and s.active is None



@kills(1, 2, 4, 12, 14, 17)
def test_the_town_stops_holding_when_its_mix_stops_running():
    """ga holds 4000 * 4000 // BP while la's person runs the town mix; with the town's order gone nothing runs it."""
    r = world((ja(),))
    s = town(r, (GA, 4000))
    assert held_of(advance(s, r, 20), r, GA) == [1600]
    gone = decide(advance(s, r, 20), r, 20, orders())
    assert held_mods(gone, r) == () and held_mods(advance(gone, r, 90), r) == ()


@kills(1, 4, 14, 17)
def test_a_share_set_to_zero_by_a_save_mix_drops_the_entry_at_that_instant():
    r = world((ja(),))
    s = town(r, (GA, 4000))
    assert held_of(s, r, GA) == [1600]
    zero = decide(s, r, 30, SaveMix(Mix(TM, (CardShare(GA, 0),))))
    assert held_mods(zero, r) == () and raised(zero, r) == 0


@kills(4, 17)
def test_a_locked_card_in_the_town_mix_holds_nothing_until_it_is_unlocked():
    """glk (1000) is la's join card, so it has the town share BP while locked; it holds nothing before its unlock at
    50 and its whole 1000 after (the share a join gives is BP)."""
    unlock = trigger(50, Outcome(unlocks=(Unlock(UnlockKind.CARD, GLK),)))
    base = world((ja(0, GLK), unlock))
    r = world((ja(0, GLK), unlock), opening_all(base, GLK))
    s = advance(new_save(r), r, 0)
    assert s.mixes and held_mods(advance(s, r, 49), r) == ()
    assert held_of(advance(s, r, 50), r, GLK) == [1000]


@kills(1, 4, 14, 17, 22)
def test_a_card_on_an_unjoined_lane_holds_nothing_until_its_person_joins():
    """gb is lb's join card: nothing before lb's join (100), its whole share's worth after; ga on la holds meanwhile."""
    r = world((ja(), jb(100)))
    s = town(r, (GA, 1000))
    assert held_of(advance(s, r, 99), r, GB) == [] and held_of(advance(s, r, 99), r, GA) == [400]
    assert held_of(advance(s, r, 100), r, GB) == [2000]


@kills(1, 2, 4, 10, 12, 13, 14, 17, 22)
def test_a_greyed_mix_holds_nothing_for_any_of_its_cards():
    """gcap (cap 1, 20 s) and gh share the hands' mix at half each: gcap's work takes 40 s at half. Until then both hold;
    at 40 gcap completes, the mix greys and neither holds; gcap is completed for good."""
    r = world()
    s = hands(r, (GH, 5000), (GCAP, 5000))
    live = advance(s, r, 39)
    assert (held_of(live, r, GH), held_of(live, r, GCAP)) == ([2500], [1250])
    greyed = advance(s, r, 40)
    assert greyed.active == HM and held_mods(greyed, r) == ()
    assert held_mods(advance(s, r, 400), r) == ()


@kills(1, 2, 4, 10, 12, 13, 14, 17, 22)
def test_a_retired_card_greys_its_mix_and_holds_nothing_with_it():
    base = world()
    r = world((trigger(50, Outcome(unlocks=(Unlock(UnlockKind.RETIRED, GH),))),), opening_all(base))
    s = hands(r, (GH, 5000), (GH2, 3000))
    assert held_of(advance(s, r, 49), r, GH) == [2500] and held_of(advance(s, r, 49), r, GH2) == [600]
    assert held_mods(advance(s, r, 50), r) == ()


@kills(1, 14, 17, 22)
def test_a_work_speed_changes_how_fast_the_bar_fills_never_the_share():
    """la's LaneSpeed is doubled at 50: ga holds the same 1600 before and after (no entry follows a rate)."""
    speed = trigger(50, Outcome(modifiers=(Modifier(LaneSpeed(LA), ModifierKind.MUL_BP, 20000, SourceId("tool")),)))
    r = world((ja(), speed))
    s = town(r, (GA, 4000))
    assert held_of(advance(s, r, 49), r, GA) == [1600] == held_of(advance(s, r, 50), r, GA) == held_of(advance(s, r, 900), r, GA)
