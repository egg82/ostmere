"""What a route does in week two's chapters before the shared chapter moves (daythree/moves.py, Later.own), read off the
save the way the page shows it: a person's split in the town's mix set once a moment has come (the town mix's Change),
one decision. Ids come from the chapter (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import dataclass

from ashfall_app.engine import (
    BP, CardId, CardShare, Mix, Rules, Save, SaveMix, Unlock, UnlockKind, View,
)
from tests.dayone.policy import Move


@dataclass(frozen=True)
class Split:
    """One person's time in the town's mix once `after` is unlocked: each card at its share. Per lane the last split
    whose `after` holds is the one kept."""

    lane: str
    shares: tuple[tuple[str, int], ...]
    after: Unlock


@dataclass(frozen=True)
class WeekTwoKnobs:
    splits: tuple[Split, ...] = ()


def feature(fid: str) -> Unlock:
    return Unlock(UnlockKind.FEATURE, fid)


def card(cid: str) -> Unlock:
    return Unlock(UnlockKind.CARD, cid)


def lane_of(rules: Rules) -> dict[str, str]:
    return {str(c.id): str(c.lane) for c in rules.cards}


def due_splits(save: Save, knobs: WeekTwoKnobs) -> dict[str, Split]:
    held = set(save.unlocked)
    return {s.lane: s for s in knobs.splits if s.after in held}


def split_move(save: Save, rules: Rules, knobs: WeekTwoKnobs) -> Move | None:
    """The town mix saved again with each due split, once it differs from what is saved: the other people's shares as
    they were, the lane's own as the split names. A card not yet unlocked waits."""
    held = set(save.unlocked)
    lanes = lane_of(rules)
    for mix in (m for m in save.mixes if str(m.id).startswith("town:")):
        comps = [c for c in mix.components if isinstance(c, CardShare)]
        new = list(comps)
        for lane, sp in due_splits(save, knobs).items():
            if not all(Unlock(UnlockKind.CARD, c) in held for c, _ in sp.shares):
                continue
            if not any(lanes.get(str(c.card)) == lane for c in comps):
                continue   # not in the town's mix: its rules set its task
            new = [c for c in new if lanes.get(str(c.card)) != lane] + [CardShare(CardId(c), bp) for c, bp in sp.shares]
        if sorted(new, key=str) != sorted(comps, key=str):
            assert all(0 <= c.share_bp <= BP for c in new)
            return "decision", (SaveMix(Mix(mix.id, tuple(new))),)
    return None


def move(v: View, save: Save, rules: Rules, knobs: WeekTwoKnobs) -> Move | None:
    return split_move(save, rules, knobs)
