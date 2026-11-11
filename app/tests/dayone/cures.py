"""Every status chip shown in day one has a cure the player can reach. At each checked sample, the opening's own
session included, where a chip shows on the page (on in the view, and its offered_after unlocked: entries.ChipEntry;
its first sample, each visit's return, and at least every CHECK_EVERY_S while it stays), a fork of
the save must see the chip clear within CURE_S, either with nobody acting (a rule the player set, or a standing action)
or by one card on the panel that puts the chip's store up (its completion adds to it, its lines make it, or it unlocks
a standing action that makes it): tapped whenever it is ready, with whatever ready card makes a store it is short of
tapped while it is not. A capped card whose own completion count a trigger adds the store at cures by its stages
instead: the fork starts its next stage within CURE_S and the chip is off by the completion that trigger counts. A chip whose content marks it no_cure (entries.ChipEntry) is not checked.

Problems name the chip, the minute of play and ids only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Callable, Iterator

from ashfall_app.engine import (
    CardDef, CardId, ChipId, Rules, Save, StoreId, StoreValue, TapCard, Unlock, UnlockKind, View, advance, decide, next_event,
    value, view,
)
from ashfall_app.opening.convert import unlock
from ashfall_app.engine.checks import check_hand_tap
from ashfall_app.engine.errors import InvalidVerbError
from ashfall_app.engine.work import completions
from ashfall_app.engine.cure_reading import count_stores, cures_chip
from tests.dayone.player import DayOnePlayer
from tests.opening.playthrough import opening

CURE_S = 600
"""How long a present player may take to clear a chip from when it is checked."""
CHECK_EVERY_S = 3600
STAGE_STEPS = 1000
"""Instants a capped cure card's stages may take to land before the plan is given up."""


def uncured(p: DayOnePlayer, since: int = 0) -> list[str]:
    """One problem per checked sample from `since` (seconds) where nothing clears its chip."""
    return [f"{chip} at minute {save.time // 60}: nothing on offer clears it"
            for save, v, chip in checked(p) if save.time >= since and not cured(save, p.rules, v, chip)]


def checked(p: DayOnePlayer) -> Iterator[tuple[Save, View, str]]:
    exempt = {c.id for c in opening().chips if c.no_cure}
    after = {c.id: unlock(c.offered_after) for c in opening().chips if c.offered_after is not None}
    returns = {v.start for v in p.visits if v.gap > 0}
    last: dict[str, int] = {}
    before: tuple[str, ...] = ()
    for save, v in p.history:
        shown = tuple(str(c) for c in v.chips if c not in after or after[c] in v.unlocked)
        for chip in shown:
            due = chip not in before or save.time in returns or save.time - last[chip] >= CHECK_EVERY_S
            if chip not in exempt and due:
                last[chip] = save.time
                yield save, v, chip
        before = shown


def cured(save: Save, rules: Rules, v: View, chip: str) -> bool:
    """Some way of playing on from `save` shows `chip` cleared within CURE_S: nobody acting, or one card's plan."""
    deadline = save.time + CURE_S
    store = _store(rules, chip)
    return any(_clears(save, rules, chip, deadline, c.card) or _staged(save, rules, chip, deadline, c.card, store)
               for c in v.cards if cures_chip(rules, c.card, ChipId(chip)) and tappable(rules, c.card)) \
        or _clears(save, rules, chip, deadline, None)


def tappable(rules: Rules, card: CardId) -> bool:
    """Whether the hands may tap `card`: a card on a lane a rule sets (a townsperson's) is the rule's, not a cure on offer."""
    try:
        check_hand_tap(rules, TapCard(card))
    except InvalidVerbError:
        return False
    return True


def _store(rules: Rules, chip: str) -> str:
    when = next(c.when for c in rules.chips if c.id == chip)
    subject = getattr(when, "subject", None)
    assert isinstance(subject, StoreValue), f"chip {chip} does not watch a store"
    return subject.store


def _card(rules: Rules, card: CardId) -> CardDef:
    return next(x for x in rules.cards if x.id == card)


def _clears(save: Save, rules: Rules, chip: str, deadline: int, card: CardId | None) -> bool:
    return _until(save, rules, deadline, card, lambda s: not _shown(s, rules, chip))


def raises(save: Save, rules: Rules, store: str, card: CardId) -> bool:
    """Playing on from `save` with `card` tapped as `cured` taps one (act), `store` stands higher within CURE_S."""
    level = value(save, rules, StoreId(store), save.time)
    return _until(save, rules, save.time + CURE_S, card, lambda s: value(s, rules, StoreId(store), s.time) > level)


def _until(save: Save, rules: Rules, deadline: int, card: CardId | None, done: Callable[[Save], bool]) -> bool:
    """Whether `done` holds by `deadline` playing on with nobody acting but `card`'s tap, taken whenever it can be."""
    while not done(save):
        if card is not None:
            save = act(save, rules, card)
        event = next_event(save, rules)
        t = deadline if event is None or event.time > deadline else event.time
        if t <= save.time:
            t = save.time + 1   # an instant that resolved to itself: step past it
        if t > deadline:
            return False
        save = advance(save, rules, t)
    return True


def _staged(save: Save, rules: Rules, chip: str, deadline: int, card: CardId, store: str) -> bool:
    """A capped `card` whose completion count a trigger adds `store` at: its next stage is started by `deadline`, and
    the chip is off when the completion that count names has landed."""
    count = count_stores(rules, _card(rules, card)).get(store)
    if _card(rules, card).cap is None or count is None:
        return False
    started = False
    for _ in range(STAGE_STEPS):
        if not _shown(save, rules, chip):
            return True
        if completions(save, rules, card) >= count:
            return False
        if not _running(save, card):
            save = act(save, rules, card)
        started = started or _running(save, card)
        event = next_event(save, rules)
        if event is None:
            return False
        t = max(event.time, save.time + 1)
        if t > deadline and not started:
            return False
        save = advance(save, rules, t)
    return False


def _running(save: Save, card: CardId) -> bool:
    return any(ls.card == card for ls in save.lanes)


def act(save: Save, rules: Rules, card: CardId) -> Save:
    """Tap `card` when it is ready and its lane free or it cuts in (CardView.cuts_in); else a ready card on a free lane
    making a store it is short of."""
    v = view(save, rules)
    free = {b.lane for b in v.lanes if b.card is None}
    panel = {c.card: c for c in v.cards}
    target = panel.get(card)
    if target is None:
        return save
    cards = {c.id: c for c in rules.cards}
    if target.blocker is None:
        return decide(save, rules, save.time, TapCard(card)) if cards[card].lane in free or target.cuts_in else save
    short = {n.store for n in target.needs if n.segment.start_value < n.quantity}
    feeder = next((c.card for c in v.cards if c.blocker is None and cards[c.card].lane in free and tappable(rules, c.card) and any(
        s in short for s in (*(a.store for a in cards[c.card].outcome.stores), *(f.store for f in cards[c.card].makes)))),
        None)
    return save if feeder is None else decide(save, rules, save.time, TapCard(feeder))


def _shown(save: Save, rules: Rules, chip: str) -> bool:
    i = next(i for i, c in enumerate(rules.chips) if c.id == chip)
    return save.chips[i] and Unlock(UnlockKind.CHIP, chip) in save.unlocked
