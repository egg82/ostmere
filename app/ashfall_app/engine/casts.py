"""What a Cast does to a save: one lane's feature joins the unlock set. Semantics: api/contract/casting.txt, "CASTING".
Reads the counts and the people at the instant; the fact it writes only grows, so a rebase replays the same cast."""
from dataclasses import replace

from .cards import Cast, CastPick
from .castparts import cast_features
from .counts import completions
from .gone import is_left
from .joins import is_joined
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind, unlock_key


def cast_roles(save: Save, rules: Rules, casts: tuple[Cast, ...]) -> Save:
    """Each cast in tuple order, unless its role is cast already (then it changes nothing)."""
    for c in casts:
        held = {u.id for u in save.unlocked if u.kind is UnlockKind.FEATURE}
        if not any(p.feature in held for p in c.picks):
            chosen = _chosen(save, rules, c, held)
            if chosen is not None:
                unlocked = {*save.unlocked, Unlock(UnlockKind.FEATURE, chosen.feature)}
                save = replace(save, unlocked=tuple(sorted(unlocked, key=unlock_key)))
    return save


def _chosen(save: Save, rules: Rules, c: Cast, held: set[str]) -> CastPick | None:
    """The pick the cast gives the role to, None when no lane is eligible: joined, not left, holding no cast feature (a
    lane holds at most one role); then each pattern keeps the lanes with the most completions."""
    by_lane = cast_features(rules)
    running = [p for p in c.picks if is_joined(save, rules, p.lane) and not is_left(save, p.lane)
               and not by_lane.get(p.lane, frozenset()) & held]
    for i in range(len(c.picks[0].counted) if c.picks else 0):
        if len(running) <= 1:
            break
        counts = [(_count(save, rules, p, i), p) for p in running]
        top = max(n for n, _ in counts)
        running = [p for n, p in counts if n == top]
    return running[0] if running else None


def _count(save: Save, rules: Rules, pick: CastPick, pattern: int) -> int:
    card = pick.counted[pattern]
    return 0 if card is None else completions(save, rules, card)
