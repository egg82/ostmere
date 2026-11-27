"""The whenever player on the fixture outpost: the visits it makes, the moves it makes in each (the gatherer first,
then its sinks: tests/dayone/sinks.py), and the log of every verb it sent, for the 2 AM replay (dayone/parity.py)."""
from dataclasses import dataclass, field
from typing import Unpack

from ashfall_app.engine import (
    BP, AtLeast, CardCount, CardShare, Mix, MixId, QueueEntry, Rules, Save, SaveMix, SetQueue, SwitchMix, TapCard, Verb, View,
    advance, decide, new_save, view,
)
from tests.dayone import sinks
from tests.supply.chapter import BUILD, CHAPTER, GATHER, STAGES, Knobs, rules

Visit = tuple[int, int]
MOVES_PER_VISIT = 20


@dataclass
class Played:
    save: Save
    log: list[tuple[int, Verb]] = field(default_factory=lambda: [])


def play(visits: tuple[Visit, ...], knobs: sinks.SinkKnobs, until: int, **kw: Unpack[Knobs]) -> Played:
    """The route from a new save through `visits` (start, end), then on with nobody deciding to `until`; each visit's
    moves are made at its start and again at its end, one after another until the view shows nothing left to do."""
    r = rules(**kw)
    p = Played(new_save(r))
    for start, end in (v for v in visits if v[0] <= until):
        for at in (start, min(end, until)):
            p.save = advance(p.save, r, at)
            _settle(p, r, at, knobs)
    p.save = advance(p.save, r, until)
    return p


def _settle(p: Played, r: Rules, at: int, knobs: sinks.SinkKnobs) -> None:
    for _ in range(MOVES_PER_VISIT):
        m = _gather(p.save) or _stages(view(p.save, r), p.save) or sinks.move(view(p.save, r), r, p.save, CHAPTER, knobs)
        if m is None:
            return
        for verb in m[1]:
            p.save = decide(p.save, r, at, verb)
            p.log.append((at, verb))
    raise AssertionError("a visit never settled")


def _gather(save: Save) -> tuple[str, tuple[Verb, ...]] | None:
    """The first move: the gatherer alone in the mix."""
    if save.active is not None:
        return None
    mix = Mix(MixId("gather_only"), (CardShare(GATHER, BP),))
    return "decision", (SaveMix(mix), SwitchMix(mix.id))


def _stages(v: View, save: Save) -> tuple[str, tuple[Verb, ...]] | None:
    """Once the build shows, every stage queued at once, When ready (the queue carries them across the night)."""
    if save.queue or all(c.card != BUILD for c in v.cards):
        return None
    queue = tuple(QueueEntry(TapCard(BUILD), AtLeast(CardCount(BUILD), n, n)) for n in range(1, STAGES + 1))
    return "decision", (SetQueue(queue),)
