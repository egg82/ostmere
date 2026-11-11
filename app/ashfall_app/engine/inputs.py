"""What a tap of a card still takes of its input stores: its whole inputs per completion and the rest of the current
one (DESIGN.txt, "Inputs against a dry store"). Reads only."""
from . import counts, gates
from .cards import CardDef
from .ids import CardId, StoreId
from .lumps import lump_amount
from .memo import PartsMemo
from .modifiers import FlowKind, RateRef
from .rules import Rules
from .state import Save
from .units import ceil_div


def input_rest(save: Save, rules: Rules, card: CardDef) -> tuple[tuple[StoreId, int], ...]:
    """What the rest of the card's current completion still takes of each input store, in declaration order: the
    inputs per completion under the modifiers aimed at the line (not the speed ones, which cancel), rounded up as costs
    are, and prorated to the work left. A store whose rest is 0 is left out."""
    done = counts.work_value(save, card.id) % counts.unit(card)
    found: list[tuple[StoreId, int]] = []
    for store, whole in input_whole(save, rules, card):
        rest = whole if done == 0 else ceil_div(whole * (counts.unit(card) - done), counts.unit(card))
        if rest > 0:
            found.append((store, rest))
    return tuple(found)


_WHOLE: PartsMemo[dict[CardId, tuple[tuple[StoreId, int], ...]]] = PartsMemo(8)
"""A card's whole inputs read the effective stack alone, so they are kept as rates' lines are (rates._kept_line)."""


def input_whole(save: Save, rules: Rules, card: CardDef) -> tuple[tuple[StoreId, int], ...]:
    """What one whole completion takes of each input store, in declaration order: the inputs per completion under the
    modifiers aimed at the line (not the speed ones, which cancel), rounded up as costs are."""
    kept = _WHOLE.get(gates.stack_inputs(save, rules), dict, save.chips)
    found = kept.get(card.id)
    if found is None:
        found = kept[card.id] = _input_whole(save, rules, card)
    return found


def _input_whole(save: Save, rules: Rules, card: CardDef) -> tuple[tuple[StoreId, int], ...]:
    return tuple((a.store, lump_amount(save, rules, card, RateRef(card.id, FlowKind.COST, a.store)))
                 for a in card.inputs)
