"""Invariants 94, 95 and 97 (engine DESIGN.txt, "THE TOWN'S MIX": "Join", "Why the uncapped always rule becomes the
share", "Rebase"). A join converts a person's uncapped always rule into a share without changing what the person does;
it lands once; a save past a join's trigger gets the same result through a rebase."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, AtLeast, CardId, CardShare, IdKind, Join, LaneId, Mix, Order, Outcome, Rename, StoreValue, SwitchMix,
    RunKind, TapCard, Unlock, UnlockKind, advance, decide, encode, rebase, view,
)
from ashfall_app.engine.renaming import Renamer, renamed_outcome
from town_mix_world import (
    A1, A2, AC, ALWAYS, B1, BIG, LA, LB, TM, TM2, TOWN_RULE, V, X, Y, always, card_view, count, joined, joiner, orders,
    start, stored, sub_rules, sub_save, work_done, world,
)

JOIN_AT = 205
"""Mid-completion of a1's tap (completions land at 10, 20, ...), so a tap is running when the join lands."""
GATE = Order(AtLeast(StoreValue(Y), BIG, BIG), TapCard(AC))
"""A rule on la that is not an always rule and never acts here."""
SETUP = (GATE, always(A1), always(B1))


def _pair():
    """The same save under rules that join la at JOIN_AT and rules that never do."""
    with_join = world((joiner("ja", LA, TM, None, JOIN_AT),))
    without = replace(with_join, triggers=())
    return (with_join, start(with_join, orders(*SETUP))), (without, start(without, orders(*SETUP)))


@given(t=st.integers(JOIN_AT, 4000))
def test_a_join_keeps_what_the_person_does(t: int):
    """Invariant 94: at every t >= the join, with no decision, the stores, the card's work and its completions equal
    the same save's without the join (y included: a lump is paid as a rate by the tap and by the share alike); lb, not
    joined, is untouched."""
    (jr, js), (nr, ns) = _pair()
    assert stored(js, jr, X, t) == stored(ns, nr, X, t)
    assert stored(js, jr, V, t) == stored(ns, nr, V, t)
    assert work_done(js, jr, A1, t) == work_done(ns, nr, A1, t)
    assert count(js, jr, A1, t) == count(ns, nr, A1, t)
    assert stored(js, jr, Y, t) == stored(ns, nr, Y, t)


def test_a_join_changes_only_what_invariant_94_lists():
    """Invariant 94: at the join, the orders differ by la's uncapped always rule removed and the town's always rule
    added at the end (latched); the rules that are not always rules, and lb's, keep their order and latches; the mixes
    differ by the one mix, holding the first uncapped always rule's card at BP; the unlock set by JOINED la."""
    (jr, js), (nr, ns) = _pair()
    j, n = advance(js, jr, JOIN_AT), advance(ns, nr, JOIN_AT)
    assert n.orders == SETUP and joined(j, LA) and not joined(n, LA)
    assert j.orders == (GATE, always(B1), TOWN_RULE)
    assert j.latches[:2] == (n.latches[0], n.latches[2]) and j.latches[2]
    assert set(j.mixes) - set(n.mixes) == {Mix(TM, (CardShare(A1, BP),))} and set(n.mixes) <= set(j.mixes)
    assert set(j.unlocked) - set(n.unlocked) == {Unlock(UnlockKind.JOINED, LA)}
    assert set(n.unlocked) <= set(j.unlocked)
    assert view(j, jr).running_town_mix == TM


def test_a_running_tap_at_the_join_is_not_cut_it_lands_at_its_next_completion():
    """"Join": the running tap on la is not cut: a1's completion at 210 lands whole, then the share runs."""
    (jr, js), _ = _pair()
    assert count(js, jr, A1, 209) == 20 and count(js, jr, A1, 210) == 21
    assert card_view(js, jr, A1, 209)[0].run == RunKind.YIELDED and card_view(js, jr, A1, 210)[0].run == RunKind.FULL
    assert stored(js, jr, Y, 210) == 21 * Q


# ---- invariant 95: once -------------------------------------------------------------------------------------------

def test_a_second_join_of_a_joined_lane_changes_nothing():
    """Invariant 95: a2 would be a second share card for la; a join of an already joined lane changes nothing."""
    once = world((joiner("ja", LA, TM, A1, 100),))
    twice = world((joiner("ja", LA, TM, A1, 100), joiner("ja2", LA, TM, A2, 200)))
    a, b = advance(start(once), once, 300), advance(start(twice), twice, 300)
    assert (a.orders, a.mixes, a.unlocked, a.latches) == (b.orders, b.mixes, b.unlocked, b.latches)


def test_a_second_join_of_a_joined_lane_leaves_a_later_always_rule_on_it_alone():
    """Invariant 95: the player puts an uncapped always rule on la after its join; a later join of la does not strip it."""
    r = world((joiner("ja", LA, TM, A1, 100), joiner("ja2", LA, TM, A2, 200)))
    s = decide(advance(start(r), r, 150), r, 150, orders(TOWN_RULE, always(A2)))
    after = advance(s, r, 300)
    assert after.orders == (TOWN_RULE, always(A2)) and [m.components for m in after.mixes] == [(CardShare(A1, BP),)]


def test_a_town_rule_the_player_removed_comes_back_only_by_a_join_whose_mix_is_absent():
    """Invariant 95: the player empties the orders at 150; a join into the present town:main (lb at 200) adds
    its card and no rule; a join of a lane into the absent town:two adds the mix and its rule, appended below the
    player's own order, never inserted above it."""
    r = world((joiner("ja", LA, TM, A1, 100), joiner("jb", LB, TM, B1, 200)))
    s = decide(start(r), r, 150, orders())
    after = advance(s, r, 300)
    assert after.orders == () and joined(after, LB)
    assert [m for m in after.mixes if m.id == TM] == [Mix(TM, (CardShare(A1, BP), CardShare(B1, BP)))]
    mine = Order(AfterTime(160), SwitchMix(TM))
    r2 = world((joiner("ja", LA, TM, A1, 100), joiner("jb", LB, TM2, B1, 200)))
    s2 = decide(start(r2), r2, 150, orders(mine))
    assert advance(s2, r2, 300).orders == (mine, Order(ALWAYS, SwitchMix(TM2)))


# ---- invariant 97: rebase -----------------------------------------------------------------------------------------

def test_a_save_past_a_joins_trigger_rebased_into_rules_that_add_it_has_the_joined_town():
    """Invariant 97: a save at 500 running a1 by its always rule, rebased into rules that add a trigger joining la at
    100, holds JOINED la, town:main with a1 at BP and the town's rule in place of a1's, at the save's time, and its
    stores carry on as the unjoined save's do."""
    r1 = world()
    s = advance(start(r1, orders(always(A1))), r1, 500)
    r2 = world((joiner("ja", LA, TM, None, 100),))
    got = rebase(encode(s, r1), r2)
    assert got.time == 500 and joined(got, LA)
    assert got.orders == (TOWN_RULE,) and got.latches == (True,)
    assert set(got.mixes) == {Mix(TM, (CardShare(A1, BP),))}
    for t in (500, 505, 700, 1234):
        assert stored(got, r2, X, t) == stored(s, r1, X, t)
        assert work_done(got, r2, A1, t) == work_done(s, r1, A1, t)


def test_a_released_outcome_through_renames_renames_its_joins_lane_and_card():
    """Invariant 97 ("Rebase": Join's lane and card in released outcomes are renamed as installs' are; mix ids never):
    what the release lock forwards a released outcome through."""
    joined_out = Outcome(joins=(Join(LA, TM, A1),))
    got = renamed_outcome(joined_out, Renamer((Rename(IdKind.LANE, "la", "la2"), Rename(IdKind.CARD, "a1", "a9")), cards=("a1",)))
    assert got == Outcome(joins=(Join(LaneId("la2"), TM, CardId("a9")),))


def test_a_rename_of_a_lane_renames_the_join_a_trigger_has_yet_to_land():
    """Invariant 97 ("Rebase": Join's lane is renamed as installs' are): a save before the join, rebased through a
    rename of la to la2, joins la2 when the trigger fires."""
    r = world((joiner("ja", LA, TM, A1, 100),))
    s = advance(start(r), r, 50)
    got = rebase(encode(s, r), sub_rules(r, {"la": "la2"}), (Rename(IdKind.LANE, "la", "la2"),))
    later = advance(got, sub_rules(r, {"la": "la2"}), 300)
    assert not joined(got, LA) and Unlock(UnlockKind.JOINED, LaneId("la2")) in later.unlocked


def test_a_rename_of_a_joined_lane_renames_its_unlock_and_changes_nothing_else():
    """Invariant 97: rebasing a save holding Unlock(JOINED, la) through a rename of la to la2 gives
    Unlock(JOINED, la2); the town's mix and rule stay as they were (mix ids are never renamed)."""
    r = world((joiner("ja", LA, TM, A1, 100),))
    s = advance(start(r), r, 300)
    ids = {"la": "la2"}
    r2 = sub_rules(r, ids)
    got = rebase(encode(s, r), r2, (Rename(IdKind.LANE, "la", "la2"),))
    assert Unlock(UnlockKind.JOINED, LaneId("la2")) in got.unlocked
    assert Unlock(UnlockKind.JOINED, LA) not in got.unlocked
    want = sub_save(s, ids)
    assert (got.unlocked, got.orders, got.latches, got.mixes) == (want.unlocked, want.orders, want.latches, want.mixes)
    assert got.orders == (TOWN_RULE,) and got.time == s.time
