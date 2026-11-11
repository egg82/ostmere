"""Invariants 82 (its strength half: raising entries never lower a strength) and 83 (no entry aimed at a ThreatStrength
outside a trigger's outcome, and no save's ThreatStrength falls), from DESIGN.txt, "FIGHTS", alone. Each refusal is
paired with a valid control, so a validator that refuses everything cannot pass."""
from collections.abc import Callable
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, AfterTime, AnswerDef, AnswerId, AtLeast, ChipDef, ChipId, InvalidRulesError, InvalidVerbError, Modifier,
    ModifierKind, OfferDef, OfferId, Outcome, SideDef, SideId, SideStrength, SourceId, StoreDef, StoreValue,
    ThreatDef, ThreatId, ThreatStrength, Rules, TriggerDef, TriggerId, advance, explain_strength, new_save, strength,
    validate_rules,
)
from contract_gen import Q, card, make_rules, store_id

ADD, MUL = ModifierKind.ADD_BP, ModifierKind.MUL_BP
HAND, WOLF = SideId("hand"), ThreatId("wolf")
RAMP, RAMP2 = TriggerId("ramp"), TriggerId("ramp2")
ME, THEM = SideStrength(HAND), ThreatStrength(WOLF)


def entry(target: SideStrength | ThreatStrength, kind: ModifierKind, bp: int, source: str) -> Modifier:
    return Modifier(target, kind, bp, SourceId(source))


def world(*, triggers: tuple[TriggerDef, ...] = (), **parts: tuple[object, ...]) -> Rules:
    r = make_rules([StoreDef(store_id(0), 10 * Q)], [card(0)])
    return replace(r, sides=(SideDef(HAND, 4),), threats=(ThreatDef(WOLF, 10),), triggers=triggers, **parts)


def ramp(trigger: TriggerId, *mods: Modifier, at: int = 100) -> TriggerDef:
    return TriggerDef(trigger, AfterTime(at), Outcome(modifiers=mods))


def test_a_strength_is_its_base_under_adds_summed_and_muls_multiplied_rounded_down_once():
    r = world()
    s = new_save(r, (entry(ME, ADD, 1_000, "spear"), entry(ME, ADD, 500, "belt"), entry(ME, MUL, 15_000, "oath"),
                     entry(THEM, MUL, 12_500, "winter")))
    assert strength(s, r, ME) == 4 * 11_500 * 15_000 // BP**2 == 6          # 4 * 1.15 * 1.5 = 6.9, rounded down
    assert strength(s, r, THEM) == 10 * 12_500 // BP == 12                  # 12.5 rounded down
    odd = new_save(r, (entry(ME, ADD, 1_250, "x"),))
    assert strength(odd, r, ME) == 4 * 11_250 // BP == 4                    # 4.5 rounded down, once
    assert strength(new_save(r), r, ME) == 4 and strength(new_save(r), r, THEM) == 10


def test_the_sum_of_adds_is_floored_at_zero_so_a_strength_never_goes_negative():
    r = world()
    assert strength(new_save(r, (entry(ME, ADD, -30_000, "curse"),)), r, ME) == 0


def test_explain_names_every_entry_in_stack_order_chips_included_and_ignores_other_targets():
    chip = ChipDef(ChipId("hurt"), AtLeast(StoreValue(store_id(0)), 0, 0), (entry(ME, MUL, 5_000, "hurt"),))
    r = world(chips=(chip,))
    other = entry(THEM, ADD, 100, "elsewhere")
    s = new_save(r, (entry(ME, ADD, 1_000, "spear"), other, entry(ME, ADD, 500, "belt"), entry(ME, MUL, 20_000, "oath")))
    e = explain_strength(s, r, ME)
    assert (e.target, e.base, e.value) == (ME, 4, strength(s, r, ME))
    assert [m.source for m in e.adds] == ["spear", "belt"] and [m.source for m in e.muls] == ["oath", "hurt"]
    assert other not in e.adds + e.muls


@given(st.integers(0, 40), st.lists(st.tuples(st.sampled_from([ADD, MUL]), st.integers(-3_000, 30_000)), max_size=4),
       st.sampled_from([ADD, MUL]), st.integers(0, 30_000))
def test_a_raising_entry_never_lowers_a_side_or_a_threat(
    base: int, entries: list[tuple[ModifierKind, int]], kind: ModifierKind, bp: int,
):
    """Invariant 82, strength half. A raising entry is add_bp >= 0 or mul_bp >= BP."""
    bp = bp if kind is ADD else BP + bp
    r = replace(world(), sides=(SideDef(HAND, base),), threats=(ThreatDef(WOLF, max(base, 1)),))
    for target in (ME, THEM):
        floor = {ADD: 0, MUL: BP} if target == THEM else {ADD: -BP, MUL: 0}   # a threat's stack only has raising entries
        mods = tuple(entry(target, k, max(floor[k], b), "e") for k, b in entries)
        before = strength(new_save(r, mods), r, target)
        after = strength(new_save(r, mods + (entry(target, kind, bp, "more"),)), r, target)
        assert after >= before


type Parts = dict[str, tuple[object, ...]]


def _chip_with(m: Modifier) -> Parts:
    return {"chips": (ChipDef(ChipId("c"), AtLeast(StoreValue(store_id(0)), 0, 0), (m,)),)}


def _in_card_outcome(m: Modifier) -> Parts:
    return {"cards": (replace(card(0), cap=1, outcome=Outcome(modifiers=(m,))),)}


def _in_card_finished(m: Modifier) -> Parts:
    return {"cards": (replace(card(0), cap=1, finished=Outcome(modifiers=(m,))),)}


def _in_answer(m: Modifier) -> Parts:
    return {"offers": (OfferDef(OfferId("o"), (AnswerDef(AnswerId("a"), Outcome(modifiers=(m,))), AnswerDef(AnswerId("b")))),)}


def _in_trigger(m: Modifier) -> Parts:
    return {"triggers": (ramp(RAMP, m),)}


AIMED = entry(THEM, ADD, 500, "ramp")


def test_a_threat_entry_in_a_triggers_outcome_sourced_by_it_is_valid():
    """The control for every refusal below."""
    for m in (AIMED, entry(THEM, MUL, BP, "ramp"), entry(THEM, ADD, 0, "ramp"), entry(THEM, MUL, 20_000, "ramp")):
        validate_rules(replace(world(), **_in_trigger(m)))


@pytest.mark.parametrize("where", [_in_card_outcome, _in_card_finished, _in_answer, _chip_with], ids=lambda f: f.__name__)
def test_a_threat_entry_anywhere_but_a_triggers_outcome_is_refused(where: Callable[[Modifier], Parts]):
    """Invariant 83, the rule half: "never by your defences". Planted control: the same entry in a trigger passes."""
    validate_rules(replace(world(), **_in_trigger(AIMED)))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), **where(replace(AIMED, source=SourceId("c")) if where is _chip_with else AIMED)))


@pytest.mark.parametrize("low", [entry(THEM, ADD, -1, "ramp"), entry(THEM, MUL, BP - 1, "ramp"), entry(THEM, MUL, 0, "ramp")],
                         ids=["add", "mul-just-under", "mul-zero"])
def test_a_lowering_threat_entry_is_refused_even_in_a_trigger(low: Modifier):
    validate_rules(replace(world(), **_in_trigger(AIMED)))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), **_in_trigger(low)))


def test_a_threat_entry_must_be_sourced_by_its_trigger_and_name_a_known_threat():
    validate_rules(replace(world(), **_in_trigger(AIMED)))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), **_in_trigger(entry(THEM, ADD, 500, "gear"))))
    with pytest.raises(InvalidRulesError):                              # another trigger's id is not its own
        validate_rules(replace(world(), triggers=(ramp(RAMP2, AIMED), ramp(RAMP))))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), **_in_trigger(entry(ThreatStrength(ThreatId("ghost")), ADD, 5, "ramp"))))


def test_side_entries_come_from_anywhere_and_a_chip_may_lower_one():
    lower = entry(ME, MUL, 5_000, "c")
    for where in (_chip_with, _in_trigger, _in_answer, _in_card_outcome, _in_card_finished):
        validate_rules(replace(world(), **where(replace(lower, source=SourceId("c") if where is _chip_with else lower.source))))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), **_in_trigger(entry(SideStrength(SideId("ghost")), ADD, 5, "ramp"))))


def test_sides_and_threats_have_unique_ids_a_side_base_of_zero_or_more_and_a_threat_base_above_zero():
    validate_rules(replace(world(), sides=(SideDef(HAND, 0),)))
    for bad in (dict(sides=(SideDef(HAND, 1), SideDef(HAND, 2))), dict(threats=(ThreatDef(WOLF, 1), ThreatDef(WOLF, 2))),
                dict(sides=(SideDef(HAND, -1),)), dict(threats=(ThreatDef(WOLF, 0),))):
        with pytest.raises(InvalidRulesError):
            validate_rules(replace(world(), **bad))


def test_a_lowering_threat_entry_in_a_starting_stack_is_refused_a_raising_one_is_not():
    r = world()
    new_save(r, (entry(THEM, ADD, 100, "gear"),))
    for low in (entry(THEM, ADD, -100, "gear"), entry(THEM, MUL, BP - 1, "gear")):
        with pytest.raises(InvalidVerbError):
            new_save(r, (low,))


def test_no_threat_falls_over_a_play_whatever_the_clock_does():
    """Invariant 83, the save half: sampled across a ramp, ThreatStrength is non-decreasing at every instant, while a
    side entry from a chip may move it either way."""
    r = world(triggers=(ramp(RAMP, entry(THEM, ADD, 5_000, "ramp"), at=100), ramp(RAMP2, entry(THEM, MUL, 20_000, "ramp2"), at=300)))
    s, seen = new_save(r), list[int]()
    for t in range(0, 500, 25):
        s = advance(s, r, t)
        seen.append(strength(s, r, THEM))
    assert seen == sorted(seen) and seen[0] == 10 and seen[-1] == 10 * 15_000 * 20_000 // BP**2 == 30
