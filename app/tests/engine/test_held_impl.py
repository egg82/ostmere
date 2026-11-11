"""Entries held while a card runs (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS", invariants 110-118): the
implementation's own tests beside the blind contract suite."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, AfterTime, CardId, CardShare, InvalidRulesError, InvalidVerbError, Mix, Modifier, ModifierKind, Outcome,
    Rules, RunKind, Save, SaveMix, SideId, SideStrength, SourceId, TapCard, ThreatStrength, TriggerDef, TriggerId,
    Unlock, UnlockKind, WhileRunning, advance, decide, decode, encode, explain_strength, new_save, rebase,
    rules_digest, validate_rules, view,
)
from ashfall_app.engine.gates import effective_stack, stack_inputs
from held_impl_world import (
    B1, CAP, DEF, GUARD, HAND, HUNT, LA, M, NEED, TM, WARM, WATCH, WET, WOLF, joined, mixed, world,
)


def held(s: Save, r: Rules, side: SideId = HAND) -> list[Modifier]:
    return [m for m in explain_strength(s, r, SideStrength(side)).adds if str(m.source).startswith("held:")]


def entry(card: CardId, amount: int, side: SideId = HAND) -> Modifier:
    return Modifier(SideStrength(side), ModifierKind.ADD_BP, amount, SourceId(f"held:{card}"))


def test_a_tap_holds_the_whole_amount_to_its_end_and_the_strength_is_the_hand_written_twin():
    r = world()
    s = decide(new_save(r), r, 0, TapCard(GUARD))
    assert held(new_save(r), r) == [] and held(s, r) == [entry(GUARD, 5000)]
    twin = world(held=False)
    by_hand = new_save(twin, (Modifier(SideStrength(HAND), ModifierKind.ADD_BP, 5000, SourceId("by-hand")),))
    assert explain_strength(s, r, SideStrength(HAND)).value == explain_strength(by_hand, twin, SideStrength(HAND)).value == 1500
    assert held(advance(s, r, 9), r) == [entry(GUARD, 5000)] and held(advance(s, r, 10), r) == []


def test_a_mix_share_scales_the_amount_rounded_down_and_a_zero_product_is_still_held():
    r = world()
    assert held(mixed(r, (GUARD, 3000)), r) == [entry(GUARD, 1500)]
    assert held(mixed(r, (GUARD, 1)), r) == [entry(GUARD, 0)]
    assert held(mixed(r, (GUARD, 3000), (WARM, 2500)), r) == [entry(GUARD, 1500), entry(WARM, 1250)]


def test_a_card_both_tapped_and_mixed_counts_once_at_the_whole_share():
    r = world()
    s = decide(mixed(r, (GUARD, 4000)), r, 0, TapCard(GUARD))
    assert held(s, r) == [entry(GUARD, 5000)]
    assert [(h.card, h.share_bp) for h in view(s, r).held] == [(GUARD, BP)]


def test_a_saved_mix_nothing_runs_holds_nothing():
    r = world()
    s = mixed(r, (GUARD, BP), run=False)
    assert held(s, r) == [] and view(s, r).held == ()


def test_a_spent_waiting_or_greyed_card_holds_nothing():
    r = world()
    spent = mixed(r, (WET, BP))
    assert [c.run for c in view(spent, r).cards if c.card == WET] == [RunKind.SPENT] and held(spent, r) == []
    waiting = mixed(r, (NEED, BP))
    assert [c.run for c in view(waiting, r).cards if c.card == NEED] == [RunKind.WAITING] and held(waiting, r) == []
    greyed = advance(decide(mixed(r, (GUARD, 5000), (CAP, 100)), r, 0, TapCard(CAP)), r, 25)
    assert view(greyed, r).greyed_mixes == (M,) and held(greyed, r) == []
    control = advance(mixed(r, (GUARD, 5000), (CAP, 100)), r, 25)
    assert held(control, r) == [entry(GUARD, 2500)]


def test_a_town_card_holds_once_its_lane_has_joined_in_declaration_order():
    r = world(joined(LA, WATCH, at=20))
    pending = advance(new_save(r), r, 19)
    assert held(pending, r) == [] and view(pending, r).running_town_mix is None
    s = advance(pending, r, 20)
    assert view(s, r).running_town_mix == TM and held(s, r) == [entry(WATCH, 4000)]
    s = decide(s, r, 20, SaveMix(Mix(TM, (CardShare(WATCH, 3000),))))
    assert held(s, r) == [entry(WATCH, 1200)] and held(s, r, DEF) == [entry(WATCH, 300, DEF)]
    assert [(h.card, h.share_bp, len(h.entries)) for h in view(s, r).held] == [(WATCH, 3000, 2)]


def test_a_town_card_never_unlocked_holds_nothing_however_its_lane_joined():
    locked = replace(world(joined(LA, WATCH)), opening=(Unlock(UnlockKind.CARD, B1),))
    s = advance(new_save(locked), locked, 5)
    assert view(s, locked).running_town_mix == TM and held(s, locked) == []
    unlocked = replace(locked, opening=(Unlock(UnlockKind.CARD, WATCH),))
    assert held(advance(new_save(unlocked), unlocked, 5), unlocked) == [entry(WATCH, 4000)]


def test_a_mixed_fights_odds_move_at_the_instant_the_share_changes_and_not_before():
    r = world(joined(LA, WATCH))
    s = decide(mixed(r, (HUNT, BP)), r, 0, SaveMix(Mix(TM, (CardShare(WATCH, 2000),))))

    def loss(save: Save) -> list[int]:
        return [f.loss_bp for f in view(save, r).fights]
    first = loss(s)
    assert loss(advance(s, r, 49)) == first
    at = advance(s, r, 50)
    more = decide(at, r, 50, SaveMix(Mix(TM, (CardShare(WATCH, 8000),))))
    assert loss(at) == first and loss(more)[0] < first[0]


def test_slicing_the_same_decisions_into_advances_and_views_gives_equal_saves():
    r = world(joined(LA, WATCH))
    s = decide(mixed(r, (HUNT, BP)), r, 0, SaveMix(Mix(TM, (CardShare(WATCH, 2000),))))
    sliced = s
    for t in (7, 31, 32, 90, 333):
        sliced = advance(sliced, r, t)
        view(sliced, r)
        explain_strength(sliced, r, SideStrength(HAND))
    assert sliced == advance(s, r, 333)


def test_held_entries_are_never_stored_and_aim_only_at_sides():
    r = world(joined(LA, WATCH))
    s = decide(decide(mixed(r, (GUARD, 4000)), r, 0, SaveMix(Mix(TM, (CardShare(WATCH, 2000),)))), r, 0, TapCard(HUNT))
    s = advance(s, r, 5)
    assert held(s, r) and s.modifiers == () and all(not str(m.source).startswith("held:") for ls in s.lanes
                                                    for m in (ls.speed or ()))
    assert not any(str(m.source).startswith("held:") for m in explain_strength(s, r, ThreatStrength(WOLF)).adds)
    assert {type(m.target).__name__ for m in effective_stack(s, r) if str(m.source).startswith("held:")} == {"SideStrength"}
    assert decode(encode(s, r), r) == s


def test_the_field_is_part_of_the_rules_digest_and_a_save_round_trips_under_it():
    plain, with_field = world(held=False), world()
    assert rules_digest(plain) != rules_digest(with_field)
    s = advance(mixed(with_field, (GUARD, 4000)), with_field, 17)
    assert decode(encode(s, with_field), with_field) == s


def test_a_fight_tap_keeps_the_odds_it_started_at_whatever_is_held_meanwhile():
    r = world(joined(LA, WATCH))
    s = decide(new_save(r), r, 0, SaveMix(Mix(TM, (CardShare(WATCH, 8000),))))
    before = view(s, r).fights[0].loss_bp
    tapped = decide(s, r, 0, TapCard(HUNT))
    assert view(tapped, r).fights[0].loss_bp == before
    later = advance(decide(tapped, r, 0, SaveMix(Mix(TM, (CardShare(WATCH, 0),)))), r, 40)
    assert view(later, r).fights[0].loss_bp == before and held(later, r, HAND) == []


@pytest.mark.parametrize("bad", [
    (WhileRunning(SideId("ghost"), 100),), (WhileRunning(HAND, 0),), (WhileRunning(HAND, 1), WhileRunning(HAND, 2)),
], ids=["unknown side", "amount below one", "side twice"])
def test_validation_refuses_a_bad_while_running(bad: tuple[WhileRunning, ...]):
    r = world()
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(r, cards=(replace(r.cards[0], while_running=bad), *r.cards[1:])))


def test_the_engines_held_source_is_refused_in_rules_and_in_a_starting_stack():
    mod = Modifier(SideStrength(HAND), ModifierKind.ADD_BP, 1, SourceId("held:guard"))
    r = world(TriggerDef(TriggerId("t"), AfterTime(0), Outcome(modifiers=(mod,))))
    with pytest.raises(InvalidRulesError):
        validate_rules(r)
    with pytest.raises(InvalidVerbError):
        new_save(world(), (mod,))


def test_adding_the_field_to_a_card_rebases_a_save_with_its_values_unchanged():
    old, new = world(held=False), world()
    s = advance(decide(new_save(old), old, 0, TapCard(HUNT)), old, 30)
    r = rebase(encode(s, old), new)
    assert (r.time, r.stores, r.cards, r.unlocked) == (s.time, s.stores, s.cards, s.unlocked)


def test_held_view_lists_the_cards_in_rules_order_with_their_entries():
    r = world()
    s = mixed(r, (WARM, 2000), (GUARD, 5000))
    assert [(h.card, h.share_bp, h.entries) for h in view(s, r).held] == [
        (GUARD, 5000, (entry(GUARD, 2500),)), (WARM, 2000, (entry(WARM, 1000),))]


def test_the_stack_inputs_follow_the_held_state_and_rules_without_it_keep_their_parts():
    r = world()
    low, high = mixed(r, (GUARD, 2000)), mixed(r, (GUARD, 6000))
    assert stack_inputs(low, r) != stack_inputs(high, r)
    assert stack_inputs(mixed(r, (GUARD, 2000)), r)[-1] is stack_inputs(low, r)[-1]
    plain = world(held=False)
    assert len(stack_inputs(new_save(plain), plain)) == 3 + 1   # rules, modifiers, unlocks, and the one fight tap's speed
