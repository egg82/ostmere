"""What a chain adds to the read model and the codec (engine/design/spells.txt, "SPELLS": Read model, Codec, Rebase;
invariants 188, 191), written blind from that part alone."""
from dataclasses import replace

from ashfall_app.engine import (
    AfterTime, ChainReach, ChainView, ModifierKind, Outcome, TriggerDef, TriggerId, Unlock, UnlockKind, advance, chain_views,
    decode, encode, new_save, rebase, rules_digest, view, QUANTITY_SCALE as Q,
)
from fight_world import world as fight_world
from spells_world import (
    LINK_KEYS, RAID, SPELL, SPELL2, chained, due_of, entry, fought, kills, play, raid, spell, world,
)

PER = 3600
TWO = (spell(10, 2, LINK_KEYS[:1], cap=1), spell(10, 3, LINK_KEYS[1:2], card_id=SPELL2))


@kills(36)
def test_one_view_per_unlocked_chain_card_that_is_not_completed_in_rules_order():
    r = world(4, cards=TWO, per=PER)
    s = new_save(r)
    assert [(v.card, v.runner) for v in chain_views(s, r)] == [(SPELL, RAID), (SPELL2, RAID)]
    s, _ = play(r, (0,))
    assert [v.card for v in chain_views(s, r)] == [SPELL2]


@kills(36)
def test_a_locked_card_has_no_view_until_it_is_unlocked():
    unlock = TriggerDef(TriggerId("u"), AfterTime(5), Outcome(unlocks=(Unlock(UnlockKind.CARD, SPELL),)))
    r = replace(world(4, per=PER, triggers=(unlock,)), opening=(Unlock(UnlockKind.ACTION, RAID),))
    s = new_save(r)
    assert chain_views(s, r) == ()
    assert [v.card for v in chain_views(advance(s, r, 6), r)] == [SPELL]


@kills(37)
def test_the_view_due_is_the_members_of_the_group_now_under_way_still_to_be_fought():
    r = world(4, 9, per=PER)
    s, _ = play(r, (0,))
    for t in (10, 11, 12, 13, 14, 25):
        at = advance(s, r, t)
        (v,) = chain_views(at, r)
        assert v.due == due_of(4, fought(r, t), chained(r, s, t))
        assert isinstance(v, ChainView) and 1 <= v.due <= 4
    assert chain_views(s, r)[0].due == 4         # the chain ended the group at 10: a whole group is due next


@kills(5, 37)
def test_the_view_due_is_zero_while_the_runner_is_not_fighting():
    r = world(4, 3, per=PER, fought_cap=5 * Q)
    (v,) = chain_views(advance(new_save(r), r, 20), r)
    assert v.due == 0


@kills(6)
def test_the_view_reach_is_what_the_next_completion_runs_and_reading_writes_nothing():
    mods = (entry(SPELL, ModifierKind.ADD_BP, 10_000),)
    r = world(40, 2, per=PER)
    s = new_save(r, mods)
    before = s
    (v,) = chain_views(s, r)
    assert v.reach.target == ChainReach(SPELL) and v.reach.value == 4 and s == before


@kills(35)
def test_the_fight_view_serves_the_whole_links_chained_and_zero_for_a_runner_with_none():
    r = world(4, 3, per=PER)
    s, _ = play(r, (0, 11))
    assert chained(r, s) > 0 and view(s, r).fights[0].chained == chained(r, s)
    bare = replace(r, cards=(replace(r.cards[0], chain=None),), standing=(raid(chained=None),),
                   threats=(replace(r.threats[0], members=1),))
    assert view(advance(new_save(bare), bare, 50), bare).fights[0].chained == 0


@kills(33)
def test_a_save_holding_chain_reach_entries_and_a_chained_tally_round_trips_and_rebases_to_itself():
    mods = (entry(SPELL, ModifierKind.ADD_BP, 5000), entry(SPELL, ModifierKind.MUL_BP, 15_000))
    r = world(6, 3, per=PER)
    s, _ = play(r, (0, 11), mods=mods)
    assert chained(r, s) > 0 and s.modifiers == mods
    assert decode(encode(s, r), r) == s
    assert rebase(encode(s, r), r) == s


@kills(34)
def test_rules_with_no_chain_no_chained_tally_and_single_creatures_keep_the_digest_they_had():
    """The digest of fights' own fixture world, taken on the tree before chains existed."""
    assert rules_digest(fight_world(2, 6)) == "d226f902884e34bdef9b2aa1f6e99b795a49e2b87f4bf906ac3d4b4a4200b392"


def test_a_chain_is_part_of_the_rules_digest():
    r = world(3, 2, per=PER)
    assert rules_digest(r) != rules_digest(replace(r, cards=(replace(r.cards[0], chain=None),)))
    assert rules_digest(r) != rules_digest(replace(r, threats=(replace(r.threats[0], members=4),)))
