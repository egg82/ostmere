"""Rebase step 6 lands a join (engine DESIGN.txt, "THE TOWN'S MIX", "Rebase"; invariant 97): a save written before the
join's rules, loaded under rules whose trigger joins and is already true, comes out joined with its first person's
rules as the town's standing orders and its stores unchanged."""
from ashfall_app.engine import (
    BP, CardShare, Mix, Order, SwitchMix, TapCard, Unlock, UnlockKind, advance, encode, rebase,
)
from join_world import ALWAYS, A, PERSON, RULE, TOWN, new_rules, old_rules, saved_before_the_join


def test_a_save_past_the_join_comes_out_joined_with_its_rules_and_stores_kept():
    before, r = saved_before_the_join(), new_rules()
    after = rebase(encode(before, old_rules()), r)
    assert Unlock(UnlockKind.JOINED, PERSON) in after.unlocked
    assert after.mixes == (Mix(TOWN, (CardShare(A, BP),)),)
    assert after.orders == (RULE, Order(ALWAYS, SwitchMix(TOWN)))
    assert Order(ALWAYS, TapCard(A)) not in after.orders
    assert after.stores == before.stores
    assert [(c.card, c.work.start_value, c.raised) for c in after.cards] == \
           [(c.card, c.work.start_value, c.raised) for c in before.cards]   # the bar's limit differs: a share, no tap
    assert before.orders == (RULE, Order(ALWAYS, TapCard(A)))   # control: the save really held the rules named
    for t in (before.time + 1, before.time + 300, 5000):
        assert advance(after, r, t).stores == advance(before, old_rules(), t).stores


def test_a_trigger_not_yet_true_joins_nothing_at_the_rebase():
    after = rebase(encode(saved_before_the_join(), old_rules()), new_rules(at=10**6))
    assert Unlock(UnlockKind.JOINED, PERSON) not in after.unlocked and after.mixes == ()
    assert after.orders == saved_before_the_join().orders
