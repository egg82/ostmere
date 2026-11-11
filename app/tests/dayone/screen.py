"""What the page states and draws on the human-paced player's day, read through the page's own rules, mirrored here from
client/src/game/shown.ts (currentAim, the chips and the hands strip) and ui/ledger.ts: the aim stated at each view
(the last aim in content order whose `after` the view's unlocks hold), and the Ashfall-specific mechanics drawn
(docs/decisions.md, "The screen arrives when it means something"). The page's own tests hold those rules; these read
when they fire in play. Aims and mechanics are named by id or kind, never by text."""
from collections.abc import Iterable, Mapping, Sequence

from ashfall_app.engine import Save, View
from ashfall_app.opening.feature_entries import AimEntry
from tests.dayone.human import HumanPlayer
from tests.opening.playthrough import opening

Key = tuple[str, str]
FIRST_S = 300
"""The opening window the readout lists the drawn mechanics for."""


def aim_at(aims: Sequence[AimEntry], have: set[Key]) -> str | None:
    on = [a.id for a in aims if a.after is None or (a.after.unlock_kind, a.after.id) in have]
    return on[-1] if on else None


def stated(aims: Sequence[AimEntry], views: Iterable[tuple[int, View]]) -> list[tuple[int, str | None]]:
    """(game time, the aim the page states) at each view."""
    return [(t, aim_at(aims, {(u.kind.value, str(u.id)) for u in v.unlocked})) for t, v in views]


def unstated(aims: Sequence[AimEntry], seen: list[tuple[int, str | None]]) -> list[str]:
    """The aims never stated at any view: an `after` that never lands in play."""
    assert seen, "no views to read"
    met = {a for _, a in seen}
    return [a.id for a in aims if a.id not in met]


def aimless(seen: list[tuple[int, str | None]]) -> list[int]:
    """The game times of the views that state no aim."""
    return [t for t, a in seen if a is None]


def views(p: HumanPlayer) -> list[tuple[int, View]]:
    return [(save.time, v) for save, v in p.history]


def unlocked(v: View) -> set[Key]:
    return {(u.kind.value, str(u.id)) for u in v.unlocked}


def drawn(save: Save, v: View, chip_after: Mapping[str, Key]) -> set[str]:
    """The Ashfall-specific mechanics the page draws for this view: a chip on whose offered_after holds; the hands
    strip (the mix) from the first mix's feature or a saved mix or rule; rules, once one exists or the ledger offers
    one under a red line; the mix editor's Edit, once a mix greys or an action card the first mix does not hold is in
    play."""
    o, have = opening(), unlocked(v)
    out: set[str] = set()
    if any(c not in chip_after or chip_after[c] in have for c in map(str, v.chips)):
        out.add("chips")
    if ("feature", o.first_mix.feature) in have or save.mixes or save.orders:
        out.add("mix")
    red = {str(ln.store) for ln in v.ledger if ln.starved or (ln.falling and not ln.covered)}
    offers = [c for c in o.order_cards if c.chip is None and c.store in red
              and (c.offered_after is None or (c.offered_after.unlock_kind, c.offered_after.id) in have)]
    if save.orders or (("feature", "ledger") in have and offers):
        out.add("rules")
    cards = {c.id: c for c in o.cards}
    first = set(o.first_mix.cards)
    if v.greyed_mixes or any(cards[str(c.card)].presentation == "action" and cards[str(c.card)].lane == "hands"
                             and str(c.card) not in first for c in v.cards):
        out.add("mix editor")
    return out


def early(p: HumanPlayer, chip_after: Mapping[str, Key]) -> set[str]:
    """Every mechanic drawn at some view in the first FIRST_S seconds."""
    return set[str]().union(*(drawn(save, v, chip_after) for save, v in p.history if save.time <= FIRST_S))


def chip_after() -> dict[str, Key]:
    return {c.id: (c.offered_after.unlock_kind, c.offered_after.id)
            for c in opening().chips if c.offered_after is not None}
