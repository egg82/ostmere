"""How the content reads a cure: the stores a card puts up. One reading, shared by the day-one cures gate
(tests/dayone/cures.py, a chip's cure) and the fight checks (opening/fight_checks.py, a lost fight's loses store)."""
from .cards import CardDef
from .gates import shown_chips
from .ids import CardId, ChipId
from .index import derived
from .orders import AtLeast, AtMost, CardCount, StoreValue
from .rules import Rules
from .state import Save
from .unlocks import UnlockKind


def puts_up(rules: Rules, card: CardDef) -> set[str]:
    """The stores a card puts up: what it feeds directly, and what the standing actions it unlocks make."""
    standing = {str(a.id): a for a in rules.standing}
    unlocked = [u.id for o in (card.outcome, card.finished) for u in o.unlocks if u.kind is UnlockKind.ACTION]
    return {*feeds(rules, card), *(str(f.store) for a in unlocked if a in standing for f in standing[a].makes)}


def feeds(rules: Rules, card: CardDef) -> set[str]:
    """The stores a card itself adds to: what its completion adds, what its lines make, what a trigger on its own
    completion count adds. A standing action it merely unlocks is not the card feeding."""
    return {*(str(a.store) for o in (card.outcome, card.finished) for a in o.stores), *(str(f.store) for f in card.makes),
            *count_stores(rules, card)}


def count_stores(rules: Rules, card: CardDef) -> dict[str, int]:
    """Each store a trigger adds once the card's own completion count is at least n, with the least such n."""
    return dict(derived(rules, "_count_stores", _count_stores).get(card.id, {}))


def _count_stores(rules: Rules) -> dict[CardId, dict[str, int]]:
    """count_stores of every card, the triggers read once."""
    found: dict[CardId, dict[str, int]] = {}
    for t in rules.triggers:
        if isinstance(t.when, AtLeast) and isinstance(t.when.subject, CardCount):
            mine = found.setdefault(t.when.subject.card, {})
            for a in t.outcome.stores:
                mine[str(a.store)] = min(t.when.value, mine.get(str(a.store), t.when.value))
    return found


def takes(rules: Rules, card: CardDef) -> set[str]:
    """The stores a card takes from: its inputs, its drains, its cost lines, and the cost lines of the standing actions
    it unlocks."""
    standing = {str(a.id): a for a in rules.standing}
    unlocked = [u.id for o in (card.outcome, card.finished) for u in o.unlocks if u.kind is UnlockKind.ACTION]
    return {*(str(a.store) for a in (*card.inputs, *card.drains)), *(str(f.store) for f in card.costs),
            *(str(f.store) for a in unlocked if a in standing for f in standing[a].costs)}


def cures_chip(rules: Rules, card: CardId, chip: ChipId) -> bool:
    """Whether `card` moves the store `chip` watches toward clearing it: up for a chip that shows while the store is
    low (AtMost), down for one that shows while it is high (AtLeast)."""
    return card in derived(rules, "_cure_reading", _reading).get(chip, frozenset())


def cures_shown(save: Save, rules: Rules, card: CardId) -> bool:
    """Whether `card` is a cure for a chip shown now (DESIGN.txt, "CURE CUT-IN")."""
    return any(cures_chip(rules, card, c) for c in shown_chips(save, rules))


def _reading(rules: Rules) -> dict[ChipId, frozenset[CardId]]:
    """The cards that cure each chip watching a store."""
    moves = {c.id: (puts_up(rules, c), takes(rules, c)) for c in rules.cards}
    found: dict[ChipId, frozenset[CardId]] = {}
    for chip in rules.chips:
        when = chip.when
        if isinstance(when, (AtLeast, AtMost)) and isinstance(when.subject, StoreValue):
            store, up = str(when.subject.store), isinstance(when, AtMost)
            found[chip.id] = frozenset(c for c, m in moves.items() if store in m[0 if up else 1])
    return found
