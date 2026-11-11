"""What a Leave does to a save: the person is gone, and the plan loses what it held for them, the orders tapping the
lane's cards and their shares in every saved mix, and the pauses of what stopped with them. The inverse of joins.py. What follows from the fact (the
lane's cards out of play, the listed standings stopped) is derived where it is read (gone.py). Semantics: DESIGN.txt,
"LEAVES"."""
from dataclasses import replace

from .cards import Leave, RuleInstall
from .gone import is_left
from .ids import CardId
from .index import index
from .installs import without_taps
from .mixes import CardShare, Mix, MixLayer
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind, unlock_key


def left(save: Save, rules: Rules, leaves: tuple[Leave, ...]) -> Save:
    """Each leave in tuple order, unless its lane has left already (then it changes nothing)."""
    for leave in leaves:
        if not is_left(save, leave.lane):
            save = _leave(save, rules, leave)
    return save


def present_installs(save: Save, rules: Rules, installs: tuple[RuleInstall, ...]) -> tuple[RuleInstall, ...]:
    """The installs whose card is not on a lane that has left: an install there changes nothing."""
    cards = index(rules).cards
    return tuple(i for i in installs if not is_left(save, cards[i.card].lane))


def _leave(save: Save, rules: Rules, leave: Leave) -> Save:
    unlocked = tuple(sorted({*save.unlocked, Unlock(UnlockKind.LEFT, leave.lane)}, key=unlock_key))
    cards = frozenset(c.id for c in rules.cards if c.lane == leave.lane)
    save = without_taps(replace(save, unlocked=unlocked), cards)
    runners = {*cards, *leave.stops}
    made = index(rules).town_mixes
    return replace(save, mixes=tuple(_without(m, cards, m.id in made) for m in save.mixes),
                   pauses=tuple(p for p in save.pauses if p.runner not in runners))


def _without(mix: Mix, cards: frozenset[CardId], made: bool) -> Mix:
    """The mix less each share of `cards`; the very mix when it holds none. A mix left empty stays, and stays a
    town mix: a card of a person's lane is only in a town mix, so one a join did not make is marked TOWN."""
    components = tuple(c for c in mix.components if not (isinstance(c, CardShare) and c.card in cards))
    if len(components) == len(mix.components):
        return mix
    return replace(mix, components=components,
                   layer=mix.layer if components or made else MixLayer.TOWN)
