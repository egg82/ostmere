"""Invariants 116 and 117, the engine half (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "Validation", "Rebase"):
InvalidRulesError for a WhileRunning naming an undeclared side (a threat's id included), amount_bp below 1, one side
twice in a card, and any rules Modifier whose source begins "held:"; rebasing any save the engine returned under the
rules without while_running into rules that add it (or the reverse) succeeds and keeps its time, stores, card work and
unlocks."""
from collections.abc import Callable
from dataclasses import replace
from typing import Any

import pytest

from ashfall_app.engine import (
    AfterTime, ChipDef, ChipId, InvalidRulesError, InvalidVerbError, Modifier, ModifierKind, Outcome, Rules, Save, SideId,
    SideStrength, SourceId, TapCard, TriggerDef, TriggerId, advance, decide, encode, new_save, rebase, validate_rules,
)
from held_world import G, G2, GA, GH, GH2, HF, HELD, WOLF, hands, ja, kills, plain, town, world, wr

type Edit = Callable[[Rules], Rules]


def card_with(card: str, **kw: Any) -> Edit:
    return lambda r: replace(r, cards=tuple(replace(c, **kw) if c.id == card else c for c in r.cards))


def entries(*e: Any) -> Edit:
    return card_with(GH, while_running=tuple(e))


def held_mod(source: str) -> Modifier:
    return Modifier(SideStrength(G), ModifierKind.ADD_BP, 100, SourceId(source))


def trigger_with(m: Modifier) -> Edit:
    t = TriggerDef(TriggerId("t"), AfterTime(5), Outcome(modifiers=(m,)))
    return lambda r: replace(r, triggers=(t,))


BAD: dict[str, Callable[[], Edit]] = {
    "an undeclared side": lambda: entries(wr(SideId("nope"), 1000)),
    "a threat's id as the side": lambda: entries(wr(SideId(WOLF), 1000)),
    "an amount of 0": lambda: entries(wr(G, 0)),
    "a negative amount": lambda: entries(wr(G, -5)),
    "one side twice in a card": lambda: entries(wr(G, 100), wr(G, 200)),
    "a held source in a trigger's outcome": lambda: trigger_with(held_mod("held:ga")),
    "a held source in a card's outcome": lambda: card_with(GH, outcome=Outcome(modifiers=(held_mod("held:gh"),))),
    "a held source in a card's finished outcome": lambda: card_with(
        "gcap", finished=Outcome(modifiers=(held_mod("held:gcap"),))),
    "a held source in a chip's effects": lambda: lambda r: replace(
        r, chips=(ChipDef(ChipId("held:x"), AfterTime(5), (held_mod("held:x"),)),)),
}
"""Each refusal is built when its test runs, so this module imports before the engine has WhileRunning."""


def test_the_valid_world_passes_the_control_for_every_refusal():
    """Controls: the fixture itself, two sides in one card, an amount of 1, and sources that merely resemble the tag."""
    r = world((ja(),))
    validate_rules(r)
    validate_rules(entries(wr(G, 100), wr(G2, 100))(r))
    validate_rules(entries(wr(G, 1))(r))
    for source in ("gh", "held", "heldx:gh", "holds:gh"):
        validate_rules(trigger_with(held_mod(source))(r))
    assert len(BAD) == 9


@kills(19)
@pytest.mark.parametrize("name", list(BAD))
def test_each_invalid_shape_is_refused(name: str):
    with pytest.raises(InvalidRulesError):
        validate_rules(BAD[name]()(world((ja(),))))


@kills(19)
def test_a_held_source_is_refused_in_a_starting_stack_too_and_another_source_is_not():
    """AMBIGUITY H1: the class raised by new_save for a held-sourced starting entry (InvalidVerbError, as for "odds:",
    or InvalidRulesError, as the sentence about validation says); either is accepted."""
    r = world((ja(),))
    new_save(r, (held_mod("gear"),))
    with pytest.raises((InvalidRulesError, InvalidVerbError)):
        new_save(r, (held_mod(HELD + "gh"),))


def saves_under(r: Rules) -> list[Save]:
    """Saves the engine returns under `r`, at several instants, with taps, mixes and the town running."""
    out: list[Save] = []
    for base in (decide(new_save(r), r, 0, TapCard(GH)), hands(r, (GH, 4000), (GH2, 4000)),
                 decide(new_save(r), r, 0, TapCard(HF)), town(r, (GA, 4000))):
        out += [advance(base, r, t) for t in (0, 33, 101, 250)]
    return out


def kept(s: Save) -> tuple[object, ...]:
    return (s.time, tuple((x.store, x.segment.start_value) for x in s.stores),
            tuple((c.card, c.work.start_value) for c in s.cards), s.unlocked)


@kills(24)
@pytest.mark.parametrize("direction", ["adding", "removing"])
def test_rebasing_any_save_across_the_addition_or_removal_of_while_running_keeps_what_it_had(direction: str):
    """Invariant 117: nothing the save earned changes; the engine's own (unchanged) instant resolution aside, it is the
    same save under the other rules."""
    r = world((ja(),))
    old, new = (plain(r), r) if direction == "adding" else (r, plain(r))
    saves = saves_under(old)
    assert len(saves) == 16
    for s in saves:
        again = rebase(encode(s, old), new)
        assert kept(again) == kept(s), s.time
        assert again.modifiers == s.modifiers, s.time
