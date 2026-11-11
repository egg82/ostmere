"""The running mixes: the hands' (an order's, else the player's own) and the town's (an order's alone), and their
cards' shares with how each runs now. Semantics: DESIGN.txt, "Order mix" and "THE TOWN'S MIX"."""
from collections.abc import Callable

from .counts import greyed
from .ids import HANDS, CardId, LaneId, MixId, StoreId
from .index import index
from .memo import SaveMemo
from .mixes import CardShare, Mix, SpentShare, flatten_shares
from .modifiers import Run, RunKind
from .plan import running_mix_id, running_town_mix_id
from .requires import first_unmet
from .rules import Rules
from .spent import spend, yielded
from .state import Save
from .unlocked import is_unlocked
from .unlocks import Unlock, UnlockKind


def _busy(save: Save, lane: LaneId) -> bool:
    """A tap holds the lane."""
    return any(ls.lane == lane and ls.card is not None for ls in save.lanes)


def running_mix(save: Save, rules: Rules) -> Mix | None:
    """The mix the hands run now: an order's while its condition holds, else the player's own (DESIGN.txt, "Order
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


def mix_entries(save: Save, rules: Rules) -> Entries:
    """The running mix's cards in flattened order with their effective share (their saved share plus their gains from
    paused and spent cards) and how that share runs, a tapped card's included (YIELDED, or whichever longer-lasting Run applies):
    grey, then spent, then pause, then waiting, then yield (held, which running() applies to a card still at FULL,
    comes last)."""
    return _MIX.get(save, rules, lambda: _mix_entries(save, rules))[0]


def town_entries(save: Save, rules: Rules) -> Entries:
    """The running town mix's cards on joined lanes, in flattened order, with their effective share of their person's
    time and how it runs: as mix_entries, a share YIELDED while a tap holds the card's lane (DESIGN.txt, "THE TOWN'S
    MIX", "Rates on a joined lane"). A card on a lane not joined runs nothing."""
    return _TOWN.get(save, rules, lambda: _town_entries(save, rules))[0]


def mix_gains(save: Save, rules: Rules) -> Gains:
    """Each card of the running mixes receiving a paused or spent card's share, with what it receives from each, in the
    mix order of the givers (DESIGN.txt, "SPENT"); a card absent receives nothing."""
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


def _town_entries(save: Save, rules: Rules) -> tuple[Entries, Gains]:
    mix = running_town_mix(save, rules)
    if mix is None:
        return (), {}
    cards = index(rules).cards
    present = tuple(s for s in flatten_shares(save.mixes, mix.id)
                    if is_unlocked(save, rules, Unlock(UnlockKind.JOINED, cards[s.card].lane)))
    entries = _entries(save, rules, present, mix.id, lambda card: _busy(save, cards[card].lane))
    return yielded(entries, lambda card: cards[card].lane)


def _entries(save: Save, rules: Rules, shares: tuple[CardShare, ...], mix: MixId, handed: Callable[[CardId], bool]
             ) -> Entries:
    """Each card at its saved share, a card paused on a spent store SPENT (spent.spend)."""
    paused = {p.runner: p.store for p in save.pauses}
    grey = greyed(save, rules, mix)
    return spend(save, rules, tuple(
        (s.card, s.share_bp, _mix_run(save, rules, s.card, paused.get(s.card), grey, handed(s.card))) for s in shares))


def _mix_run(save: Save, rules: Rules, card: CardId, paused_on: StoreId | None, grey: bool, handed: bool) -> Run:
    if grey:
        return Run(RunKind.GREYED, 0, 1)
    if paused_on is not None:
        return Run(RunKind.PAUSED, 0, 1, paused_on)
    unmet = first_unmet(save, rules, index(rules).cards[card])
    if unmet is not None:
        return Run(RunKind.WAITING, 0, 1, None, unmet)
    return Run(RunKind.YIELDED, 0, 1) if handed else Run(RunKind.FULL)
