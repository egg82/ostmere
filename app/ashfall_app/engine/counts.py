"""What a card's work says: its completions, its effective cap, whether it is completed, which saved mixes are greyed.

Below rates and work in the import order, so both read the same derived facts (DESIGN.txt, "Caps", "Greyed mix").
"""
from .cards import CardDef, CardState
from .gone import left_cards
from .ids import HANDS, CardId, MixId
from .index import index
from .memo import PartsMemo, SaveMemo
from .mixes import flatten_shares
from .rules import Rules
from .segments import Segment
from .state import Save
from .units import BP
from .unlocks import UnlockKind


def unit(card: CardDef) -> int:
    """Work units in one completion."""
    return card.work_s * BP


_CARDS: SaveMemo[dict[CardId, CardState]] = SaveMemo()


def card_state(save: Save, card: CardId) -> CardState | None:
    return _CARDS.get(save, None, lambda: {cs.card: cs for cs in save.cards}).get(card)


def work_segment(save: Save, card: CardId) -> Segment:
    """The card's work segment, or a still zero one at save.time when the card has none yet."""
    cs = card_state(save, card)
    return Segment(save.time, 0, 0) if cs is None else cs.work


def repeating(save: Save, rules: Rules, card: CardId) -> bool:
    """The card is tapped on its lane, a declared one, and its work runs with no limit: a repeating tap, which does
    not end by itself (DESIGN.txt, "REPEATING TAPS"). Only retap.settle starts one; a fresh tap is bounded."""
    lane = index(rules).cards[card].lane
    seg = work_segment(save, card)
    return lane != HANDS and seg.limit is None and seg.rate > 0 and any(
        ls.lane == lane and ls.card == card for ls in save.lanes)


def work_value(save: Save, card: CardId) -> int:
    return work_segment(save, card).start_value


def completions(save: Save, rules: Rules, card: CardId) -> int:
    cs = card_state(save, card)
    return (0 if cs is None else cs.work.start_value) // unit(index(rules).cards[card])


def effective_cap(save: Save, rules: Rules, card: CardId) -> int | None:
    cap = index(rules).cards[card].cap
    cs = card_state(save, card)
    return None if cap is None else cap + (0 if cs is None else cs.raised)


_RETIRED: PartsMemo[frozenset[str]] = PartsMemo()
"""The retired cards' ids, kept while the rules and the save's unlock set are the same objects (unlocked.py keeps its
set the same way)."""


def is_retired(save: Save, rules: Rules, card: CardId) -> bool:
    """Unlock(RETIRED, card) is in the unlock set (never with rules.opening None, where nothing is gated), or the card's
    lane has left (DESIGN.txt, "LEAVES": held as JOINED is, so with any opening)."""
    return card in _RETIRED.get((save.unlocked, rules), lambda: _retired(save, rules))


def _retired(save: Save, rules: Rules) -> frozenset[str]:
    named: frozenset[str] = frozenset() if rules.opening is None else frozenset(
        u.id for u in save.unlocked if u.kind is UnlockKind.RETIRED)
    return named | left_cards(save, rules)


def is_completed(save: Save, rules: Rules, card: CardId) -> bool:
    """Out of play: retired, or its completions have reached its cap (DESIGN.txt, "Caps", "Retired")."""
    if is_retired(save, rules, card):
        return True
    cap = effective_cap(save, rules, card)
    return cap is not None and completions(save, rules, card) >= cap


def greyed(save: Save, rules: Rules, mix: MixId) -> bool:
    return any(is_completed(save, rules, s.card) for s in flatten_shares(save.mixes, mix))
