"""The entries a card or a standing action holds while it runs, on a side or a lane's speed (DESIGN.txt, "ENTRIES HELD
WHILE A CARD RUNS", "HELD SPEED"): derived from the save's discrete state wherever the stack is read, never stored.
Reads only the lanes' taps, the running mixes, the unlock set and the pauses, never a rate, so building the stack never
recurses into rates.running."""
from .cards import HELD_PREFIX, CardDef, Held, HeldSpeed
from .counts import is_completed
from .gone import stopped
from .ids import CardId, Runner, SourceId
from .index import derived
from .memo import SaveMemo
from .mixruns import mix_entries, town_entries
from .modifiers import LaneSpeed, Modifier, ModifierKind, RunKind, SideStrength
from .rules import Rules, StandingDef
from .state import Save
from .unlocked import is_unlocked
from .units import BP
from .unlocks import Unlock, UnlockKind
from .viewparts import HeldView


def held_source(runner: Runner) -> SourceId:
    return SourceId(f"{HELD_PREFIX}{runner}")


def holders(rules: Rules) -> tuple[CardDef | StandingDef, ...]:
    """The cards that declare while_running, in rules order, then the standing actions that do, in rules order."""
    return derived(rules, "_holders", lambda r: (*(c for c in r.cards if c.while_running),
                                                 *(a for a in r.standing if a.while_running)))


def held_cards(save: Save, rules: Rules) -> dict[Runner, int]:
    """Each holder with a share above 0, in holders order, and its share h: for a card, BP while a lane holds a tap of
    it, else its flattened share in its layer's running mix when that share runs in full; for a standing action, BP
    while it runs (unlocked, not stopped, not paused)."""
    return _SHARES.get(save, rules, lambda: _held_cards(save, rules))


_SHARES: SaveMemo[dict[Runner, int]] = SaveMemo(4)
"""Callers never change what it returns."""


def _held_cards(save: Save, rules: Rules) -> dict[Runner, int]:
    runners = holders(rules)
    if not runners:
        return {}
    cards = [c for c in runners if isinstance(c, CardDef)]
    tapped = {ls.card for ls in save.lanes if ls.card is not None and not is_completed(save, rules, ls.card)}
    mixed: dict[CardId, int] = {card: share for card, share, run in (*mix_entries(save, rules), *town_entries(save, rules))
                                if run.kind is RunKind.FULL and is_unlocked(save, rules, Unlock(UnlockKind.CARD, card))}
    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) for c in cards}
    if len(cards) < len(runners):
        shares |= _standing_shares(save, rules, [a for a in runners if isinstance(a, StandingDef)])
    return {runner: share for runner, share in shares.items() if share > 0}


def _standing_shares(save: Save, rules: Rules, actions: list[StandingDef]) -> dict[Runner, int]:
    paused = {p.runner for p in save.pauses}
    gone = stopped(save, rules)
    return {a.id: BP if a.id not in paused and a.id not in gone
            and is_unlocked(save, rules, Unlock(UnlockKind.ACTION, a.id)) else 0 for a in actions}


def _entry(runner: Runner, w: Held, share: int) -> Modifier:
    target = LaneSpeed(w.lane) if isinstance(w, HeldSpeed) else SideStrength(w.side)
    return Modifier(target, ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))


def held_views(save: Save, rules: Rules) -> tuple[HeldView, ...]:
    """One per held runner, in holders order, with its entries as the stack holds them: each rounds down once, on the
    flattened share, so it never favours the player."""
    if not holders(rules):
        return ()
    shares = held_cards(save, rules)
    return tuple(HeldView(r.id, shares[r.id], tuple(_entry(r.id, w, shares[r.id]) for w in r.while_running))
                 for r in holders(rules) if r.id in shares)


def held_entries(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    """The entries of every held runner, in holders order then declaration order."""
    return tuple(m for h in held_views(save, rules) for m in h.entries)


_CANON: dict[tuple[Modifier, ...], tuple[Modifier, ...]] = {}


def held_part(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    """held_entries as one object per distinct value, so stack_inputs' PartsMemo (which compares parts by identity)
    keeps what it built while the entries are unchanged."""
    entries = held_entries(save, rules)
    if len(_CANON) >= 256:
        _CANON.clear()
    return _CANON.setdefault(entries, entries)
