"""What the player keeps doing, counted from the save's decision log (api/CONTRACT.txt, "Repeats"): the same hands
card tapped while the hands ran a mix that does not hold it, and the same switch of the player's own mix made while a
chip showed. Each logged decision keeps its context (engine DecisionContext), so the count reads the log alone, needs
no replay, and comes out the same for a save rebuilt by replaying that log. How many make a habit, and over how much
game time, is opening.toml's [repeat_offers]."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from .. import engine as e


@dataclass(frozen=True)
class RepeatRules:
    """opening.toml's [repeat_offers]."""

    hand_taps: int
    """Taps of one card that make it offered to the mix."""
    hand_taps_within_s: int
    """The game seconds back from now that taps are counted over."""
    switches: int
    """Switches to one mix under one chip that make a rule offered."""
    switches_within_s: int
    """The game seconds back from now that switches are counted over."""


@dataclass(frozen=True)
class Logged:
    """One decision as the log keeps it."""

    at: int
    verb: e.Verb
    context: e.DecisionContext | None
    """None on a row written before contexts were kept: it counts for nothing."""


@dataclass(frozen=True)
class Repeats:
    """The repeats that reached their count, each with its count, in the order each was first made in the window."""

    taps: tuple[tuple[e.CardId, int], ...] = ()
    switches: tuple[tuple[e.ChipId, e.MixId, int], ...] = ()


def since(r: RepeatRules, now: int) -> dict[str, int]:
    """The earliest game time counted, per logged kind (write.KINDS)."""
    return {"tap_card": now - r.hand_taps_within_s, "switch_mix": now - r.switches_within_s}


def count(log: Iterable[Logged], now: int, hands: frozenset[e.CardId], r: RepeatRules) -> Repeats:
    """The repeats in `log` (in decision order) as of game time `now`. A tap counts when its card is on the hands lane
    (`hands`) and the hands ran a mix that did not hold it; a switch counts once for each chip shown when it was made,
    unless the hands already ran that mix."""
    taps: Counter[e.CardId] = Counter()
    switches: Counter[tuple[e.ChipId, e.MixId]] = Counter()
    for d in log:
        c = d.context
        if c is None:
            continue
        if isinstance(d.verb, e.TapCard) and d.at >= now - r.hand_taps_within_s and d.verb.card in hands \
                and c.mix is not None and not c.in_mix:
            taps[d.verb.card] += 1
        if isinstance(d.verb, e.SwitchMix) and d.at >= now - r.switches_within_s and c.mix != d.verb.mix:
            for chip in c.chips:
                switches[(chip, d.verb.mix)] += 1
    return Repeats(taps=tuple((k, n) for k, n in taps.items() if n >= r.hand_taps),
                   switches=tuple((chip, mix, n) for (chip, mix), n in switches.items() if n >= r.switches))


def hands_cards(rules: e.Rules) -> frozenset[e.CardId]:
    return frozenset(c.id for c in rules.cards if c.lane == e.HANDS)
