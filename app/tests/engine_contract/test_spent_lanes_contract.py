"""SPENT, whose share moves (engine DESIGN.txt, "SPENT", invariant 134's lane and mix clauses). Written blind from that
part; MUTANTS_spent.txt names the wrong implementations each test must turn red for. Shares move among the cards of one
running mix on one lane: the hands for a hands mix, one person's lane for the town's mix. The town world is two joined
lanes: la (EATA, spent from the first instant, and RA) and lb (RB)."""
from collections.abc import Sequence

from ashfall_app.engine import CardDef, CardId, CardShare, Mix, MixId, Rules, Save, SaveMix, SubMix, SwitchMix, decide, new_save
from spent_world import (
    EAT, EATA, MIX, P2, R1, R2, R3, RA, RB, TM, UNITS_PER_BP as U, W, Z, card_view, eater, gained_of, gains,
    kills, make_run, mixed, plain, rate, share_of, spent_kind, spent_store_of, town_cards, town_rules, world,
)



def _hands_world() -> Rules:
    return world(eater(), *plain(R1, R2, R3))


def town(shares: Sequence[tuple[CardId, int]], *cards: CardDef) -> tuple[Rules, Save]:
    """The town world (plus `cards`), its town mix saved with these shares at 0 and so running."""
    r = town_rules(*town_cards(), *cards)
    return r, decide(new_save(r), r, 0, SaveMix(Mix(TM, tuple(CardShare(c, b) for c, b in shares))))


@kills(2)
def test_a_town_card_spent_gives_its_share_to_its_own_lane_only():
    """Invariant 134 (lanes): EATA 3000 is spent on la, RA 2000 shares la, RB 5000 is on lb. RA gains all 3000 (Rsum 2000
    on la); RB gains nothing, though a mix-wide split would give RB 2142 of it."""
    r, s = town([(EATA, 3000), (RA, 2000), (RB, 5000)])
    assert make_run(s, r, EATA, 40) == spent_kind() and spent_store_of(card_view(s, r, EATA, 40)) is not None
    assert (share_of(s, r, RA, 40), gains(s, r, RA, 40), rate(s, r, Z, 40)) == (5000, ((EATA, 3000),), 5000 * U)
    assert (share_of(s, r, RB, 40), gains(s, r, RB, 40), rate(s, r, W, 40)) == (5000, (), 5000 * U)


@kills(2)
def test_a_lane_with_nothing_else_on_it_gives_nothing_to_anyone():
    """Invariant 134 (Rsum 0): la holds only the spent EATA, so its share idles; lb's RB does not receive it."""
    r, s = town([(EATA, 3000), (RB, 5000)])
    assert make_run(s, r, EATA, 40) == spent_kind()
    assert (share_of(s, r, RB, 40), gains(s, r, RB, 40), rate(s, r, W, 40)) == (5000, (), 5000 * U)


@kills(3)
def test_the_hands_mix_and_the_town_mix_keep_their_yields_apart():
    """Invariant 134 (mixes): a spent hands card gives to the hands' R1 alone, a spent town card to RA alone; nobody in
    the other mix gains from either, though R1 and RA are both uncapped and unspent."""
    r, s = town([(EATA, 3000), (RA, 2000), (RB, 5000)], eater(EAT, P2), *plain(R1))
    s = mixed(r, [(EAT, 4000), (R1, 2000)], base=s)
    assert make_run(s, r, EAT, 40) == make_run(s, r, EATA, 40) == spent_kind()
    assert (share_of(s, r, R1, 40), gains(s, r, R1, 40)) == (6000, ((EAT, 4000),))
    assert (share_of(s, r, RA, 40), gains(s, r, RA, 40)) == (5000, ((EATA, 3000),))
    assert (share_of(s, r, RB, 40), gains(s, r, RB, 40)) == (5000, ())


@kills(3)
def test_a_saved_mix_that_is_not_running_gains_nothing():
    """Invariant 134: R3 sits in a saved mix that is not the running one: it has no share, no run and no gains, while the
    running mix's R1 takes the spent card's share."""
    r = _hands_world()
    s = decide(mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)]), r, 0, SaveMix(Mix(MixId("idle"), (CardShare(R3, 5000),))))
    cv = card_view(s, r, R3, 40)
    assert (cv.share_bp, cv.run, gained_of(cv), spent_store_of(cv)) == (0, None, (), None)
    assert gains(s, r, R1, 40) == ((EAT, 2500),) and rate(s, r, Z, 40) == 5000 * U


@kills(21)
def test_a_card_in_a_sub_mix_counts_with_its_shares_summed():
    """Invariant 134 ("flattened, repeats summed"): R1 is 1000 in the mix and 5000 of a sub-mix dropped in at 3000 (1500), so it
    is 2500 flattened; with R2 1500 and EAT 4000 spent, R1 gains floor(4000 * 2500 / 4000) = 2500, not 1600."""
    r = _hands_world()
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("sub"), (CardShare(R1, 5000),))))
    s = decide(s, r, 0, SaveMix(Mix(MIX, (CardShare(EAT, 4000), CardShare(R1, 1000), SubMix(MixId("sub"), 3000),
                                         CardShare(R2, 1500)))))
    s = decide(s, r, 0, SwitchMix(MIX))
    assert (share_of(s, r, R1, 40), gains(s, r, R1, 40)) == (5000, ((EAT, 2500),))
    assert (share_of(s, r, R2, 40), gains(s, r, R2, 40)) == (3000, ((EAT, 1500),))


@kills(21)
def test_a_card_listed_twice_in_the_mix_counts_with_its_shares_summed():
    """Invariant 134 ("flattened, repeats summed"), the direct form: R1 is 1000 and again 1500 in the mix, so 2500 flattened;
    with R2 1500 and EAT 4000 spent, R1 gains floor(4000 * 2500 / 4000) = 2500."""
    r = _hands_world()
    s = decide(new_save(r), r, 0, SaveMix(Mix(MIX, (CardShare(EAT, 4000), CardShare(R1, 1000), CardShare(R2, 1500),
                                                    CardShare(R1, 1500)))))
    s = decide(s, r, 0, SwitchMix(MIX))
    assert (share_of(s, r, R1, 40), gains(s, r, R1, 40)) == (5000, ((EAT, 2500),))
    assert (share_of(s, r, R2, 40), gains(s, r, R2, 40)) == (3000, ((EAT, 1500),))
