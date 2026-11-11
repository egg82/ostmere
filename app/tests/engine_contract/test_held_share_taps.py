"""Invariant 111, the tap half (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "The held share h(c)", rules 1 and
the One bar clause; "Cut-in and interrupt"): h(c) = BP while any lane holds a tap of c, whoever ran it, bounded or
repeating; a share the tap yields holds nothing; a task interrupted with its work kept holds nothing until it is tapped
again; a card both tapped and in the running mix counts once, at BP."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    AfterTime, AtLeast, CardCount, Order, QueueEntry, SetOrders, SetQueue, TapCard, advance, decide, new_save,
)
from held_world import (
    BUILD, GA, GA2, GAC, GB, GH, PH, STEP, STEPG, flat, hands, held_of, ja, kills, raised, town, world,
)
from town_mix_world import B1, TOWN_RULE, always, orders


def queued() -> SetQueue:
    return SetQueue((QueueEntry(TapCard(BUILD), AtLeast(CardCount(BUILD), 1, 1)),))


@kills(14, 17)
def test_a_card_the_queue_taps_holds_its_whole_amount():
    r = world()
    s = decide(new_save(r), r, 0, queued())
    assert held_of(advance(s, r, 50), r, BUILD) == [3500]


@kills(14, 17, 22)
def test_a_card_a_rule_taps_holds_its_whole_amount_through_its_completions():
    """gh is 100 s; the always rule taps it again at each landing, and at 100, 200 it is held as at 50 and 150."""
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(GH)),)))
    for t in (50, 99, 100, 150, 200, 250):
        assert held_of(advance(s, r, t), r, GH) == [5000], t


@kills(14, 17, 22)
@given(t=st.integers(0, 400))
def test_a_ruled_lanes_repeating_task_holds_its_whole_amount_at_every_instant(t: int):
    """gb (10 s a completion, lane lb never joined) tapped by lb's always rule: held at BP before, at and after each
    completion, completions included."""
    r = world()
    s = decide(new_save(r), r, 0, orders(always(GB)))
    assert held_of(advance(s, r, t), r, GB) == [2000]


@kills(2, 4, 14, 17, 22)
def test_a_capped_one_off_on_a_ruled_lane_holds_until_its_cap_completion():
    """gac (20 s, cap 1) on lane la, tapped by la's always rule: held at 19, gone at the completion that reaches its cap."""
    r = world()
    s = decide(new_save(r), r, 0, orders(always(GAC)))
    assert held_of(advance(s, r, 19), r, GAC) == [4000]
    assert held_of(advance(s, r, 20), r, GAC) == [] and held_of(advance(s, r, 80), r, GAC) == []


@kills(2, 4, 14, 17, 22)
def test_a_lane_whose_rule_moves_to_another_card_stops_holding_the_old_one():
    """lb's always rule taps gb (10 s a completion); the player's new orders put b1 there: from the next landing on gb
    holds nothing."""
    r = world()
    s = decide(new_save(r), r, 0, orders(always(GB)))
    assert held_of(advance(s, r, 3), r, GB) == [2000]
    s = decide(advance(s, r, 3), r, 3, orders(always(B1)))
    assert held_of(advance(s, r, 25), r, GB) == [] and raised(advance(s, r, 25), r) == 0


@kills(1, 7, 14, 17, 22)
def test_a_card_tapped_while_in_the_running_mix_counts_once_at_bp():
    """gh at 3000 in the hands' mix holds 1500; tapped, it holds the whole 5000, not 5000 + 1500 and not 6500; once
    the tap lands (100) it holds its share again."""
    r = world()
    s = hands(r, (GH, 3000))
    assert held_of(s, r, GH) == [1500]
    s = decide(s, r, 0, TapCard(GH))
    for t in (0, 60, 99):
        assert held_of(advance(s, r, t), r, GH) == [5000], t
    assert held_of(advance(s, r, 100), r, GH) == [1500]


@kills(1, 2, 4, 6, 12, 13, 14, 17)
def test_a_hands_tap_over_the_hands_mix_yields_the_shares_it_holds_nothing():
    """gh in the hands' mix at 5000 holds 2500; a tap of the plain card ph takes the hands for 100 s and yields it."""
    r = world()
    s = decide(advance(hands(r, (GH, 5000)), r, 10), r, 10, TapCard(PH))
    for t in (10, 60, 109):
        a = advance(s, r, t)
        assert held_of(a, r, GH) == [] and raised(a, r) == 0, t
    assert held_of(advance(s, r, 110), r, GH) == [2500]


@kills(1, 2, 4, 6, 14, 17, 22)
def test_a_rules_tap_on_a_joined_lane_yields_that_persons_shares_and_holds_its_own():
    """la's person (joined) holds ga 4000 and ga2 3000 by their shares (1600 + 900); la's always rule taps the capped
    gac for 20 s: gac holds its whole 4000 and the two shares hold nothing; after 20 they hold theirs again."""
    r = world((ja(),))
    s = decide(town(r, (GA, 4000), (GA2, 3000)), r, 0, orders(TOWN_RULE, always(GAC)))
    for t in (0, 10, 19):
        a = advance(s, r, t)
        assert (held_of(a, r, GAC), held_of(a, r, GA), held_of(a, r, GA2)) == ([4000], [], []), t
        assert raised(a, r) == 4000
    after = advance(s, r, 20)
    assert (held_of(after, r, GAC), held_of(after, r, GA), held_of(after, r, GA2)) == ([], [flat(4000, 4000)], [flat(3000, 3000)])


@kills(2, 4, 12, 14, 17, 22)
def test_a_task_a_cut_in_interrupts_holds_nothing_until_it_is_tapped_again():
    """The queue's build (held at BP) is interrupted by the plain glowing step at 100 (5 s): the build holds nothing
    meanwhile (its work is kept, not its presence) and holds again at the instant the queue takes it up, at 105."""
    r = world()
    s = advance(decide(new_save(r), r, 0, queued()), r, 100)
    assert held_of(s, r, BUILD) == [3500]
    cut = decide(s, r, 100, TapCard(STEP))
    for t in (100, 102, 104):
        a = advance(cut, r, t)
        assert held_of(a, r, BUILD) == [] and raised(a, r) == 0, t
    assert held_of(advance(cut, r, 105), r, BUILD) == [3500]


@kills(2, 4, 12, 14, 17, 22)
def test_the_card_that_cuts_in_holds_its_own_entry_and_the_interrupted_one_does_not():
    """stepg (1500, glowing, 5 s) cuts into the queue's build at 100: during its 5 s only stepg's entry is held."""
    r = world()
    cut = decide(advance(decide(new_save(r), r, 0, queued()), r, 100), r, 100, TapCard(STEPG))
    for t in (100, 103, 104):
        a = advance(cut, r, t)
        assert (held_of(a, r, STEPG), held_of(a, r, BUILD), raised(a, r)) == ([1500], [], 1500), t
    back = advance(cut, r, 105)
    assert (held_of(back, r, STEPG), held_of(back, r, BUILD)) == ([], [3500])
