"""Which ledger lines need the player: covered, falling and starved, read off a save at its time. Reads only.

The read model's ledger (view.py) and View.all_covered read it, so "every line white" is one rule. Semantics:
DESIGN.txt, "Read model" and "Starved line".
"""
from .answers import AnswerKind, AnswerOffer
from .cardsides import card_makes
from .gates import is_unlocked
from .ids import CardId, StoreId
from .index import index
from .lanes import TapCard
from .mixes import flatten_shares
from .orders import OrderVerb
from .plan import is_dead, live_queue_verb
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind
from .work import starved


def covered(save: Save, rules: Rules, store: StoreId) -> bool:
    """Some order's verb (latched or not) or the queue's controlling entry makes this store; a dead verb covers
    nothing."""
    queued = live_queue_verb(save, rules)
    verbs = [o.then for o in save.orders] + ([] if queued is None else [queued])
    return any(_makes(save, rules, v, store) for v in verbs if not is_dead(save, rules, v))


def all_covered(save: Save, rules: Rules) -> bool:
    """No unlocked store's line needs the player: none falling uncovered and none starved."""
    return not any((st.segment.rate < 0 and not covered(save, rules, d.id)) or starved(save, rules, d.id)
                   for d, st in zip(rules.stores, save.stores)
                   if is_unlocked(save, rules, Unlock(UnlockKind.STORE, d.id)))


def _makes(save: Save, rules: Rules, verb: OrderVerb, store: StoreId) -> bool:
    ix = index(rules)
    if isinstance(verb, TapCard):
        return _card_makes(rules, verb.card, store, set())
    if isinstance(verb, (AnswerOffer, AnswerKind)):
        return False   # it acts once: covered is about what keeps a line fed
    return any(store in card_makes(ix.cards[s.card]) for s in flatten_shares(save.mixes, verb.mix))


def _card_makes(rules: Rules, card: CardId, store: StoreId, seen: set[CardId]) -> bool:
    """What the card's outcome adds, what its flows make, or what any card its outcome starts makes."""
    c = index(rules).cards.get(card)
    if c is None or card in seen:
        return False
    seen.add(card)
    return store in card_makes(c) or any(_card_makes(rules, q, store, seen) for q in c.outcome.starts)
