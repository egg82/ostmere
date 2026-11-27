"""A working's chain on a group threat: what is due, how far it reaches, and the links one completion resolves
(design/spells.txt, "SPELLS"). Reads the runner's tallies; writes only its chained tally and the link lines."""
from dataclasses import dataclass

from ..cards.cards import Amount, Outcome
from ..cards.counts import is_completed
from ..unlocks.gates import base_stack, is_unlocked
from ..people.gone import is_left
from ..core.ids import ActionId, CardId, LineKey, StoreId
from ..core.index import index
from ..modifiers.modifiers import ChainReach
from ..loop.motion import store_segment
from ..core.rules import Rules
from ..core.state import Save
from .strengthmath import StrengthExplanation, explain_over
from ..core.units import QUANTITY_SCALE
from ..unlocks.unlocks import Unlock, UnlockKind
from ..loop.work import apply_outcome


@dataclass(frozen=True)
class ChainView:
    """One unlocked card with a chain, neither completed nor on a left lane: its reach now with every entry behind it,
    and what is due on its runner now."""

    card: CardId
    runner: ActionId
    reach: StrengthExplanation
    due: int


def due(save: Save, rules: Rules, runner: ActionId) -> int:
    """The group members under way still to be fought: m - ((F + C) mod m) while the runner fights (its fought tally
    rises now), else 0. F and C: its fought and chained tallies, floored to whole fights."""
    ix = index(rules)
    fight = ix.standing[runner].fight
    assert fight is not None and fight.fought is not None
    if store_segment(save, rules, fight.fought).rate <= 0:
        return 0
    members = next(t.members for t in rules.threats if t.id == fight.threat)
    done = _whole(save, rules, fight.fought) + (0 if fight.chained is None else _whole(save, rules, fight.chained))
    return members - done % members


def reach(save: Save, rules: Rules, card: CardId) -> StrengthExplanation:
    """The card's chain reach now: ChainDef.reach under the entries of base_stack aimed at ChainReach(card)."""
    return explain_over(base_stack(save, rules), rules, ChainReach(card))


def resolve(save: Save, rules: Rules, card: CardId, room: int) -> tuple[Save, tuple[LineKey, ...], tuple[LineKey, ...]]:
    """The chain of `card`'s completion, now: k = min(due, reach, room) links added to the runner's chained tally, and
    k link lines. Returns the save, the link lines (the card's, in link order) and any chip on_line the add shows."""
    chain = index(rules).cards[card].chain
    assert chain is not None
    k = min(due(save, rules, chain.runner), reach(save, rules, card).value, max(0, room))
    if k == 0:
        return save, (), ()
    fight = index(rules).standing[chain.runner].fight
    assert fight is not None and fight.chained is not None
    links = tuple(chain.lines[min(i, len(chain.lines)) - 1] for i in range(1, k + 1))
    save, lines = apply_outcome(save, rules, Outcome(stores=(Amount(fight.chained, k * QUANTITY_SCALE),), lines=links))
    return save, lines[:k], lines[k:]


def chain_views(save: Save, rules: Rules) -> tuple[ChainView, ...]:
    """In rules.cards order. Reading writes nothing."""
    return tuple(ChainView(c.id, c.chain.runner, reach(save, rules, c.id), due(save, rules, c.chain.runner))
                 for c in rules.cards
                 if c.chain is not None and is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id))
                 and not is_left(save, c.lane) and not is_completed(save, rules, c.id))


def _whole(save: Save, rules: Rules, store: StoreId) -> int:
    return store_segment(save, rules, store).start_value // QUANTITY_SCALE
