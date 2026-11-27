"""Which ledger lines need the player: covered, falling and starved, read off a save at its time. Reads only.

The read model's ledger (view.py) and View.all_covered read it, so "every line white" is one rule. Semantics:
engine/design/, "Read model" and "Starved line".
"""
from ..offers.answers import AnswerKind, AnswerOffer
from ..loop.cardsides import card_makes, outcome_stores
from ..unlocks.gates import is_unlocked
from ..core.ids import CardId, StoreId
from ..core.index import index
from ..orders.lanes import TapCard
from ..mixes.mixes import flatten_shares
from ..orders.orders import OrderVerb
from ..orders.plan import is_dead, live_queue_verb
from ..core.memo import SaveMemo
from ..core.rules import Rules
from ..core.state import Save
from ..unlocks.unlocks import Unlock, UnlockKind
from ..loop.work import starved


def covered(save: Save, rules: Rules, store: StoreId) -> bool:
    """Some order's verb (latched or not) or the queue's controlling entry makes this store, a dead verb covering
    nothing; or a card paused full pays it, and resumes as it falls (design/full-output.txt, "FULL OUTPUT", "Read model")."""
    return store in _COVERING.get(save, rules, lambda: _covering(save, rules)) or _held_full(save, rules, store)


_COVERING: SaveMemo[frozenset[StoreId]] = SaveMemo(2)
"""The stores the live verbs make, read once per save: the ledger asks of every store."""


def _covering(save: Save, rules: Rules) -> frozenset[StoreId]:
    queued = live_queue_verb(save, rules)
    verbs = [a for o in save.orders for a in o.actions] + ([] if queued is None else [queued])
    return frozenset(st for v in dict.fromkeys(verbs) if not is_dead(save, rules, v) for st in _made(save, rules, v))


def _held_full(save: Save, rules: Rules, store: StoreId) -> bool:
    cards = index(rules).cards
    return any((c := cards.get(CardId(p.runner))) is not None and p.store in card_makes(c) and store in outcome_stores(c)
               for p in save.pauses)


def all_covered(save: Save, rules: Rules) -> bool:
    """No unlocked store's line needs the player: none falling uncovered and none starved."""
    return not any((st.segment.rate < 0 and not covered(save, rules, d.id)) or starved(save, rules, d.id)
                   for d, st in zip(rules.stores, save.stores)
                   if is_unlocked(save, rules, Unlock(UnlockKind.STORE, d.id)))


def _made(save: Save, rules: Rules, verb: OrderVerb) -> frozenset[StoreId]:
    ix = index(rules)
    if isinstance(verb, TapCard):
        return _card_made(rules, verb.card, set())
    if isinstance(verb, (AnswerOffer, AnswerKind)):
        return frozenset()   # it acts once: covered is about what keeps a line fed
    return frozenset(st for s in flatten_shares(save.mixes, verb.mix) for st in card_makes(ix.cards[s.card]))


def _card_made(rules: Rules, card: CardId, seen: set[CardId]) -> frozenset[StoreId]:
    """What the card's outcome adds, what its flows make, and what any card its outcome starts makes."""
    c = index(rules).cards.get(card)
    if c is None or card in seen:
        return frozenset()
    seen.add(card)
    return card_makes(c).union(*(_card_made(rules, q, seen) for q in c.outcome.starts))
