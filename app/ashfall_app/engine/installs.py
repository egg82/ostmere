"""What an outcome adds to the player's plan, installed rules (Outcome.orders) and queued one-offs (Outcome.queues),
and what it takes away, the orders tapping retired chores (Outcome.retire_orders). Afterwards nothing tells either from
what the player set. Semantics: DESIGN.txt, "Installed rule", "Queued one-off", "Retired chores"."""
from collections.abc import Callable, Collection
from dataclasses import replace

from .cards import RuleInstall
from .counts import completions
from .ids import CardId
from .lanes import TapCard
from .orders import AfterTime, AtLeast, CardCount, Latch, Order, OrderVerb, QueueEntry, initial_latch, pruned, rule_on
from .orders import placed, unplaced
from .rules import Rules
from .state import Save


def always_rule(install: RuleInstall) -> Order:
    """The one shape an install sets: a ruled lane's always rule on its card."""
    return Order(AfterTime(0), TapCard(install.card))


def installed(save: Save, installs: tuple[RuleInstall, ...]) -> Save:
    """Each install in tuple order, unless an equal order is already set: the first=True ones as one block at the top
    (the first of them at index 0), the rest appended; each new latch as SetOrders latches a new order (always
    true)."""
    orders, latches = list(save.orders), list(save.latches)
    top = 0
    for ri in installs:
        order = always_rule(ri)
        if order in map(unplaced, orders):
            continue
        at = top if ri.first else len(orders)
        top += ri.first
        orders.insert(at, order)
        latches.insert(at, initial_latch(order.when, None, save.time))
    if len(orders) == len(save.orders):
        return save
    return replace(save, orders=placed(tuple(orders)), latches=tuple(latches))


def without_taps(save: Save, cards: Collection[CardId]) -> Save:
    """Every TapCard of one of `cards` taken out of the orders' actions (without_actions)."""
    if not cards:
        return save
    return without_actions(save, lambda o, a: isinstance(a, TapCard) and a.card in cards)


def without_actions(save: Save, drop: Callable[[Order, OrderVerb], bool]) -> Save:
    """Each order with the actions `drop` names taken out of its list (orders.pruned), keeping its place and its latch;
    an order left with none is removed with its latch (DESIGN.txt, "OR ELSE")."""
    kept: list[tuple[Order, Latch]] = []
    for o, on in zip(save.orders, save.latches):
        p = pruned(o, lambda a, o=o: drop(o, a))
        if p is not None:
            kept.append((p, on))
    if [o for o, _ in kept] == list(save.orders):
        return save
    return replace(save, orders=tuple(o for o, _ in kept), latches=tuple(on for _, on in kept))


def when_ready(save: Save, rules: Rules, card: CardId) -> QueueEntry:
    """The page's When ready entry for one more completion of `card`: tap it until its count reaches the next."""
    n = completions(save, rules, card) + 1
    return QueueEntry(TapCard(card), AtLeast(CardCount(card), n, n))


def queued(save: Save, rules: Rules, cards: tuple[CardId, ...]) -> Save:
    """Each card's When ready entry at the queue's front, several in tuple order, unless an equal entry is already
    queued (DESIGN.txt, "Queued one-off")."""
    entries: list[QueueEntry] = []
    for card in cards:
        e = when_ready(save, rules, card)
        if e not in save.queue and e not in entries:
            entries.append(e)
    return replace(save, queue=(*entries, *save.queue)) if entries else save


def requeued(save: Save, rules: Rules, card: CardId) -> Save:
    """`card`'s When ready entry at the queue's front unless a true order or a queue entry already taps it: the way an
    interrupted hands task is taken up again (DESIGN.txt, "CURE CUT-IN", "Inputs against a dry store")."""
    verb = TapCard(card)
    planned = any(rule_on(on) and verb in o.actions for o, on in zip(save.orders, save.latches)) \
        or any(e.verb == verb for e in save.queue)
    return save if planned else queued(save, rules, (card,))
