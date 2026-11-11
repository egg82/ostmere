"""The yield and spent stores: a running mix's card holding a Pause gives its share to the rest of its mix on its lane,
in proportion to their saved shares, and a card paused on a store nothing in play can make again reads SPENT. Derived
from the save at one instant, never stored (DESIGN.txt, "SPENT")."""
from collections.abc import Callable

from .cardsides import card_makes
from .counts import is_completed
from .fightlines import fight_costs
from .gone import stopped
from .ids import CardId, LaneId, Runner, StoreId
from .index import derived
from .memo import SaveMemo
from .mixes import SpentShare
from .modifiers import Run, RunKind
from .rules import Rules
from .sides import costs, makes
from .state import Save
from .unlocked import is_unlocked
from .unlocks import Unlock, UnlockKind

type Maker = tuple[Runner, Unlock, frozenset[StoreId]]
"""A runner that can make a store: its id, the unlock that puts it in play, and the stores it takes (costs, inputs)."""

type Entry = tuple[CardId, int, Run]

GIVES = frozenset({RunKind.SPENT, RunKind.PAUSED})
"""The Runs of a mix card holding a Pause: a giver (DESIGN.txt, "SPENT", "Giver")."""


def spent_stores(save: Save, rules: Rules) -> frozenset[StoreId]:
    """The largest S such that every maker in play of each store in S takes from a store of S at 0 (DESIGN.txt,
    "SPENT", "Spent stores"): found by removing, until nothing changes, each store with a maker taking from none."""
    return _SPENT.get(save, rules, lambda: _spent(save, rules))


_SPENT: SaveMemo[frozenset[StoreId]] = SaveMemo(4)


def _spent(save: Save, rules: Rules) -> frozenset[StoreId]:
    empty = {st.store for st in save.stores if st.segment.start_value == 0}
    live = {x: [takes for runner, u, takes in found if _in_play(save, rules, runner, u)]
            for x, found in _makers(rules).items()}
    spent = {d.id for d in rules.stores}
    changed = True
    while changed:
        changed = False
        blocked = spent & empty
        for x in list(spent):
            if any(not (takes & blocked) for takes in live.get(x, ())):
                spent.discard(x)
                changed = True
    return frozenset(spent)


def _in_play(save: Save, rules: Rules, runner: Runner, u: Unlock) -> bool:
    """Unlocked, and neither a card completed (or out of play) nor a standing a Leave stopped (LEAVES, "Stops")."""
    if not is_unlocked(save, rules, u):
        return False
    if u.kind is UnlockKind.ACTION:
        return runner not in stopped(save, rules)
    return u.kind is not UnlockKind.CARD or not is_completed(save, rules, CardId(runner))


def _makers(rules: Rules) -> dict[StoreId, list[Maker]]:
    return derived(rules, "_spent_makers", _all_makers)


def _all_makers(rules: Rules) -> dict[StoreId, list[Maker]]:
    """Every standing action and card by the stores it can make; triggers and answers are never makers."""
    out: dict[StoreId, list[Maker]] = {}
    for a in rules.standing:
        for x in makes(rules, a.id):
            out.setdefault(x, []).append((a.id, Unlock(UnlockKind.ACTION, a.id), costs(rules, a.id)))
    for c in rules.cards:
        takes = frozenset(f.store for f in c.costs) | frozenset(
            x.store for x in (*c.inputs, *(fight_costs(c.fight) if c.fight else ())))
        for x in card_makes(c) | frozenset(a.store for a in c.finished.stores):
            out.setdefault(x, []).append((c.id, Unlock(UnlockKind.CARD, c.id), takes))
    return out


def spend(save: Save, rules: Rules, entries: tuple[Entry, ...]) -> tuple[Entry, ...]:
    """`entries` with each PAUSED run on a spent store made SPENT; the store set is read only when a run is paused."""
    if not any(run.kind is RunKind.PAUSED for _, _, run in entries):
        return entries
    spent = spent_stores(save, rules)
    return tuple((card, share, Run(RunKind.SPENT, 0, 1, run.store))
                 if run.kind is RunKind.PAUSED and run.store in spent else (card, share, run)
                 for card, share, run in entries)


def yielded(entries: tuple[Entry, ...], lane_of: Callable[[CardId], LaneId]
            ) -> tuple[tuple[Entry, ...], dict[CardId, tuple[SpentShare, ...]]]:
    """The entries at their effective shares, and each receiver's gains in the mix order of the givers: on each lane,
    every card r that is no giver gains floor(s_k * s_r / Rsum) from each giver k, Rsum those cards' saved shares
    summed; nothing moves while Rsum is 0 (DESIGN.txt, "SPENT", "The yield")."""
    if not any(run.kind in GIVES for _, _, run in entries):
        return entries, {}
    gains: dict[CardId, tuple[SpentShare, ...]] = {}
    for lane in dict.fromkeys(lane_of(card) for card, _, _ in entries):
        on = [e for e in entries if lane_of(e[0]) == lane]
        given = [(card, share) for card, share, run in on if run.kind in GIVES]
        rest = [(card, share) for card, share, run in on if run.kind not in GIVES]
        total = sum(share for _, share in rest)
        if total == 0:
            continue
        for card, share in rest:
            got = tuple(SpentShare(k, g) for k, s_k in given if (g := s_k * share // total) > 0)
            if got:
                gains[card] = got
    return tuple((card, share + sum(g.share_bp for g in gains.get(card, ())), run)
                 for card, share, run in entries), gains
