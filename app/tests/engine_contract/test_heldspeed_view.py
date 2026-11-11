"""Invariant 118, the engine half, with standing holders (engine DESIGN.txt, "HELD SPEED ...": "View"): View.held lists
the standing holders that run too, after the cards, in rules.standing order, each with share_bp BP and the entries the stack
holds for it, `card` holding the runner's id; a paused or locked one is not listed and a standing action with no entry
never is."""
from dataclasses import replace

from ashfall_app.engine import BP, HeldView, advance, new_save, view
from held_world import kills
from heldspeed_world import (
    EAT1, EAT2, GS, LP, LQ, after, dry_instant, eater, held_mods, held_speed, hands_mix, maker, resumed, speed_mod, stew_world, tapped, unlock_at, opening_without, world,
)


def listing(held: tuple[HeldView, ...]) -> list[tuple[str, int, list[tuple[str, int]]]]:
    """Each holder as (id, share_bp, [(source, amount_bp) of its entries])."""
    return [(h.card, h.share_bp, [(m.source, m.amount_bp) for m in h.entries]) for h in held]


@kills(2, 10)
def test_the_list_holds_the_cards_first_then_the_running_standing_holders_in_rules_order():
    """gs at 6000 of the hands' time holds 2400 on lp; eat1 and eat2 run at BP; mk holds nothing and is not listed."""
    r = world()
    s = after(new_save(r), r, *hands_mix((GS, 6000)))
    held = view(s, r).held
    assert listing(held) == [("gs", 6000, [("held:gs", 2400)]), ("eat1", BP, [("held:eat1", 5000)]),
                             ("eat2", BP, [("held:eat2", 3000)])]
    assert tuple(m for h in held for m in h.entries) == held_mods(s, r)


@kills(10)
def test_standing_holders_follow_rules_standing_order_whatever_order_they_were_unlocked_in():
    """eat2 is declared after eat1 and unlocked first; the list still reads eat1, eat2."""
    r = replace(world(), standing=(eater(EAT1, held_speed(LP, 100)), eater(EAT2, held_speed(LQ, 200)), maker(3)))
    r = replace(r, opening=opening_without(r, EAT1), triggers=(unlock_at(EAT1, 50),))
    assert [h.card for h in view(advance(new_save(r), r, 10), r).held] == [EAT2]
    assert [h.card for h in view(advance(new_save(r), r, 60), r).held] == [EAT1, EAT2]


@kills(1, 10)
def test_a_paused_standing_holder_is_not_listed_and_is_again_once_it_resumes():
    r, s = stew_world(3)
    d = dry_instant(r, s)
    assert listing(view(d, r).held) == [("eat1", BP, [("held:eat1", 5000)])]
    n = resumed(r, d, EAT2)
    assert listing(view(n, r).held) == [("eat1", BP, [("held:eat1", 5000)]), ("eat2", BP, [("held:eat2", 3000)])]
    assert view(n, r).held[1].entries == (speed_mod(EAT2, LQ, 3000),)


@kills(2, 10)
def test_a_tapped_card_and_a_standing_holder_are_both_listed_with_the_card_first():
    r = world()
    held = view(tapped(r, GS), r).held
    assert [(h.card, h.share_bp) for h in held] == [("gs", BP), ("eat1", BP), ("eat2", BP)]
