"""What a player does about the town's mix (engine DESIGN.txt, "THE TOWN'S MIX"), by kind and not by id. The default
leaves the split a join made: the join turns each person's always task into their share, the town's own rule runs the
mix, and nobody acts. `resplit` is the attention the default is measured against: at a visit, each joined person's whole
time on the card of theirs that makes the most, the best split a player could set by hand. Ids come from the rules
passed in (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Callable

from ashfall_app.engine import BP, CardDef, CardShare, Mix, Rules, Save, SaveMix, UnlockKind
from tests.dayone.policy import Move


Policy = Callable[[Save, Rules], Move | None]
"""A town policy: the move a player makes at a visit, or None to leave the town as it is."""


def default_split(save: Save, rules: Rules) -> Move | None:
    """The town's default policy: leave the join's split."""
    return None


def town_mixes(save: Save) -> tuple[Mix, ...]:
    return tuple(m for m in save.mixes if str(m.id).startswith("town:"))


def joined(save: Save, rules: Rules) -> tuple[str, ...]:
    held = {u.id for u in save.unlocked if u.kind == UnlockKind.JOINED}
    return tuple(str(lane.id) for lane in rules.lanes if str(lane.id) in held)


def worth(card: CardDef) -> int:
    """What a card makes per hour at a full share, summed over its flows (the fixture's stores share a unit)."""
    return sum(f.per_hour for f in card.makes)


def best_card(rules: Rules, lane: str) -> CardDef | None:
    """The lane's card making the most; of equals the last declared, so a re-split is a real change from the join's."""
    on_lane = [c for c in rules.cards if str(c.lane) == lane and c.cap is None and worth(c) > 0]
    return max(reversed(on_lane), key=worth, default=None)


def resplit(save: Save, rules: Rules) -> Move | None:
    """Every town mix saved again with each joined person's time on their best card, once it differs from what is
    saved; None when it already is that split."""
    saves: list[SaveMix] = []
    for mix in town_mixes(save):
        shares = tuple(CardShare(c.id, BP) for lane in joined(save, rules) if (c := best_card(rules, lane)) is not None)
        best = Mix(mix.id, shares)
        if best != mix:
            saves.append(SaveMix(best))
    return ("decision", tuple(saves)) if saves else None
