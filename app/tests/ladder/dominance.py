"""Whether one saved mix shape always wins (the ladder readout, tests/ladder/readout.py). Pure: the caller supplies, at
each sampled instant, every saved mix's shape and score.

A mix's shape is its flattened cards and shares in basis points. Two shapes are the same when they hold the same cards
and no card's share differs by more than SAME_BP, so a mix saved again with a few points moved stays one shape. At an
instant where two or more shapes are saved, the shape of the highest-scoring mix wins; a tie for the top between
shapes, or a top score of zero, leaves the instant out. One shape always wins when it wins every instant that is
compared. The score (ticks.mix_scores) is the ladder's own unit: levels gained per game hour, each skill's XP rate
over the XP width of the level it stands in."""
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

type Shape = tuple[tuple[str, int], ...]
type Point = tuple[int, Mapping[str, tuple[Shape, float]]]
"""An instant and each saved mix's (shape, score) there."""

SAME_BP = 1000


def same_shape(a: Shape, b: Shape) -> bool:
    ca, cb = dict(a), dict(b)
    return ca.keys() == cb.keys() and all(abs(ca[c] - cb[c]) <= SAME_BP for c in ca)


@dataclass(frozen=True)
class Dominance:
    shapes: tuple[Shape, ...]
    """Each shape's first-seen form, in order of first appearance."""
    winners: tuple[tuple[int, int], ...]
    """(instant, index into shapes) of each compared instant."""
    left_out: int
    """Instants with two or more shapes saved that a tie or a zero top score left out."""
    single: int
    """Instants with fewer than two shapes saved."""

    @property
    def wins(self) -> Counter[int]:
        return Counter(i for _, i in self.winners)

    @property
    def always(self) -> bool:
        return bool(self.winners) and len(self.wins) == 1


def dominance(points: Sequence[Point]) -> Dominance:
    shapes: list[Shape] = []

    def index_of(shape: Shape) -> int:
        found = next((i for i, s in enumerate(shapes) if same_shape(s, shape)), None)
        if found is None:
            shapes.append(shape)
            return len(shapes) - 1
        return found

    winners: list[tuple[int, int]] = []
    left_out = single = 0
    for t, mixes in points:
        best: dict[int, float] = {}
        for shape, score in mixes.values():
            i = index_of(shape)
            best[i] = max(best.get(i, 0.0), score)
        if len(best) < 2:
            single += 1
            continue
        top = max(best.values())
        leaders = [i for i, s in best.items() if s == top]
        if top <= 0 or len(leaders) > 1:
            left_out += 1
        else:
            winners.append((t, leaders[0]))
    return Dominance(tuple(shapes), tuple(winners), left_out, single)
