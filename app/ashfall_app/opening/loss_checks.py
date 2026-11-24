"""A fight card that tells its losses from pools of its own (api/CONTRACT.txt, "LOSS LINES"): the four authored fields
come together, only on a card of the player's own (`only_player = "self"`, no town lane, no town twin) whose lost
fight costs nothing but the attempt, and never on a card that can be unlocked before the feature `loss_after` names.
Structural fields only. Raises ValueError naming the card (refs.fail)."""
from typing import TYPE_CHECKING

from .offer_caps import Chain
from .refs import fail

if TYPE_CHECKING:
    from .entries import CardEntry, FightEntry
    from .schema import Opening


def carries(f: "FightEntry | None") -> bool:
    """Whether a fight carries any of the four fields."""
    return f is not None and any(x is not None for x in (f.loss_pool, f.loss_notes, f.on_loss_key, f.loss_after))


def told(o: "Opening") -> "list[CardEntry]":
    """The cards whose fight tells its losses from its own pools, in content order."""
    return [c for c in o.cards if carries(c.fight)]


def check_loss_lines(o: "Opening") -> None:
    for a in o.standing:
        if carries(a.fight):
            fail(f"action {a.id}", "loss_pool, loss_notes, on_loss_key and loss_after are only on a card's fight")
    for c in told(o):
        _check_card(c)


def _check_card(c: "CardEntry") -> None:
    """`only_player = "self"` also keeps the card off a town lane and without a town twin (player_checks.py)."""
    f, where = c.fight, f"card {c.id}"
    assert f is not None
    if f.loss_pool is None or f.loss_notes is None or f.on_loss_key is None or f.loss_after is None:
        fail(where, "loss_pool, loss_notes, on_loss_key and loss_after come together, all four or none")
    if c.only_player != "self":
        fail(where, 'only a card whose only_player is "self" tells losses of its own')
    if f.loses or f.wounds:
        fail(where, "a fight with loss lines costs only the attempt: no loses, no wounds")
    if f.lost_line_keys:
        fail(where, "loss_pool words its lost fights: lost_line_keys stays empty")
    if not f.loss_pool or not f.loss_notes:
        fail(where, "loss_pool and loss_notes each hold at least one key")
    if len(set(f.loss_notes)) != len(f.loss_notes):
        fail(where, "loss_notes holds a key twice")


def check_loss_order(o: "Opening", chain: Chain | None = None) -> None:
    """No card with loss lines can be unlocked before its loss_after feature: not by the start, and not by an outcome
    that need not wait for an unlocker of the feature."""
    cards = told(o)
    if not cards:
        return
    chain = chain or Chain(o)
    features = {x.id for x in o.features}
    start = {(u.unlock_kind, u.id) for u in o.start}
    for c in cards:
        after = c.fight.loss_after if c.fight is not None else None
        if after is None or after not in features:
            fail(f"card {c.id}", f"loss_after {after} is not a feature")
        gives = set(chain.unlockers("feature", after))
        ways = chain.unlockers("card", c.id)
        if ("card", c.id) in start or not ways or not all(chain.before[w] & gives for w in ways):
            fail(f"card {c.id}", f"can be unlocked before the feature {after} (loss_after)")
