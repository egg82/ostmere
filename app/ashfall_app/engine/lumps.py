"""A card's lump lines, and what moves a store: its flows plus each lump paid by its card's work (DESIGN.txt, "Rate
form"; motion.store_segment puts them together).

Below rates in the import order: it reads the rules, the effective stack and the cards' work, never what runs.
"""
from collections.abc import Callable
from math import lcm

from .cards import Amount, CardDef
from .counts import unit
from .fightlines import fight_costs, fight_makes
from .gates import effective_stack, stack_inputs
from .ids import ActionId, CardId, StoreId
from .index import derived, index
from .memo import PartsMemo
from .modifiers import FlowKind, Modifier, RateRef, Run, RunKind, Target, modified_rate
from .rules import Rules, StandingDef
from .segments import Lump, LumpSegment, Segment
from .state import Save
from .units import BP, QUANTITY_SCALE


def lump_of(card: CardDef, ref: RateRef) -> int:
    """The per-completion quantity of the card's line `ref` (an outcome store for a make, an input for a cost), 0 when
    the line is a flow: a store is on a card once, so a line is a flow or a lump (validation)."""
    return sum(a.quantity for a in _amounts(card, ref.kind) if a.store == ref.store)


def _amounts(card: CardDef, kind: FlowKind) -> tuple[Amount, ...]:
    """The per-completion amounts of one side: outcome stores, or inputs and drains; then what the card's fight adds."""
    if kind is FlowKind.MAKE:
        return card.outcome.stores + (fight_makes(card.fight) if card.fight else ())
    return card.inputs + card.drains + (fight_costs(card.fight) if card.fight else ()) if kind is FlowKind.COST else ()


def has_lump(card: CardDef, ref: RateRef) -> bool:
    """The card's line `ref` carries a per-completion amount."""
    return lump_of(card, ref) > 0


def base_of(rules: Rules, ref: RateRef) -> tuple[int, int]:
    """(base, base_den) of a line at a 100% share: a flow's per_hour over 1; a card's lump line, the lump's quantity
    over work_s. Validation keeps a flow and a lump off one store of one card (DESIGN.txt, "Rate form")."""
    ix = index(rules)
    card = ix.cards.get(CardId(ref.runner))
    if card is None:
        a = ix.standing[ActionId(ref.runner)]
        if ref.kind is FlowKind.XP:
            return a.xp_per_hour, 1
        fought = _fought(a, ref)
        if fought:
            return fought, QUANTITY_SCALE
        return sum(f.per_hour for f in (a.makes if ref.kind is FlowKind.MAKE else a.costs) if f.store == ref.store), 1
    if ref.kind is FlowKind.XP:
        return card.xp_per_hour, 1
    lump = lump_of(card, ref)
    if lump > 0:
        return lump, card.work_s
    flows = card.makes if ref.kind is FlowKind.MAKE else card.costs
    return sum(f.per_hour for f in flows if f.store == ref.store), 1


def _fought(a: StandingDef, ref: RateRef) -> int:
    """A standing fight's line on `ref`: the amount per fight times fights per hour (over QUANTITY_SCALE, a rate)."""
    if a.fight is None:
        return 0
    amounts = fight_makes(a.fight) if ref.kind is FlowKind.MAKE else fight_costs(a.fight)
    return sum(x.quantity for x in amounts if x.store == ref.store) * a.fight.per_hour


_AIMED: PartsMemo[dict[Target, tuple[Modifier, ...]]] = PartsMemo(8)
"""The effective stack's entries by what they aim at, in stack order: a function of the stack alone."""
_AMOUNTS: PartsMemo[dict[tuple[RateRef, tuple[Modifier, ...]], int]] = PartsMemo()
"""A lump's amount by its line and the entries aimed at it, kept while the rules are the same: a stack that changes
elsewhere (a fight's odds entries, a rule on another line) leaves every amount as it was."""


def lump_amount(save: Save, rules: Rules, card: CardDef, ref: RateRef) -> int:
    """What one whole completion moves on the line `ref`: its lump under the modifiers aimed at the line itself (not
    the speed ones, which change how fast the work runs, not what a completion is), rounded down for an outcome store
    and up for an input, as the rate formula rounds makes and costs."""
    return _amount(card, ref, _aimed_by_target(save, rules), _AMOUNTS.get((rules,), dict))


def _aimed_by_target(save: Save, rules: Rules) -> dict[Target, tuple[Modifier, ...]]:
    return _AIMED.get(stack_inputs(save, rules), lambda: _aimed(save, rules), save.chips)


def _amount(card: CardDef, ref: RateRef, aimed: dict[Target, tuple[Modifier, ...]],
            kept: dict[tuple[RateRef, tuple[Modifier, ...]], int]) -> int:
    own = aimed.get(ref, ())
    found = kept.get((ref, own))
    if found is None:
        found = kept[ref, own] = modified_rate(ref, lump_of(card, ref), BP, own, Run(RunKind.FULL)).per_hour
    return found


def _aimed(save: Save, rules: Rules) -> dict[Target, tuple[Modifier, ...]]:
    found: dict[Target, list[Modifier]] = {}
    for m in effective_stack(save, rules):
        found.setdefault(m.target, []).append(m)
    return {target: tuple(ms) for target, ms in found.items()}


def motion(seg: Segment, flow: int, den: int, lumps: tuple[Lump, ...]) -> Segment:
    """A store's plain Segment (start, value, limit) moved by `flow` and the `lumps` moving it (moving_lumps), its rate
    the exact slope rounded down: itself when no lump moves it, or when it is held still (rate 0 and no limit)."""
    if not lumps or (seg.rate == 0 and seg.limit is None):
        return seg
    rate = (flow * den + sum(k.num * k.work.rate for k in lumps)) // den
    return LumpSegment(seg.start, seg.start_value, rate, seg.limit, flow, den, lumps)


type Terms = tuple[int, tuple[tuple[CardId, int], ...]]
"""A store's den and, per lump line on it, its card and what one unit of the card's work moves the store, over den
(negative for an input); den is one for the store, the lcm of the work per completion of every card with a lump on
it."""
NO_TERMS: Terms = (1, ())


def moving_lumps(terms: Terms, work: Callable[[CardId], Segment]) -> tuple[int, tuple[Lump, ...]]:
    """(den, lumps): each of a store's lump `terms` whose card's `work` is rising."""
    den, lines = terms
    return den, tuple(Lump(seg, num) for card, num in lines if (seg := work(card)).rate > 0)


_TERMS: PartsMemo[dict[StoreId, Terms]] = PartsMemo(8)


def lump_terms(save: Save, rules: Rules) -> dict[StoreId, Terms]:
    """Each store's Terms, for the stores some card has a lump on: a function of the effective stack, kept as
    lump_amount is."""
    def build() -> dict[StoreId, Terms]:
        found: dict[StoreId, Terms] = {}
        aimed, kept = _aimed_by_target(save, rules), _AMOUNTS.get((rules,), dict)
        for store, lines in derived(rules, "_lump_lines", _all_lump_lines).items():
            den = lcm(*(unit(card) for card, _ in lines))
            found[store] = den, tuple((card.id, _signed(card, ref, aimed, kept) * (den // unit(card)))
                                      for card, ref in lines)
        return found
    return _TERMS.get(stack_inputs(save, rules), build, save.chips)


def _signed(card: CardDef, ref: RateRef, aimed: dict[Target, tuple[Modifier, ...]],
            kept: dict[tuple[RateRef, tuple[Modifier, ...]], int]) -> int:
    amount = _amount(card, ref, aimed, kept)
    return amount if ref.kind is FlowKind.MAKE else -amount


def drainers(rules: Rules, store: StoreId) -> frozenset[CardId]:
    """The cards with a drain on `store` (DESIGN.txt, "DRAINS")."""
    return derived(rules, "_drainers", _all_drainers).get(store, frozenset())


def _all_drainers(rules: Rules) -> dict[StoreId, frozenset[CardId]]:
    out: dict[StoreId, set[CardId]] = {}
    for c in rules.cards:
        for a in c.drains:
            out.setdefault(a.store, set()).add(c.id)
    return {s: frozenset(cs) for s, cs in out.items()}


def forgiven(rules: Rules, store: StoreId, flow: int, terms: Terms, work: Callable[[CardId], Segment]) -> bool:
    """At 0, the store's drains take less than their rate: its net without them (`flow` and the other lump `terms`
    moving under `work`) is at or above 0 and its net with them below, so it stays at 0, the rest forgiven."""
    taken = drainers(rules, store)
    if not taken:
        return False
    den, lines = terms
    others = flow * den + sum(num * work(c).rate for c, num in lines if c not in taken)
    drained = sum(num * work(c).rate for c, num in lines if c in taken)
    return others >= 0 > others + drained


def lump_lines(rules: Rules, store: StoreId) -> tuple[tuple[CardDef, RateRef], ...]:
    """Every card's lump line on `store` (an outcome store's make, an input's cost), in rules order."""
    return derived(rules, "_lump_lines", _all_lump_lines).get(store, ())


def _all_lump_lines(rules: Rules) -> dict[StoreId, tuple[tuple[CardDef, RateRef], ...]]:
    out: dict[StoreId, list[tuple[CardDef, RateRef]]] = {}
    for c in rules.cards:
        for kind in (FlowKind.MAKE, FlowKind.COST):
            for a in _amounts(c, kind):
                out.setdefault(a.store, []).append((c, RateRef(c.id, kind, a.store)))
    return {s: tuple(lines) for s, lines in out.items()}
