"""A node's rank entry is the only modifier sourced NODE_PREFIX + its id (pickentries.pick_source): rules whose
outcome or chip carries such a source are refused, as are a new save's starting modifiers, so explain() never
names a node for an entry no pick made."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AfterTime, ChipDef, FlowKind, RateRef, ChipId, InvalidRulesError, InvalidVerbError, Modifier, ModifierKind, Outcome, Rules, SourceId,
    TriggerDef, TriggerId, new_save, validate_rules,
)
from tests.engine.test_prestige_impl import PICK, RULES, WOOD


def faster(source: str) -> Modifier:
    return Modifier(RateRef(PICK, FlowKind.MAKE, WOOD), ModifierKind.ADD_BP, 100, SourceId(source))


def in_trigger(source: str) -> Rules:
    return replace(RULES, triggers=(TriggerDef(TriggerId("t"), AfterTime(5), Outcome(modifiers=(faster(source),))),))


def in_chip(source: str) -> Rules:
    """A chip's effects are sourced by the chip, so the chip carries the id."""
    return replace(RULES, chips=(ChipDef(ChipId(source), AfterTime(5), (faster(source),)),))


def without_prestige(source: str) -> Rules:
    return replace(in_trigger(source), prestige=None, nodes=())


PLACES: list[Callable[[str], Rules]] = [in_trigger, in_chip, without_prestige]


@pytest.mark.parametrize("place", PLACES, ids=["trigger", "chip", "no_prestige"])
def test_a_node_source_in_content_is_refused(place: Callable[[str], Rules]):
    for source in ("nodes:a", "node", "a_node:a"):   # controls: sources that merely resemble the prefix
        validate_rules(place(source))
    with pytest.raises(InvalidRulesError, match="node source"):
        validate_rules(place("node:a"))


def test_a_node_source_in_a_new_saves_modifiers_is_refused():
    new_save(RULES, (faster("nodes:a"),))
    with pytest.raises(InvalidVerbError, match="node source"):
        new_save(RULES, (faster("node:a"),))
