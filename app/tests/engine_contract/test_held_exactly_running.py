"""Invariant 110 (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "The entries"): for each WhileRunning(side, a) of a
card c, the effective stack and explain_strength hold exactly one Modifier(SideStrength(side), ADD_BP, a * h // BP,
"held:" + c) while h(c) > 0 and none while h(c) = 0; the strength equals the same rules with the entries written into
save.modifiers by hand. h is set by the scenario (a tap: BP; a town share: its basis points); the share rules
themselves are test_held_share_*.py."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, CardShare, Mix, Modifier, ModifierKind, SaveMix, SideStrength, SourceId, SubMix, SwitchMix, TapCard, ThreatStrength,
    advance, decide, explain_strength, new_save, strength, value,
)
from ashfall_app.engine import MixId
from held_world import (
    G, G2, GA, GB, GH, GH2, HM, RLOST, STASH, WOLF, flat, hands, held_mods, held_of, ja, jb, kills, loss, odds_loss, plain,
    raised, town, world,
)

HAND_G = SideStrength(G)


def by_hand(amount_bp: int) -> Modifier:
    return Modifier(HAND_G, ModifierKind.ADD_BP, amount_bp, SourceId("by-hand"))


@kills(4)
def test_an_unlocked_card_in_no_mix_and_untapped_holds_nothing():
    """h = 0 for a card unlocked but in no running mix and untapped (rule 3): no entry anywhere, base strength."""
    r = world()
    s = new_save(r)
    assert held_mods(s, r) == () and raised(s, r) == 0 and loss(s, r) == odds_loss(0)
    s = advance(s, r, 500)
    assert held_mods(s, r) == () and explain_strength(s, r, HAND_G).adds == ()


@kills(2, 3, 4, 14, 17, 22)
def test_a_tap_holds_its_whole_amount_as_one_entry_and_gives_it_up_at_the_landing():
    """h = BP while the tap holds the lane (gh is 100 s): one entry at the whole 5000 with source held:gh, listed by
    explain_strength among its adds; at the landing instant (100) it is gone."""
    r = world()
    s = decide(new_save(r), r, 0, TapCard(GH))
    for t in (0, 1, 99):
        a = advance(s, r, t)
        assert held_mods(a, r) == (Modifier(HAND_G, ModifierKind.ADD_BP, 5000, SourceId("held:gh")),)
        assert explain_strength(a, r, HAND_G).adds == held_mods(a, r)
        assert strength(a, r, HAND_G) == BP + 5000
    done = advance(s, r, 100)
    assert held_mods(done, r) == () and strength(done, r, HAND_G) == BP


@kills(3, 4, 14, 22)
def test_a_tap_pays_as_the_rules_with_the_entry_written_by_hand_do():
    """Invariant 110, the twin: gh tapped over its 100 s is the same game as the entry-free rules with +5000 on g in
    save.modifiers, in the odds and so in everything the standing fight touches (stash drain, lost tally)."""
    r = world()
    s = decide(new_save(r), r, 0, TapCard(GH))
    twin_rules = plain(r)
    twin = new_save(twin_rules, (by_hand(5000),))
    for t in (1, 50, 99):
        a, b = advance(s, r, t), advance(twin, twin_rules, t)
        assert strength(a, r, HAND_G) == strength(b, twin_rules, HAND_G)
        assert loss(a, r) == loss(b, twin_rules) == odds_loss(5000)
        for store in (STASH, RLOST):
            assert value(a, r, store, t) == value(b, twin_rules, store, t), (store, t)


@kills(1, 4, 5, 14, 17)
@given(share=st.integers(1, BP))
def test_a_town_share_scales_the_amount_and_floors_it_once(share: int):
    """ga (4000) at a town share s > 0 holds 4000 * s // BP, rounded down, never up or to nearest."""
    r = world((ja(),))
    s = town(r, (GA, share))
    assert held_of(s, r, GA) == [flat(4000, share)]
    assert raised(s, r) == flat(4000, share)


@kills(4)
def test_a_share_of_zero_holds_nothing():
    """h = 0 (a card at share 0 runs nothing): no entry sourced held:ga, however the mix names it."""
    r = world((ja(),))
    s = town(r, (GA, 0))
    assert held_mods(s, r) == () and raised(s, r) == 0


@kills(1, 5, 14, 17)
def test_a_share_that_rounds_up_or_to_nearest_still_floors():
    """4000 * 3337 / BP = 1334.8: floor 1334, ceil and nearest 1335."""
    r = world((ja(),))
    assert held_of(town(r, (GA, 3337)), r, GA) == [1334]


@kills(1, 4, 5, 14, 17)
def test_an_entry_whose_product_rounds_to_zero_is_still_held_at_amount_zero():
    """A running card whose a * h // BP is 0 keeps its entry at amount 0 (gb 2000 at a 4 basis point share)."""
    r = world((ja(), jb()))
    s = town(r, (GB, 4))
    assert held_of(s, r, GB) == [0] and raised(s, r) == 0


@kills(1, 4, 14, 15, 17)
def test_a_nested_share_is_floored_once_on_the_flattened_share():
    """gh (5000) in a mix inside a mix: the flattened share is 656 * 275 // BP = 18, the entry 5000 * 18 // BP = 9.
    Flooring the nested share first (5000 * 275 // BP = 137, then 137 * 656 // BP) would give 8."""
    r = world()
    inner = Mix(HM, (CardShare(GH, 656),))
    outer = Mix(MixId("outer"), (SubMix(HM, 275),))
    s = new_save(r)
    for verb in (SaveMix(inner), SaveMix(outer), SwitchMix(outer.id)):
        s = decide(s, r, 0, verb)
    assert held_of(s, r, GH) == [9] and raised(s, r) == 9


@kills(1, 5, 14, 15, 17)
@given(outer=st.integers(1, BP), inner=st.integers(1, BP))
def test_a_nested_share_property_the_entry_follows_the_flattened_share(outer: int, inner: int):
    """For any nested shares the entry is 5000 * (inner * outer // BP) // BP: one floor on the flattened share."""
    r = world()
    mixes = (Mix(HM, (CardShare(GH, inner),)), Mix(MixId("outer"), (SubMix(HM, outer),)))
    s = new_save(r)
    for verb in (*(SaveMix(m) for m in mixes), SwitchMix(MixId("outer"))):
        s = decide(s, r, 0, verb)
    assert held_of(s, r, GH) == ([flat(5000, inner * outer // BP)] if inner * outer // BP else [])


@kills(1, 3, 4, 14, 17)
def test_entries_follow_the_cards_in_rules_order_and_a_card_lists_its_sides_in_declaration_order():
    """gh (g 5000) is declared before gh2 (g 2000 then g2 1500): at BP shares each (a mix of two cards at 5000 each)
    the stack holds held:gh, held:gh2 on g, held:gh2 on g2, in that order; g2's strength lists only gh2's."""
    r = world()
    s = hands(r, (GH, 5000), (GH2, 5000))
    assert [(m.source, m.target, m.amount_bp) for m in held_mods(s, r)] == [
        ("held:gh", HAND_G, 2500), ("held:gh2", HAND_G, 1000), ("held:gh2", SideStrength(G2), 750)]
    assert [m.source for m in explain_strength(s, r, SideStrength(G2)).adds] == ["held:gh2"]
    assert explain_strength(s, r, HAND_G).adds == held_mods(s, r)[:2]


@kills(3, 17)
def test_a_held_entry_never_lands_on_a_threat():
    """Invariant 110 aims only at sides: the threat's explanation carries none and its value is its base."""
    r = world()
    s = decide(new_save(r), r, 0, TapCard(GH))
    e = explain_strength(s, r, ThreatStrength(WOLF))
    assert e.adds == () and e.muls == () and e.value == BP and held_mods(s, r)


@kills(1, 3, 4, 14)
def test_two_cards_of_one_side_add_their_entries():
    """Held entries sum like any adds: gh and gh2 at half shares each raise g by 2500 + 1000."""
    r = world()
    s = hands(r, (GH, 5000), (GH2, 5000))
    assert raised(s, r) == 3500 and loss(s, r) == odds_loss(3500)
