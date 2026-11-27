"""The running mixes: the hands' (an order's, else the player's own) and the town's (an order's alone), and their
cards' shares with how each runs now. Semantics: engine/design/, "Order mix" and "THE TOWN'S MIX"."""
from collections.abc import Callable

from ..cards.counts import greyed, is_retired
from .groups import crewed, present
from ..core.ids import HANDS, CardId, LaneId, MixId, StoreId
from ..core.index import index
from ..core.memo import KeyedMemo, SaveMemo
from .mixes import CardShare, Mix, SpentShare, flatten_shares
from ..modifiers.modifiers import Run, RunKind
from ..orders.plan import keep_mix_ids, running_mix_id, running_town_mix_id
from ..cards.requires import first_unmet
from ..core.rules import Rules
from .spent import keep_spent, spend, spent_stores, yielded
from ..core.state import Save


def _busy(save: Save, lane: LaneId) -> bool:
    """A tap holds the lane."""
    return any(ls.lane == lane and ls.card is not None for ls in save.lanes)


def running_mix(save: Save, rules: Rules) -> Mix | None:
    """The mix the hands run now: an order's while its condition holds, else the player's own (engine/design/, "Order
    mix")."""
    mix = running_mix_id(save, rules)
    return next((m for m in save.mixes if m.id == mix), None)


def running_town_mix(save: Save, rules: Rules) -> Mix | None:
    """The town mix running now: an order's while its condition holds, else none."""
    mix = running_town_mix_id(save, rules)
    return next((m for m in save.mixes if m.id == mix), None)


type Entries = tuple[tuple[CardId, int, Run], ...]
type Gains = dict[CardId, tuple[SpentShare, ...]]

_MIX: SaveMemo[tuple[Entries, Gains]] = SaveMemo(4)
_TOWN: SaveMemo[tuple[Entries, Gains]] = SaveMemo(4)
"""A save's entries and gains, built once: running, the held entries and the view each read them of the same save."""


def keep_entries(source: Save, target: Save, rules: Rules) -> None:
    """`target` has the values and the discrete state of `source`, all the running mixes and their entries read."""
    for memo in (_MIX, _TOWN):
        memo.carry(source, target, rules)
    keep_mix_ids(source, target, rules)
    keep_spent(source, target, rules)


def mix_entries(save: Save, rules: Rules) -> Entries:
    """The running mix's cards in flattened order with their effective share (their saved share plus their gains from
    paused and spent cards) and how that share runs, a tapped card's included (YIELDED, or whichever longer-lasting Run applies):
    grey, then spent, then pause, then waiting, then yield (held, which running() applies to a card still at FULL,
    comes last)."""
    return _MIX.get(save, rules, lambda: _mix_entries(save, rules))[0]


def town_entries(save: Save, rules: Rules) -> Entries:
    """The running town mix's cards on joined lanes, in flattened order, with their effective share of their person's
    time and how it runs: as mix_entries, a share YIELDED while a tap holds the card's lane (engine/design/, "THE TOWN'S
    MIX", "Rates on a joined lane"). A card on a lane not joined runs nothing."""
    return _TOWN.get(save, rules, lambda: _town_entries(save, rules))[0]


def mix_gains(save: Save, rules: Rules) -> Gains:
    """Each card of the running mixes receiving a paused or spent card's share, with what it receives from each, in the
    mix order of the givers (design/spent.txt, "SPENT"); a card absent receives nothing."""
    hands = _MIX.get(save, rules, lambda: _mix_entries(save, rules))[1]
    town = _TOWN.get(save, rules, lambda: _town_entries(save, rules))[1]
    return hands | town if town else hands


def _mix_entries(save: Save, rules: Rules) -> tuple[Entries, Gains]:
    mix = running_mix(save, rules)
    if mix is None:
        return (), {}
    handed = _busy(save, HANDS)
    entries = _entries(save, rules, flatten_shares(save.mixes, mix.id), mix.id, lambda _: handed)
    return yielded(entries, lambda _: HANDS)


_TOWN_BUILT: KeyedMemo[tuple[Entries, Gains]] = KeyedMemo()
"""_town_entries kept across saves (see _town_key): an advance's instants mostly leave all of its inputs as they were."""


def _town_entries(save: Save, rules: Rules) -> tuple[Entries, Gains]:
    mix = running_town_mix(save, rules)
    if mix is None:
        return (), {}
    shares = flatten_shares(save.mixes, mix.id)
    return _TOWN_BUILT.get((rules, save.unlocked), _town_key(save, rules, shares),
                           lambda: _town_built(save, rules, mix, shares))


def _town_key(save: Save, rules: Rules, shares: tuple[CardShare, ...]) -> tuple[object, ...]:
    """Everything _town_built reads beyond the rules and the unlock set (the memo's parts, by identity: the joined, left
    and retired, the maker sets): the running mix's flattened shares (all it reads of save.mixes; its id only asks
    whether it is greyed, which a town mix, holding no card of the hands, never is); each lane's tap held and own split
    (busy lanes, crews); who is paused on what; each share's first unmet require (its WAITING run); and, only while a
    card is paused, the spent stores (read only for a run paused dry)."""
    cards = index(rules).cards
    return (shares,
            tuple((ls.lane, ls.card is not None, ls.own_split) for ls in save.lanes),
            tuple((p.runner, p.store) for p in save.pauses),
            tuple(first_unmet(save, rules, cards[s.card]) for s in shares),
            spent_stores(save, rules) if save.pauses else None)


def _town_built(save: Save, rules: Rules, mix: Mix, shares: tuple[CardShare, ...]) -> tuple[Entries, Gains]:
    cards = index(rules).cards
    shares = present(save, rules, shares)
    entries = _entries(save, rules, shares, mix.id, lambda card: _busy(save, cards[card].lane))
    return crewed(save, rules, *yielded(entries, lambda card: cards[card].lane))


def _entries(save: Save, rules: Rules, shares: tuple[CardShare, ...], mix: MixId, handed: Callable[[CardId], bool]
             ) -> Entries:
    """Each card at its saved share, a card paused on a spent store SPENT (spent.spend)."""
    paused = {p.runner: p.store for p in save.pauses}
    grey = greyed(save, rules, mix)
    return spend(save, rules, tuple(
        (s.card, s.share_bp, _mix_run(save, rules, s.card, paused.get(s.card), grey, handed(s.card))) for s in shares))


def _mix_run(save: Save, rules: Rules, card: CardId, paused_on: StoreId | None, grey: bool, handed: bool) -> Run:
    if grey or is_retired(save, rules, card):
        return Run(RunKind.GREYED, 0, 1)
    if paused_on is not None:
        return Run(RunKind.PAUSED, 0, 1, paused_on)
    unmet = first_unmet(save, rules, index(rules).cards[card])
    if unmet is not None:
        return Run(RunKind.WAITING, 0, 1, None, unmet)
    return Run(RunKind.YIELDED, 0, 1) if handed else Run(RunKind.FULL)
