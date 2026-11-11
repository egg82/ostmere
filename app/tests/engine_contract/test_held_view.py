"""Invariant 118, the engine half (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "View"): View.held lists exactly
the cards with h(c) > 0, in rules.cards order, each with share_bp = h(c) and entries equal to its held entries in the
stack; explain_strength (and so FightView.power) lists the held entries among its adds with their "held:" source. The
wire half is test_held_wire.py."""
from ashfall_app.engine import (
    BP, RunKind, SideStrength, TapCard, ThreatStrength, advance, decide, explain_strength, new_save, view,
)
from held_world import (
    G, GA, GAC, GB, GH, GH2, GREQ, HELD, WOLF, first, hands, held_mods, ja, jb, kills, run_of, town, world,
)
from town_mix_world import TOWN_RULE, always, orders


@kills(1, 3, 4, 14, 17, 18)
def test_the_list_holds_exactly_the_cards_with_a_share_in_rules_order_with_their_entries():
    """gh2 is named before gh in the mix, but the list follows rules.cards (gh, gh2): shares 3000 and 5000, entries as
    the stack holds them (gh2's two entries, g then g2)."""
    r = world()
    s = hands(r, (GH2, 5000), (GH, 3000))
    held = view(s, r).held
    assert [(h.card, h.share_bp) for h in held] == [(GH, 3000), (GH2, 5000)]
    stack = held_mods(s, r)
    assert tuple(m for h in held for m in h.entries) == stack and len(stack) == 3
    assert [m.amount_bp for m in held[1].entries] == [1000, 750]
    assert all(m.source == HELD + h.card for h in held for m in h.entries)


@kills(2, 4, 9, 12, 13, 18)
def test_a_card_that_holds_nothing_is_not_listed():
    """Unlocked but in no mix, waiting on its requires, and a tapped plain card: none is listed."""
    r = world()
    assert view(new_save(r), r).held == ()
    s = hands(r, (GREQ, BP))
    assert [h.card for h in view(s, r).held] == [GREQ]
    waiting = first(s, r, lambda x: run_of(x, r, GREQ) is RunKind.WAITING)
    assert view(waiting, r).held == ()


@kills(2, 4, 18)
def test_a_tapped_card_lists_the_whole_share_and_the_town_lists_its_people_by_their_shares():
    r = world((ja(), jb()))
    tapped = decide(new_save(r), r, 0, TapCard(GH))
    assert [(h.card, h.share_bp) for h in view(tapped, r).held if h.card == GH] == [(GH, BP)]
    s = decide(town(r, (GA, 2500), (GB, 7000)), r, 0, orders(TOWN_RULE, always(GAC)))
    held = view(advance(s, r, 30), r).held
    assert [(h.card, h.share_bp) for h in held] == [(GA, 2500), (GB, 7000)]


@kills(4, 7, 18)
def test_a_tapped_card_that_is_also_in_the_running_mix_is_listed_once_at_the_whole_share():
    r = world()
    s = decide(hands(r, (GH, 3000)), r, 0, TapCard(GH))
    assert [(h.card, h.share_bp, [m.amount_bp for m in h.entries]) for h in view(s, r).held] == [(GH, BP, [5000])]


@kills(1, 4, 5, 18)
def test_the_listed_entry_is_the_held_one_not_the_declared_amount():
    """ga declares 4000; at a 2500 share the list serves 1000, and it lists a card whose held amount rounds to 0."""
    r = world((ja(), jb()))
    s = town(r, (GA, 2500), (GB, 4))
    entries = {h.card: [m.amount_bp for m in h.entries] for h in view(s, r).held}
    assert entries == {GA: [1000], GB: [0]}


@kills(3, 4, 14, 18)
def test_the_strength_explanations_and_the_fight_view_list_the_held_entries_among_their_adds():
    r = world()
    s = hands(r, (GH, 5000), (GH2, 5000))
    held = tuple(m for h in view(s, r).held for m in h.entries if m.target == SideStrength(G))
    assert len(held) == 2 and explain_strength(s, r, SideStrength(G)).adds == held
    fights = view(s, r).fights
    assert fights and all(f.power.adds == held for f in fights if f.side == G)
    assert all(not f.threat_strength.adds for f in fights)
    assert explain_strength(s, r, ThreatStrength(WOLF)).adds == ()
